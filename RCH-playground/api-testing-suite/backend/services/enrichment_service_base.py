"""
Base Enrichment Service

Unified interface for all enrichment services (Financial, Staff, FSA, Google, CQC).
Eliminates code duplication across enrichment implementations.

Implements:
- Unified enrich() method signature
- Unified batch processing with semaphores
- Unified error handling
- Unified logging
- Standard result format
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import asyncio
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class EnrichmentResult:
    """Standard enrichment result format for all services"""
    
    source: str                     # Service name: 'financial', 'staff', 'fsa', 'google', 'cqc'
    status: str                     # 'success', 'failed', 'partial', 'timeout'
    data: Dict[str, Any]           # Enriched data (empty if failed)
    error: Optional[str] = None    # Error message if failed
    processing_time: float = 0.0   # Seconds taken
    home_id: Optional[str] = None  # Home identifier for tracing
    retry_count: int = 0           # Number of retries attempted
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def is_success(self) -> bool:
        """Check if enrichment was successful"""
        return self.status == 'success'
    
    def is_failed(self) -> bool:
        """Check if enrichment failed"""
        return self.status == 'failed'


class BaseEnrichmentService(ABC):
    """
    Abstract base class for all enrichment services.
    
    Provides:
    - Unified enrich() interface for single home
    - Batch processing with semaphore control
    - Standard error handling and logging
    - Timeout management
    """
    
    def __init__(self, timeout_seconds: int = 30):
        """
        Initialize base service.
        
        Args:
            timeout_seconds: Default timeout for API calls
        """
        self.timeout_seconds = timeout_seconds
        self._request_count = 0
        self._error_count = 0
    
    @property
    @abstractmethod
    def service_name(self) -> str:
        """
        Unique service identifier.
        
        Must be implemented by subclasses.
        Example: 'financial', 'staff', 'fsa', 'google', 'cqc'
        """
        pass
    
    @abstractmethod
    async def enrich(
        self,
        home: Dict[str, Any],
        **kwargs
    ) -> EnrichmentResult:
        """
        Enrich a single home.
        
        Must be implemented by subclasses.
        
        Args:
            home: Care home object with at minimum:
                - cqc_location_id or id
                - name
            **kwargs: Service-specific parameters
        
        Returns:
            EnrichmentResult with status, data, and error info
        """
        pass
    
    async def enrich_batch(
        self,
        homes: List[Dict[str, Any]],
        parallel_limit: int = 5,
        timeout: Optional[int] = None,
        **kwargs
    ) -> List[EnrichmentResult]:
        """
        Enrich multiple homes in parallel using semaphore.
        
        Args:
            homes: List of care home objects
            parallel_limit: Max concurrent requests (default 5)
            timeout: Override default timeout for batch
            **kwargs: Service-specific parameters
        
        Returns:
            List of EnrichmentResult objects (one per home)
        """
        if not homes:
            return []
        
        semaphore = asyncio.Semaphore(parallel_limit)
        tasks = []
        
        for home in homes:
            task = self._enrich_with_semaphore(
                semaphore, home, timeout or self.timeout_seconds, **kwargs
            )
            tasks.append(task)
        
        # Run all tasks concurrently and gather results
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results - convert exceptions to failed EnrichmentResult
        final_results = []
        for home, result in zip(homes, results):
            if isinstance(result, Exception):
                home_id = home.get('cqc_location_id') or home.get('id')
                logger.error(
                    f"{self.service_name} batch error for {home.get('name')} "
                    f"(ID: {home_id}): {str(result)}"
                )
                final_results.append(EnrichmentResult(
                    source=self.service_name,
                    status='failed',
                    data={},
                    error=str(result),
                    home_id=home_id
                ))
            else:
                final_results.append(result)
        
        return final_results
    
    async def _enrich_with_semaphore(
        self,
        semaphore: asyncio.Semaphore,
        home: Dict[str, Any],
        timeout: int,
        **kwargs
    ) -> EnrichmentResult:
        """
        Enrich with semaphore control and timeout.
        
        Args:
            semaphore: Asyncio semaphore for concurrency control
            home: Care home object
            timeout: Timeout in seconds
            **kwargs: Service-specific parameters
        
        Returns:
            EnrichmentResult
        """
        async with semaphore:
            start_time = time.time()
            home_id = home.get('cqc_location_id') or home.get('id')
            home_name = home.get('name', 'Unknown')
            
            try:
                # Call the service's enrich method with timeout
                result = await asyncio.wait_for(
                    self.enrich(home, **kwargs),
                    timeout=timeout
                )
                
                # Add processing time
                result.processing_time = time.time() - start_time
                result.home_id = home_id
                
                # Log success
                if result.is_success():
                    logger.debug(
                        f"✅ {self.service_name} enriched {home_name} "
                        f"(ID: {home_id}) in {result.processing_time:.2f}s"
                    )
                    self._request_count += 1
                else:
                    logger.warning(
                        f"⚠️ {self.service_name} partial enrichment for {home_name} "
                        f"(ID: {home_id}): {result.error}"
                    )
                
                return result
                
            except asyncio.TimeoutError:
                elapsed = time.time() - start_time
                logger.warning(
                    f"⏱️ {self.service_name} timeout for {home_name} "
                    f"(ID: {home_id}) after {elapsed:.2f}s"
                )
                self._error_count += 1
                return EnrichmentResult(
                    source=self.service_name,
                    status='timeout',
                    data={},
                    error=f'Timeout after {timeout}s',
                    processing_time=elapsed,
                    home_id=home_id
                )
                
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    f"❌ {self.service_name} error for {home_name} "
                    f"(ID: {home_id}): {str(e)}",
                    exc_info=True
                )
                self._error_count += 1
                return EnrichmentResult(
                    source=self.service_name,
                    status='failed',
                    data={},
                    error=str(e),
                    processing_time=elapsed,
                    home_id=home_id
                )
    
    def _handle_error(
        self,
        home_id: str,
        home_name: str,
        error: Exception,
        default_return: Any = None
    ) -> Optional[Dict[str, Any]]:
        """
        Unified error handling across all services.
        
        Args:
            home_id: Home identifier
            home_name: Home name for logging
            error: Exception that occurred
            default_return: Default value to return on error
        
        Returns:
            default_return or None
        """
        logger.error(
            f"{self.service_name} error for {home_name} (ID: {home_id}): {str(error)}",
            exc_info=True
        )
        self._error_count += 1
        return default_return
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        success_rate = (
            100 * (self._request_count / (self._request_count + self._error_count))
            if (self._request_count + self._error_count) > 0
            else 0
        )
        
        return {
            'service': self.service_name,
            'requests': self._request_count,
            'errors': self._error_count,
            'success_rate': f"{success_rate:.1f}%",
            'timeout': self.timeout_seconds
        }
    
    def reset_stats(self):
        """Reset service statistics"""
        self._request_count = 0
        self._error_count = 0


class EnrichmentServiceFactory:
    """Factory for creating enrichment services (for dependency injection)"""
    
    _services: Dict[str, BaseEnrichmentService] = {}
    
    @classmethod
    def register(cls, service_name: str, service: BaseEnrichmentService) -> None:
        """Register a service"""
        cls._services[service_name] = service
        logger.info(f"Registered enrichment service: {service_name}")
    
    @classmethod
    def get(cls, service_name: str) -> Optional[BaseEnrichmentService]:
        """Get a registered service"""
        return cls._services.get(service_name)
    
    @classmethod
    def get_all(cls) -> Dict[str, BaseEnrichmentService]:
        """Get all registered services"""
        return cls._services.copy()
    
    @classmethod
    def list_services(cls) -> List[str]:
        """List all registered service names"""
        return list(cls._services.keys())

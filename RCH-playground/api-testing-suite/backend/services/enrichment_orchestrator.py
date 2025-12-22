"""
Enrichment Orchestrator

Central hub for managing all enrichment services (Financial, Staff, FSA, Google, CQC).
Provides unified interface for batch enrichment with:
- Parallel processing with semaphore control
- Timeout management
- Error handling
- Caching support
- Progress tracking
- Service statistics
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict

from services.enrichment_service_base import BaseEnrichmentService, EnrichmentResult
from services.financial_enrichment_service import FinancialEnrichmentService
from services.staff_enrichment_service import StaffEnrichmentService
from services.fsa_enrichment_service import FSAEnrichmentService
from services.google_places_enrichment_service import GooglePlacesEnrichmentService

logger = logging.getLogger(__name__)


@dataclass
class EnrichmentConfig:
    """Configuration for enrichment pipeline"""
    
    enabled_sources: List[str] = None  # ['financial', 'staff', 'fsa', 'google']
    parallel_limit: int = 5            # Max concurrent requests per service
    timeout_per_source: int = 30       # Timeout for each service in seconds
    retry_failed: bool = False          # Retry failed enrichments (v2 feature)
    cache_results: bool = True         # Cache enrichment results
    
    def __post_init__(self):
        if self.enabled_sources is None:
            self.enabled_sources = ['financial', 'staff', 'fsa', 'google']


@dataclass
class EnrichmentBatch:
    """Result of batch enrichment operation"""
    
    total_homes: int
    total_enrichments: int
    successful: int
    failed: int
    partial: int
    timeout: int
    processing_time: float
    sources_used: List[str]
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class EnrichmentOrchestrator:
    """
    Central orchestrator for enrichment services.
    
    Manages:
    - Service initialization and registration
    - Batch enrichment with parallel processing
    - Result aggregation
    - Error tracking
    - Statistics and monitoring
    """
    
    def __init__(self):
        """Initialize orchestrator and register services"""
        self.services: Dict[str, BaseEnrichmentService] = {}
        self.cache: Dict[str, Dict[str, Any]] = {}  # home_id -> {source -> result}
        self.stats = {
            'batches_processed': 0,
            'total_homes': 0,
            'total_enrichments': 0,
            'successful': 0,
            'failed': 0,
            'total_time': 0.0
        }
        
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize and register all enrichment services"""
        try:
            self.services['financial'] = FinancialEnrichmentService()
            logger.info("✅ FinancialEnrichmentService registered")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize FinancialEnrichmentService: {e}")
        
        try:
            self.services['staff'] = StaffEnrichmentService()
            logger.info("✅ StaffEnrichmentService registered")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize StaffEnrichmentService: {e}")
        
        try:
            self.services['fsa'] = FSAEnrichmentService()
            logger.info("✅ FSAEnrichmentService registered")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize FSAEnrichmentService: {e}")
        
        try:
            import os
            google_api_key = os.getenv("GOOGLE_PLACES_API_KEY")
            if google_api_key:
                self.services['google'] = GooglePlacesEnrichmentService(api_key=google_api_key)
                logger.info("✅ GooglePlacesEnrichmentService registered")
            else:
                logger.warning("⚠️ GOOGLE_PLACES_API_KEY not set, skipping GooglePlacesEnrichmentService")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize GooglePlacesEnrichmentService: {e}")
    
    async def enrich_home(
        self,
        home: Dict[str, Any],
        config: EnrichmentConfig,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate enrichment of a single home.
        
        Args:
            home: Care home object
            config: Enrichment configuration
            context: Additional context (questionnaire, user_profile, etc.)
        
        Returns:
            {
                'home_id': str,
                'home': {base home data},
                'enrichments': {
                    'financial': {data} or None,
                    'staff': {data} or None,
                    'fsa': {data} or None,
                    'google': {data} or None
                },
                'metadata': {
                    'enrichment_time': float,
                    'sources_used': [str],
                    'sources_failed': [str],
                    'errors': [str]
                }
            }
        """
        home_id = home.get('cqc_location_id') or home.get('id')
        
        # Check cache
        if config.cache_results and home_id in self.cache:
            logger.debug(f"Cache hit for home {home_id}")
            return self.cache[home_id]
        
        enrichments = {}
        errors = []
        start_time = time.time()
        
        # Run enrichments in parallel with semaphore
        semaphore = asyncio.Semaphore(config.parallel_limit)
        tasks = []
        
        for source_name in config.enabled_sources:
            if source_name not in self.services:
                errors.append(f"Service not available: {source_name}")
                enrichments[source_name] = None
                continue
            
            service = self.services[source_name]
            
            # Get source-specific context
            source_context = self._get_source_context(
                source_name, home, context or {}
            )
            
            task = self._enrich_with_semaphore(
                semaphore, source_name, service, home,
                source_context, config.timeout_per_source
            )
            tasks.append(task)
        
        # Wait for all enrichments
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        sources_used = []
        sources_failed = []
        
        for source_name, result in zip(config.enabled_sources, results):
            if isinstance(result, Exception):
                errors.append(f"{source_name}: {str(result)}")
                enrichments[source_name] = None
                sources_failed.append(source_name)
            elif isinstance(result, EnrichmentResult):
                if result.is_success():
                    enrichments[source_name] = result.data
                    sources_used.append(source_name)
                elif result.status == 'timeout':
                    errors.append(f"{source_name}: {result.error}")
                    enrichments[source_name] = None
                    sources_failed.append(source_name)
                else:
                    logger.warning(f"{source_name} partial: {result.error}")
                    enrichments[source_name] = result.data  # Keep partial data
                    sources_used.append(source_name)
            else:
                errors.append(f"{source_name}: Unknown result type")
                enrichments[source_name] = None
                sources_failed.append(source_name)
        
        enrichment_time = time.time() - start_time
        
        result = {
            'home_id': home_id,
            'home': home,
            'enrichments': enrichments,
            'metadata': {
                'enrichment_time': round(enrichment_time, 2),
                'sources_used': sources_used,
                'sources_failed': sources_failed,
                'errors': errors
            }
        }
        
        # Cache result
        if config.cache_results:
            self.cache[home_id] = result
        
        return result
    
    async def enrich_homes_batch(
        self,
        homes: List[Dict[str, Any]],
        config: EnrichmentConfig,
        context: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> List[Dict[str, Any]]:
        """
        Batch enrich multiple homes.
        
        Args:
            homes: List of care home objects
            config: Enrichment configuration
            context: Additional context
            progress_callback: Optional callback for progress updates
                Receives (progress: float 0-100, message: str)
        
        Returns:
            List of enriched home dictionaries
        """
        if not homes:
            return []
        
        results = []
        batch_start = time.time()
        
        for i, home in enumerate(homes):
            result = await self.enrich_home(home, config, context)
            results.append(result)
            
            # Call progress callback
            if progress_callback:
                progress = ((i + 1) / len(homes)) * 100
                home_name = home.get('name', 'Unknown')
                message = f"Enriched {i + 1}/{len(homes)} homes: {home_name}"
                progress_callback(progress, message)
        
        # Update batch statistics
        batch_time = time.time() - batch_start
        successful = sum(1 for r in results if r['metadata']['errors'] == [])
        failed = sum(1 for r in results if r['metadata']['sources_failed'])
        
        batch_info = EnrichmentBatch(
            total_homes=len(homes),
            total_enrichments=len(homes) * len(config.enabled_sources),
            successful=successful,
            failed=failed,
            partial=len(homes) - successful - failed,
            timeout=sum(1 for r in results if any('timeout' in e for e in r['metadata']['errors'])),
            processing_time=batch_time,
            sources_used=config.enabled_sources
        )
        
        self.stats['batches_processed'] += 1
        self.stats['total_homes'] += len(homes)
        self.stats['successful'] += successful
        self.stats['failed'] += failed
        self.stats['total_time'] += batch_time
        
        logger.info(
            f"✅ Batch enrichment complete: {successful}/{len(homes)} successful "
            f"in {batch_time:.2f}s"
        )
        
        return results
    
    async def _enrich_with_semaphore(
        self,
        semaphore: asyncio.Semaphore,
        source_name: str,
        service: BaseEnrichmentService,
        home: Dict[str, Any],
        context: Dict[str, Any],
        timeout: int
    ) -> EnrichmentResult:
        """
        Enrich with semaphore control and timeout.
        
        Args:
            semaphore: Asyncio semaphore for concurrency control
            source_name: Name of enrichment source
            service: Enrichment service instance
            home: Care home object
            context: Service-specific context
            timeout: Timeout in seconds
        
        Returns:
            EnrichmentResult
        """
        async with semaphore:
            try:
                result = await asyncio.wait_for(
                    service.enrich(home, **context),
                    timeout=timeout
                )
                return result
            except asyncio.TimeoutError:
                logger.warning(f"⏱️ {source_name} enrichment timeout for {home.get('name')}")
                return EnrichmentResult(
                    source=source_name,
                    status='timeout',
                    data={},
                    error=f'Timeout after {timeout}s'
                )
            except Exception as e:
                logger.error(f"❌ {source_name} enrichment error: {str(e)}", exc_info=True)
                return EnrichmentResult(
                    source=source_name,
                    status='failed',
                    data={},
                    error=str(e)
                )
    
    def _get_source_context(
        self,
        source_name: str,
        home: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get source-specific context parameters.
        
        Args:
            source_name: Name of enrichment source
            home: Care home object
            context: Overall context
        
        Returns:
            Source-specific kwargs
        """
        if source_name == 'financial':
            return {
                'company_number': home.get('company_number'),
                'years': 3
            }
        elif source_name == 'staff':
            return {
                'use_perplexity': context.get('use_perplexity', True)
            }
        elif source_name == 'fsa':
            return {}
        elif source_name == 'google':
            return {}
        else:
            return {}
    
    def get_service(self, source_name: str) -> Optional[BaseEnrichmentService]:
        """Get a registered service"""
        return self.services.get(source_name)
    
    def list_services(self) -> List[str]:
        """List all registered service names"""
        return list(self.services.keys())
    
    def clear_cache(self):
        """Clear enrichment cache"""
        self.cache.clear()
        logger.info("Enrichment cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return {
            'orchestrator': {
                'batches_processed': self.stats['batches_processed'],
                'total_homes_enriched': self.stats['total_homes'],
                'successful': self.stats['successful'],
                'failed': self.stats['failed'],
                'total_time': round(self.stats['total_time'], 2),
                'avg_time_per_batch': (
                    round(self.stats['total_time'] / self.stats['batches_processed'], 2)
                    if self.stats['batches_processed'] > 0 else 0
                )
            },
            'services': {
                name: service.get_stats()
                for name, service in self.services.items()
            },
            'cache_size': len(self.cache)
        }
    
    def reset_stats(self):
        """Reset all statistics"""
        self.stats = {
            'batches_processed': 0,
            'total_homes': 0,
            'total_enrichments': 0,
            'successful': 0,
            'failed': 0,
            'total_time': 0.0
        }
        for service in self.services.values():
            service.reset_stats()
        logger.info("Statistics reset")

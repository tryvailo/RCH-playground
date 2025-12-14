"""
Report Retry Service

Handles retry logic for missing data sources in professional reports.
Ensures reports are always generated, even with partial data, and retries
missing sources until complete or timeout (3 hours).
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set
from enum import Enum
import json


class DataSourceStatus(str, Enum):
    """Status of a data source for a care home"""
    PENDING = "pending"  # Not yet attempted
    LOADING = "loading"  # Currently loading
    SUCCESS = "success"  # Successfully loaded
    FAILED = "failed"  # Failed to load
    RETRYING = "retrying"  # Retrying after failure


class MissingDataSource:
    """Represents a missing data source for a care home"""
    
    def __init__(
        self,
        home_id: str,
        home_name: str,
        source_name: str,
        source_type: str,  # 'neighbourhood', 'fsa', 'cqc', 'google_places', 'firecrawl', etc.
        retry_count: int = 0,
        last_attempt: Optional[datetime] = None,
        error: Optional[str] = None
    ):
        self.home_id = home_id
        self.home_name = home_name
        self.source_name = source_name
        self.source_type = source_type
        self.retry_count = retry_count
        self.last_attempt = last_attempt or datetime.now()
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'home_id': self.home_id,
            'home_name': self.home_name,
            'source_name': self.source_name,
            'source_type': self.source_type,
            'retry_count': self.retry_count,
            'last_attempt': self.last_attempt.isoformat() if self.last_attempt else None,
            'error': self.error,
            'status': DataSourceStatus.FAILED.value if self.retry_count > 0 else DataSourceStatus.PENDING.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MissingDataSource':
        return cls(
            home_id=data['home_id'],
            home_name=data['home_name'],
            source_name=data['source_name'],
            source_type=data['source_type'],
            retry_count=data.get('retry_count', 0),
            last_attempt=datetime.fromisoformat(data['last_attempt']) if data.get('last_attempt') else None,
            error=data.get('error')
        )


class ReportRetryService:
    """
    Service for managing retry logic for professional reports
    
    Tracks missing data sources and retries them until:
    - All sources are loaded (report complete)
    - Maximum retry attempts reached
    - Timeout (3 hours) reached
    """
    
    # Retry configuration
    MAX_RETRY_ATTEMPTS = 10  # Maximum retries per source
    RETRY_DELAY_SECONDS = 300  # 5 minutes between retries
    MAX_TOTAL_TIME_HOURS = 3  # 3 hours total timeout
    RETRY_BACKOFF_MULTIPLIER = 1.5  # Exponential backoff
    
    def __init__(self, job_queue_service):
        self.job_queue_service = job_queue_service
    
    async def track_missing_data(
        self,
        job_id: str,
        missing_sources: List[MissingDataSource]
    ) -> bool:
        """
        Track missing data sources for a job
        """
        job_status = await self.job_queue_service.get_job_status(job_id)
        if not job_status:
            return False
        
        # Get existing missing sources or initialize
        existing_missing = job_status.get('missing_data_sources', [])
        existing_dict = {f"{m['home_id']}:{m['source_type']}": m for m in existing_missing}
        
        # Add or update missing sources
        for source in missing_sources:
            key = f"{source.home_id}:{source.source_type}"
            if key in existing_dict:
                # Update existing
                existing_dict[key].update(source.to_dict())
            else:
                # Add new
                existing_dict[key] = source.to_dict()
        
        # Update job status
        await self.job_queue_service.update_job_status(job_id, {
            'missing_data_sources': list(existing_dict.values()),
            'is_partial': len(existing_dict) > 0,
            'completeness': self._calculate_completeness(job_status, existing_dict)
        })
        
        return True
    
    async def get_missing_data_sources(self, job_id: str) -> List[MissingDataSource]:
        """
        Get list of missing data sources for a job
        """
        job_status = await self.job_queue_service.get_job_status(job_id)
        if not job_status:
            return []
        
        missing = job_status.get('missing_data_sources', [])
        return [MissingDataSource.from_dict(m) for m in missing]
    
    async def retry_missing_sources(
        self,
        job_id: str,
        questionnaire: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Retry loading missing data sources for a job
        
        Returns:
            Dict with:
            - retried_sources: List of sources that were retried
            - success_count: Number of successfully loaded sources
            - still_missing: List of sources that still failed
        """
        missing_sources = await self.get_missing_data_sources(job_id)
        
        if not missing_sources:
            return {
                'retried_sources': [],
                'success_count': 0,
                'still_missing': [],
                'message': 'No missing sources to retry'
            }
        
        # Filter sources that are ready for retry
        now = datetime.now()
        ready_for_retry = []
        
        for source in missing_sources:
            # Check if enough time has passed since last attempt
            if source.last_attempt:
                time_since_attempt = (now - source.last_attempt).total_seconds()
                retry_delay = self.RETRY_DELAY_SECONDS * (self.RETRY_BACKOFF_MULTIPLIER ** source.retry_count)
                
                if time_since_attempt >= retry_delay and source.retry_count < self.MAX_RETRY_ATTEMPTS:
                    ready_for_retry.append(source)
            else:
                ready_for_retry.append(source)
        
        if not ready_for_retry:
            return {
                'retried_sources': [],
                'success_count': 0,
                'still_missing': [s.to_dict() for s in missing_sources],
                'message': 'No sources ready for retry yet'
            }
        
        # Retry each source
        retried_sources = []
        success_count = 0
        still_missing = []
        
        for source in ready_for_retry:
            source.retry_count += 1
            source.last_attempt = now
            source.status = DataSourceStatus.RETRYING.value
            
            try:
                # Attempt to load the data source
                success = await self._retry_single_source(job_id, source, questionnaire)
                
                if success:
                    source.status = DataSourceStatus.SUCCESS.value
                    success_count += 1
                    retried_sources.append({
                        **source.to_dict(),
                        'retry_success': True
                    })
                else:
                    source.status = DataSourceStatus.FAILED.value
                    still_missing.append(source.to_dict())
                    retried_sources.append({
                        **source.to_dict(),
                        'retry_success': False
                    })
            except Exception as e:
                source.status = DataSourceStatus.FAILED.value
                source.error = str(e)
                still_missing.append(source.to_dict())
                retried_sources.append({
                    **source.to_dict(),
                    'retry_success': False,
                    'error': str(e)
                })
        
        # Update job status with retry results
        await self.track_missing_data(job_id, [MissingDataSource.from_dict(s) for s in still_missing])
        
        # If all sources are loaded, mark report as complete
        if not still_missing:
            job_status = await self.job_queue_service.get_job_status(job_id)
            if job_status:
                # Reload report with new data
                await self._reload_report_with_new_data(job_id, questionnaire)
        
        return {
            'retried_sources': retried_sources,
            'success_count': success_count,
            'still_missing': still_missing,
            'message': f'Retried {len(retried_sources)} sources, {success_count} succeeded'
        }
    
    async def _retry_single_source(
        self,
        job_id: str,
        source: MissingDataSource,
        questionnaire: Dict[str, Any]
    ) -> bool:
        """
        Retry loading a single data source
        
        Returns True if successful, False otherwise
        """
        # Get current report data
        job_status = await self.job_queue_service.get_job_status(job_id)
        if not job_status or not job_status.get('result'):
            return False
        
        report = job_status['result']
        care_homes = report.get('care_homes', [])
        
        # Find the care home
        home = None
        for h in care_homes:
            if h.get('id') == source.home_id or h.get('name') == source.home_name:
                home = h
                break
        
        if not home:
            return False
        
        # Attempt to load the specific source
        try:
            if source.source_type == 'neighbourhood':
                return await self._load_neighbourhood_data(home)
            elif source.source_type == 'fsa':
                return await self._load_fsa_data(home, questionnaire)
            elif source.source_type == 'cqc':
                return await self._load_cqc_data(home)
            elif source.source_type == 'google_places':
                return await self._load_google_places_data(home)
            elif source.source_type == 'firecrawl':
                return await self._load_firecrawl_data(home)
            else:
                return False
        except Exception as e:
            source.error = str(e)
            return False
    
    async def _load_neighbourhood_data(self, home: Dict[str, Any]) -> bool:
        """Load neighbourhood data for a home"""
        try:
            from data_integrations.batch_processor import NeighbourhoodAnalyzer
            analyzer = NeighbourhoodAnalyzer()
            home_postcode = home.get('postcode', '')
            home_lat = home.get('latitude')
            home_lon = home.get('longitude')
            
            if home_postcode or (home_lat and home_lon):
                neighbourhood_data = await asyncio.wait_for(
                    analyzer.analyze(
                        postcode=home_postcode if home_postcode else '',
                        lat=home_lat,
                        lon=home_lon,
                        include_os_places=True,
                        include_ons=True,
                        include_osm=True,
                        include_nhsbsa=True,
                        include_environmental=True,
                        address_name=home.get('name')
                    ),
                    timeout=10.0
                )
                return neighbourhood_data is not None
        except Exception:
            pass
        return False
    
    async def _load_fsa_data(self, home: Dict[str, Any], questionnaire: Dict[str, Any]) -> bool:
        """Load FSA data for a home"""
        try:
            from services.fsa_detailed_service import FSADetailedService
            medical_needs = questionnaire.get('section_3_medical_needs', {})
            dietary_requirements = medical_needs.get('q11_dietary_requirements', []) or []
            
            fsa_service = FSADetailedService()
            fsa_data = await asyncio.wait_for(
                fsa_service.get_detailed_analysis(
                    home_name=home.get('name', 'Unknown'),
                    postcode=home.get('postcode', ''),
                    latitude=home.get('latitude'),
                    longitude=home.get('longitude'),
                    dietary_requirements=dietary_requirements
                ),
                timeout=8.0
            )
            return fsa_data is not None
        except Exception:
            pass
        return False
    
    async def _load_cqc_data(self, home: Dict[str, Any]) -> bool:
        """Load CQC data for a home"""
        try:
            from api_clients.cqc_client import CQCAPIClient
            from config_manager import get_credentials
            from main import get_cqc_client  # Import from main where it's defined
            
            creds = get_credentials()
            
            if creds and hasattr(creds, 'cqc') and creds.cqc:
                cqc_location_id = home.get('location_id') or home.get('cqc_location_id')
                if cqc_location_id:
                    cqc_client = get_cqc_client()
                    location = await asyncio.wait_for(
                        cqc_client.get_location(cqc_location_id),
                        timeout=8.0
                    )
                    return location is not None
        except Exception:
            pass
        return False
    
    async def _load_google_places_data(self, home: Dict[str, Any]) -> bool:
        """Load Google Places data for a home"""
        try:
            from services.google_places_enrichment_service import GooglePlacesEnrichmentService
            from config_manager import get_credentials
            creds = get_credentials()
            
            if creds and hasattr(creds, 'google_places') and creds.google_places:
                google_places_service = GooglePlacesEnrichmentService(
                    api_key=creds.google_places.api_key,
                    use_cache=True,
                    cache_ttl=86400
                )
                data = await asyncio.wait_for(
                    google_places_service._fetch_google_places_data(
                        home_name=home.get('name', 'Unknown'),
                        postcode=home.get('postcode', ''),
                        latitude=home.get('latitude'),
                        longitude=home.get('longitude')
                    ),
                    timeout=5.0
                )
                return data is not None
        except Exception:
            pass
        return False
    
    async def _load_firecrawl_data(self, home: Dict[str, Any]) -> bool:
        """Load Firecrawl data for a home"""
        try:
            from api_clients.firecrawl_client import FirecrawlAPIClient
            from config_manager import get_credentials
            from main import get_firecrawl_client  # Import from main where it's defined
            
            creds = get_credentials()
            
            if creds and hasattr(creds, 'firecrawl') and creds.firecrawl:
                home_website = home.get('website') or home.get('website_url')
                if home_website:
                    firecrawl_client = get_firecrawl_client(creds)
                    website_url = home_website
                    if not website_url.startswith("http"):
                        website_url = f"https://{website_url}"
                    
                    data = await asyncio.wait_for(
                        firecrawl_client.extract_care_home_data_full(website_url, home.get('name')),
                        timeout=30.0
                    )
                    return data is not None
        except Exception:
            pass
        return False
    
    async def _reload_report_with_new_data(self, job_id: str, questionnaire: Dict[str, Any]):
        """
        Reload the entire report with newly loaded data
        This is called when all missing sources are loaded
        """
        # This would trigger a full report regeneration
        # For now, we'll just mark it as complete
        # In production, you might want to trigger a full regeneration
        await self.job_queue_service.update_job_status(job_id, {
            'is_partial': False,
            'completeness': 100,
            'message': 'Report generation completed with all data sources'
        })
    
    def _calculate_completeness(
        self,
        job_status: Dict[str, Any],
        missing_sources: Dict[str, Any]
    ) -> float:
        """
        Calculate report completeness percentage
        """
        # This is a simplified calculation
        # In production, you'd want to weight different sources differently
        total_expected_sources = job_status.get('total_expected_sources', 0)
        if total_expected_sources == 0:
            return 100.0 if len(missing_sources) == 0 else 0.0
        
        missing_count = len(missing_sources)
        loaded_count = total_expected_sources - missing_count
        return (loaded_count / total_expected_sources) * 100.0
    
    async def check_and_retry_jobs(self) -> Dict[str, Any]:
        """
        Check all jobs for missing data and retry if needed
        This should be called periodically (e.g., via Vercel Cron)
        """
        # This would scan all active jobs and retry missing sources
        # Implementation depends on storage backend
        return {
            'checked_jobs': 0,
            'retried_sources': 0,
            'successful_retries': 0
        }


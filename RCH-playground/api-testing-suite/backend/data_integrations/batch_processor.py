"""
Batch Processor
Handles batch processing of care homes through all data integrations
"""
import asyncio
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
import logging

from .os_places_loader import OSPlacesLoader
from .ons_loader import ONSLoader
from .osm_loader import OSMLoader
from .nhsbsa_loader import NHSBSALoader
from .cache_manager import get_cache_manager

logger = logging.getLogger(__name__)


@dataclass
class BatchProgress:
    """Track batch processing progress"""
    total: int = 0
    completed: int = 0
    failed: int = 0
    current_item: str = ""
    started_at: Optional[datetime] = None
    errors: List[Dict[str, str]] = field(default_factory=list)
    
    @property
    def percent_complete(self) -> float:
        if self.total == 0:
            return 0
        return round((self.completed / self.total) * 100, 1)
    
    @property
    def elapsed_seconds(self) -> float:
        if not self.started_at:
            return 0
        return (datetime.now() - self.started_at).total_seconds()
    
    @property
    def items_per_second(self) -> float:
        elapsed = self.elapsed_seconds
        if elapsed == 0:
            return 0
        return round(self.completed / elapsed, 2)
    
    @property
    def estimated_remaining_seconds(self) -> float:
        if self.items_per_second == 0:
            return 0
        remaining = self.total - self.completed
        return round(remaining / self.items_per_second, 1)


class BatchProcessor:
    """
    Process multiple care homes through data integrations
    
    Features:
    - Concurrent processing with rate limiting
    - Progress tracking
    - Error handling and retry
    - Chunked processing for memory efficiency
    """
    
    def __init__(
        self,
        max_concurrent: int = 5,
        chunk_size: int = 100,
        retry_failed: bool = True,
        max_retries: int = 2
    ):
        """
        Initialize batch processor
        
        Args:
            max_concurrent: Max concurrent API calls
            chunk_size: Process in chunks of this size
            retry_failed: Whether to retry failed items
            max_retries: Max retry attempts
        """
        self.max_concurrent = max_concurrent
        self.chunk_size = chunk_size
        self.retry_failed = retry_failed
        self.max_retries = max_retries
        self.progress = BatchProgress()
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._progress_callback: Optional[Callable] = None
    
    def set_progress_callback(self, callback: Callable[[BatchProgress], None]):
        """Set callback for progress updates"""
        self._progress_callback = callback
    
    def _update_progress(self, item_name: str = "", success: bool = True, error: str = None):
        """Update progress and notify callback"""
        if success:
            self.progress.completed += 1
        else:
            self.progress.failed += 1
            if error:
                self.progress.errors.append({
                    'item': item_name,
                    'error': error,
                    'timestamp': datetime.now().isoformat()
                })
        
        self.progress.current_item = item_name
        
        if self._progress_callback:
            self._progress_callback(self.progress)
    
    async def process_care_homes(
        self,
        care_homes: List[Dict[str, Any]],
        include_os_places: bool = True,
        include_ons: bool = True,
        include_osm: bool = True,
        include_nhsbsa: bool = True
    ) -> Dict[str, Any]:
        """
        Process multiple care homes through all data integrations
        
        Args:
            care_homes: List of care home dicts with postcode, lat, lon
            include_*: Flags to include/exclude specific integrations
            
        Returns:
            Dict with results and statistics
        """
        self.progress = BatchProgress(
            total=len(care_homes),
            started_at=datetime.now()
        )
        
        results = []
        
        # Process in chunks for memory efficiency
        for i in range(0, len(care_homes), self.chunk_size):
            chunk = care_homes[i:i + self.chunk_size]
            
            # Process chunk concurrently
            chunk_tasks = [
                self._process_single_home(
                    home, 
                    include_os_places, 
                    include_ons, 
                    include_osm, 
                    include_nhsbsa
                )
                for home in chunk
            ]
            
            chunk_results = await asyncio.gather(*chunk_tasks, return_exceptions=True)
            
            for home, result in zip(chunk, chunk_results):
                if isinstance(result, Exception):
                    results.append({
                        'home': home,
                        'success': False,
                        'error': str(result)
                    })
                else:
                    results.append(result)
        
        return {
            'results': results,
            'statistics': {
                'total': self.progress.total,
                'completed': self.progress.completed,
                'failed': self.progress.failed,
                'success_rate': round((self.progress.completed / self.progress.total) * 100, 1) if self.progress.total > 0 else 0,
                'elapsed_seconds': self.progress.elapsed_seconds,
                'items_per_second': self.progress.items_per_second
            },
            'errors': self.progress.errors,
            'completed_at': datetime.now().isoformat()
        }
    
    async def _process_single_home(
        self,
        home: Dict[str, Any],
        include_os_places: bool,
        include_ons: bool,
        include_osm: bool,
        include_nhsbsa: bool
    ) -> Dict[str, Any]:
        """Process a single care home through all integrations"""
        async with self._semaphore:
            home_id = home.get('id', home.get('name', 'unknown'))
            postcode = home.get('postcode', '')
            lat = home.get('latitude') or home.get('lat')
            lon = home.get('longitude') or home.get('lon')
            
            result = {
                'home': home,
                'success': True,
                'data': {}
            }
            
            try:
                # OS Places - coordinate resolution
                if include_os_places and postcode and not (lat and lon):
                    try:
                        async with OSPlacesLoader() as loader:
                            coords = await loader.get_coordinates(postcode)
                            if coords:
                                result['data']['os_places'] = coords
                                lat = coords.get('latitude')
                                lon = coords.get('longitude')
                    except Exception as e:
                        result['data']['os_places_error'] = str(e)
                
                # ONS - area profile
                if include_ons and postcode:
                    try:
                        async with ONSLoader() as loader:
                            profile = await loader.get_full_area_profile(postcode)
                            result['data']['ons'] = {
                                'lsoa': profile.get('geography', {}).get('lsoa_code'),
                                'local_authority': profile.get('geography', {}).get('local_authority'),
                                'wellbeing_score': profile.get('wellbeing', {}).get('social_wellbeing_index', {}).get('score'),
                                'economic_score': profile.get('economic', {}).get('economic_stability_index', {}).get('score'),
                                'elderly_percent': profile.get('demographics', {}).get('elderly_care_context', {}).get('over_65_percent')
                            }
                    except Exception as e:
                        result['data']['ons_error'] = str(e)
                
                # OSM - walk score
                if include_osm and lat and lon:
                    try:
                        async with OSMLoader() as loader:
                            walk_score = await loader.calculate_walk_score(lat, lon)
                            result['data']['osm'] = {
                                'walk_score': walk_score.get('walk_score'),
                                'walk_rating': walk_score.get('rating'),
                                'care_home_relevance': walk_score.get('care_home_relevance', {}).get('score'),
                                'healthcare_access': walk_score.get('care_home_relevance', {}).get('healthcare_access')
                            }
                    except Exception as e:
                        result['data']['osm_error'] = str(e)
                
                # NHSBSA - health profile
                if include_nhsbsa and postcode:
                    try:
                        async with NHSBSALoader() as loader:
                            health_profile = await loader.get_area_health_profile(postcode, radius_km=5.0)
                            result['data']['nhsbsa'] = {
                                'health_index': health_profile.get('health_index', {}).get('score'),
                                'health_rating': health_profile.get('health_index', {}).get('rating'),
                                'practices_nearby': health_profile.get('practices_analyzed', 0),
                                'considerations_count': len(health_profile.get('care_home_considerations', []))
                            }
                    except Exception as e:
                        result['data']['nhsbsa_error'] = str(e)
                
                # Calculate composite score
                result['data']['composite_score'] = self._calculate_composite_score(result['data'])
                
                self._update_progress(home_id, success=True)
                
            except Exception as e:
                result['success'] = False
                result['error'] = str(e)
                self._update_progress(home_id, success=False, error=str(e))
            
            return result
    
    def _calculate_composite_score(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate composite neighbourhood score from all data sources"""
        scores = []
        weights = []
        
        # ONS Wellbeing (weight: 25%)
        ons_score = data.get('ons', {}).get('wellbeing_score')
        if ons_score is not None:
            scores.append(ons_score)
            weights.append(0.25)
        
        # OSM Walk Score (weight: 20%)
        osm_score = data.get('osm', {}).get('walk_score')
        if osm_score is not None:
            scores.append(osm_score)
            weights.append(0.20)
        
        # OSM Care Home Relevance (weight: 25%)
        care_relevance = data.get('osm', {}).get('care_home_relevance')
        if care_relevance is not None:
            scores.append(care_relevance)
            weights.append(0.25)
        
        # NHSBSA Health Index (weight: 30%)
        health_score = data.get('nhsbsa', {}).get('health_index')
        if health_score is not None:
            scores.append(health_score)
            weights.append(0.30)
        
        if not scores:
            return {'score': None, 'rating': 'Insufficient Data', 'components': 0}
        
        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        # Calculate weighted average
        composite = sum(s * w for s, w in zip(scores, normalized_weights))
        
        # Determine rating
        if composite >= 75:
            rating = 'Excellent'
        elif composite >= 60:
            rating = 'Good'
        elif composite >= 45:
            rating = 'Average'
        elif composite >= 30:
            rating = 'Below Average'
        else:
            rating = 'Poor'
        
        return {
            'score': round(composite, 1),
            'rating': rating,
            'components': len(scores),
            'confidence': 'High' if len(scores) >= 3 else 'Medium' if len(scores) >= 2 else 'Low'
        }
    
    async def enrich_care_home(self, care_home: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a single care home with all neighbourhood data
        
        Convenience method for processing one home
        """
        results = await self.process_care_homes(
            [care_home],
            include_os_places=True,
            include_ons=True,
            include_osm=True,
            include_nhsbsa=True
        )
        
        if results['results']:
            return results['results'][0]
        return {'success': False, 'error': 'No results'}


class NeighbourhoodAnalyzer:
    """
    High-level analyzer combining all data sources
    
    Provides unified neighbourhood analysis for care homes
    """
    
    def __init__(self):
        self.cache = get_cache_manager()
    
    async def analyze(
        self,
        postcode: str,
        lat: float = None,
        lon: float = None,
        include_os_places: bool = True,
        include_ons: bool = True,
        include_osm: bool = True,
        include_nhsbsa: bool = True,
        include_environmental: bool = False,
        address_name: str = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive neighbourhood analysis
        
        Args:
            postcode: UK postcode
            lat: Optional latitude (will resolve from postcode if not provided)
            lon: Optional longitude
            include_os_places: Include OS Places data (coordinates, UPRN, address)
            include_ons: Include ONS data (wellbeing, economics, demographics)
            include_osm: Include OpenStreetMap data (walk score, amenities)
            include_nhsbsa: Include NHSBSA data (health profile, GP access)
            
        Returns:
            Comprehensive neighbourhood analysis
        """
        # Build cache key including source selection, coordinates, and address_name
        # This ensures care home selections with specific coordinates get different cache entries
        sources = []
        if include_os_places: sources.append('os')
        if include_ons: sources.append('ons')
        if include_osm: sources.append('osm')
        if include_nhsbsa: sources.append('nhs')
        coord_part = f"_{lat}_{lon}" if (lat and lon) else ""
        address_part = f"_{address_name}" if address_name else ""
        cache_key = f"analysis_{postcode}_{'_'.join(sources)}{coord_part}{address_part}"
        
        cached = self.cache.get('neighbourhood', cache_key)
        if cached:
            return cached
        
        result = {
            'postcode': postcode,
            'analyzed_at': datetime.now().isoformat(),
            'errors': {}
        }
        
        # Get coordinates if not provided (always needed for OSM and other sources)
        # Coordinates are required for:
        # - OSM (OpenStreetMap) - requires lat/lon for walk score and amenities
        # - NHSBSA - uses coordinates internally for proximity matching
        # - OS Places - can provide coordinates from postcode
        
        # If coordinates not provided, we need to get them from available sources
        # Priority: ONS (if included) > OS Places (always try if needed) > Error
        
        if not (lat and lon):
            # Try ONS first (if included) as it often has coordinates
            if include_ons:
                async with ONSLoader() as loader:
                    try:
                        ons_profile = await loader.get_full_area_profile(postcode)
                        result['ons'] = ons_profile
                        # Try to get coordinates from ONS geography
                        if ons_profile.get('geography'):
                            geo = ons_profile['geography']
                            if geo.get('latitude') and geo.get('longitude'):
                                lat = geo['latitude']
                                lon = geo['longitude']
                                result['coordinates'] = {
                                    'latitude': lat,
                                    'longitude': lon
                                }
                    except Exception as e:
                        result['errors']['ons'] = str(e)
            
            # If still no coordinates, try OS Places (even if not explicitly included)
            # This is needed for OSM and NHSBSA which require coordinates
            if not (lat and lon) and (include_osm or include_nhsbsa or include_os_places):
                async with OSPlacesLoader() as loader:
                    try:
                        coords = await loader.get_coordinates(postcode)
                        if coords and coords.get('latitude') and coords.get('longitude'):
                            lat = coords['latitude']
                            lon = coords['longitude']
                            result['coordinates'] = coords
                        else:
                            # OS Places couldn't resolve coordinates
                            coord_error = 'Could not resolve postcode to coordinates'
                            if include_osm or include_nhsbsa:
                                if include_osm and include_nhsbsa:
                                    coord_error += '. Both OSM and NHSBSA require coordinates.'
                                elif include_osm:
                                    coord_error += '. OSM analysis requires latitude and longitude.'
                                elif include_nhsbsa:
                                    coord_error += '. NHSBSA analysis requires coordinates for proximity matching.'
                                result['errors']['coordinates'] = coord_error
                    except Exception as e:
                        error_key = 'os_places' if include_os_places else 'coordinates'
                        error_msg = str(e)
                        coord_error = f'Could not get coordinates: {error_msg}'
                        if include_osm or include_nhsbsa:
                            if include_osm and include_nhsbsa:
                                coord_error += '. Both OSM and NHSBSA require coordinates.'
                            elif include_osm:
                                coord_error += '. OSM analysis requires latitude and longitude.'
                            elif include_nhsbsa:
                                coord_error += '. NHSBSA analysis requires coordinates.'
                        result['errors'][error_key] = coord_error
        else:
            result['coordinates'] = {'latitude': lat, 'longitude': lon}
        
        # OS Places Data (if not already loaded)
        if include_os_places and not result.get('os_places'):
            async with OSPlacesLoader() as loader:
                try:
                    # If we have specific coordinates (e.g., from care home selection),
                    # create a single address result instead of getting all addresses in postcode area
                    if lat and lon:
                        # Create a single address result from coordinates
                        # This ensures we get the specific location, not all addresses in the postcode
                        os_places_result = loader.create_address_from_coordinates(
                            postcode=postcode,
                            latitude=lat,
                            longitude=lon,
                            address_name=address_name  # Use care home name if provided
                        )
                        result['os_places'] = os_places_result
                    else:
                        # Normal postcode lookup - get all addresses in postcode area
                        os_places_result = await loader.get_address_by_postcode(postcode)
                        result['os_places'] = os_places_result
                        # If coordinates not set yet, try to get from OS Places result
                        if not (lat and lon) and os_places_result.get('centroid'):
                            lat = os_places_result['centroid']['latitude']
                            lon = os_places_result['centroid']['longitude']
                            result['coordinates'] = os_places_result['centroid']
                except Exception as e:
                    result['errors']['os_places'] = str(e)
        
        # ONS Data (if not already loaded)
        if include_ons and not result.get('ons'):
            async with ONSLoader() as loader:
                try:
                    ons_profile = await loader.get_full_area_profile(postcode)
                    result['ons'] = ons_profile
                    # If coordinates not set yet, try to get from ONS geography
                    if not (lat and lon) and ons_profile.get('geography'):
                        geo = ons_profile['geography']
                        if geo.get('latitude') and geo.get('longitude'):
                            lat = geo['latitude']
                            lon = geo['longitude']
                            result['coordinates'] = {
                                'latitude': lat,
                                'longitude': lon
                            }
                except Exception as e:
                    result['errors']['ons'] = str(e)
        
        # Walk Score and Amenities (OSM)
        if include_osm:
            if lat and lon:
                async with OSMLoader() as loader:
                    try:
                        walk_score = await loader.calculate_walk_score(lat, lon)
                        amenities = await loader.get_nearby_amenities(lat, lon, radius_m=1600)
                        infrastructure = await loader.get_infrastructure_report(lat, lon)
                        
                        result['osm'] = {
                            'walk_score': walk_score,
                            'amenities': amenities,
                            'infrastructure': infrastructure
                        }
                    except Exception as e:
                        result['errors']['osm'] = str(e)
            else:
                # Coordinates not available for OSM
                # This should rarely happen now as we try to get coordinates from OS Places or ONS
                # But if it does, provide helpful error message
                if 'coordinates' in result['errors']:
                    # Don't duplicate the error - coordinates error already explains the issue
                    result['errors']['osm'] = 'OSM analysis requires coordinates. See coordinates error above.'
                elif 'os_places' in result['errors'] and 'coordinates' in result['errors']['os_places']:
                    result['errors']['osm'] = 'OSM analysis requires coordinates. See os_places error above.'
                else:
                    result['errors']['osm'] = 'Coordinates not available. OSM analysis requires latitude and longitude. The system attempted to resolve coordinates from OS Places or ONS but failed. Please ensure at least one of these data sources is available, or provide coordinates directly.'
        
        # Environmental Analysis (Noise & Pollution)
        # Wrapped in try-except to ensure it never breaks the entire request
        if include_environmental and lat and lon:
            try:
                from .environmental_analyzer import EnvironmentalAnalyzer
                async with EnvironmentalAnalyzer() as env_analyzer:
                    try:
                        # Use shorter timeout to prevent hanging
                        environmental = await asyncio.wait_for(
                            env_analyzer.analyze_environmental(lat, lon, radius_m=500),
                            timeout=15.0  # 15 second timeout (reduced from 30)
                        )
                        result['environmental'] = environmental
                    except asyncio.TimeoutError:
                        logger.warning(f"Environmental analysis timed out for {postcode}")
                        result['errors']['environmental'] = 'Environmental analysis timed out'
                    except Exception as e:
                        logger.warning(f"Environmental analysis error for {postcode}: {e}")
                        result['errors']['environmental'] = str(e)
            except ImportError as e:
                logger.warning(f"EnvironmentalAnalyzer not available: {e}")
                result['errors']['environmental'] = 'Environmental analysis not available'
            except Exception as e:
                logger.warning(f"Failed to initialize EnvironmentalAnalyzer for {postcode}: {e}")
                result['errors']['environmental'] = f"Initialization failed: {str(e)}"
        
        # Health Profile (NHSBSA)
        if include_nhsbsa:
            async with NHSBSALoader() as loader:
                try:
                    health_profile = await loader.get_area_health_profile(postcode, radius_km=5.0)
                    result['nhsbsa'] = health_profile
                except Exception as e:
                    result['errors']['nhsbsa'] = str(e)
        
        # Calculate overall score
        result['overall'] = self._calculate_overall_score(result)
        
        # Cache result
        self.cache.set('neighbourhood', cache_key, result)
        
        return result
    
    def _calculate_overall_score(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall neighbourhood score from available data sources"""
        scores = []
        
        # ONS Wellbeing (Social Wellbeing Index)
        ons = data.get('ons', {})
        if ons:
            wellbeing = ons.get('wellbeing', {}).get('social_wellbeing_index', {})
            if wellbeing and wellbeing.get('score') is not None:
                scores.append(('Social Wellbeing', wellbeing['score'], 0.25))
        
        # OSM Walkability
        osm = data.get('osm', {})
        if osm:
            walk_score = osm.get('walk_score', {})
            if walk_score and walk_score.get('walk_score') is not None:
                scores.append(('Walkability', walk_score['walk_score'], 0.20))
            
            # Care Home Relevance from walk score
            care_home_relevance = walk_score.get('care_home_relevance', {})
            if care_home_relevance and care_home_relevance.get('score') is not None:
                scores.append(('Care Home Suitability', care_home_relevance['score'], 0.25))
        
        # NHSBSA Health Index
        nhsbsa = data.get('nhsbsa', {})
        if nhsbsa:
            health_index = nhsbsa.get('health_index', {})
            if health_index and health_index.get('score') is not None:
                scores.append(('Area Health', health_index['score'], 0.30))
        
        if not scores:
            return {
                'score': None, 
                'rating': 'Insufficient Data',
                'confidence': 'low',
                'breakdown': []
            }
        
        # Normalize and calculate
        total_weight = sum(w for _, _, w in scores)
        if total_weight == 0:
            return {
                'score': None,
                'rating': 'Insufficient Data',
                'confidence': 'low',
                'breakdown': []
            }
        
        weighted = sum((s * w) / total_weight for _, s, w in scores)
        
        # Determine confidence based on number of sources
        source_count = len(scores)
        if source_count >= 3:
            confidence = 'high'
        elif source_count == 2:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        if weighted >= 75:
            rating = 'Excellent Neighbourhood'
        elif weighted >= 60:
            rating = 'Good Neighbourhood'
        elif weighted >= 45:
            rating = 'Average Neighbourhood'
        else:
            rating = 'Below Average Neighbourhood'
        
        return {
            'score': round(weighted, 1),
            'rating': rating,
            'confidence': confidence,
            'breakdown': [{'name': n, 'score': s, 'weight': f"{int((w/total_weight)*100)}%"} for n, s, w in scores]
        }

"""
Report Data Loader

Loads and prepares care home data for professional report generation.
Handles:
- Location resolution (postcode to coordinates)
- Care home loading from multiple sources
- Distance calculation
- Fallback mechanisms

Extracted from report_routes.py lines 144-382
"""

import asyncio
import logging
from typing import Dict, List, Any, Tuple, Optional
import httpx
import math

logger = logging.getLogger(__name__)


class ReportDataLoader:
    """Load and prepare data for report generation"""
    
    async def resolve_user_location(
        self,
        questionnaire: Dict[str, Any]
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Resolve user location to coordinates from postcode or city.
        
        Args:
            questionnaire: User questionnaire
        
        Returns:
            (latitude, longitude) or (None, None)
        """
        location_budget = questionnaire.get('section_2_location_budget', {})
        postcode = location_budget.get('q4_postcode', '')
        preferred_city = location_budget.get('q5_preferred_city', '')
        
        user_lat, user_lon = None, None
        
        # Try postcode first
        if postcode:
            logger.info(f"Resolving postcode: {postcode}")
            try:
                from postcode_resolver import PostcodeResolver
                resolver = PostcodeResolver()
                coords = resolver.resolve_postcode(postcode)
                if coords:
                    user_lat, user_lon = coords
                    logger.info(f"✅ Postcode resolved: ({user_lat}, {user_lon})")
            except Exception as e:
                logger.warning(f"Postcode resolution failed: {e}")
        
        # Fallback to city geocoding
        if not user_lat or not user_lon:
            if preferred_city:
                logger.info(f"Geocoding city: {preferred_city}")
                try:
                    lat, lon = await self._geocode_city(preferred_city)
                    if lat and lon:
                        user_lat, user_lon = lat, lon
                        logger.info(f"✅ City geocoded: ({user_lat}, {user_lon})")
                except Exception as e:
                    logger.warning(f"City geocoding failed: {e}")
        
        if not user_lat or not user_lon:
            logger.warning("Could not resolve user location")
        
        return user_lat, user_lon
    
    async def _geocode_city(self, city_name: str) -> Tuple[Optional[float], Optional[float]]:
        """Geocode city using OpenStreetMap Nominatim"""
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': f"{city_name}, UK",
            'format': 'json',
            'limit': 1
        }
        headers = {'User-Agent': 'CareHomeMatchingService/1.0'}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data:
                    lat = float(data[0]['lat'])
                    lon = float(data[0]['lon'])
                    return lat, lon
        
        return None, None
    
    async def load_homes(
        self,
        questionnaire: Dict[str, Any],
        normalized_city: Optional[str],
        care_type: Optional[str],
        max_distance_km: Optional[float],
        user_lat: Optional[float],
        user_lon: Optional[float]
    ) -> List[Dict[str, Any]]:
        """
        Load care homes from database with fallback mechanisms.
        
        Args:
            questionnaire: User questionnaire
            normalized_city: Normalized city name
            care_type: Type of care ('nursing', 'residential', 'dementia')
            max_distance_km: Maximum distance
            user_lat, user_lon: User coordinates
        
        Returns:
            List of care home objects
        """
        care_homes = []
        
        # Try CSV/hybrid first
        try:
            from services.csv_care_homes_service import get_care_homes
            
            logger.info("Loading homes from CSV/hybrid...")
            care_homes = await asyncio.to_thread(
                get_care_homes,
                local_authority=normalized_city,
                care_type=care_type,
                max_distance_km=max_distance_km,
                user_lat=user_lat,
                user_lon=user_lon,
                limit=50,
                use_hybrid=True
            )
            logger.info(f"✅ Loaded {len(care_homes)} homes from CSV/hybrid")
        except Exception as e:
            logger.warning(f"CSV loading failed: {e}")
        
        # Fallback to AsyncDataLoader
        if not care_homes or len(care_homes) == 0:
            try:
                from services.async_data_loader import get_async_loader
                
                logger.info("Falling back to AsyncDataLoader...")
                loader = get_async_loader()
                
                care_homes, loader_lat, loader_lon = await loader.load_initial_data(
                    preferred_city=normalized_city,
                    care_type=care_type,
                    max_distance_km=max_distance_km,
                    postcode=questionnaire.get('section_2_location_budget', {}).get('q4_postcode'),
                    limit=20
                )
                
                logger.info(f"✅ AsyncDataLoader returned {len(care_homes)} homes")
            except Exception as e:
                logger.warning(f"AsyncDataLoader failed: {e}")
        
        # Final fallback to mock data
        if not care_homes or len(care_homes) == 0:
            try:
                from services.mock_care_homes import load_mock_care_homes
                
                logger.info("Falling back to mock data...")
                all_mock = await asyncio.to_thread(load_mock_care_homes)
                
                if all_mock:
                    care_homes = all_mock[:20]
                    logger.info(f"✅ Loaded {len(care_homes)} mock homes")
            except Exception as e:
                logger.error(f"Mock data loading failed: {e}")
        
        return care_homes
    
    async def calculate_distances(
        self,
        homes: List[Dict[str, Any]],
        user_lat: float,
        user_lon: float
    ) -> List[Dict[str, Any]]:
        """
        Calculate distance_km for all homes.
        
        Args:
            homes: List of care homes
            user_lat, user_lon: User coordinates
        
        Returns:
            Homes with distance_km calculated
        """
        if not homes or not user_lat or not user_lon:
            return homes
        
        try:
            from utils.geo import calculate_distance_km, validate_coordinates
        except ImportError:
            def calculate_distance_km(lat1, lon1, lat2, lon2):
                R = 6371.0
                try:
                    dlat = math.radians(float(lat2) - float(lat1))
                    dlon = math.radians(float(lon2) - float(lon1))
                    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(float(lat1))) * \
                        math.cos(math.radians(float(lat2))) * math.sin(dlon / 2) ** 2
                    c = 2 * math.asin(math.sqrt(a))
                    return R * c
                except (ValueError, TypeError):
                    return 9999.0
            
            def validate_coordinates(lat, lon):
                return -90 <= lat <= 90 and -180 <= lon <= 180
        
        calculated_count = 0
        
        for home in homes:
            if home.get('distance_km') and home.get('distance_km') < 999:
                continue
            
            lat = home.get('latitude')
            lon = home.get('longitude')
            
            if lat and lon:
                try:
                    lat_float = float(lat)
                    lon_float = float(lon)
                    
                    if validate_coordinates(lat_float, lon_float) and lat_float != 0 and lon_float != 0:
                        distance = calculate_distance_km(user_lat, user_lon, lat_float, lon_float)
                        home['distance_km'] = round(distance, 2)
                        calculated_count += 1
                    else:
                        home['distance_km'] = 9999.0
                except (ValueError, TypeError):
                    home['distance_km'] = 9999.0
            else:
                home['distance_km'] = 9999.0
        
        logger.info(f"✅ Calculated distances for {calculated_count}/{len(homes)} homes")
        return homes

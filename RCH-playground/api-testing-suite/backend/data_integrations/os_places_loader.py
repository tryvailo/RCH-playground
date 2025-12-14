"""
OS Places API Loader
Provides access to Ordnance Survey Places API (AddressBase Premium)

API Documentation: https://osdatahub.os.uk/docs/places/overview
"""
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
from pathlib import Path

from .cache_manager import get_cache_manager


class OSPlacesLoader:
    """
    OS Places API Client
    
    Provides:
    - Postcode to coordinates conversion
    - Address details lookup
    - UPRN (Unique Property Reference Number) retrieval
    - Batch address processing
    """
    
    BASE_URL = "https://api.os.uk/search/places/v1"
    FEATURES_URL = "https://api.os.uk/features/v1/wfs"
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """
        Initialize OS Places loader
        
        Args:
            api_key: OS Data Hub API key (optional, loads from config if not provided)
            api_secret: OS Data Hub API secret (optional)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = self.BASE_URL  # Default, can be overridden from config
        
        # Load from config if not provided
        if not self.api_key:
            self._load_from_config()
        
        self.cache = get_cache_manager()
        self.client = httpx.AsyncClient(timeout=30.0)
    
    def _load_from_config(self):
        """Load API credentials and endpoint from config.json"""
        try:
            config_path = Path(__file__).parent.parent / "config.json"
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                    os_config = config.get('os_places', {})
                    self.api_key = os_config.get('api_key')
                    self.api_secret = os_config.get('api_secret')
                    # Use custom endpoint if provided, otherwise use default
                    if os_config.get('places_endpoint'):
                        # Remove trailing slash if present
                        self.base_url = os_config.get('places_endpoint').rstrip('/')
        except Exception as e:
            print(f"Failed to load OS Places config: {e}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers"""
        return {
            "Accept": "application/json"
        }
    
    def _add_api_key_to_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add API key to query parameters (new endpoint format)"""
        if self.api_key:
            params['key'] = self.api_key
        return params
    
    async def get_address_by_postcode(
        self, 
        postcode: str,
        max_results: int = 100
    ) -> Dict[str, Any]:
        """
        Get addresses for a postcode
        
        Args:
            postcode: UK postcode (e.g., "B1 1BB")
            max_results: Maximum number of results to return
            
        Returns:
            Dict with addresses and metadata
        """
        # Normalize postcode
        postcode = postcode.upper().strip().replace(" ", "")
        
        # Check cache first
        cached = self.cache.get('os_places', postcode, endpoint='postcode')
        if cached:
            return cached
        
        if not self.api_key:
            return {
                'error': 'OS Places API key not configured',
                'postcode': postcode,
                'address_count': 0,
                'addresses': [],
                'centroid': None,
                'fetched_at': datetime.now().isoformat()
            }
        
        try:
            url = f"{self.base_url}/postcode"
            params = {
                "postcode": postcode,
                "maxresults": max_results,
                "output_srs": "EPSG:4326"  # WGS84 for lat/lon
            }
            # Add API key to query parameters (new endpoint format)
            params = self._add_api_key_to_params(params)
            
            response = await self.client.get(
                url,
                params=params,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                result = self._parse_postcode_response(data, postcode)
                
                # Cache successful response
                self.cache.set('os_places', postcode, result, endpoint='postcode')
                
                return result
            elif response.status_code == 401:
                return {
                    'error': 'Invalid API key',
                    'postcode': postcode,
                    'address_count': 0,
                    'addresses': [],
                    'centroid': None,
                    'fetched_at': datetime.now().isoformat()
                }
            elif response.status_code == 404:
                return {
                    'error': 'Postcode not found',
                    'postcode': postcode,
                    'address_count': 0,
                    'addresses': [],
                    'centroid': None,
                    'fetched_at': datetime.now().isoformat()
                }
            else:
                return {
                    'error': f'API error: {response.status_code}',
                    'postcode': postcode,
                    'address_count': 0,
                    'addresses': [],
                    'centroid': None,
                    'fetched_at': datetime.now().isoformat(),
                    'raw_error': response.text
                }
                
        except Exception as e:
            return {
                'error': str(e),
                'postcode': postcode,
                'address_count': 0,
                'addresses': [],
                'centroid': None,
                'fetched_at': datetime.now().isoformat()
            }
    
    def _parse_postcode_response(self, data: Dict[str, Any], postcode: str) -> Dict[str, Any]:
        """Parse OS Places API postcode response"""
        results = data.get('results', [])
        
        addresses = []
        for result in results:
            dpa = result.get('DPA', {})
            
            # Extract coordinates
            lat = dpa.get('LAT') or dpa.get('LATITUDE')
            lon = dpa.get('LNG') or dpa.get('LONGITUDE')
            
            address = {
                'uprn': dpa.get('UPRN'),
                'address': dpa.get('ADDRESS'),
                'building_name': dpa.get('BUILDING_NAME'),
                'building_number': dpa.get('BUILDING_NUMBER'),
                'street': dpa.get('THOROUGHFARE_NAME') or dpa.get('DEPENDENT_THOROUGHFARE_NAME'),
                'locality': dpa.get('DEPENDENT_LOCALITY'),
                'town': dpa.get('POST_TOWN'),
                'postcode': dpa.get('POSTCODE'),
                'country': dpa.get('COUNTRY_CODE'),
                'latitude': float(lat) if lat else None,
                'longitude': float(lon) if lon else None,
                'x_coordinate': dpa.get('X_COORDINATE'),
                'y_coordinate': dpa.get('Y_COORDINATE'),
                'classification_code': dpa.get('CLASSIFICATION_CODE'),
                'classification_description': dpa.get('CLASSIFICATION_CODE_DESCRIPTION'),
                'local_authority': dpa.get('LOCAL_CUSTODIAN_CODE_DESCRIPTION')
            }
            addresses.append(address)
        
        # Get centroid coordinates from first result
        centroid = None
        if addresses and addresses[0].get('latitude'):
            centroid = {
                'latitude': addresses[0]['latitude'],
                'longitude': addresses[0]['longitude']
            }
        
        return {
            'postcode': postcode,
            'address_count': len(addresses),
            'addresses': addresses,
            'centroid': centroid,
            'header': data.get('header', {}),
            'fetched_at': datetime.now().isoformat()
        }
    
    async def get_coordinates(self, postcode: str) -> Optional[Dict[str, float]]:
        """
        Get coordinates for a postcode (simplified method)
        
        Args:
            postcode: UK postcode
            
        Returns:
            Dict with latitude and longitude, or None
        """
        result = await self.get_address_by_postcode(postcode, max_results=1)
        
        if result.get('centroid'):
            return result['centroid']
        
        if result.get('addresses') and len(result['addresses']) > 0:
            first = result['addresses'][0]
            if first.get('latitude') and first.get('longitude'):
                return {
                    'latitude': first['latitude'],
                    'longitude': first['longitude']
                }
        
        return None
    
    def create_address_from_coordinates(
        self,
        postcode: str,
        latitude: float,
        longitude: float,
        address_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a single address result from coordinates (for care homes with known location)
        
        Args:
            postcode: UK postcode
            latitude: Latitude
            longitude: Longitude
            address_name: Optional address name/description
            
        Returns:
            OS Places result structure with single address
        """
        address = {
            'latitude': latitude,
            'longitude': longitude,
            'postcode': postcode.upper().strip(),
            'address': address_name or f"Location at {postcode}",
            'uprn': None,  # UPRN not available when using coordinates directly
            'building_name': address_name,
            'building_number': None,
            'thoroughfare': None,
            'post_town': None,
            'local_authority': None
        }
        
        return {
            'postcode': postcode.upper().strip(),
            'address_count': 1,
            'addresses': [address],
            'centroid': {
                'latitude': latitude,
                'longitude': longitude
            },
            'fetched_at': datetime.now().isoformat(),
            'source': 'coordinates'  # Indicate this was created from coordinates
        }
    
    async def get_uprn(self, postcode: str, building_name_or_number: Optional[str] = None) -> Optional[str]:
        """
        Get UPRN for an address
        
        Args:
            postcode: UK postcode
            building_name_or_number: Optional building identifier to match
            
        Returns:
            UPRN string or None
        """
        result = await self.get_address_by_postcode(postcode)
        
        if not result.get('addresses'):
            return None
        
        if building_name_or_number:
            # Try to match building
            building_lower = building_name_or_number.lower()
            for addr in result['addresses']:
                building_name = (addr.get('building_name') or '').lower()
                building_num = str(addr.get('building_number') or '').lower()
                if building_lower in building_name or building_lower == building_num:
                    return addr.get('uprn')
        
        # Return first UPRN if no specific match
        return result['addresses'][0].get('uprn')
    
    async def search_address(
        self, 
        query: str,
        max_results: int = 25
    ) -> Dict[str, Any]:
        """
        Free-text address search
        
        Args:
            query: Address search query
            max_results: Maximum results
            
        Returns:
            Search results
        """
        # Check cache
        cache_key = query.lower().replace(" ", "_")[:50]
        cached = self.cache.get('os_places', cache_key, endpoint='find')
        if cached:
            return cached
        
        if not self.api_key:
            return {
                'error': 'OS Places API key not configured',
                'query': query,
                'results': []
            }
        
        try:
            url = f"{self.base_url}/find"
            params = {
                "query": query,
                "maxresults": max_results,
                "output_srs": "EPSG:4326"
            }
            # Add API key to query parameters (new endpoint format)
            params = self._add_api_key_to_params(params)
            
            response = await self.client.get(
                url,
                params=params,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    'query': query,
                    'results': self._parse_search_results(data),
                    'total_results': data.get('header', {}).get('totalresults', 0),
                    'fetched_at': datetime.now().isoformat()
                }
                
                self.cache.set('os_places', cache_key, result, endpoint='find')
                return result
            else:
                return {
                    'error': f'API error: {response.status_code}',
                    'query': query,
                    'results': []
                }
                
        except Exception as e:
            return {
                'error': str(e),
                'query': query,
                'results': []
            }
    
    def _parse_search_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse search results"""
        results = []
        for result in data.get('results', []):
            dpa = result.get('DPA', {})
            results.append({
                'uprn': dpa.get('UPRN'),
                'address': dpa.get('ADDRESS'),
                'postcode': dpa.get('POSTCODE'),
                'town': dpa.get('POST_TOWN'),
                'latitude': dpa.get('LAT'),
                'longitude': dpa.get('LNG'),
                'match_score': result.get('MATCH')
            })
        return results
    
    async def batch_get_coordinates(
        self, 
        postcodes: List[str]
    ) -> Dict[str, Optional[Dict[str, float]]]:
        """
        Get coordinates for multiple postcodes
        
        Args:
            postcodes: List of postcodes
            
        Returns:
            Dict mapping postcode to coordinates
        """
        results = {}
        
        for postcode in postcodes:
            coords = await self.get_coordinates(postcode)
            results[postcode] = coords
        
        return results
    
    async def get_address_details(self, uprn: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed address information by UPRN
        
        Args:
            uprn: Unique Property Reference Number
            
        Returns:
            Address details or None
        """
        # Check cache
        cached = self.cache.get('os_places', uprn, endpoint='uprn')
        if cached:
            return cached
        
        if not self.api_key:
            return None
        
        try:
            url = f"{self.base_url}/uprn"
            params = {
                "uprn": uprn,
                "output_srs": "EPSG:4326"
            }
            # Add API key to query parameters (new endpoint format)
            params = self._add_api_key_to_params(params)
            
            response = await self.client.get(
                url,
                params=params,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                if results:
                    dpa = results[0].get('DPA', {})
                    result = {
                        'uprn': dpa.get('UPRN'),
                        'address': dpa.get('ADDRESS'),
                        'building_name': dpa.get('BUILDING_NAME'),
                        'building_number': dpa.get('BUILDING_NUMBER'),
                        'street': dpa.get('THOROUGHFARE_NAME'),
                        'locality': dpa.get('DEPENDENT_LOCALITY'),
                        'town': dpa.get('POST_TOWN'),
                        'postcode': dpa.get('POSTCODE'),
                        'latitude': dpa.get('LAT'),
                        'longitude': dpa.get('LNG'),
                        'local_authority': dpa.get('LOCAL_CUSTODIAN_CODE_DESCRIPTION'),
                        'classification': dpa.get('CLASSIFICATION_CODE_DESCRIPTION'),
                        'fetched_at': datetime.now().isoformat()
                    }
                    
                    self.cache.set('os_places', uprn, result, endpoint='uprn')
                    return result
            
            return None
            
        except Exception as e:
            print(f"Error fetching UPRN {uprn}: {e}")
            return None
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# Convenience function
async def get_postcode_coordinates(postcode: str) -> Optional[Dict[str, float]]:
    """
    Quick helper to get coordinates for a postcode
    
    Usage:
        coords = await get_postcode_coordinates("B1 1BB")
        # Returns: {"latitude": 52.479, "longitude": -1.896}
    """
    async with OSPlacesLoader() as loader:
        return await loader.get_coordinates(postcode)

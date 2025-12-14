"""
Mock Care Homes Data Service
Uses simplified mock data for FREE Report
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Optional

# Path to mock data
# Try multiple possible paths
_backend_dir = Path(__file__).parent
_possible_paths = [
    _backend_dir.parent.parent.parent / "input" / "care_homes_mock_simplified.json",  # RCH-playground/input/
    _backend_dir.parent.parent.parent.parent / "RCH-playground" / "input" / "care_homes_mock_simplified.json",  # From RCH-admin-playground root
    _backend_dir.parent.parent / "input" / "care_homes_mock_simplified.json",  # Alternative
]

MOCK_DATA_PATH = None
for path in _possible_paths:
    if path.exists():
        MOCK_DATA_PATH = path
        break

# If still not found, use the first path as default
if MOCK_DATA_PATH is None:
    MOCK_DATA_PATH = _possible_paths[0]

# Cache for loaded data
_mock_care_homes_cache: Optional[List[Dict]] = None


def load_mock_care_homes() -> List[Dict]:
    """Load mock data from JSON file"""
    global _mock_care_homes_cache
    
    if _mock_care_homes_cache is not None:
        return _mock_care_homes_cache
    
    if not MOCK_DATA_PATH.exists():
        print(f"⚠️ Mock data file not found: {MOCK_DATA_PATH}")
        return []
    
    try:
        with open(MOCK_DATA_PATH, 'r', encoding='utf-8') as f:
            _mock_care_homes_cache = json.load(f)
        print(f"✅ Loaded {len(_mock_care_homes_cache)} mock care homes")
        return _mock_care_homes_cache
    except Exception as e:
        print(f"❌ Error loading mock data: {e}")
        return []


def get_mock_care_homes_by_postcode(postcode: str) -> List[Dict]:
    """Get mock homes by postcode (by prefix)"""
    homes = load_mock_care_homes()
    postcode_prefix = postcode.upper().split()[0]  # First part of postcode (e.g., "B44")
    
    return [
        h for h in homes
        if h.get('postcode', '').upper().startswith(postcode_prefix)
    ]


def get_mock_care_homes_by_local_authority(local_authority: str) -> List[Dict]:
    """Get mock homes by local authority"""
    homes = load_mock_care_homes()
    
    return [
        h for h in homes
        if h.get('local_authority', '').lower() == local_authority.lower()
    ]


def get_mock_care_homes_by_care_type(care_type: str) -> List[Dict]:
    """Get mock homes by care type"""
    homes = load_mock_care_homes()
    
    return [
        h for h in homes
        if care_type.lower() in [ct.lower() for ct in h.get('care_types', [])]
    ]


def get_mock_care_home_by_location_id(location_id: str) -> Optional[Dict]:
    """Get specific home by CQC location_id"""
    homes = load_mock_care_homes()
    
    for home in homes:
        if home.get('location_id') == location_id:
            return home
    
    return None


def filter_mock_care_homes(
    postcode: Optional[str] = None,
    local_authority: Optional[str] = None,
    care_type: Optional[str] = None,
    max_budget: Optional[float] = None,
    max_distance_km: Optional[float] = None,
    user_lat: Optional[float] = None,
    user_lon: Optional[float] = None
) -> List[Dict]:
    """
    Filter mock homes by various criteria
    
    Args:
        postcode: Filter by postcode (prefix)
        local_authority: Filter by local authority
        care_type: Filter by care type
        max_budget: Maximum budget (weekly GBP)
        max_distance_km: Maximum distance in km
        user_lat: User latitude
        user_lon: User longitude
    """
    homes = load_mock_care_homes()
    
    # Filter by postcode
    if postcode:
        postcode_prefix = postcode.upper().split()[0]
        homes = [
            h for h in homes
            if h.get('postcode', '').upper().startswith(postcode_prefix)
        ]
    
    # Filter by local authority (with normalization support)
    if local_authority:
        try:
            from services.location_normalizer import LocationNormalizer
            location_variants = LocationNormalizer.get_local_authority_variants(local_authority)
            
            if location_variants:
                # Match against all variants
                variant_lowers = [v.lower() for v in location_variants]
                homes = [
                    h for h in homes
                    if h.get('local_authority', '').lower() in variant_lowers or
                       h.get('city', '').lower() in variant_lowers or
                       any(variant_lower in h.get('local_authority', '').lower() for variant_lower in variant_lowers) or
                       any(variant_lower in h.get('city', '').lower() for variant_lower in variant_lowers)
                ]
            else:
                # Fallback to simple matching
                homes = [
                    h for h in homes
                    if h.get('local_authority', '').lower() == local_authority.lower() or
                       h.get('city', '').lower() == local_authority.lower()
                ]
        except ImportError:
            # Fallback if normalizer not available
            homes = [
                h for h in homes
                if h.get('local_authority', '').lower() == local_authority.lower() or
                   h.get('city', '').lower() == local_authority.lower()
            ]
    
    # Filter by care type
    if care_type:
        homes = [
            h for h in homes
            if care_type.lower() in [ct.lower() for ct in h.get('care_types', [])]
        ]
    
    # Filter by budget
    if max_budget:
        filtered = []
        for h in homes:
            costs = h.get('weekly_costs', {})
            # Check all care types
            if any(cost <= max_budget for cost in costs.values() if cost):
                filtered.append(h)
        homes = filtered
    
    # Filter by distance
    if max_distance_km and user_lat and user_lon:
        try:
            from utils.geo import calculate_distance_km
        except ImportError:
            # Fallback if utils.geo not available
            from math import radians, cos, sin, asin, sqrt
            def calculate_distance_km(lat1, lon1, lat2, lon2):
                R = 6371.0
                if not (lat2 and lon2):
                    return 9999.0  # Large distance if coordinates missing
                dlat = radians(lat2 - lat1)
                dlon = radians(lon2 - lon1)
                a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
                c = 2 * asin(sqrt(a))
                return R * c
        
        filtered = []
        for h in homes:
            lat2 = h.get('latitude')
            lon2 = h.get('longitude')
            if not (lat2 and lon2):
                continue  # Skip homes without coordinates
            distance = calculate_distance_km(user_lat, user_lon, lat2, lon2)
            if distance <= max_distance_km:
                h['distance_km'] = round(distance, 2)
                filtered.append(h)
        homes = filtered
    
    return homes


# Export for use in other modules
__all__ = [
    'load_mock_care_homes',
    'get_mock_care_homes_by_postcode',
    'get_mock_care_homes_by_local_authority',
    'get_mock_care_homes_by_care_type',
    'get_mock_care_home_by_location_id',
    'filter_mock_care_homes',
]


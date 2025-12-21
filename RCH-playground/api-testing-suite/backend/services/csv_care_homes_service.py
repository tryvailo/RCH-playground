"""
CSV Care Homes Data Service
Loads care homes data from merged_care_homes_west_midlands.csv for FREE Report matching

UPDATED: Now supports hybrid approach (CQC + Staging) with fallback to legacy CSV
"""
import csv
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Use shared geo utility instead of duplicating Haversine formula
try:
    from utils.geo import calculate_distance_km, validate_coordinates
    USE_SHARED_GEO = True
except ImportError:
    # Fallback if utils.geo not available (shouldn't happen in normal operation)
    from math import radians, cos, sin, asin, sqrt
    USE_SHARED_GEO = False

# Path to CSV file
_backend_dir = Path(__file__).parent
_possible_paths = [
    _backend_dir.parent.parent.parent.parent / "documents" / "merged_care_homes_west_midlands.csv",  # From RCH-admin-playground root
    _backend_dir.parent.parent.parent / "documents" / "merged_care_homes_west_midlands.csv",  # Alternative
    Path("/Users/alexander/Documents/Products/RCH-admin-playground/documents/merged_care_homes_west_midlands.csv"),  # Absolute path
]

CSV_DATA_PATH = None
for path in _possible_paths:
    if path.exists():
        CSV_DATA_PATH = path
        break

# Cache for loaded data
_csv_care_homes_cache: Optional[List[Dict]] = None


def _calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula.
    Uses shared utils.geo.calculate_distance_km if available, otherwise fallback.
    """
    if USE_SHARED_GEO:
        try:
            # Use shared geo utility (validates coordinates and uses proper Haversine)
            if validate_coordinates(lat2, lon2):
                return calculate_distance_km(lat1, lon1, lat2, lon2)
            else:
                return 9999.0  # Large distance if coordinates invalid
        except (ValueError, TypeError):
            return 9999.0
    else:
        # Fallback implementation (shouldn't be used in normal operation)
        R = 6371.0  # Earth radius in km
        if not (lat2 and lon2):
            return 9999.0  # Large distance if coordinates missing
        
        try:
            dlat = radians(float(lat2) - float(lat1))
            dlon = radians(float(lon2) - float(lon1))
            a = sin(dlat/2)**2 + cos(radians(float(lat1))) * cos(radians(float(lat2))) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            return R * c
        except (ValueError, TypeError):
            return 9999.0


def _parse_float(value: Optional[str]) -> Optional[float]:
    """Safely parse float from CSV value"""
    if not value or value == '':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _parse_bool(value: Optional[str]) -> bool:
    """Safely parse boolean from CSV value"""
    if not value:
        return False
    value_lower = str(value).lower().strip()
    return value_lower in ('true', '1', 'yes', 't')


def _parse_json_field(value: Optional[str]) -> Optional[Dict]:
    """Parse JSON field from CSV"""
    if not value or value == '':
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return None


def load_csv_care_homes() -> List[Dict]:
    """Load care homes from CSV file"""
    global _csv_care_homes_cache
    
    if _csv_care_homes_cache is not None:
        return _csv_care_homes_cache
    
    if not CSV_DATA_PATH or not CSV_DATA_PATH.exists():
        print(f"⚠️ CSV data file not found: {CSV_DATA_PATH}")
        return []
    
    try:
        homes = []
        with open(CSV_DATA_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse coordinates
                latitude = _parse_float(row.get('latitude'))
                longitude = _parse_float(row.get('longitude'))
                
                # Parse beds
                beds_total = _parse_float(row.get('beds_total'))
                beds_available = _parse_float(row.get('beds_available'))
                
                # Parse prices first (needed for care type inference)
                fee_residential_from = _parse_float(row.get('fee_residential_from'))
                fee_nursing_from = _parse_float(row.get('fee_nursing_from'))
                fee_dementia_from = _parse_float(row.get('fee_dementia_from'))
                fee_respite_from = _parse_float(row.get('fee_respite_from'))
                
                # Parse care types
                # First try boolean fields
                care_residential = _parse_bool(row.get('care_residential'))
                care_nursing = _parse_bool(row.get('care_nursing'))
                care_dementia = _parse_bool(row.get('care_dementia'))
                care_respite = _parse_bool(row.get('care_respite'))
                
                # If boolean fields are False, check if prices exist (indicates care type availability)
                if not care_residential and fee_residential_from:
                    care_residential = True
                if not care_nursing and fee_nursing_from:
                    care_nursing = True
                if not care_dementia and fee_dementia_from:
                    care_dementia = True
                if not care_respite and fee_respite_from:
                    care_respite = True
                
                # Also check name for hints (e.g., "Nursing and Residential")
                name_lower = (row.get('name') or '').lower()
                if 'nursing' in name_lower and not care_nursing:
                    care_nursing = True
                if 'residential' in name_lower and not care_residential:
                    care_residential = True
                if 'dementia' in name_lower and not care_dementia:
                    care_dementia = True
                
                # Build care_types list
                care_types = []
                if care_residential:
                    care_types.append('residential')
                if care_nursing:
                    care_types.append('nursing')
                if care_dementia:
                    care_types.append('dementia')
                if care_respite:
                    care_types.append('respite')
                
                # Default to residential if no care types detected
                if not care_types:
                    care_types.append('residential')
                
                # Parse ratings
                cqc_rating_overall = row.get('cqc_rating_overall', '').strip() or None
                cqc_rating_safe = row.get('cqc_rating_safe', '').strip() or None
                cqc_rating_effective = row.get('cqc_rating_effective', '').strip() or None
                cqc_rating_caring = row.get('cqc_rating_caring', '').strip() or None
                cqc_rating_responsive = row.get('cqc_rating_responsive', '').strip() or None
                cqc_rating_well_led = row.get('cqc_rating_well_led', '').strip() or None
                
                # Parse Google rating
                google_rating = _parse_float(row.get('google_rating'))
                review_count = _parse_float(row.get('review_count'))
                
                # Parse facilities
                wheelchair_access = _parse_bool(row.get('wheelchair_access'))
                ensuite_rooms = _parse_bool(row.get('ensuite_rooms'))
                secure_garden = _parse_bool(row.get('secure_garden'))
                wifi_available = _parse_bool(row.get('wifi_available'))
                parking_onsite = _parse_bool(row.get('parking_onsite'))
                
                # Parse JSON fields
                activities = _parse_json_field(row.get('activities'))
                media = _parse_json_field(row.get('media'))
                location_context = _parse_json_field(row.get('location_context'))
                
                # Build home dict
                home = {
                    'id': row.get('id') or row.get('cqc_location_id') or '',
                    'cqc_location_id': row.get('cqc_location_id') or '',
                    'location_ods_code': row.get('location_ods_code') or '',
                    'name': row.get('name') or 'Unknown',
                    'name_normalized': row.get('name_normalized') or '',
                    'provider_name': row.get('provider_name') or '',
                    'provider_id': row.get('provider_id') or '',
                    'brand_name': row.get('brand_name') or '',
                    'telephone': row.get('telephone') or '',
                    'email': row.get('email') or '',
                    'website': row.get('website') or '',
                    'city': row.get('city') or '',
                    'county': row.get('county') or '',
                    'postcode': row.get('postcode') or '',
                    'latitude': latitude,
                    'longitude': longitude,
                    'region': row.get('region') or '',
                    'local_authority': row.get('local_authority') or '',
                    'beds_total': beds_total,
                    'beds_available': beds_available,
                    'has_availability': _parse_bool(row.get('has_availability')),
                    'availability_status': row.get('availability_status') or '',
                    'care_residential': care_residential,
                    'care_nursing': care_nursing,
                    'care_dementia': care_dementia,
                    'care_respite': care_respite,
                    'care_types': care_types,
                    'fee_residential_from': fee_residential_from,
                    'fee_nursing_from': fee_nursing_from,
                    'fee_dementia_from': fee_dementia_from,
                    'fee_respite_from': fee_respite_from,
                    'cqc_rating_overall': cqc_rating_overall,
                    'cqc_rating_safe': cqc_rating_safe,
                    'cqc_rating_effective': cqc_rating_effective,
                    'cqc_rating_caring': cqc_rating_caring,
                    'cqc_rating_responsive': cqc_rating_responsive,
                    'cqc_rating_well_led': cqc_rating_well_led,
                    'cqc_last_inspection_date': row.get('cqc_last_inspection_date') or '',
                    'cqc_publication_date': row.get('cqc_publication_date') or '',
                    'cqc_latest_report_url': row.get('cqc_latest_report_url') or '',
                    'google_rating': google_rating,
                    'review_count': review_count,
                    'review_average_score': _parse_float(row.get('review_average_score')),
                    'wheelchair_access': wheelchair_access,
                    'ensuite_rooms': ensuite_rooms,
                    'secure_garden': secure_garden,
                    'wifi_available': wifi_available,
                    'parking_onsite': parking_onsite,
                    'activities': activities,
                    'media': media,
                    'location_context': location_context,
                }
                
                homes.append(home)
        
        _csv_care_homes_cache = homes
        print(f"✅ Loaded {len(homes)} care homes from CSV: {CSV_DATA_PATH}")
        return homes
    except Exception as e:
        print(f"❌ Error loading CSV data: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_care_homes(
    local_authority: Optional[str] = None,
    care_type: Optional[str] = None,
    max_distance_km: Optional[float] = None,
    user_lat: Optional[float] = None,
    user_lon: Optional[float] = None,
    limit: Optional[int] = None,
    min_required: int = 5,  # Minimum homes required (for auto-expansion)
    auto_expand: bool = True  # Enable automatic radius expansion
) -> List[Dict]:
    """
    Get care homes from CSV with filtering and automatic radius expansion.
    
    Implements STEP 2 from MVP Matching Algorithm:
    - Calculate distance for ALL homes
    - Sort by distance
    - Filter by preferred radius
    - Auto-expand if insufficient homes (MIN_REQUIRED = 5)
    
    Args:
        local_authority: Filter by local authority
        care_type: Filter by care type (residential, nursing, dementia, respite)
        max_distance_km: Preferred maximum distance in km (will expand if needed)
        user_lat: User latitude for distance calculation
        user_lon: User longitude for distance calculation
        limit: Maximum number of results
        min_required: Minimum homes required before auto-expansion stops
        auto_expand: Enable automatic radius expansion if insufficient homes
    
    Returns:
        List of care home dictionaries with distance_km calculated and sorted by distance
    """
    homes = load_csv_care_homes()
    
    # Filter by local authority
    if local_authority:
        homes = [
            h for h in homes
            if h.get('local_authority', '').lower() == local_authority.lower() or
               h.get('city', '').lower() == local_authority.lower() or
               local_authority.lower() in h.get('local_authority', '').lower() or
               local_authority.lower() in h.get('city', '').lower()
        ]
    
    # Filter by care type
    if care_type:
        care_type_lower = care_type.lower()
        filtered = []
        for h in homes:
            care_types = h.get('care_types', [])
            if care_type_lower in [ct.lower() for ct in care_types]:
                filtered.append(h)
            # Also check boolean fields for compatibility
            elif care_type_lower == 'residential' and h.get('care_residential'):
                filtered.append(h)
            elif care_type_lower == 'nursing' and h.get('care_nursing'):
                filtered.append(h)
            elif care_type_lower == 'dementia' and h.get('care_dementia'):
                filtered.append(h)
            elif care_type_lower == 'respite' and h.get('care_respite'):
                filtered.append(h)
        homes = filtered
    
    # STEP 2: Calculate distance for ALL homes and sort by distance
    # This ensures distance_km is always available in the home dict
    if user_lat and user_lon:
        for h in homes:
            lat = h.get('latitude')
            lon = h.get('longitude')
            if lat and lon:
                try:
                    distance = _calculate_distance_km(user_lat, user_lon, float(lat), float(lon))
                    h['distance_km'] = round(distance, 2)
                except (ValueError, TypeError) as e:
                    # If calculation fails, set large distance so it sorts last
                    h['distance_km'] = 9999.0
            else:
                # Missing coordinates - set large distance
                h['distance_km'] = 9999.0
        
        # Sort by distance (closest first)
        homes.sort(key=lambda h: h.get('distance_km', 9999.0))
        
        # Filter by preferred radius
        preferred_radius = max_distance_km if max_distance_km else 100.0
        in_preferred = [
            h for h in homes
            if h.get('distance_km', 9999.0) <= preferred_radius
        ]
        
        # Auto-expand if insufficient homes (STEP 2 from MVP Matching Algorithm)
        if auto_expand and len(in_preferred) < min_required:
            EXPANSION_STEPS = [5, 10, 15, 30, 50, 75, 100]
            expanded_radius = preferred_radius
            
            for step in EXPANSION_STEPS:
                if step > preferred_radius:
                    expanded_radius = step
                    in_expanded = [
                        h for h in homes
                        if h.get('distance_km', 9999.0) <= expanded_radius
                    ]
                    if len(in_expanded) >= min_required:
                        # Mark homes as preferred vs expanded
                        for h in in_expanded:
                            h['within_preferred_radius'] = h.get('distance_km', 9999.0) <= preferred_radius
                            h['radius_category'] = 'preferred' if h.get('within_preferred_radius') else 'expanded'
                        
                        # Apply limit and return
                        result = in_expanded[:limit] if limit else in_expanded
                        return result
            
            # If even after expansion insufficient, return all we have
            for h in in_preferred:
                h['within_preferred_radius'] = True
                h['radius_category'] = 'preferred'
            result = in_preferred[:limit] if limit else in_preferred
            return result
        else:
            # Enough homes in preferred radius, mark them
            for h in in_preferred:
                h['within_preferred_radius'] = True
                h['radius_category'] = 'preferred'
            homes = in_preferred
    else:
        # No coordinates - can't calculate distance, return as-is
        for h in homes:
            h['distance_km'] = None
    
    # Apply limit
    if limit:
        homes = homes[:limit]
    
    return homes


def get_care_homes_hybrid(
    local_authority: Optional[str] = None,
    care_type: Optional[str] = None,
    max_distance_km: Optional[float] = None,
    user_lat: Optional[float] = None,
    user_lon: Optional[float] = None,
    limit: Optional[int] = None,
    min_required: int = 5,
    auto_expand: bool = True
) -> List[Dict[str, Any]]:
    """
    Загрузить дома используя гибридный подход (CQC + Staging).
    
    This is the new preferred method that uses:
    - Primary source: CQC CSV (cqc_carehomes_master_full_data_rows.csv)
    - Auxiliary source: Staging CSV (carehome_staging_export.csv)
    
    Args:
        local_authority: Filter by local authority
        care_type: Filter by care type (residential, nursing, dementia, respite)
        max_distance_km: Preferred maximum distance in km (will expand if needed)
        user_lat: User latitude for distance calculation
        user_lon: User longitude for distance calculation
        limit: Maximum number of results
        min_required: Minimum homes required before auto-expansion stops
        auto_expand: Enable automatic radius expansion if insufficient homes
    
    Returns:
        List[Dict]: Объединенные данные из CQC и Staging
    """
    try:
        from services.cqc_data_loader import load_cqc_homes
        from services.staging_data_loader import load_staging_data
        from services.hybrid_data_merger import merge_cqc_and_staging
        
        # 1. Загрузить CQC
        logger.info("Loading CQC homes...")
        cqc_homes = load_cqc_homes()
        
        if not cqc_homes:
            logger.warning("No CQC homes loaded, falling back to legacy CSV")
            raise Exception("No CQC homes loaded")
        
        # 2. Загрузить Staging
        logger.info("Loading Staging data...")
        staging_list = load_staging_data()
        
        # 3. Объединить
        logger.info("Merging CQC and Staging data...")
        merged_homes = merge_cqc_and_staging(cqc_homes, staging_list)
        
        # 4. Фильтрация по local_authority
        if local_authority:
            local_authority_lower = local_authority.lower() if local_authority else ''
            merged_homes = [
                h for h in merged_homes
                if (h.get('local_authority') or '').lower() == local_authority_lower or
                   (h.get('city') or '').lower() == local_authority_lower or
                   local_authority_lower in (h.get('local_authority') or '').lower() or
                   local_authority_lower in (h.get('city') or '').lower()
            ]
        
        # 5. Фильтрация по care_type
        if care_type:
            care_type_lower = care_type.lower()
            filtered = []
            for h in merged_homes:
                # Check boolean fields
                if care_type_lower == 'residential' and h.get('care_residential'):
                    filtered.append(h)
                elif care_type_lower == 'nursing' and h.get('care_nursing'):
                    filtered.append(h)
                elif care_type_lower == 'dementia' and h.get('care_dementia'):
                    filtered.append(h)
                elif care_type_lower == 'respite' and h.get('care_respite'):
                    filtered.append(h)
            merged_homes = filtered
        
        # 6. Calculate distance for ALL homes and sort by distance
        if user_lat and user_lon:
            for h in merged_homes:
                lat = h.get('latitude')
                lon = h.get('longitude')
                if lat and lon:
                    try:
                        distance = _calculate_distance_km(user_lat, user_lon, float(lat), float(lon))
                        h['distance_km'] = round(distance, 2)
                    except (ValueError, TypeError):
                        h['distance_km'] = 9999.0
                else:
                    h['distance_km'] = 9999.0
            
            # Sort by distance (closest first)
            merged_homes.sort(key=lambda h: h.get('distance_km', 9999.0))
            
            # Filter by preferred radius
            preferred_radius = max_distance_km if max_distance_km else 100.0
            in_preferred = [
                h for h in merged_homes
                if h.get('distance_km', 9999.0) <= preferred_radius
            ]
            
            # Auto-expand if insufficient homes
            if auto_expand and len(in_preferred) < min_required:
                EXPANSION_STEPS = [5, 10, 15, 30, 50, 75, 100]
                expanded_radius = preferred_radius
                
                for step in EXPANSION_STEPS:
                    if step > preferred_radius:
                        expanded_radius = step
                        in_expanded = [
                            h for h in merged_homes
                            if h.get('distance_km', 9999.0) <= expanded_radius
                        ]
                        if len(in_expanded) >= min_required:
                            # Mark homes as preferred vs expanded
                            for h in in_expanded:
                                h['within_preferred_radius'] = h.get('distance_km', 9999.0) <= preferred_radius
                                h['radius_category'] = 'preferred' if h.get('within_preferred_radius') else 'expanded'
                            
                            # Apply limit and return
                            result = in_expanded[:limit] if limit else in_expanded
                            logger.info(f"✅ Hybrid approach: {len(result)} homes (expanded to {expanded_radius}km)")
                            return result
                
                # If even after expansion insufficient, return all we have
                for h in in_preferred:
                    h['within_preferred_radius'] = True
                    h['radius_category'] = 'preferred'
                result = in_preferred[:limit] if limit else in_preferred
                logger.info(f"✅ Hybrid approach: {len(result)} homes (preferred radius only)")
                return result
            else:
                # Enough homes in preferred radius
                for h in in_preferred:
                    h['within_preferred_radius'] = True
                    h['radius_category'] = 'preferred'
                merged_homes = in_preferred
        else:
            # No coordinates - can't calculate distance
            for h in merged_homes:
                h['distance_km'] = None
        
        # 7. Apply limit
        if limit:
            merged_homes = merged_homes[:limit]
        
        logger.info(f"✅ Hybrid approach: {len(merged_homes)} homes loaded")
        return merged_homes
    
    except Exception as e:
        logger.warning(f"Hybrid approach failed: {e}, falling back to legacy CSV")
        raise  # Re-raise to trigger fallback in get_care_homes()


def get_care_homes(
    local_authority: Optional[str] = None,
    care_type: Optional[str] = None,
    max_distance_km: Optional[float] = None,
    user_lat: Optional[float] = None,
    user_lon: Optional[float] = None,
    limit: Optional[int] = None,
    min_required: int = 5,
    auto_expand: bool = True,
    use_hybrid: bool = True  # New parameter: enable hybrid approach by default
) -> List[Dict]:
    """
    Get care homes from CSV with filtering and automatic radius expansion.
    
    UPDATED: Now tries hybrid approach (CQC + Staging) first, with fallback to legacy CSV.
    
    Implements STEP 2 from MVP Matching Algorithm:
    - Calculate distance for ALL homes
    - Sort by distance
    - Filter by preferred radius
    - Auto-expand if insufficient homes (MIN_REQUIRED = 5)
    
    Args:
        local_authority: Filter by local authority
        care_type: Filter by care type (residential, nursing, dementia, respite)
        max_distance_km: Preferred maximum distance in km (will expand if needed)
        user_lat: User latitude for distance calculation
        user_lon: User longitude for distance calculation
        limit: Maximum number of results
        min_required: Minimum homes required before auto-expansion stops
        auto_expand: Enable automatic radius expansion if insufficient homes
        use_hybrid: If True, try hybrid approach first (default: True)
    
    Returns:
        List of care home dictionaries with distance_km calculated and sorted by distance
    """
    # Try hybrid approach first (if enabled)
    if use_hybrid:
        try:
            return get_care_homes_hybrid(
                local_authority=local_authority,
                care_type=care_type,
                max_distance_km=max_distance_km,
                user_lat=user_lat,
                user_lon=user_lon,
                limit=limit,
                min_required=min_required,
                auto_expand=auto_expand
            )
        except Exception as e:
            logger.warning(f"Hybrid approach failed: {e}, falling back to legacy CSV")
            # Fall through to legacy CSV loading
    
    # Fallback to legacy CSV (merged_care_homes_west_midlands.csv)
    logger.info("Using legacy CSV (merged_care_homes_west_midlands.csv)")
    homes = load_csv_care_homes()
    
    # Filter by local authority
    if local_authority:
        homes = [
            h for h in homes
            if h.get('local_authority', '').lower() == local_authority.lower() or
               h.get('city', '').lower() == local_authority.lower() or
               local_authority.lower() in h.get('local_authority', '').lower() or
               local_authority.lower() in h.get('city', '').lower()
        ]
    
    # Filter by care type
    if care_type:
        care_type_lower = care_type.lower()
        filtered = []
        for h in homes:
            care_types = h.get('care_types', [])
            if care_type_lower in [ct.lower() for ct in care_types]:
                filtered.append(h)
            # Also check boolean fields for compatibility
            elif care_type_lower == 'residential' and h.get('care_residential'):
                filtered.append(h)
            elif care_type_lower == 'nursing' and h.get('care_nursing'):
                filtered.append(h)
            elif care_type_lower == 'dementia' and h.get('care_dementia'):
                filtered.append(h)
            elif care_type_lower == 'respite' and h.get('care_respite'):
                filtered.append(h)
        homes = filtered
    
    # STEP 2: Calculate distance for ALL homes and sort by distance
    # This ensures distance_km is always available in the home dict
    if user_lat and user_lon:
        for h in homes:
            lat = h.get('latitude')
            lon = h.get('longitude')
            if lat and lon:
                try:
                    distance = _calculate_distance_km(user_lat, user_lon, float(lat), float(lon))
                    h['distance_km'] = round(distance, 2)
                except (ValueError, TypeError) as e:
                    # If calculation fails, set large distance so it sorts last
                    h['distance_km'] = 9999.0
            else:
                # Missing coordinates - set large distance
                h['distance_km'] = 9999.0
        
        # Sort by distance (closest first)
        homes.sort(key=lambda h: h.get('distance_km', 9999.0))
        
        # Filter by preferred radius
        preferred_radius = max_distance_km if max_distance_km else 100.0
        in_preferred = [
            h for h in homes
            if h.get('distance_km', 9999.0) <= preferred_radius
        ]
        
        # Auto-expand if insufficient homes (STEP 2 from MVP Matching Algorithm)
        if auto_expand and len(in_preferred) < min_required:
            EXPANSION_STEPS = [5, 10, 15, 30, 50, 75, 100]
            expanded_radius = preferred_radius
            
            for step in EXPANSION_STEPS:
                if step > preferred_radius:
                    expanded_radius = step
                    in_expanded = [
                        h for h in homes
                        if h.get('distance_km', 9999.0) <= expanded_radius
                    ]
                    if len(in_expanded) >= min_required:
                        # Mark homes as preferred vs expanded
                        for h in in_expanded:
                            h['within_preferred_radius'] = h.get('distance_km', 9999.0) <= preferred_radius
                            h['radius_category'] = 'preferred' if h.get('within_preferred_radius') else 'expanded'
                        
                        # Apply limit and return
                        result = in_expanded[:limit] if limit else in_expanded
                        return result
            
            # If even after expansion insufficient, return all we have
            for h in in_preferred:
                h['within_preferred_radius'] = True
                h['radius_category'] = 'preferred'
            result = in_preferred[:limit] if limit else in_preferred
            return result
        else:
            # Enough homes in preferred radius, mark them
            for h in in_preferred:
                h['within_preferred_radius'] = True
                h['radius_category'] = 'preferred'
            homes = in_preferred
    else:
        # No coordinates - can't calculate distance, return as-is
        for h in homes:
            h['distance_km'] = None
    
    # Apply limit
    if limit:
        homes = homes[:limit]
    
    return homes


# Export for use in other modules
__all__ = [
    'load_csv_care_homes',
    'get_care_homes',
    'get_care_homes_hybrid',
]


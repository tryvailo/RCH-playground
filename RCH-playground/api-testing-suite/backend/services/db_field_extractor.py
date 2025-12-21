"""
Database Field Extractor: Helper functions to extract data from DB structure

This module provides helper functions to extract data from both flat fields
and JSONB structures in the care_homes database, ensuring the matching
algorithm correctly uses all available data.
"""

from typing import Dict, Any, List, Optional, Union


def get_service_user_band(
    home: Dict[str, Any],
    band_name: str
) -> Optional[bool]:
    """
    Get Service User Band value from home data.
    
    Checks both flat fields and JSONB structure:
    1. Flat field: `serves_*` (e.g., `serves_dementia_band`)
    2. JSONB field: `service_user_bands` -> `bands` array
    
    Args:
        home: Care home data dictionary
        band_name: Service user band name (e.g., 'dementia_band', 'older_people')
        
    Returns:
        True if band is present, False if explicitly absent, None if unknown
    """
    # Map band names to flat field names
    band_to_field = {
        'dementia_band': 'serves_dementia_band',
        'older_people': 'serves_older_people',
        'younger_adults': 'serves_younger_adults',
        'mental_health': 'serves_mental_health',
        'physical_disabilities': 'serves_physical_disabilities',
        'sensory_impairments': 'serves_sensory_impairments',
        'learning_disabilities': 'serves_learning_disabilities',
        'children': 'serves_children',
        'detained_mha': 'serves_detained_mha',
        'substance_misuse': 'serves_substance_misuse',
        'eating_disorders': 'serves_eating_disorders',
        'whole_population': 'serves_whole_population'
    }
    
    # Map to CQC API band names (for JSONB matching)
    band_to_cqc_name = {
        'dementia_band': ['Dementia', 'People with dementia'],
        'older_people': ['Older people', 'Older People'],
        'younger_adults': ['Younger adults', 'Younger Adults'],
        'mental_health': ['Mental health', 'Mental Health'],
        'physical_disabilities': ['Physical disability', 'Physical Disability'],
        'sensory_impairments': ['Sensory impairment', 'Sensory Impairment'],
        'learning_disabilities': ['Learning disabilities', 'Learning Disabilities', 'Autistic spectrum disorder'],
        'children': ['Children (0-18 years)', 'Children'],
        'detained_mha': ['People detained under the Mental Health Act'],
        'substance_misuse': ['People who misuse drugs and alcohol'],
        'eating_disorders': ['People with an eating disorder'],
        'whole_population': ['Whole population', 'Whole Population']
    }
    
    # ─────────────────────────────────────────────────────
    # LEVEL 1: Check flat field (preferred - direct)
    # ─────────────────────────────────────────────────────
    field_name = band_to_field.get(band_name)
    if field_name:
        flat_value = home.get(field_name)
        if flat_value is not None:
            return bool(flat_value)
    
    # ─────────────────────────────────────────────────────
    # LEVEL 2: Check JSONB field (fallback)
    # ─────────────────────────────────────────────────────
    service_user_bands = home.get('service_user_bands')
    if service_user_bands:
        # Handle different JSONB structures
        bands_list = None
        
        if isinstance(service_user_bands, dict):
            # Structure: {"bands": ["Older People", "Mental Health", ...]}
            bands_list = service_user_bands.get('bands', [])
        elif isinstance(service_user_bands, list):
            # Structure: ["Older People", "Mental Health", ...]
            bands_list = service_user_bands
        
        if bands_list:
            cqc_names = band_to_cqc_name.get(band_name, [])
            # Check if any CQC name matches
            for cqc_name in cqc_names:
                if any(
                    cqc_name.lower() in str(band).lower() or
                    str(band).lower() in cqc_name.lower()
                    for band in bands_list
                ):
                    return True
    
    # ─────────────────────────────────────────────────────
    # LEVEL 3: Unknown (NULL in both flat and JSONB)
    # ─────────────────────────────────────────────────────
    return None


def get_regulated_activity(
    home: Dict[str, Any],
    activity_id: str
) -> Optional[bool]:
    """
    Get Regulated Activity status from home data.
    
    Checks both flat fields and JSONB structure:
    1. Flat field: `has_*_license` (e.g., `has_nursing_care_license`)
    2. JSONB field: `regulated_activities` -> `activities` array
    
    Args:
        home: Care home data dictionary
        activity_id: Regulated activity ID (e.g., 'nursing_care', 'personal_care')
        
    Returns:
        True if activity is active, False if explicitly inactive, None if unknown
    """
    # Map activity IDs to flat field names
    activity_to_field = {
        'nursing_care': 'has_nursing_care_license',
        'personal_care': 'has_personal_care_license',
        'surgical_procedures': 'has_surgical_procedures_license',
        'treatment_disease': 'has_treatment_license',
        'diagnostic_screening': 'has_diagnostic_license'
    }
    
    # ─────────────────────────────────────────────────────
    # LEVEL 1: Check flat field (preferred - direct)
    # ─────────────────────────────────────────────────────
    field_name = activity_to_field.get(activity_id)
    if field_name:
        flat_value = home.get(field_name)
        if flat_value is not None:
            return bool(flat_value)
    
    # ─────────────────────────────────────────────────────
    # LEVEL 2: Check JSONB field (fallback - all 14 activities)
    # ─────────────────────────────────────────────────────
    regulated_activities = home.get('regulated_activities')
    if regulated_activities:
        # Handle different JSONB structures
        activities_list = None
        
        if isinstance(regulated_activities, dict):
            # Structure: {"activities": [{"id": "...", "active": true}, ...]}
            activities_list = regulated_activities.get('activities', [])
        elif isinstance(regulated_activities, list):
            # Structure: [{"id": "...", "active": true}, ...]
            activities_list = regulated_activities
        
        if activities_list:
            for activity in activities_list:
                if isinstance(activity, dict):
                    activity_id_from_db = activity.get('id') or activity.get('name', '').lower().replace(' ', '_')
                    is_active = activity.get('active', True)
                    
                    # Match by ID or name
                    if (activity_id in activity_id_from_db or 
                        activity_id_from_db in activity_id):
                        return bool(is_active)
                elif isinstance(activity, str):
                    # Simple string match
                    if activity_id.lower() in activity.lower():
                        return True
    
    # ─────────────────────────────────────────────────────
    # LEVEL 3: Unknown (NULL in both flat and JSONB)
    # ─────────────────────────────────────────────────────
    return None


def get_inspection_date(
    home: Dict[str, Any],
    enriched_data: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Get last inspection date from home data.
    
    Checks multiple sources:
    1. Flat field: `cqc_last_inspection_date`
    2. Enriched data: `cqc_detailed.inspection_date`
    3. Enriched data: `cqc_detailed.last_inspection_date`
    
    Args:
        home: Care home data dictionary
        enriched_data: Optional enriched data from APIs
        
    Returns:
        Inspection date as string (YYYY-MM-DD) or None
    """
    # ─────────────────────────────────────────────────────
    # LEVEL 1: Check flat field
    # ─────────────────────────────────────────────────────
    inspection_date = home.get('cqc_last_inspection_date')
    if inspection_date:
        # Convert date object to string if needed
        if hasattr(inspection_date, 'strftime'):
            return inspection_date.strftime('%Y-%m-%d')
        return str(inspection_date)
    
    # ─────────────────────────────────────────────────────
    # LEVEL 2: Check enriched data
    # ─────────────────────────────────────────────────────
    if enriched_data:
        cqc_data = enriched_data.get('cqc_detailed', {})
        inspection_date = (
            cqc_data.get('inspection_date') or
            cqc_data.get('last_inspection_date') or
            cqc_data.get('inspectionDate')
        )
        if inspection_date:
            if hasattr(inspection_date, 'strftime'):
                return inspection_date.strftime('%Y-%m-%d')
            return str(inspection_date)
    
    return None


def get_facility_value(
    home: Dict[str, Any],
    facility_key: str,
    facility_category: Optional[str] = None
) -> Optional[Any]:
    """
    Get facility value from JSONB `facilities` field.
    
    Args:
        home: Care home data dictionary
        facility_key: Facility key to look for (e.g., 'medical_equipment', 'on_site_pharmacy')
        facility_category: Optional category (e.g., 'medical_facilities', 'general_amenities')
        
    Returns:
        Facility value or None
    """
    facilities = home.get('facilities')
    if not facilities:
        return None
    
    if not isinstance(facilities, dict):
        return None
    
    # If category specified, check in that category first
    if facility_category:
        category_data = facilities.get(facility_category, {})
        if isinstance(category_data, dict) and facility_key in category_data:
            return category_data[facility_key]
    
    # Check at top level
    if facility_key in facilities:
        return facilities[facility_key]
    
    # Check in all categories
    for category, category_data in facilities.items():
        if isinstance(category_data, dict) and facility_key in category_data:
            return category_data[facility_key]
    
    return None


def get_staff_information(
    home: Dict[str, Any],
    info_key: str
) -> Optional[Any]:
    """
    Get staff information from JSONB `staff_information` field.
    
    Args:
        home: Care home data dictionary
        info_key: Information key (e.g., 'staff_ratio', 'staff_retention_rate', 'nurse_to_resident_ratio')
        
    Returns:
        Staff information value or None
    """
    staff_info = home.get('staff_information')
    if not staff_info:
        return None
    
    if not isinstance(staff_info, dict):
        return None
    
    return staff_info.get(info_key)


def get_cqc_rating(
    home: Dict[str, Any],
    rating_type: str,
    enriched_data: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Get CQC rating from home data.
    
    Checks multiple sources:
    1. Flat field: `cqc_rating_*`
    2. Enriched data: `cqc_detailed.*_rating`
    3. Enriched data: `cqc_detailed.detailed_ratings.*.rating`
    
    Args:
        home: Care home data dictionary
        rating_type: Rating type ('overall', 'safe', 'caring', 'effective', 'responsive', 'well_led')
        enriched_data: Optional enriched data from APIs
        
    Returns:
        Rating value ('Outstanding', 'Good', 'Requires improvement', 'Inadequate') or None
    """
    # ─────────────────────────────────────────────────────
    # LEVEL 1: Check flat field
    # ─────────────────────────────────────────────────────
    flat_field = f'cqc_rating_{rating_type}'
    rating = home.get(flat_field)
    if rating:
        return str(rating)
    
    # ─────────────────────────────────────────────────────
    # LEVEL 2: Check enriched data
    # ─────────────────────────────────────────────────────
    if enriched_data:
        cqc_data = enriched_data.get('cqc_detailed', {})
        
        # Try direct field
        rating = cqc_data.get(f'{rating_type}_rating')
        if rating:
            return str(rating)
        
        # Try detailed_ratings structure
        detailed_ratings = cqc_data.get('detailed_ratings', {})
        if isinstance(detailed_ratings, dict):
            rating_obj = detailed_ratings.get(rating_type, {})
            if isinstance(rating_obj, dict):
                rating = rating_obj.get('rating')
                if rating:
                    return str(rating)
        
        # Try camelCase
        camel_case = rating_type.replace('_', ' ').title().replace(' ', '')
        camel_case = camel_case[0].lower() + camel_case[1:] if camel_case else rating_type
        rating = cqc_data.get(f'{camel_case}Rating') or cqc_data.get(f'{camel_case}_rating')
        if rating:
            return str(rating)
    
    return None


def get_funding_acceptance(
    home: Dict[str, Any],
    funding_type: str
) -> Optional[bool]:
    """
    Get funding acceptance status from home data.
    
    Checks flat fields:
    - accepts_self_funding
    - accepts_local_authority
    - accepts_nhs_chc
    - accepts_third_party_topup
    
    Args:
        home: Care home data dictionary
        funding_type: Funding type ('self_funding', 'local_authority', 'nhs_chc', 'third_party_topup')
        
    Returns:
        True if accepts, False if explicitly doesn't, None if unknown
    """
    funding_to_field = {
        'self_funding': 'accepts_self_funding',
        'local_authority': 'accepts_local_authority',
        'nhs_chc': 'accepts_nhs_chc',
        'third_party_topup': 'accepts_third_party_topup'
    }
    
    field_name = funding_to_field.get(funding_type)
    if field_name:
        value = home.get(field_name)
        if value is not None:
            return bool(value)
    
    return None


def get_review_data(
    home: Dict[str, Any],
    review_type: str = 'average'
) -> Optional[Union[float, int]]:
    """
    Get review data from home data.
    
    Checks flat fields:
    - review_average_score
    - review_count
    - google_rating
    
    Also checks JSONB `reviews_detailed` if available.
    
    Args:
        home: Care home data dictionary
        review_type: Review type ('average', 'count', 'google')
        
    Returns:
        Review value (float for scores, int for count) or None
    """
    # ─────────────────────────────────────────────────────
    # LEVEL 1: Check flat fields
    # ─────────────────────────────────────────────────────
    if review_type == 'average':
        value = home.get('review_average_score')
        if value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                pass
    elif review_type == 'count':
        value = home.get('review_count')
        if value is not None:
            try:
                return int(value)
            except (ValueError, TypeError):
                pass
    elif review_type == 'google':
        value = home.get('google_rating')
        if value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                pass
    
    # ─────────────────────────────────────────────────────
    # LEVEL 2: Check JSONB reviews_detailed
    # ─────────────────────────────────────────────────────
    reviews_detailed = home.get('reviews_detailed')
    if reviews_detailed and isinstance(reviews_detailed, dict):
        if review_type == 'average':
            value = reviews_detailed.get('average_score') or reviews_detailed.get('average')
            if value is not None:
                try:
                    return float(value)
                except (ValueError, TypeError):
                    pass
        elif review_type == 'count':
            value = reviews_detailed.get('total_count') or reviews_detailed.get('count')
            if value is not None:
                try:
                    return int(value)
                except (ValueError, TypeError):
                    pass
        elif review_type == 'google':
            value = reviews_detailed.get('google_rating') or reviews_detailed.get('google')
            if value is not None:
                try:
                    return float(value)
                except (ValueError, TypeError):
                    pass
    
    return None


def get_amenity_value(
    home: Dict[str, Any],
    amenity_name: str
) -> Optional[bool]:
    """
    Get amenity value from home data.
    
    Checks both flat fields and JSONB `facilities` field.
    
    Flat fields:
    - wheelchair_access
    - ensuite_rooms
    - secure_garden
    - wifi_available
    - parking_onsite
    
    Args:
        home: Care home data dictionary
        amenity_name: Amenity name (e.g., 'wheelchair_access', 'ensuite_rooms', 'secure_garden', 'wifi_available', 'parking_onsite')
        
    Returns:
        True if available, False if explicitly not available, None if unknown
    """
    # ─────────────────────────────────────────────────────
    # LEVEL 1: Check flat field (preferred)
    # ─────────────────────────────────────────────────────
    flat_value = home.get(amenity_name)
    if flat_value is not None:
        return bool(flat_value)
    
    # ─────────────────────────────────────────────────────
    # LEVEL 2: Check JSONB facilities field
    # ─────────────────────────────────────────────────────
    facilities = home.get('facilities')
    if facilities and isinstance(facilities, dict):
        # Check in general_amenities
        general_amenities = facilities.get('general_amenities', [])
        if isinstance(general_amenities, list):
            if amenity_name in general_amenities or any(
                amenity_name.lower() in str(amenity).lower() 
                for amenity in general_amenities
            ):
                return True
        
        # Check at top level
        if amenity_name in facilities:
            value = facilities[amenity_name]
            if isinstance(value, bool):
                return value
            elif value:
                return True
    
    return None


def get_availability_info(
    home: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Get availability information from home data.
    
    Checks flat fields:
    - has_availability
    - beds_available
    - beds_total
    - availability_status
    
    Args:
        home: Care home data dictionary
        
    Returns:
        Dictionary with availability information
    """
    return {
        'has_availability': home.get('has_availability'),
        'beds_available': home.get('beds_available'),
        'beds_total': home.get('beds_total'),
        'availability_status': home.get('availability_status')
    }


def get_year_info(
    home: Dict[str, Any]
) -> Dict[str, Optional[int]]:
    """
    Get year information from home data.
    
    Checks flat fields:
    - year_opened
    - year_registered
    
    Args:
        home: Care home data dictionary
        
    Returns:
        Dictionary with year information
    """
    year_opened = home.get('year_opened')
    year_registered = home.get('year_registered')
    
    return {
        'year_opened': int(year_opened) if year_opened is not None else None,
        'year_registered': int(year_registered) if year_registered is not None else None
    }

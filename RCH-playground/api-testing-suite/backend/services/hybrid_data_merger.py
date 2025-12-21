"""
Hybrid Data Merger
Merges data from CQC (primary) and Staging (auxiliary) sources

Part of hybrid database approach:
- CQC is primary source (authoritative for critical fields)
- Staging is auxiliary source (for additional fields)
- Merges with priority: CQC → Staging (fallback)
- Uses care_home_matcher for matching since staging doesn't have cqc_location_id
"""
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Critical fields that should come from CQC (not Staging)
CQC_CRITICAL_FIELDS = {
    # Service User Bands
    'serves_older_people', 'serves_dementia_band', 'serves_mental_health',
    'serves_physical_disabilities', 'serves_sensory_impairments',
    'serves_children', 'serves_learning_disabilities', 'serves_detained_mha',
    'serves_substance_misuse', 'serves_eating_disorders',
    'serves_whole_population', 'serves_younger_adults',
    
    # CQC Ratings
    'cqc_rating_overall', 'cqc_rating_safe', 'cqc_rating_effective',
    'cqc_rating_caring', 'cqc_rating_responsive', 'cqc_rating_well_led',
    
    # Location
    'latitude', 'longitude', 'postcode', 'city', 'local_authority',
    
    # Care Types
    'care_nursing', 'care_residential', 'care_dementia',
    
    # Licenses
    'has_nursing_care_license', 'has_personal_care_license',
    'has_surgical_procedures_license', 'has_treatment_license',
    'has_diagnostic_license',
    
    # IDs
    'id', 'location_id', 'cqc_location_id', 'name', 'provider_id', 'provider_name'
}

# Fields that should come from Staging (if available)
STAGING_PREFERRED_FIELDS = {
    # Pricing
    'fee_residential_from', 'fee_nursing_from', 'fee_dementia_from', 'fee_respite_from',
    
    # Reviews
    'review_average_score', 'review_count',
    
    # Amenities
    'wheelchair_access', 'wifi_available', 'parking_onsite',
    
    # Availability
    'beds_total',
    
    # Funding
    'accepts_self_funding', 'accepts_local_authority', 'accepts_nhs_chc'
}


def merge_single_home(
    cqc_home: Dict[str, Any],
    staging_data: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Объединить данные для одного дома.
    
    Приоритеты:
    1. CQC для критических полей (Service User Bands, Ratings, Location, Care Types)
    2. Staging для дополнительных полей (Pricing, Reviews, Amenities, Availability, Funding)
    3. Fallback: если поле пустое в CQC → использовать Staging
    
    Args:
        cqc_home: Данные из CQC
        staging_data: Данные из Staging (может быть None)
        
    Returns:
        Dict с объединенными данными
    """
    merged = cqc_home.copy()
    
    if not staging_data:
        return merged
    
    # ─────────────────────────────────────────────────────
    # Merge Staging fields
    # ─────────────────────────────────────────────────────
    for field, value in staging_data.items():
        if field == 'cqc_location_id':
            continue  # Skip connection key
        
        # Priority 1: Critical fields from CQC (never override)
        if field in CQC_CRITICAL_FIELDS:
            # Only use Staging if CQC value is None/empty
            if merged.get(field) is None:
                merged[field] = value
            continue
        
        # Priority 2: Staging preferred fields (use Staging if available)
        if field in STAGING_PREFERRED_FIELDS:
            if value is not None:
                merged[field] = value
            continue
        
        # Priority 3: Fallback - use Staging if CQC is None/empty
        if merged.get(field) is None and value is not None:
            merged[field] = value
    
    return merged


def merge_cqc_and_staging(
    cqc_homes: List[Dict[str, Any]],
    staging_list: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Объединить данные из CQC и Staging.
    
    Приоритеты:
    1. CQC для критических полей (Service User Bands, Ratings, Location, Care Types)
    2. Staging для дополнительных полей (Pricing, Reviews, Amenities, Availability, Funding)
    3. Fallback: если поле пустое в CQC → использовать Staging
    
    Args:
        cqc_homes: Список домов из CQC
        staging_list: Список данных Staging (не индексированный, т.к. нет location_id)
        
    Returns:
        List[Dict]: Объединенные данные
    """
    from services.care_home_matcher import (
        build_staging_index_with_keys,
        match_cqc_to_staging
    )
    
    # Build staging index with matching keys (name+postcode, name+city, etc.)
    staging_index = build_staging_index_with_keys(staging_list)
    
    merged_homes = []
    matched_count = 0
    matched_by_location_id = 0
    matched_by_fields = 0
    
    for cqc_home in cqc_homes:
        staging_data = None
        
        # First, try to match by location_id if available
        location_id = (
            cqc_home.get('location_id') or 
            cqc_home.get('cqc_location_id') or
            cqc_home.get('id')
        )
        
        if location_id:
            location_id = str(location_id).strip()
            # Try to find in staging by location_id (if any staging records have it)
            for staging_record in staging_list:
                if staging_record.get('cqc_location_id') == location_id:
                    staging_data = staging_record
                    matched_by_location_id += 1
                    break
        
        # If not found by location_id, use field-based matching
        if not staging_data:
            staging_data = match_cqc_to_staging(cqc_home, staging_index)
            if staging_data:
                matched_by_fields += 1
        
        # Merge CQC and Staging
        merged_home = merge_single_home(cqc_home, staging_data)
        
        if staging_data:
            matched_count += 1
        
        merged_homes.append(merged_home)
    
    logger.info(
        f"✅ Merged {len(merged_homes)} homes: "
        f"{matched_count} matched with Staging "
        f"({matched_by_location_id} by location_id, {matched_by_fields} by fields), "
        f"{len(merged_homes) - matched_count} CQC only"
    )
    
    return merged_homes


def get_merge_statistics(
    cqc_homes: List[Dict[str, Any]],
    staging_list: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Получить статистику объединения данных.
    
    Args:
        cqc_homes: Список домов из CQC
        staging_list: Список данных Staging
        
    Returns:
        Dict со статистикой
    """
    from services.care_home_matcher import (
        build_staging_index_with_keys,
        match_cqc_to_staging
    )
    
    total_cqc = len(cqc_homes)
    total_staging = len(staging_list)
    
    # Build staging index for matching
    staging_index = build_staging_index_with_keys(staging_list)
    
    matched = 0
    matched_by_location_id = 0
    matched_by_fields = 0
    
    for cqc_home in cqc_homes:
        # Try location_id first
        location_id = (
            cqc_home.get('location_id') or 
            cqc_home.get('cqc_location_id') or
            cqc_home.get('id')
        )
        
        found = False
        if location_id:
            location_id = str(location_id).strip()
            for staging_record in staging_list:
                if staging_record.get('cqc_location_id') == location_id:
                    matched_by_location_id += 1
                    matched += 1
                    found = True
                    break
        
        # Try field-based matching
        if not found:
            staging_data = match_cqc_to_staging(cqc_home, staging_index)
            if staging_data:
                matched_by_fields += 1
                matched += 1
    
    cqc_only = total_cqc - matched
    staging_only = total_staging - matched
    
    return {
        'total_cqc': total_cqc,
        'total_staging': total_staging,
        'matched': matched,
        'matched_by_location_id': matched_by_location_id,
        'matched_by_fields': matched_by_fields,
        'cqc_only': cqc_only,
        'staging_only': staging_only,
        'match_rate': round(matched / total_cqc * 100, 1) if total_cqc > 0 else 0.0
    }


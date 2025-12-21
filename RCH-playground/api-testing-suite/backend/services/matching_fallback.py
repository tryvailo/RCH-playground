"""
Matching Fallback Logic: NULL handling and Proxy field checking

This module implements the two-level matching logic with fallbacks for handling
NULL values in database fields. NULL does not mean FALSE - it means "unknown",
so we use proxy fields to infer values.

Source: documents/report-algorithms/matching-fallback-logic.py
"""

from typing import Dict, List, Optional, Tuple, Any
from .matching_fallback_config import (
    MatchResult,
    FieldMatchResult,
    get_proxy_config
)
from .db_field_extractor import (
    get_service_user_band,
    get_regulated_activity,
    get_inspection_date,
    get_facility_value,
    get_staff_information,
    get_cqc_rating
)


def check_field_with_fallback(
    home: Dict[str, Any],
    field_name: str,
    required_value: bool = True
) -> FieldMatchResult:
    """
    Check a field with fallback to proxy fields if NULL.
    
    UPDATED: Now supports both flat fields and JSONB structures from DB.
    
    Three-level logic:
    - Level 1: Direct match (field has value TRUE/FALSE) - checks both flat and JSONB
    - Level 2: Proxy match (field is NULL, but proxy field indicates match)
    - Level 3: Unknown (field is NULL, no proxy available)
    
    Args:
        home: Care home data dictionary
        field_name: Primary field to check (e.g., 'serves_dementia_band')
        required_value: Expected value (usually True)
    
    Returns:
        FieldMatchResult with match status and confidence
    """
    # Get field configuration
    config = get_proxy_config(field_name)
    
    # ─────────────────────────────────────────────────────
    # ENHANCED: Check both flat field and JSONB structure
    # ─────────────────────────────────────────────────────
    primary_value = None
    
    # Map Service User Band fields to JSONB lookup
    service_band_mapping = {
        'serves_dementia_band': 'dementia_band',
        'serves_older_people': 'older_people',
        'serves_younger_adults': 'younger_adults',
        'serves_mental_health': 'mental_health',
        'serves_physical_disabilities': 'physical_disabilities',
        'serves_sensory_impairments': 'sensory_impairments',
        'serves_learning_disabilities': 'learning_disabilities',
        'serves_children': 'children',
        'serves_detained_mha': 'detained_mha',
        'serves_substance_misuse': 'substance_misuse',
        'serves_eating_disorders': 'eating_disorders',
        'serves_whole_population': 'whole_population'
    }
    
    # Map Regulated Activity fields to JSONB lookup
    regulated_activity_mapping = {
        'has_nursing_care_license': 'nursing_care',
        'has_personal_care_license': 'personal_care',
        'has_surgical_procedures_license': 'surgical_procedures',
        'has_treatment_license': 'treatment_disease',
        'has_diagnostic_license': 'diagnostic_screening'
    }
    
    # Try flat field first
    primary_value = home.get(field_name)
    
    # If NULL, try JSONB lookup
    if primary_value is None:
        if field_name in service_band_mapping:
            # Try JSONB service_user_bands
            band_name = service_band_mapping[field_name]
            primary_value = get_service_user_band(home, band_name)
        elif field_name in regulated_activity_mapping:
            # Try JSONB regulated_activities
            activity_id = regulated_activity_mapping[field_name]
            primary_value = get_regulated_activity(home, activity_id)
    
    # ─────────────────────────────────────────────────────
    # LEVEL 1: Direct match (field has value)
    # ─────────────────────────────────────────────────────
    if primary_value is not None:
        if primary_value == required_value:
            return FieldMatchResult(
                result=MatchResult.MATCH,
                field_checked=field_name,
                field_value=primary_value,
                confidence=1.0,
                score_multiplier=1.0
            )
        else:
            return FieldMatchResult(
                result=MatchResult.NO_MATCH,
                field_checked=field_name,
                field_value=primary_value,
                confidence=1.0,
                score_multiplier=0.0  # No score for explicit FALSE
            )
    
    # ─────────────────────────────────────────────────────
    # LEVEL 2: Proxy match (primary is NULL)
    # ─────────────────────────────────────────────────────
    for proxy in config.get('proxies', []):
        proxy_field = proxy['field']
        proxy_value = home.get(proxy_field)
        proxy_confidence = proxy['confidence']
        expected_condition = proxy.get('condition', True)
        
        if proxy_value is not None and proxy_value == expected_condition:
            # Proxy indicates likely match
            return FieldMatchResult(
                result=MatchResult.PROXY_MATCH,
                field_checked=field_name,
                field_value=None,
                proxy_used=proxy_field,
                proxy_value=proxy_value,
                confidence=proxy_confidence,
                score_multiplier=proxy_confidence  # Score based on confidence
            )
    
    # ─────────────────────────────────────────────────────
    # LEVEL 3: Unknown (no data available)
    # ─────────────────────────────────────────────────────
    return FieldMatchResult(
        result=MatchResult.UNKNOWN,
        field_checked=field_name,
        field_value=None,
        confidence=0.0,
        score_multiplier=config['null_penalty']  # Partial score
    )


def check_multiple_fields(
    home: Dict[str, Any],
    requirements: Dict[str, bool]
) -> Dict[str, FieldMatchResult]:
    """
    Check multiple fields at once.
    
    Args:
        home: Care home data dictionary
        requirements: Dict of {field_name: required_value}
    
    Returns:
        Dict of {field_name: FieldMatchResult}
    """
    results = {}
    for field, required in requirements.items():
        results[field] = check_field_with_fallback(home, field, required)
    return results


def check_care_types_v2(
    home: Dict[str, Any],
    required_care: List[str]
) -> Dict[str, Any]:
    """
    Check care types with NULL handling.
    
    Key difference: NULL means unknown, not FALSE.
    
    Args:
        home: Care home data dictionary
        required_care: List of required care types from questionnaire
        
    Returns:
        Dict with:
        - matched: List of matched care types
        - unknown: List of care types with NULL values
        - explicit_false: List of care types with FALSE values
        - has_explicit_false: Boolean indicating if any explicit FALSE found
    """
    from .matching_constants import CARE_TYPE_TO_DB_FIELD
    
    if not required_care:
        return {
            'matched': [],
            'unknown': [],
            'explicit_false': [],
            'has_explicit_false': False
        }
    
    matched = []
    unknown = []
    explicit_false = []
    
    for care in required_care:
        db_field = CARE_TYPE_TO_DB_FIELD.get(care)
        if not db_field:
            # No mapping for this care type (e.g., 'palliative')
            continue
        
        value = home.get(db_field)
        
        if value is True:
            matched.append(care)
        elif value is False:
            explicit_false.append(care)
        else:  # NULL
            unknown.append(care)
    
    return {
        'matched': matched,
        'unknown': unknown,
        'explicit_false': explicit_false,
        'has_explicit_false': len(explicit_false) > 0 and len(matched) == 0
    }


def evaluate_home_match_v2(
    home: Dict[str, Any],
    required_care: List[str],
    conditions: List[str],
    mobility: str,
    behavioral: List[str]
) -> Dict[str, Any]:
    """
    Evaluate home match with fallback logic.
    
    Key difference from v1:
    - NULL fields don't automatically disqualify
    - Proxy matches are considered
    - Confidence levels affect final score
    
    Args:
        home: Care home data dictionary
        required_care: List of required care types
        conditions: List of medical conditions
        mobility: Mobility level
        behavioral: List of behavioral concerns
        
    Returns:
        Dict with:
        - status: 'match' | 'partial' | 'uncertain' | 'disqualified'
        - score: float (0-100)
        - matched: List of matched requirements
        - partial: List of proxy matches
        - missing: List of missing requirements
        - unknown: List of unknown requirements
        - warnings: List of warnings
        - data_completeness: float (0-100)
    """
    from .matching_constants import (
        CONDITION_TO_SERVICE_BAND,
        BEHAVIORAL_TO_SERVICE_BAND,
        MOBILITY_TO_FIELDS
    )
    
    matched = []
    partial = []  # Proxy matches
    missing = []
    unknown = []
    warnings = []
    
    # ─────────────────────────────────────────────────────
    # 1. CARE TYPES (Critical - disqualify if explicit FALSE)
    # ─────────────────────────────────────────────────────
    care_result = check_care_types_v2(home, required_care)
    
    if care_result['has_explicit_false']:
        # Home explicitly doesn't provide required care
        return {
            'status': 'disqualified',
            'score': 0,
            'reason': f"Home does not provide: {care_result['explicit_false']}",
            'matched': matched,
            'missing': care_result['explicit_false'],
            'partial': [],
            'unknown': care_result['unknown'],
            'warnings': []
        }
    
    matched.extend(care_result['matched'])
    unknown.extend(care_result['unknown'])
    
    # ─────────────────────────────────────────────────────
    # 2. MEDICAL CONDITIONS
    # ─────────────────────────────────────────────────────
    critical_missing = []
    
    for condition in conditions:
        mapping = CONDITION_TO_SERVICE_BAND.get(condition)
        if not mapping:
            continue
        
        field = mapping.get('required_field')
        if not field:
            continue
        
        result = check_field_with_fallback(home, field, True)
        weight = mapping.get('weight', 'medium')
        
        if result.result == MatchResult.MATCH:
            matched.append(f"{condition}→{field}")
        elif result.result == MatchResult.PROXY_MATCH:
            partial.append(f"{condition}→{result.proxy_used} (proxy)")
        elif result.result == MatchResult.NO_MATCH:
            if weight == 'critical':
                critical_missing.append(condition)
            missing.append(f"{condition} ({weight})")
        else:  # UNKNOWN
            unknown.append(f"{condition}→{field}")
            if weight == 'critical':
                warnings.append(f"Cannot verify {condition} support - data unavailable")
    
    # ─────────────────────────────────────────────────────
    # 3. MOBILITY
    # ─────────────────────────────────────────────────────
    mobility_config = MOBILITY_TO_FIELDS.get(mobility, {})
    
    for field in mobility_config.get('required_fields', []):
        result = check_field_with_fallback(home, field, True)
        
        if result.result == MatchResult.MATCH:
            matched.append(f"mobility→{field}")
        elif result.result == MatchResult.PROXY_MATCH:
            partial.append(f"mobility→{result.proxy_used} (proxy)")
        elif result.result == MatchResult.NO_MATCH:
            if mobility_config.get('weight') == 'critical':
                critical_missing.append(f"{field} for {mobility}")
            missing.append(f"{field} ({mobility})")
        else:
            unknown.append(f"mobility→{field}")
            if mobility_config.get('weight') == 'critical':
                warnings.append(f"Cannot verify {field} - recommend calling home")
    
    # ─────────────────────────────────────────────────────
    # 4. BEHAVIORAL CONCERNS
    # ─────────────────────────────────────────────────────
    for concern in behavioral:
        mapping = BEHAVIORAL_TO_SERVICE_BAND.get(concern)
        if not mapping:
            continue
        
        field = mapping.get('required_field')
        if not field:
            continue
        
        result = check_field_with_fallback(home, field, True)
        
        if result.result == MatchResult.MATCH:
            matched.append(f"{concern}→{field}")
        elif result.result == MatchResult.PROXY_MATCH:
            partial.append(f"{concern}→{result.proxy_used} (proxy)")
        elif result.result == MatchResult.NO_MATCH:
            missing.append(f"{concern}")
        else:
            unknown.append(f"{concern}→{field}")
        
        # Check amenity requirement (e.g., secure_garden for wandering)
        amenity = mapping.get('amenity_required')
        if amenity:
            amenity_result = check_field_with_fallback(home, amenity, True)
            
            if amenity_result.result == MatchResult.MATCH:
                matched.append(f"{concern}→{amenity}")
            elif amenity_result.result == MatchResult.PROXY_MATCH:
                partial.append(f"{concern}→{amenity_result.proxy_used} (proxy)")
            elif amenity_result.result == MatchResult.NO_MATCH:
                missing.append(f"{concern}→{amenity}")
            else:
                unknown.append(f"{concern}→{amenity}")
                warnings.append(f"Cannot verify {amenity} for {concern}")
    
    # ─────────────────────────────────────────────────────
    # 5. DETERMINE STATUS
    # ─────────────────────────────────────────────────────
    
    # Critical missing with explicit FALSE = disqualify
    if critical_missing and any(
        check_field_with_fallback(
            home,
            CONDITION_TO_SERVICE_BAND.get(c, {}).get('required_field', ''),
            True
        ).result == MatchResult.NO_MATCH
        for c in critical_missing
        if c in CONDITION_TO_SERVICE_BAND
    ):
        return {
            'status': 'disqualified',
            'score': 0,
            'reason': f"Missing critical with explicit FALSE: {critical_missing}",
            'matched': matched,
            'partial': partial,
            'missing': missing,
            'unknown': unknown,
            'warnings': warnings
        }
    
    # Calculate confidence-adjusted score
    total = len(matched) + len(partial) + len(missing) + len(unknown)
    if total == 0:
        score = 100.0
    else:
        # Full points for matched, partial for proxy, penalty for missing
        points = (
            len(matched) * 1.0 +
            len(partial) * 0.75 +  # Proxy match = 75%
            len(unknown) * 0.5 +   # Unknown = 50% (benefit of doubt)
            len(missing) * 0.0      # Missing = 0%
        )
        score = (points / total) * 100
    
    # Determine status
    if missing and not unknown:
        status = 'partial'
    elif unknown and len(unknown) > len(matched):
        status = 'uncertain'  # Too much unknown data
    elif missing:
        status = 'partial'
    else:
        status = 'match'
    
    return {
        'status': status,
        'score': round(score, 1),
        'matched': matched,
        'partial': partial,
        'missing': missing,
        'unknown': unknown,
        'warnings': warnings,
        'data_completeness': round((len(matched) + len(partial)) / max(total, 1) * 100, 1)
    }


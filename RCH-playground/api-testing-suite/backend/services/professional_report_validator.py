"""
Validator for Professional Report Questionnaire

Validates questionnaire structure and data before processing.
"""

from typing import Dict, Any, List, Optional
import re


class QuestionnaireValidationError(Exception):
    """Raised when questionnaire validation fails"""
    pass


def validate_questionnaire(questionnaire: Dict[str, Any]) -> List[str]:
    """
    Validate questionnaire structure and data
    
    Args:
        questionnaire: Questionnaire data to validate
        
    Returns:
        List of validation errors (empty if valid)
        
    Raises:
        QuestionnaireValidationError: If validation fails
    """
    errors = []
    
    # Check required sections
    required_sections = [
        'section_1_contact_emergency',
        'section_2_location_budget',
        'section_3_medical_needs',
        'section_4_safety_special_needs',
        'section_5_timeline'
    ]
    
    for section in required_sections:
        if section not in questionnaire:
            errors.append(f"Missing required section: {section}")
            continue
        
        # Validate section-specific fields
        section_errors = _validate_section(section, questionnaire[section])
        errors.extend(section_errors)
    
    # Check q16_social_personality - can be in section_4 or section_5 (for backward compatibility)
    valid_personality = ['very_sociable', 'moderately_sociable', 'prefers_quiet', 'social']
    section_4 = questionnaire.get('section_4_safety_special_needs', {})
    section_5 = questionnaire.get('section_5_timeline', {})
    
    q16_in_section_4 = 'q16_social_personality' in section_4
    q16_in_section_5 = 'q16_social_personality' in section_5
    
    if not q16_in_section_4 and not q16_in_section_5:
        errors.append("q16_social_personality is required (in section_4_safety_special_needs or section_5_timeline)")
    elif q16_in_section_4:
        # Validate if in section_4
        if section_4.get('q16_social_personality') not in valid_personality:
            errors.append(f"q16_social_personality must be one of: {', '.join(valid_personality)}")
    elif q16_in_section_5:
        # Validate if in section_5
        if section_5.get('q16_social_personality') not in valid_personality:
            errors.append(f"q16_social_personality must be one of: {', '.join(valid_personality)}")
    
    if errors:
        raise QuestionnaireValidationError(f"Validation failed: {'; '.join(errors)}")
    
    return []


def _validate_section(section_name: str, section_data: Dict[str, Any]) -> List[str]:
    """Validate a specific section"""
    errors = []
    
    if section_name == 'section_1_contact_emergency':
        errors.extend(_validate_contact_section(section_data))
    elif section_name == 'section_2_location_budget':
        errors.extend(_validate_location_budget_section(section_data))
    elif section_name == 'section_3_medical_needs':
        errors.extend(_validate_medical_needs_section(section_data))
    elif section_name == 'section_4_safety_special_needs':
        errors.extend(_validate_safety_section(section_data))
    elif section_name == 'section_5_timeline':
        errors.extend(_validate_timeline_section(section_data))
    
    return errors


def _validate_contact_section(section: Dict[str, Any]) -> List[str]:
    """Validate contact & emergency section"""
    errors = []
    
    if 'q1_names' not in section or not section.get('q1_names'):
        errors.append("q1_names is required")
    
    if 'q2_email' not in section or not section.get('q2_email'):
        errors.append("q2_email is required")
    elif not _is_valid_email(section['q2_email']):
        errors.append("q2_email must be a valid email address")
    
    if 'q3_phone' not in section or not section.get('q3_phone'):
        errors.append("q3_phone is required")
    
    if 'q4_emergency_contact' not in section or not section.get('q4_emergency_contact'):
        errors.append("q4_emergency_contact is required")
    
    return errors


def _validate_location_budget_section(section: Dict[str, Any]) -> List[str]:
    """Validate location & budget section"""
    errors = []
    
    if 'q5_preferred_city' not in section or not section.get('q5_preferred_city'):
        errors.append("q5_preferred_city is required")
    
    valid_distances = ['within_5km', 'within_15km', 'within_30km', 'distance_not_important']
    # Also accept legacy formats: '5km', '10km', '15km', '20km', '30km'
    legacy_distances = ['5km', '10km', '15km', '20km', '30km']
    all_valid_distances = valid_distances + legacy_distances
    
    if 'q6_max_distance' not in section:
        errors.append("q6_max_distance is required")
    else:
        distance = section.get('q6_max_distance')
        if distance not in all_valid_distances:
            errors.append(f"q6_max_distance must be one of: {', '.join(valid_distances)} or legacy formats: {', '.join(legacy_distances)}")
        else:
            # Normalize legacy formats to standard format
            if distance == '5km':
                section['q6_max_distance'] = 'within_5km'
            elif distance in ['10km', '15km']:
                section['q6_max_distance'] = 'within_15km'
            elif distance in ['20km', '30km']:
                section['q6_max_distance'] = 'within_30km'
    
    valid_budgets = [
        'under_3000_self', 'under_3000_local',
        '3000_5000_self', '3000_5000_local',
        '5000_7000_self', '5000_7000_local',
        'over_7000_self', 'over_7000_local',
        'need_budget_guidance'
    ]
    if 'q7_budget' not in section:
        errors.append("q7_budget is required")
    elif section.get('q7_budget') not in valid_budgets:
        errors.append(f"q7_budget must be one of: {', '.join(valid_budgets)}")
    
    return errors


def _validate_medical_needs_section(section: Dict[str, Any]) -> List[str]:
    """Validate medical needs section"""
    errors = []
    
    valid_care_types = ['general_residential', 'medical_nursing', 'specialised_dementia', 'temporary_respite']
    if 'q8_care_types' not in section:
        errors.append("q8_care_types is required")
    elif not isinstance(section.get('q8_care_types'), list):
        errors.append("q8_care_types must be a list")
    elif not section.get('q8_care_types'):
        errors.append("q8_care_types cannot be empty")
    elif not all(ct in valid_care_types for ct in section.get('q8_care_types', [])):
        errors.append(f"q8_care_types must contain only: {', '.join(valid_care_types)}")
    
    valid_conditions = [
        'dementia_alzheimers', 'mobility_problems', 'diabetes',
        'heart_conditions', 'no_serious_medical'
    ]
    if 'q9_medical_conditions' not in section:
        errors.append("q9_medical_conditions is required")
    elif not isinstance(section.get('q9_medical_conditions'), list):
        errors.append("q9_medical_conditions must be a list")
    elif not section.get('q9_medical_conditions'):
        errors.append("q9_medical_conditions cannot be empty")
    elif not all(c in valid_conditions for c in section.get('q9_medical_conditions', [])):
        errors.append(f"q9_medical_conditions must contain only: {', '.join(valid_conditions)}")
    
    valid_mobility = ['fully_mobile', 'walking_aids', 'wheelchair_sometimes', 'wheelchair_permanent']
    if 'q10_mobility_level' not in section:
        errors.append("q10_mobility_level is required")
    elif section.get('q10_mobility_level') not in valid_mobility:
        errors.append(f"q10_mobility_level must be one of: {', '.join(valid_mobility)}")
    
    # Accept both old and new medication management values for backward compatibility
    valid_medication_old = ['none', 'simple_1_2', 'several_simple_routine', 'many_complex_routine']
    valid_medication_new = ['independent', 'reminders_needed', 'full_administration_required']
    valid_medication = valid_medication_old + valid_medication_new
    
    if 'q11_medication_management' not in section:
        errors.append("q11_medication_management is required")
    elif section.get('q11_medication_management') not in valid_medication:
        errors.append(f"q11_medication_management must be one of: {', '.join(valid_medication)}")
    
    valid_ages = ['65_74', '75_84', '85_94', '95_plus']
    if 'q12_age_range' not in section:
        errors.append("q12_age_range is required")
    elif section.get('q12_age_range') not in valid_ages:
        errors.append(f"q12_age_range must be one of: {', '.join(valid_ages)}")
    
    return errors


def _validate_safety_section(section: Dict[str, Any]) -> List[str]:
    """Validate safety & special needs section"""
    errors = []
    
    valid_fall_history = [
        'no_falls_occurred', '1_2_no_serious_injuries',
        '3_plus_or_serious_injuries', 'high_risk_of_falling'
    ]
    if 'q13_fall_history' not in section:
        errors.append("q13_fall_history is required")
    elif section.get('q13_fall_history') not in valid_fall_history:
        errors.append(f"q13_fall_history must be one of: {', '.join(valid_fall_history)}")
    
    valid_allergies = ['food_allergies', 'medication_allergies', 'environmental_allergies', 'no_allergies']
    if 'q14_allergies' not in section:
        errors.append("q14_allergies is required")
    elif not isinstance(section.get('q14_allergies'), list):
        errors.append("q14_allergies must be a list")
    # Allow empty array - user may have no allergies
    elif section.get('q14_allergies') and not all(a in valid_allergies for a in section.get('q14_allergies', [])):
        errors.append(f"q14_allergies must contain only: {', '.join(valid_allergies)}")
    
    valid_dietary = ['diabetic_diet', 'pureed_soft_food', 'vegetarian_vegan', 'no_special_requirements']
    if 'q15_dietary_requirements' not in section:
        errors.append("q15_dietary_requirements is required")
    elif not isinstance(section.get('q15_dietary_requirements'), list):
        errors.append("q15_dietary_requirements must be a list")
    # Allow empty array - user may have no special dietary requirements
    elif section.get('q15_dietary_requirements') and not all(d in valid_dietary for d in section.get('q15_dietary_requirements', [])):
        errors.append(f"q15_dietary_requirements must contain only: {', '.join(valid_dietary)}")
    
    # q16_social_personality can be in section_4 (frontend sends it here) or section_5
    # Check here for backward compatibility with frontend
    valid_personality = ['very_sociable', 'moderately_sociable', 'prefers_quiet', 'social']
    if 'q16_social_personality' in section:
        if section.get('q16_social_personality') not in valid_personality:
            errors.append(f"q16_social_personality must be one of: {', '.join(valid_personality)}")
    
    return errors


def _validate_timeline_section(section: Dict[str, Any]) -> List[str]:
    """Validate timeline section"""
    errors = []
    
    valid_timelines = [
        'urgent_2_weeks', 'next_month',
        'planning_2_3_months', 'exploring_6_plus_months'
    ]
    if 'q17_placement_timeline' not in section:
        errors.append("q17_placement_timeline is required")
    elif section.get('q17_placement_timeline') not in valid_timelines:
        errors.append(f"q17_placement_timeline must be one of: {', '.join(valid_timelines)}")
    
    return errors


def _is_valid_email(email: str) -> bool:
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


# ============================================================================
# Care Home Basic Information Validation (Section 1-5)
# ============================================================================

class BasicHomeInfoValidationError(Exception):
    """Raised when basic home information validation fails"""
    pass


class BasicHomeInfoValidationResult:
    """Result of basic home information validation"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.is_valid: bool = True
    
    def add_error(self, field: str, message: str):
        """Add a validation error"""
        self.errors.append(f"{field}: {message}")
        self.is_valid = False
    
    def add_warning(self, field: str, message: str):
        """Add a validation warning (non-critical)"""
        self.warnings.append(f"{field}: {message}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }


def validate_basic_home_info(home: Dict[str, Any], home_name: Optional[str] = None) -> BasicHomeInfoValidationResult:
    """
    Validate basic home information (Section 1-5) according to PROFESSIONAL_REPORT_SPEC_v3.2
    
    Validates required fields:
    - Section 1 (Identity): cqc_location_id, name
    - Section 2 (Address): city, postcode, latitude, longitude
    - Section 4 (Capacity): has_availability
    
    Args:
        home: Care home data dictionary
        home_name: Optional name for logging (if not in home dict)
        
    Returns:
        BasicHomeInfoValidationResult with validation results
    """
    result = BasicHomeInfoValidationResult()
    
    # Extract name for logging
    display_name = home_name or home.get('name') or home.get('cqc_location_id') or 'Unknown'
    
    # Helper to get value from various possible field names
    def get_field_value(field_variants: List[str]) -> Optional[Any]:
        """Try multiple field name variants"""
        for variant in field_variants:
            value = home.get(variant)
            if value is not None and value != '':
                return value
        return None
    
    # ========================================================================
    # Section 1: Identity (REQUIRED FIELDS)
    # ========================================================================
    
    # cqc_location_id (REQUIRED)
    cqc_location_id = get_field_value([
        'cqc_location_id',
        'location_id',
        'id',
        'cqcLocationId',
        'locationId'
    ])
    if not cqc_location_id:
        result.add_error(
            'cqc_location_id',
            'Required field missing. Must be present for care home identification.'
        )
    elif not isinstance(cqc_location_id, str) or len(cqc_location_id.strip()) == 0:
        result.add_error(
            'cqc_location_id',
            'Must be a non-empty string.'
        )
    
    # name (REQUIRED)
    name = get_field_value(['name', 'care_home_name', 'home_name'])
    if not name:
        result.add_error(
            'name',
            'Required field missing. Care home name is essential for identification.'
        )
    elif not isinstance(name, str) or len(name.strip()) == 0:
        result.add_error(
            'name',
            'Must be a non-empty string.'
        )
    
    # ========================================================================
    # Section 2: Address (REQUIRED FIELDS)
    # ========================================================================
    
    # city (REQUIRED)
    city = get_field_value(['city', 'town', 'location'])
    if not city:
        result.add_error(
            'city',
            'Required field missing. City/town is essential for location matching.'
        )
    elif not isinstance(city, str) or len(city.strip()) == 0:
        result.add_error(
            'city',
            'Must be a non-empty string.'
        )
    
    # postcode (REQUIRED)
    postcode = get_field_value(['postcode', 'postal_code', 'post_code'])
    if not postcode:
        result.add_error(
            'postcode',
            'Required field missing. Postcode is essential for location matching and distance calculations.'
        )
    elif not isinstance(postcode, str) or len(postcode.strip()) == 0:
        result.add_error(
            'postcode',
            'Must be a non-empty string.'
        )
    elif not _is_valid_uk_postcode(postcode):
        result.add_warning(
            'postcode',
            f'Postcode format may be invalid: {postcode}. Expected UK postcode format.'
        )
    
    # latitude (REQUIRED)
    latitude = get_field_value(['latitude', 'lat'])
    if latitude is None:
        result.add_error(
            'latitude',
            'Required field missing. Latitude is essential for distance calculations and map display.'
        )
    else:
        try:
            lat_float = float(latitude)
            if not (-90 <= lat_float <= 90):
                result.add_error(
                    'latitude',
                    f'Invalid value: {latitude}. Must be between -90 and 90.'
                )
        except (ValueError, TypeError):
            result.add_error(
                'latitude',
                f'Invalid type: {type(latitude)}. Must be a number.'
            )
    
    # longitude (REQUIRED)
    longitude = get_field_value(['longitude', 'lon', 'lng'])
    if longitude is None:
        result.add_error(
            'longitude',
            'Required field missing. Longitude is essential for distance calculations and map display.'
        )
    else:
        try:
            lon_float = float(longitude)
            if not (-180 <= lon_float <= 180):
                result.add_error(
                    'longitude',
                    f'Invalid value: {longitude}. Must be between -180 and 180.'
                )
        except (ValueError, TypeError):
            result.add_error(
                'longitude',
                f'Invalid type: {type(longitude)}. Must be a number.'
            )
    
    # ========================================================================
    # Section 4: Capacity (REQUIRED FIELDS)
    # ========================================================================
    
    # has_availability (REQUIRED)
    has_availability = get_field_value(['has_availability', 'hasAvailability', 'available'])
    if has_availability is None:
        result.add_error(
            'has_availability',
            'Required field missing. Availability status is essential for matching algorithm.'
        )
    elif not isinstance(has_availability, bool):
        # Try to convert to bool if it's a string or number
        if isinstance(has_availability, str):
            has_availability_lower = has_availability.lower()
            if has_availability_lower in ['true', 'yes', '1', 'available']:
                result.add_warning(
                    'has_availability',
                    f'String value "{has_availability}" converted to boolean. Should be boolean type.'
                )
            elif has_availability_lower in ['false', 'no', '0', 'unavailable']:
                result.add_warning(
                    'has_availability',
                    f'String value "{has_availability}" converted to boolean. Should be boolean type.'
                )
            else:
                result.add_error(
                    'has_availability',
                    f'Invalid value: {has_availability}. Must be a boolean (true/false).'
                )
        else:
            result.add_error(
                'has_availability',
                f'Invalid type: {type(has_availability)}. Must be a boolean.'
            )
    
    # ========================================================================
    # Optional Fields (Warnings only)
    # ========================================================================
    
    # Section 1: Optional contact fields
    telephone = get_field_value(['telephone', 'phone', 'contact_phone'])
    if not telephone:
        result.add_warning(
            'telephone',
            'Optional field missing. Contact phone number recommended for user convenience.'
        )
    
    # Section 2: Optional address fields
    county = get_field_value(['county', 'region'])
    if not county:
        result.add_warning(
            'county',
            'Optional field missing. County/region recommended for better location context.'
        )
    
    local_authority = get_field_value(['local_authority', 'localAuthority', 'council'])
    if not local_authority:
        result.add_warning(
            'local_authority',
            'Optional field missing. Local authority recommended for funding options analysis.'
        )
    
    # Section 3: Optional provider fields
    provider_name = get_field_value(['provider_name', 'providerName', 'provider'])
    if not provider_name:
        result.add_warning(
            'provider_name',
            'Optional field missing. Provider name recommended for provider-level analysis.'
        )
    
    # Section 4: Optional capacity fields
    beds_total = get_field_value(['beds_total', 'bedsTotal', 'total_beds', 'capacity'])
    if beds_total is None:
        result.add_warning(
            'beds_total',
            'Optional field missing. Total beds recommended for capacity analysis.'
        )
    elif beds_total is not None:
        try:
            beds_int = int(beds_total)
            if beds_int <= 0:
                result.add_warning(
                    'beds_total',
                    f'Invalid value: {beds_total}. Should be a positive number.'
                )
        except (ValueError, TypeError):
            result.add_warning(
                'beds_total',
                f'Invalid type: {type(beds_total)}. Should be an integer.'
            )
    
    # Section 5: Optional pricing fields
    has_pricing = any([
        get_field_value(['fee_residential_from', 'feeResidentialFrom', 'residential_fee']),
        get_field_value(['fee_nursing_from', 'feeNursingFrom', 'nursing_fee']),
        get_field_value(['fee_dementia_from', 'feeDementiaFrom', 'dementia_fee']),
        get_field_value(['fee_respite_from', 'feeRespiteFrom', 'respite_fee']),
    ])
    if not has_pricing:
        result.add_warning(
            'pricing',
            'No pricing information found. At least one fee field recommended for cost analysis.'
        )
    
    return result


def _is_valid_uk_postcode(postcode: str) -> bool:
    """
    Basic UK postcode validation
    
    UK postcode format:
    - Area: 1-2 letters
    - District: 1-2 digits + optional letter
    - Space
    - Sector: 1 digit
    - Unit: 2 letters
    
    Examples: SW1A 1AA, M1 1AA, B33 8TH
    """
    # Remove spaces and convert to uppercase
    postcode_clean = postcode.replace(' ', '').upper()
    
    # Basic pattern: 5-7 characters, alphanumeric
    if len(postcode_clean) < 5 or len(postcode_clean) > 7:
        return False
    
    # More detailed pattern matching
    # Area: 1-2 letters
    # District: 1-2 digits + optional letter
    # Sector: 1 digit
    # Unit: 2 letters
    pattern = r'^[A-Z]{1,2}[0-9]{1,2}[A-Z]?[0-9][A-Z]{2}$'
    return bool(re.match(pattern, postcode_clean))


def validate_care_homes_batch(homes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate a batch of care homes
    
    Args:
        homes: List of care home dictionaries
        
    Returns:
        Dictionary with validation summary
    """
    results = []
    total_errors = 0
    total_warnings = 0
    valid_count = 0
    invalid_count = 0
    
    for home in homes:
        home_name = home.get('name') or home.get('cqc_location_id') or 'Unknown'
        result = validate_basic_home_info(home, home_name)
        results.append({
            'home_name': home_name,
            'cqc_location_id': home.get('cqc_location_id') or home.get('location_id'),
            'validation': result.to_dict()
        })
        
        if result.is_valid:
            valid_count += 1
        else:
            invalid_count += 1
        
        total_errors += len(result.errors)
        total_warnings += len(result.warnings)
    
    return {
        'total_homes': len(homes),
        'valid_homes': valid_count,
        'invalid_homes': invalid_count,
        'total_errors': total_errors,
        'total_warnings': total_warnings,
        'results': results
    }


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
    
    valid_medication = ['none', 'simple_1_2', 'several_simple_routine', 'many_complex_routine']
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
    elif not section.get('q14_allergies'):
        errors.append("q14_allergies cannot be empty")
    elif not all(a in valid_allergies for a in section.get('q14_allergies', [])):
        errors.append(f"q14_allergies must contain only: {', '.join(valid_allergies)}")
    
    valid_dietary = ['diabetic_diet', 'pureed_soft_food', 'vegetarian_vegan', 'no_special_requirements']
    if 'q15_dietary_requirements' not in section:
        errors.append("q15_dietary_requirements is required")
    elif not isinstance(section.get('q15_dietary_requirements'), list):
        errors.append("q15_dietary_requirements must be a list")
    elif not section.get('q15_dietary_requirements'):
        errors.append("q15_dietary_requirements cannot be empty")
    elif not all(d in valid_dietary for d in section.get('q15_dietary_requirements', [])):
        errors.append(f"q15_dietary_requirements must contain only: {', '.join(valid_dietary)}")
    
    valid_personality = ['very_sociable', 'moderately_sociable', 'prefers_quiet']
    if 'q16_social_personality' not in section:
        errors.append("q16_social_personality is required")
    elif section.get('q16_social_personality') not in valid_personality:
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


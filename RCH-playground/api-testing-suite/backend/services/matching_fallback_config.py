"""
Matching Fallback Configuration: NULL handling and Proxy fields

This module defines the fallback logic for handling NULL values in database fields.
NULL does not mean FALSE - it means "unknown", so we use proxy fields to infer values.

Source: documents/report-algorithms/matching-fallback-logic.py
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, List, Any


class MatchResult(Enum):
    """Result of field matching."""
    MATCH = "match"              # Field = TRUE, requirement met
    NO_MATCH = "no_match"        # Field = FALSE, requirement NOT met
    PROXY_MATCH = "proxy_match"  # Primary NULL, but proxy indicates match
    PROXY_LIKELY = "proxy_likely" # Proxy suggests likely match (less confident)
    UNKNOWN = "unknown"          # No data available
    NOT_REQUIRED = "not_required" # User didn't request this


@dataclass
class FieldMatchResult:
    """Detailed result of a field match check."""
    result: MatchResult
    field_checked: str
    field_value: Optional[bool]
    proxy_used: Optional[str] = None
    proxy_value: Optional[bool] = None
    confidence: float = 1.0  # 0.0 to 1.0
    score_multiplier: float = 1.0


# =============================================================================
# FIELD PROXY CONFIGURATION
# =============================================================================
# Defines proxy fields and confidence levels for each Service User Band field
# =============================================================================

FIELD_PROXY_CONFIG: Dict[str, Dict[str, Any]] = {
    # Service User Bands
    'serves_dementia_band': {
        'proxies': [
            {'field': 'care_dementia', 'confidence': 0.9, 'condition': True},
            {'field': 'care_nursing', 'confidence': 0.5, 'condition': True},
        ],
        'null_penalty': 0.7,  # Score multiplier when NULL and no proxy
        'description': 'Serves people with dementia'
    },
    
    'serves_mental_health': {
        'proxies': [
            {'field': 'care_nursing', 'confidence': 0.6, 'condition': True},
            {'field': 'serves_whole_population', 'confidence': 0.4, 'condition': True},
        ],
        'null_penalty': 0.7,
        'description': 'Serves people with mental health needs'
    },
    
    'serves_physical_disabilities': {
        'proxies': [
            {'field': 'wheelchair_access', 'confidence': 0.8, 'condition': True},
            {'field': 'care_nursing', 'confidence': 0.6, 'condition': True},
            {'field': 'serves_older_people', 'confidence': 0.5, 'condition': True},
        ],
        'null_penalty': 0.7,
        'description': 'Serves people with physical disabilities'
    },
    
    'serves_sensory_impairments': {
        'proxies': [
            {'field': 'serves_older_people', 'confidence': 0.6, 'condition': True},
            {'field': 'serves_physical_disabilities', 'confidence': 0.5, 'condition': True},
        ],
        'null_penalty': 0.75,
        'description': 'Serves people with sensory impairments'
    },
    
    'serves_learning_disabilities': {
        'proxies': [
            {'field': 'serves_younger_adults', 'confidence': 0.5, 'condition': True},
        ],
        'null_penalty': 0.6,
        'description': 'Serves people with learning disabilities'
    },
    
    'serves_older_people': {
        'proxies': [
            {'field': 'serves_whole_population', 'confidence': 0.8, 'condition': True},
            {'field': 'care_dementia', 'confidence': 0.6, 'condition': True},
        ],
        'null_penalty': 0.7,
        'description': 'Serves people 65+'
    },
    
    'serves_younger_adults': {
        'proxies': [
            {'field': 'serves_whole_population', 'confidence': 0.8, 'condition': True},
        ],
        'null_penalty': 0.7,
        'description': 'Serves adults 18-64'
    },
    
    # Amenities
    'wheelchair_access': {
        'proxies': [
            {'field': 'serves_physical_disabilities', 'confidence': 0.7, 'condition': True},
            {'field': 'care_nursing', 'confidence': 0.6, 'condition': True},
        ],
        'null_penalty': 0.6,  # Lower penalty - common amenity
        'description': 'Wheelchair accessible'
    },
    
    'secure_garden': {
        'proxies': [
            {'field': 'serves_dementia_band', 'confidence': 0.8, 'condition': True},
            {'field': 'care_dementia', 'confidence': 0.8, 'condition': True},
        ],
        'null_penalty': 0.7,
        'description': 'Has secure garden'
    },
    
    'ensuite_rooms': {
        'proxies': [],  # No good proxy
        'null_penalty': 0.8,  # Most homes have ensuite nowadays
        'description': 'Has ensuite rooms'
    },
    
    # Licenses
    'has_nursing_care_license': {
        'proxies': [
            {'field': 'care_nursing', 'confidence': 0.95, 'condition': True},
        ],
        'null_penalty': 0.5,  # Important field
        'description': 'Licensed for nursing care'
    },
    
    'has_personal_care_license': {
        'proxies': [
            {'field': 'care_residential', 'confidence': 0.9, 'condition': True},
        ],
        'null_penalty': 0.8,
        'description': 'Licensed for personal care'
    },
    
    'has_surgical_procedures_license': {
        'proxies': [
            {'field': 'care_nursing', 'confidence': 0.7, 'condition': True},
            {'field': 'has_nursing_care_license', 'confidence': 0.6, 'condition': True},
        ],
        'null_penalty': 0.6,
        'description': 'Licensed for surgical procedures'
    },
    
    'has_treatment_license': {
        'proxies': [
            {'field': 'care_nursing', 'confidence': 0.7, 'condition': True},
            {'field': 'has_nursing_care_license', 'confidence': 0.6, 'condition': True},
        ],
        'null_penalty': 0.6,
        'description': 'Licensed for treatment of disease/disorder/injury'
    },
    
    'has_diagnostic_license': {
        'proxies': [
            {'field': 'care_nursing', 'confidence': 0.6, 'condition': True},
            {'field': 'has_nursing_care_license', 'confidence': 0.5, 'condition': True},
        ],
        'null_penalty': 0.6,
        'description': 'Licensed for diagnostic and screening procedures'
    },
}


def get_proxy_config(field_name: str) -> Dict[str, Any]:
    """
    Get proxy configuration for a field.
    
    Args:
        field_name: Name of the field to get configuration for
        
    Returns:
        Configuration dict with 'proxies', 'null_penalty', and 'description'
    """
    return FIELD_PROXY_CONFIG.get(field_name, {
        'proxies': [],
        'null_penalty': 0.7,  # Default penalty
        'description': field_name
    })


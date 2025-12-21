"""
Matching Constants: Questionnaire → Database Fields Mapping

This module defines the mapping between questionnaire answers and database fields,
specifically for Service User Bands matching.

Source: documents/report-algorithms/cursor-context-doc.md
"""

# =============================================================================
# Q9: Medical Conditions → DB Service User Bands
# =============================================================================

CONDITION_TO_SERVICE_BAND = {
    'dementia_alzheimers': {
        'required_field': 'serves_dementia_band',
        'weight': 'critical',  # Must match
        'fallback_fields': ['care_dementia']
    },
    'parkinsons': {
        'required_field': 'serves_physical_disabilities',
        'weight': 'high',
        'fallback_fields': []
    },
    'stroke_recovery': {
        'required_field': 'serves_physical_disabilities',
        'weight': 'high',
        'fallback_fields': []
    },
    'heart_conditions': {
        'required_field': None,  # No direct mapping
        'weight': 'medium',
        'fallback_fields': ['has_nursing_care_license']
    },
    'diabetes': {
        'required_field': None,
        'weight': 'low',
        'fallback_fields': []
    },
    'arthritis': {
        'required_field': 'serves_physical_disabilities',
        'weight': 'medium',
        'fallback_fields': []
    },
    'visual_impairment': {
        'required_field': 'serves_sensory_impairments',
        'weight': 'high',
        'fallback_fields': []
    },
    'hearing_impairment': {
        'required_field': 'serves_sensory_impairments',
        'weight': 'medium',
        'fallback_fields': []
    },
    'mobility_problems': {
        'required_field': 'serves_physical_disabilities',
        'weight': 'high',
        'fallback_fields': []
    },
    'no_serious_medical': {
        'required_field': None,
        'weight': 'none',
        'fallback_fields': []
    }
}

# =============================================================================
# Q16: Behavioral Concerns → DB Service User Bands
# =============================================================================

BEHAVIORAL_TO_SERVICE_BAND = {
    'anxiety': {
        'required_field': 'serves_mental_health',
        'weight': 'medium'
    },
    'depression': {
        'required_field': 'serves_mental_health',
        'weight': 'medium'
    },
    'wandering_risk': {
        'required_field': 'serves_dementia_band',
        'weight': 'critical',
        'amenity_required': 'secure_garden'
    },
    'sundowning': {
        'required_field': 'serves_dementia_band',
        'weight': 'high'
    },
    'aggression_risk': {
        'required_field': 'serves_mental_health',
        'weight': 'high'
    },
    'social_withdrawal': {
        'required_field': 'serves_mental_health',
        'weight': 'low'
    },
    'no_behavioral_concerns': {
        'required_field': None,
        'weight': 'none'
    }
}

# =============================================================================
# Q10: Mobility Level → DB Fields
# =============================================================================

MOBILITY_TO_FIELDS = {
    'fully_independent': {
        'required_fields': [],
        'preferred_fields': [],
        'weight': 'none'
    },
    'uses_walking_aid': {
        'required_fields': [],
        'preferred_fields': [],
        'weight': 'low'
    },
    'wheelchair_user': {
        'required_fields': ['wheelchair_access'],
        'preferred_fields': ['serves_physical_disabilities'],
        'weight': 'critical'
    },
    'wheelchair_bound': {  # Alias
        'required_fields': ['wheelchair_access'],
        'preferred_fields': ['serves_physical_disabilities'],
        'weight': 'critical'
    },
    'limited_mobility': {  # Alias
        'required_fields': ['wheelchair_access'],
        'preferred_fields': ['serves_physical_disabilities'],
        'weight': 'high'
    },
    'bed_bound': {
        'required_fields': ['has_nursing_care_license'],
        'preferred_fields': ['serves_physical_disabilities'],
        'weight': 'critical'
    }
}

# =============================================================================
# Q12/Q13: Age Range → DB Service User Bands
# =============================================================================

AGE_TO_SERVICE_BAND = {
    'under_65': 'serves_younger_adults',
    '65_74': 'serves_older_people',
    '75_84': 'serves_older_people',
    '85_94': 'serves_older_people',
    '95_plus': 'serves_older_people'
}

# =============================================================================
# Weight values for scoring
# =============================================================================

WEIGHT_VALUES = {
    'critical': 1.0,   # Must match, severe penalty if not
    'high': 0.8,
    'medium': 0.5,
    'low': 0.3,
    'none': 0.0
}

# =============================================================================
# Q8: Care Types → DB Fields (for reference)
# =============================================================================

CARE_TYPE_TO_DB_FIELD = {
    'residential': 'care_residential',
    'general_residential': 'care_residential',
    'nursing': 'care_nursing',
    'medical_nursing': 'care_nursing',
    'dementia': 'care_dementia',
    'specialised_dementia': 'care_dementia',
    'respite': 'care_respite',
    'respite_care': 'care_respite',
    'palliative': None  # No direct mapping - use proxy
}


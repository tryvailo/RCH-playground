"""
Scoring Constants
Constants for scoring calculations to avoid magic numbers
"""
from typing import Dict


class ScoringRatios:
    """Ratios for scoring calculations"""
    # Care Type Match ratios
    CLOSE_MATCH_RATIO = 0.67  # 67% of max score for close matches
    GENERAL_MATCH_RATIO = 0.33  # 33% of max score for general matches
    
    # CQC Rating ratios
    GOOD_RATING_RATIO = 0.8  # 80% of max score for Good CQC rating
    REQUIRES_IMPROVEMENT_RATIO = 0.4  # 40% of max score for Requires Improvement
    
    # Availability ratios
    LIMITED_AVAILABILITY_RATIO = 0.5  # 50% of max score for limited availability
    
    # Budget ratios
    NEUTRAL_BUDGET_RATIO = 0.5  # 50% of max score when no budget specified


class DefaultScores:
    """Default scores for various scenarios"""
    # Location defaults
    LOCATION_DEFAULT = 5  # Default score when coordinates missing
    LOCATION_NO_COORDS = 5  # Score when no coordinates available
    
    # Budget defaults
    BUDGET_NEUTRAL = 10  # Neutral score when no budget specified
    
    # Care Type defaults
    CARE_TYPE_GENERAL = 5  # General match score
    
    # Availability defaults
    AVAILABILITY_NONE = 0  # No availability data
    AVAILABILITY_FULL = 0  # Full / no beds available
    
    # CQC defaults
    CQC_NONE = 0  # No CQC rating
    CQC_INADEQUATE = 0  # Inadequate rating
    
    # Google Reviews defaults
    GOOGLE_REVIEWS_NONE = 0  # No Google rating


class ScoringBaseMax:
    """Base maximum scores for scaling calculations"""
    LOCATION_BASE_MAX = 20
    CQC_BASE_MAX = 25
    BUDGET_BASE_MAX = 20
    CARE_TYPE_BASE_MAX = 15
    AVAILABILITY_BASE_MAX = 10
    GOOGLE_REVIEWS_BASE_MAX = 10


class ScoringPresets:
    """
    Scoring presets for FREE Report
    
    Available presets:
    - CURRENT (100 points): Google Reviews focused, current implementation
    - SPEC_V3 (50 points): Matches specification v3.0 exactly
    """
    
    # Preset 1: CURRENT (100 points) - includes Google Reviews
    CURRENT = {
        'name': 'current',
        'total_points': 100,
        'description': 'Current implementation with Google Reviews',
        'weights': {
            'location': 20,
            'cqc': 25,
            'budget': 20,
            'careType': 15,
            'availability': 10,
            'googleReviews': 10,
        },
        'thresholds': {
            'location': {
                'within5Miles': 20,
                'within10Miles': 15,
                'within15Miles': 10,
                'over15Miles': 5,
            },
            'budget': {
                'withinBudget': 20,
                'plus50': 20,
                'plus100': 15,
                'plus200': 10,
            },
            'googleReviews': {
                'highRating': 10,
                'goodRatingManyReviews': 7,
                'goodRatingFewReviews': 5,
                'mediumRatingMany': 4,
                'mediumRatingFew': 2,
            },
        },
    }
    
    # Preset 2: SPEC_V3 (50 points) - matches specification v3.0
    SPEC_V3 = {
        'name': 'spec_v3',
        'total_points': 50,
        'description': 'Specification v3.0 compliant (50-point algorithm)',
        'weights': {
            'medical': 10,      # Medical Match (care type + conditions)
            'safety': 10,       # Safety Score (CQC Safe + FSA bonus)
            'location': 8,      # Location Score
            'budget': 8,        # Budget Fit
            'quality': 8,       # Quality Rating (CQC Overall)
            'availability': 6,  # Availability
        },
        'thresholds': {
            'location': {
                'within5km': 8,
                'within15km': 6,
                'within30km': 4,
                'over30km': 0,
            },
            'budget': {
                'withinBudget': 8,
                'plus50': 6,
                'plus100': 4,
                'plus200': 0,
            },
            'safety': {
                'excellent': 10,  # CQC Safe Excellent
                'good': 8,        # CQC Safe Good
                'improvement': 5, # Requires Improvement
                'inadequate': 0,
                'fsa_5': 1,       # FSA 5/5 bonus
                'fsa_3_below': -1, # FSA 3/5 or below penalty
            },
            'quality': {
                'outstanding': 8,
                'good': 6,
                'improvement': 0,  # Don't show
                'inadequate': 0,   # Never shown
            },
        },
    }
    
    @classmethod
    def get_preset(cls, name: str) -> dict:
        """Get scoring preset by name"""
        presets = {
            'current': cls.CURRENT,
            'spec_v3': cls.SPEC_V3,
        }
        return presets.get(name.lower(), cls.CURRENT)
    
    @classmethod
    def list_presets(cls) -> list:
        """List available preset names"""
        return ['current', 'spec_v3']


class ScoringDefaults:
    """Default scoring configuration (uses CURRENT preset)"""
    DEFAULT_WEIGHTS: Dict[str, int] = ScoringPresets.CURRENT['weights']
    
    DEFAULT_THRESHOLDS: Dict[str, Dict[str, int]] = ScoringPresets.CURRENT['thresholds']


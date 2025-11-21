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


class ScoringDefaults:
    """Default scoring configuration"""
    DEFAULT_WEIGHTS: Dict[str, int] = {
        'location': 20,
        'cqc': 25,
        'budget': 20,
        'careType': 15,
        'availability': 10,
        'googleReviews': 10,
    }
    
    DEFAULT_THRESHOLDS: Dict[str, Dict[str, int]] = {
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
    }


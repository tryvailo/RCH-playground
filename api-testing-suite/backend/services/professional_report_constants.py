"""
Constants for Professional Report Scoring

Centralized constants to avoid magic numbers and improve maintainability.
"""


class ScoringConstants:
    """Scoring thresholds and constants"""
    
    # Financial Stability Thresholds
    EXCELLENT_MARGIN = 0.15  # 15%+
    GOOD_MARGIN = 0.10  # 10-15%
    AVERAGE_MARGIN = 0.05  # 5-10%
    MIN_MARGIN = 0.0  # 0-5%
    
    # Working Capital Thresholds
    EXCELLENT_CURRENT_RATIO = 2.0
    GOOD_CURRENT_RATIO = 1.5
    MIN_CURRENT_RATIO = 1.0
    
    # Altman Z-Score Thresholds
    HIGH_RISK_Z_SCORE = 1.8
    MEDIUM_RISK_Z_SCORE = 2.5
    LOW_RISK_Z_SCORE = 3.0
    
    # Distance Thresholds (miles)
    CLOSE_DISTANCE = 5.0
    MEDIUM_DISTANCE = 15.0
    FAR_DISTANCE = 30.0
    
    # Distance Conversions (km to miles)
    KM_5_TO_MILES = 3.1
    KM_15_TO_MILES = 9.3
    KM_30_TO_MILES = 18.6
    
    # Rating Thresholds
    EXCELLENT_RATING = 4.5
    GOOD_RATING = 4.0
    AVERAGE_RATING = 3.5
    MIN_RATING = 3.0
    
    # Staff Quality Thresholds
    EXCELLENT_TENURE_YEARS = 5.0
    GOOD_TENURE_YEARS = 3.0
    AVERAGE_TENURE_YEARS = 2.0
    MIN_TENURE_YEARS = 1.0
    
    # Turnover Rate Thresholds
    VERY_HIGH_TURNOVER = 0.5  # 50%+
    HIGH_TURNOVER = 0.3  # 30-50%
    MEDIUM_TURNOVER = 0.2  # 20-30%
    LOW_TURNOVER = 0.1  # 10-20%
    
    # Review Count Thresholds
    HIGH_REVIEW_COUNT = 50
    MEDIUM_REVIEW_COUNT = 20
    LOW_REVIEW_COUNT = 10
    
    # Dwell Time Thresholds (minutes)
    LONG_DWELL_TIME = 60
    MEDIUM_DWELL_TIME = 30
    SHORT_DWELL_TIME = 15
    
    # Repeat Visitor Rate Thresholds
    HIGH_REPEAT_RATE = 0.5
    MEDIUM_REPEAT_RATE = 0.3
    
    # Transport Distance Thresholds (meters)
    BUS_STOP_CLOSE = 400
    TRAIN_STATION_CLOSE = 1000
    
    # Emergency Response Time Thresholds (minutes)
    FAST_RESPONSE_TIME = 5
    MEDIUM_RESPONSE_TIME = 10
    
    # RN Count Thresholds
    HIGH_RN_COUNT = 3
    MIN_RN_COUNT = 1
    
    # Activity Count Thresholds
    MANY_ACTIVITIES = 5
    SOME_ACTIVITIES = 3
    FEW_ACTIVITIES = 1
    
    # Specialist Program Thresholds
    MULTIPLE_PROGRAMS = 2
    
    # Enrichment Activities Thresholds
    MANY_ENRICHMENT = 5
    SOME_ENRICHMENT = 3


class CQCRatingMap:
    """CQC rating to score mapping"""
    OUTSTANDING = 4
    GOOD = 3
    REQUIRES_IMPROVEMENT = 1
    INADEQUATE = 0
    
    @classmethod
    def get_score(cls, rating: str) -> int:
        """Get score for CQC rating"""
        rating_upper = rating.capitalize()
        if rating_upper == 'Outstanding':
            return cls.OUTSTANDING
        elif rating_upper == 'Good':
            return cls.GOOD
        elif rating_upper == 'Requires improvement':
            return cls.REQUIRES_IMPROVEMENT
        elif rating_upper == 'Inadequate':
            return cls.INADEQUATE
        return cls.GOOD  # Default


class FSARatingMap:
    """FSA rating to score mapping"""
    RATING_5 = 8.0
    RATING_4 = 6.0
    RATING_3 = 4.0
    RATING_2 = 2.0
    RATING_1 = 0.0
    
    @classmethod
    def get_score(cls, rating: int) -> float:
        """Get score for FSA rating"""
        if rating >= 5:
            return cls.RATING_5
        elif rating >= 4:
            return cls.RATING_4
        elif rating >= 3:
            return cls.RATING_3
        elif rating >= 2:
            return cls.RATING_2
        return cls.RATING_1


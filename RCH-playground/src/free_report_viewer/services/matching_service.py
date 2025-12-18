"""
Matching Service
Finds top 3 care homes: Safe Bet, Best Value, Premium
Implements 50-point matching algorithm for FREE Report
"""
from typing import List, Dict, Optional, Any
import math
import sys
from pathlib import Path

# Try to import geo utilities
try:
    # Try from api-testing-suite/backend/utils
    project_root = Path(__file__).parent.parent.parent.parent
    utils_path = project_root / "api-testing-suite" / "backend" / "utils"
    if str(utils_path) not in sys.path:
        sys.path.insert(0, str(utils_path))
    
    from geo import calculate_distance_km
    GEO_UTILS_AVAILABLE = True
except ImportError:
    # Fallback: define locally if import fails
    GEO_UTILS_AVAILABLE = False
    
    def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Fallback distance calculation"""
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2 +
            math.cos(math.radians(lat1)) *
            math.cos(math.radians(lat2)) *
            math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))
        return round(R * c, 2)

# Try to import scoring constants
try:
    project_root = Path(__file__).parent.parent.parent.parent
    utils_path = project_root / "api-testing-suite" / "backend" / "utils"
    if str(utils_path) not in sys.path:
        sys.path.insert(0, str(utils_path))
    
    from scoring_constants import ScoringRatios, DefaultScores, ScoringBaseMax, ScoringDefaults, ScoringPresets
    SCORING_CONSTANTS_AVAILABLE = True
except ImportError:
    SCORING_CONSTANTS_AVAILABLE = False
    # Fallback constants
    class ScoringRatios:
        CLOSE_MATCH_RATIO = 0.67
        GENERAL_MATCH_RATIO = 0.33
        GOOD_RATING_RATIO = 0.8
        REQUIRES_IMPROVEMENT_RATIO = 0.4
        LIMITED_AVAILABILITY_RATIO = 0.5
        NEUTRAL_BUDGET_RATIO = 0.5
    
    class DefaultScores:
        LOCATION_DEFAULT = 5
        BUDGET_NEUTRAL = 10
        CARE_TYPE_GENERAL = 5
        AVAILABILITY_NONE = 0
        AVAILABILITY_FULL = 0
        CQC_NONE = 0
        GOOGLE_REVIEWS_NONE = 0
    
    class ScoringBaseMax:
        LOCATION_BASE_MAX = 20
        CQC_BASE_MAX = 25
        BUDGET_BASE_MAX = 20
        CARE_TYPE_BASE_MAX = 15
        AVAILABILITY_BASE_MAX = 10
        GOOGLE_REVIEWS_BASE_MAX = 10
    
    class ScoringPresets:
        """Fallback scoring presets"""
        CURRENT = {
            'name': 'current',
            'total_points': 100,
            'weights': {
                'location': 20, 'cqc': 25, 'budget': 20,
                'careType': 15, 'availability': 10, 'googleReviews': 10,
            },
            'thresholds': {
                'location': {'within5Miles': 20, 'within10Miles': 15, 'within15Miles': 10, 'over15Miles': 5},
                'budget': {'withinBudget': 20, 'plus50': 20, 'plus100': 15, 'plus200': 10},
                'googleReviews': {'highRating': 10, 'goodRatingManyReviews': 7, 'goodRatingFewReviews': 5,
                                'mediumRatingMany': 4, 'mediumRatingFew': 2},
            },
        }
        SPEC_V3 = {
            'name': 'spec_v3',
            'total_points': 50,
            'weights': {
                'medical': 10, 'safety': 10, 'location': 8,
                'budget': 8, 'quality': 8, 'availability': 6,
            },
            'thresholds': {
                'location': {'within5km': 8, 'within15km': 6, 'within30km': 4, 'over30km': 0},
                'budget': {'withinBudget': 8, 'plus50': 6, 'plus100': 4, 'plus200': 0},
                'safety': {'excellent': 10, 'good': 8, 'improvement': 5, 'inadequate': 0, 'fsa_5': 1, 'fsa_3_below': -1},
                'quality': {'outstanding': 8, 'good': 6, 'improvement': 0, 'inadequate': 0},
            },
        }
        
        @classmethod
        def get_preset(cls, name: str) -> dict:
            presets = {'current': cls.CURRENT, 'spec_v3': cls.SPEC_V3}
            return presets.get(name.lower(), cls.CURRENT)
        
        @classmethod
        def list_presets(cls) -> list:
            return ['current', 'spec_v3']
    
    class ScoringDefaults:
        DEFAULT_WEIGHTS = ScoringPresets.CURRENT['weights']
        DEFAULT_THRESHOLDS = ScoringPresets.CURRENT['thresholds']

# Try to import matching models (for new 50-point algorithm)
try:
    # Try from api-testing-suite/backend/models
    project_root = Path(__file__).parent.parent.parent.parent
    models_path = project_root / "api-testing-suite" / "backend" / "models"
    if str(models_path) not in sys.path:
        sys.path.insert(0, str(models_path))
    
    from matching_models import MatchingInputs, MatchingScore
except ImportError:
    # Fallback: define simple classes if import fails
    class MatchingInputs:
        def __init__(self, postcode, budget=None, care_type=None, user_lat=None, user_lon=None, max_distance_miles=None,
                     location_postcode=None, timeline=None, medical_conditions=None, max_distance_km=None,
                     priority_order=None, priority_weights=None):
            self.postcode = postcode
            self.budget = budget
            self.care_type = care_type
            self.user_lat = user_lat
            self.user_lon = user_lon
            self.max_distance_miles = max_distance_miles
            self.location_postcode = location_postcode or postcode
            self.timeline = timeline
            self.medical_conditions = medical_conditions or []
            self.max_distance_km = max_distance_km
            self.priority_order = priority_order or ['quality', 'cost', 'proximity']
            self.priority_weights = priority_weights or [40, 35, 25]
        
        def get_max_distance_km(self):
            """Get max distance in km"""
            if self.max_distance_km:
                return self.max_distance_km
            if self.max_distance_miles:
                return self.max_distance_miles * 1.60934
            return 30.0
    
    class MatchingScore:
        def __init__(self):
            self.location_score = 0
            self.cqc_score = 0
            self.budget_score = 0
            self.care_type_score = 0
            self.availability_score = 0
            self.google_reviews_score = 0
            self.total_score = 0
        
        def calculate_total(self):
            self.total_score = (
                self.location_score + self.cqc_score + self.budget_score +
                self.care_type_score + self.availability_score + self.google_reviews_score
            )


class MatchingService:
    """Service for matching care homes"""
    
    def __init__(
        self,
        scoring_weights: Optional[Dict[str, int]] = None,
        scoring_thresholds: Optional[Dict[str, Any]] = None,
        preset: Optional[str] = None
    ):
        """
        Initialize MatchingService with optional custom scoring configuration
        
        Args:
            scoring_weights: Dict with weights for each category
            scoring_thresholds: Dict with thresholds for scoring
            preset: Preset name ('current' or 'spec_v3')
                - 'current': 100-point algorithm with Google Reviews
                - 'spec_v3': 50-point algorithm matching specification v3.0
        
        Available presets:
            - 'current' (100 pts): location=20, cqc=25, budget=20, careType=15, availability=10, googleReviews=10
            - 'spec_v3' (50 pts): medical=10, safety=10, location=8, budget=8, quality=8, availability=6
        """
        # Load preset if specified
        if preset:
            preset_config = ScoringPresets.get_preset(preset)
            self.preset_name = preset_config.get('name', 'current')
            self.total_points = preset_config.get('total_points', 100)
            self.weights = scoring_weights or preset_config.get('weights', {}).copy()
            self.thresholds = scoring_thresholds or preset_config.get('thresholds', {}).copy()
        else:
            # Default weights (total = 100) - use constants
            self.preset_name = 'current'
            self.total_points = 100
            self.weights = scoring_weights or ScoringDefaults.DEFAULT_WEIGHTS.copy()
            self.thresholds = scoring_thresholds or ScoringDefaults.DEFAULT_THRESHOLDS.copy()
        
        # Normalize weights to ensure they sum to total_points (if custom weights provided)
        if scoring_weights:
            total = sum(self.weights.values())
            if total != self.total_points and total > 0:
                # Scale weights proportionally
                for key in self.weights:
                    self.weights[key] = int((self.weights[key] / total) * self.total_points)
    
    @classmethod
    def with_preset(cls, preset_name: str) -> 'MatchingService':
        """
        Factory method to create MatchingService with a specific preset
        
        Args:
            preset_name: 'current' or 'spec_v3'
            
        Returns:
            MatchingService configured with the preset
            
        Example:
            service = MatchingService.with_preset('spec_v3')
        """
        return cls(preset=preset_name)
    
    @staticmethod
    def available_presets() -> list:
        """List available scoring presets"""
        return ScoringPresets.list_presets()
    
    def find_top_3_homes(
        self,
        care_homes: List[Dict],
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None
    ) -> Dict[str, Dict]:
        """
        Find top 3 homes: Safe Bet, Best Value, Premium
        
        Args:
            care_homes: List of care home dicts from database
            user_lat: User latitude
            user_lon: User longitude
            
        Returns:
            Dict with 'safe_bet', 'best_value', 'premium' keys
        """
        if not care_homes:
            return {}
        
        # Calculate distances if coordinates available
        if user_lat and user_lon:
            for home in care_homes:
                if home.get('latitude') and home.get('longitude'):
                    home['distance_km'] = self._calculate_distance(
                        user_lat, user_lon,
                        home['latitude'], home['longitude']
                    )
        
        # Safe Bet: Best CQC rating + closest distance
        safe_bet = self._find_safe_bet(care_homes)
        
        # Best Value: Best score/price ratio
        best_value = self._find_best_value(care_homes)
        
        # Premium: Outstanding rating
        premium = self._find_premium(care_homes)
        
        return {
            "safe_bet": safe_bet,
            "best_value": best_value,
            "premium": premium
        }
    
    def _find_safe_bet(self, homes: List[Dict]) -> Optional[Dict]:
        """Find Safe Bet: best CQC rating + closest"""
        if not homes:
            return None
        
        # Rating priority: Outstanding > Good > Requires Improvement > Inadequate
        rating_scores = {
            "Outstanding": 4,
            "Good": 3,
            "Requires improvement": 2,
            "Inadequate": 1,
            None: 0
        }
        
        best_home = None
        best_score = -1
        
        for home in homes:
            rating = home.get('rating') or home.get('overall_rating')
            rating_score = rating_scores.get(rating, 0)
            distance = home.get('distance_km', 999)
            
            # Score = rating_score * 100 - distance (closer is better)
            # Prefer Good+ ratings
            if rating_score >= 3:  # Good or Outstanding
                score = rating_score * 100 - distance
                
                if score > best_score:
                    best_score = score
                    best_home = home.copy()
                    best_home['match_type'] = 'Safe Bet'
        
        # If no Good+ found, return best available
        if not best_home and homes:
            for home in homes:
                rating = home.get('rating') or home.get('overall_rating')
                rating_score = rating_scores.get(rating, 0)
                distance = home.get('distance_km', 999)
                score = rating_score * 100 - distance
                
                if score > best_score:
                    best_score = score
                    best_home = home.copy()
                    best_home['match_type'] = 'Safe Bet'
        
        return best_home
    
    def _find_best_value(self, homes: List[Dict]) -> Optional[Dict]:
        """Find Best Value: best score/price ratio"""
        if not homes:
            return None
        
        rating_scores = {
            "Outstanding": 4,
            "Good": 3,
            "Requires improvement": 2,
            "Inadequate": 1,
            None: 0
        }
        
        best_home = None
        best_ratio = -1
        
        for home in homes:
            rating = home.get('rating') or home.get('overall_rating')
            rating_score = rating_scores.get(rating, 0)
            price = home.get('weekly_cost', 999999)
            
            if price > 0:
                # Value ratio = rating_score / (price / 100)
                ratio = rating_score / (price / 100)
                
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_home = home.copy()
                    best_home['match_type'] = 'Best Value'
        
        return best_home
    
    def _find_premium(self, homes: List[Dict]) -> Optional[Dict]:
        """Find Premium: Outstanding rating"""
        outstanding_homes = [
            h for h in homes
            if (h.get('rating') or h.get('overall_rating')) == "Outstanding"
        ]
        
        if not outstanding_homes:
            # Fallback to best rated
            rating_scores = {
                "Outstanding": 4,
                "Good": 3,
                "Requires improvement": 2,
                "Inadequate": 1
            }
            outstanding_homes = sorted(
                homes,
                key=lambda h: rating_scores.get(h.get('rating') or h.get('overall_rating'), 0),
                reverse=True
            )[:1]
        
        if outstanding_homes:
            premium = outstanding_homes[0].copy()
            premium['match_type'] = 'Premium'
            return premium
        
        return None
    
    def _calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Calculate distance in km using Haversine formula (delegates to geo utility)"""
        return calculate_distance_km(lat1, lon1, lat2, lon2)
    
    def _scale_score(self, base_score: int, base_max: int, target_max: int) -> int:
        """Scale a score from one max to another proportionally"""
        if base_max == 0:
            return 0
        return int((base_score / base_max) * target_max)
    
    # ==================== 50-POINT SCORING METHODS ====================
    
    def score_location(
        self,
        home_lat: Optional[float],
        home_lon: Optional[float],
        user_lat: Optional[float],
        user_lon: Optional[float]
    ) -> int:
        """
        Calculate location score (uses configured weight)
        
        Scoring thresholds (configurable):
        - ≤5 miles: within5Miles points
        - ≤10 miles: within10Miles points
        - ≤15 miles: within15Miles points
        - >15 miles: over15Miles points
        """
        if not all([home_lat, home_lon, user_lat, user_lon]):
            # Return proportional default score
            max_score = self.weights.get('location', ScoringBaseMax.LOCATION_BASE_MAX)
            default_threshold = self.thresholds.get('location', {}).get('over15Miles', DefaultScores.LOCATION_DEFAULT)
            base_max = ScoringBaseMax.LOCATION_BASE_MAX
            return self._scale_score(default_threshold, base_max, max_score) if max_score > 0 else DefaultScores.LOCATION_DEFAULT
        
        distance_km = self._calculate_distance(
            user_lat, user_lon,
            home_lat, home_lon
        )
        distance_miles = distance_km * 0.621371
        
        # Get thresholds from config
        loc_thresholds = self.thresholds.get('location', {})
        max_score = self.weights.get('location', ScoringBaseMax.LOCATION_BASE_MAX)
        
        # Scale thresholds proportionally to max_score
        default_loc_thresholds = ScoringDefaults.DEFAULT_THRESHOLDS.get('location', {})
        if distance_miles <= 5:
            base_score = loc_thresholds.get('within5Miles', default_loc_thresholds.get('within5Miles', ScoringBaseMax.LOCATION_BASE_MAX))
        elif distance_miles <= 10:
            base_score = loc_thresholds.get('within10Miles', default_loc_thresholds.get('within10Miles', 15))
        elif distance_miles <= 15:
            base_score = loc_thresholds.get('within15Miles', default_loc_thresholds.get('within15Miles', 10))
        else:
            base_score = loc_thresholds.get('over15Miles', default_loc_thresholds.get('over15Miles', DefaultScores.LOCATION_DEFAULT))
        
        # Scale to configured weight
        base_max = ScoringBaseMax.LOCATION_BASE_MAX
        return self._scale_score(base_score, base_max, max_score)
    
    def score_cqc_rating(self, rating: Optional[str], fsa_rating: Optional[int] = None) -> int:
        """
        Calculate CQC rating score with FSA bonus/penalty (uses configured weight)
        
        Scoring (scaled to configured weight):
        - Outstanding: 100% of weight
        - Good: 80% of weight
        - Requires Improvement: 40% of weight
        - Inadequate: 0 points
        
        FSA Integration (spec v3.0):
        - FSA 5/5: +1 point bonus
        - FSA 3/5 or below: -1 point penalty
        
        Args:
            rating: CQC overall or safe rating
            fsa_rating: Food Standards Agency rating (1-5)
        """
        max_score = self.weights.get('cqc', 25)
        
        if not rating:
            return 0
        
        rating_lower = rating.lower()
        if 'outstanding' in rating_lower:
            base_score = max_score
        elif 'good' in rating_lower:
            base_score = int(max_score * 0.8)
        elif 'requires improvement' in rating_lower or 'requires' in rating_lower:
            base_score = int(max_score * 0.4)
        elif 'inadequate' in rating_lower:
            base_score = 0
        else:
            base_score = 0
        
        # Apply FSA bonus/penalty
        if fsa_rating is not None:
            if fsa_rating >= 5:
                base_score += 1  # +1 bonus for excellent food hygiene
            elif fsa_rating <= 3:
                base_score -= 1  # -1 penalty for poor food hygiene
        
        return max(0, min(base_score, max_score))
    
    def score_budget_match(
        self,
        home_price: float,
        user_budget: Optional[float],
        care_type: Optional[str] = None
    ) -> int:
        """
        Calculate budget match score (uses configured weight and thresholds)
        
        Scoring thresholds (configurable):
        - Within budget (≤0): withinBudget points
        - +£0-50: plus50 points
        - +£50-100: plus100 points
        - +£100-200: plus200 points
        - +£200+: 0 points
        """
        max_score = self.weights.get('budget', ScoringBaseMax.BUDGET_BASE_MAX)
        budget_thresholds = self.thresholds.get('budget', {})
        
        if not user_budget or user_budget <= 0:
            # Neutral score if no budget specified
            return int(max_score * ScoringRatios.NEUTRAL_BUDGET_RATIO)
        
        price_diff = home_price - user_budget
        
        # Get score from thresholds and scale to configured weight
        if price_diff <= 0:
            base_score = budget_thresholds.get('withinBudget', 20)
        elif price_diff <= 50:
            base_score = budget_thresholds.get('plus50', 20)
        elif price_diff <= 100:
            base_score = budget_thresholds.get('plus100', 15)
        elif price_diff <= 200:
            base_score = budget_thresholds.get('plus200', 10)
        else:
            return 0
        
        # Scale to configured weight (assuming base max was 20)
        return int((base_score / 20) * max_score) if max_score > 0 else 0
    
    def score_care_type_match(
        self,
        user_care_type: Optional[str],
        home_care_types: List[str]
    ) -> int:
        """
        Calculate care type match score (15 points)
        
        Scoring:
        - Perfect match: 15 points
        - Close match: 10 points
        - General match: 5 points
        - No match: 0 points
        """
        if not user_care_type or not home_care_types:
            return 5  # General match
        
        user_type = user_care_type.lower()
        home_types = [ct.lower() for ct in home_care_types]
        
        max_score = self.weights.get('careType', ScoringBaseMax.CARE_TYPE_BASE_MAX)
        
        # Perfect match
        if user_type in home_types:
            return max_score
        
        # Close matches
        close_matches = {
            'residential': ['residential_dementia'],
            'nursing': ['nursing_dementia'],
            'dementia': ['residential_dementia', 'nursing_dementia']
        }
        
        if user_type in close_matches:
            for close_type in close_matches[user_type]:
                if close_type in home_types:
                    return int(max_score * ScoringRatios.CLOSE_MATCH_RATIO)
        
        # General match (any care type available)
        return int(max_score * ScoringRatios.GENERAL_MATCH_RATIO)
    
    def score_availability(
        self,
        beds_available: Optional[int],
        availability_status: Optional[str],
        has_availability: Optional[bool]
    ) -> int:
        """
        Calculate availability score (uses configured weight)
        
        Scoring (scaled to configured weight):
        - Beds available now: 100% of weight
        - Limited availability / <4 weeks waiting: 50% of weight
        - Full / 4+ weeks waiting: 0 points
        """
        max_score = self.weights.get('availability', ScoringBaseMax.AVAILABILITY_BASE_MAX)
        
        # Beds available now
        if beds_available and beds_available > 0:
            return max_score
        
        # Check availability status
        if availability_status:
            status_lower = availability_status.lower()
            if 'available' in status_lower:
                return max_score
            elif 'limited' in status_lower:
                return int(max_score * ScoringRatios.LIMITED_AVAILABILITY_RATIO)
            elif 'waiting' in status_lower:
                return int(max_score * ScoringRatios.LIMITED_AVAILABILITY_RATIO)
            elif 'full' in status_lower:
                return DefaultScores.AVAILABILITY_FULL
        
        # Check boolean flag
        if has_availability is True:
            return max_score
        elif has_availability is False:
            return DefaultScores.AVAILABILITY_FULL
        
        # No data
        return DefaultScores.AVAILABILITY_NONE
    
    def score_google_reviews(
        self,
        google_rating: Optional[float],
        review_count: Optional[int]
    ) -> int:
        """
        Calculate Google reviews score (uses configured weight and thresholds)
        
        Scoring thresholds (configurable):
        - ≥4.5 rating: highRating points
        - ≥4.0 rating with ≥20 reviews: goodRatingManyReviews points
        - ≥4.0 rating with <20 reviews: goodRatingFewReviews points
        - ≥3.5 rating with ≥10 reviews: mediumRatingMany points
        - ≥3.5 rating with <10 reviews: mediumRatingFew points
        - <3.5 rating: 0 points
        """
        max_score = self.weights.get('googleReviews', ScoringBaseMax.GOOGLE_REVIEWS_BASE_MAX)
        review_thresholds = self.thresholds.get('googleReviews', {})
        
        if not google_rating:
            return DefaultScores.GOOGLE_REVIEWS_NONE
        
        review_count = review_count or 0
        
        # Get base score from thresholds and scale to configured weight
        if google_rating >= 4.5:
            base_score = review_thresholds.get('highRating', 10)
        elif google_rating >= 4.0:
            if review_count >= 20:
                base_score = review_thresholds.get('goodRatingManyReviews', 7)
            else:
                base_score = review_thresholds.get('goodRatingFewReviews', 5)
        elif google_rating >= 3.5:
            if review_count >= 10:
                base_score = review_thresholds.get('mediumRatingMany', 4)
            else:
                base_score = review_thresholds.get('mediumRatingFew', 2)
        else:
            return 0
        
        # Scale to configured weight
        base_max = ScoringBaseMax.GOOGLE_REVIEWS_BASE_MAX
        return self._scale_score(base_score, base_max, max_score)
    
    def _get_home_price(
        self,
        home: Dict[str, Any],
        care_type: Optional[str]
    ) -> float:
        """Get home price based on care type"""
        if not care_type:
            return home.get('weekly_cost', 0)
        
        care_type_lower = care_type.lower()
        
        # Try to get specific price for care type
        if care_type_lower == 'residential':
            price = home.get('fee_residential_from')
            if price:
                return float(price)
        elif care_type_lower == 'nursing':
            price = home.get('fee_nursing_from')
            if price:
                return float(price)
        elif care_type_lower == 'dementia':
            price = home.get('fee_dementia_from')
            if price:
                return float(price)
        elif care_type_lower == 'respite':
            price = home.get('fee_respite_from')
            if price:
                return float(price)
        
        # Try weekly_costs dict
        weekly_costs = home.get('weekly_costs', {})
        if isinstance(weekly_costs, dict) and care_type_lower in weekly_costs:
            price = weekly_costs[care_type_lower]
            if price:
                return float(price)
        
        # Fallback to weekly_cost
        return home.get('weekly_cost', 0)
    
    def _get_home_care_types(self, home: Dict[str, Any]) -> List[str]:
        """Extract care types from home data"""
        # Try care_types list
        if 'care_types' in home and isinstance(home['care_types'], list):
            return home['care_types']
        
        # Try boolean flags
        care_types = []
        if home.get('care_residential'):
            care_types.append('residential')
        if home.get('care_nursing'):
            care_types.append('nursing')
        if home.get('care_dementia'):
            care_types.append('dementia')
        if home.get('care_respite'):
            care_types.append('respite')
        
        return care_types
    
    def calculate_50_point_score(
        self,
        home: Dict[str, Any],
        user_inputs: MatchingInputs
    ) -> MatchingScore:
        """
        Calculate full score for a care home (100 points with FSA integration)
        
        Args:
            home: Care home data dict
            user_inputs: User inputs from questionnaire
        
        Returns:
            MatchingScore with breakdown
            
        Note:
            FSA rating is integrated into CQC score:
            - FSA 5/5: +1 bonus
            - FSA 3/5 or below: -1 penalty
        """
        score = MatchingScore()
        
        # 1. Location (20 points)
        score.location_score = self.score_location(
            home.get('latitude'),
            home.get('longitude'),
            user_inputs.user_lat,
            user_inputs.user_lon
        )
        
        # 2. CQC Rating with FSA integration (25 points)
        rating = (
            home.get('rating') or
            home.get('overall_rating') or
            home.get('cqc_rating_overall')
        )
        # Get FSA rating for bonus/penalty
        fsa_rating = home.get('fsa_rating') or home.get('food_hygiene_rating')
        if isinstance(fsa_rating, str):
            try:
                fsa_rating = int(fsa_rating)
            except (ValueError, TypeError):
                fsa_rating = None
        
        score.cqc_score = self.score_cqc_rating(rating, fsa_rating)
        
        # 3. Budget Match (20 points)
        home_price = self._get_home_price(home, user_inputs.care_type)
        score.budget_score = self.score_budget_match(
            home_price,
            user_inputs.budget,
            user_inputs.care_type
        )
        
        # 4. Care Type Match (15 points)
        home_care_types = self._get_home_care_types(home)
        score.care_type_score = self.score_care_type_match(
            user_inputs.care_type,
            home_care_types
        )
        
        # 5. Availability (10 points)
        score.availability_score = self.score_availability(
            home.get('beds_available'),
            home.get('availability_status'),
            home.get('has_availability')
        )
        
        # 6. Google Reviews (10 points)
        score.google_reviews_score = self.score_google_reviews(
            home.get('google_rating'),
            home.get('review_count') or home.get('user_ratings_total')
        )
        
        # Calculate total
        score.calculate_total()
        
        return score
    
    def select_3_strategic_homes(
        self,
        candidates: List[Dict[str, Any]],
        user_inputs: MatchingInputs
    ) -> Dict[str, Dict[str, Any]]:
        """
        Select 3 strategic homes using 50-point scoring
        
        Strategies:
        1. Safe Bet: Highest CQC + Location score (within 10 miles)
        2. Best Reputation: Highest Google Reviews + CQC score
        3. Smart Value: Best total score / price ratio
        
        Args:
            candidates: List of care home dicts
            user_inputs: MatchingInputs with user preferences
        
        Returns:
            Dict with 'safe_bet', 'best_reputation', 'smart_value' keys
        """
        if not candidates:
            return {}
        
        # Calculate distances if coordinates available
        if user_inputs.user_lat and user_inputs.user_lon:
            for home in candidates:
                if home.get('latitude') and home.get('longitude'):
                    home['distance_km'] = self._calculate_distance(
                        user_inputs.user_lat, user_inputs.user_lon,
                        home['latitude'], home['longitude']
                    )
        
        # Calculate 50-point scores for all candidates
        scored_homes = []
        for home in candidates:
            score = self.calculate_50_point_score(home, user_inputs)
            home['match_score'] = score.total_score
            home['score_breakdown'] = score.to_dict() if hasattr(score, 'to_dict') else {
                'location': score.location_score,
                'cqc': score.cqc_score,
                'budget': score.budget_score,
                'care_type': score.care_type_score,
                'availability': score.availability_score,
                'google_reviews': score.google_reviews_score,
                'total': score.total_score
            }
            scored_homes.append(home)
        
        # STRATEGY 1: Safe Bet
        # Highest CQC + Location within 10 miles
        safe_bet_candidates = [
            h for h in scored_homes
            if h.get('distance_km', 999) <= 16  # ~10 miles
            and h['score_breakdown']['cqc'] >= 20  # Good or Outstanding
        ]
        
        if safe_bet_candidates:
            safe_bet = max(
                safe_bet_candidates,
                key=lambda h: (
                    h['score_breakdown']['cqc'],
                    h['score_breakdown']['location']
                )
            )
        else:
            # Fallback: best CQC score
            safe_bet = max(
                scored_homes,
                key=lambda h: h['score_breakdown']['cqc']
            )
        
        safe_bet = safe_bet.copy()
        safe_bet['match_type'] = 'Safe Bet'
        
        # STRATEGY 2: Best Reputation
        # Highest Google Reviews + CQC
        reputation_candidates = [
            h for h in scored_homes
            if h['score_breakdown']['google_reviews'] >= 7  # ≥4.0 rating
            and h['score_breakdown']['cqc'] >= 20
        ]
        
        if reputation_candidates:
            best_reputation = max(
                reputation_candidates,
                key=lambda h: (
                    h['score_breakdown']['google_reviews'],
                    h['score_breakdown']['cqc']
                )
            )
        else:
            # Fallback: best Google reviews score
            best_reputation = max(
                scored_homes,
                key=lambda h: h['score_breakdown']['google_reviews']
            )
        
        best_reputation = best_reputation.copy()
        best_reputation['match_type'] = 'Best Reputation'
        
        # STRATEGY 3: Smart Value
        # Best total score / price ratio
        for h in scored_homes:
            price = self._get_home_price(h, user_inputs.care_type)
            if price > 0:
                h['value_ratio'] = h['match_score'] / price
            else:
                h['value_ratio'] = 0
        
        # Filter by budget if specified
        if user_inputs.budget:
            value_candidates = [
                h for h in scored_homes
                if self._get_home_price(h, user_inputs.care_type) <= user_inputs.budget
                and h['score_breakdown']['cqc'] >= 20
            ]
        else:
            value_candidates = [
                h for h in scored_homes
                if h['score_breakdown']['cqc'] >= 20
            ]
        
        if value_candidates:
            smart_value = max(
                value_candidates,
                key=lambda h: h.get('value_ratio', 0)
            )
        else:
            # Fallback: best score/price ratio overall
            smart_value = max(
                scored_homes,
                key=lambda h: h.get('value_ratio', 0)
            )
        
        smart_value = smart_value.copy()
        smart_value['match_type'] = 'Smart Value'
        
        # Remove duplicates
        result = {}
        seen_ids = set()
        
        for home in [safe_bet, best_reputation, smart_value]:
            home_id = home.get('location_id') or home.get('id') or home.get('name')
            if home_id not in seen_ids:
                seen_ids.add(home_id)
                match_type = home['match_type'].lower().replace(' ', '_')
                result[match_type] = home
        
        # Fill missing strategies if needed
        if len(result) < 3:
            remaining = [h for h in scored_homes if (h.get('location_id') or h.get('id') or h.get('name')) not in seen_ids]
            remaining.sort(key=lambda h: h['match_score'], reverse=True)
            
            for home in remaining:
                if len(result) >= 3:
                    break
                match_type = f"strategy_{len(result) + 1}"
                home_copy = home.copy()
                home_copy['match_type'] = match_type.replace('_', ' ').title()
                result[match_type] = home_copy
        
        return result
    
    def find_top_3_homes_legacy(
        self,
        care_homes: List[Dict],
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None
    ) -> Dict[str, Dict]:
        """
        Legacy method for backward compatibility
        Use select_3_strategic_homes with MatchingInputs for new code
        """
        return self.find_top_3_homes(care_homes, user_lat, user_lon)
    
    # ==================== SPEC_V3 SCORING METHODS (50 points) ====================
    
    def score_medical_match_v3(
        self,
        user_care_type: Optional[str],
        user_conditions: Optional[List[str]],
        home_care_types: List[str]
    ) -> int:
        """
        Calculate Medical Match score for spec_v3 (10 points max)
        
        Scoring:
        - Care type match: up to 7 points
        - Condition match: up to 3 points
        """
        max_score = self.weights.get('medical', 10)
        score = 0
        
        if not user_care_type or not home_care_types:
            return int(max_score * 0.5)  # Neutral
        
        user_type = user_care_type.lower()
        home_types = [ct.lower() for ct in home_care_types]
        
        # Care type match (7 points)
        if user_type in home_types:
            score += int(max_score * 0.7)
        elif user_type == 'dementia' and ('residential_dementia' in home_types or 'nursing_dementia' in home_types):
            score += int(max_score * 0.5)
        elif user_type == 'nursing' and 'nursing' in ' '.join(home_types):
            score += int(max_score * 0.4)
        
        # Condition bonus (3 points) - if conditions provided
        if user_conditions:
            if 'dementia' in user_conditions and 'dementia' in ' '.join(home_types):
                score += int(max_score * 0.3)
        
        return min(score, max_score)
    
    def score_safety_v3(
        self,
        cqc_safe_rating: Optional[str],
        fsa_rating: Optional[int]
    ) -> int:
        """
        Calculate Safety Score for spec_v3 (10 points max)
        
        Includes FSA bonus/penalty:
        - CQC Safe: Excellent=9, Good=7, Improvement=5, Inadequate=0
        - FSA 5/5: +1 bonus
        - FSA 3/5 or below: -1 penalty
        """
        max_score = self.weights.get('safety', 10)
        safety_thresholds = self.thresholds.get('safety', {})
        score = 0
        
        # CQC Safe rating (0-9 points)
        if cqc_safe_rating:
            rating_lower = cqc_safe_rating.lower()
            if 'excellent' in rating_lower or 'outstanding' in rating_lower:
                score = safety_thresholds.get('excellent', 10) - 1  # 9 points, leave room for FSA bonus
            elif 'good' in rating_lower:
                score = safety_thresholds.get('good', 8) - 1  # 7 points
            elif 'requires' in rating_lower or 'improvement' in rating_lower:
                score = safety_thresholds.get('improvement', 5)
            else:
                score = safety_thresholds.get('inadequate', 0)
        
        # FSA bonus/penalty
        if fsa_rating is not None:
            if fsa_rating >= 5:
                score += safety_thresholds.get('fsa_5', 1)  # +1 bonus
            elif fsa_rating <= 3:
                score += safety_thresholds.get('fsa_3_below', -1)  # -1 penalty
        
        return max(0, min(score, max_score))
    
    def score_quality_v3(self, overall_rating: Optional[str]) -> int:
        """
        Calculate Quality Rating score for spec_v3 (8 points max)
        
        Scoring:
        - Outstanding: 8 points
        - Good: 6 points
        - Requires Improvement: 0 (don't show)
        - Inadequate: 0 (never show)
        """
        max_score = self.weights.get('quality', 8)
        quality_thresholds = self.thresholds.get('quality', {})
        
        if not overall_rating:
            return 0
        
        rating_lower = overall_rating.lower()
        if 'outstanding' in rating_lower:
            return quality_thresholds.get('outstanding', max_score)
        elif 'good' in rating_lower:
            return quality_thresholds.get('good', int(max_score * 0.75))
        else:
            return 0  # Don't recommend if not Good+
    
    def score_location_v3(
        self,
        distance_km: Optional[float]
    ) -> int:
        """
        Calculate Location Score for spec_v3 (8 points max)
        
        Scoring (km-based as per spec):
        - ≤5 km: 8 points
        - ≤15 km: 6 points
        - ≤30 km: 4 points
        - >30 km: 0 points
        """
        max_score = self.weights.get('location', 8)
        loc_thresholds = self.thresholds.get('location', {})
        
        if distance_km is None:
            return int(max_score * 0.5)  # Neutral if unknown
        
        if distance_km <= 5:
            return loc_thresholds.get('within5km', max_score)
        elif distance_km <= 15:
            return loc_thresholds.get('within15km', int(max_score * 0.75))
        elif distance_km <= 30:
            return loc_thresholds.get('within30km', int(max_score * 0.5))
        else:
            return loc_thresholds.get('over30km', 0)
    
    def score_budget_v3(
        self,
        home_price: float,
        user_budget: Optional[float]
    ) -> int:
        """
        Calculate Budget Fit score for spec_v3 (8 points max)
        
        Scoring:
        - Within budget: 8 points
        - +£1-50: 6 points
        - +£51-100: 4 points
        - +£100-200: 0 points (filter out >£200)
        """
        max_score = self.weights.get('budget', 8)
        budget_thresholds = self.thresholds.get('budget', {})
        
        if not user_budget or user_budget <= 0:
            return int(max_score * 0.5)  # Neutral
        
        diff = home_price - user_budget
        
        if diff <= 0:
            return budget_thresholds.get('withinBudget', max_score)
        elif diff <= 50:
            return budget_thresholds.get('plus50', int(max_score * 0.75))
        elif diff <= 100:
            return budget_thresholds.get('plus100', int(max_score * 0.5))
        elif diff <= 200:
            return budget_thresholds.get('plus200', 0)
        else:
            return 0  # Filter out homes >£200 over budget
    
    def score_availability_v3(
        self,
        beds_available: Optional[int],
        has_availability: Optional[bool]
    ) -> int:
        """
        Calculate Availability score for spec_v3 (6 points max)
        
        Scoring:
        - <70% occupancy: 6 points
        - 70-85%: 4 points
        - 85-95%: 2 points
        - 95%+: 0 points
        """
        max_score = self.weights.get('availability', 6)
        
        if beds_available is not None and beds_available > 0:
            return max_score  # Has beds = full points
        
        if has_availability is True:
            return max_score
        elif has_availability is False:
            return 0
        
        return int(max_score * 0.5)  # Unknown = neutral
    
    def calculate_50_point_score_v3(
        self,
        home: Dict[str, Any],
        user_inputs: MatchingInputs,
        user_conditions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Calculate 50-point score using spec_v3 algorithm
        
        Categories (50 total):
        - Medical: 10 pts
        - Safety: 10 pts (with FSA)
        - Location: 8 pts
        - Budget: 8 pts
        - Quality: 8 pts
        - Availability: 6 pts
        """
        # Calculate distance if coords available
        distance_km = None
        if user_inputs.user_lat and user_inputs.user_lon:
            if home.get('latitude') and home.get('longitude'):
                distance_km = self._calculate_distance(
                    user_inputs.user_lat, user_inputs.user_lon,
                    home['latitude'], home['longitude']
                )
        
        home_care_types = self._get_home_care_types(home)
        home_price = self._get_home_price(home, user_inputs.care_type)
        
        # Get ratings
        overall_rating = home.get('rating') or home.get('overall_rating') or home.get('cqc_rating_overall')
        safe_rating = home.get('cqc_rating_safe') or overall_rating
        fsa_rating = home.get('fsa_rating') or home.get('food_hygiene_rating')
        
        # Calculate each category
        medical_score = self.score_medical_match_v3(
            user_inputs.care_type,
            user_conditions,
            home_care_types
        )
        
        safety_score = self.score_safety_v3(safe_rating, fsa_rating)
        location_score = self.score_location_v3(distance_km)
        budget_score = self.score_budget_v3(home_price, user_inputs.budget)
        quality_score = self.score_quality_v3(overall_rating)
        availability_score = self.score_availability_v3(
            home.get('beds_available'),
            home.get('has_availability')
        )
        
        total = medical_score + safety_score + location_score + budget_score + quality_score + availability_score
        
        return {
            'total': total,
            'max_possible': 50,
            'breakdown': {
                'medical': medical_score,
                'safety': safety_score,
                'location': location_score,
                'budget': budget_score,
                'quality': quality_score,
                'availability': availability_score,
            },
            'preset': 'spec_v3'
        }
    
    # ==================== SIMPLE STRATEGIC SELECTION (CARE-HOME-MATCHING) ====================
    
    def select_3_strategic_homes_simple(
        self,
        candidates: List[Dict[str, Any]],
        user_inputs: MatchingInputs
    ) -> Dict[str, Dict[str, Any]]:
        """
        Простой стратегический выбор 3 домов на основе 50-point scoring
        
        Стратегии (из CARE-HOME-MATCHING-ALGORITHM):
        1. Safe Bet - Максимальная безопасность (safety_score + quality)
        2. Best Reputation - Лучшая репутация (quality + Google reviews)
        3. Smart Value - Оптимальное соотношение цена/качество (budget + quality/price)
        
        Args:
            candidates: List of care home dicts (already filtered)
            user_inputs: MatchingInputs with user preferences
        
        Returns:
            Dict with 'safe_bet', 'best_reputation', 'smart_value' keys
        """
        if not candidates:
            return {}
        
        # Calculate distances if coordinates available
        if user_inputs.user_lat and user_inputs.user_lon:
            for home in candidates:
                if home.get('latitude') and home.get('longitude'):
                    home['distance_km'] = self._calculate_distance(
                        user_inputs.user_lat, user_inputs.user_lon,
                        home['latitude'], home['longitude']
                    )
        
        # Calculate 50-point scores for all candidates using spec_v3
        scored_homes = []
        for home in candidates:
            score_data = self.calculate_50_point_score_v3(
                home,
                user_inputs,
                user_inputs.medical_conditions
            )
            home['scores'] = score_data['breakdown']
            home['match_score'] = score_data['total']
            scored_homes.append(home)
        
        # Get home ID function
        def get_home_id(home):
            return home.get('location_id') or home.get('id') or home.get('name') or str(id(home))
        
        # STRATEGY 1: Safe Bet - Максимальная безопасность
        # Используем: safety_score (10 pts) + quality (8 pts)
        safe_bet = max(
            scored_homes,
            key=lambda h: (
                h['scores'].get('safety', 0),
                h['scores'].get('quality', 0),
                h['match_score']
            )
        )
        safe_bet = safe_bet.copy()
        safe_bet['strategy'] = 'safe-bet'
        safe_bet['match_reasoning'] = self._generate_safe_bet_reasoning(safe_bet)
        safe_bet['match_type'] = 'Safe Bet'
        
        # STRATEGY 2: Best Reputation - Лучшая репутация
        # Используем: quality (8 pts) + Google rating (если есть)
        # Исключаем Safe Bet
        safe_bet_id = get_home_id(safe_bet)
        reputation_candidates = [
            h for h in scored_homes 
            if get_home_id(h) != safe_bet_id
        ]
        
        if not reputation_candidates:
            # Fallback: если только один дом, используем его для Best Reputation тоже
            best_reputation = safe_bet.copy()
            best_reputation['strategy'] = 'best-reputation'
            best_reputation['match_reasoning'] = self._generate_reputation_reasoning(best_reputation)
            best_reputation['match_type'] = 'Best Reputation'
        else:
            best_reputation = max(
                reputation_candidates,
                key=lambda h: (
                    h['scores'].get('quality', 0),
                    h.get('google_rating', 0) or 0,  # Google rating если есть
                    h.get('review_count', 0) or h.get('user_ratings_total', 0) or 0,  # Количество отзывов
                    h['match_score']
                )
            )
            best_reputation = best_reputation.copy()
            best_reputation['strategy'] = 'best-reputation'
            best_reputation['match_reasoning'] = self._generate_reputation_reasoning(best_reputation)
            best_reputation['match_type'] = 'Best Reputation'
        
        # STRATEGY 3: Smart Value - Оптимальное соотношение цена/качество
        # Используем: budget (8 pts) + соотношение quality/price
        # Исключаем уже выбранные дома
        best_reputation_id = get_home_id(best_reputation)
        value_candidates = [
            h for h in scored_homes 
            if get_home_id(h) != safe_bet_id 
            and get_home_id(h) != best_reputation_id
        ]
        
        if not value_candidates:
            # Fallback: если только два дома, используем лучший из оставшихся
            value_candidates = [h for h in scored_homes if get_home_id(h) != safe_bet_id]
            if not value_candidates:
                # Если только один дом, используем его для Smart Value тоже
                smart_value = safe_bet.copy()
                smart_value['strategy'] = 'smart-value'
                smart_value['match_reasoning'] = self._generate_value_reasoning(smart_value, user_inputs)
                smart_value['match_type'] = 'Smart Value'
            else:
                # Вычисляем value ratio для оставшихся кандидатов
                for home in value_candidates:
                    price = self._get_home_price(home, user_inputs.care_type)
                    if price > 0:
                        quality_total = home['scores'].get('quality', 0) + home['scores'].get('safety', 0)
                        home['value_ratio'] = quality_total / (price / 100)
                    else:
                        home['value_ratio'] = 0
                
                smart_value = max(
                    value_candidates,
                    key=lambda h: (
                        h.get('value_ratio', 0),
                        h['scores'].get('budget', 0),
                        h['scores'].get('quality', 0),
                        h['match_score']
                    )
                )
                smart_value = smart_value.copy()
                smart_value['strategy'] = 'smart-value'
                smart_value['match_reasoning'] = self._generate_value_reasoning(smart_value, user_inputs)
                smart_value['match_type'] = 'Smart Value'
        else:
            # Вычисляем value ratio (quality per pound)
            for home in value_candidates:
                price = self._get_home_price(home, user_inputs.care_type)
                if price > 0:
                    # Value = (quality + safety) / price (нормализуем цену)
                    quality_total = home['scores'].get('quality', 0) + home['scores'].get('safety', 0)
                    home['value_ratio'] = quality_total / (price / 100)
                else:
                    home['value_ratio'] = 0
            
            smart_value = max(
                value_candidates,
                key=lambda h: (
                    h.get('value_ratio', 0),
                    h['scores'].get('budget', 0),  # В пределах бюджета
                    h['scores'].get('quality', 0),
                    h['match_score']
                )
            )
            smart_value = smart_value.copy()
            smart_value['strategy'] = 'smart-value'
            smart_value['match_reasoning'] = self._generate_value_reasoning(smart_value, user_inputs)
            smart_value['match_type'] = 'Smart Value'
        
        # Применяем приоритеты пользователя (если есть)
        if user_inputs.priority_order and user_inputs.priority_weights:
            for home in [safe_bet, best_reputation, smart_value]:
                if home:
                    home['priority_adjusted_score'] = self._apply_priority_weights(home, user_inputs)
        
        # Строим результат, исключая None значения
        result = {}
        if safe_bet:
            result['safe_bet'] = safe_bet
        if best_reputation:
            result['best_reputation'] = best_reputation
        if smart_value:
            result['smart_value'] = smart_value
        
        return result
    
    def _generate_safe_bet_reasoning(self, home: Dict[str, Any]) -> List[str]:
        """Простое объяснение для Safe Bet"""
        reasons = []
        
        cqc_rating = home.get('rating') or home.get('overall_rating') or home.get('cqc_rating_overall', '')
        if cqc_rating:
            rating_lower = cqc_rating.lower()
            if 'outstanding' in rating_lower:
                reasons.append("Outstanding CQC rating - highest regulatory standard")
            elif 'good' in rating_lower:
                reasons.append("Good CQC rating - meets regulatory standards")
        
        fsa_rating = home.get('fsa_rating') or home.get('food_hygiene_rating')
        if fsa_rating:
            try:
                fsa_int = int(fsa_rating) if isinstance(fsa_rating, (int, float, str)) else None
                if fsa_int == 5:
                    reasons.append("Excellent food hygiene rating (5/5)")
            except (ValueError, TypeError):
                pass
        
        safe_rating = home.get('cqc_rating_safe') or home.get('cqc_safe_rating', '')
        if safe_rating:
            safe_lower = safe_rating.lower()
            if 'excellent' in safe_lower or 'outstanding' in safe_lower:
                reasons.append("Excellent safety record")
        
        # Если нет причин, добавить общую
        if not reasons:
            safety_score = home.get('scores', {}).get('safety', 0)
            if safety_score >= 8:
                reasons.append("High safety score based on regulatory ratings")
        
        return reasons
    
    def _generate_reputation_reasoning(self, home: Dict[str, Any]) -> List[str]:
        """Простое объяснение для Best Reputation"""
        reasons = []
        
        cqc_rating = home.get('rating') or home.get('overall_rating') or home.get('cqc_rating_overall', '')
        if cqc_rating:
            rating_lower = cqc_rating.lower()
            if 'outstanding' in rating_lower:
                reasons.append("Outstanding CQC rating - recognised excellence")
            elif 'good' in rating_lower:
                reasons.append("Good CQC rating - reliable care standards")
        
        google_rating = home.get('google_rating')
        review_count = home.get('review_count') or home.get('user_ratings_total', 0)
        
        if google_rating:
            try:
                google_float = float(google_rating)
                if google_float >= 4.5:
                    reasons.append(f"Exceptional reviews - {google_float:.1f} stars from {review_count} families")
                elif google_float >= 4.0:
                    reasons.append(f"Strong reviews - {google_float:.1f} stars")
            except (ValueError, TypeError):
                pass
        
        # Если нет причин, добавить общую
        if not reasons:
            quality_score = home.get('scores', {}).get('quality', 0)
            if quality_score >= 6:
                reasons.append("High quality rating from regulatory body")
        
        return reasons
    
    def _generate_value_reasoning(self, home: Dict[str, Any], user_inputs: MatchingInputs) -> List[str]:
        """Простое объяснение для Smart Value"""
        reasons = []
        
        price = self._get_home_price(home, user_inputs.care_type)
        budget = user_inputs.budget
        
        if budget and price > 0:
            if price <= budget:
                savings = budget - price
                if savings > 0:
                    reasons.append(f"Within budget - saves £{savings:.0f}/week compared to your budget")
                else:
                    reasons.append("Within your budget")
            else:
                over_budget = price - budget
                if over_budget <= 50:
                    reasons.append(f"Slightly over budget by £{over_budget:.0f}/week")
        
        # Quality per pound
        scores = home.get('scores', {})
        quality_total = scores.get('quality', 0) + scores.get('safety', 0)
        if price > 0:
            quality_per_pound = quality_total / (price / 100)
            if quality_per_pound > 1.5:
                reasons.append("Excellent quality-to-price ratio")
            elif quality_per_pound > 1.0:
                reasons.append("Good value for money")
        
        cqc_rating = home.get('rating') or home.get('overall_rating') or home.get('cqc_rating_overall', '')
        if cqc_rating:
            rating_lower = cqc_rating.lower()
            if 'good' in rating_lower or 'outstanding' in rating_lower:
                reasons.append("High quality care at competitive rates")
        
        # Если нет причин, добавить общую
        if not reasons:
            budget_score = scores.get('budget', 0)
            if budget_score >= 6:
                reasons.append("Good budget fit with quality care")
        
        return reasons
    
    def _apply_priority_weights(self, home: Dict[str, Any], user_inputs: MatchingInputs) -> float:
        """
        Применяем приоритеты пользователя к финальному скору
        (если есть priority_order и priority_weights)
        """
        if not user_inputs.priority_order or not user_inputs.priority_weights:
            return home.get('match_score', 0)
        
        weights = user_inputs.priority_weights
        priority_order = user_inputs.priority_order
        scores = home.get('scores', {})
        
        # Маппинг приоритетов к категориям из 50-point
        scores_map = {
            'quality': scores.get('quality', 0) + scores.get('safety', 0),  # Quality = Quality + Safety
            'cost': scores.get('budget', 0),  # Cost = Budget Fit
            'proximity': scores.get('location', 0)  # Proximity = Location
        }
        
        # Взвешенная сумма
        priority_score = 0.0
        for i, priority in enumerate(priority_order):
            if i < len(weights) and priority in scores_map:
                priority_score += scores_map[priority] * (weights[i] / 100.0)
        
        return priority_score


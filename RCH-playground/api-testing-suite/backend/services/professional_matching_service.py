"""
Professional Matching Service with Dynamic Scoring Weights

Implements 156-point matching algorithm with adaptive weights based on client profile.
Based on TECHNICAL_PROFESSIONAL_Dynamic_Weights_v2.md
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import math
from pathlib import Path
import sys

# Import geo utilities
try:
    utils_path = Path(__file__).parent.parent / "utils"
    if str(utils_path) not in sys.path:
        sys.path.insert(0, str(utils_path))
    from geo import calculate_distance_km, calculate_distance_miles
except ImportError:
    # Fallback implementation
    def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        return round(R * c, 2)
    
    def calculate_distance_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        return round(calculate_distance_km(lat1, lon1, lat2, lon2) * 0.621371, 2)


@dataclass
class ScoringWeights:
    """Dynamic scoring weights for 156-point algorithm"""
    medical: float = 19.0
    safety: float = 16.0
    location: float = 10.0
    social: float = 10.0
    financial: float = 13.0
    staff: float = 13.0
    cqc: float = 13.0
    services: float = 7.0

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
        return {
            'medical': self.medical,
            'safety': self.safety,
            'location': self.location,
            'social': self.social,
            'financial': self.financial,
            'staff': self.staff,
            'cqc': self.cqc,
            'services': self.services
        }

    def normalize(self) -> 'ScoringWeights':
        """Normalize weights to sum to 100%"""
        total = sum([
            self.medical, self.safety, self.location, self.social,
            self.financial, self.staff, self.cqc, self.services
        ])
        if total == 0:
            return self
        
        return ScoringWeights(
            medical=round((self.medical / total) * 100, 1),
            safety=round((self.safety / total) * 100, 1),
            location=round((self.location / total) * 100, 1),
            social=round((self.social / total) * 100, 1),
            financial=round((self.financial / total) * 100, 1),
            staff=round((self.staff / total) * 100, 1),
            cqc=round((self.cqc / total) * 100, 1),
            services=round((self.services / total) * 100, 1)
        )


class ProfessionalMatchingService:
    """
    Professional matching service with dynamic weights.
    
    Implements 156-point matching algorithm with adaptive weights based on:
    - Fall risk (Q13)
    - Dementia (Q9)
    - Multiple medical conditions (Q9)
    - Nursing required (Q8)
    - Low budget (Q7)
    - Urgent placement (Q17)
    """
    
    BASE_WEIGHTS = ScoringWeights()
    
    def calculate_dynamic_weights(
        self,
        questionnaire: Dict[str, Any]
    ) -> Tuple[ScoringWeights, List[str]]:
        """
        Calculate adaptive weights based on client conditions.
        
        Priority order: Fall Risk > Dementia > Complex Medical > Nursing > Budget > Urgent
        
        Args:
            questionnaire: Professional questionnaire response
            
        Returns:
            Tuple of (ScoringWeights, applied_conditions)
        """
        weights = ScoringWeights()
        applied_conditions = []
        
        # Extract questionnaire data (handle None values)
        medical_needs = questionnaire.get('section_3_medical_needs') or {}
        safety_needs = questionnaire.get('section_4_safety_special_needs') or {}
        location_budget = questionnaire.get('section_2_location_budget') or {}
        timeline = questionnaire.get('section_5_timeline') or {}
        
        fall_history = safety_needs.get('q13_fall_history', '')
        medical_conditions = medical_needs.get('q9_medical_conditions', [])
        care_types = medical_needs.get('q8_care_types', [])
        budget = location_budget.get('q7_budget', '')
        placement_timeline = timeline.get('q17_placement_timeline', '')
        
        # Priority 1: Fall Risk (HIGHEST - overrides other medical adjustments)
        if fall_history in ["3_plus_or_serious_injuries", "high_risk_of_falling"]:
            weights.safety += 9
            weights.medical -= 1
            weights.location -= 2
            weights.social -= 2
            weights.financial -= 1
            weights.staff -= 1
            weights.cqc -= 1
            weights.services -= 2
            applied_conditions.append('high_fall_risk')
            return weights.normalize(), applied_conditions
        
        # Priority 2: Dementia (if no fall risk)
        if 'dementia_alzheimers' in medical_conditions:
            weights.medical += 7
            weights.safety += 2
            weights.location -= 2
            weights.staff += 1
            weights.cqc -= 3
            weights.services -= 5
            applied_conditions.append('dementia')
            return weights.normalize(), applied_conditions
        
        # Priority 3: Multiple complex conditions (if not dementia)
        # Filter out 'no_serious_medical' if present
        actual_conditions = [c for c in medical_conditions if c != 'no_serious_medical']
        if len(actual_conditions) >= 3:
            weights.medical += 10
            weights.location -= 3
            weights.social -= 3
            weights.staff += 1
            weights.services -= 4
            applied_conditions.append('multiple_conditions')
            return weights.normalize(), applied_conditions
        
        # Priority 4: Nursing required
        if 'medical_nursing' in care_types:
            weights.medical += 3
            weights.staff += 3
            weights.location -= 1
            weights.social -= 2
            weights.services -= 2
            applied_conditions.append('nursing_required')
        
        # Priority 5: Low budget
        if budget.startswith('under_3000'):
            weights.financial += 6
            weights.medical -= 1
            weights.location -= 1
            weights.social -= 1
            weights.services -= 4
            applied_conditions.append('low_budget')
        
        # Priority 6: Urgent placement
        if placement_timeline == "urgent_2_weeks":
            weights.location += 7
            weights.medical -= 1
            weights.social -= 1
            weights.financial -= 1
            weights.services -= 5
            applied_conditions.append('urgent_placement')
        
        # Normalize to ensure sum = 100%
        return weights.normalize(), applied_conditions
    
    def calculate_156_point_match(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any],
        weights: Optional[ScoringWeights] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive match score with DYNAMIC WEIGHTS.
        
        Args:
            home: Care home data
            user_profile: User profile from questionnaire
            enriched_data: Enriched data from APIs
            weights: Optional pre-calculated weights (if None, will calculate)
        
        Returns:
            Dict with total score, normalized score, weights, category scores, point allocations
        """
        # Calculate weights if not provided
        if weights is None:
            weights, _ = self.calculate_dynamic_weights(user_profile)
        
        # Calculate category scores (0-1.0 scale)
        # Note: These functions need to be implemented separately
        category_scores = {
            'medical': self._calculate_medical_capabilities(home, user_profile, enriched_data),
            'safety': self._calculate_safety_quality(home, user_profile, enriched_data),
            'location': self._calculate_location_access(home, user_profile),
            'social': self._calculate_cultural_social(home, user_profile, enriched_data),
            'financial': self._calculate_financial_stability(home, enriched_data),
            'staff': self._calculate_staff_quality(home, enriched_data),
            'cqc': self._calculate_cqc_compliance(home, enriched_data),
            'services': self._calculate_additional_services(home, user_profile)
        }
        
        # Calculate point allocations with adjusted weights
        weights_dict = weights.to_dict()
        
        # Ensure all category scores are floats (not None)
        safe_category_scores = {}
        for key, value in category_scores.items():
            if value is None:
                safe_category_scores[key] = 0.0
            else:
                try:
                    safe_category_scores[key] = float(value)
                except (ValueError, TypeError):
                    safe_category_scores[key] = 0.0
        
        # Ensure all weights are floats (not None)
        safe_weights = {}
        for key, value in weights_dict.items():
            if value is None:
                safe_weights[key] = 0.0
            else:
                try:
                    safe_weights[key] = float(value)
                except (ValueError, TypeError):
                    safe_weights[key] = 0.0
        
        point_allocations = {
            'medical': safe_category_scores['medical'] * (safe_weights['medical'] / 100) * 156,
            'safety': safe_category_scores['safety'] * (safe_weights['safety'] / 100) * 156,
            'location': safe_category_scores['location'] * (safe_weights['location'] / 100) * 156,
            'social': safe_category_scores['social'] * (safe_weights['social'] / 100) * 156,
            'financial': safe_category_scores['financial'] * (safe_weights['financial'] / 100) * 156,
            'staff': safe_category_scores['staff'] * (safe_weights['staff'] / 100) * 156,
            'cqc': safe_category_scores['cqc'] * (safe_weights['cqc'] / 100) * 156,
            'services': safe_category_scores['services'] * (safe_weights['services'] / 100) * 156
        }
        
        # Calculate total match score
        total_score = sum(point_allocations.values())
        
        # Ensure total_score is a number
        if total_score is None:
            total_score = 0.0
        else:
            try:
                total_score = float(total_score)
            except (ValueError, TypeError):
                total_score = 0.0
        
        # Calculate normalized score (0-100)
        normalized = (total_score / 156) * 100 if total_score > 0 else 0.0
        try:
            normalized = float(normalized)
        except (ValueError, TypeError):
            normalized = 0.0
        
        return {
            'total': int(total_score),
            'normalized': int(normalized),
            'weights': weights_dict,
            'category_scores': category_scores,
            'point_allocations': point_allocations
        }
    
    # ==================== SCORING METHODS (0-1.0 scale) ====================
    
    def _calculate_medical_capabilities(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """
        Calculate medical capabilities score (0-1.0)
        
        Factors (30 points total):
        - Specialist care match: 10 points
        - Nursing level: 8 points
        - Medical equipment: 7 points
        - Emergency protocol: 5 points
        """
        score = 0.0
        max_score = 30.0
        
        medical_needs = user_profile.get('section_3_medical_needs', {})
        medical_conditions = medical_needs.get('q9_medical_conditions', [])
        care_types = medical_needs.get('q8_care_types', [])
        mobility_level = medical_needs.get('q10_mobility_level', '')
        medication_needs = medical_needs.get('q11_medication_management', '')
        
        # 1. Specialist care match (10 points)
        specialist_score = 0.0
        home_care_types = home.get('care_types', [])
        if isinstance(home_care_types, str):
            home_care_types = [home_care_types]
        
        # Check for dementia care
        if 'dementia_alzheimers' in medical_conditions:
            if 'dementia' in str(home_care_types).lower() or 'specialised_dementia' in care_types:
                specialist_score += 4.0
        
        # Check for diabetes care
        if 'diabetes' in medical_conditions:
            if 'diabetes' in str(home.get('specialist_care', '')).lower():
                specialist_score += 2.0
        
        # Check for cardiac care
        if 'heart_conditions' in medical_conditions:
            if 'cardiac' in str(home.get('specialist_care', '')).lower():
                specialist_score += 2.0
        
        # Check for mobility support
        if 'mobility_problems' in medical_conditions or mobility_level in ['wheelchair_bound', 'limited_mobility']:
            if home.get('wheelchair_accessible', False):
                specialist_score += 2.0
        
        specialist_score = min(specialist_score, 10.0)
        score += specialist_score
        
        # 2. Nursing level (8 points)
        nursing_score = 0.0
        if 'medical_nursing' in care_types:
            if home.get('care_nursing', False) or 'nursing' in str(home_care_types).lower():
                nursing_score += 5.0
                # Check for RN count
                rn_count = enriched_data.get('staff_data', {}).get('registered_nurses', 0)
                if rn_count is not None:
                    try:
                        rn_count = float(rn_count)
                        if rn_count >= 3:
                            nursing_score += 3.0
                        elif rn_count >= 1:
                            nursing_score += 1.5
                    except (ValueError, TypeError):
                        pass
        else:
            # Still give points for having nursing capability
            if home.get('care_nursing', False):
                nursing_score += 2.0
        
        score += min(nursing_score, 8.0)
        
        # 3. Medical equipment (7 points)
        equipment_score = 0.0
        if home.get('medical_equipment', False):
            equipment_score += 3.0
        if home.get('on_site_pharmacy', False):
            equipment_score += 2.0
        if enriched_data.get('medical_capabilities', {}).get('emergency_protocols', False):
            equipment_score += 2.0
        
        score += min(equipment_score, 7.0)
        
        # 4. Emergency protocol (5 points)
        emergency_score = 0.0
        emergency_response_time = enriched_data.get('medical_capabilities', {}).get('emergency_response_time')
        if emergency_response_time is not None:
            try:
                emergency_response_time = float(emergency_response_time)
                if emergency_response_time <= 5:
                    emergency_score += 3.0
                elif emergency_response_time <= 10:
                    emergency_score += 1.5
            except (ValueError, TypeError):
                pass
        
        if medication_needs in ['complex_medication', 'multiple_medications']:
            if enriched_data.get('medical_capabilities', {}).get('medication_management', False):
                emergency_score += 2.0
        
        score += min(emergency_score, 5.0)
        
        return min(score / max_score, 1.0)
    
    def _calculate_safety_quality(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """
        Calculate safety & quality score (0-1.0)
        
        Factors (25 points total):
        - CQC overall trend: 10 points
        - FSA food safety: 8 points
        - Safeguarding incidents: 5 points
        - Audit compliance: 2 points
        """
        score = 0.0
        max_score = 25.0
        
        safety_needs = user_profile.get('section_4_safety_special_needs', {})
        fall_history = safety_needs.get('q13_fall_history', '')
        high_fall_risk = fall_history in ["3_plus_or_serious_injuries", "high_risk_of_falling"]
        
        # 1. CQC overall trend (10 points)
        cqc_trend_score = 0.0
        cqc_data = enriched_data.get('cqc_detailed', {})
        overall_rating = cqc_data.get('overall_rating', home.get('rating', home.get('overall_rating')))
        
        # Rating scoring
        rating_map = {'Outstanding': 4.0, 'Good': 3.0, 'Requires improvement': 1.0, 'Inadequate': 0.0}
        if overall_rating in rating_map:
            cqc_trend_score += rating_map[overall_rating] * 1.5
        
        # Trend analysis (improving vs declining)
        trend = cqc_data.get('trend', 'stable')
        if trend == 'improving':
            cqc_trend_score += 2.0
        elif trend == 'declining':
            cqc_trend_score -= 1.0
        
        # Fall prevention specific (if high fall risk)
        if high_fall_risk:
            safe_rating = cqc_data.get('safe_rating', overall_rating)
            if safe_rating in rating_map:
                cqc_trend_score += rating_map[safe_rating] * 1.5
        
        score += max(0.0, min(cqc_trend_score, 10.0))
        
        # 2. FSA food safety (8 points) - Updated for spec v3.0
        fsa_score = 0.0
        
        # Check for FSA detailed scoring data (new format from fsa_detailed_service)
        fsa_scoring = enriched_data.get('fsa_scoring', {})
        if fsa_scoring:
            # Use pre-calculated points (max 7) scaled to 8
            fsa_points = fsa_scoring.get('fsa_points', 0)
            fsa_score = (fsa_points / 7.0) * 8.0
        else:
            # Fallback to old format
            fsa_data = enriched_data.get('fsa_detailed', {})
            fsa_rating = fsa_data.get('rating', home.get('fsa_rating'))
            
            # FSA rating: 5 = 8pts, 4 = 6pts, 3 = 4pts, 2 = 2pts, 1 = 0pts
            if fsa_rating is not None:
                try:
                    fsa_rating = float(fsa_rating)
                    if fsa_rating >= 5:
                        fsa_score = 8.0
                    elif fsa_rating >= 4:
                        fsa_score = 6.0
                    elif fsa_rating >= 3:
                        fsa_score = 4.0
                    elif fsa_rating >= 2:
                        fsa_score = 2.0
                except (ValueError, TypeError):
                    pass
            
            # Add trend bonus (spec v3.0)
            fsa_trend = fsa_data.get('trend', enriched_data.get('fsa_trend'))
            if fsa_trend == 'improving' and fsa_score > 0:
                fsa_score = min(8.0, fsa_score + 1.0)  # +1 bonus for improving
            elif fsa_trend == 'declining' and fsa_score > 0:
                fsa_score = max(0.0, fsa_score - 1.0)  # -1 penalty for declining
        
        score += fsa_score
        
        # 3. Safeguarding incidents (5 points)
        incident_score = 5.0
        incidents = enriched_data.get('cqc_detailed', {}).get('safeguarding_incidents', 0)
        if incidents is not None:
            try:
                incidents = float(incidents)
                if incidents > 0:
                    incident_score = max(0.0, 5.0 - (incidents * 1.0))
            except (ValueError, TypeError):
                pass
        
        score += incident_score
        
        # 4. Audit compliance (2 points)
        audit_score = 0.0
        financial_data = enriched_data.get('financial_data', {})
        if financial_data.get('filing_compliance', True):
            audit_score += 2.0
        
        score += audit_score
        
        return min(score / max_score, 1.0)
    
    def _calculate_location_access(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> float:
        """
        Calculate location & access score (0-1.0)
        
        Factors (15 points total):
        - Distance from postcode: 10 points
        - Public transport: 3 points
        - Parking availability: 2 points
        """
        score = 0.0
        max_score = 15.0
        
        location_budget = user_profile.get('section_2_location_budget', {})
        max_distance = location_budget.get('q6_max_distance', 'distance_not_important')
        
        # Get coordinates
        home_lat = home.get('latitude')
        home_lon = home.get('longitude')
        user_lat = location_budget.get('user_latitude')
        user_lon = location_budget.get('user_longitude')
        
        # 1. Distance scoring (10 points)
        distance_score = 0.0
        if home_lat and home_lon and user_lat and user_lon:
            try:
                distance_miles = calculate_distance_miles(user_lat, user_lon, home_lat, home_lon)
                # Ensure distance_miles is a number
                if distance_miles is None:
                    distance_score = 5.0  # Default score if calculation fails
                else:
                    try:
                        distance_miles = float(distance_miles)
                    except (ValueError, TypeError):
                        distance_score = 5.0  # Default score if conversion fails
                        distance_miles = None
                
                if distance_miles is not None:
                    # Distance thresholds based on max_distance preference
                    if max_distance == 'distance_not_important':
                        # Still score, but less weight
                        if distance_miles <= 5:
                            distance_score = 10.0
                        elif distance_miles <= 15:
                            distance_score = 7.0
                        elif distance_miles <= 30:
                            distance_score = 4.0
                        else:
                            distance_score = 2.0
                    elif max_distance == 'within_5km':
                        max_miles = 3.1  # 5km
                        if distance_miles <= max_miles:
                            distance_score = 10.0
                        else:
                            # Penalty for exceeding
                            distance_score = max(0.0, 10.0 - (distance_miles - max_miles) * 2.0)
                    elif max_distance == 'within_15km':
                        max_miles = 9.3  # 15km
                        if distance_miles <= 5:
                            distance_score = 10.0
                        elif distance_miles <= max_miles:
                            distance_score = 7.0
                        else:
                            distance_score = max(0.0, 7.0 - (distance_miles - max_miles) * 0.5)
                    elif max_distance == 'within_30km':
                        max_miles = 18.6  # 30km
                        if distance_miles <= 5:
                            distance_score = 10.0
                        elif distance_miles <= 15:
                            distance_score = 8.0
                        elif distance_miles <= max_miles:
                            distance_score = 5.0
                        else:
                            distance_score = max(0.0, 5.0 - (distance_miles - max_miles) * 0.3)
            except (ValueError, TypeError, Exception):
                distance_score = 5.0  # Default score if calculation fails
        else:
            # Default score if coordinates missing
            distance_score = 5.0
        
        score += distance_score
        
        # 2. Public transport (3 points)
        transport_score = 0.0
        if home.get('public_transport_nearby', False):
            transport_score += 3.0
        bus_distance = home.get('bus_stop_distance')
        if bus_distance is not None:
            try:
                if float(bus_distance) <= 400:  # meters
                    transport_score += 2.0
            except (ValueError, TypeError):
                pass
        
        train_distance = home.get('train_station_distance')
        if train_distance is not None:
            try:
                if float(train_distance) <= 1000:  # meters
                    transport_score += 1.5
            except (ValueError, TypeError):
                pass
        
        score += transport_score
        
        # 3. Parking availability (2 points)
        parking_score = 0.0
        if home.get('visitor_parking', False):
            parking_score += 2.0
        elif home.get('parking_available', False):
            parking_score += 1.0
        
        score += parking_score
        
        return min(score / max_score, 1.0)
    
    def _calculate_cultural_social(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """
        Calculate cultural & social score (0-1.0)
        
        Factors (15 points total):
        - Visitor engagement: 8 points
        - Community integration: 4 points
        - Activity programs: 3 points
        """
        score = 0.0
        max_score = 15.0
        
        safety_needs = user_profile.get('section_4_safety_special_needs', {})
        social_personality = safety_needs.get('q16_social_personality', '')
        
        # 1. Visitor engagement (8 points)
        visitor_score = 0.0
        google_data = enriched_data.get('google_places', {})
        
        # Review frequency and patterns
        review_count = google_data.get('review_count') or home.get('google_review_count') or 0
        if review_count is not None:
            try:
                review_count = float(review_count)
                if review_count >= 50:
                    visitor_score += 3.0
                elif review_count >= 20:
                    visitor_score += 2.0
                elif review_count >= 10:
                    visitor_score += 1.0
            except (ValueError, TypeError):
                pass
        
        # Dwell time and repeat visitors (from Google Places Insights if available)
        dwell_time = google_data.get('average_dwell_time_minutes')
        if dwell_time is not None:
            try:
                dwell_time = float(dwell_time)
                if dwell_time >= 60:
                    visitor_score += 3.0
                elif dwell_time >= 30:
                    visitor_score += 2.0
                elif dwell_time >= 15:
                    visitor_score += 1.0
            except (ValueError, TypeError):
                pass
        
        repeat_visitor_rate = google_data.get('repeat_visitor_rate')
        if repeat_visitor_rate is not None:
            try:
                repeat_visitor_rate = float(repeat_visitor_rate)
                if repeat_visitor_rate >= 0.5:
                    visitor_score += 2.0
                elif repeat_visitor_rate >= 0.3:
                    visitor_score += 1.0
            except (ValueError, TypeError):
                pass
        
        score += min(visitor_score, 8.0)
        
        # 2. Community integration (4 points)
        community_score = 0.0
        if home.get('local_partnerships', False):
            community_score += 2.0
        if home.get('community_events', False):
            community_score += 1.0
        community_integration_score = enriched_data.get('google_places', {}).get('community_integration_score')
        if community_integration_score is not None:
            try:
                if float(community_integration_score) > 0.5:
                    community_score += 1.0
            except (ValueError, TypeError):
                pass
        
        score += min(community_score, 4.0)
        
        # 3. Activity programs (3 points)
        activity_score = 0.0
        activities = home.get('activities', [])
        if isinstance(activities, str):
            activities = [activities]
        
        # Match activities to social personality
        # Support both variants: 'very_social'/'very_sociable', 'moderately_social'/'moderately_sociable'
        if social_personality in ('very_social', 'very_sociable'):
            if len(activities) >= 5:
                activity_score = 3.0
            elif len(activities) >= 3:
                activity_score = 2.0
        elif social_personality in ('moderately_social', 'moderately_sociable'):
            if len(activities) >= 3:
                activity_score = 2.5
            elif len(activities) >= 1:
                activity_score = 1.5
        else:  # prefers_quiet
            if len(activities) >= 1:
                activity_score = 1.0
        
        score += min(activity_score, 3.0)
        
        return min(score / max_score, 1.0)
    
    def _calculate_financial_stability(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """
        Calculate financial stability score (0-1.0)
        
        Factors (20 points total) per spec v3.0:
        - Altman Z-Score: 10 points
        - Director Stability: 3 points  
        - Ownership Stability: 2 points
        - Accounts Status: 5 points
        
        Uses CompaniesHouseService scoring_data if available,
        otherwise falls back to enriched_data.financial_data
        """
        score = 0.0
        max_score = 20.0
        
        # Check for Companies House scoring data (new format)
        ch_scoring = enriched_data.get('companies_house_scoring', {})
        if ch_scoring:
            # Use pre-calculated score from CompaniesHouseService
            score = ch_scoring.get('financial_stability_score', 0)
            return min(score / max_score, 1.0)
        
        # Fallback to old format (handle None)
        financial_data = enriched_data.get('financial_data') or {}
        
        # 1. Altman Z-Score (10 points)
        altman_score = 0.0
        altman_z = financial_data.get('altman_z_score')
        if altman_z is not None:
            try:
                altman_z = float(altman_z)
                if altman_z >= 3.0:  # Very safe
                    altman_score = 10.0
                elif altman_z >= 2.5:  # Safe
                    altman_score = 7.0
                elif altman_z >= 1.5:  # Watch
                    altman_score = 3.0
                # < 1.5 = 0 (bankruptcy risk)
            except (ValueError, TypeError):
                altman_score = 5.0  # Default if no data
        else:
            altman_score = 5.0  # Default if no data
        
        score += altman_score
        
        # 2. Director Stability (3 points)
        director_score = 0.0
        director_data = financial_data.get('director_stability', {})
        resignations = director_data.get('resignations_last_2_years', 0)
        active_directors = director_data.get('active_directors', 2)
        
        if resignations == 0 and active_directors >= 2:
            director_score = 3.0
        elif resignations <= 1:
            director_score = 2.0
        elif resignations <= 2:
            director_score = 1.0
        # > 2 resignations = 0
        
        score += director_score
        
        # 3. Ownership Stability (2 points)
        ownership_score = 0.0
        ownership_data = financial_data.get('ownership_stability', {})
        ownership_changes = ownership_data.get('changes_last_5_years', 0)
        is_pe = ownership_data.get('is_private_equity', False)
        
        if ownership_changes <= 1 and not is_pe:
            ownership_score = 2.0
        elif ownership_changes <= 2:
            ownership_score = 1.0
        # > 2 changes or PE = 0
        
        score += ownership_score
        
        # 4. Accounts Status (5 points)
        accounts_score = 0.0
        accounts_overdue = financial_data.get('accounts_overdue', False)
        if not accounts_overdue:
            accounts_score = 5.0
        
        score += accounts_score
        
        return min(score / max_score, 1.0)
    
    def _calculate_staff_quality(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """
        Calculate staff quality score (0-1.0)
        
        Uses StaffQualityService data if available (from staff_quality enrichment),
        otherwise falls back to legacy staff_data fields.
        
        Factors (20 points total):
        - Staff Quality Score from StaffQualityService: up to 16 points (based on 0-100 score)
        - CQC Well-Led/Effective ratings: 4 bonus points
        OR (fallback):
        - Employee satisfaction: 8 points
        - Staff tenure: 7 points
        - Turnover rate: 5 points
        """
        score = 0.0
        max_score = 20.0
        
        # Priority 1: Use StaffQualityService enriched data if available
        staff_quality = enriched_data.get('staff_quality', {})
        staff_quality_score_data = staff_quality.get('staff_quality_score', {})
        
        if staff_quality_score_data and staff_quality_score_data.get('overall_score') is not None:
            # Use the comprehensive staff quality score (0-100 scale)
            overall_score = staff_quality_score_data.get('overall_score', 0)
            try:
                overall_score = float(overall_score)
            except (ValueError, TypeError):
                overall_score = 0.0
            
            # Convert 0-100 to 0-16 points (max 16 from overall score)
            base_score = (overall_score / 100) * 16.0
            score += base_score
            
            # Bonus points from CQC components (max 4 points)
            components = staff_quality_score_data.get('components', {})
            
            # CQC Well-Led bonus (0-2 points)
            well_led = components.get('cqc_well_led', {})
            well_led_rating = well_led.get('rating', '')
            if well_led_rating == 'Outstanding':
                score += 2.0
            elif well_led_rating == 'Good':
                score += 1.5
            elif well_led_rating == 'Requires improvement':
                score += 0.5
            
            # CQC Effective bonus (0-2 points)
            effective = components.get('cqc_effective', {})
            effective_rating = effective.get('rating', '')
            if effective_rating == 'Outstanding':
                score += 2.0
            elif effective_rating == 'Good':
                score += 1.5
            elif effective_rating == 'Requires improvement':
                score += 0.5
            
            return min(score / max_score, 1.0)
        
        # Priority 2: Fallback to legacy staff_data fields
        staff_data = enriched_data.get('staff_data', {})
        
        # 1. Employee satisfaction (8 points)
        satisfaction_score = 0.0
        glassdoor_rating_raw = staff_data.get('glassdoor_rating', 0)
        try:
            glassdoor_rating = float(glassdoor_rating_raw) if glassdoor_rating_raw is not None else 0.0
        except (ValueError, TypeError):
            glassdoor_rating = 0.0
        
        if glassdoor_rating >= 4.5:
            satisfaction_score = 8.0
        elif glassdoor_rating >= 4.0:
            satisfaction_score = 6.0
        elif glassdoor_rating >= 3.5:
            satisfaction_score = 4.0
        elif glassdoor_rating >= 3.0:
            satisfaction_score = 2.0
        
        score += satisfaction_score
        
        # 2. Staff tenure (7 points)
        tenure_score = 0.0
        avg_tenure_years_raw = staff_data.get('average_tenure_years', 0)
        try:
            avg_tenure_years = float(avg_tenure_years_raw) if avg_tenure_years_raw is not None else 0.0
        except (ValueError, TypeError):
            avg_tenure_years = 0.0
        
        if avg_tenure_years >= 5:
            tenure_score = 7.0
        elif avg_tenure_years >= 3:
            tenure_score = 5.0
        elif avg_tenure_years >= 2:
            tenure_score = 3.0
        elif avg_tenure_years >= 1:
            tenure_score = 1.5
        
        score += tenure_score
        
        # 3. Turnover rate (5 points)
        turnover_score = 5.0
        turnover_rate_raw = staff_data.get('annual_turnover_rate', 0)
        try:
            turnover_rate = float(turnover_rate_raw) if turnover_rate_raw is not None else 0.0
        except (ValueError, TypeError):
            turnover_rate = 0.0
        
        if turnover_rate >= 0.5:  # 50%+
            turnover_score = 0.0
        elif turnover_rate >= 0.3:  # 30-50%
            turnover_score = 1.0
        elif turnover_rate >= 0.2:  # 20-30%
            turnover_score = 2.5
        elif turnover_rate >= 0.1:  # 10-20%
            turnover_score = 4.0
        # < 10% = 5.0
        
        score += turnover_score
        
        return min(score / max_score, 1.0)
    
    def _calculate_cqc_compliance(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """
        Calculate CQC compliance score (0-1.0)
        
        Factors (20 points total):
        - Safe rating: 4 points
        - Effective rating: 4 points
        - Caring rating: 4 points
        - Responsive rating: 4 points
        - Well-led rating: 4 points
        """
        score = 0.0
        max_score = 20.0
        
        cqc_data = enriched_data.get('cqc_detailed', {})
        rating_map = {'Outstanding': 4, 'Good': 3, 'Requires improvement': 1, 'Inadequate': 0}
        
        # Each rating worth 4 points
        ratings = ['safe', 'effective', 'caring', 'responsive', 'well_led']
        for rating_key in ratings:
            rating_value = cqc_data.get(f'{rating_key}_rating', home.get(f'cqc_{rating_key}_rating'))
            if rating_value in rating_map:
                score += rating_map[rating_value]
            else:
                # Default to Good if not specified
                score += 2.0
        
        return min(score / max_score, 1.0)
    
    def _calculate_additional_services(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> float:
        """
        Calculate additional services score (0-1.0)
        
        Factors (11 points total):
        - Physiotherapy: 3 points
        - Mental health services: 3 points
        - Specialist programs: 3 points
        - Enrichment activities: 2 points
        """
        score = 0.0
        max_score = 11.0
        
        medical_needs = user_profile.get('section_3_medical_needs', {})
        medical_conditions = medical_needs.get('q9_medical_conditions', [])
        
        # 1. Physiotherapy (3 points)
        if home.get('physiotherapy_available', False):
            score += 3.0
        
        # 2. Mental health services (3 points)
        if home.get('mental_health_services', False) or home.get('psychologist_available', False):
            score += 3.0
        
        # 3. Specialist programs (3 points)
        specialist_programs = home.get('specialist_programs') or []
        if isinstance(specialist_programs, str):
            specialist_programs = [specialist_programs]
        if specialist_programs is None:
            specialist_programs = []
        
        program_match = False
        if 'dementia_alzheimers' in medical_conditions:
            if 'dementia' in str(specialist_programs).lower():
                program_match = True
        if 'diabetes' in medical_conditions:
            if 'diabetes' in str(specialist_programs).lower():
                program_match = True
        
        if program_match or len(specialist_programs) >= 2:
            score += 3.0
        elif len(specialist_programs) >= 1:
            score += 1.5
        
        # 4. Enrichment activities (2 points)
        enrichment = home.get('enrichment_activities') or []
        if isinstance(enrichment, str):
            enrichment = [enrichment]
        if enrichment is None:
            enrichment = []
        
        if len(enrichment) >= 5:
            score += 2.0
        elif len(enrichment) >= 3:
            score += 1.0
        
        return min(score / max_score, 1.0)


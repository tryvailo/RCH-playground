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
        normalized_weights = weights.normalize()
        
        # Apply user priorities if provided
        priorities = questionnaire.get('section_6_priorities', {}).get('q18_priority_ranking', {})
        if priorities and priorities.get('priority_order') and priorities.get('priority_weights'):
            normalized_weights = self.apply_user_priorities(normalized_weights, priorities)
            applied_conditions.append('user_priorities_applied')
        
        return normalized_weights, applied_conditions
    
    def apply_user_priorities(
        self,
        base_weights: ScoringWeights,
        user_priorities: Dict[str, Any]
    ) -> ScoringWeights:
        """
        Apply user priorities to base weights (from dynamic weights).
        
        Args:
            base_weights: Base scoring weights (from dynamic weights)
            user_priorities: User priority ranking from questionnaire
                {
                    'priority_order': ['quality_reputation', 'cost_financial', ...],
                    'priority_weights': [40, 30, 20, 10]
                }
        
        Returns:
            Adjusted ScoringWeights with user priorities applied
        """
        if not user_priorities:
            return base_weights
        
        priority_order = user_priorities.get('priority_order', [])
        priority_weights = user_priorities.get('priority_weights', [])
        
        if not priority_order or not priority_weights or len(priority_order) != len(priority_weights):
            return base_weights
        
        # Map user priorities to algorithm categories
        priority_mapping = {
            'quality_reputation': {
                'cqc': 0.5,      # 50% of priority weight goes to CQC
                'staff': 0.5     # 50% of priority weight goes to staff
            },
            'cost_financial': {
                'financial': 1.0  # 100% of priority weight goes to financial
            },
            'location_social': {
                'location': 0.5,  # 50% of priority weight goes to location
                'social': 0.5     # 50% of priority weight goes to social
            },
            'comfort_amenities': {
                'services': 1.0   # 100% of priority weight goes to services
            }
        }
        
        # Calculate adjustment factors
        # We'll adjust base weights proportionally based on priority weights
        # Priority weight represents how much that category should be emphasized
        
        # Start with base weights
        adjusted = ScoringWeights(
            medical=base_weights.medical,
            safety=base_weights.safety,
            location=base_weights.location,
            social=base_weights.social,
            financial=base_weights.financial,
            staff=base_weights.staff,
            cqc=base_weights.cqc,
            services=base_weights.services
        )
        
        # Calculate total base weight for priority categories
        base_priority_total = (
            adjusted.cqc + adjusted.staff +  # quality_reputation
            adjusted.financial +              # cost_financial
            adjusted.location + adjusted.social +  # location_social
            adjusted.services                # comfort_amenities
        )
        
        if base_priority_total == 0:
            return base_weights
        
        # Apply priority adjustments
        for i, priority_id in enumerate(priority_order):
            if i >= len(priority_weights):
                break
            
            user_weight_percent = priority_weights[i]  # e.g., 40 for 40%
            mapping = priority_mapping.get(priority_id, {})
            
            if not mapping:
                continue
            
            # Calculate how much to adjust each category
            # The idea: if user prioritizes quality_reputation at 40%, 
            # we should increase cqc and staff weights proportionally
            for category, ratio in mapping.items():
                if hasattr(adjusted, category):
                    current_weight = getattr(adjusted, category)
                    # Calculate target weight based on priority
                    # Priority weight is a percentage of the total priority space
                    target_total = base_priority_total * (user_weight_percent / 100.0)
                    target_weight = target_total * ratio
                    
                    # Adjust proportionally (don't make huge jumps)
                    adjustment_factor = (target_weight / current_weight) if current_weight > 0 else 1.0
                    # Limit adjustment to reasonable range (0.5x to 2x)
                    adjustment_factor = max(0.5, min(2.0, adjustment_factor))
                    
                    new_weight = current_weight * adjustment_factor
                    setattr(adjusted, category, new_weight)
        
        # Normalize to ensure sum = 100%
        return adjusted.normalize()
    
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
        if home_care_types is None:
            home_care_types = []
        
        # Check for dementia care
        if 'dementia_alzheimers' in medical_conditions:
            # Check multiple ways: care_types list, care_dementia boolean, name
            home_care_types_str = str(home_care_types).lower()
            has_dementia = (
                'dementia' in home_care_types_str or
                home.get('care_dementia', False) or
                'dementia' in str(home.get('name', '')).lower() or
                'specialised_dementia' in care_types
            )
            if has_dementia:
                specialist_score += 4.0
        
        # Check for diabetes care
        # Note: specialist_care field may not exist in CSV, check care_types and name instead
        if 'diabetes' in medical_conditions:
            home_name = str(home.get('name', '')).lower()
            home_care_types_str = str(home_care_types).lower()
            if 'diabetes' in home_name or 'diabetes' in home_care_types_str or 'diabetes' in str(home.get('specialist_care', '')).lower():
                specialist_score += 2.0
        
        # Check for cardiac care
        if 'heart_conditions' in medical_conditions:
            home_name = str(home.get('name', '')).lower()
            home_care_types_str = str(home_care_types).lower()
            if 'cardiac' in home_name or 'cardiac' in home_care_types_str or 'cardiac' in str(home.get('specialist_care', '')).lower() or 'heart' in home_name:
                specialist_score += 2.0
        
        # Check for mobility support
        if 'mobility_problems' in medical_conditions or mobility_level in ['wheelchair_bound', 'limited_mobility']:
            # Support both field names: wheelchair_accessible (DB) and wheelchair_access (CSV)
            wheelchair_accessible = home.get('wheelchair_accessible', False) or home.get('wheelchair_access', False)
            if wheelchair_accessible:
                specialist_score += 2.0
        
        specialist_score = min(specialist_score, 10.0)
        score += specialist_score
        
        # 2. Nursing level (8 points)
        # PRIORITY: Use enriched_data (API) first, then fallback to home (DB)
        nursing_score = 0.0
        if 'medical_nursing' in care_types:
            if home.get('care_nursing', False) or 'nursing' in str(home_care_types).lower():
                nursing_score += 5.0
                # Check for RN count from enriched_data (API) first
                rn_count = (
                    enriched_data.get('staff_data', {}).get('registered_nurses') or  # API data first
                    enriched_data.get('staff_quality', {}).get('staff_quality_score', {}).get('components', {}).get('registered_nurses', {}).get('count') or  # Staff Quality API
                    home.get('registered_nurses') or  # DB/CSV fallback
                    0
                )
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
        # Note: medical_equipment and on_site_pharmacy may not exist in CSV
        # Use nursing care as proxy for medical equipment availability
        equipment_score = 0.0
        
        # If home has nursing care, assume basic medical equipment
        if home.get('care_nursing', False) or 'nursing' in str(home_care_types).lower():
            equipment_score += 3.0  # Nursing homes typically have medical equipment
        
        # Check for medical equipment field (if exists)
        if home.get('medical_equipment', False):
            equipment_score += 3.0
        
        # Check for on-site pharmacy (if exists)
        if home.get('on_site_pharmacy', False):
            equipment_score += 2.0
        
        # Check enriched data for emergency protocols
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
        # PRIORITY: Use enriched_data (API) first, then fallback to home (DB)
        cqc_trend_score = 0.0
        cqc_data = enriched_data.get('cqc_detailed', {})
        
        # Try multiple field name variations for overall rating
        # PRIORITY 1: enriched_data (from API)
        # PRIORITY 2: home data (from DB/CSV)
        overall_rating = (
            cqc_data.get('overall_rating') or  # API data first
            cqc_data.get('current_rating') or   # API alternative
            home.get('cqc_rating_overall') or   # DB/CSV fallback
            home.get('rating') or
            home.get('overall_rating') or
            home.get('cqc_rating')
        )
        
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
            # PRIORITY: Use enriched_data safe_rating first, then fallback
            safe_rating = (
                cqc_data.get('safe_rating') or  # API data first
                cqc_data.get('detailed_ratings', {}).get('safe', {}).get('rating') or  # API nested
                home.get('cqc_rating_safe') or   # DB/CSV fallback
                overall_rating
            )
            if safe_rating in rating_map:
                cqc_trend_score += rating_map[safe_rating] * 1.5
        
        score += max(0.0, min(cqc_trend_score, 10.0))
        
        # 2. FSA food safety (8 points) - Updated for spec v3.0
        # PRIORITY: Use enriched_data (API) first, then fallback to home (DB)
        fsa_score = 0.0
        
        # Check for FSA detailed scoring data (new format from fsa_detailed_service)
        # PRIORITY 1: fsa_scoring (pre-calculated from API)
        fsa_scoring = enriched_data.get('fsa_scoring', {})
        if fsa_scoring:
            # Use pre-calculated points (max 7) scaled to 8
            fsa_points = fsa_scoring.get('fsa_points', 0)
            fsa_score = (fsa_points / 7.0) * 8.0
        else:
            # PRIORITY 2: fsa_detailed (from API)
            # PRIORITY 3: home data (from DB/CSV)
            fsa_data = enriched_data.get('fsa_detailed', {})
            fsa_rating = (
                fsa_data.get('rating') or  # API data first
                fsa_data.get('rating_value') or  # API alternative
                home.get('fsa_rating') or  # DB/CSV fallback
                home.get('food_hygiene_rating')
            )
            
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
        # PRIORITY: Use enriched_data (API) first
        incident_score = 5.0
        incidents = (
            enriched_data.get('cqc_detailed', {}).get('safeguarding_incidents') or  # API data first
            home.get('safeguarding_incidents') or  # DB/CSV fallback
            0
        )
        if incidents is not None:
            try:
                incidents = float(incidents)
                if incidents > 0:
                    incident_score = max(0.0, 5.0 - (incidents * 1.0))
            except (ValueError, TypeError):
                pass
        
        score += incident_score
        
        # 4. Audit compliance (2 points)
        # PRIORITY: Use enriched_data (API) first, then fallback
        audit_score = 0.0
        financial_data = enriched_data.get('financial_data', {})
        companies_house_data = enriched_data.get('companies_house_scoring', {})
        
        # Check filing compliance from API data first
        filing_compliance = (
            companies_house_data.get('filing_compliance') or  # Companies House API
            financial_data.get('filing_compliance') or  # Financial enrichment API
            True  # Default to compliant if no data
        )
        
        if filing_compliance:
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
        
        # PRIORITY: Use enriched_data (API) first, then fallback to home (DB)
        # Check for Companies House scoring data (new format from API)
        ch_scoring = enriched_data.get('companies_house_scoring', {})
        if ch_scoring:
            # Use pre-calculated score from CompaniesHouseService (API)
            score = ch_scoring.get('financial_stability_score', 0)
            if score > 0:
                return min(score / max_score, 1.0)
        
        # PRIORITY 2: Financial data from enrichment API
        # PRIORITY 3: Home data from DB/CSV
        financial_data = enriched_data.get('financial_data') or {}
        
        # Also check if home has financial_stability data
        home_financial = home.get('financial_stability') or home.get('financialStability')
        if isinstance(home_financial, dict):
            # Extract from home financial_stability dict if available
            if home_financial.get('risk_score') is not None:
                risk_score = home_financial.get('risk_score', 50)
                # Convert risk_score (0-100, lower=safer) to stability score (0-20)
                score = max(0, 20 - int(risk_score / 5))
                return min(score / max_score, 1.0)
        
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
        
        # Priority 2: Fallback to CQC Well-Led/Effective ratings (for matching stage)
        # This is used when Staff Quality API hasn't been called yet (saves paid API costs)
        staff_data = enriched_data.get('staff_data', {})
        
        # Check if we have CQC-based estimation (from matching stage)
        if staff_data.get('estimated_from_cqc'):
            # Use CQC Well-Led and Effective ratings to estimate staff quality
            well_led_rating = staff_data.get('cqc_well_led_rating', '')
            effective_rating = staff_data.get('cqc_effective_rating', '')
            
            # Map CQC ratings to points (similar to Priority 1 logic)
            rating_map = {'Outstanding': 4.0, 'Good': 3.0, 'Requires improvement': 1.0, 'Inadequate': 0.0}
            
            well_led_points = rating_map.get(well_led_rating, 0) * 1.5  # Max 6 points
            effective_points = rating_map.get(effective_rating, 0) * 1.5  # Max 6 points
            
            # Base score from CQC ratings (max 12 points, scaled to 16)
            base_score = (well_led_points + effective_points) / 12.0 * 16.0
            
            # Add bonus points
            if well_led_rating == 'Outstanding':
                base_score += 2.0
            elif well_led_rating == 'Good':
                base_score += 1.5
            elif well_led_rating == 'Requires improvement':
                base_score += 0.5
            
            if effective_rating == 'Outstanding':
                base_score += 2.0
            elif effective_rating == 'Good':
                base_score += 1.5
            elif effective_rating == 'Requires improvement':
                base_score += 0.5
            
            score += min(base_score, 16.0)  # Cap at 16 points
            return min(score / max_score, 1.0)
        
        # Priority 3: Fallback to legacy staff_data fields (if available)
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
        
        # PRIORITY: Use enriched_data (API) first, then fallback to home (DB)
        cqc_data = enriched_data.get('cqc_detailed', {})
        rating_map = {'Outstanding': 4, 'Good': 3, 'Requires improvement': 1, 'Inadequate': 0}
        
        # Each rating worth 4 points
        ratings = ['safe', 'effective', 'caring', 'responsive', 'well_led']
        for rating_key in ratings:
            # Try multiple field name variations
            # PRIORITY 1: enriched_data (API)
            # PRIORITY 2: home data (DB/CSV)
            rating_value = (
                cqc_data.get(f'{rating_key}_rating') or  # API direct
                cqc_data.get('detailed_ratings', {}).get(rating_key, {}).get('rating') or  # API nested
                cqc_data.get(f'{rating_key}') or  # API alternative
                home.get(f'cqc_rating_{rating_key}') or  # DB/CSV fallback
                home.get(f'cqc_{rating_key}_rating') or
                home.get(f'{rating_key}_rating')
            )
            
            if rating_value and rating_value in rating_map:
                score += rating_map[rating_value]
            else:
                # Try to infer from overall rating if individual rating not available
                overall_rating = (
                    cqc_data.get('overall_rating') or
                    home.get('cqc_rating_overall') or
                    home.get('rating') or
                    home.get('overall_rating')
                )
                if overall_rating and overall_rating in rating_map:
                    # Use overall rating as fallback (slightly lower score)
                    score += rating_map[overall_rating] * 0.8
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
    
    # ==================== TOP 5 + CATEGORY WINNERS ====================
    
    def select_top_5_with_category_winners(
        self,
        candidates: List[Dict[str, Any]],
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any],
        weights: ScoringWeights
    ) -> Dict[str, Any]:
        """
        Select TOP 5 homes with user priorities, then show winners by categories.
        
        Returns:
            {
                'top_5': [...],  # TOP 5 homes sorted by match score (with priorities)
                'category_winners': {
                    'best_overall': {...},           # Highest total score
                    'best_medical_safety': {...},    # Best Medical & Safety (AUTOMATIC)
                    'priority_1': {...},             # Best match for user's 1st priority
                    'priority_2': {...},             # Best match for user's 2nd priority
                    'priority_3': {...},             # Best match for user's 3rd priority
                    'priority_4': {...}              # Best match for user's 4th priority
                }
            }
        """
        # Score all candidates
        # enriched_data can be:
        # 1. Dict with home_id keys (from report_routes.py)
        # 2. Single dict for all homes (legacy)
        scored_homes = []
        for home in candidates:
            try:
                # Extract enriched_data for this specific home
                home_id = home.get('cqc_location_id') or home.get('id') or home.get('name', 'unknown')
                home_enriched_data = {}
                
                if isinstance(enriched_data, dict):
                    # Check if enriched_data is keyed by home_id
                    if home_id in enriched_data:
                        home_enriched_data = enriched_data[home_id]
                    elif len(enriched_data) > 0 and not any(k in enriched_data for k in ['cqc_detailed', 'fsa_detailed', 'financial_data']):
                        # enriched_data is keyed by home_id, but this home not found
                        # Build basic enriched_data from home data
                        home_enriched_data = {
                            'cqc_detailed': {
                                'overall_rating': home.get('cqc_rating_overall') or home.get('rating'),
                                'safe_rating': home.get('cqc_rating_safe'),
                                'effective_rating': home.get('cqc_rating_effective'),
                                'caring_rating': home.get('cqc_rating_caring'),
                                'responsive_rating': home.get('cqc_rating_responsive'),
                                'well_led_rating': home.get('cqc_rating_well_led'),
                            },
                            'fsa_detailed': {
                                'rating': home.get('fsa_rating') or home.get('food_hygiene_rating')
                            },
                            'financial_data': {},
                            'staff_data': {},
                            'medical_capabilities': {}
                        }
                    else:
                        # enriched_data is a single dict for all homes (legacy)
                        home_enriched_data = enriched_data
                else:
                    # enriched_data is not a dict, use empty
                    home_enriched_data = {}
                
                match_result = self.calculate_156_point_match(
                    home, user_profile, home_enriched_data, weights
                )
                home_data = {
                    'home': home,
                    'match_score': match_result.get('total', 0),
                    'category_scores': match_result.get('category_scores', {}),
                    'match_result': match_result
                }
                scored_homes.append(home_data)
            except Exception as e:
                print(f"⚠️ Error scoring home {home.get('name', 'unknown')}: {e}")
                continue
        
        if not scored_homes:
            return {
                'top_5': [],
                'category_winners': {}
            }
        
        # Sort by match score and take TOP 5
        scored_homes.sort(key=lambda h: h['match_score'], reverse=True)
        top_5 = scored_homes[:5]
        
        # Ensure diversity (different providers and locations)
        top_5_before = top_5.copy()
        top_5, replaced_count = self.ensure_diversity(top_5, scored_homes)
        
        # Log diversity metrics
        diversity_metrics = self._calculate_diversity_metrics(top_5)
        diversity_metrics['replaced_homes'] = replaced_count
        print(f"\n   📊 Diversity Metrics:")
        print(f"      Unique providers: {diversity_metrics['unique_providers']}/{len(top_5)}")
        print(f"      Unique locations: {diversity_metrics['unique_locations']}/{len(top_5)}")
        if replaced_count > 0:
            print(f"      Replaced {replaced_count} homes for diversity")
        
        # Extract user priorities
        priorities = user_profile.get('section_6_priorities', {}).get('q18_priority_ranking', {})
        priority_order = priorities.get('priority_order', [])
        priority_weights = priorities.get('priority_weights', [])
        
        # Map priority IDs to categories (NEW format: quality_reputation, cost_financial, location_social, comfort_amenities)
        # Also support OLD format: medical_safety, quality_reputation, cost_financial, location_social
        priority_mapping = {
            'quality_reputation': {
                'categories': ['cqc', 'staff'],
                'label': 'Quality & Reputation'
            },
            'cost_financial': {
                'categories': ['financial'],
                'label': 'Cost & Financial Stability',
                'use_value_ratio': True
            },
            'location_social': {
                'categories': ['location', 'social'],
                'label': 'Location & Social'
            },
            'comfort_amenities': {
                'categories': ['services'],
                'label': 'Comfort & Amenities'
            },
            # OLD format support (for backward compatibility)
            'medical_safety': {
                'categories': ['medical', 'safety'],
                'label': 'Medical & Safety'
            }
        }
        
        # Find winners
        category_winners = {}
        
        # Best Overall
        if top_5:
            category_winners['best_overall'] = {
                'home': top_5[0]['home'],
                'home_data': top_5[0],
                'label': 'Best Overall Match',
                'reasoning': self.generate_match_reasoning(
                    top_5[0]['home'], 'best_overall', user_profile, enriched_data, top_5[0]
                ),
                'is_automatic': False
            }
        
        # Best Medical & Safety (AUTOMATIC - always shown)
        if top_5:
            best_medical = max(
                top_5,
                key=lambda h: (
                    h['category_scores'].get('medical', 0),
                    h['category_scores'].get('safety', 0)
                )
            )
            category_winners['best_medical_safety'] = {
                'home': best_medical['home'],
                'home_data': best_medical,
                'label': 'Best Medical & Safety',
                'reasoning': self.generate_match_reasoning(
                    best_medical['home'], 'best_medical_safety', user_profile, enriched_data, best_medical
                ),
                'is_automatic': True
            }
        
        # For each user priority
        for i, priority_id in enumerate(priority_order):
            if i >= len(priority_weights):
                break
            
            priority_info = priority_mapping.get(priority_id, {})
            categories = priority_info.get('categories', [])
            label = priority_info.get('label', priority_id)
            weight = priority_weights[i]
            
            if not categories:
                continue
            
            # Skip medical_safety if it's in priorities (it's handled automatically)
            if priority_id == 'medical_safety':
                continue
            
            # Find best match for this priority
            if priority_info.get('use_value_ratio'):
                # For cost, calculate value ratio
                for home_data in top_5:
                    price = self._get_home_price(home_data['home'], user_profile)
                    if price > 0:
                        quality_total = sum(
                            home_data['category_scores'].get(cat, 0)
                            for cat in ['medical', 'safety', 'cqc']
                        )
                        home_data['value_ratio'] = quality_total / (price / 100)
                    else:
                        home_data['value_ratio'] = 0
                
                best_match = max(
                    top_5,
                    key=lambda h: (
                        sum(h['category_scores'].get(cat, 0) for cat in categories),
                        h.get('value_ratio', 0)
                    )
                )
            else:
                best_match = max(
                    top_5,
                    key=lambda h: sum(
                        h['category_scores'].get(cat, 0) for cat in categories
                    )
                )
            
            category_winners[f'priority_{i+1}'] = {
                'home': best_match['home'],
                'home_data': best_match,
                'label': f'Best {label}',
                'priority_rank': i + 1,
                'priority_weight': weight,
                'priority_id': priority_id,
                'reasoning': self.generate_match_reasoning(
                    best_match['home'], f'priority_{i+1}', user_profile, enriched_data, best_match
                ),
                'is_automatic': False
            }
        
        return {
            'top_5': top_5,
            'category_winners': category_winners
        }
    
    def _get_home_price(self, home: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
        """Extract weekly price from home data"""
        try:
            from utils.price_extractor import extract_weekly_price
            price = extract_weekly_price(home)
            return float(price) if price else 0.0
        except:
            # Fallback: try common price fields
            price_fields = ['weekly_price', 'price_weekly', 'cost_weekly', 'weekly_cost']
            for field in price_fields:
                price = home.get(field)
                if price:
                    try:
                        return float(price)
                    except:
                        continue
            return 0.0
    
    def generate_match_reasoning(
        self,
        home: Dict[str, Any],
        category: str,
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any],
        home_data: Dict[str, Any]
    ) -> List[str]:
        """
        Generate reasoning for why this home was selected in this category
        
        Args:
            home: Care home data
            category: 'best_overall', 'best_medical_safety', 'priority_1', etc.
            user_profile: User questionnaire
            enriched_data: Enriched data
            home_data: Full home data with scores
        
        Returns:
            List of reasoning strings
        """
        reasons = []
        category_scores = home_data.get('category_scores', {})
        
        if category == 'best_medical_safety':
            reasons.extend(self._generate_medical_reasoning(home, user_profile, enriched_data, category_scores))
        elif category.startswith('priority_'):
            priorities = user_profile.get('section_6_priorities', {}).get('q18_priority_ranking', {})
            priority_order = priorities.get('priority_order', [])
            priority_index = int(category.split('_')[1]) - 1 if category.split('_')[1].isdigit() else -1
            if 0 <= priority_index < len(priority_order):
                priority = priority_order[priority_index]
                if priority == 'quality_reputation':
                    reasons.extend(self._generate_quality_reasoning(home, enriched_data, category_scores))
                elif priority == 'cost_financial':
                    reasons.extend(self._generate_cost_reasoning(home, user_profile, home_data))
                elif priority == 'location_social':
                    reasons.extend(self._generate_location_reasoning(home, user_profile, category_scores))
                elif priority == 'comfort_amenities':
                    reasons.extend(self._generate_comfort_reasoning(home, category_scores))
        elif category == 'best_overall':
            reasons.extend(self._generate_overall_reasoning(home, user_profile, enriched_data, home_data))
        
        return reasons if reasons else ["Strong match across all criteria"]
    
    def _generate_medical_reasoning(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any],
        category_scores: Dict[str, float]
    ) -> List[str]:
        """Generate reasoning for Best Medical & Safety"""
        reasons = []
        
        medical_score = category_scores.get('medical', 0)
        safety_score = category_scores.get('safety', 0)
        
        if medical_score >= 0.8:
            reasons.append("Excellent medical capabilities matching your needs")
        elif medical_score >= 0.6:
            reasons.append("Good medical support available")
        
        if safety_score >= 0.8:
            reasons.append("Outstanding safety measures and protocols")
        elif safety_score >= 0.6:
            reasons.append("Good safety standards")
        
        # Check for specialist care
        medical_conditions = user_profile.get('section_3_medical_needs', {}).get('q9_medical_conditions', [])
        if 'dementia_alzheimers' in medical_conditions:
            if 'dementia' in str(home.get('care_types', [])).lower():
                reasons.append("Specialist dementia care available")
        
        # CQC Safe rating
        safe_rating = home.get('cqc_rating_safe') or enriched_data.get('cqc_detailed', {}).get('safe_rating')
        if safe_rating == 'Outstanding':
            reasons.append("Outstanding CQC Safe rating - highest safety standards")
        elif safe_rating == 'Good':
            reasons.append("Good CQC Safe rating - meets safety standards")
        
        return reasons
    
    def _generate_quality_reasoning(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any],
        category_scores: Dict[str, float]
    ) -> List[str]:
        """Generate reasoning for Best Quality & Reputation"""
        reasons = []
        
        cqc_score = category_scores.get('cqc', 0)
        staff_score = category_scores.get('staff', 0)
        
        # CQC Overall rating
        cqc_rating = home.get('rating') or home.get('overall_rating') or enriched_data.get('cqc_detailed', {}).get('overall_rating')
        if cqc_rating == 'Outstanding':
            reasons.append("Outstanding CQC rating - recognised excellence")
        elif cqc_rating == 'Good':
            reasons.append("Good CQC rating - reliable care standards")
        
        if staff_score >= 0.8:
            reasons.append("Excellent staff quality and stability")
        elif staff_score >= 0.7:
            reasons.append("Good staff quality and retention")
        
        # Google reviews
        google_rating = home.get('google_rating')
        review_count = home.get('review_count') or home.get('user_ratings_total', 0)
        if google_rating and google_rating >= 4.5:
            reasons.append(f"Exceptional reviews - {google_rating:.1f} stars from {review_count} families")
        elif google_rating and google_rating >= 4.0:
            reasons.append(f"Positive reviews - {google_rating:.1f} stars")
        
        return reasons
    
    def _generate_cost_reasoning(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        home_data: Dict[str, Any]
    ) -> List[str]:
        """Generate reasoning for Best Cost & Financial"""
        reasons = []
        
        price = self._get_home_price(home, user_profile)  # Weekly price
        budget = user_profile.get('section_2_location_budget', {}).get('q7_budget', '')
        
        if price > 0 and budget:
            # Budget ranges in weekly £ (monthly ÷ 4.33)
            # Convert monthly budget to weekly for comparison
            BUDGET_RANGES_WEEKLY = {
                'under_3000_self': (0, 692),       # £3000/month ÷ 4.33
                'under_3000_council': (0, 692),
                '3000_5000_self': (692, 1154),     # £3000-5000/month
                '3000_5000_council': (692, 1154),
                '5000_7000_self': (1154, 1616),    # £5000-7000/month
                '5000_7000_local': (1154, 1616),
                '7000_plus_self': (1616, 5000),    # £7000+/month
                'not_sure': (0, 5000),             # Any budget
            }
            
            min_budget_weekly, max_budget_weekly = BUDGET_RANGES_WEEKLY.get(budget, (0, 5000))
            
            # Check if price is within weekly budget range
            if price <= max_budget_weekly:
                if price <= min_budget_weekly * 0.8:
                    reasons.append("Within budget - affordable pricing")
                elif price <= min_budget_weekly:
                    reasons.append("Within budget - good value")
                else:
                    reasons.append("Within your budget range")
            elif price <= max_budget_weekly * 1.1:
                reasons.append("Slightly over budget but manageable")
            else:
                # Price significantly exceeds budget - don't add positive reason
                pass
        
        # Value ratio
        value_ratio = home_data.get('value_ratio', 0)
        if value_ratio > 1.5:
            reasons.append("Excellent quality-to-price ratio")
        elif value_ratio > 1.0:
            reasons.append("Good value for money")
        
        # Financial stability
        financial_score = home_data.get('category_scores', {}).get('financial', 0)
        if financial_score >= 0.8:
            reasons.append("Strong financial stability - reliable provider")
        
        return reasons
    
    def _generate_location_reasoning(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        category_scores: Dict[str, float]
    ) -> List[str]:
        """Generate reasoning for Best Location & Social"""
        reasons = []
        
        distance_km = home.get('distance_km')
        if distance_km is not None:
            if distance_km <= 5:
                reasons.append("Very close to your preferred location (within 5km)")
            elif distance_km <= 15:
                reasons.append("Convenient location (within 15km)")
        
        location_score = category_scores.get('location', 0)
        if location_score >= 0.8:
            reasons.append("Excellent location and accessibility")
        
        social_score = category_scores.get('social', 0)
        if social_score >= 0.8:
            reasons.append("Wide range of social activities and programs")
        elif social_score >= 0.6:
            reasons.append("Good variety of social activities")
        
        return reasons
    
    def _generate_comfort_reasoning(
        self,
        home: Dict[str, Any],
        category_scores: Dict[str, float]
    ) -> List[str]:
        """Generate reasoning for Best Comfort & Amenities"""
        reasons = []
        
        services_score = category_scores.get('services', 0)
        if services_score >= 0.7:
            reasons.append("Modern facilities and comfortable living spaces")
        
        # Check for additional services
        services = home.get('additional_services', [])
        if isinstance(services, str):
            services = [services]
        if len(services) >= 3:
            reasons.append("Comprehensive range of additional services")
        
        return reasons
    
    def ensure_diversity(
        self,
        top_5: List[Dict[str, Any]],
        all_scored_homes: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Ensure diversity in TOP 5 by avoiding duplicate providers and locations.
        
        Args:
            top_5: Current top 5 homes
            all_scored_homes: All scored homes (for finding alternatives)
        
        Returns:
            Tuple of (List of 5 homes with diversity ensured, count of replaced homes)
        """
        if len(top_5) < 2:
            return top_5, 0
        
        diverse_homes = []
        used_providers = set()
        used_locations = set()
        replaced_count = 0
        
        # First pass: add homes with unique providers and locations
        for home_data in top_5:
            provider_id = self._get_provider_id(home_data)
            location_id = self._get_location_id(home_data)
            
            # Check if this home adds diversity
            provider_duplicate = provider_id and provider_id in used_providers
            location_duplicate = location_id and location_id in used_locations
            
            # If no duplicates, add it
            if not provider_duplicate and not location_duplicate:
                diverse_homes.append(home_data)
                if provider_id:
                    used_providers.add(provider_id)
                if location_id:
                    used_locations.add(location_id)
            elif len(diverse_homes) < 5:
                # If we still need homes, check if we can find an alternative
                alternative = self._find_diverse_alternative(
                    home_data, all_scored_homes, used_providers, used_locations, diverse_homes
                )
                if alternative:
                    diverse_homes.append(alternative)
                    replaced_count += 1
                    alt_provider = self._get_provider_id(alternative)
                    alt_location = self._get_location_id(alternative)
                    if alt_provider:
                        used_providers.add(alt_provider)
                    if alt_location:
                        used_locations.add(alt_location)
                else:
                    # No alternative found, add original (better than nothing)
                    diverse_homes.append(home_data)
                    if provider_id:
                        used_providers.add(provider_id)
                    if location_id:
                        used_locations.add(location_id)
            
            if len(diverse_homes) >= 5:
                break
        
        # If we don't have 5 homes yet, fill from remaining top_5
        if len(diverse_homes) < 5:
            for home_data in top_5:
                if home_data not in diverse_homes:
                    diverse_homes.append(home_data)
                    if len(diverse_homes) >= 5:
                        break
        
        # If still not 5, fill from all_scored_homes
        if len(diverse_homes) < 5:
            for home_data in all_scored_homes:
                if home_data not in diverse_homes:
                    provider_id = self._get_provider_id(home_data)
                    location_id = self._get_location_id(home_data)
                    
                    provider_duplicate = provider_id and provider_id in used_providers
                    location_duplicate = location_id and location_id in used_locations
                    
                    if not provider_duplicate or not location_duplicate:
                        diverse_homes.append(home_data)
                        if provider_id:
                            used_providers.add(provider_id)
                        if location_id:
                            used_locations.add(location_id)
                    
                    if len(diverse_homes) >= 5:
                        break
        
        return diverse_homes[:5], replaced_count
    
    def _find_diverse_alternative(
        self,
        current_home: Dict[str, Any],
        all_scored_homes: List[Dict[str, Any]],
        used_providers: set,
        used_locations: set,
        already_selected: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Find an alternative home that adds diversity.
        
        Args:
            current_home: Home we're trying to replace
            all_scored_homes: All available homes
            used_providers: Set of already used provider IDs
            used_locations: Set of already used location IDs
            already_selected: Homes already in diverse list
        
        Returns:
            Alternative home or None
        """
        current_score = current_home.get('match_score', 0)
        
        # Look for alternatives with similar score but different provider/location
        for home_data in all_scored_homes:
            if home_data in already_selected or home_data == current_home:
                continue
            
            # Score should be within 10% of current
            alt_score = home_data.get('match_score', 0)
            if alt_score < current_score * 0.9:
                continue
            
            provider_id = self._get_provider_id(home_data)
            location_id = self._get_location_id(home_data)
            
            # Check if this adds diversity
            provider_duplicate = provider_id and provider_id in used_providers
            location_duplicate = location_id and location_id in used_locations
            
            # If it adds diversity (at least one is different), return it
            if not provider_duplicate or not location_duplicate:
                return home_data
        
        return None
    
    def _get_provider_id(self, home_data: Dict[str, Any]) -> Optional[str]:
        """
        Extract provider identifier from home data.
        
        Args:
            home_data: Home data dict (can be from scored_homes format or direct home dict)
        
        Returns:
            Provider ID (normalized string) or None
        """
        home = home_data.get('home', {}) if 'home' in home_data else home_data
        provider_id = home.get('provider_id') or home.get('providerId')
        provider_name = home.get('provider_name') or home.get('providerName')
        if provider_id:
            return str(provider_id).lower().strip()
        if provider_name:
            return str(provider_name).lower().strip()
        return None
    
    def _get_location_id(self, home_data: Dict[str, Any]) -> Optional[str]:
        """
        Extract location identifier from home data.
        
        Args:
            home_data: Home data dict (can be from scored_homes format or direct home dict)
        
        Returns:
            Location ID (normalized string) or None
        """
        home = home_data.get('home', {}) if 'home' in home_data else home_data
        local_authority = home.get('local_authority') or home.get('localAuthority')
        city = home.get('city')
        postcode = home.get('postcode')
        
        # Use local_authority first, then city, then postcode area
        if local_authority:
            return str(local_authority).lower().strip()
        if city:
            return str(city).lower().strip()
        if postcode:
            # Extract postcode area (first part, e.g., "B1" from "B1 1AA")
            postcode_parts = str(postcode).split()
            if postcode_parts:
                return postcode_parts[0].lower().strip()
        return None
    
    def _calculate_diversity_metrics(
        self,
        homes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate diversity metrics for a list of homes.
        
        Returns:
            {
                'unique_providers': int,
                'unique_locations': int,
                'replaced_homes': int  # Will be set externally
            }
        """
        providers = set()
        locations = set()
        
        for home_data in homes:
            provider_id = self._get_provider_id(home_data)
            location_id = self._get_location_id(home_data)
            
            if provider_id:
                providers.add(provider_id)
            if location_id:
                locations.add(location_id)
        
        return {
            'unique_providers': len(providers),
            'unique_locations': len(locations),
            'replaced_homes': 0  # Will be calculated in ensure_diversity if needed
        }
    
    def _generate_overall_reasoning(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any],
        home_data: Dict[str, Any]
    ) -> List[str]:
        """Generate reasoning for Best Overall Match"""
        reasons = []
        
        match_score = home_data.get('match_score', 0)
        if match_score >= 120:
            reasons.append("Highest overall match score - best fit for your needs")
        
        # User priorities alignment
        priorities = user_profile.get('section_6_priorities', {}).get('q18_priority_ranking', {})
        priority_order = priorities.get('priority_order', [])
        if priority_order:
            priority_labels = {
                'quality_reputation': 'Quality & Reputation',
                'cost_financial': 'Cost & Financial Stability',
                'location_social': 'Location & Social',
                'comfort_amenities': 'Comfort & Amenities'
            }
            top_priority = priority_order[0]
            label = priority_labels.get(top_priority, top_priority)
            reasons.append(f"Best alignment with your top priority: {label}")
        
        return reasons


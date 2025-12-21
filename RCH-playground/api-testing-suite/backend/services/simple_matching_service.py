"""
Simple Matching Service for Bootstrap MVP

Implements 100-point matching algorithm with simplified logic:
- 5 categories instead of 8
- 3 cumulative conditions instead of 6 exclusive priorities
- No user priorities (Section 6) - to be added in v2

Based on MVP_SCORING_SYSTEM.md proposal.
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


@dataclass
class SimpleScoringWeights:
    """Simplified scoring weights for 100-point algorithm (5 categories)"""
    medical_safety: float = 35.0
    quality_care: float = 25.0
    location: float = 15.0
    financial: float = 15.0
    lifestyle: float = 10.0

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
        return {
            'medical_safety': self.medical_safety,
            'quality_care': self.quality_care,
            'location': self.location,
            'financial': self.financial,
            'lifestyle': self.lifestyle
        }

    def normalize(self) -> 'SimpleScoringWeights':
        """Normalize weights to sum to 100%"""
        total = sum([
            self.medical_safety, self.quality_care, self.location,
            self.financial, self.lifestyle
        ])
        if total == 0:
            return self
        
        return SimpleScoringWeights(
            medical_safety=round((self.medical_safety / total) * 100, 1),
            quality_care=round((self.quality_care / total) * 100, 1),
            location=round((self.location / total) * 100, 1),
            financial=round((self.financial / total) * 100, 1),
            lifestyle=round((self.lifestyle / total) * 100, 1)
        )


class SimpleMatchingService:
    """
    Simplified matching service for bootstrap MVP.
    
    Implements 100-point matching algorithm with:
    - 5 categories (Medical & Safety, Quality & Care, Location, Financial, Lifestyle)
    - 3 cumulative conditions (High Risk, Urgent, Long-term)
    - No user priorities (Section 6) - to be added in v2
    """
    
    BASE_WEIGHTS = SimpleScoringWeights()
    
    def calculate_dynamic_weights(
        self,
        questionnaire: Dict[str, Any]
    ) -> Tuple[SimpleScoringWeights, List[str]]:
        """
        Calculate adaptive weights based on user profile.
        Conditions are CUMULATIVE (not mutually exclusive).
        
        Args:
            questionnaire: Professional questionnaire response
            
        Returns:
            Tuple of (SimpleScoringWeights, applied_conditions)
        """
        weights = SimpleScoringWeights()
        applied_conditions = []
        
        # Extract questionnaire data
        medical_needs = questionnaire.get('section_3_medical_needs', {}) or {}
        safety_needs = questionnaire.get('section_4_safety_special_needs', {}) or {}
        timeline = questionnaire.get('section_5_timeline', {}) or {}
        
        fall_history = safety_needs.get('q13_fall_history', '')
        medical_conditions = medical_needs.get('q9_medical_conditions', [])
        placement_timeline = timeline.get('q17_placement_timeline', '')
        
        # ─────────────────────────────────────────────────────
        # CONDITION 1: HIGH RISK (Fall Risk OR Dementia)
        # ─────────────────────────────────────────────────────
        high_risk = False
        
        if fall_history in ['3_plus_or_serious_injuries', 'high_risk_of_falling']:
            high_risk = True
            applied_conditions.append('high_fall_risk')
        
        if 'dementia_alzheimers' in medical_conditions:
            high_risk = True
            applied_conditions.append('dementia')
        
        if high_risk:
            weights.medical_safety += 10  # 35 → 45
            weights.quality_care += 5     # 25 → 30
            weights.lifestyle -= 8        # 10 → 2
            weights.financial -= 7        # 15 → 8
        
        # ─────────────────────────────────────────────────────
        # CONDITION 2: URGENT PLACEMENT
        # ─────────────────────────────────────────────────────
        if placement_timeline == 'urgent_2_weeks':
            weights.location += 8         # 15 → 23
            weights.lifestyle -= 5        # (will clamp to minimum)
            weights.financial -= 3
            applied_conditions.append('urgent_placement')
        
        # ─────────────────────────────────────────────────────
        # CONDITION 3: LONG-TERM PLACEMENT (Financial matters more)
        # ─────────────────────────────────────────────────────
        if placement_timeline in ['6_months_plus', 'planning_ahead']:
            weights.financial += 5        # 15 → 20
            weights.location -= 3
            weights.lifestyle -= 2
            applied_conditions.append('long_term_financial')
        
        # ─────────────────────────────────────────────────────
        # NORMALIZE (ensure sum = 100, no negatives)
        # ─────────────────────────────────────────────────────
        # Clamp negative values to minimum 2%
        weights.medical_safety = max(weights.medical_safety, 2.0)
        weights.quality_care = max(weights.quality_care, 2.0)
        weights.location = max(weights.location, 2.0)
        weights.financial = max(weights.financial, 2.0)
        weights.lifestyle = max(weights.lifestyle, 2.0)
        
        # Normalize to 100
        normalized = weights.normalize()
        
        return normalized, applied_conditions
    
    def calculate_100_point_match(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any],
        weights: Optional[SimpleScoringWeights] = None,
        debug: bool = False
    ) -> Dict[str, Any]:
        # FIX: Validate inputs to prevent NoneType errors
        if home is None:
            raise ValueError("home cannot be None")
        if not isinstance(home, dict):
            raise ValueError(f"home must be a dict, got {type(home)}")
        if user_profile is None:
            user_profile = {}
        if not isinstance(user_profile, dict):
            raise ValueError(f"user_profile must be a dict, got {type(user_profile)}")
        if enriched_data is None:
            enriched_data = {}
        if not isinstance(enriched_data, dict):
            enriched_data = {}
        """
        Calculate match score using simplified 100-point algorithm.
        
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
        
        # Calculate category scores (0-100 normalized scale)
        medical_result = self._calculate_medical_safety(home, user_profile, enriched_data, debug=debug)
        if debug and isinstance(medical_result, tuple):
            medical_score, medical_debug = medical_result
        else:
            medical_score = medical_result
            medical_debug = None
        
        financial_result = self._calculate_financial(home, enriched_data, user_profile, debug=debug)
        if debug and isinstance(financial_result, tuple):
            financial_score, financial_debug = financial_result
        else:
            financial_score = financial_result
            financial_debug = None
        
        quality_care_score = self._calculate_quality_care(home, enriched_data)
        location_score = self._calculate_location(home, user_profile)
        lifestyle_score = self._calculate_lifestyle(home)
        
        category_scores = {
            'medical_safety': medical_score,
            'quality_care': quality_care_score,
            'location': location_score,
            'financial': financial_score,
            'lifestyle': lifestyle_score
        }
        
        # Apply data quality factor (NULL penalty system)
        data_quality_factor = self._calculate_data_quality_factor(home, enriched_data)
        if data_quality_factor != 1.0:
            # Apply factor to all category scores
            for key in category_scores:
                category_scores[key] = min(category_scores[key] * data_quality_factor, 100.0)
        
        # Store debug info if requested
        debug_data = {}
        if debug:
            debug_data = {
                'medical_safety': medical_debug,
                'financial': financial_debug,
                'data_quality_factor': data_quality_factor,
                'api_data_usage': {
                    'cqc_api_used': bool(enriched_data.get('cqc_detailed', {}).get('safe_rating') or enriched_data.get('cqc_detailed', {}).get('detailed_ratings', {}).get('safe', {}).get('rating')),
                    'companies_house_api_used': bool(enriched_data.get('companies_house_scoring') or enriched_data.get('financial_data', {}).get('altman_z_score'))
                }
            }
        
        # Calculate point allocations with adjusted weights
        weights_dict = weights.to_dict()
        
        # Ensure all category scores are floats
        safe_category_scores = {}
        for key, value in category_scores.items():
            if value is None:
                safe_category_scores[key] = 0.0
            else:
                try:
                    safe_category_scores[key] = float(value)
                except (ValueError, TypeError):
                    safe_category_scores[key] = 0.0
        
        # Ensure all weights are floats
        safe_weights = {}
        for key, value in weights_dict.items():
            if value is None:
                safe_weights[key] = 0.0
            else:
                try:
                    safe_weights[key] = float(value)
                except (ValueError, TypeError):
                    safe_weights[key] = 0.0
        
        # Calculate point allocations (0-100 scale)
        point_allocations = {
            'medical_safety': safe_category_scores['medical_safety'] * (safe_weights['medical_safety'] / 100.0),
            'quality_care': safe_category_scores['quality_care'] * (safe_weights['quality_care'] / 100.0),
            'location': safe_category_scores['location'] * (safe_weights['location'] / 100.0),
            'financial': safe_category_scores['financial'] * (safe_weights['financial'] / 100.0),
            'lifestyle': safe_category_scores['lifestyle'] * (safe_weights['lifestyle'] / 100.0)
        }
        
        # Calculate total match score (0-100)
        total_score = sum(point_allocations.values())
        
        # Ensure total_score is a number
        if total_score is None:
            total_score = 0.0
        else:
            try:
                total_score = float(total_score)
            except (ValueError, TypeError):
                total_score = 0.0
        
        # Normalized score is the same as total (0-100 scale)
        normalized = total_score
        
        result = {
            'total': round(total_score, 1),
            'normalized': round(normalized, 1),
            'weights': weights_dict,
            'category_scores': category_scores,
            'point_allocations': point_allocations
        }
        
        if debug and debug_data:
            result['debug'] = debug_data
        
        return result
    
    # ==================== SCORING METHODS (0-100 normalized scale) ====================
    
    def _calculate_medical_safety(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any],
        debug: bool = False
    ) -> float:
        """
        Calculate Medical & Safety score (0-100 normalized).
        
        UPDATED: Includes Service Bands Score (v2) for medical conditions and behavioral concerns.
        
        Components:
        - Service Bands Score: 35 points (NEW! - uses Service User Bands with fallback logic)
        - CQC Safe Rating: 25 points (uses CQC API data)
        - Care Type Match: 20 points (reduced from 30, Service Bands covers conditions)
        - Accessibility: 10 points (reduced from 15)
        - Medication Match: 5 points (reduced from 15, Service Bands covers medical needs)
        - Equipment Match: 3 points (reduced from 10)
        - Age Match: 2 points (reduced from 5)
        
        Total: 100 points (normalized)
        """
        score = 0.0
        debug_info = {} if debug else None
        
        medical_needs = user_profile.get('section_3_medical_needs', {}) or {}
        safety_needs = user_profile.get('section_4_safety_special_needs', {}) or {}
        required_care = medical_needs.get('q8_care_types', [])
        medical_conditions = medical_needs.get('q9_medical_conditions', [])
        mobility_level = medical_needs.get('q10_mobility_level', '')
        medication_management = medical_needs.get('q11_medication_management', 'simple_routine')
        # Q12: Special Equipment (NEW!)
        special_equipment = medical_needs.get('q12_special_equipment', []) or medical_needs.get('special_equipment', [])
        # Q13: Age Range (renamed from q12_age_range to q13_age_range after adding equipment)
        age_range = medical_needs.get('q13_age_range', '') or medical_needs.get('q12_age_range', '')
        fall_history = safety_needs.get('q13_fall_history', '')
        
        # ─────────────────────────────────────────────────────
        # 1. SERVICE BANDS SCORE (35 points) - NEW!
        # ─────────────────────────────────────────────────────
        # Uses Service User Bands to match medical conditions and behavioral concerns
        # with fallback logic for NULL values
        service_bands_score, service_bands_details = self._calculate_service_bands_score_v2(home, user_profile)
        # Scale from 0-100 to 0-35
        service_bands_points = (service_bands_score / 100.0) * 35.0
        score += service_bands_points
        
        if debug_info is not None:
            debug_info['service_bands'] = {
                'score': service_bands_score,
                'points': round(service_bands_points, 2),
                'data_quality': service_bands_details.get('data_quality', {}),
                'checks_count': len(service_bands_details.get('checks', [])),
                'warning': service_bands_details.get('warning')
            }
        
        # ─────────────────────────────────────────────────────
        # 2. CARE TYPE MATCH (20 points) - Reduced from 30
        # ─────────────────────────────────────────────────────
        care_match = 0
        if 'specialised_dementia' in required_care:
            home_care_types = home.get('care_types', [])
            if isinstance(home_care_types, str):
                home_care_types = [home_care_types]
            home_care_types_str = str(home_care_types).lower()
            # UPDATED: Use DB field extractor to check both flat and JSONB fields
            from .db_field_extractor import get_service_user_band
            serves_dementia = get_service_user_band(home, 'dementia_band')
            if (home.get('care_dementia', False) or 
                (serves_dementia if serves_dementia is not None else home.get('serves_dementia_band', False)) or
                'dementia' in home_care_types_str or
                'dementia' in str(home.get('name', '')).lower()):
                care_match = 20
            else:
                care_match = 0  # Critical mismatch
        elif 'medical_nursing' in required_care:
            if home.get('care_nursing', False) or 'nursing' in str(home.get('care_types', '')).lower():
                care_match = 20
            else:
                care_match = 0
        elif 'general_residential' in required_care:
            if home.get('care_residential', False):
                care_match = 20
            else:
                care_match = 10
        else:
            care_match = 20  # No specific requirement
        
        score += care_match
        
        # ─────────────────────────────────────────────────────
        # 3. CQC SAFE RATING (25 points) - USES CQC API DATA
        # ─────────────────────────────────────────────────────
        cqc_data = enriched_data.get('cqc_detailed', {})
        
        # PRIORITY 1: CQC API data (from enriched_data)
        # PRIORITY 2: DB/CSV fallback
        # UPDATED: Use DB field extractor for consistent rating retrieval
        from .db_field_extractor import get_cqc_rating
        safe_rating = get_cqc_rating(home, 'safe', enriched_data) or (
            cqc_data.get('safe_rating') or
            cqc_data.get('detailed_ratings', {}).get('safe', {}).get('rating') or
            home.get('cqc_rating_safe') or
            home.get('rating')
        )
        
        # Determine data source for logging
        data_source = 'CQC_API' if (cqc_data.get('safe_rating') or cqc_data.get('detailed_ratings', {}).get('safe', {}).get('rating') or get_cqc_rating(home, 'safe', enriched_data)) else 'DB/CSV'
        
        safe_score = {
            'Outstanding': 25,
            'Good': 20,
            'Requires improvement': 10,
            'Inadequate': 0
        }.get(safe_rating, 12)  # Default if unknown
        
        score += safe_score
        
        if debug_info is not None:
            debug_info['cqc_safe'] = {
                'rating': safe_rating,
                'score': safe_score,
                'data_source': data_source,
                'has_api_data': bool(cqc_data.get('safe_rating') or cqc_data.get('detailed_ratings', {}).get('safe', {}).get('rating'))
            }
        
        # ─────────────────────────────────────────────────────
        # 4. ACCESSIBILITY (10 points) - Reduced from 15
        # ─────────────────────────────────────────────────────
        needs_wheelchair = (
            'mobility_problems' in medical_conditions or
            mobility_level in ['wheelchair_bound', 'limited_mobility', 'wheelchair_user']
        )
        
        if needs_wheelchair:
            wheelchair_accessible = home.get('wheelchair_accessible', False) or home.get('wheelchair_access', False)
            if wheelchair_accessible:
                score += 10
            else:
                score += 2  # Critical for mobility issues - reduced score
        else:
            score += 10  # Not needed, full points
        
        # ─────────────────────────────────────────────────────
        # 5. MEDICATION MATCH (5 points) - Reduced from 15
        # ─────────────────────────────────────────────────────
        medication_score = self._calculate_medication_match(home, medication_management)
        # Scale medication score from 0-15 to 0-5
        medication_score_scaled = (medication_score / 15.0) * 5.0
        score += medication_score_scaled
        
        # ─────────────────────────────────────────────────────
        # 6. EQUIPMENT MATCH (3 points) - Reduced from 10
        # ─────────────────────────────────────────────────────
        equipment_score = self._calculate_equipment_match(home, special_equipment)
        # Scale equipment score from 0-10 to 0-3
        equipment_score_scaled = (equipment_score / 10.0) * 3.0
        score += equipment_score_scaled
        
        # ─────────────────────────────────────────────────────
        # 7. AGE MATCH (2 points) - Reduced from 5
        # ─────────────────────────────────────────────────────
        age_score = self._calculate_age_match(home, age_range)
        # Scale age score from 0-10 to 0-2
        age_score_scaled = (age_score / 10.0) * 2.0
        score += age_score_scaled
        
        # ─────────────────────────────────────────────────────
        # 7. SPECIAL NEEDS MATCH (0 points) - Removed, integrated into other components
        # Dementia secure garden is now part of care type match
        # ─────────────────────────────────────────────────────
        
        return min(score, 100.0)
    
    def _calculate_medication_match(
        self,
        home: Dict[str, Any],
        medication_management: str
    ) -> float:
        """
        Calculate medication management match score (0-15 points).
        
        Complex medication requires nursing care.
        """
        # Complex medication requires nursing care
        complex_meds = medication_management in ['complex_medication', 'multiple_medications']
        
        if complex_meds:
            # Check if home has nursing care
            # UPDATED: Use DB field extractor to check both flat and JSONB fields
            from .db_field_extractor import get_regulated_activity
            has_nursing_license = get_regulated_activity(home, 'nursing_care')
            has_nursing = (
                home.get('care_nursing', False) or
                'nursing' in str(home.get('care_types', '')).lower() or
                (has_nursing_license if has_nursing_license is not None else home.get('has_nursing_care_license', False))
            )
            if has_nursing:
                return 15.0  # Perfect match
            else:
                return 6.0   # No nursing - risk for complex meds (40% of 15)
        else:
            # Simple routine - any home suitable
            return 15.0
    
    def _calculate_age_match(
        self,
        home: Dict[str, Any],
        age_range: str
    ) -> float:
        """
        Calculate age range match score (0-10 points).
        
        Note: This score is scaled to 0-5 in _calculate_medical_safety.
        """
        if not age_range:
            return 10.0  # No data - assume suitable
        
        # UPDATED: Use DB field extractor to check both flat and JSONB fields
        from .db_field_extractor import get_service_user_band
        
        # Young adults (under 65)
        if age_range == 'under_65':
            serves_younger = get_service_user_band(home, 'younger_adults')
            serves_whole = get_service_user_band(home, 'whole_population')
            
            if serves_younger is True:
                return 10.0
            elif serves_whole is True:
                return 8.0
            else:
                return 3.0  # Home for older people - not ideal
        
        # Older adults (65+)
        elif age_range in ['65_74', '75_84', '85_94', '95_plus']:
            serves_older = get_service_user_band(home, 'older_people')
            serves_whole = get_service_user_band(home, 'whole_population')
            
            if serves_older is True:
                return 10.0
            elif serves_whole is True:
                return 9.0
            else:
                return 5.0  # Possibly not suitable
        
        return 10.0  # Unknown age range - assume suitable
    
    def _calculate_equipment_match(
        self,
        home: Dict[str, Any],
        special_equipment: List[str]
    ) -> float:
        """
        Calculate special equipment match score (0-10 points).
        
        Uses care_nursing as proxy for complex equipment availability.
        
        Logic:
        - Complex equipment (oxygen, hospital bed, hoist) requires nursing care
        - Simple equipment (pressure mattress) - most homes have
        - No equipment needed - full points
        
        Args:
            home: Care home data dictionary
            special_equipment: List of required equipment from questionnaire
            
        Returns:
            Score from 0-10 points
        """
        if not special_equipment or 'no_special_equipment' in special_equipment:
            return 10.0  # No equipment needed - full points
        
        # Normalize equipment names (handle different formats)
        equipment_lower = [str(eq).lower().strip() for eq in special_equipment]
        
        # Complex equipment that requires nursing care
        complex_equipment_keywords = [
            'oxygen', 'oxygen_equipment', 'oxygen_support',
            'hospital', 'hospital_bed', 'hospital-style_bed', 'hospital_style_bed',
            'hoist', 'hoist_lift', 'lift', 'patient_hoist'
        ]
        
        # Check if any complex equipment is needed
        needs_complex = any(
            any(keyword in eq for keyword in complex_equipment_keywords)
            for eq in equipment_lower
        )
        
        if needs_complex:
            # Check if home has nursing care (proxy for equipment availability)
            # UPDATED: Use DB field extractor to check both flat and JSONB fields
            from .db_field_extractor import get_regulated_activity
            has_nursing_license = get_regulated_activity(home, 'nursing_care')
            has_nursing = (
                home.get('care_nursing', False) or
                'nursing' in str(home.get('care_types', '')).lower() or
                (has_nursing_license if has_nursing_license is not None else home.get('has_nursing_care_license', False))
            )
            
            if has_nursing:
                return 10.0  # Nursing home likely has complex equipment
            else:
                return 3.0   # Residential may not have (30% of 10)
        else:
            # Simple equipment (pressure mattress, catheter, etc.) - most homes have
            return 8.0  # Assume available (80% of 10)
    
    def _calculate_service_bands_score_v2(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate Service User Bands score with fallback logic (0-100).
        
        NEW: Uses Service User Bands fields from database to match medical conditions
        and behavioral concerns from questionnaire. Implements fallback logic for
        handling NULL values (NULL ≠ FALSE).
        
        Args:
            home: Care home data dictionary
            user_profile: Professional questionnaire response
            
        Returns:
            Tuple of (score: float 0-100, details: dict)
        """
        from .matching_constants import (
            CONDITION_TO_SERVICE_BAND,
            BEHAVIORAL_TO_SERVICE_BAND,
            WEIGHT_VALUES
        )
        from .matching_fallback import check_field_with_fallback
        from .matching_fallback_config import MatchResult
        
        medical = user_profile.get('section_3_medical_needs', {}) or {}
        safety = user_profile.get('section_4_safety_special_needs', {}) or {}
        
        conditions = medical.get('q9_medical_conditions', []) or []
        behavioral = safety.get('q16_behavioral_concerns', []) or safety.get('behavioral_concerns', []) or []
        
        total_weight = 0.0
        achieved_score = 0.0
        details = {
            'checks': [],
            'data_quality': {
                'direct_matches': 0,
                'proxy_matches': 0,
                'unknowns': 0
            }
        }
        
        # ─────────────────────────────────────────────────────
        # CHECK MEDICAL CONDITIONS
        # ─────────────────────────────────────────────────────
        for condition in conditions:
            # Skip if no serious medical conditions
            if condition == 'no_serious_medical':
                continue
                
            mapping = CONDITION_TO_SERVICE_BAND.get(condition)
            if not mapping:
                continue
            
            required_field = mapping.get('required_field')
            if not required_field:
                continue
            
            weight = WEIGHT_VALUES.get(mapping.get('weight', 'medium'), 0.5)
            total_weight += weight
            
            # Check with fallback
            result = check_field_with_fallback(home, required_field, True)
            
            # Calculate score contribution
            if result.result == MatchResult.MATCH:
                contribution = weight * 1.0
                details['data_quality']['direct_matches'] += 1
            elif result.result == MatchResult.PROXY_MATCH:
                contribution = weight * result.score_multiplier
                details['data_quality']['proxy_matches'] += 1
            elif result.result == MatchResult.UNKNOWN:
                contribution = weight * result.score_multiplier
                details['data_quality']['unknowns'] += 1
            else:  # NO_MATCH
                contribution = 0.0
                details['data_quality']['direct_matches'] += 1
            
            achieved_score += contribution
            
            details['checks'].append({
                'requirement': condition,
                'field': required_field,
                'result': result.result.value,
                'confidence': result.confidence,
                'proxy_used': result.proxy_used,
                'weight': weight,
                'contribution': round(contribution, 3)
            })
        
        # ─────────────────────────────────────────────────────
        # CHECK BEHAVIORAL CONCERNS
        # ─────────────────────────────────────────────────────
        for concern in behavioral:
            # Skip if no behavioral concerns
            if concern == 'no_behavioral_concerns':
                continue
                
            mapping = BEHAVIORAL_TO_SERVICE_BAND.get(concern)
            if not mapping:
                continue
            
            required_field = mapping.get('required_field')
            if not required_field:
                continue
            
            weight = WEIGHT_VALUES.get(mapping.get('weight', 'medium'), 0.5)
            total_weight += weight
            
            result = check_field_with_fallback(home, required_field, True)
            
            if result.result in [MatchResult.MATCH, MatchResult.PROXY_MATCH]:
                contribution = weight * result.score_multiplier
                if result.result == MatchResult.MATCH:
                    details['data_quality']['direct_matches'] += 1
                else:
                    details['data_quality']['proxy_matches'] += 1
            elif result.result == MatchResult.UNKNOWN:
                contribution = weight * result.score_multiplier
                details['data_quality']['unknowns'] += 1
            else:
                contribution = 0.0
                details['data_quality']['direct_matches'] += 1
            
            achieved_score += contribution
            
            details['checks'].append({
                'requirement': concern,
                'field': required_field,
                'result': result.result.value,
                'confidence': result.confidence,
                'proxy_used': result.proxy_used,
                'weight': weight,
                'contribution': round(contribution, 3)
            })
            
            # Check amenity requirement (e.g., secure_garden for wandering)
            amenity = mapping.get('amenity_required')
            if amenity:
                amenity_weight = weight * 0.3
                total_weight += amenity_weight
                
                amenity_result = check_field_with_fallback(home, amenity, True)
                
                if amenity_result.result in [MatchResult.MATCH, MatchResult.PROXY_MATCH]:
                    amenity_contribution = amenity_weight * amenity_result.score_multiplier
                    if amenity_result.result == MatchResult.MATCH:
                        details['data_quality']['direct_matches'] += 1
                    else:
                        details['data_quality']['proxy_matches'] += 1
                elif amenity_result.result == MatchResult.UNKNOWN:
                    amenity_contribution = amenity_weight * amenity_result.score_multiplier
                    details['data_quality']['unknowns'] += 1
                else:
                    amenity_contribution = 0.0
                    details['data_quality']['direct_matches'] += 1
                
                achieved_score += amenity_contribution
                
                details['checks'].append({
                    'requirement': f"{concern}_amenity",
                    'field': amenity,
                    'result': amenity_result.result.value,
                    'confidence': amenity_result.confidence,
                    'proxy_used': amenity_result.proxy_used,
                    'weight': amenity_weight,
                    'contribution': round(amenity_contribution, 3)
                })
        
        # ─────────────────────────────────────────────────────
        # CALCULATE FINAL SCORE
        # ─────────────────────────────────────────────────────
        if total_weight == 0:
            score = 100.0  # No requirements = full score
        else:
            score = (achieved_score / total_weight) * 100
        
        # Data quality adjustment
        total_checks = sum(details['data_quality'].values())
        if total_checks > 0:
            unknown_ratio = details['data_quality']['unknowns'] / total_checks
            details['data_quality']['unknown_ratio'] = round(unknown_ratio, 2)
            
            # Add warning if too many unknowns
            if unknown_ratio > 0.5:
                details['warning'] = 'Limited data available for accurate matching'
        
        return round(score, 1), details
    
    def _calculate_data_quality_factor(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """
        Calculate data quality factor (0.8 - 1.2).
        
        Homes with complete data get bonus (1.2).
        Homes with missing data get penalty (0.8).
        
        This creates differentiation even with similar base scores.
        """
        # UPDATED: Import extractor functions at the start of function
        from .db_field_extractor import (
            get_amenity_value,
            get_review_data,
            get_funding_acceptance,
            get_availability_info
        )
        
        completeness = 0
        total_fields = 0
        
        cqc_data = enriched_data.get('cqc_detailed', {})
        financial_data = enriched_data.get('financial_data', {})
        
        # Check key data fields with weights
        checks = [
            # CQC data (weight 2 each for critical ratings)
            (cqc_data.get('overall_rating') or home.get('cqc_rating_overall'), 2),
            (cqc_data.get('safe_rating') or home.get('cqc_rating_safe'), 2),
            (cqc_data.get('caring_rating') or home.get('cqc_rating_caring'), 1),
            (cqc_data.get('effective_rating') or home.get('cqc_rating_effective'), 1),
            (cqc_data.get('responsive_rating') or home.get('cqc_rating_responsive'), 1),  # NEW!
            (cqc_data.get('well_led_rating') or home.get('cqc_rating_well_led'), 1),
            (cqc_data.get('inspection_date') or home.get('cqc_last_inspection_date') or home.get('last_inspection_date'), 1),
            
            # Financial data
            (financial_data.get('altman_z_score') or enriched_data.get('companies_house_scoring', {}).get('altman_z_score'), 2),
            (financial_data.get('revenue_trend'), 1),
            
            # DB data - UPDATED: Use extractor functions for comprehensive field checking
            (home.get('fee_residential_from') or home.get('fee_nursing_from') or home.get('fee_dementia_from'), 2),
            (home.get('beds_total') or home.get('total_beds'), 1),
            (get_amenity_value(home, 'wheelchair_access') is not None, 1),
            (get_amenity_value(home, 'secure_garden') is not None, 1),
            (get_amenity_value(home, 'wifi_available') is not None, 1),
            (get_amenity_value(home, 'parking_onsite') is not None, 1),
            (get_amenity_value(home, 'ensuite_rooms') is not None, 1),
            (get_review_data(home, 'average') is not None, 1),
            (get_review_data(home, 'google') is not None, 1),
            (get_funding_acceptance(home, 'self_funding') is not None, 1),
            (get_funding_acceptance(home, 'local_authority') is not None, 1),
            (get_availability_info(home).get('beds_available') is not None, 1),
        ]
        
        for value, weight in checks:
            total_fields += weight
            if value is not None and value != '':
                completeness += weight
        
        # Calculate factor: 0.8 (0% data) to 1.2 (100% data)
        if total_fields > 0:
            ratio = completeness / total_fields
            factor = 0.8 + (ratio * 0.4)  # 0.8 to 1.2
        else:
            factor = 1.0  # No checks = neutral
        
        return factor
    
    def _calculate_quality_care(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """
        Calculate Quality & Care score (0-100 normalized).
        
        UPDATED: Includes ALL 6 CQC ratings (including Responsive) + inspection freshness.
        
        Components:
        - CQC Ratings: 75 points (Overall: 25, Caring: 20, Effective: 15, Responsive: 10, Well-Led: 5)
        - Inspection Freshness: 15 points
        - Size Factor: 10 points
        - No Enforcement Actions: 15 points (if available)
        """
        score = 0.0
        
        cqc_data = enriched_data.get('cqc_detailed', {})
        
        # ─────────────────────────────────────────────────────
        # 1. CQC RATINGS (75 points total)
        # ─────────────────────────────────────────────────────
        # Overall: 25 points
        # UPDATED: Use DB field extractor for consistent rating retrieval
        from .db_field_extractor import get_cqc_rating
        overall = get_cqc_rating(home, 'overall', enriched_data) or (
            cqc_data.get('overall_rating') or
            cqc_data.get('current_rating') or
            home.get('cqc_rating_overall') or
            home.get('rating')
        )
        overall_score = {
            'Outstanding': 25,
            'Good': 17.5,  # 70% of 25
            'Requires improvement': 8.75,  # 35% of 25
            'Inadequate': 2.5  # 10% of 25
        }.get(overall, 12.5)  # Unknown = 50%
        score += overall_score
        
        # Caring: 20 points
        # UPDATED: Use DB field extractor for consistent rating retrieval
        caring = get_cqc_rating(home, 'caring', enriched_data) or (
            cqc_data.get('caring_rating') or
            cqc_data.get('detailed_ratings', {}).get('caring', {}).get('rating') or
            home.get('cqc_rating_caring')
        )
        caring_score = {
            'Outstanding': 20,
            'Good': 14,  # 70% of 20
            'Requires improvement': 7,  # 35% of 20
            'Inadequate': 2  # 10% of 20
        }.get(caring, 10)  # Unknown = 50%
        score += caring_score
        
        # Effective: 15 points
        # UPDATED: Use DB field extractor for consistent rating retrieval
        effective = get_cqc_rating(home, 'effective', enriched_data) or (
            cqc_data.get('effective_rating') or
            cqc_data.get('detailed_ratings', {}).get('effective', {}).get('rating') or
            home.get('cqc_rating_effective')
        )
        effective_score = {
            'Outstanding': 15,
            'Good': 10.5,  # 70% of 15
            'Requires improvement': 5.25,  # 35% of 15
            'Inadequate': 1.5  # 10% of 15
        }.get(effective, 7.5)  # Unknown = 50%
        score += effective_score
        
        # Responsive: 10 points (NEW!)
        # UPDATED: Use DB field extractor for consistent rating retrieval
        from .db_field_extractor import get_cqc_rating
        responsive = get_cqc_rating(home, 'responsive', enriched_data) or (
            cqc_data.get('responsive_rating') or
            cqc_data.get('detailed_ratings', {}).get('responsive', {}).get('rating') or
            home.get('cqc_rating_responsive')
        )
        responsive_score = {
            'Outstanding': 10,
            'Good': 7,  # 70% of 10
            'Requires improvement': 3.5,  # 35% of 10
            'Inadequate': 1  # 10% of 10
        }.get(responsive, 5)  # Unknown = 50%
        score += responsive_score
        
        # Well-Led: 5 points (reduced from 15 to make room for Responsive)
        # UPDATED: Use DB field extractor for consistent rating retrieval
        well_led = get_cqc_rating(home, 'well_led', enriched_data) or (
            cqc_data.get('well_led_rating') or
            cqc_data.get('detailed_ratings', {}).get('well_led', {}).get('rating') or
            home.get('cqc_rating_well_led') or
            home.get('cqc_well_led_rating')
        )
        well_led_score = {
            'Outstanding': 5,
            'Good': 3.5,  # 70% of 5
            'Requires improvement': 1.75,  # 35% of 5
            'Inadequate': 0.5  # 10% of 5
        }.get(well_led, 2.5)  # Unknown = 50%
        score += well_led_score
        
        # ─────────────────────────────────────────────────────
        # 2. INSPECTION FRESHNESS (15 points)
        # ─────────────────────────────────────────────────────
        # UPDATED: Use DB field extractor to check both flat and enriched data
        from .db_field_extractor import get_inspection_date
        inspection_date = get_inspection_date(home, enriched_data)
        if inspection_date:
            try:
                from datetime import datetime
                # Try to parse various date formats
                if isinstance(inspection_date, str):
                    # Try ISO format first
                    try:
                        insp_date = datetime.fromisoformat(inspection_date.replace('Z', '+00:00'))
                    except:
                        # Try other formats
                        try:
                            insp_date = datetime.strptime(inspection_date, '%Y-%m-%d')
                        except:
                            insp_date = None
                else:
                    insp_date = inspection_date
                
                if insp_date:
                    days_ago = (datetime.now(insp_date.tzinfo) if hasattr(insp_date, 'tzinfo') and insp_date.tzinfo else datetime.now() - insp_date.replace(tzinfo=None)).days
                    if days_ago <= 180:  # < 6 months
                        score += 15
                    elif days_ago <= 365:  # < 1 year
                        score += 12
                    elif days_ago <= 730:  # < 2 years
                        score += 8
                    else:
                        score += 4  # Old inspection
                else:
                    score += 7  # Could not parse
            except Exception:
                score += 7  # Error parsing
        else:
            score += 7  # No data
        
        # ─────────────────────────────────────────────────────
        # 3. SIZE FACTOR (10 points)
        # ─────────────────────────────────────────────────────
        beds = home.get('beds_total') or home.get('total_beds') or home.get('beds')
        if beds:
            try:
                beds = int(beds)
                if 30 <= beds <= 60:
                    score += 10  # Optimal size
                elif 20 <= beds < 30 or 60 < beds <= 80:
                    score += 8
                elif 10 <= beds < 20 or 80 < beds <= 100:
                    score += 6
                else:
                    score += 4  # Very small or very large
            except (ValueError, TypeError):
                score += 5  # Invalid data
        else:
            score += 5  # No data
        
        # ─────────────────────────────────────────────────────
        # 4. NO ENFORCEMENT ACTIONS (15 points)
        # ─────────────────────────────────────────────────────
        enforcement = (
            cqc_data.get('enforcement_actions') or
            cqc_data.get('enforcements') or
            []
        )
        if isinstance(enforcement, list):
            if len(enforcement) == 0:
                score += 15  # No problems
            elif len(enforcement) == 1:
                score += 8  # One problem
            else:
                score += 0  # Multiple problems
        else:
            # If enforcement is not a list, assume no data = neutral
            score += 7.5  # Unknown
        
        return min(score, 100.0)
    
    def _calculate_location(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> float:
        """
        Calculate Location score (0-100 normalized).
        
        UPDATED: Uses linear interpolation for better differentiation.
        FIXED: Added coordinate validation and detailed error handling.
        
        Components:
        - Distance: 70 points (linear interpolation)
        - Within Preferred Radius Bonus: 20 points
        - Accessibility Bonus: 10 points (parking, wheelchair access)
        """
        score = 0.0
        
        location_budget = user_profile.get('section_2_location_budget', {}) or {}
        distance_pref = location_budget.get('q6_max_distance', 'within_30km')
        
        # Parse preferred distance
        preferred_radius = 30.0  # Default
        if distance_pref == 'within_5km':
            preferred_radius = 5.0
        elif distance_pref == 'within_15km':
            preferred_radius = 15.0
        elif distance_pref == 'within_30km':
            preferred_radius = 30.0
        elif distance_pref == 'distance_not_important':
            preferred_radius = 100.0
        
        # Get distance (should be calculated during geo-filtering)
        distance_km = home.get('distance_km', 999)
        if distance_km is None:
            distance_km = 999
        
        # FIX: Validate coordinates and distance
        home_lat = home.get('latitude')
        home_lon = home.get('longitude')
        
        # Check if coordinates are valid
        if home_lat is None or home_lon is None:
            print(f"      ⚠️ [LOCATION SCORE] {home.get('name', 'Unknown')[:30]}: Missing coordinates (lat={home_lat}, lon={home_lon})")
            return 30.0  # Neutral score if no coordinates
        
        try:
            home_lat = float(home_lat)
            home_lon = float(home_lon)
        except (ValueError, TypeError):
            print(f"      ⚠️ [LOCATION SCORE] {home.get('name', 'Unknown')[:30]}: Invalid coordinates (lat={home_lat}, lon={home_lon})")
            return 30.0  # Neutral score if invalid coordinates
        
        # Check for zero coordinates (invalid)
        if home_lat == 0.0 and home_lon == 0.0:
            print(f"      ⚠️ [LOCATION SCORE] {home.get('name', 'Unknown')[:30]}: Zero coordinates")
            return 30.0  # Neutral score if zero coordinates
        
        # Check if distance is valid (not 999 or 9999)
        if distance_km >= 999:
            print(f"      ⚠️ [LOCATION SCORE] {home.get('name', 'Unknown')[:30]}: Invalid distance ({distance_km}km) - coordinates may not be resolved")
            return 30.0  # Neutral score if distance invalid
        
        # ─────────────────────────────────────────────────────
        # 1. DISTANCE SCORE (70 points) - LINEAR INTERPOLATION
        # ─────────────────────────────────────────────────────
        if distance_km <= preferred_radius:
            # Within preferred radius - linear interpolation
            # Closer = better (50-70 points)
            if preferred_radius > 0:
                proximity_ratio = 1.0 - (distance_km / preferred_radius)
                distance_score = 50.0 + (proximity_ratio * 20.0)  # 50-70 points
            else:
                distance_score = 70.0
        else:
            # Beyond preferred radius - penalty per km
            overage = distance_km - preferred_radius
            penalty = min(overage * 2.0, 40.0)  # -2 points per km, max -40
            distance_score = max(50.0 - penalty, 10.0)  # 10-50 points
        
        score += distance_score
        
        # ─────────────────────────────────────────────────────
        # 2. WITHIN PREFERRED RADIUS BONUS (20 points)
        # ─────────────────────────────────────────────────────
        if distance_km <= preferred_radius:
            score += 20
        else:
            score += 0  # Expanded search, no bonus
        
        # ─────────────────────────────────────────────────────
        # 3. ACCESSIBILITY BONUS (10 points)
        # ─────────────────────────────────────────────────────
        # UPDATED: Use DB field extractor for amenities
        from .db_field_extractor import get_amenity_value
        
        parking_onsite = get_amenity_value(home, 'parking_onsite') or home.get('parking_available')
        if parking_onsite is True:
            score += 5
        
        wheelchair_access = get_amenity_value(home, 'wheelchair_access') or home.get('wheelchair_accessible')
        if wheelchair_access is True:
            score += 5
        
        final_score = min(score, 100.0)
        
        # Debug logging for first few homes
        home_name = home.get('name', 'Unknown')[:30]
        if distance_km < 50:  # Only log for reasonable distances
            print(f"      [LOCATION SCORE] {home_name}: distance={distance_km:.1f}km, preferred={preferred_radius}km, score={final_score:.1f}/100")
        
        return final_score
    
    def _calculate_financial(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any],
        user_profile: Optional[Dict[str, Any]] = None,
        debug: bool = False
    ) -> float:
        """
        Calculate Financial Stability score (0-100 normalized).
        
        UPDATED: Includes budget match as primary factor.
        
        Components:
        - Budget Match: 35 points (NEW!)
        - Altman Z-Score: 30 points (uses Companies House API data)
        - Revenue Trend: 20 points (uses Companies House API data)
        - Red Flags Penalty: 15 points max (uses Companies House API data)
        """
        score = 0.0
        debug_info = {} if debug else None
        
        # ─────────────────────────────────────────────────────
        # 1. BUDGET MATCH (35 points) - NEW! CRITICAL!
        # ─────────────────────────────────────────────────────
        budget_score = self._calculate_budget_match(home, user_profile or {})
        score += budget_score
        
        financial_data = enriched_data.get('financial_data', {})
        
        # If no financial data, return budget score only (scaled to 100)
        if not financial_data:
            return min(score * (100.0 / 35.0), 100.0)  # Scale budget to 100 if no other data
        
        # ─────────────────────────────────────────────────────
        # 2. ALTMAN Z-SCORE (30 points) - USES COMPANIES HOUSE API DATA
        # ─────────────────────────────────────────────────────
        # Check Companies House scoring first (pre-calculated)
        ch_scoring = enriched_data.get('companies_house_scoring', {})
        altman_z = None
        data_source = 'None'
        
        if ch_scoring and isinstance(ch_scoring, dict):
            # Use pre-calculated score from Companies House API
            altman_z = ch_scoring.get('altman_z_score')
            data_source = 'Companies_House_API'
        elif financial_data:
            # Use financial_data from API
            altman_z = financial_data.get('altman_z_score')
            data_source = 'Companies_House_API' if altman_z else 'None'
        
        if altman_z is not None:
            try:
                altman_z = float(altman_z)
                if altman_z >= 3.0:
                    z_score = 30  # Excellent
                elif altman_z >= 2.7:
                    z_score = 25  # Good
                elif altman_z >= 2.0:
                    z_score = 18  # Acceptable
                elif altman_z >= 1.8:
                    z_score = 10  # Borderline
                else:
                    z_score = 5   # Poor
            except (ValueError, TypeError):
                z_score = 15  # No data
                data_source = 'None'
        else:
            z_score = 15  # No data
            data_source = 'None'
        
        score += z_score
        
        if debug_info is not None:
            debug_info['altman_z'] = {
                'value': altman_z,
                'score': z_score,
                'data_source': data_source,
                'has_api_data': data_source == 'Companies_House_API'
            }
        
        # ─────────────────────────────────────────────────────
        # 3. REVENUE TREND (20 points) - USES COMPANIES HOUSE API DATA
        # ─────────────────────────────────────────────────────
        revenue_trend = financial_data.get('revenue_trend', '').lower() if financial_data else ''
        trend_data_source = 'Companies_House_API' if (financial_data and financial_data.get('revenue_trend')) else 'None'
        
        trend_score = {
            'growing': 20,
            'stable': 15,
            'declining': 5,
            '': 10  # Unknown
        }.get(revenue_trend, 10)
        
        score += trend_score
        
        if debug_info is not None:
            debug_info['revenue_trend'] = {
                'value': revenue_trend or 'unknown',
                'score': trend_score,
                'data_source': trend_data_source,
                'has_api_data': trend_data_source == 'Companies_House_API'
            }
        
        # ─────────────────────────────────────────────────────
        # 4. RED FLAGS PENALTY (15 points - subtract penalties) - USES COMPANIES HOUSE API DATA
        # ─────────────────────────────────────────────────────
        red_flags = financial_data.get('red_flags', []) if financial_data else []
        penalty = min(len(red_flags) * 5, 15)
        red_flags_score = 15 - penalty
        score += red_flags_score
        
        red_flags_data_source = 'Companies_House_API' if (financial_data and financial_data.get('red_flags')) else 'None'
        
        final_score = min(max(score, 0), 100.0)
        
        if debug_info is not None:
            debug_info['red_flags'] = {
                'count': len(red_flags),
                'penalty': penalty,
                'score': red_flags_score,
                'data_source': red_flags_data_source,
                'has_api_data': red_flags_data_source == 'Companies_House_API'
            }
            debug_info['total'] = final_score
            debug_info['breakdown'] = {
                'budget_match': budget_score,
                'altman_z': z_score,
                'revenue_trend': trend_score,
                'red_flags': red_flags_score
            }
            return final_score, debug_info
        
        return final_score
    
    def _calculate_budget_match(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> float:
        """
        Calculate budget match score (0-35 points).
        
        CRITICAL: This ensures we don't recommend homes outside user's budget.
        """
        location_budget = user_profile.get('section_2_location_budget', {}) or {}
        budget_key = location_budget.get('q7_budget', 'not_sure')
        
        # Budget ranges in weekly £ (monthly ÷ 4.33)
        BUDGET_RANGES = {
            'under_3000_self': (0, 692),       # £3000/month ÷ 4.33
            'under_3000_council': (0, 692),
            '3000_5000_self': (692, 1154),    # £3000-5000/month
            '3000_5000_council': (692, 1154),
            '5000_7000_self': (1154, 1616),   # £5000-7000/month
            '5000_7000_local': (1154, 1616),
            '7000_plus_self': (1616, 5000),   # £7000+/month
            'not_sure': (0, 5000),            # Any budget
        }
        
        min_budget, max_budget = BUDGET_RANGES.get(budget_key, (0, 5000))
        
        # Get home price - use most relevant care type
        medical_needs = user_profile.get('section_3_medical_needs', {}) or {}
        required_care = medical_needs.get('q8_care_types', [])
        
        weekly_fee = None
        if 'specialised_dementia' in required_care:
            weekly_fee = (
                home.get('fee_dementia_from') or
                home.get('fee_nursing_from') or
                home.get('fee_residential_from')
            )
        elif 'medical_nursing' in required_care:
            weekly_fee = (
                home.get('fee_nursing_from') or
                home.get('fee_residential_from')
            )
        else:
            weekly_fee = (
                home.get('fee_residential_from') or
                home.get('fee_nursing_from')
            )
        
        # Try to extract from price strings if needed
        if weekly_fee is None or weekly_fee == 0:
            # Try to extract from price fields that might be strings
            for price_field in ['fee_dementia_from', 'fee_nursing_from', 'fee_residential_from', 'weekly_fee']:
                price_val = home.get(price_field)
                if price_val:
                    try:
                        if isinstance(price_val, str):
                            # Extract number from string like "£1,051" or "1051"
                            import re
                            numbers = re.findall(r'[\d.]+', price_val.replace(',', ''))
                            if numbers:
                                weekly_fee = float(numbers[0])
                                break
                        else:
                            weekly_fee = float(price_val)
                            break
                    except (ValueError, TypeError):
                        continue
        
        if not weekly_fee or weekly_fee == 0:
            return 17.5  # No price data - neutral score (50% of 35)
        
        try:
            weekly_fee = float(weekly_fee)
        except (ValueError, TypeError):
            return 17.5  # Invalid price - neutral score
        
        # Scoring logic
        if weekly_fee <= max_budget:
            if weekly_fee <= min_budget * 0.8:
                return 35.0  # Significantly below budget - excellent
            elif weekly_fee <= min_budget:
                return 33.25  # Below minimum budget - very good (95% of 35)
            else:
                # Within budget - linear interpolation
                if max_budget > min_budget:
                    ratio = (weekly_fee - min_budget) / (max_budget - min_budget)
                    return 31.5 - (ratio * 7.0)  # 31.5 → 24.5 (90% → 70% of 35)
                else:
                    return 31.5  # At budget limit
        else:
            # Exceeds budget - penalty
            overage_pct = (weekly_fee - max_budget) / max_budget
            if overage_pct <= 0.1:
                return 19.25  # Up to 10% over - acceptable (55% of 35)
            elif overage_pct <= 0.2:
                return 14.0   # Up to 20% over - poor (40% of 35)
            elif overage_pct <= 0.3:
                return 8.75   # Up to 30% over - very poor (25% of 35)
            else:
                return 3.5    # Significantly over - minimal score (10% of 35)
    
    def _calculate_lifestyle(
        self,
        home: Dict[str, Any]
    ) -> float:
        """
        Calculate Lifestyle & Amenities score (0-100 normalized).
        
        Renamed from Services/Additional Services.
        
        Components:
        - Room Quality: 40 points
        - Facilities: 40 points
        - Availability: 20 points
        """
        score = 0.0
        
        # ─────────────────────────────────────────────────────
        # 1. ROOM QUALITY (40 points)
        # ─────────────────────────────────────────────────────
        if home.get('ensuite_rooms', False):
            score += 40
        else:
            score += 20
        
        # ─────────────────────────────────────────────────────
        # 2. FACILITIES (40 points)
        # ─────────────────────────────────────────────────────
        # UPDATED: Use DB field extractor to check both flat and JSONB fields
        from .db_field_extractor import get_amenity_value
        facilities_score = 0
        
        # Secure garden (15 points)
        secure_garden = get_amenity_value(home, 'secure_garden')
        if secure_garden is True:
            facilities_score += 15
        elif secure_garden is False:
            facilities_score += 5  # Explicitly not available
        else:
            facilities_score += 10  # Unknown - neutral
        
        # Wheelchair access (10 points)
        wheelchair_access = get_amenity_value(home, 'wheelchair_access') or home.get('wheelchair_accessible')
        if wheelchair_access is True:
            facilities_score += 10
        elif wheelchair_access is False:
            facilities_score += 3  # Explicitly not available
        else:
            facilities_score += 6  # Unknown - neutral
        
        # Size factor (10 points)
        beds_total = home.get('beds_total') or home.get('total_beds')
        if beds_total and beds_total >= 30:
            facilities_score += 10  # Larger = more resources
        elif beds_total:
            facilities_score += 5  # Smaller home
        else:
            facilities_score += 7  # Unknown - neutral
        
        # WiFi available (5 points) - NEW
        wifi_available = get_amenity_value(home, 'wifi_available')
        if wifi_available is True:
            facilities_score += 5
        elif wifi_available is False:
            facilities_score += 1  # Explicitly not available
        else:
            facilities_score += 3  # Unknown - neutral
        
        score += min(facilities_score, 40)
        
        # ─────────────────────────────────────────────────────
        # 3. AVAILABILITY (20 points)
        # ─────────────────────────────────────────────────────
        # UPDATED: Use DB field extractor for availability info
        from .db_field_extractor import get_availability_info
        availability = get_availability_info(home)
        
        has_availability = availability.get('has_availability')
        beds_available = availability.get('beds_available')
        beds_total = availability.get('beds_total')
        availability_status = availability.get('availability_status')
        
        if has_availability is True:
            score += 20  # Confirmed availability
        elif has_availability is False:
            score += 5   # Explicitly no availability
        elif beds_available is not None and beds_available > 0:
            score += 18  # Has available beds
        elif availability_status in ['available_now', 'waitlist']:
            score += 15  # Status indicates availability
        elif availability_status == 'full':
            score += 5   # Explicitly full
        else:
            score += 10  # Unknown availability - neutral
        
        return min(score, 100.0)
    
    def select_top_5_with_category_winners(
        self,
        candidates: List[Dict[str, Any]],
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any],
        weights: Optional[SimpleScoringWeights] = None
    ) -> Dict[str, Any]:
        """
        Select top 5 homes and determine category winners.
        
        Simplified version - no diversity checks for MVP.
        """
        if weights is None:
            weights, _ = self.calculate_dynamic_weights(user_profile)
        
        # Score all candidates
        scored_homes = []
        for candidate in candidates:
            # FIX: Handle None and ensure candidate is a dict
            if candidate is None:
                continue
            
            if not isinstance(candidate, dict):
                print(f"      ⚠️ Skipping invalid candidate (not a dict): {type(candidate)}")
                continue
            
            home = candidate.get('home', candidate)  # Support both formats
            
            # FIX: Ensure home is a dict
            if home is None:
                print(f"      ⚠️ Skipping candidate with None home")
                continue
            
            if not isinstance(home, dict):
                print(f"      ⚠️ Skipping candidate with invalid home type: {type(home)}")
                continue
            
            try:
                # FIX: Ensure user_profile is not None
                if user_profile is None:
                    print(f"      ⚠️ ERROR: user_profile is None for {home.get('name', 'unknown')}")
                    user_profile = {}
                
                # Get enriched_data for this home
                home_id = home.get('cqc_location_id') or home.get('id') or home.get('name', 'unknown')
                home_enriched_data = enriched_data.get(home_id, {}) if enriched_data else {}
                
                # FIX: Ensure enriched_data is a dict
                if home_enriched_data is None:
                    home_enriched_data = {}
                
                match_result = self.calculate_100_point_match(
                    home=home,
                    user_profile=user_profile,
                    enriched_data=home_enriched_data,
                    weights=weights
                )
                scored_homes.append({
                    'home': home,
                    'matchScore': match_result.get('total', 0),
                    'matchResult': match_result,
                    'match_result': match_result,  # Also include for compatibility
                    'category_scores': match_result.get('category_scores', {})
                })
            except Exception as e:
                print(f"⚠️ Error scoring home {home.get('name', 'unknown')}: {e}")
                continue
        
        # Sort by match score
        scored_homes.sort(key=lambda x: x.get('matchScore', 0), reverse=True)
        
        # Select top 5
        top_5 = scored_homes[:5]
        
        # Determine category winners (simplified)
        category_winners = {}
        if top_5:
            # Best Overall
            category_winners['best_overall'] = {
                'home': top_5[0]['home'],
                'label': 'Best Overall Match',
                'reasoning': [f'Highest match score: {top_5[0]["matchScore"]}/100']  # List format for compatibility
            }
            
            # Best for Care (Medical & Safety + Quality & Care)
            best_care = max(
                top_5,
                key=lambda x: (
                    x['matchResult'].get('point_allocations', {}).get('medical_safety', 0) +
                    x['matchResult'].get('point_allocations', {}).get('quality_care', 0)
                )
            )
            category_winners['best_care'] = {
                'home': best_care['home'],
                'label': 'Best for Care Quality',
                'reasoning': ['Highest combined medical safety and quality ratings']  # List format for compatibility
            }
            
            # Best Value (score / price ratio)
            homes_with_price = []
            for home_data in top_5:
                home = home_data['home']
                price = home.get('fee_nursing_from') or home.get('fee_residential_from') or home.get('fee_dementia_from')
                if price and price > 0:
                    homes_with_price.append((home_data, price))
            
            if homes_with_price:
                best_value = max(
                    homes_with_price,
                    key=lambda x: x[0]['matchScore'] / x[1]
                )
                category_winners['best_value'] = {
                    'home': best_value[0]['home'],
                    'label': 'Best Value',
                    'reasoning': ['Best quality-to-price ratio']  # List format for compatibility
                }
        
        return {
            'top_5': top_5,
            'category_winners': category_winners
        }
    
    def generate_match_reasoning(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        match_result: Dict[str, Any]
    ) -> List[str]:
        """
        Generate human-readable reasoning for match.
        Simplified version for MVP.
        """
        reasons = []
        score = match_result.get('total', 0)
        category_scores = match_result.get('category_scores', {})
        
        if score >= 85:
            reasons.append("Excellent match - meets all key criteria")
        elif score >= 70:
            reasons.append("Good match - meets most criteria")
        elif score >= 55:
            reasons.append("Fair match - some compromises may be needed")
        else:
            reasons.append("Acceptable match - consider alternatives")
        
        # Add top category
        if category_scores:
            top_category = max(category_scores.items(), key=lambda x: x[1])
            reasons.append(f"Strong in {top_category[0].replace('_', ' ').title()}")
        
        return reasons


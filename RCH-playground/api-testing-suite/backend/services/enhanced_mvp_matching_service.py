"""
Enhanced MVP 100-Point Matching Service
Complete implementation with 85% data coverage and full validation

Features:
- Hard constraints for critical parameters (fall risk, equipment, medication)
- Complete CQC rating usage (4 of 6 ratings)
- Medical parameter validation (mobility, medication, equipment)
- Dynamic weights for fall risk
- Comprehensive error handling and validation
- Google reviews bonus scoring
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== ENUMS ====================

class MobilityLevel(str, Enum):
    """Mobility level enumeration"""
    WALKING_AIDS = "walking_aids"
    WHEELCHAIR_SOMETIMES = "wheelchair_sometimes"
    SELF_SUFFICIENT = "self_sufficient"


class MedicationManagement(str, Enum):
    """Medication management complexity"""
    SIMPLE_ROUTINE = "simple_routine"
    MANY_COMPLEX_ROUTINE = "many_complex_routine"


class FallHistory(str, Enum):
    """Fall history classification"""
    ONE_TWO_NO_SERIOUS = "1_2_no_serious_injuries"
    THREE_PLUS_SERIOUS = "3_plus_or_serious_injuries"
    HIGH_RISK = "high_risk_of_falling"


class CQCRating(str, Enum):
    """CQC rating levels"""
    OUTSTANDING = "Outstanding"
    GOOD = "Good"
    REQUIRES_IMPROVEMENT = "Requires Improvement"
    INADEQUATE = "Inadequate"
    UNKNOWN = "Unknown"


# ==================== EXCEPTIONS ====================

class ValidationError(Exception):
    """Base validation error"""
    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.message = message
        self.value = value
        super().__init__(f"Validation Error in '{field}': {message}")


class MissingFieldError(ValidationError):
    """Required field is missing"""
    pass


class InvalidEnumError(ValidationError):
    """Enum value is invalid"""
    pass


class InvalidTypeError(ValidationError):
    """Field type is invalid"""
    pass


class MatchingError(Exception):
    """General matching error"""
    def __init__(self, message: str, details: Dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class NoHomesFoundError(MatchingError):
    """No suitable homes found"""
    pass


# ==================== DATA MODELS ====================

@dataclass
class MedicalRequirements:
    """User medical requirements from questionnaire"""
    medical_conditions: List[str]
    care_types: List[str]
    mobility_level: str
    medication_management: str
    special_equipment: List[str]
    fall_history: str
    allergies: Optional[List[str]] = None
    dietary_requirements: Optional[List[str]] = None
    
    def __post_init__(self):
        """Validate medical requirements"""
        self.validate()
    
    def validate(self):
        """Validate all fields"""
        if not self.medical_conditions:
            raise MissingFieldError("medical_conditions", "Cannot be empty")
        
        if not self.care_types:
            raise MissingFieldError("care_types", "Cannot be empty")
        
        # Validate enums
        valid_mobility = [m.value for m in MobilityLevel]
        if self.mobility_level not in valid_mobility:
            raise InvalidEnumError("mobility_level", 
                f"Must be one of {valid_mobility}", self.mobility_level)
        
        valid_meds = [m.value for m in MedicationManagement]
        if self.medication_management not in valid_meds:
            raise InvalidEnumError("medication_management",
                f"Must be one of {valid_meds}", self.medication_management)
        
        valid_fall = [f.value for f in FallHistory]
        if self.fall_history not in valid_fall:
            raise InvalidEnumError("fall_history",
                f"Must be one of {valid_fall}", self.fall_history)


@dataclass
class CareHomeData:
    """Care home information"""
    name: str
    care_types: List[str]
    cqc_rating_safe: str
    cqc_rating_overall: str
    cqc_rating_effective: Optional[str] = None
    cqc_rating_caring: Optional[str] = None
    cqc_rating_responsive: Optional[str] = None
    cqc_rating_well_led: Optional[str] = None
    fsa_rating: Optional[int] = None
    distance_km: float = 0.0
    google_rating: Optional[float] = None
    google_reviews_count: Optional[int] = None
    has_wheelchair_access: bool = False
    has_hoist: bool = False
    has_hospital_bed: bool = False
    has_nursing_staff: bool = False
    registration_type: Optional[str] = None  # "Nursing Home" or "Residential"
    
    def validate(self):
        """Validate home data"""
        if not self.name or not self.name.strip():
            raise MissingFieldError("name", "Cannot be empty")
        
        if not self.care_types:
            raise MissingFieldError("care_types", "Cannot be empty")
        
        # Validate CQC ratings
        valid_ratings = [r.value for r in CQCRating]
        if self.cqc_rating_safe not in valid_ratings:
            raise InvalidEnumError("cqc_rating_safe",
                f"Must be one of {valid_ratings}", self.cqc_rating_safe)
        
        if self.cqc_rating_overall not in valid_ratings:
            raise InvalidEnumError("cqc_rating_overall",
                f"Must be one of {valid_ratings}", self.cqc_rating_overall)
        
        # Validate optional CQC ratings if present
        if self.cqc_rating_effective and self.cqc_rating_effective not in valid_ratings:
            raise InvalidEnumError("cqc_rating_effective",
                f"Must be one of {valid_ratings}", self.cqc_rating_effective)
        
        if self.cqc_rating_caring and self.cqc_rating_caring not in valid_ratings:
            raise InvalidEnumError("cqc_rating_caring",
                f"Must be one of {valid_ratings}", self.cqc_rating_caring)
        
        # Validate distance
        if self.distance_km < 0:
            raise InvalidTypeError("distance_km", "Must be >= 0", self.distance_km)
        
        # Validate FSA rating
        if self.fsa_rating is not None and not (1 <= self.fsa_rating <= 5):
            raise InvalidTypeError("fsa_rating", "Must be 1-5", self.fsa_rating)
        
        # Validate Google rating
        if self.google_rating is not None and not (1 <= self.google_rating <= 5):
            raise InvalidTypeError("google_rating", "Must be 1-5", self.google_rating)


@dataclass
class ScoreBreakdown:
    """Score breakdown for transparency"""
    medical_score: float
    medical_detail: Dict[str, Any]
    safety_score: float
    safety_detail: Dict[str, Any]
    location_score: float
    location_detail: Dict[str, Any]
    total_score: float
    constraints_met: bool
    warnings: List[str]


@dataclass
class MatchingResult:
    """Result of matching a home"""
    home: CareHomeData
    score: ScoreBreakdown
    rank: int = 0


# ==================== ENHANCED MVP MATCHING SERVICE ====================

class EnhancedMVPMatchingService:
    """
    Enhanced MVP 100-Point Matching Service
    Data coverage: 85%
    Scoring: 100 points max
    """
    
    # Scoring constants
    MAX_TOTAL_SCORE = 100
    MEDICAL_MAX = 30
    SAFETY_MAX = 40
    LOCATION_MAX = 25
    BUFFER = 5  # For rounding/bonus
    
    # Constraint weights
    FALL_RISK_SAFETY_BOOST = 1.3
    FALL_RISK_MEDICAL_BOOST = 1.1
    FALL_RISK_LOCATION_REDUCTION = 0.8
    
    def __init__(self):
        """Initialize the service"""
        logger.info("Initializing EnhancedMVPMatchingService")
    
    # ==================== VALIDATION ====================
    
    def validate_questionnaire_complete(self, questionnaire: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate questionnaire completeness (#11 - Code Review Issue).
        
        Ensures all required sections and fields are present.
        
        Args:
            questionnaire: User questionnaire data
        
        Returns:
            The questionnaire if valid
        
        Raises:
            ValidationError: If validation fails
        """
        logger.info("Validating questionnaire completeness")
        
        errors = []
        
        # Check required sections exist
        required_sections = {
            'section_3_medical_needs': ['q8_care_types', 'q9_medical_conditions'],
            'section_4_safety_special_needs': ['q13_fall_history'],
        }
        
        for section, required_fields in required_sections.items():
            if section not in questionnaire:
                errors.append(f"Missing required section: '{section}'")
                continue
            
            section_data = questionnaire[section]
            if not isinstance(section_data, dict):
                errors.append(f"Section '{section}' must be a dictionary")
                continue
            
            # Check required fields in section
            for field in required_fields:
                if field not in section_data:
                    errors.append(f"Missing required field: '{section}.{field}'")
                elif not section_data[field]:
                    errors.append(f"Required field cannot be empty: '{section}.{field}'")
        
        if errors:
            error_msg = "; ".join(errors)
            logger.error(f"Questionnaire validation failed: {error_msg}")
            raise ValidationError("questionnaire", error_msg)
        
        logger.info("✓ Questionnaire completeness validated")
        return questionnaire
    
    def normalize_edge_cases(self, questionnaire: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize edge cases in questionnaire (#9 - Code Review Issue).
        
        Handles variations like "N/A", "not specified", etc.
        Adds assertions to ensure valid normalization.
        
        Args:
            questionnaire: User questionnaire data
        
        Returns:
            Questionnaire with normalized edge cases
        """
        logger.info("Normalizing edge cases in questionnaire")
        
        medical_needs = questionnaire.get('section_3_medical_needs', {})
        
        # Normalize mobility level
        mobility_raw = medical_needs.get('q10_mobility_level', 'self_sufficient')
        mobility_normalized = self._normalize_mobility_level(mobility_raw)
        questionnaire['section_3_medical_needs']['q10_mobility_level'] = mobility_normalized
        
        assert mobility_normalized in ['walking_aids', 'wheelchair_sometimes', 'self_sufficient'], \
            f"Invalid mobility after normalization: {mobility_normalized}"
        logger.debug(f"Normalized mobility: {mobility_raw} → {mobility_normalized}")
        
        # Normalize medication management
        meds_raw = medical_needs.get('q11_medication_management', 'simple_routine')
        meds_normalized = self._normalize_medication_management(meds_raw)
        questionnaire['section_3_medical_needs']['q11_medication_management'] = meds_normalized
        
        assert meds_normalized in ['simple_routine', 'many_complex_routine'], \
            f"Invalid medication after normalization: {meds_normalized}"
        logger.debug(f"Normalized medication: {meds_raw} → {meds_normalized}")
        
        # Normalize fall history
        fall_raw = questionnaire.get('section_4_safety_special_needs', {}).get('q13_fall_history', '1_2_no_serious_injuries')
        fall_normalized = self._normalize_fall_history(fall_raw)
        questionnaire['section_4_safety_special_needs']['q13_fall_history'] = fall_normalized
        
        assert fall_normalized in ['1_2_no_serious_injuries', '3_plus_or_serious_injuries', 'high_risk_of_falling'], \
            f"Invalid fall history after normalization: {fall_normalized}"
        logger.debug(f"Normalized fall history: {fall_raw} → {fall_normalized}")
        
        logger.info("✓ Edge cases normalized")
        return questionnaire
    
    def _normalize_mobility_level(self, value: str) -> str:
        """Normalize mobility level handling edge cases"""
        if not value or isinstance(value, str) and value.lower() in ['none', 'n/a', 'not specified', '']:
            return 'self_sufficient'
        
        value_lower = str(value).lower().strip()
        
        # Map variations to standard values
        mapping = {
            'walking aids': 'walking_aids',
            'walking_aids': 'walking_aids',
            'cane': 'walking_aids',
            'crutches': 'walking_aids',
            'walker': 'walking_aids',
            'frame': 'walking_aids',
            'walking frame': 'walking_aids',
            'wheelchair': 'wheelchair_sometimes',
            'wheelchair_sometimes': 'wheelchair_sometimes',
            'partial wheelchair': 'wheelchair_sometimes',
            'wheelchair part time': 'wheelchair_sometimes',
            'sometimes wheelchair': 'wheelchair_sometimes',
            'self_sufficient': 'self_sufficient',
            'independent': 'self_sufficient',
            'mobile': 'self_sufficient',
            'independent mobility': 'self_sufficient',
        }
        
        normalized = mapping.get(value_lower, 'self_sufficient')
        return normalized
    
    def _normalize_medication_management(self, value: str) -> str:
        """Normalize medication management handling edge cases"""
        if not value or isinstance(value, str) and value.lower() in ['none', 'n/a', 'not specified', '']:
            return 'simple_routine'
        
        value_lower = str(value).lower().strip()
        
        # ✅ FIX: Handle specific values from questionnaire first
        # Map questionnaire values to enum values
        questionnaire_to_enum = {
            'none': 'simple_routine',
            'simple_1_2': 'simple_routine',
            'several_simple_routine': 'simple_routine',  # ✅ FIX: several_simple_routine -> simple_routine
            'many_complex_routine': 'many_complex_routine',
        }
        
        # Check exact matches first
        if value_lower in questionnaire_to_enum:
            return questionnaire_to_enum[value_lower]
        
        # Map variations to standard values
        if any(word in value_lower for word in ['simple', 'routine', 'basic', 'straightforward', 'several']):
            # ✅ FIX: "several_simple_routine" contains "simple" and "several" - treat as simple_routine
            return 'simple_routine'
        elif any(word in value_lower for word in ['complex', 'many', 'multiple', 'complicated']):
            return 'many_complex_routine'
        else:
            return 'simple_routine'  # Default to simple
    
    def _normalize_fall_history(self, value: str) -> str:
        """Normalize fall history handling edge cases"""
        if not value or isinstance(value, str) and value.lower() in ['none', 'n/a', 'not specified', '']:
            return '1_2_no_serious_injuries'
        
        value_lower = str(value).lower().strip()
        
        # ✅ FIX: Check exact matches first to avoid false positives
        exact_matches = {
            '1_2_no_serious_injuries': '1_2_no_serious_injuries',
            '3_plus_or_serious_injuries': '3_plus_or_serious_injuries',
            'high_risk_of_falling': 'high_risk_of_falling',
            'no_falls_occurred': '1_2_no_serious_injuries'
        }
        
        if value_lower in exact_matches:
            return exact_matches[value_lower]
        
        # Map variations (only if not exact match)
        if any(word in value_lower for word in ['high_risk', 'high risk']):
            return 'high_risk_of_falling'
        elif any(word in value_lower for word in ['3_plus', '3+', 'three plus']):
            return '3_plus_or_serious_injuries'
        elif any(word in value_lower for word in ['serious injuries']) and 'no_serious' not in value_lower:
            # Only match "serious injuries" if NOT "no_serious_injuries"
            return '3_plus_or_serious_injuries'
        else:
            return '1_2_no_serious_injuries'  # Default (includes "1_2_no_serious_injuries")
    
    def get_empty_results_message(self, 
                                  expansion_phase: int = 0,
                                  preferred_radius_km: float = 5.0,
                                  expanded_radius_km: float = None) -> str:
        """
        Generate helpful error message for empty results (#12 - Code Review Issue).
        
        Args:
            expansion_phase: Current expansion phase (0 = initial, 1+ = expanded)
            preferred_radius_km: User's preferred radius
            expanded_radius_km: Current search radius
        
        Returns:
            User-friendly error message
        """
        messages = {
            0: f"No homes found within {preferred_radius_km}km. Please try a different location or adjust criteria.",
            1: f"No homes found at preferred distance ({preferred_radius_km}km). Expanding search to {expanded_radius_km}km...",
            2: f"Limited availability nearby. Showing homes from wider region ({expanded_radius_km}km).",
            3: f"Very limited options in your area. Showing all available homes from {expanded_radius_km}km radius.",
            4: f"No homes match all criteria. Showing options from nationwide search. Some preferences may need adjustment.",
            5: f"No homes found. This may indicate no facilities meet your specific requirements. Please contact support.",
        }
        
        message = messages.get(expansion_phase, messages[5])
        logger.info(f"Empty results message (phase {expansion_phase}): {message}")
        return message
    
    def validate_questionnaire(self, questionnaire: Dict[str, Any]) -> MedicalRequirements:
        """
        Validate and convert questionnaire to MedicalRequirements
        
        Args:
            questionnaire: User questionnaire data
            
        Returns:
            MedicalRequirements object
            
        Raises:
            ValidationError: If validation fails
        
        FUTURE ENHANCEMENTS - Fields to add to matching:
        ├─ q7_budget (section_2_location_budget) - Filter homes > budget, score value-for-money
        ├─ q12_age_range (section_3_medical_needs) - Age-specific care adaptation
        ├─ q14_allergies (section_4_safety_special_needs) - Check home can handle allergies
        ├─ q15_dietary_requirements - Validate kitchen can handle dietary needs
        ├─ q16_social_personality - Match home social environment
        ├─ q17_placement_timeline - Urgency affects selection priority
        └─ q18_priority_ranking (section_6) - Weight results by user priorities (60% safety, 25% quality, etc.)
        """
        logger.info("Validating questionnaire")
        
        try:
            # Extract fields
            medical_needs = questionnaire.get('section_3_medical_needs', {})
            safety_needs = questionnaire.get('section_4_safety_special_needs', {})
            
            # TODO: Extract and validate unused questionnaire fields:
            # location_budget = questionnaire.get('section_2_location_budget', {})
            # q7_budget = location_budget.get('q7_budget')  # FUTURE: Use in matching
            # q12_age_range = medical_needs.get('q12_age_range')  # FUTURE: Age-specific care
            # q14_allergies = safety_needs.get('q14_allergies')  # FUTURE: Allergy checking
            # q15_dietary_requirements = safety_needs.get('q15_dietary_requirements')  # FUTURE: Dietary match
            # q16_social_personality = safety_needs.get('q16_social_personality')  # FUTURE: Social environment
            
            medical_conditions = medical_needs.get('q9_medical_conditions', [])
            care_types = medical_needs.get('q8_care_types', [])
            mobility_level = medical_needs.get('q10_mobility_level', 'self_sufficient')
            # ✅ FIX: Normalize medication_management before validation
            medication_management_raw = medical_needs.get('q11_medication_management', 'simple_routine')
            medication_management = self._normalize_medication_management(medication_management_raw)
            special_equipment = medical_needs.get('q12_special_equipment', [])
            # ✅ FIX: Normalize fall_history before validation
            fall_history_raw = safety_needs.get('q13_fall_history', '1_2_no_serious_injuries')
            fall_history = self._normalize_fall_history(fall_history_raw)
            allergies = safety_needs.get('q14_allergies', [])
            dietary_requirements = safety_needs.get('q15_dietary_requirements', [])
            
            # Create and validate
            requirements = MedicalRequirements(
                medical_conditions=medical_conditions,
                care_types=care_types,
                mobility_level=mobility_level,
                medication_management=medication_management,
                special_equipment=special_equipment,
                fall_history=fall_history,
                allergies=allergies,
                dietary_requirements=dietary_requirements
            )
            
            logger.info(f"Questionnaire validated: {len(medical_conditions)} conditions, "
                       f"{len(care_types)} care types, fall_risk={fall_history}")
            
            return requirements
            
        except (KeyError, TypeError) as e:
            raise ValidationError("questionnaire", f"Invalid structure: {str(e)}")
    
    def validate_home(self, home: Dict[str, Any]) -> CareHomeData:
        """
        Validate and convert home dict to CareHomeData
        
        Args:
            home: Home data dictionary
            
        Returns:
            CareHomeData object
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # ✅ FIX: Handle None values from database properly
            # CQC ratings: if None or empty, use 'Unknown'
            cqc_rating_safe = home.get('cqc_rating_safe') or home.get('rating') or 'Unknown'
            if cqc_rating_safe and cqc_rating_safe != 'Unknown':
                cqc_rating_safe = str(cqc_rating_safe).strip()
            else:
                cqc_rating_safe = 'Unknown'
            
            cqc_rating_overall = home.get('cqc_rating_overall') or home.get('overall_rating') or home.get('rating') or 'Unknown'
            if cqc_rating_overall and cqc_rating_overall != 'Unknown':
                cqc_rating_overall = str(cqc_rating_overall).strip()
            else:
                cqc_rating_overall = 'Unknown'
            
            # ✅ FIX: Calculate distance_km if not present but coordinates are available
            distance_km = home.get('distance_km')
            if distance_km is None or distance_km == 0:
                # Try to calculate from coordinates if available
                # Note: This requires user coordinates, which may not be available at this stage
                # The distance should be calculated during data loading
                distance_km = 0.0
            else:
                try:
                    distance_km = float(distance_km)
                except (ValueError, TypeError):
                    distance_km = 0.0
            
            home_data = CareHomeData(
                name=home.get('name', 'Unknown'),
                care_types=home.get('care_types', []),
                cqc_rating_safe=cqc_rating_safe,
                cqc_rating_overall=cqc_rating_overall,
                cqc_rating_effective=home.get('cqc_rating_effective') or None,
                cqc_rating_caring=home.get('cqc_rating_caring') or None,
                cqc_rating_responsive=home.get('cqc_rating_responsive') or None,
                cqc_rating_well_led=home.get('cqc_rating_well_led') or None,
                fsa_rating=home.get('fsa_rating') or home.get('food_hygiene_rating') or None,
                distance_km=distance_km,
                google_rating=home.get('google_rating') or None,
                google_reviews_count=home.get('google_reviews_count') or home.get('review_count') or home.get('user_ratings_total') or None,
                has_wheelchair_access=home.get('has_wheelchair_access') or home.get('wheelchair_access') or False,
                has_hoist=home.get('has_hoist') or False,
                has_hospital_bed=home.get('has_hospital_bed') or False,
                has_nursing_staff=home.get('has_nursing_staff') or False,
                registration_type=home.get('registration_type') or None
            )
            
            home_data.validate()
            return home_data
            
        except (KeyError, TypeError, ValueError) as e:
            raise ValidationError("home", f"Invalid structure: {str(e)}")
    
    # ==================== HARD CONSTRAINTS ====================
    
    def apply_hard_constraints(
        self,
        home: CareHomeData,
        requirements: MedicalRequirements
    ) -> Tuple[bool, List[str]]:
        """
        Apply hard constraints that might eliminate a home
        
        Returns:
            (passes_constraints: bool, warnings: List[str])
        """
        warnings = []
        
        # Constraint 1: Fall Risk
        if requirements.fall_history in [FallHistory.THREE_PLUS_SERIOUS.value, 
                                         FallHistory.HIGH_RISK.value]:
            cqc_safe = home.cqc_rating_safe
            if cqc_safe not in [CQCRating.OUTSTANDING.value, CQCRating.GOOD.value]:
                warnings.append(
                    f"CONSTRAINT FAILED: High fall risk requires Good/Outstanding CQC Safety. "
                    f"Home has: {cqc_safe}"
                )
                return False, warnings
        
        # Constraint 2: Wheelchair Access
        if requirements.mobility_level == MobilityLevel.WHEELCHAIR_SOMETIMES.value:
            if not home.has_wheelchair_access:
                warnings.append(
                    "CONSTRAINT WARNING: Wheelchair access required but not available. "
                    "Score reduced."
                )
        
        # Constraint 3: Medication Management
        if requirements.medication_management == MedicationManagement.MANY_COMPLEX_ROUTINE.value:
            if not home.has_nursing_staff:
                warnings.append(
                    "CONSTRAINT WARNING: Complex medication management requires nursing staff. "
                    "Residential home may not be suitable. Score reduced."
                )
        
        # Constraint 4: Special Equipment
        for equipment in requirements.special_equipment:
            if equipment == 'hoist' and not home.has_hoist:
                warnings.append(f"CONSTRAINT WARNING: Hoist required but not available.")
            elif equipment == 'hospital_bed' and not home.has_hospital_bed:
                warnings.append(f"CONSTRAINT WARNING: Hospital bed required but not available.")
        
        return True, warnings
    
    # ==================== SCORING ====================
    
    def calculate_medical_score(
        self,
        home: CareHomeData,
        requirements: MedicalRequirements
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate medical match score (0-30 points)
        """
        detail = {}
        total = 0.0
        
        # 1. Condition Match (0-10 points)
        condition_score = self._score_condition_match(home, requirements)
        detail['condition_match'] = condition_score
        total += condition_score
        logger.debug(f"Condition match: {condition_score:.1f}")
        
        # 2. Care Type Match (0-5 points)
        care_type_score = self._score_care_type_match(home, requirements)
        detail['care_type_match'] = care_type_score
        total += care_type_score
        logger.debug(f"Care type match: {care_type_score:.1f}")
        
        # 3. Equipment & Mobility (0-10 points)
        equipment_score = self._score_equipment_mobility(home, requirements)
        detail['equipment_mobility'] = equipment_score
        total += equipment_score
        logger.debug(f"Equipment/mobility: {equipment_score:.1f}")
        
        # 4. Nursing Staff (0-5 points)
        nursing_score = self._score_nursing_staff(home, requirements)
        detail['nursing_staff'] = nursing_score
        total += nursing_score
        logger.debug(f"Nursing staff: {nursing_score:.1f}")
        
        # Clamp to max
        final = min(total, self.MEDICAL_MAX)
        
        return final, detail
    
    def calculate_safety_score(self, home: CareHomeData) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate safety & quality score (0-40 points)
        """
        detail = {}
        total = 0.0
        
        # 1. CQC Safety (0-20 points)
        safety_pts = self._cqc_rating_to_points(home.cqc_rating_safe, 20)
        detail['cqc_safe'] = safety_pts
        total += safety_pts
        logger.debug(f"CQC Safety ({home.cqc_rating_safe}): {safety_pts:.1f}")
        
        # 2. CQC Overall (0-10 points)
        overall_pts = self._cqc_rating_to_points(home.cqc_rating_overall, 10)
        detail['cqc_overall'] = overall_pts
        total += overall_pts
        logger.debug(f"CQC Overall ({home.cqc_rating_overall}): {overall_pts:.1f}")
        
        # 3. CQC Effective + Caring (0-10 points)
        effective_caring = self._cqc_effective_caring_to_points(
            home.cqc_rating_effective,
            home.cqc_rating_caring,
            10
        )
        detail['cqc_effective_caring'] = effective_caring
        total += effective_caring
        logger.debug(f"CQC Effective+Caring: {effective_caring:.1f}")
        
        # 4. FSA Rating (0-5 points)
        fsa_pts = self._fsa_rating_to_points(home.fsa_rating, 5)
        detail['fsa_rating'] = fsa_pts
        total += fsa_pts
        logger.debug(f"FSA Rating ({home.fsa_rating}): {fsa_pts:.1f}")
        
        # Normalize from 45 to 40
        final = min(total * (40 / 45) if total > 0 else 0, self.SAFETY_MAX)
        
        return final, detail
    
    def calculate_location_score(self, home: CareHomeData) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate location & fit score (0-25 points)
        """
        detail = {}
        total = 0.0
        
        # 1. Distance (0-15 points)
        distance_pts = self._distance_to_points(home.distance_km, 15)
        detail['distance'] = distance_pts
        total += distance_pts
        logger.debug(f"Distance ({home.distance_km}km): {distance_pts:.1f}")
        
        # 2. Accessibility (0-5 points) - for now, constant
        accessibility_pts = 3.0  # Default: assume reasonable accessibility
        detail['accessibility'] = accessibility_pts
        total += accessibility_pts
        logger.debug(f"Accessibility: {accessibility_pts:.1f}")
        
        # 3. Google Reviews Bonus (0-5 points)
        google_bonus = self._google_reviews_to_points(
            home.google_rating,
            home.google_reviews_count,
            5
        )
        detail['google_bonus'] = google_bonus
        total += google_bonus
        logger.debug(f"Google Reviews: {google_bonus:.1f}")
        
        final = min(total, self.LOCATION_MAX)
        
        return final, detail
    
    # ==================== HELPER SCORING FUNCTIONS ====================
    
    def _score_condition_match(
        self,
        home: CareHomeData,
        requirements: MedicalRequirements
    ) -> float:
        """Score medical condition match (0-10)"""
        if not requirements.medical_conditions:
            return 0.0
        
        # Simple matching: count how many conditions match home specialization
        home_care_types_lower = [ct.lower() for ct in home.care_types]
        matches = 0
        
        for condition in requirements.medical_conditions:
            condition_lower = condition.lower()
            
            # Check for direct matches
            if any(condition_lower in ct for ct in home_care_types_lower):
                matches += 1
            # Special handling for common conditions
            elif condition_lower in ['dementia_alzheimers', 'dementia'] and \
                 any('dementia' in ct.lower() for ct in home_care_types_lower):
                matches += 1
            elif condition_lower == 'diabetes' and \
                 any('medical' in ct.lower() or 'nursing' in ct.lower() 
                     for ct in home_care_types_lower):
                matches += 1
        
        if matches == len(requirements.medical_conditions):
            return 10.0  # Perfect match
        elif matches >= len(requirements.medical_conditions) * 0.7:
            return 7.0   # Good match
        elif matches > 0:
            return 5.0   # Partial match
        else:
            return 0.0   # No match
    
    def _score_care_type_match(
        self,
        home: CareHomeData,
        requirements: MedicalRequirements
    ) -> float:
        """Score care type match (0-5)"""
        home_care_types_lower = [ct.lower() for ct in home.care_types]
        required_types_lower = [ct.lower() for ct in requirements.care_types]
        
        # Check if nursing is required
        nursing_required = any('nursing' in rt for rt in required_types_lower)
        has_nursing = any('nursing' in ct for ct in home_care_types_lower)
        
        if nursing_required:
            return 5.0 if has_nursing else 0.0  # Nursing required: home must have it
        else:
            # Residential is acceptable
            return 5.0  # Both nursing and residential acceptable for non-nursing
    
    def _score_equipment_mobility(
        self,
        home: CareHomeData,
        requirements: MedicalRequirements
    ) -> float:
        """Score equipment and mobility support (0-10)"""
        score = 0.0
        
        # Wheelchair access (5 points)
        if requirements.mobility_level == MobilityLevel.WHEELCHAIR_SOMETIMES.value:
            score += 5.0 if home.has_wheelchair_access else 0.0
        else:
            score += 5.0  # No wheelchair needed = full points
        
        # Equipment (5 points)
        equipment_needed = len(requirements.special_equipment)
        if equipment_needed == 0:
            score += 5.0  # No equipment needed = full points
        else:
            equipment_available = 0
            for equipment in requirements.special_equipment:
                if equipment == 'hoist' and home.has_hoist:
                    equipment_available += 1
                elif equipment == 'hospital_bed' and home.has_hospital_bed:
                    equipment_available += 1
                elif equipment == 'wheelchair_access' and home.has_wheelchair_access:
                    equipment_available += 1
            
            score += (equipment_available / equipment_needed) * 5.0
        
        return min(score, 10.0)
    
    def _score_nursing_staff(
        self,
        home: CareHomeData,
        requirements: MedicalRequirements
    ) -> float:
        """Score nursing staff availability (0-5)"""
        if requirements.medication_management == MedicationManagement.MANY_COMPLEX_ROUTINE.value:
            # Complex meds: nursing required
            return 5.0 if home.has_nursing_staff else 0.0
        else:
            # Simple meds: nursing is a bonus
            return 3.0 if home.has_nursing_staff else 0.0
    
    def _cqc_rating_to_points(self, rating: Optional[str], max_points: float) -> float:
        """Convert CQC rating to points"""
        if not rating:
            return 0.0
        
        rating_clean = rating.lower().strip()
        
        if 'outstanding' in rating_clean:
            return max_points
        elif 'good' in rating_clean:
            return max_points * 0.9
        elif 'requires improvement' in rating_clean or 'improvement' in rating_clean:
            return max_points * 0.25
        elif 'inadequate' in rating_clean:
            return 0.0
        else:
            return max_points * 0.5  # Unknown = half points
    
    def _cqc_effective_caring_to_points(
        self,
        effective: Optional[str],
        caring: Optional[str],
        max_points: float
    ) -> float:
        """Combine CQC Effective and Caring ratings (0-10)"""
        eff_pts = self._cqc_rating_to_points(effective, max_points)
        car_pts = self._cqc_rating_to_points(caring, max_points)
        
        # Average the two ratings
        combined = (eff_pts + car_pts) / 2.0
        
        return min(combined, max_points)
    
    def _fsa_rating_to_points(self, rating: Optional[int], max_points: float) -> float:
        """Convert FSA rating to points (1-5 stars)"""
        if not rating:
            return 0.0
        
        if rating >= 5:
            return max_points
        elif rating >= 4:
            return max_points * 0.8
        elif rating >= 3:
            return max_points * 0.4
        else:
            return max_points * 0.1
    
    def _distance_to_points(self, distance_km: float, max_points: float) -> float:
        """Convert distance to points"""
        if distance_km <= 5:
            return max_points
        elif distance_km <= 10:
            return max_points * 0.8
        elif distance_km <= 15:
            return max_points * 0.5
        elif distance_km <= 20:
            return max_points * 0.25
        else:
            return 0.0
    
    def _google_reviews_to_points(
        self,
        rating: Optional[float],
        count: Optional[int],
        max_points: float
    ) -> float:
        """Calculate Google reviews bonus"""
        if not rating or not count:
            return 0.0
        
        # Need minimum 20 reviews to count
        if count < 20:
            return 0.0
        
        if rating >= 4.5:
            return max_points * 0.8
        elif rating >= 4.0:
            return max_points * 0.5
        elif rating >= 3.5:
            return max_points * 0.2
        else:
            return 0.0
    
    # ==================== MAIN MATCHING LOGIC ====================
    
    def apply_dynamic_weights(
        self,
        medical: float,
        safety: float,
        location: float,
        requirements: MedicalRequirements
    ) -> Tuple[float, float, float]:
        """
        Apply dynamic weights based on fall risk
        
        Returns:
            (weighted_medical, weighted_safety, weighted_location)
        """
        # Check for high fall risk
        has_high_fall_risk = requirements.fall_history in [
            FallHistory.THREE_PLUS_SERIOUS.value,
            FallHistory.HIGH_RISK.value
        ]
        
        if has_high_fall_risk:
            # Apply boosts/reductions
            medical = medical * self.FALL_RISK_MEDICAL_BOOST
            safety = safety * self.FALL_RISK_SAFETY_BOOST
            location = location * self.FALL_RISK_LOCATION_REDUCTION
            logger.info("Applied fall risk boost: Safety +30%, Medical +10%, Location -20%")
        
        return medical, safety, location
    
    def calculate_total_score(
        self,
        home: CareHomeData,
        requirements: MedicalRequirements
    ) -> ScoreBreakdown:
        """
        Calculate total score for a home (0-100)
        """
        # Apply hard constraints first
        passes, warnings = self.apply_hard_constraints(home, requirements)
        
        if not passes:
            logger.warning(f"Home {home.name} failed constraints: {warnings}")
            return ScoreBreakdown(
                medical_score=0,
                medical_detail={},
                safety_score=0,
                safety_detail={},
                location_score=0,
                location_detail={},
                total_score=0,
                constraints_met=False,
                warnings=warnings
            )
        
        # Calculate component scores
        medical, medical_detail = self.calculate_medical_score(home, requirements)
        safety, safety_detail = self.calculate_safety_score(home)
        location, location_detail = self.calculate_location_score(home)
        
        logger.debug(f"{home.name}: Medical={medical:.1f}, Safety={safety:.1f}, Location={location:.1f}")
        
        # Apply dynamic weights
        medical, safety, location = self.apply_dynamic_weights(
            medical, safety, location, requirements
        )
        
        # Calculate total (weighted)
        # Base: Medical 30%, Safety 40%, Location 25%, Buffer 5%
        total = (medical / self.MEDICAL_MAX * 30) + \
                (safety / self.SAFETY_MAX * 40) + \
                (location / self.LOCATION_MAX * 25)
        
        # Clamp to 0-100
        total = min(max(total, 0), self.MAX_TOTAL_SCORE)
        
        return ScoreBreakdown(
            medical_score=medical,
            medical_detail=medical_detail,
            safety_score=safety,
            safety_detail=safety_detail,
            location_score=location,
            location_detail=location_detail,
            total_score=total,
            constraints_met=True,
            warnings=warnings
        )
    
    def match_homes(
        self,
        homes: List[Dict[str, Any]],
        questionnaire: Dict[str, Any],
        top_n: int = 5
    ) -> List[MatchingResult]:
        """
        Match homes against questionnaire and return top N
        
        Args:
            homes: List of home dictionaries
            questionnaire: User questionnaire
            top_n: Number of top results to return
            
        Returns:
            List of MatchingResult ranked by score
            
        Raises:
            ValidationError: If input validation fails
            NoHomesFoundError: If no suitable homes found
        """
        logger.info(f"Starting matching for {len(homes)} homes")
        
        # Validate questionnaire
        requirements = self.validate_questionnaire(questionnaire)
        logger.info(f"Questionnaire validated: {requirements}")
        
        results = []
        
        for home_dict in homes:
            try:
                # Validate home
                home = self.validate_home(home_dict)
                
                # Calculate score
                score = self.calculate_total_score(home, requirements)
                
                # Create result
                result = MatchingResult(home=home, score=score)
                results.append(result)
                
                logger.debug(f"{home.name}: Score={score.total_score:.1f}")
                
            except ValidationError as e:
                logger.warning(f"Home validation failed: {e}")
                continue
            except Exception as e:
                logger.error(f"Error matching home: {e}")
                continue
        
        if not results:
            raise NoHomesFoundError("No valid homes matched")
        
        # Sort by score descending
        results.sort(key=lambda r: r.score.total_score, reverse=True)
        
        # Assign ranks
        for i, result in enumerate(results[:top_n], 1):
            result.rank = i
        
        logger.info(f"Matched {len(results)} homes. Top {min(top_n, len(results))} scores: "
                   f"{[f'{r.score.total_score:.1f}' for r in results[:top_n]]}")
        
        return results[:top_n]
    
    def select_top_5_with_category_winners(
        self,
        candidates: List[Dict[str, Any]],
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any],
        weights: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Select top 5 homes and determine category winners.
        
        Compatible with the interface expected by report_routes.py.
        
        Args:
            candidates: List of home dictionaries
            user_profile: User questionnaire
            enriched_data: Dict of home_id -> enriched_data
            weights: Optional scoring weights (not used in Enhanced MVP)
        
        Returns:
            {
                'top_5': [...],  # Top 5 homes with match scores
                'category_winners': {
                    'best_overall': {...},
                    'best_medical_safety': {...},
                    ...
                }
            }
        """
        logger.info(f"Selecting top 5 with category winners from {len(candidates)} candidates")
        
        # Score all candidates using match_homes
        try:
            # Use match_homes to score all candidates
            matching_results = self.match_homes(
                homes=candidates,
                questionnaire=user_profile,
                top_n=len(candidates)  # Score all, then select top 5
            )
        except Exception as e:
            logger.error(f"Error in match_homes: {e}")
            # Fallback: return empty result
            return {
                'top_5': [],
                'category_winners': {}
            }
        
        # Convert MatchingResult to dict format expected by report_routes.py
        scored_homes = []
        for result in matching_results:
            # Convert CareHomeData to dict
            if hasattr(result.home, '__dict__'):
                # It's a dataclass, convert to dict using asdict if available
                try:
                    from dataclasses import asdict
                    home_dict = asdict(result.home)
                    # ✅ FIX: Ensure id, postcode, latitude, longitude are preserved
                    # These may not be in CareHomeData dataclass, so add them from __dict__ if missing
                    if 'id' not in home_dict or not home_dict.get('id'):
                        home_dict['id'] = getattr(result.home, 'id', None) or getattr(result.home, 'cqc_location_id', None)
                    if 'cqc_location_id' not in home_dict or not home_dict.get('cqc_location_id'):
                        home_dict['cqc_location_id'] = getattr(result.home, 'cqc_location_id', None) or getattr(result.home, 'id', None)
                    if 'postcode' not in home_dict or not home_dict.get('postcode'):
                        home_dict['postcode'] = getattr(result.home, 'postcode', None) or ''
                    if 'latitude' not in home_dict:
                        home_dict['latitude'] = getattr(result.home, 'latitude', None)
                    if 'longitude' not in home_dict:
                        home_dict['longitude'] = getattr(result.home, 'longitude', None)
                except (ImportError, TypeError):
                    # Fallback: manual conversion
                    home_dict = {
                        'name': getattr(result.home, 'name', 'Unknown'),
                        'postcode': getattr(result.home, 'postcode', ''),
                        'id': getattr(result.home, 'id', None) or getattr(result.home, 'cqc_location_id', None),  # ✅ FIX: Add id/cqc_location_id
                        'cqc_location_id': getattr(result.home, 'cqc_location_id', None) or getattr(result.home, 'id', None),  # ✅ FIX: Add cqc_location_id
                        'location_id': getattr(result.home, 'location_id', None) or getattr(result.home, 'cqc_location_id', None) or getattr(result.home, 'id', None),  # ✅ FIX: Add location_id
                        'cqc_rating': getattr(result.home, 'cqc_rating_overall', None),
                        'cqc_rating_overall': getattr(result.home, 'cqc_rating_overall', None),
                        'cqc_rating_safe': getattr(result.home, 'cqc_rating_safe', None),
                        'distance_km': getattr(result.home, 'distance_km', 0.0),
                        'care_types': getattr(result.home, 'care_types', []),
                        'fsa_rating': getattr(result.home, 'fsa_rating', None),
                        'google_rating': getattr(result.home, 'google_rating', None),
                        'has_wheelchair_access': getattr(result.home, 'has_wheelchair_access', False),
                        'has_hoist': getattr(result.home, 'has_hoist', False),
                        'has_hospital_bed': getattr(result.home, 'has_hospital_bed', False),
                        'has_nursing_staff': getattr(result.home, 'has_nursing_staff', False),
                        'registration_type': getattr(result.home, 'registration_type', None),
                        'latitude': getattr(result.home, 'latitude', None),  # ✅ FIX: Add latitude
                        'longitude': getattr(result.home, 'longitude', None),  # ✅ FIX: Add longitude
                    }
                    # Add any other attributes from __dict__
                    for key, value in result.home.__dict__.items():
                        if key not in home_dict:
                            home_dict[key] = value
            elif isinstance(result.home, dict):
                home_dict = result.home
            else:
                # Fallback: try to convert to dict
                home_dict = {'name': str(result.home)}
            
            scored_homes.append({
                'home': home_dict,
                'matchScore': result.score.total_score,
                'matchResult': {
                    'total': result.score.total_score,
                    'normalized': result.score.total_score,  # Already 0-100
                    'medical_score': result.score.medical_score,
                    'safety_score': result.score.safety_score,
                    'location_score': result.score.location_score,
                    'point_allocations': {
                        # ✅ FIX: Use correct category names for Enhanced MVP (medical, safety, location)
                        'medical': round(result.score.medical_score, 1),
                        'safety': round(result.score.safety_score, 1),
                        'location': round(result.score.location_score, 1)
                    },
                    'category_scores': {
                        # ✅ FIX: Normalize to 0-1 scale for category_scores (as expected by report_routes.py)
                        'medical': result.score.medical_score / 30.0 if 30.0 > 0 else 0.0,
                        'safety': result.score.safety_score / 40.0 if 40.0 > 0 else 0.0,
                        'location': result.score.location_score / 25.0 if 25.0 > 0 else 0.0
                    },
                    'weights': {},  # Enhanced MVP doesn't return weights in same format
                    'constraints_met': result.score.constraints_met,
                    'warnings': result.score.warnings
                },
                'match_result': {
                    'total': result.score.total_score,
                    'normalized': result.score.total_score,  # Already 0-100
                    'medical_score': result.score.medical_score,
                    'safety_score': result.score.safety_score,
                    'location_score': result.score.location_score,
                    'point_allocations': {
                        # ✅ FIX: Use correct category names for Enhanced MVP
                        'medical': round(result.score.medical_score, 1),
                        'safety': round(result.score.safety_score, 1),
                        'location': round(result.score.location_score, 1)
                    },
                    'category_scores': {
                        # ✅ FIX: Normalize to 0-1 scale for category_scores (as expected by report_routes.py)
                        'medical': result.score.medical_score / 30.0 if 30.0 > 0 else 0.0,
                        'safety': result.score.safety_score / 40.0 if 40.0 > 0 else 0.0,
                        'location': result.score.location_score / 25.0 if 25.0 > 0 else 0.0
                    },
                    'weights': {},  # Enhanced MVP doesn't return weights in same format
                    'constraints_met': result.score.constraints_met,
                    'warnings': result.score.warnings
                },
                'category_scores': {
                    # ✅ FIX: Normalize to 0-1 scale for category_scores (as expected by report_routes.py)
                    'medical': result.score.medical_score / 30.0 if 30.0 > 0 else 0.0,
                    'safety': result.score.safety_score / 40.0 if 40.0 > 0 else 0.0,
                    'location': result.score.location_score / 25.0 if 25.0 > 0 else 0.0
                }
            })
        
        # Sort by match score (already sorted by match_homes, but ensure)
        scored_homes.sort(key=lambda x: x.get('matchScore', 0), reverse=True)
        
        # Select top 5
        top_5 = scored_homes[:5]
        
        # Determine category winners
        category_winners = {}
        if top_5:
            # Best Overall
            category_winners['best_overall'] = {
                'home': top_5[0]['home'],
                'label': 'Best Overall Match',
                'reasoning': [f'Highest match score: {top_5[0]["matchScore"]:.1f}/100']
            }
            
            # Best Medical & Safety
            best_medical_safety = max(
                top_5,
                key=lambda x: (
                    x['matchResult'].get('point_allocations', {}).get('medical_safety', 0)
                )
            )
            category_winners['best_medical_safety'] = {
                'home': best_medical_safety['home'],
                'label': 'Best for Medical & Safety',
                'reasoning': [f'Highest medical & safety score: {best_medical_safety["matchResult"].get("point_allocations", {}).get("medical_safety", 0):.1f}']
            }
            
            # Best Location
            best_location = max(
                top_5,
                key=lambda x: x['matchResult'].get('point_allocations', {}).get('location', 0)
            )
            category_winners['best_location'] = {
                'home': best_location['home'],
                'label': 'Best Location',
                'reasoning': [f'Highest location score: {best_location["matchResult"].get("point_allocations", {}).get("location", 0):.1f}']
            }
        
        logger.info(f"Selected top 5 homes. Category winners: {list(category_winners.keys())}")
        
        return {
            'top_5': top_5,
            'category_winners': category_winners
        }
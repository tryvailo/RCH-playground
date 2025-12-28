"""
Constraint Relaxation Manager for Enhanced MVP Matching Service
Implements progressive constraint relaxation when insufficient results found
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ConstraintLevel(Enum):
    """Constraint relaxation levels"""
    STRICT = 0      # All constraints applied (Tier 1 + Tier 2)
    RELAXED = 1     # Only Tier 1 constraints (critical)
    CRITICAL = 2    # Only essential Tier 1 (care type + safety)
    MINIMAL = 3     # Absolute minimum (care type only)


@dataclass
class ConstraintConfig:
    """Configuration for constraint application"""
    level: ConstraintLevel
    apply_care_type: bool = True
    apply_cqc_safety: bool = True
    apply_wheelchair: bool = True
    apply_medication: bool = True
    apply_equipment: bool = True
    apply_nursing: bool = True
    apply_reviews: bool = True
    reason: str = ""


class ConstraintRelaxationManager:
    """
    Manages progressive constraint relaxation for home matching.
    
    When initial search with all constraints returns insufficient results,
    systematically relaxes non-critical constraints while maintaining safety.
    """
    
    # Constraint relaxation phases
    RELAXATION_PHASES = [
        ConstraintConfig(
            level=ConstraintLevel.STRICT,
            apply_care_type=True,
            apply_cqc_safety=True,
            apply_wheelchair=True,
            apply_medication=True,
            apply_equipment=True,
            apply_nursing=True,
            apply_reviews=True,
            reason="All constraints applied (strict matching)"
        ),
        ConstraintConfig(
            level=ConstraintLevel.RELAXED,
            apply_care_type=True,
            apply_cqc_safety=True,
            apply_wheelchair=True,
            apply_medication=False,  # Relax
            apply_equipment=False,   # Relax
            apply_nursing=False,     # Relax
            apply_reviews=False,     # Relax
            reason="Relaxed: Medication, equipment, and nursing preferences"
        ),
        ConstraintConfig(
            level=ConstraintLevel.CRITICAL,
            apply_care_type=True,
            apply_cqc_safety=True,
            apply_wheelchair=True,
            apply_medication=False,
            apply_equipment=False,
            apply_nursing=False,
            apply_reviews=False,
            reason="Critical: Only care type and safety enforced"
        ),
        ConstraintConfig(
            level=ConstraintLevel.MINIMAL,
            apply_care_type=True,
            apply_cqc_safety=False,  # Relax safety for non-fall-risk
            apply_wheelchair=False,   # Relax wheelchair
            apply_medication=False,
            apply_equipment=False,
            apply_nursing=False,
            apply_reviews=False,
            reason="Minimal: Only care type matching"
        ),
    ]
    
    def __init__(self):
        """Initialize constraint relaxation manager"""
        logger.info("Initializing ConstraintRelaxationManager")
    
    def relax_constraints_progressively(
        self,
        homes: List[Dict[str, Any]],
        matching_service,
        questionnaire: Dict[str, Any],
        top_n: int = 5,
        min_results_threshold: int = 3
    ) -> Tuple[List[Any], ConstraintConfig, str]:
        """
        Progressively relax constraints until sufficient results found.
        
        Args:
            homes: All available homes
            matching_service: Service with match_homes() method
            questionnaire: User questionnaire data
            top_n: Number of results to return
            min_results_threshold: Minimum results needed before relaxing
        
        Returns:
            (matched_homes, constraint_config_used, status_message)
        """
        
        logger.info("Starting progressive constraint relaxation")
        
        # Try each constraint level
        for constraint_config in self.RELAXATION_PHASES:
            logger.info(f"Constraint Level {constraint_config.level.name}: {constraint_config.reason}")
            
            try:
                # Apply constraints through filtering
                filtered_homes = self._apply_constraints(
                    homes=homes,
                    questionnaire=questionnaire,
                    config=constraint_config
                )
                
                logger.debug(f"Homes after constraint filtering: {len(filtered_homes)}")
                
                if not filtered_homes:
                    logger.debug(f"No homes pass {constraint_config.level.name} constraints, continuing...")
                    continue
                
                # Match filtered homes
                matching_results = matching_service.match_homes(
                    homes=filtered_homes,
                    questionnaire=questionnaire,
                    top_n=min(top_n, len(filtered_homes))
                )
                
                num_results = len(matching_results)
                logger.info(f"Got {num_results} results at {constraint_config.level.name} level")
                
                # Check if we have enough results
                if num_results >= min_results_threshold or constraint_config.level == ConstraintLevel.MINIMAL:
                    message = self._create_relaxation_message(
                        constraint_config=constraint_config,
                        num_results=num_results,
                        total_homes_evaluated=len(homes)
                    )
                    return matching_results, constraint_config, message
                
            except Exception as e:
                logger.warning(f"Error at {constraint_config.level.name} level: {e}")
                continue
        
        # Fallback: return all matches from minimal constraints
        logger.warning("No sufficient results even with minimal constraints")
        try:
            minimal_homes = self._apply_constraints(
                homes=homes,
                questionnaire=questionnaire,
                config=self.RELAXATION_PHASES[-1]
            )
            
            matching_results = matching_service.match_homes(
                homes=minimal_homes,
                questionnaire=questionnaire,
                top_n=top_n
            )
            
            message = f"Critical: Very limited options available. Showing all {len(matching_results)} homes found."
            return matching_results, self.RELAXATION_PHASES[-1], message
            
        except Exception as e:
            logger.error(f"Fallback constraint relaxation failed: {e}")
            return [], self.RELAXATION_PHASES[-1], f"Error: {str(e)}"
    
    def _apply_constraints(
        self,
        homes: List[Dict[str, Any]],
        questionnaire: Dict[str, Any],
        config: ConstraintConfig
    ) -> List[Dict[str, Any]]:
        """
        Apply constraints to filter homes.
        
        Args:
            homes: All homes to filter
            questionnaire: User requirements
            config: Constraint configuration
        
        Returns:
            Filtered list of homes
        
        FUTURE ENHANCEMENTS - Database fields available but not yet used:
        ├─ CQC Ratings (4 of 6 available, 2 unused):
        │  ├─ cqc_rating_responsive - "Responsive to people's needs"
        │  │  └─ FUTURE: Use for quality-of-life score
        │  └─ cqc_rating_well_led - "Well-led organization"
        │     └─ FUTURE: Use for stability/governance score
        │
        ├─ Facilities (not yet used in matching):
        │  ├─ ensuite_rooms - Privacy/dignity factor
        │  │  └─ FUTURE: Requirement for dementia patients
        │  ├─ secure_garden - Critical for dementia safety
        │  │  └─ FUTURE: Bonus for dementia care
        │  ├─ wifi_available - Quality of life
        │  │  └─ FUTURE: Bonus scoring, resident connection
        │  └─ parking_onsite - Visitor convenience
        │     └─ FUTURE: Bonus for families
        │
        ├─ Availability (not used):
        │  ├─ beds_available - Current availability
        │  │  └─ FUTURE: Filter only available homes
        │  └─ has_availability - Known availability
        │     └─ FUTURE: Penalty/filter if no beds
        │
        └─ Equipment (CODE REFERENCES BUT NOT IN DB - CRITICAL):
           ├─ has_nursing_staff ⚠️ Referenced but MISSING FROM DB!
           │  └─ SOLUTION: Infer from care_nursing=true
           ├─ has_hoist ⚠️ Referenced but MISSING FROM DB!
           │  └─ SOLUTION: Add to DB schema from provider data
           └─ has_hospital_bed ⚠️ Referenced but MISSING FROM DB!
              └─ SOLUTION: Add to DB schema from provider data
        """
        filtered = homes
        
        # Care type constraint (ALWAYS applied)
        if config.apply_care_type:
            filtered = self._filter_by_care_type(filtered, questionnaire)
            logger.debug(f"After care type filter: {len(filtered)} homes")
        
        # CQC Safety constraint (critical for high-risk patients)
        if config.apply_cqc_safety:
            filtered = self._filter_by_cqc_safety(filtered, questionnaire)
            logger.debug(f"After CQC safety filter: {len(filtered)} homes")
        
        # Wheelchair access constraint
        if config.apply_wheelchair:
            filtered = self._filter_by_wheelchair(filtered, questionnaire)
            logger.debug(f"After wheelchair filter: {len(filtered)} homes")
        
        # Medication support constraint
        if config.apply_medication:
            filtered = self._filter_by_medication_support(filtered, questionnaire)
            logger.debug(f"After medication filter: {len(filtered)} homes")
        
        # Equipment constraint
        if config.apply_equipment:
            filtered = self._filter_by_equipment(filtered, questionnaire)
            logger.debug(f"After equipment filter: {len(filtered)} homes")
        
        # Nursing staff constraint
        if config.apply_nursing:
            filtered = self._filter_by_nursing_staff(filtered, questionnaire)
            logger.debug(f"After nursing filter: {len(filtered)} homes")
        
        return filtered
    
    def _filter_by_care_type(self, homes: List[Dict], questionnaire: Dict) -> List[Dict]:
        """Filter homes by required care type"""
        medical_needs = questionnaire.get('section_3_medical_needs', {})
        required_care_types = medical_needs.get('q8_care_types', [])
        
        if not required_care_types:
            return homes
        
        # Normalize care types
        required = set(str(ct).lower().replace('_', ' ').strip() for ct in required_care_types)
        
        filtered = []
        for home in homes:
            home_types = home.get('care_types', [])
            home_types_normalized = set(str(ct).lower().replace('_', ' ').strip() for ct in home_types)
            
            # Check if any required type matches home types
            if any(rt in home_types_normalized or 
                   any(rt.replace('specialised', 'specialized').startswith(prefix) 
                       for prefix in home_types_normalized)
                   for rt in required):
                filtered.append(home)
        
        logger.debug(f"Care type filter: {len(filtered)}/{len(homes)} homes match {required}")
        return filtered
    
    def _filter_by_cqc_safety(self, homes: List[Dict], questionnaire: Dict) -> List[Dict]:
        """
        Filter by CQC Safety rating - ENFORCED FOR ALL PATIENTS.
        
        Minimum standard: All patients deserve safe care environments.
        - Non-high-risk: Accept Good+, Adequate (lower safety threshold)
        - High-risk: MUST be Good+ (Outstanding, Good)
        - Never accept: Requires Improvement, Inadequate
        
        Returns:
            Filtered homes meeting minimum safety requirements
        """
        safety_needs = questionnaire.get('section_4_safety_special_needs', {})
        fall_history = safety_needs.get('q13_fall_history', '1_2_no_serious_injuries')
        
        # Determine risk level
        is_high_risk = fall_history in ['3_plus_or_serious_injuries', 'high_risk_of_falling']
        
        filtered = []
        for home in homes:
            cqc_safe = home.get('cqc_rating_safe', '').lower()
            
            if is_high_risk:
                # High-risk patients: MUST have Good+ safety
                # Accept: Outstanding, Good
                if any(rating in cqc_safe for rating in ['outstanding', 'good']):
                    filtered.append(home)
            else:
                # Non-high-risk patients: Accept Good+, Adequate
                # Reject: Requires Improvement, Inadequate
                if any(rating in cqc_safe for rating in ['outstanding', 'good', 'adequate']):
                    filtered.append(home)
                # If CQC rating missing, include but log warning
                elif not cqc_safe or cqc_safe == 'unknown':
                    logger.warning(f"Home {home.get('name')} has unknown CQC safety rating")
                    filtered.append(home)  # Include but with warning
        
        logger.debug(f"CQC Safety filter ({'high-risk' if is_high_risk else 'standard'}): {len(filtered)}/{len(homes)} homes")
        return filtered
    
    def _filter_by_wheelchair(self, homes: List[Dict], questionnaire: Dict) -> List[Dict]:
        """Filter by wheelchair accessibility"""
        medical_needs = questionnaire.get('section_3_medical_needs', {})
        mobility_level = medical_needs.get('q10_mobility_level', 'self_sufficient')
        special_equipment = medical_needs.get('q12_special_equipment', [])
        
        # Check if wheelchair needed
        needs_wheelchair = (
            mobility_level == 'wheelchair_sometimes' or
            'wheelchair' in str(special_equipment).lower()
        )
        
        if not needs_wheelchair:
            return homes  # No filter needed
        
        # Filter: wheelchair users need wheelchair access
        filtered = []
        for home in homes:
            # Check wheelchair access fields
            has_access = (
                home.get('wheelchair_accessible') or
                home.get('has_wheelchair_access') or
                home.get('wheelchair_access') or
                'wheelchair' in str(home.get('special_facilities', '')).lower()
            )
            
            if has_access:
                filtered.append(home)
        
        logger.debug(f"Wheelchair filter: {len(filtered)}/{len(homes)} homes accessible")
        return filtered
    
    def _filter_by_medication_support(self, homes: List[Dict], questionnaire: Dict) -> List[Dict]:
        """Filter by medication management support"""
        medical_needs = questionnaire.get('section_3_medical_needs', {})
        medication_level = medical_needs.get('q11_medication_management', 'simple_routine')
        
        # Only filter if complex medications
        if medication_level != 'many_complex_routine':
            return homes
        
        # Filter: complex meds need nursing/support
        filtered = []
        for home in homes:
            has_nursing = (
                home.get('has_nursing_staff') or
                home.get('nursing_staff') or
                'nursing' in str(home.get('care_types', '')).lower()
            )
            
            if has_nursing:
                filtered.append(home)
        
        logger.debug(f"Medication filter: {len(filtered)}/{len(homes)} homes have nursing")
        return filtered
    
    def _filter_by_equipment(self, homes: List[Dict], questionnaire: Dict) -> List[Dict]:
        """
        Filter by special equipment availability.
        
        FUTURE IMPROVEMENTS:
        ├─ Use database fields instead of special_facilities string:
        │  ├─ has_hoist (boolean) - Currently missing from DB! ⚠️
        │  ├─ has_hospital_bed - Currently missing from DB! ⚠️
        │  └─ wheelchair_access (already used, improve with ramp info)
        │
        ├─ Implement partial matching (70%+ instead of 100%):
        │  └─ If patient needs [wheelchair, hoist] and home has only wheelchair,
        │     Still include with warning instead of rejecting
        │
        ├─ Add equipment quality/age consideration:
        │  └─ Modern hoist > old hoist (if data available)
        │
        └─ Link to q12_special_equipment normalization:
           └─ Handle variations: "wheelchair" = "wheelchair access", "hoist" = "ceiling hoist"
        """
        medical_needs = questionnaire.get('section_3_medical_needs', {})
        special_equipment = medical_needs.get('q12_special_equipment', [])
        
        if not special_equipment:
            return homes
        
        required_equipment = set(str(eq).lower() for eq in special_equipment)
        
        filtered = []
        for home in homes:
            # TODO: Replace string matching with database fields when available:
            # home_has_hoist = home.get('has_hoist')  # Will be added to DB
            # home_has_hospital_bed = home.get('has_hospital_bed')  # Will be added to DB
            
            home_facilities = str(home.get('special_facilities', '')).lower()
            
            # Check if home has required equipment
            # TODO: Implement fuzzy/partial matching instead of strict AND logic
            has_all = all(
                eq in home_facilities or eq.replace('_', ' ') in home_facilities
                for eq in required_equipment
            )
            
            if has_all:
                filtered.append(home)
        
        logger.debug(f"Equipment filter: {len(filtered)}/{len(homes)} homes have equipment")
        return filtered
    
    def _filter_by_nursing_staff(self, homes: List[Dict], questionnaire: Dict) -> List[Dict]:
        """Filter by nursing staff availability"""
        medical_needs = questionnaire.get('section_3_medical_needs', {})
        care_types = medical_needs.get('q8_care_types', [])
        
        # Only filter if nursing-specific care needed
        needs_nursing = any('nursing' in str(ct).lower() for ct in care_types)
        
        if not needs_nursing:
            return homes
        
        # Filter: nursing care homes must have nursing staff
        filtered = []
        for home in homes:
            has_nursing = home.get('has_nursing_staff') or \
                         'nursing' in str(home.get('care_types', '')).lower()
            
            if has_nursing:
                filtered.append(home)
        
        logger.debug(f"Nursing filter: {len(filtered)}/{len(homes)} homes have nursing")
        return filtered
    
    def _create_relaxation_message(
        self,
        constraint_config: ConstraintConfig,
        num_results: int,
        total_homes_evaluated: int
    ) -> str:
        """Create message describing constraint relaxation"""
        
        level_name = constraint_config.level.name
        reason = constraint_config.reason
        
        if constraint_config.level == ConstraintLevel.STRICT:
            return f"Found {num_results} homes with strict matching criteria"
        
        elif constraint_config.level == ConstraintLevel.RELAXED:
            return (
                f"Limited options with strict criteria. "
                f"Relaxed: medication, equipment, and nursing preferences. "
                f"Found {num_results} homes."
            )
        
        elif constraint_config.level == ConstraintLevel.CRITICAL:
            return (
                f"Very limited availability in your area. "
                f"Only enforcing critical requirements (care type, safety). "
                f"Found {num_results} homes."
            )
        
        else:  # MINIMAL
            return (
                f"Critical: Very limited options matching your care type. "
                f"Showing all {num_results} available homes. "
                f"Please contact support to discuss alternatives."
            )
    
    def get_constraint_explanation(self, config: ConstraintConfig) -> Dict[str, Any]:
        """Get detailed explanation of constraints being applied"""
        return {
            'level': config.level.name,
            'reason': config.reason,
            'constraints_applied': {
                'care_type': config.apply_care_type,
                'cqc_safety': config.apply_cqc_safety,
                'wheelchair_access': config.apply_wheelchair,
                'medication_support': config.apply_medication,
                'equipment': config.apply_equipment,
                'nursing_staff': config.apply_nursing,
                'google_reviews': config.apply_reviews,
            }
        }


# ==================== INTEGRATION HELPER ====================

def apply_constraint_relaxation_to_matching(
    expansion_result_homes: List[Dict],
    matching_service,
    questionnaire: Dict,
    top_n: int = 5
) -> Tuple[List[Any], Dict[str, Any]]:
    """
    Helper function to apply constraint relaxation to matching results.
    
    Use this when distance expansion doesn't return enough results.
    
    Args:
        expansion_result_homes: Homes from distance expansion
        matching_service: Enhanced MVP matching service
        questionnaire: User questionnaire
        top_n: Number of results to return
    
    Returns:
        (matched_homes, metadata)
    
    Example usage:
        # After distance expansion
        if len(expansion_result.matched_homes) < 3:
            # Apply constraint relaxation
            matched_homes, constraint_meta = apply_constraint_relaxation_to_matching(
                expansion_result_homes=expansion_result.matched_homes,
                matching_service=matching_service,
                questionnaire=questionnaire,
                top_n=5
            )
    """
    
    relaxation_manager = ConstraintRelaxationManager()
    
    # Run constraint relaxation
    matched_homes, constraint_config, message = relaxation_manager.relax_constraints_progressively(
        homes=expansion_result_homes,
        matching_service=matching_service,
        questionnaire=questionnaire,
        top_n=top_n,
        min_results_threshold=3
    )
    
    # Create metadata
    metadata = {
        'constraint_level': constraint_config.level.name,
        'constraints_applied': constraint_config,
        'constraint_explanation': relaxation_manager.get_constraint_explanation(constraint_config),
        'constraint_message': message,
        'homes_matched': len(matched_homes),
        'warnings': [] if constraint_config.level == ConstraintLevel.STRICT else [
            f"⚠️ Search constraints relaxed to {constraint_config.level.name} level",
            message
        ]
    }
    
    return matched_homes, metadata

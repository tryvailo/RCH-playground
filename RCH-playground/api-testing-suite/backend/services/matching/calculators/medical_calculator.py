"""
Medical Capabilities Calculator

Scores home's medical capabilities for different client conditions.
Max points: 30 (distributed as: specialist 10 + nursing 8 + equipment 7 + emergency 5)

Factors:
- Specialist care match (dementia, diabetes, cardiac, mobility)
- Nursing level and RN count
- Medical equipment availability
- Emergency protocols and response time
"""

import logging
from typing import Dict, Any
from services.matching.calculator_base import CategoryCalculator

logger = logging.getLogger(__name__)


class MedicalCalculator(CategoryCalculator):
    """Calculate medical capabilities score (0-1.0)"""
    
    CATEGORY_NAME = 'medical'
    MAX_POINTS = 30.0
    
    async def calculate(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Calculate medical capabilities score"""
        score = 0.0
        home_id = home.get('cqc_location_id') or home.get('id')
        
        try:
            # Extract user medical needs
            medical_needs = user_profile.get('section_3_medical_needs', {}) or {}
            medical_conditions = medical_needs.get('q9_medical_conditions', []) or []
            care_types = medical_needs.get('q8_care_types', []) or []
            mobility_level = medical_needs.get('q10_mobility_level', '')
            medication_needs = medical_needs.get('q11_medication_management', '')
            
            # 1. Specialist care match (10 points)
            specialist_score = await self._score_specialist_care(
                home, medical_conditions, enriched_data
            )
            score += specialist_score
            
            # 2. Nursing level (8 points)
            nursing_score = await self._score_nursing_level(
                home, care_types, enriched_data
            )
            score += nursing_score
            
            # 3. Medical equipment (7 points)
            equipment_score = await self._score_equipment(home, enriched_data)
            score += equipment_score
            
            # 4. Emergency protocols (5 points)
            emergency_score = await self._score_emergency(
                home, medication_needs, enriched_data
            )
            score += emergency_score
            
            # Normalize to 0-1.0
            normalized = min(score / self.MAX_POINTS, 1.0)
            self._log_debug(f"Medical score: {normalized:.2f} ({score}/{self.MAX_POINTS} points)")
            
            return normalized
            
        except Exception as e:
            self._log_warning(f"Error calculating medical score: {str(e)}", home_id)
            return 0.0
    
    async def _score_specialist_care(
        self,
        home: Dict[str, Any],
        medical_conditions: list,
        enriched_data: Dict[str, Any]
    ) -> float:
        """Score specialist care match (0-10 points)"""
        score = 0.0
        
        home_care_types = home.get('care_types', []) or []
        if isinstance(home_care_types, str):
            home_care_types = [home_care_types]
        
        home_care_types_str = str(home_care_types).lower()
        home_name_lower = str(home.get('name', '')).lower()
        
        # Dementia care (4 points)
        if 'dementia_alzheimers' in medical_conditions:
            if self._check_contains(home_care_types_str, 'dementia') or \
               home.get('care_dementia', False) or \
               'dementia' in home_name_lower or \
               self._extract_field(enriched_data, 'cqc_detailed', 'dementia_care', default=False):
                score += 4.0
        
        # Diabetes care (2 points)
        if 'diabetes' in medical_conditions:
            if 'diabetes' in home_name_lower or \
               'diabetes' in home_care_types_str or \
               'diabetes' in self._normalize_string(home.get('specialist_care', '')):
                score += 2.0
        
        # Cardiac care (2 points)
        if 'heart_conditions' in medical_conditions:
            if 'cardiac' in home_name_lower or 'cardiac' in home_care_types_str or \
               'cardiac' in self._normalize_string(home.get('specialist_care', '')) or \
               'heart' in home_name_lower:
                score += 2.0
        
        # Mobility support (2 points)
        if 'mobility_problems' in medical_conditions:
            if home.get('wheelchair_accessible', False) or home.get('wheelchair_access', False):
                score += 2.0
        
        return min(score, 10.0)
    
    async def _score_nursing_level(
        self,
        home: Dict[str, Any],
        care_types: list,
        enriched_data: Dict[str, Any]
    ) -> float:
        """Score nursing level (0-8 points)"""
        score = 0.0
        
        home_care_types = home.get('care_types', []) or []
        if isinstance(home_care_types, str):
            home_care_types = [home_care_types]
        
        home_care_types_str = str(home_care_types).lower()
        
        # Check if nursing required
        if 'medical_nursing' in care_types or 'nursing' in care_types:
            if home.get('care_nursing', False) or 'nursing' in home_care_types_str:
                score += 5.0
                
                # Bonus for RN count
                rn_count = self._safe_int(
                    self._extract_field(enriched_data, 'staff_data', 'combined_analysis', 
                                       'registered_nurses') or
                    home.get('registered_nurses')
                )
                
                if rn_count >= 3:
                    score += 3.0
                elif rn_count >= 1:
                    score += 1.5
        else:
            # Still give some points for having nursing capability
            if home.get('care_nursing', False):
                score += 2.0
        
        return min(score, 8.0)
    
    async def _score_equipment(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Score medical equipment (0-7 points)"""
        score = 0.0
        
        home_care_types = home.get('care_types', []) or []
        home_care_types_str = str(home_care_types).lower()
        
        # Nursing homes typically have equipment (3 points)
        if home.get('care_nursing', False) or 'nursing' in home_care_types_str:
            score += 3.0
        
        # Explicit equipment field (3 points)
        if home.get('medical_equipment', False):
            score += 3.0
        
        # On-site pharmacy (2 points)
        if home.get('on_site_pharmacy', False):
            score += 2.0
        
        # Check enriched data for emergency protocols (1 point)
        if self._extract_field(enriched_data, 'medical_capabilities', 
                              'emergency_protocols', default=False):
            score += 1.0
        
        return min(score, 7.0)
    
    async def _score_emergency(
        self,
        home: Dict[str, Any],
        medication_needs: str,
        enriched_data: Dict[str, Any]
    ) -> float:
        """Score emergency protocols (0-5 points)"""
        score = 0.0
        
        # Emergency response time (3 points)
        response_time = self._safe_float(
            self._extract_field(enriched_data, 'medical_capabilities', 
                              'emergency_response_time')
        )
        
        if response_time > 0:
            if response_time <= 5:
                score += 3.0
            elif response_time <= 10:
                score += 1.5
        
        # Medication management (2 points)
        if medication_needs in ['complex_medication', 'multiple_medications']:
            if self._extract_field(enriched_data, 'medical_capabilities', 
                                  'medication_management', default=False):
                score += 2.0
        
        return min(score, 5.0)

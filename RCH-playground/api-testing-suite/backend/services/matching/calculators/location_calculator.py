"""
Location & Access Calculator

Scores home's location and accessibility.
Max points: 15 (distance 10 + accessibility 5)

Factors:
- Distance from preferred location
- Accessibility features
- Transport access
"""

import logging
from typing import Dict, Any
from services.matching.calculator_base import CategoryCalculator

logger = logging.getLogger(__name__)


class LocationCalculator(CategoryCalculator):
    """Calculate location & access score (0-1.0)"""
    
    CATEGORY_NAME = 'location'
    MAX_POINTS = 15.0
    
    async def calculate(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Calculate location & access score"""
        score = 0.0
        home_id = home.get('cqc_location_id') or home.get('id')
        
        try:
            # Extract user location preferences
            location_budget = user_profile.get('section_2_location_budget', {}) or {}
            max_distance_pref = location_budget.get('q6_max_distance', 'distance_not_important')
            
            # 1. Distance score (10 points)
            distance_score = await self._score_distance(home, max_distance_pref)
            score += distance_score
            
            # 2. Accessibility score (5 points)
            accessibility_score = await self._score_accessibility(
                home, user_profile, enriched_data
            )
            score += accessibility_score
            
            # Normalize to 0-1.0
            normalized = min(score / self.MAX_POINTS, 1.0)
            self._log_debug(f"Location score: {normalized:.2f} ({score}/{self.MAX_POINTS} points)")
            
            return normalized
            
        except Exception as e:
            self._log_warning(f"Error calculating location score: {str(e)}", home_id)
            return 0.0
    
    async def _score_distance(
        self,
        home: Dict[str, Any],
        max_distance_pref: str
    ) -> float:
        """Score distance preference (0-10 points)"""
        score = 0.0
        
        # Get distance (already calculated in report_routes.py)
        distance_km = self._safe_float(home.get('distance_km', 9999.0))
        
        if distance_km >= 9999:
            return 0.0  # No valid distance
        
        # Score based on user preference
        if max_distance_pref == 'within_5km':
            if distance_km <= 5:
                score = 10.0
            elif distance_km <= 15:
                score = 5.0
            else:
                score = 0.0
        elif max_distance_pref == 'within_15km':
            if distance_km <= 15:
                score = 10.0
            elif distance_km <= 30:
                score = 5.0
            else:
                score = 0.0
        elif max_distance_pref == 'within_30km':
            if distance_km <= 30:
                score = 10.0
            elif distance_km <= 50:
                score = 5.0
            else:
                score = 0.0
        else:  # distance_not_important
            # Still give some score based on absolute distance
            if distance_km <= 10:
                score = 10.0
            elif distance_km <= 25:
                score = 8.0
            elif distance_km <= 50:
                score = 5.0
            elif distance_km <= 100:
                score = 2.0
            else:
                score = 0.0
        
        return min(max(score, 0.0), 10.0)
    
    async def _score_accessibility(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Score accessibility features (0-5 points)"""
        score = 0.0
        
        # Extract user mobility needs
        medical_needs = user_profile.get('section_3_medical_needs', {}) or {}
        mobility_level = medical_needs.get('q10_mobility_level', '')
        
        # Wheelchair access (2 points)
        if mobility_level in ['wheelchair_bound', 'limited_mobility']:
            if home.get('wheelchair_accessible', False) or home.get('wheelchair_access', False):
                score += 2.0
        else:
            # General accessibility (1 point)
            if home.get('wheelchair_accessible', False) or home.get('wheelchair_access', False):
                score += 1.0
        
        # Ground floor accommodation (1 point)
        if home.get('ground_floor_rooms', False):
            score += 1.0
        
        # Lift/elevator access (1 point)
        if home.get('lift_access', False) or home.get('elevator_access', False):
            score += 1.0
        
        # Parking availability (1 point)
        if home.get('parking_available', False):
            score += 1.0
        
        return min(max(score, 0.0), 5.0)

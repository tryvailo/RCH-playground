"""
Additional Services & Amenities Calculator

Scores home's additional services and facility amenities.
Max points: 10 (amenities 6 + services 4)

Factors:
- Facility amenities (gym, spa, library, etc.)
- Additional services (hairdressing, catering, etc.)
- Quality of living spaces
"""

import logging
from typing import Dict, Any
from services.matching.calculator_base import CategoryCalculator

logger = logging.getLogger(__name__)


class ServicesCalculator(CategoryCalculator):
    """Calculate services & amenities score (0-1.0)"""
    
    CATEGORY_NAME = 'services'
    MAX_POINTS = 10.0
    
    async def calculate(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Calculate services & amenities score"""
        score = 0.0
        home_id = home.get('cqc_location_id') or home.get('id')
        
        try:
            # 1. Amenities (6 points)
            amenities_score = await self._score_amenities(home, enriched_data)
            score += amenities_score
            
            # 2. Additional services (4 points)
            services_score = await self._score_services(home, enriched_data)
            score += services_score
            
            # Normalize to 0-1.0
            normalized = min(score / self.MAX_POINTS, 1.0)
            self._log_debug(f"Services score: {normalized:.2f} ({score}/{self.MAX_POINTS} points)")
            
            return normalized
            
        except Exception as e:
            self._log_warning(f"Error calculating services score: {str(e)}", home_id)
            return 0.0
    
    async def _score_amenities(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Score facility amenities (0-6 points)"""
        score = 0.0
        
        # Check for amenity fields
        amenities = self._safe_list(home.get('amenities', []))
        
        # Count amenity types (0.5 points each, max 6)
        amenity_count = len(amenities)
        score = min(6.0, amenity_count * 0.5)
        
        # Bonus for specific premium amenities
        premium_amenities = ['gym', 'spa', 'swimming_pool', 'library', 'cinema']
        for premium in premium_amenities:
            if self._check_contains(amenities, premium):
                score += 0.5
        
        return min(max(score, 0.0), 6.0)
    
    async def _score_services(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Score additional services (0-4 points)"""
        score = 0.0
        
        # Count additional services
        services = self._safe_list(home.get('additional_services', []))
        
        # Services like hairdressing, laundry, catering, etc.
        service_count = len(services)
        score = min(4.0, service_count * 0.5)  # 0.5 points per service
        
        # Bonus for specific important services
        important_services = [
            'hairdressing', 'laundry', 'catering', 'pharmacy',
            'transport', 'medical_clinic'
        ]
        for service in important_services:
            if self._check_contains(services, service):
                score += 0.3
        
        return min(max(score, 0.0), 4.0)

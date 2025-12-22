"""
CQC Quality Calculator

Scores home's CQC quality domain ratings.
Max points: 16 (overall 5 + effective 3 + caring 3 + responsive 3 + well-led 2)

Factors:
- Overall CQC rating
- Key CQC domains: Effective, Caring, Responsive, Well-Led
"""

import logging
from typing import Dict, Any
from services.matching.calculator_base import CategoryCalculator

logger = logging.getLogger(__name__)


class CQCCalculator(CategoryCalculator):
    """Calculate CQC quality score (0-1.0)"""
    
    CATEGORY_NAME = 'cqc'
    MAX_POINTS = 16.0
    
    RATING_MAP = {
        'Outstanding': 1.0,
        'Good': 0.75,
        'Requires improvement': 0.4,
        'Inadequate': 0.0
    }
    
    async def calculate(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Calculate CQC quality score"""
        score = 0.0
        home_id = home.get('cqc_location_id') or home.get('id')
        
        try:
            # 1. Overall rating (5 points)
            overall_score = await self._score_overall_rating(home, enriched_data)
            score += overall_score
            
            # 2. Key domains (11 points)
            domains_score = await self._score_domain_ratings(home, enriched_data)
            score += domains_score
            
            # Normalize to 0-1.0
            normalized = min(score / self.MAX_POINTS, 1.0)
            self._log_debug(f"CQC score: {normalized:.2f} ({score}/{self.MAX_POINTS} points)")
            
            return normalized
            
        except Exception as e:
            self._log_warning(f"Error calculating CQC score: {str(e)}", home_id)
            return 0.0
    
    async def _score_overall_rating(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Score overall CQC rating (0-5 points)"""
        
        overall_rating = (
            self._extract_field(enriched_data, 'cqc_detailed', 'overall_rating') or
            home.get('rating') or
            home.get('overall_rating')
        )
        
        if not overall_rating:
            return 0.0
        
        rating_factor = self._score_rating(overall_rating, self.RATING_MAP)
        return rating_factor * 5.0  # Scale to 5 points
    
    async def _score_domain_ratings(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Score CQC domain ratings (0-11 points)"""
        score = 0.0
        
        detailed_ratings = self._extract_field(enriched_data, 'cqc_detailed', 
                                              'detailed_ratings', default={})
        
        # Effective (3 points)
        effective = detailed_ratings.get('effective', {}).get('rating')
        if effective:
            effective_factor = self._score_rating(effective, self.RATING_MAP)
            score += effective_factor * 3.0
        
        # Caring (3 points)
        caring = detailed_ratings.get('caring', {}).get('rating')
        if caring:
            caring_factor = self._score_rating(caring, self.RATING_MAP)
            score += caring_factor * 3.0
        
        # Responsive (3 points)
        responsive = detailed_ratings.get('responsive', {}).get('rating')
        if responsive:
            responsive_factor = self._score_rating(responsive, self.RATING_MAP)
            score += responsive_factor * 3.0
        
        # Well-led (2 points)
        well_led = detailed_ratings.get('well-led', {}).get('rating')
        if well_led:
            well_led_factor = self._score_rating(well_led, self.RATING_MAP)
            score += well_led_factor * 2.0
        
        return min(max(score, 0.0), 11.0)

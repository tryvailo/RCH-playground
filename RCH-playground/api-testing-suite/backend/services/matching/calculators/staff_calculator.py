"""
Staff Quality Calculator

Scores home's staff quality and stability.
Max points: 18 (ratings 6 + retention 6 + qualifications 6)

Factors:
- Glassdoor/employee satisfaction ratings
- Staff retention and turnover
- Staff qualifications and certifications
"""

import logging
from typing import Dict, Any
from services.matching.calculator_base import CategoryCalculator

logger = logging.getLogger(__name__)


class StaffCalculator(CategoryCalculator):
    """Calculate staff quality score (0-1.0)"""
    
    CATEGORY_NAME = 'staff'
    MAX_POINTS = 18.0
    
    async def calculate(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Calculate staff quality score"""
        score = 0.0
        home_id = home.get('cqc_location_id') or home.get('id')
        
        try:
            # 1. Staff satisfaction ratings (6 points)
            ratings_score = await self._score_satisfaction_ratings(home, enriched_data)
            score += ratings_score
            
            # 2. Staff retention (6 points)
            retention_score = await self._score_retention(home, enriched_data)
            score += retention_score
            
            # 3. Qualifications (6 points)
            qualifications_score = await self._score_qualifications(home, enriched_data)
            score += qualifications_score
            
            # Normalize to 0-1.0
            normalized = min(score / self.MAX_POINTS, 1.0)
            self._log_debug(f"Staff score: {normalized:.2f} ({score}/{self.MAX_POINTS} points)")
            
            return normalized
            
        except Exception as e:
            self._log_warning(f"Error calculating staff score: {str(e)}", home_id)
            return 0.0
    
    async def _score_satisfaction_ratings(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Score employee satisfaction (0-6 points)"""
        score = 0.0
        
        # Glassdoor rating (0-5 stars)
        glassdoor_rating = self._safe_float(
            self._extract_field(enriched_data, 'staff_data', 'combined_analysis',
                              'employee_satisfaction_rating')
        )
        
        if glassdoor_rating > 0:
            # Convert 0-5 to 0-6 points
            score = (glassdoor_rating / 5.0) * 6.0
        
        return min(max(score, 0.0), 6.0)
    
    async def _score_retention(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Score staff retention (0-6 points)"""
        score = 6.0  # Base score (start high, deduct for turnover)
        
        # Turnover rate (%)
        turnover_rate = self._safe_float(
            self._extract_field(enriched_data, 'staff_data', 'combined_analysis',
                              'turnover_rate_percent')
        )
        
        if turnover_rate > 0:
            # High turnover = lower score
            if turnover_rate <= 10:
                score = 6.0  # Excellent
            elif turnover_rate <= 20:
                score = 5.0  # Good
            elif turnover_rate <= 30:
                score = 4.0  # Okay
            elif turnover_rate <= 50:
                score = 2.0  # Concerning
            else:
                score = 0.0  # Very high turnover
        
        # Average tenure bonus (2+ years = bonus)
        avg_tenure = self._safe_float(
            self._extract_field(enriched_data, 'staff_data', 'combined_analysis',
                              'average_tenure_years')
        )
        
        if avg_tenure >= 2.0:
            score = min(6.0, score + 1.0)
        
        return min(max(score, 0.0), 6.0)
    
    async def _score_qualifications(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Score staff qualifications (0-6 points)"""
        score = 0.0
        
        # Check certifications list
        certifications = self._safe_list(
            self._extract_field(enriched_data, 'staff_data', 'combined_analysis',
                              'certifications', default=[])
        )
        
        if certifications:
            # Award points based on number of certifications
            score += min(len(certifications) * 0.5, 3.0)
        
        # Management score from Glassdoor
        management_score = self._safe_float(
            self._extract_field(enriched_data, 'staff_data', 'combined_analysis',
                              'management_score')
        )
        
        if management_score > 0:
            # Convert 0-5 to 0-3 points
            score += (management_score / 5.0) * 3.0
        
        return min(max(score, 0.0), 6.0)

"""
Safety & Quality Calculator

Scores home's safety and quality standards.
Max points: 25 (CQC 10 + FSA 8 + safeguarding 5 + audit 2)

Factors:
- CQC overall rating and trend
- FSA food hygiene rating
- Safeguarding incidents
- Filing compliance
"""

import logging
from typing import Dict, Any
from services.matching.calculator_base import CategoryCalculator

logger = logging.getLogger(__name__)


class SafetyCalculator(CategoryCalculator):
    """Calculate safety & quality score (0-1.0)"""
    
    CATEGORY_NAME = 'safety'
    MAX_POINTS = 25.0
    
    # CQC rating scoring
    CQC_RATING_MAP = {
        'Outstanding': 4.0,
        'Good': 3.0,
        'Requires improvement': 1.0,
        'Inadequate': 0.0
    }
    
    # FSA rating scoring
    FSA_RATING_MAP = {
        5: 8.0,   # 5 = Excellent
        4: 6.0,   # 4 = Good
        3: 4.0,   # 3 = Satisfactory
        2: 2.0,   # 2 = Needs improvement
        1: 0.0    # 1 = Unacceptable
    }
    
    async def calculate(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Calculate safety & quality score"""
        score = 0.0
        home_id = home.get('cqc_location_id') or home.get('id')
        
        try:
            # Extract user safety needs
            safety_needs = user_profile.get('section_4_safety_special_needs', {}) or {}
            fall_history = safety_needs.get('q13_fall_history', '')
            high_fall_risk = fall_history in ['3_plus_or_serious_injuries', 'high_risk_of_falling']
            
            # 1. CQC compliance (10 points)
            cqc_score = await self._score_cqc(home, enriched_data, high_fall_risk)
            score += cqc_score
            
            # 2. FSA food safety (8 points)
            fsa_score = await self._score_fsa(home, enriched_data)
            score += fsa_score
            
            # 3. Safeguarding incidents (5 points)
            safeguarding_score = await self._score_safeguarding(home, enriched_data)
            score += safeguarding_score
            
            # 4. Filing compliance (2 points)
            compliance_score = await self._score_compliance(home, enriched_data)
            score += compliance_score
            
            # Normalize to 0-1.0
            normalized = min(score / self.MAX_POINTS, 1.0)
            self._log_debug(f"Safety score: {normalized:.2f} ({score}/{self.MAX_POINTS} points)")
            
            return normalized
            
        except Exception as e:
            self._log_warning(f"Error calculating safety score: {str(e)}", home_id)
            return 0.0
    
    async def _score_cqc(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any],
        high_fall_risk: bool
    ) -> float:
        """Score CQC compliance (0-10 points)"""
        score = 0.0
        
        # Overall rating (priority: API > DB > CSV)
        overall_rating = (
            self._extract_field(enriched_data, 'cqc_detailed', 'overall_rating') or
            self._extract_field(enriched_data, 'cqc_detailed', 'current_rating') or
            home.get('cqc_rating_overall') or
            home.get('rating') or
            home.get('overall_rating')
        )
        
        if overall_rating:
            rating_score = self._score_rating(overall_rating, self.CQC_RATING_MAP)
            score += rating_score * 1.5  # Weight overall rating
        
        # Trend analysis (improving = +2, declining = -1)
        trend = self._extract_field(enriched_data, 'cqc_detailed', 'trend', default='stable')
        if trend == 'improving':
            score += 2.0
        elif trend == 'declining':
            score -= 1.0
        
        # Fall prevention specific (if high fall risk)
        if high_fall_risk:
            safe_rating = (
                self._extract_field(enriched_data, 'cqc_detailed', 'safe_rating') or
                self._extract_field(enriched_data, 'cqc_detailed', 'detailed_ratings', 
                                   'safe', 'rating') or
                home.get('cqc_rating_safe') or
                overall_rating
            )
            
            if safe_rating:
                safe_score = self._score_rating(safe_rating, self.CQC_RATING_MAP)
                score += safe_score * 1.5  # Extra weight for fall risk
        
        return min(max(score, 0.0), 10.0)
    
    async def _score_fsa(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Score FSA food safety (0-8 points)"""
        score = 0.0
        
        # Check for FSA scoring (pre-calculated from API)
        fsa_scoring = enriched_data.get('fsa_scoring', {})
        if fsa_scoring:
            fsa_points = self._safe_float(fsa_scoring.get('fsa_points', 0))
            score = (fsa_points / 7.0) * 8.0  # Scale to 8 points
        else:
            # Fallback to direct rating
            fsa_data = enriched_data.get('fsa_detailed', {})
            fsa_rating = (
                self._extract_field(fsa_data, 'rating') or
                self._extract_field(fsa_data, 'rating_value') or
                home.get('fsa_rating') or
                home.get('food_hygiene_rating')
            )
            
            if fsa_rating:
                fsa_rating_int = self._safe_int(fsa_rating)
                score = self._safe_float(self.FSA_RATING_MAP.get(fsa_rating_int, 0.0))
            
            # Trend bonus
            fsa_trend = self._extract_field(fsa_data, 'trend') or \
                       enriched_data.get('fsa_trend')
            if fsa_trend == 'improving' and score > 0:
                score = min(8.0, score + 1.0)
            elif fsa_trend == 'declining' and score > 0:
                score = max(0.0, score - 1.0)
        
        return min(max(score, 0.0), 8.0)
    
    async def _score_safeguarding(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Score safeguarding (0-5 points, higher is better)"""
        score = 5.0  # Start with full points
        
        # Get incident count (priority: API > DB)
        incidents = (
            self._extract_field(enriched_data, 'cqc_detailed', 
                              'safeguarding_incidents') or
            home.get('safeguarding_incidents')
        )
        
        if incidents is not None:
            incident_count = self._safe_int(incidents)
            if incident_count > 0:
                # Deduct 1 point per incident (max 5)
                score = max(0.0, 5.0 - (incident_count * 1.0))
        
        return min(max(score, 0.0), 5.0)
    
    async def _score_compliance(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Score filing compliance (0-2 points)"""
        score = 0.0
        
        # Check filing compliance from APIs (priority: Companies House > Financial)
        filing_compliance = (
            self._extract_field(enriched_data, 'companies_house_scoring', 
                              'filing_compliance') or
            self._extract_field(enriched_data, 'financial_data', 
                              'filing_compliance') or
            True  # Default to compliant if unknown
        )
        
        if filing_compliance:
            score = 2.0
        
        return score

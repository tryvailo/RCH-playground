"""
Financial Stability Calculator

Scores home's financial stability and affordability.
Max points: 20 (price match 8 + stability 8 + value 4)

Factors:
- Price vs user budget
- Financial stability (Altman Z-score, bankruptcy risk)
- Quality-to-price ratio
"""

import logging
from typing import Dict, Any
from services.matching.calculator_base import CategoryCalculator

logger = logging.getLogger(__name__)


class FinancialCalculator(CategoryCalculator):
    """Calculate financial stability score (0-1.0)"""
    
    CATEGORY_NAME = 'financial'
    MAX_POINTS = 20.0
    
    async def calculate(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Calculate financial stability score"""
        score = 0.0
        home_id = home.get('cqc_location_id') or home.get('id')
        
        try:
            # 1. Price match score (8 points)
            price_score = await self._score_price_match(home, user_profile)
            score += price_score
            
            # 2. Financial stability (8 points)
            stability_score = await self._score_financial_stability(home, enriched_data)
            score += stability_score
            
            # 3. Value ratio (4 points)
            value_score = await self._score_value_ratio(home, enriched_data)
            score += value_score
            
            # Normalize to 0-1.0
            normalized = min(score / self.MAX_POINTS, 1.0)
            self._log_debug(f"Financial score: {normalized:.2f} ({score}/{self.MAX_POINTS} points)")
            
            return normalized
            
        except Exception as e:
            self._log_warning(f"Error calculating financial score: {str(e)}", home_id)
            return 0.0
    
    async def _score_price_match(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> float:
        """Score price match to budget (0-8 points)"""
        score = 0.0
        
        # Get home price (weekly)
        try:
            from utils.price_extractor import extract_weekly_price
            price = extract_weekly_price(home)
        except:
            price_fields = ['weekly_price', 'price_weekly', 'cost_weekly']
            price = None
            for field in price_fields:
                price = home.get(field)
                if price:
                    break
        
        price = self._safe_float(price)
        if price <= 0:
            return 0.0  # No valid price
        
        # Get user budget
        location_budget = user_profile.get('section_2_location_budget', {}) or {}
        budget = location_budget.get('q7_budget', '')
        
        # Budget ranges in weekly £
        budget_ranges = {
            'under_3000_self': (0, 692),
            'under_3000_council': (0, 692),
            '3000_5000_self': (692, 1154),
            '3000_5000_council': (692, 1154),
            '5000_7000_self': (1154, 1616),
            '5000_7000_local': (1154, 1616),
            '7000_plus_self': (1616, 5000),
            'not_sure': (0, 5000)
        }
        
        min_budget, max_budget = budget_ranges.get(budget, (0, 5000))
        
        # Score based on budget fit
        if price <= max_budget * 0.8:
            score = 8.0  # Well within budget
        elif price <= max_budget:
            score = 6.0  # Within budget
        elif price <= max_budget * 1.2:
            score = 4.0  # Slightly over
        else:
            score = 0.0  # Way over budget
        
        return min(max(score, 0.0), 8.0)
    
    async def _score_financial_stability(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Score financial stability (0-8 points)"""
        score = 4.0  # Base score
        
        # Altman Z-score (4 bonus points)
        altman_z = self._safe_float(
            self._extract_field(enriched_data, 'financial_data', 'altman_z_score')
        )
        
        if altman_z > 0:
            if altman_z >= 2.99:
                score += 4.0  # Safe zone
            elif altman_z >= 1.81:
                score += 2.0  # Gray zone
            else:
                score -= 2.0  # High risk
        
        # Check for red flags (deduct points)
        red_flags = self._extract_field(enriched_data, 'financial_data', 'red_flags', default=[])
        red_flags_count = len(red_flags) if red_flags else 0
        
        if red_flags_count > 0:
            score -= min(red_flags_count * 0.5, 4.0)  # Deduct up to 2 points
        
        # Company status check
        company_status = self._extract_field(enriched_data, 'financial_data', 'company_status', default='').lower()
        if company_status and company_status != 'active':
            score -= 3.0  # Major concern
        
        return min(max(score, 0.0), 8.0)
    
    async def _score_value_ratio(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Score quality-to-price ratio (0-4 points)"""
        
        # Get CQC rating as proxy for quality
        cqc_rating = self._extract_field(enriched_data, 'cqc_detailed', 'overall_rating') or \
                    home.get('rating')
        
        # Get price
        try:
            from utils.price_extractor import extract_weekly_price
            price = extract_weekly_price(home)
        except:
            price = home.get('weekly_price') or home.get('price_weekly')
        
        price = self._safe_float(price)
        
        if price <= 0:
            return 2.0  # Unknown price, moderate score
        
        # Score based on rating and price
        rating_quality = 1.0
        if cqc_rating:
            rating_map = {'Outstanding': 1.0, 'Good': 0.7, 'Requires improvement': 0.4, 'Inadequate': 0.0}
            rating_quality = rating_map.get(cqc_rating, 0.5)
        
        # Calculate value ratio (adjusted for price levels)
        # Cheaper homes get slight bonus for value
        if price <= 600:  # Affordable
            return min(4.0, 3.0 + rating_quality)
        elif price <= 1000:  # Mid-range
            return min(4.0, 2.0 + rating_quality)
        else:  # Premium
            return min(4.0, 1.0 + rating_quality)

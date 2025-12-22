"""
Social & Community Calculator

Scores home's social activities and community integration.
Max points: 12 (activities 8 + community 4)

Factors:
- Social activities and programs
- Community integration
- Visitor support
"""

import logging
from typing import Dict, Any
from services.matching.calculator_base import CategoryCalculator

logger = logging.getLogger(__name__)


class SocialCalculator(CategoryCalculator):
    """Calculate social & community score (0-1.0)"""
    
    CATEGORY_NAME = 'social'
    MAX_POINTS = 12.0
    
    async def calculate(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Calculate social & community score"""
        score = 0.0
        home_id = home.get('cqc_location_id') or home.get('id')
        
        try:
            # 1. Social activities (8 points)
            activities_score = await self._score_activities(home, enriched_data)
            score += activities_score
            
            # 2. Community integration (4 points)
            community_score = await self._score_community(home, enriched_data)
            score += community_score
            
            # Normalize to 0-1.0
            normalized = min(score / self.MAX_POINTS, 1.0)
            self._log_debug(f"Social score: {normalized:.2f} ({score}/{self.MAX_POINTS} points)")
            
            return normalized
            
        except Exception as e:
            self._log_warning(f"Error calculating social score: {str(e)}", home_id)
            return 0.0
    
    async def _score_activities(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Score social activities (0-8 points)"""
        score = 0.0
        
        # Check CQC Responsive domain (includes activities)
        responsive_rating = self._extract_field(
            enriched_data, 'cqc_detailed', 'detailed_ratings', 
            'responsive', 'rating'
        )
        
        if responsive_rating:
            rating_map = {
                'Outstanding': 8.0,
                'Good': 6.0,
                'Requires improvement': 3.0,
                'Inadequate': 0.0
            }
            score = rating_map.get(responsive_rating, 0.0)
        else:
            # Fallback: count activity mentions
            activities = self._safe_list(home.get('activities', []))
            activity_programs = self._safe_list(home.get('activity_programs', []))
            
            total_activities = len(activities) + len(activity_programs)
            score = min(8.0, total_activities * 1.0)  # 1 point per activity type
        
        return min(max(score, 0.0), 8.0)
    
    async def _score_community(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """Score community integration (0-4 points)"""
        score = 0.0
        
        # Visitor support (1 point)
        if home.get('visiting_hours', False) or home.get('visitor_support', False):
            score += 1.0
        
        # Community events (1 point)
        if home.get('community_events', False) or \
           self._check_contains(home.get('activities', []), 'community', 'event'):
            score += 1.0
        
        # Volunteer programs (1 point)
        if home.get('volunteer_programs', False):
            score += 1.0
        
        # Local partnerships (1 point)
        if home.get('local_partnerships', False) or \
           self._check_contains(home.get('activities', []), 'partnership', 'local'):
            score += 1.0
        
        return min(max(score, 0.0), 4.0)

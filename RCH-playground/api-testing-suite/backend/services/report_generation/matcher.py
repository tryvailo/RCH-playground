"""
Report Matcher

Orchestrates matching of care homes for professional reports.
Wrapper around MatchingService with calculators and selection.

Extracted from report_routes.py lines 900-1200
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ReportMatcher:
    """Orchestrate matching for professional reports"""
    
    def __init__(self):
        """Initialize matcher"""
        from services.professional_matching_service import ProfessionalMatchingService
        self.matching_service = ProfessionalMatchingService()
    
    async def match_homes(
        self,
        homes: List[Dict[str, Any]],
        questionnaire: Dict[str, Any],
        enriched_homes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Match and score all homes.
        
        Args:
            homes: List of care homes
            questionnaire: User questionnaire
            enriched_homes: Enriched home data from orchestrator
        
        Returns:
            List of scored homes
        """
        logger.info(f"Matching {len(homes)} homes...")
        
        # Calculate dynamic weights based on user profile
        weights, conditions = self.matching_service.calculate_dynamic_weights(questionnaire)
        logger.info(f"Applied conditions: {conditions}")
        
        scored_homes = []
        
        for home, enriched_home in zip(homes, enriched_homes):
            enriched_data = enriched_home.get('enrichments', {})
            
            # Calculate match score
            match_result = self.matching_service.calculate_156_point_match(
                home, questionnaire, enriched_data, weights
            )
            
            scored_homes.append({
                'home': home,
                'match_score': match_result['total'],
                'normalized_score': match_result['normalized'],
                'category_scores': match_result['category_scores'],
                'point_allocations': match_result['point_allocations'],
                'weights': match_result['weights']
            })
        
        # Sort by score descending
        scored_homes.sort(key=lambda h: h['match_score'], reverse=True)
        
        logger.info(f"✅ Matched {len(scored_homes)} homes")
        logger.info(f"Top 3 scores: {[h['match_score'] for h in scored_homes[:3]]}")
        
        return scored_homes

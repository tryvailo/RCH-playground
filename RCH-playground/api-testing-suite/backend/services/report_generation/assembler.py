"""
Report Assembler

Assembles final professional report from scored homes.
Handles:
- Top-5 selection with diversity
- Reasoning generation
- Report formatting
- Final assembly

Extracted from report_routes.py lines 1200-1600
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ReportAssembler:
    """Assemble final professional report"""
    
    def __init__(self):
        """Initialize assembler"""
        from services.matching.selection_service import SelectionService
        from services.matching.reasoning_generator import ReasoningGenerator
        
        self.selection_service = SelectionService()
        self.reasoning_generator = ReasoningGenerator()
    
    async def assemble_report(
        self,
        scored_homes: List[Dict[str, Any]],
        questionnaire: Dict[str, Any],
        enriched_homes_map: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """
        Assemble final professional report.
        
        Args:
            scored_homes: Scored homes from matcher
            questionnaire: User questionnaire
            enriched_homes_map: Map of home_id -> enriched_data
        
        Returns:
            Complete professional report
        """
        logger.info("Assembling professional report...")
        
        # 1. Select top 5 with diversity
        selection_result = await self.selection_service.select_top_5(
            scored_homes, questionnaire, enriched_homes_map
        )
        
        top_5 = selection_result['top_5']
        category_winners = selection_result['category_winners']
        diversity_metrics = selection_result['diversity_metrics']
        
        logger.info(
            f"Selected top 5: {diversity_metrics['unique_providers']} providers, "
            f"{diversity_metrics['unique_locations']} locations"
        )
        
        # 2. Generate reasoning for each
        top_5_with_reasoning = []
        
        for i, home_data in enumerate(top_5):
            home = home_data.get('home', home_data)
            home_id = home.get('cqc_location_id') or home.get('id')
            
            enriched = enriched_homes_map.get(home_id, {})
            
            # Get full home data with scores from scored_homes
            full_home_data = None
            for scored in scored_homes:
                if (scored.get('home', {}).get('cqc_location_id') or 
                    scored.get('home', {}).get('id')) == home_id:
                    full_home_data = scored
                    break
            
            if not full_home_data:
                full_home_data = home_data
            
            # Generate reasoning
            reasoning = self.reasoning_generator.generate_reasoning(
                home, 
                home_data.get('category', 'best_overall'),
                questionnaire,
                enriched,
                full_home_data
            )
            
            top_5_with_reasoning.append({
                'rank': i + 1,
                'home': {
                    'id': home.get('cqc_location_id') or home.get('id'),
                    'name': home.get('name'),
                    'location': home.get('city') or home.get('local_authority'),
                    'distance_km': home.get('distance_km'),
                    'rating': home.get('rating') or home.get('overall_rating'),
                    'price_weekly': home.get('weekly_price'),
                    'care_types': home.get('care_types', [])
                },
                'match': {
                    'score': home_data.get('score', full_home_data.get('match_score', 0)),
                    'normalized': int((home_data.get('score', full_home_data.get('match_score', 0)) / 156) * 100),
                    'category_scores': full_home_data.get('category_scores', {}),
                    'point_allocations': full_home_data.get('point_allocations', {})
                },
                'reasoning': reasoning,
                'category': home_data.get('category', 'best_overall')
            })
        
        # 3. Build report
        report = {
            'summary': {
                'generated_at': datetime.now().isoformat(),
                'user_location': self._get_user_location(questionnaire),
                'care_type': self._get_care_type(questionnaire),
                'total_homes_evaluated': len(scored_homes),
                'diversity': {
                    'unique_providers': diversity_metrics.get('unique_providers', 0),
                    'unique_locations': diversity_metrics.get('unique_locations', 0)
                }
            },
            'matching': {
                'top_5': top_5_with_reasoning,
                'category_winners': {
                    name: {
                        'home_name': winner.get('home', {}).get('name'),
                        'score': winner.get('score', 0),
                        'category': winner.get('category', '')
                    }
                    for name, winner in category_winners.items()
                }
            }
        }
        
        logger.info("✅ Report assembled successfully")
        
        return report
    
    def _get_user_location(self, questionnaire: Dict) -> str:
        """Extract user location from questionnaire"""
        location_budget = questionnaire.get('section_2_location_budget', {})
        postcode = location_budget.get('q4_postcode', '')
        city = location_budget.get('q5_preferred_city', '')
        
        if postcode:
            return f"{postcode} ({city})" if city else postcode
        elif city:
            return city
        else:
            return "Not specified"
    
    def _get_care_type(self, questionnaire: Dict) -> str:
        """Extract care type from questionnaire"""
        medical_needs = questionnaire.get('section_3_medical_needs', {})
        care_types = medical_needs.get('q8_care_types', [])
        
        care_type_labels = {
            'specialised_dementia': 'Dementia Care',
            'nursing': 'Nursing Care',
            'general_nursing': 'Nursing Care',
            'general_residential': 'Residential Care'
        }
        
        for care_type in care_types:
            if care_type in care_type_labels:
                return care_type_labels[care_type]
        
        return 'Residential Care'

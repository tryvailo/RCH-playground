"""
Selection Service - Top-5 Home Selection

Selects top 5 matched homes with diversity guarantees.
Implements:
- Best overall match selection
- Best medical & safety match selection  
- Priority-based winners (quality, cost, location, amenities)
- Diversity enforcement (no duplicate providers/locations)
- Reasoning generation for each selection

Extracted from professional_matching_service.py to improve modularity.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SelectionResult:
    """Result of home selection"""
    
    home: Dict[str, Any]
    rank: int
    score: float
    category: str
    reasoning: List[str]
    is_automatic: bool = True


class SelectionService:
    """
    Service for selecting top 5 homes with multiple criteria and diversity guarantees.
    
    Selection categories:
    - Best Overall (highest match score)
    - Best Medical & Safety (medical + safety weights)
    - Priority 1 (user's top priority)
    - Priority 2 (user's 2nd priority)
    - Priority 3 (user's 3rd priority)
    """
    
    # Priority category mapping
    PRIORITY_MAPPING = {
        'quality_reputation': {
            'cqc': 0.5,
            'staff': 0.5
        },
        'cost_financial': {
            'financial': 1.0
        },
        'location_social': {
            'location': 0.5,
            'social': 0.5
        },
        'comfort_amenities': {
            'services': 1.0
        }
    }
    
    async def select_top_5(
        self,
        scored_homes: List[Dict[str, Any]],
        user_profile: Dict[str, Any],
        enriched_data_map: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """
        Select top 5 homes with multiple categories.
        
        Args:
            scored_homes: List of homes with scores
            user_profile: User questionnaire
            enriched_data_map: Dict of home_id -> enriched_data
        
        Returns:
            {
                'top_5': [SelectionResult, ...],
                'category_winners': {category: SelectionResult, ...},
                'diversity_metrics': {...}
            }
        """
        if not scored_homes:
            return {
                'top_5': [],
                'category_winners': {},
                'diversity_metrics': {
                    'unique_providers': 0,
                    'unique_locations': 0,
                    'homes_replaced': 0
                }
            }
        
        # 1. Select best overall
        best_overall = self._select_best_overall(scored_homes)
        
        # 2. Select category winners
        category_winners = {}
        
        # Best medical & safety
        best_medical = self._select_best_medical_safety(scored_homes)
        category_winners['best_medical_safety'] = best_medical
        
        # Priority-based winners
        priorities = user_profile.get('section_6_priorities', {}).get('q18_priority_ranking', {})
        priority_order = priorities.get('priority_order', [])
        
        for i, priority_id in enumerate(priority_order[:4]):  # Max 4 priorities
            winner = self._select_priority_winner(
                scored_homes, i, priority_id, user_profile
            )
            if winner:
                category_winners[f'priority_{i+1}_{priority_id}'] = winner
        
        # 3. Build top 5 from all winners
        all_candidates = [best_overall] + list(category_winners.values())
        
        # 4. Ensure diversity
        top_5, replaced = self.ensure_diversity(
            all_candidates, scored_homes
        )
        
        # 5. Add ranking
        ranked_top_5 = []
        for rank, home_data in enumerate(top_5[:5], 1):
            home_data['rank'] = rank
            ranked_top_5.append(home_data)
        
        # 6. Calculate diversity metrics
        diversity_metrics = self._calculate_diversity_metrics(ranked_top_5)
        diversity_metrics['homes_replaced'] = replaced
        
        logger.info(
            f"✅ Top 5 selected: {replaced} homes replaced for diversity, "
            f"{diversity_metrics['unique_providers']} providers, "
            f"{diversity_metrics['unique_locations']} locations"
        )
        
        return {
            'top_5': ranked_top_5,
            'category_winners': category_winners,
            'diversity_metrics': diversity_metrics
        }
    
    def _select_best_overall(self, scored_homes: List[Dict]) -> Dict[str, Any]:
        """Select home with highest match score"""
        if not scored_homes:
            return None
        
        best = max(scored_homes, key=lambda h: h.get('match_score', 0))
        
        return SelectionResult(
            home=best.get('home', best),
            rank=1,
            score=best.get('match_score', 0),
            category='best_overall',
            reasoning=['Highest overall match score'],
            is_automatic=True
        )
    
    def _select_best_medical_safety(self, scored_homes: List[Dict]) -> Dict[str, Any]:
        """Select home with best medical & safety scores"""
        if not scored_homes:
            return None
        
        def medical_safety_score(home_data):
            scores = home_data.get('category_scores', {})
            medical = scores.get('medical', 0) * 0.19
            safety = scores.get('safety', 0) * 0.16
            return medical + safety
        
        best = max(scored_homes, key=medical_safety_score)
        
        return SelectionResult(
            home=best.get('home', best),
            rank=2,
            score=best.get('match_score', 0),
            category='best_medical_safety',
            reasoning=[
                'Best medical capabilities',
                'Best safety standards'
            ],
            is_automatic=True
        )
    
    def _select_priority_winner(
        self,
        scored_homes: List[Dict],
        priority_index: int,
        priority_id: str,
        user_profile: Dict
    ) -> Optional[Dict[str, Any]]:
        """Select winner for specific user priority"""
        if not scored_homes or not priority_id:
            return None
        
        # Define scoring function per priority
        if priority_id == 'quality_reputation':
            def score_fn(h):
                scores = h.get('category_scores', {})
                return scores.get('cqc', 0) * 0.5 + scores.get('staff', 0) * 0.5
            reasoning = ['Best quality & reputation']
        
        elif priority_id == 'cost_financial':
            def score_fn(h):
                return h.get('category_scores', {}).get('financial', 0)
            reasoning = ['Best cost value & financial stability']
        
        elif priority_id == 'location_social':
            def score_fn(h):
                scores = h.get('category_scores', {})
                return scores.get('location', 0) * 0.5 + scores.get('social', 0) * 0.5
            reasoning = ['Best location & social activities']
        
        elif priority_id == 'comfort_amenities':
            def score_fn(h):
                return h.get('category_scores', {}).get('services', 0)
            reasoning = ['Best comfort & amenities']
        
        else:
            return None
        
        best = max(scored_homes, key=score_fn)
        
        return SelectionResult(
            home=best.get('home', best),
            rank=priority_index + 2,
            score=best.get('match_score', 0),
            category=f'priority_{priority_index + 1}_{priority_id}',
            reasoning=reasoning,
            is_automatic=True
        )
    
    def ensure_diversity(
        self,
        top_5_candidates: List[Dict],
        all_scored_homes: List[Dict]
    ) -> Tuple[List[Dict], int]:
        """
        Ensure diversity in top 5 by avoiding duplicate providers and locations.
        
        Args:
            top_5_candidates: Initial top 5 candidates
            all_scored_homes: All scored homes for finding alternatives
        
        Returns:
            (diverse_top_5, count_of_replaced_homes)
        """
        if len(top_5_candidates) < 2:
            return top_5_candidates, 0
        
        diverse_homes = []
        used_providers = set()
        used_locations = set()
        replaced_count = 0
        
        # First pass: add homes with unique providers and locations
        for home_data in top_5_candidates:
            provider_id = self._get_provider_id(home_data)
            location_id = self._get_location_id(home_data)
            
            provider_duplicate = provider_id and provider_id in used_providers
            location_duplicate = location_id and location_id in used_locations
            
            if not provider_duplicate and not location_duplicate:
                diverse_homes.append(home_data)
                if provider_id:
                    used_providers.add(provider_id)
                if location_id:
                    used_locations.add(location_id)
            
            elif len(diverse_homes) < 5:
                # Try to find alternative
                alternative = self._find_diverse_alternative(
                    home_data, all_scored_homes, used_providers, used_locations, diverse_homes
                )
                
                if alternative:
                    diverse_homes.append(alternative)
                    replaced_count += 1
                    
                    alt_provider = self._get_provider_id(alternative)
                    alt_location = self._get_location_id(alternative)
                    
                    if alt_provider:
                        used_providers.add(alt_provider)
                    if alt_location:
                        used_locations.add(alt_location)
                else:
                    # No alternative found, add original
                    diverse_homes.append(home_data)
                    if provider_id:
                        used_providers.add(provider_id)
                    if location_id:
                        used_locations.add(location_id)
            
            if len(diverse_homes) >= 5:
                break
        
        # Fill remaining from all_scored_homes if needed
        if len(diverse_homes) < 5:
            for home_data in all_scored_homes:
                if home_data not in diverse_homes and len(diverse_homes) < 5:
                    provider_id = self._get_provider_id(home_data)
                    location_id = self._get_location_id(home_data)
                    
                    provider_dup = provider_id and provider_id in used_providers
                    location_dup = location_id and location_id in used_locations
                    
                    if not provider_dup or not location_dup:
                        diverse_homes.append(home_data)
                        if provider_id:
                            used_providers.add(provider_id)
                        if location_id:
                            used_locations.add(location_id)
        
        return diverse_homes[:5], replaced_count
    
    def _find_diverse_alternative(
        self,
        current_home: Dict,
        all_scored_homes: List[Dict],
        used_providers: Set[str],
        used_locations: Set[str],
        already_selected: List[Dict]
    ) -> Optional[Dict]:
        """Find alternative with similar score but different provider/location"""
        
        current_score = current_home.get('match_score', 0)
        
        for home_data in all_scored_homes:
            if home_data in already_selected or home_data == current_home:
                continue
            
            # Score within 10% of current
            alt_score = home_data.get('match_score', 0)
            if alt_score < current_score * 0.9:
                continue
            
            provider_id = self._get_provider_id(home_data)
            location_id = self._get_location_id(home_data)
            
            provider_dup = provider_id and provider_id in used_providers
            location_dup = location_id and location_id in used_locations
            
            # Return if adds diversity
            if not provider_dup or not location_dup:
                return home_data
        
        return None
    
    def _get_provider_id(self, home_data: Dict) -> Optional[str]:
        """Extract provider identifier"""
        home = home_data.get('home', {}) if 'home' in home_data else home_data
        
        provider_id = home.get('provider_id') or home.get('providerId')
        provider_name = home.get('provider_name') or home.get('providerName')
        
        if provider_id:
            return str(provider_id).lower().strip()
        if provider_name:
            return str(provider_name).lower().strip()
        
        return None
    
    def _get_location_id(self, home_data: Dict) -> Optional[str]:
        """Extract location identifier"""
        home = home_data.get('home', {}) if 'home' in home_data else home_data
        
        local_authority = home.get('local_authority') or home.get('localAuthority')
        city = home.get('city')
        postcode = home.get('postcode')
        
        if local_authority:
            return str(local_authority).lower().strip()
        if city:
            return str(city).lower().strip()
        if postcode:
            postcode_area = str(postcode).split()[0] if postcode else None
            if postcode_area:
                return postcode_area.lower().strip()
        
        return None
    
    def _calculate_diversity_metrics(
        self,
        homes: List[Dict]
    ) -> Dict[str, int]:
        """Calculate diversity metrics"""
        providers = set()
        locations = set()
        
        for home_data in homes:
            home = home_data.get('home', home_data)
            
            provider_id = self._get_provider_id(home_data)
            location_id = self._get_location_id(home_data)
            
            if provider_id:
                providers.add(provider_id)
            if location_id:
                locations.add(location_id)
        
        return {
            'unique_providers': len(providers),
            'unique_locations': len(locations),
            'homes_replaced': 0
        }

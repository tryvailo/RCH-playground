"""
Reasoning Generator - Generates human-readable explanations for home matches

Generates reasoning for:
- Best overall match
- Best medical & safety match
- Priority-based winners
- General quality explanations

Extracted from professional_matching_service.py to improve modularity.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ReasoningGenerator:
    """Generates human-readable reasoning for home selections"""
    
    def generate_reasoning(
        self,
        home: Dict[str, Any],
        category: str,
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any],
        home_data: Dict[str, Any]
    ) -> List[str]:
        """
        Generate reasoning for why this home was selected in this category.
        
        Args:
            home: Care home data
            category: Selection category ('best_overall', 'best_medical_safety', 'priority_*', etc)
            user_profile: User questionnaire
            enriched_data: Enriched data
            home_data: Full home data with scores
        
        Returns:
            List of reasoning strings
        """
        reasons = []
        category_scores = home_data.get('category_scores', {})
        
        if category == 'best_medical_safety':
            reasons = self._generate_medical_reasoning(
                home, user_profile, enriched_data, category_scores
            )
        elif category.startswith('priority_'):
            reasons = self._generate_priority_reasoning(
                home, category, user_profile, enriched_data, category_scores, home_data
            )
        elif category == 'best_overall':
            reasons = self._generate_overall_reasoning(
                home, user_profile, enriched_data, home_data
            )
        
        return reasons if reasons else ['Strong match across all criteria']
    
    def _generate_medical_reasoning(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any],
        category_scores: Dict[str, float]
    ) -> List[str]:
        """Generate reasoning for Best Medical & Safety"""
        reasons = []
        
        medical_score = category_scores.get('medical', 0)
        safety_score = category_scores.get('safety', 0)
        
        # Medical capabilities
        if medical_score >= 0.8:
            reasons.append("Excellent medical capabilities matching your needs")
        elif medical_score >= 0.6:
            reasons.append("Good medical support available")
        
        # Safety standards
        if safety_score >= 0.8:
            reasons.append("Outstanding safety measures and protocols")
        elif safety_score >= 0.6:
            reasons.append("Good safety standards")
        
        # Specialist care
        medical_conditions = user_profile.get('section_3_medical_needs', {}).get(
            'q9_medical_conditions', []
        )
        
        if 'dementia_alzheimers' in medical_conditions:
            home_care_types = str(home.get('care_types', [])).lower()
            if 'dementia' in home_care_types:
                reasons.append("Specialist dementia care available")
        
        # CQC Safe rating
        safe_rating = home.get('cqc_rating_safe') or enriched_data.get(
            'cqc_detailed', {}
        ).get('safe_rating')
        
        if safe_rating == 'Outstanding':
            reasons.append("Outstanding CQC Safe rating - highest safety standards")
        elif safe_rating == 'Good':
            reasons.append("Good CQC Safe rating - meets safety standards")
        
        return reasons
    
    def _generate_priority_reasoning(
        self,
        home: Dict[str, Any],
        category: str,
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any],
        category_scores: Dict[str, float],
        home_data: Dict[str, Any]
    ) -> List[str]:
        """Generate reasoning based on user priority"""
        reasons = []
        
        # Extract priority from category (e.g., 'priority_1_quality_reputation')
        try:
            priority_str = category.split('_')[2]  # 1, 2, 3, or 4
            priority_idx = int(priority_str) - 1
            
            priorities = user_profile.get('section_6_priorities', {}).get(
                'q18_priority_ranking', {}
            )
            priority_order = priorities.get('priority_order', [])
            
            if priority_idx < len(priority_order):
                priority_id = priority_order[priority_idx]
                
                if priority_id == 'quality_reputation':
                    reasons = self._generate_quality_reasoning(
                        home, enriched_data, category_scores
                    )
                elif priority_id == 'cost_financial':
                    reasons = self._generate_cost_reasoning(
                        home, user_profile, home_data, enriched_data
                    )
                elif priority_id == 'location_social':
                    reasons = self._generate_location_reasoning(
                        home, user_profile, category_scores
                    )
                elif priority_id == 'comfort_amenities':
                    reasons = self._generate_comfort_reasoning(
                        home, category_scores
                    )
        except (ValueError, IndexError):
            pass
        
        return reasons
    
    def _generate_quality_reasoning(
        self,
        home: Dict[str, Any],
        enriched_data: Dict[str, Any],
        category_scores: Dict[str, float]
    ) -> List[str]:
        """Generate reasoning for Best Quality & Reputation"""
        reasons = []
        
        # CQC Overall rating
        cqc_rating = (
            home.get('rating') or
            home.get('overall_rating') or
            enriched_data.get('cqc_detailed', {}).get('overall_rating')
        )
        
        if cqc_rating == 'Outstanding':
            reasons.append("Outstanding CQC rating - recognised excellence")
        elif cqc_rating == 'Good':
            reasons.append("Good CQC rating - reliable care standards")
        
        # Staff quality
        staff_score = category_scores.get('staff', 0)
        if staff_score >= 0.8:
            reasons.append("Excellent staff quality and stability")
        elif staff_score >= 0.7:
            reasons.append("Good staff quality and retention")
        
        # Google reviews
        google_rating = home.get('google_rating')
        review_count = home.get('review_count') or home.get('user_ratings_total', 0)
        
        if google_rating and google_rating >= 4.5:
            reasons.append(f"Exceptional reviews - {google_rating:.1f} stars from {review_count} families")
        elif google_rating and google_rating >= 4.0:
            reasons.append(f"Positive reviews - {google_rating:.1f} stars")
        
        return reasons
    
    def _generate_cost_reasoning(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        home_data: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> List[str]:
        """Generate reasoning for Best Cost & Financial"""
        reasons = []
        
        # Price
        try:
            from utils.price_extractor import extract_weekly_price
            price = extract_weekly_price(home)
        except:
            price = home.get('weekly_price') or home.get('price_weekly')
        
        price = float(price) if price else 0
        
        if price <= 0:
            return reasons
        
        # Budget
        location_budget = user_profile.get('section_2_location_budget', {})
        budget = location_budget.get('q7_budget', '')
        
        # Budget ranges
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
        
        if price <= max_budget:
            if price <= min_budget * 0.8:
                reasons.append("Within budget - affordable pricing")
            elif price <= min_budget:
                reasons.append("Within budget - good value")
            else:
                reasons.append("Within your budget range")
        elif price <= max_budget * 1.1:
            reasons.append("Slightly over budget but manageable")
        
        # Value ratio
        value_ratio = home_data.get('value_ratio', 0)
        if value_ratio > 1.5:
            reasons.append("Excellent quality-to-price ratio")
        elif value_ratio > 1.0:
            reasons.append("Good value for money")
        
        # Financial stability
        financial_score = home_data.get('category_scores', {}).get('financial', 0)
        if financial_score >= 0.8:
            reasons.append("Strong financial stability - reliable provider")
        
        return reasons
    
    def _generate_location_reasoning(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        category_scores: Dict[str, float]
    ) -> List[str]:
        """Generate reasoning for Best Location & Social"""
        reasons = []
        
        # Distance
        distance_km = home.get('distance_km')
        if distance_km is not None:
            if distance_km <= 5:
                reasons.append("Very close to your preferred location (within 5km)")
            elif distance_km <= 15:
                reasons.append("Convenient location (within 15km)")
        
        # Location accessibility
        location_score = category_scores.get('location', 0)
        if location_score >= 0.8:
            reasons.append("Excellent location and accessibility")
        
        # Social activities
        social_score = category_scores.get('social', 0)
        if social_score >= 0.8:
            reasons.append("Wide range of social activities and programs")
        elif social_score >= 0.6:
            reasons.append("Good variety of social activities")
        
        return reasons
    
    def _generate_comfort_reasoning(
        self,
        home: Dict[str, Any],
        category_scores: Dict[str, float]
    ) -> List[str]:
        """Generate reasoning for Best Comfort & Amenities"""
        reasons = []
        
        services_score = category_scores.get('services', 0)
        if services_score >= 0.7:
            reasons.append("Modern facilities and comfortable living spaces")
        
        # Additional services
        services = home.get('additional_services', [])
        if isinstance(services, str):
            services = [services]
        
        if len(services) >= 3:
            reasons.append("Comprehensive range of additional services")
        
        return reasons
    
    def _generate_overall_reasoning(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any],
        home_data: Dict[str, Any]
    ) -> List[str]:
        """Generate reasoning for Best Overall Match"""
        reasons = []
        
        match_score = home_data.get('match_score', 0)
        if match_score >= 120:
            reasons.append("Highest overall match score - best fit for your needs")
        
        # User priorities alignment
        priorities = user_profile.get('section_6_priorities', {}).get(
            'q18_priority_ranking', {}
        )
        priority_order = priorities.get('priority_order', [])
        
        if priority_order:
            priority_labels = {
                'quality_reputation': 'Quality & Reputation',
                'cost_financial': 'Cost & Financial Stability',
                'location_social': 'Location & Social',
                'comfort_amenities': 'Comfort & Amenities'
            }
            
            top_priority = priority_order[0]
            label = priority_labels.get(top_priority, top_priority)
            reasons.append(f"Best alignment with your top priority: {label}")
        
        return reasons

"""
Comparative Analysis Service
Generates side-by-side comparison of top 5 care homes with match scores,
price comparison, and key differentiators for Professional Report
"""
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


def _safe_float_convert(value: Union[str, int, float, None]) -> float:
    """
    Safely convert a value to float, handling strings that may contain text.
    
    Args:
        value: Value to convert (can be string, int, float, or None)
        
    Returns:
        Float value if conversion successful, 0.0 otherwise
    """
    if value is None:
        return 0.0
    
    # If already a number, return it
    if isinstance(value, (int, float)):
        return float(value)
    
    # If string, try to extract number
    if isinstance(value, str):
        # Try direct conversion first
        try:
            return float(value.strip())
        except (ValueError, TypeError):
            pass
        
        # Try to extract number from string (e.g., "Waived fees or 2" -> 2)
        match = re.search(r'(\d+\.?\d*)', value)
        if match:
            try:
                return float(match.group(1))
            except (ValueError, TypeError):
                pass
    
    return 0.0


class ComparativeAnalysisService:
    """Service for generating comparative analysis of care homes"""
    
    def generate_comparative_analysis(
        self,
        care_homes: List[Dict[str, Any]],
        questionnaire: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive comparative analysis of top 5 care homes
        
        Args:
            care_homes: List of care homes (already sorted by match score)
            questionnaire: Professional questionnaire response
        
        Returns:
            Dict with comparative analysis including:
            - Side-by-side comparison table
            - Match score rankings
            - Price comparison
            - Key differentiators
        """
        # Take top 5 homes
        top_5_homes = care_homes[:5] if len(care_homes) >= 5 else care_homes
        
        if not top_5_homes:
            # Return empty structure with proper nested objects to prevent frontend errors
            return {
                'error': 'No care homes available for comparison',
                'comparison_table': [],
                'rankings': {
                    'rankings': [],
                    'statistics': {
                        'highest_score': 0,
                        'lowest_score': 0,
                        'average_score': 0,
                        'score_range': 0,
                        'score_variance': 0
                    },
                    'tier_analysis': {}
                },
                'price_comparison': {
                    'comparison': [],
                    'sorted_by_price': [],
                    'statistics': {
                        'highest_weekly': 0,
                        'lowest_weekly': 0,
                        'average_weekly': 0,
                        'price_range': 0,
                        'highest_annual': 0,
                        'lowest_annual': 0,
                        'average_annual': 0
                    },
                    'best_value': None
                },
                'key_differentiators': [],
                'summary': {
                    'total_homes_compared': 0,
                    'match_score_range': 0,
                    'price_range_weekly': 0,
                    'price_range_annual': 0,
                    'recommendation': 'No care homes available for comparison'
                },
                'generated_at': datetime.now().isoformat()
            }
        
        # Generate comparison table
        comparison_table = self._generate_comparison_table(top_5_homes, questionnaire)
        
        # Generate match score rankings
        rankings = self._generate_match_score_rankings(top_5_homes)
        
        # Generate price comparison
        price_comparison = self._generate_price_comparison(top_5_homes)
        
        # Generate key differentiators
        key_differentiators = self._identify_key_differentiators(top_5_homes, questionnaire)
        
        return {
            'comparison_table': comparison_table,
            'rankings': rankings,
            'price_comparison': price_comparison,
            'key_differentiators': key_differentiators,
            'summary': self._generate_comparison_summary(top_5_homes, rankings, price_comparison),
            'generated_at': datetime.now().isoformat()
        }
    
    def _generate_comparison_table(
        self,
        homes: List[Dict[str, Any]],
        questionnaire: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate side-by-side comparison table for 5 homes"""
        comparison_rows = []
        
        # Extract client needs for comparison
        medical_needs = questionnaire.get('section_3_medical_needs', {})
        care_types = medical_needs.get('q8_care_types', [])
        conditions = medical_needs.get('q9_medical_conditions', [])
        
        # Row 1: Basic Information
        comparison_rows.append({
            'category': 'Basic Information',
            'metric': 'Name',
            'homes': {f'home_{i+1}': {
                'value': home.get('name', 'N/A'),
                'highlight': False
            } for i, home in enumerate(homes)}
        })
        
        comparison_rows.append({
            'category': 'Basic Information',
            'metric': 'Location',
            'homes': {f'home_{i+1}': {
                'value': home.get('location', 'N/A'),
                'highlight': False
            } for i, home in enumerate(homes)}
        })
        
        comparison_rows.append({
            'category': 'Basic Information',
            'metric': 'Distance',
            'homes': {f'home_{i+1}': {
                'value': home.get('distance', 'N/A'),
                'highlight': False,
                'sort_value': self._extract_distance_value(home.get('distance', ''))
            } for i, home in enumerate(homes)}
        })
        
        comparison_rows.append({
            'category': 'Basic Information',
            'metric': 'Postcode',
            'homes': {f'home_{i+1}': {
                'value': home.get('postcode', 'N/A'),
                'highlight': False
            } for i, home in enumerate(homes)}
        })
        
        # Row 2: Match Scores
        comparison_rows.append({
            'category': 'Match Score',
            'metric': 'Overall Match Score',
            'homes': {f'home_{i+1}': {
                'value': f"{home.get('matchScore', 0)}%",
                'highlight': True,
                'sort_value': home.get('matchScore', 0),
                'badge': self._get_match_score_badge(home.get('matchScore', 0))
            } for i, home in enumerate(homes)}
        })
        
        # Row 3: Factor Scores Breakdown
        if homes[0].get('factorScores'):
            factor_categories = [
                'Medical Capabilities', 'Safety & Quality', 'Location & Access',
                'Cultural & Social', 'Financial Stability', 'Staff Quality',
                'CQC Compliance', 'Additional Services'
            ]
            
            for category in factor_categories:
                comparison_rows.append({
                    'category': 'Factor Scores',
                    'metric': category,
                    'homes': {f'home_{i+1}': {
                        'value': self._get_factor_score(home, category),
                        'highlight': False,
                        'sort_value': self._get_factor_score_value(home, category)
                    } for i, home in enumerate(homes)}
                })
        
        # Row 4: CQC Ratings
        comparison_rows.append({
            'category': 'CQC Ratings',
            'metric': 'Overall Rating',
            'homes': {f'home_{i+1}': {
                'value': home.get('cqcRating', 'N/A'),
                'highlight': True,
                'badge': self._get_cqc_badge(home.get('cqcRating', ''))
            } for i, home in enumerate(homes)}
        })
        
        # Add detailed CQC ratings if available
        if homes[0].get('cqcDeepDive') and homes[0]['cqcDeepDive'].get('detailed_ratings'):
            detailed_ratings = ['Safe', 'Effective', 'Caring', 'Responsive', 'Well-led']
            for rating in detailed_ratings:
                comparison_rows.append({
                    'category': 'CQC Ratings',
                    'metric': rating,
                    'homes': {f'home_{i+1}': {
                        'value': self._get_detailed_cqc_rating(home, rating),
                        'highlight': False
                    } for i, home in enumerate(homes)}
                })
        
        # Row 5: Pricing
        comparison_rows.append({
            'category': 'Pricing',
            'metric': 'Weekly Price',
            'homes': {f'home_{i+1}': {
                'value': f"£{_safe_float_convert(home.get('weeklyPrice', 0)):,.0f}",
                'highlight': True,
                'sort_value': _safe_float_convert(home.get('weeklyPrice', 0))
            } for i, home in enumerate(homes)}
        })
        
        comparison_rows.append({
            'category': 'Pricing',
            'metric': 'Annual Cost',
            'homes': {f'home_{i+1}': {
                'value': f"£{(home.get('weeklyPrice', 0) * 52):,.0f}",
                'highlight': False,
                'sort_value': home.get('weeklyPrice', 0) * 52
            } for i, home in enumerate(homes)}
        })
        
        # Row 6: Financial Stability
        for i, home in enumerate(homes):
            financial = home.get('financialStability')
            if financial:
                comparison_rows.append({
                    'category': 'Financial Stability',
                    'metric': 'Altman Z-Score',
                    'homes': {f'home_{j+1}': {
                        'value': self._format_financial_metric(homes[j].get('financialStability', {}).get('altman_z_score')),
                        'highlight': False,
                        'sort_value': homes[j].get('financialStability', {}).get('altman_z_score')
                    } for j in range(len(homes))}
                })
                
                comparison_rows.append({
                    'category': 'Financial Stability',
                    'metric': 'Bankruptcy Risk',
                    'homes': {f'home_{j+1}': {
                        'value': self._format_bankruptcy_risk(homes[j].get('financialStability', {}).get('bankruptcy_risk_score')),
                        'highlight': True,
                        'badge': self._get_bankruptcy_risk_badge(homes[j].get('financialStability', {}).get('bankruptcy_risk_score'))
                    } for j in range(len(homes))}
                }
                )
                break
        
        # Row 7: FSA Ratings
        comparison_rows.append({
            'category': 'Food Safety',
            'metric': 'FSA Rating',
            'homes': {f'home_{i+1}': {
                'value': self._get_fsa_rating(home),
                'highlight': False
            } for i, home in enumerate(homes)}
        })
        
        # Row 8: Google Places
        comparison_rows.append({
            'category': 'Reviews',
            'metric': 'Google Rating',
            'homes': {f'home_{i+1}': {
                'value': self._get_google_rating(home),
                'highlight': False
            } for i, home in enumerate(homes)}
        })
        
        comparison_rows.append({
            'category': 'Reviews',
            'metric': 'Review Count',
            'homes': {f'home_{i+1}': {
                'value': self._get_review_count(home),
                'highlight': False
            } for i, home in enumerate(homes)}
        })
        
        # Row 9: Key Strengths
        comparison_rows.append({
            'category': 'Highlights',
            'metric': 'Key Strengths',
            'homes': {f'home_{i+1}': {
                'value': ', '.join(home.get('keyStrengths', [])[:3]) or 'N/A',
                'highlight': False,
                'is_list': True
            } for i, home in enumerate(homes)}
        })
        
        return comparison_rows
    
    def _generate_match_score_rankings(self, homes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate match score rankings analysis"""
        if not homes:
            # Return empty structure with default statistics to prevent frontend errors
            return {
                'rankings': [],
                'statistics': {
                    'highest_score': 0,
                    'lowest_score': 0,
                    'average_score': 0,
                    'score_range': 0,
                    'score_variance': 0
                },
                'tier_analysis': {}
            }
        
        scores = [home.get('matchScore', 0) for home in homes]
        max_score = max(scores) if scores else 0
        min_score = min(scores) if scores else 0
        avg_score = sum(scores) / len(scores) if scores else 0
        
        rankings = []
        for i, home in enumerate(homes):
            score = home.get('matchScore', 0)
            rankings.append({
                'rank': i + 1,
                'home_id': home.get('id'),
                'home_name': home.get('name'),
                'match_score': score,
                'score_difference_from_top': max_score - score if max_score > 0 else 0,
                'percentile': ((len(homes) - i) / len(homes) * 100) if len(homes) > 0 else 0
            })
        
        return {
            'rankings': rankings,
            'statistics': {
                'highest_score': max_score,
                'lowest_score': min_score,
                'average_score': round(avg_score, 1),
                'score_range': round(max_score - min_score, 1),
                'score_variance': round(sum((s - avg_score) ** 2 for s in scores) / len(scores), 1) if scores else 0
            },
            'tier_analysis': self._analyze_score_tiers(rankings)
        }
    
    def _generate_price_comparison(self, homes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate price comparison analysis"""
        if not homes:
            return {}
        
        # Safely extract prices, filtering out None and non-numeric values
        prices = []
        for home in homes:
            price = home.get('weeklyPrice', 0)
            if price is not None:
                try:
                    price_float = _safe_float_convert(price)
                    if price_float and price_float > 0:
                        prices.append(price_float)
                except (ValueError, TypeError):
                    pass
        valid_prices = prices
        
        if not valid_prices:
            # Return empty structure with default statistics to prevent frontend errors
            return {
                'comparison': [],
                'sorted_by_price': [],
                'statistics': {
                    'highest_weekly': 0,
                    'lowest_weekly': 0,
                    'average_weekly': 0,
                    'price_range': 0,
                    'highest_annual': 0,
                    'lowest_annual': 0,
                    'average_annual': 0
                },
                'best_value': None,
                'error': 'No valid prices available'
            }
        
        max_price = max(valid_prices)
        min_price = min(valid_prices)
        avg_price = sum(valid_prices) / len(valid_prices)
        
        price_comparison = []
        for i, home in enumerate(homes):
            price_raw = home.get('weeklyPrice', 0)
            price = _safe_float_convert(price_raw) if price_raw is not None else 0.0
            annual_price = price * 52 if price > 0 else 0.0
            price_comparison.append({
                'rank': i + 1,
                'home_id': home.get('id'),
                'home_name': home.get('name'),
                'weekly_price': price,
                'annual_price': annual_price,
                'price_difference_from_lowest': price - min_price if min_price > 0 and price > 0 else 0,
                'price_percent_difference': ((price - min_price) / min_price * 100) if min_price > 0 and price > 0 else 0,
                'value_score': self._calculate_value_score(home, price, avg_price)
            })
        
        # Sort by price (ascending)
        price_comparison_sorted = sorted(price_comparison, key=lambda x: x['weekly_price'])
        
        return {
            'comparison': price_comparison,
            'sorted_by_price': price_comparison_sorted,
            'statistics': {
                'highest_weekly': max_price,
                'lowest_weekly': min_price,
                'average_weekly': round(avg_price, 2),
                'price_range': round(max_price - min_price, 2),
                'highest_annual': max_price * 52,
                'lowest_annual': min_price * 52,
                'average_annual': round(avg_price * 52, 2)
            },
            'best_value': self._identify_best_value(homes, price_comparison)
    }
    
    def _identify_key_differentiators(
        self,
        homes: List[Dict[str, Any]],
        questionnaire: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify key differentiators between homes"""
        differentiators = []
        
        if len(homes) < 2:
            return differentiators
        
        # 1. Match Score Differentiators
        # Safely extract scores, filtering out None values
        scores = []
        for home in homes:
            score = home.get('matchScore', 0)
            if score is not None:
                try:
                    score_float = float(score)
                    scores.append(score_float)
                except (ValueError, TypeError):
                    scores.append(0.0)
            else:
                scores.append(0.0)
        
        if not scores or max(scores) == 0:
            return differentiators
        
        max_score_idx = scores.index(max(scores))
        differentiators.append({
            'type': 'match_score',
            'title': 'Highest Match Score',
            'description': f"{homes[max_score_idx].get('name')} has the highest match score ({max(scores)}%)",
            'home_name': homes[max_score_idx].get('name'),
            'value': max(scores),
            'importance': 'high'
        })
        
        # 2. Price Differentiators
        # Safely extract prices, filtering out None and non-numeric values
        prices = []
        home_prices_map = {}  # Map home index to price
        for i, home in enumerate(homes):
            price = home.get('weeklyPrice', 0)
            if price is not None:
                try:
                    price_float = _safe_float_convert(price)
                    if price_float and price_float > 0:
                        prices.append(price_float)
                        home_prices_map[i] = price_float
                except (ValueError, TypeError):
                    pass
        if prices:
            min_price = min(prices)
            max_price = max(prices)
            min_price_idx = next((i for i, price in home_prices_map.items() if price == min_price), None)
            max_price_idx = next((i for i, price in home_prices_map.items() if price == max_price), None)
            
            if min_price_idx is not None:
                differentiators.append({
                    'type': 'price',
                    'title': 'Most Affordable',
                    'description': f"{homes[min_price_idx].get('name')} offers the lowest weekly price (£{min(prices):,.0f})",
                    'home_name': homes[min_price_idx].get('name'),
                    'value': min(prices),
                    'importance': 'high'
                })
            
            if max_price_idx is not None and max_price_idx != min_price_idx:
                differentiators.append({
                    'type': 'price',
                    'title': 'Premium Option',
                    'description': f"{homes[max_price_idx].get('name')} is the most expensive (£{max(prices):,.0f}/week)",
                    'home_name': homes[max_price_idx].get('name'),
                    'value': max(prices),
                    'importance': 'medium'
                })
        
        # 3. CQC Rating Differentiators
        cqc_ratings = {}
        for home in homes:
            rating = home.get('cqcRating', '')
            if rating and rating not in ['N/A', '']:
                if rating not in cqc_ratings:
                    cqc_ratings[rating] = []
                cqc_ratings[rating].append(home.get('name'))
        
        if 'Outstanding' in cqc_ratings:
            differentiators.append({
                'type': 'cqc',
                'title': 'Outstanding CQC Rating',
                'description': f"{', '.join(cqc_ratings['Outstanding'])} has/have Outstanding CQC rating",
                'home_name': ', '.join(cqc_ratings['Outstanding']),
                'value': 'Outstanding',
                'importance': 'high'
            })
        
        # 4. Financial Stability Differentiators
        financial_scores = []
        for home in homes:
            financial = home.get('financialStability')
            if financial and financial.get('altman_z_score') is not None:
                financial_scores.append({
                    'home': home.get('name'),
                    'altman_z': financial.get('altman_z_score'),
                    'risk_score': financial.get('bankruptcy_risk_score')
                })
        
        if financial_scores:
            best_financial = max(financial_scores, key=lambda x: x.get('altman_z', 0))
            worst_financial = min(financial_scores, key=lambda x: x.get('altman_z', float('inf')))
            
            # Ensure altman_z is a number
            best_altman_z = best_financial.get('altman_z')
            try:
                best_altman_z = float(best_altman_z) if best_altman_z is not None else 0.0
            except (ValueError, TypeError):
                best_altman_z = 0.0
            
            if best_altman_z > 2.99:  # Safe zone
                differentiators.append({
                    'type': 'financial',
                    'title': 'Strongest Financial Stability',
                    'description': f"{best_financial['home']} has the strongest financial position (Altman Z: {best_altman_z:.2f})",
                    'home_name': best_financial['home'],
                    'value': best_altman_z,
                    'importance': 'high'
                })
        
        # 5. Distance Differentiators
        distances = []
        for home in homes:
            distance_str = home.get('distance', '')
            distance_value = self._extract_distance_value(distance_str)
            if distance_value:
                distances.append({
                    'home': home.get('name'),
                    'distance': distance_value,
                    'distance_str': distance_str
                })
        
        if distances:
            closest = min(distances, key=lambda x: x['distance'])
            differentiators.append({
                'type': 'location',
                'title': 'Closest Location',
                'description': f"{closest['home']} is the closest ({closest['distance_str']})",
                'home_name': closest['home'],
                'value': closest['distance_str'],
                'importance': 'medium'
            })
        
        # 6. Factor Score Differentiators
        medical_scores = []
        for home in homes:
            factor_scores = home.get('factorScores', [])
            medical_score = next((fs for fs in factor_scores if fs.get('category') == 'Medical Capabilities'), None)
            if medical_score:
                medical_scores.append({
                    'home': home.get('name'),
                    'score': medical_score.get('score', 0),
                    'max_score': medical_score.get('maxScore', 30)
                })
        
        if medical_scores:
            best_medical = max(medical_scores, key=lambda x: x['score'])
            differentiators.append({
                'type': 'medical',
                'title': 'Best Medical Capabilities',
                'description': f"{best_medical['home']} scores highest for medical capabilities ({best_medical['score']}/{best_medical['max_score']})",
                'home_name': best_medical['home'],
                'value': f"{best_medical['score']}/{best_medical['max_score']}",
                'importance': 'high'
            })
        
        return differentiators
    
    def _generate_comparison_summary(
        self,
        homes: List[Dict[str, Any]],
        rankings: Dict[str, Any],
        price_comparison: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate overall comparison summary"""
        return {
            'total_homes_compared': len(homes),
            'match_score_range': rankings.get('statistics', {}).get('score_range', 0),
            'price_range_weekly': price_comparison.get('statistics', {}).get('price_range', 0),
            'price_range_annual': price_comparison.get('statistics', {}).get('price_range', 0) * 52,
            'recommendation': self._generate_recommendation(homes, rankings, price_comparison)
        }
    
    # Helper methods
    def _extract_distance_value(self, distance_str: str) -> Optional[float]:
        """Extract numeric distance value from string like '5.2 miles'"""
        if not distance_str:
            return None
        try:
            import re
            match = re.search(r'(\d+\.?\d*)', distance_str)
            if match:
                return float(match.group(1))
        except:
            pass
        return None
    
    def _get_match_score_badge(self, score: float) -> str:
        """Get badge color for match score"""
        if score >= 90:
            return 'excellent'
        elif score >= 80:
            return 'very_good'
        elif score >= 70:
            return 'good'
        elif score >= 60:
            return 'fair'
        else:
            return 'poor'
    
    def _get_cqc_badge(self, rating: str) -> str:
        """Get badge type for CQC rating"""
        rating_lower = rating.lower()
        if 'outstanding' in rating_lower:
            return 'excellent'
        elif 'good' in rating_lower:
            return 'good'
        elif 'requires improvement' in rating_lower:
            return 'warning'
        elif 'inadequate' in rating_lower:
            return 'poor'
        return 'unknown'
    
    def _get_bankruptcy_risk_badge(self, risk_score: Optional[float]) -> str:
        """Get badge for bankruptcy risk score"""
        if risk_score is None:
            return 'unknown'
        if risk_score >= 60:
            return 'high_risk'
        elif risk_score >= 40:
            return 'medium_risk'
        else:
            return 'low_risk'
    
    def _get_factor_score(self, home: Dict[str, Any], category: str) -> str:
        """Get factor score for a category"""
        factor_scores = home.get('factorScores', [])
        score_obj = next((fs for fs in factor_scores if fs.get('category') == category), None)
        if score_obj:
            score = score_obj.get('score', 0)
            max_score = score_obj.get('maxScore', 0)
            # Round to 2 decimal places to avoid floating point precision issues
            return f"{round(score, 2)}/{int(max_score)}"
        return 'N/A'
    
    def _get_factor_score_value(self, home: Dict[str, Any], category: str) -> float:
        """Get numeric factor score value for sorting"""
        factor_scores = home.get('factorScores', [])
        score_obj = next((fs for fs in factor_scores if fs.get('category') == category), None)
        if score_obj:
            max_score = score_obj.get('maxScore', 1)
            score = score_obj.get('score', 0)
            return (score / max_score * 100) if max_score > 0 else 0
        return 0
    
    def _get_detailed_cqc_rating(self, home: Dict[str, Any], rating_type: str) -> str:
        """Get detailed CQC rating"""
        cqc_deep_dive = home.get('cqcDeepDive')
        if cqc_deep_dive and cqc_deep_dive.get('detailed_ratings'):
            detailed = cqc_deep_dive['detailed_ratings']
            rating_key = rating_type.lower().replace('-', '_')
            rating_obj = detailed.get(rating_key)
            if rating_obj:
                return rating_obj.get('rating', 'N/A')
        return 'N/A'
    
    def _format_financial_metric(self, value: Optional[float]) -> str:
        """Format financial metric"""
        if value is None:
            return 'N/A'
        return f"{value:.2f}"
    
    def _format_bankruptcy_risk(self, risk_score: Optional[float]) -> str:
        """Format bankruptcy risk score"""
        if risk_score is None:
            return 'N/A'
        return f"{risk_score:.0f}/100"
    
    def _get_fsa_rating(self, home: Dict[str, Any]) -> str:
        """Get FSA rating"""
        fsa = home.get('fsaDetailed')
        if fsa and fsa.get('rating'):
            rating = fsa['rating']
            return str(rating) if rating else 'N/A'
        return 'N/A'
    
    def _get_google_rating(self, home: Dict[str, Any]) -> str:
        """Get Google Places rating"""
        google = home.get('googlePlaces')
        if google and google.get('rating') is not None:
            return f"{google['rating']}/5"
        return 'N/A'
    
    def _get_review_count(self, home: Dict[str, Any]) -> str:
        """Get review count"""
        google = home.get('googlePlaces')
        if google and google.get('user_ratings_total') is not None:
            return str(google['user_ratings_total'])
        return 'N/A'
    
    def _calculate_value_score(self, home: Dict[str, Any], price: float, avg_price: float) -> float:
        """Calculate value score (match score / price ratio)"""
        match_score_raw = home.get('matchScore', 0)
        match_score = float(match_score_raw) if match_score_raw is not None else 0.0
        
        # Ensure price is a number
        try:
            price = float(price) if price is not None else 0.0
        except (ValueError, TypeError):
            price = 0.0
        
        if price > 0 and match_score > 0:
            # Higher match score and lower price = better value
            value_score = (match_score / price) * 1000  # Scale for readability
            return round(value_score, 2)
        return 0
    
    def _identify_best_value(self, homes: List[Dict[str, Any]], price_comparison: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Identify best value home (best match score to price ratio)"""
        if not price_comparison:
            return None
        
        best_value = max(price_comparison, key=lambda x: x.get('value_score', 0))
        return {
            'home_id': best_value.get('home_id'),
            'home_name': best_value.get('home_name'),
            'value_score': best_value.get('value_score', 0),
            'match_score': next((h.get('matchScore', 0) for h in homes if h.get('id') == best_value.get('home_id')), 0),
            'weekly_price': best_value.get('weekly_price', 0)
        }
    
    def _analyze_score_tiers(self, rankings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze match scores into tiers"""
        if not rankings:
            return {}
        
        # Safely extract scores, filtering out None values
        scores = []
        for r in rankings:
            score = r.get('match_score', 0)
            if score is not None:
                try:
                    score_float = float(score)
                    scores.append(score_float)
                except (ValueError, TypeError):
                    scores.append(0.0)
            else:
                scores.append(0.0)
        
        # Safely filter rankings by score tiers
        tier_1 = []
        tier_2 = []
        tier_3 = []
        tier_4 = []
        for r in rankings:
            score = r.get('match_score', 0)
            try:
                score_float = float(score) if score is not None else 0.0
            except (ValueError, TypeError):
                score_float = 0.0
            
            if score_float >= 90:
                tier_1.append(r)
            elif 80 <= score_float < 90:
                tier_2.append(r)
            elif 70 <= score_float < 80:
                tier_3.append(r)
            elif score_float < 70:
                tier_4.append(r)
        
        return {
            'tier_1_excellent': {
                'count': len(tier_1),
                'homes': [r['home_name'] for r in tier_1],
                'range': '90-100%'
            },
            'tier_2_very_good': {
                'count': len(tier_2),
                'homes': [r['home_name'] for r in tier_2],
                'range': '80-89%'
            },
            'tier_3_good': {
                'count': len(tier_3),
                'homes': [r['home_name'] for r in tier_3],
                'range': '70-79%'
            },
            'tier_4_fair': {
                'count': len(tier_4),
                'homes': [r['home_name'] for r in tier_4],
                'range': '<70%'
            }
        }
    
    def _generate_recommendation(
        self,
        homes: List[Dict[str, Any]],
        rankings: Dict[str, Any],
        price_comparison: Dict[str, Any]
    ) -> str:
        """Generate overall recommendation"""
        if not homes:
            return "No homes available for comparison"
        
        top_home = homes[0]  # Already sorted by match score
        top_score_raw = top_home.get('matchScore', 0)
        top_price_raw = top_home.get('weeklyPrice', 0)
        
        # Ensure top_score is a number
        try:
            top_score = float(top_score_raw) if top_score_raw is not None else 0.0
        except (ValueError, TypeError):
            top_score = 0.0
        
        # Ensure top_price is a number
        try:
            top_price = float(top_price_raw) if top_price_raw is not None else 0.0
        except (ValueError, TypeError):
            top_price = 0.0
        
        stats = rankings.get('statistics', {})
        price_stats = price_comparison.get('statistics', {})
        
        score_range_raw = stats.get('score_range', 0)
        price_range_raw = price_stats.get('price_range', 0)
        
        # Ensure score_range is a number
        try:
            score_range = float(score_range_raw) if score_range_raw is not None else 0.0
        except (ValueError, TypeError):
            score_range = 0.0
        
        # Ensure price_range is a number
        try:
            price_range = float(price_range_raw) if price_range_raw is not None else 0.0
        except (ValueError, TypeError):
            price_range = 0.0
        
        recommendation_parts = []
        
        if top_score >= 90:
            recommendation_parts.append(f"{top_home.get('name')} stands out with an excellent match score of {top_score}%")
        elif top_score >= 80:
            recommendation_parts.append(f"{top_home.get('name')} offers a very strong match at {top_score}%")
        else:
            recommendation_parts.append(f"{top_home.get('name')} is the top match with a score of {top_score}%")
        
        if score_range < 5:
            recommendation_parts.append("All homes have similar match scores, so other factors like price and location become more important")
        
        if price_range > 200:
            recommendation_parts.append(f"There's a significant price range (£{price_range:.0f}/week difference), so budget considerations are important")
        
        best_value = price_comparison.get('best_value')
        if best_value and best_value.get('home_name') != top_home.get('name'):
            recommendation_parts.append(f"For best value, consider {best_value.get('home_name')} which offers strong match score at a competitive price")
        
        return ". ".join(recommendation_parts) + "."


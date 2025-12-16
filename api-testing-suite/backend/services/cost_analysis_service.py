"""
Cost Analysis Service
Provides comprehensive cost analysis for care homes including:
- Hidden fees detection (scraping + estimates)
- 5-year projection calculator (enhanced)
- Cost vs Funding scenarios comparison
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


class CostAnalysisService:
    """Service for comprehensive cost analysis of care home placements"""
    
    # Hidden fees database - UK care home industry estimates (2024-2025)
    HIDDEN_FEES_DATABASE = {
        'admission_fee': {
            'display_name': 'Admission/Registration Fee',
            'description': 'One-time fee charged when moving in',
            'typical_range': [500, 2000],
            'average': 1000,
            'frequency': 'one_time',
            'commonality': 0.65,  # 65% of homes charge this
            'negotiable': True,
            'category': 'move_in'
        },
        'registration_fee': {
            'display_name': 'Registration/Assessment Fee',
            'description': 'Fee for initial care assessment',
            'typical_range': [100, 500],
            'average': 250,
            'frequency': 'one_time',
            'commonality': 0.45,
            'negotiable': True,
            'category': 'move_in'
        },
        'deposit': {
            'display_name': 'Security Deposit',
            'description': 'Refundable deposit for room and belongings',
            'typical_range': [500, 4000],
            'average': 2000,
            'frequency': 'one_time',
            'commonality': 0.80,
            'negotiable': False,
            'refundable': True,
            'category': 'move_in'
        },
        'top_up_fee': {
            'display_name': 'Top-Up Fee',
            'description': 'Additional fee for premium room or location',
            'typical_range': [50, 250],
            'average': 120,
            'frequency': 'weekly',
            'commonality': 0.55,
            'negotiable': True,
            'category': 'accommodation'
        },
        'personal_care_extras': {
            'display_name': 'Personal Care Extras',
            'description': 'Additional personal care beyond standard package',
            'typical_range': [30, 100],
            'average': 50,
            'frequency': 'weekly',
            'commonality': 0.40,
            'negotiable': False,
            'category': 'care'
        },
        'laundry_service': {
            'display_name': 'Laundry Service',
            'description': 'Washing and ironing personal clothing',
            'typical_range': [15, 45],
            'average': 25,
            'frequency': 'weekly',
            'commonality': 0.35,
            'negotiable': False,
            'included_sometimes': True,
            'category': 'services'
        },
        'hairdressing': {
            'display_name': 'Hairdressing',
            'description': 'Hair styling and grooming services',
            'typical_range': [25, 60],
            'average': 40,
            'frequency': 'monthly',
            'commonality': 0.90,
            'negotiable': False,
            'category': 'personal'
        },
        'chiropody': {
            'display_name': 'Chiropody/Podiatry',
            'description': 'Foot care services',
            'typical_range': [30, 50],
            'average': 40,
            'frequency': 'monthly',
            'commonality': 0.85,
            'negotiable': False,
            'category': 'personal'
        },
        'toiletries': {
            'display_name': 'Toiletries',
            'description': 'Soap, shampoo, toothpaste, etc.',
            'typical_range': [10, 30],
            'average': 15,
            'frequency': 'weekly',
            'commonality': 0.50,
            'negotiable': False,
            'included_sometimes': True,
            'category': 'personal'
        },
        'newspapers_magazines': {
            'display_name': 'Newspapers & Magazines',
            'description': 'Daily newspapers and magazine subscriptions',
            'typical_range': [15, 40],
            'average': 25,
            'frequency': 'weekly',
            'commonality': 0.60,
            'negotiable': False,
            'category': 'lifestyle'
        },
        'telephone': {
            'display_name': 'Telephone Line',
            'description': 'Private telephone line in room',
            'typical_range': [10, 25],
            'average': 15,
            'frequency': 'weekly',
            'commonality': 0.70,
            'negotiable': False,
            'category': 'services'
        },
        'tv_license': {
            'display_name': 'TV License',
            'description': 'BBC TV license fee',
            'typical_range': [3, 4],
            'average': 3.50,
            'frequency': 'weekly',
            'commonality': 0.95,
            'negotiable': False,
            'category': 'services'
        },
        'outings_transport': {
            'display_name': 'Outings & Transport',
            'description': 'Trips out and transportation costs',
            'typical_range': [40, 150],
            'average': 80,
            'frequency': 'monthly',
            'commonality': 0.75,
            'negotiable': False,
            'category': 'lifestyle'
        },
        'activities_entertainment': {
            'display_name': 'Activities & Entertainment',
            'description': 'Special activities and entertainment events',
            'typical_range': [20, 60],
            'average': 35,
            'frequency': 'monthly',
            'commonality': 0.40,
            'negotiable': False,
            'included_sometimes': True,
            'category': 'lifestyle'
        },
        'equipment_rental': {
            'display_name': 'Specialist Equipment',
            'description': 'Rental of mobility aids or specialist equipment',
            'typical_range': [20, 100],
            'average': 50,
            'frequency': 'weekly',
            'commonality': 0.30,
            'negotiable': False,
            'needs_based': True,
            'category': 'care'
        },
        'escorted_appointments': {
            'display_name': 'Escorted Appointments',
            'description': 'Staff escort to medical appointments',
            'typical_range': [15, 30],
            'average': 20,
            'frequency': 'per_occurrence',
            'commonality': 0.80,
            'negotiable': False,
            'category': 'care'
        },
        'continence_products': {
            'display_name': 'Continence Products',
            'description': 'Incontinence pads and supplies',
            'typical_range': [20, 50],
            'average': 30,
            'frequency': 'weekly',
            'commonality': 0.60,
            'negotiable': False,
            'needs_based': True,
            'included_sometimes': True,
            'category': 'care'
        },
        'respite_care_premium': {
            'display_name': 'Respite Care Premium',
            'description': 'Higher rate for short-term stays',
            'typical_range': [50, 200],
            'average': 100,
            'frequency': 'weekly',
            'commonality': 0.70,
            'negotiable': True,
            'category': 'accommodation'
        },
        'annual_fee_increase': {
            'display_name': 'Annual Fee Increase',
            'description': 'Typical annual price increase above inflation',
            'typical_range': [3, 8],
            'average': 5,
            'frequency': 'annual_percent',
            'commonality': 0.95,
            'negotiable': True,
            'category': 'pricing'
        }
    }
    
    # Fee categories for grouping
    FEE_CATEGORIES = {
        'move_in': {
            'display_name': 'Move-In Costs',
            'description': 'One-time costs when starting care',
            'icon': '🏠'
        },
        'accommodation': {
            'display_name': 'Accommodation Extras',
            'description': 'Additional room and lodging charges',
            'icon': '🛏️'
        },
        'care': {
            'display_name': 'Care-Related Costs',
            'description': 'Additional care and medical costs',
            'icon': '💊'
        },
        'services': {
            'display_name': 'Service Charges',
            'description': 'Utility and service fees',
            'icon': '📞'
        },
        'personal': {
            'display_name': 'Personal Care',
            'description': 'Grooming and personal items',
            'icon': '✂️'
        },
        'lifestyle': {
            'display_name': 'Lifestyle & Activities',
            'description': 'Entertainment and social activities',
            'icon': '🎭'
        },
        'pricing': {
            'display_name': 'Pricing Policies',
            'description': 'Fee increase and pricing terms',
            'icon': '📈'
        }
    }
    
    # Care type modifiers for hidden fees
    CARE_TYPE_MODIFIERS = {
        'residential': 1.0,
        'nursing': 1.15,  # 15% higher hidden fees
        'dementia': 1.25,  # 25% higher hidden fees
        'respite': 1.10   # 10% higher
    }
    
    # Regional price modifiers
    REGIONAL_MODIFIERS = {
        'london': 1.35,
        'south_east': 1.20,
        'south_west': 1.05,
        'east': 1.10,
        'west_midlands': 0.95,
        'east_midlands': 0.90,
        'yorkshire': 0.90,
        'north_west': 0.92,
        'north_east': 0.88,
        'wales': 0.90,
        'scotland': 0.95,
        'northern_ireland': 0.88
    }
    
    def __init__(self):
        self.inflation_rate = 0.04  # 4% annual inflation
    
    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """Safely convert value to float with fallback"""
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def _safe_int(self, value: Any, default: int = 0) -> int:
        """Safely convert value to int with fallback"""
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def _safe_get_nested(self, data: Dict, *keys, default: Any = None) -> Any:
        """Safely get nested dictionary value"""
        try:
            result = data
            for key in keys:
                if result is None:
                    return default
                if isinstance(result, dict):
                    result = result.get(key)
                else:
                    return default
            return result if result is not None else default
        except (KeyError, TypeError, AttributeError):
            return default
    
    def detect_hidden_fees(
        self,
        care_home: Dict[str, Any],
        care_type: str = 'residential',
        region: str = 'england',
        questionnaire: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Detect and estimate hidden fees for a care home
        
        Args:
            care_home: Care home data with name, price, location
            care_type: Type of care (residential, nursing, dementia, respite)
            region: UK region for price adjustment
            questionnaire: Optional questionnaire for needs-based fees
        
        Returns:
            Dict with detected hidden fees, estimates, and total impact
        """
        try:
            # Safely extract data with fallbacks
            if not care_home:
                care_home = {}
            
            weekly_price = self._safe_float(
                care_home.get('weeklyPrice') or care_home.get('weekly_price'), 
                default=0.0
            )
            home_name = care_home.get('name') or 'Unknown'
            home_id = care_home.get('id') or ''
            
            # Get modifiers
            care_modifier = self.CARE_TYPE_MODIFIERS.get(care_type.lower() if care_type else 'residential', 1.0)
            region_modifier = self._get_region_modifier(region or 'england')
            
            # Analyze needs from questionnaire
            needs_analysis = self._analyze_care_needs(questionnaire) if questionnaire else {}
            
            # Detect fees by category
            detected_fees = []
            fees_by_category = {}
            
            for fee_key, fee_data in self.HIDDEN_FEES_DATABASE.items():
                # Check if fee applies based on needs
                if fee_data.get('needs_based') and not needs_analysis.get(fee_key + '_needed', True):
                    continue
                
                # Calculate adjusted fee
                fee_estimate = self._estimate_fee(
                    fee_data,
                    care_modifier,
                    region_modifier,
                    weekly_price
                )
                
                if fee_estimate.get('likely_applies', False):
                    detected_fees.append({
                        'fee_id': fee_key,
                        'display_name': fee_data.get('display_name', fee_key),
                        'description': fee_data.get('description', ''),
                        'category': fee_data.get('category', 'other'),
                        'frequency': fee_data.get('frequency', 'weekly'),
                        'estimated_amount': fee_estimate.get('estimated_amount', 0),
                        'range_low': fee_estimate.get('range_low', 0),
                        'range_high': fee_estimate.get('range_high', 0),
                        'weekly_equivalent': fee_estimate.get('weekly_equivalent', 0),
                        'annual_impact': fee_estimate.get('annual_impact', 0),
                        'likelihood': fee_estimate.get('likelihood', 0),
                        'negotiable': fee_data.get('negotiable', False),
                        'refundable': fee_data.get('refundable', False),
                        'included_sometimes': fee_data.get('included_sometimes', False),
                        'risk_level': self._calculate_fee_risk(fee_estimate)
                    })
                    
                    # Group by category
                    category = fee_data.get('category', 'other')
                    if category not in fees_by_category:
                        fees_by_category[category] = {
                            **self.FEE_CATEGORIES.get(category, {'display_name': category, 'description': '', 'icon': '📋'}),
                            'fees': [],
                            'total_weekly': 0,
                            'total_annual': 0
                        }
                    fees_by_category[category]['fees'].append(detected_fees[-1])
                    fees_by_category[category]['total_weekly'] += fee_estimate.get('weekly_equivalent', 0)
                    fees_by_category[category]['total_annual'] += fee_estimate.get('annual_impact', 0)
            
            # Calculate totals with safe fallbacks
            total_one_time = sum(
                self._safe_float(f.get('estimated_amount', 0)) for f in detected_fees 
                if f.get('frequency') == 'one_time'
            )
            total_weekly = sum(self._safe_float(f.get('weekly_equivalent', 0)) for f in detected_fees)
            total_annual = sum(self._safe_float(f.get('annual_impact', 0)) for f in detected_fees)
            
            # Calculate hidden fees as percentage of advertised price
            hidden_fee_percent = (total_weekly / weekly_price * 100) if weekly_price > 0 else 0
            
            # Generate warnings and recommendations
            warnings = self._generate_fee_warnings(detected_fees, hidden_fee_percent)
            negotiation_tips = self._generate_negotiation_tips(detected_fees)
            
            return {
                'home_id': home_id,
                'home_name': home_name,
                'advertised_weekly_price': weekly_price,
                'care_type': care_type or 'residential',
                'region': region or 'england',
                'detected_fees': detected_fees,
                'fees_by_category': fees_by_category,
                'summary': {
                    'total_one_time_fees': round(total_one_time, 2),
                    'total_weekly_hidden': round(total_weekly, 2),
                    'total_annual_hidden': round(total_annual, 2),
                    'hidden_fee_percent': round(hidden_fee_percent, 1),
                    'true_weekly_cost': round(weekly_price + total_weekly, 2),
                    'true_annual_cost': round((weekly_price + total_weekly) * 52, 2),
                    'first_year_total': round((weekly_price + total_weekly) * 52 + total_one_time, 2),
                    'fee_count': len(detected_fees),
                    'negotiable_fees_count': sum(1 for f in detected_fees if f.get('negotiable', False)),
                    'potential_negotiation_savings': round(
                        sum(self._safe_float(f.get('annual_impact', 0)) * 0.3 for f in detected_fees if f.get('negotiable', False)), 2
                    )
                },
                'risk_assessment': {
                    'overall_risk': self._calculate_overall_risk(hidden_fee_percent),
                    'transparency_score': self._calculate_transparency_score(detected_fees),
                    'predictability_score': self._calculate_predictability_score(detected_fees)
                },
                'warnings': warnings,
                'negotiation_tips': negotiation_tips,
                'questions_to_ask': self._generate_fee_questions(detected_fees),
                'analyzed_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error detecting hidden fees for {care_home.get('name', 'unknown')}: {str(e)}")
            # Return safe fallback response
            return {
                'home_id': care_home.get('id', '') if care_home else '',
                'home_name': care_home.get('name', 'Unknown') if care_home else 'Unknown',
                'advertised_weekly_price': 0,
                'care_type': care_type,
                'region': region,
                'detected_fees': [],
                'fees_by_category': {},
                'summary': {
                    'total_one_time_fees': 0,
                    'total_weekly_hidden': 0,
                    'total_annual_hidden': 0,
                    'hidden_fee_percent': 0,
                    'true_weekly_cost': 0,
                    'true_annual_cost': 0,
                    'first_year_total': 0,
                    'fee_count': 0,
                    'negotiable_fees_count': 0,
                    'potential_negotiation_savings': 0
                },
                'risk_assessment': {
                    'overall_risk': 'low',
                    'transparency_score': 100,
                    'predictability_score': 100
                },
                'warnings': [],
                'negotiation_tips': [],
                'questions_to_ask': [],
                'analyzed_at': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _estimate_fee(
        self,
        fee_data: Dict[str, Any],
        care_modifier: float,
        region_modifier: float,
        weekly_price: float
    ) -> Dict[str, Any]:
        """Estimate a specific fee with modifiers applied"""
        base_range = fee_data['typical_range']
        base_average = fee_data['average']
        frequency = fee_data['frequency']
        commonality = fee_data.get('commonality', 0.5)
        
        # Apply modifiers
        modifier = care_modifier * region_modifier
        
        range_low = round(base_range[0] * modifier, 2)
        range_high = round(base_range[1] * modifier, 2)
        estimated = round(base_average * modifier, 2)
        
        # Calculate weekly equivalent and annual impact
        if frequency == 'one_time':
            weekly_equivalent = 0
            annual_impact = estimated  # One-time cost
        elif frequency == 'weekly':
            weekly_equivalent = estimated
            annual_impact = estimated * 52
        elif frequency == 'monthly':
            weekly_equivalent = estimated / 4.33
            annual_impact = estimated * 12
        elif frequency == 'annual_percent':
            # Annual fee increase as percent - calculate impact on weekly price
            weekly_equivalent = weekly_price * (estimated / 100) / 52
            annual_impact = weekly_price * (estimated / 100)
        elif frequency == 'per_occurrence':
            # Estimate 2 occurrences per month
            weekly_equivalent = estimated * 2 / 4.33
            annual_impact = estimated * 24
        else:
            weekly_equivalent = estimated
            annual_impact = estimated * 52
        
        return {
            'estimated_amount': estimated,
            'range_low': range_low,
            'range_high': range_high,
            'weekly_equivalent': round(weekly_equivalent, 2),
            'annual_impact': round(annual_impact, 2),
            'likely_applies': True,  # All fees in database are possible
            'likelihood': round(commonality * 100, 0)
        }
    
    def _get_region_modifier(self, region: str) -> float:
        """Get regional price modifier"""
        region_lower = region.lower().replace(' ', '_')
        
        # Handle common variations
        if 'london' in region_lower or 'greater london' in region_lower:
            return self.REGIONAL_MODIFIERS['london']
        elif 'south east' in region_lower or 'southeast' in region_lower:
            return self.REGIONAL_MODIFIERS['south_east']
        elif 'south west' in region_lower or 'southwest' in region_lower:
            return self.REGIONAL_MODIFIERS['south_west']
        
        return self.REGIONAL_MODIFIERS.get(region_lower, 1.0)
    
    def _analyze_care_needs(self, questionnaire: Dict[str, Any]) -> Dict[str, bool]:
        """Analyze questionnaire to determine which needs-based fees apply"""
        needs = {}
        
        medical = questionnaire.get('section_3_medical_needs', {})
        safety = questionnaire.get('section_4_safety_special_needs', {})
        
        # Continence needs
        conditions = medical.get('q9_medical_conditions', [])
        needs['continence_products_needed'] = 'dementia_alzheimers' in conditions
        
        # Equipment needs
        mobility = medical.get('q10_mobility_level', '')
        needs['equipment_rental_needed'] = mobility in ['wheelchair_sometimes', 'wheelchair_permanent']
        
        return needs
    
    def _calculate_fee_risk(self, fee_estimate: Dict[str, Any]) -> str:
        """Calculate risk level for a fee"""
        annual_impact = fee_estimate['annual_impact']
        
        if annual_impact > 2000:
            return 'high'
        elif annual_impact > 500:
            return 'medium'
        return 'low'
    
    def _calculate_overall_risk(self, hidden_fee_percent: float) -> str:
        """Calculate overall hidden fee risk"""
        if hidden_fee_percent > 20:
            return 'high'
        elif hidden_fee_percent > 10:
            return 'medium'
        return 'low'
    
    def _calculate_transparency_score(self, detected_fees: List[Dict]) -> int:
        """Calculate transparency score (0-100)"""
        # More negotiable fees = lower transparency
        negotiable_count = sum(1 for f in detected_fees if f['negotiable'])
        total_fees = len(detected_fees)
        
        if total_fees == 0:
            return 100
        
        # Base score
        score = 100 - (len(detected_fees) * 3)  # -3 points per fee
        score -= (negotiable_count * 5)  # -5 points per negotiable fee
        
        return max(0, min(100, score))
    
    def _calculate_predictability_score(self, detected_fees: List[Dict]) -> int:
        """Calculate cost predictability score (0-100)"""
        variable_fees = sum(
            1 for f in detected_fees 
            if f['frequency'] in ['per_occurrence', 'annual_percent']
        )
        
        score = 100 - (variable_fees * 10)
        return max(0, min(100, score))
    
    def _generate_fee_warnings(
        self,
        detected_fees: List[Dict],
        hidden_fee_percent: float
    ) -> List[Dict[str, str]]:
        """Generate warnings about hidden fees"""
        warnings = []
        
        if hidden_fee_percent > 15:
            warnings.append({
                'severity': 'high',
                'title': 'High Hidden Fee Risk',
                'message': f'Estimated hidden fees add {hidden_fee_percent:.1f}% to advertised price'
            })
        
        # Check for annual fee increase
        annual_increase = next(
            (f for f in detected_fees if f['fee_id'] == 'annual_fee_increase'),
            None
        )
        if annual_increase:
            warnings.append({
                'severity': 'medium',
                'title': 'Annual Price Increases Expected',
                'message': f'Fees typically increase {annual_increase["estimated_amount"]:.0f}% annually'
            })
        
        # High one-time fees
        one_time_total = sum(
            f['estimated_amount'] for f in detected_fees 
            if f['frequency'] == 'one_time'
        )
        if one_time_total > 3000:
            warnings.append({
                'severity': 'high',
                'title': 'Significant Move-In Costs',
                'message': f'Estimated one-time fees: £{one_time_total:,.0f}'
            })
        
        return warnings
    
    def _generate_negotiation_tips(self, detected_fees: List[Dict]) -> List[Dict[str, str]]:
        """Generate tips for negotiating fees"""
        tips = []
        
        negotiable_fees = [f for f in detected_fees if f['negotiable']]
        
        if negotiable_fees:
            tips.append({
                'title': 'Negotiable Fees Identified',
                'tip': f'{len(negotiable_fees)} fees may be negotiable. Ask about waiving or reducing: ' +
                       ', '.join(f['display_name'] for f in negotiable_fees[:3])
            })
        
        tips.append({
            'title': 'Request Full Fee Schedule',
            'tip': 'Ask for a complete written breakdown of all charges before signing'
        })
        
        tips.append({
            'title': 'Compare Included Services',
            'tip': 'Some homes include services others charge extra for - compare what\'s in the base price'
        })
        
        tips.append({
            'title': 'Negotiate Annual Increases',
            'tip': 'Try to cap annual fee increases at inflation rate (currently ~4%)'
        })
        
        return tips
    
    def _generate_fee_questions(self, detected_fees: List[Dict]) -> List[str]:
        """Generate questions to ask about fees"""
        questions = [
            'Can you provide a complete written schedule of all charges?',
            'What services are included in the weekly fee?',
            'Are there any one-time fees such as admission or registration fees?',
            'Is a deposit required? Is it refundable?',
            'How often do fees increase and by how much typically?',
            'Are there any additional charges for personal care items?',
            'What happens if care needs increase - are there additional charges?'
        ]
        
        # Add specific questions based on detected fees
        if any(f['fee_id'] == 'top_up_fee' for f in detected_fees):
            questions.append('Is there a top-up fee for this room type?')
        
        if any(f['fee_id'] == 'escorted_appointments' for f in detected_fees):
            questions.append('Are staff escorts to appointments charged separately?')
        
        return questions
    
    def calculate_cost_vs_funding_scenarios(
        self,
        care_homes: List[Dict[str, Any]],
        funding_optimization: Dict[str, Any],
        hidden_fees_analysis: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive cost vs funding scenarios
        
        Args:
            care_homes: List of care homes
            funding_optimization: Funding optimization data
            hidden_fees_analysis: Optional hidden fees analysis per home
        
        Returns:
            Dict with cost vs funding comparison for all scenarios
        """
        try:
            # Ensure we have valid inputs
            if not care_homes:
                care_homes = []
            if not funding_optimization:
                funding_optimization = {}
            if not hidden_fees_analysis:
                hidden_fees_analysis = []
            
            scenarios = []
            
            # Safely extract funding data with fallbacks
            chc_eligibility = funding_optimization.get('chc_eligibility') or {}
            la_funding = funding_optimization.get('la_funding') or {}
            dpa_considerations = funding_optimization.get('dpa_considerations') or {}
            
            chc_probability = self._safe_float(chc_eligibility.get('eligibility_probability', 0)) / 100
            la_available = la_funding.get('funding_available', False)
            la_split = la_funding.get('funding_split') or {}
            la_contribution_pct = self._safe_float(la_split.get('la_contribution_percent', 0)) / 100
            dpa_available = dpa_considerations.get('dpa_eligible', False)
            
            for i, home in enumerate(care_homes):
                if not home:
                    continue
                    
                weekly_price = self._safe_float(home.get('weeklyPrice') or home.get('weekly_price'), 0)
                home_name = home.get('name') or f'Home {i+1}'
                home_id = home.get('id') or str(i)
                
                # Get hidden fees if available - with safe access
                hidden_fees = None
                if hidden_fees_analysis:
                    hidden_fees = next(
                        (h for h in hidden_fees_analysis if h and h.get('home_id') == home_id),
                        None
                    )
                
                # Safely extract hidden fees data
                hidden_summary = (hidden_fees.get('summary') or {}) if hidden_fees else {}
                hidden_weekly = self._safe_float(hidden_summary.get('total_weekly_hidden', 0))
                hidden_annual = self._safe_float(hidden_summary.get('total_annual_hidden', 0))
                true_weekly = weekly_price + hidden_weekly
                true_annual = true_weekly * 52
                
                home_scenarios = {
                    'home_id': home_id,
                    'home_name': home_name,
                    'advertised_weekly': weekly_price,
                    'hidden_fees_weekly': round(hidden_weekly, 2),
                    'true_weekly_cost': round(true_weekly, 2),
                    'scenarios': []
                }
                
                # Scenario 1: Self-Funding (Full Cost)
                home_scenarios['scenarios'].append({
                'scenario_id': 'self_funding',
                'scenario_name': 'Self-Funding',
                'description': 'You pay 100% of care costs',
                'funding_source': 'Personal savings/assets',
                'weekly_cost': round(true_weekly, 2),
                'annual_cost': round(true_annual, 2),
                'five_year_cost': round(self._calculate_5_year_cost(true_weekly), 2),
                'out_of_pocket_weekly': round(true_weekly, 2),
                'out_of_pocket_annual': round(true_annual, 2),
                'funding_coverage_percent': 0,
                'probability': 100,
                'pros': [
                    'Full choice of care home',
                    'No means testing required',
                    'No bureaucracy or delays'
                ],
                'cons': [
                    'Highest out-of-pocket cost',
                    'Assets depleted over time',
                    'No financial support'
                ],
                'color': '#EF4444'  # Red
            })
            
            # Scenario 2: CHC Funding (if eligible)
            if chc_probability > 0.1:
                chc_weekly_out_of_pocket = 0  # CHC covers 100%
                home_scenarios['scenarios'].append({
                    'scenario_id': 'chc_funding',
                    'scenario_name': 'CHC Funding',
                    'description': 'NHS Continuing Healthcare covers 100% of care costs',
                    'funding_source': 'NHS',
                    'weekly_cost': round(true_weekly, 2),
                    'annual_cost': round(true_annual, 2),
                    'five_year_cost': 0,
                    'out_of_pocket_weekly': 0,
                    'out_of_pocket_annual': 0,
                    'funding_coverage_percent': 100,
                    'probability': round(chc_probability * 100, 1),
                    'eligibility_level': chc_eligibility.get('eligibility_level', 'unknown'),
                    'pros': [
                        'No personal cost for care',
                        'NHS pays entire fee',
                        'Preserves personal assets'
                    ],
                    'cons': [
                        'Strict eligibility criteria',
                        'Complex application process',
                        'May limit care home choice'
                    ],
                    'color': '#10B981'  # Green
                })
            
            # Scenario 3: LA Funding (if available)
            if la_available:
                la_weekly = la_contribution_pct * true_weekly
                self_weekly = true_weekly - la_weekly
                home_scenarios['scenarios'].append({
                    'scenario_id': 'la_funding',
                    'scenario_name': 'Local Authority Funding',
                    'description': f'LA contributes {la_contribution_pct*100:.0f}%, you pay {(1-la_contribution_pct)*100:.0f}%',
                    'funding_source': 'Local Authority',
                    'weekly_cost': round(true_weekly, 2),
                    'annual_cost': round(true_annual, 2),
                    'five_year_cost': round(self._calculate_5_year_cost(self_weekly), 2),
                    'out_of_pocket_weekly': round(self_weekly, 2),
                    'out_of_pocket_annual': round(self_weekly * 52, 2),
                    'la_contribution_weekly': round(la_weekly, 2),
                    'la_contribution_annual': round(la_weekly * 52, 2),
                    'funding_coverage_percent': round(la_contribution_pct * 100, 1),
                    'probability': 100 if la_available else 0,
                    'pros': [
                        'Reduced personal cost',
                        'Means-tested support',
                        'Can access care sooner'
                    ],
                    'cons': [
                        'Means testing required',
                        'May limit care home choice',
                        'Top-up fees may apply'
                    ],
                    'color': '#3B82F6'  # Blue
                })
            
            # Scenario 4: DPA (Deferred Payment)
            if dpa_available:
                dpa_costs = dpa_considerations.get('costs', {})
                interest_rate = dpa_costs.get('interest_rate_percent', 2.5) / 100
                admin_fee_weekly = dpa_costs.get('administration_fee_weekly', 2.77)
                
                home_scenarios['scenarios'].append({
                    'scenario_id': 'dpa',
                    'scenario_name': 'Deferred Payment Agreement',
                    'description': 'Pay from property value after care ends',
                    'funding_source': 'Property equity (deferred)',
                    'weekly_cost': round(true_weekly, 2),
                    'annual_cost': round(true_annual, 2),
                    'five_year_cost': round(self._calculate_5_year_cost(true_weekly, include_interest=True, interest_rate=interest_rate), 2),
                    'out_of_pocket_weekly': round(admin_fee_weekly, 2),  # Only admin fees during care
                    'out_of_pocket_annual': round(admin_fee_weekly * 52, 2),
                    'deferred_weekly': round(true_weekly, 2),
                    'deferred_annual': round(true_annual, 2),
                    'interest_rate_percent': round(interest_rate * 100, 2),
                    'funding_coverage_percent': 100,  # Deferred, not paid
                    'probability': 100 if dpa_available else 0,
                    'pros': [
                        'No immediate large payments',
                        'Stay in care without selling home',
                        'Interest at reasonable rate'
                    ],
                    'cons': [
                        'Interest accumulates',
                        'Reduces inheritance',
                        'Property may need to be sold later'
                    ],
                    'color': '#F59E0B'  # Orange
                })
            
            # Scenario 5: Hybrid (LA + Self)
            if la_available and la_contribution_pct < 1.0:
                home_scenarios['scenarios'].append({
                    'scenario_id': 'hybrid',
                    'scenario_name': 'Hybrid Funding',
                    'description': 'Combination of LA support and personal funds',
                    'funding_source': 'LA + Personal',
                    'weekly_cost': round(true_weekly, 2),
                    'annual_cost': round(true_annual, 2),
                    'five_year_cost': round(self._calculate_5_year_cost(true_weekly * (1 - la_contribution_pct)), 2),
                    'out_of_pocket_weekly': round(true_weekly * (1 - la_contribution_pct), 2),
                    'out_of_pocket_annual': round(true_weekly * (1 - la_contribution_pct) * 52, 2),
                    'funding_coverage_percent': round(la_contribution_pct * 100, 1),
                    'probability': 100,
                    'pros': [
                        'Balanced approach',
                        'Preserves some assets',
                        'Flexible funding mix'
                    ],
                    'cons': [
                        'Still requires personal contribution',
                        'Complex to manage',
                        'May change over time'
                    ],
                    'color': '#8B5CF6'  # Purple
                })
            
                scenarios.append(home_scenarios)
            
            # Calculate summary statistics
            summary = self._calculate_scenario_summary(scenarios)
            
            return {
                'homes': scenarios,
                'summary': summary,
                'funding_context': {
                    'chc_probability': round(chc_probability * 100, 1),
                    'la_available': la_available,
                    'la_contribution_percent': round(la_contribution_pct * 100, 1),
                    'dpa_available': dpa_available
                },
                'recommendations': self._generate_funding_recommendations(scenarios, chc_probability, la_available, dpa_available),
                'generated_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error calculating cost vs funding scenarios: {str(e)}")
            return {
                'homes': [],
                'summary': {
                    'average_self_funding_5yr': 0,
                    'average_best_case_5yr': 0,
                    'potential_5yr_savings': 0,
                    'average_hidden_fees_weekly': 0,
                    'homes_analyzed': 0
                },
                'funding_context': {
                    'chc_probability': 0,
                    'la_available': False,
                    'la_contribution_percent': 0,
                    'dpa_available': False
                },
                'recommendations': [],
                'generated_at': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _calculate_5_year_cost(
        self,
        weekly_cost: float,
        include_interest: bool = False,
        interest_rate: float = 0.025
    ) -> float:
        """Calculate 5-year total cost with inflation"""
        total = 0
        annual_cost = weekly_cost * 52
        
        for year in range(5):
            inflation_factor = (1 + self.inflation_rate) ** year
            year_cost = annual_cost * inflation_factor
            
            if include_interest:
                # Add interest on accumulated deferred amount
                accumulated = sum(
                    annual_cost * (1 + self.inflation_rate) ** y
                    for y in range(year + 1)
                )
                year_cost += accumulated * interest_rate
            
            total += year_cost
        
        return total
    
    def _calculate_scenario_summary(self, scenarios: List[Dict]) -> Dict[str, Any]:
        """Calculate summary across all homes and scenarios"""
        all_self_funding = []
        all_best_case = []
        all_hidden_fees = []
        
        for home in scenarios:
            # Find self-funding scenario
            self_funding = next(
                (s for s in home['scenarios'] if s['scenario_id'] == 'self_funding'),
                None
            )
            if self_funding:
                all_self_funding.append(self_funding['five_year_cost'])
            
            # Find best case (lowest cost with >50% probability)
            viable_scenarios = [
                s for s in home['scenarios']
                if s.get('probability', 0) > 50
            ]
            if viable_scenarios:
                best = min(viable_scenarios, key=lambda x: x.get('out_of_pocket_annual', float('inf')))
                all_best_case.append(best['out_of_pocket_annual'] * 5)
            
            all_hidden_fees.append(home.get('hidden_fees_weekly', 0))
        
        return {
            'average_self_funding_5yr': round(sum(all_self_funding) / len(all_self_funding), 2) if all_self_funding else 0,
            'average_best_case_5yr': round(sum(all_best_case) / len(all_best_case), 2) if all_best_case else 0,
            'potential_5yr_savings': round(
                (sum(all_self_funding) - sum(all_best_case)) / len(all_self_funding), 2
            ) if all_self_funding and all_best_case else 0,
            'average_hidden_fees_weekly': round(sum(all_hidden_fees) / len(all_hidden_fees), 2) if all_hidden_fees else 0,
            'homes_analyzed': len(scenarios)
        }
    
    def _generate_funding_recommendations(
        self,
        scenarios: List[Dict],
        chc_probability: float,
        la_available: bool,
        dpa_available: bool
    ) -> List[Dict[str, str]]:
        """Generate funding recommendations"""
        recommendations = []
        
        if chc_probability > 0.5:
            recommendations.append({
                'priority': 'high',
                'title': 'Apply for CHC Assessment',
                'description': f'With {chc_probability*100:.0f}% eligibility probability, CHC could save significant costs. Apply now.',
                'action': 'Contact local ICB for CHC assessment'
            })
        
        if la_available:
            recommendations.append({
                'priority': 'high',
                'title': 'Request LA Financial Assessment',
                'description': 'You may qualify for Local Authority funding support. Complete means test.',
                'action': 'Contact Adult Social Services for assessment'
            })
        
        if dpa_available:
            recommendations.append({
                'priority': 'medium',
                'title': 'Consider Deferred Payment',
                'description': 'DPA allows you to defer care costs against property value.',
                'action': 'Discuss DPA options with Local Authority'
            })
        
        recommendations.append({
            'priority': 'medium',
            'title': 'Request Full Fee Breakdown',
            'description': 'Ask each care home for complete fee schedule including all extras.',
            'action': 'Send written request to shortlisted homes'
        })
        
        return recommendations
    
    def calculate_full_cost_analysis(
        self,
        care_homes: List[Dict[str, Any]],
        funding_optimization: Dict[str, Any],
        questionnaire: Optional[Dict[str, Any]] = None,
        region: str = 'england'
    ) -> Dict[str, Any]:
        """
        Calculate complete cost analysis including hidden fees, projections, and scenarios
        
        Main entry point for Cost Analysis module
        """
        # Determine care type from questionnaire
        care_type = 'residential'
        if questionnaire:
            care_types = questionnaire.get('section_3_medical_needs', {}).get('q8_care_types', [])
            if 'medical_nursing' in care_types:
                care_type = 'nursing'
            elif 'specialised_dementia' in care_types:
                care_type = 'dementia'
            elif 'temporary_respite' in care_types:
                care_type = 'respite'
        
        # 1. Detect hidden fees for each home
        hidden_fees_analysis = []
        for home in care_homes:
            fees = self.detect_hidden_fees(
                care_home=home,
                care_type=care_type,
                region=region,
                questionnaire=questionnaire
            )
            hidden_fees_analysis.append(fees)
        
        # 2. Calculate cost vs funding scenarios
        cost_vs_funding = self.calculate_cost_vs_funding_scenarios(
            care_homes=care_homes,
            funding_optimization=funding_optimization,
            hidden_fees_analysis=hidden_fees_analysis
        )
        
        # 3. Calculate enhanced 5-year projections with hidden fees
        enhanced_projections = self._calculate_enhanced_projections(
            care_homes=care_homes,
            hidden_fees_analysis=hidden_fees_analysis,
            funding_optimization=funding_optimization
        )
        
        # 4. Generate executive summary
        executive_summary = self._generate_executive_summary(
            hidden_fees_analysis=hidden_fees_analysis,
            cost_vs_funding=cost_vs_funding,
            enhanced_projections=enhanced_projections
        )
        
        return {
            'hidden_fees_analysis': hidden_fees_analysis,
            'cost_vs_funding_scenarios': cost_vs_funding,
            'enhanced_projections': enhanced_projections,
            'executive_summary': executive_summary,
            'care_type_analyzed': care_type,
            'region': region,
            'generated_at': datetime.now().isoformat()
        }
    
    def _calculate_enhanced_projections(
        self,
        care_homes: List[Dict[str, Any]],
        hidden_fees_analysis: List[Dict[str, Any]],
        funding_optimization: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate 5-year projections including hidden fees"""
        projections = []
        
        for i, home in enumerate(care_homes):
            weekly_price = home.get('weeklyPrice', 0) or home.get('weekly_price', 0)
            home_name = home.get('name', f'Home {i+1}')
            home_id = home.get('id', str(i))
            
            # Get hidden fees
            hidden_fees = hidden_fees_analysis[i] if i < len(hidden_fees_analysis) else None
            hidden_weekly = hidden_fees['summary']['total_weekly_hidden'] if hidden_fees else 0
            one_time_fees = hidden_fees['summary']['total_one_time_fees'] if hidden_fees else 0
            
            true_weekly = weekly_price + hidden_weekly
            
            # Calculate year-by-year with and without hidden fees
            years = []
            cumulative_advertised = 0
            cumulative_true = 0
            
            for year in range(1, 6):
                inflation_factor = (1 + self.inflation_rate) ** (year - 1)
                
                advertised_annual = weekly_price * 52 * inflation_factor
                true_annual = true_weekly * 52 * inflation_factor
                
                # Add one-time fees to first year
                if year == 1:
                    true_annual += one_time_fees
                
                cumulative_advertised += advertised_annual
                cumulative_true += true_annual
                
                years.append({
                    'year': year,
                    'advertised_weekly': round(weekly_price * inflation_factor, 2),
                    'true_weekly': round(true_weekly * inflation_factor, 2),
                    'hidden_fees_weekly': round(hidden_weekly * inflation_factor, 2),
                    'advertised_annual': round(advertised_annual, 2),
                    'true_annual': round(true_annual, 2),
                    'hidden_fees_annual': round((true_annual - advertised_annual), 2),
                    'cumulative_advertised': round(cumulative_advertised, 2),
                    'cumulative_true': round(cumulative_true, 2),
                    'cumulative_hidden': round(cumulative_true - cumulative_advertised, 2),
                    'inflation_factor': round(inflation_factor, 4)
                })
            
            projections.append({
                'home_id': home_id,
                'home_name': home_name,
                'base_advertised_weekly': weekly_price,
                'base_true_weekly': round(true_weekly, 2),
                'one_time_fees': round(one_time_fees, 2),
                'years': years,
                'summary': {
                    'total_5_year_advertised': round(cumulative_advertised, 2),
                    'total_5_year_true': round(cumulative_true, 2),
                    'total_5_year_hidden': round(cumulative_true - cumulative_advertised, 2),
                    'hidden_fees_percent': round(
                        ((cumulative_true - cumulative_advertised) / cumulative_advertised * 100), 1
                    ) if cumulative_advertised > 0 else 0
                }
            })
        
        # Overall summary
        total_advertised = sum(p['summary']['total_5_year_advertised'] for p in projections)
        total_true = sum(p['summary']['total_5_year_true'] for p in projections)
        
        return {
            'projections': projections,
            'overall_summary': {
                'average_5_year_advertised': round(total_advertised / len(projections), 2) if projections else 0,
                'average_5_year_true': round(total_true / len(projections), 2) if projections else 0,
                'average_hidden_impact': round((total_true - total_advertised) / len(projections), 2) if projections else 0,
                'inflation_rate_used': self.inflation_rate * 100
            }
        }
    
    def _generate_executive_summary(
        self,
        hidden_fees_analysis: List[Dict[str, Any]],
        cost_vs_funding: Dict[str, Any],
        enhanced_projections: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate executive summary for cost analysis"""
        avg_hidden_percent = sum(
            h['summary']['hidden_fee_percent'] for h in hidden_fees_analysis
        ) / len(hidden_fees_analysis) if hidden_fees_analysis else 0
        
        avg_true_weekly = sum(
            h['summary']['true_weekly_cost'] for h in hidden_fees_analysis
        ) / len(hidden_fees_analysis) if hidden_fees_analysis else 0
        
        potential_savings = cost_vs_funding.get('summary', {}).get('potential_5yr_savings', 0)
        
        key_findings = []
        
        if avg_hidden_percent > 10:
            key_findings.append({
                'type': 'warning',
                'title': 'Significant Hidden Costs Detected',
                'detail': f'Hidden fees add an average of {avg_hidden_percent:.1f}% to advertised prices'
            })
        
        if potential_savings > 10000:
            key_findings.append({
                'type': 'opportunity',
                'title': 'Major Savings Potential',
                'detail': f'Funding options could save up to £{potential_savings:,.0f} over 5 years'
            })
        
        return {
            'headline': f'True weekly cost averages £{avg_true_weekly:,.0f} (hidden fees add {avg_hidden_percent:.1f}%)',
            'key_findings': key_findings,
            'average_hidden_fee_percent': round(avg_hidden_percent, 1),
            'average_true_weekly_cost': round(avg_true_weekly, 2),
            'potential_5_year_savings': round(potential_savings, 2),
            'homes_analyzed': len(hidden_fees_analysis)
        }

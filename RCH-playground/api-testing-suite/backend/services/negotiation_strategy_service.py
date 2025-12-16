"""
Negotiation Strategy Service
Generates negotiation strategy including market-rate analysis, discount points,
contract review checklist, and email templates for Professional Report
"""
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


def _safe_float_convert(value: Union[str, int, float, None]) -> Optional[float]:
    """
    Safely convert a value to float, handling strings that may contain text.
    
    Args:
        value: Value to convert (can be string, int, float, or None)
        
    Returns:
        Float value if conversion successful, None otherwise
    """
    if value is None:
        return None
    
    # If already a number, return it
    if isinstance(value, (int, float)):
        return float(value)
    
    # If string, try to extract number
    if isinstance(value, str):
        # Remove common non-numeric characters but keep decimal point and minus
        cleaned = value.strip()
        
        # Try direct conversion first
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            pass
        
        # Try to extract number from string (e.g., "Waived fees or 2" -> 2)
        # Look for patterns like: "2", "2.5", "£2", "2%", "2-3", etc.
        number_patterns = [
            r'(\d+\.?\d*)',  # Simple number: 2, 2.5
            r'£\s*(\d+\.?\d*)',  # Currency: £2, £2.5
            r'(\d+\.?\d*)\s*%',  # Percentage: 2%, 2.5%
            r'(\d+\.?\d*)\s*-\s*\d+',  # Range: 2-3 (take first number)
        ]
        
        for pattern in number_patterns:
            match = re.search(pattern, cleaned)
            if match:
                try:
                    return float(match.group(1))
                except (ValueError, TypeError):
                    continue
    
    return None

# Note: Autumna pricing scraper removed - using database prices from care_homes instead
# Prices are extracted from care_homes (weeklyPrice, weekly_costs, fee_* fields)
AUTUMNA_AVAILABLE = False


class NegotiationStrategyService:
    """Service for generating negotiation strategy for care homes"""
    
    # UK Average Weekly Care Home Costs (2024-2025)
    UK_AVERAGE_WEEKLY_COSTS = {
        'residential': 800,
        'nursing': 1100,
        'dementia': 950,
        'residential_dementia': 900,
        'nursing_dementia': 1200
    }
    
    # Regional Price Variations (% above/below UK average)
    REGIONAL_VARIATIONS = {
        'london': 1.35,  # 35% above average
        'south_east': 1.15,  # 15% above
        'south_west': 1.05,  # 5% above
        'east': 1.0,  # Average
        'west_midlands': 0.95,  # 5% below
        'east_midlands': 0.92,  # 8% below
        'yorkshire': 0.90,  # 10% below
        'north_west': 0.88,  # 12% below
        'north_east': 0.85,  # 15% below
        'scotland': 0.90,  # 10% below
        'wales': 0.88,  # 12% below
        'northern_ireland': 0.85  # 15% below
    }
    
    async def generate_negotiation_strategy(
        self,
        care_homes: List[Dict[str, Any]],
        questionnaire: Dict[str, Any],
        postcode: str = None,
        region: str = None,
        autumna_proxy_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive negotiation strategy
        
        Args:
            care_homes: List of top 5 care homes
            questionnaire: Professional questionnaire response
            postcode: Client postcode for regional analysis
            region: UK region (optional, will be inferred from postcode if not provided)
        
        Returns:
            Dict with negotiation strategy including:
            - Market-rate analysis
            - Discount negotiation points
            - Contract review checklist
            - Email templates
            - Questions to ask at visit
        """
        # Determine care type from questionnaire
        care_type = self._determine_care_type(questionnaire)
        
        # Determine region if not provided
        if not region and postcode:
            region = self._infer_region_from_postcode(postcode)
        
        # Use pricing data from care_homes database instead of Autumna
        # Prices are already available in care_homes (weeklyPrice, weekly_costs, fee_* fields)
        autumna_data = None  # No longer using Autumna - prices come from database
        
        # Generate market-rate analysis using database prices
        market_analysis = self._generate_market_rate_analysis(
            care_homes, care_type, region, autumna_data
        )
        
        # Generate discount negotiation points
        discount_points = self._generate_discount_negotiation_points(
            care_homes, questionnaire
        )
        
        # Generate contract review checklist
        contract_checklist = self._generate_contract_checklist(
            care_homes, questionnaire
        )
        
        # Generate email templates
        email_templates = self._generate_email_templates(
            care_homes, questionnaire
        )
        
        # Generate questions to ask at visit
        visit_questions = self._generate_visit_questions(
            care_homes, questionnaire
        )
        
        return {
            'market_rate_analysis': market_analysis,
            'discount_negotiation_points': discount_points,
            'contract_review_checklist': contract_checklist,
            'email_templates': email_templates,
            'questions_to_ask_at_visit': visit_questions,
            'generated_at': datetime.now().isoformat()
        }
    
    def _determine_care_type(self, questionnaire: Dict[str, Any]) -> str:
        """Determine primary care type from questionnaire"""
        medical_needs = questionnaire.get('section_3_medical_needs', {})
        care_types = medical_needs.get('q8_care_types', [])
        
        if 'nursing' in care_types:
            if 'dementia' in care_types or 'alzheimers' in care_types:
                return 'nursing_dementia'
            return 'nursing'
        elif 'dementia' in care_types or 'alzheimers' in care_types:
            return 'residential_dementia'
        else:
            return 'residential'
    
    def _infer_region_from_postcode(self, postcode: str) -> str:
        """Infer UK region from postcode"""
        if not postcode:
            return 'east'  # Default
        
        postcode_upper = postcode.upper().strip()
        
        # London postcodes
        if postcode_upper.startswith(('E', 'N', 'NW', 'SE', 'SW', 'W', 'WC', 'EC')):
            return 'london'
        # South East
        elif postcode_upper.startswith(('GU', 'PO', 'RG', 'SL', 'SO', 'KT', 'TW', 'UB', 'HA', 'WD', 'HP', 'AL', 'SG', 'CM', 'SS', 'RM', 'IG', 'EN', 'BR', 'DA', 'CR')):
            return 'south_east'
        # South West
        elif postcode_upper.startswith(('BA', 'BS', 'DT', 'EX', 'GL', 'PL', 'SN', 'SP', 'TA', 'TR')):
            return 'south_west'
        # West Midlands
        elif postcode_upper.startswith(('B', 'CV', 'DY', 'WR', 'WS', 'WV')):
            return 'west_midlands'
        # East Midlands
        elif postcode_upper.startswith(('DE', 'LE', 'NG', 'PE', 'LN', 'NG')):
            return 'east_midlands'
        # Yorkshire
        elif postcode_upper.startswith(('BD', 'HD', 'HG', 'HU', 'HX', 'LS', 'S', 'WF', 'YO')):
            return 'yorkshire'
        # North West
        elif postcode_upper.startswith(('BB', 'BL', 'CA', 'CH', 'CW', 'FY', 'L', 'M', 'OL', 'PR', 'SK', 'WA', 'WN')):
            return 'north_west'
        # North East
        elif postcode_upper.startswith(('DH', 'DL', 'NE', 'SR', 'TS')):
            return 'north_east'
        # Scotland
        elif postcode_upper.startswith(('AB', 'DD', 'DG', 'EH', 'FK', 'G', 'HS', 'IV', 'KA', 'KW', 'KY', 'ML', 'PA', 'PH', 'TD', 'ZE')):
            return 'scotland'
        # Wales
        elif postcode_upper.startswith(('CF', 'LD', 'LL', 'NP', 'SA', 'SY')):
            return 'wales'
        # Northern Ireland
        elif postcode_upper.startswith(('BT')):
            return 'northern_ireland'
        else:
            return 'east'  # Default
    
    # Note: Autumna pricing scraper removed - using database prices from care_homes instead
    # This method is kept for backward compatibility but always returns None
    async def _fetch_autumna_pricing(
        self,
        location: str,
        care_type: str,
        proxy_url: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch pricing data from Autumna - DEPRECATED: Using database prices instead"""
        return None  # No longer using Autumna - prices come from care_homes database
    
    def _generate_market_rate_analysis(
        self,
        care_homes: List[Dict[str, Any]],
        care_type: str,
        region: str,
        autumna_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate market-rate analysis"""
        # Get UK average for care type
        uk_average = self.UK_AVERAGE_WEEKLY_COSTS.get(care_type, 800)
        
        # Apply regional variation
        regional_multiplier = self.REGIONAL_VARIATIONS.get(region, 1.0)
        try:
            regional_multiplier = float(regional_multiplier) if regional_multiplier is not None else 1.0
        except (ValueError, TypeError):
            regional_multiplier = 1.0
        
        try:
            uk_average = float(uk_average) if uk_average is not None else 800.0
        except (ValueError, TypeError):
            uk_average = 800.0
        
        regional_average = uk_average * regional_multiplier
        
        # Use pricing data from care_homes database (no longer using Autumna)
        # Prices are extracted from care_homes below
        
        # Analyze care home prices
        prices = []
        for home in care_homes:
            price = home.get('weeklyPrice') or home.get('weekly_cost') or home.get('weekly_price_avg')
            price_float = _safe_float_convert(price)
            if price_float and price_float > 0:
                prices.append(price_float)
        
        if not prices:
            prices = [regional_average]  # Fallback
        
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
        
        # Compare to market
        price_comparison = []
        for home in care_homes:
            price = home.get('weeklyPrice') or home.get('weekly_cost') or home.get('weekly_price_avg')
            price_float = _safe_float_convert(price)
            if price_float and price_float > 0 and regional_average > 0:
                try:
                    vs_market = ((price_float - regional_average) / regional_average) * 100
                    vs_uk = ((price_float - uk_average) / uk_average) * 100 if uk_average > 0 else 0.0
                    
                    # Ensure vs_market and vs_uk are numbers
                    vs_market = float(vs_market) if vs_market is not None else 0.0
                    vs_uk = float(vs_uk) if vs_uk is not None else 0.0
                    
                    price_comparison.append({
                        'home_name': home.get('name', 'Unknown'),
                        'weekly_price': price_float,
                        'vs_regional_average': round(vs_market, 1),
                        'vs_uk_average': round(vs_uk, 1),
                        'positioning': self._get_price_positioning(vs_market),
                        'negotiation_potential': self._assess_negotiation_potential(vs_market, home)
                    })
                except (ValueError, TypeError, ZeroDivisionError):
                    pass  # Skip this home if calculation fails
        
        # Value positioning analysis
        value_analysis = self._analyze_value_positioning(care_homes, prices, regional_average)
        
        market_analysis = {
            'uk_average_weekly': uk_average,
            'regional_average_weekly': round(regional_average, 2),
            'region': region,
            'care_type': care_type,
            'market_price_range': {
                'minimum': round(min_price, 2),
                'maximum': round(max_price, 2),
                'average': round(avg_price, 2)
            },
            'price_comparison': price_comparison,
            'value_positioning': value_analysis,
            'market_insights': self._generate_market_insights(prices, regional_average, care_homes)
        }
        
        return market_analysis
    
    def _get_price_positioning(self, vs_market_percent: float) -> str:
        """Get price positioning label"""
        # Ensure vs_market_percent is a number
        try:
            vs_market_percent = float(vs_market_percent) if vs_market_percent is not None else 0.0
        except (ValueError, TypeError):
            vs_market_percent = 0.0
        
        if vs_market_percent > 20:
            return 'Premium'
        elif vs_market_percent > 10:
            return 'Above Market'
        elif vs_market_percent > -5:
            return 'Market Rate'
        elif vs_market_percent > -15:
            return 'Below Market'
        else:
            return 'Budget'
    
    def _assess_negotiation_potential(
        self,
        vs_market_percent: float,
        home: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess negotiation potential for a home"""
        # Ensure vs_market_percent is a number
        try:
            vs_market_percent = float(vs_market_percent) if vs_market_percent is not None else 0.0
        except (ValueError, TypeError):
            vs_market_percent = 0.0
        
        # Higher prices = more negotiation room
        if vs_market_percent > 15:
            potential = 'high'
            discount_range = '5-15%'
            reasoning = 'Priced significantly above market average'
        elif vs_market_percent > 5:
            potential = 'medium'
            discount_range = '3-8%'
            reasoning = 'Priced above market average'
        elif vs_market_percent > -5:
            potential = 'medium'
            discount_range = '2-5%'
            reasoning = 'Market rate pricing - standard discounts may apply'
        else:
            potential = 'low'
            discount_range = '0-3%'
            reasoning = 'Already priced below market - limited discount room'
        
        # Adjust based on home characteristics
        match_score_raw = home.get('matchScore', 0)
        try:
            match_score = float(match_score_raw) if match_score_raw is not None else 0.0
        except (ValueError, TypeError):
            match_score = 0.0
        
        cqc_rating = home.get('cqcRating', '').lower()
        
        # High match score = less negotiation leverage
        if match_score > 85:
            potential = 'low' if potential == 'high' else potential
            reasoning += '. High match score may limit negotiation room.'
        
        # Lower CQC rating = more negotiation room
        if 'requires improvement' in cqc_rating or 'inadequate' in cqc_rating:
            if potential == 'low':
                potential = 'medium'
            discount_range = f"{discount_range.split('-')[0]}-{int(discount_range.split('-')[1].replace('%', '')) + 3}%"
            reasoning += ' Lower CQC rating may provide negotiation leverage.'
        
        return {
            'potential': potential,
            'discount_range': discount_range,
            'reasoning': reasoning,
            'recommended_approach': self._get_recommended_approach(potential, vs_market_percent)
        }
    
    def _get_recommended_approach(self, potential: str, vs_market_percent: float) -> str:
        """Get recommended negotiation approach"""
        if potential == 'high':
            return 'Start with 10-12% discount request. Emphasize long-term commitment and self-funding.'
        elif potential == 'medium':
            return 'Start with 5-7% discount request. Focus on self-funding benefits and trial period commitment.'
        else:
            return 'Focus on value-added services rather than price reduction. Consider asking for waived fees or included services.'
    
    def _analyze_value_positioning(
        self,
        care_homes: List[Dict[str, Any]],
        prices: List[float],
        regional_average: float
    ) -> Dict[str, Any]:
        """Analyze value positioning of care homes"""
        if not prices:
            return {'best_value': None, 'premium_options': [], 'budget_options': []}
        
        avg_price = sum(prices) / len(prices)
        
        # Find best value (highest match score relative to price)
        best_value = None
        best_value_score = 0
        
        premium_options = []
        budget_options = []
        
        for home in care_homes:
            price = home.get('weeklyPrice') or home.get('weekly_cost') or home.get('weekly_price_avg')
            price_float = _safe_float_convert(price)
            match_score_raw = home.get('matchScore', 0)
            
            # Ensure match_score is a number
            try:
                match_score = float(match_score_raw) if match_score_raw is not None else 0.0
            except (ValueError, TypeError):
                match_score = 0.0
            
            # Ensure regional_average is a number
            try:
                regional_average_safe = float(regional_average) if regional_average is not None else 0.0
            except (ValueError, TypeError):
                regional_average_safe = 0.0
            
            if price_float and price_float > 0 and match_score > 0 and regional_average_safe > 0:
                # Value score = match score / (price / regional_average)
                try:
                    value_score = match_score / (price_float / regional_average_safe)
                    
                    # Ensure value_score is a number
                    value_score = float(value_score) if value_score is not None else 0.0
                    
                    if value_score > best_value_score:
                        best_value_score = value_score
                        best_value = {
                            'home_name': home.get('name'),
                            'match_score': match_score,
                            'weekly_price': price_float,
                            'value_score': round(value_score, 2)
                        }
                    
                    # Categorize
                    if price_float > regional_average_safe * 1.15:
                        premium_options.append({
                            'home_name': home.get('name'),
                            'weekly_price': price_float,
                            'match_score': match_score
                        })
                    elif price_float < regional_average_safe * 0.90:
                        budget_options.append({
                            'home_name': home.get('name'),
                            'weekly_price': price_float,
                            'match_score': match_score
                        })
                except (ValueError, TypeError, ZeroDivisionError):
                    pass  # Skip this home if calculation fails
        
        return {
            'best_value': best_value,
            'premium_options': premium_options,
            'budget_options': budget_options,
            'market_average': round(regional_average, 2)
        }
    
    def _generate_market_insights(
        self,
        prices: List[float],
        regional_average: float,
        care_homes: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate market insights"""
        insights = []
        
        if not prices:
            return ['Pricing data not available for market comparison']
        
        # Ensure all prices are numbers
        safe_prices = []
        for p in prices:
            try:
                p_float = float(p) if p is not None else 0.0
                if p_float > 0:
                    safe_prices.append(p_float)
            except (ValueError, TypeError):
                pass
        
        if not safe_prices:
            return ['Pricing data not available for market comparison']
        
        avg_price = sum(safe_prices) / len(safe_prices)
        
        # Ensure regional_average is a number
        try:
            regional_average_safe = float(regional_average) if regional_average is not None else 0.0
        except (ValueError, TypeError):
            regional_average_safe = 0.0
        
        if regional_average_safe > 0:
            if avg_price > regional_average_safe * 1.1:
                insights.append(f"Average price of selected homes ({avg_price:.0f}) is {((avg_price - regional_average_safe) / regional_average_safe * 100):.0f}% above regional average - indicates premium positioning")
            elif avg_price < regional_average_safe * 0.9:
                insights.append(f"Average price of selected homes ({avg_price:.0f}) is {((regional_average_safe - avg_price) / regional_average_safe * 100):.0f}% below regional average - good value positioning")
            else:
                insights.append(f"Average price aligns with regional market average ({regional_average_safe:.0f})")
        
        price_range = max(safe_prices) - min(safe_prices)
        if regional_average_safe > 0 and price_range > regional_average_safe * 0.3:
            insights.append(f"Significant price variation ({price_range:.0f}/week range) - opportunity to negotiate based on value comparison")
        
        # CQC rating insights
        outstanding_count = sum(1 for h in care_homes if 'outstanding' in h.get('cqcRating', '').lower())
        if outstanding_count > 0:
            insights.append(f"{outstanding_count} home(s) with Outstanding CQC rating - premium pricing may be justified")
        
        return insights
    
    def _generate_discount_negotiation_points(
        self,
        care_homes: List[Dict[str, Any]],
        questionnaire: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate discount negotiation points"""
        # Determine funding type
        funding_section = questionnaire.get('section_5_funding', {})
        funding_type = funding_section.get('q17_funding_type', 'self_funding')
        
        negotiation_points = []
        
        # 1. Long-term commitment discount
        placement_timeline = funding_section.get('q18_placement_timeline', '')
        if placement_timeline in ['within_1_month', 'within_3_months']:
            negotiation_points.append({
                'type': 'long_term_commitment',
                'title': 'Long-Term Commitment Discount',
                'description': 'Commit to 12+ months placement',
                'potential_discount': '5-10%',
                'reasoning': 'Homes value guaranteed occupancy and reduced marketing costs',
                'how_to_negotiate': 'Offer to sign 12-month contract in exchange for 5-10% weekly rate reduction',
                'priority': 'high'
            })
        
        # 2. Self-funding discount
        if funding_type == 'self_funding':
            negotiation_points.append({
                'type': 'self_funding',
                'title': 'Self-Funding Discount',
                'description': 'Pay privately without local authority involvement',
                'potential_discount': '3-7%',
                'reasoning': 'Self-funding clients pay faster, no LA delays, simpler administration',
                'how_to_negotiate': 'Emphasize prompt payment and reduced administrative burden',
                'priority': 'high'
            })
        
        # 3. Off-peak placement discount
        negotiation_points.append({
            'type': 'off_peak',
            'title': 'Off-Peak Placement Discount',
            'description': 'Placement during quieter periods (Jan-Mar, Sep-Nov)',
            'potential_discount': '2-5%',
            'reasoning': 'Homes have lower occupancy during these periods',
            'how_to_negotiate': 'Offer flexible start date to align with home\'s occupancy needs',
            'priority': 'medium'
        })
        
        # 4. Referral discount
        negotiation_points.append({
            'type': 'referral',
            'title': 'Referral Discount',
            'description': 'Refer other families to the home',
            'potential_discount': '2-4% per referral',
            'reasoning': 'Word-of-mouth referrals are valuable marketing',
            'how_to_negotiate': 'Offer to refer friends/family members seeking care',
            'priority': 'low'
        })
        
        # 5. Trial period discount
        negotiation_points.append({
            'type': 'trial_period',
            'title': 'Trial Period Commitment',
            'description': 'Commit to 4-6 week trial period',
            'potential_discount': 'Waived fees or 2-3%',
            'reasoning': 'Trial periods reduce risk for both parties',
            'how_to_negotiate': 'Request waived assessment fees or reduced rate during trial',
            'priority': 'medium'
        })
        
        # 6. Multiple services discount
        medical_needs = questionnaire.get('section_3_medical_needs', {})
        if len(medical_needs.get('q9_medical_conditions', [])) > 2:
            negotiation_points.append({
                'type': 'multiple_services',
                'title': 'Multiple Services Discount',
                'description': 'Require multiple specialized services',
                'potential_discount': '3-5%',
                'reasoning': 'Bundled services reduce administrative overhead',
                'how_to_negotiate': 'Request package pricing for multiple care services',
                'priority': 'medium'
            })
        
        return {
            'available_discounts': negotiation_points,
            'total_potential_discount': self._calculate_total_potential_discount(negotiation_points),
            'negotiation_strategy': self._generate_negotiation_strategy_guide(negotiation_points, funding_type)
        }
    
    def _calculate_total_potential_discount(self, negotiation_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate total potential discount"""
        high_priority = [p for p in negotiation_points if p.get('priority') == 'high']
        medium_priority = [p for p in negotiation_points if p.get('priority') == 'medium']
        
        # Extract discount ranges
        high_discounts = []
        medium_discounts = []
        
        for point in high_priority:
            discount_range = point.get('potential_discount', '0%')
            if '-' in discount_range:
                # Safely convert discount range values
                range_values = []
                for x in discount_range.split('-'):
                    cleaned = x.replace('%', '').strip()
                    value = _safe_float_convert(cleaned)
                    if value is not None:
                        range_values.append(value)
                if len(range_values) == 2:
                    high_discounts.append(range_values)
        
        for point in medium_priority:
            discount_range = point.get('potential_discount', '0%')
            if '-' in discount_range:
                # Safely convert discount range values
                range_values = []
                for x in discount_range.split('-'):
                    cleaned = x.replace('%', '').strip()
                    value = _safe_float_convert(cleaned)
                    if value is not None:
                        range_values.append(value)
                if len(range_values) == 2:
                    medium_discounts.append(range_values)
        
        # Conservative estimate: use lower end of ranges, don't stack all discounts
        conservative_min = sum(d[0] for d in high_discounts[:2]) if high_discounts else 0
        conservative_max = sum(d[1] for d in high_discounts[:2]) if high_discounts else 0
        
        # Optimistic estimate: combine high and medium priority
        optimistic_min = conservative_min + (sum(d[0] for d in medium_discounts[:1]) if medium_discounts else 0)
        optimistic_max = conservative_max + (sum(d[1] for d in medium_discounts[:1]) if medium_discounts else 0)
        
        return {
            'conservative_range': f"{conservative_min:.0f}-{conservative_max:.0f}%",
            'optimistic_range': f"{optimistic_min:.0f}-{optimistic_max:.0f}%",
            'realistic_expectation': f"{(conservative_min + conservative_max) / 2:.0f}%",
            'note': 'Discounts may not stack - focus on 2-3 highest priority points'
        }
    
    def _generate_negotiation_strategy_guide(
        self,
        negotiation_points: List[Dict[str, Any]],
        funding_type: str
    ) -> Dict[str, Any]:
        """Generate negotiation strategy guide"""
        high_priority = [p for p in negotiation_points if p.get('priority') == 'high']
        
        opening_strategy = []
        if high_priority:
            opening_strategy.append(f"Start with: {high_priority[0].get('title')} ({high_priority[0].get('potential_discount')})")
            if len(high_priority) > 1:
                opening_strategy.append(f"Then mention: {high_priority[1].get('title')} ({high_priority[1].get('potential_discount')})")
        
        return {
            'opening_strategy': opening_strategy,
            'key_talking_points': [p.get('how_to_negotiate') for p in high_priority[:3]],
            'timing': 'Best to negotiate after initial visit but before contract signing',
            'approach': 'Professional and collaborative - emphasize mutual benefits',
            'red_flags': [
                'Avoid homes that refuse any negotiation - may indicate inflexibility',
                'Be cautious if discount is offered immediately without discussion',
                'Ensure discounts are documented in contract'
            ]
        }
    
    def _generate_contract_checklist(
        self,
        care_homes: List[Dict[str, Any]],
        questionnaire: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate contract review checklist"""
        checklist = {
            'essential_terms': [
                {
                    'term': 'Weekly Rate',
                    'what_to_check': 'Base weekly cost, what\'s included, what\'s extra',
                    'red_flags': ['Vague pricing', 'Many hidden fees', 'Unclear inclusions']
                },
                {
                    'term': 'Price Increase Clauses',
                    'what_to_check': 'Annual increase policy, maximum increase %, notice period',
                    'red_flags': ['Unlimited increases', 'No cap on increases', 'Short notice periods']
                },
                {
                    'term': 'Cancellation Terms',
                    'what_to_check': 'Notice period required, cancellation fees, refund policy',
                    'red_flags': ['Excessive notice periods (>4 weeks)', 'High cancellation fees', 'No refund policy']
                },
                {
                    'term': 'Trial Period',
                    'what_to_check': 'Trial period length, terms, what happens if not suitable',
                    'red_flags': ['No trial period', 'Trial fees not refundable', 'Unclear trial terms']
                },
                {
                    'term': 'Additional Services Pricing',
                    'what_to_check': 'Cost of extra services (physio, hairdressing, etc.)',
                    'red_flags': ['Unclear pricing', 'Excessive charges', 'No price list']
                },
                {
                    'term': 'Deposit & Fees',
                    'what_to_check': 'Deposit amount, refundable?, assessment fees, admin fees',
                    'red_flags': ['Non-refundable deposits', 'High assessment fees', 'Multiple hidden fees']
                },
                {
                    'term': 'Care Plan Review',
                    'what_to_check': 'How often care plan reviewed, who pays for changes',
                    'red_flags': ['No regular reviews', 'Client pays for all changes', 'Unclear process']
                },
                {
                    'term': 'Complaints Procedure',
                    'what_to_check': 'How to raise concerns, escalation process, CQC involvement',
                    'red_flags': ['No clear procedure', 'Discourages complaints', 'No escalation path']
                }
            ],
            'recommended_additions': [
                'Price freeze for first 12 months',
                'Written confirmation of included services',
                'Right to request care plan review every 6 months',
                'Clear policy on staff changes affecting care',
                'Transparency on any planned renovations/disruptions'
            ],
            'negotiation_leverage_points': self._identify_leverage_points(care_homes, questionnaire)
        }
        
        return checklist
    
    def _identify_leverage_points(
        self,
        care_homes: List[Dict[str, Any]],
        questionnaire: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify contract negotiation leverage points"""
        leverage_points = []
        
        # Check for homes with lower CQC ratings
        for home in care_homes:
            cqc_rating = home.get('cqcRating', '').lower()
            if 'requires improvement' in cqc_rating:
                leverage_points.append({
                    'home_name': home.get('name'),
                    'leverage': 'Lower CQC rating',
                    'suggestion': 'Request price reduction or enhanced services to compensate for rating concerns'
                })
        
        # Check for financial stability concerns
        for home in care_homes:
            financial = home.get('financialStability')
            if financial:
                bankruptcy_risk = financial.get('bankruptcy_risk_score', 0)
                if bankruptcy_risk > 50:
                    leverage_points.append({
                        'home_name': home.get('name'),
                        'leverage': 'Financial stability concerns',
                        'suggestion': 'Request shorter contract term or exit clause if financial situation deteriorates'
                    })
        
        # Check for multiple options
        if len(care_homes) >= 3:
            leverage_points.append({
                'home_name': 'Multiple Options',
                'leverage': 'Competitive market',
                'suggestion': 'Use competitive quotes to negotiate better terms - homes aware of alternatives'
            })
        
        return leverage_points
    
    def _generate_email_templates(
        self,
        care_homes: List[Dict[str, Any]],
        questionnaire: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate email templates for inquiry and negotiation"""
        client_name = questionnaire.get('section_1_personal_info', {}).get('q1_client_name', 'Client')
        care_type = self._determine_care_type(questionnaire)
        
        # Initial inquiry template
        initial_inquiry = f"""Subject: Inquiry About Care Home Placement - {client_name}

Dear [Care Home Manager],

I am writing to inquire about care home placement for [client_name], who requires {care_type} care.

Based on my research, [Care Home Name] appears to be an excellent match for our needs, particularly:
- [Match point 1 from report]
- [Match point 2 from report]
- [Match point 3 from report]

I would like to arrange a visit to discuss:
- Available placement dates
- Care plan details
- Pricing and what's included
- Contract terms

I am [self-funding / exploring funding options] and looking to make a decision within [timeline].

Would you be available for a visit in the next [1-2 weeks]?

Thank you for your time.

Best regards,
[Your Name]
[Your Phone Number]
[Your Email]"""
        
        # Follow-up negotiation template
        negotiation_followup = f"""Subject: Follow-up: Care Home Placement Discussion - {client_name}

Dear [Care Home Manager],

Thank you for the visit to [Care Home Name] last week. We were very impressed with [specific positive aspects].

After careful consideration, we would like to proceed with placement, subject to agreeing on terms that work for both parties.

Given our circumstances:
- [Self-funding / Long-term commitment / etc.]
- [Any specific needs]

We would like to discuss:
1. Weekly rate and what's included
2. Potential for [discount type] given [reason]
3. Contract terms, particularly [specific concern]
4. Trial period arrangements

We are prepared to make a decision quickly if terms are agreeable.

Would you be available for a call this week to discuss?

Thank you.

Best regards,
[Your Name]
[Your Phone Number]"""
        
        # Contract clarification template
        contract_clarification = f"""Subject: Contract Terms Clarification - {client_name}

Dear [Care Home Manager],

Thank you for providing the contract for [Care Home Name]. Before we proceed, I would like to clarify a few points:

1. **Pricing**: Could you confirm the base weekly rate and provide a detailed breakdown of what's included vs. additional charges?

2. **Price Increases**: What is your policy on annual price increases? Is there a maximum percentage increase?

3. **Trial Period**: What are the terms of the trial period? What happens if the placement is not suitable?

4. **Cancellation**: What notice period is required for cancellation? Are there any cancellation fees?

5. **Additional Services**: Could you provide a price list for additional services (physiotherapy, hairdressing, etc.)?

6. **Care Plan Reviews**: How often are care plans reviewed? Who covers the cost of care plan changes?

I appreciate your patience as we ensure we fully understand the terms before making a commitment.

Best regards,
[Your Name]"""
        
        return {
            'initial_inquiry': {
                'template': initial_inquiry,
                'when_to_use': 'First contact with care home',
                'customization_notes': 'Fill in [bracketed] sections with specific details from report'
            },
            'negotiation_followup': {
                'template': negotiation_followup,
                'when_to_use': 'After initial visit, before contract signing',
                'customization_notes': 'Mention specific discount points from negotiation strategy'
            },
            'contract_clarification': {
                'template': contract_clarification,
                'when_to_use': 'When reviewing contract before signing',
                'customization_notes': 'Add any specific concerns identified in contract checklist'
            }
        }
    
    def _generate_visit_questions(
        self,
        care_homes: List[Dict[str, Any]],
        questionnaire: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate questions to ask at visit"""
        medical_needs = questionnaire.get('section_3_medical_needs', {})
        conditions = medical_needs.get('q9_medical_conditions', [])
        
        questions = {
            'medical_care': [
                'What medical care is provided on-site vs. requiring external services?',
                'How many registered nurses are on staff?',
                'What is the staff-to-resident ratio during day/night shifts?',
                'How are medications managed and administered?',
                'What is the protocol for medical emergencies?',
                'How quickly can a GP visit be arranged?'
            ],
            'staff_qualifications': [
                'What qualifications do care staff hold?',
                'What is the average tenure of care staff?',
                'How often is staff training updated?',
                'What is the staff turnover rate?',
                'How are new staff members onboarded?'
            ],
            'cqc_feedback': [
                'What feedback did you receive from your last CQC inspection?',
                'Are there any active improvement plans?',
                'How have you addressed any concerns raised by CQC?',
                'What changes have you made since the last inspection?'
            ],
            'financial_stability': [
                'How long has the home been operating?',
                'Who owns/manages the home?',
                'Are there any planned changes to ownership or management?',
                'How stable is the home financially?'
            ],
            'trial_period': [
                'Do you offer a trial period?',
                'What are the terms of the trial period?',
                'What happens if the placement is not suitable after trial?',
                'Are trial period fees refundable?'
            ],
            'cancellation_terms': [
                'What notice period is required for cancellation?',
                'Are there any cancellation fees?',
                'What happens to deposits if we need to cancel?',
                'Can we exit early if circumstances change?'
            ],
            'pricing': [
                'What is included in the weekly rate?',
                'What additional services incur extra charges?',
                'What is your policy on annual price increases?',
                'Are there any discounts available for long-term commitment or self-funding?',
                'What fees are charged upfront (deposit, assessment, etc.)?'
            ]
        }
        
        # Add condition-specific questions
        if 'dementia' in conditions or 'alzheimers' in conditions:
            questions['dementia_specific'] = [
                'What specialized dementia care programs do you offer?',
                'How do you manage challenging behaviors?',
                'What activities are available for residents with dementia?',
                'How secure is the facility for residents who may wander?'
            ]
        
        if 'diabetes' in conditions:
            questions['diabetes_specific'] = [
                'How do you manage diabetes care and monitoring?',
                'Do you have staff trained in diabetes management?',
                'How are blood sugar levels monitored?'
            ]
        
        return {
            'questions_by_category': questions,
            'priority_questions': self._identify_priority_questions(care_homes, questionnaire),
            'red_flag_questions': [
                'Have there been any safeguarding incidents in the past year?',
                'Are there any ongoing regulatory actions or investigations?',
                'Have there been any significant staff changes recently?',
                'Are there any planned renovations or disruptions?'
            ]
        }
    
    def _identify_priority_questions(
        self,
        care_homes: List[Dict[str, Any]],
        questionnaire: Dict[str, Any]
    ) -> List[str]:
        """Identify priority questions based on care home characteristics"""
        priority = []
        
        # Check for CQC concerns
        for home in care_homes:
            cqc_rating = home.get('cqcRating', '').lower()
            if 'requires improvement' in cqc_rating:
                priority.append('What specific improvements have been made since the CQC inspection?')
                break
        
        # Check for financial concerns
        for home in care_homes:
            financial = home.get('financialStability')
            if financial:
                bankruptcy_risk = financial.get('bankruptcy_risk_score', 0)
                # Ensure bankruptcy_risk is a number
                try:
                    bankruptcy_risk = float(bankruptcy_risk) if bankruptcy_risk is not None else 0.0
                except (ValueError, TypeError):
                    bankruptcy_risk = 0.0
                
                if bankruptcy_risk > 50:
                    priority.append('How stable is the home financially? Are there any concerns about long-term viability?')
                    break
        
        # Check for staff concerns
        for home in care_homes:
            staff = home.get('staffQuality')
            if staff:
                turnover_rate = staff.get('turnover_rate_percent', 0)
                # Ensure turnover_rate is a number
                try:
                    turnover_rate = float(turnover_rate) if turnover_rate is not None else 0.0
                except (ValueError, TypeError):
                    turnover_rate = 0.0
                
                if turnover_rate > 30:
                    priority.append('What is causing the high staff turnover rate? What steps are being taken to improve retention?')
                    break
        
        return priority


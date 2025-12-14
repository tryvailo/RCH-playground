"""
Funding Optimization Service
Calculates CHC eligibility, LA funding availability, DPA considerations,
estimated funding outcomes, and 5-year cost projections for Professional Report
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import logging

logger = logging.getLogger(__name__)


class FundingOptimizationService:
    """Service for calculating funding optimization for care home placements"""
    
    # UK Average Care Home Costs (2024-2025)
    UK_AVERAGE_WEEKLY_COSTS = {
        'residential': 800,  # £800/week average
        'nursing': 1200,     # £1,200/week average
        'dementia': 1000,    # £1,000/week average
        'respite': 900       # £900/week average
    }
    
    # CHC Eligibility Criteria Thresholds
    CHC_ELIGIBILITY_THRESHOLDS = {
        'primary_health_need': {
            'severe': 0.8,      # 80%+ chance if severe medical needs
            'moderate': 0.4,    # 40% chance if moderate
            'low': 0.1          # 10% chance if low
        },
        'complexity_factors': {
            'multiple_conditions': 0.15,  # +15% for multiple conditions
            'nursing_care': 0.20,         # +20% if nursing care required
            'mobility_severe': 0.10,      # +10% for severe mobility issues
            'dementia_severe': 0.15,      # +15% for severe dementia
            'medication_complex': 0.10     # +10% for complex medication
        }
    }
    
    # LA Funding Thresholds (2024-2025)
    LA_FUNDING_THRESHOLDS = {
        'capital_threshold': 23250,      # £23,250 capital threshold
        'income_threshold': 189.50,      # £189.50/week income threshold
        'maximum_contribution': 0.8,      # LA covers up to 80% typically
        'minimum_contribution': 0.2      # Self-funding minimum 20%
    }
    
    # DPA (Deferred Payment Agreement) Parameters
    DPA_PARAMETERS = {
        'minimum_equity': 14250,         # £14,250 minimum equity required
        'interest_rate': 0.025,          # 2.5% annual interest rate
        'maximum_deferral': 0.7,         # Up to 70% of property value
        'administration_fee': 144,      # £144 annual admin fee
        'setup_fee': 0                   # Usually no setup fee
    }
    
    # Annual Cost Inflation Rate
    COST_INFLATION_RATE = 0.04  # 4% annual increase
    
    def calculate_chc_eligibility(
        self,
        questionnaire: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate NHS Continuing Healthcare (CHC) eligibility probability
        
        Based on NHS Decision Support Tool (DST) framework with 12 care domains:
        1. Breathing, 2. Nutrition, 3. Continence, 4. Skin integrity,
        5. Mobility, 6. Communication, 7. Psychological/Emotional,
        8. Cognition, 9. Behaviour, 10. Drug therapies,
        11. Altered states of consciousness, 12. Other significant needs
        
        CHC is available for people with a "primary health need" - meaning their
        main need for care is health-related rather than social care.
        
        Args:
            questionnaire: Professional questionnaire response
        
        Returns:
            Dict with CHC eligibility assessment including DST domain scores
        """
        medical_needs = questionnaire.get('section_3_medical_needs', {})
        safety_needs = questionnaire.get('section_4_safety_special_needs', {})
        
        # Extract medical conditions
        conditions = medical_needs.get('q9_medical_conditions', [])
        mobility_level = medical_needs.get('q10_mobility_level', '')
        medication_management = medical_needs.get('q11_medication_management', '')
        care_types = medical_needs.get('q8_care_types', [])
        fall_history = safety_needs.get('q13_fall_history', '')
        age_range = medical_needs.get('q12_age_range', '')
        
        # Assess DST domains (Decision Support Tool framework)
        dst_domains = self._assess_dst_domains(
            conditions, mobility_level, medication_management,
            care_types, fall_history, age_range
        )
        
        # Calculate overall severity score based on DST
        severity_score = self._calculate_dst_severity_score(dst_domains)
        
        # Calculate primary health need indicators
        primary_health_need_score = self._assess_primary_health_need(dst_domains, conditions, care_types)
        
        # Calculate eligibility probability based on DST framework
        eligibility_probability, eligibility_level, recommendation = self._calculate_chc_probability(
            severity_score, primary_health_need_score, dst_domains
        )
        
        # Identify key factors
        key_factors = self._identify_chc_factors(conditions, care_types, mobility_level, medication_management, fall_history)
        
        # Calculate potential savings
        estimated_savings = self._calculate_chc_savings(eligibility_probability)
        
        # Generate detailed assessment
        assessment_details = self._generate_chc_assessment_details(
            dst_domains, eligibility_level, primary_health_need_score
        )
        
        return {
            'eligibility_probability': round(eligibility_probability * 100, 1),  # As percentage
            'eligibility_level': eligibility_level,
            'severity_score': round(severity_score, 2),
            'primary_health_need_score': round(primary_health_need_score, 2),
            'recommendation': recommendation,
            'key_factors': key_factors,
            'dst_domains': dst_domains,  # Detailed DST domain assessments
            'assessment_details': assessment_details,
            'next_steps': self._get_chc_next_steps(eligibility_level),
            'estimated_annual_savings': estimated_savings,
            'important_notes': [
                'CHC eligibility requires a "primary health need" assessment',
                'Full assessment uses NHS Decision Support Tool (DST)',
                'Assessment is free and can be requested from your local ICB (Integrated Care Board)',
                'Even if CHC is not approved, you may qualify for NHS-funded nursing care (FNC)',
                'You can appeal CHC decisions if you disagree with the outcome'
            ]
        }
    
    def _assess_dst_domains(
        self,
        conditions: List[str],
        mobility_level: str,
        medication_management: str,
        care_types: List[str],
        fall_history: str,
        age_range: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Assess 12 DST care domains based on questionnaire responses
        
        Returns domain assessments with severity levels (A=priority, B=severe, C=moderate/low)
        """
        domains = {}
        
        # 1. Breathing
        breathing_severity = 'C'  # Default: no needs
        if 'heart_conditions' in conditions:
            breathing_severity = 'B'  # Severe - heart conditions affect breathing
        if any(c in conditions for c in ['dementia_alzheimers']):  # Advanced dementia can affect breathing
            if breathing_severity == 'C':
                breathing_severity = 'B'
        domains['breathing'] = {
            'severity': breathing_severity,
            'level': self._severity_to_level(breathing_severity),
            'description': self._get_domain_description('breathing', breathing_severity),
            'score': self._severity_to_score(breathing_severity)
        }
        
        # 2. Nutrition
        nutrition_severity = 'C'
        if 'diabetes' in conditions:
            nutrition_severity = 'B'  # Requires careful monitoring
        domains['nutrition'] = {
            'severity': nutrition_severity,
            'level': self._severity_to_level(nutrition_severity),
            'description': self._get_domain_description('nutrition', nutrition_severity),
            'score': self._severity_to_score(nutrition_severity)
        }
        
        # 3. Continence
        continence_severity = 'C'
        if 'dementia_alzheimers' in conditions:
            continence_severity = 'B'  # Dementia often affects continence
        domains['continence'] = {
            'severity': continence_severity,
            'level': self._severity_to_level(continence_severity),
            'description': self._get_domain_description('continence', continence_severity),
            'score': self._severity_to_score(continence_severity)
        }
        
        # 4. Skin integrity
        skin_severity = 'C'
        if mobility_level == 'wheelchair_permanent':
            skin_severity = 'B'  # Immobility increases pressure sore risk
        if fall_history in ['3_plus_or_serious_injuries', 'high_risk_of_falling']:
            skin_severity = 'B'
        domains['skin_integrity'] = {
            'severity': skin_severity,
            'level': self._severity_to_level(skin_severity),
            'description': self._get_domain_description('skin_integrity', skin_severity),
            'score': self._severity_to_score(skin_severity)
        }
        
        # 5. Mobility
        mobility_severity = 'C'
        if mobility_level == 'wheelchair_permanent':
            mobility_severity = 'A'  # Priority - permanent wheelchair use
        elif mobility_level == 'wheelchair_sometimes':
            mobility_severity = 'B'
        elif 'mobility_problems' in conditions:
            mobility_severity = 'B'
        domains['mobility'] = {
            'severity': mobility_severity,
            'level': self._severity_to_level(mobility_severity),
            'description': self._get_domain_description('mobility', mobility_severity),
            'score': self._severity_to_score(mobility_severity)
        }
        
        # 6. Communication
        communication_severity = 'C'
        if 'dementia_alzheimers' in conditions:
            communication_severity = 'B'  # Dementia affects communication
        domains['communication'] = {
            'severity': communication_severity,
            'level': self._severity_to_level(communication_severity),
            'description': self._get_domain_description('communication', communication_severity),
            'score': self._severity_to_score(communication_severity)
        }
        
        # 7. Psychological/Emotional needs
        psychological_severity = 'C'
        if 'dementia_alzheimers' in conditions:
            psychological_severity = 'A'  # Priority - dementia is psychological condition
        domains['psychological_emotional'] = {
            'severity': psychological_severity,
            'level': self._severity_to_level(psychological_severity),
            'description': self._get_domain_description('psychological_emotional', psychological_severity),
            'score': self._severity_to_score(psychological_severity)
        }
        
        # 8. Cognition
        cognition_severity = 'C'
        if 'dementia_alzheimers' in conditions:
            cognition_severity = 'A'  # Priority - dementia is cognitive condition
        domains['cognition'] = {
            'severity': cognition_severity,
            'level': self._severity_to_level(cognition_severity),
            'description': self._get_domain_description('cognition', cognition_severity),
            'score': self._severity_to_score(cognition_severity)
        }
        
        # 9. Behaviour
        behaviour_severity = 'C'
        if 'dementia_alzheimers' in conditions:
            behaviour_severity = 'B'  # Dementia can cause challenging behaviour
        domains['behaviour'] = {
            'severity': behaviour_severity,
            'level': self._severity_to_level(behaviour_severity),
            'description': self._get_domain_description('behaviour', behaviour_severity),
            'score': self._severity_to_score(behaviour_severity)
        }
        
        # 10. Drug therapies and medication
        medication_severity = 'C'
        if medication_management == 'many_complex_routine':
            medication_severity = 'A'  # Priority - complex medication needs
        elif medication_management == 'several_simple_routine':
            medication_severity = 'B'
        if 'diabetes' in conditions or 'heart_conditions' in conditions:
            if medication_severity == 'C':
                medication_severity = 'B'
        domains['drug_therapies'] = {
            'severity': medication_severity,
            'level': self._severity_to_level(medication_severity),
            'description': self._get_domain_description('drug_therapies', medication_severity),
            'score': self._severity_to_score(medication_severity)
        }
        
        # 11. Altered states of consciousness
        consciousness_severity = 'C'
        if 'dementia_alzheimers' in conditions:
            consciousness_severity = 'B'  # Dementia can cause altered consciousness
        domains['altered_consciousness'] = {
            'severity': consciousness_severity,
            'level': self._severity_to_level(consciousness_severity),
            'description': self._get_domain_description('altered_consciousness', consciousness_severity),
            'score': self._severity_to_score(consciousness_severity)
        }
        
        # 12. Other significant care needs
        other_needs_severity = 'C'
        if len(conditions) >= 3:
            other_needs_severity = 'B'  # Multiple conditions = complex needs
        if 'medical_nursing' in care_types:
            other_needs_severity = 'A'  # Priority - nursing care required
        if fall_history in ['3_plus_or_serious_injuries', 'high_risk_of_falling']:
            if other_needs_severity == 'C':
                other_needs_severity = 'B'
        domains['other_significant_needs'] = {
            'severity': other_needs_severity,
            'level': self._severity_to_level(other_needs_severity),
            'description': self._get_domain_description('other_significant_needs', other_needs_severity),
            'score': self._severity_to_score(other_needs_severity)
        }
        
        return domains
    
    def _severity_to_level(self, severity: str) -> str:
        """Convert DST severity (A/B/C) to descriptive level"""
        mapping = {
            'A': 'Priority/Severe',
            'B': 'Severe/High',
            'C': 'Moderate/Low/No Needs'
        }
        return mapping.get(severity, 'Unknown')
    
    def _severity_to_score(self, severity: str) -> float:
        """Convert DST severity to numeric score (0-1)"""
        mapping = {
            'A': 1.0,  # Priority
            'B': 0.6,  # Severe
            'C': 0.2   # Moderate/Low
        }
        return mapping.get(severity, 0.0)
    
    def _get_domain_description(self, domain: str, severity: str) -> str:
        """Get description for DST domain based on severity"""
        descriptions = {
            'breathing': {
                'A': 'Severe breathing difficulties requiring constant monitoring',
                'B': 'Breathing issues requiring regular monitoring and intervention',
                'C': 'No significant breathing difficulties'
            },
            'nutrition': {
                'A': 'Severe nutritional problems requiring specialist intervention',
                'B': 'Nutritional needs requiring monitoring and support',
                'C': 'Able to maintain adequate nutrition with minimal support'
            },
            'continence': {
                'A': 'Complete incontinence requiring full management',
                'B': 'Partial incontinence requiring regular assistance',
                'C': 'Able to manage continence independently'
            },
            'skin_integrity': {
                'A': 'High risk of pressure sores requiring constant monitoring',
                'B': 'Moderate risk requiring regular repositioning and care',
                'C': 'Low risk, skin integrity maintained'
            },
            'mobility': {
                'A': 'Completely immobile, requires full assistance',
                'B': 'Significantly limited mobility, requires substantial assistance',
                'C': 'Able to move independently or with minimal assistance'
            },
            'communication': {
                'A': 'Unable to communicate effectively',
                'B': 'Significant communication difficulties',
                'C': 'Able to communicate needs effectively'
            },
            'psychological_emotional': {
                'A': 'Severe psychological/emotional needs requiring specialist care',
                'B': 'Significant psychological/emotional support required',
                'C': 'Minimal psychological/emotional support needs'
            },
            'cognition': {
                'A': 'Severe cognitive impairment',
                'B': 'Moderate cognitive difficulties',
                'C': 'Able to make decisions independently'
            },
            'behaviour': {
                'A': 'Challenging behaviour requiring specialist management',
                'B': 'Some challenging behaviour requiring support',
                'C': 'No significant challenging behaviour'
            },
            'drug_therapies': {
                'A': 'Complex medication regime requiring specialist management',
                'B': 'Multiple medications requiring regular monitoring',
                'C': 'Simple medication needs or no medication'
            },
            'altered_consciousness': {
                'A': 'Frequent altered states requiring constant monitoring',
                'B': 'Occasional altered states requiring monitoring',
                'C': 'No altered states of consciousness'
            },
            'other_significant_needs': {
                'A': 'Multiple complex care needs requiring specialist intervention',
                'B': 'Several significant care needs',
                'C': 'Standard care needs'
            }
        }
        return descriptions.get(domain, {}).get(severity, 'Assessment required')
    
    def _calculate_dst_severity_score(self, dst_domains: Dict[str, Dict[str, Any]]) -> float:
        """Calculate overall severity score from DST domains"""
        total_score = sum(domain.get('score', 0) for domain in dst_domains.values())
        max_possible_score = len(dst_domains) * 1.0  # All domains at priority level
        return min(total_score / max_possible_score, 1.0)
    
    def _assess_primary_health_need(self, dst_domains: Dict[str, Dict[str, Any]], conditions: List[str], care_types: List[str]) -> float:
        """
        Assess "primary health need" - key CHC eligibility criterion
        
        Primary health need means the main need is health-related, not social care.
        Indicators: multiple priority/severe domains, nursing care requirement, complex medical needs.
        """
        score = 0.0
        
        # Count priority/severe domains (A or B)
        priority_domains = sum(1 for d in dst_domains.values() if d.get('severity') in ['A', 'B'])
        if priority_domains >= 4:
            score += 0.4  # Multiple severe domains = health need
        elif priority_domains >= 2:
            score += 0.2
        
        # Nursing care requirement strongly indicates health need
        if 'medical_nursing' in care_types:
            score += 0.3
        
        # Complex medical conditions
        if len(conditions) >= 3:
            score += 0.2
        elif len(conditions) >= 2:
            score += 0.1
        
        # Specific conditions that indicate health need
        if 'dementia_alzheimers' in conditions:
            score += 0.15
        if 'heart_conditions' in conditions:
            score += 0.15
        
        return min(score, 1.0)
    
    def _calculate_chc_probability(
        self,
        severity_score: float,
        primary_health_need_score: float,
        dst_domains: Dict[str, Dict[str, Any]]
    ) -> tuple[float, str, str]:
        """
        Calculate CHC eligibility probability based on DST assessment
        
        Returns: (probability, level, recommendation)
        """
        # Count priority (A) domains
        priority_count = sum(1 for d in dst_domains.values() if d.get('severity') == 'A')
        severe_count = sum(1 for d in dst_domains.values() if d.get('severity') == 'B')
        
        # High eligibility indicators
        if priority_count >= 2 or (priority_count >= 1 and severe_count >= 3):
            if primary_health_need_score >= 0.7:
                return (0.80, 'high', 'Strong candidate for CHC. Multiple priority domains indicate primary health need. Urgently request full DST assessment.')
            else:
                return (0.65, 'high', 'Strong candidate for CHC assessment. Multiple severe care domains identified. Request full DST assessment.')
        
        elif priority_count >= 1 or (severe_count >= 3):
            if primary_health_need_score >= 0.6:
                return (0.55, 'moderate_high', 'Good chance of CHC eligibility. Several severe domains and health needs identified. Worth pursuing full assessment.')
            else:
                return (0.40, 'moderate', 'Moderate chance of CHC eligibility. Some severe care needs identified. Consider requesting assessment.')
        
        elif severe_count >= 2:
            if primary_health_need_score >= 0.5:
                return (0.30, 'moderate_low', 'Possible CHC eligibility. Some health-related needs identified. May qualify for joint funding or NHS-funded nursing care.')
            else:
                return (0.20, 'low', 'Lower chance of CHC eligibility. May qualify for NHS-funded nursing care (FNC) if nursing care required.')
        
        else:
            return (0.10, 'very_low', 'Unlikely to qualify for full CHC. May still qualify for NHS-funded nursing care (FNC) if nursing care is required. Focus on LA funding or self-funding.')
    
    def _generate_chc_assessment_details(
        self,
        dst_domains: Dict[str, Dict[str, Any]],
        eligibility_level: str,
        primary_health_need_score: float
    ) -> Dict[str, Any]:
        """Generate detailed assessment information"""
        priority_domains = [name for name, d in dst_domains.items() if d.get('severity') == 'A']
        severe_domains = [name for name, d in dst_domains.items() if d.get('severity') == 'B']
        
        return {
            'priority_domains_count': len(priority_domains),
            'severe_domains_count': len(severe_domains),
            'priority_domains': priority_domains,
            'severe_domains': severe_domains,
            'primary_health_need_indicated': primary_health_need_score >= 0.5,
            'assessment_framework': 'NHS Decision Support Tool (DST)',
            'domains_assessed': len(dst_domains),
            'next_assessment_stage': 'Full DST assessment by ICB (Integrated Care Board)' if eligibility_level in ['high', 'moderate_high'] else 'CHC Checklist assessment'
        }
    
    def _get_chc_next_steps(self, eligibility_level: str) -> List[str]:
        """Get next steps based on eligibility level"""
        base_steps = [
            'Contact your local ICB (Integrated Care Board) - previously CCG',
            'Request CHC Checklist assessment (initial screening)',
            'Gather medical evidence from GP, specialists, and care providers',
            'Keep detailed records of all care needs and medical conditions'
        ]
        
        if eligibility_level in ['high', 'moderate_high']:
            return base_steps + [
                'Prepare for full Decision Support Tool (DST) assessment',
                'Consider getting support from CHC advocacy services',
                'Request assessment within 28 days if in hospital or care home',
                'Be prepared to appeal if initial assessment is negative'
            ]
        elif eligibility_level == 'moderate':
            return base_steps + [
                'Consider NHS-funded nursing care (FNC) as alternative',
                'Prepare evidence showing health needs vs social care needs',
                'May qualify for joint funding (CHC + LA)'
            ]
        else:
            return base_steps + [
                'Consider NHS-funded nursing care (FNC) if nursing care required',
                'Focus on LA funding assessment',
                'Explore other funding options (DPA, self-funding)'
            ]
    
    def _identify_chc_factors(
        self,
        conditions: List[str],
        care_types: List[str],
        mobility_level: str,
        medication_management: str,
        fall_history: str
    ) -> List[str]:
        """Identify key factors affecting CHC eligibility"""
        factors = []
        
        if 'dementia_alzheimers' in conditions:
            factors.append('Dementia/Alzheimer\'s condition')
        if 'heart_conditions' in conditions:
            factors.append('Heart conditions requiring monitoring')
        if 'medical_nursing' in care_types:
            factors.append('Nursing care requirement')
        if mobility_level == 'wheelchair_permanent':
            factors.append('Permanent wheelchair use')
        if medication_management == 'many_complex_routine':
            factors.append('Complex medication management')
        if fall_history in ['3_plus_or_serious_injuries', 'high_risk_of_falling']:
            factors.append('High fall risk')
        if len(conditions) >= 3:
            factors.append('Multiple complex medical conditions')
        
        return factors if factors else ['Standard care needs']
    
    def _calculate_chc_savings(self, probability: float) -> Dict[str, Any]:
        """Calculate potential annual savings if CHC approved"""
        # Average weekly cost for nursing care
        weekly_cost = self.UK_AVERAGE_WEEKLY_COSTS['nursing']
        annual_cost = weekly_cost * 52
        
        # CHC covers 100% of care costs
        potential_annual_savings = annual_cost * probability
        
        return {
            'if_approved': round(annual_cost, 2),
            'probability_adjusted': round(potential_annual_savings, 2),
            'weekly_equivalent': round(potential_annual_savings / 52, 2)
        }
    
    def calculate_la_funding_availability(
        self,
        questionnaire: Dict[str, Any],
        estimated_assets: Optional[float] = None,
        estimated_income: Optional[float] = None,
        property_value: Optional[float] = None,
        property_occupied_by_spouse: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Calculate Local Authority funding availability
        
        LA funding is means-tested based on capital and income thresholds (2024-2025):
        - Capital threshold: £23,250 (below = full funding, above = tariff income calculated)
        - Income threshold: £189.50/week (below = full funding, above = contribution required)
        - Property disregarded if occupied by spouse/partner or relative over 60/disabled
        
        Args:
            questionnaire: Professional questionnaire response
            estimated_assets: Estimated capital/assets (savings, investments, excluding property if disregarded)
            estimated_income: Estimated weekly income (pensions, benefits)
            property_value: Estimated property value (if applicable)
            property_occupied_by_spouse: Whether property is occupied by spouse/partner/relative
        
        Returns:
            Dict with detailed LA funding assessment
        """
        location_budget = questionnaire.get('section_2_location_budget', {})
        budget_preference = location_budget.get('q7_budget', '')
        
        # Default estimates if not provided, and ensure they are numbers
        if estimated_assets is None:
            # Estimate based on budget preference
            if 'over_7000' in budget_preference:
                estimated_assets = 500000  # Higher budget suggests more assets
            elif '5000_7000' in budget_preference:
                estimated_assets = 300000
            elif '3000_5000' in budget_preference:
                estimated_assets = 150000
            else:
                estimated_assets = 50000
        else:
            # Ensure it's a number
            try:
                estimated_assets = float(estimated_assets) if estimated_assets is not None else 50000
            except (ValueError, TypeError):
                estimated_assets = 50000
        
        if estimated_income is None:
            # Default UK state pension + benefits average
            estimated_income = 250.0  # £250/week average
        else:
            # Ensure it's a number
            try:
                estimated_income = float(estimated_income) if estimated_income is not None else 250.0
            except (ValueError, TypeError):
                estimated_income = 250.0
        
        if property_value is None:
            # Estimate property value based on budget
            if 'over_7000' in budget_preference:
                property_value = 400000
            elif '5000_7000' in budget_preference:
                property_value = 250000
            elif '3000_5000' in budget_preference:
                property_value = 150000
            else:
                property_value = 100000
        else:
            # Ensure it's a number
            try:
                property_value = float(property_value) if property_value is not None else 100000
            except (ValueError, TypeError):
                property_value = 100000
        
        if property_occupied_by_spouse is None:
            property_occupied_by_spouse = True  # Default assumption
        
        # Calculate funding eligibility
        capital_threshold = self.LA_FUNDING_THRESHOLDS['capital_threshold']
        income_threshold = self.LA_FUNDING_THRESHOLDS['income_threshold']
        
        # Property assessment - property disregarded if occupied by spouse/partner/relative over 60/disabled
        property_disregarded = property_occupied_by_spouse
        # Ensure property_value is a number
        property_value = float(property_value) if property_value is not None else 0.0
        if property_disregarded:
            property_assessment = f'Property (£{property_value:,.0f}) disregarded - occupied by spouse/partner/relative'
            assessable_property_value = 0
        else:
            property_assessment = f'Property (£{property_value:,.0f}) may be included in assessment'
            assessable_property_value = property_value
        
        # Total assessable capital = assets + property (if not disregarded)
        # Ensure all values are numbers
        estimated_assets = float(estimated_assets) if estimated_assets is not None else 0.0
        assessable_property_value = float(assessable_property_value) if assessable_property_value is not None else 0.0
        total_assessable_capital = estimated_assets + assessable_property_value
        
        # Capital assessment
        if total_assessable_capital <= capital_threshold:
            capital_eligible = True
            capital_assessment = f'Below threshold (£{capital_threshold:,}) - eligible for LA funding'
            capital_contribution = 0
            excess_capital = 0
            tariff_income = 0
        else:
            capital_eligible = False
            excess_capital = total_assessable_capital - capital_threshold
            # Calculate tariff income: £1 per £250 of excess capital above threshold
            tariff_income = excess_capital / 250
            capital_assessment = f'Above threshold - tariff income: £{tariff_income:.2f}/week from excess capital (£{excess_capital:,.0f})'
            capital_contribution = tariff_income
        
        # Income assessment
        # Ensure all values are numbers
        estimated_income = float(estimated_income) if estimated_income is not None else 0.0
        capital_contribution = float(capital_contribution) if capital_contribution is not None else 0.0
        total_assessed_income = estimated_income + capital_contribution
        if total_assessed_income <= income_threshold:
            income_eligible = True
            income_assessment = f'Below threshold (£{income_threshold:.2f}/week) - full LA funding available'
            income_contribution = 0
            excess_income = 0
        else:
            income_eligible = False
            excess_income = total_assessed_income - income_threshold
            income_assessment = f'Above threshold - contribution required: £{excess_income:.2f}/week'
            income_contribution = excess_income
        
        # Calculate weekly contribution
        # Ensure all values are numbers
        income_contribution = float(income_contribution) if income_contribution is not None else 0.0
        capital_contribution = float(capital_contribution) if capital_contribution is not None else 0.0
        total_weekly_contribution = income_contribution + capital_contribution
        
        # Determine funding availability and level
        if capital_eligible and income_eligible:
            funding_available = True
            funding_level = 'full'
            la_contribution_pct = 100
            self_contribution_pct = 0
            funding_explanation = 'Full LA funding available - both capital and income below thresholds'
        elif total_weekly_contribution < 100:  # Small contribution
            funding_available = True
            funding_level = 'substantial'
            # Estimate LA covers 85-95% for substantial funding
            la_contribution_pct = 90
            self_contribution_pct = 10
            funding_explanation = f'Substantial LA funding available - small weekly contribution (£{total_weekly_contribution:.2f})'
        elif total_weekly_contribution < 300:  # Moderate contribution
            funding_available = True
            funding_level = 'partial'
            # Estimate LA covers 60-80% for partial funding
            la_contribution_pct = 70
            self_contribution_pct = 30
            funding_explanation = f'Partial LA funding available - moderate weekly contribution (£{total_weekly_contribution:.2f})'
        elif total_weekly_contribution < 500:  # Higher contribution
            funding_available = True
            funding_level = 'minimal'
            la_contribution_pct = 40
            self_contribution_pct = 60
            funding_explanation = f'Minimal LA funding available - significant weekly contribution (£{total_weekly_contribution:.2f})'
        else:
            funding_available = False
            funding_level = 'none'
            la_contribution_pct = 0
            self_contribution_pct = 100
            funding_explanation = 'No LA funding available - contribution exceeds typical care costs'
        
        # Calculate annual costs
        avg_weekly_cost = self.UK_AVERAGE_WEEKLY_COSTS.get('nursing', 1200)
        annual_cost = avg_weekly_cost * 52
        la_annual_contribution = annual_cost * (la_contribution_pct / 100)
        self_annual_contribution = annual_cost * (self_contribution_pct / 100)
        
        # Generate detailed breakdown
        assessment_breakdown = self._generate_la_assessment_breakdown(
            total_assessable_capital, capital_threshold, excess_capital,
            estimated_income, income_threshold, excess_income,
            property_disregarded, property_value
        )
        
        return {
            'funding_available': funding_available,
            'funding_level': funding_level,
            'funding_explanation': funding_explanation,
            'property_assessment': {
                'property_value': property_value,
                'disregarded': property_disregarded,
                'assessment': property_assessment,
                'assessable_value': assessable_property_value
            },
            'capital_assessment': {
                'total_assessable_capital': round(total_assessable_capital, 2),
                'assets': estimated_assets,
                'property_value': assessable_property_value,
                'threshold': capital_threshold,
                'excess_capital': round(excess_capital, 2) if excess_capital > 0 else 0,
                'eligible': capital_eligible,
                'assessment': capital_assessment,
                'tariff_income': round(tariff_income, 2) if tariff_income > 0 else 0
            },
            'income_assessment': {
                'weekly_income': estimated_income,
                'tariff_income_from_capital': round(capital_contribution, 2),
                'total_assessed_income': round(total_assessed_income, 2),
                'threshold': income_threshold,
                'excess_income': round(excess_income, 2) if excess_income > 0 else 0,
                'eligible': income_eligible,
                'assessment': income_assessment,
                'contribution_required': round(income_contribution, 2) if income_contribution > 0 else 0
            },
            'funding_split': {
                'la_contribution_percent': la_contribution_pct,
                'self_contribution_percent': self_contribution_pct,
                'estimated_weekly_contribution': round(total_weekly_contribution, 2),
                'estimated_annual_contribution': round(self_annual_contribution, 2),
                'la_weekly_contribution': round(la_annual_contribution / 52, 2),
                'la_annual_contribution': round(la_annual_contribution, 2)
            },
            'assessment_breakdown': assessment_breakdown,
            'important_notes': [
                'Property is disregarded if occupied by spouse/partner or relative over 60/disabled',
                'Capital threshold: £23,250 (2024-2025)',
                'Income threshold: £189.50/week (2024-2025)',
                'Tariff income: £1 per £250 of excess capital above threshold',
                'You can still receive LA funding even if above thresholds - you pay the difference',
                'Care needs assessment is separate from financial assessment - both required'
            ],
            'next_steps': self._get_la_funding_next_steps(funding_level, funding_available)
        }
    
    def _generate_la_assessment_breakdown(
        self,
        total_capital: float,
        capital_threshold: float,
        excess_capital: float,
        weekly_income: float,
        income_threshold: float,
        excess_income: float,
        property_disregarded: bool,
        property_value: float
    ) -> Dict[str, Any]:
        """Generate detailed breakdown of LA funding assessment"""
        return {
            'capital_calculation': {
                'step1_total_capital': round(total_capital, 2),
                'step2_threshold': capital_threshold,
                'step3_excess': round(excess_capital, 2) if excess_capital > 0 else 0,
                'step4_tariff_income': round(excess_capital / 250, 2) if excess_capital > 0 else 0,
                'explanation': f'Excess capital (£{excess_capital:,.0f}) ÷ 250 = tariff income'
            },
            'income_calculation': {
                'step1_weekly_income': round(weekly_income, 2),
                'step2_tariff_income': round(excess_capital / 250, 2) if excess_capital > 0 else 0,
                'step3_total_assessed': round(weekly_income + (excess_capital / 250 if excess_capital > 0 else 0), 2),
                'step4_threshold': income_threshold,
                'step5_excess': round(excess_income, 2) if excess_income > 0 else 0,
                'explanation': 'Total assessed income - threshold = contribution required'
            },
            'property_status': {
                'disregarded': property_disregarded,
                'value': property_value,
                'included_in_assessment': not property_disregarded,
                'reason': 'Property disregarded if occupied by spouse/partner/relative over 60/disabled' if property_disregarded else 'Property may be included in capital assessment'
            }
        }
    
    def _get_la_funding_next_steps(self, funding_level: str, funding_available: bool) -> List[str]:
        """Get next steps based on LA funding level"""
        base_steps = [
            'Contact your local authority social services department',
            'Request a care needs assessment (free, separate from financial assessment)',
            'Request a financial assessment (means test)',
            'Gather evidence: bank statements, pension statements, property documents',
            'If property occupied by spouse/partner, provide evidence'
        ]
        
        if funding_available:
            if funding_level == 'full':
                return base_steps + [
                    'You qualify for full LA funding - no financial contribution required',
                    'LA will arrange care and pay care home directly',
                    'You may still need to contribute from income (pension) if above threshold'
                ]
            elif funding_level in ['substantial', 'partial']:
                return base_steps + [
                    'You qualify for LA funding with contribution',
                    'LA will arrange care and pay their share directly',
                    'You will need to pay your contribution weekly/monthly',
                    'Consider DPA if you need to defer property sale'
                ]
            else:
                return base_steps + [
                    'You qualify for minimal LA funding',
                    'Consider all funding options: CHC, LA, DPA, self-funding',
                    'May be worth exploring if care costs exceed your contribution'
                ]
        else:
            return base_steps + [
                'You do not qualify for LA funding based on current assessment',
                'Consider self-funding or DPA (Deferred Payment Agreement)',
                'Reassess if circumstances change (assets decrease, income changes)',
                'Still worth requesting assessment - thresholds and calculations vary by LA'
            ]
    
    def calculate_dpa_considerations(
        self,
        questionnaire: Dict[str, Any],
        property_value: Optional[float] = None,
        outstanding_mortgage: Optional[float] = None,
        estimated_weekly_care_cost: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate Deferred Payment Agreement (DPA) considerations
        
        DPA allows people to delay paying for care costs until they sell their property
        or after death, using their property as security.
        
        Key features:
        - Minimum equity: £14,250
        - Maximum deferral: 70% of property equity
        - Interest rate: 2.5% per annum (2024-2025)
        - Admin fee: £144 per year
        - Repayment: On property sale or death
        
        Args:
            questionnaire: Professional questionnaire response
            property_value: Estimated property value
            outstanding_mortgage: Outstanding mortgage amount
            estimated_weekly_care_cost: Estimated weekly care cost (for projections)
        
        Returns:
            Dict with detailed DPA assessment
        """
        location_budget = questionnaire.get('section_2_location_budget', {})
        budget_preference = location_budget.get('q7_budget', '')
        
        # Estimate property value if not provided
        if property_value is None:
            if 'over_7000' in budget_preference:
                property_value = 400000
            elif '5000_7000' in budget_preference:
                property_value = 250000
            elif '3000_5000' in budget_preference:
                property_value = 150000
            else:
                property_value = 100000
        else:
            # Ensure it's a number
            try:
                property_value = float(property_value) if property_value is not None else 100000
            except (ValueError, TypeError):
                property_value = 100000
        
        if outstanding_mortgage is None:
            outstanding_mortgage = 0  # Assume no mortgage
        else:
            # Ensure it's a number
            try:
                outstanding_mortgage = float(outstanding_mortgage) if outstanding_mortgage is not None else 0.0
            except (ValueError, TypeError):
                outstanding_mortgage = 0.0
        
        if estimated_weekly_care_cost is None:
            estimated_weekly_care_cost = self.UK_AVERAGE_WEEKLY_COSTS.get('nursing', 1200)
        else:
            # Ensure it's a number
            try:
                estimated_weekly_care_cost = float(estimated_weekly_care_cost) if estimated_weekly_care_cost is not None else 1200.0
            except (ValueError, TypeError):
                estimated_weekly_care_cost = 1200.0
        
        # Calculate equity - ensure all values are numbers
        property_value = float(property_value) if property_value is not None else 0.0
        outstanding_mortgage = float(outstanding_mortgage) if outstanding_mortgage is not None else 0.0
        equity = property_value - outstanding_mortgage
        
        # DPA eligibility
        minimum_equity = self.DPA_PARAMETERS['minimum_equity']
        maximum_deferral_pct = self.DPA_PARAMETERS['maximum_deferral']
        interest_rate = self.DPA_PARAMETERS['interest_rate']
        admin_fee = self.DPA_PARAMETERS['administration_fee']
        
        if equity < minimum_equity:
            dpa_eligible = False
            dpa_assessment = f'Insufficient equity (£{equity:,.0f}) - minimum £{minimum_equity:,} required'
            available_deferral = 0
            equity_shortfall = minimum_equity - equity
        else:
            dpa_eligible = True
            available_deferral = equity * maximum_deferral_pct
            dpa_assessment = f'DPA available - up to £{available_deferral:,.0f} can be deferred (70% of equity)'
            equity_shortfall = 0
        
        # Calculate costs and projections
        annual_care_cost = estimated_weekly_care_cost * 52
        
        if dpa_eligible:
            # Calculate how long DPA can cover costs
            years_coverable = available_deferral / annual_care_cost if annual_care_cost > 0 else 0
            
            # Calculate interest costs for deferring annual cost
            annual_interest = annual_care_cost * interest_rate
            weekly_interest = annual_interest / 52
            weekly_admin_fee = admin_fee / 52
            
            # Total weekly cost if deferring
            total_weekly_cost_deferred = weekly_interest + weekly_admin_fee
            
            # Calculate cumulative costs over different time periods
            projections = []
            for years in [1, 2, 3, 5]:
                if years <= years_coverable:
                    deferred_amount = annual_care_cost * years
                    interest_accrued = deferred_amount * interest_rate * years
                    admin_fees_total = admin_fee * years
                    total_cost = deferred_amount + interest_accrued + admin_fees_total
                    projections.append({
                        'years': years,
                        'deferred_amount': round(deferred_amount, 2),
                        'interest_accrued': round(interest_accrued, 2),
                        'admin_fees': round(admin_fees_total, 2),
                        'total_cost': round(total_cost, 2),
                        'within_limit': True
                    })
                else:
                    projections.append({
                        'years': years,
                        'deferred_amount': round(available_deferral, 2),
                        'interest_accrued': round(available_deferral * interest_rate * years, 2),
                        'admin_fees': round(admin_fee * years, 2),
                        'total_cost': round(available_deferral + (available_deferral * interest_rate * years) + (admin_fee * years), 2),
                        'within_limit': False,
                        'note': f'DPA limit reached after {years_coverable:.1f} years'
                    })
        else:
            years_coverable = 0
            annual_interest = 0
            weekly_interest = 0
            weekly_admin_fee = 0
            total_weekly_cost_deferred = 0
            projections = []
        
        # Calculate savings vs immediate payment
        if dpa_eligible:
            # If paying immediately, full cost upfront
            # With DPA, costs deferred but interest accrues
            immediate_payment_5yr = annual_care_cost * 5
            dpa_payment_5yr_raw = projections[3].get('total_cost', 0) if len(projections) > 3 else 0
            try:
                dpa_payment_5yr = float(dpa_payment_5yr_raw) if dpa_payment_5yr_raw is not None else 0.0
            except (ValueError, TypeError):
                dpa_payment_5yr = 0.0
            
            savings_vs_immediate = immediate_payment_5yr - dpa_payment_5yr if dpa_payment_5yr > 0 else 0
        else:
            immediate_payment_5yr = annual_care_cost * 5
            dpa_payment_5yr = 0
            savings_vs_immediate = 0
        
        return {
            'dpa_eligible': dpa_eligible,
            'property_assessment': {
                'property_value': property_value,
                'outstanding_mortgage': outstanding_mortgage,
                'equity': equity,
                'equity_percent': round((equity / property_value * 100), 1) if property_value > 0 else 0
            },
            'eligibility': {
                'minimum_equity_required': minimum_equity,
                'equity_shortfall': round(equity_shortfall, 2) if equity_shortfall > 0 else 0,
                'meets_minimum': equity >= minimum_equity,
                'assessment': dpa_assessment
            },
            'deferral_limits': {
                'maximum_deferral_percent': maximum_deferral_pct * 100,
                'available_deferral': round(available_deferral, 2) if dpa_eligible else 0,
                'years_coverable': round(years_coverable, 1) if dpa_eligible else 0,
                'explanation': f'Can defer up to {maximum_deferral_pct * 100}% of equity (£{available_deferral:,.0f})'
            },
            'costs': {
                'interest_rate_percent': interest_rate * 100,
                'administration_fee_annual': admin_fee,
                'administration_fee_weekly': round(admin_fee / 52, 2),
                'annual_interest_example': round(annual_interest, 2) if dpa_eligible else 0,
                'weekly_interest_example': round(weekly_interest, 2) if dpa_eligible else 0,
                'total_weekly_cost_deferred': round(total_weekly_cost_deferred, 2) if dpa_eligible else 0
            },
            'projections': projections,
            'comparison': {
                'immediate_payment_5yr': round(immediate_payment_5yr, 2),
                'dpa_payment_5yr': round(dpa_payment_5yr, 2) if dpa_eligible else 0,
                'savings_vs_immediate': round(savings_vs_immediate, 2) if dpa_eligible else 0,
                'note': 'DPA allows deferral but interest accrues - compare with immediate payment options'
            },
            'key_considerations': [
                'Property must be your main residence (or former main residence)',
                'Interest accrues on deferred amount at 2.5% per annum',
                'Repayment required when property is sold or after death',
                'May affect inheritance planning - deferred amount deducted from estate',
                'Suitable for short to medium-term deferral (typically 2-5 years)',
                'Can combine with LA funding - defer your contribution portion',
                'Property can remain occupied by spouse/partner during deferral',
                'DPA can be cancelled if circumstances change'
            ],
            'important_notes': [
                'DPA is a loan secured against your property',
                'Interest rate is set by government (currently 2.5% p.a.)',
                'Admin fee of £144/year applies while DPA is active',
                'You can still receive LA funding alongside DPA',
                'Property sale proceeds used to repay deferred amount + interest',
                'If property not sold, repayment due after death from estate',
                'Consider impact on inheritance - beneficiaries receive less'
            ],
            'next_steps': self._get_dpa_next_steps(dpa_eligible, equity, minimum_equity)
        }
    
    def _get_dpa_next_steps(self, dpa_eligible: bool, equity: float, minimum_equity: float) -> List[str]:
        """Get next steps based on DPA eligibility"""
        base_steps = [
            'Contact your local authority to discuss DPA eligibility',
            'Obtain professional property valuation (required for DPA)',
            'Review DPA terms and conditions carefully',
            'Consider impact on inheritance and family planning',
            'Seek independent financial advice before committing'
        ]
        
        if dpa_eligible:
            return base_steps + [
                f'You have sufficient equity (£{equity:,.0f}) for DPA',
                'Apply for DPA through local authority',
                'Provide property documents and valuation',
                'Consider combining with LA funding if eligible',
                'Plan for repayment: property sale or estate settlement'
            ]
        else:
            shortfall = minimum_equity - equity
            return base_steps + [
                f'Insufficient equity - need additional £{shortfall:,.0f}',
                'Consider alternative funding: LA funding, self-funding, or family support',
                'Reassess if property value increases or mortgage decreases',
                'Explore other options: equity release, family loan, or downsizing'
            ]
    
    def calculate_funding_outcomes(
        self,
        questionnaire: Dict[str, Any],
        care_homes: List[Dict[str, Any]],
        chc_eligibility: Dict[str, Any],
        la_funding: Dict[str, Any],
        dpa_considerations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate estimated funding outcomes for each care home
        
        Args:
            questionnaire: Professional questionnaire response
            care_homes: List of care homes with pricing
            chc_eligibility: CHC eligibility assessment
            la_funding: LA funding assessment
            dpa_considerations: DPA considerations
        
        Returns:
            Dict with estimated funding outcomes for each home
        """
        medical_needs = questionnaire.get('section_3_medical_needs', {})
        care_types = medical_needs.get('q8_care_types', [])
        
        # Determine primary care type for cost estimation
        if 'medical_nursing' in care_types:
            care_type = 'nursing'
        elif 'specialised_dementia' in care_types:
            care_type = 'dementia'
        elif 'temporary_respite' in care_types:
            care_type = 'respite'
        else:
            care_type = 'residential'
        
        base_weekly_cost = self.UK_AVERAGE_WEEKLY_COSTS.get(care_type, 800)
        
        outcomes = []
        
        for home in care_homes:
            weekly_cost = home.get('weeklyPrice', base_weekly_cost)
            annual_cost = weekly_cost * 52
            
            # Scenario 1: CHC Funding (if eligible)
            # Ensure eligibility_probability is a number
            eligibility_probability = chc_eligibility.get('eligibility_probability', 0)
            try:
                eligibility_probability = float(eligibility_probability) if eligibility_probability is not None else 0.0
            except (ValueError, TypeError):
                eligibility_probability = 0.0
            
            chc_weekly_cost = 0 if eligibility_probability > 50 else weekly_cost
            chc_annual_cost = chc_weekly_cost * 52
            chc_probability = eligibility_probability / 100
            
            # Scenario 2: LA Funding
            if la_funding['funding_available']:
                la_contribution_pct = la_funding['funding_split']['la_contribution_percent']
                la_weekly_contribution = weekly_cost * (la_contribution_pct / 100)
                self_weekly_contribution = weekly_cost * (la_funding['funding_split']['self_contribution_percent'] / 100)
            else:
                la_weekly_contribution = 0
                self_weekly_contribution = weekly_cost
            
            # Scenario 3: Self-Funding
            self_funding_weekly = weekly_cost
            self_funding_annual = annual_cost
            
            # Scenario 4: DPA (if eligible)
            if dpa_considerations.get('dpa_eligible', False):
                # Get available_deferral from deferral_limits structure
                deferral_limits = dpa_considerations.get('deferral_limits', {})
                dpa_available = deferral_limits.get('available_deferral', 0)
                # Can defer up to available amount
                deferrable_annual = min(annual_cost, dpa_available) if dpa_available > 0 else 0
                dpa_weekly_deferred = deferrable_annual / 52 if deferrable_annual > 0 else 0
                costs = dpa_considerations.get('costs', {})
                interest_rate_pct = costs.get('interest_rate_percent', 2.5)
                dpa_interest_weekly = dpa_weekly_deferred * interest_rate_pct / 100 if dpa_weekly_deferred > 0 else 0
            else:
                dpa_weekly_deferred = 0
                dpa_interest_weekly = 0
            
            outcomes.append({
                'home_id': home.get('id'),
                'home_name': home.get('name'),
                'weekly_cost': weekly_cost,
                'annual_cost': annual_cost,
                'scenarios': {
                    'chc_funding': {
                        'available': eligibility_probability > 50,
                        'probability': eligibility_probability,
                        'weekly_cost': chc_weekly_cost,
                        'annual_cost': chc_annual_cost,
                        'savings_weekly': weekly_cost - chc_weekly_cost,
                        'savings_annual': annual_cost - chc_annual_cost
                    },
                    'la_funding': {
                        'available': la_funding['funding_available'],
                        'la_contribution_weekly': round(la_weekly_contribution, 2),
                        'self_contribution_weekly': round(self_weekly_contribution, 2),
                        'la_contribution_annual': round(la_weekly_contribution * 52, 2),
                        'self_contribution_annual': round(self_weekly_contribution * 52, 2)
                    },
                    'self_funding': {
                        'weekly_cost': self_funding_weekly,
                        'annual_cost': self_funding_annual
                    },
                    'dpa_deferral': {
                        'available': dpa_considerations['dpa_eligible'],
                        'weekly_deferred': round(dpa_weekly_deferred, 2),
                        'weekly_interest': round(dpa_interest_weekly, 2),
                        'annual_deferred': round(dpa_weekly_deferred * 52, 2),
                        'annual_interest': round(dpa_interest_weekly * 52, 2)
                    }
                },
                'recommended_scenario': self._recommend_funding_scenario(
                    chc_eligibility, la_funding, dpa_considerations, weekly_cost
                )
            })
        
        return {
            'outcomes': outcomes,
            'summary': self._calculate_funding_summary(outcomes, chc_eligibility, la_funding)
        }
    
    def _recommend_funding_scenario(
        self,
        chc_eligibility: Dict[str, Any],
        la_funding: Dict[str, Any],
        dpa_considerations: Dict[str, Any],
        weekly_cost: float
    ) -> Dict[str, Any]:
        """Recommend best funding scenario"""
        # Ensure eligibility_probability is a number
        eligibility_probability = chc_eligibility.get('eligibility_probability', 0)
        try:
            eligibility_probability = float(eligibility_probability) if eligibility_probability is not None else 0.0
        except (ValueError, TypeError):
            eligibility_probability = 0.0
        
        if eligibility_probability > 50:
            return {
                'scenario': 'chc',
                'priority': 1,
                'reason': 'High CHC eligibility probability - pursue NHS funding first',
                'weekly_cost': 0,
                'annual_cost': 0
            }
        elif la_funding['funding_available'] and la_funding['funding_level'] == 'full':
            return {
                'scenario': 'la_full',
                'priority': 2,
                'reason': 'Full LA funding available',
                'weekly_cost': 0,
                'annual_cost': 0
            }
        elif la_funding['funding_available']:
            self_contribution = weekly_cost * (la_funding['funding_split']['self_contribution_percent'] / 100)
            return {
                'scenario': 'la_partial',
                'priority': 3,
                'reason': 'Partial LA funding with self-contribution',
                'weekly_cost': self_contribution,
                'annual_cost': self_contribution * 52
            }
        elif dpa_considerations['dpa_eligible']:
            return {
                'scenario': 'dpa',
                'priority': 4,
                'reason': 'DPA available to defer costs',
                'weekly_cost': weekly_cost,
                'annual_cost': weekly_cost * 52,
                'note': 'Costs deferred until property sale'
            }
        else:
            return {
                'scenario': 'self_funding',
                'priority': 5,
                'reason': 'Self-funding required',
                'weekly_cost': weekly_cost,
                'annual_cost': weekly_cost * 52
            }
    
    def _calculate_funding_summary(
        self,
        outcomes: List[Dict[str, Any]],
        chc_eligibility: Dict[str, Any],
        la_funding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate summary of funding options"""
        avg_weekly_cost = sum(o['weekly_cost'] for o in outcomes) / len(outcomes) if outcomes else 0
        
        # Ensure eligibility_probability is a number
        eligibility_probability = chc_eligibility.get('eligibility_probability', 0)
        try:
            eligibility_probability = float(eligibility_probability) if eligibility_probability is not None else 0.0
        except (ValueError, TypeError):
            eligibility_probability = 0.0
        
        return {
            'average_weekly_cost': round(avg_weekly_cost, 2),
            'average_annual_cost': round(avg_weekly_cost * 52, 2),
            'best_case_scenario': {
                'type': 'CHC' if eligibility_probability > 50 else 'LA Full',
                'weekly_cost': 0 if eligibility_probability > 50 or la_funding.get('funding_level') == 'full' else avg_weekly_cost * 0.2,
                'annual_cost': 0 if eligibility_probability > 50 or la_funding.get('funding_level') == 'full' else avg_weekly_cost * 0.2 * 52
            },
            'worst_case_scenario': {
                'type': 'Self-Funding',
                'weekly_cost': avg_weekly_cost,
                'annual_cost': avg_weekly_cost * 52
            }
        }
    
    def calculate_five_year_projections(
        self,
        questionnaire: Dict[str, Any],
        care_homes: List[Dict[str, Any]],
        funding_outcomes: Dict[str, Any],
        chc_eligibility: Optional[Dict[str, Any]] = None,
        la_funding: Optional[Dict[str, Any]] = None,
        dpa_considerations: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive 5-year cost projections for all funding scenarios
        
        Projects costs for:
        - CHC Funding (if eligible)
        - LA Funding (full/partial)
        - Self-Funding
        - DPA Deferral (if eligible)
        - Recommended scenario
        
        Args:
            questionnaire: Professional questionnaire response
            care_homes: List of care homes
            funding_outcomes: Funding outcomes from calculate_funding_outcomes
            chc_eligibility: CHC eligibility assessment (optional)
            la_funding: LA funding assessment (optional)
            dpa_considerations: DPA considerations (optional)
        
        Returns:
            Dict with detailed 5-year cost projections for all scenarios
        """
        projections = []
        current_year = datetime.now().year
        
        for outcome in funding_outcomes.get('outcomes', []):
            home_id = outcome['home_id']
            home_name = outcome['home_name']
            base_weekly_cost = outcome['weekly_cost']
            base_annual_cost = outcome['annual_cost']
            
            scenarios = outcome.get('scenarios', {})
            recommended = outcome.get('recommended_scenario', {})
            
            # Calculate projections for each funding scenario
            scenario_projections = {}
            
            # Scenario 1: CHC Funding
            chc_scenario = scenarios.get('chc_funding', {})
            if chc_scenario.get('available', False):
                chc_projections = self._calculate_scenario_projections(
                    base_weekly_cost=0,  # CHC covers 100%
                    base_annual_cost=0,
                    scenario_name='CHC Funding',
                    probability=chc_scenario.get('probability', 0) / 100,
                    current_year=current_year
                )
                scenario_projections['chc'] = chc_projections
            
            # Scenario 2: LA Funding
            la_scenario = scenarios.get('la_funding', {})
            if la_scenario.get('available', False):
                self_contribution_weekly = la_scenario.get('self_contribution_weekly', base_weekly_cost)
                la_projections = self._calculate_scenario_projections(
                    base_weekly_cost=self_contribution_weekly,
                    base_annual_cost=self_contribution_weekly * 52,
                    scenario_name='LA Funding',
                    la_contribution_weekly=la_scenario.get('la_contribution_weekly', 0),
                    current_year=current_year
                )
                scenario_projections['la'] = la_projections
            
            # Scenario 3: Self-Funding
            self_scenario = scenarios.get('self_funding', {})
            self_projections = self._calculate_scenario_projections(
                base_weekly_cost=self_scenario.get('weekly_cost', base_weekly_cost),
                base_annual_cost=self_scenario.get('annual_cost', base_annual_cost),
                scenario_name='Self-Funding',
                current_year=current_year
            )
            scenario_projections['self'] = self_projections
            
            # Scenario 4: DPA Deferral
            dpa_scenario = scenarios.get('dpa_deferral', {})
            if dpa_scenario.get('available', False) and dpa_considerations:
                dpa_projections = self._calculate_dpa_projections(
                    base_weekly_cost=base_weekly_cost,
                    base_annual_cost=base_annual_cost,
                    dpa_considerations=dpa_considerations,
                    current_year=current_year
                )
                scenario_projections['dpa'] = dpa_projections
            
            # Recommended Scenario
            recommended_weekly = recommended.get('weekly_cost', base_weekly_cost)
            recommended_projections = self._calculate_scenario_projections(
                base_weekly_cost=recommended_weekly,
                base_annual_cost=recommended_weekly * 52,
                scenario_name='Recommended',
                scenario_type=recommended.get('scenario', 'self'),
                current_year=current_year
            )
            scenario_projections['recommended'] = recommended_projections

            # Ensure all scenarios exist for UI consistency
            if 'chc' not in scenario_projections:
                fallback_chc = self._calculate_scenario_projections(
                    base_weekly_cost=0,
                    base_annual_cost=0,
                    scenario_name='CHC Funding',
                    current_year=current_year,
                    probability=0.0
                )
                fallback_chc['notes'] = 'Not available'
                scenario_projections['chc'] = fallback_chc

            if 'la' not in scenario_projections:
                fallback_la = self._calculate_scenario_projections(
                    base_weekly_cost=base_weekly_cost,
                    base_annual_cost=base_annual_cost,
                    scenario_name='LA Funding',
                    current_year=current_year
                )
                fallback_la['notes'] = 'Not available (self-funding equivalence)'
                scenario_projections['la'] = fallback_la

            if 'dpa' not in scenario_projections:
                fallback_dpa = self._calculate_scenario_projections(
                    base_weekly_cost=base_weekly_cost,
                    base_annual_cost=base_annual_cost,
                    scenario_name='DPA Deferral',
                    current_year=current_year
                )
                fallback_dpa['notes'] = 'Not available'
                scenario_projections['dpa'] = fallback_dpa
            
            # Calculate year-by-year breakdown
            year_by_year = self._calculate_year_by_year_breakdown(
                scenario_projections, current_year
            )
            
            projections.append({
                'home_id': home_id,
                'home_name': home_name,
                'base_weekly_cost': base_weekly_cost,
                'base_annual_cost': base_annual_cost,
                'scenario_projections': scenario_projections,
                'year_by_year': year_by_year,
                'summary': self._calculate_home_projection_summary(
                    scenario_projections, base_weekly_cost
                )
            })
        
        # Calculate overall summary
        overall_summary = self._calculate_overall_projection_summary(projections)
        
        return {
            'projections': projections,
            'summary': overall_summary,
            'assumptions': [
                f'Annual cost inflation: {self.COST_INFLATION_RATE * 100}% (based on UK care home cost trends)',
                'CHC funding: 100% coverage if approved (probability-adjusted projections shown)',
                'LA funding: Based on current means-test thresholds (£23,250 capital, £189.50/week income)',
                'DPA deferral: Interest at 2.5% p.a. + £144/year admin fee',
                'Projections assume same care home and care level for 5 years',
                'Does not account for: care level changes, home closures, additional services',
                'Actual costs may vary based on: care needs changes, home-specific pricing, regional variations'
            ],
            'inflation_details': {
                'annual_rate': self.COST_INFLATION_RATE * 100,
                'compounded_5_year': round(((1 + self.COST_INFLATION_RATE) ** 5 - 1) * 100, 2),
                'explanation': 'Costs increase by 4% annually, compounding over 5 years'
            }
        }
    
    def _calculate_scenario_projections(
        self,
        base_weekly_cost: float,
        base_annual_cost: float,
        scenario_name: str,
        current_year: int,
        probability: Optional[float] = None,
        la_contribution_weekly: Optional[float] = None,
        scenario_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate 5-year projections for a specific funding scenario"""
        year_projections = []
        cumulative_cost = 0
        cumulative_la_contribution = 0
        
        for year_offset in range(5):
            year = current_year + year_offset
            inflation_factor = (1 + self.COST_INFLATION_RATE) ** year_offset
            
            # Calculate inflated costs
            projected_weekly = base_weekly_cost * inflation_factor
            projected_annual = projected_weekly * 52
            cumulative_cost += projected_annual
            
            # LA contribution (if applicable)
            if la_contribution_weekly is not None:
                la_weekly = la_contribution_weekly * inflation_factor
                la_annual = la_weekly * 52
                cumulative_la_contribution += la_annual
            else:
                la_weekly = 0
                la_annual = 0
            
            year_projections.append({
                'year': year,
                'year_number': year_offset + 1,
                'weekly_cost': round(projected_weekly, 2),
                'annual_cost': round(projected_annual, 2),
                'cumulative_cost': round(cumulative_cost, 2),
                'la_contribution_weekly': round(la_weekly, 2) if la_weekly > 0 else None,
                'la_contribution_annual': round(la_annual, 2) if la_annual > 0 else None,
                'inflation_factor': round(inflation_factor, 4),
                'inflation_rate': self.COST_INFLATION_RATE * 100
            })
        
        return {
            'scenario_name': scenario_name,
            'scenario_type': scenario_type,
            'base_weekly_cost': base_weekly_cost,
            'base_annual_cost': base_annual_cost,
            'projections': year_projections,
            'total_5_year_cost': round(cumulative_cost, 2),
            'total_5_year_la_contribution': round(cumulative_la_contribution, 2) if cumulative_la_contribution > 0 else None,
            'average_annual_cost': round(cumulative_cost / 5, 2),
            'average_weekly_cost': round(cumulative_cost / (5 * 52), 2),
            'probability': probability,
            'total_savings_vs_self': None  # Will be calculated in summary
        }
    
    def _calculate_dpa_projections(
        self,
        base_weekly_cost: float,
        base_annual_cost: float,
        dpa_considerations: Dict[str, Any],
        current_year: int
    ) -> Dict[str, Any]:
        """Calculate 5-year projections for DPA deferral scenario"""
        year_projections = []
        cumulative_deferred = 0
        cumulative_interest = 0
        cumulative_admin_fees = 0
        
        available_deferral_raw = dpa_considerations.get('deferral_limits', {}).get('available_deferral', 0)
        try:
            available_deferral = float(available_deferral_raw) if available_deferral_raw is not None else 0.0
        except (ValueError, TypeError):
            available_deferral = 0.0
        
        interest_rate_raw = dpa_considerations.get('costs', {}).get('interest_rate_percent', 2.5)
        try:
            interest_rate = float(interest_rate_raw) / 100 if interest_rate_raw is not None else 0.025
        except (ValueError, TypeError):
            interest_rate = 0.025
        
        admin_fee_annual_raw = dpa_considerations.get('costs', {}).get('administration_fee_annual', 144)
        try:
            admin_fee_annual = float(admin_fee_annual_raw) if admin_fee_annual_raw is not None else 144.0
        except (ValueError, TypeError):
            admin_fee_annual = 144.0
        
        for year_offset in range(5):
            year = current_year + year_offset
            inflation_factor = (1 + self.COST_INFLATION_RATE) ** year_offset
            
            # Calculate inflated costs
            projected_weekly = base_weekly_cost * inflation_factor
            projected_annual = projected_weekly * 52
            
            # Check if DPA limit reached
            if cumulative_deferred + projected_annual <= available_deferral:
                # Can defer full amount
                deferred_this_year = projected_annual
                within_limit = True
            else:
                # DPA limit reached
                deferred_this_year = max(0, available_deferral - cumulative_deferred)
                within_limit = False
            
            cumulative_deferred += deferred_this_year
            
            # Calculate interest on cumulative deferred amount
            interest_this_year = cumulative_deferred * interest_rate
            cumulative_interest += interest_this_year
            
            # Admin fee (annual)
            admin_fee_this_year = admin_fee_annual if deferred_this_year > 0 else 0
            cumulative_admin_fees += admin_fee_this_year
            
            # Total cost this year (deferred + interest + admin)
            total_cost_this_year = deferred_this_year + interest_this_year + admin_fee_this_year
            cumulative_total_cost = cumulative_deferred + cumulative_interest + cumulative_admin_fees
            
            year_projections.append({
                'year': year,
                'year_number': year_offset + 1,
                'weekly_cost': round(projected_weekly, 2),
                'annual_cost': round(projected_annual, 2),
                'deferred_amount': round(deferred_this_year, 2),
                'cumulative_deferred': round(cumulative_deferred, 2),
                'interest_accrued': round(interest_this_year, 2),
                'cumulative_interest': round(cumulative_interest, 2),
                'admin_fee': round(admin_fee_this_year, 2),
                'cumulative_admin_fees': round(cumulative_admin_fees, 2),
                'total_cost': round(total_cost_this_year, 2),
                'cumulative_total_cost': round(cumulative_total_cost, 2),
                'within_dpa_limit': within_limit,
                'inflation_factor': round(inflation_factor, 4)
            })
        
        return {
            'scenario_name': 'DPA Deferral',
            'scenario_type': 'dpa',
            'base_weekly_cost': base_weekly_cost,
            'base_annual_cost': base_annual_cost,
            'projections': year_projections,
            'total_5_year_deferred': round(cumulative_deferred, 2),
            'total_5_year_interest': round(cumulative_interest, 2),
            'total_5_year_admin_fees': round(cumulative_admin_fees, 2),
            'total_5_year_cost': round(cumulative_total_cost, 2),
            'average_annual_cost': round(cumulative_total_cost / 5, 2),
            'dpa_limit_reached': cumulative_deferred >= available_deferral,
            'years_covered': next((i + 1 for i, p in enumerate(year_projections) if not p.get('within_dpa_limit', True)), 5)
        }
    
    def _calculate_year_by_year_breakdown(
        self,
        scenario_projections: Dict[str, Dict[str, Any]],
        current_year: int
    ) -> List[Dict[str, Any]]:
        """Calculate year-by-year comparison across all scenarios"""
        year_breakdown = []
        
        for year_offset in range(5):
            year = current_year + year_offset
            year_data = {
                'year': year,
                'year_number': year_offset + 1,
                'scenarios': {}
            }
            
            for scenario_key, scenario_data in scenario_projections.items():
                projections = scenario_data.get('projections', [])
                if year_offset < len(projections):
                    year_projection = projections[year_offset]
                    year_data['scenarios'][scenario_key] = {
                        'annual_cost': year_projection.get('annual_cost', 0),
                        'cumulative_cost': year_projection.get('cumulative_cost', 0),
                        'scenario_name': scenario_data.get('scenario_name', scenario_key)
                    }
            
            year_breakdown.append(year_data)
        
        return year_breakdown
    
    def _calculate_home_projection_summary(
        self,
        scenario_projections: Dict[str, Dict[str, Any]],
        base_weekly_cost: float
    ) -> Dict[str, Any]:
        """Calculate summary for a single home's projections"""
        summaries = {}
        
        for scenario_key, scenario_data in scenario_projections.items():
            total_cost = scenario_data.get('total_5_year_cost', 0)
            summaries[scenario_key] = {
                'scenario_name': scenario_data.get('scenario_name', scenario_key),
                'total_5_year_cost': total_cost,
                'average_annual_cost': scenario_data.get('average_annual_cost', 0),
                'average_weekly_cost': scenario_data.get('average_weekly_cost', 0)
            }
        
        # Calculate savings vs self-funding
        self_cost = summaries.get('self', {}).get('total_5_year_cost', 0)
        if self_cost > 0:
            for scenario_key, summary in summaries.items():
                if scenario_key != 'self':
                    savings = self_cost - summary['total_5_year_cost']
                    summary['savings_vs_self'] = round(savings, 2)
                    summary['savings_percent'] = round((savings / self_cost * 100), 1) if self_cost > 0 else 0
                else:
                    summary['savings_vs_self'] = 0.0
                    summary['savings_percent'] = 0.0
        else:
            for summary in summaries.values():
                summary['savings_vs_self'] = 0.0
                summary['savings_percent'] = 0.0
        
        # Find best scenario (lowest cost)
        best_scenario = min(summaries.items(), key=lambda x: x[1].get('total_5_year_cost', float('inf')))
        best_key, best_summary = best_scenario
        
        return {
            'scenario_summaries': summaries,
            'best_scenario': best_key,
            'best_scenario_cost': best_summary.get('total_5_year_cost', 0),
            'worst_scenario': 'self',
            'worst_scenario_cost': self_cost,
            'potential_savings': round(self_cost - best_scenario[1].get('total_5_year_cost', 0), 2)
        }
    
    def _calculate_overall_projection_summary(
        self,
        projections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate overall summary across all homes"""
        all_costs = []
        all_recommended_costs = []
        
        for proj in projections:
            summary = proj.get('summary', {})
            scenario_summaries = summary.get('scenario_summaries', {})
            
            # Self-funding costs
            self_cost = scenario_summaries.get('self', {}).get('total_5_year_cost', 0)
            if self_cost > 0:
                all_costs.append(self_cost)
            
            # Recommended scenario costs
            recommended_cost = scenario_summaries.get('recommended', {}).get('total_5_year_cost', 0)
            if recommended_cost > 0:
                all_recommended_costs.append(recommended_cost)
        
        avg_5_year_cost = sum(all_costs) / len(all_costs) if all_costs else 0
        avg_recommended_cost = sum(all_recommended_costs) / len(all_recommended_costs) if all_recommended_costs else 0
        
        return {
            'average_5_year_cost_self_funding': round(avg_5_year_cost, 2),
            'average_5_year_cost_recommended': round(avg_recommended_cost, 2),
            'average_annual_cost_self_funding': round(avg_5_year_cost / 5, 2),
            'average_annual_cost_recommended': round(avg_recommended_cost / 5, 2),
            'potential_annual_savings': round((avg_5_year_cost - avg_recommended_cost) / 5, 2),
            'potential_5_year_savings': round(avg_5_year_cost - avg_recommended_cost, 2),
            'inflation_rate_percent': self.COST_INFLATION_RATE * 100,
            'compounded_inflation_5yr': round(((1 + self.COST_INFLATION_RATE) ** 5 - 1) * 100, 2)
        }
    
    def calculate_funding_optimization(
        self,
        questionnaire: Dict[str, Any],
        care_homes: List[Dict[str, Any]],
        estimated_assets: Optional[float] = None,
        estimated_income: Optional[float] = None,
        property_value: Optional[float] = None,
        outstanding_mortgage: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Main method to calculate complete funding optimization
        
        Args:
            questionnaire: Professional questionnaire response
            care_homes: List of care homes with pricing
            estimated_assets: Estimated capital/assets
            estimated_income: Estimated weekly income
            property_value: Estimated property value
            outstanding_mortgage: Outstanding mortgage amount
        
        Returns:
            Complete funding optimization analysis
        """
        # Calculate all components
        chc_eligibility = self.calculate_chc_eligibility(questionnaire)
        la_funding = self.calculate_la_funding_availability(
            questionnaire, estimated_assets, estimated_income
        )
        dpa_considerations = self.calculate_dpa_considerations(
            questionnaire, property_value, outstanding_mortgage
        )
        funding_outcomes = self.calculate_funding_outcomes(
            questionnaire, care_homes, chc_eligibility, la_funding, dpa_considerations
        )
        five_year_projections = self.calculate_five_year_projections(
            questionnaire, care_homes, funding_outcomes,
            chc_eligibility=chc_eligibility,
            la_funding=la_funding,
            dpa_considerations=dpa_considerations
        )
        
        return {
            'chc_eligibility': chc_eligibility,
            'la_funding': la_funding,
            'dpa_considerations': dpa_considerations,
            'funding_outcomes': funding_outcomes,
            'five_year_projections': five_year_projections,
            'generated_at': datetime.now().isoformat()
        }


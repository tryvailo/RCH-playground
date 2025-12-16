"""
Red Flags & Risk Assessment Service
Identifies and analyzes red flags and risks for care homes in Professional Report
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RedFlagsService:
    """Service for identifying red flags and risk assessment"""
    
    def generate_risk_assessment(
        self,
        care_homes: List[Dict[str, Any]],
        questionnaire: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive risk assessment with red flags for all care homes
        
        Args:
            care_homes: List of care homes (already sorted by match score)
            questionnaire: Professional questionnaire response
        
        Returns:
            Dict with risk assessment including:
            - Financial stability warnings
            - CQC compliance issues
            - Staff turnover concerns
            - Pricing increases history
            - Overall risk scores
        """
        if not care_homes:
            return {
                'error': 'No care homes available for risk assessment',
                'homes_assessment': [],
                'summary': {}
            }
        
        homes_assessment = []
        total_red_flags = 0
        high_risk_count = 0
        medium_risk_count = 0
        low_risk_count = 0
        
        for home in care_homes:
            if not home:
                continue
            assessment = self._assess_single_home(home, questionnaire)
            homes_assessment.append(assessment)
            
            # Count risk levels
            risk_level = assessment.get('overall_risk_level', 'low')
            if risk_level == 'high':
                high_risk_count += 1
            elif risk_level == 'medium':
                medium_risk_count += 1
            else:
                low_risk_count += 1
            
            total_red_flags += len(assessment.get('red_flags', []))
        
        # Generate summary
        summary = self._generate_summary(
            homes_assessment,
            total_red_flags,
            high_risk_count,
            medium_risk_count,
            low_risk_count
        )
        
        return {
            'homes_assessment': homes_assessment,
            'summary': summary,
            'generated_at': datetime.now().isoformat()
        }
    
    def _assess_single_home(
        self,
        home: Dict[str, Any],
        questionnaire: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess a single care home for red flags and risks"""
        if not home or not isinstance(home, dict):
            return {
                'home_id': None,
                'home_name': 'Unknown',
                'red_flags': [],
                'warnings': [],
                'risk_score': 0,
                'overall_risk_level': 'low',
                'financial_assessment': {'status': 'unknown', 'risk_score': 0, 'red_flags': [], 'warnings': []},
                'cqc_assessment': {'status': 'unknown', 'risk_score': 0, 'red_flags': [], 'warnings': []},
                'staff_assessment': {'status': 'unknown', 'risk_score': 0, 'red_flags': [], 'warnings': []},
                'pricing_assessment': {'status': 'unknown', 'risk_score': 0, 'red_flags': [], 'warnings': []}
            }
        
        red_flags = []
        warnings = []
        risk_score = 0
        
        try:
            home_id = home.get('id')
            home_name = home.get('name', 'Unknown')
        
        # 1. Financial Stability Warnings
        financial_flags = self._assess_financial_stability(home)
        red_flags.extend(financial_flags['red_flags'])
        warnings.extend(financial_flags['warnings'])
        risk_score += financial_flags['risk_score']
        
        # 2. CQC Compliance Issues
        cqc_flags = self._assess_cqc_compliance(home)
        red_flags.extend(cqc_flags['red_flags'])
        warnings.extend(cqc_flags['warnings'])
        risk_score += cqc_flags['risk_score']
        
        # 3. Staff Turnover Concerns
        staff_flags = self._assess_staff_turnover(home)
        red_flags.extend(staff_flags['red_flags'])
        warnings.extend(staff_flags['warnings'])
        risk_score += staff_flags['risk_score']
        
        # 4. Pricing Increases History
        pricing_flags = self._assess_pricing_history(home)
        red_flags.extend(pricing_flags['red_flags'])
        warnings.extend(pricing_flags['warnings'])
        risk_score += pricing_flags['risk_score']
        
        # Calculate overall risk level
        overall_risk_level = self._calculate_risk_level(risk_score, len(red_flags))
        
            return {
                'home_id': home_id,
                'home_name': home_name,
                'red_flags': red_flags,
                'warnings': warnings,
                'risk_score': min(risk_score, 100),  # Cap at 100
                'overall_risk_level': overall_risk_level,
                'financial_assessment': financial_flags,
                'cqc_assessment': cqc_flags,
                'staff_assessment': staff_flags,
                'pricing_assessment': pricing_flags
            }
        except Exception as e:
            logger.error(f"Error assessing home {home.get('name', 'Unknown') if isinstance(home, dict) else 'Unknown'}: {e}")
            return {
                'home_id': home.get('id') if isinstance(home, dict) else None,
                'home_name': home.get('name', 'Unknown') if isinstance(home, dict) else 'Unknown',
                'red_flags': [],
                'warnings': [{'type': 'system', 'severity': 'low', 'title': 'Assessment Error', 'description': str(e)}],
                'risk_score': 0,
                'overall_risk_level': 'low',
                'financial_assessment': {'status': 'error', 'risk_score': 0, 'red_flags': [], 'warnings': []},
                'cqc_assessment': {'status': 'error', 'risk_score': 0, 'red_flags': [], 'warnings': []},
                'staff_assessment': {'status': 'error', 'risk_score': 0, 'red_flags': [], 'warnings': []},
                'pricing_assessment': {'status': 'error', 'risk_score': 0, 'red_flags': [], 'warnings': []}
            }
    
    def _assess_financial_stability(self, home: Dict[str, Any]) -> Dict[str, Any]:
        """Assess financial stability and identify red flags"""
        red_flags = []
        warnings = []
        risk_score = 0
        
        financial = home.get('financialStability')
        if not financial:
            warnings.append({
                'type': 'financial',
                'severity': 'low',
                'title': 'Financial Data Unavailable',
                'description': 'Financial stability data not available for this home',
                'impact': 'Cannot assess financial risk'
            })
            return {
                'red_flags': red_flags,
                'warnings': warnings,
                'risk_score': risk_score,
                'status': 'unknown'
            }
        
        # Altman Z-Score Analysis
        altman_z = financial.get('altman_z_score')
        if altman_z is not None:
            try:
                altman_z = float(altman_z)
            except (ValueError, TypeError):
                altman_z = None
            
            if altman_z is not None and altman_z < 1.8:
                red_flags.append({
                    'type': 'financial',
                    'severity': 'high',
                    'title': 'High Bankruptcy Risk',
                    'description': f'Altman Z-Score of {altman_z:.2f} indicates high bankruptcy risk (below 1.8)',
                    'impact': 'Significant risk of financial distress or closure',
                    'recommendation': 'Consider alternative options or request financial guarantees'
                })
                risk_score += 30
            elif altman_z < 2.99:
                warnings.append({
                    'type': 'financial',
                    'severity': 'medium',
                    'title': 'Moderate Financial Risk',
                    'description': f'Altman Z-Score of {altman_z:.2f} indicates moderate risk (1.8-2.99)',
                    'impact': 'Monitor financial stability closely',
                    'recommendation': 'Request recent financial statements'
                })
                risk_score += 15
        
        # Bankruptcy Risk Score
        bankruptcy_risk = financial.get('bankruptcy_risk_score')
        if bankruptcy_risk is not None:
            try:
                bankruptcy_risk = float(bankruptcy_risk)
            except (ValueError, TypeError):
                bankruptcy_risk = None
            
            if bankruptcy_risk is not None and bankruptcy_risk >= 60:
                red_flags.append({
                    'type': 'financial',
                    'severity': 'high',
                    'title': 'High Bankruptcy Risk Score',
                    'description': f'Bankruptcy risk score of {bankruptcy_risk}/100 indicates high risk',
                    'impact': 'Elevated risk of financial failure',
                    'recommendation': 'Exercise caution and consider alternatives'
                })
                risk_score += 25
            elif bankruptcy_risk >= 40:
                warnings.append({
                    'type': 'financial',
                    'severity': 'medium',
                    'title': 'Moderate Bankruptcy Risk',
                    'description': f'Bankruptcy risk score of {bankruptcy_risk}/100 indicates moderate risk',
                    'impact': 'Monitor financial health',
                    'recommendation': 'Request financial stability updates'
                })
                risk_score += 10
        
        # Red Flags Detection
        red_flags_list = financial.get('red_flags', [])
        for flag in red_flags_list:
            flag_type = flag.get('type', 'unknown')
            severity = flag.get('severity', 'medium')
            
            if severity == 'high':
                red_flags.append({
                    'type': 'financial',
                    'severity': 'high',
                    'title': flag.get('title', 'Financial Red Flag'),
                    'description': flag.get('description', ''),
                    'impact': flag.get('impact', ''),
                    'recommendation': flag.get('recommendation', 'Review financial documents')
                })
                risk_score += 20
            else:
                warnings.append({
                    'type': 'financial',
                    'severity': severity,
                    'title': flag.get('title', 'Financial Warning'),
                    'description': flag.get('description', ''),
                    'impact': flag.get('impact', ''),
                    'recommendation': flag.get('recommendation', 'Monitor closely')
                })
                risk_score += 5
        
        # Financial Summary Analysis
        financial_summary = financial.get('three_year_summary', {})
        if financial_summary:
            revenues = financial_summary.get('revenues', [])
            margins = financial_summary.get('margins', [])
            
            # Declining Revenue Trend
            if len(revenues) >= 2:
                # Ensure values are numbers
                try:
                    revenue_start = float(revenues[0]) if revenues[0] is not None else 0.0
                except (ValueError, TypeError):
                    revenue_start = 0.0
                
                try:
                    revenue_end = float(revenues[-1]) if revenues[-1] is not None else 0.0
                except (ValueError, TypeError):
                    revenue_end = 0.0
                
                if revenue_start > 0 and revenue_end < revenue_start * 0.8:  # 20% decline
                    warnings.append({
                        'type': 'financial',
                        'severity': 'medium',
                        'title': 'Declining Revenue Trend',
                        'description': f'Revenue declined from £{revenue_start:,.0f} to £{revenue_end:,.0f} over 3 years',
                        'impact': 'Potential financial instability',
                        'recommendation': 'Inquire about recent financial performance'
                    })
                    risk_score += 10
            
            # Negative Margins
            if margins and any((float(m) if m is not None else 0.0) < 0 for m in margins):
                red_flags.append({
                    'type': 'financial',
                    'severity': 'high',
                    'title': 'Negative Profit Margins',
                    'description': 'Home has reported negative profit margins in recent years',
                    'impact': 'Unsustainable financial position',
                    'recommendation': 'Request explanation and financial recovery plan'
                })
                risk_score += 25
        
        return {
            'red_flags': red_flags,
            'warnings': warnings,
            'risk_score': risk_score,
            'status': 'assessed',
            'altman_z_score': altman_z,
            'bankruptcy_risk': bankruptcy_risk
        }
    
    def _assess_cqc_compliance(self, home: Dict[str, Any]) -> Dict[str, Any]:
        """Assess CQC compliance and identify issues"""
        red_flags = []
        warnings = []
        risk_score = 0
        
        cqc_rating = home.get('cqcRating', '')
        cqc_deep_dive = home.get('cqcDeepDive', {})
        
        # Overall Rating Issues
        if cqc_rating:
            rating_lower = cqc_rating.lower()
            if 'inadequate' in rating_lower:
                red_flags.append({
                    'type': 'cqc',
                    'severity': 'high',
                    'title': 'Inadequate CQC Rating',
                    'description': f'Home has an "Inadequate" CQC rating - the lowest possible rating',
                    'impact': 'Serious compliance and quality concerns',
                    'recommendation': 'Avoid unless significant improvements are demonstrated'
                })
                risk_score += 40
            elif 'requires improvement' in rating_lower:
                warnings.append({
                    'type': 'cqc',
                    'severity': 'medium',
                    'title': 'CQC Requires Improvement',
                    'description': f'Home has a "Requires Improvement" CQC rating',
                    'impact': 'Quality and compliance issues identified',
                    'recommendation': 'Review improvement plans and recent inspection reports'
                })
                risk_score += 20
        
        # Detailed Ratings Analysis
        detailed_ratings = cqc_deep_dive.get('detailed_ratings', {})
        if detailed_ratings:
            inadequate_count = 0
            requires_improvement_count = 0
            
            for rating_key, rating_data in detailed_ratings.items():
                rating_value = rating_data.get('rating', '').lower() if isinstance(rating_data, dict) else ''
                if 'inadequate' in rating_value:
                    inadequate_count += 1
                elif 'requires improvement' in rating_value:
                    requires_improvement_count += 1
            
            if inadequate_count > 0:
                red_flags.append({
                    'type': 'cqc',
                    'severity': 'high',
                    'title': f'{inadequate_count} Inadequate Detailed Ratings',
                    'description': f'Home has {inadequate_count} category(ies) rated as "Inadequate"',
                    'impact': 'Specific areas of serious concern',
                    'recommendation': 'Review detailed inspection reports for specific issues'
                })
                risk_score += 15 * inadequate_count
            
            if requires_improvement_count >= 2:
                warnings.append({
                    'type': 'cqc',
                    'severity': 'medium',
                    'title': f'{requires_improvement_count} Categories Require Improvement',
                    'description': f'Multiple categories ({requires_improvement_count}) require improvement',
                    'impact': 'Broad quality concerns across multiple areas',
                    'recommendation': 'Review improvement plans and progress'
                })
                risk_score += 10
        
        # Action Plans / Improvement Plans
        action_plans = cqc_deep_dive.get('action_plans', [])
        if action_plans:
            active_plans = [plan for plan in action_plans if plan.get('status') == 'active']
            if len(active_plans) > 0:
                warnings.append({
                    'type': 'cqc',
                    'severity': 'medium',
                    'title': f'{len(active_plans)} Active Improvement Plan(s)',
                    'description': f'Home has {len(active_plans)} active improvement plan(s) from CQC',
                    'impact': 'Ongoing compliance issues being addressed',
                    'recommendation': 'Review improvement plan details and timeline'
                })
                risk_score += 5 * len(active_plans)
        
        # Rating Trend Analysis
        trend = cqc_deep_dive.get('trend', '')
        if trend:
            if 'declining' in trend.lower() or 'deteriorating' in trend.lower():
                warnings.append({
                    'type': 'cqc',
                    'severity': 'medium',
                    'title': 'Declining CQC Rating Trend',
                    'description': f'CQC ratings show a {trend} trend over recent inspections',
                    'impact': 'Quality may be deteriorating',
                    'recommendation': 'Review recent inspection history and improvement actions'
                })
                risk_score += 15
        
        return {
            'red_flags': red_flags,
            'warnings': warnings,
            'risk_score': risk_score,
            'status': 'assessed',
            'overall_rating': cqc_rating,
            'detailed_ratings_count': len(detailed_ratings) if detailed_ratings else 0,
            'active_action_plans': len(action_plans) if action_plans else 0
        }
    
    def _assess_staff_turnover(self, home: Dict[str, Any]) -> Dict[str, Any]:
        """Assess staff turnover and identify concerns"""
        red_flags = []
        warnings = []
        risk_score = 0
        
        # Glassdoor Data
        google_places = home.get('googlePlaces', {})
        staff_quality = home.get('staffQuality', {})
        
        # Staff Turnover Rate
        turnover_rate = staff_quality.get('turnover_rate_percent')
        if turnover_rate is not None:
            try:
                turnover_rate = float(turnover_rate)
            except (ValueError, TypeError):
                turnover_rate = None
            
            if turnover_rate is not None and turnover_rate >= 50:
                red_flags.append({
                    'type': 'staff',
                    'severity': 'high',
                    'title': 'Very High Staff Turnover',
                    'description': f'Staff turnover rate of {turnover_rate}% indicates very high turnover',
                    'impact': 'Potential care quality issues, instability, and management concerns',
                    'recommendation': 'Inquire about staff retention strategies and management practices'
                })
                risk_score += 25
            elif turnover_rate >= 30:
                warnings.append({
                    'type': 'staff',
                    'severity': 'medium',
                    'title': 'High Staff Turnover',
                    'description': f'Staff turnover rate of {turnover_rate}% is above industry average',
                    'impact': 'May indicate management or workplace culture issues',
                    'recommendation': 'Ask about staff retention and satisfaction initiatives'
                })
                risk_score += 15
        
        # Average Tenure
        avg_tenure = staff_quality.get('average_tenure_years')
        if avg_tenure is not None:
            try:
                avg_tenure = float(avg_tenure)
            except (ValueError, TypeError):
                avg_tenure = None
            
            if avg_tenure is not None and avg_tenure < 1:
                red_flags.append({
                    'type': 'staff',
                    'severity': 'high',
                    'title': 'Very Low Staff Tenure',
                    'description': f'Average staff tenure of {avg_tenure:.1f} years indicates high turnover',
                    'impact': 'Lack of experienced staff, potential care continuity issues',
                    'recommendation': 'Inquire about staff stability and retention programs'
                })
                risk_score += 20
            elif avg_tenure < 2:
                warnings.append({
                    'type': 'staff',
                    'severity': 'medium',
                    'title': 'Low Staff Tenure',
                    'description': f'Average staff tenure of {avg_tenure:.1f} years is below ideal',
                    'impact': 'May affect care consistency and resident relationships',
                    'recommendation': 'Ask about staff development and retention'
                })
                risk_score += 10
        
        # Glassdoor Rating (if available)
        glassdoor_rating = staff_quality.get('glassdoor_rating')
        if glassdoor_rating is not None:
            try:
                glassdoor_rating = float(glassdoor_rating)
            except (ValueError, TypeError):
                glassdoor_rating = None
            
            if glassdoor_rating is not None and glassdoor_rating < 2.5:
                warnings.append({
                    'type': 'staff',
                    'severity': 'medium',
                    'title': 'Low Employee Satisfaction',
                    'description': f'Glassdoor rating of {glassdoor_rating}/5 indicates low employee satisfaction',
                    'impact': 'May correlate with high turnover and care quality issues',
                    'recommendation': 'Review employee feedback and management practices'
                })
                risk_score += 10
        
        # Job Board Activity (High Hiring Frequency)
        job_listings_count_raw = staff_quality.get('recent_job_listings_count', 0)
        try:
            job_listings_count = float(job_listings_count_raw) if job_listings_count_raw is not None else 0.0
        except (ValueError, TypeError):
            job_listings_count = 0.0
        
        if job_listings_count >= 5:
            warnings.append({
                'type': 'staff',
                'severity': 'low',
                'title': 'High Job Posting Activity',
                'description': f'{job_listings_count} recent job postings may indicate ongoing hiring needs',
                'impact': 'Could suggest turnover or expansion',
                'recommendation': 'Inquire about staffing levels and stability'
            })
            risk_score += 5
        
        return {
            'red_flags': red_flags,
            'warnings': warnings,
            'risk_score': risk_score,
            'status': 'assessed',
            'turnover_rate': turnover_rate,
            'average_tenure': avg_tenure,
            'glassdoor_rating': glassdoor_rating
        }
    
    def _assess_pricing_history(self, home: Dict[str, Any]) -> Dict[str, Any]:
        """Assess pricing increases history and identify concerns"""
        red_flags = []
        warnings = []
        risk_score = 0
        
        # Pricing Data
        weekly_price = home.get('weeklyPrice', 0)
        pricing_history = home.get('pricingHistory', [])
        
        if not pricing_history or len(pricing_history) < 2:
            # No pricing history available
            return {
                'red_flags': red_flags,
                'warnings': warnings,
                'risk_score': risk_score,
                'status': 'insufficient_data',
                'note': 'Pricing history not available'
            }
        
        # Analyze pricing trends
        # Safely extract prices, filtering out None and non-numeric values
        prices = []
        for entry in pricing_history:
            price = entry.get('weekly_price')
            if price is not None:
                try:
                    price_float = float(price)
                    if price_float > 0:
                        prices.append(price_float)
                except (ValueError, TypeError):
                    pass
        dates = [entry.get('date') for entry in pricing_history if entry.get('date')]
        
        if len(prices) < 2:
            return {
                'red_flags': red_flags,
                'warnings': warnings,
                'risk_score': risk_score,
                'status': 'insufficient_data'
            }
        
        # Calculate price increases
        increases = []
        for i in range(1, len(prices)):
            if prices[i-1] > 0:
                increase_pct = ((prices[i] - prices[i-1]) / prices[i-1]) * 100
                increases.append({
                    'from': prices[i-1],
                    'to': prices[i],
                    'increase_pct': increase_pct,
                    'date': dates[i] if i < len(dates) else None
                })
        
        # Analyze increases
        if increases:
            avg_increase = sum(inc['increase_pct'] for inc in increases) / len(increases)
            max_increase = max(inc['increase_pct'] for inc in increases)
            total_increase = ((prices[-1] - prices[0]) / prices[0] * 100) if prices[0] > 0 else 0
            
            # High Average Increase Rate
            if avg_increase > 10:
                warnings.append({
                    'type': 'pricing',
                    'severity': 'medium',
                    'title': 'High Average Price Increase Rate',
                    'description': f'Average price increase of {avg_increase:.1f}% per period is above typical',
                    'impact': 'May indicate aggressive pricing strategy or cost pressures',
                    'recommendation': 'Inquire about pricing policy and future increases'
                })
                risk_score += 10
            
            # Very High Single Increase
            if max_increase > 20:
                red_flags.append({
                    'type': 'pricing',
                    'severity': 'high',
                    'title': 'Very Large Price Increase',
                    'description': f'Price increased by {max_increase:.1f}% in a single period',
                    'impact': 'Significant cost increase, may indicate financial pressure',
                    'recommendation': 'Request explanation and future pricing forecast'
                })
                risk_score += 20
            
            # Significant Total Increase
            if total_increase > 30:
                warnings.append({
                    'type': 'pricing',
                    'severity': 'medium',
                    'title': 'Significant Total Price Increase',
                    'description': f'Total price increase of {total_increase:.1f}% over available history',
                    'impact': 'Substantial cost escalation over time',
                    'recommendation': 'Review pricing trend and budget accordingly'
                })
                risk_score += 15
            
            # Frequent Increases
            if len(increases) >= 3:
                warnings.append({
                    'type': 'pricing',
                    'severity': 'low',
                    'title': 'Frequent Price Increases',
                    'description': f'{len(increases)} price increases recorded in recent history',
                    'impact': 'May indicate ongoing cost pressures',
                    'recommendation': 'Inquire about pricing stability and future increases'
                })
                risk_score += 5
        
        return {
            'red_flags': red_flags,
            'warnings': warnings,
            'risk_score': risk_score,
            'status': 'assessed',
            'pricing_history_available': True,
            'total_increase_pct': total_increase if increases else 0,
            'average_increase_pct': avg_increase if increases else 0,
            'max_increase_pct': max_increase if increases else 0,
            'increase_count': len(increases)
        }
    
    def _calculate_risk_level(self, risk_score: float, red_flag_count: int) -> str:
        """Calculate overall risk level based on score and red flags"""
        if risk_score >= 50 or red_flag_count >= 3:
            return 'high'
        elif risk_score >= 25 or red_flag_count >= 1:
            return 'medium'
        else:
            return 'low'
    
    def _generate_summary(
        self,
        homes_assessment: List[Dict[str, Any]],
        total_red_flags: int,
        high_risk_count: int,
        medium_risk_count: int,
        low_risk_count: int
    ) -> Dict[str, Any]:
        """Generate overall summary of risk assessment"""
        total_homes = len(homes_assessment)
        
        # Count flags by type
        financial_flags = sum(len(h.get('financial_assessment', {}).get('red_flags', [])) for h in homes_assessment)
        cqc_flags = sum(len(h.get('cqc_assessment', {}).get('red_flags', [])) for h in homes_assessment)
        staff_flags = sum(len(h.get('staff_assessment', {}).get('red_flags', [])) for h in homes_assessment)
        pricing_flags = sum(len(h.get('pricing_assessment', {}).get('red_flags', [])) for h in homes_assessment)
        
        # Find homes with highest risk
        homes_by_risk = sorted(homes_assessment, key=lambda x: x.get('risk_score', 0), reverse=True)
        highest_risk_homes = [
            {
                'home_name': h.get('home_name'),
                'risk_score': h.get('risk_score', 0),
                'risk_level': h.get('overall_risk_level', 'low'),
                'red_flag_count': len(h.get('red_flags', []))
            }
            for h in homes_by_risk[:3]
        ]
        
        return {
            'total_homes_assessed': total_homes,
            'total_red_flags': total_red_flags,
            'risk_distribution': {
                'high': high_risk_count,
                'medium': medium_risk_count,
                'low': low_risk_count
            },
            'flags_by_category': {
                'financial': financial_flags,
                'cqc': cqc_flags,
                'staff': staff_flags,
                'pricing': pricing_flags
            },
            'highest_risk_homes': highest_risk_homes,
            'overall_assessment': self._generate_overall_assessment(
                total_red_flags,
                high_risk_count,
                total_homes
            )
        }
    
    def _generate_overall_assessment(
        self,
        total_red_flags: int,
        high_risk_count: int,
        total_homes: int
    ) -> str:
        """Generate overall assessment text"""
        if high_risk_count == 0 and total_red_flags == 0:
            return "All assessed homes show low risk indicators. No significant red flags identified."
        elif high_risk_count == 0:
            return f"Most homes show acceptable risk levels. {total_red_flags} warning(s) identified across {total_homes} homes, primarily requiring monitoring rather than immediate concern."
        elif high_risk_count <= 2:
            return f"{high_risk_count} home(s) show elevated risk levels with significant red flags. Review detailed assessments carefully before making placement decisions."
        else:
            return f"Multiple homes ({high_risk_count}) show high risk indicators. Exercise caution and review all red flags and warnings before proceeding with any placement."


"""
Companies House Service for Professional Report
Provides financial intelligence for care home companies

Features:
- Fetch company by name/registration
- Calculate Altman Z-Score (simplified proxy)
- Director history & stability analysis
- Financial stability scoring (0-100)
- Risk assessment with signals

Based on spec v3.0 PROFESSIONAL Report requirements:
- Financial Stability (20 points / 13% weight in 156-point algorithm)
- Altman Z-Score (0-10 pts)
- Profit Margin Trend (0-5 pts) 
- Director Stability (0-3 pts)
- Ownership Stability (0-2 pts)
"""
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass, asdict
import asyncio
import sys
from pathlib import Path

# Add path for api_clients
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))


@dataclass
class DirectorStability:
    """Director stability analysis result"""
    active_directors: int
    total_directors: int
    resignations_last_year: int
    resignations_last_2_years: int
    longest_tenure_years: float
    average_tenure_years: float
    stability_score: int  # 0-3 points
    stability_label: str  # "Excellent", "Good", "Concerning", "High Risk"
    issues: List[str]


@dataclass
class OwnershipStability:
    """Ownership stability analysis result"""
    ownership_type: str  # "Family", "Corporate", "Private Equity", "Offshore"
    is_private_equity: bool
    has_offshore_entities: bool
    ownership_changes_last_5_years: int
    stability_score: int  # 0-2 points
    stability_label: str
    issues: List[str]


@dataclass
class AltmanZScoreProxy:
    """
    Altman Z-Score Proxy
    
    Note: True Altman Z-Score requires financial statements data which
    Companies House API doesn't provide directly. This is a proxy based on:
    - Company age
    - Accounts filing status
    - Charges/debt indicators
    - Director stability
    """
    z_score: float
    z_score_label: str  # "Very Safe", "Safe", "Watch", "High Risk"
    z_score_range: str  # "> 3.0", "2.5-3.0", "1.5-2.5", "< 1.5"
    score_points: int   # 0-10 points for algorithm
    components: Dict[str, float]
    methodology_note: str


@dataclass
class FinancialStabilityResult:
    """Complete financial stability result for Professional Report"""
    company_number: str
    company_name: str
    company_status: str
    incorporation_date: Optional[str]
    company_age_years: float
    
    # Scores
    total_score: int  # 0-20 points for algorithm
    altman_z_score: AltmanZScoreProxy
    director_stability: DirectorStability
    ownership_stability: OwnershipStability
    
    # Risk assessment
    risk_level: str  # "Very Low", "Low", "Medium", "High", "Critical"
    risk_score: int  # 0-100
    
    # Issues and recommendations
    issues: List[str]
    recommendations: List[str]
    
    # Raw data for detailed view
    charges_summary: Dict[str, int]
    accounts_status: Dict[str, Any]
    
    # Metadata
    analysis_date: str
    data_source: str


class CompaniesHouseService:
    """
    Service for fetching and analyzing Companies House data
    for Professional Report financial stability assessment
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize service
        
        Args:
            api_key: Companies House API key. If None, will try to get from config.
        """
        self.api_key = api_key
        self._client = None
    
    async def _get_client(self):
        """Get or create Companies House client"""
        if self._client is None:
            try:
                from api_clients.companies_house_client import CompaniesHouseAPIClient
                from utils.client_factory import get_companies_house_client
                self._client = get_companies_house_client()
            except Exception as e:
                raise RuntimeError(f"Failed to initialize Companies House client: {e}")
        return self._client
    
    async def find_company_for_care_home(
        self,
        care_home_name: str,
        address: Optional[str] = None,
        postcode: Optional[str] = None
    ) -> Optional[str]:
        """
        Find company number for a care home
        
        Args:
            care_home_name: Name of the care home
            address: Optional address for better matching
            postcode: Optional postcode for better matching
            
        Returns:
            Company number or None if not found
        """
        client = await self._get_client()
        
        # Try exact name first
        company_number = await client.find_company_by_name(
            care_home_name, 
            prefer_care_home=True
        )
        
        if company_number:
            return company_number
        
        # Try with "Ltd" suffix
        if not care_home_name.lower().endswith(('ltd', 'limited')):
            company_number = await client.find_company_by_name(
                f"{care_home_name} Ltd",
                prefer_care_home=True
            )
            if company_number:
                return company_number
        
        # Try with "Care" added
        if 'care' not in care_home_name.lower():
            company_number = await client.find_company_by_name(
                f"{care_home_name} Care",
                prefer_care_home=True
            )
            if company_number:
                return company_number
        
        return None
    
    async def get_financial_stability(
        self,
        company_number: str
    ) -> FinancialStabilityResult:
        """
        Get complete financial stability analysis for a company
        
        Args:
            company_number: Companies House company number
            
        Returns:
            FinancialStabilityResult with all analysis
        """
        client = await self._get_client()
        
        # Fetch all data in parallel
        profile, officers, charges, pscs = await asyncio.gather(
            client.get_company_profile(company_number),
            client.get_company_officers(company_number),
            client.get_charges(company_number),
            client.get_persons_with_significant_control(company_number),
            return_exceptions=True
        )
        
        # Handle errors
        if isinstance(profile, Exception):
            raise profile
        officers = officers if not isinstance(officers, Exception) else []
        charges = charges if not isinstance(charges, Exception) else []
        pscs = pscs if not isinstance(pscs, Exception) else []
        
        # Calculate company age
        company_age = self._calculate_company_age(profile)
        
        # Analyze directors
        director_stability = self._analyze_director_stability(officers)
        
        # Analyze ownership
        ownership_stability = self._analyze_ownership_stability(pscs)
        
        # Calculate Altman Z-Score proxy
        altman_z = self._calculate_altman_z_proxy(
            profile, officers, charges, company_age
        )
        
        # Calculate total score (0-20 points)
        total_score = (
            altman_z.score_points +  # 0-10
            director_stability.stability_score +  # 0-3
            ownership_stability.stability_score +  # 0-2
            self._calculate_accounts_score(profile)  # 0-5
        )
        
        # Collect all issues
        all_issues = (
            director_stability.issues + 
            ownership_stability.issues +
            self._get_accounts_issues(profile) +
            self._get_charges_issues(charges)
        )
        
        # Determine risk level
        risk_level, risk_score = self._calculate_risk_level(
            profile, total_score, all_issues
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            risk_level, all_issues, director_stability, ownership_stability
        )
        
        # Prepare charges summary
        outstanding_charges = [c for c in charges if not c.get('satisfied_on')]
        charges_summary = {
            'total': len(charges),
            'outstanding': len(outstanding_charges),
            'satisfied': len(charges) - len(outstanding_charges)
        }
        
        # Prepare accounts status
        accounts = profile.get('accounts', {})
        accounts_status = {
            'overdue': accounts.get('overdue', False),
            'last_accounts_date': accounts.get('last_accounts', {}).get('made_up_to'),
            'next_due': accounts.get('next_due')
        }
        
        return FinancialStabilityResult(
            company_number=company_number,
            company_name=profile.get('company_name', ''),
            company_status=profile.get('company_status', ''),
            incorporation_date=profile.get('date_of_creation'),
            company_age_years=company_age,
            total_score=total_score,
            altman_z_score=altman_z,
            director_stability=director_stability,
            ownership_stability=ownership_stability,
            risk_level=risk_level,
            risk_score=risk_score,
            issues=all_issues,
            recommendations=recommendations,
            charges_summary=charges_summary,
            accounts_status=accounts_status,
            analysis_date=datetime.now().isoformat(),
            data_source='Companies House API'
        )
    
    def _calculate_company_age(self, profile: Dict) -> float:
        """Calculate company age in years"""
        creation_date_str = profile.get('date_of_creation')
        if not creation_date_str:
            return 0.0
        try:
            creation_date = datetime.strptime(creation_date_str, '%Y-%m-%d').date()
            age_days = (date.today() - creation_date).days
            return round(age_days / 365.25, 1)
        except:
            return 0.0
    
    def _analyze_director_stability(self, officers: List[Dict]) -> DirectorStability:
        """Analyze director stability"""
        directors = [o for o in officers if o.get('officer_role') == 'director']
        active = [d for d in directors if not d.get('resigned_on')]
        
        # Count resignations
        now = date.today()
        one_year_ago = now - timedelta(days=365)
        two_years_ago = now - timedelta(days=730)
        
        resignations_1y = 0
        resignations_2y = 0
        
        for director in directors:
            resigned_str = director.get('resigned_on')
            if resigned_str:
                try:
                    resigned_date = datetime.strptime(resigned_str, '%Y-%m-%d').date()
                    if resigned_date >= one_year_ago:
                        resignations_1y += 1
                    if resigned_date >= two_years_ago:
                        resignations_2y += 1
                except:
                    pass
        
        # Calculate tenures
        tenures = []
        for director in active:
            appointed_str = director.get('appointed_on')
            if appointed_str:
                try:
                    appointed_date = datetime.strptime(appointed_str, '%Y-%m-%d').date()
                    tenure_years = (now - appointed_date).days / 365.25
                    tenures.append(tenure_years)
                except:
                    pass
        
        longest_tenure = max(tenures) if tenures else 0.0
        avg_tenure = sum(tenures) / len(tenures) if tenures else 0.0
        
        # Calculate stability score (0-3)
        issues = []
        if resignations_2y == 0 and len(active) >= 2:
            score = 3
            label = "Excellent"
        elif resignations_2y <= 1 and len(active) >= 2:
            score = 2
            label = "Good"
        elif resignations_2y <= 2:
            score = 1
            label = "Concerning"
            issues.append(f"{resignations_2y} director changes in last 2 years")
        else:
            score = 0
            label = "High Risk"
            issues.append(f"High director turnover: {resignations_2y} changes in 2 years")
        
        if len(active) < 2:
            issues.append(f"Only {len(active)} active director(s) - governance risk")
            score = min(score, 1)
        
        return DirectorStability(
            active_directors=len(active),
            total_directors=len(directors),
            resignations_last_year=resignations_1y,
            resignations_last_2_years=resignations_2y,
            longest_tenure_years=round(longest_tenure, 1),
            average_tenure_years=round(avg_tenure, 1),
            stability_score=score,
            stability_label=label,
            issues=issues
        )
    
    def _analyze_ownership_stability(self, pscs: List[Dict]) -> OwnershipStability:
        """Analyze ownership structure and stability"""
        active_pscs = [p for p in pscs if not p.get('ceased_on')]
        
        # Detect ownership type
        pe_keywords = ['capital', 'partners', 'equity', 'investment', 'fund', 'holdings']
        offshore_jurisdictions = [
            'jersey', 'guernsey', 'cayman', 'bvi', 'isle of man', 
            'bermuda', 'luxembourg', 'gibraltar'
        ]
        
        is_pe = False
        has_offshore = False
        ownership_type = "Standard"
        
        for psc in active_pscs:
            name = psc.get('name', '').lower()
            
            if any(kw in name for kw in pe_keywords):
                is_pe = True
                ownership_type = "Private Equity"
            
            if psc.get('kind') == 'corporate-entity':
                identification = psc.get('identification', {})
                if isinstance(identification, dict):
                    jurisdiction = identification.get('legal_authority', '').lower()
                    country = identification.get('country_registered', '').lower()
                    if any(off in jurisdiction or off in country for off in offshore_jurisdictions):
                        has_offshore = True
                        if not is_pe:
                            ownership_type = "Offshore"
        
        if not is_pe and not has_offshore:
            if len(active_pscs) <= 2:
                ownership_type = "Family/Individual"
            else:
                ownership_type = "Corporate"
        
        # Count ownership changes
        now = datetime.now()
        five_years_ago = now - timedelta(days=5*365)
        
        changes = 0
        for psc in pscs:
            notified_str = psc.get('notified_on')
            if notified_str:
                try:
                    notified_date = datetime.fromisoformat(notified_str.replace('Z', '+00:00'))
                    if notified_date > five_years_ago:
                        changes += 1
                except:
                    pass
        
        # Calculate score (0-2)
        issues = []
        if changes == 0 or (changes == 1 and not is_pe and not has_offshore):
            score = 2
            label = "Stable"
        elif changes <= 2 and not is_pe:
            score = 1
            label = "Minor Changes"
        else:
            score = 0
            label = "Unstable"
            issues.append(f"{changes} ownership changes in last 5 years")
        
        if is_pe:
            issues.append("Private Equity ownership detected - higher debt burden typical")
            score = min(score, 1)
        
        if has_offshore:
            issues.append("Offshore entities in ownership - profit extraction risk")
            score = min(score, 1)
        
        return OwnershipStability(
            ownership_type=ownership_type,
            is_private_equity=is_pe,
            has_offshore_entities=has_offshore,
            ownership_changes_last_5_years=changes,
            stability_score=score,
            stability_label=label,
            issues=issues
        )
    
    def _calculate_altman_z_proxy(
        self,
        profile: Dict,
        officers: List[Dict],
        charges: List[Dict],
        company_age: float
    ) -> AltmanZScoreProxy:
        """
        Calculate Altman Z-Score proxy
        
        Real Altman Z-Score: Z = 1.2X1 + 1.4X2 + 3.3X3 + 0.6X4 + 1.0X5
        
        Our proxy uses available data:
        - Company age (proxy for retained earnings)
        - Accounts filing status (proxy for operational health)
        - Charges (proxy for leverage)
        - Director stability (proxy for management quality)
        """
        # Component scores (0-1 each, weighted to approximate Z-score range)
        components = {}
        
        # Age component (0-1): Established companies are safer
        if company_age >= 10:
            age_score = 1.0
        elif company_age >= 5:
            age_score = 0.8
        elif company_age >= 3:
            age_score = 0.5
        else:
            age_score = 0.3
        components['company_age'] = age_score
        
        # Accounts component (0-1)
        accounts = profile.get('accounts', {})
        if accounts.get('overdue'):
            accounts_score = 0.0
        else:
            last_accounts = accounts.get('last_accounts', {}).get('made_up_to')
            if last_accounts:
                try:
                    last_date = datetime.strptime(last_accounts, '%Y-%m-%d').date()
                    days_since = (date.today() - last_date).days
                    if days_since < 400:
                        accounts_score = 1.0
                    elif days_since < 600:
                        accounts_score = 0.7
                    else:
                        accounts_score = 0.4
                except:
                    accounts_score = 0.5
            else:
                accounts_score = 0.5
        components['accounts_status'] = accounts_score
        
        # Charges component (0-1): Fewer outstanding charges = better
        outstanding = len([c for c in charges if not c.get('satisfied_on')])
        if outstanding == 0:
            charges_score = 1.0
        elif outstanding <= 2:
            charges_score = 0.7
        elif outstanding <= 4:
            charges_score = 0.4
        else:
            charges_score = 0.1
        components['debt_level'] = charges_score
        
        # Company status component
        status = profile.get('company_status', '').lower()
        if status == 'active':
            status_score = 1.0
        elif status == 'dormant':
            status_score = 0.5
        else:
            status_score = 0.0
        components['company_status'] = status_score
        
        # Calculate proxy Z-score (scaled to typical Z-score range 0-4+)
        weighted_score = (
            age_score * 0.8 +
            accounts_score * 1.0 +
            charges_score * 1.2 +
            status_score * 1.0
        )
        z_score = round(weighted_score, 2)
        
        # Determine label and points
        if z_score > 3.0:
            label = "Very Safe"
            range_str = "> 3.0"
            points = 10
        elif z_score >= 2.5:
            label = "Safe"
            range_str = "2.5-3.0"
            points = 7
        elif z_score >= 1.5:
            label = "Watch"
            range_str = "1.5-2.5"
            points = 3
        else:
            label = "High Risk"
            range_str = "< 1.5"
            points = 0
        
        return AltmanZScoreProxy(
            z_score=z_score,
            z_score_label=label,
            z_score_range=range_str,
            score_points=points,
            components=components,
            methodology_note=(
                "Proxy Z-Score based on company age, accounts status, "
                "debt indicators, and operational status. "
                "True Altman Z-Score requires financial statements."
            )
        )
    
    def _calculate_accounts_score(self, profile: Dict) -> int:
        """Calculate accounts score (0-5 points)"""
        accounts = profile.get('accounts', {})
        
        if accounts.get('overdue'):
            return 0
        
        last_accounts = accounts.get('last_accounts', {}).get('made_up_to')
        if not last_accounts:
            return 2
        
        try:
            last_date = datetime.strptime(last_accounts, '%Y-%m-%d').date()
            days_since = (date.today() - last_date).days
            
            if days_since < 400:
                return 5
            elif days_since < 600:
                return 3
            else:
                return 1
        except:
            return 2
    
    def _get_accounts_issues(self, profile: Dict) -> List[str]:
        """Get issues related to accounts"""
        issues = []
        accounts = profile.get('accounts', {})
        
        if accounts.get('overdue'):
            issues.append("Accounts filing overdue - compliance risk")
        
        last_accounts = accounts.get('last_accounts', {}).get('made_up_to')
        if last_accounts:
            try:
                last_date = datetime.strptime(last_accounts, '%Y-%m-%d').date()
                days_since = (date.today() - last_date).days
                if days_since > 730:
                    issues.append(f"Last accounts filed over 2 years ago ({days_since} days)")
            except:
                pass
        
        return issues
    
    def _get_charges_issues(self, charges: List[Dict]) -> List[str]:
        """Get issues related to charges"""
        issues = []
        outstanding = len([c for c in charges if not c.get('satisfied_on')])
        
        if outstanding >= 5:
            issues.append(f"High debt level: {outstanding} outstanding charges")
        elif outstanding >= 3:
            issues.append(f"{outstanding} outstanding charges registered")
        
        return issues
    
    def _calculate_risk_level(
        self,
        profile: Dict,
        total_score: int,
        issues: List[str]
    ) -> Tuple[str, int]:
        """Calculate overall risk level and score"""
        # Critical checks
        status = profile.get('company_status', '').lower()
        if status != 'active':
            return "Critical", 100
        
        if profile.get('has_insolvency_history'):
            return "Critical", 100
        
        # Score-based risk
        max_score = 20
        percentage = (total_score / max_score) * 100
        
        # Adjust for issues
        issue_penalty = len(issues) * 5
        risk_score = 100 - percentage + issue_penalty
        risk_score = max(0, min(100, risk_score))
        
        if risk_score >= 80:
            level = "Critical"
        elif risk_score >= 60:
            level = "High"
        elif risk_score >= 40:
            level = "Medium"
        elif risk_score >= 20:
            level = "Low"
        else:
            level = "Very Low"
        
        return level, int(risk_score)
    
    def _generate_recommendations(
        self,
        risk_level: str,
        issues: List[str],
        director_stability: DirectorStability,
        ownership_stability: OwnershipStability
    ) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if risk_level == "Critical":
            recommendations.append("⚠️ IMMEDIATE ACTION: Consider alternative care homes")
            recommendations.append("Contact local authority for emergency options")
        elif risk_level == "High":
            recommendations.append("Closely monitor this facility (weekly checks)")
            recommendations.append("Research alternative care home options")
        elif risk_level == "Medium":
            recommendations.append("Regular monitoring recommended (monthly)")
            recommendations.append("Review CQC reports when published")
        else:
            recommendations.append("Standard monitoring sufficient (quarterly)")
            recommendations.append("Facility appears financially stable")
        
        # Specific recommendations
        if director_stability.active_directors < 2:
            recommendations.append("Check for director appointments - governance gap")
        
        if ownership_stability.is_private_equity:
            recommendations.append("Monitor for fee increases - PE ownership")
        
        return recommendations
    
    def to_scoring_data(self, result: FinancialStabilityResult) -> Dict:
        """
        Convert result to data format for 156-point algorithm
        
        Returns dict for Financial Stability category (20 points)
        """
        return {
            'financial_stability_score': result.total_score,
            'altman_z_score': result.altman_z_score.z_score,
            'altman_z_label': result.altman_z_score.z_score_label,
            'altman_z_points': result.altman_z_score.score_points,
            'director_stability_score': result.director_stability.stability_score,
            'director_stability_label': result.director_stability.stability_label,
            'ownership_stability_score': result.ownership_stability.stability_score,
            'ownership_type': result.ownership_stability.ownership_type,
            'risk_level': result.risk_level,
            'risk_score': result.risk_score,
            'issues_count': len(result.issues),
            'company_age_years': result.company_age_years,
            'company_status': result.company_status
        }
    
    def to_report_section(self, result: FinancialStabilityResult) -> Dict:
        """
        Convert result to Professional Report section format
        
        Returns formatted section for PDF/HTML report
        """
        return {
            'title': 'Financial Stability Assessment',
            'company_info': {
                'name': result.company_name,
                'number': result.company_number,
                'status': result.company_status,
                'age_years': result.company_age_years,
                'incorporated': result.incorporation_date
            },
            'scores': {
                'total': f"{result.total_score}/20",
                'percentage': f"{int(result.total_score / 20 * 100)}%",
                'risk_level': result.risk_level,
                'risk_score': result.risk_score
            },
            'altman_z': {
                'score': result.altman_z_score.z_score,
                'label': result.altman_z_score.z_score_label,
                'range': result.altman_z_score.z_score_range,
                'points': f"{result.altman_z_score.score_points}/10",
                'note': result.altman_z_score.methodology_note
            },
            'directors': {
                'active': result.director_stability.active_directors,
                'label': result.director_stability.stability_label,
                'score': f"{result.director_stability.stability_score}/3",
                'avg_tenure': f"{result.director_stability.average_tenure_years} years",
                'longest_tenure': f"{result.director_stability.longest_tenure_years} years"
            },
            'ownership': {
                'type': result.ownership_stability.ownership_type,
                'label': result.ownership_stability.stability_label,
                'score': f"{result.ownership_stability.stability_score}/2",
                'is_pe': result.ownership_stability.is_private_equity,
                'has_offshore': result.ownership_stability.has_offshore_entities
            },
            'charges': result.charges_summary,
            'accounts': result.accounts_status,
            'issues': result.issues,
            'recommendations': result.recommendations,
            'analysis_date': result.analysis_date
        }


async def enrich_care_home_with_financial_data(
    care_home_name: str,
    address: Optional[str] = None,
    postcode: Optional[str] = None
) -> Optional[Dict]:
    """
    Convenience function to enrich a care home with financial data
    
    Args:
        care_home_name: Name of the care home
        address: Optional address
        postcode: Optional postcode
        
    Returns:
        Financial data dict or None if company not found
    """
    service = CompaniesHouseService()
    
    # Find company
    company_number = await service.find_company_for_care_home(
        care_home_name, address, postcode
    )
    
    if not company_number:
        return None
    
    # Get financial stability
    result = await service.get_financial_stability(company_number)
    
    return {
        'company_number': company_number,
        'scoring_data': service.to_scoring_data(result),
        'report_section': service.to_report_section(result),
        'raw_result': asdict(result)
    }

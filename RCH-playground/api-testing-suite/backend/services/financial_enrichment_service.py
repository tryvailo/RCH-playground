"""
Financial Enrichment Service
Enriches care home data with comprehensive financial information including:
- 3-year financial summary (revenue, profitability, working capital)
- Bankruptcy risk score (0-100) based on Altman Z-score
- UK industry benchmarks comparison
- Red flags detection
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, date, timedelta
import logging
from api_clients.companies_house_client import CompaniesHouseAPIClient

logger = logging.getLogger(__name__)


class FinancialEnrichmentService:
    """Service for enriching care home data with comprehensive financial information"""
    
    # UK Care Home Industry Benchmarks (based on industry research)
    UK_CARE_HOME_BENCHMARKS = {
        'revenue_growth_3yr_avg': 0.05,  # 5% average annual growth
        'net_margin_avg': 0.12,  # 12% average net margin
        'current_ratio_avg': 1.5,  # 1.5 average current ratio
        'debt_to_equity_avg': 0.6,  # 0.6 average debt-to-equity
        'working_capital_avg': 0.15,  # 15% of revenue average
        'altman_z_safe': 2.99,  # Safe zone threshold
        'altman_z_gray': 1.81,  # Gray zone threshold
    }
    
    def __init__(self, companies_house_client: Optional[CompaniesHouseAPIClient] = None, api_key: Optional[str] = None):
        """
        Initialize Financial Enrichment Service
        
        Args:
            companies_house_client: Optional Companies House API client instance.
            api_key: Optional API key for Companies House (if client not provided).
        """
        if companies_house_client:
            self.companies_house_client = companies_house_client
        elif api_key:
            self.companies_house_client = CompaniesHouseAPIClient(api_key)
        else:
            # Try to get from environment
            import os
            api_key = os.getenv("COMPANIES_HOUSE_API_KEY")
            if api_key:
                self.companies_house_client = CompaniesHouseAPIClient(api_key)
            else:
                # Create a mock client that will return default data
                self.companies_house_client = None
    
    async def enrich_financial_data(
        self,
        company_number: str,
        years: int = 3
    ) -> Dict[str, Any]:
        """
        Enrich care home data with comprehensive financial information.
        
        Args:
            company_number: Companies House company number
            years: Number of years for financial summary (default 3)
        
        Returns:
            Dict with enriched financial data:
            - 3_year_summary: Revenue, profitability, working capital trends
            - altman_z_score: Calculated Altman Z-score
            - bankruptcy_risk_score: Risk score 0-100 (>60 = high risk)
            - uk_benchmarks_comparison: Comparison to UK industry averages
            - red_flags: List of detected red flags
        """
        if not self.companies_house_client:
            logger.warning(f"No Companies House client available, returning default data for {company_number}")
            return self._get_default_financial_data(company_number)
        
        try:
            # Get company profile
            profile = await self.companies_house_client.get_company_profile(company_number)
            if not profile:
                return self._get_default_financial_data(company_number)
            
            # Get filing history to find accounts
            filings = await self.companies_house_client.get_filing_history(
                company_number, 
                items_per_page=100
            )
            
            # Extract financial data from accounts
            financial_years = self._extract_financial_data_from_filings(filings, years)
            
            # Calculate 3-year summary
            three_year_summary = self._calculate_three_year_summary(financial_years)
            
            # Calculate Altman Z-score
            altman_z_score = self._calculate_altman_z_score(financial_years)
            
            # Calculate bankruptcy risk score (0-100)
            bankruptcy_risk_score = self._calculate_bankruptcy_risk_score(altman_z_score, financial_years)
            
            # Compare to UK benchmarks
            uk_benchmarks_comparison = self._compare_to_uk_benchmarks(three_year_summary, altman_z_score)
            
            # Detect red flags
            red_flags = self._detect_red_flags(profile, financial_years, filings)
            
            # Build enriched data structure
            enriched_data = {
                'company_number': company_number,
                'company_name': profile.get('company_name', ''),
                'company_status': profile.get('company_status', ''),
                
                'three_year_summary': three_year_summary,
                
                'altman_z_score': altman_z_score,
                'altman_z_interpretation': self._interpret_altman_z(altman_z_score),
                
                'bankruptcy_risk_score': bankruptcy_risk_score,
                'bankruptcy_risk_level': self._get_risk_level(bankruptcy_risk_score),
                
                'uk_benchmarks_comparison': uk_benchmarks_comparison,
                
                'red_flags': red_flags,
                'red_flags_count': len(red_flags),
                
                'filing_compliance': self._check_filing_compliance(profile, filings),
                
                'enrichment_date': datetime.now().isoformat()
            }
            
            logger.info(f"Financial data enriched for company {company_number}: "
                       f"altman_z={altman_z_score:.2f}, "
                       f"risk_score={bankruptcy_risk_score}, "
                       f"red_flags={len(red_flags)}")
            
            return enriched_data
            
        except Exception as e:
            logger.error(f"Error enriching financial data for company {company_number}: {str(e)}")
            return self._get_default_financial_data(company_number, error=str(e))
    
    def _extract_financial_data_from_filings(
        self,
        filings: List[Dict],
        years: int
    ) -> List[Dict[str, Any]]:
        """
        Extract financial data from Companies House filings.
        
        Note: This is a simplified extraction. In production, you would need to:
        1. Download account documents (PDF/XBRL)
        2. Parse structured data from XBRL or extract from PDF
        3. Extract balance sheet and profit & loss data
        
        For now, we'll use a mock structure that can be populated with real data.
        """
        financial_years = []
        
        # Filter for accounts filings
        accounts_filings = [
            f for f in filings 
            if f.get('category') == 'accounts' and f.get('subcategory') in ['full', 'small-full', 'micro-entity']
        ]
        
        # Sort by date (newest first)
        accounts_filings.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        # Extract up to 'years' most recent accounts
        cutoff_date = date.today() - timedelta(days=years * 365)
        
        for filing in accounts_filings[:years]:
            filing_date_str = filing.get('date')
            if not filing_date_str:
                continue
            
            try:
                filing_date = datetime.strptime(filing_date_str, "%Y-%m-%d").date()
                if filing_date < cutoff_date:
                    continue
                
                # In production, download and parse the actual accounts document
                # For now, return structure that can be populated
                financial_years.append({
                    'year': filing_date.year,
                    'date': filing_date_str,
                    'filing_id': filing.get('transaction_id'),
                    'revenue': None,  # Would be extracted from accounts
                    'profit_before_tax': None,
                    'profit_after_tax': None,
                    'total_assets': None,
                    'current_assets': None,
                    'current_liabilities': None,
                    'total_liabilities': None,
                    'retained_earnings': None,
                    'ebit': None,
                    'working_capital': None,
                    'net_margin': None,
                    'current_ratio': None,
                })
            except ValueError:
                continue
        
        return financial_years
    
    def _calculate_three_year_summary(
        self,
        financial_years: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate 3-year financial summary"""
        if not financial_years:
            return {
                'revenue_trend': 'unknown',
                'revenue_3yr_avg': None,
                'revenue_growth_rate': None,
                'profitability_trend': 'unknown',
                'net_margin_3yr_avg': None,
                'working_capital_trend': 'unknown',
                'working_capital_3yr_avg': None,
                'current_ratio_3yr_avg': None,
                'debt_levels': 'unknown',
                'debt_to_equity_avg': None,
            }
        
        # Calculate averages (filtering None values)
        revenues = [f.get('revenue') for f in financial_years if f.get('revenue') is not None]
        margins = [f.get('net_margin') for f in financial_years if f.get('net_margin') is not None]
        working_capitals = [f.get('working_capital') for f in financial_years if f.get('working_capital') is not None]
        current_ratios = [f.get('current_ratio') for f in financial_years if f.get('current_ratio') is not None]
        
        # Revenue trend
        revenue_trend = 'stable'
        if len(revenues) >= 2:
            rev0 = revenues[0]
            rev_last = revenues[-1]
            if rev0 is not None and rev_last is not None:
                try:
                    rev0_float = float(rev0)
                    rev_last_float = float(rev_last)
                    if rev0_float > rev_last_float * 1.1:
                        revenue_trend = 'increasing'
                    elif rev0_float < rev_last_float * 0.9:
                        revenue_trend = 'decreasing'
                except (ValueError, TypeError):
                    pass
        
        # Profitability trend
        profitability_trend = 'stable'
        if len(margins) >= 2:
            margin0 = margins[0]
            margin_last = margins[-1]
            if margin0 is not None and margin_last is not None:
                try:
                    margin0_float = float(margin0)
                    margin_last_float = float(margin_last)
                    if margin0_float > margin_last_float + 0.02:
                        profitability_trend = 'improving'
                    elif margin0_float < margin_last_float - 0.02:
                        profitability_trend = 'declining'
                except (ValueError, TypeError):
                    pass
        
        # Working capital trend
        working_capital_trend = 'stable'
        if len(working_capitals) >= 2:
            wc0 = working_capitals[0]
            wc_last = working_capitals[-1]
            if wc0 is not None and wc_last is not None:
                try:
                    wc0_float = float(wc0)
                    wc_last_float = float(wc_last)
                    if wc0_float > wc_last_float * 1.1:
                        working_capital_trend = 'improving'
                    elif wc0_float < wc_last_float * 0.9:
                        working_capital_trend = 'declining'
                except (ValueError, TypeError):
                    pass
        
        return {
            'revenue_trend': revenue_trend,
            'revenue_3yr_avg': sum(revenues) / len(revenues) if revenues else None,
            'revenue_growth_rate': self._calculate_growth_rate(revenues) if len(revenues) >= 2 else None,
            'profitability_trend': profitability_trend,
            'net_margin_3yr_avg': sum(margins) / len(margins) if margins else None,
            'working_capital_trend': working_capital_trend,
            'working_capital_3yr_avg': sum(working_capitals) / len(working_capitals) if working_capitals else None,
            'current_ratio_3yr_avg': sum(current_ratios) / len(current_ratios) if current_ratios else None,
            'debt_levels': 'unknown',  # Would need total_liabilities data
            'debt_to_equity_avg': None,  # Would need equity data
        }
    
    def _calculate_altman_z_score(
        self,
        financial_years: List[Dict[str, Any]]
    ) -> Optional[float]:
        """
        Calculate Altman Z-score for bankruptcy risk prediction.
        
        Formula: Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
        
        Where:
        - X1 = Working Capital / Total Assets
        - X2 = Retained Earnings / Total Assets
        - X3 = EBIT / Total Assets
        - X4 = Market Value of Equity / Book Value of Liabilities
        - X5 = Sales / Total Assets
        
        Risk zones:
        - Z > 2.99: Safe zone
        - 1.81-2.99: Gray zone
        - Z < 1.81: High risk zone
        """
        if not financial_years:
            return None
        
        # Use most recent year's data
        latest = financial_years[0]
        
        total_assets = latest.get('total_assets')
        if not total_assets or total_assets == 0:
            return None
        
        # X1 = Working Capital / Total Assets
        working_capital = latest.get('working_capital')
        if working_capital is None:
            # Calculate from current assets - current liabilities
            current_assets = latest.get('current_assets', 0)
            current_liabilities = latest.get('current_liabilities', 0)
            working_capital = current_assets - current_liabilities
        x1 = working_capital / total_assets if total_assets > 0 else 0
        
        # X2 = Retained Earnings / Total Assets
        retained_earnings = latest.get('retained_earnings', 0)
        x2 = retained_earnings / total_assets if total_assets > 0 else 0
        
        # X3 = EBIT / Total Assets
        ebit = latest.get('ebit', 0)
        x3 = ebit / total_assets if total_assets > 0 else 0
        
        # X4 = Market Value of Equity / Book Value of Liabilities
        # For private companies, use book value of equity instead
        total_liabilities = latest.get('total_liabilities', 0)
        equity = total_assets - total_liabilities
        x4 = equity / total_liabilities if total_liabilities > 0 else 1.0
        
        # X5 = Sales / Total Assets
        revenue = latest.get('revenue', 0)
        x5 = revenue / total_assets if total_assets > 0 else 0
        
        # Calculate Z-score
        z_score = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5
        
        return round(z_score, 2)
    
    def _calculate_bankruptcy_risk_score(
        self,
        altman_z_score: Optional[float],
        financial_years: List[Dict[str, Any]]
    ) -> int:
        """
        Calculate bankruptcy risk score (0-100, where >60 = high risk).
        
        Score calculation:
        - Based on Altman Z-score zones
        - Additional factors: negative working capital, declining revenue, etc.
        """
        if altman_z_score is None:
            return 50  # Unknown risk
        
        # Base score from Altman Z-score
        if altman_z_score < 1.81:
            base_score = 80  # High risk
        elif altman_z_score < 2.99:
            base_score = 50  # Gray zone
        else:
            base_score = 20  # Safe zone
        
        # Adjust for additional factors
        if financial_years:
            latest = financial_years[0]
            
            # Negative working capital
            working_capital = latest.get('working_capital')
            if working_capital is not None and working_capital < 0:
                base_score += 15
            
            # Declining revenue
            if len(financial_years) >= 2:
                revenue_current = financial_years[0].get('revenue')
                revenue_previous = financial_years[1].get('revenue')
                if revenue_current and revenue_previous and revenue_current < revenue_previous * 0.9:
                    base_score += 10
            
            # Negative profit margin
            net_margin = latest.get('net_margin')
            if net_margin is not None and net_margin < 0:
                base_score += 10
        
        return min(max(base_score, 0), 100)
    
    def _compare_to_uk_benchmarks(
        self,
        three_year_summary: Dict[str, Any],
        altman_z_score: Optional[float]
    ) -> Dict[str, Any]:
        """Compare company metrics to UK care home industry benchmarks"""
        benchmarks = self.UK_CARE_HOME_BENCHMARKS
        
        comparison = {
            'revenue_growth': {
                'company': three_year_summary.get('revenue_growth_rate'),
                'industry_avg': benchmarks['revenue_growth_3yr_avg'],
                'vs_industry': 'unknown'
            },
            'net_margin': {
                'company': three_year_summary.get('net_margin_3yr_avg'),
                'industry_avg': benchmarks['net_margin_avg'],
                'vs_industry': 'unknown'
            },
            'current_ratio': {
                'company': three_year_summary.get('current_ratio_3yr_avg'),
                'industry_avg': benchmarks['current_ratio_avg'],
                'vs_industry': 'unknown'
            },
            'altman_z_score': {
                'company': altman_z_score,
                'industry_safe_threshold': benchmarks['altman_z_safe'],
                'vs_industry': 'unknown'
            }
        }
        
        # Calculate comparisons
        if comparison['revenue_growth']['company'] is not None:
            company_growth = comparison['revenue_growth']['company']
            industry_growth = comparison['revenue_growth']['industry_avg']
            if company_growth > industry_growth * 1.1:
                comparison['revenue_growth']['vs_industry'] = 'above_average'
            elif company_growth < industry_growth * 0.9:
                comparison['revenue_growth']['vs_industry'] = 'below_average'
            else:
                comparison['revenue_growth']['vs_industry'] = 'average'
        
        if comparison['net_margin']['company'] is not None:
            company_margin = comparison['net_margin']['company']
            industry_margin = comparison['net_margin']['industry_avg']
            if company_margin > industry_margin * 1.1:
                comparison['net_margin']['vs_industry'] = 'above_average'
            elif company_margin < industry_margin * 0.9:
                comparison['net_margin']['vs_industry'] = 'below_average'
            else:
                comparison['net_margin']['vs_industry'] = 'average'
        
        if comparison['current_ratio']['company'] is not None:
            company_ratio = comparison['current_ratio']['company']
            industry_ratio = comparison['current_ratio']['industry_avg']
            if company_ratio > industry_ratio * 1.2:
                comparison['current_ratio']['vs_industry'] = 'above_average'
            elif company_ratio < industry_ratio * 0.8:
                comparison['current_ratio']['vs_industry'] = 'below_average'
            else:
                comparison['current_ratio']['vs_industry'] = 'average'
        
        if altman_z_score is not None:
            if altman_z_score >= benchmarks['altman_z_safe']:
                comparison['altman_z_score']['vs_industry'] = 'safe'
            elif altman_z_score >= benchmarks['altman_z_gray']:
                comparison['altman_z_score']['vs_industry'] = 'gray_zone'
            else:
                comparison['altman_z_score']['vs_industry'] = 'high_risk'
        
        return comparison
    
    def _detect_red_flags(
        self,
        profile: Dict[str, Any],
        financial_years: List[Dict[str, Any]],
        filings: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Detect financial red flags"""
        red_flags = []
        
        # 1. Company status
        status = profile.get('company_status', '').lower()
        if status != 'active':
            red_flags.append({
                'type': 'company_status',
                'severity': 'critical',
                'description': f'Company status is {status}',
                'impact': 'Company is not active - do not recommend'
            })
        
        # 2. Insolvency history
        if profile.get('has_insolvency_history'):
            red_flags.append({
                'type': 'insolvency_history',
                'severity': 'critical',
                'description': 'Company has insolvency history',
                'impact': 'High risk of financial failure'
            })
        
        # 3. Accounts overdue
        accounts = profile.get('accounts', {})
        if accounts.get('overdue', False):
            red_flags.append({
                'type': 'accounts_overdue',
                'severity': 'high',
                'description': 'Accounts filing is overdue',
                'impact': 'May indicate financial difficulties or management issues'
            })
        
        # 4. Negative working capital
        if financial_years:
            latest = financial_years[0]
            working_capital = latest.get('working_capital')
            if working_capital is not None and working_capital < 0:
                red_flags.append({
                    'type': 'negative_working_capital',
                    'severity': 'high',
                    'description': 'Negative working capital',
                    'impact': 'May indicate liquidity problems'
                })
        
        # 5. Declining revenue trend
        if len(financial_years) >= 2:
            revenue_current = financial_years[0].get('revenue')
            revenue_previous = financial_years[1].get('revenue')
            if revenue_current and revenue_previous and revenue_current < revenue_previous * 0.85:
                red_flags.append({
                    'type': 'declining_revenue',
                    'severity': 'medium',
                    'description': f'Revenue declined by {(1 - revenue_current/revenue_previous)*100:.1f}%',
                    'impact': 'May indicate business challenges'
                })
        
        # 6. Low Altman Z-score
        if financial_years:
            altman_z = self._calculate_altman_z_score(financial_years)
            if altman_z is not None and altman_z < 1.81:
                red_flags.append({
                    'type': 'low_altman_z_score',
                    'severity': 'high',
                    'description': f'Altman Z-score is {altman_z:.2f} (high risk zone)',
                    'impact': 'High bankruptcy risk'
                })
        
        # 7. Late filing detection
        if filings:
            recent_filings = sorted(filings, key=lambda x: x.get('date', ''), reverse=True)[:5]
            # Check if filings are significantly delayed
            # (This would need more sophisticated logic in production)
        
        return red_flags
    
    def _check_filing_compliance(
        self,
        profile: Dict[str, Any],
        filings: List[Dict]
    ) -> Dict[str, Any]:
        """Check filing compliance and timeliness"""
        accounts = profile.get('accounts', {})
        
        return {
            'accounts_overdue': accounts.get('overdue', False),
            'last_accounts_date': accounts.get('last_accounts', {}).get('made_up_to'),
            'next_accounts_due': accounts.get('next_due'),
            'filing_timeliness': 'compliant' if not accounts.get('overdue') else 'overdue'
        }
    
    def _calculate_growth_rate(self, values: List[float]) -> Optional[float]:
        """Calculate average annual growth rate"""
        if len(values) < 2:
            return None
        
        # Calculate CAGR (Compound Annual Growth Rate)
        start_value = values[-1]
        end_value = values[0]
        years = len(values) - 1
        
        if start_value <= 0:
            return None
        
        growth_rate = ((end_value / start_value) ** (1 / years)) - 1
        return round(growth_rate, 4)
    
    def _interpret_altman_z(self, z_score: Optional[float]) -> str:
        """Interpret Altman Z-score"""
        if z_score is None:
            return 'Unknown'
        elif z_score > 2.99:
            return 'Safe zone - Low bankruptcy risk'
        elif z_score >= 1.81:
            return 'Gray zone - Moderate bankruptcy risk'
        else:
            return 'High risk zone - High bankruptcy risk'
    
    def _get_risk_level(self, risk_score: int) -> str:
        """Get risk level from risk score"""
        if risk_score >= 60:
            return 'HIGH'
        elif risk_score >= 40:
            return 'MEDIUM'
        elif risk_score >= 20:
            return 'LOW'
        else:
            return 'VERY_LOW'
    
    def _get_default_financial_data(
        self,
        company_number: str,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Return default financial data structure when enrichment fails"""
        return {
            'company_number': company_number,
            'company_name': '',
            'company_status': 'unknown',
            'three_year_summary': {},
            'altman_z_score': None,
            'altman_z_interpretation': 'Unknown',
            'bankruptcy_risk_score': 50,
            'bankruptcy_risk_level': 'UNKNOWN',
            'uk_benchmarks_comparison': {},
            'red_flags': [],
            'red_flags_count': 0,
            'filing_compliance': {},
            'error': error,
            'enrichment_date': datetime.now().isoformat()
        }
    
    async def close(self):
        """Close Companies House client connection"""
        if self.companies_house_client:
            await self.companies_house_client.close()
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()


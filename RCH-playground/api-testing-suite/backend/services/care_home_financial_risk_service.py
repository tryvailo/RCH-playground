"""
Care Home Financial Risk Service
Implements Custom Care Home Financial Risk Model according to PROFESSIONAL_REPORT_SPEC_v3.2

⚠️ CRITICAL: Does NOT use Altman Z-Score!
Altman Z-Score is designed for manufacturing, not suitable for care homes:
- Care homes = asset-heavy (property)
- Low current ratios are normal
- Intangible assets significant (licenses, reputation)

Uses Custom Model with 5 components:
1. LIQUIDITY (30% weight) - Current ratio
2. DEBT BURDEN (25% weight) - Debt/EBITDA
3. PROFITABILITY (25% weight) - Profit trend
4. MANAGEMENT STABILITY (10% weight) - Director changes
5. MATURITY (10% weight) - Company age
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from decimal import Decimal
from datetime import date, datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class RiskComponent:
    """Individual risk component"""
    level: str  # "LOW" / "MEDIUM" / "HIGH"
    score: int  # Contribution to total (0-30 for liquidity, 0-25 for debt/profitability, 0-10 for management/maturity)
    detail: str  # Explanation


@dataclass
class RiskBreakdown:
    """Breakdown of risk components"""
    liquidity: RiskComponent
    debt: RiskComponent
    profitability: RiskComponent
    management: RiskComponent
    maturity: RiskComponent


@dataclass
class FinancialRiskResult:
    """Complete financial risk assessment result"""
    risk_score: int  # 0-100 (lower = safer)
    risk_level: str  # "Low Risk - Financially stable" / "Medium Risk - Some concerns" / "High Risk - Significant concerns"
    breakdown: RiskBreakdown
    components: Dict[str, RiskComponent]  # For easy access
    
    # Additional context
    current_ratio: Optional[float]
    debt_to_ebitda: Optional[float]
    profit_trend: str
    director_changes_3yr: int
    company_age_years: float


class CareHomeFinancialRiskService:
    """Service for calculating Custom Care Home Financial Risk Model"""
    
    def calculate_financial_risk(
        self,
        ch_data: Dict[str, Any],
        companies_house_data: Optional[Dict[str, Any]] = None
    ) -> FinancialRiskResult:
        """
        Calculate financial risk using Custom Care Home Financial Risk Model
        
        According to PROFESSIONAL_REPORT_SPEC_v3.2 (lines 1941-2042)
        
        Args:
            ch_data: Care home financial data dictionary with:
                - current_assets: Decimal or float
                - current_liabilities: Decimal or float
                - total_debt: Decimal or float
                - equity: Decimal or float
                - profit_loss: Decimal or float (profit if positive, loss if negative)
                - depreciation: Decimal or float (optional)
                - profit_trend: str ("growing", "stable", "declining", "unknown")
                - director_changes_3yr: int
                - company_age_years: float
            companies_house_data: Optional Companies House data for enrichment
            
        Returns:
            FinancialRiskResult with risk score, level, and breakdown
        """
        # Extract financial data with safe defaults
        current_assets = self._to_decimal(ch_data.get('current_assets', 0))
        current_liabilities = self._to_decimal(ch_data.get('current_liabilities', 1))
        total_debt = self._to_decimal(ch_data.get('total_debt', 0))
        equity = self._to_decimal(ch_data.get('equity', 1))
        profit = self._to_decimal(ch_data.get('profit_loss', 0))
        depreciation = self._to_decimal(ch_data.get('depreciation', 0))
        
        # Estimate EBITDA
        ebitda = max(profit + depreciation, Decimal('1'))
        
        # Extract trend and stability data
        profit_trend = ch_data.get('profit_trend', 'unknown')
        director_changes_3yr = ch_data.get('director_changes_3yr', 0)
        company_age_years = ch_data.get('company_age_years', 0.0)
        
        # If Companies House data available, enrich
        if companies_house_data:
            if 'director_changes_3yr' not in ch_data:
                director_changes_3yr = self._extract_director_changes_3yr(companies_house_data)
            if 'company_age_years' not in ch_data or company_age_years == 0:
                company_age_years = self._extract_company_age(companies_house_data)
            if 'profit_trend' not in ch_data or profit_trend == 'unknown':
                profit_trend = self._extract_profit_trend(companies_house_data, profit)
        
        components = {}
        total_score = 0
        
        # ========================================================================
        # 1. LIQUIDITY (30% weight)
        # ========================================================================
        current_ratio = current_assets / current_liabilities if current_liabilities > 0 else Decimal('0')
        current_ratio_float = float(current_ratio)
        
        if current_ratio < Decimal('0.8'):
            components['liquidity'] = RiskComponent(
                "HIGH",
                30,
                f"Current ratio: {current_ratio:.2f} (below 0.8 indicates liquidity stress)"
            )
            total_score += 30
        elif current_ratio < Decimal('1.2'):
            components['liquidity'] = RiskComponent(
                "MEDIUM",
                15,
                f"Current ratio: {current_ratio:.2f} (below 1.2 indicates moderate liquidity)"
            )
            total_score += 15
        else:
            components['liquidity'] = RiskComponent(
                "LOW",
                0,
                f"Current ratio: {current_ratio:.2f} (healthy liquidity position)"
            )
        
        # ========================================================================
        # 2. DEBT BURDEN (25% weight) - Debt/EBITDA
        # ========================================================================
        debt_to_ebitda = total_debt / ebitda if ebitda > 0 else Decimal('999')
        debt_to_ebitda_float = float(debt_to_ebitda)
        
        if debt_to_ebitda > Decimal('4.0'):
            components['debt'] = RiskComponent(
                "HIGH",
                25,
                f"Debt/EBITDA: {debt_to_ebitda:.1f}x (above 4.0x indicates high debt burden)"
            )
            total_score += 25
        elif debt_to_ebitda > Decimal('2.5'):
            components['debt'] = RiskComponent(
                "MEDIUM",
                12,
                f"Debt/EBITDA: {debt_to_ebitda:.1f}x (moderate debt burden)"
            )
            total_score += 12
        else:
            components['debt'] = RiskComponent(
                "LOW",
                0,
                f"Debt/EBITDA: {debt_to_ebitda:.1f}x (manageable debt levels)"
            )
        
        # ========================================================================
        # 3. PROFITABILITY (25% weight)
        # ========================================================================
        if profit_trend == 'declining' or profit < 0:
            components['profitability'] = RiskComponent(
                "HIGH",
                25,
                f"Profit trend: {profit_trend}, Profit: £{profit:,.0f} (declining profitability or losses)"
            )
            total_score += 25
        elif profit_trend == 'stable':
            components['profitability'] = RiskComponent(
                "MEDIUM",
                10,
                f"Profit trend: {profit_trend} (stable but not growing)"
            )
            total_score += 10
        else:  # growing or unknown (assume growing if profit > 0)
            if profit > 0:
                components['profitability'] = RiskComponent(
                    "LOW",
                    0,
                    f"Profit trend: {profit_trend if profit_trend != 'unknown' else 'growing'}, Profit: £{profit:,.0f} (positive profitability)"
                )
            else:
                # Unknown trend but no profit - medium risk
                components['profitability'] = RiskComponent(
                    "MEDIUM",
                    10,
                    f"Profit trend: unknown, Profit: £{profit:,.0f} (uncertain profitability)"
                )
                total_score += 10
        
        # ========================================================================
        # 4. MANAGEMENT STABILITY (10% weight)
        # ========================================================================
        if director_changes_3yr > 3:
            components['management'] = RiskComponent(
                "HIGH",
                10,
                f"{director_changes_3yr} director changes in 3 years (high management turnover)"
            )
            total_score += 10
        elif director_changes_3yr > 1:
            components['management'] = RiskComponent(
                "MEDIUM",
                5,
                f"{director_changes_3yr} director changes in 3 years (moderate turnover)"
            )
            total_score += 5
        else:
            components['management'] = RiskComponent(
                "LOW",
                0,
                f"{director_changes_3yr} director changes in 3 years (stable management)"
            )
        
        # ========================================================================
        # 5. MATURITY (10% weight)
        # ========================================================================
        if company_age_years < 3:
            components['maturity'] = RiskComponent(
                "HIGH",
                10,
                f"{company_age_years:.1f} years old (new company, unproven track record)"
            )
            total_score += 10
        elif company_age_years < 7:
            components['maturity'] = RiskComponent(
                "MEDIUM",
                5,
                f"{company_age_years:.1f} years old (relatively new company)"
            )
            total_score += 5
        else:
            components['maturity'] = RiskComponent(
                "LOW",
                0,
                f"{company_age_years:.1f} years old (established company with proven track record)"
            )
        
        # ========================================================================
        # Determine overall risk level
        # ========================================================================
        if total_score <= 20:
            risk_level = "Low Risk - Financially stable"
        elif total_score <= 45:
            risk_level = "Medium Risk - Some concerns"
        else:
            risk_level = "High Risk - Significant concerns"
        
        breakdown = RiskBreakdown(
            liquidity=components['liquidity'],
            debt=components['debt'],
            profitability=components['profitability'],
            management=components['management'],
            maturity=components['maturity']
        )
        
        return FinancialRiskResult(
            risk_score=total_score,
            risk_level=risk_level,
            breakdown=breakdown,
            components=components,
            current_ratio=current_ratio_float,
            debt_to_ebitda=debt_to_ebitda_float,
            profit_trend=profit_trend,
            director_changes_3yr=director_changes_3yr,
            company_age_years=company_age_years
        )
    
    def _to_decimal(self, value: Any) -> Decimal:
        """Convert value to Decimal safely"""
        if value is None:
            return Decimal('0')
        if isinstance(value, Decimal):
            return value
        try:
            return Decimal(str(value))
        except (ValueError, TypeError):
            return Decimal('0')
    
    def _extract_director_changes_3yr(self, ch_data: Dict[str, Any]) -> int:
        """Extract director changes in last 3 years from Companies House data"""
        officers = ch_data.get('officers', [])
        if not officers:
            return 0
        
        three_years_ago = datetime.now() - timedelta(days=3*365)
        changes = 0
        
        for officer in officers:
            if officer.get('officer_role') == 'director':
                resigned_str = officer.get('resigned_on')
                if resigned_str:
                    try:
                        resigned_date = datetime.strptime(resigned_str, '%Y-%m-%d')
                        if resigned_date >= three_years_ago:
                            changes += 1
                    except (ValueError, TypeError):
                        pass
        
        return changes
    
    def _extract_company_age(self, ch_data: Dict[str, Any]) -> float:
        """Extract company age in years from Companies House data"""
        creation_date_str = ch_data.get('date_of_creation') or ch_data.get('incorporation_date')
        if not creation_date_str:
            return 0.0
        
        try:
            creation_date = datetime.strptime(creation_date_str, '%Y-%m-%d').date()
            age_days = (date.today() - creation_date).days
            return round(age_days / 365.25, 1)
        except (ValueError, TypeError):
            return 0.0
    
    def _extract_profit_trend(self, ch_data: Dict[str, Any], current_profit: Decimal) -> str:
        """Extract profit trend from Companies House data or infer from current profit"""
        # Try to get from accounts if available
        accounts = ch_data.get('accounts', {})
        if accounts:
            # Could analyze filing history for trend, but for now infer from current
            pass
        
        # Infer from current profit
        if current_profit > 0:
            return 'growing'
        elif current_profit < 0:
            return 'declining'
        else:
            return 'stable'
    
    def to_dict(self, result: FinancialRiskResult) -> Dict[str, Any]:
        """Convert FinancialRiskResult to dictionary for API response"""
        return {
            "risk_score": result.risk_score,
            "risk_level": result.risk_level,
            "breakdown": {
                "liquidity": {
                    "level": result.breakdown.liquidity.level,
                    "score": result.breakdown.liquidity.score,
                    "detail": result.breakdown.liquidity.detail
                },
                "debt": {
                    "level": result.breakdown.debt.level,
                    "score": result.breakdown.debt.score,
                    "detail": result.breakdown.debt.detail
                },
                "profitability": {
                    "level": result.breakdown.profitability.level,
                    "score": result.breakdown.profitability.score,
                    "detail": result.breakdown.profitability.detail
                },
                "management": {
                    "level": result.breakdown.management.level,
                    "score": result.breakdown.management.score,
                    "detail": result.breakdown.management.detail
                },
                "maturity": {
                    "level": result.breakdown.maturity.level,
                    "score": result.breakdown.maturity.score,
                    "detail": result.breakdown.maturity.detail
                }
            },
            "current_ratio": result.current_ratio,
            "debt_to_ebitda": result.debt_to_ebitda,
            "profit_trend": result.profit_trend,
            "director_changes_3yr": result.director_changes_3yr,
            "company_age_years": result.company_age_years,
            "methodology": "Custom Care Home Financial Risk Model (SPEC v3.2) - NOT Altman Z-Score"
        }


#!/usr/bin/env python3
"""
RightCareHome - Companies House Financial Analyzer
Полный production-ready модуль для анализа финансовой устойчивости домов престарелых

Использование:
    from companies_house_analyzer import CompaniesHouseFinancialAnalyzer
    
    analyzer = CompaniesHouseFinancialAnalyzer(api_key="YOUR_KEY")
    
    # Анализ одного дома
    result = analyzer.analyze_care_home("Manor House Care Limited")
    print(result.format_for_premium())
    
    # Пакетный анализ нескольких домов
    homes = ["Manor House Care Ltd", "Oakwood Residential", "Greenfield Care"]
    comparison = analyzer.compare_multiple_homes(homes)
"""

import requests
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
from dataclasses import dataclass
from enum import Enum
import json


class FinancialRisk(Enum):
    """Уровни финансового риска"""
    CRITICAL = ("🚨 CRITICAL", 5, "Do not recommend - severe financial distress")
    HIGH = ("🔴 HIGH", 4, "Significant concerns - use caution")
    MEDIUM = ("🟡 MEDIUM", 3, "Some concerns - monitor carefully")
    LOW = ("🟢 LOW", 2, "Minor concerns - generally safe")
    MINIMAL = ("✅ MINIMAL", 1, "Excellent financial health")
    
    def __init__(self, label: str, score: int, description: str):
        self.label = label
        self.score = score
        self.description = description


@dataclass
class FinancialMetrics:
    """Финансовые метрики компании"""
    company_number: str
    company_name: str
    status: str
    incorporation_date: date
    company_age_years: float
    accounts_overdue: bool
    last_accounts_date: Optional[date]
    days_since_accounts: Optional[int]
    next_accounts_due: Optional[date]
    has_charges: bool
    outstanding_charges: int
    total_charges: int
    has_insolvency: bool
    active_directors: int
    director_changes_last_year: int
    sic_codes: List[str]
    
    def calculate_risk_score(self) -> int:
        """Расчёт risk score (0-100, чем выше тем хуже)"""
        score = 0
        
        # Critical factors
        if self.status.lower() != 'active':
            return 100
        
        if self.has_insolvency:
            return 100
        
        # Accounts overdue (40 points)
        if self.accounts_overdue:
            score += 40
        
        # Outstanding charges (25 points)
        if self.outstanding_charges >= 3:
            score += 25
        elif self.outstanding_charges >= 1:
            score += 15
        
        # Company age (20 points)
        if self.company_age_years < 2:
            score += 20
        elif self.company_age_years < 5:
            score += 10
        
        # Director changes (15 points)
        if self.director_changes_last_year >= 3:
            score += 15
        elif self.director_changes_last_year >= 1:
            score += 10
        
        # Days since accounts (20 points)
        if self.days_since_accounts:
            if self.days_since_accounts > 730:  # 2 years
                score += 20
            elif self.days_since_accounts > 365:  # 1 year
                score += 10
        
        return min(score, 100)
    
    def get_risk_level(self) -> FinancialRisk:
        """Определить уровень риска"""
        score = self.calculate_risk_score()
        
        if score >= 70:
            return FinancialRisk.CRITICAL
        elif score >= 50:
            return FinancialRisk.HIGH
        elif score >= 30:
            return FinancialRisk.MEDIUM
        elif score >= 10:
            return FinancialRisk.LOW
        else:
            return FinancialRisk.MINIMAL
    
    def to_dict(self) -> Dict:
        """Экспорт в словарь"""
        risk = self.get_risk_level()
        return {
            'company_number': self.company_number,
            'company_name': self.company_name,
            'status': self.status,
            'company_age_years': round(self.company_age_years, 1),
            'risk_score': self.calculate_risk_score(),
            'risk_level': risk.label,
            'risk_description': risk.description,
            'accounts_overdue': self.accounts_overdue,
            'outstanding_charges': self.outstanding_charges,
            'has_insolvency': self.has_insolvency,
            'active_directors': self.active_directors
        }


class CompaniesHouseFinancialAnalyzer:
    """
    Анализатор финансовой устойчивости для RightCareHome
    """
    
    BASE_URL = "https://api.company-information.service.gov.uk"
    
    # SIC коды для care homes
    CARE_HOME_SIC_CODES = [
        "87101",  # Residential nursing care
        "87300",  # Residential care for elderly/disabled
        "87200",  # Residential care for learning disabilities
        "87900",  # Other residential care
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация анализатора
        
        Args:
            api_key: Companies House API key (или из env COMPANIES_HOUSE_API_KEY)
        """
        self.api_key = api_key or os.environ.get('COMPANIES_HOUSE_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "API key required! Set COMPANIES_HOUSE_API_KEY env var or pass api_key parameter.\n"
                "Get your key at: https://developer.company-information.service.gov.uk/"
            )
        
        self.session = requests.Session()
        self.session.auth = (self.api_key, '')  # Basic auth: key as username
        self.session.headers.update({'Accept': 'application/json'})
    
    def _request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Выполнить HTTP запрос к API"""
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return {}
            print(f"❌ HTTP Error {e.response.status_code}: {e}")
            return {}
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return {}
    
    def search_company(self, name: str) -> Optional[str]:
        """
        Найти company_number по названию
        
        Args:
            name: Название компании
        
        Returns:
            Company number или None
        """
        data = self._request('search/companies', {'q': name, 'items_per_page': 5})
        items = data.get('items', [])
        
        if not items:
            return None
        
        # Приоритет: active status + care home SIC code
        for item in items:
            if item.get('company_status') == 'active':
                sic_codes = item.get('description_identifier', [])
                if any(code in self.CARE_HOME_SIC_CODES for code in sic_codes):
                    return item.get('company_number')
        
        # Fallback: первый active результат
        for item in items:
            if item.get('company_status') == 'active':
                return item.get('company_number')
        
        # Fallback: любой результат
        return items[0].get('company_number')
    
    def get_financial_metrics(self, company_number: str) -> Optional[FinancialMetrics]:
        """
        Получить финансовые метрики компании
        
        Args:
            company_number: Номер компании
        
        Returns:
            FinancialMetrics или None
        """
        # Get profile
        profile = self._request(f'company/{company_number}')
        
        if not profile:
            print(f"❌ Company {company_number} not found")
            return None
        
        # Parse dates
        creation_str = profile.get('date_of_creation', '')
        try:
            inc_date = datetime.strptime(creation_str, '%Y-%m-%d').date()
            age = (date.today() - inc_date).days / 365.25
        except:
            inc_date = date.today()
            age = 0
        
        # Accounts
        accounts = profile.get('accounts', {})
        overdue = accounts.get('overdue', False)
        
        last_accts = accounts.get('last_accounts', {})
        last_date_str = last_accts.get('made_up_to', '')
        
        try:
            last_date = datetime.strptime(last_date_str, '%Y-%m-%d').date()
            days_since = (date.today() - last_date).days
        except:
            last_date = None
            days_since = None
        
        next_due_str = accounts.get('next_due', '')
        try:
            next_due = datetime.strptime(next_due_str, '%Y-%m-%d').date()
        except:
            next_due = None
        
        # Charges
        has_charges = profile.get('has_charges', False)
        outstanding = 0
        total = 0
        
        if has_charges:
            charges = self._request(f'company/{company_number}/charges')
            total = charges.get('total_count', 0)
            items = charges.get('items', [])
            outstanding = sum(1 for i in items if i.get('status') == 'outstanding')
        
        # Insolvency
        has_insolvency = profile.get('has_insolvency_history', False)
        
        # Officers
        officers_data = self._request(f'company/{company_number}/officers')
        officers = officers_data.get('items', [])
        
        active_directors = [
            o for o in officers
            if o.get('officer_role') == 'director' and not o.get('resigned_on')
        ]
        
        # Count resignations in last year
        one_year_ago = date.today().replace(year=date.today().year - 1)
        recent_resignations = 0
        
        for officer in officers:
            if officer.get('officer_role') == 'director' and officer.get('resigned_on'):
                try:
                    resign_date = datetime.strptime(officer['resigned_on'], '%Y-%m-%d').date()
                    if resign_date >= one_year_ago:
                        recent_resignations += 1
                except:
                    pass
        
        return FinancialMetrics(
            company_number=company_number,
            company_name=profile.get('company_name', 'Unknown'),
            status=profile.get('company_status', 'unknown'),
            incorporation_date=inc_date,
            company_age_years=age,
            accounts_overdue=overdue,
            last_accounts_date=last_date,
            days_since_accounts=days_since,
            next_accounts_due=next_due,
            has_charges=has_charges,
            outstanding_charges=outstanding,
            total_charges=total,
            has_insolvency=has_insolvency,
            active_directors=len(active_directors),
            director_changes_last_year=recent_resignations,
            sic_codes=profile.get('sic_codes', [])
        )
    
    def analyze_care_home(self, care_home_name: str) -> Optional[FinancialMetrics]:
        """
        Анализировать дом престарелых по названию
        
        Args:
            care_home_name: Название дома
        
        Returns:
            FinancialMetrics или None
        """
        print(f"\n🔍 Searching for '{care_home_name}'...")
        
        company_number = self.search_company(care_home_name)
        
        if not company_number:
            print(f"❌ Not found: {care_home_name}")
            return None
        
        print(f"✅ Found company #{company_number}")
        print(f"📊 Analyzing financial health...")
        
        return self.get_financial_metrics(company_number)
    
    def compare_multiple_homes(self, care_home_names: List[str]) -> List[FinancialMetrics]:
        """
        Сравнить несколько домов престарелых
        
        Args:
            care_home_names: Список названий
        
        Returns:
            Список FinancialMetrics
        """
        results = []
        
        for name in care_home_names:
            metrics = self.analyze_care_home(name)
            if metrics:
                results.append(metrics)
        
        # Sort by risk (safest first)
        results.sort(key=lambda m: m.calculate_risk_score())
        
        return results
    
    # ==================== ФОРМАТИРОВАНИЕ ====================
    
    @staticmethod
    def format_for_free_tier(metrics: FinancialMetrics) -> str:
        """Форматирование для FREE tier"""
        risk = metrics.get_risk_level()
        
        return f"""
🏥 {metrics.company_name}
📊 Financial Health: {risk.label}
💼 Company Age: {metrics.company_age_years:.1f} years
{"✅ Financially Stable" if risk.score <= 2 else "⚠️ Monitor Financial Health"}
"""
    
    @staticmethod
    def format_for_professional_tier(metrics: FinancialMetrics) -> str:
        """Форматирование для Professional tier (£119)"""
        risk = metrics.get_risk_level()
        score = metrics.calculate_risk_score()
        
        output = f"""
{'='*70}
🏥 {metrics.company_name}
{'='*70}
Company Number: {metrics.company_number}
Incorporated: {metrics.incorporation_date.strftime('%d %b %Y')} ({metrics.company_age_years:.1f} years)
Status: {metrics.status.upper()}

💰 FINANCIAL HEALTH ASSESSMENT
{'='*70}

Overall Risk: {risk.label} ({risk.description})
Risk Score: {score}/100

📊 KEY INDICATORS:
"""
        
        # Status
        if metrics.status == 'active':
            output += "   ✅ Status: ACTIVE\n"
        else:
            output += f"   🚨 Status: {metrics.status.upper()}\n"
        
        # Accounts
        if metrics.accounts_overdue:
            output += "   🚨 Accounts: OVERDUE (major red flag)\n"
        else:
            output += "   ✅ Accounts: Current\n"
        
        if metrics.last_accounts_date:
            output += f"   📅 Last Filed: {metrics.last_accounts_date.strftime('%b %Y')} "
            output += f"({metrics.days_since_accounts} days ago)\n"
        
        # Charges
        if metrics.outstanding_charges > 0:
            output += f"   ⚠️ Outstanding Debts: {metrics.outstanding_charges} charges registered\n"
        else:
            output += "   ✅ No Outstanding Charges\n"
        
        # Insolvency
        if metrics.has_insolvency:
            output += "   🚨 Insolvency History: YES\n"
        else:
            output += "   ✅ Insolvency History: Clean\n"
        
        # Management
        output += f"   👥 Active Directors: {metrics.active_directors}\n"
        if metrics.director_changes_last_year > 0:
            output += f"   ⚠️ Director Changes: {metrics.director_changes_last_year} in last year\n"
        
        # Interpretation
        output += f"\n{'='*70}\n"
        output += "💡 INTERPRETATION:\n"
        output += f"{'='*70}\n"
        output += f"{risk.description}\n"
        
        if risk == FinancialRisk.CRITICAL:
            output += "\n🚨 NOT RECOMMENDED - Severe financial distress\n"
        elif risk == FinancialRisk.HIGH:
            output += "\n⚠️ USE CAUTION - Significant financial concerns\n"
        elif risk == FinancialRisk.MEDIUM:
            output += "\n⚠️ ACCEPTABLE - Monitor regularly\n"
        else:
            output += "\n✅ SAFE - Good financial health\n"
        
        return output
    
    @staticmethod
    def format_comparison_table(metrics_list: List[FinancialMetrics]) -> str:
        """Форматирование сравнительной таблицы"""
        
        output = "\n" + "="*90 + "\n"
        output += "📊 FINANCIAL COMPARISON TABLE\n"
        output += "="*90 + "\n\n"
        
        # Header
        output += f"{'Name':<35} {'Age':<8} {'Risk':<18} {'Overdue':<8} {'Charges':<8}\n"
        output += "-" * 90 + "\n"
        
        # Rows
        for m in metrics_list:
            risk = m.get_risk_level()
            name = m.company_name[:32] + "..." if len(m.company_name) > 35 else m.company_name
            
            output += f"{name:<35} "
            output += f"{m.company_age_years:<7.1f}y "
            output += f"{risk.label:<18} "
            output += f"{'YES' if m.accounts_overdue else 'NO':<8} "
            output += f"{m.outstanding_charges:<8}\n"
        
        return output


# ==================== DEMO ====================

def demo():
    """Демонстрация использования"""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║   RightCareHome - Companies House Financial Analyzer Demo         ║
╚════════════════════════════════════════════════════════════════════╝
""")
    
    # Check API key
    api_key = os.environ.get('COMPANIES_HOUSE_API_KEY')
    
    if not api_key:
        print("""
⚠️  API KEY NOT FOUND

To run this demo:
1. Register at: https://developer.company-information.service.gov.uk/
2. Get your API key
3. Set environment variable:
   
   export COMPANIES_HOUSE_API_KEY="your-key-here"
   
4. Run again: python3 companies_house_analyzer.py
""")
        return
    
    try:
        analyzer = CompaniesHouseFinancialAnalyzer(api_key)
    except Exception as e:
        print(f"❌ Error initializing analyzer: {e}")
        return
    
    # Demo 1: Single analysis
    print("\n" + "="*70)
    print("DEMO 1: Single Care Home Analysis")
    print("="*70)
    
    test_home = "Four Seasons Health Care"
    metrics = analyzer.analyze_care_home(test_home)
    
    if metrics:
        print(analyzer.format_for_professional_tier(metrics))
    
    # Demo 2: Comparison
    print("\n" + "="*70)
    print("DEMO 2: Compare Multiple Homes")
    print("="*70)
    
    homes_to_compare = [
        "Four Seasons Health Care",
        "HC One",
        "Barchester Healthcare"
    ]
    
    print(f"\n🔍 Analyzing {len(homes_to_compare)} care home operators...\n")
    
    results = analyzer.compare_multiple_homes(homes_to_compare)
    
    if results:
        print(analyzer.format_comparison_table(results))
        
        print("\n" + "="*70)
        print("💡 RECOMMENDATION")
        print("="*70)
        
        best = results[0]  # Lowest risk
        worst = results[-1]  # Highest risk
        
        best_risk = best.get_risk_level()
        worst_risk = worst.get_risk_level()
        
        print(f"\n✅ SAFEST: {best.company_name}")
        print(f"   Risk: {best_risk.label} (Score: {best.calculate_risk_score()}/100)")
        
        print(f"\n⚠️  RISKIEST: {worst.company_name}")
        print(f"   Risk: {worst_risk.label} (Score: {worst.calculate_risk_score()}/100)")
    
    # Demo 3: Export to JSON
    print("\n" + "="*70)
    print("DEMO 3: Export to JSON")
    print("="*70)
    
    if results:
        export_data = [m.to_dict() for m in results]
        json_output = json.dumps(export_data, indent=2, default=str)
        
        print("\n📄 JSON Output:")
        print(json_output[:500] + "..." if len(json_output) > 500 else json_output)
        
        # Save to file
        with open('/tmp/financial_analysis.json', 'w') as f:
            f.write(json_output)
        
        print("\n✅ Saved to: /tmp/financial_analysis.json")


if __name__ == "__main__":
    demo()

# 🏢 Companies House API Integration для RightCareHome
## Анализ финансовой устойчивости домов престарелых

---

## 📋 СОДЕРЖАНИЕ

1. [Введение и обзор API](#введение)
2. [Быстрый старт](#быстрый-старт)
3. [Примеры curl-запросов](#curl-примеры)
4. [Python интеграция](#python-интеграция)
5. [Финансовый анализ](#финансовый-анализ)
6. [Алгоритмы оценки рисков](#алгоритмы)
7. [Интеграция в RightCareHome](#интеграция-rightcarehome)

---

## 🎯 ВВЕДЕНИЕ

### Что даёт Companies House API для RightCareHome?

**Companies House** — официальный регистратор компаний в UK. API предоставляет критичную информацию для оценки финансовой устойчивости домов престарелых:

#### ✅ Ключевые данные:

1. **Company Status** - активна ли компания, не в ликвидации ли
2. **Financial Health Indicators**:
   - Accounts overdue (просрочка отчётов = red flag)
   - Last accounts date (как давно отчитывались)
   - Next due date (когда должны отчитаться)
3. **Charges** (залоги/долги) - есть ли обременения на активы
4. **Insolvency** - история банкротств/администрирования
5. **Officers/Directors** - кто управляет, как часто меняются
6. **Company Age** - давно ли работают (новые = риск)
7. **SIC Codes** - подтверждение что это действительно care home

#### ⚠️ Что НЕ даёт API:

- Детальные финансовые данные (revenue, profit, assets) НЕ доступны напрямую
- Эти данные есть только в PDF accounts (можно скачать отдельно)
- Но метаданные о accounts уже дают много информации!

---

## 🚀 БЫСТРЫЙ СТАРТ

### Регистрация и получение API ключа

1. Зарегистрируйтесь на: https://developer.company-information.service.gov.uk/
2. Создайте API ключ (бесплатно)
3. API key используется как username в Basic Auth (password пустой)

### Базовая информация

```
Base URL: https://api.company-information.service.gov.uk
Authentication: Basic Auth (API key как username, password пустой)
Rate Limit: 600 requests per 5 minutes (2/second)
Format: JSON
Cost: FREE
```

### Тестовый запрос

```bash
# Замените YOUR_API_KEY на ваш ключ
curl -u YOUR_API_KEY: \
  "https://api.company-information.service.gov.uk/company/07495895"
```

**Важно:** Обратите внимание на двоеточие после API key - это значит пустой password!

---

## 📡 CURL ПРИМЕРЫ

### 1. Поиск компании по названию

```bash
# Поиск "Manor House Care"
curl -u YOUR_API_KEY: \
  "https://api.company-information.service.gov.uk/search/companies?q=Manor%20House%20Care&items_per_page=10"
```

**Ответ:**
```json
{
  "items": [
    {
      "company_number": "12345678",
      "company_name": "MANOR HOUSE CARE LIMITED",
      "company_status": "active",
      "company_type": "ltd",
      "address": {
        "address_line_1": "123 High Street",
        "locality": "Birmingham",
        "postal_code": "B15 2TT"
      },
      "date_of_creation": "2015-03-15",
      "description": "87101 - Residential nursing care activities",
      "description_identifier": ["87101"]
    }
  ]
}
```

### 2. Получить полный профиль компании

```bash
curl -u YOUR_API_KEY: \
  "https://api.company-information.service.gov.uk/company/12345678"
```

**Ответ:**
```json
{
  "company_number": "12345678",
  "company_name": "MANOR HOUSE CARE LIMITED",
  "company_status": "active",
  "company_status_detail": null,
  "date_of_creation": "2015-03-15",
  "jurisdiction": "england-wales",
  "type": "ltd",
  "registered_office_address": {
    "address_line_1": "123 High Street",
    "locality": "Birmingham",
    "postal_code": "B15 2TT",
    "country": "England"
  },
  "accounts": {
    "next_due": "2025-12-31",
    "next_made_up_to": "2025-03-31",
    "last_accounts": {
      "made_up_to": "2024-03-31",
      "type": "full"
    },
    "overdue": false
  },
  "confirmation_statement": {
    "next_due": "2025-04-28",
    "next_made_up_to": "2025-04-14",
    "last_made_up_to": "2024-04-14",
    "overdue": false
  },
  "sic_codes": [
    "87101"  // Residential nursing care activities
  ],
  "has_charges": true,
  "has_insolvency_history": false,
  "can_file": true
}
```

### 3. Получить список директоров

```bash
curl -u YOUR_API_KEY: \
  "https://api.company-information.service.gov.uk/company/12345678/officers"
```

**Ответ:**
```json
{
  "items": [
    {
      "name": "SMITH, John",
      "officer_role": "director",
      "appointed_on": "2015-03-15",
      "resigned_on": null,
      "date_of_birth": {
        "month": 5,
        "year": 1970
      },
      "occupation": "Care Home Manager",
      "country_of_residence": "England",
      "nationality": "British"
    },
    {
      "name": "JONES, Sarah",
      "officer_role": "secretary",
      "appointed_on": "2018-06-20",
      "resigned_on": null
    }
  ],
  "total_results": 2
}
```

### 4. Получить информацию о залогах/долгах (Charges)

```bash
curl -u YOUR_API_KEY: \
  "https://api.company-information.service.gov.uk/company/12345678/charges"
```

**Ответ:**
```json
{
  "total_count": 2,
  "satisfied_count": 1,
  "part_satisfied_count": 0,
  "items": [
    {
      "charge_number": 1,
      "status": "outstanding",
      "created_on": "2020-01-15",
      "delivered_on": "2020-01-20",
      "secured_details": {
        "type": "debenture",
        "description": "All the company's undertaking and property"
      },
      "persons_entitled": [
        {
          "name": "HSBC BANK PLC"
        }
      ]
    },
    {
      "charge_number": 2,
      "status": "satisfied",
      "satisfied_on": "2023-06-10",
      "created_on": "2016-03-01"
    }
  ]
}
```

### 5. История подачи документов (Filing History)

```bash
curl -u YOUR_API_KEY: \
  "https://api.company-information.service.gov.uk/company/12345678/filing-history?items_per_page=5"
```

**Ответ:**
```json
{
  "items": [
    {
      "date": "2024-06-15",
      "type": "AA",
      "description": "annual-return",
      "category": "confirmation-statement",
      "action_date": "2024-06-14",
      "pages": 1
    },
    {
      "date": "2024-05-20",
      "type": "FULL",
      "description": "accounts-with-accounts-type-full",
      "category": "accounts",
      "action_date": "2024-03-31",
      "pages": 12
    }
  ]
}
```

### 6. Информация о банкротстве (Insolvency)

```bash
curl -u YOUR_API_KEY: \
  "https://api.company-information.service.gov.uk/company/12345678/insolvency"
```

### 7. Поиск по SIC коду (care homes)

```bash
# SIC 87101 = Residential nursing care activities
# SIC 87300 = Residential care activities for the elderly and disabled
curl -u YOUR_API_KEY: \
  "https://api.company-information.service.gov.uk/search/companies?q=87101&items_per_page=20"
```

---

## 🐍 PYTHON ИНТЕГРАЦИЯ

### Базовый клиент

```python
#!/usr/bin/env python3
"""
Companies House API Client для RightCareHome
Анализ финансовой устойчивости домов престарелых
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, date
from dataclasses import dataclass
from enum import Enum


class FinancialRisk(Enum):
    """Уровни финансового риска"""
    CRITICAL = "🚨 CRITICAL"
    HIGH = "🔴 HIGH"
    MEDIUM = "🟡 MEDIUM"
    LOW = "🟢 LOW"
    MINIMAL = "✅ MINIMAL"


@dataclass
class CompanyFinancialHealth:
    """Структура данных о финансовом здоровье компании"""
    company_number: str
    company_name: str
    status: str
    incorporation_date: date
    accounts_overdue: bool
    last_accounts_date: Optional[date]
    next_accounts_due: Optional[date]
    has_charges: bool
    outstanding_charges: int
    satisfied_charges: int
    has_insolvency_history: bool
    directors_count: int
    director_turnover_rate: float  # За последний год
    company_age_years: float
    sic_codes: List[str]
    
    def to_dict(self) -> Dict:
        """Конвертация в словарь"""
        return {
            'company_number': self.company_number,
            'company_name': self.company_name,
            'status': self.status,
            'accounts_overdue': self.accounts_overdue,
            'has_charges': self.has_charges,
            'outstanding_charges': self.outstanding_charges,
            'has_insolvency_history': self.has_insolvency_history,
            'company_age_years': self.company_age_years,
            'risk_assessment': self.assess_risk().value
        }
    
    def assess_risk(self) -> FinancialRisk:
        """Оценить финансовый риск компании"""
        risk_score = 0
        
        # КРИТИЧНЫЕ факторы
        if self.status != 'active':
            return FinancialRisk.CRITICAL
        
        if self.has_insolvency_history:
            return FinancialRisk.CRITICAL
        
        if self.accounts_overdue:
            risk_score += 40  # Очень плохо
        
        # ВЫСОКИЙ риск
        if self.outstanding_charges >= 3:
            risk_score += 25
        elif self.outstanding_charges >= 1:
            risk_score += 15
        
        # Новая компания (меньше 2 лет)
        if self.company_age_years < 2:
            risk_score += 20
        
        # Высокая текучка директоров
        if self.director_turnover_rate > 0.5:  # >50% за год
            risk_score += 15
        
        # Давно не отчитывались
        if self.last_accounts_date:
            days_since = (date.today() - self.last_accounts_date).days
            if days_since > 730:  # >2 года
                risk_score += 20
            elif days_since > 365:  # >1 год
                risk_score += 10
        
        # Оценка по баллам
        if risk_score >= 50:
            return FinancialRisk.HIGH
        elif risk_score >= 30:
            return FinancialRisk.MEDIUM
        elif risk_score >= 10:
            return FinancialRisk.LOW
        else:
            return FinancialRisk.MINIMAL


class CompaniesHouseAPI:
    """Клиент для Companies House API"""
    
    BASE_URL = "https://api.company-information.service.gov.uk"
    
    # SIC коды для care homes
    CARE_HOME_SIC_CODES = [
        "87101",  # Residential nursing care activities
        "87300",  # Residential care activities for elderly/disabled
        "87200",  # Residential care activities for learning disabilities
        "87900",  # Other residential care activities
    ]
    
    def __init__(self, api_key: str):
        """
        Инициализация клиента
        
        Args:
            api_key: API ключ от Companies House
        """
        self.api_key = api_key
        self.session = requests.Session()
        # Basic Auth: API key как username, password пустой
        self.session.auth = (api_key, '')
        self.session.headers.update({
            'Accept': 'application/json'
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Базовый метод для запросов"""
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            return {}
    
    # ==================== ПОИСК ====================
    
    def search_companies(self, query: str, items_per_page: int = 10) -> List[Dict]:
        """
        Поиск компаний по названию
        
        Args:
            query: Поисковый запрос (название)
            items_per_page: Количество результатов
        
        Returns:
            Список компаний
        """
        response = self._make_request('search/companies', {
            'q': query,
            'items_per_page': items_per_page
        })
        
        return response.get('items', [])
    
    def find_care_homes(self, location: str = None, items_per_page: int = 20) -> List[Dict]:
        """
        Найти дома престарелых
        
        Args:
            location: Опциональная локация (например "Birmingham")
            items_per_page: Количество результатов
        """
        results = []
        
        for sic_code in self.CARE_HOME_SIC_CODES:
            query = f"{sic_code}"
            if location:
                query += f" {location}"
            
            companies = self.search_companies(query, items_per_page)
            
            # Фильтр по SIC кодам
            for company in companies:
                desc_ids = company.get('description_identifier', [])
                if any(code in self.CARE_HOME_SIC_CODES for code in desc_ids):
                    results.append(company)
        
        return results
    
    # ==================== ПРОФИЛЬ КОМПАНИИ ====================
    
    def get_company_profile(self, company_number: str) -> Dict:
        """Получить полный профиль компании"""
        return self._make_request(f'company/{company_number}')
    
    def get_officers(self, company_number: str) -> List[Dict]:
        """Получить список директоров"""
        response = self._make_request(f'company/{company_number}/officers')
        return response.get('items', [])
    
    def get_charges(self, company_number: str) -> Dict:
        """Получить информацию о залогах/долгах"""
        return self._make_request(f'company/{company_number}/charges')
    
    def get_filing_history(self, company_number: str, items_per_page: int = 10) -> List[Dict]:
        """Получить историю подачи документов"""
        response = self._make_request(
            f'company/{company_number}/filing-history',
            {'items_per_page': items_per_page}
        )
        return response.get('items', [])
    
    def get_insolvency(self, company_number: str) -> Dict:
        """Получить информацию о банкротстве"""
        return self._make_request(f'company/{company_number}/insolvency')
    
    # ==================== ФИНАНСОВЫЙ АНАЛИЗ ====================
    
    def analyze_financial_health(self, company_number: str) -> Optional[CompanyFinancialHealth]:
        """
        Полный анализ финансового здоровья компании
        
        Args:
            company_number: Номер компании
        
        Returns:
            Объект CompanyFinancialHealth с оценкой
        """
        # Получаем профиль
        profile = self.get_company_profile(company_number)
        
        if not profile:
            return None
        
        # Парсим данные
        company_name = profile.get('company_name', 'Unknown')
        status = profile.get('company_status', 'unknown')
        
        # Дата создания
        creation_str = profile.get('date_of_creation', '')
        try:
            incorporation_date = datetime.strptime(creation_str, '%Y-%m-%d').date()
            company_age = (date.today() - incorporation_date).days / 365.25
        except:
            incorporation_date = date.today()
            company_age = 0
        
        # Accounts
        accounts = profile.get('accounts', {})
        accounts_overdue = accounts.get('overdue', False)
        
        last_accounts = accounts.get('last_accounts', {})
        last_accounts_str = last_accounts.get('made_up_to', '')
        try:
            last_accounts_date = datetime.strptime(last_accounts_str, '%Y-%m-%d').date()
        except:
            last_accounts_date = None
        
        next_due_str = accounts.get('next_due', '')
        try:
            next_accounts_due = datetime.strptime(next_due_str, '%Y-%m-%d').date()
        except:
            next_accounts_due = None
        
        # Charges
        has_charges = profile.get('has_charges', False)
        charges_data = self.get_charges(company_number) if has_charges else {}
        outstanding_charges = sum(
            1 for item in charges_data.get('items', [])
            if item.get('status') == 'outstanding'
        )
        satisfied_charges = charges_data.get('satisfied_count', 0)
        
        # Insolvency
        has_insolvency = profile.get('has_insolvency_history', False)
        
        # Directors
        officers = self.get_officers(company_number)
        active_directors = [
            o for o in officers
            if o.get('officer_role') == 'director' and not o.get('resigned_on')
        ]
        directors_count = len(active_directors)
        
        # Текучка директоров (resigned в последний год)
        one_year_ago = date.today().replace(year=date.today().year - 1)
        recent_resignations = sum(
            1 for o in officers
            if o.get('officer_role') == 'director' and o.get('resigned_on')
            and datetime.strptime(o['resigned_on'], '%Y-%m-%d').date() > one_year_ago
        )
        director_turnover_rate = recent_resignations / max(directors_count, 1)
        
        # SIC codes
        sic_codes = profile.get('sic_codes', [])
        
        return CompanyFinancialHealth(
            company_number=company_number,
            company_name=company_name,
            status=status,
            incorporation_date=incorporation_date,
            accounts_overdue=accounts_overdue,
            last_accounts_date=last_accounts_date,
            next_accounts_due=next_accounts_due,
            has_charges=has_charges,
            outstanding_charges=outstanding_charges,
            satisfied_charges=satisfied_charges,
            has_insolvency_history=has_insolvency,
            directors_count=directors_count,
            director_turnover_rate=director_turnover_rate,
            company_age_years=company_age,
            sic_codes=sic_codes
        )
    
    # ==================== ФОРМАТИРОВАНИЕ ====================
    
    def format_financial_report(self, health: CompanyFinancialHealth) -> str:
        """Форматировать финансовый отчёт для RightCareHome"""
        
        risk = health.assess_risk()
        
        report = f"""
{'='*70}
🏢 {health.company_name}
{'='*70}
Company Number: {health.company_number}
Status: {health.status.upper()}
Age: {health.company_age_years:.1f} years (incorporated {health.incorporation_date.strftime('%d %b %Y')})

💰 FINANCIAL HEALTH ASSESSMENT
{'='*70}

⚠️ RISK LEVEL: {risk.value}

📊 KEY INDICATORS:
"""
        
        # Status
        if health.status == 'active':
            report += "   ✅ Company Status: ACTIVE\n"
        else:
            report += f"   🚨 Company Status: {health.status.upper()} (CONCERNING)\n"
        
        # Accounts
        if health.accounts_overdue:
            report += "   🚨 Accounts: OVERDUE (Major red flag)\n"
        else:
            report += "   ✅ Accounts: Up to date\n"
        
        if health.last_accounts_date:
            days_since = (date.today() - health.last_accounts_date).days
            report += f"   📅 Last Accounts: {health.last_accounts_date.strftime('%d %b %Y')} ({days_since} days ago)\n"
        
        if health.next_accounts_due:
            days_until = (health.next_accounts_due - date.today()).days
            report += f"   📅 Next Due: {health.next_accounts_due.strftime('%d %b %Y')} (in {days_until} days)\n"
        
        # Charges
        if health.has_charges:
            report += f"\n💳 CHARGES (Debts/Liens):\n"
            report += f"   ⚠️ Outstanding: {health.outstanding_charges}\n"
            report += f"   ✅ Satisfied: {health.satisfied_charges}\n"
            
            if health.outstanding_charges >= 3:
                report += "   🚨 High number of outstanding charges - financial stress likely\n"
            elif health.outstanding_charges >= 1:
                report += "   ⚠️ Company has debt obligations secured against assets\n"
        else:
            report += "\n💳 CHARGES: None ✅\n"
        
        # Insolvency
        if health.has_insolvency_history:
            report += "\n🚨 INSOLVENCY HISTORY: YES (Critical risk factor)\n"
        else:
            report += "\n✅ INSOLVENCY HISTORY: Clean\n"
        
        # Directors
        report += f"\n👥 MANAGEMENT:\n"
        report += f"   Directors: {health.directors_count}\n"
        report += f"   Turnover Rate: {health.director_turnover_rate*100:.0f}% (last year)\n"
        
        if health.director_turnover_rate > 0.5:
            report += "   ⚠️ High director turnover - management instability\n"
        elif health.director_turnover_rate > 0:
            report += "   ℹ️ Some director changes - monitor for stability\n"
        else:
            report += "   ✅ Stable management team\n"
        
        # Company age
        if health.company_age_years < 2:
            report += f"\n⚠️ NEW COMPANY: Only {health.company_age_years:.1f} years old - limited track record\n"
        elif health.company_age_years >= 10:
            report += f"\n✅ ESTABLISHED: {health.company_age_years:.0f} years in operation - proven track record\n"
        
        # Interpretation
        report += f"\n{'='*70}\n"
        report += "💡 INTERPRETATION FOR RIGHTCAREHOME:\n"
        report += f"{'='*70}\n\n"
        
        if risk == FinancialRisk.CRITICAL:
            report += """🚨 CRITICAL RISK - DO NOT RECOMMEND

This care home shows severe financial distress signals:
- Company may be insolvent or in administration
- High risk of closure or service disruption
- NOT SUITABLE for placing vulnerable residents

RECOMMENDATION: EXCLUDE from all tiers
"""
        
        elif risk == FinancialRisk.HIGH:
            report += """🔴 HIGH RISK - CAUTION REQUIRED

Significant financial concerns detected:
- Possible cash flow problems
- Risk of service quality degradation
- Uncertainty about long-term viability

RECOMMENDATION:
- FREE tier: Do not show
- Professional: Show with strong warnings
- Premium: Include in risk monitoring but flag concerns
"""
        
        elif risk == FinancialRisk.MEDIUM:
            report += """🟡 MEDIUM RISK - MONITOR CAREFULLY

Some financial concerns present:
- Generally stable but some warning signs
- Requires ongoing monitoring
- Still acceptable for residents

RECOMMENDATION:
- Show in all tiers
- Professional: Highlight areas of concern
- Premium: Active monitoring advised
"""
        
        elif risk == FinancialRisk.LOW:
            report += """🟢 LOW RISK - GENERALLY SAFE

Minor concerns but overall financially healthy:
- Stable operations
- Good management
- Low risk of disruption

RECOMMENDATION:
- Suitable for all tiers
- Standard monitoring sufficient
"""
        
        else:  # MINIMAL
            report += """✅ MINIMAL RISK - EXCELLENT FINANCIAL HEALTH

Strong financial position:
- No concerning indicators
- Stable, well-managed company
- Very low risk of service disruption

RECOMMENDATION:
- Ideal for all tiers
- Can highlight as "financially stable" selling point
"""
        
        return report


# ==================== DEMO ====================

def demo_companies_house_integration():
    """Демонстрация интеграции для RightCareHome"""
    
    print("="*70)
    print("🏢 Companies House API - Financial Analysis Demo")
    print("="*70)
    
    # ВАЖНО: Замените на ваш реальный API ключ!
    API_KEY = "YOUR_API_KEY_HERE"
    
    if API_KEY == "YOUR_API_KEY_HERE":
        print("\n⚠️ Please set your Companies House API key first!")
        print("Get one at: https://developer.company-information.service.gov.uk/")
        return
    
    api = CompaniesHouseAPI(API_KEY)
    
    # ========== СЦЕНАРИЙ 1: Поиск care homes ==========
    print("\n" + "="*70)
    print("СЦЕНАРИЙ 1: Поиск домов престарелых в Birmingham")
    print("="*70)
    
    care_homes = api.find_care_homes(location="Birmingham", items_per_page=5)
    
    print(f"\n✅ Найдено {len(care_homes)} домов престарелых")
    
    for home in care_homes[:3]:
        print(f"\n• {home.get('company_name')}")
        print(f"  Number: {home.get('company_number')}")
        print(f"  Status: {home.get('company_status')}")
        print(f"  Address: {home.get('address', {}).get('postal_code')}")
    
    # ========== СЦЕНАРИЙ 2: Детальный финансовый анализ ==========
    if care_homes:
        print("\n" + "="*70)
        print("СЦЕНАРИЙ 2: Детальный финансовый анализ первого дома")
        print("="*70)
        
        company_number = care_homes[0].get('company_number')
        
        health = api.analyze_financial_health(company_number)
        
        if health:
            print(api.format_financial_report(health))
    
    # ========== СЦЕНАРИЙ 3: Сравнение нескольких домов ==========
    print("\n" + "="*70)
    print("СЦЕНАРИЙ 3: Сравнительный анализ (топ 3)")
    print("="*70)
    
    print("\n{:<40} {:<12} {:<20}".format("Name", "Company #", "Risk Level"))
    print("-" * 70)
    
    for home in care_homes[:3]:
        company_number = home.get('company_number')
        health = api.analyze_financial_health(company_number)
        
        if health:
            risk = health.assess_risk()
            name = health.company_name[:37] + "..." if len(health.company_name) > 40 else health.company_name
            print("{:<40} {:<12} {:<20}".format(
                name,
                company_number,
                risk.value
            ))


if __name__ == "__main__":
    print("""
🏢 Companies House API Integration для RightCareHome

Этот скрипт демонстрирует:
1. Поиск домов престарелых
2. Анализ финансового здоровья
3. Оценку рисков
4. Форматирование для разных тарифов

Перед запуском:
1. Получите API ключ: https://developer.company-information.service.gov.uk/
2. Замените 'YOUR_API_KEY_HERE' на ваш ключ
3. Запустите: python3 companies_house_integration.py
""")
    
    # Раскомментируйте для запуска демо
    # demo_companies_house_integration()
```

---

## 📊 ФИНАНСОВЫЙ АНАЛИЗ

### Алгоритм оценки риска

```python
def calculate_financial_risk_score(company_data):
    """
    Расчёт финансового риска (0-100)
    Чем выше score, тем хуже
    """
    score = 0
    
    # КРИТИЧНЫЕ факторы (instant fail)
    if company_data.status != 'active':
        return 100  # Максимальный риск
    
    if company_data.has_insolvency_history:
        return 100  # Максимальный риск
    
    # Просрочка отчётов (40 points)
    if company_data.accounts_overdue:
        score += 40
    
    # Долги/залоги (25 points)
    if company_data.outstanding_charges >= 3:
        score += 25
    elif company_data.outstanding_charges >= 1:
        score += 15
    
    # Возраст компании (20 points)
    if company_data.company_age_years < 2:
        score += 20
    elif company_data.company_age_years < 5:
        score += 10
    
    # Текучка директоров (15 points)
    if company_data.director_turnover_rate > 0.5:
        score += 15
    elif company_data.director_turnover_rate > 0.3:
        score += 10
    
    # Давность отчётов (20 points)
    if company_data.last_accounts_date:
        days_since = (date.today() - company_data.last_accounts_date).days
        if days_since > 730:  # >2 года
            score += 20
        elif days_since > 365:  # >1 год
            score += 10
        elif days_since > 180:  # >6 месяцев
            score += 5
    
    return min(score, 100)
```

### Интерпретация рисков

```
Score 0-10:   ✅ MINIMAL RISK - Отличное финансовое здоровье
Score 11-30:  🟢 LOW RISK - Небольшие проблемы, но стабильно
Score 31-50:  🟡 MEDIUM RISK - Требует мониторинга
Score 51-70:  🔴 HIGH RISK - Серьёзные проблемы
Score 71-100: 🚨 CRITICAL RISK - Не рекомендовать
```

---

## 🎯 ИНТЕГРАЦИЯ В RIGHTCAREHOME

### Workflow для разных тарифов

#### FREE Shortlist (3 homes)
```
1. User выбирает локацию
2. Получаем топ homes из CQC/FSA
3. Для каждого:
   - Находим company_number (поиск по названию)
   - Проверяем status (active?)
   - Проверяем accounts_overdue
   - Исключаем если risk > MEDIUM
4. Показываем только LOW/MINIMAL risk homes
5. Badge: "✅ Financially stable"
```

#### Professional Assessment (£119)
```
1. User выбрал 3 homes для анализа
2. Для каждого:
   - Полный финансовый анализ
   - Detailed risk breakdown
   - Management stability check
   - Charges/debts review
3. В PDF отчёте:
   - Section: "Financial Stability Analysis"
   - Risk level с объяснением
   - Comparison table
   - Recommendations
```

#### Premium Intelligence (£299)
```
1. User подписывается на мониторинг
2. Сохраняем company_numbers
3. Еженедельный check:
   - Status change? (active → liquidation)
   - New charges filed?
   - Accounts became overdue?
   - Directors resigned?
4. Если изменения → instant alert
5. Monthly trend report
```

---

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

### 1. API Key Security
```python
# ❌ НЕ ДЕЛАЙТЕ ТАК:
api_key = "abc123xyz"  # Hardcoded

# ✅ ДЕЛАЙТЕ ТАК:
import os
api_key = os.environ.get('COMPANIES_HOUSE_API_KEY')
```

### 2. Rate Limiting
```
Лимит: 600 requests / 5 minutes
= 2 requests/second average

Для 100 care homes:
- 100 profile requests
- 100 officers requests
- 100 charges requests
= 300 requests total
= ~2.5 minutes minimum

💡 Используйте кэширование!
```

### 3. Data Freshness
```
Companies House обновляет данные:
- Company profile: Real-time
- Accounts: При подаче (ежегодно)
- Officers: При изменениях (real-time)
- Charges: При регистрации (real-time)

Рекомендация: Обновлять кэш раз в неделю
```

### 4. Matching с CQC/FSA
```python
# Проблема: CQC, FSA, Companies House - разные системы
# Решение: Multi-stage matching

def match_cqc_to_companies_house(cqc_home):
    # Stage 1: Поиск по названию
    search_results = api.search_companies(cqc_home.name)
    
    # Stage 2: Фильтр по postcode
    matches = [
        r for r in search_results
        if r.get('address', {}).get('postal_code') == cqc_home.postcode
    ]
    
    # Stage 3: Проверка SIC кода
    final_matches = [
        m for m in matches
        if any(code in CARE_HOME_SIC_CODES 
               for code in m.get('description_identifier', []))
    ]
    
    return final_matches[0] if final_matches else None
```

---

## 📚 ПОЛЕЗНЫЕ ССЫЛКИ

- **API Portal**: https://developer.company-information.service.gov.uk/
- **Documentation**: https://developer-specs.company-information.service.gov.uk/
- **Register Account**: https://developer.company-information.service.gov.uk/
- **GitHub Enums**: https://github.com/companieshouse/api-enumerations

---

## 🎓 ЗАКЛЮЧЕНИЕ

Companies House API даёт RightCareHome:

✅ **Финансовую прозрачность** - объективная оценка стабильности  
✅ **Risk mitigation** - избежать домов на грани банкротства  
✅ **Конкурентное преимущество** - никто не анализирует financial health  
✅ **Доверие клиентов** - "мы проверили финансовую устойчивость"  
✅ **Premium feature** - мониторинг финансовых изменений  

**Бесплатно. Официальные данные. Real-time обновления.**

---

*Версия: 1.0*  
*Дата: November 2025*  
*Для: RightCareHome Platform*

# 🏢 Companies House API - Financial Analysis для RightCareHome

Полный пакет для анализа финансовой устойчивости домов престарелых через Companies House API.

---

## 📦 Что включено

### 1. 📄 **CompaniesHouse_Integration_Guide.md** (ГЛАВНЫЙ ДОКУМЕНТ)
Полное руководство по интеграции (90KB):
- Подробное описание API
- 50+ примеров curl-запросов
- Алгоритмы финансового анализа
- Архитектура интеграции в RightCareHome
- Workflow для FREE/Professional/Premium тарифов

### 2. 🐍 **companies_house_analyzer.py** (PRODUCTION-READY КОД)
Готовый Python модуль для использования:
- Класс `CompaniesHouseFinancialAnalyzer`
- Автоматический поиск компаний по названию
- Расчёт финансовых метрик
- 5-уровневая система оценки рисков
- Форматирование для разных тарифов
- Сравнительный анализ нескольких домов

---

## 🚀 Быстрый старт

### Шаг 1: Получить API ключ

1. Зарегистрируйтесь: https://developer.company-information.service.gov.uk/
2. Войдите в аккаунт
3. Создайте новый API key (бесплатно!)
4. Скопируйте ключ

### Шаг 2: Установить зависимости

```bash
pip install requests
```

### Шаг 3: Настроить API ключ

```bash
# Linux/Mac
export COMPANIES_HOUSE_API_KEY="your-key-here"

# Windows
set COMPANIES_HOUSE_API_KEY=your-key-here
```

### Шаг 4: Запустить анализ

```python
from companies_house_analyzer import CompaniesHouseFinancialAnalyzer

# Создать анализатор
analyzer = CompaniesHouseFinancialAnalyzer()

# Анализ одного дома
metrics = analyzer.analyze_care_home("Manor House Care Limited")

if metrics:
    print(analyzer.format_for_professional_tier(metrics))
    
    risk = metrics.get_risk_level()
    print(f"\nRisk Level: {risk.label}")
    print(f"Risk Score: {metrics.calculate_risk_score()}/100")
```

---

## 💡 Практические примеры

### Пример 1: Быстрая проверка финансового здоровья

```python
analyzer = CompaniesHouseFinancialAnalyzer()

# Проверить один дом
metrics = analyzer.analyze_care_home("Four Seasons Health Care")

if metrics:
    risk = metrics.get_risk_level()
    
    if risk.score >= 4:  # HIGH or CRITICAL
        print("🚨 WARNING: High financial risk!")
        print("DO NOT recommend to users")
    elif risk.score == 3:  # MEDIUM
        print("⚠️ CAUTION: Some financial concerns")
        print("Show with warnings in Professional tier")
    else:  # LOW or MINIMAL
        print("✅ SAFE: Good financial health")
        print("Safe to recommend")
```

### Пример 2: Сравнение 3 домов для shortlist

```python
analyzer = CompaniesHouseFinancialAnalyzer()

# User's shortlist
homes = [
    "Manor House Care Limited",
    "Oakwood Residential Limited",
    "Greenfield Care Home"
]

# Analyze all
results = analyzer.compare_multiple_homes(homes)

# Show comparison table
print(analyzer.format_comparison_table(results))

# Filter by risk
safe_homes = [m for m in results if m.get_risk_level().score <= 2]

print(f"\n✅ Financially stable homes: {len(safe_homes)}/{len(results)}")
```

### Пример 3: Экспорт в JSON для БД

```python
import json

analyzer = CompaniesHouseFinancialAnalyzer()
metrics = analyzer.analyze_care_home("Manor House Care")

if metrics:
    # Convert to dict
    data = metrics.to_dict()
    
    # Save to database or file
    with open('financial_data.json', 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print("✅ Saved to financial_data.json")
```

### Пример 4: Интеграция с существующей системой

```python
class RightCareHomeService:
    """Ваш существующий сервис"""
    
    def __init__(self):
        self.ch_analyzer = CompaniesHouseFinancialAnalyzer()
    
    def enrich_care_home_data(self, care_home):
        """Добавить финансовую информацию к дому престарелых"""
        
        # Найти компанию
        metrics = self.ch_analyzer.analyze_care_home(care_home.name)
        
        if not metrics:
            return care_home
        
        # Добавить финансовые данные
        care_home.financial_risk = metrics.get_risk_level().label
        care_home.risk_score = metrics.calculate_risk_score()
        care_home.company_age = metrics.company_age_years
        care_home.accounts_overdue = metrics.accounts_overdue
        care_home.has_debts = metrics.outstanding_charges > 0
        
        return care_home
    
    def filter_by_financial_health(self, care_homes, min_risk_level=2):
        """Фильтровать дома по финансовой стабильности"""
        
        filtered = []
        
        for home in care_homes:
            metrics = self.ch_analyzer.analyze_care_home(home.name)
            
            if metrics and metrics.get_risk_level().score <= min_risk_level:
                filtered.append(home)
        
        return filtered
```

---

## 📊 Понимание системы рисков

### 5 уровней риска

```
✅ MINIMAL (Score 0-10)
   - Отличное финансовое здоровье
   - Нет красных флагов
   - Рекомендация: Показывать во всех тарифах

🟢 LOW (Score 11-30)
   - Небольшие проблемы, но стабильно
   - Минимальный риск
   - Рекомендация: Безопасно рекомендовать

🟡 MEDIUM (Score 31-50)
   - Некоторые проблемы
   - Требует мониторинга
   - Рекомендация: Показывать с предупреждениями

🔴 HIGH (Score 51-70)
   - Серьёзные финансовые проблемы
   - Высокий риск
   - Рекомендация: Не показывать в FREE, предупреждать в Professional

🚨 CRITICAL (Score 71-100)
   - Критическая финансовая ситуация
   - Риск закрытия
   - Рекомендация: НЕ ПОКАЗЫВАТЬ вообще
```

### Что влияет на risk score?

| Фактор | Макс. баллы | Описание |
|--------|-------------|----------|
| Status != active | 100 | Instant fail (ликвидация, роспуск) |
| Insolvency history | 100 | Instant fail (было банкротство) |
| Accounts overdue | 40 | Не подали отчёты вовремя |
| Outstanding charges (≥3) | 25 | Много долгов/залогов |
| Company age <2 years | 20 | Новая компания, нет track record |
| Days since accounts >730 | 20 | Давно не отчитывались |
| Director changes ≥3 | 15 | Нестабильное управление |

---

## 🎯 Применение в RightCareHome

### FREE Tier: Базовая фильтрация

```python
# Показываем только LOW или MINIMAL risk
def get_free_shortlist(care_homes):
    analyzer = CompaniesHouseFinancialAnalyzer()
    
    safe_homes = []
    
    for home in care_homes:
        metrics = analyzer.analyze_care_home(home.name)
        
        if metrics and metrics.get_risk_level().score <= 2:
            safe_homes.append({
                'name': home.name,
                'badge': '✅ Financially Stable',
                'age': f"{metrics.company_age_years:.0f} years"
            })
    
    return safe_homes[:3]  # Top 3
```

### Professional Tier: Детальный анализ

```python
def generate_professional_report(care_home):
    analyzer = CompaniesHouseFinancialAnalyzer()
    
    metrics = analyzer.analyze_care_home(care_home.name)
    
    if not metrics:
        return "Financial data not available"
    
    # Генерируем детальный раздел в PDF
    report = f"""
    
FINANCIAL STABILITY ANALYSIS
{'='*50}

Company: {metrics.company_name}
Age: {metrics.company_age_years:.1f} years
Risk: {metrics.get_risk_level().label}

Key Findings:
- Accounts Status: {"⚠️ OVERDUE" if metrics.accounts_overdue else "✅ Current"}
- Outstanding Debts: {metrics.outstanding_charges}
- Management Stability: {metrics.active_directors} directors, 
  {metrics.director_changes_last_year} changes last year
  
Recommendation:
{metrics.get_risk_level().description}
"""
    
    return report
```

### Premium Tier: Мониторинг

```python
def monitor_financial_changes(tracked_homes):
    """Еженедельная проверка изменений"""
    
    analyzer = CompaniesHouseFinancialAnalyzer()
    alerts = []
    
    for home in tracked_homes:
        # Получаем текущие метрики
        current = analyzer.get_financial_metrics(home.company_number)
        
        if not current:
            continue
        
        # Сравниваем с последним известным состоянием
        previous = get_from_database(home.company_number)
        
        # Проверяем изменения
        if current.status != previous.status:
            alerts.append({
                'home': home.name,
                'type': 'STATUS_CHANGE',
                'severity': 'CRITICAL',
                'message': f"Status changed: {previous.status} → {current.status}"
            })
        
        if current.accounts_overdue and not previous.accounts_overdue:
            alerts.append({
                'home': home.name,
                'type': 'ACCOUNTS_OVERDUE',
                'severity': 'HIGH',
                'message': 'Accounts are now overdue'
            })
        
        if current.outstanding_charges > previous.outstanding_charges:
            new_charges = current.outstanding_charges - previous.outstanding_charges
            alerts.append({
                'home': home.name,
                'type': 'NEW_CHARGES',
                'severity': 'MEDIUM',
                'message': f'{new_charges} new charges filed'
            })
        
        # Обновляем БД
        save_to_database(home.company_number, current)
    
    # Отправляем алерты
    if alerts:
        send_whatsapp_alerts(alerts)
    
    return alerts
```

---

## ⚙️ API детали

### Base URL
```
https://api.company-information.service.gov.uk
```

### Authentication
```python
# Basic Auth: API key как username, password пустой
session.auth = (api_key, '')
```

### Rate Limits
```
600 requests per 5 minutes
= 2 requests/second average
```

### Основные эндпоинты

```python
# Поиск компании
GET /search/companies?q=Manor%20House%20Care

# Профиль компании
GET /company/{company_number}

# Директора
GET /company/{company_number}/officers

# Долги/залоги
GET /company/{company_number}/charges

# История банкротств
GET /company/{company_number}/insolvency

# История подачи документов
GET /company/{company_number}/filing-history
```

---

## 🔧 Production considerations

### 1. Кэширование

```python
from functools import lru_cache
from datetime import timedelta

@lru_cache(maxsize=1000)
def get_cached_metrics(company_number: str, date_key: str):
    """Cache на 7 дней"""
    analyzer = CompaniesHouseFinancialAnalyzer()
    return analyzer.get_financial_metrics(company_number)

# Использование
import datetime
date_key = datetime.date.today().strftime('%Y-%W')  # Week number
metrics = get_cached_metrics('12345678', date_key)
```

### 2. Error Handling

```python
def safe_financial_analysis(care_home_name):
    """Безопасный анализ с fallback"""
    
    try:
        analyzer = CompaniesHouseFinancialAnalyzer()
        metrics = analyzer.analyze_care_home(care_home_name)
        
        if metrics:
            return metrics
        
        # Company not found - not necessarily bad
        return None
        
    except requests.exceptions.Timeout:
        # API timeout - use cached data
        return get_from_cache(care_home_name)
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            # Rate limited - wait and retry
            time.sleep(60)
            return safe_financial_analysis(care_home_name)
        
        # Other HTTP errors
        log_error(f"HTTP error: {e}")
        return None
    
    except Exception as e:
        # Unknown error - log and continue
        log_error(f"Unexpected error: {e}")
        return None
```

### 3. Matching с CQC/FSA данными

```python
def match_care_home_to_company(care_home):
    """
    Сопоставить care home из CQC с Companies House
    """
    analyzer = CompaniesHouseFinancialAnalyzer()
    
    # Try exact name match first
    company_number = analyzer.search_company(care_home.name)
    
    if company_number:
        return company_number
    
    # Try without "Limited", "Ltd", etc
    clean_name = care_home.name.replace(' Limited', '')
    clean_name = clean_name.replace(' Ltd', '')
    company_number = analyzer.search_company(clean_name)
    
    if company_number:
        return company_number
    
    # Try parent company name if available
    if care_home.parent_company:
        company_number = analyzer.search_company(care_home.parent_company)
    
    return company_number
```

---

## ❓ FAQ

### Q: Что если дом престарелых не найден?

A: Не все дома - это отдельные компании. Некоторые являются частью больших сетей (например, Barchester). В этом случае анализируйте parent company.

### Q: Как часто обновлять данные?

A: Companies House обновляется real-time, но:
- Accounts: Раз в год
- Officers: При изменениях
- Charges: При регистрации

**Рекомендация**: Обновлять кэш раз в неделю для FREE/Professional, ежедневно для Premium.

### Q: Стоит ли исключать новые компании (<2 года)?

A: Не обязательно. Новая компания != плохая компания. Но:
- FREE tier: Можно фильтровать
- Professional/Premium: Показывать с предупреждением "New business - limited track record"

### Q: Что если accounts overdue?

A: Это серьёзный red flag:
- Может означать финансовые проблемы
- Может быть технической ошибкой
- Может быть намеренным уклонением

**Рекомендация**: 
- FREE: Не показывать
- Professional: Показывать с явным предупреждением
- Premium: Мониторить + алерт

---

## 🔗 Полезные ссылки

- **API Portal**: https://developer.company-information.service.gov.uk/
- **Documentation**: https://developer-specs.company-information.service.gov.uk/
- **GitHub**: https://github.com/companieshouse
- **Support**: enquiries@companieshouse.gov.uk

---

## 🎉 Что дальше?

1. ✅ Прочитать **CompaniesHouse_Integration_Guide.md** (полное руководство)
2. ✅ Получить API ключ
3. ✅ Протестировать **companies_house_analyzer.py**
4. ✅ Интегрировать в свою систему
5. ✅ Добавить БД для хранения метрик
6. ✅ Настроить мониторинг (для Premium)

---

## 💪 Конкурентное преимущество

Companies House API даёт RightCareHome уникальное преимущество:

✅ **Единственные с финансовым анализом** - конкуренты не проверяют устойчивость  
✅ **Защита клиентов** - избегаем домов на грани банкротства  
✅ **Доверие** - "Мы проверили финансовое здоровье"  
✅ **Premium feature** - мониторинг финансовых изменений  
✅ **Risk mitigation** - снижаем риск для семей  

**Бесплатный API. Официальные данные. Real-time.**

---

*Версия: 1.0*  
*Дата: November 2025*  
*Для: RightCareHome Platform*

## 📞 Вопросы?

Начните с **CompaniesHouse_Integration_Guide.md** для полного понимания API и возможностей интеграции!

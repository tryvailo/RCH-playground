# ✅ Исправление использования недельных цен из Staging базы данных

**Дата:** 2025-12-20  
**Статус:** ✅ ИСПРАВЛЕНО

---

## 🎯 Проблемы обнаружены и исправлены

### **Проблема 1: Отсутствовал маппинг `fee_nursing_from`** ❌ → ✅

**Проблема:**
- В staging CSV есть поле `parsed_fee_nursing_from`
- В матчинге используется `fee_nursing_from`
- НО маппинг отсутствовал в `STAGING_PRICING_MAPPING`

**Исправление:**
```python
# services/staging_data_loader.py
STAGING_PRICING_MAPPING = {
    'fee_residential_from': 'parsed_fee_residential_from',
    'fee_nursing_from': 'parsed_fee_nursing_from',  # ✅ ДОБАВЛЕНО
    'fee_dementia_from': 'parsed_fee_dementia_from',
    'fee_respite_from': 'parsed_fee_respite_from'
}
```

**Также добавлено в:**
- `STAGING_PREFERRED_FIELDS` в `hybrid_data_merger.py` ✅

---

### **Проблема 2: Неправильная проверка бюджета в профессиональном отчете** ❌ → ✅

**Проблема:**
- Цены из staging хранятся как **недельные** (Weekly fees)
- `_get_home_price()` возвращает недельную цену
- НО проверка бюджета использовала месячные значения (3000, 5000, 7000) напрямую

**Исправление:**
```python
# services/professional_matching_service.py
# _generate_cost_reasoning()

# Budget ranges in weekly £ (monthly ÷ 4.33)
BUDGET_RANGES_WEEKLY = {
    'under_3000_self': (0, 692),       # £3000/month ÷ 4.33
    'under_3000_council': (0, 692),
    '3000_5000_self': (692, 1154),     # £3000-5000/month
    '3000_5000_council': (692, 1154),
    '5000_7000_self': (1154, 1616),    # £5000-7000/month
    '5000_7000_local': (1154, 1616),
    '7000_plus_self': (1616, 5000),    # £7000+/month
    'not_sure': (0, 5000),             # Any budget
}

min_budget_weekly, max_budget_weekly = BUDGET_RANGES_WEEKLY.get(budget, (0, 5000))

# Check if price is within weekly budget range
if price <= max_budget_weekly:
    # ... правильная проверка недельной цены против недельного бюджета
```

---

## 📊 Проверка использования цен

### **1. Бесплатный отчет (SimpleMatchingService)** ✅

**Файл:** `services/simple_matching_service.py`

**Метод:** `_calculate_budget_match()` (строки 1309-1407)

**Используемые поля:**
- ✅ `fee_dementia_from` - загружается из staging
- ✅ `fee_nursing_from` - **ТЕПЕРЬ загружается из staging** (исправлено)
- ✅ `fee_residential_from` - загружается из staging

**Бюджет конвертируется:**
- ✅ Месячный бюджет → недельный: `monthly ÷ 4.33`
- ✅ Недельная цена сравнивается с недельным бюджетом

**Статус:** ✅ **ПРАВИЛЬНО**

---

### **2. Профессиональный отчет (ProfessionalMatchingService)** ✅

**Файл:** `services/professional_matching_service.py`

**Метод:** `_get_home_price()` (строки 1538-1554)
- ✅ Использует `extract_weekly_price()` из `utils/price_extractor.py`
- ✅ Проверяет поля: `fee_residential_from`, `fee_nursing_from`, `fee_dementia_from`, `fee_respite_from`
- ✅ Возвращает недельную цену

**Метод:** `_generate_cost_reasoning()` (строки 1673-1706)
- ✅ **ТЕПЕРЬ правильно конвертирует месячный бюджет в недельный** (исправлено)
- ✅ Сравнивает недельную цену с недельным бюджетом

**Статус:** ✅ **ПРАВИЛЬНО** (после исправления)

---

## 📋 Формат цен в Staging базе

**Подтверждено:**
- ✅ Цены в staging хранятся как **недельные** (Weekly fees)
- ✅ Документация: "Weekly fees - maps to fee_*_from flat fields"
- ✅ Поля: `parsed_fee_residential_from`, `parsed_fee_nursing_from`, `parsed_fee_dementia_from`, `parsed_fee_respite_from`
- ✅ Все цены в формате GBP (фунты стерлингов)

**Конвертация НЕ требуется:**
- ✅ Цены уже недельные
- ✅ Используются напрямую в матчинге

---

## ✅ Итоговая таблица использования цен

| Поле | В staging CSV | В маппинге | Используется в матчинге | Статус |
|------|---------------|------------|------------------------|--------|
| `fee_residential_from` | ✅ `parsed_fee_residential_from` | ✅ | ✅ Бесплатный + Профессиональный | ✅ **OK** |
| `fee_nursing_from` | ✅ `parsed_fee_nursing_from` | ✅ **ИСПРАВЛЕНО** | ✅ Бесплатный + Профессиональный | ✅ **OK** |
| `fee_dementia_from` | ✅ `parsed_fee_dementia_from` | ✅ | ✅ Бесплатный + Профессиональный | ✅ **OK** |
| `fee_respite_from` | ✅ `parsed_fee_respite_from` | ✅ | ⚠️ Редко | ✅ **OK** |

---

## ✅ Проверка конвертации бюджета

### **Бесплатный отчет:**
- ✅ Бюджет конвертируется: `monthly ÷ 4.33` → недельный
- ✅ Недельная цена сравнивается с недельным бюджетом
- ✅ **ПРАВИЛЬНО**

### **Профессиональный отчет:**
- ✅ **ИСПРАВЛЕНО:** Бюджет конвертируется: `monthly ÷ 4.33` → недельный
- ✅ Недельная цена сравнивается с недельным бюджетом
- ✅ **ПРАВИЛЬНО** (после исправления)

---

## 🎯 Выводы

### **Исправления применены:**

1. ✅ Добавлен маппинг `fee_nursing_from` → `parsed_fee_nursing_from` в `staging_data_loader.py`
2. ✅ Добавлен `fee_nursing_from` в `STAGING_PREFERRED_FIELDS` в `hybrid_data_merger.py`
3. ✅ Исправлена проверка бюджета в профессиональном отчете (конвертация месячного в недельный)

### **Проверка формата цен:**

- ✅ Цены в staging хранятся как **недельные** (Weekly fees)
- ✅ Конвертация НЕ требуется
- ✅ Используются напрямую в матчинге

### **Использование в матчинге:**

- ✅ **Бесплатный отчет:** Правильно использует недельные цены из staging
- ✅ **Профессиональный отчет:** Правильно использует недельные цены из staging (после исправления)

---

**Все проблемы исправлены!** ✅

**Последнее обновление:** 2025-12-20






# 🔍 Анализ использования недельных цен из Staging базы данных

**Дата:** 2025-12-20  
**Статус:** 🔍 АНАЛИЗ

---

## 🎯 Цель

Проверить правильность использования недельных цен из staging базы данных при анализе и матчинге бесплатного и профессионального отчетов.

---

## 📊 Проблемы обнаружены

### **Проблема 1: Отсутствует маппинг `fee_nursing_from` в staging_data_loader.py** ❌

**Текущий маппинг:**
```python
STAGING_PRICING_MAPPING = {
    'fee_residential_from': 'parsed_fee_residential_from',
    'fee_dementia_from': 'parsed_fee_dementia_from',
    'fee_respite_from': 'parsed_fee_respite_from'
    # ❌ ОТСУТСТВУЕТ: 'fee_nursing_from': 'parsed_fee_nursing_from'
}
```

**В staging CSV ЕСТЬ поле:** `parsed_fee_nursing_from` ✅

**В матчинге используется:** `fee_nursing_from` ✅

**Проблема:** `fee_nursing_from` не загружается из staging базы, хотя поле есть в CSV!

---

### **Проблема 2: Неясно, в каком формате хранятся цены в staging**

**Вопросы:**
- Хранятся ли цены в staging как недельные или месячные?
- Нужна ли конвертация?

**В матчинге:**
- Бюджет конвертируется из месячного в недельный: `monthly ÷ 4.33`
- Цены используются напрямую как `weekly_fee`

**Если цены в staging месячные, то они используются неправильно!**

---

## 📋 Текущее использование цен

### **1. Бесплатный отчет (SimpleMatchingService)**

**Файл:** `services/simple_matching_service.py`

**Метод:** `_calculate_budget_match()` (строки 1309-1407)

**Используемые поля:**
- `fee_dementia_from` ✅
- `fee_nursing_from` ✅ (НО не загружается из staging!)
- `fee_residential_from` ✅

**Логика:**
```python
weekly_fee = None
if 'specialised_dementia' in required_care:
    weekly_fee = (
        home.get('fee_dementia_from') or
        home.get('fee_nursing_from') or  # ❌ Может быть None, т.к. не загружается из staging
        home.get('fee_residential_from')
    )
elif 'medical_nursing' in required_care:
    weekly_fee = (
        home.get('fee_nursing_from') or  # ❌ Может быть None, т.к. не загружается из staging
        home.get('fee_residential_from')
    )
else:
    weekly_fee = (
        home.get('fee_residential_from') or
        home.get('fee_nursing_from')  # ❌ Может быть None, т.к. не загружается из staging
    )
```

**Бюджет конвертируется:**
```python
BUDGET_RANGES = {
    'under_3000_self': (0, 692),       # £3000/month ÷ 4.33
    '3000_5000_self': (692, 1154),    # £3000-5000/month
    '5000_7000_self': (1154, 1616),   # £5000-7000/month
    '7000_plus_self': (1616, 5000),   # £7000+/month
}
```

**Вывод:** ✅ Бюджет правильно конвертируется из месячного в недельный  
❌ `fee_nursing_from` не загружается из staging

---

### **2. Профессиональный отчет (ProfessionalMatchingService)**

**Файл:** `services/professional_matching_service.py`

**Метод:** `_get_home_price()` (нужно проверить)

**Использование:** В `_generate_match_reasoning()` (строка 1682)

**Проблема:** Нужно проверить, как используется цена в профессиональном отчете

---

## 🔧 Необходимые исправления

### **Исправление 1: Добавить маппинг `fee_nursing_from`**

**Файл:** `services/staging_data_loader.py`

**Изменить:**
```python
STAGING_PRICING_MAPPING = {
    'fee_residential_from': 'parsed_fee_residential_from',
    'fee_dementia_from': 'parsed_fee_dementia_from',
    'fee_respite_from': 'parsed_fee_respite_from',
    'fee_nursing_from': 'parsed_fee_nursing_from'  # ✅ ДОБАВИТЬ
}
```

---

### **Исправление 2: Проверить формат цен в staging**

**Нужно проверить:**
1. В каком формате хранятся цены в staging CSV (недельные или месячные)?
2. Если месячные - добавить конвертацию при загрузке
3. Если недельные - оставить как есть

---

### **Исправление 3: Проверить использование цен в профессиональном отчете**

**Нужно проверить:**
1. Используется ли `_get_home_price()` в профессиональном отчете?
2. Правильно ли конвертируется бюджет?
3. Используются ли правильные поля цен?

---

## 📊 Текущее состояние

| Поле | В staging CSV | В маппинге | Используется в матчинге | Статус |
|------|---------------|------------|------------------------|--------|
| `fee_residential_from` | ✅ `parsed_fee_residential_from` | ✅ | ✅ | ✅ **OK** |
| `fee_dementia_from` | ✅ `parsed_fee_dementia_from` | ✅ | ✅ | ✅ **OK** |
| `fee_respite_from` | ✅ `parsed_fee_respite_from` | ✅ | ⚠️ Редко | ✅ **OK** |
| `fee_nursing_from` | ✅ `parsed_fee_nursing_from` | ❌ **ОТСУТСТВУЕТ** | ✅ | ❌ **ПРОБЛЕМА** |

---

## ⚠️ Критичность

**Высокая:** `fee_nursing_from` критично важен для матчинга домов с nursing care, но не загружается из staging базы!

---

**Последнее обновление:** 2025-12-20






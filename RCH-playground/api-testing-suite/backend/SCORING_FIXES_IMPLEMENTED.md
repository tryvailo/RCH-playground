# Исправления скоринга: Реализованные доработки

**Дата:** 2025-12-18  
**Источник:** `documents/report-algorithms/scoring-fix.py`

---

## ✅ Реализованные исправления

### 1. Budget Match (q7_budget) - КРИТИЧНО! ✅

**Проблема:** Бюджет клиента полностью игнорировался в матчинге.

**Решение:**
- ✅ Добавлен метод `_calculate_budget_match()` в `SimpleMatchingService`
- ✅ Интегрирован в `_calculate_financial()` как **35% веса** (самый важный фактор)
- ✅ Парсинг бюджетных диапазонов из анкеты
- ✅ Извлечение цены дома с учетом типа ухода (dementia/nursing/residential)
- ✅ Скоринг: 100% если в бюджете, снижение при превышении

**Файл:** `services/simple_matching_service.py` (метод `_calculate_financial`)

**Логика:**
```python
Budget Match: 35 points
- В пределах бюджета: 24.5-35 points
- До 10% превышения: 19.25 points
- До 20% превышения: 14 points
- До 30% превышения: 8.75 points
- >30% превышения: 3.5 points
```

---

### 2. Medication Management (q11) ✅

**Проблема:** Требования по медикаментам не учитывались.

**Решение:**
- ✅ Добавлен метод `_calculate_medication_match()` в `SimpleMatchingService`
- ✅ Интегрирован в `_calculate_medical_safety()` как **15% веса**
- ✅ Сложные медикаменты требуют nursing care
- ✅ Простые медикаменты - любой дом подходит

**Файл:** `services/simple_matching_service.py` (метод `_calculate_medical_safety`)

**Логика:**
```python
Medication Match: 15 points
- Complex/Multiple medications + Nursing care: 15 points
- Complex/Multiple medications + No nursing: 6 points (40%)
- Simple routine: 15 points (any home)
```

---

### 3. Age Range (q12) ✅

**Проблема:** Возрастная группа не учитывалась.

**Решение:**
- ✅ Добавлен метод `_calculate_age_match()` в `SimpleMatchingService`
- ✅ Интегрирован в `_calculate_medical_safety()` как **10% веса**
- ✅ Проверка `serves_younger_adults`, `serves_older_people`, `serves_whole_population`

**Файл:** `services/simple_matching_service.py` (метод `_calculate_medical_safety`)

**Логика:**
```python
Age Match: 10 points
- Under 65 + serves_younger_adults: 10 points
- Under 65 + serves_whole_population: 8 points
- Under 65 + serves_older_people only: 3 points
- 65+ + serves_older_people: 10 points
- 65+ + serves_whole_population: 9 points
```

---

### 4. Обновленная структура скоринга

#### Financial Scoring (было → стало)

| Компонент | Было | Стало | Изменение |
|-----------|------|-------|-----------|
| **Budget Match** | ❌ 0% | ✅ **35%** | **НОВОЕ!** |
| Altman Z-Score | 40% | 30% | -10% |
| Revenue Trend | 25% | 20% | -5% |
| Profitability | 20% | ❌ Убрано | -20% |
| Red Flags | 15% | 15% | Без изменений |

#### Medical & Safety Scoring (было → стало)

| Компонент | Было | Стало | Изменение |
|-----------|------|-------|-----------|
| Care Type Match | 40% | 30% | -10% |
| CQC Safe Rating | 35% | 25% | -10% |
| Accessibility | 15% | 15% | Без изменений |
| **Medication Match** | ❌ 0% | ✅ **15%** | **НОВОЕ!** |
| **Age Match** | ❌ 0% | ✅ **10%** | **НОВОЕ!** |
| Special Needs | 10% | 5% | -5% |

---

## 📊 Итоговая таблица использования полей анкеты

| Поле | Было | Стало | Где используется |
|------|------|-------|------------------|
| q5_preferred_city | ⚠️ Частично | ✅ Исправлено | Geo-filter (geocoding) |
| q6_max_distance | ✅ | ✅ | Geo-filter + Location scoring |
| **q7_budget** | ❌ **НЕ использовалось** | ✅ **35% Financial** | **КРИТИЧНО!** |
| q8_care_types | ✅ | ✅ | Care type filter + Medical (30%) |
| q9_medical_conditions | ✅ | ✅ | Dynamic weights + Accessibility |
| q10_mobility_level | ✅ | ✅ | Accessibility (15%) |
| **q11_medication_management** | ❌ **НЕ использовалось** | ✅ **15% Medical** | **ВАЖНО!** |
| **q12_age_range** | ❌ **НЕ использовалось** | ✅ **10% Medical** | **ВАЖНО!** |
| q13_fall_history | ✅ | ✅ | Dynamic weights |
| q14_allergies | ❌ | ❌ | Только для отчёта (OK) |
| q15_dietary_requirements | ❌ | ❌ | Только для отчёта (OK) |
| q16_social_personality | ❌ | ❌ | v1.1 (Nice-to-have) |
| q17_placement_timeline | ✅ | ✅ | Dynamic weights |
| q18_priority_ranking | ❌ (намеренно) | ❌ | v2 (после MVP) |

---

## 🔍 Детали реализации

### Budget Match - Логика извлечения цены

```python
# Приоритет цены зависит от типа ухода:
if 'specialised_dementia' in required_care:
    weekly_fee = fee_dementia_from OR fee_nursing_from OR fee_residential_from
elif 'medical_nursing' in required_care:
    weekly_fee = fee_nursing_from OR fee_residential_from
else:
    weekly_fee = fee_residential_from OR fee_nursing_from
```

### Medication Match - Проверка nursing care

```python
# Сложные медикаменты требуют:
- care_nursing = True
- OR 'nursing' in care_types
- OR has_nursing_care_license = True
```

### Age Match - Проверка возрастной группы

```python
# Поля в базе данных:
- serves_younger_adults (для <65)
- serves_older_people (для 65+)
- serves_whole_population (для всех)
```

---

## ⚠️ Важные замечания

### 1. Postcode vs City

**Текущая реализация:**
- Используется `q5_preferred_city` (может быть и postcode, и город)
- Геокодирование через Nominatim (OpenStreetMap) для городов
- Postcode resolution через postcodes.io (если формат соответствует)

**Рекомендация:** Для MVP достаточно. Postcode можно добавить как отдельное поле в v1.1.

### 2. Budget Ranges

**Формат:** Месячный бюджет → конвертируется в недельный (÷ 4.33)

**Диапазоны:**
- `under_3000_*`: £0-692/week
- `3000_5000_*`: £692-1154/week
- `5000_7000_*`: £1154-1616/week
- `7000_plus_*`: £1616+/week

### 3. Medication Values

**Возможные значения:**
- `simple_routine` → любой дом (15 points)
- `several_simple_routine` → любой дом (15 points)
- `complex_medication` → требует nursing (15 или 6 points)
- `multiple_medications` → требует nursing (15 или 6 points)

### 4. Age Range Values

**Возможные значения:**
- `under_65` → проверка `serves_younger_adults`
- `65_74`, `75_84`, `85_94`, `95_plus` → проверка `serves_older_people`

---

## ✅ Тестирование

### Тест 1: Budget Match

**Анкета:** `q7_budget = "5000_7000_local"` (бюджет £1154-1616/week)

**Дом 1:** `fee_dementia_from = 1200` → ✅ В бюджете → 31.5 points
**Дом 2:** `fee_dementia_from = 1800` → ⚠️ Превышает на 11% → 19.25 points
**Дом 3:** `fee_dementia_from = 2200` → ❌ Превышает на 36% → 3.5 points

### Тест 2: Medication Match

**Анкета:** `q11_medication_management = "complex_medication"`

**Дом 1:** `care_nursing = True` → ✅ 15 points
**Дом 2:** `care_nursing = False` → ⚠️ 6 points (40%)

### Тест 3: Age Match

**Анкета:** `q12_age_range = "85_94"`

**Дом 1:** `serves_older_people = True` → ✅ 10 points
**Дом 2:** `serves_whole_population = True` → ✅ 9 points
**Дом 3:** `serves_younger_adults = True` → ⚠️ 5 points

---

## 📝 Следующие шаги

1. ✅ **Реализовано:** Budget, Medication, Age в скоринг
2. ⏳ **v1.1:** Social Personality (q16) в Lifestyle scoring
3. ⏳ **v2:** User Priorities (Section 6) в динамические веса

---

**Статус:** ✅ Все критические исправления внедрены


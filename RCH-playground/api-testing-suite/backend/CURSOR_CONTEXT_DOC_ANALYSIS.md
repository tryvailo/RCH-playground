# Глубокий анализ: Обновления логики матчинга из базы данных

## 📋 Обзор документов

**Основной документ:** `documents/report-algorithms/cursor-context-doc.md`  
**Fallback логика:** `documents/report-algorithms/matching-fallback-logic.py`  
**Приоритет:** HIGH  
**Проблема:** Текущий алгоритм игнорирует 80% доступных полей БД, что приводит к плохой дифференциации между домами  
**Решение:** Использовать 12 Service User Band полей и все CQC данные для точного матчинга с двухуровневой fallback логикой для обработки NULL значений

---

## 🔍 Текущее состояние vs. Требуемое

### Проблемы текущей реализации

#### 1. Service User Bands (12 полей) — НЕ ИСПОЛЬЗУЮТСЯ ❌

**Поля в БД:**
- `serves_older_people`
- `serves_younger_adults`
- `serves_mental_health`
- `serves_physical_disabilities`
- `serves_sensory_impairments`
- `serves_dementia_band`
- `serves_children`
- `serves_learning_disabilities`
- `serves_detained_mha`
- `serves_substance_misuse`
- `serves_eating_disorders`
- `serves_whole_population`

**Текущее использование:** ❌ Не используются в матчинге

**Требуется:** ✅ Использовать для матчинга медицинских условий и поведенческих проблем

---

#### 2. CQC Ratings (6 полей) — Используется только 4 ❌

**Поля в БД:**
- ✅ `cqc_rating_overall` — используется
- ✅ `cqc_rating_safe` — используется
- ✅ `cqc_rating_effective` — используется
- ✅ `cqc_rating_caring` — используется
- ❌ `cqc_rating_responsive` — **НЕ используется**
- ✅ `cqc_rating_well_led` — используется
- ❌ `cqc_last_inspection_date` — **НЕ используется** (inspection freshness)

**Требуется:** ✅ Использовать все 6 рейтингов + inspection freshness

---

#### 3. Licenses (5 полей) — НЕ ИСПОЛЬЗУЮТСЯ ❌

**Поля в БД:**
- `has_nursing_care_license`
- `has_personal_care_license`
- `has_surgical_procedures_license`
- `has_treatment_license`
- `has_diagnostic_license`

**Текущее использование:** ❌ Не используются напрямую (только как proxy для care_nursing)

**Требуется:** ✅ Использовать для более точного матчинга медицинских потребностей

---

## 📊 Маппинг: Questionnaire → Database Fields

### Q9: Medical Conditions → Service User Bands

| Условие из анкеты | Поле в БД | Вес | Fallback |
|-------------------|-----------|-----|----------|
| `dementia_alzheimers` | `serves_dementia_band` | critical | `care_dementia` |
| `parkinsons` | `serves_physical_disabilities` | high | - |
| `stroke_recovery` | `serves_physical_disabilities` | high | - |
| `heart_conditions` | - | medium | `has_nursing_care_license` |
| `diabetes` | - | low | - |
| `arthritis` | `serves_physical_disabilities` | medium | - |
| `visual_impairment` | `serves_sensory_impairments` | high | - |
| `hearing_impairment` | `serves_sensory_impairments` | medium | - |

### Q16: Behavioral Concerns → Service User Bands

| Проблема из анкеты | Поле в БД | Вес | Amenity |
|-------------------|-----------|-----|---------|
| `anxiety` | `serves_mental_health` | medium | - |
| `depression` | `serves_mental_health` | medium | - |
| `wandering_risk` | `serves_dementia_band` | critical | `secure_garden` |
| `sundowning` | `serves_dementia_band` | high | - |
| `aggression_risk` | `serves_mental_health` | high | - |
| `social_withdrawal` | `serves_mental_health` | low | - |

### Q10: Mobility Level → DB Fields

| Уровень мобильности | Обязательные поля | Вес |
|---------------------|-------------------|-----|
| `wheelchair_user` | `wheelchair_access` | critical |
| `bed_bound` | `has_nursing_care_license` | critical |
| `uses_walking_aid` | - | low |
| `fully_independent` | - | none |

### Q12: Age Range → Service User Bands

| Возраст | Поле в БД |
|---------|-----------|
| `under_65` | `serves_younger_adults` |
| `65_74`, `75_84`, `85_94`, `95_plus` | `serves_older_people` |

---

## 🎯 Требуемые изменения

### 1. Создать файл `matching/constants.py` ✅ НОВЫЙ ФАЙЛ

**Содержимое:**
- `CONDITION_TO_SERVICE_BAND` — маппинг медицинских условий
- `BEHAVIORAL_TO_SERVICE_BAND` — маппинг поведенческих проблем
- `MOBILITY_TO_FIELDS` — маппинг уровня мобильности
- `AGE_TO_SERVICE_BAND` — маппинг возраста
- `WEIGHT_VALUES` — значения весов для скоринга

**Приоритет:** HIGH

---

### 2. Обновить фильтрацию (Step 3) ✅ ОБНОВИТЬ

**Файл:** `services/simple_matching_service.py` или создать `matching/filters.py`

**Текущая логика:**
```python
# Только базовая проверка care types
if 'specialised_dementia' in required_care:
    if home.care_dementia or home.serves_dementia_band:
        matches = True
```

**Новая логика:**
- Проверка Service User Bands для медицинских условий
- Проверка Service User Bands для поведенческих проблем
- Проверка mobility requirements
- Проверка age range
- Возврат статуса: `match` | `partial` | `disqualified`

**Приоритет:** HIGH

---

### 3. Добавить Service Bands Score Component ✅ НОВЫЙ МЕТОД

**Файл:** `services/simple_matching_service.py`

**Новый метод:** `_calculate_service_bands_score()`

**Логика:**
- Проверка соответствия медицинских условий → Service User Bands
- Проверка соответствия поведенческих проблем → Service User Bands
- Взвешенный скоринг на основе весов (critical, high, medium, low)
- Fallback логика для условий без прямого маппинга

**Приоритет:** HIGH

---

### 4. Обновить Quality Score ✅ ОБНОВИТЬ

**Файл:** `services/simple_matching_service.py`

**Текущая логика:**
- Использует только 4 CQC рейтинга (overall, safe, caring, effective, well_led)
- Не использует `cqc_rating_responsive`
- Не использует `cqc_last_inspection_date` (inspection freshness)

**Новая логика:**
- Использовать все 6 CQC рейтингов с весами:
  - Overall: 25%
  - Safe: 25%
  - Caring: 20%
  - Effective: 15%
  - **Responsive: 10%** ← НОВОЕ
  - Well-led: 5%
- Добавить Inspection Freshness Bonus (до +10 points):
  - ≤180 дней: +10 points
  - ≤365 дней: +7 points
  - ≤730 дней: +4 points
  - >730 дней: 0 points

**Приоритет:** HIGH

---

### 5. Обновить Medical & Safety Score ✅ ОБНОВИТЬ

**Файл:** `services/simple_matching_service.py`

**Текущая логика:**
- Care Type Match: 30 points
- CQC Safe Rating: 25 points
- Accessibility: 15 points
- Medication Match: 15 points
- Equipment Match: 10 points
- Age Match: 5 points

**Новая логика:**
- **Service Bands Score: 35%** ← НОВОЕ (вместо Care Type Match)
- CQC Safe Rating: 30%
- Care Type Match: 20%
- Accessibility: 15%

**Приоритет:** HIGH

---

## 📝 План внедрения

### Этап 1: Создание констант маппинга

**Файл:** `services/matching_constants.py` (новый)

**Задачи:**
1. ✅ Создать `CONDITION_TO_SERVICE_BAND` словарь
2. ✅ Создать `BEHAVIORAL_TO_SERVICE_BAND` словарь
3. ✅ Создать `MOBILITY_TO_FIELDS` словарь
4. ✅ Создать `AGE_TO_SERVICE_BAND` словарь
5. ✅ Создать `WEIGHT_VALUES` словарь

**Оценка:** 1-2 часа

---

### Этап 2: Обновление фильтрации

**Файл:** `services/simple_matching_service.py`

**Задачи:**
1. ✅ Создать метод `_evaluate_home_match()` для проверки соответствия
2. ✅ Обновить логику загрузки домов для использования Service User Bands
3. ✅ Добавить проверку critical requirements (disqualify если не соответствуют)
4. ✅ Добавить проверку partial matches (warnings)

**Оценка:** 2-3 часа

---

### Этап 3: Добавление Service Bands Score

**Файл:** `services/simple_matching_service.py`

**Задачи:**
1. ✅ Создать метод `_calculate_service_bands_score()`
2. ✅ Интегрировать в `_calculate_medical_safety()`
3. ✅ Добавить fallback логику для условий без прямого маппинга
4. ✅ Добавить логирование для debugging

**Оценка:** 2-3 часа

---

### Этап 4: Обновление Quality Score

**Файл:** `services/simple_matching_service.py`

**Задачи:**
1. ✅ Обновить `_calculate_quality_care()` для использования всех 6 CQC рейтингов
2. ✅ Добавить Inspection Freshness Bonus
3. ✅ Обновить веса рейтингов (responsive: 10%)
4. ✅ Добавить логирование для debugging

**Оценка:** 1-2 часа

---

### Этап 5: Обновление Medical & Safety Score

**Файл:** `services/simple_matching_service.py`

**Задачи:**
1. ✅ Интегрировать Service Bands Score в `_calculate_medical_safety()`
2. ✅ Обновить веса компонентов:
   - Service Bands: 35%
   - CQC Safe: 30%
   - Care Type: 20%
   - Accessibility: 15%
3. ✅ Убедиться, что общий вес = 100%

**Оценка:** 1-2 часа

---

### Этап 6: Тестирование

**Задачи:**
1. ✅ Unit тесты для Service Bands matching
2. ✅ Unit тесты для Quality Score с responsive
3. ✅ Integration тесты для полного flow
4. ✅ Проверка дифференциации scores (должна быть 30+ points spread)

**Оценка:** 2-3 часа

---

## 🔧 Технические детали

### Структура файлов

```
services/
├── simple_matching_service.py (обновить)
├── matching_constants.py (создать)
└── matching_filters.py (опционально, можно интегрировать в simple_matching_service.py)
```

### Интеграция с текущим кодом

**Текущая структура:**
- `SimpleMatchingService` использует `_calculate_medical_safety()`
- `_calculate_medical_safety()` использует базовые проверки
- `_calculate_quality_care()` использует только 4 CQC рейтинга

**Новая структура:**
- `SimpleMatchingService` использует `_calculate_medical_safety()` (обновлен)
- `_calculate_medical_safety()` использует `_calculate_service_bands_score()` (новый)
- `_calculate_quality_care()` использует все 6 CQC рейтингов + freshness (обновлен)

---

## ⚠️ Важные вопросы для уточнения

1. **Hard filter vs. Soft penalty:**
   - Документ предлагает hard filter для critical requirements
   - Текущая реализация использует soft penalty (снижение score)
   - **Рекомендация:** Использовать hard filter для critical (wheelchair_access, has_nursing_care_license), soft penalty для остальных

2. **Palliative care:**
   - В анкете есть `palliative`, но в БД нет `serves_palliative`
   - **Рекомендация:** Использовать proxy через `has_nursing_care_license` + `care_nursing`

3. **Inspection freshness:**
   - Документ предлагает bonus (до +10 points)
   - **Рекомендация:** Интегрировать в Quality Score как bonus

4. **Minimum data quality:**
   - Документ не указывает минимальный порог
   - **Рекомендация:** Использовать текущий порог (если есть) или не фильтровать по data quality

---

## 📊 Ожидаемые результаты

### До изменений:
```
Home A: 72/100
Home B: 71/100
Home C: 73/100
Home D: 72/100
Home E: 71/100
(Spread: 2 points)
```

### После изменений:
```
Home A: 89/100 (serves_dementia_band=True, secure_garden=True)
Home B: 78/100 (serves_dementia_band=True, secure_garden=False)
Home C: 65/100 (serves_dementia_band=False, care_dementia=True)
Home D: 52/100 (serves_dementia_band=False, no dementia care)
Home E: 45/100 (no matching service bands)
(Spread: 44 points)
```

---

## ✅ Приоритеты внедрения

| Этап | Приоритет | Сложность | Время |
|------|-----------|-----------|-------|
| 1. Константы маппинга | HIGH | Low | 1-2h |
| 2. Обновление фильтрации | HIGH | Medium | 2-3h |
| 3. Service Bands Score | HIGH | Medium | 2-3h |
| 4. Quality Score (responsive + freshness) | HIGH | Low | 1-2h |
| 5. Medical & Safety (интеграция) | HIGH | Low | 1-2h |
| 6. Тестирование | MEDIUM | Medium | 2-3h |
| **ИТОГО** | - | - | **9-15 часов** |

---

## 🎯 Следующие шаги

1. ✅ Создать `matching_constants.py` с маппингами
2. ✅ Обновить `_calculate_medical_safety()` для использования Service Bands
3. ✅ Обновить `_calculate_quality_care()` для использования всех 6 рейтингов + freshness
4. ✅ Добавить `_calculate_service_bands_score()` метод
5. ✅ Обновить фильтрацию для проверки critical requirements
6. ✅ Добавить тесты
7. ✅ Проверить дифференциацию scores

---

---

## 🔄 КРИТИЧЕСКИ ВАЖНО: Fallback логика для NULL значений

### Проблема NULL vs. FALSE

**Источник:** `matching-fallback-logic.py`

**НЕПРАВИЛЬНОЕ предположение:**
```python
if home.get('serves_dementia_band') is None:
    # Дом НЕ принимает пациентов с деменцией
    return 0.0
```

**ПРАВИЛЬНАЯ интерпретация:**
```python
if home.get('serves_dementia_band') is None:
    # Мы НЕ ЗНАЕМ! Проверить proxy поля
    # NULL ≠ FALSE
    # NULL = "данные недоступны"
```

### Двухуровневая система матчинга

#### Level 1: Direct Match (прямое соответствие)
- Поле имеет значение (TRUE или FALSE)
- **TRUE** → `MatchResult.MATCH` → Score: 100% веса
- **FALSE** → `MatchResult.NO_MATCH` → Score: 0% веса (если critical → DISQUALIFY)

#### Level 2: Proxy Match (proxy соответствие)
- Поле = NULL, но есть proxy поле с TRUE
- **Proxy TRUE** → `MatchResult.PROXY_MATCH` → Score: confidence% веса (70-90%)
- **Proxy NULL** → `MatchResult.UNKNOWN` → Score: null_penalty% веса (50-70%)

#### Level 3: Unknown (неизвестно)
- Поле = NULL, proxy поля тоже NULL
- **Все NULL** → `MatchResult.UNKNOWN` → Score: null_penalty% веса
- Добавляется warning: "Cannot verify - recommend calling home"

---

### Конфигурация Proxy полей

**Источник:** `matching-fallback-logic.py`, `FIELD_PROXY_CONFIG`

#### Ключевые Proxy маппинги:

```python
FIELD_PROXY_CONFIG = {
    'serves_dementia_band': {
        'proxies': [
            {'field': 'care_dementia', 'confidence': 0.9, 'condition': True},
            {'field': 'care_nursing', 'confidence': 0.5, 'condition': True},
        ],
        'null_penalty': 0.7,
    },
    
    'serves_physical_disabilities': {
        'proxies': [
            {'field': 'wheelchair_access', 'confidence': 0.8, 'condition': True},
            {'field': 'care_nursing', 'confidence': 0.6, 'condition': True},
        ],
        'null_penalty': 0.7,
    },
    
    'wheelchair_access': {
        'proxies': [
            {'field': 'serves_physical_disabilities', 'confidence': 0.7, 'condition': True},
            {'field': 'care_nursing', 'confidence': 0.6, 'condition': True},
        ],
        'null_penalty': 0.6,
    },
    
    'has_nursing_care_license': {
        'proxies': [
            {'field': 'care_nursing', 'confidence': 0.95, 'condition': True},
        ],
        'null_penalty': 0.5,
    },
}
```

---

### Примеры работы Fallback логики

#### Сценарий 1: Dementia patient, `serves_dementia_band` = NULL

**Дом:**
```python
{
    'serves_dementia_band': None,  # NULL!
    'care_dementia': True,          # Proxy поле
}
```

**Результат:**
```python
FieldMatchResult(
    result=MatchResult.PROXY_MATCH,
    field_checked='serves_dementia_band',
    proxy_used='care_dementia',
    confidence=0.9,
    score_multiplier=0.9  # 90% веса вместо 100%
)
```

---

#### Сценарий 2: Все поля NULL

**Дом:**
```python
{
    'wheelchair_access': None,
    'serves_physical_disabilities': None,
    'care_nursing': None
}
```

**Результат:**
```python
FieldMatchResult(
    result=MatchResult.UNKNOWN,
    score_multiplier=0.6  # null_penalty
)
```

**Warning:** "Cannot verify wheelchair_access - recommend calling home"

---

### Интеграция в Service Bands Score

**Метод:** `calculate_service_bands_score_v2()` из `matching-fallback-logic.py`

**Логика:**
1. Для каждого условия: проверка через `check_field_with_fallback()`
2. Отслеживание качества данных (direct, proxy, unknown)
3. Warnings при `unknown_ratio > 0.5`

---

### Критические различия: v1 vs. v2

#### v1 (текущая):
```python
if home.get('serves_dementia_band'):
    score += weight
else:
    score += 0  # ❌ NULL = 0 (неправильно!)
```

#### v2 (с fallback):
```python
result = check_field_with_fallback(home, 'serves_dementia_band', True)

if result.result == MatchResult.MATCH:
    score += weight * 1.0
elif result.result == MatchResult.PROXY_MATCH:
    score += weight * result.score_multiplier  # 0.7-0.9
elif result.result == MatchResult.UNKNOWN:
    score += weight * result.score_multiplier  # 0.5-0.7
```

---

## 📊 Обновленный план внедрения с Fallback логикой

### Этап 1: Создание констант + Proxy конфигурации

**Файлы:**
1. `services/matching_constants.py` (НОВЫЙ)
2. `services/matching_fallback_config.py` (НОВЫЙ) - `FIELD_PROXY_CONFIG`

**Оценка:** 2-3 часа

---

### Этап 2: Реализация Fallback функций

**Файл:** `services/matching_fallback.py` (НОВЫЙ)

**Функции:**
- `check_field_with_fallback()`
- `check_multiple_fields()`
- `check_care_types_v2()`

**Оценка:** 2-3 часа

---

### Этап 3: Service Bands Score с Fallback

**Метод:** `_calculate_service_bands_score_v2()`
- Использует fallback логику
- Отслеживает data quality
- Генерирует warnings

**Оценка:** 3-4 часа

---

### Этап 4: Обновление фильтрации с Fallback

**Метод:** `evaluate_home_match_v2()`
- Возвращает статус: `match`, `partial`, `uncertain`, `disqualified`
- Включает `data_completeness`

**Оценка:** 2-3 часа

---

## ⚠️ Критические моменты реализации

### 1. NULL vs. FALSE

**ВСЕГДА:**
```python
if value is True:  # Явно TRUE
elif value is False:  # Явно FALSE
else:  # None - использовать fallback
```

**НЕ использовать:**
```python
if home.get('field'):  # ❌ NULL будет False!
```

---

### 2. Data Quality Tracking

**Обязательно отслеживать:**
- Direct matches, proxy matches, unknowns
- Unknown ratio для warnings

---

**Дата анализа:** 2025-01-XX  
**Статус:** Готов к внедрению с учетом fallback логики


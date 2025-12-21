# План внедрения: Обновления логики матчинга из базы данных (с Fallback логикой)

**Источники:**
- `documents/report-algorithms/cursor-context-doc.md` (основной документ)
- `documents/report-algorithms/matching-fallback-logic.py` (fallback логика для NULL значений)

**Дата:** 2025-01-XX  
**Приоритет:** HIGH

---

## 🔄 КРИТИЧЕСКИ ВАЖНО: Fallback логика

**Проблема:** NULL ≠ FALSE  
**Решение:** Двухуровневая система (Direct → Proxy → Unknown) с confidence уровнями

---

## 📊 Текущее состояние vs. Требуемое

### ✅ Что уже реализовано

1. **Service User Bands - частично используется:**
   - ✅ `serves_dementia_band` используется в `_calculate_age_match()` (строка 356)
   - ✅ `serves_younger_adults`, `serves_older_people`, `serves_whole_population` используются в `_calculate_age_match()` (строки 498-509)
   - ❌ НЕ используется для матчинга медицинских условий (Q9)
   - ❌ НЕ используется для матчинга поведенческих проблем (Q16)

2. **CQC Ratings:**
   - ✅ Используется: `overall`, `safe`, `caring`, `effective`, `well_led`
   - ❌ НЕ используется: `cqc_rating_responsive`
   - ✅ `cqc_last_inspection_date` используется для Inspection Freshness (строка 709)

3. **Inspection Freshness:**
   - ✅ Уже реализовано в `_calculate_quality_care()` (15 points)

---

### ❌ Что нужно добавить/обновить

1. **Service User Bands для медицинских условий (Q9):**
   - ❌ Нет маппинга `dementia_alzheimers` → `serves_dementia_band`
   - ❌ Нет маппинга `parkinsons`, `stroke_recovery` → `serves_physical_disabilities`
   - ❌ Нет маппинга `visual_impairment`, `hearing_impairment` → `serves_sensory_impairments`
   - ❌ Нет маппинга `anxiety`, `depression` → `serves_mental_health`

2. **Service User Bands для поведенческих проблем (Q16):**
   - ❌ Нет маппинга `wandering_risk` → `serves_dementia_band` + `secure_garden`
   - ❌ Нет маппинга `aggression_risk` → `serves_mental_health`

3. **CQC Rating Responsive:**
   - ❌ Не используется в `_calculate_quality_care()`

4. **Mobility Level:**
   - ✅ `wheelchair_access` уже проверяется в `_calculate_medical_safety()` (Accessibility: 15 points)
   - ❌ Нет критической проверки для `bed_bound` → `has_nursing_care_license`

---

## 🎯 План внедрения

### Этап 1: Создание констант маппинга

**Файл:** `services/matching_constants.py` (НОВЫЙ)

**Задачи:**
1. Создать `CONDITION_TO_SERVICE_BAND` словарь
2. Создать `BEHAVIORAL_TO_SERVICE_BAND` словарь
3. Создать `MOBILITY_TO_FIELDS` словарь (расширить текущую логику)
4. Создать `WEIGHT_VALUES` словарь

**Оценка:** 1-2 часа

**Критичность:** HIGH

---

### Этап 2: Добавление Service Bands Score Component

**Файл:** `services/simple_matching_service.py`

**Задачи:**
1. Создать метод `_calculate_service_bands_score()`:
   - Проверка медицинских условий (Q9) → Service User Bands
   - Проверка поведенческих проблем (Q16) → Service User Bands
   - Взвешенный скоринг (critical, high, medium, low)
   - Fallback логика

2. Интегрировать в `_calculate_medical_safety()`:
   - Заменить часть Care Type Match на Service Bands Score
   - Обновить веса:
     - Service Bands: 35%
     - CQC Safe: 30%
     - Care Type: 20%
     - Accessibility: 15%

**Оценка:** 2-3 часа

**Критичность:** HIGH

---

### Этап 3: Обновление Quality Score

**Файл:** `services/simple_matching_service.py`

**Задачи:**
1. Обновить `_calculate_quality_care()`:
   - Добавить `cqc_rating_responsive` с весом 10%
   - Обновить веса всех рейтингов:
     - Overall: 25%
     - Safe: 25%
     - Caring: 20%
     - Effective: 15%
     - **Responsive: 10%** ← НОВОЕ
     - Well-led: 5%

2. Inspection Freshness уже реализован (15 points) - проверить корректность

**Оценка:** 1-2 часа

**Критичность:** HIGH

---

### Этап 4: Обновление фильтрации (критические требования)

**Файл:** `services/simple_matching_service.py` или `routers/report_routes.py`

**Задачи:**
1. Добавить проверку критических требований перед скорингом:
   - `wheelchair_user` → `wheelchair_access` (hard filter)
   - `bed_bound` → `has_nursing_care_license` (hard filter)
   - `dementia_alzheimers` → `serves_dementia_band` (soft penalty, но можно сделать hard filter)

2. Создать метод `_evaluate_critical_requirements()`:
   - Возвращает `(passed: bool, missing: List[str])`
   - Если `passed=False`, дом исключается из результатов

**Оценка:** 1-2 часа

**Критичность:** MEDIUM (можно сделать soft penalty вместо hard filter)

---

### Этап 5: Тестирование

**Задачи:**
1. Unit тесты для `_calculate_service_bands_score()`
2. Unit тесты для Quality Score с responsive
3. Integration тесты для полного flow
4. Проверка дифференциации scores (должна быть 30+ points spread)

**Оценка:** 2-3 часа

**Критичность:** MEDIUM

---

## 📝 Детальный план реализации

### Шаг 1.1: Создать `matching_constants.py`

```python
# services/matching_constants.py

# Q9: Medical Conditions → DB Service User Bands
CONDITION_TO_SERVICE_BAND = {
    'dementia_alzheimers': {
        'required_field': 'serves_dementia_band',
        'weight': 'critical',
        'fallback_fields': ['care_dementia']
    },
    'parkinsons': {
        'required_field': 'serves_physical_disabilities',
        'weight': 'high',
        'fallback_fields': []
    },
    # ... остальные условия
}

# Q16: Behavioral Concerns → DB Service User Bands
BEHAVIORAL_TO_SERVICE_BAND = {
    'wandering_risk': {
        'required_field': 'serves_dementia_band',
        'weight': 'critical',
        'amenity_required': 'secure_garden'
    },
    # ... остальные проблемы
}

# Weight values
WEIGHT_VALUES = {
    'critical': 1.0,
    'high': 0.8,
    'medium': 0.5,
    'low': 0.3,
    'none': 0.0
}
```

---

### Шаг 2.1: Создать `matching_fallback.py` (НОВЫЙ!)

**Файл:** `services/matching_fallback.py`

**Функции:**
1. `check_field_with_fallback()` - основная функция проверки с fallback
2. `check_multiple_fields()` - batch проверка
3. `check_care_types_v2()` - проверка care types с NULL handling

**Логика:**
- Level 1: Direct match (TRUE/FALSE)
- Level 2: Proxy match (NULL → proxy поле)
- Level 3: Unknown (все NULL)

---

### Шаг 2.2: Добавить `_calculate_service_bands_score_v2()` (с Fallback!)

**Место:** `services/simple_matching_service.py`, после `_calculate_equipment_match()`

**Логика:**
1. Извлечь `medical_conditions` и `behavioral_concerns`
2. Для каждого условия/проблемы:
   - Использовать `check_field_with_fallback()` вместо простой проверки
   - Применить `score_multiplier` из результата (confidence-based)
   - Отслеживать data quality (direct, proxy, unknown)
3. Рассчитать взвешенный score (0-100)
4. Генерировать warnings при `unknown_ratio > 0.5`

---

### Шаг 2.2: Интегрировать в `_calculate_medical_safety()`

**Текущая структура:**
```python
# Components:
# - Care Type Match: 30 points
# - CQC Safe Rating: 25 points
# - Accessibility: 15 points
# - Medication Match: 15 points
# - Equipment Match: 10 points
# - Age Match: 5 points
```

**Новая структура:**
```python
# Components:
# - Service Bands Score: 35 points (NEW!)
# - CQC Safe Rating: 30 points
# - Care Type Match: 20 points (reduced from 30)
# - Accessibility: 15 points
```

**Примечание:** Medication Match, Equipment Match, Age Match остаются, но их веса могут быть скорректированы.

---

### Шаг 3.1: Обновить `_calculate_quality_care()`

**Текущая структура:**
```python
# CQC Sub-ratings:
# - Overall: 25 points
# - Safe: 25 points
# - Caring: 20 points
# - Effective: 15 points
# - Well-Led: 15 points
```

**Новая структура:**
```python
# CQC Sub-ratings:
# - Overall: 25 points
# - Safe: 25 points
# - Caring: 20 points
# - Effective: 15 points
# - Responsive: 10 points (NEW!)
# - Well-Led: 5 points (reduced from 15)
```

---

### Шаг 4.1: Добавить проверку критических требований

**Место:** `routers/report_routes.py`, перед вызовом `calculate_100_point_match()`

**Логика:**
```python
def _check_critical_requirements(home: dict, questionnaire: dict) -> Tuple[bool, List[str]]:
    """
    Check if home meets critical requirements.
    Returns (passed, missing_requirements).
    """
    medical = questionnaire.get('section_3_medical_needs', {})
    mobility = medical.get('q10_mobility_level', '')
    
    missing = []
    
    # Critical: wheelchair_user requires wheelchair_access
    if mobility == 'wheelchair_user':
        if not home.get('wheelchair_access'):
            missing.append('wheelchair_access (required for wheelchair users)')
    
    # Critical: bed_bound requires nursing license
    if mobility == 'bed_bound':
        if not home.get('has_nursing_care_license'):
            missing.append('has_nursing_care_license (required for bed-bound patients)')
    
    return len(missing) == 0, missing
```

---

## 🔧 Технические детали

### Файлы для изменения

| Файл | Действие | Приоритет |
|------|----------|-----------|
| `services/matching_constants.py` | CREATE | HIGH |
| `services/simple_matching_service.py` | UPDATE | HIGH |
| `routers/report_routes.py` | UPDATE (опционально, для hard filter) | MEDIUM |
| `tests/test_simple_matching_service.py` | CREATE/UPDATE | MEDIUM |

### Обратная совместимость

- ✅ Все изменения обратно совместимы
- ✅ Если Service User Bands отсутствуют, используется fallback логика
- ✅ Если `cqc_rating_responsive` отсутствует, используется нейтральный score (50)

---

## ⚠️ Важные решения

### 1. Hard Filter vs. Soft Penalty

**Рекомендация:** Использовать **soft penalty** для большинства случаев, **hard filter** только для критических:
- ✅ Hard filter: `wheelchair_user` → `wheelchair_access`
- ✅ Hard filter: `bed_bound` → `has_nursing_care_license`
- ⚠️ Soft penalty: `dementia_alzheimers` → `serves_dementia_band` (может быть fallback на `care_dementia`)

### 2. Palliative Care

**Рекомендация:** Использовать proxy через `has_nursing_care_license` + `care_nursing`

### 3. Inspection Freshness

**Статус:** ✅ Уже реализовано (15 points)

---

## 📊 Ожидаемые результаты

### До изменений:
- Spread: 2-5 points
- Дифференциация: низкая
- Используется: ~20% полей БД

### После изменений:
- Spread: 30-44 points
- Дифференциация: высокая
- Используется: ~80% полей БД

---

## ✅ Чеклист внедрения

- [ ] Создать `services/matching_constants.py`
- [ ] Добавить `_calculate_service_bands_score()` в `simple_matching_service.py`
- [ ] Обновить `_calculate_medical_safety()` для использования Service Bands Score
- [ ] Обновить `_calculate_quality_care()` для использования `cqc_rating_responsive`
- [ ] Добавить проверку критических требований (опционально)
- [ ] Добавить unit тесты
- [ ] Проверить дифференциацию scores
- [ ] Обновить документацию

---

---

## 🔄 КРИТИЧЕСКИ ВАЖНО: Fallback логика для NULL значений

### Проблема: NULL ≠ FALSE

**Источник:** `matching-fallback-logic.py`

**НЕПРАВИЛЬНО:**
```python
if home.get('serves_dementia_band'):  # ❌ NULL = False!
    score += weight
```

**ПРАВИЛЬНО:**
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

### Дополнительные файлы для создания

1. **`services/matching_fallback_config.py`** (НОВЫЙ)
   - `MatchResult` enum
   - `FieldMatchResult` dataclass
   - `FIELD_PROXY_CONFIG` (proxy маппинги)

2. **`services/matching_fallback.py`** (НОВЫЙ)
   - `check_field_with_fallback()`
   - `check_multiple_fields()`
   - `check_care_types_v2()`

---

### Обновленная оценка времени

| Этап | Описание | Время |
|------|----------|-------|
| 1. Константы + Proxy config | Маппинги + fallback конфигурация | 2-3h |
| 2. Fallback функции | Реализация check_field_with_fallback() | 2-3h |
| 3. Service Bands Score v2 | С fallback и data quality tracking | 3-4h |
| 4. Фильтрация v2 | С fallback и статусами | 2-3h |
| 5. Quality Score | Responsive + freshness | 1-2h |
| 6. Medical & Safety | Интеграция Service Bands | 1-2h |
| 7. Тестирование | Unit + Integration тесты | 3-4h |
| **ИТОГО** | | **14-21 час** |

---

**Дата создания:** 2025-01-XX  
**Статус:** Готов к реализации с учетом fallback логики


# Обновление алгоритма матчинга для учета структуры БД

**Дата:** 2025-01-XX  
**Статус:** ✅ РЕАЛИЗОВАНО

---

## ✅ Выполненные изменения

### 1. Создан модуль `db_field_extractor.py` ✅

**Новый файл:** `services/db_field_extractor.py`

**Функции:**
- `get_service_user_band()` - извлекает Service User Band из плоских полей и JSONB
- `get_regulated_activity()` - извлекает Regulated Activity из плоских полей и JSONB
- `get_inspection_date()` - извлекает дату инспекции из плоских полей и enriched data
- `get_facility_value()` - извлекает значения из JSONB `facilities`
- `get_staff_information()` - извлекает информацию о персонале из JSONB `staff_information`
- `get_cqc_rating()` - извлекает CQC рейтинги из плоских полей и enriched data

**Логика:**
- **Level 1:** Проверяет плоские поля (например, `serves_dementia_band`)
- **Level 2:** Проверяет JSONB поля (например, `service_user_bands->bands`)
- **Level 3:** Возвращает `None` если данные отсутствуют

---

### 2. Обновлен `matching_fallback.py` ✅

**Изменения:**
- Добавлена поддержка JSONB полей в `check_field_with_fallback()`
- Теперь проверяет как плоские поля, так и JSONB структуры
- Использует `db_field_extractor` для извлечения данных

**Логика:**
```python
# 1. Проверяет плоское поле
primary_value = home.get(field_name)

# 2. Если NULL, проверяет JSONB
if primary_value is None:
    if field_name in service_band_mapping:
        primary_value = get_service_user_band(home, band_name)
    elif field_name in regulated_activity_mapping:
        primary_value = get_regulated_activity(home, activity_id)
```

---

### 3. Обновлен `simple_matching_service.py` ✅

#### 3.1. Service User Bands ✅

**Обновлено:**
- `_calculate_age_match()` - использует `get_service_user_band()` для проверки `serves_younger_adults`, `serves_older_people`, `serves_whole_population`
- `_calculate_service_bands_score_v2()` - уже использует `check_field_with_fallback()`, который теперь поддерживает JSONB

**Результат:** Алгоритм теперь проверяет как плоские поля, так и JSONB `service_user_bands`.

---

#### 3.2. Regulated Activities (Licenses) ✅

**Обновлено:**
- `_calculate_medication_match()` - использует `get_regulated_activity()` для проверки `has_nursing_care_license`
- `_calculate_equipment_match()` - использует `get_regulated_activity()` для проверки `has_nursing_care_license`

**Результат:** Алгоритм теперь проверяет как плоские поля, так и JSONB `regulated_activities`.

---

#### 3.3. CQC Ratings ✅

**Обновлено:**
- `_calculate_quality_care()` - использует `get_cqc_rating()` для всех 6 рейтингов:
  - `overall` ✅
  - `safe` ✅
  - `caring` ✅
  - `effective` ✅
  - `responsive` ✅ (уже использовался, теперь через extractor)
  - `well_led` ✅

**Результат:** Алгоритм теперь использует все 6 CQC рейтингов из плоских полей и enriched data.

---

#### 3.4. Inspection Date ✅

**Обновлено:**
- `_calculate_quality_care()` - использует `get_inspection_date()` для проверки `cqc_last_inspection_date`
- `_calculate_data_quality_factor()` - обновлен для использования `cqc_last_inspection_date`

**Результат:** Алгоритм теперь использует правильное поле БД `cqc_last_inspection_date` для freshness scoring.

---

## 📊 Поддерживаемые поля БД

### Плоские поля (используются напрямую)

#### Service User Bands (12 полей)
- ✅ `serves_dementia_band`
- ✅ `serves_older_people`
- ✅ `serves_younger_adults`
- ✅ `serves_mental_health`
- ✅ `serves_physical_disabilities`
- ✅ `serves_sensory_impairments`
- ✅ `serves_learning_disabilities`
- ✅ `serves_children`
- ✅ `serves_detained_mha`
- ✅ `serves_substance_misuse`
- ✅ `serves_eating_disorders`
- ✅ `serves_whole_population`

#### Licenses (5 полей)
- ✅ `has_nursing_care_license`
- ✅ `has_personal_care_license`
- ✅ `has_surgical_procedures_license`
- ✅ `has_treatment_license`
- ✅ `has_diagnostic_license`

#### CQC Ratings (6 полей)
- ✅ `cqc_rating_overall`
- ✅ `cqc_rating_safe`
- ✅ `cqc_rating_caring`
- ✅ `cqc_rating_effective`
- ✅ `cqc_rating_responsive`
- ✅ `cqc_rating_well_led`

#### Inspection Date (1 поле)
- ✅ `cqc_last_inspection_date`

---

### JSONB поля (используются через extractor)

#### Service User Bands
- ✅ `service_user_bands` → `{"bands": ["Older People", "Mental Health", ...]}`

#### Regulated Activities
- ✅ `regulated_activities` → `{"activities": [{"id": "nursing_care", "active": true}, ...]}`

#### Facilities (для будущего использования)
- ✅ `facilities` → `{"medical_equipment": [...], "on_site_pharmacy": true, ...}`

#### Staff Information (для будущего использования)
- ✅ `staff_information` → `{"staff_ratio": 1.5, "staff_retention_rate": 85.5, ...}`

---

## 🔄 Логика работы

### Пример: Service User Band

**До обновления:**
```python
serves_dementia = home.get('serves_dementia_band', False)
# Проблема: если поле NULL в CSV, всегда возвращает False
```

**После обновления:**
```python
serves_dementia = get_service_user_band(home, 'dementia_band')
# 1. Проверяет плоское поле: home.get('serves_dementia_band')
# 2. Если NULL, проверяет JSONB: service_user_bands->bands
# 3. Возвращает True/False/None (None = unknown, не FALSE)
```

---

### Пример: Regulated Activity

**До обновления:**
```python
has_nursing = home.get('has_nursing_care_license', False)
# Проблема: если поле NULL в CSV, всегда возвращает False
```

**После обновления:**
```python
has_nursing = get_regulated_activity(home, 'nursing_care')
# 1. Проверяет плоское поле: home.get('has_nursing_care_license')
# 2. Если NULL, проверяет JSONB: regulated_activities->activities
# 3. Возвращает True/False/None (None = unknown, не FALSE)
```

---

### Пример: CQC Rating

**До обновления:**
```python
overall = (
    cqc_data.get('overall_rating') or
    home.get('cqc_rating_overall')
)
# Проблема: не проверяет все возможные источники
```

**После обновления:**
```python
overall = get_cqc_rating(home, 'overall', enriched_data) or (
    cqc_data.get('overall_rating') or
    home.get('cqc_rating_overall')
)
# Проверяет все источники: flat field, enriched data, detailed_ratings
```

---

## 📋 Обновленные методы

### `_calculate_medical_safety()`
- ✅ Использует `get_service_user_band()` для age matching
- ✅ Использует `get_regulated_activity()` для medication matching
- ✅ Использует `get_regulated_activity()` для equipment matching
- ✅ Использует `get_cqc_rating()` для safe rating
- ✅ Использует `get_service_user_band()` для dementia care type matching

### `_calculate_quality_care()`
- ✅ Использует `get_cqc_rating()` для всех 6 рейтингов
- ✅ Использует `get_inspection_date()` для freshness scoring

### `_calculate_data_quality_factor()`
- ✅ Использует `cqc_last_inspection_date` (правильное поле БД)
- ✅ Проверяет все 6 CQC рейтингов (включая responsive)

### `_calculate_medication_match()`
- ✅ Использует `get_regulated_activity()` для проверки nursing license

### `_calculate_equipment_match()`
- ✅ Использует `get_regulated_activity()` для проверки nursing license

### `_calculate_age_match()`
- ✅ Использует `get_service_user_band()` для проверки age bands

---

## 🎯 Преимущества обновления

### 1. Использование всех данных БД ✅

**До:**
- Использовались только плоские поля
- JSONB поля игнорировались
- Если плоское поле NULL, считалось FALSE

**После:**
- Используются и плоские поля, и JSONB
- Если плоское поле NULL, проверяется JSONB
- NULL ≠ FALSE (правильная обработка)

---

### 2. Правильная обработка NULL ✅

**До:**
```python
serves_dementia = home.get('serves_dementia_band', False)
# NULL → False (неправильно!)
```

**После:**
```python
serves_dementia = get_service_user_band(home, 'dementia_band')
# NULL → None (правильно! unknown, не FALSE)
# Затем используется fallback логика
```

---

### 3. Поддержка всех 12 Service User Bands ✅

**До:**
- Использовались только 8 полей
- 4 дополнительных поля игнорировались

**После:**
- Используются все 12 полей
- Поддержка через JSONB для всех полей

---

### 4. Поддержка всех 14 Regulated Activities ✅

**До:**
- Использовались только 5 плоских полей
- Остальные 9 activities игнорировались

**После:**
- Используются все 14 activities через JSONB
- Поддержка через `regulated_activities` JSONB

---

### 5. Использование правильных полей БД ✅

**До:**
- `last_inspection_date` (неправильное поле)
- Не все CQC рейтинги использовались

**После:**
- `cqc_last_inspection_date` (правильное поле БД)
- Все 6 CQC рейтингов используются

---

## 📊 Итоговая таблица использования полей

| Категория | Поля БД | Использование | Статус |
|-----------|---------|---------------|--------|
| **Service User Bands** | 12 плоских + JSONB | ✅ Через `get_service_user_band()` | ✅ Полное |
| **Licenses** | 5 плоских + JSONB | ✅ Через `get_regulated_activity()` | ✅ Полное |
| **CQC Ratings** | 6 плоских | ✅ Через `get_cqc_rating()` | ✅ Полное |
| **Inspection Date** | 1 плоское | ✅ Через `get_inspection_date()` | ✅ Полное |
| **Facilities** | JSONB | ✅ Через `get_facility_value()` | ✅ Готово |
| **Staff Information** | JSONB | ✅ Через `get_staff_information()` | ✅ Готово |

---

## ✅ Проверка

Все функции успешно реализованы:
- ✅ `db_field_extractor.py` создан и работает
- ✅ `matching_fallback.py` обновлен для поддержки JSONB
- ✅ `simple_matching_service.py` обновлен для использования extractor функций
- ✅ Все импорты работают
- ✅ Нет ошибок линтера

---

## 🎯 Результат

**Алгоритм матчинга теперь:**
1. ✅ Использует все плоские поля из БД
2. ✅ Использует JSONB поля как fallback
3. ✅ Правильно обрабатывает NULL (NULL ≠ FALSE)
4. ✅ Использует все 12 Service User Bands
5. ✅ Использует все 14 Regulated Activities
6. ✅ Использует все 6 CQC рейтингов
7. ✅ Использует правильное поле для inspection date

**Готово к использованию реальных данных из БД!**

---

**Статус:** ✅ РЕАЛИЗОВАНО


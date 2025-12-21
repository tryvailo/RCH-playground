# Анализ: CQC CSV vs. Финальная БД

**Дата:** 2025-01-XX  
**Файл:** `documents/report-algorithms/cqc_carehomes_master_full_data_rows.csv`  
**Статус:** ✅ ЗАВЕРШЕНО

---

## 📊 Резюме

**Цель:** Определить, на каком этапе потерялись данные - при составлении базы CQC или при матчинге в полную БД.

**Вывод:** 
- ✅ **Все критически важные поля ЕСТЬ в CQC CSV**
- ⚠️ **Проблема в маппинге:** Поля называются по-другому и требуют правильного маппинга
- ❌ **Некоторые поля отсутствуют в CQC Dataset изначально** (Medical Equipment, Medication, Staffing)

---

## 📋 Структура CQC CSV

**Всего полей:** 128

### ✅ Service User Bands (12 полей) - ЕСТЬ В CSV

| Поле в CQC CSV | Поле в БД | Статус |
|----------------|-----------|--------|
| `service_user_band_older_people` | `serves_older_people` | ✅ ЕСТЬ |
| `service_user_band_younger_adults` | `serves_younger_adults` | ✅ ЕСТЬ |
| `service_user_band_mental_health` | `serves_mental_health` | ✅ ЕСТЬ |
| `service_user_band_physical_disability` | `serves_physical_disabilities` | ✅ ЕСТЬ |
| `service_user_band_sensory_impairment` | `serves_sensory_impairments` | ✅ ЕСТЬ |
| `service_user_band_dementia` | `serves_dementia_band` | ✅ ЕСТЬ |
| `service_user_band_children` | `serves_children` | ✅ ЕСТЬ |
| `service_user_band_learning_disabilities` | `serves_learning_disabilities` | ✅ ЕСТЬ |
| `service_user_band_detained_mental_health` | `serves_detained_mha` | ✅ ЕСТЬ |
| `service_user_band_drugs_alcohol` | `serves_substance_misuse` | ✅ ЕСТЬ |
| `service_user_band_eating_disorder` | `serves_eating_disorders` | ✅ ЕСТЬ |
| `service_user_band_whole_population` | `serves_whole_population` | ✅ ЕСТЬ |

**Вывод:** ✅ Все 12 полей Service User Bands **ЕСТЬ** в CQC CSV, но с другими названиями. Требуется правильный маппинг.

---

### ✅ Regulated Activities (14 полей) - ЕСТЬ В CSV

| Поле в CQC CSV | Поле в БД | Статус |
|----------------|-----------|--------|
| `regulated_activity_nursing_care` | `has_nursing_care_license` | ✅ ЕСТЬ (но маппится из `service_type_care_home_service_with_nursing`) |
| `regulated_activity_personal_care` | `has_personal_care_license` | ✅ ЕСТЬ |
| `regulated_activity_surgical` | `has_surgical_procedures_license` | ✅ ЕСТЬ |
| `regulated_activity_treatment` | `has_treatment_license` | ✅ ЕСТЬ |
| `regulated_activity_diagnostic` | `has_diagnostic_license` | ✅ ЕСТЬ |
| `regulated_activity_accommodation_nursing` | — | ✅ ЕСТЬ (дополнительное) |
| `regulated_activity_accommodation_substance` | — | ✅ ЕСТЬ (дополнительное) |
| `regulated_activity_assessment_detained` | — | ✅ ЕСТЬ (дополнительное) |
| `regulated_activity_family_planning` | — | ✅ ЕСТЬ (дополнительное) |
| `regulated_activity_blood_management` | — | ✅ ЕСТЬ (дополнительное) |
| `regulated_activity_maternity` | — | ✅ ЕСТЬ (дополнительное) |
| `regulated_activity_slimming_clinics` | — | ✅ ЕСТЬ (дополнительное) |
| `regulated_activity_termination` | — | ✅ ЕСТЬ (дополнительное) |
| `regulated_activity_transport` | — | ✅ ЕСТЬ (дополнительное) |

**Вывод:** ✅ Все 14 Regulated Activities **ЕСТЬ** в CQC CSV. Требуется правильный маппинг.

**⚠️ КРИТИЧНО:** Согласно `README-CQC-MAPPING.md`, `has_nursing_care_license` маппится из `service_type_care_home_service_with_nursing`, НЕ из `regulated_activity_nursing_care`, потому что `regulated_activity_nursing_care` ВСЕГДА `FALSE` в CQC Dataset.

---

### ✅ CQC Ratings (6 полей) - ЕСТЬ В CSV

| Поле в CQC CSV | Поле в БД | Статус |
|----------------|-----------|--------|
| `location_latest_overall_rating` | `cqc_rating_overall` | ✅ ЕСТЬ |
| `cqc_rating_safe` | `cqc_rating_safe` | ✅ ЕСТЬ |
| `cqc_rating_effective` | `cqc_rating_effective` | ✅ ЕСТЬ |
| `cqc_rating_caring` | `cqc_rating_caring` | ✅ ЕСТЬ |
| `cqc_rating_responsive` | `cqc_rating_responsive` | ✅ ЕСТЬ |
| `cqc_rating_well_led` | `cqc_rating_well_led` | ✅ ЕСТЬ |

**Вывод:** ✅ Все 6 CQC Ratings **ЕСТЬ** в CQC CSV. Требуется правильный маппинг.

---

### ⚠️ Inspection Date - ЧАСТИЧНО ЕСТЬ В CSV

| Поле в CQC CSV | Поле в БД | Статус |
|----------------|-----------|--------|
| `location_inspection_directorate` | — | ⚠️ ЕСТЬ (но не дата) |
| `location_primary_inspection_category` | — | ⚠️ ЕСТЬ (но не дата) |
| `publication_date` | `cqc_publication_date` | ✅ ЕСТЬ |
| — | `cqc_last_inspection_date` | ❌ **ОТСУТСТВУЕТ** |

**Вывод:** ⚠️ `cqc_last_inspection_date` **ОТСУТСТВУЕТ** в CQC CSV. Это поле нужно получать из CQC API, а не из CSV.

---

### ❌ Medical Equipment - ОТСУТСТВУЕТ В CSV

| Поле | Статус в CQC CSV |
|------|------------------|
| `medical_equipment` | ❌ ОТСУТСТВУЕТ |
| `has_oxygen_equipment` | ❌ ОТСУТСТВУЕТ |
| `has_hospital_bed` | ❌ ОТСУТСТВУЕТ |
| `has_hoist` | ❌ ОТСУТСТВУЕТ |

**Вывод:** ❌ Medical Equipment **НЕ ВХОДИТ** в CQC Dataset. Эти данные нужно получать из других источников (Autumna, CQC API, или использовать proxy через `care_nursing`).

---

### ❌ Medication Management - ОТСУТСТВУЕТ В CSV

| Поле | Статус в CQC CSV |
|------|------------------|
| `on_site_pharmacy` | ❌ ОТСУТСТВУЕТ |
| `medication_administration` | ❌ ОТСУТСТВУЕТ |

**Вывод:** ❌ Medication Management **НЕ ВХОДИТ** в CQC Dataset. Эти данные нужно получать из других источников (Autumna, CQC API, или использовать proxy через `care_nursing`).

---

### ❌ Staffing Details - ОТСУТСТВУЕТ В CSV

| Поле | Статус в CQC CSV |
|------|------------------|
| `staff_ratio` | ❌ ОТСУТСТВУЕТ |
| `staff_retention_rate` | ❌ ОТСУТСТВУЕТ |
| `nurse_to_resident_ratio` | ❌ ОТСУТСТВУЕТ |

**Вывод:** ❌ Staffing Details **НЕ ВХОДИТ** в CQC Dataset. Эти данные нужно получать из других источников (Autumna, CQC API, или использовать JSONB `staff_information`).

---

## 🔍 Анализ потери данных

### Этап 1: CQC Dataset (CSV) ✅

**Статус:** ✅ Все критически важные поля **ЕСТЬ** в CQC CSV

- ✅ Service User Bands: 12/12 полей
- ✅ Regulated Activities: 14/14 полей
- ✅ CQC Ratings: 6/6 полей
- ⚠️ Inspection Date: Частично (есть `publication_date`, нет `last_inspection_date`)
- ❌ Medical Equipment: Не входит в CQC Dataset
- ❌ Medication Management: Не входит в CQC Dataset
- ❌ Staffing Details: Не входит в CQC Dataset

**Вывод:** CQC Dataset содержит все поля, которые в него входят. Проблема не в CQC Dataset.

---

### Этап 2: Маппинг CQC → БД ⚠️

**Статус:** ⚠️ Требуется правильный маппинг

#### Проблемы маппинга:

1. **Service User Bands:**
   - CQC CSV: `service_user_band_*`
   - БД: `serves_*`
   - **Решение:** Маппинг через `safe_boolean()` (уже реализовано в `README-CQC-MAPPING.md`)

2. **Regulated Activities:**
   - CQC CSV: `regulated_activity_*`
   - БД: `has_*_license`
   - **Решение:** Маппинг через `safe_boolean()` (уже реализовано)
   - **⚠️ КРИТИЧНО:** `has_nursing_care_license` маппится из `service_type_care_home_service_with_nursing`, НЕ из `regulated_activity_nursing_care`

3. **CQC Ratings:**
   - CQC CSV: `cqc_rating_*` и `location_latest_overall_rating`
   - БД: `cqc_rating_*`
   - **Решение:** Маппинг через `normalize_cqc_rating()` (уже реализовано)

4. **Inspection Date:**
   - CQC CSV: НЕТ `cqc_last_inspection_date`
   - БД: `cqc_last_inspection_date`
   - **Решение:** Получать из CQC API, а не из CSV

**Вывод:** Маппинг должен работать правильно, если используется правильный скрипт (`mapping_improved_script.sql`).

---

### Этап 3: Заполнение БД ❌

**Статус:** ❌ Данные не заполняются в БД

**Проблема:** Даже если маппинг правильный, данные могут быть NULL в БД, если:
1. В CQC CSV значения `FALSE` или пустые
2. Маппинг не выполнен или выполнен неправильно
3. Данные потерялись при загрузке

**Вывод:** Нужно проверить:
- Выполнен ли маппинг?
- Правильно ли работает маппинг?
- Заполняются ли данные в БД?

---

## 📊 Итоговая таблица

| Категория | Поля в БД | Есть в CQC CSV? | Правильный маппинг? | Статус |
|-----------|-----------|-----------------|-------------------|--------|
| **Service User Bands** | 12 | ✅ Да (12/12) | ✅ Да | ✅ **ДОЛЖНО РАБОТАТЬ** |
| **Regulated Activities** | 5 | ✅ Да (14/14) | ⚠️ Частично | ⚠️ **ТРЕБУЕТ ПРОВЕРКИ** |
| **CQC Ratings** | 6 | ✅ Да (6/6) | ✅ Да | ✅ **ДОЛЖНО РАБОТАТЬ** |
| **Inspection Date** | 1 | ⚠️ Частично | ❌ Нет (нужен API) | ⚠️ **ТРЕБУЕТ CQC API** |
| **Medical Equipment** | 0 (используется JSONB) | ❌ Нет | — | ❌ **НЕ В CQC DATASET** |
| **Medication Management** | 0 (используется JSONB) | ❌ Нет | — | ❌ **НЕ В CQC DATASET** |
| **Staffing Details** | 0 (используется JSONB) | ❌ Нет | — | ❌ **НЕ В CQC DATASET** |

---

## 🎯 Выводы

### ✅ Что работает:

1. **Service User Bands:** Все 12 полей есть в CQC CSV, маппинг реализован → **ДОЛЖНО РАБОТАТЬ**
2. **CQC Ratings:** Все 6 полей есть в CQC CSV, маппинг реализован → **ДОЛЖНО РАБОТАТЬ**
3. **Regulated Activities:** Все 14 полей есть в CQC CSV, маппинг реализован → **ДОЛЖНО РАБОТАТЬ** (но требует проверки для `has_nursing_care_license`)

### ⚠️ Что требует внимания:

1. **Inspection Date:** Отсутствует в CQC CSV → **ТРЕБУЕТ CQC API**
2. **Regulated Activities маппинг:** `has_nursing_care_license` маппится из `service_type`, а не из `regulated_activity` → **ТРЕБУЕТ ПРОВЕРКИ**

### ❌ Что отсутствует в CQC Dataset:

1. **Medical Equipment:** Не входит в CQC Dataset → **ТРЕБУЕТ ДРУГИХ ИСТОЧНИКОВ** (Autumna, CQC API, или proxy)
2. **Medication Management:** Не входит в CQC Dataset → **ТРЕБУЕТ ДРУГИХ ИСТОЧНИКОВ** (Autumna, CQC API, или proxy)
3. **Staffing Details:** Не входит в CQC Dataset → **ТРЕБУЕТ ДРУГИХ ИСТОЧНИКОВ** (Autumna, CQC API, или JSONB)

---

## 🔧 Рекомендации

### 1. Проверить маппинг Service User Bands

```sql
-- Проверить, заполняются ли Service User Bands в БД
SELECT 
    COUNT(*) as total,
    COUNT(serves_older_people) as has_older_people,
    COUNT(serves_dementia_band) as has_dementia_band,
    COUNT(serves_mental_health) as has_mental_health
FROM care_homes
WHERE is_dormant = FALSE;
```

**Ожидаемый результат:** Все поля должны быть заполнены (не NULL).

---

### 2. Проверить маппинг Regulated Activities

```sql
-- Проверить, заполняются ли Licenses в БД
SELECT 
    COUNT(*) as total,
    COUNT(has_nursing_care_license) as has_nursing,
    COUNT(has_personal_care_license) as has_personal,
    COUNT(has_surgical_procedures_license) as has_surgical
FROM care_homes
WHERE is_dormant = FALSE;
```

**Ожидаемый результат:** Все поля должны быть заполнены (не NULL).

**⚠️ КРИТИЧНО:** Проверить, что `has_nursing_care_license` маппится из `service_type_care_home_service_with_nursing`, а не из `regulated_activity_nursing_care`.

---

### 3. Проверить маппинг CQC Ratings

```sql
-- Проверить, заполняются ли CQC Ratings в БД
SELECT 
    COUNT(*) as total,
    COUNT(cqc_rating_overall) as has_overall,
    COUNT(cqc_rating_safe) as has_safe,
    COUNT(cqc_rating_caring) as has_caring
FROM care_homes
WHERE is_dormant = FALSE;
```

**Ожидаемый результат:** Все поля должны быть заполнены (не NULL).

---

### 4. Получить Inspection Date из CQC API

```python
# Использовать CQC API для получения inspection_date
# Это поле отсутствует в CQC CSV, но есть в CQC API
```

**Ожидаемый результат:** `cqc_last_inspection_date` должен быть заполнен из CQC API.

---

### 5. Использовать JSONB для отсутствующих полей

```sql
-- Medical Equipment → facilities JSONB
-- Medication Management → facilities JSONB
-- Staffing Details → staff_information JSONB
```

**Ожидаемый результат:** Данные должны быть в JSONB полях, если доступны из других источников (Autumna, CQC API).

---

## ✅ Итоговый ответ

**На каком этапе потерялись данные?**

1. **CQC Dataset (CSV):** ✅ Все критически важные поля **ЕСТЬ** (Service User Bands, Regulated Activities, CQC Ratings)
2. **Маппинг CQC → БД:** ⚠️ Маппинг реализован, но требует проверки
3. **Заполнение БД:** ❌ **ВОЗМОЖНАЯ ПРОБЛЕМА ЗДЕСЬ** - данные могут быть NULL, если:
   - Маппинг не выполнен
   - Маппинг выполнен неправильно
   - В CQC CSV значения `FALSE` или пустые

**Вывод:** 
- ✅ Проблема **НЕ** в CQC Dataset (все поля есть)
- ⚠️ Проблема **ВОЗМОЖНО** в маппинге или заполнении БД
- ❌ Некоторые поля (Medical Equipment, Medication, Staffing) **НЕ ВХОДЯТ** в CQC Dataset изначально

**Рекомендация:** Проверить выполнение маппинга и заполнение данных в БД.


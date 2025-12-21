# Анализ недостающих полей в базе данных

**Дата:** 2025-01-XX  
**Статус:** ✅ АНАЛИЗ ЗАВЕРШЕН

---

## 📊 Критические поля - полностью отсутствуют (100% NULL)

### ⚠️ ВАЖНО: Эти поля ЕСТЬ в структуре БД, но не заполнены в CSV!

**См. детальный анализ:** `DB_STRUCTURE_ANALYSIS.md`

### 1. Service User Bands (100% NULL в CSV) ⚠️ КРИТИЧНО

**Статус в БД:** ✅ **ЕСТЬ** (12 плоских полей + JSONB `service_user_bands`)

| Поле | Статус в БД | Статус в CSV | Proxy Available | Источник данных |
|------|-------------|--------------|-----------------|-----------------|
| `serves_dementia_band` | ✅ ЕСТЬ (BOOLEAN) | ❌ 100% NULL | ✅ `care_dementia` (0.9), `care_nursing` (0.5) | CQC API: `serviceUserBands` |
| `serves_older_people` | ✅ ЕСТЬ (BOOLEAN) | ❌ 100% NULL | ✅ `serves_whole_population` (0.4), `care_dementia` (0.5) | CQC API: `serviceUserBands` |
| `serves_mental_health` | ✅ ЕСТЬ (BOOLEAN) | ❌ 100% NULL | ✅ `care_nursing` (0.6), `serves_whole_population` (0.4) | CQC API: `serviceUserBands` |
| `serves_physical_disabilities` | ✅ ЕСТЬ (BOOLEAN) | ❌ 100% NULL | ✅ `wheelchair_access` (0.8), `care_nursing` (0.6) | CQC API: `serviceUserBands` |
| `serves_sensory_impairments` | ✅ ЕСТЬ (BOOLEAN) | ❌ 100% NULL | ✅ `serves_older_people` (0.6), `serves_physical_disabilities` (0.5) | CQC API: `serviceUserBands` |
| `serves_learning_disabilities` | ✅ ЕСТЬ (BOOLEAN) | ❌ 100% NULL | ✅ `serves_younger_adults` (0.5) | CQC API: `serviceUserBands` |
| `serves_younger_adults` | ✅ ЕСТЬ (BOOLEAN) | ❌ 100% NULL | ❌ Нет proxy | CQC API: `serviceUserBands` |
| `serves_whole_population` | ✅ ЕСТЬ (BOOLEAN) | ❌ 100% NULL | ❌ Нет proxy | CQC API: `serviceUserBands` |
| `service_user_bands` | ✅ ЕСТЬ (JSONB) | ❌ Пусто | - | CQC API: `serviceUserBands` |

**Решение:** Использовать CQC API для получения `serviceUserBands` данных и заполнения существующих полей в БД.

**CQC API Endpoint:**
```
GET /locations/{locationId}
Response includes: "serviceUserBands": ["Older people", "People with dementia", ...]
```

---

### 2. Licenses (100% NULL в CSV) ⚠️

**Статус в БД:** ✅ **ЕСТЬ** (5 плоских полей + JSONB `regulated_activities`)

| Поле | Статус в БД | Статус в CSV | Proxy Available | Источник данных |
|------|-------------|--------------|-----------------|-----------------|
| `has_nursing_care_license` | ✅ ЕСТЬ (BOOLEAN) | ❌ 100% NULL | ✅ `care_nursing` (0.95) | CQC API: `regulatedActivities` |
| `has_personal_care_license` | ✅ ЕСТЬ (BOOLEAN) | ❌ 100% NULL | ✅ `care_residential` (0.9) | CQC API: `regulatedActivities` |
| `regulated_activities` | ✅ ЕСТЬ (JSONB) | ❌ Пусто | - | CQC API: `regulatedActivities` (14 activities) |

**Решение:** Использовать CQC API для получения `regulatedActivities` данных и заполнения существующих полей в БД.

**CQC API Endpoint:**
```
GET /locations/{locationId}
Response includes: "regulatedActivities": [
  {"name": "Personal care", "code": "RA1"},
  {"name": "Nursing care", "code": "RA2"},
  ...
]
```

---

### 3. Inspection Date (100% NULL в CSV) ⚠️

**Статус в БД:** ✅ **ЕСТЬ** (поле `cqc_last_inspection_date`)

| Поле | Статус в БД | Статус в CSV | Источник данных |
|------|-------------|--------------|-----------------|
| `cqc_last_inspection_date` | ✅ ЕСТЬ (DATE) | ❌ 100% NULL | CQC API: `inspectionDate` |

**Решение:** Использовать CQC API для получения `inspectionDate` и заполнения существующего поля в БД.

**CQC API Endpoint:**
```
GET /locations/{locationId}
Response includes: "inspectionDate": "2024-01-15"
```

---

## 📊 Частично отсутствующие поля

### 1. CQC Ratings (6-8% NULL) ✅ ХОРОШО

| Поле | NULL Rate | Coverage | Источник данных |
|------|-----------|----------|-----------------|
| `cqc_rating_overall` | 8.7% | 91.3% | CQC API: `overallRating` |
| `cqc_rating_safe` | 8.6% | 91.4% | CQC API: `ratings.safe` |
| `cqc_rating_caring` | 6.0% | 94.0% | CQC API: `ratings.caring` |
| `cqc_rating_effective` | 6.0% | 94.0% | CQC API: `ratings.effective` |
| `cqc_rating_responsive` | 6.0% | 94.0% | CQC API: `ratings.responsive` |
| `cqc_rating_well_led` | 6.0% | 94.0% | CQC API: `ratings.wellLed` |

**Рекомендация:** Использовать CQC API для обновления отсутствующих рейтингов (6-8% домов).

---

## 🔍 Поля, которые нельзя найти в доступных источниках

### 1. Medical Equipment ❌

| Поле | Статус | Источник данных | Решение |
|------|--------|-----------------|---------|
| `medical_equipment` | ❌ Отсутствует | ❌ Нет в CQC API | ✅ Используем `care_nursing` как proxy |
| `has_oxygen_equipment` | ❌ Отсутствует | ❌ Нет в CQC API | ✅ Используем `care_nursing` как proxy |
| `has_hospital_bed` | ❌ Отсутствует | ❌ Нет в CQC API | ✅ Используем `care_nursing` как proxy |
| `has_hoist` | ❌ Отсутствует | ❌ Нет в CQC API | ✅ Используем `care_nursing` как proxy |

**Текущее решение:** Используем `care_nursing` как proxy для сложного медицинского оборудования.

**Рекомендация:** Запрашивать напрямую у дома престарелых при посещении.

---

### 2. Medication Management ❌

| Поле | Статус | Источник данных | Решение |
|------|--------|-----------------|---------|
| `on_site_pharmacy` | ❌ Отсутствует | ❌ Нет в CQC API | ✅ Используем `care_nursing` как proxy |
| `medication_administration` | ❌ Отсутствует | ❌ Нет в CQC API | ✅ Используем `care_nursing` как proxy |

**Текущее решение:** Используем `care_nursing` как proxy для сложного управления медикаментами.

**Рекомендация:** Запрашивать напрямую у дома престарелых при посещении.

---

### 3. Staffing Details ❌

| Поле | Статус | Источник данных | Решение |
|------|--------|-----------------|---------|
| `staff_ratio` | ❌ Отсутствует | ❌ Нет в CQC API | ✅ Используем Staff Quality API (Perplexity) |
| `staff_retention_rate` | ❌ Отсутствует | ❌ Нет в CQC API | ✅ Используем Staff Quality API (Perplexity) |
| `nurse_to_resident_ratio` | ❌ Отсутствует | ❌ Нет в CQC API | ✅ Используем Staff Quality API (Perplexity) |

**Текущее решение:** Используем Staff Quality API (Perplexity) для анализа отзывов и веб-сайтов.

**Рекомендация:** Запрашивать напрямую у дома престарелых при посещении.

---

## 📋 Итоговый список недостающих полей

### ⚠️ ВАЖНО: Большинство полей ЕСТЬ в структуре БД, но не заполнены в CSV!

**См. детальный анализ:** `DB_STRUCTURE_ANALYSIS.md`

### Критические (можно получить из CQC API) - ЕСТЬ в БД, нужно заполнить

1. ✅ **Service User Bands** (12 полей + JSONB) - **ЕСТЬ в БД**
   - `serves_dementia_band` ✅ ЕСТЬ (BOOLEAN)
   - `serves_older_people` ✅ ЕСТЬ (BOOLEAN)
   - `serves_mental_health` ✅ ЕСТЬ (BOOLEAN)
   - `serves_physical_disabilities` ✅ ЕСТЬ (BOOLEAN)
   - `serves_sensory_impairments` ✅ ЕСТЬ (BOOLEAN)
   - `serves_learning_disabilities` ✅ ЕСТЬ (BOOLEAN)
   - `serves_younger_adults` ✅ ЕСТЬ (BOOLEAN)
   - `serves_whole_population` ✅ ЕСТЬ (BOOLEAN)
   - `serves_children` ✅ ЕСТЬ (BOOLEAN) - дополнительно
   - `serves_detained_mha` ✅ ЕСТЬ (BOOLEAN) - дополнительно
   - `serves_substance_misuse` ✅ ЕСТЬ (BOOLEAN) - дополнительно
   - `serves_eating_disorders` ✅ ЕСТЬ (BOOLEAN) - дополнительно
   - `service_user_bands` ✅ ЕСТЬ (JSONB)

2. ✅ **Licenses** (5 полей + JSONB) - **ЕСТЬ в БД**
   - `has_nursing_care_license` ✅ ЕСТЬ (BOOLEAN)
   - `has_personal_care_license` ✅ ЕСТЬ (BOOLEAN)
   - `has_surgical_procedures_license` ✅ ЕСТЬ (BOOLEAN) - дополнительно
   - `has_treatment_license` ✅ ЕСТЬ (BOOLEAN) - дополнительно
   - `has_diagnostic_license` ✅ ЕСТЬ (BOOLEAN) - дополнительно
   - `regulated_activities` ✅ ЕСТЬ (JSONB) - все 14 activities

3. ✅ **Inspection Date** (1 поле) - **ЕСТЬ в БД**
   - `cqc_last_inspection_date` ✅ ЕСТЬ (DATE)

**Итого:** Все 11+ полей **ЕСТЬ в БД**, нужно заполнить из CQC API

---

### Некритические (отсутствуют в БД, можно использовать JSONB)

1. ❌ **Medical Equipment** (4+ поля) - **НЕТ в БД**
   - `medical_equipment` (array) - можно использовать JSONB `facilities`
   - `has_oxygen_equipment` - можно использовать JSONB `facilities`
   - `has_hospital_bed` - можно использовать JSONB `facilities`
   - `has_hoist` - можно использовать JSONB `facilities`

2. ❌ **Medication Management** (2 поля) - **НЕТ в БД**
   - `on_site_pharmacy` - можно использовать JSONB `facilities`
   - `medication_administration` - можно использовать JSONB `facilities`

3. ⚠️ **Staffing Details** (3+ поля) - **ЕСТЬ JSONB поле**
   - `staff_ratio` - можно использовать JSONB `staff_information` ✅ ЕСТЬ в БД
   - `staff_retention_rate` - можно использовать JSONB `staff_information` ✅ ЕСТЬ в БД
   - `nurse_to_resident_ratio` - можно использовать JSONB `staff_information` ✅ ЕСТЬ в БД

**Итого:** 6 полей отсутствуют в БД (можно использовать JSONB), 3 поля можно использовать через JSONB `staff_information`

---

## 🎯 Рекомендации

### ⚠️ ВАЖНО: Структура БД полная! Проблема в заполнении данных.

**См. детальный анализ:** `DB_STRUCTURE_ANALYSIS.md`

### Приоритет 1: Заполнить существующие поля из CQC API ✅

**Все поля ЕСТЬ в БД, нужно только заполнить их данными:**

1. **Service User Bands** - использовать CQC API `serviceUserBands`
   - Заполнить 12 плоских полей: `serves_*` (все ЕСТЬ в БД)
   - Заполнить JSONB поле: `service_user_bands` (ЕСТЬ в БД)

2. **Licenses** - использовать CQC API `regulatedActivities`
   - Заполнить 5 плоских полей: `has_*_license` (все ЕСТЬ в БД)
   - Заполнить JSONB поле: `regulated_activities` (ЕСТЬ в БД, содержит все 14 activities)

3. **Inspection Date** - использовать CQC API `inspectionDate`
   - Заполнить поле: `cqc_last_inspection_date` (ЕСТЬ в БД)

**Endpoint:**
```
GET /locations/{locationId}
```

**Поля в ответе:**
- `serviceUserBands`: ["Older people", "People with dementia", ...]
- `regulatedActivities`: [{"name": "Personal care", "code": "RA1"}, ...]
- `inspectionDate`: "2024-01-15"

**Действие:** Обновить ETL процесс для заполнения существующих полей в БД

---

### Приоритет 2: Увеличить таймауты и задержки

**Текущие таймауты:**
- CQC API: 30.0 секунд
- Companies House API: 30.0 секунд

**Рекомендации:**
- Увеличить CQC API timeout до 60.0 секунд
- Увеличить Companies House API timeout до 60.0 секунд
- Добавить задержки между запросами (1-2 секунды)
- Добавить retry logic с exponential backoff

---

### Приоритет 2: Использовать JSONB поля для отсутствующих данных

**Для полей, которых нет в БД:**

1. **Medical Equipment** - использовать JSONB поле `facilities`:
   ```json
   {
     "medical_equipment": ["oxygen", "hospital_bed", "hoist"],
     "has_oxygen_equipment": true,
     "has_hospital_bed": true,
     "has_hoist": true
   }
   ```

2. **Medication Management** - использовать JSONB поле `facilities`:
   ```json
   {
     "on_site_pharmacy": false,
     "medication_administration": "full"
   }
   ```

3. **Staffing Details** - использовать JSONB поле `staff_information` (ЕСТЬ в БД):
   ```json
   {
     "staff_ratio": 1.5,
     "staff_retention_rate": 85.5,
     "nurse_to_resident_ratio": 0.3
   }
   ```

### Приоритет 3: Поля, которые нельзя найти

**Решение:**
- Использовать proxy fields (уже реализовано)
- Использовать JSONB поля для хранения (см. Приоритет 2)
- Запрашивать напрямую у дома престарелых при посещении
- Использовать Staff Quality API для анализа отзывов

---

**Статус:** ✅ АНАЛИЗ ЗАВЕРШЕН


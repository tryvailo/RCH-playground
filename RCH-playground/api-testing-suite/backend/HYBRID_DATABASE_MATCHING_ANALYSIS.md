# Анализ полей для матчинга: Гибридный подход (CQC + Staging)

**Дата:** 2025-01-XX  
**Статус:** ✅ АНАЛИЗ ЗАВЕРШЕН

---

## 📊 Резюме

**База 1 (Основная):** `cqc_carehomes_master_full_data_rows.csv` - CQC данные (128 полей)  
**База 2 (Вспомогательная):** `carehome_staging_export.csv` - Дополнительные данные (114 полей)  
**Связь:** `location_id` (CQC) ↔ `cqc_location_id` (Staging)  
**Формат ID:** `1-10000302982`

---

## ✅ Поля для матчинга из CQC (основная база)

### 1. Service User Bands (12 полей) - **КРИТИЧНО ДЛЯ МАТЧИНГА**

| Поле в БД | Поле в CQC CSV | Статус данных | Использование |
|-----------|---------------|----------------|---------------|
| `serves_older_people` | `service_user_band_older_people` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |
| `serves_dementia_band` | `service_user_band_dementia` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |
| `serves_mental_health` | `service_user_band_mental_health` | ⚠️ ПУСТО (но поле есть) | ✅ ИСПОЛЬЗОВАТЬ (fallback) |
| `serves_physical_disabilities` | `service_user_band_physical_disability` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |
| `serves_sensory_impairments` | `service_user_band_sensory_impairment` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |
| `serves_children` | `service_user_band_children` | ⚠️ ПУСТО (но поле есть) | ✅ ИСПОЛЬЗОВАТЬ (fallback) |
| `serves_learning_disabilities` | `service_user_band_learning_disabilities` | ⚠️ ПУСТО (но поле есть) | ✅ ИСПОЛЬЗОВАТЬ (fallback) |
| `serves_detained_mha` | `service_user_band_detained_mental_health` | ⚠️ ПУСТО (но поле есть) | ✅ ИСПОЛЬЗОВАТЬ (fallback) |
| `serves_substance_misuse` | `service_user_band_drugs_alcohol` | ⚠️ ПУСТО (но поле есть) | ✅ ИСПОЛЬЗОВАТЬ (fallback) |
| `serves_eating_disorders` | `service_user_band_eating_disorder` | ⚠️ ПУСТО (но поле есть) | ✅ ИСПОЛЬЗОВАТЬ (fallback) |
| `serves_whole_population` | `service_user_band_whole_population` | ⚠️ ПУСТО (но поле есть) | ✅ ИСПОЛЬЗОВАТЬ (fallback) |
| `serves_younger_adults` | `service_user_band_younger_adults` | ⚠️ ПУСТО (но поле есть) | ✅ ИСПОЛЬЗОВАТЬ (fallback) |

**Вывод:** ✅ Все 12 полей **ЕСТЬ** в CQC. Некоторые пустые, но это нормально (используется fallback логика для NULL значений).

---

### 2. Regulated Activities (14 полей) - **КРИТИЧНО ДЛЯ МАТЧИНГА**

| Поле в БД | Поле в CQC CSV | Статус данных | Использование |
|-----------|---------------|----------------|---------------|
| `has_nursing_care_license` | `service_type_care_home_nursing` | ⚠️ ПУСТО (но поле есть) | ✅ ИСПОЛЬЗОВАТЬ ⚠️ **КРИТИЧНО: НЕ из `regulated_activity_nursing_care`!** |
| `has_personal_care_license` | `service_type_care_home_without_nursing` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |
| `has_surgical_procedures_license` | `regulated_activity_surgical` | ⚠️ ПУСТО (но поле есть) | ✅ ИСПОЛЬЗОВАТЬ (fallback) |
| `has_treatment_license` | `regulated_activity_treatment` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |
| `has_diagnostic_license` | `regulated_activity_diagnostic` | ⚠️ ПУСТО (но поле есть) | ✅ ИСПОЛЬЗОВАТЬ (fallback) |
| — | `regulated_activity_accommodation_nursing` | ✅ ЕСТЬ ДАННЫЕ | ⚠️ Дополнительное (не используется в матчинге) |
| — | `regulated_activity_personal_care` | ⚠️ ПУСТО | ⚠️ Не используется (используется `service_type`) |
| ... (еще 7 полей) | ... | ⚠️ ПУСТО | ⚠️ Дополнительные (не используются в матчинге) |

**Вывод:** ✅ Все 5 критических полей **ЕСТЬ** в CQC. ⚠️ **КРИТИЧНО:** `has_nursing_care_license` маппится из `service_type_care_home_nursing`, НЕ из `regulated_activity_nursing_care`.

---

### 3. CQC Ratings (6 полей) - **КРИТИЧНО ДЛЯ МАТЧИНГА**

| Поле в БД | Поле в CQC CSV | Статус данных | Использование |
|-----------|---------------|----------------|---------------|
| `cqc_rating_overall` | `location_latest_overall_rating` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |
| `cqc_rating_safe` | `cqc_rating_safe` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |
| `cqc_rating_effective` | `cqc_rating_effective` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |
| `cqc_rating_caring` | `cqc_rating_caring` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |
| `cqc_rating_responsive` | `cqc_rating_responsive` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |
| `cqc_rating_well_led` | `cqc_rating_well_led` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |

**Вывод:** ✅ Все 6 полей **ЕСТЬ** в CQC с данными. Использовать из CQC.

---

### 4. Location (5 полей) - **КРИТИЧНО ДЛЯ МАТЧИНГА**

| Поле в БД | Поле в CQC CSV | Статус данных | Использование |
|-----------|---------------|----------------|---------------|
| `latitude` | `location_latitude` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |
| `longitude` | `location_longitude` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |
| `postcode` | `location_postal_code` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |
| `city` | `location_city` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |
| `local_authority` | `location_local_authority` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |

**Вывод:** ✅ Все 5 полей **ЕСТЬ** в CQC с данными. Использовать из CQC.

---

### 5. Care Types (4 поля) - **КРИТИЧНО ДЛЯ МАТЧИНГА**

| Поле в БД | Поле в CQC CSV | Статус данных | Использование |
|-----------|---------------|----------------|---------------|
| `care_nursing` | `service_type_care_home_nursing` | ⚠️ ПУСТО (но поле есть) | ✅ ИСПОЛЬЗОВАТЬ (fallback) |
| `care_residential` | `service_type_care_home_without_nursing` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |
| `care_dementia` | `service_user_band_dementia` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ (proxy) |
| `care_respite` | — | ❌ ОТСУТСТВУЕТ | ⚠️ Нет в CQC |

**Вывод:** ✅ 3 из 4 полей **ЕСТЬ** в CQC. ⚠️ **КРИТИЧНО:** `care_nursing` используется для маппинга `has_nursing_care_license`.

---

## ✅ Поля для матчинга из STAGING (дополнительная база)

### 1. Pricing (4 поля) - **ВАЖНО ДЛЯ МАТЧИНГА**

| Поле в БД | Поле в Staging CSV | Статус данных | Использование |
|-----------|-------------------|----------------|---------------|
| `fee_residential_from` | `parsed_fee_residential_from` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |
| `fee_nursing_from` | `parsed_fee_nursing_from` | ⚠️ ПУСТО | ⚠️ Fallback на другие поля |
| `fee_dementia_from` | `parsed_fee_dementia_from` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |
| `fee_respite_from` | `parsed_fee_respite_from` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |

**Вывод:** ✅ 3 из 4 полей **ЕСТЬ** в Staging с данными. Цены **ОТСУТСТВУЮТ** в CQC, использовать из Staging.

---

### 2. Reviews (3 поля) - **ВАЖНО ДЛЯ МАТЧИНГА**

| Поле в БД | Поле в Staging CSV | Статус данных | Использование |
|-----------|-------------------|----------------|---------------|
| `review_average_score` | `parsed_review_average_score` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |
| `review_count` | `parsed_review_count` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |
| `google_rating` | `parsed_google_rating` | ⚠️ ПУСТО | ⚠️ Fallback |

**Вывод:** ✅ 2 из 3 полей **ЕСТЬ** в Staging с данными. Отзывы **ОТСУТСТВУЮТ** в CQC, использовать из Staging.

---

### 3. Amenities (5 полей) - **ВАЖНО ДЛЯ МАТЧИНГА**

| Поле в БД | Поле в Staging CSV | Статус данных | Использование |
|-----------|-------------------|----------------|---------------|
| `wheelchair_access` | `parsed_wheelchair_access` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |
| `ensuite_rooms` | `parsed_ensuite_rooms` | ⚠️ ПУСТО | ⚠️ Fallback |
| `secure_garden` | `parsed_secure_garden` | ⚠️ ПУСТО | ⚠️ Fallback |
| `wifi_available` | `parsed_wifi_available` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |
| `parking_onsite` | `parsed_parking_onsite` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |

**Вывод:** ✅ 3 из 5 полей **ЕСТЬ** в Staging с данными. Удобства **ОТСУТСТВУЮТ** в CQC, использовать из Staging.

---

### 4. Availability (4 поля) - **ВАЖНО ДЛЯ МАТЧИНГА**

| Поле в БД | Поле в Staging CSV | Статус данных | Использование |
|-----------|-------------------|----------------|---------------|
| `beds_total` | `parsed_beds_total` | ✅ ЕСТЬ ДАННЫЕ | ✅ ИСПОЛЬЗОВАТЬ |
| `beds_available` | `parsed_beds_available` | ⚠️ ПУСТО | ⚠️ Fallback |
| `has_availability` | `parsed_has_availability` | ⚠️ ПУСТО | ⚠️ Fallback |
| `availability_status` | `parsed_availability_status` | ⚠️ ПУСТО | ⚠️ Fallback |

**Вывод:** ✅ 1 из 4 полей **ЕСТЬ** в Staging с данными. В CQC есть `care_homes_beds` (аналог `beds_total`), но остальные поля только в Staging.

---

### 5. Medical Equipment (4 поля) - **ОПЦИОНАЛЬНО**

| Поле в БД | Поле в Staging CSV | Статус данных | Использование |
|-----------|-------------------|----------------|---------------|
| `medical_equipment` | — | ❌ ОТСУТСТВУЕТ | ⚠️ Использовать proxy через `care_nursing` |
| `has_oxygen_equipment` | — | ❌ ОТСУТСТВУЕТ | ⚠️ Использовать proxy через `care_nursing` |
| `has_hospital_bed` | — | ❌ ОТСУТСТВУЕТ | ⚠️ Использовать proxy через `care_nursing` |
| `has_hoist` | — | ❌ ОТСУТСТВУЕТ | ⚠️ Использовать proxy через `care_nursing` |

**Вывод:** ❌ Медицинское оборудование **ОТСУТСТВУЕТ** в обеих базах. Использовать proxy через `care_nursing` (если `care_nursing = TRUE`, то вероятно есть оборудование).

---

### 6. Medication Management (2 поля) - **ОПЦИОНАЛЬНО**

| Поле в БД | Поле в Staging CSV | Статус данных | Использование |
|-----------|-------------------|----------------|---------------|
| `on_site_pharmacy` | — | ❌ ОТСУТСТВУЕТ | ⚠️ Использовать proxy через `care_nursing` |
| `medication_administration` | — | ❌ ОТСУТСТВУЕТ | ⚠️ Использовать proxy через `care_nursing` |

**Вывод:** ❌ Управление медикаментами **ОТСУТСТВУЕТ** в обеих базах. Использовать proxy через `care_nursing` (если `care_nursing = TRUE`, то вероятно есть управление медикаментами).

---

### 7. Staffing Details (3 поля) - **ОПЦИОНАЛЬНО**

| Поле в БД | Поле в Staging CSV | Статус данных | Использование |
|-----------|-------------------|----------------|---------------|
| `staff_ratio` | `parsed_staff_ratio` | ⚠️ ПУСТО | ⚠️ Fallback |
| `staff_retention_rate` | — | ❌ ОТСУТСТВУЕТ | ⚠️ Не используется |
| `nurse_to_resident_ratio` | — | ❌ ОТСУТСТВУЕТ | ⚠️ Не используется |

**Вывод:** ⚠️ Данные о персонале **ОТСУТСТВУЮТ** или **ПУСТЫЕ** в обеих базах. Не использовать в матчинге (или использовать proxy через CQC ratings).

---

## 🔗 Связь между базами

### Идентификаторы:

- **CQC:** `location_id` (формат: `1-10000302982`)
- **Staging:** `cqc_location_id` (формат: `1-10000302982`)

**Вывод:** ✅ Связь возможна через `location_id` (CQC) ↔ `cqc_location_id` (Staging).

**Пример связи:**
```python
# CQC
location_id = "1-10000302982"

# Staging
cqc_location_id = "1-10000302982"  # Тот же ID
```

---

## 📋 Итоговые рекомендации

### ✅ Использовать из CQC (основная база):

1. **Service User Bands** (12 полей) - **КРИТИЧНО**
   - Все поля: `service_user_band_*` → `serves_*`
   - Статус: ✅ ЕСТЬ в CQC (некоторые пустые, но поле есть)

2. **Regulated Activities** (5 полей) - **КРИТИЧНО**
   - `service_type_care_home_nursing` → `has_nursing_care_license` ⚠️ **КРИТИЧНО: НЕ из `regulated_activity_nursing_care`!**
   - `service_type_care_home_without_nursing` → `has_personal_care_license`
   - `regulated_activity_surgical` → `has_surgical_procedures_license`
   - `regulated_activity_treatment` → `has_treatment_license`
   - `regulated_activity_diagnostic` → `has_diagnostic_license`

3. **CQC Ratings** (6 полей) - **КРИТИЧНО**
   - `location_latest_overall_rating` → `cqc_rating_overall`
   - `cqc_rating_safe` → `cqc_rating_safe`
   - `cqc_rating_effective` → `cqc_rating_effective`
   - `cqc_rating_caring` → `cqc_rating_caring`
   - `cqc_rating_responsive` → `cqc_rating_responsive`
   - `cqc_rating_well_led` → `cqc_rating_well_led`

4. **Location** (5 полей) - **КРИТИЧНО**
   - `location_latitude` → `latitude`
   - `location_longitude` → `longitude`
   - `location_postal_code` → `postcode`
   - `location_city` → `city`
   - `location_local_authority` → `local_authority`

5. **Care Types** (3 поля) - **КРИТИЧНО**
   - `service_type_care_home_nursing` → `care_nursing`
   - `service_type_care_home_without_nursing` → `care_residential`
   - `service_user_band_dementia` → `care_dementia` (proxy)

**Всего:** 31 поле для матчинга из CQC.

---

### ✅ Использовать из STAGING (дополнительная база):

1. **Pricing** (3 поля) - **ВАЖНО**
   - `parsed_fee_residential_from` → `fee_residential_from` ✅ ЕСТЬ ДАННЫЕ
   - `parsed_fee_dementia_from` → `fee_dementia_from` ✅ ЕСТЬ ДАННЫЕ
   - `parsed_fee_respite_from` → `fee_respite_from` ✅ ЕСТЬ ДАННЫЕ
   - `parsed_fee_nursing_from` → `fee_nursing_from` ⚠️ ПУСТО

2. **Reviews** (2 поля) - **ВАЖНО**
   - `parsed_review_average_score` → `review_average_score` ✅ ЕСТЬ ДАННЫЕ
   - `parsed_review_count` → `review_count` ✅ ЕСТЬ ДАННЫЕ
   - `parsed_google_rating` → `google_rating` ⚠️ ПУСТО

3. **Amenities** (3 поля) - **ВАЖНО**
   - `parsed_wheelchair_access` → `wheelchair_access` ✅ ЕСТЬ ДАННЫЕ
   - `parsed_wifi_available` → `wifi_available` ✅ ЕСТЬ ДАННЫЕ
   - `parsed_parking_onsite` → `parking_onsite` ✅ ЕСТЬ ДАННЫЕ
   - `parsed_ensuite_rooms` → `ensuite_rooms` ⚠️ ПУСТО
   - `parsed_secure_garden` → `secure_garden` ⚠️ ПУСТО

4. **Availability** (1 поле) - **ВАЖНО**
   - `parsed_beds_total` → `beds_total` ✅ ЕСТЬ ДАННЫЕ
   - `parsed_beds_available` → `beds_available` ⚠️ ПУСТО
   - `parsed_has_availability` → `has_availability` ⚠️ ПУСТО
   - `parsed_availability_status` → `availability_status` ⚠️ ПУСТО

5. **Funding** (3 поля) - **ВАЖНО**
   - `parsed_accepts_self_funding` → `accepts_self_funding` ✅ ЕСТЬ ДАННЫЕ
   - `parsed_accepts_local_authority` → `accepts_local_authority` ✅ ЕСТЬ ДАННЫЕ
   - `parsed_accepts_nhs_chc` → `accepts_nhs_chc` ✅ ЕСТЬ ДАННЫЕ
   - `parsed_accepts_third_party_topup` → `accepts_third_party_topup` ⚠️ ПУСТО

6. **Medical Equipment** (0 полей) - **ОПЦИОНАЛЬНО**
   - ❌ ОТСУТСТВУЕТ в обеих базах → Использовать proxy через `care_nursing`

7. **Medication Management** (0 полей) - **ОПЦИОНАЛЬНО**
   - ❌ ОТСУТСТВУЕТ в обеих базах → Использовать proxy через `care_nursing`

8. **Staffing Details** (0 полей) - **ОПЦИОНАЛЬНО**
   - ❌ ОТСУТСТВУЕТ или ПУСТЫЕ → Не использовать в матчинге

**Всего:** 12 полей для матчинга из Staging (с данными).

---

### ⚠️ Приоритеты при конфликтах:

Если поле есть в обеих базах:
1. **CQC** - для Service User Bands, Regulated Activities, CQC Ratings, Location, Care Types
2. **Staging** - для Pricing, Reviews, Amenities, Availability
3. **Fallback:** Если нет в CQC → использовать из Staging

---

## 🏗️ Архитектура загрузки данных

### Шаг 1: Загрузить CQC базу

```python
def load_cqc_homes() -> List[Dict]:
    """
    Загрузить дома из CQC CSV.
    """
    homes = []
    with open('cqc_carehomes_master_full_data_rows.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            home = {
                'location_id': row['location_id'],
                # Service User Bands
                'serves_older_people': row.get('service_user_band_older_people') == 'TRUE',
                'serves_dementia_band': row.get('service_user_band_dementia') == 'TRUE',
                # ... все остальные поля из CQC
            }
            homes.append(home)
    return homes
```

---

### Шаг 2: Загрузить Staging базу и связать с CQC

```python
def load_staging_data() -> Dict[str, Dict]:
    """
    Загрузить данные из Staging CSV и создать индекс по location_id.
    """
    staging_index = {}
    with open('carehome_staging_export.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            location_id = row.get('location_id') or row.get('cqc_location_id')
            if location_id:
                staging_index[location_id] = {
                    # Pricing
                    'fee_residential_from': row.get('fee_residential_from'),
                    'fee_nursing_from': row.get('fee_nursing_from'),
                    # ... все остальные поля из Staging
                }
    return staging_index
```

---

### Шаг 3: Объединить данные

```python
def merge_cqc_and_staging(cqc_homes: List[Dict], staging_index: Dict[str, Dict]) -> List[Dict]:
    """
    Объединить данные из CQC и Staging.
    """
    merged_homes = []
    for home in cqc_homes:
        location_id = home['location_id']
        staging_data = staging_index.get(location_id, {})
        
        # Добавить данные из Staging
        home.update({
            # Pricing (из Staging)
            'fee_residential_from': staging_data.get('fee_residential_from') or home.get('fee_residential_from'),
            'fee_nursing_from': staging_data.get('fee_nursing_from') or home.get('fee_nursing_from'),
            # Reviews (из Staging)
            'review_average_score': staging_data.get('review_average_score'),
            'review_count': staging_data.get('review_count'),
            'google_rating': staging_data.get('google_rating'),
            # Amenities (из Staging)
            'wheelchair_access': staging_data.get('wheelchair_access') or home.get('wheelchair_access'),
            'ensuite_rooms': staging_data.get('ensuite_rooms'),
            'secure_garden': staging_data.get('secure_garden'),
            # ... остальные поля
        })
        
        merged_homes.append(home)
    
    return merged_homes
```

---

## 📊 Маппинг полей для алгоритма матчинга

### Service User Bands (из CQC):

```python
CQC_TO_DB_SERVICE_BANDS = {
    'service_user_band_older_people': 'serves_older_people',
    'service_user_band_dementia': 'serves_dementia_band',
    'service_user_band_mental_health': 'serves_mental_health',
    'service_user_band_physical_disability': 'serves_physical_disabilities',
    'service_user_band_sensory_impairment': 'serves_sensory_impairments',
    'service_user_band_children': 'serves_children',
    'service_user_band_learning_disabilities': 'serves_learning_disabilities',
    'service_user_band_detained_mental_health': 'serves_detained_mha',
    'service_user_band_drugs_alcohol': 'serves_substance_misuse',
    'service_user_band_eating_disorder': 'serves_eating_disorders',
    'service_user_band_whole_population': 'serves_whole_population',
    'service_user_band_younger_adults': 'serves_younger_adults'
}
```

---

### Regulated Activities (из CQC):

```python
CQC_TO_DB_LICENSES = {
    'service_type_care_home_nursing': 'has_nursing_care_license',  # ⚠️ КРИТИЧНО: не из regulated_activity!
    'service_type_care_home_without_nursing': 'has_personal_care_license',
    'regulated_activity_surgical': 'has_surgical_procedures_license',
    'regulated_activity_treatment': 'has_treatment_license',
    'regulated_activity_diagnostic': 'has_diagnostic_license'
}
```

---

### CQC Ratings (из CQC):

```python
CQC_TO_DB_RATINGS = {
    'location_latest_overall_rating': 'cqc_rating_overall',
    'cqc_rating_safe': 'cqc_rating_safe',
    'cqc_rating_effective': 'cqc_rating_effective',
    'cqc_rating_caring': 'cqc_rating_caring',
    'cqc_rating_responsive': 'cqc_rating_responsive',
    'cqc_rating_well_led': 'cqc_rating_well_led'
}
```

---

### Location (из CQC):

```python
CQC_TO_DB_LOCATION = {
    'location_latitude': 'latitude',
    'location_longitude': 'longitude',
    'location_postal_code': 'postcode',
    'location_city': 'city',
    'location_local_authority': 'local_authority'
}
```

---

### Pricing (из Staging):

```python
STAGING_TO_DB_PRICING = {
    'fee_residential_from': 'fee_residential_from',
    'fee_nursing_from': 'fee_nursing_from',
    'fee_dementia_from': 'fee_dementia_from',
    'fee_respite_from': 'fee_respite_from'
}
```

---

### Reviews (из Staging):

```python
STAGING_TO_DB_REVIEWS = {
    'review_average_score': 'review_average_score',
    'review_count': 'review_count',
    'google_rating': 'google_rating'
}
```

---

### Amenities (из Staging):

```python
STAGING_TO_DB_AMENITIES = {
    'wheelchair_access': 'wheelchair_access',
    'ensuite_rooms': 'ensuite_rooms',
    'secure_garden': 'secure_garden',
    'wifi_available': 'wifi_available',
    'parking_onsite': 'parking_onsite'
}
```

---

## ✅ Итоговые рекомендации

### 1. Использовать CQC как основную базу ✅

- Все критически важные поля для матчинга **ЕСТЬ** в CQC
- Service User Bands, Regulated Activities, CQC Ratings, Location, Care Types

### 2. Использовать Staging как дополнительную базу ✅

- Поля, которых нет в CQC: Pricing, Reviews, Amenities, Availability
- Опциональные поля: Medical Equipment, Medication, Staffing

### 3. Связь через `location_id` ✅

- CQC: `location_id`
- Staging: `location_id` или `cqc_location_id`
- Формат: `1-10000302982`

### 4. Приоритеты при конфликтах ✅

- **CQC** - для критических полей (Service User Bands, Ratings, Location)
- **Staging** - для дополнительных полей (Pricing, Reviews, Amenities)
- **Fallback:** Если нет в CQC → использовать из Staging

---

## 📋 Следующие шаги

1. ✅ Создать функцию загрузки CQC базы
2. ✅ Создать функцию загрузки Staging базы
3. ✅ Создать функцию объединения данных
4. ✅ Обновить алгоритм матчинга для использования объединенных данных
5. ✅ Протестировать на реальных данных

---

**Статус:** ✅ АНАЛИЗ ЗАВЕРШЕН, РЕКОМЕНДАЦИИ ГОТОВЫ


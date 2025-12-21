# Точный маппинг полей: CQC → БД и STAGING → БД

**Дата:** 2025-01-XX  
**Статус:** ✅ ГОТОВО ДЛЯ ИСПОЛЬЗОВАНИЯ

---

## 🔗 Связь между базами

- **CQC:** `location_id` (формат: `1-10000302982`)
- **Staging:** `cqc_location_id` (формат: `1-10000302982`)
- **Связь:** `location_id` (CQC) = `cqc_location_id` (Staging)

---

## 📋 Маппинг полей из CQC (основная база)

### Service User Bands (12 полей)

```python
CQC_SERVICE_BANDS_MAPPING = {
    'serves_older_people': 'service_user_band_older_people',
    'serves_dementia_band': 'service_user_band_dementia',
    'serves_mental_health': 'service_user_band_mental_health',
    'serves_physical_disabilities': 'service_user_band_physical_disability',
    'serves_sensory_impairments': 'service_user_band_sensory_impairment',
    'serves_children': 'service_user_band_children',
    'serves_learning_disabilities': 'service_user_band_learning_disabilities',
    'serves_detained_mha': 'service_user_band_detained_mental_health',
    'serves_substance_misuse': 'service_user_band_drugs_alcohol',
    'serves_eating_disorders': 'service_user_band_eating_disorder',
    'serves_whole_population': 'service_user_band_whole_population',
    'serves_younger_adults': 'service_user_band_younger_adults'
}
```

**Преобразование:** `TRUE`/`FALSE` (строка) → `True`/`False` (boolean)

---

### Regulated Activities (5 полей)

```python
CQC_LICENSES_MAPPING = {
    'has_nursing_care_license': 'service_type_care_home_nursing',  # ⚠️ КРИТИЧНО: НЕ из regulated_activity!
    'has_personal_care_license': 'service_type_care_home_without_nursing',
    'has_surgical_procedures_license': 'regulated_activity_surgical',
    'has_treatment_license': 'regulated_activity_treatment',
    'has_diagnostic_license': 'regulated_activity_diagnostic'
}
```

**Преобразование:** `TRUE`/`FALSE` (строка) → `True`/`False` (boolean)

---

### CQC Ratings (6 полей)

```python
CQC_RATINGS_MAPPING = {
    'cqc_rating_overall': 'location_latest_overall_rating',
    'cqc_rating_safe': 'cqc_rating_safe',
    'cqc_rating_effective': 'cqc_rating_effective',
    'cqc_rating_caring': 'cqc_rating_caring',
    'cqc_rating_responsive': 'cqc_rating_responsive',
    'cqc_rating_well_led': 'cqc_rating_well_led'
}
```

**Преобразование:** `'Good'`, `'Outstanding'`, `'Requires improvement'`, `'Inadequate'` → нормализация через `normalize_cqc_rating()`

---

### Location (5 полей)

```python
CQC_LOCATION_MAPPING = {
    'latitude': 'location_latitude',
    'longitude': 'location_longitude',
    'postcode': 'location_postal_code',
    'city': 'location_city',
    'local_authority': 'location_local_authority'
}
```

**Преобразование:**
- `latitude`/`longitude`: строка с запятой → `float` (использовать `safe_latitude()`/`safe_longitude()`)
- `postcode`/`city`/`local_authority`: `clean_text()`

---

### Care Types (3 поля)

```python
CQC_CARE_TYPES_MAPPING = {
    'care_nursing': 'service_type_care_home_nursing',
    'care_residential': 'service_type_care_home_without_nursing',
    'care_dementia': 'service_user_band_dementia'  # Proxy
}
```

**Преобразование:** `TRUE`/`FALSE` (строка) → `True`/`False` (boolean)

---

## 📋 Маппинг полей из STAGING (дополнительная база)

### Pricing (3 поля)

```python
STAGING_PRICING_MAPPING = {
    'fee_residential_from': 'parsed_fee_residential_from',
    'fee_dementia_from': 'parsed_fee_dementia_from',
    'fee_respite_from': 'parsed_fee_respite_from'
    # 'fee_nursing_from': 'parsed_fee_nursing_from'  # ⚠️ ПУСТО
}
```

**Преобразование:** Число (строка или float) → `float` (weekly fee)

---

### Reviews (2 поля)

```python
STAGING_REVIEWS_MAPPING = {
    'review_average_score': 'parsed_review_average_score',
    'review_count': 'parsed_review_count'
    # 'google_rating': 'parsed_google_rating'  # ⚠️ ПУСТО
}
```

**Преобразование:**
- `review_average_score`: `float` (0.0-5.0)
- `review_count`: `int`

---

### Amenities (3 поля)

```python
STAGING_AMENITIES_MAPPING = {
    'wheelchair_access': 'parsed_wheelchair_access',
    'wifi_available': 'parsed_wifi_available',
    'parking_onsite': 'parsed_parking_onsite'
    # 'ensuite_rooms': 'parsed_ensuite_rooms'  # ⚠️ ПУСТО
    # 'secure_garden': 'parsed_secure_garden'  # ⚠️ ПУСТО
}
```

**Преобразование:** `True`/`False` (строка или boolean) → `True`/`False` (boolean)

---

### Availability (1 поле)

```python
STAGING_AVAILABILITY_MAPPING = {
    'beds_total': 'parsed_beds_total'
    # 'beds_available': 'parsed_beds_available'  # ⚠️ ПУСТО
    # 'has_availability': 'parsed_has_availability'  # ⚠️ ПУСТО
    # 'availability_status': 'parsed_availability_status'  # ⚠️ ПУСТО
}
```

**Преобразование:** Число (строка или int) → `int`

---

### Funding (3 поля)

```python
STAGING_FUNDING_MAPPING = {
    'accepts_self_funding': 'parsed_accepts_self_funding',
    'accepts_local_authority': 'parsed_accepts_local_authority',
    'accepts_nhs_chc': 'parsed_accepts_nhs_chc'
    # 'accepts_third_party_topup': 'parsed_accepts_third_party_topup'  # ⚠️ ПУСТО
}
```

**Преобразование:** `True`/`False` (строка или boolean) → `True`/`False` (boolean)

---

## 🔄 Логика объединения данных

### Приоритеты:

1. **CQC** - для критических полей (Service User Bands, Ratings, Location, Care Types)
2. **Staging** - для дополнительных полей (Pricing, Reviews, Amenities, Availability, Funding)
3. **Fallback:** Если поле пустое в CQC → проверить Staging

### Пример кода:

```python
def merge_cqc_and_staging(cqc_home: dict, staging_data: dict) -> dict:
    """
    Объединить данные из CQC и Staging.
    """
    merged = {}
    
    # 1. Service User Bands (из CQC)
    for db_field, cqc_field in CQC_SERVICE_BANDS_MAPPING.items():
        value = cqc_home.get(cqc_field, '').upper() == 'TRUE'
        merged[db_field] = value
    
    # 2. CQC Ratings (из CQC)
    for db_field, cqc_field in CQC_RATINGS_MAPPING.items():
        value = cqc_home.get(cqc_field)
        merged[db_field] = normalize_cqc_rating(value) if value else None
    
    # 3. Location (из CQC)
    for db_field, cqc_field in CQC_LOCATION_MAPPING.items():
        if db_field in ['latitude', 'longitude']:
            value = safe_latitude(cqc_home.get(cqc_field)) if db_field == 'latitude' else safe_longitude(cqc_home.get(cqc_field))
        else:
            value = clean_text(cqc_home.get(cqc_field))
        merged[db_field] = value
    
    # 4. Pricing (из Staging)
    for db_field, staging_field in STAGING_PRICING_MAPPING.items():
        value = staging_data.get(staging_field)
        if value:
            try:
                merged[db_field] = float(value)
            except (ValueError, TypeError):
                merged[db_field] = None
        else:
            merged[db_field] = None
    
    # 5. Reviews (из Staging)
    for db_field, staging_field in STAGING_REVIEWS_MAPPING.items():
        value = staging_data.get(staging_field)
        if value:
            try:
                if db_field == 'review_count':
                    merged[db_field] = int(value)
                else:
                    merged[db_field] = float(value)
            except (ValueError, TypeError):
                merged[db_field] = None
        else:
            merged[db_field] = None
    
    # 6. Amenities (из Staging)
    for db_field, staging_field in STAGING_AMENITIES_MAPPING.items():
        value = staging_data.get(staging_field)
        if value:
            merged[db_field] = str(value).upper() in ['TRUE', '1', 'YES', 'TRUE']
        else:
            merged[db_field] = None
    
    # 7. Availability (из Staging)
    for db_field, staging_field in STAGING_AVAILABILITY_MAPPING.items():
        value = staging_data.get(staging_field)
        if value:
            try:
                merged[db_field] = int(value)
            except (ValueError, TypeError):
                merged[db_field] = None
        else:
            merged[db_field] = None
    
    # 8. Funding (из Staging)
    for db_field, staging_field in STAGING_FUNDING_MAPPING.items():
        value = staging_data.get(staging_field)
        if value:
            merged[db_field] = str(value).upper() in ['TRUE', '1', 'YES', 'TRUE']
        else:
            merged[db_field] = None
    
    return merged
```

---

## ✅ Итоговая таблица полей

| Категория | Поля в БД | Источник | Статус |
|-----------|-----------|----------|--------|
| **Service User Bands** | 12 полей | CQC | ✅ ЕСТЬ |
| **Regulated Activities** | 5 полей | CQC | ✅ ЕСТЬ |
| **CQC Ratings** | 6 полей | CQC | ✅ ЕСТЬ ДАННЫЕ |
| **Location** | 5 полей | CQC | ✅ ЕСТЬ ДАННЫЕ |
| **Care Types** | 3 поля | CQC | ✅ ЕСТЬ |
| **Pricing** | 3 поля | Staging | ✅ ЕСТЬ ДАННЫЕ |
| **Reviews** | 2 поля | Staging | ✅ ЕСТЬ ДАННЫЕ |
| **Amenities** | 3 поля | Staging | ✅ ЕСТЬ ДАННЫЕ |
| **Availability** | 1 поле | Staging | ✅ ЕСТЬ ДАННЫЕ |
| **Funding** | 3 поля | Staging | ✅ ЕСТЬ ДАННЫЕ |
| **ИТОГО** | **43 поля** | — | ✅ **ГОТОВО** |

---

**Статус:** ✅ МАППИНГ ГОТОВ ДЛЯ ИСПОЛЬЗОВАНИЯ


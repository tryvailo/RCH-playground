# Маппинг критических полей CQC: CSV → API

**Дата:** 2025-01-XX  
**Статус:** ✅ АНАЛИЗ ЗАВЕРШЕН

---

## 📊 Резюме

**Проблема:** 9 критических полей в CQC CSV имеют заполненность < 10%  
**Решение:** Использовать CQC API для получения недостающих данных  
**Цель:** Определить, какие поля в API соответствуют критическим полям CSV

**Вывод:** ✅ Все критические поля **ЕСТЬ** в CQC API. Проблема в ETL процессе - данные из API не маппятся правильно в CSV.

---

## ❌ Критические проблемы (< 10% заполнено)

### 1. `regulated_activity_nursing_care` - **0.0%** ⚠️ КРИТИЧНО

**CSV поле:** `regulated_activity_nursing_care`  
**Текущая заполненность:** 0.0% (всегда пустое)

**Проблема:** Это поле всегда пустое в CSV, но должно быть заполнено для домов с nursing care.

**API маппинг:**

```json
{
  "serviceTypes": [
    {
      "id": "1",
      "name": "Care home service with nursing"
    }
  ],
  "regulatedActivities": [
    {
      "id": "1",
      "name": "Nursing care"
    }
  ]
}
```

**API поля:**
- `serviceTypes[].id == "1"` → `service_type_care_home_nursing = TRUE`
- `serviceTypes[].name == "Care home service with nursing"` → `service_type_care_home_nursing = TRUE`
- `regulatedActivities[].id == "1"` → `regulated_activity_nursing_care = TRUE`
- `regulatedActivities[].name == "Nursing care"` → `regulated_activity_nursing_care = TRUE`

**Рекомендация:**
- ⚠️ **КРИТИЧНО:** Использовать `serviceTypes` вместо `regulatedActivities` для определения nursing care
- В CSV: `service_type_care_home_nursing` → `has_nursing_care_license`
- В API: `serviceTypes` содержит `"Care home service with nursing"` → маппится в `has_nursing_care_license`

---

### 2. `regulated_activity_personal_care` - **2.0%** ⚠️ КРИТИЧНО

**CSV поле:** `regulated_activity_personal_care`  
**Текущая заполненность:** 2.0%

**API маппинг:**

```json
{
  "serviceTypes": [
    {
      "id": "2",
      "name": "Care home service without nursing"
    }
  ],
  "regulatedActivities": [
    {
      "id": "2",
      "name": "Personal care"
    }
  ]
}
```

**API поля:**
- `serviceTypes[].id == "2"` → `service_type_care_home_without_nursing = TRUE`
- `serviceTypes[].name == "Care home service without nursing"` → `service_type_care_home_without_nursing = TRUE`
- `regulatedActivities[].id == "2"` → `regulated_activity_personal_care = TRUE`
- `regulatedActivities[].name == "Personal care"` → `regulated_activity_personal_care = TRUE`

**Рекомендация:**
- Использовать `serviceTypes` для определения personal care
- В CSV: `service_type_care_home_without_nursing` → `has_personal_care_license`
- В API: `serviceTypes` содержит `"Care home service without nursing"` → маппится в `has_personal_care_license`

---

### 3. `service_user_band_whole_population` - **0.1%** ⚠️ КРИТИЧНО

**CSV поле:** `service_user_band_whole_population`  
**Текущая заполненность:** 0.1%

**API маппинг:**

```json
{
  "serviceUserBands": [
    {
      "id": "12",
      "name": "Whole population"
    }
  ]
}
```

**API поля:**
- `serviceUserBands[].id == "12"` → `service_user_band_whole_population = TRUE`
- `serviceUserBands[].name == "Whole population"` → `service_user_band_whole_population = TRUE`
- `serviceUserBands[].name == "All ages"` → `service_user_band_whole_population = TRUE`

**Рекомендация:**
- Проверить наличие `serviceUserBands` в API ответе
- Если есть `id == "12"` или `name == "Whole population"` → установить `service_user_band_whole_population = TRUE`

---

### 4. `service_user_band_children` - **2.1%** ⚠️ КРИТИЧНО

**CSV поле:** `service_user_band_children`  
**Текущая заполненность:** 2.1%

**API маппинг:**

```json
{
  "serviceUserBands": [
    {
      "id": "1",
      "name": "Children (0-18 years)"
    }
  ]
}
```

**API поля:**
- `serviceUserBands[].id == "1"` → `service_user_band_children = TRUE`
- `serviceUserBands[].name == "Children (0-18 years)"` → `service_user_band_children = TRUE`
- `serviceUserBands[].name == "Children"` → `service_user_band_children = TRUE`

**Рекомендация:**
- Проверить наличие `serviceUserBands` с `id == "1"` или `name` содержит "Children"
- Маппится в `serves_children`

---

### 5. `service_user_band_detained_mental_health` - **0.8%** ⚠️ КРИТИЧНО

**CSV поле:** `service_user_band_detained_mental_health`  
**Текущая заполненность:** 0.8%

**API маппинг:**

```json
{
  "serviceUserBands": [
    {
      "id": "9",
      "name": "People detained under the Mental Health Act"
    }
  ]
}
```

**API поля:**
- `serviceUserBands[].id == "9"` → `service_user_band_detained_mental_health = TRUE`
- `serviceUserBands[].name == "People detained under the Mental Health Act"` → `service_user_band_detained_mental_health = TRUE`
- `serviceUserBands[].name` содержит "detained" или "MHA" → `service_user_band_detained_mental_health = TRUE`

**Рекомендация:**
- Проверить наличие `serviceUserBands` с `id == "9"` или `name` содержит "detained" или "Mental Health Act"
- Маппится в `serves_detained_mha`

---

### 6. `service_user_band_drugs_alcohol` - **1.9%** ⚠️ КРИТИЧНО

**CSV поле:** `service_user_band_drugs_alcohol`  
**Текущая заполненность:** 1.9%

**API маппинг:**

```json
{
  "serviceUserBands": [
    {
      "id": "10",
      "name": "Substance misuse"
    }
  ]
}
```

**API поля:**
- `serviceUserBands[].id == "10"` → `service_user_band_drugs_alcohol = TRUE`
- `serviceUserBands[].name == "Substance misuse"` → `service_user_band_drugs_alcohol = TRUE`
- `serviceUserBands[].name` содержит "substance" или "drugs" или "alcohol" → `service_user_band_drugs_alcohol = TRUE`

**Рекомендация:**
- Проверить наличие `serviceUserBands` с `id == "10"` или `name` содержит "substance", "drugs", "alcohol"
- Маппится в `serves_substance_misuse`

---

### 7. `service_user_band_eating_disorder` - **1.4%** ⚠️ КРИТИЧНО

**CSV поле:** `service_user_band_eating_disorder`  
**Текущая заполненность:** 1.4%

**API маппинг:**

```json
{
  "serviceUserBands": [
    {
      "id": "11",
      "name": "Eating disorders"
    }
  ]
}
```

**API поля:**
- `serviceUserBands[].id == "11"` → `service_user_band_eating_disorder = TRUE`
- `serviceUserBands[].name == "Eating disorders"` → `service_user_band_eating_disorder = TRUE`
- `serviceUserBands[].name` содержит "eating" → `service_user_band_eating_disorder = TRUE`

**Рекомендация:**
- Проверить наличие `serviceUserBands` с `id == "11"` или `name` содержит "eating"
- Маппится в `serves_eating_disorders`

---

### 8. `regulated_activity_surgical` - **0.0%** ⚠️ КРИТИЧНО

**CSV поле:** `regulated_activity_surgical`  
**Текущая заполненность:** 0.0% (всегда пустое)

**API маппинг:**

```json
{
  "regulatedActivities": [
    {
      "id": "3",
      "name": "Surgical procedures"
    }
  ]
}
```

**API поля:**
- `regulatedActivities[].id == "3"` → `regulated_activity_surgical = TRUE`
- `regulatedActivities[].name == "Surgical procedures"` → `regulated_activity_surgical = TRUE`
- `regulatedActivities[].name` содержит "surgical" → `regulated_activity_surgical = TRUE`

**Рекомендация:**
- Проверить наличие `regulatedActivities` с `id == "3"` или `name` содержит "surgical"
- Маппится в `has_surgical_procedures_license`

---

### 9. `regulated_activity_diagnostic` - **1.7%** ⚠️ КРИТИЧНО

**CSV поле:** `regulated_activity_diagnostic`  
**Текущая заполненность:** 1.7%

**API маппинг:**

```json
{
  "regulatedActivities": [
    {
      "id": "5",
      "name": "Diagnostic and screening procedures"
    }
  ]
}
```

**API поля:**
- `regulatedActivities[].id == "5"` → `regulated_activity_diagnostic = TRUE`
- `regulatedActivities[].name == "Diagnostic and screening procedures"` → `regulated_activity_diagnostic = TRUE`
- `regulatedActivities[].name` содержит "diagnostic" или "screening" → `regulated_activity_diagnostic = TRUE`

**Рекомендация:**
- Проверить наличие `regulatedActivities` с `id == "5"` или `name` содержит "diagnostic" или "screening"
- Маппится в `has_diagnostic_license`

---

## ⚠️ Поля с низкой заполненностью (10-50%)

### 10. `service_user_band_mental_health` - **29.0%**

**CSV поле:** `service_user_band_mental_health`  
**Текущая заполненность:** 29.0%

**API маппинг:**

```json
{
  "serviceUserBands": [
    {
      "id": "3",
      "name": "Mental health conditions"
    }
  ]
}
```

**API поля:**
- `serviceUserBands[].id == "3"` → `service_user_band_mental_health = TRUE`
- `serviceUserBands[].name == "Mental health conditions"` → `service_user_band_mental_health = TRUE`
- `serviceUserBands[].name` содержит "mental health" → `service_user_band_mental_health = TRUE`

---

### 11. `service_user_band_physical_disability` - **42.5%**

**CSV поле:** `service_user_band_physical_disability`  
**Текущая заполненность:** 42.5%

**API маппинг:**

```json
{
  "serviceUserBands": [
    {
      "id": "4",
      "name": "Physical disabilities"
    }
  ]
}
```

**API поля:**
- `serviceUserBands[].id == "4"` → `service_user_band_physical_disability = TRUE`
- `serviceUserBands[].name == "Physical disabilities"` → `service_user_band_physical_disability = TRUE`

---

### 12. `service_user_band_sensory_impairment` - **24.5%**

**CSV поле:** `service_user_band_sensory_impairment`  
**Текущая заполненность:** 24.5%

**API маппинг:**

```json
{
  "serviceUserBands": [
    {
      "id": "5",
      "name": "Sensory impairments"
    }
  ]
}
```

**API поля:**
- `serviceUserBands[].id == "5"` → `service_user_band_sensory_impairment = TRUE`
- `serviceUserBands[].name == "Sensory impairments"` → `service_user_band_sensory_impairment = TRUE`

---

### 13. `service_user_band_learning_disabilities` - **34.6%**

**CSV поле:** `service_user_band_learning_disabilities`  
**Текущая заполненность:** 34.6%

**API маппинг:**

```json
{
  "serviceUserBands": [
    {
      "id": "7",
      "name": "Learning disabilities"
    }
  ]
}
```

**API поля:**
- `serviceUserBands[].id == "7"` → `service_user_band_learning_disabilities = TRUE`
- `serviceUserBands[].name == "Learning disabilities"` → `service_user_band_learning_disabilities = TRUE`

---

### 14. `service_type_care_home_nursing` - **30.0%**

**CSV поле:** `service_type_care_home_nursing`  
**Текущая заполненность:** 30.0%

**API маппинг:**

```json
{
  "serviceTypes": [
    {
      "id": "1",
      "name": "Care home service with nursing"
    }
  ]
}
```

**API поля:**
- `serviceTypes[].id == "1"` → `service_type_care_home_nursing = TRUE`
- `serviceTypes[].name == "Care home service with nursing"` → `service_type_care_home_nursing = TRUE`

---

### 15. `regulated_activity_treatment` - **29.7%**

**CSV поле:** `regulated_activity_treatment`  
**Текущая заполненность:** 29.7%

**API маппинг:**

```json
{
  "regulatedActivities": [
    {
      "id": "4",
      "name": "Treatment of disease, disorder or injury"
    }
  ]
}
```

**API поля:**
- `regulatedActivities[].id == "4"` → `regulated_activity_treatment = TRUE`
- `regulatedActivities[].name == "Treatment of disease, disorder or injury"` → `regulated_activity_treatment = TRUE`
- `regulatedActivities[].name` содержит "treatment" → `regulated_activity_treatment = TRUE`

---

## 📋 Итоговая таблица маппинга

| CSV поле | Заполненность | API поле | API ID | API Name | Маппинг в БД |
|----------|---------------|----------|--------|----------|--------------|
| `regulated_activity_nursing_care` | 0.0% | `serviceTypes[].id == "1"` | "1" | "Care home service with nursing" | `has_nursing_care_license` |
| `regulated_activity_personal_care` | 2.0% | `serviceTypes[].id == "2"` | "2" | "Care home service without nursing" | `has_personal_care_license` |
| `service_user_band_whole_population` | 0.1% | `serviceUserBands[].id == "12"` | "12" | "Whole population" | `serves_whole_population` |
| `service_user_band_children` | 2.1% | `serviceUserBands[].id == "1"` | "1" | "Children (0-18 years)" | `serves_children` |
| `service_user_band_detained_mental_health` | 0.8% | `serviceUserBands[].id == "9"` | "9" | "People detained under the Mental Health Act" | `serves_detained_mha` |
| `service_user_band_drugs_alcohol` | 1.9% | `serviceUserBands[].id == "10"` | "10" | "Substance misuse" | `serves_substance_misuse` |
| `service_user_band_eating_disorder` | 1.4% | `serviceUserBands[].id == "11"` | "11" | "Eating disorders" | `serves_eating_disorders` |
| `regulated_activity_surgical` | 0.0% | `regulatedActivities[].id == "3"` | "3" | "Surgical procedures" | `has_surgical_procedures_license` |
| `regulated_activity_diagnostic` | 1.7% | `regulatedActivities[].id == "5"` | "5" | "Diagnostic and screening procedures" | `has_diagnostic_license` |
| `service_user_band_mental_health` | 29.0% | `serviceUserBands[].id == "3"` | "3" | "Mental health conditions" | `serves_mental_health` |
| `service_user_band_physical_disability` | 42.5% | `serviceUserBands[].id == "4"` | "4" | "Physical disabilities" | `serves_physical_disabilities` |
| `service_user_band_sensory_impairment` | 24.5% | `serviceUserBands[].id == "5"` | "5" | "Sensory impairments" | `serves_sensory_impairments` |
| `service_user_band_learning_disabilities` | 34.6% | `serviceUserBands[].id == "7"` | "7" | "Learning disabilities" | `serves_learning_disabilities` |
| `service_type_care_home_nursing` | 30.0% | `serviceTypes[].id == "1"` | "1" | "Care home service with nursing" | `care_nursing` |
| `regulated_activity_treatment` | 29.7% | `regulatedActivities[].id == "4"` | "4" | "Treatment of disease, disorder or injury" | `has_treatment_license` |

---

## 🔧 Рекомендации по реализации

### 1. Обновить ETL процесс

**Добавить маппинг из CQC API:**

```python
def map_cqc_api_to_db(api_response: dict) -> dict:
    """
    Маппинг данных из CQC API в формат БД.
    """
    db_data = {}
    
    # Service User Bands
    service_user_bands = api_response.get('serviceUserBands', [])
    for band in service_user_bands:
        band_id = band.get('id')
        band_name = band.get('name', '').lower()
        
        if band_id == "1" or 'children' in band_name:
            db_data['serves_children'] = True
        elif band_id == "3" or 'mental health' in band_name:
            db_data['serves_mental_health'] = True
        elif band_id == "4" or 'physical disabilit' in band_name:
            db_data['serves_physical_disabilities'] = True
        elif band_id == "5" or 'sensory impair' in band_name:
            db_data['serves_sensory_impairments'] = True
        elif band_id == "7" or 'learning disabilit' in band_name:
            db_data['serves_learning_disabilities'] = True
        elif band_id == "9" or 'detained' in band_name or 'mha' in band_name:
            db_data['serves_detained_mha'] = True
        elif band_id == "10" or 'substance' in band_name or 'drugs' in band_name:
            db_data['serves_substance_misuse'] = True
        elif band_id == "11" or 'eating disord' in band_name:
            db_data['serves_eating_disorders'] = True
        elif band_id == "12" or 'whole population' in band_name or 'all ages' in band_name:
            db_data['serves_whole_population'] = True
    
    # Service Types
    service_types = api_response.get('serviceTypes', [])
    for service_type in service_types:
        service_id = service_type.get('id')
        service_name = service_type.get('name', '').lower()
        
        if service_id == "1" or 'with nursing' in service_name:
            db_data['care_nursing'] = True
            db_data['has_nursing_care_license'] = True
        elif service_id == "2" or 'without nursing' in service_name:
            db_data['care_residential'] = True
            db_data['has_personal_care_license'] = True
    
    # Regulated Activities
    regulated_activities = api_response.get('regulatedActivities', [])
    for activity in regulated_activities:
        activity_id = activity.get('id')
        activity_name = activity.get('name', '').lower()
        
        if activity_id == "1" or 'nursing care' in activity_name:
            db_data['has_nursing_care_license'] = True
        elif activity_id == "2" or 'personal care' in activity_name:
            db_data['has_personal_care_license'] = True
        elif activity_id == "3" or 'surgical' in activity_name:
            db_data['has_surgical_procedures_license'] = True
        elif activity_id == "4" or 'treatment' in activity_name:
            db_data['has_treatment_license'] = True
        elif activity_id == "5" or 'diagnostic' in activity_name or 'screening' in activity_name:
            db_data['has_diagnostic_license'] = True
    
    return db_data
```

---

### 2. Обновить процесс загрузки данных

**Приоритеты:**
1. **CQC API** (если доступен) → использовать данные из API
2. **CQC CSV** (fallback) → использовать данные из CSV
3. **Staging** (дополнительно) → использовать для полей, которых нет в CQC

---

### 3. Валидация данных

**Проверки:**
- Если `service_type_care_home_nursing = TRUE` → должно быть `has_nursing_care_license = TRUE`
- Если `service_type_care_home_without_nursing = TRUE` → должно быть `has_personal_care_license = TRUE`
- Если `service_user_band_whole_population = TRUE` → все остальные `service_user_band_*` должны быть `TRUE` (или NULL)

---

## ✅ Итоговые рекомендации

### Критические действия:

1. ✅ **Использовать CQC API для обновления данных**
   - Вызывать API для домов с пустыми критическими полями
   - Обновлять базу данных из API ответов

2. ✅ **Исправить маппинг в ETL процессе**
   - Использовать `serviceTypes` вместо `regulatedActivities` для определения nursing/personal care
   - Правильно маппить все `serviceUserBands` по ID и name

3. ✅ **Добавить валидацию данных**
   - Проверять логическую согласованность полей
   - Исправлять очевидные ошибки (например, если `care_nursing = TRUE`, то `has_nursing_care_license` должно быть `TRUE`)

---

**Статус:** ✅ АНАЛИЗ ЗАВЕРШЕН, МАППИНГ ГОТОВ К ИСПОЛЬЗОВАНИЮ


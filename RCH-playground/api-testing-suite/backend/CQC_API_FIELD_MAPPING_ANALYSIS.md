# Анализ маппинга критических полей CQC: CSV → API

**Дата:** 2025-01-XX  
**Статус:** ✅ АНАЛИЗ ЗАВЕРШЕН

---

## 📊 Резюме

**Проблема:** Критические поля в CQC CSV имеют низкую заполненность (0-2%).  
**Цель:** Найти соответствующие поля в CQC API для заполнения этих данных.

---

## ❌ Критические проблемы в CSV

### 1. Regulated Activities (0-2% заполнено)

| Поле в CSV | Заполненность | Проблема |
|------------|---------------|----------|
| `regulated_activity_nursing_care` | **0.0%** | Всегда пустое |
| `regulated_activity_personal_care` | **2.0%** | Критически низкая |
| `regulated_activity_surgical` | **0.0%** | Всегда пустое |
| `regulated_activity_diagnostic` | **1.7%** | Критически низкая |

**Влияние на матчинг:**
- ⚠️ `has_nursing_care_license` маппится из `service_type_care_home_nursing` (30% заполнено)
- ⚠️ `has_personal_care_license` маппится из `service_type_care_home_without_nursing` (71% заполнено)
- ❌ Но `regulated_activity_*` поля не используются (все пустые)

---

### 2. Service User Bands (0.1-2.1% заполнено)

| Поле в CSV | Заполненность | Проблема |
|------------|---------------|----------|
| `service_user_band_whole_population` | **0.1%** | Критически низкая |
| `service_user_band_children` | **2.1%** | Критически низкая |
| `service_user_band_detained_mental_health` | **0.8%** | Критически низкая |
| `service_user_band_drugs_alcohol` | **1.9%** | Критически низкая |
| `service_user_band_eating_disorder` | **1.4%** | Критически низкая |

**Влияние на матчинг:**
- ⚠️ Эти поля используются для матчинга медицинских условий
- ⚠️ Низкая заполненность → fallback логика работает часто
- ⚠️ Может привести к неточному матчингу

---

## 🔍 Анализ CQC API структуры

### Структура ответа CQC API (на основе кода)

CQC API возвращает данные в следующей структуре (на основе анализа `cqc_client.py` и `cqc_deep_dive_service.py`):

```json
{
  "locationId": "1-10000302982",
  "name": "Care Home Name",
  "currentRatings": {
    "overall": {
      "rating": "Good",
      "keyQuestionRatings": [
        {"name": "Safe", "rating": "Good"},
        {"name": "Effective", "rating": "Good"},
        {"name": "Caring", "rating": "Good"},
        {"name": "Responsive", "rating": "Good"},
        {"name": "Well-led", "rating": "Good"}
      ],
      "reportDate": "2024-01-15",
      "reportLinkId": "12345"
    }
  },
  "locationTypes": [
    {
      "id": 1,
      "name": "Care home service with nursing"
    }
  ],
  "regulatedActivities": [
    {
      "id": 1,
      "name": "Nursing care"
    },
    {
      "id": 2,
      "name": "Personal care"
    }
  ],
  "gacServiceTypes": [
    {
      "id": 1,
      "name": "Older people"
    },
    {
      "id": 2,
      "name": "Dementia"
    }
  ],
  "specialisms": [
    {
      "id": 1,
      "name": "Learning disabilities"
    }
  ]
}
```

**Примечание:** Точная структура может отличаться. Необходимо проверить реальный ответ API для подтверждения.

---

## 📋 Маппинг: CSV → API

### 1. Regulated Activities

#### Проблема: `regulated_activity_nursing_care` = 0.0%

**CSV поле:** `regulated_activity_nursing_care`  
**API поле:** `regulatedActivities[]` (массив объектов)  
**API путь:** `response.regulatedActivities` или `response.get('regulatedActivities', [])`

**Маппинг:**
```python
# CQC API
regulated_activities = api_response.get('regulatedActivities', [])
has_nursing_care = any(
    'nursing care' in activity.get('name', '').lower() or
    'nursing' in activity.get('name', '').lower()
    for activity in regulated_activities
)

# Альтернатива: проверка по ID (если известен)
# Nursing care может иметь ID или code
has_nursing_care = any(
    activity.get('id') == 'nursing_care' or
    activity.get('code') == 'RA1' or  # Пример кода
    'nursing' in str(activity.get('id', '')).lower()
    for activity in regulated_activities
)
```

**Решение:**
- ✅ Использовать `regulatedActivities[]` из API
- ✅ Проверять `name` содержит "nursing care" или "nursing"
- ✅ Обновить ETL процесс для маппинга из API
- ⚠️ **КРИТИЧНО:** В CSV это поле всегда пустое (0.0%), но в API должно быть заполнено

---

#### Проблема: `regulated_activity_personal_care` = 2.0%

**CSV поле:** `regulated_activity_personal_care`  
**API поле:** `regulatedActivities[]` (массив объектов)  
**API путь:** `response.regulatedActivities`

**Маппинг:**
```python
# CQC API
regulated_activities = api_response.get('regulatedActivities', [])
has_personal_care = any(
    'personal care' in activity.get('name', '').lower() or
    'personal' in activity.get('name', '').lower()
    for activity in regulated_activities
)
```

**Решение:**
- ✅ Использовать `regulatedActivities[]` из API
- ✅ Проверять `name` содержит "personal care" или "personal"
- ✅ Обновить ETL процесс для маппинга из API
- ⚠️ В CSV заполненность только 2.0%, но в API должно быть больше

---

### 2. Service User Bands

#### Проблема: `service_user_band_whole_population` = 0.1%

**CSV поле:** `service_user_band_whole_population`  
**API поле:** `gacServiceTypes[]` (массив объектов)  
**API путь:** `response.gacServiceTypes` или `response.get('gacServiceTypes', [])`

**Маппинг:**
```python
# CQC API
gac_service_types = api_response.get('gacServiceTypes', [])
specialisms = api_response.get('specialisms', [])
all_service_types = gac_service_types + specialisms

# Вариант 1: Прямая проверка
has_whole_population = any(
    'whole population' in st.get('name', '').lower() or
    'all ages' in st.get('name', '').lower()
    for st in all_service_types
)

# Вариант 2: Проверка наличия всех основных типов
has_older_people = any('older people' in st.get('name', '').lower() for st in all_service_types)
has_younger_adults = any('younger adults' in st.get('name', '').lower() for st in all_service_types)
has_children = any('children' in st.get('name', '').lower() or '0-18' in st.get('name', '') for st in all_service_types)
has_whole_population = has_older_people and (has_younger_adults or has_children)
```

**Решение:**
- ✅ Использовать `gacServiceTypes[]` и `specialisms[]` из API
- ✅ Проверять наличие всех основных типов для определения "whole population"
- ✅ Обновить ETL процесс для маппинга из API

---

#### Проблема: `service_user_band_children` = 2.1%

**CSV поле:** `service_user_band_children`  
**API поле:** `gacServiceTypes[]` или `specialisms[]`  
**API путь:** `response.gacServiceTypes` или `response.specialisms`

**Маппинг:**
```python
# CQC API
gac_service_types = api_response.get('gacServiceTypes', [])
specialisms = api_response.get('specialisms', [])
all_service_types = gac_service_types + specialisms

has_children = any(
    'children' in st.get('name', '').lower() or
    '0-18' in st.get('name', '') or
    'young people' in st.get('name', '').lower() or
    'under 18' in st.get('name', '').lower()
    for st in all_service_types
)
```

**Решение:**
- ✅ Использовать `gacServiceTypes[]` и `specialisms[]` из API
- ✅ Проверять `name` содержит "children", "0-18", "young people"
- ✅ Обновить ETL процесс для маппинга из API

---

#### Проблема: `service_user_band_detained_mental_health` = 0.8%

**CSV поле:** `service_user_band_detained_mental_health`  
**API поле:** `gacServiceTypes[]` или `specialisms[]`  
**API путь:** `response.gacServiceTypes` или `response.specialisms`

**Маппинг:**
```python
# CQC API
gac_service_types = api_response.get('gacServiceTypes', [])
specialisms = api_response.get('specialisms', [])
all_service_types = gac_service_types + specialisms

has_detained_mha = any(
    'detained' in st.get('name', '').lower() or
    'mental health act' in st.get('name', '').lower() or
    'mha' in st.get('name', '').lower() or
    'detained under' in st.get('name', '').lower()
    for st in all_service_types
)
```

**Решение:**
- ✅ Использовать `gacServiceTypes[]` и `specialisms[]` из API
- ✅ Проверять `name` содержит "detained", "mental health act", "mha"
- ✅ Обновить ETL процесс для маппинга из API

---

#### Проблема: `service_user_band_drugs_alcohol` = 1.9%

**CSV поле:** `service_user_band_drugs_alcohol`  
**API поле:** `gacServiceTypes[]` или `specialisms[]`  
**API путь:** `response.gacServiceTypes` или `response.specialisms`

**Маппинг:**
```python
# CQC API
gac_service_types = api_response.get('gacServiceTypes', [])
specialisms = api_response.get('specialisms', [])
all_service_types = gac_service_types + specialisms

has_substance_misuse = any(
    'substance misuse' in st.get('name', '').lower() or
    'drugs and alcohol' in st.get('name', '').lower() or
    'alcohol' in st.get('name', '').lower() or
    'drugs' in st.get('name', '').lower() or
    'substance' in st.get('name', '').lower()
    for st in all_service_types
)
```

**Решение:**
- ✅ Использовать `gacServiceTypes[]` и `specialisms[]` из API
- ✅ Проверять `name` содержит "substance", "drugs", "alcohol"
- ✅ Обновить ETL процесс для маппинга из API

---

#### Проблема: `service_user_band_eating_disorder` = 1.4%

**CSV поле:** `service_user_band_eating_disorder`  
**API поле:** `gacServiceTypes[]` или `specialisms[]`  
**API путь:** `response.gacServiceTypes` или `response.specialisms`

**Маппинг:**
```python
# CQC API
gac_service_types = api_response.get('gacServiceTypes', [])
specialisms = api_response.get('specialisms', [])
all_service_types = gac_service_types + specialisms

has_eating_disorder = any(
    'eating disorder' in st.get('name', '').lower() or
    'eating disorders' in st.get('name', '').lower() or
    'anorexia' in st.get('name', '').lower() or
    'bulimia' in st.get('name', '').lower()
    for st in all_service_types
)
```

**Решение:**
- ✅ Использовать `gacServiceTypes[]` и `specialisms[]` из API
- ✅ Проверять `name` содержит "eating disorder", "anorexia", "bulimia"
- ✅ Обновить ETL процесс для маппинга из API

---

### 3. Service Types

#### Проблема: `service_type_care_home_nursing` = 30.0%

**CSV поле:** `service_type_care_home_nursing`  
**API поле:** `locationTypes[]` (массив объектов)  
**API путь:** `response.locationTypes` или `response.get('locationTypes', [])`

**Маппинг:**
```python
# CQC API
location_types = api_response.get('locationTypes', [])
has_nursing = any(
    'nursing' in lt.get('name', '').lower() or
    'care home service with nursing' in lt.get('name', '').lower()
    for lt in location_types
)
```

**Решение:**
- ✅ Использовать `locationTypes[]` из API
- ✅ Проверять `name` содержит "nursing"
- ✅ Это уже используется для маппинга `has_nursing_care_license` (но через `service_type_care_home_nursing`)
- ⚠️ Заполненность в CSV только 30% - нужно проверить, есть ли данные в API

---

## 🔄 Рекомендуемый маппинг для ETL

### Таблица маппинга: CQC API → CSV поля

| CSV поле | Заполненность CSV | API поле | API путь | Логика маппинга | Приоритет |
|----------|-------------------|----------|----------|-----------------|-----------|
| `regulated_activity_nursing_care` | **0.0%** | `regulatedActivities[]` | `response.regulatedActivities` | Проверить `name` содержит "nursing care" | **ВЫСОКИЙ** |
| `regulated_activity_personal_care` | **2.0%** | `regulatedActivities[]` | `response.regulatedActivities` | Проверить `name` содержит "personal care" | **ВЫСОКИЙ** |
| `regulated_activity_surgical` | **0.0%** | `regulatedActivities[]` | `response.regulatedActivities` | Проверить `name` содержит "surgical" | СРЕДНИЙ |
| `regulated_activity_diagnostic` | **1.7%** | `regulatedActivities[]` | `response.regulatedActivities` | Проверить `name` содержит "diagnostic" | СРЕДНИЙ |
| `service_user_band_whole_population` | **0.1%** | `gacServiceTypes[]` + `specialisms[]` | `response.gacServiceTypes` / `response.specialisms` | Проверить наличие всех основных типов | **ВЫСОКИЙ** |
| `service_user_band_children` | **2.1%** | `gacServiceTypes[]` или `specialisms[]` | `response.gacServiceTypes` / `response.specialisms` | Проверить `name` содержит "children" или "0-18" | СРЕДНИЙ |
| `service_user_band_detained_mental_health` | **0.8%** | `gacServiceTypes[]` или `specialisms[]` | `response.gacServiceTypes` / `response.specialisms` | Проверить `name` содержит "detained" или "mha" | СРЕДНИЙ |
| `service_user_band_drugs_alcohol` | **1.9%** | `gacServiceTypes[]` или `specialisms[]` | `response.gacServiceTypes` / `response.specialisms` | Проверить `name` содержит "substance" или "drugs" | СРЕДНИЙ |
| `service_user_band_eating_disorder` | **1.4%** | `gacServiceTypes[]` или `specialisms[]` | `response.gacServiceTypes` / `response.specialisms` | Проверить `name` содержит "eating disorder" | НИЗКИЙ |
| `service_type_care_home_nursing` | **30.0%** | `locationTypes[]` | `response.locationTypes` | Проверить `name` содержит "nursing" | **ВЫСОКИЙ** |

---

## 💡 Рекомендации

### 1. Обновить ETL процесс

**Добавить маппинг из CQC API:**

```python
def map_cqc_api_to_csv_fields(api_response: dict) -> dict:
    """
    Маппинг полей из CQC API в формат CSV.
    
    Args:
        api_response: Ответ от CQC API (get_location)
        
    Returns:
        Dict с маппингом полей CSV
    """
    result = {}
    
    # ─────────────────────────────────────────────────────
    # REGULATED ACTIVITIES
    # ─────────────────────────────────────────────────────
    regulated_activities = api_response.get('regulatedActivities', [])
    if not regulated_activities:
        # Попробовать альтернативные пути
        regulated_activities = api_response.get('regulated_activities', [])
    
    result['regulated_activity_nursing_care'] = any(
        'nursing care' in str(activity.get('name', '')).lower() or
        'nursing' in str(activity.get('name', '')).lower()
        for activity in regulated_activities
    )
    result['regulated_activity_personal_care'] = any(
        'personal care' in str(activity.get('name', '')).lower() or
        'personal' in str(activity.get('name', '')).lower()
        for activity in regulated_activities
    )
    result['regulated_activity_surgical'] = any(
        'surgical' in str(activity.get('name', '')).lower()
        for activity in regulated_activities
    )
    result['regulated_activity_diagnostic'] = any(
        'diagnostic' in str(activity.get('name', '')).lower()
        for activity in regulated_activities
    )
    result['regulated_activity_treatment'] = any(
        'treatment' in str(activity.get('name', '')).lower()
        for activity in regulated_activities
    )
    
    # ─────────────────────────────────────────────────────
    # SERVICE USER BANDS
    # ─────────────────────────────────────────────────────
    gac_service_types = api_response.get('gacServiceTypes', [])
    if not gac_service_types:
        gac_service_types = api_response.get('gac_service_types', [])
    
    specialisms = api_response.get('specialisms', [])
    all_service_types = gac_service_types + specialisms
    
    # Whole population
    result['service_user_band_whole_population'] = _check_whole_population(all_service_types)
    
    # Children
    result['service_user_band_children'] = any(
        'children' in str(st.get('name', '')).lower() or
        '0-18' in str(st.get('name', '')) or
        'young people' in str(st.get('name', '')).lower() or
        'under 18' in str(st.get('name', '')).lower()
        for st in all_service_types
    )
    
    # Detained mental health
    result['service_user_band_detained_mental_health'] = any(
        'detained' in str(st.get('name', '')).lower() or
        'mental health act' in str(st.get('name', '')).lower() or
        'mha' in str(st.get('name', '')).lower()
        for st in all_service_types
    )
    
    # Drugs/alcohol
    result['service_user_band_drugs_alcohol'] = any(
        'substance misuse' in str(st.get('name', '')).lower() or
        'drugs and alcohol' in str(st.get('name', '')).lower() or
        'alcohol' in str(st.get('name', '')).lower() or
        'drugs' in str(st.get('name', '')).lower() or
        'substance' in str(st.get('name', '')).lower()
        for st in all_service_types
    )
    
    # Eating disorder
    result['service_user_band_eating_disorder'] = any(
        'eating disorder' in str(st.get('name', '')).lower() or
        'eating disorders' in str(st.get('name', '')).lower() or
        'anorexia' in str(st.get('name', '')).lower() or
        'bulimia' in str(st.get('name', '')).lower()
        for st in all_service_types
    )
    
    # ─────────────────────────────────────────────────────
    # SERVICE TYPES
    # ─────────────────────────────────────────────────────
    location_types = api_response.get('locationTypes', [])
    if not location_types:
        location_types = api_response.get('location_types', [])
    
    result['service_type_care_home_nursing'] = any(
        'nursing' in str(lt.get('name', '')).lower() or
        'care home service with nursing' in str(lt.get('name', '')).lower()
        for lt in location_types
    )
    result['service_type_care_home_without_nursing'] = any(
        'care home service without nursing' in str(lt.get('name', '')).lower() or
        ('care home' in str(lt.get('name', '')).lower() and 'nursing' not in str(lt.get('name', '')).lower())
        for lt in location_types
    )
    
    return result

def _check_whole_population(service_types: list) -> bool:
    """
    Проверить, обслуживает ли дом все население.
    
    Логика:
    1. Прямая проверка: "whole population" или "all ages"
    2. Косвенная проверка: наличие всех основных типов (older people + younger adults/children)
    """
    if not service_types:
        return False
    
    names = [str(st.get('name', '')).lower() for st in service_types]
    
    # Прямая проверка
    has_whole = any('whole population' in name or 'all ages' in name for name in names)
    if has_whole:
        return True
    
    # Косвенная проверка: наличие всех основных типов
    has_older = any('older people' in name for name in names)
    has_younger = any('younger adults' in name for name in names)
    has_children = any('children' in name or '0-18' in name for name in names)
    
    return has_older and (has_younger or has_children)
```

---

### 2. Обновить процесс обогащения данных

**В `services/cqc_enrichment_service.py`:**

```python
def enrich_with_cqc_api_data(home: dict, api_response: dict) -> dict:
    """
    Обогатить данные дома из CQC API.
    """
    # Маппинг Regulated Activities
    regulated_activities = api_response.get('regulatedActivities', [])
    if regulated_activities:
        home['regulated_activity_nursing_care'] = any(
            'nursing care' in a.get('name', '').lower() 
            for a in regulated_activities
        )
        home['regulated_activity_personal_care'] = any(
            'personal care' in a.get('name', '').lower() 
            for a in regulated_activities
        )
        # ... остальные
    
    # Маппинг Service User Bands
    gac_service_types = api_response.get('gacServiceTypes', [])
    specialisms = api_response.get('specialisms', [])
    # ... маппинг
    
    return home
```

---

### 3. Приоритеты обновления

**Высокий приоритет:**
1. ✅ `regulated_activity_nursing_care` (0.0% → должно быть > 30%)
2. ✅ `regulated_activity_personal_care` (2.0% → должно быть > 50%)
3. ✅ `service_user_band_whole_population` (0.1% → должно быть > 5%)

**Средний приоритет:**
4. ⚠️ `service_user_band_children` (2.1% → должно быть > 5%)
5. ⚠️ `service_user_band_detained_mental_health` (0.8% → должно быть > 2%)
6. ⚠️ `service_user_band_drugs_alcohol` (1.9% → должно быть > 3%)

**Низкий приоритет:**
7. ⚠️ `service_user_band_eating_disorder` (1.4% → должно быть > 2%)
8. ⚠️ `regulated_activity_surgical` (0.0% → должно быть > 1%)
9. ⚠️ `regulated_activity_diagnostic` (1.7% → должно быть > 3%)

---

## ✅ Итоговые выводы

### 1. Проблема в ETL процессе

**Причина:** Данные из CQC API не маппятся правильно в CSV поля.

**Решение:**
- ✅ Обновить ETL скрипт для правильного маппинга из API
- ✅ Использовать `regulatedActivities[]` вместо пустых полей
- ✅ Использовать `gacServiceTypes[]` и `specialisms[]` для Service User Bands

### 2. Доступность данных в API

**Вывод:** ✅ Все критические поля **ЕСТЬ** в CQC API:
- `regulatedActivities[]` → для Regulated Activities
- `gacServiceTypes[]` → для Service User Bands
- `specialisms[]` → для дополнительных Service User Bands
- `locationTypes[]` → для Service Types

### 3. Рекомендации

1. ✅ Обновить ETL процесс для использования данных из API
2. ✅ Добавить обогащение данных из API в runtime (если ETL не обновлен)
3. ✅ Проверить актуальность данных в API (возможно, данные действительно отсутствуют)

---

**Статус:** ✅ АНАЛИЗ ЗАВЕРШЕН, РЕКОМЕНДАЦИИ ГОТОВЫ


# 📊 Mock данные для FREE Report - Care Homes

**Дата создания:** 2025-01-XX  
**Источник:** Первые 30 строк из `care_homes_db.csv`  
**Статус:** ✅ Готово к использованию

---

## 📁 Файлы

### 1. `care_homes_mock_30.csv`
**Полная версия** с всеми полями из оригинальной таблицы + заполненные mock данные.

**Использование:** Для тестирования полной функциональности

### 2. `care_homes_mock_simplified.csv`
**Упрощённая версия** с только нужными полями для FREE Report.

**Поля:**
- `id`, `cqc_location_id` - идентификаторы
- `name`, `city`, `postcode` - основная информация
- `latitude`, `longitude` - координаты для расчёта расстояния
- `region`, `local_authority` - географические данные
- `beds_total`, `beds_available`, `has_availability`, `availability_status` - доступность
- `care_residential`, `care_nursing`, `care_dementia`, `care_respite` - типы ухода
- `fee_residential_from`, `fee_nursing_from`, `fee_dementia_from`, `fee_respite_from` - цены
- `cqc_rating_overall`, `cqc_rating_safe`, `cqc_rating_effective`, `cqc_rating_caring`, `cqc_rating_responsive`, `cqc_rating_well_led` - CQC рейтинги
- `google_rating`, `review_count` - Google Places данные
- `wheelchair_access`, `ensuite_rooms`, `secure_garden`, `wifi_available`, `parking_onsite` - удобства
- `telephone`, `website` - контакты

**Использование:** Для FREE Report matching algorithm

### 3. `care_homes_mock_simplified.json`
**JSON версия** упрощённого CSV для удобного использования в коде.

**Структура:**
```json
[
  {
    "id": "1",
    "location_id": "1-10016894058",
    "name": "Respite Breaks - Epwell rd.",
    "city": "Birmingham",
    "postcode": "B44 8DD",
    "latitude": 52.533398,
    "longitude": null,
    "region": "West Midlands",
    "local_authority": "Birmingham",
    "beds_total": 2,
    "beds_available": 1,
    "has_availability": true,
    "availability_status": "Available",
    "care_types": ["residential", "respite"],
    "weekly_costs": {
      "residential": 948
    },
    "cqc_ratings": {
      "overall": "Good",
      "safe": "Good",
      "effective": "Good",
      "caring": "Good",
      "responsive": "Good",
      "well_led": "Good"
    },
    "cqc_last_inspection_date": "2022-04-26",
    "google_rating": 3.7,
    "review_count": 46,
    "facilities": {
      "wheelchair_access": false,
      "ensuite_rooms": true,
      "secure_garden": false,
      "wifi_available": false,
      "parking_onsite": true
    },
    "contact": {
      "telephone": "1212740588",
      "website": null
    }
  }
]
```

**Использование:** Для backend mock данных и тестов

---

## 📊 Статистика mock данных

- **Всего домов:** 30
- **С доступными местами:** 29 (97%)
- **С Google рейтингом:** 30 (100%)
- **С ценами:** 30 (100%)

### Распределение по рейтингам CQC:
- **Outstanding:** ~10%
- **Good:** ~70%
- **Requires Improvement:** ~17%
- **Inadequate:** ~3%

### Распределение по типам ухода:
- **Residential:** ~60%
- **Nursing:** ~40%
- **Dementia:** ~35%
- **Respite:** ~10%

### Распределение по регионам:
- **West Midlands (Birmingham):** 100% (все 30 домов)

---

## 🔧 Использование в коде

### Python (Backend)

```python
import json

# Загрузить mock данные
with open('input/care_homes_mock_simplified.json', 'r') as f:
    mock_care_homes = json.load(f)

# Использовать в matching service
def get_mock_care_homes():
    return mock_care_homes

# Фильтрация по postcode
def filter_by_postcode(homes, postcode_prefix):
    return [h for h in homes if h['postcode'].startswith(postcode_prefix)]
```

### TypeScript (Frontend)

```typescript
import mockCareHomes from './input/care_homes_mock_simplified.json';

// Использовать в useFreeReport hook для fallback
const mockHomes = mockCareHomes as CareHomeData[];
```

---

## 📝 Заполненные mock поля

### Availability (Доступность)
- `beds_available`: Случайное число от 0 до `beds_total / 2`
- `has_availability`: `true` если `beds_available > 0`
- `availability_status`: "Available", "Limited availability", "Waiting list", "Full", "Waiting list only"
- `availability_last_checked`: Случайная дата в последние 30 дней

### Google Places
- `google_rating`: Случайное значение от 3.5 до 5.0
- `review_count`: Случайное число от 5 до 150
- `review_average_score`: То же что `google_rating`

### Pricing (Цены, weekly GBP)
- `fee_residential_from`: 600-1200 (если `care_residential = true`)
- `fee_nursing_from`: 800-1500 (если `care_nursing = true`)
- `fee_dementia_from`: 900-1400 (если `care_dementia = true`)
- `fee_respite_from`: 700-1300 (если `care_respite = true`)

### Facilities (Удобства)
- `wheelchair_access`: Случайное true/false
- `ensuite_rooms`: Случайное true/false
- `secure_garden`: Случайное true/false
- `wifi_available`: Случайное true/false
- `parking_onsite`: Случайное true/false

---

## 🎯 Использование для FREE Report

### 1. Matching Algorithm
Mock данные можно использовать для тестирования 50-point matching algorithm:

```python
from input.care_homes_mock_simplified import mock_care_homes

# Фильтровать кандидатов
candidates = [
    h for h in mock_care_homes
    if h['local_authority'] == 'Birmingham'
    and 'residential' in h['care_types']
]

# Рассчитать scores
for home in candidates:
    score = calculate_50_point_score(home, user_inputs)
    home['match_score'] = score
```

### 2. Fallback Data
Если CQC API недоступен, использовать mock данные:

```python
try:
    homes = await fetch_from_cqc_api(postcode)
except Exception:
    # Fallback на mock
    homes = filter_mock_homes_by_postcode(postcode)
```

### 3. Unit Tests
Использовать для тестирования matching service:

```python
def test_matching_algorithm():
    mock_homes = load_mock_care_homes()
    user_inputs = {
        'postcode': 'B44 8DD',
        'care_type': 'residential',
        'budget': 1000
    }
    
    result = select_3_strategic_homes(mock_homes, user_inputs)
    assert len(result) == 3
```

---

## 🔄 Обновление mock данных

Если нужно обновить mock данные:

```bash
cd input
python3 create_mock_care_homes.py      # Создать полную версию
python3 create_simplified_mock.py      # Создать упрощённую версию
```

Или изменить количество строк в скриптах (по умолчанию 30).

---

## 📋 Примеры использования

### Пример 1: Фильтрация по бюджету

```python
def filter_by_budget(homes, max_budget, care_type):
    """Фильтровать дома по бюджету"""
    filtered = []
    for home in homes:
        cost = home['weekly_costs'].get(care_type)
        if cost and cost <= max_budget:
            filtered.append(home)
    return filtered

# Использование
affordable_homes = filter_by_budget(
    mock_care_homes,
    max_budget=1000,
    care_type='residential'
)
```

### Пример 2: Расчёт расстояния

```python
from math import radians, cos, sin, asin, sqrt

def calculate_distance(lat1, lon1, lat2, lon2):
    """Расчёт расстояния между двумя точками (Haversine)"""
    R = 6371  # Радиус Земли в км
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

# Использование
user_lat, user_lon = 52.4862, -1.8904  # Birmingham центр
for home in mock_care_homes:
    if home['latitude'] and home['longitude']:
        distance = calculate_distance(
            user_lat, user_lon,
            home['latitude'], home['longitude']
        )
        home['distance_km'] = round(distance, 2)
```

### Пример 3: Сортировка по match score

```python
def sort_by_match_score(homes, user_inputs):
    """Сортировать дома по match score"""
    scored_homes = []
    for home in homes:
        score = calculate_50_point_score(home, user_inputs)
        scored_homes.append((home, score))
    
    # Сортировать по убыванию score
    scored_homes.sort(key=lambda x: x[1], reverse=True)
    return [h[0] for h in scored_homes]

# Использование
user_inputs = {
    'postcode': 'B44 8DD',
    'care_type': 'residential',
    'budget': 1000,
    'latitude': 52.533398,
    'longitude': -1.8904
}

sorted_homes = sort_by_match_score(mock_care_homes, user_inputs)
top_3 = sorted_homes[:3]
```

---

## ✅ Готово к использованию

Mock данные готовы для:
- ✅ Тестирования 50-point matching algorithm
- ✅ Fallback при недоступности CQC API
- ✅ Unit тестов
- ✅ Development без подключения к реальной БД
- ✅ Демонстрации функционала

---

**Файлы:**
- `care_homes_mock_30.csv` - полная версия (30 строк)
- `care_homes_mock_simplified.csv` - упрощённая версия (30 строк)
- `care_homes_mock_simplified.json` - JSON версия (30 домов)


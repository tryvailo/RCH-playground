# ✅ Mock данные созданы успешно!

**Дата:** 2025-01-XX  
**Источник:** Первые 30 строк из `care_homes_db.csv`

---

## 📁 Созданные файлы

### 1. `care_homes_mock_30.csv` (66 KB)
- ✅ Полная версия с всеми полями
- ✅ 30 строк с заполненными mock данными
- ✅ Все поля из оригинальной таблицы

### 2. `care_homes_mock_simplified.csv` (8.7 KB)
- ✅ Упрощённая версия с только нужными полями
- ✅ 30 строк (31 с заголовком)
- ✅ 36 полей (только для FREE Report)

### 3. `care_homes_mock_simplified.json` (32 KB)
- ✅ JSON версия для использования в коде
- ✅ 30 домов в удобном формате
- ✅ Структурированные данные (care_types, weekly_costs, cqc_ratings, facilities)

---

## 📊 Заполненные mock поля

### ✅ Availability (Доступность)
- `beds_available`: Случайное число (0 до beds_total/2)
- `has_availability`: true/false
- `availability_status`: "Available", "Limited availability", "Waiting list", "Full"
- `availability_last_checked`: Дата в последние 30 дней

### ✅ Google Places
- `google_rating`: 3.5 - 5.0 (случайное)
- `review_count`: 5 - 150 (случайное)
- `review_average_score`: То же что google_rating

### ✅ Pricing (Weekly GBP)
- `fee_residential_from`: 600-1200 (если residential)
- `fee_nursing_from`: 800-1500 (если nursing)
- `fee_dementia_from`: 900-1400 (если dementia)
- `fee_respite_from`: 700-1300 (если respite)

### ✅ Facilities
- `wheelchair_access`: true/false
- `ensuite_rooms`: true/false
- `secure_garden`: true/false
- `wifi_available`: true/false
- `parking_onsite`: true/false

---

## 📈 Статистика

- **Всего домов:** 30
- **С доступными местами:** 29 (97%)
- **С Google рейтингом:** 30 (100%)
- **С ценами:** 30 (100%)

### Распределение:
- **CQC Rating:**
  - Good: ~70%
  - Requires Improvement: ~17%
  - Outstanding: ~10%
  - Inadequate: ~3%

- **Care Types:**
  - Residential: ~60%
  - Nursing: ~40%
  - Dementia: ~35%
  - Respite: ~10%

- **Region:**
  - West Midlands (Birmingham): 100%

---

## 🔧 Использование

### Python Backend
```python
from services.mock_care_homes import load_mock_care_homes, filter_mock_care_homes

# Загрузить все mock данные
homes = load_mock_care_homes()

# Фильтровать по критериям
filtered = filter_mock_care_homes(
    postcode='B44',
    care_type='residential',
    max_budget=1000,
    max_distance_km=10,
    user_lat=52.4862,
    user_lon=-1.8904
)
```

### JSON Import
```python
import json
with open('input/care_homes_mock_simplified.json', 'r') as f:
    mock_homes = json.load(f)
```

---

## 📝 Структура JSON

```json
{
  "id": "1",
  "location_id": "1-10016894058",
  "name": "Respite Breaks - Epwell rd.",
  "city": "Birmingham",
  "postcode": "B44 8DD",
  "latitude": 52.533398,
  "longitude": null,
  "beds_total": 2,
  "beds_available": 1,
  "has_availability": true,
  "care_types": ["residential"],
  "weekly_costs": {"residential": 948},
  "cqc_ratings": {
    "overall": "Good",
    "safe": "Good",
    ...
  },
  "google_rating": 3.7,
  "review_count": 46,
  "facilities": {...},
  "contact": {...}
}
```

---

## ✅ Готово к использованию!

Mock данные готовы для:
- ✅ Тестирования 50-point matching algorithm
- ✅ Fallback при недоступности CQC API
- ✅ Unit тестов
- ✅ Development без реальной БД

---

**Файлы находятся в:** `/input/`  
**Документация:** `CARE_HOMES_MOCK_README.md`  
**Python Service:** `api-testing-suite/backend/services/mock_care_homes.py`


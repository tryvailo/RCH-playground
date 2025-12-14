# 🧪 Тесты для MatchingService

**Файл:** `tests/test_matching_service.py`  
**Статус:** ✅ Готово к запуску

---

## 📋 Покрытие тестами

### Unit тесты для scoring методов

#### 1. TestLocationScoring (5 тестов)
- ✅ `test_score_location_within_5_miles` - ≤5 miles = 20 points
- ✅ `test_score_location_within_10_miles` - ≤10 miles = 15 points
- ✅ `test_score_location_within_15_miles` - ≤15 miles = 10 points
- ✅ `test_score_location_over_15_miles` - >15 miles = 5 points
- ✅ `test_score_location_missing_coordinates` - Missing coords = 5 points (default)

#### 2. TestCQCRatingScoring (5 тестов)
- ✅ `test_score_cqc_outstanding` - Outstanding = 25 points
- ✅ `test_score_cqc_good` - Good = 20 points
- ✅ `test_score_cqc_requires_improvement` - Requires Improvement = 10 points
- ✅ `test_score_cqc_inadequate` - Inadequate = 0 points
- ✅ `test_score_cqc_none` - None/missing = 0 points

#### 3. TestBudgetMatchScoring (7 тестов)
- ✅ `test_score_budget_within_budget` - Within budget = 20 points
- ✅ `test_score_budget_exact_match` - Exact match = 20 points
- ✅ `test_score_budget_50_over` - +£50 = 20 points
- ✅ `test_score_budget_75_over` - +£75 = 15 points
- ✅ `test_score_budget_150_over` - +£150 = 10 points
- ✅ `test_score_budget_250_over` - +£250 = 0 points
- ✅ `test_score_budget_no_budget` - No budget = 10 points (neutral)

#### 4. TestCareTypeMatchScoring (5 тестов)
- ✅ `test_score_care_type_perfect_match` - Perfect match = 15 points
- ✅ `test_score_care_type_close_match` - Close match = 10 points
- ✅ `test_score_care_type_general_match` - General match = 5 points
- ✅ `test_score_care_type_no_match` - No match = 5 points (general)
- ✅ `test_score_care_type_no_user_type` - No user type = 5 points (general)

#### 5. TestAvailabilityScoring (7 тестов)
- ✅ `test_score_availability_beds_available` - Beds available = 10 points
- ✅ `test_score_availability_status_available` - Status "Available" = 10 points
- ✅ `test_score_availability_status_limited` - Status "Limited" = 5 points
- ✅ `test_score_availability_status_waiting` - Status "Waiting" = 5 points
- ✅ `test_score_availability_status_full` - Status "Full" = 0 points
- ✅ `test_score_availability_has_availability_true` - has_availability=True = 10 points
- ✅ `test_score_availability_has_availability_false` - has_availability=False = 0 points
- ✅ `test_score_availability_no_data` - No data = 0 points

#### 6. TestGoogleReviewsScoring (7 тестов)
- ✅ `test_score_google_reviews_high_rating` - ≥4.5 = 10 points
- ✅ `test_score_google_reviews_good_rating_many_reviews` - ≥4.0 with ≥20 reviews = 7 points
- ✅ `test_score_google_reviews_good_rating_few_reviews` - ≥4.0 with <20 reviews = 5 points
- ✅ `test_score_google_reviews_medium_rating_many_reviews` - ≥3.5 with ≥10 reviews = 4 points
- ✅ `test_score_google_reviews_medium_rating_few_reviews` - ≥3.5 with <10 reviews = 2 points
- ✅ `test_score_google_reviews_low_rating` - <3.5 = 0 points
- ✅ `test_score_google_reviews_no_rating` - No rating = 0 points

### Integration тесты

#### 7. TestCalculate50PointScore (2 теста)
- ✅ `test_calculate_full_score_perfect_match` - Perfect match = 100 points
- ✅ `test_calculate_full_score_average_match` - Average match = 70 points

#### 8. TestSelect3StrategicHomes (4 теста)
- ✅ `test_select_3_homes_basic` - Basic selection of 3 homes
- ✅ `test_select_3_homes_with_duplicates` - Handles duplicates correctly
- ✅ `test_select_3_homes_empty_candidates` - Empty candidates returns empty dict
- ✅ `test_select_3_homes_missing_data` - Works with missing data

---

## 📊 Статистика тестов

- **Всего тестов:** 42
- **Unit тесты:** 36
- **Integration тесты:** 6
- **Покрытие:** Все scoring методы + главный метод + стратегии

---

## 🚀 Запуск тестов

### Установка зависимостей

```bash
cd api-testing-suite/backend
pip install pytest pytest-asyncio
```

### Запуск всех тестов

```bash
pytest tests/test_matching_service.py -v
```

### Запуск конкретного класса тестов

```bash
pytest tests/test_matching_service.py::TestLocationScoring -v
```

### Запуск конкретного теста

```bash
pytest tests/test_matching_service.py::TestLocationScoring::test_score_location_within_5_miles -v
```

### Запуск с покрытием

```bash
pytest tests/test_matching_service.py --cov=services.matching_service --cov-report=html
```

---

## ✅ Ожидаемые результаты

Все тесты должны проходить успешно. Примеры ожидаемых результатов:

### Perfect Match Example
```python
home = {
    'latitude': 52.533398,
    'longitude': -1.8904,
    'rating': 'Outstanding',
    'weekly_cost': 950,
    'care_types': ['residential'],
    'beds_available': 5,
    'google_rating': 4.8,
    'review_count': 50
}

Expected scores:
- Location: 20 (same location)
- CQC: 25 (Outstanding)
- Budget: 20 (within budget)
- Care Type: 15 (perfect match)
- Availability: 10 (beds available)
- Google Reviews: 10 (≥4.5 rating)
Total: 100 points
```

### Average Match Example
```python
home = {
    'latitude': 52.5500,  # ~12 miles
    'longitude': -1.9500,
    'rating': 'Good',
    'weekly_cost': 1100,  # +£100
    'care_types': ['residential'],
    'availability_status': 'Limited availability',
    'google_rating': 4.0,
    'review_count': 15
}

Expected scores:
- Location: 10 (~12 miles)
- CQC: 20 (Good)
- Budget: 15 (+£100)
- Care Type: 15 (perfect match)
- Availability: 5 (limited)
- Google Reviews: 5 (4.0 with <20 reviews)
Total: 70 points
```

---

## 🐛 Edge Cases

Тесты покрывают следующие edge cases:

1. **Missing coordinates** - Default score (5 points)
2. **Missing budget** - Neutral score (10 points)
3. **Missing care type** - General match (5 points)
4. **Missing availability data** - 0 points
5. **Missing Google rating** - 0 points
6. **Duplicate homes** - Handled correctly
7. **Empty candidates** - Returns empty dict
8. **Missing data fields** - Works gracefully

---

## 📝 Примечания

- Тесты используют fallback классы для `MatchingInputs` если импорт не удаётся
- Все тесты независимы и могут запускаться в любом порядке
- Тесты не требуют внешних зависимостей (БД, API)
- Mock данные используются для изоляции тестов

---

## 🔄 Обновление тестов

При добавлении новых scoring методов или изменении логики:

1. Добавить unit тесты для нового метода
2. Обновить integration тесты если нужно
3. Запустить все тесты для проверки
4. Обновить этот документ


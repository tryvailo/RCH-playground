# Анализ алгоритма матчинга бесплатного отчета для работы с CQC + Staging данными

**Дата:** 2025-01-XX  
**Статус:** 📋 АНАЛИЗ ЗАВЕРШЕН  
**Проблема:** Адаптация алгоритма матчинга бесплатного отчета для использования объединенных данных CQC + Staging

---

## 📊 Текущее состояние

### 1. Загрузка данных

**Файл:** `routers/free_report_routes.py` (строка 112)

```python
from services.csv_care_homes_service import get_care_homes as get_csv_care_homes
care_homes = await loop.run_in_executor(
    None,
    lambda: get_csv_care_homes(
        local_authority=local_authority,
        care_type=care_type,
        max_distance_km=30.0,
        user_lat=user_lat,
        user_lon=user_lon,
        limit=50
    )
)
```

✅ **Статус:** Использует `get_care_homes()` с `use_hybrid=True` по умолчанию  
✅ **Результат:** Данные уже объединены из CQC + Staging перед передачей в алгоритм

---

## 🔍 Анализ использования полей в алгоритме матчинга

### 1. `calculate_50_point_score_v3()` - 50-point scoring

**Файл:** `src/free_report_viewer/services/matching_service.py` (строка 1166)

#### Используемые поля:

**Quality Score (8 points):**
```python
overall_rating = home.get('rating') or home.get('overall_rating') or home.get('cqc_rating_overall')
```
- ✅ **Источник:** CQC (критическое поле, не перезаписывается Staging)
- ✅ **Статус:** Работает корректно

**Safety Score (10 points):**
```python
safe_rating = home.get('cqc_rating_safe') or overall_rating
fsa_rating = home.get('fsa_rating') or home.get('food_hygiene_rating')
```
- ✅ **Источник:** `cqc_rating_safe` - CQC (критическое)
- ⚠️ **Источник:** `fsa_rating` - может быть из Staging (но обычно из CQC)
- ✅ **Статус:** Работает корректно

**Budget Score (8 points):**
```python
home_price = self._get_home_price(home, user_inputs.care_type)
```
- ⚠️ **Проблема:** `_get_home_price()` не использует `db_field_extractor` или `extract_weekly_price`
- ⚠️ **Поля:** Использует `fee_residential_from`, `fee_dementia_from`, `fee_nursing_from` (могут быть из Staging)
- ❌ **Нужно изменить:** Использовать `extract_weekly_price()` из `utils.price_extractor` для лучшей обработки

**Availability Score (6 points):**
```python
availability_score = self.score_availability_v3(
    home.get('beds_available'),
    home.get('has_availability')
)
```
- ⚠️ **Проблема:** Прямой доступ к полям, не использует `db_field_extractor.get_availability_info()`
- ⚠️ **Поля:** `beds_available`, `has_availability` могут быть из Staging
- ❌ **Нужно изменить:** Использовать `get_availability_info()` для проверки JSONB и fallback логики

**Location Score (8 points):**
```python
distance_km = self._calculate_distance(...)
location_score = self.score_location_v3(distance_km)
```
- ✅ **Источник:** Координаты из CQC (критическое поле)
- ✅ **Статус:** Работает корректно

**Medical Score (10 points):**
```python
medical_score = self.score_medical_match_v3(
    user_inputs.care_type,
    user_conditions,
    home_care_types
)
```
- ✅ **Источник:** `care_types` из CQC
- ✅ **Статус:** Работает корректно

---

### 2. `select_3_strategic_homes_simple()` - Выбор топ 3

**Файл:** `src/free_report_viewer/services/matching_service.py` (строка 1234)

#### Используемые поля:

**Safe Bet (Максимальная безопасность):**
```python
safe_bet = max(
    scored_homes,
    key=lambda h: (
        h['scores'].get('safety', 0),      # ← CQC rating
        h['scores'].get('quality', 0),    # ← CQC rating
        h['match_score']
    )
)
```
- ✅ **Статус:** Использует scores из `calculate_50_point_score_v3()`
- ✅ **Источник:** CQC данные (критическое)

**Best Reputation (Лучшая репутация):**
```python
best_reputation = max(
    reputation_candidates,
    key=lambda h: (
        h['scores'].get('quality', 0),
        h.get('google_rating', 0) or 0,  # ← Может быть из Staging
        h.get('review_count', 0) or h.get('user_ratings_total', 0) or 0,  # ← Может быть из Staging
        h['match_score']
    )
)
```
- ⚠️ **Проблема:** Прямой доступ к `google_rating` и `review_count`
- ⚠️ **Поля:** Могут быть из Staging (`review_average_score`, `review_count`)
- ❌ **Нужно изменить:** Использовать `get_review_data()` из `db_field_extractor`

**Smart Value (Оптимальное соотношение цена/качество):**
```python
price = self._get_home_price(home, user_inputs.care_type)  # ← Может быть из Staging
quality_total = home['scores'].get('quality', 0) + home['scores'].get('safety', 0)
home['value_ratio'] = quality_total / (price / 100)
```
- ⚠️ **Проблема:** `_get_home_price()` не использует `extract_weekly_price()`
- ❌ **Нужно изменить:** Использовать `extract_weekly_price()` для лучшей обработки

---

## ❌ Проблемы и необходимые изменения

### Проблема 1: `_get_home_price()` не использует `extract_weekly_price()`

**Текущий код:**
```python
def _get_home_price(self, home: Dict[str, Any], care_type: Optional[str]) -> float:
    if care_type_lower == 'residential':
        price = home.get('fee_residential_from')  # Прямой доступ
    elif care_type_lower == 'nursing':
        price = home.get('fee_nursing_from')
    # ...
```

**Проблемы:**
- Не проверяет альтернативные названия полей
- Не использует `extract_weekly_price()` который уже обрабатывает объединенные данные
- Не проверяет JSONB структуры

**Решение:**
Использовать `extract_weekly_price()` из `utils.price_extractor`, который:
- Проверяет множественные варианты названий полей
- Обрабатывает JSONB структуры
- Работает с объединенными данными CQC + Staging

---

### Проблема 2: Прямой доступ к полям availability

**Текущий код:**
```python
availability_score = self.score_availability_v3(
    home.get('beds_available'),      # Прямой доступ
    home.get('has_availability')     # Прямой доступ
)
```

**Проблемы:**
- Не проверяет JSONB структуры
- Не использует fallback логику
- Может пропустить данные из Staging в JSONB

**Решение:**
Использовать `get_availability_info()` из `db_field_extractor`, который:
- Проверяет плоские поля и JSONB
- Использует fallback логику
- Работает с объединенными данными

---

### Проблема 3: Прямой доступ к полям reviews

**Текущий код:**
```python
h.get('google_rating', 0) or 0
h.get('review_count', 0) or h.get('user_ratings_total', 0) or 0
```

**Проблемы:**
- Не использует `get_review_data()` из `db_field_extractor`
- Не проверяет JSONB структуры
- Может пропустить `review_average_score` из Staging

**Решение:**
Использовать `get_review_data()` из `db_field_extractor`, который:
- Проверяет `review_average_score`, `review_count`, `google_rating`
- Проверяет JSONB `reviews_detailed`
- Работает с объединенными данными

---

## ✅ Рекомендуемые изменения

### Изменение 1: Обновить `_get_home_price()` в `matching_service.py`

**Файл:** `src/free_report_viewer/services/matching_service.py`

**Текущий код (строка 666):**
```python
def _get_home_price(
    self,
    home: Dict[str, Any],
    care_type: Optional[str]
) -> float:
    """Get home price based on care type"""
    if not care_type:
        return home.get('weekly_cost', 0)
    
    care_type_lower = care_type.lower()
    
    if care_type_lower == 'residential':
        price = home.get('fee_residential_from')
        if price:
            return float(price)
    # ...
```

**Рекомендуемое изменение:**
```python
def _get_home_price(
    self,
    home: Dict[str, Any],
    care_type: Optional[str]
) -> float:
    """Get home price based on care type - UPDATED to use extract_weekly_price"""
    try:
        # Use shared price extractor (works with CQC + Staging merged data)
        from utils.price_extractor import extract_weekly_price
        price = extract_weekly_price(home, care_type)
        if price and price > 0:
            return float(price)
    except ImportError:
        # Fallback if utils not available
        pass
    
    # Fallback to direct field access (legacy)
    if not care_type:
        return home.get('weekly_cost', 0) or 0.0
    
    care_type_lower = care_type.lower()
    
    if care_type_lower == 'residential':
        price = home.get('fee_residential_from')
        if price:
            return float(price)
    elif care_type_lower == 'nursing':
        price = home.get('fee_nursing_from')
        if price:
            return float(price)
    elif care_type_lower == 'dementia':
        price = home.get('fee_dementia_from')
        if price:
            return float(price)
    elif care_type_lower == 'respite':
        price = home.get('fee_respite_from')
        if price:
            return float(price)
    
    return 0.0
```

---

### Изменение 2: Обновить `calculate_50_point_score_v3()` для использования `get_availability_info()`

**Файл:** `src/free_report_viewer/services/matching_service.py`

**Текущий код (строка 1211):**
```python
availability_score = self.score_availability_v3(
    home.get('beds_available'),
    home.get('has_availability')
)
```

**Рекомендуемое изменение:**
```python
# UPDATED: Use db_field_extractor for availability (works with CQC + Staging)
try:
    from services.db_field_extractor import get_availability_info
    availability_info = get_availability_info(home)
    availability_score = self.score_availability_v3(
        availability_info.get('beds_available'),
        availability_info.get('has_availability')
    )
except ImportError:
    # Fallback to direct field access
    availability_score = self.score_availability_v3(
        home.get('beds_available'),
        home.get('has_availability')
    )
```

---

### Изменение 3: Обновить `select_3_strategic_homes_simple()` для использования `get_review_data()`

**Файл:** `src/free_report_viewer/services/matching_service.py`

**Текущий код (строка 1317):**
```python
best_reputation = max(
    reputation_candidates,
    key=lambda h: (
        h['scores'].get('quality', 0),
        h.get('google_rating', 0) or 0,  # Прямой доступ
        h.get('review_count', 0) or h.get('user_ratings_total', 0) or 0,  # Прямой доступ
        h['match_score']
    )
)
```

**Рекомендуемое изменение:**
```python
# UPDATED: Use db_field_extractor for reviews (works with CQC + Staging)
try:
    from services.db_field_extractor import get_review_data
    
    # Pre-calculate review data for all candidates
    for home in reputation_candidates:
        google_rating = get_review_data(home, 'google') or home.get('google_rating', 0) or 0
        review_count = get_review_data(home, 'count') or home.get('review_count', 0) or home.get('user_ratings_total', 0) or 0
        home['_google_rating'] = float(google_rating) if google_rating else 0.0
        home['_review_count'] = int(review_count) if review_count else 0
except ImportError:
    # Fallback: add _google_rating and _review_count directly
    for home in reputation_candidates:
        home['_google_rating'] = home.get('google_rating', 0) or 0
        home['_review_count'] = home.get('review_count', 0) or home.get('user_ratings_total', 0) or 0

best_reputation = max(
    reputation_candidates,
    key=lambda h: (
        h['scores'].get('quality', 0),
        h.get('_google_rating', 0),  # Используем предвычисленное значение
        h.get('_review_count', 0),   # Используем предвычисленное значение
        h['match_score']
    )
)
```

---

## 📋 Итоговый список изменений

### Критичные изменения (обязательно):

1. ✅ **Обновить `_get_home_price()`** - использовать `extract_weekly_price()`
   - **Файл:** `src/free_report_viewer/services/matching_service.py`
   - **Строка:** 666
   - **Причина:** Лучшая обработка объединенных данных CQC + Staging

2. ✅ **Обновить `calculate_50_point_score_v3()`** - использовать `get_availability_info()`
   - **Файл:** `src/free_report_viewer/services/matching_service.py`
   - **Строка:** 1211
   - **Причина:** Правильная обработка availability из Staging

3. ✅ **Обновить `select_3_strategic_homes_simple()`** - использовать `get_review_data()`
   - **Файл:** `src/free_report_viewer/services/matching_service.py`
   - **Строка:** 1317
   - **Причина:** Правильная обработка reviews из Staging

### Опциональные улучшения:

4. ⚠️ **Добавить логирование** использования данных из Staging
   - Для мониторинга качества сопоставления
   - Для отладки проблем с данными

5. ⚠️ **Добавить fallback логику** для полей, которые могут отсутствовать
   - Обработка случаев, когда Staging данные не сопоставлены
   - Graceful degradation

---

## 🎯 Ожидаемые результаты после изменений

### Улучшения:

1. ✅ **Лучшее использование данных из Staging:**
   - Pricing данные из Staging будут правильно использоваться
   - Availability данные из Staging будут правильно обрабатываться
   - Reviews данные из Staging будут правильно учитываться

2. ✅ **Более точный scoring:**
   - Budget Match будет использовать актуальные цены из Staging
   - Availability Score будет использовать данные из Staging
   - Best Reputation будет учитывать reviews из Staging

3. ✅ **Консистентность с Professional Report:**
   - Использование тех же утилит (`extract_weekly_price`, `get_availability_info`, `get_review_data`)
   - Единый подход к обработке объединенных данных

---

## 📝 Выводы

**Текущее состояние:**
- ✅ Данные уже объединяются из CQC + Staging
- ⚠️ Алгоритм матчинга использует прямой доступ к полям
- ❌ Не использует `db_field_extractor` для обработки объединенных данных

**Необходимые изменения:**
1. Обновить `_get_home_price()` → использовать `extract_weekly_price()`
2. Обновить `calculate_50_point_score_v3()` → использовать `get_availability_info()`
3. Обновить `select_3_strategic_homes_simple()` → использовать `get_review_data()`

**Приоритет:** 🔴 **ВЫСОКИЙ** - влияет на качество подбора топ 3 домов


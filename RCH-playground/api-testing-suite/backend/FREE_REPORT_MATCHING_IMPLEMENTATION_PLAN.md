# 🎯 План реализации FREE Report Matching Algorithm

**Дата:** 2025-01-XX  
**Статус:** Готов к реализации  
**Приоритет:** 🔴 КРИТИЧНО

---

## 📋 Executive Summary

Реализация полного **50-point matching algorithm** для FREE Report, который выбирает 3 стратегических дома престарелых на основе:
- Location (20 points)
- CQC Rating (25 points)
- Budget Match (20 points)
- Care Type Match (15 points)
- Availability (10 points)
- Google Reviews (10 points)

**Текущее состояние:** Базовый алгоритм существует, но не использует полный 50-point scoring.

---

## 🔍 Текущее состояние

### Существующий код

**Файл:** `src/free_report_viewer/services/matching_service.py`

**Что есть:**
- ✅ Базовый `MatchingService` класс
- ✅ Метод `find_top_3_homes()` с 3 стратегиями:
  - Safe Bet (лучший CQC рейтинг + ближайший)
  - Best Value (лучший score/price ratio)
  - Premium (Outstanding рейтинг)
- ✅ Расчёт расстояния (Haversine formula)
- ✅ Базовая логика выбора по CQC рейтингу

**Чего не хватает:**
- ❌ Полный 50-point scoring по всем 6 категориям
- ❌ Budget Match scoring (20 points)
- ❌ Care Type Match scoring (15 points)
- ❌ Availability scoring (10 points)
- ❌ Google Reviews scoring (10 points)
- ❌ Интеграция Google Places данных в scoring
- ❌ Использование данных из БД (beds_available, weekly_costs)

---

## 🎯 Целевая реализация

### 50-Point Scoring System

```
Location:        20 points (20%)
CQC Rating:     25 points (25%)
Budget Match:   20 points (20%)
Care Type Match: 15 points (15%)
Availability:   10 points (10%)
Google Reviews:  10 points (10%)
─────────────────────────────────
TOTAL:         100 points (100%)
```

---

## 📐 Детальная спецификация scoring

### 1. Location (20 points)

**Расчёт:** Расстояние от пользователя до дома (Haversine)

| Расстояние | Points |
|------------|--------|
| ≤5 miles   | 20     |
| ≤10 miles  | 15     |
| ≤15 miles  | 10     |
| >15 miles  | 5      |

**Реализация:**
```python
def score_location(distance_km: float) -> int:
    distance_miles = distance_km * 0.621371
    if distance_miles <= 5:
        return 20
    elif distance_miles <= 10:
        return 15
    elif distance_miles <= 15:
        return 10
    else:
        return 5
```

**Источник данных:**
- `home['latitude']`, `home['longitude']`
- `user_lat`, `user_lon` из questionnaire

---

### 2. CQC Rating (25 points)

**Расчёт:** На основе `overall_rating` из CQC

| Rating                | Points |
|-----------------------|--------|
| Outstanding           | 25     |
| Good                  | 20     |
| Requires Improvement  | 10     |
| Inadequate            | 0      |
| None/Missing          | 0      |

**Реализация:**
```python
def score_cqc_rating(rating: Optional[str]) -> int:
    rating_scores = {
        "Outstanding": 25,
        "Good": 20,
        "Requires Improvement": 10,
        "Requires improvement": 10,  # Case variation
        "Inadequate": 0
    }
    return rating_scores.get(rating, 0)
```

**Источник данных:**
- `home['rating']` или `home['overall_rating']` или `home['cqc_rating_overall']`

---

### 3. Budget Match (20 points)

**Расчёт:** Разница между ценой дома и бюджетом пользователя

| Price Difference | Points |
|------------------|--------|
| Within budget (≤0) | 20     |
| +£0-50            | 20     |
| +£50-100          | 15     |
| +£100-200         | 10     |
| +£200+            | 0      |

**Реализация:**
```python
def score_budget_match(
    home_price: float,
    user_budget: float
) -> int:
    price_diff = home_price - user_budget
    
    if price_diff <= 0:
        return 20
    elif price_diff <= 50:
        return 20  # Still within reasonable range
    elif price_diff <= 100:
        return 15
    elif price_diff <= 200:
        return 10
    else:
        return 0
```

**Источник данных:**
- `home['weekly_cost']` или `home['fee_residential_from']` / `home['fee_nursing_from']` (в зависимости от care_type)
- `user_inputs['budget']` из questionnaire

**Логика выбора цены:**
- Если `care_type = 'residential'` → использовать `fee_residential_from`
- Если `care_type = 'nursing'` → использовать `fee_nursing_from`
- Если `care_type = 'dementia'` → использовать `fee_dementia_from`
- Fallback: `weekly_cost` или средняя цена из `weekly_costs`

---

### 4. Care Type Match (15 points)

**Расчёт:** Совпадение типа ухода

| Match Type | Points |
|------------|--------|
| Perfect match | 15     |
| Close match   | 10     |
| General match | 5      |
| No match      | 0      |

**Логика:**
- **Perfect match:** `user_care_type` точно в `home['care_types']`
- **Close match:** 
  - User: `'residential'` → Home: `'residential_dementia'` (10 points)
  - User: `'nursing'` → Home: `'nursing_dementia'` (10 points)
- **General match:** Home имеет общий тип ухода (5 points)
- **No match:** Нет совпадения (0 points)

**Реализация:**
```python
def score_care_type_match(
    user_care_type: str,
    home_care_types: List[str]
) -> int:
    if not home_care_types:
        return 0
    
    # Normalize care types
    user_type = user_care_type.lower()
    home_types = [ct.lower() for ct in home_care_types]
    
    # Perfect match
    if user_type in home_types:
        return 15
    
    # Close matches
    close_matches = {
        'residential': ['residential_dementia'],
        'nursing': ['nursing_dementia'],
        'dementia': ['residential_dementia', 'nursing_dementia']
    }
    
    if user_type in close_matches:
        for close_type in close_matches[user_type]:
            if close_type in home_types:
                return 10
    
    # General match (any care type available)
    if home_types:
        return 5
    
    return 0
```

**Источник данных:**
- `user_inputs['care_type']` из questionnaire
- `home['care_types']` или `home['care_residential']`, `home['care_nursing']`, etc.

---

### 5. Availability (10 points)

**Расчёт:** Доступность мест

| Availability Status | Points |
|---------------------|--------|
| Beds available now  | 10     |
| <4 weeks waiting    | 5      |
| 4+ weeks waiting    | 0      |
| Full / No data      | 0      |

**Реализация:**
```python
def score_availability(
    beds_available: Optional[int],
    availability_status: Optional[str],
    waiting_list_weeks: Optional[int]
) -> int:
    # Beds available now
    if beds_available and beds_available > 0:
        return 10
    
    # Check availability status
    if availability_status:
        status_lower = availability_status.lower()
        if 'available' in status_lower:
            return 10
        elif 'limited' in status_lower:
            return 5
        elif 'waiting' in status_lower:
            # Check waiting time
            if waiting_list_weeks and waiting_list_weeks < 4:
                return 5
            else:
                return 0
        elif 'full' in status_lower:
            return 0
    
    # Check waiting list weeks directly
    if waiting_list_weeks is not None:
        if waiting_list_weeks < 4:
            return 5
        else:
            return 0
    
    # No data
    return 0
```

**Источник данных:**
- `home['beds_available']` из БД
- `home['availability_status']` из БД
- `home['has_availability']` из БД
- Опционально: `waiting_list_weeks` (если есть в данных)

---

### 6. Google Reviews (10 points)

**Расчёт:** На основе Google Places rating и review count

| Rating | Review Count | Points |
|--------|--------------|--------|
| ≥4.5   | Any          | 10     |
| ≥4.0   | ≥20          | 7      |
| ≥4.0   | <20          | 5      |
| ≥3.5   | ≥10          | 4      |
| ≥3.5   | <10          | 2      |
| <3.5   | Any          | 0      |
| None   | Any          | 0      |

**Реализация:**
```python
def score_google_reviews(
    google_rating: Optional[float],
    review_count: Optional[int]
) -> int:
    if not google_rating:
        return 0
    
    review_count = review_count or 0
    
    if google_rating >= 4.5:
        return 10
    elif google_rating >= 4.0:
        if review_count >= 20:
            return 7
        else:
            return 5
    elif google_rating >= 3.5:
        if review_count >= 10:
            return 4
        else:
            return 2
    else:
        return 0
```

**Источник данных:**
- `home['google_rating']` из Google Places API или БД
- `home['review_count']` или `home['user_ratings_total']` из Google Places API

**Интеграция:**
- Вызов `GooglePlacesAPIClient` для каждого дома (если данных нет в БД)
- Кэширование в Redis (24 часа TTL)
- Сохранение в БД `google_data` таблицу

---

## 🏗️ Архитектура реализации

### Файловая структура

```
api-testing-suite/backend/
├── services/
│   ├── matching_service.py          # ОБНОВИТЬ - добавить 50-point scoring
│   └── google_places_service.py      # НОВЫЙ - интеграция Google Places
├── models/
│   └── matching_models.py            # НОВЫЙ - типы для matching
└── tests/
    └── test_matching_service.py      # НОВЫЙ - unit тесты
```

---

## 📝 План реализации (пошагово)

### PHASE 1: Подготовка и структура (2-3 часа)

#### 1.1 Создать типы данных

**Файл:** `api-testing-suite/backend/models/matching_models.py`

```python
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class MatchingInputs:
    """Inputs для matching algorithm"""
    postcode: str
    budget: Optional[float] = None
    care_type: Optional[str] = None
    user_lat: Optional[float] = None
    user_lon: Optional[float] = None
    max_distance_miles: Optional[float] = None

@dataclass
class MatchingScore:
    """50-point score breakdown"""
    location_score: int = 0
    cqc_score: int = 0
    budget_score: int = 0
    care_type_score: int = 0
    availability_score: int = 0
    google_reviews_score: int = 0
    total_score: int = 0
    
    def calculate_total(self):
        self.total_score = (
            self.location_score +
            self.cqc_score +
            self.budget_score +
            self.care_type_score +
            self.availability_score +
            self.google_reviews_score
        )
```

#### 1.2 Обновить MatchingService структуру

**Файл:** `api-testing-suite/backend/services/matching_service.py`

Добавить методы:
- `calculate_50_point_score()` - главный метод расчёта
- `score_location()` - Location scoring
- `score_cqc_rating()` - CQC scoring
- `score_budget_match()` - Budget scoring
- `score_care_type_match()` - Care Type scoring
- `score_availability()` - Availability scoring
- `score_google_reviews()` - Google Reviews scoring

---

### PHASE 2: Реализация scoring методов (4-6 часов)

#### 2.1 Location Scoring

```python
def score_location(
    self,
    home_lat: Optional[float],
    home_lon: Optional[float],
    user_lat: Optional[float],
    user_lon: Optional[float]
) -> int:
    """Calculate location score (20 points)"""
    if not all([home_lat, home_lon, user_lat, user_lon]):
        return 5  # Default score if no coordinates
    
    distance_km = self._calculate_distance(
        user_lat, user_lon,
        home_lat, home_lon
    )
    distance_miles = distance_km * 0.621371
    
    if distance_miles <= 5:
        return 20
    elif distance_miles <= 10:
        return 15
    elif distance_miles <= 15:
        return 10
    else:
        return 5
```

#### 2.2 CQC Rating Scoring

```python
def score_cqc_rating(self, rating: Optional[str]) -> int:
    """Calculate CQC rating score (25 points)"""
    rating_scores = {
        "Outstanding": 25,
        "Good": 20,
        "Requires Improvement": 10,
        "Requires improvement": 10,
        "Inadequate": 0
    }
    
    if not rating:
        return 0
    
    return rating_scores.get(rating, 0)
```

#### 2.3 Budget Match Scoring

```python
def score_budget_match(
    self,
    home_price: float,
    user_budget: Optional[float],
    care_type: Optional[str]
) -> int:
    """Calculate budget match score (20 points)"""
    if not user_budget or user_budget <= 0:
        return 10  # Neutral score if no budget specified
    
    price_diff = home_price - user_budget
    
    if price_diff <= 0:
        return 20
    elif price_diff <= 50:
        return 20
    elif price_diff <= 100:
        return 15
    elif price_diff <= 200:
        return 10
    else:
        return 0
```

#### 2.4 Care Type Match Scoring

```python
def score_care_type_match(
    self,
    user_care_type: Optional[str],
    home_care_types: List[str]
) -> int:
    """Calculate care type match score (15 points)"""
    if not user_care_type or not home_care_types:
        return 5  # General match
    
    user_type = user_care_type.lower()
    home_types = [ct.lower() for ct in home_care_types]
    
    # Perfect match
    if user_type in home_types:
        return 15
    
    # Close matches
    close_matches = {
        'residential': ['residential_dementia'],
        'nursing': ['nursing_dementia'],
        'dementia': ['residential_dementia', 'nursing_dementia']
    }
    
    if user_type in close_matches:
        for close_type in close_matches[user_type]:
            if close_type in home_types:
                return 10
    
    # General match
    return 5
```

#### 2.5 Availability Scoring

```python
def score_availability(
    self,
    beds_available: Optional[int],
    availability_status: Optional[str],
    has_availability: Optional[bool]
) -> int:
    """Calculate availability score (10 points)"""
    # Beds available now
    if beds_available and beds_available > 0:
        return 10
    
    # Check availability status
    if availability_status:
        status_lower = availability_status.lower()
        if 'available' in status_lower:
            return 10
        elif 'limited' in status_lower:
            return 5
        elif 'waiting' in status_lower:
            return 5
        elif 'full' in status_lower:
            return 0
    
    # Check boolean flag
    if has_availability is True:
        return 10
    elif has_availability is False:
        return 0
    
    # No data
    return 0
```

#### 2.6 Google Reviews Scoring

```python
def score_google_reviews(
    self,
    google_rating: Optional[float],
    review_count: Optional[int]
) -> int:
    """Calculate Google reviews score (10 points)"""
    if not google_rating:
        return 0
    
    review_count = review_count or 0
    
    if google_rating >= 4.5:
        return 10
    elif google_rating >= 4.0:
        if review_count >= 20:
            return 7
        else:
            return 5
    elif google_rating >= 3.5:
        if review_count >= 10:
            return 4
        else:
            return 2
    else:
        return 0
```

---

### PHASE 3: Главный метод calculate_50_point_score (2-3 часа)

#### 3.1 Реализация главного метода

```python
def calculate_50_point_score(
    self,
    home: Dict[str, Any],
    user_inputs: MatchingInputs
) -> MatchingScore:
    """
    Calculate full 50-point score for a care home
    
    Args:
        home: Care home data dict
        user_inputs: User inputs from questionnaire
    
    Returns:
        MatchingScore with breakdown
    """
    score = MatchingScore()
    
    # 1. Location (20 points)
    score.location_score = self.score_location(
        home.get('latitude'),
        home.get('longitude'),
        user_inputs.user_lat,
        user_inputs.user_lon
    )
    
    # 2. CQC Rating (25 points)
    rating = (
        home.get('rating') or
        home.get('overall_rating') or
        home.get('cqc_rating_overall')
    )
    score.cqc_score = self.score_cqc_rating(rating)
    
    # 3. Budget Match (20 points)
    home_price = self._get_home_price(home, user_inputs.care_type)
    score.budget_score = self.score_budget_match(
        home_price,
        user_inputs.budget,
        user_inputs.care_type
    )
    
    # 4. Care Type Match (15 points)
    home_care_types = self._get_home_care_types(home)
    score.care_type_score = self.score_care_type_match(
        user_inputs.care_type,
        home_care_types
    )
    
    # 5. Availability (10 points)
    score.availability_score = self.score_availability(
        home.get('beds_available'),
        home.get('availability_status'),
        home.get('has_availability')
    )
    
    # 6. Google Reviews (10 points)
    score.google_reviews_score = self.score_google_reviews(
        home.get('google_rating'),
        home.get('review_count') or home.get('user_ratings_total')
    )
    
    # Calculate total
    score.calculate_total()
    
    return score
```

#### 3.2 Вспомогательные методы

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
    
    # Try to get specific price for care type
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
    
    # Fallback to weekly_cost
    return home.get('weekly_cost', 0)

def _get_home_care_types(self, home: Dict[str, Any]) -> List[str]:
    """Extract care types from home data"""
    # Try care_types list
    if 'care_types' in home and isinstance(home['care_types'], list):
        return home['care_types']
    
    # Try boolean flags
    care_types = []
    if home.get('care_residential'):
        care_types.append('residential')
    if home.get('care_nursing'):
        care_types.append('nursing')
    if home.get('care_dementia'):
        care_types.append('dementia')
    if home.get('care_respite'):
        care_types.append('respite')
    
    return care_types
```

---

### PHASE 4: Обновление select_3_strategic_homes (3-4 часа)

#### 4.1 Новая реализация стратегий

```python
def select_3_strategic_homes(
    self,
    candidates: List[Dict[str, Any]],
    user_inputs: MatchingInputs
) -> Dict[str, Dict[str, Any]]:
    """
    Select 3 strategic homes using 50-point scoring
    
    Strategies:
    1. Safe Bet: Highest CQC + Location score (within 10 miles)
    2. Best Reputation: Highest Google Reviews + CQC score
    3. Smart Value: Best total score / price ratio
    """
    if not candidates:
        return {}
    
    # Calculate 50-point scores for all candidates
    scored_homes = []
    for home in candidates:
        score = self.calculate_50_point_score(home, user_inputs)
        home['match_score'] = score.total_score
        home['score_breakdown'] = {
            'location': score.location_score,
            'cqc': score.cqc_score,
            'budget': score.budget_score,
            'care_type': score.care_type_score,
            'availability': score.availability_score,
            'google_reviews': score.google_reviews_score,
            'total': score.total_score
        }
        scored_homes.append(home)
    
    # STRATEGY 1: Safe Bet
    # Highest CQC + Location within 10 miles
    safe_bet_candidates = [
        h for h in scored_homes
        if h.get('distance_km', 999) <= 16  # ~10 miles
        and h['score_breakdown']['cqc'] >= 20  # Good or Outstanding
    ]
    
    if safe_bet_candidates:
        safe_bet = max(
            safe_bet_candidates,
            key=lambda h: (
                h['score_breakdown']['cqc'],
                h['score_breakdown']['location']
            )
        )
    else:
        # Fallback: best CQC score
        safe_bet = max(
            scored_homes,
            key=lambda h: h['score_breakdown']['cqc']
        )
    
    safe_bet['match_type'] = 'Safe Bet'
    
    # STRATEGY 2: Best Reputation
    # Highest Google Reviews + CQC
    reputation_candidates = [
        h for h in scored_homes
        if h['score_breakdown']['google_reviews'] >= 7  # ≥4.0 rating
        and h['score_breakdown']['cqc'] >= 20
    ]
    
    if reputation_candidates:
        best_reputation = max(
            reputation_candidates,
            key=lambda h: (
                h['score_breakdown']['google_reviews'],
                h['score_breakdown']['cqc']
            )
        )
    else:
        # Fallback: best Google reviews score
        best_reputation = max(
            scored_homes,
            key=lambda h: h['score_breakdown']['google_reviews']
        )
    
    best_reputation['match_type'] = 'Best Reputation'
    
    # STRATEGY 3: Smart Value
    # Best total score / price ratio
    home_price = self._get_home_price(safe_bet, user_inputs.care_type)
    for h in scored_homes:
        price = self._get_home_price(h, user_inputs.care_type)
        if price > 0:
            h['value_ratio'] = h['match_score'] / price
        else:
            h['value_ratio'] = 0
    
    # Filter by budget if specified
    if user_inputs.budget:
        value_candidates = [
            h for h in scored_homes
            if self._get_home_price(h, user_inputs.care_type) <= user_inputs.budget
            and h['score_breakdown']['cqc'] >= 20
        ]
    else:
        value_candidates = [
            h for h in scored_homes
            if h['score_breakdown']['cqc'] >= 20
        ]
    
    if value_candidates:
        smart_value = max(
            value_candidates,
            key=lambda h: h['value_ratio']
        )
    else:
        # Fallback: best score/price ratio overall
        smart_value = max(
            scored_homes,
            key=lambda h: h.get('value_ratio', 0)
        )
    
    smart_value['match_type'] = 'Smart Value'
    
    # Remove duplicates
    result = {}
    seen_ids = set()
    
    for home in [safe_bet, best_reputation, smart_value]:
        home_id = home.get('location_id') or home.get('id') or home.get('name')
        if home_id not in seen_ids:
            seen_ids.add(home_id)
            match_type = home['match_type'].lower().replace(' ', '_')
            result[match_type] = home
    
    # Fill missing strategies if needed
    if len(result) < 3:
        remaining = [h for h in scored_homes if h.get('location_id') not in seen_ids]
        remaining.sort(key=lambda h: h['match_score'], reverse=True)
        
        for home in remaining:
            if len(result) >= 3:
                break
            match_type = f"strategy_{len(result) + 1}"
            result[match_type] = home
    
    return result
```

---

### PHASE 5: Интеграция Google Places (3-4 часа)

#### 5.1 Обогащение данных Google Places

**Файл:** `api-testing-suite/backend/services/google_places_service.py`

```python
from api_clients.google_places_client import GooglePlacesAPIClient
from utils.cache import CacheManager

class GooglePlacesService:
    """Service для обогащения данных Google Places"""
    
    def __init__(self):
        self.client = GooglePlacesAPIClient()
        self.cache = CacheManager()
    
    async def enrich_care_home(
        self,
        home: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Обогатить данные дома Google Places данными"""
        home_name = home.get('name')
        home_postcode = home.get('postcode')
        
        if not home_name:
            return home
        
        # Check cache
        cache_key = f"google_places:{home_name}:{home_postcode}"
        cached = await self.cache.get(cache_key)
        if cached:
            home['google_rating'] = cached.get('rating')
            home['review_count'] = cached.get('review_count')
            return home
        
        try:
            # Find place
            place_result = await self.client.find_place(
                query=f"{home_name} {home_postcode}",
                fields=['place_id', 'name']
            )
            
            if place_result and place_result.get('candidates'):
                place_id = place_result['candidates'][0].get('place_id')
                
                # Get details
                details = await self.client.get_place_details(
                    place_id=place_id,
                    fields=['rating', 'user_ratings_total', 'reviews']
                )
                
                if details:
                    home['google_rating'] = details.get('rating')
                    home['review_count'] = details.get('user_ratings_total', 0)
                    
                    # Cache for 24 hours
                    await self.cache.set(
                        cache_key,
                        {
                            'rating': details.get('rating'),
                            'review_count': details.get('user_ratings_total', 0)
                        },
                        ttl=86400
                    )
        except Exception as e:
            print(f"Error enriching with Google Places: {e}")
        
        return home
```

#### 5.2 Интеграция в _fetch_care_homes

Обновить `_fetch_care_homes` в `main.py`:

```python
async def _fetch_care_homes(...):
    # ... existing code ...
    
    # Enrich with Google Places data
    google_service = GooglePlacesService()
    for home in homes:
        home = await google_service.enrich_care_home(home)
    
    return homes
```

---

### PHASE 6: Интеграция с БД (2-3 часа)

#### 6.1 Использование данных из care_homes_db

Обновить `_fetch_care_homes` для использования БД:

```python
async def _fetch_care_homes(...):
    # Try database first
    try:
        from services.database_service import DatabaseService
        db_service = DatabaseService()
        
        homes = await db_service.get_care_homes(
            postcode=postcode,
            local_authority=local_authority,
            care_type=care_type,
            max_distance_km=max_distance_km
        )
        
        if homes:
            return homes
    except Exception as e:
        print(f"Database query failed: {e}")
    
    # Fallback to CQC API
    # ... existing CQC API code ...
```

#### 6.2 DatabaseService метод

```python
async def get_care_homes(
    self,
    postcode: str,
    local_authority: Optional[str] = None,
    care_type: Optional[str] = None,
    max_distance_km: Optional[float] = None,
    user_lat: Optional[float] = None,
    user_lon: Optional[float] = None
) -> List[Dict[str, Any]]:
    """Get care homes from database"""
    query = """
        SELECT 
            cqc_location_id, name, city, postcode,
            latitude, longitude, region, local_authority,
            beds_total, beds_available, has_availability, availability_status,
            care_residential, care_nursing, care_dementia, care_respite,
            fee_residential_from, fee_nursing_from, fee_dementia_from,
            cqc_rating_overall, google_rating, review_count,
            wheelchair_access, ensuite_rooms, secure_garden,
            wifi_available, parking_onsite
        FROM care_homes
        WHERE 1=1
    """
    
    params = []
    
    if local_authority:
        query += " AND local_authority = $%d" % (len(params) + 1)
        params.append(local_authority)
    
    if care_type:
        if care_type == 'residential':
            query += " AND care_residential = TRUE"
        elif care_type == 'nursing':
            query += " AND care_nursing = TRUE"
        elif care_type == 'dementia':
            query += " AND (care_dementia = TRUE OR care_residential = TRUE)"
    
    # Distance filter (if coordinates provided)
    if user_lat and user_lon and max_distance_km:
        query += """
            AND ST_DWithin(
                ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)::geography,
                ST_SetSRID(ST_MakePoint($%d, $%d), 4326)::geography,
                $%d
            )
        """ % (len(params) + 1, len(params) + 2, len(params) + 3)
        params.extend([user_lon, user_lat, max_distance_km * 1000])  # meters
    
    query += " LIMIT 50"
    
    # Execute query
    # ... database execution ...
    
    # Transform to dict format
    homes = []
    for row in rows:
        home = {
            'location_id': row['cqc_location_id'],
            'name': row['name'],
            'city': row['city'],
            'postcode': row['postcode'],
            'latitude': float(row['latitude']) if row['latitude'] else None,
            'longitude': float(row['longitude']) if row['longitude'] else None,
            'region': row['region'],
            'local_authority': row['local_authority'],
            'beds_total': row['beds_total'],
            'beds_available': row['beds_available'],
            'has_availability': row['has_availability'],
            'availability_status': row['availability_status'],
            'care_types': self._extract_care_types(row),
            'weekly_cost': self._get_weekly_cost(row, care_type),
            'rating': row['cqc_rating_overall'],
            'overall_rating': row['cqc_rating_overall'],
            'google_rating': float(row['google_rating']) if row['google_rating'] else None,
            'review_count': row['review_count'],
            # ... other fields ...
        }
        homes.append(home)
    
    return homes
```

---

### PHASE 7: Тестирование (4-6 часов)

#### 7.1 Unit тесты для каждого scoring метода

**Файл:** `api-testing-suite/backend/tests/test_matching_service.py`

```python
import pytest
from services.matching_service import MatchingService
from models.matching_models import MatchingInputs

def test_score_location():
    service = MatchingService()
    
    # ≤5 miles
    assert service.score_location(52.4862, -1.8904, 52.4862, -1.8904) == 20
    
    # ≤10 miles
    assert service.score_location(52.4862, -1.8904, 52.5000, -1.9000) == 15
    
    # ≤15 miles
    assert service.score_location(52.4862, -1.8904, 52.5500, -1.9500) == 10
    
    # >15 miles
    assert service.score_location(52.4862, -1.8904, 52.6000, -2.0000) == 5

def test_score_cqc_rating():
    service = MatchingService()
    
    assert service.score_cqc_rating("Outstanding") == 25
    assert service.score_cqc_rating("Good") == 20
    assert service.score_cqc_rating("Requires Improvement") == 10
    assert service.score_cqc_rating("Inadequate") == 0
    assert service.score_cqc_rating(None) == 0

def test_score_budget_match():
    service = MatchingService()
    
    # Within budget
    assert service.score_budget_match(950, 1000, "residential") == 20
    
    # +£50-100
    assert service.score_budget_match(1050, 1000, "residential") == 15
    
    # +£100-200
    assert service.score_budget_match(1150, 1000, "residential") == 10
    
    # +£200+
    assert service.score_budget_match(1300, 1000, "residential") == 0

def test_score_care_type_match():
    service = MatchingService()
    
    # Perfect match
    assert service.score_care_type_match("residential", ["residential"]) == 15
    
    # Close match
    assert service.score_care_type_match("residential", ["residential_dementia"]) == 10
    
    # General match
    assert service.score_care_type_match("residential", ["nursing"]) == 5
    
    # No match
    assert service.score_care_type_match("residential", []) == 5

def test_score_availability():
    service = MatchingService()
    
    # Beds available
    assert service.score_availability(5, None, True) == 10
    
    # Limited availability
    assert service.score_availability(0, "Limited availability", None) == 5
    
    # Full
    assert service.score_availability(0, "Full", False) == 0

def test_score_google_reviews():
    service = MatchingService()
    
    # ≥4.5 rating
    assert service.score_google_reviews(4.5, 10) == 10
    
    # ≥4.0 with 20+ reviews
    assert service.score_google_reviews(4.0, 25) == 7
    
    # ≥4.0 with <20 reviews
    assert service.score_google_reviews(4.0, 10) == 5
    
    # ≥3.5 with 10+ reviews
    assert service.score_google_reviews(3.5, 15) == 4
    
    # <3.5
    assert service.score_google_reviews(3.0, 50) == 0
```

#### 7.2 Integration тесты

```python
def test_calculate_50_point_score_full():
    """Test full 50-point score calculation"""
    service = MatchingService()
    user_inputs = MatchingInputs(
        postcode="B44 8DD",
        budget=1000,
        care_type="residential",
        user_lat=52.533398,
        user_lon=-1.8904
    )
    
    home = {
        'name': 'Test Home',
        'latitude': 52.533398,
        'longitude': -1.8904,
        'rating': 'Good',
        'weekly_cost': 950,
        'care_types': ['residential'],
        'beds_available': 5,
        'google_rating': 4.5,
        'review_count': 50
    }
    
    score = service.calculate_50_point_score(home, user_inputs)
    
    assert score.location_score == 20  # Same location
    assert score.cqc_score == 20  # Good
    assert score.budget_score == 20  # Within budget
    assert score.care_type_score == 15  # Perfect match
    assert score.availability_score == 10  # Beds available
    assert score.google_reviews_score == 10  # ≥4.5 rating
    assert score.total_score == 95

def test_select_3_strategic_homes():
    """Test selection of 3 strategic homes"""
    service = MatchingService()
    user_inputs = MatchingInputs(
        postcode="B44 8DD",
        budget=1000,
        care_type="residential",
        user_lat=52.533398,
        user_lon=-1.8904
    )
    
    candidates = [
        {
            'name': 'Safe Bet Home',
            'latitude': 52.533398,
            'longitude': -1.8904,
            'rating': 'Outstanding',
            'weekly_cost': 1000,
            'care_types': ['residential'],
            'beds_available': 5,
            'google_rating': 4.0,
            'review_count': 20
        },
        {
            'name': 'Best Reputation Home',
            'latitude': 52.5400,
            'longitude': -1.9000,
            'rating': 'Good',
            'weekly_cost': 1100,
            'care_types': ['residential'],
            'beds_available': 3,
            'google_rating': 4.8,
            'review_count': 150
        },
        {
            'name': 'Smart Value Home',
            'latitude': 52.5500,
            'longitude': -1.9100,
            'rating': 'Good',
            'weekly_cost': 800,
            'care_types': ['residential'],
            'beds_available': 2,
            'google_rating': 4.2,
            'review_count': 45
        }
    ]
    
    result = service.select_3_strategic_homes(candidates, user_inputs)
    
    assert len(result) == 3
    assert 'safe_bet' in result
    assert 'best_reputation' in result
    assert 'smart_value' in result
```

---

### PHASE 8: Обновление endpoint (1-2 часа)

#### 8.1 Обновить generate_free_report

```python
@app.post("/api/free-report")
async def generate_free_report(request: Dict[str, Any] = Body(...)):
    # ... existing code ...
    
    # Create MatchingInputs
    matching_inputs = MatchingInputs(
        postcode=postcode,
        budget=budget,
        care_type=care_type,
        user_lat=user_lat,
        user_lon=user_lon
    )
    
    # Get care homes
    care_homes_raw = await _fetch_care_homes(...)
    
    # Enrich with Google Places
    google_service = GooglePlacesService()
    for home in care_homes_raw:
        home = await google_service.enrich_care_home(home)
    
    # Matching with 50-point algorithm
    matching_service = MatchingService()
    matched_homes = matching_service.select_3_strategic_homes(
        care_homes_raw,
        matching_inputs
    )
    
    # ... rest of code ...
```

---

## 📊 Метрики успеха

### Performance Targets

- **Matching time:** <500ms для 50 домов
- **Google Places enrichment:** <2s для 3 домов (параллельно)
- **Total endpoint time:** <60s (включая все API calls)

### Quality Targets

- **Score distribution:** Дома должны иметь scores от 40-100
- **Strategy diversity:** 3 дома должны быть разными (не дубликаты)
- **Coverage:** Все 6 категорий должны учитываться

---

## 🧪 Тестовые сценарии

### Сценарий 1: Birmingham Residential (questionnaire_4.json)

**Inputs:**
- Postcode: B44 8DD
- Budget: £950/week
- Care Type: residential
- CHC Probability: 15.2%

**Expected:**
- Safe Bet: Outstanding/Good рейтинг, ≤10 miles, в бюджете
- Best Reputation: Google rating ≥4.0, ≥20 reviews
- Smart Value: Лучший score/price ratio, в бюджете

### Сценарий 2: Birmingham Dementia (questionnaire_5.json)

**Inputs:**
- Postcode: B31 2TX
- Budget: £1,200/week
- Care Type: dementia
- CHC Probability: 45.8%

**Expected:**
- Все 3 дома должны поддерживать dementia care
- Safe Bet: Специализированный dementia care, безопасный сад
- Higher CHC probability должна учитываться в scoring

### Сценарий 3: Birmingham Nursing (questionnaire_6.json)

**Inputs:**
- Postcode: B72 1DU
- Budget: £1,400/week
- Care Type: nursing
- CHC Probability: 68.5%

**Expected:**
- Все 3 дома должны поддерживать nursing care
- Safe Bet: 24/7 nursing, хороший CQC рейтинг
- Higher budget позволяет выбирать из более дорогих домов

---

## 🔄 Миграция существующего кода

### Шаг 1: Сохранить текущий код

```python
# В matching_service.py добавить:
def find_top_3_homes_legacy(self, ...):
    """Старая реализация (для fallback)"""
    # ... existing code ...
```

### Шаг 2: Постепенная миграция

1. Добавить новые методы scoring
2. Добавить `calculate_50_point_score`
3. Обновить `select_3_strategic_homes` использовать новый scoring
4. Тестировать параллельно со старой версией
5. Переключить endpoint на новую версию
6. Удалить старую версию после проверки

---

## 📋 Checklist реализации

### PHASE 1: Подготовка
- [ ] Создать `matching_models.py` с типами данных
- [ ] Обновить структуру `MatchingService`
- [ ] Добавить импорты и зависимости

### PHASE 2: Scoring методы
- [ ] `score_location()` - Location (20 points)
- [ ] `score_cqc_rating()` - CQC Rating (25 points)
- [ ] `score_budget_match()` - Budget Match (20 points)
- [ ] `score_care_type_match()` - Care Type Match (15 points)
- [ ] `score_availability()` - Availability (10 points)
- [ ] `score_google_reviews()` - Google Reviews (10 points)

### PHASE 3: Главный метод
- [ ] `calculate_50_point_score()` - полный расчёт
- [ ] `_get_home_price()` - выбор цены по care_type
- [ ] `_get_home_care_types()` - извлечение типов ухода

### PHASE 4: Стратегии
- [ ] Обновить `select_3_strategic_homes()`
- [ ] Safe Bet стратегия
- [ ] Best Reputation стратегия
- [ ] Smart Value стратегия
- [ ] Удаление дубликатов

### PHASE 5: Google Places
- [ ] Создать `GooglePlacesService`
- [ ] Интегрировать в `_fetch_care_homes`
- [ ] Кэширование Google данных
- [ ] Сохранение в БД `google_data`

### PHASE 6: БД интеграция
- [ ] Создать `DatabaseService`
- [ ] Метод `get_care_homes()` с PostGIS
- [ ] Интеграция в `_fetch_care_homes`
- [ ] Fallback на CQC API

### PHASE 7: Тестирование
- [ ] Unit тесты для каждого scoring метода
- [ ] Integration тесты для `select_3_strategic_homes`
- [ ] Тесты на edge cases
- [ ] Performance тесты

### PHASE 8: Интеграция
- [ ] Обновить `generate_free_report` endpoint
- [ ] Использовать `MatchingInputs`
- [ ] Обогащение Google Places данными
- [ ] Обновить response format

---

## ⏱️ Оценка времени

| Phase | Задачи | Время |
|-------|--------|-------|
| PHASE 1 | Подготовка и структура | 2-3 часа |
| PHASE 2 | Scoring методы | 4-6 часов |
| PHASE 3 | Главный метод | 2-3 часа |
| PHASE 4 | Стратегии | 3-4 часа |
| PHASE 5 | Google Places | 3-4 часа |
| PHASE 6 | БД интеграция | 2-3 часа |
| PHASE 7 | Тестирование | 4-6 часов |
| PHASE 8 | Интеграция | 1-2 часа |
| **ИТОГО** | | **21-31 час** |

**Рекомендуемый timeline:** 3-4 рабочих дня

---

## 🎯 Приоритеты

### 🔴 КРИТИЧНО (Must Have)
1. ✅ Scoring методы (PHASE 2)
2. ✅ Главный метод `calculate_50_point_score` (PHASE 3)
3. ✅ Обновление `select_3_strategic_homes` (PHASE 4)
4. ✅ Unit тесты (PHASE 7)

### 🟡 ВАЖНО (Should Have)
5. Google Places интеграция (PHASE 5)
6. БД интеграция (PHASE 6)
7. Integration тесты (PHASE 7)

### 🟢 ЖЕЛАТЕЛЬНО (Nice to Have)
8. Performance оптимизация
9. Расширенная аналитика scoring
10. A/B testing разных стратегий

---

## 📚 Референсы

- `TECHNICAL_FREE_Report_Only.md` - полная спецификация алгоритма
- `FREE_Report_Complete.md` - бизнес-требования
- `src/free_report_viewer/services/matching_service.py` - текущая реализация
- `input/care_homes_mock_simplified.json` - тестовые данные

---

## ✅ Готово к реализации

План детализирован и готов к выполнению. Все компоненты имеют чёткие спецификации и примеры кода.


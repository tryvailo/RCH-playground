# 📋 Обновлённый план реализации FREE Report

**Дата:** 2025-01-XX  
**Статус:** Обновлено с учётом имеющихся данных

---

## ✅ Что уже есть

1. **База данных `care_homes_db`** ✅
   - Таблица `care_homes` (предположительно)
   - Таблица `msif_fees_2025` (точно есть)

2. **Google Places API** ✅
   - GooglePlacesAPIClient работает
   - Методы: `find_place()`, `get_place_details()`
   - Возвращает: `rating`, `user_ratings_total`, `reviews`
   - Redis caching (24h TTL)
   - API key в `config.json`

3. **CQC API** ✅
   - CQCAPIClient работает
   - Методы для поиска care homes

4. **FSA API** ✅
   - FSAAPIClient работает
   - Методы для получения food hygiene ratings

5. **Базовый MatchingService** ✅
   - Safe Bet, Best Value, Premium алгоритмы
   - Расчёт расстояния (Haversine)

---

## 🔴 Что нужно реализовать

### 1. Подключение к базе данных `care_homes_db`

**Файл:** `api-testing-suite/backend/services/database_service.py` (новый)

**Задачи:**
- Создать DatabaseService для работы с `care_homes_db`
- Проверить существующие таблицы
- Создать недостающие таблицы (если нужно):
  - `questionnaires`
  - `free_reports`
  - `google_data` (опционально, для кэширования)

**Connection string:**
```python
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/care_homes_db")
```

**Вопросы:**
- Какой точный connection string?
- Какие таблицы уже существуют?
- Нужен ли PostGIS для geo-queries?

---

### 2. 50-Point Matching Algorithm (полная реализация)

**Файл:** `api-testing-suite/backend/services/matching_service.py` (обновить существующий)

**Текущее состояние:**
- ✅ Базовый алгоритм (Safe Bet, Best Value, Premium)
- ❌ Нет полного 50-point scoring

**Что добавить:**

```python
def calculate_50_point_score(home: Dict, user_inputs: Dict) -> int:
    """
    Location: 20 points (≤5mi=20, ≤10mi=15, ≤15mi=10, >15mi=5)
    CQC Rating: 25 points (Outstanding=25, Good=20, RI=10, Inadequate=0)
    Budget Match: 20 points (within=20, +£50-100=15, +£100-200=10, +£200+=0)
    Care Type Match: 15 points (perfect=15, close=10, general=5)
    Availability: 10 points (available=10, <4wks=5, 4+wks=0)
    Google Reviews: 10 points (≥4.5=10, ≥4.0=7, ≥3.5=4, <3.5=0)
    """
    score = 0
    
    # Location (20 points) - УЖЕ ЕСТЬ частично
    distance_km = home.get('distance_km', 999)
    if distance_km <= 5:
        score += 20
    elif distance_km <= 10:
        score += 15
    elif distance_km <= 15:
        score += 10
    else:
        score += 5
    
    # CQC Rating (25 points) - УЖЕ ЕСТЬ частично
    rating = home.get('rating') or home.get('overall_rating')
    rating_scores = {
        "Outstanding": 25,
        "Good": 20,
        "Requires improvement": 10,
        "Inadequate": 0
    }
    score += rating_scores.get(rating, 0)
    
    # Budget Match (20 points) - НУЖНО ДОБАВИТЬ
    user_budget = user_inputs.get('budget', 0)
    home_price = home.get('weekly_cost', 0)
    price_diff = home_price - user_budget
    
    if price_diff <= 0:
        score += 20
    elif price_diff <= 100:
        score += 15
    elif price_diff <= 200:
        score += 10
    else:
        score += 0
    
    # Care Type Match (15 points) - НУЖНО ДОБАВИТЬ
    user_care_type = user_inputs.get('care_type', '')
    home_care_types = home.get('care_types', [])
    
    if user_care_type == 'not_sure':
        score += 10
    elif user_care_type in home_care_types:
        score += 15
    else:
        score += 0
    
    # Availability (10 points) - НУЖНО ДОБАВИТЬ (данные из БД или mock)
    beds_available = home.get('beds_available', 0)
    waiting_weeks = home.get('waiting_list_weeks')
    
    if beds_available > 0:
        score += 10
    elif waiting_weeks and waiting_weeks <= 4:
        score += 5
    else:
        score += 0
    
    # Google Reviews (10 points) - НУЖНО ДОБАВИТЬ (интеграция с GooglePlacesAPIClient)
    google_rating = home.get('google_rating')
    if google_rating:
        if google_rating >= 4.5:
            score += 10
        elif google_rating >= 4.0:
            score += 7
        elif google_rating >= 3.5:
            score += 4
        else:
            score += 0
    
    return score
```

---

### 3. Интеграция Google Places в Matching

**Файл:** `api-testing-suite/backend/main.py` (обновить `_fetch_care_homes()`)

**Текущее состояние:**
- ✅ GooglePlacesAPIClient доступен
- ❌ Не используется в `_fetch_care_homes()`

**Что добавить:**

```python
async def _fetch_care_homes(...) -> List[Dict]:
    """Fetch care homes and enrich with Google Places data"""
    # ... существующий код для получения homes из CQC ...
    
    # Обогатить данными из Google Places
    creds = get_credentials()
    if creds and hasattr(creds, 'google_places') and creds.google_places:
        api_key = getattr(creds.google_places, 'api_key')
        google_client = GooglePlacesAPIClient(api_key=api_key)
        
        for home in homes:
            try:
                # Поиск места по имени и адресу
                query = f"{home['name']} {home.get('postcode', '')}"
                place = await google_client.find_place(query)
                
                if place:
                    # Получить детали (rating, reviews)
                    place_id = place.get('place_id')
                    if place_id:
                        details = await google_client.get_place_details(
                            place_id,
                            fields=['rating', 'user_ratings_total', 'reviews']
                        )
                        
                        home['google_rating'] = details.get('rating')
                        home['google_review_count'] = details.get('user_ratings_total', 0)
                        home['google_reviews'] = details.get('reviews', [])[:3]  # Top 3 reviews
            except Exception as e:
                print(f"Google Places error for {home['name']}: {e}")
                # Продолжить без Google данных
    
    return homes
```

---

### 4. Availability Data

**Статус:** ❌ НЕТ

**Варианты решения:**

**Вариант A: Из базы данных `care_homes_db`**
- Если в таблице `care_homes` есть колонка `beds_available` или `number_of_beds`
- Использовать эти данные напрямую

**Вариант B: Mock данные для FREE tier**
- Для FREE отчёта использовать mock данные
- В Professional tier получать реальные данные из Autumna или других источников

**Вариант C: CQC API**
- Проверить, предоставляет ли CQC API данные о доступности
- (Скорее всего нет)

**Рекомендация:** Вариант B (mock для FREE) + проверка БД

---

### 5. Database Models для новых таблиц

**Файл:** `api-testing-suite/backend/models/free_report_models.py` (новый)

**Таблицы для создания:**

```sql
-- Questionnaires
CREATE TABLE IF NOT EXISTS questionnaires (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    postcode VARCHAR(10) NOT NULL,
    care_type VARCHAR(50),
    budget_max DECIMAL(10,2),
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Free Reports
CREATE TABLE IF NOT EXISTS free_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    questionnaire_id UUID REFERENCES questionnaires(id),
    home_ids UUID[],
    pdf_s3_url TEXT,
    generated_at TIMESTAMP DEFAULT NOW()
);

-- Google Data (опционально, для кэширования)
CREATE TABLE IF NOT EXISTS google_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    care_home_location_id VARCHAR(50),  -- CQC location_id
    place_id VARCHAR(255),
    rating DECIMAL(2,1),
    review_count INTEGER,
    reviews JSONB,
    last_fetched TIMESTAMP DEFAULT NOW(),
    UNIQUE(care_home_location_id)
);
```

---

## 📋 Приоритетный план действий

### Week 1: Database & Matching

1. **День 1-2: Database Service**
   - [ ] Создать `database_service.py`
   - [ ] Подключиться к `care_homes_db`
   - [ ] Проверить существующие таблицы
   - [ ] Создать недостающие таблицы (migrations)

2. **День 2-4: 50-Point Algorithm**
   - [ ] Реализовать полный `calculate_50_point_score()`
   - [ ] Добавить Budget Match scoring
   - [ ] Добавить Care Type Match scoring
   - [ ] Добавить Availability scoring (mock для начала)
   - [ ] Unit тесты

3. **День 4-5: Google Places Integration**
   - [ ] Интегрировать GooglePlacesAPIClient в `_fetch_care_homes()`
   - [ ] Добавить Google rating в scoring
   - [ ] Сохранять Google data в БД (опционально)

### Week 2: Email & PDF

4. **День 1-3: Email Service**
   - [ ] SendGrid интеграция
   - [ ] Email templates
   - [ ] 3-email sequence

5. **День 3-5: PDF & S3**
   - [ ] Backend PDF generation
   - [ ] S3 upload
   - [ ] Presigned URLs

---

## 🔧 Технические детали

### Database Connection

```python
# api-testing-suite/backend/services/database_service.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:pass@localhost:5432/care_homes_db"
)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)
```

### Google Places Integration

```python
# В main.py, функция _fetch_care_homes()
from api_clients.google_places_client import GooglePlacesAPIClient

# Получить API key из config
creds = get_credentials()
google_api_key = creds.google_places.api_key
google_client = GooglePlacesAPIClient(api_key=google_api_key)

# Для каждого дома
place = await google_client.find_place(f"{home['name']} {home['postcode']}")
if place:
    details = await google_client.get_place_details(place['place_id'])
    home['google_rating'] = details.get('rating')
    home['google_review_count'] = details.get('user_ratings_total')
```

---

## ❓ Остающиеся вопросы

1. **Database:**
   - Точный connection string для `care_homes_db`?
   - Какие таблицы уже существуют?
   - Есть ли PostGIS?

2. **Availability:**
   - Есть ли `beds_available` в таблице `care_homes`?
   - Или использовать mock для FREE tier?

3. **Email & S3:**
   - Есть ли SendGrid API key?
   - Есть ли AWS credentials для S3?

---

**Готов к реализации после получения ответов на вопросы выше.**


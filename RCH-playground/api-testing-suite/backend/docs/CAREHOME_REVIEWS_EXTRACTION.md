# 📊 CareHome.co.uk Reviews Extraction & Semantic Analysis

## Обзор

CareHome.co.uk — главный UK-специфичный источник отзывов о домах престарелых с **400,000+ верифицированных отзывов**.

### Преимущества для небольших care homes:
- ✅ **Максимальное покрытие** — почти каждый UK care home имеет профиль
- ✅ **Верифицированные отзывы** — модерируются перед публикацией
- ✅ **Детальные рейтинги** — 11 категорий (Staff, Care, Cleanliness, etc.)
- ✅ **Связь reviewer'а** — известно кто оставил (дочь, сын, жена резидента)
- ✅ **Отзывы от семей** — косвенно отражают качество персонала

---

## 🔍 Структура данных CareHome.co.uk

### URL Pattern
```
https://www.carehome.co.uk/carehome.cfm/searchazref/{ID}
https://www.carehome.co.uk/carehome.cfm/searchazref/{ID}/startpage/{PAGE}
```

### Пагинация
- **20 отзывов на страницу**
- Страницы: `/startpage/1`, `/startpage/2`, etc.
- Максимум ~100+ отзывов для популярных домов

### Review Score (0-10)
Алгоритм:
- 5 баллов за Average Rating (1-5 звезд)
- 5 баллов за количество позитивных отзывов за 24 месяца

### Rating Categories (11)
| Категория | Описание |
|-----------|----------|
| Overall Experience | Общий рейтинг 1-5 |
| Facilities | Помещения, оборудование |
| Care / Support | Качество ухода |
| Cleanliness | Чистота |
| Treated with Dignity | Уважение к резиденту |
| Food & Drink | Питание |
| **Staff** | ⭐ Персонал — ключевая метрика |
| Activities | Активности, досуг |
| **Management** | ⭐ Менеджмент — индикатор текучки |
| Safety / Security | Безопасность |
| Rooms | Комнаты |
| Value for Money | Соотношение цена/качество |

### Reviewer Connections
```
- Daughter of Resident/Service User (самый частый)
- Son of Resident/Service User
- Wife/Husband of Resident
- Resident / Service User (сам проживающий)
- Friend, Niece, Nephew, etc.
```

---

## 🛠️ Алгоритм извлечения

### Шаг 1: Поиск Care Home
```python
# Google Custom Search API
query = f'"{care_home_name}" {postcode} site:carehome.co.uk'

# Извлекаем searchazref ID из URL
# /carehome.cfm/searchazref/20001050HARA → "20001050HARA"
```

### Шаг 2: Scraping с пагинацией
```python
# Firecrawl для каждой страницы
page_1 = scrape(f"{base_url}")
page_2 = scrape(f"{base_url}/startpage/2")
...
```

### Шаг 3: LLM Extraction
```python
# GPT-4o-mini извлекает структурированные данные
{
    "reviewer_initials": "J S",
    "reviewer_connection": "Daughter of Resident",
    "date": "16 September 2025",
    "overall_rating": 5,
    "review_text": "Very happy with my dad's care...",
    "category_ratings": {
        "Staff": 5,
        "Care / Support": 5,
        "Management": 4
    }
}
```

---

## 🧠 Семантический анализ

### Aspect-Based Sentiment Analysis

Для каждого аспекта ищем позитивные и негативные ключевые слова:

```python
ASPECT_KEYWORDS = {
    "staff_quality": {
        "positive": ["caring staff", "friendly staff", "kind staff", 
                     "professional", "dedicated", "lovely staff"],
        "negative": ["rude staff", "unprofessional", "staff shortage",
                     "understaffed", "high turnover", "agency staff"]
    },
    "care_quality": {
        "positive": ["excellent care", "wonderful care", "dignity",
                     "person-centered", "tailored care"],
        "negative": ["poor care", "neglected", "ignored", "complaints"]
    },
    "communication": {
        "positive": ["good communication", "kept informed", "responsive"],
        "negative": ["poor communication", "not informed", "unanswered"]
    },
    # ... другие аспекты
}
```

### Staff Quality Signals (из отзывов семей)

Семьи часто упоминают признаки качества персонала:

```python
STAFF_SIGNALS = {
    "training": ["trained", "qualified", "NVQ", "diploma"],
    "tenure": ["long-serving", "been here years", "experienced", "new staff"],
    "morale": ["happy staff", "staff enjoy", "staff seem stressed"],
    "ratio": ["enough staff", "plenty of staff", "understaffed"],
    "turnover": ["same faces", "staff left", "always different"]
}
```

### Формула Staff Quality Score

```python
# 1. Базовый балл из категории "Staff" (0-100)
base_score = (avg_staff_rating / 5) * 100

# 2. Корректировка по sentiment analysis (-10 to +10)
sentiment_adjustment = staff_sentiment_score * 10

# 3. Корректировка по management (индикатор морали)
management_adjustment = management_sentiment_score * 5

final_score = base_score + sentiment_adjustment + management_adjustment
```

---

## 📈 Output Structure

```json
{
    "care_home": {
        "name": "Harbledown Lodge Nursing Home",
        "postcode": "CT2 7NH"
    },
    "carehome_co_uk": {
        "searchazref": "20001050HARA",
        "url": "https://www.carehome.co.uk/carehome.cfm/searchazref/20001050HARA",
        "rating": 9.6,
        "total_reviews": 89
    },
    "reviews": [
        {
            "reviewer_initials": "J S",
            "reviewer_connection": "Daughter of Resident",
            "date": "16 September 2025",
            "overall_rating": 5,
            "review_text": "Very happy with my dad's care...",
            "category_ratings": {"Staff": 5, "Care / Support": 5}
        }
    ],
    "analysis": {
        "total_reviews": 50,
        "average_rating": 4.6,
        "rating_distribution": {5: 35, 4: 12, 3: 2, 2: 1},
        "aspect_sentiment": {
            "staff_quality": {
                "score": 0.85,
                "sentiment": "positive",
                "positive_mentions": 42,
                "negative_mentions": 3
            },
            "management": {
                "score": 0.72,
                "sentiment": "positive"
            }
        },
        "themes": {
            "caring_staff": 28,
            "good_communication": 15,
            "clean_environment": 12
        },
        "staff_quality_score": {
            "score": 87.5,
            "category": "EXCELLENT",
            "confidence": "high",
            "review_count": 50
        },
        "key_quotes": [
            {
                "text": "The staff are so caring and professional...",
                "rating": 5,
                "type": "positive"
            }
        ]
    }
}
```

---

## 🔧 Использование

### Python API
```python
from services.carehome_reviews_service import CareHomeReviewsService

service = CareHomeReviewsService(
    google_api_key="...",
    google_search_engine_id="...",
    firecrawl_client=firecrawl_client,
    openai_client=openai_client
)

result = await service.get_reviews_with_analysis(
    name="Harbledown Lodge Nursing Home",
    postcode="CT2 7NH",
    max_reviews=100
)

staff_score = result["analysis"]["staff_quality_score"]["score"]
```

### Интеграция со Staff Quality Service

```python
# В staff_quality_service.py добавить:

# PRIORITY 0: CareHome.co.uk reviews (UK-specific, most comprehensive)
if self.carehome_reviews_service:
    carehome_result = await self.carehome_reviews_service.get_reviews_with_analysis(
        name=home_name,
        postcode=home_postcode,
        max_reviews=100
    )
    
    if carehome_result.get("success"):
        # Извлекаем отзывы
        carehome_reviews = carehome_result.get("reviews", [])
        
        # Конвертируем в унифицированный формат
        for review in carehome_reviews:
            reviews.append({
                "source": "CareHome.co.uk",
                "rating": review.get("overall_rating"),
                "sentiment": self._map_rating_to_sentiment(review.get("overall_rating")),
                "text": review.get("review_text"),
                "date": review.get("date"),
                "author": review.get("reviewer_initials"),
                "reviewer_type": review.get("reviewer_connection")  # Семейная связь
            })
        
        # Используем семантический анализ
        semantic_analysis = carehome_result.get("analysis", {})
        carehome_staff_score = semantic_analysis.get("staff_quality_score", {})
```

---

## ⚠️ Важные замечания

### Rate Limiting
- CareHome.co.uk не блокирует, но рекомендуется 1-2 сек между запросами
- Firecrawl имеет свои лимиты (проверьте план)

### Качество данных
- Отзывы **от семей**, не от сотрудников
- Косвенно отражают качество персонала через:
  - Категорию "Staff" рейтинг
  - Упоминания персонала в тексте
  - Категорию "Management" как индикатор морали

### Комбинирование с другими источниками
```
Рекомендуемые веса:
- CareHome.co.uk Staff rating: 30%
- Indeed/Glassdoor employee reviews: 30%
- CQC Well-Led + Effective: 30%
- CQC Report sentiment: 10%
```

---

## 📊 Тестирование

```bash
cd backend
python -c "
import asyncio
from services.carehome_reviews_service import test_carehome_reviews
asyncio.run(test_carehome_reviews())
"
```

---

## 🔗 Связанные файлы

- `services/carehome_reviews_service.py` — основной сервис
- `services/staff_quality_service.py` — интеграция в Staff Quality Score
- `api_clients/google_custom_search_client.py` — поиск care home
- `api_clients/firecrawl_client.py` — scraping

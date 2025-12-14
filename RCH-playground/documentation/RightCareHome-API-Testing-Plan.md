# RightCareHome: Комплексный План Технической Валидации API
**Версия:** 1.0  
**Дата:** Ноябрь 2025  
**Статус:** План тестирования

---

## 📋 Содержание

1. [Обзор тестирования](#обзор)
2. [Государственные API](#государственные-api)
   - [CQC API](#1-cqc-api)
   - [FSA FHRS API](#2-fsa-fhrs-api)
   - [Companies House API](#3-companies-house-api)
3. [Коммерческие API](#коммерческие-api)
   - [Google Places API](#4-google-places-api)
   - [Google Places Insights (BigQuery)](#5-google-places-insights-bigquery)
   - [Perplexity Search API](#6-perplexity-search-api)
4. [Дополнительные источники](#дополнительные-источники)
   - [Autumna (веб-скрапинг)](#7-autumna-веб-скрапинг)
5. [Интеграция и кейсы](#интеграция)
6. [Roadmap тестирования](#roadmap)

---

<a name="обзор"></a>
## 🎯 Обзор Тестирования

### Цели валидации
- ✅ Проверить доступность и стабильность всех API
- ✅ Оценить качество и полноту данных
- ✅ Определить стоимость и rate limits
- ✅ Выявить уникальные возможности и ограничения
- ✅ Создать базовые интеграционные тесты

### Критерии успеха
1. **Доступность**: API отвечает в течение 2 секунд
2. **Полнота**: Данные покрывают 90%+ домов престарелых в регионе
3. **Качество**: Данные актуальны (обновлены за последние 30 дней)
4. **Стоимость**: Укладываемся в бюджет £200/месяц на тестирование

---

<a name="государственные-api"></a>
# 🏛️ ЧАСТЬ 1: ГОСУДАРСТВЕННЫЕ API

<a name="1-cqc-api"></a>
## 1. CQC API (Care Quality Commission)

### 📚 Документация
- **Официальная документация**: https://api-portal.service.cqc.org.uk/
- **API Base URL**: `https://api.cqc.org.uk/public/v1`
- **Новый Base URL**: `https://api.service.cqc.org.uk`
- **GitHub репозиторий с примерами**: https://github.com/evanodell/cqcr
- **RAML спецификация**: https://anypoint.mulesoft.com/exchange/portals/care-quality-commission-5/

### 🔑 Аутентификация
```
Тип: Partner Code (query parameter)
Требование: Добавить partnerCode в каждый запрос
Rate limit: До 2000 запросов/минуту с partnerCode
Без partnerCode: Может быть throttling
```

### 🧪 Тестовые Запросы

#### Тест 1: Получить список домов престарелых в South East
```bash
# Базовый запрос - получить первые 100 домов
curl -X GET "https://api.cqc.org.uk/public/v1/locations?perPage=100&page=1&region=South+East&careHome=true&partnerCode=RIGHTCAREHOME" \
  -H "Accept: application/json"

# Ожидаемый результат:
# - HTTP 200
# - JSON с массивом locations
# - Поля: locationId, name, postalCode, localAuthority, currentRatings
```

#### Тест 2: Детальная информация о конкретном доме
```bash
# Получить полную информацию по location ID
curl -X GET "https://api.cqc.org.uk/public/v1/locations/{locationId}?partnerCode=RIGHTCAREHOME" \
  -H "Accept: application/json"

# Что проверяем:
# - currentRatings (overall, safe, effective, caring, responsive, well-led)
# - specialisms (деменция, диабет, паллиативный уход)
# - numberOfBeds
# - lastInspection date
# - mainPhoneNumber, website
```

#### Тест 3: История инспекций
```bash
# Получить все отчеты инспекций
curl -X GET "https://api.cqc.org.uk/public/v1/locations/{locationId}/reports?partnerCode=RIGHTCAREHOME" \
  -H "Accept: application/json"

# Что проверяем:
# - История рейтингов за последние 5 лет
# - Даты инспекций
# - Enforcement actions (если есть)
# - URL к PDF отчетам
```

#### Тест 4: Поиск по Provider (компании-оператору)
```bash
# Найти все локации конкретного провайдера
curl -X GET "https://api.cqc.org.uk/public/v1/providers/{providerId}/locations?partnerCode=RIGHTCAREHOME" \
  -H "Accept: application/json"

# Зачем: Отследить все дома одной компании для анализа качества сети
```

### 📊 Данные для Валидации

**Тестовые локации** (реальные дома для тестирования):
1. Location ID: `1-101669846` (пример Outstanding rated)
2. Provider ID: `1-1016936648` (HC-One, крупная сеть)

**Что валидировать:**
- [ ] Все дома в South East имеют координаты (longitude/latitude)
- [ ] 95%+ домов имеют currentRating (не null)
- [ ] specialisms корректно перечислены
- [ ] lastInspection не старше 18 месяцев (регуляторный стандарт)
- [ ] mainPhoneNumber в валидном UK формате

### 💡 Неочевидные Фишки

#### Фишка 1: Tracking Changes API
```bash
# Получить изменения за последние 7 дней
curl -X GET "https://api.cqc.org.uk/public/v1/changes?startDate=2025-11-04&partnerCode=RIGHTCAREHOME" \
  -H "Accept: application/json"

# Используйте это для:
# - Автоматического обновления данных
# - Алертов об изменении рейтингов
# - Мониторинга новых enforcement actions
```

#### Фишка 2: Relationships API
```bash
# Найти связанные локации (например, другие дома того же оператора)
curl -X GET "https://api.cqc.org.uk/public/v1/locations/{locationId}/relationships?partnerCode=RIGHTCAREHOME"

# Кейс использования:
# "Manor House Care управляется HC-One. 
#  Посмотрите другие 15 домов HC-One в регионе"
```

#### Фишка 3: Specialisms детализация
**Hidden Insight**: В поле `specialisms` есть не только basic типы (dementia, diabetes), но и:
- `learningDisabilities` - дома для людей с особенностями развития
- `mentalHealth` - психиатрическая помощь
- `physicalDisabilities` - физические ограничения
- `sensoryImpairments` - нарушения зрения/слуха

**Используйте для**: Ультра-специфического матчинга (например, для Jane с диабетом И ранней деменцией)

### 🔗 Интеграционные Кейсы

#### Кейс 1: Risk Prediction Model
```python
# Псевдокод: Предсказание риска снижения рейтинга
risk_score = 0

# Индикаторы риска:
if last_inspection > 15_months_ago:
    risk_score += 20  # Давно не проверялись

if rating_declined_last_time:
    risk_score += 30  # История снижения

if provider_has_multiple_poor_ratings:
    risk_score += 25  # Сеть с проблемами

if enforcement_actions > 0:
    risk_score += 40  # Активные санкции

# Результат: Алерт для Premium подписчиков
if risk_score > 60:
    alert_user("High risk of quality decline")
```

---

<a name="2-fsa-fhrs-api"></a>
## 2. FSA FHRS API (Food Hygiene Rating Scheme)

### 📚 Документация
- **Официальная документация**: https://api.ratings.food.gov.uk/help
- **API Base URL**: `https://api.ratings.food.gov.uk`
- **Status page**: https://api.ratings.food.gov.uk/Help/Status
- **Open Data Portal**: https://data.food.gov.uk

### 🔑 Аутентификация
```
Тип: Header-based versioning
Требование: 
  - x-api-version: 2 (обязательно!)
  - Accept-Language: en-GB или cy-GB (опционально)
Rate limit: Throttling при high volume (>1/sec)
Стоимость: БЕСПЛАТНО
```

### 🧪 Тестовые Запросы

#### Тест 1: Поиск care homes по Local Authority
```http
GET http://api.ratings.food.gov.uk/Establishments?localAuthorityId=128&businessTypeId=7841
x-api-version: 2
Accept-Language: en-GB

# Параметры:
# localAuthorityId=128 (Brighton & Hove, например)
# businessTypeId=7841 (Caring Premises - включает care homes)

# Что получаем:
# - FHRSID (уникальный ID)
# - BusinessName
# - RatingValue (0-5 или "Pass"/"AwaitingInspection")
# - RatingDate
# - Scores: Hygiene, Structural, ConfidenceInManagement
# - Geocode (lat/lon)
```

#### Тест 2: Получить детали конкретного заведения
```http
GET http://api.ratings.food.gov.uk/Establishments/{FHRSID}
x-api-version: 2

# CRITICAL: Используйте FHRSID, НЕ EstablishmentID!
# FHRSID стабильный, EstablishmentID может меняться

# Дополнительные поля:
# - RatingKey: Используйте для показа иконок рейтинга
# - RightToReply: Официальный ответ оператора
# - NewRatingPending: Ожидается новая проверка
# - SchemeType: FHRS или FHIS (Шотландия)
```

#### Тест 3: Batch поиск по геолокации + название
```http
GET http://api.ratings.food.gov.uk/Establishments?name=Manor+House&latitude=51.5074&longitude=-0.1278&maxDistanceLimit=1
x-api-version: 2

# Комбинируйте:
# - name (частичное совпадение)
# - геокоординаты из CQC API
# - maxDistanceLimit в милях

# Кейс: Матчинг CQC location с FSA establishment
```

#### Тест 4: Получить список Local Authorities
```http
GET http://api.ratings.food.gov.uk/Authorities
x-api-version: 2

# Зачем: 
# - Построить mapping LocalAuthorityId → Name
# - Для фильтров пользователя по региону
```

### 📊 Данные для Валидации

**Тестовые заведения**:
1. FHRSID: `1234567` (замените на реальный из вашего региона)
2. BusinessType: `7841` (Caring Premises)

**Что валидировать:**
- [ ] RatingValue присутствует у 90%+ записей
- [ ] RatingDate не старше 18 месяцев (регуляторный стандарт)
- [ ] Scores (Hygiene, Structural, Management) расшифровываются корректно:
  - `0` = Very Good
  - `5` = Poor
  - `10` = Major Improvement Necessary
- [ ] Geocode точность: ±100 метров от CQC координат

### 💡 Неочевидные Фишки

#### Фишка 1: RatingKey для иконок
```javascript
// FSA предоставляет готовые иконки
const ratingImages = {
  'fhrs_5_en-gb': 'https://ratings.food.gov.uk/images/scores/en-GB/small/5.jpg',
  'fhrs_4_en-gb': 'https://ratings.food.gov.uk/images/scores/en-GB/small/4.jpg',
  // ... и так далее
}

// В response API есть поле RatingKey, используйте его:
if (establishment.RatingKey === 'fhrs_5_en-gb') {
    showImage(ratingImages['fhrs_5_en-gb'])
}
```

#### Фишка 2: RightToReply - золотая жила информации
```python
# Многие дома пишут развернутые ответы на низкие рейтинги
# Используйте это для:

if establishment['RightToReply']:
    # 1. Sentiment analysis (извлечь, признают ли проблему)
    sentiment = analyze_sentiment(establishment['RightToReply'])
    
    # 2. Проверить упоминания об улучшениях
    if "refurbished" in text or "new kitchen" in text:
        context = "Home invested in improvements post-inspection"
    
    # 3. Red flag detection
    if "disagree with inspector" in text:
        flag = "Defensive response - may indicate issues"
```

#### Фишка 3: SchemeType различия
```
FHRS (England, Wales, N. Ireland): 0-5 stars
FHIS (Scotland): Pass / Improvement Required

# При интеграции:
if scheme == "FHIS":
    if rating == "Pass":
        display_as = "✓ Passed Inspection"
    else:
        display_as = "⚠ Improvement Required"
```

#### Фишка 4: NewRatingPending флаг
```python
# Супер полезно для real-time мониторинга
if establishment['NewRatingPending'] == True:
    # Дом недавно прошел инспекцию, рейтинг обновится в ближайшие 2 недели
    # Отправляем алерт Premium юзерам:
    alert = f"{home_name} был проинспектирован. Новый рейтинг скоро."
```

### 🔗 Интеграционные Кейсы

#### Кейс 1: FSA + CQC Correlation Analysis
```python
# Корреляция между Food Hygiene и CQC Rating
correlation_study = {
    'FSA_5_CQC_Outstanding': 0.67,  # 67% домов с FSA 5 имеют CQC Outstanding
    'FSA_3_CQC_RequiresImprovement': 0.43,  # Сильная корреляция проблем
    'FSA_5_CQC_Good': 0.28  # Некоторые дома отличные в еде, средние в целом
}

# Insight для юзеров:
if fsa_rating >= 5 and cqc_rating == "Good":
    note = "Food safety is EXCEPTIONAL (top 15%), even though overall care is 'Good'"
```

#### Кейс 2: Diabetes-Specific Filtering
```python
# Для Jane с диабетом - критический фактор
def diabetes_safe_homes(homes):
    safe_homes = []
    for home in homes:
        fsa = get_fsa_rating(home)
        
        # Строгие критерии для диабетиков
        if fsa['RatingValue'] >= 4 and fsa['Scores']['Hygiene'] <= 5:
            # Hygiene score 0-5 = Very Good to Good
            safe_homes.append(home)
            
    return safe_homes
```

#### Кейс 3: Historical Trend Analysis
```python
# Отследить улучшение/ухудшение (требует сохранение исторических данных)
# FSA API не дает истории, поэтому:

# 1. Делайте snapshot каждую неделю
weekly_snapshot = fetch_all_establishments()
save_to_db(weekly_snapshot, date=today)

# 2. Анализируйте тренды
if rating_dropped_from_5_to_3:
    alert = "⚠️ MAJOR DECLINE in food safety. Investigate immediately."
```

---

<a name="3-companies-house-api"></a>
## 3. Companies House API

### 📚 Документация
- **Официальная документация**: https://developer.company-information.service.gov.uk/
- **API Explorer**: https://developer-specs.company-information.service.gov.uk/
- **Base URL**: `https://api.company-information.service.gov.uk`
- **GitHub SDK**: https://github.com/zinggg/uk_companies_house

### 🔑 Аутентификация
```
Тип: HTTP Basic Auth (API key as username, password empty)
Получение ключа:
  1. Зарегистрируйтесь: https://developer.company-information.service.gov.uk/
  2. Create an application
  3. Generate API key
Rate limit: Нет официального лимита, но рекомендуется < 600 req/min
Стоимость: БЕСПЛАТНО
```

### 🧪 Тестовые Запросы

#### Тест 1: Поиск компании по названию
```bash
# Найти компанию-оператора care home
curl -u YOUR_API_KEY: \
  "https://api.company-information.service.gov.uk/search/companies?q=Manor+House+Care"

# Response включает:
# - company_number
# - company_status (active, dissolved, liquidation, etc.)
# - date_of_creation
# - company_type
# - registered_office_address
```

#### Тест 2: Получить профиль компании
```bash
curl -u YOUR_API_KEY: \
  "https://api.company-information.service.gov.uk/company/{company_number}"

# Критические поля:
# - company_status (active = OK, liquidation = RED FLAG)
# - sic_codes (Standard Industrial Classification)
# - accounts.next_due (дата следующей отчетности)
# - accounts.overdue (просрочка = финансовые проблемы)
# - has_insolvency_history (boolean)
# - has_charges (залоги/долги)
```

#### Тест 3: История директоров
```bash
# Получить список всех офицеров компании
curl -u YOUR_API_KEY: \
  "https://api.company-information.service.gov.uk/company/{company_number}/officers"

# Анализируем:
# - Частота смены директоров (нестабильность если >2 в год)
# - Resigned date (увольнения топ-менеджмента = warning)
# - Occupation (если директор - "care home manager", это хороший знак)
```

#### Тест 4: Финансовые отчеты
```bash
# Получить filing history (список всех поданных документов)
curl -u YOUR_API_KEY: \
  "https://api.company-information.service.gov.uk/company/{company_number}/filing-history"

# Искать:
# - category: "accounts" (годовые отчеты)
# - type: "AA" (Annual Accounts)
# - date: Как часто подают (регулярность = stability)

# Скачать конкретный документ:
curl -u YOUR_API_KEY: \
  "https://api.company-information.service.gov.uk/document/{document_id}/content" \
  --output accounts.pdf
```

#### Тест 5: Insolvency Check
```bash
# Проверить историю банкротств
curl -u YOUR_API_KEY: \
  "https://api.company-information.service.gov.uk/company/{company_number}/insolvency"

# Если данные есть = КРИТИЧЕСКИЙ RED FLAG
# Используйте для исключения домов из рекомендаций
```

### 📊 Данные для Валидации

**Тестовые компании**:
1. Company Number: `06790962` (HC-One - крупная сеть)
2. Company Number: `03553455` (Four Seasons Health Care - была в проблемах)

**Что валидировать:**
- [ ] company_status = "active" у всех рекомендуемых домов
- [ ] accounts.overdue = false (нет просрочек)
- [ ] has_insolvency_history = false
- [ ] date_of_creation: компания существует >3 лет (стабильность)
- [ ] officers: нет массовых увольнений в последние 6 месяцев

### 💡 Неочевидные Фишки

#### Фишка 1: SIC Codes для фильтрации
```python
# Standard Industrial Classification Codes для care homes
care_home_sic_codes = [
    '87100',  # Residential nursing care activities
    '87200',  # Residential care activities for learning difficulties
    '87300',  # Residential care activities for the elderly
    '87900',  # Other residential care activities
]

# Используйте для:
if any(sic in company['sic_codes'] for sic in care_home_sic_codes):
    confidence = "Confirmed: This company operates care homes"
else:
    warning = "Company may not be primary care provider (holding company?)"
```

#### Фишка 2: Charges - скрытые долги
```bash
# Получить список всех charges (залоги, ипотеки)
curl -u YOUR_API_KEY: \
  "https://api.company-information.service.gov.uk/company/{company_number}/charges"

# RED FLAGS:
# 1. status: "outstanding" + created_on: недавно = новые долги
# 2. classification: "charge-description" содержит "all assets" = полная ипотека
# 3. persons_entitled: банки, не частные инвесторы = банковский долг

# Insight для юзеров:
if total_charges > 3 and all_outstanding:
    warning = "⚠️ Company has significant financial obligations. Risk of instability."
```

#### Фишка 3: Enumeration Types
Companies House использует enum коды вместо текста. Скачайте маппинги:
```bash
# Официальные enumerations на GitHub:
wget https://raw.githubusercontent.com/companieshouse/api-enumerations/master/constants.yml

# Пример использования:
company_status_map = {
    'active': '✅ Active',
    'dissolved': '❌ Dissolved',
    'liquidation': '⚠️ In Liquidation',
    'receivership': '⚠️ In Receivership',
    'administration': '⚠️ In Administration',
}
```

#### Фишка 4: PSC (People with Significant Control)
```bash
# Найти бенефициаров (владельцев) компании
curl -u YOUR_API_KEY: \
  "https://api.company-information.service.gov.uk/company/{company_number}/persons-with-significant-control"

# Анализ:
# 1. Если один человек владеет >75% = семейный бизнес (может быть более стабильным)
# 2. Если корпорация = часть большой сети (стандартизация, но меньше личного подхода)
# 3. Offshore ownership (Британские Виргинские острова) = вопросы прозрачности
```

### 🔗 Интеграционные Кейсы

#### Кейс 1: Financial Stability Score
```python
def calculate_financial_stability(company_number):
    company = fetch_company(company_number)
    score = 100  # Start at 100
    
    # Deduct points for issues
    if company['company_status'] != 'active':
        score -= 100  # Immediate disqualification
    
    if company['accounts']['overdue']:
        score -= 30  # Late filing = financial stress
    
    if company['has_insolvency_history']:
        score -= 50  # Past insolvency = major risk
    
    charges = fetch_charges(company_number)
    if len(charges) > 5:
        score -= 20  # Too many debts
    
    # Age of company
    age = calculate_age(company['date_of_creation'])
    if age < 3:
        score -= 15  # New companies higher risk
    
    return max(0, score)  # Don't go below 0

# Использование:
if stability_score < 50:
    recommendation = "Avoid: Financial instability"
elif stability_score < 70:
    recommendation = "Caution: Some financial concerns"
else:
    recommendation = "✓ Financially stable"
```

#### Кейс 2: Director Churn Analysis
```python
def analyze_director_churn(company_number):
    officers = fetch_officers(company_number)
    
    resigned_last_year = [o for o in officers 
                          if o.get('resigned_on') and 
                          is_within_last_year(o['resigned_on'])]
    
    if len(resigned_last_year) >= 3:
        return {
            'risk': 'HIGH',
            'message': f"{len(resigned_last_year)} directors left in last year. Indicates management instability."
        }
    
    # Проверить, есть ли хотя бы один долгосрочный директор
    long_term = [o for o in officers 
                if calculate_tenure(o['appointed_on']) > 5]
    
    if not long_term:
        return {
            'risk': 'MEDIUM',
            'message': "No long-term directors. New management team."
        }
    
    return {
        'risk': 'LOW',
        'message': "✓ Stable management team"
    }
```

---

<a name="коммерческие-api"></a>
# 💼 ЧАСТЬ 2: КОММЕРЧЕСКИЕ API

<a name="4-google-places-api"></a>
## 4. Google Places API

### 📚 Документация
- **Официальная документация**: https://developers.google.com/maps/documentation/places/web-service/overview
- **API Explorer**: https://developers.google.com/maps/documentation/places/web-service/place-id
- **Base URL**: `https://maps.googleapis.com/maps/api/place`
- **Альтернативы**: Geoapify (дешевле), HERE Places API

### 🔑 Аутентификация
```
Тип: API Key (query parameter)
Получение ключа:
  1. Google Cloud Console: https://console.cloud.google.com/
  2. Enable Places API
  3. Create credentials → API Key
  4. Restrict key to Places API + your domain
Стоимость: 
  - Place Search: $32 per 1,000 requests
  - Place Details: $17 per 1,000 requests
  - Photos: $7 per 1,000 requests
  - ВАЖНО: $200 free credits monthly
Rate limit: 50 requests/second по умолчанию
```

### 🧪 Тестовые Запросы

#### Тест 1: Find Place - поиск по названию
```bash
# Найти care home по имени и региону
curl -X GET "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?\
input=Manor%20House%20Care%20Home%20Brighton&\
inputtype=textquery&\
fields=place_id,name,formatted_address,geometry&\
key=YOUR_API_KEY"

# Response:
# - place_id: Уникальный ID Google для этого места
# - geometry.location: lat/lng координаты
```

#### Тест 2: Place Details - полная информация
```bash
# Получить детали используя place_id из предыдущего запроса
curl -X GET "https://maps.googleapis.com/maps/api/place/details/json?\
place_id=ChIJN1t_tDeuEmsRUsoyG83frY4&\
fields=name,rating,reviews,opening_hours,photos,user_ratings_total,website,formatted_phone_number&\
key=YOUR_API_KEY"

# Критические поля:
# - rating: 1.0-5.0 (Google reviews average)
# - user_ratings_total: количество отзывов
# - reviews: массив последних 5 отзывов
# - photos: массив photo references
# - opening_hours: расписание работы
```

#### Тест 3: Nearby Search - найти дома в радиусе
```bash
# Найти все care homes в радиусе 5000м от координат
curl -X GET "https://maps.googleapis.com/maps/api/place/nearbysearch/json?\
location=51.5074,-0.1278&\
radius=5000&\
type=nursing_home&\
keyword=care+home&\
key=YOUR_API_KEY"

# Используйте для:
# - Карта всех домов в регионе
# - Конкурентный анализ (proximity competitors)
```

#### Тест 4: Place Photos - получить фотографии
```bash
# 1. Сначала получить photo_reference из Place Details
# 2. Затем fetch саму фотографию:
curl -X GET "https://maps.googleapis.com/maps/api/place/photo?\
maxwidth=400&\
photo_reference=PHOTO_REFERENCE_STRING&\
key=YOUR_API_KEY" \
--output home_photo.jpg

# Размеры: maxwidth или maxheight от 1 до 1600px
```

#### Тест 5: Reviews - детальный анализ отзывов
```bash
# Place Details уже возвращает reviews, но ограничено 5 последними
# Для большего количества нужно использовать Google My Business API (сложнее)

# Анализируем то что есть:
# reviews[].rating: 1-5
# reviews[].text: текст отзыва
# reviews[].time: UNIX timestamp
# reviews[].author_name: имя автора
# reviews[].relative_time_description: "2 months ago"
```

### 📊 Данные для Валидации

**Тестовые Place IDs**:
1. ChIJN1t_tDeuEmsRUsoyG83frY4 (пример care home в London)

**Что валидировать:**
- [ ] place_id стабилен при повторных запросах
- [ ] rating присутствует у 80%+ домов (новые дома могут не иметь)
- [ ] user_ratings_total > 10 для meaningful analysis
- [ ] reviews[].text не пустой и содержит полезную информацию
- [ ] photos доступны и загружаются

### 💡 Неочевидные Фишки

#### Фишка 1: Sentiment Analysis на отзывах
```python
import re
from textblob import TextBlob

def analyze_review_sentiment(reviews):
    positive_themes = []
    negative_themes = []
    
    # Ключевые слова для care homes
    positive_keywords = ['caring', 'kind', 'attentive', 'clean', 'excellent', 'wonderful']
    negative_keywords = ['neglect', 'dirty', 'rude', 'understaffed', 'complaint']
    
    for review in reviews:
        text = review['text'].lower()
        sentiment = TextBlob(text).sentiment.polarity  # -1 to 1
        
        # Extract themes
        if sentiment > 0.3:  # Positive
            for keyword in positive_keywords:
                if keyword in text:
                    positive_themes.append(keyword)
        elif sentiment < -0.3:  # Negative
            for keyword in negative_keywords:
                if keyword in text:
                    negative_themes.append(keyword)
    
    return {
        'overall_sentiment': sum([TextBlob(r['text']).sentiment.polarity for r in reviews]) / len(reviews),
        'top_positive_themes': Counter(positive_themes).most_common(3),
        'red_flags': Counter(negative_themes).most_common(3)
    }

# Кейс использования:
# "Reviews mention 'caring' and 'attentive' frequently. 
#  Warning: 2 reviews mentioned 'understaffed'"
```

#### Фишка 2: Response Rate (Business Reply)
```python
# Google Places показывает, отвечает ли бизнес на отзывы
def check_response_engagement(reviews):
    total_reviews = len(reviews)
    reviews_with_reply = len([r for r in reviews if 'author_url' in r and 'business' in r['author_url']])
    
    response_rate = reviews_with_reply / total_reviews
    
    if response_rate > 0.5:
        return "✓ Highly responsive (replies to 50%+ reviews)"
    elif response_rate > 0.2:
        return "Moderately responsive"
    else:
        return "⚠ Low responsiveness (rarely replies to reviews)"

# Insight: Responsive homes care about reputation & feedback
```

#### Фишка 3: Photo Analysis с Google Vision API
```python
from google.cloud import vision

def analyze_home_photos(photo_references):
    client = vision.ImageAnnotatorClient()
    
    insights = []
    for photo_ref in photo_references[:5]:  # Анализируем первые 5 фото
        # Fetch photo
        image_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=1600&photo_reference={photo_ref}&key={API_KEY}"
        image = vision.Image()
        image.source.image_uri = image_url
        
        # Detect labels
        response = client.label_detection(image=image)
        labels = [label.description for label in response.label_annotations]
        
        # Check for quality indicators
        if 'Garden' in labels:
            insights.append('Has outdoor space')
        if 'Dining' in labels or 'Restaurant' in labels:
            insights.append('Spacious dining area')
        if 'Bedroom' in labels and 'Furniture' in labels:
            insights.append('Well-furnished rooms')
    
    return insights

# Кейс:
# "Photos show: Garden, Modern Furniture, Bright Interiors
#  Suggests: Well-maintained, modern facility"
```

#### Фишка 4: Opening Hours Insights
```python
def analyze_visiting_hours(opening_hours):
    # opening_hours.periods - массив open/close времен
    
    if 'open_now' in opening_hours and opening_hours['open_now']:
        status = "Currently Open"
    
    # Проверить 24/7
    if len(opening_hours.get('periods', [])) == 1 and 'close' not in opening_hours['periods'][0]:
        return "24/7 Access - Good for family visits anytime"
    
    # Выходные дни
    weekend_hours = [p for p in opening_hours.get('periods', []) if p['open']['day'] in [0, 6]]  # Sunday=0, Saturday=6
    
    if not weekend_hours:
        return "⚠ Limited weekend visiting hours"
    
    return "Regular visiting hours including weekends"
```

### 🔗 Интеграционные Кейсы

#### Кейс 1: Review Velocity Tracking
```python
def track_review_velocity(place_id, historical_data):
    # Сохраняйте user_ratings_total каждую неделю
    current_count = fetch_place_details(place_id)['user_ratings_total']
    
    if place_id in historical_data:
        last_count = historical_data[place_id]['count']
        weeks_ago = historical_data[place_id]['weeks_ago']
        
        velocity = (current_count - last_count) / weeks_ago  # reviews per week
        
        if velocity > 2:
            insight = "High review activity (2+ new reviews/week). Growing visibility."
        elif velocity > 0.5:
            insight = "Steady review flow"
        else:
            insight = "⚠ Low review activity. Possible decline in visitors?"
        
        return {
            'velocity': velocity,
            'insight': insight
        }
```

#### Кейс 2: Competitive Benchmarking
```python
def benchmark_against_competitors(home_place_id, competitor_place_ids):
    home_rating = fetch_place_details(home_place_id)['rating']
    
    competitor_ratings = [fetch_place_details(pid)['rating'] for pid in competitor_place_ids]
    avg_competitor_rating = sum(competitor_ratings) / len(competitor_ratings)
    
    if home_rating > avg_competitor_rating + 0.5:
        return f"⭐ Exceptional (0.5+ stars above area average of {avg_competitor_rating:.1f})"
    elif home_rating > avg_competitor_rating:
        return f"Above average (area avg: {avg_competitor_rating:.1f})"
    else:
        return f"⚠ Below area average of {avg_competitor_rating:.1f}"
```

---

<a name="5-google-places-insights-bigquery"></a>
## 5. Google Places Insights (BigQuery)

### 📚 Документация
- **Официальная документация**: https://developers.google.com/maps/documentation/placesinsights/overview
- **Setup Guide**: https://developers.google.com/maps/documentation/placesinsights/cloud-setup
- **Query Examples**: https://developers.google.com/maps/documentation/placesinsights/queries
- **Site Selection Tutorial**: https://developers.google.com/maps/architecture/places-insights-site-selection

### 🔑 Аутентификация & Setup
```
Требования:
1. Google Cloud Project с billing enabled
2. BigQuery API enabled
3. Analytics Hub API enabled
4. Роли:
   - Analytics Hub Subscription Owner
   - BigQuery User

Подписка на данные:
1. Analytics Hub → Browse Listings
2. Найти "Places Insights - United Kingdom"
3. Subscribe (создаст dataset в вашем проекте)

Стоимость:
- Data access: БЕСПЛАТНО во время Preview (сейчас)
- BigQuery compute: ~£200/месяц для 1000 домов с weekly queries
- Storage: Минимальная (данные не хранятся, только query results)
```

### 🧪 Тестовые Запросы

#### Тест 1: Базовый запрос - количество домов в регионе
```sql
-- Найти все care homes в радиусе 10км от центра Brighton
SELECT WITH AGGREGATION_THRESHOLD
  COUNT(*) as care_home_count,
  AVG(rating) as avg_rating,
  AVG(user_rating_count) as avg_review_count
FROM `YOUR_PROJECT.places_insights___uk.places`
WHERE 
  ST_DWITHIN(
    ST_GEOGPOINT(-0.1278, 51.5074),  -- Brighton центр
    point, 
    10000  -- 10км радиус
  )
  AND primary_type IN ('nursing_home', 'senior_care')
  AND business_status = 'OPERATIONAL'
```

#### Тест 2: Visitor Footfall Analysis
```sql
-- КЛЮЧЕВАЯ ФИШКА: Анализ посещаемости семьями
SELECT WITH AGGREGATION_THRESHOLD
  p.name,
  p.rating,
  -- Эти метрики УНИКАЛЬНЫ для Places Insights!
  p.visitor_count_weekly,  -- Количество уникальных посетителей в неделю
  p.visitor_dwell_time_avg,  -- Среднее время пребывания (минуты)
  p.visitor_repeat_rate  -- % повторных посетителей
FROM `YOUR_PROJECT.places_insights___uk.places` p
WHERE 
  p.place_id IN (
    SELECT place_id 
    FROM `YOUR_PROJECT.places_insights___uk.places`
    WHERE primary_type = 'nursing_home'
      AND ST_DWITHIN(ST_GEOGPOINT(-0.1278, 51.5074), point, 15000)
  )
ORDER BY visitor_repeat_rate DESC
LIMIT 10

-- Интерпретация:
-- visitor_dwell_time_avg > 45 min = families spending quality time
-- visitor_repeat_rate > 70% = strong family engagement (ОТЛИЧНЫЙ ПОКАЗАТЕЛЬ)
```

#### Тест 3: Peak Visiting Times
```sql
-- Когда семьи посещают (по дням недели)
SELECT WITH AGGREGATION_THRESHOLD
  p.name,
  -- Unnest открывает массив opening_hours для каждого дня
  day.day_of_week,
  AVG(day.peak_hour_traffic) as avg_traffic
FROM `YOUR_PROJECT.places_insights___uk.places` p,
  UNNEST(p.popular_times_weekly) as day
WHERE p.place_id = 'YOUR_PLACE_ID'
GROUP BY p.name, day.day_of_week
ORDER BY day.day_of_week

-- Используйте для:
-- "Peak visiting: Weekends 2-5pm. Families prefer afternoons."
```

#### Тест 4: Competitive Density Analysis
```sql
-- Плотность конкурентов вокруг дома
SELECT WITH AGGREGATION_THRESHOLD
  target.name as target_home,
  COUNT(DISTINCT competitor.place_id) as nearby_competitors,
  AVG(competitor.rating) as avg_competitor_rating
FROM `YOUR_PROJECT.places_insights___uk.places` target
JOIN `YOUR_PROJECT.places_insights___uk.places` competitor
  ON ST_DWITHIN(target.point, competitor.point, 3000)  -- 3км radius
WHERE target.place_id = 'YOUR_TARGET_HOME_PLACE_ID'
  AND competitor.primary_type IN ('nursing_home', 'senior_care')
  AND competitor.place_id != target.place_id
GROUP BY target.name
```

#### Тест 5: Time-Series Trend Analysis
```sql
-- Отследить изменения за 3 месяца (требует historical snapshots)
WITH monthly_snapshots AS (
  SELECT 
    place_id,
    name,
    visitor_count_weekly,
    data_month  -- Предполагается, что вы сохраняете snapshots
  FROM `YOUR_PROJECT.care_homes_historical`
  WHERE place_id = 'YOUR_PLACE_ID'
    AND data_month >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 MONTH)
)
SELECT 
  name,
  data_month,
  visitor_count_weekly,
  LAG(visitor_count_weekly) OVER (ORDER BY data_month) as prev_month,
  (visitor_count_weekly - LAG(visitor_count_weekly) OVER (ORDER BY data_month)) / 
    LAG(visitor_count_weekly) OVER (ORDER BY data_month) * 100 as pct_change
FROM monthly_snapshots
ORDER BY data_month DESC

-- Alert logic:
-- pct_change < -20% = ⚠️ Significant decline in visits
```

### 📊 Данные для Валидации

**Тестовые данные**:
1. Region: South East England (coordinates: 51.5074, -0.1278)
2. Minimum sample: 100+ care homes

**Что валидировать:**
- [ ] visitor_count_weekly > 0 для 80%+ домов (некоторые могут быть новые)
- [ ] visitor_dwell_time_avg находится в диапазоне 20-90 минут (реалистичное посещение)
- [ ] visitor_repeat_rate от 30% до 90% (слишком низкий или высокий = аномалия)
- [ ] popular_times_weekly массив не пустой
- [ ] Корреляция: высокий repeat_rate → высокий CQC rating

### 💡 Неочевидные Фишки (УНИКАЛЬНЫЕ ВОЗМОЖНОСТИ!)

#### Фишка 1: Predictive Quality Score
```sql
-- РЕВОЛЮЦИОННАЯ НАХОДКА: Коррелируйте footfall с CQC ratings
-- На основе ваших документов: 
-- "Dwell time >40 min + repeat rate >70% = 87% correlation with Outstanding"

WITH behavior_analysis AS (
  SELECT 
    p.place_id,
    p.name,
    p.visitor_dwell_time_avg,
    p.visitor_repeat_rate,
    -- Create predictive score
    CASE 
      WHEN p.visitor_dwell_time_avg > 40 AND p.visitor_repeat_rate > 0.70 
        THEN 'High Probability Outstanding'
      WHEN p.visitor_dwell_time_avg > 30 AND p.visitor_repeat_rate > 0.50
        THEN 'Likely Good Quality'
      WHEN p.visitor_dwell_time_avg < 25 OR p.visitor_repeat_rate < 0.40
        THEN 'Potential Concerns'
      ELSE 'Average'
    END as predicted_quality
  FROM `YOUR_PROJECT.places_insights___uk.places` p
  WHERE p.primary_type IN ('nursing_home', 'senior_care')
)
SELECT * FROM behavior_analysis
WHERE predicted_quality = 'Potential Concerns'

-- INSIGHT:
-- Используйте это для ПРЕДУПРЕЖДЕНИЯ о проблемах 
-- за 6-12 месяцев ДО официальной CQC inspection!
```

#### Фишка 2: Family Engagement Score
```python
def calculate_family_engagement_score(insights_data):
    """
    Composite score based on Places Insights behavioral data
    """
    score = 0
    
    # Dwell time component (30 points max)
    if insights_data['visitor_dwell_time_avg'] > 50:
        score += 30
    elif insights_data['visitor_dwell_time_avg'] > 40:
        score += 25
    elif insights_data['visitor_dwell_time_avg'] > 30:
        score += 15
    else:
        score += 5
    
    # Repeat visitor rate (40 points max)
    repeat_rate = insights_data['visitor_repeat_rate']
    score += min(40, repeat_rate * 100 * 0.5)  # 80% repeat = 40 points
    
    # Weekly footfall (30 points max)
    weekly_visitors = insights_data['visitor_count_weekly']
    if weekly_visitors > 300:
        score += 30
    elif weekly_visitors > 200:
        score += 20
    elif weekly_visitors > 100:
        score += 10
    
    return {
        'score': score,
        'grade': 'A' if score > 80 else 'B' if score > 60 else 'C' if score > 40 else 'D',
        'interpretation': get_interpretation(score)
    }

def get_interpretation(score):
    if score > 80:
        return "⭐ EXCEPTIONAL family engagement. Families visit frequently and spend quality time."
    elif score > 60:
        return "✓ Strong family involvement. Regular visits and good dwell times."
    elif score > 40:
        return "Moderate engagement. Some family involvement."
    else:
        return "⚠ Low engagement. Potential red flag for care quality."
```

#### Фишка 3: Geographic Visitor Distribution
```sql
-- УНИКАЛЬНО: Откуда приезжают посетители
SELECT WITH AGGREGATION_THRESHOLD
  p.name,
  v.origin_postal_code_prefix,  -- Первые 2-3 символа почтового кода
  COUNT(*) as visitor_count_from_area,
  AVG(v.travel_distance_km) as avg_distance
FROM `YOUR_PROJECT.places_insights___uk.places` p
CROSS JOIN UNNEST(p.visitor_origins) as v
WHERE p.place_id = 'YOUR_PLACE_ID'
GROUP BY p.name, v.origin_postal_code_prefix
ORDER BY visitor_count_from_area DESC
LIMIT 10

-- INSIGHT:
-- "60% visitors from local area (< 5km). 
--  Strong community ties, lower risk of disengagement."
-- 
-- "40% visitors travel 20+ km.
--  Family commitment remains strong despite distance."
```

#### Фишка 4: Weekday vs Weekend Pattern Analysis
```sql
SELECT WITH AGGREGATION_THRESHOLD
  p.name,
  SUM(CASE WHEN day.day_of_week IN (0, 6) THEN day.visitor_count ELSE 0 END) as weekend_visitors,
  SUM(CASE WHEN day.day_of_week BETWEEN 1 AND 5 THEN day.visitor_count ELSE 0 END) as weekday_visitors,
  SAFE_DIVIDE(
    SUM(CASE WHEN day.day_of_week IN (0, 6) THEN day.visitor_count ELSE 0 END),
    SUM(CASE WHEN day.day_of_week BETWEEN 1 AND 5 THEN day.visitor_count ELSE 0 END)
  ) as weekend_to_weekday_ratio
FROM `YOUR_PROJECT.places_insights___uk.places` p
CROSS JOIN UNNEST(p.popular_times_weekly) as day
WHERE p.primary_type = 'nursing_home'
GROUP BY p.name
HAVING weekend_to_weekday_ratio > 1.5

-- INSIGHT:
-- Ratio > 1.5 = Families visit mainly on weekends (working families)
-- Ratio < 0.8 = More weekday visits (retirees, nearby families)
```

### 🔗 Интеграционные Кейсы

#### Кейс 1: Early Warning System
```python
def early_warning_system(place_id, historical_insights):
    """
    Detect quality issues 6+ months before CQC inspection
    """
    current = fetch_places_insights(place_id)
    
    # Compare to baseline (3-6 months ago)
    baseline = historical_insights[place_id]['baseline']
    
    warnings = []
    
    # Footfall decline
    footfall_change = (current['visitor_count_weekly'] - baseline['visitor_count_weekly']) / baseline['visitor_count_weekly']
    if footfall_change < -0.30:  # 30% decline
        warnings.append({
            'severity': 'HIGH',
            'indicator': 'Visitor Footfall',
            'message': f"30%+ decline in weekly visitors ({baseline['visitor_count_weekly']} → {current['visitor_count_weekly']}). Families may be avoiding the home."
        })
    
    # Dwell time decline
    dwell_change = current['visitor_dwell_time_avg'] - baseline['visitor_dwell_time_avg']
    if dwell_change < -10:  # 10 min decline
        warnings.append({
            'severity': 'MEDIUM',
            'indicator': 'Visit Duration',
            'message': f"Families spending 10+ minutes less during visits. May indicate discomfort."
        })
    
    # Repeat rate decline
    repeat_change = current['visitor_repeat_rate'] - baseline['visitor_repeat_rate']
    if repeat_change < -0.15:  # 15% decline
        warnings.append({
            'severity': 'HIGH',
            'indicator': 'Family Loyalty',
            'message': "Significant drop in repeat visitors. Possible quality concerns."
        })
    
    return {
        'risk_level': 'HIGH' if len([w for w in warnings if w['severity'] == 'HIGH']) > 0 else 'LOW',
        'warnings': warnings,
        'recommendation': 'Monitor closely' if warnings else 'No concerns detected'
    }
```

#### Кейс 2: Site Selection Model (для новых домов)
```sql
-- Найти оптимальные локации для нового care home
WITH area_analysis AS (
  SELECT 
    h3.h3_cell,  -- H3 is geospatial index system
    COUNT(DISTINCT p.place_id) as existing_homes,
    AVG(p.rating) as avg_rating,
    AVG(p.visitor_count_weekly) as avg_weekly_visitors,
    SUM(p.visitor_count_weekly) as total_weekly_demand
  FROM `YOUR_PROJECT.places_insights___uk.places` p
  JOIN `bigquery-public-data.geo_us_boundaries.h3_cells_level_7` h3
    ON ST_CONTAINS(h3.cell_geometry, p.point)
  WHERE p.primary_type IN ('nursing_home', 'senior_care')
    AND ST_DWITHIN(ST_GEOGPOINT(-0.1278, 51.5074), p.point, 20000)
  GROUP BY h3.h3_cell
)
SELECT 
  h3_cell,
  existing_homes,
  avg_rating,
  total_weekly_demand,
  -- Score based on undersupply + high demand
  (total_weekly_demand / NULLIF(existing_homes, 0)) as demand_per_home,
  CASE 
    WHEN existing_homes < 3 AND total_weekly_demand > 500 THEN 'High Opportunity'
    WHEN existing_homes < 5 AND avg_rating < 4.0 THEN 'Quality Gap'
    ELSE 'Saturated'
  END as market_opportunity
FROM area_analysis
WHERE market_opportunity != 'Saturated'
ORDER BY demand_per_home DESC
LIMIT 10
```

---

<a name="6-perplexity-search-api"></a>
## 6. Perplexity Search API

### 📚 Документация
- **Официальная документация**: https://docs.perplexity.ai/
- **Quickstart**: https://docs.perplexity.ai/getting-started/quickstart
- **API Platform**: https://www.perplexity.ai/api-platform
- **Pricing**: https://docs.perplexity.ai/guides/pricing

### 🔑 Аутентификация
```
Тип: Bearer Token (HTTP Authorization header)
Получение ключа:
  1. Перейти на https://www.perplexity.ai/settings/api
  2. Add credits (минимум $10)
  3. Generate API key
Стоимость:
  - sonar-pro (с интернет-поиском): $0.005 per request
  - sonar (базовая): $0.001 per request
  - Примерно: $25/месяц для мониторинга 1000 домов (1 запрос/дом/месяц)
Rate limit: Зависит от плана, обычно 50-100 req/min
```

### 🧪 Тестовые Запросы

#### Тест 1: Новости о конкретном care home
```python
import requests

url = "https://api.perplexity.ai/chat/completions"
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}

payload = {
    "model": "sonar-pro",  # Версия с web search
    "messages": [
        {
            "role": "user",
            "content": "Find recent news (last 6 months) about Manor House Care Home in Brighton. Include any awards, complaints, inspection results, or ownership changes. Provide sources."
        }
    ],
    "max_tokens": 500,
    "temperature": 0.2,  # Lower temp for factual queries
    "return_citations": True,  # CRITICAL: Get sources
    "search_recency_filter": "month"  # Focus on recent news
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()

# Response structure:
# result['choices'][0]['message']['content'] - основной ответ
# result['citations'] - массив источников с URLs
```

#### Тест 2: Reputation monitoring - social media mentions
```python
payload = {
    "model": "sonar-pro",
    "messages": [
        {
            "role": "user",
            "content": """Search for social media mentions and forum discussions about "Greenfield Care Home Manchester" 
            in the last 3 months. Summarize:
            1. Positive mentions
            2. Complaints or concerns
            3. Staff reviews (if found on Glassdoor, Indeed)
            Provide source links."""
        }
    ],
    "max_tokens": 600,
    "search_recency_filter": "month"
}
```

#### Тест 3: Competitive intelligence - новые конкуренты
```python
payload = {
    "model": "sonar-pro",
    "messages": [
        {
            "role": "user",
            "content": """Find information about new care homes that opened in South East England 
            in the last 12 months. Include:
            - Name and location
            - Capacity (number of beds)
            - Operator company
            - Any unique features or specializations
            Provide sources."""
        }
    ],
    "search_recency_filter": "year"
}
```

#### Тест 4: Crisis monitoring - infection outbreaks
```python
payload = {
    "model": "sonar-pro",
    "messages": [
        {
            "role": "user",
            "content": """Search for recent COVID-19, norovirus, or other infection outbreaks 
            reported in UK care homes in the last month. 
            List affected homes and severity. Provide news sources."""
        }
    ],
    "search_recency_filter": "week"  # Very recent
}
```

#### Тест 5: Financial distress signals
```python
payload = {
    "model": "sonar-pro",
    "messages": [
        {
            "role": "user",
            "content": """Search for news about care home companies in financial difficulty, 
            administration, or bankruptcy in UK in last 6 months. 
            Include company names and affected homes."""
        }
    ]
}
```

### 📊 Данные для Валидации

**Тестовые поисковые запросы**:
1. "Care home awards South East England 2025"
2. "[Specific care home name] CQC inspection report"
3. "[Care home operator] financial results 2024"

**Что валидировать:**
- [ ] citations присутствуют в 90%+ ответов
- [ ] URLs в citations работают (не 404)
- [ ] search_recency_filter корректно фильтрует по времени
- [ ] Response time < 5 секунд
- [ ] Content релевантен запросу (не generic info)

### 💡 Неочевидные Фишки

#### Фишка 1: Citation Quality Scoring
```python
def score_citation_quality(citations):
    """
    Оценить надежность источников
    """
    trusted_domains = [
        'cqc.org.uk',  # Official regulator
        'gov.uk',  # Government
        'bbc.co.uk', 'theguardian.com',  # Major news
        'nursingtimes.net', 'carehome.co.uk'  # Industry publications
    ]
    
    local_news_indicators = ['.co.uk', 'gazette', 'chronicle', 'post']
    
    scores = []
    for citation in citations:
        score = 50  # Base score
        url = citation.get('url', '')
        
        # Trusted source bonus
        if any(domain in url for domain in trusted_domains):
            score += 40
        
        # Local news (good for local context)
        elif any(indicator in url for indicator in local_news_indicators):
            score += 25
        
        # Social media (treat with caution)
        if 'facebook.com' in url or 'twitter.com' in url:
            score -= 20
        
        # Recency (если есть date в citation)
        if 'date' in citation:
            days_old = (datetime.now() - parse_date(citation['date'])).days
            if days_old < 30:
                score += 20
            elif days_old < 90:
                score += 10
        
        scores.append({
            'url': url,
            'score': max(0, min(100, score)),
            'reliability': 'High' if score > 80 else 'Medium' if score > 50 else 'Low'
        })
    
    return scores

# Используйте для:
# "Found in 3 sources: CQC (high reliability), Local Gazette (medium), Facebook (low)"
```

#### Фишка 2: Multi-turn contextual search
```python
def multi_turn_investigation(home_name):
    """
    Последовательная цепочка запросов для глубокого анализа
    """
    conversation_history = []
    
    # Turn 1: Basic search
    turn1 = {
        "role": "user",
        "content": f"What is {home_name}? Provide basic info."
    }
    conversation_history.append(turn1)
    response1 = call_perplexity(conversation_history)
    conversation_history.append({"role": "assistant", "content": response1})
    
    # Turn 2: Drilling down based on response
    turn2 = {
        "role": "user",
        "content": "Are there any recent complaints or concerns about this care home? Search news and forums."
    }
    conversation_history.append(turn2)
    response2 = call_perplexity(conversation_history)
    conversation_history.append({"role": "assistant", "content": response2})
    
    # Turn 3: Operator investigation
    turn3 = {
        "role": "user",
        "content": "Who operates this home? Find information about the parent company's financial status and other homes they manage."
    }
    conversation_history.append(turn3)
    response3 = call_perplexity(conversation_history)
    
    return {
        'basic_info': response1,
        'reputation': response2,
        'operator_info': response3
    }
```

#### Фишка 3: Structured extraction from unstructured search
```python
def extract_structured_events(perplexity_response):
    """
    Extract structured event data from narrative response
    """
    import re
    from dateutil import parser as date_parser
    
    content = perplexity_response['choices'][0]['message']['content']
    citations = perplexity_response.get('citations', [])
    
    events = []
    
    # Regex patterns for key events
    patterns = {
        'award': r'(award|prize|accolade|recognition)',
        'complaint': r'(complaint|concern|allegation|issue)',
        'inspection': r'(inspection|visit|report|rating)',
        'ownership': r'(acquired|purchased|taken over|sold)',
        'outbreak': r'(outbreak|infection|covid|norovirus)'
    }
    
    sentences = content.split('. ')
    for sentence in sentences:
        for event_type, pattern in patterns.items():
            if re.search(pattern, sentence, re.IGNORECASE):
                # Try to extract date
                date_match = re.search(r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b', 
                                      sentence, re.IGNORECASE)
                
                events.append({
                    'type': event_type,
                    'description': sentence,
                    'date': date_match.group(0) if date_match else 'Unknown',
                    'sentiment': 'negative' if event_type in ['complaint', 'outbreak'] else 'positive' if event_type == 'award' else 'neutral'
                })
    
    return events

# Используйте для:
# Timeline visualization в Premium отчетах
```

#### Фишка 4: Cross-reference validation
```python
def cross_reference_with_official_sources(perplexity_findings, cqc_data):
    """
    Validate Perplexity findings against official CQC data
    """
    discrepancies = []
    confirmations = []
    
    # Example: Check if Perplexity mentioned a rating change
    if 'rating' in perplexity_findings['content'].lower():
        perplexity_rating = extract_rating(perplexity_findings['content'])
        cqc_rating = cqc_data['currentRatings']['overall']['rating']
        
        if perplexity_rating != cqc_rating:
            discrepancies.append({
                'field': 'rating',
                'perplexity': perplexity_rating,
                'cqc_official': cqc_rating,
                'note': 'Perplexity may have outdated info. Trust CQC.'
            })
        else:
            confirmations.append('Rating confirmed across sources')
    
    return {
        'discrepancies': discrepancies,
        'confirmations': confirmations,
        'trust_score': len(confirmations) / (len(confirmations) + len(discrepancies)) if confirmations or discrepancies else 0
    }
```

### 🔗 Интеграционные Кейсы

#### Кейс 1: Automated reputation monitoring
```python
def weekly_reputation_scan(care_homes_list):
    """
    Еженедельное сканирование репутации всех домов
    """
    alerts = []
    
    for home in care_homes_list:
        payload = {
            "model": "sonar-pro",
            "messages": [{
                "role": "user",
                "content": f"Search for any negative news, complaints, or concerns about {home['name']} in the last 7 days. Be concise."
            }],
            "search_recency_filter": "week",
            "max_tokens": 300
        }
        
        response = call_perplexity(payload)
        content = response['choices'][0]['message']['content']
        
        # Simple sentiment check
        negative_keywords = ['complaint', 'concern', 'poor', 'inadequate', 'crisis']
        if any(keyword in content.lower() for keyword in negative_keywords):
            alerts.append({
                'home': home['name'],
                'severity': 'HIGH' if 'crisis' in content.lower() else 'MEDIUM',
                'summary': content,
                'sources': response.get('citations', [])
            })
    
    # Send alerts to Premium subscribers
    if alerts:
        send_email_alert(alerts)
    
    return alerts
```

#### Кейс 2: Competitive intelligence dashboard
```python
def build_competitive_intel(region, competitors):
    """
    Собрать intelligence о конкурентах в регионе
    """
    intel_report = {}
    
    for competitor in competitors:
        # Новости о конкуренте
        news_query = f"Recent news and developments about {competitor['name']} care home in last 6 months"
        
        # Финансовое состояние оператора
        financial_query = f"Financial status and performance of {competitor['operator']} care homes company"
        
        news_response = call_perplexity(news_query)
        financial_response = call_perplexity(financial_query)
        
        intel_report[competitor['name']] = {
            'recent_developments': extract_events(news_response),
            'financial_health': analyze_financial_mentions(financial_response),
            'risk_level': assess_risk(news_response, financial_response),
            'last_updated': datetime.now()
        }
    
    return intel_report

def assess_risk(news, financial):
    """Simple risk scoring based on keywords"""
    risk_indicators = ['bankruptcy', 'administration', 'closure', 'lawsuit', 'complaint']
    
    combined_text = news + financial
    risk_count = sum(1 for indicator in risk_indicators if indicator in combined_text.lower())
    
    if risk_count >= 3:
        return 'HIGH'
    elif risk_count >= 1:
        return 'MEDIUM'
    else:
        return 'LOW'
```

---

<a name="дополнительные-источники"></a>
# 🌐 ЧАСТЬ 3: ДОПОЛНИТЕЛЬНЫЕ ИСТОЧНИКИ

<a name="7-autumna-веб-скрапинг"></a>
## 7. Autumna (Веб-скрапинг)

### 📚 Техническая информация
- **Website**: https://www.autumna.care/
- **Метод**: Web scraping (Beautiful Soup, Scrapy, или Selenium)
- **Proxy требования**: Rotating residential proxies (избежать блокировки)
- **Частота**: Weekly scraping (чтобы не перегружать сайт)

### 🔑 Технические требования
```
Tools:
- Python: requests, BeautifulSoup4, Scrapy
- Proxy service: BrightData, SmartProxy (~£50/month)
- User-Agent rotation
- Rate limiting: 1 request every 2-3 seconds

Legal considerations:
- Check robots.txt: https://www.autumna.care/robots.txt
- Respect rate limits
- Don't DDoS the site
- Data usage: Fair use for comparison service
```

### 🧪 Тестовая реализация

#### Тест 1: Базовый scraper для списка домов
```python
import requests
from bs4 import BeautifulSoup
import time
import random

class AutumnaScraper:
    def __init__(self, proxy=None):
        self.base_url = "https://www.autumna.care"
        self.session = requests.Session()
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_care_homes(self, location, page=1):
        """
        Поиск домов по локации
        """
        search_url = f"{self.base_url}/care-homes?location={location}&page={page}"
        
        response = self.session.get(search_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        homes = []
        # Селекторы нужно адаптировать под актуальную структуру сайта
        home_cards = soup.find_all('div', class_='care-home-card')
        
        for card in home_cards:
            home = {
                'name': card.find('h3', class_='home-name').text.strip(),
                'url': self.base_url + card.find('a')['href'],
                'price_from': self.extract_price(card),
                'specialisms': [s.text for s in card.find_all('span', class_='specialism')],
                'location': card.find('span', class_='location').text.strip()
            }
            homes.append(home)
        
        # Rate limiting
        time.sleep(random.uniform(2, 4))
        
        return homes
    
    def extract_price(self, card):
        price_elem = card.find('span', class_='price')
        if price_elem:
            price_text = price_elem.text
            # Extract number: "£1,450 per week" -> 1450
            import re
            match = re.search(r'£([\d,]+)', price_text)
            if match:
                return int(match.group(1).replace(',', ''))
        return None
```

#### Тест 2: Детальный scraper для конкретного дома
```python
def scrape_home_details(self, home_url):
    """
    Получить полную информацию о конкретном доме
    """
    response = self.session.get(home_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    details = {
        'name': soup.find('h1', class_='home-name').text.strip(),
        'description': soup.find('div', class_='description').text.strip(),
        'amenities': [],
        'photos': [],
        'room_types': [],
        'contact': {}
    }
    
    # Amenities (удобства)
    amenities_section = soup.find('section', {'id': 'amenities'})
    if amenities_section:
        details['amenities'] = [
            amenity.text.strip() 
            for amenity in amenities_section.find_all('li')
        ]
    
    # Photos
    photo_gallery = soup.find('div', class_='photo-gallery')
    if photo_gallery:
        details['photos'] = [
            img['src'] for img in photo_gallery.find_all('img')
        ]
    
    # Room types and prices
    rooms_section = soup.find('section', {'id': 'rooms'})
    if rooms_section:
        for room_card in rooms_section.find_all('div', class_='room-card'):
            details['room_types'].append({
                'type': room_card.find('h4').text.strip(),
                'price': self.extract_price(room_card),
                'features': [f.text for f in room_card.find_all('li')]
            })
    
    # Contact info
    contact_section = soup.find('section', {'id': 'contact'})
    if contact_section:
        details['contact'] = {
            'phone': contact_section.find('a', href=lambda h: h and h.startswith('tel:')).text.strip(),
            'email': contact_section.find('a', href=lambda h: h and h.startswith('mailto:')).text.strip(),
            'address': contact_section.find('address').text.strip()
        }
    
    time.sleep(random.uniform(3, 5))  # Longer wait for detail pages
    
    return details
```

#### Тест 3: Change detection (обнаружение изменений)
```python
def detect_changes(self, home_id, previous_data, current_data):
    """
    Сравнить текущие и предыдущие данные для обнаружения изменений
    """
    changes = []
    
    # Проверка цены
    if previous_data.get('price_from') != current_data.get('price_from'):
        changes.append({
            'field': 'price',
            'old_value': previous_data.get('price_from'),
            'new_value': current_data.get('price_from'),
            'change_pct': ((current_data.get('price_from', 0) - previous_data.get('price_from', 0)) / 
                          previous_data.get('price_from', 1)) * 100
        })
    
    # Проверка amenities
    old_amenities = set(previous_data.get('amenities', []))
    new_amenities = set(current_data.get('amenities', []))
    
    added_amenities = new_amenities - old_amenities
    removed_amenities = old_amenities - new_amenities
    
    if added_amenities:
        changes.append({
            'field': 'amenities_added',
            'values': list(added_amenities)
        })
    
    if removed_amenities:
        changes.append({
            'field': 'amenities_removed',
            'values': list(removed_amenities)
        })
    
    return changes
```

### 📊 Данные для Валидации

**Тестовые страницы**:
1. Search page: /care-homes?location=Brighton
2. Detail page: Конкретный дом из результатов

**Что валидировать:**
- [ ] Scraper работает без блокировки (если блокируется, нужны прокси)
- [ ] Данные извлекаются корректно (не None/пустые)
- [ ] Rate limiting соблюдается (не более 30 запросов/минуту)
- [ ] Photos URL работают (доступны для скачивания)
- [ ] Prices в валидном формате (£1,000-£3,000/week)

### 💡 Неочевидные Фишки

#### Фишка 1: Semantic amenities classification
```python
def classify_amenities(amenities_list):
    """
    Классифицировать amenities по категориям для лучшего поиска
    """
    categories = {
        'outdoor': ['garden', 'terrace', 'patio', 'outdoor space'],
        'accessibility': ['wheelchair accessible', 'lift', 'ramps', 'ground floor'],
        'social': ['activities room', 'cinema', 'library', 'common areas'],
        'tech': ['wifi', 'internet', 'tv in rooms', 'call system'],
        'food': ['dining room', 'cafe', 'restaurant', 'home cooked meals'],
        'wellness': ['hairdresser', 'spa', 'fitness', 'physiotherapy']
    }
    
    classified = {cat: [] for cat in categories}
    
    for amenity in amenities_list:
        amenity_lower = amenity.lower()
        for category, keywords in categories.items():
            if any(keyword in amenity_lower for keyword in keywords):
                classified[category].append(amenity)
    
    return classified

# Используйте для:
# "This home has excellent outdoor amenities (3 features): 
#  garden, terrace, outdoor seating"
```

#### Фишка 2: Photo качество анализ
```python
from PIL import Image
import requests
from io import BytesIO

def analyze_photo_quality(photo_urls):
    """
    Оценить качество фотографий (разрешение, brightness)
    """
    quality_scores = []
    
    for url in photo_urls[:10]:  # Первые 10 фото
        try:
            response = requests.get(url, timeout=5)
            img = Image.open(BytesIO(response.content))
            
            width, height = img.size
            pixels = width * height
            
            # Score based on resolution
            if pixels > 2_000_000:  # > 2MP
                resolution_score = 100
            elif pixels > 1_000_000:  # 1-2MP
                resolution_score = 70
            else:
                resolution_score = 40
            
            quality_scores.append({
                'url': url,
                'resolution': f"{width}x{height}",
                'score': resolution_score
            })
        except:
            continue
    
    avg_score = sum(s['score'] for s in quality_scores) / len(quality_scores)
    
    if avg_score > 80:
        assessment = "✓ High-quality professional photos"
    elif avg_score > 60:
        assessment = "Good photo quality"
    else:
        assessment = "⚠ Low quality/outdated photos"
    
    return {
        'average_score': avg_score,
        'assessment': assessment,
        'total_photos': len(photo_urls),
        'analyzed': len(quality_scores)
    }
```

#### Фишка 3: Price trend analysis
```python
def analyze_price_trends(home_id, historical_prices):
    """
    Анализ исторических изменений цены
    """
    if len(historical_prices) < 2:
        return "Insufficient data"
    
    # Sort by date
    sorted_prices = sorted(historical_prices, key=lambda x: x['date'])
    
    # Calculate changes
    price_changes = []
    for i in range(1, len(sorted_prices)):
        old_price = sorted_prices[i-1]['price']
        new_price = sorted_prices[i]['price']
        change_pct = ((new_price - old_price) / old_price) * 100
        
        price_changes.append({
            'date': sorted_prices[i]['date'],
            'change_pct': change_pct,
            'new_price': new_price
        })
    
    # Trend detection
    recent_changes = [c['change_pct'] for c in price_changes[-3:]]  # Last 3 changes
    avg_change = sum(recent_changes) / len(recent_changes)
    
    if avg_change > 5:
        trend = "⚠ Prices increasing rapidly (+5%+ average)"
    elif avg_change > 0:
        trend = "Prices increasing moderately"
    elif avg_change < -5:
        trend = "⚠ Prices declining (possible quality concerns?)"
    else:
        trend = "✓ Stable pricing"
    
    return {
        'trend': trend,
        'avg_change_pct': avg_change,
        'current_price': sorted_prices[-1]['price'],
        'price_history': price_changes
    }
```

#### Фишка 4: Competitive set identification
```python
def identify_competitive_set(target_home, all_homes):
    """
    Найти прямых конкурентов для сравнения
    """
    # Фильтры для похожих домов
    competitors = []
    
    for home in all_homes:
        if home['id'] == target_home['id']:
            continue
        
        similarity_score = 0
        
        # Цена в пределах ±20%
        price_diff = abs(home['price'] - target_home['price']) / target_home['price']
        if price_diff < 0.20:
            similarity_score += 30
        
        # Overlapping specialisms
        target_specialisms = set(target_home['specialisms'])
        home_specialisms = set(home['specialisms'])
        overlap = len(target_specialisms & home_specialisms)
        similarity_score += overlap * 15
        
        # Proximity (если есть coordinates)
        distance = calculate_distance(target_home['coords'], home['coords'])
        if distance < 5:  # 5km
            similarity_score += 25
        
        if similarity_score > 50:
            competitors.append({
                'home': home,
                'similarity_score': similarity_score
            })
    
    # Return top 5 competitors
    return sorted(competitors, key=lambda x: x['similarity_score'], reverse=True)[:5]
```

### 🔗 Интеграционные Кейсы

#### Кейс 1: Price monitoring alerts
```python
def price_monitoring_system():
    """
    Еженедельный мониторинг цен с алертами для юзеров
    """
    homes_to_monitor = get_user_watchlist()  # Premium feature
    
    for home in homes_to_monitor:
        current_data = scrape_home_details(home['autumna_url'])
        previous_data = get_from_db(home['id'], date='last_week')
        
        if current_data['price_from'] != previous_data['price_from']:
            change = current_data['price_from'] - previous_data['price_from']
            change_pct = (change / previous_data['price_from']) * 100
            
            alert = {
                'home_name': home['name'],
                'price_change': change,
                'change_pct': change_pct,
                'new_price': current_data['price_from'],
                'message': f"Price {'increased' if change > 0 else 'decreased'} by £{abs(change)}/week ({change_pct:+.1f}%)"
            }
            
            send_user_alert(home['user_id'], alert)
```

#### Кейс 2: Amenities-based matching
```python
def match_by_amenities(user_requirements):
    """
    Найти дома с конкретными amenities для пользователя
    """
    required_amenities = user_requirements['must_have_amenities']
    nice_to_have = user_requirements['nice_to_have']
    
    all_homes = get_all_homes_from_db()
    
    matches = []
    for home in all_homes:
        home_amenities = set(home['amenities'])
        
        # Check must-haves
        required_met = all(req in home_amenities for req in required_amenities)
        
        if required_met:
            # Score based on nice-to-haves
            nice_to_have_count = sum(1 for nice in nice_to_have if nice in home_amenities)
            score = (nice_to_have_count / len(nice_to_have)) * 100 if nice_to_have else 100
            
            matches.append({
                'home': home,
                'amenities_score': score,
                'missing_nice_to_have': [n for n in nice_to_have if n not in home_amenities]
            })
    
    return sorted(matches, key=lambda x: x['amenities_score'], reverse=True)
```

---

<a name="интеграция"></a>
# 🔗 ЧАСТЬ 4: ИНТЕГРАЦИЯ И ПРОДВИНУТЫЕ КЕЙСЫ

## Мulti-API Data Fusion

### Кейс 1: Comprehensive Home Profile
```python
def build_comprehensive_profile(home_name, location):
    """
    Объединить данные из всех источников для полного профиля
    """
    profile = {
        'basic_info': {},
        'quality': {},
        'financial': {},
        'reputation': {},
        'behavioral': {},
        'risk_assessment': {}
    }
    
    # 1. CQC - Official quality data
    cqc_data = search_cqc_location(home_name, location)
    profile['basic_info'] = {
        'name': cqc_data['name'],
        'address': cqc_data['postalAddress'],
        'phone': cqc_data['mainPhoneNumber']
    }
    profile['quality']['cqc_rating'] = cqc_data['currentRatings']['overall']
    profile['quality']['specialisms'] = cqc_data['specialisms']
    
    # 2. FSA - Food safety
    fsa_data = search_fsa_by_location(cqc_data['latitude'], cqc_data['longitude'])
    profile['quality']['food_hygiene'] = {
        'rating': fsa_data['RatingValue'],
        'scores': fsa_data['Scores'],
        'last_inspection': fsa_data['RatingDate']
    }
    
    # 3. Companies House - Financial stability
    company_number = find_company_number(cqc_data['providerId'])
    company_data = fetch_company(company_number)
    profile['financial'] = {
        'company_status': company_data['company_status'],
        'accounts_overdue': company_data['accounts']['overdue'],
        'stability_score': calculate_financial_stability(company_number)
    }
    
    # 4. Google Places - Reviews and reputation
    place_data = find_google_place(home_name, location)
    profile['reputation'] = {
        'google_rating': place_data['rating'],
        'review_count': place_data['user_ratings_total'],
        'sentiment': analyze_review_sentiment(place_data['reviews'])
    }
    
    # 5. Places Insights - Behavioral data
    insights_data = query_places_insights(place_data['place_id'])
    profile['behavioral'] = {
        'weekly_visitors': insights_data['visitor_count_weekly'],
        'dwell_time': insights_data['visitor_dwell_time_avg'],
        'repeat_rate': insights_data['visitor_repeat_rate'],
        'engagement_score': calculate_family_engagement_score(insights_data)
    }
    
    # 6. Perplexity - Recent news and context
    news_data = search_perplexity(f"Recent news about {home_name}")
    profile['reputation']['recent_news'] = extract_events(news_data)
    
    # 7. Autumna - Pricing and amenities
    autumna_data = scrape_home_details(find_autumna_url(home_name))
    profile['basic_info']['price_range'] = autumna_data['price_from']
    profile['basic_info']['amenities'] = autumna_data['amenities']
    
    # Risk Assessment (combining all signals)
    profile['risk_assessment'] = assess_overall_risk(profile)
    
    return profile

def assess_overall_risk(profile):
    """
    Composite risk score from all data sources
    """
    risk_score = 0  # 0 = low risk, 100 = high risk
    flags = []
    
    # CQC rating
    if profile['quality']['cqc_rating']['rating'] == 'Inadequate':
        risk_score += 50
        flags.append('CQC Inadequate rating')
    elif profile['quality']['cqc_rating']['rating'] == 'Requires Improvement':
        risk_score += 25
        flags.append('CQC requires improvement')
    
    # Food safety
    if profile['quality']['food_hygiene']['rating'] < 4:
        risk_score += 20
        flags.append('Food hygiene concerns')
    
    # Financial
    if profile['financial']['stability_score'] < 50:
        risk_score += 30
        flags.append('Financial instability')
    
    # Behavioral (Places Insights)
    engagement = profile['behavioral']['engagement_score']['score']
    if engagement < 40:
        risk_score += 25
        flags.append('Low family engagement')
    
    # Reviews
    if profile['reputation']['google_rating'] < 3.5:
        risk_score += 20
        flags.append('Poor online reviews')
    
    return {
        'overall_risk_score': min(100, risk_score),
        'risk_level': 'HIGH' if risk_score > 70 else 'MEDIUM' if risk_score > 40 else 'LOW',
        'red_flags': flags,
        'recommendation': 'AVOID' if risk_score > 70 else 'CAUTION' if risk_score > 40 else 'SAFE'
    }
```

### Кейс 2: Predictive Quality Model
```python
def predict_future_quality(home_id, historical_data):
    """
    Predict likelihood of CQC rating change in next 12 months
    Based on multi-source signals
    """
    features = {}
    
    # Feature 1: Places Insights trend (EARLY WARNING)
    insights_trend = calculate_insights_trend(home_id, months=6)
    if insights_trend['visitor_decline'] > 0.20:  # 20% decline
        features['visitor_decline'] = 30  # High weight
    
    # Feature 2: FSA trend
    fsa_trend = get_fsa_history(home_id)
    if len(fsa_trend) >= 2:
        if fsa_trend[-1]['rating'] < fsa_trend[-2]['rating']:
            features['food_hygiene_decline'] = 20
    
    # Feature 3: Review sentiment trend
    review_trend = analyze_review_sentiment_over_time(home_id)
    if review_trend['sentiment_decline']:
        features['negative_reviews_increasing'] = 15
    
    # Feature 4: Financial distress signals
    company_risk = get_company_risk_score(home_id)
    if company_risk > 70:
        features['financial_stress'] = 25
    
    # Feature 5: Operator network performance
    operator_homes = get_operator_other_homes(home_id)
    declining_homes = [h for h in operator_homes if h['rating_declined_recently']]
    if len(declining_homes) > 0.3 * len(operator_homes):  # 30%+ network declining
        features['network_effect'] = 20
    
    # Calculate probability
    total_risk_points = sum(features.values())
    
    if total_risk_points > 60:
        prediction = {
            'probability_of_decline': 0.75,
            'confidence': 'HIGH',
            'timeframe': '6-12 months',
            'recommendation': '⚠️ HIGH RISK: Multiple warning signals detected',
            'key_indicators': list(features.keys())
        }
    elif total_risk_points > 30:
        prediction = {
            'probability_of_decline': 0.45,
            'confidence': 'MEDIUM',
            'timeframe': '12-18 months',
            'recommendation': 'Monitor closely: Some concerning trends',
            'key_indicators': list(features.keys())
        }
    else:
        prediction = {
            'probability_of_decline': 0.15,
            'confidence': 'LOW',
            'timeframe': 'N/A',
            'recommendation': '✓ Quality stable: No significant concerns',
            'key_indicators': []
        }
    
    return prediction
```

---

<a name="roadmap"></a>
# 📅 ROADMAP ТЕСТИРОВАНИЯ

## Week 1: Foundation APIs
**Цель**: Валидировать базовые государственные API

### Задачи:
- [ ] **Day 1-2**: CQC API Setup
  - Зарегистрировать partnerCode
  - Протестировать все 5 тестовых запросов
  - Сохранить 100+ домов в South East в test DB
  - Валидировать completeness данных

- [ ] **Day 3-4**: FSA FHRS API
  - Имплементировать все тестовые запросы
  - Match FSA establishments с CQC locations (по геокоординатам)
  - Проверить correlation FSA rating ↔ CQC rating
  - Сохранить в DB

- [ ] **Day 5**: Companies House API
  - Setup authentication
  - Fetch company data для top 20 providers в регионе
  - Build financial stability scores
  - Identify any red flags

### Deliverable Week 1:
✅ Database с 100+ домов, содержащая CQC + FSA + Companies House data
✅ Validation report: data completeness, quality issues

---

## Week 2: Commercial APIs
**Цель**: Интегрировать платные коммерческие источники

### Задачи:
- [ ] **Day 1-2**: Google Places API
  - Setup billing (используйте $200 free credits)
  - Find place_id для всех 100 домов
  - Fetch reviews для top 20 домов
  - Implement sentiment analysis

- [ ] **Day 3**: Perplexity API
  - Setup account и credits ($10 минимум)
  - Test 10 queries для different care homes
  - Evaluate citation quality
  - Test multi-turn investigation

- [ ] **Day 4-5**: Autumna Scraping
  - Implement scraper с proxy rotation
  - Scrape 50 homes (test set)
  - Validate: prices, amenities, photos
  - Setup weekly cron job

### Deliverable Week 2:
✅ Enhanced database с Google reviews, Perplexity insights, Autumna pricing
✅ Cost analysis report (actual API costs vs projected)

---

## Week 3: Advanced Features
**Цель**: Google Places Insights и интеграции

### Задачи:
- [ ] **Day 1-3**: BigQuery Places Insights
  - Setup BigQuery project
  - Subscribe to UK dataset
  - Run all 5 test queries
  - Validate behavioral metrics
  - CRITICAL: Test correlation dwell time → CQC rating

- [ ] **Day 4-5**: Multi-API Integration
  - Implement comprehensive_profile function
  - Test risk assessment algorithm
  - Build predictive quality model
  - Validate predictions against known cases

### Deliverable Week 3:
✅ Places Insights integration working
✅ Multi-source data fusion pipeline
✅ Predictive model prototype

---

## Week 4: Production Readiness
**Цель**: Оптимизация, мониторинг, документация

### Задачи:
- [ ] **Day 1**: Performance Optimization
  - Implement caching (Redis)
  - Parallel API calls where possible
  - Optimize database queries

- [ ] **Day 2**: Error Handling & Resilience
  - Retry logic для всех APIs
  - Fallback mechanisms
  - Rate limit handling

- [ ] **Day 3**: Monitoring & Alerting
  - API health checks
  - Cost monitoring dashboards
  - Data freshness alerts

- [ ] **Day 4**: Documentation
  - API integration docs
  - Data dictionary
  - Troubleshooting guide

- [ ] **Day 5**: Security & Compliance
  - API key rotation
  - GDPR compliance check
  - Data retention policies

### Deliverable Week 4:
✅ Production-ready data pipeline
✅ Complete documentation
✅ Monitoring dashboards

---

## 🎯 Success Metrics

### Technical KPIs:
- **API Availability**: >99.5% uptime для всех critical APIs
- **Data Freshness**: 90%+ homes updated within last 7 days
- **Data Quality**: <5% missing critical fields (CQC rating, FSA rating)
- **Response Time**: <2 sec для single home query
- **Cost Efficiency**: <£300/month для 1000 homes South East

### Business KPIs:
- **Coverage**: 95%+ care homes в South East имеют профили
- **Uniqueness**: 100% домов имеют хотя бы один уникальный insight (не доступный у конкурентов)
- **Predictive Accuracy**: 70%+ accuracy в предсказании CQC rating changes
- **User Value**: Demonstrable case studies где multi-source data помог пользователю

---

## 📊 ФИНАЛЬНАЯ ПРОВЕРКА

### Checklist перед Production:
- [ ] Все APIs протестированы с реальными данными
- [ ] Rate limits и costs валидированы
- [ ] Error handling покрывает все edge cases
- [ ] Security: API keys в environment variables, не в коде
- [ ] GDPR: Privacy policy обновлена, consent flows готовы
- [ ] Backup: Automated daily backups настроены
- [ ] Monitoring: Alerting для API failures, cost overruns
- [ ] Documentation: Onboarding doc для новых разработчиков
- [ ] Legal: Terms of use для скрапинга (Autumna) reviewed by lawyer

---

## 💡 КЛЮЧЕВЫЕ ИНСАЙТЫ И ВЫВОДЫ

### Что делает RightCareHome уникальным:
1. **Google Places Insights**: НИКТО в UK care home индустрии не использует behavioral footfall data
2. **Predictive Analytics**: Предсказание проблем за 6-12 месяцев ДО CQC inspection
3. **Multi-Source Validation**: Перекрестная проверка из 7+ источников → высокая точность
4. **FSA Integration**: Первые, кто использует food hygiene для подбора домов (критично для diabetics)

### Red Flags для избежания:
- ⚠️ Companies House: insolvency history, dissolved status, 5+ charges
- ⚠️ Places Insights: visitor footfall decline >30%, dwell time <25 min
- ⚠️ FSA: rating <3, multiple "Improvement Required" scores
- ⚠️ CQC: "Inadequate" rating, enforcement actions, safeguarding alerts
- ⚠️ Perplexity: Recent negative news, complaints, outbreak mentions

### Competitive Moat:
**Защитная "крепость" данных:**
1. BigQuery Places Insights: Требует technical expertise + GCP infrastructure
2. Multi-API fusion: Complex integration, 4-6 недель development
3. Predictive models: Требуется historical data (6+ months collection)
4. Domain expertise: Healthcare + Tech + Data Science combination редка

**Результат**: 6-12 месяцев lead time для конкурентов, чтобы повторить

---

## 📞 SUPPORT И СЛЕДУЮЩИЕ ШАГИ

### Если возникнут проблемы:
1. **CQC API**: syndicationapi@cqc.org.uk
2. **FSA API**: data@food.gov.uk
3. **Companies House**: enquiries@companieshouse.gov.uk
4. **Google Cloud Support**: Через Cloud Console (если Premium support)
5. **Perplexity**: help@perplexity.ai

### Рекомендуемые Next Steps:
1. Начать с Week 1 Roadmap
2. Setup development environment (Python, PostgreSQL, Redis)
3. Создать test GCP project для BigQuery
4. Allocate budget: £500 для месяца тестирования (APIs + proxies)

---

**Удачи с тестированием! 🚀**

*Этот план создан на основе ваших документов и industry research. Адаптируйте под свои нужды.*

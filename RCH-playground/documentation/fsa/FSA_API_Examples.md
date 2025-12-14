# FSA FHRS API - Примеры запросов для RightCareHome

## 🔑 Базовая информация

**Base URL:** `https://api.ratings.food.gov.uk`  
**Версия API:** 2 (обязательный заголовок!)  
**Регистрация:** НЕ требуется  
**API ключ:** НЕ требуется  

## 📋 Обязательные заголовки

```bash
x-api-version: 2              # КРИТИЧНО! Без этого API не работает
Accept: application/json       # Формат ответа (или application/xml)
Accept-Language: en-GB         # Язык (en-GB для английского, cy-GB для валлийского)
```

---

## 🏥 ТЕСТ 1: Получение типов бизнеса (найти ID для care homes)

### Запрос (базовый список):
```bash
curl -X GET "https://api.ratings.food.gov.uk/BusinessTypes/basic" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

### Запрос (детальный список):
```bash
curl -X GET "https://api.ratings.food.gov.uk/BusinessTypes" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

### Ожидаемый ответ:
```json
{
  "businessTypes": [
    {
      "BusinessTypeId": 7835,
      "BusinessTypeName": "Hospitals/Childcare/Caring Premises"
    },
    {
      "BusinessTypeId": 7840,
      "BusinessTypeName": "Hotel/bed & breakfast/guest house"
    }
  ]
}
```

**💡 Важно:** `BusinessTypeId = 7835` - это ID для домов престарелых!

---

## 🔍 ТЕСТ 2: Поиск по названию дома престарелых

### Запрос:
```bash
curl -X GET "https://api.ratings.food.gov.uk/Establishments?name=Manor%20House&businessTypeId=7835&pageNumber=1&pageSize=10" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

### Параметры:
- `name=Manor%20House` - часть названия (URL encoded)
- `businessTypeId=7835` - фильтр по типу "Caring Premises"
- `pageNumber=1` - номер страницы
- `pageSize=10` - количество результатов (макс 200)

### Ожидаемый ответ:
```json
{
  "meta": {
    "dataSource": "API",
    "extractDate": "2025-11-13T10:30:00",
    "pageNumber": 1,
    "pageSize": 10,
    "totalCount": 45,
    "totalPages": 5
  },
  "establishments": [
    {
      "FHRSID": 123456,
      "BusinessName": "Manor House Care Home",
      "BusinessType": "Hospitals/Childcare/Caring Premises",
      "BusinessTypeID": 7835,
      "AddressLine1": "123 High Street",
      "AddressLine2": "Edgbaston",
      "AddressLine3": "Birmingham",
      "PostCode": "B15 2TT",
      "RatingValue": "5",
      "RatingKey": "fhrs_5_en-gb",
      "RatingDate": "2024-10-23T00:00:00",
      "LocalAuthorityName": "Birmingham",
      "LocalAuthorityWebSite": "http://www.birmingham.gov.uk",
      "LocalAuthorityEmailAddress": "food.safety@birmingham.gov.uk",
      "scores": {
        "Hygiene": 5,
        "Structural": 5,
        "ConfidenceInManagement": 5
      },
      "SchemeType": "FHRS",
      "geocode": {
        "longitude": "-1.9245",
        "latitude": "52.4562"
      },
      "RightToReply": "",
      "Distance": null,
      "NewRatingPending": false
    }
  ]
}
```

---

## 📮 ТЕСТ 3: Поиск по почтовому индексу

### Запрос:
```bash
curl -X GET "https://api.ratings.food.gov.uk/Establishments?address=B15%202TT&businessTypeId=7835&pageSize=20" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

### Параметры:
- `address=B15%202TT` - почтовый индекс (или часть адреса)
- `businessTypeId=7835` - фильтр по care homes

---

## 📍 ТЕСТ 4: Поиск по координатам (геолокация)

### Запрос:
```bash
curl -X GET "https://api.ratings.food.gov.uk/Establishments?latitude=52.4862&longitude=-1.8904&maxDistanceLimit=2&businessTypeId=7835&pageSize=10" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

### Параметры:
- `latitude=52.4862` - широта (центр Birmingham)
- `longitude=-1.8904` - долгота
- `maxDistanceLimit=2` - радиус поиска в милях (!)
- `businessTypeId=7835` - фильтр по care homes

**💡 Важно:** Расстояние в МИЛЯХ, не километрах!

### Ожидаемый ответ (с расстоянием):
```json
{
  "establishments": [
    {
      "FHRSID": 123456,
      "BusinessName": "Oakwood Care Home",
      "RatingValue": "5",
      "Distance": 0.8,  // в милях от указанной точки
      "geocode": {
        "longitude": "-1.9100",
        "latitude": "52.4750"
      }
    }
  ]
}
```

---

## 🏛️ ТЕСТ 5: Поиск по местному органу власти

### Шаг 1 - Получить список органов власти:
```bash
curl -X GET "https://api.ratings.food.gov.uk/Authorities/basic" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

### Ожидаемый ответ:
```json
{
  "authorities": [
    {
      "LocalAuthorityId": 197,
      "LocalAuthorityIdCode": "760",
      "Name": "Birmingham"
    },
    {
      "LocalAuthorityId": 198,
      "LocalAuthorityIdCode": "330",
      "Name": "Manchester"
    }
  ]
}
```

### Шаг 2 - Поиск care homes в Birmingham (ID=197):
```bash
curl -X GET "https://api.ratings.food.gov.uk/Establishments?localAuthorityId=197&businessTypeId=7835&pageSize=50" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

---

## 🔬 ТЕСТ 6: Детальная информация о конкретном заведении

### Запрос:
```bash
curl -X GET "https://api.ratings.food.gov.uk/Establishments/123456" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

### Ожидаемый детальный ответ:
```json
{
  "FHRSID": 123456,
  "BusinessName": "Manor House Care Home",
  "BusinessType": "Hospitals/Childcare/Caring Premises",
  "BusinessTypeID": 7835,
  "AddressLine1": "123 High Street",
  "AddressLine2": "Edgbaston",
  "AddressLine3": "Birmingham",
  "AddressLine4": "West Midlands",
  "PostCode": "B15 2TT",
  "Phone": "0121 123 4567",
  "RatingValue": "5",
  "RatingKey": "fhrs_5_en-gb",
  "RatingDate": "2024-10-23T00:00:00",
  "LocalAuthorityName": "Birmingham",
  "LocalAuthorityWebSite": "http://www.birmingham.gov.uk",
  "LocalAuthorityEmailAddress": "food.safety@birmingham.gov.uk",
  "scores": {
    "Hygiene": 5,
    "Structural": 5,
    "ConfidenceInManagement": 5
  },
  "SchemeType": "FHRS",
  "geocode": {
    "longitude": "-1.924567",
    "latitude": "52.456234"
  },
  "RightToReply": "We are proud of our food safety standards and regularly invest in staff training.",
  "Distance": null,
  "NewRatingPending": false,
  "meta": {
    "dataSource": "API",
    "extractDate": "2025-11-13T10:30:00"
  }
}
```

---

## 📊 ТЕСТ 7: Справочник рейтингов (для интерпретации)

### Запрос:
```bash
curl -X GET "https://api.ratings.food.gov.uk/Ratings" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

### Ожидаемый ответ:
```json
{
  "ratings": [
    {
      "ratingId": 1,
      "ratingKey": "fhrs_5_en-gb",
      "ratingName": "5",
      "ratingDescription": "Hygiene standards are very good"
    },
    {
      "ratingId": 2,
      "ratingKey": "fhrs_4_en-gb",
      "ratingName": "4",
      "ratingDescription": "Hygiene standards are good"
    },
    {
      "ratingId": 3,
      "ratingKey": "fhrs_3_en-gb",
      "ratingName": "3",
      "ratingDescription": "Hygiene standards are generally satisfactory"
    },
    {
      "ratingId": 4,
      "ratingKey": "fhrs_2_en-gb",
      "ratingName": "2",
      "ratingDescription": "Some improvement is necessary"
    },
    {
      "ratingId": 5,
      "ratingKey": "fhrs_1_en-gb",
      "ratingName": "1",
      "ratingDescription": "Major improvement is necessary"
    },
    {
      "ratingId": 6,
      "ratingKey": "fhrs_0_en-gb",
      "ratingName": "0",
      "ratingDescription": "Urgent improvement is necessary"
    },
    {
      "ratingId": 7,
      "ratingKey": "fhrs_exempt_en-gb",
      "ratingName": "Exempt",
      "ratingDescription": "The business is exempt from the scheme"
    },
    {
      "ratingId": 8,
      "ratingKey": "fhis_pass_en-gb",
      "ratingName": "Pass",
      "ratingDescription": "FHIS Pass (Scotland)"
    },
    {
      "ratingId": 9,
      "ratingKey": "fhis_improvement_required_en-gb",
      "ratingName": "Improvement Required",
      "ratingDescription": "FHIS Improvement Required (Scotland)"
    }
  ]
}
```

---

## 🎯 КЛЮЧЕВЫЕ ПОЛЯ ДЛЯ RightCareHome

### Обязательные для отображения:
1. **RatingValue** (string) - "0" to "5" или "Pass"/"Improvement Required"
2. **RatingDate** (datetime) - дата последней инспекции
3. **BusinessName** (string) - название дома престарелых
4. **PostCode** (string) - почтовый индекс

### Критичные для анализа качества:
5. **scores.Hygiene** (int) - 0-20 (чем ниже, тем лучше!)
6. **scores.Structural** (int) - 0-20 (чем ниже, тем лучше!)
7. **scores.ConfidenceInManagement** (int) - 0-30 (чем ниже, тем лучше!)

**⚠️ ВАЖНО:** В scores чем НИЖЕ число, тем ЛУЧШЕ! Это penalty points!
- Hygiene: 0-5 = Excellent, 6-10 = Good, 11-15 = Fair, 16-20 = Poor
- Structural: 0-5 = Excellent, 6-10 = Good, 11-15 = Fair, 16-20 = Poor
- Management: 0-5 = Excellent, 6-10 = Good, 11-20 = Fair, 21-30 = Poor

### Дополнительные поля:
8. **geocode** (object) - координаты для карты
9. **RightToReply** (string) - официальный ответ оператора
10. **NewRatingPending** (boolean) - ожидается ли новая инспекция

---

## 🚀 Продвинутые запросы для RightCareHome

### 1. Найти все care homes с рейтингом 5/5 в радиусе 5 миль:
```bash
curl -X GET "https://api.ratings.food.gov.uk/Establishments?latitude=52.4862&longitude=-1.8904&maxDistanceLimit=5&businessTypeId=7835&ratingKey=fhrs_5_en-gb&pageSize=50" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

### 2. Найти care homes с низким рейтингом (для алертов):
```bash
curl -X GET "https://api.ratings.food.gov.uk/Establishments?localAuthorityId=197&businessTypeId=7835&ratingKey=fhrs_0_en-gb,fhrs_1_en-gb,fhrs_2_en-gb" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

### 3. Поиск с сортировкой по дате инспекции:
```bash
curl -X GET "https://api.ratings.food.gov.uk/Establishments?businessTypeId=7835&localAuthorityId=197&sortOptionKey=rating" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

**Доступные sortOptionKey:**
- `rating` - по рейтингу
- `alpha` - по алфавиту
- `inspection` - по дате инспекции (новейшие первыми)
- `distance` - по расстоянию (только для geo-запросов)

---

## 🔄 Пагинация для больших результатов

```bash
# Страница 1
curl -X GET "https://api.ratings.food.gov.uk/Establishments?businessTypeId=7835&localAuthorityId=197&pageNumber=1&pageSize=100" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"

# Страница 2
curl -X GET "https://api.ratings.food.gov.uk/Establishments?businessTypeId=7835&localAuthorityId=197&pageNumber=2&pageSize=100" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

**⚠️ Лимиты:**
- Рекомендуемый pageSize: ≤ 200
- При pageSize > 200 возможны 429 (Too Many Requests)
- Для массовых обновлений используйте [Open Data Downloads](http://ratings.food.gov.uk/open-data/)

---

## 🏴󐁧󐁢󐁳󐁣󐁴󐁿 Шотландия (FHIS) - Особенности

В Шотландии используется FHIS (Food Hygiene Information Scheme):
- Рейтинги: "Pass" / "Improvement Required" (НЕ 0-5!)
- SchemeType: "FHIS" (вместо "FHRS")

### Поиск в Шотландии:
```bash
curl -X GET "https://api.ratings.food.gov.uk/Establishments?businessTypeId=7835&localAuthorityId=317&ratingKey=fhis_pass_en-gb" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

---

## 💡 Рекомендации для интеграции в RightCareHome

### 1. Алгоритм поиска care homes:
```
1. Получить координаты пользователя (или выбранного района)
2. Запросить Establishments с:
   - latitude/longitude + maxDistanceLimit=5
   - businessTypeId=7835
   - pageSize=50
3. Для каждого результата получить детальную информацию (если нужны scores)
4. Отфильтровать по RatingValue >= 4 (для premium listings)
5. Сортировать по Distance или RatingDate
```

### 2. Фильтры для разных тарифов:

**FREE Plan:**
- Показывать только RatingValue
- Дата последней инспекции

**Professional Plan (£119):**
- Показывать детальные scores (Hygiene, Structural, Management)
- Тренд: сравнить с предыдущими инспекциями (нужно хранить историю)
- RightToReply

**Premium Plan (£299):**
- Мониторинг изменений рейтинга
- Алерты при снижении рейтинга
- Прогноз следующей инспекции

### 3. Алерты и красные флаги:

```python
def assess_food_safety_risk(establishment):
    rating = establishment.get('RatingValue')
    rating_date = establishment.get('RatingDate')
    scores = establishment.get('scores', {})
    
    # Red flags
    if rating in ['0', '1', '2']:
        return "🚨 CRITICAL - Avoid"
    
    if rating == '3':
        return "⚠️ WARNING - Needs improvement"
    
    # Check inspection date
    days_since_inspection = (datetime.now() - rating_date).days
    if days_since_inspection > 730:  # 2 years
        return "⚠️ WARNING - Inspection overdue"
    
    # Check detailed scores (if available)
    if scores.get('Hygiene', 0) > 10:
        return "⚠️ WARNING - Hygiene concerns"
    
    if rating in ['4', '5']:
        return "✅ SAFE - Good food safety"
    
    return "ℹ️ No rating available"
```

### 4. Комбинация с CQC данными:

```
Manor House Care Home:
├─ CQC: Outstanding (официальное качество ухода)
├─ FSA: 5/5 (отличная гигиена питания)
│   ├─ Hygiene: 5/20 ← превосходно
│   ├─ Structural: 5/20 ← превосходно
│   └─ Management: 5/30 ← превосходно
├─ Google Places: 78% repeat visitors, 48 min dwell
└─ 🎯 RECOMMENDATION: EXCELLENT для диабета/аллергий
```

---

## 📝 Частота обновлений

- **API (live):** Обновляется при публикации инспекций (обычно 1-2 недели после инспекции)
- **Open Data:** Обновляется ежедневно в 02:00 UTC
- **Рекомендация:** Проверять обновления еженедельно для мониторинга

---

## 🔗 Полезные ссылки

- API Documentation: https://api.ratings.food.gov.uk/help
- Open Data Downloads: http://ratings.food.gov.uk/open-data/
- Official Website: https://ratings.food.gov.uk
- FSA Main Site: https://www.food.gov.uk

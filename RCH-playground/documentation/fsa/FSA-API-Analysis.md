# 📋 Полный анализ запросов и ответов FSA FHRS API

## 🎯 Содержание

1. [Структура API запросов](#структура-api-запросов)
2. [Структура ответов](#структура-ответов)
3. [Flow использования](#flow-использования)
4. [Примеры с реальными домами](#примеры-с-реальными-домами)
5. [Критичные поля для RightCareHome](#критичные-поля-для-rightcarehome)
6. [Сравнение Backend vs FSA Direct](#сравнение-backend-vs-fsa-direct)

---

## Структура API запросов

### 1️⃣ Backend API (127.0.0.1:8000)

#### По названию заведения
```bash
GET /api/fsa/search?name=Kinross%20Residential%20Care%20Home
Accept: application/json

# Параметры:
# - name: название или часть названия
# - pageSize: (опционально) количество результатов на странице (по умолчанию 10)
```

**Примеры:**
```bash
curl "http://127.0.0.1:8000/api/fsa/search?name=Kinross%20Residential%20Care%20Home"
curl "http://127.0.0.1:8000/api/fsa/search?name=Meadows%20House"
curl "http://127.0.0.1:8000/api/fsa/search?name=Roborough%20House"

# Частичный поиск (более широкий)
curl "http://127.0.0.1:8000/api/fsa/search?name=Kinross"
```

#### По геолокации
```bash
GET /api/fsa/search?latitude=50.8435&longitude=-1.0365&max_distance=5.0
Accept: application/json

# Параметры:
# - latitude: координата широты
# - longitude: координата долготы
# - max_distance: максимальное расстояние в милях (опционально, по умолчанию 5)
```

**Примеры:**
```bash
# Portsmouth (Kinross Residential Care Home)
curl "http://127.0.0.1:8000/api/fsa/search?latitude=50.8435&longitude=-1.0365&max_distance=5.0"

# London (Meadows House)
curl "http://127.0.0.1:8000/api/fsa/search?latitude=51.4769&longitude=-0.0205&max_distance=5.0"

# Plymouth (Roborough House)
curl "http://127.0.0.1:8000/api/fsa/search?latitude=50.3755&longitude=-4.1427&max_distance=5.0"
```

#### Получение деталей по FHRSID
```bash
GET /api/fsa/establishment/{fhrs_id}
Accept: application/json

# Пример:
curl "http://127.0.0.1:8000/api/fsa/establishment/1234567"

# С Diabetes Score
curl "http://127.0.0.1:8000/api/fsa/establishment/1234567/diabetes-score"
```

---

### 2️⃣ Прямые FSA API запросы (api.ratings.food.gov.uk)

#### Обязательные заголовки для ВСЕХ запросов
```
x-api-version: 2          ← КРИТИЧНО! Без этого API не работает
Accept: application/json  ← Формат ответа
Accept-Language: en-GB    ← Рекомендуется
```

#### По названию заведения
```bash
GET /Establishments?name=Kinross%20Residential%20Care%20Home
x-api-version: 2
Accept: application/json
```

**Примеры:**
```bash
curl -X GET "https://api.ratings.food.gov.uk/Establishments?name=Kinross" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"

curl -X GET "https://api.ratings.food.gov.uk/Establishments?name=Meadows%20House" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"

curl -X GET "https://api.ratings.food.gov.uk/Establishments?name=Roborough%20House" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

#### По типу бизнеса и городу
```bash
GET /Establishments?businessTypeId=7835&localAuthorityId=197&pageSize=20
x-api-version: 2
Accept: application/json

# Параметры:
# - businessTypeId: 7835 = "Hospitals/Childcare/Caring Premises" (care homes)
# - localAuthorityId: код местного органа власти
# - pageSize: количество результатов на странице
# - name: (опционально) для дополнительной фильтрации
```

**Local Authority IDs:**
- Portsmouth: 197
- London (Greenwich): 204
- Plymouth: 207

**Примеры:**
```bash
# Care homes в Portsmouth
curl -X GET "https://api.ratings.food.gov.uk/Establishments?businessTypeId=7835&localAuthorityId=197&name=Kinross" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"

# Care homes в London
curl -X GET "https://api.ratings.food.gov.uk/Establishments?businessTypeId=7835&localAuthorityId=204&name=Meadows" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"

# Care homes в Plymouth
curl -X GET "https://api.ratings.food.gov.uk/Establishments?businessTypeId=7835&localAuthorityId=207&name=Roborough" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

#### По геолокации
```bash
GET /Establishments?latitude=50.8435&longitude=-1.0365&maxDistanceLimit=5.0
x-api-version: 2
Accept: application/json

# ВАЖНО: параметр называется maxDistanceLimit (не max_distance!)
```

**Примеры:**
```bash
curl -X GET "https://api.ratings.food.gov.uk/Establishments?latitude=50.8435&longitude=-1.0365&maxDistanceLimit=5.0" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

#### Получение деталей по FHRS ID
```bash
GET /Establishments/{fhrs_id}
x-api-version: 2
Accept: application/json

# Пример с реальным ID
curl -X GET "https://api.ratings.food.gov.uk/Establishments/1234567" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

---

## Структура ответов

### Успешный ответ (HTTP 200)

```json
{
  "meta": {
    "dataSource": "ElasticSearch",
    "itemCount": 1,
    "returncode": "OK",
    "totalCount": 1
  },
  "establishments": [
    {
      "FHRSID": 1234567,
      "BusinessName": "Kinross Residential Care Home",
      "BusinessType": "Hospitals/Childcare/Caring Premises",
      "BusinessTypeID": "7835",
      "AddressLine1": "201 Havant Road",
      "AddressLine2": "Drayton",
      "AddressLine3": "Portsmouth",
      "PostCode": "PO6 1EE",
      "Phone": "02392 XXX XXX",
      "LocalAuthorityName": "Portsmouth",
      "LocalAuthorityCode": "197",
      "RatingValue": "5",
      "RatingDate": "2024-06-15T00:00:00",
      "SchemeType": "FHRS",
      "scores": {
        "Hygiene": 5,
        "Structural": 8,
        "ConfidenceInManagement": 10
      },
      "geocode": {
        "latitude": 50.8435,
        "longitude": -1.0365
      },
      "RightToReply": "We fully agree with the rating..."
    }
  ]
}
```

### Структура элемента establishment

| Поле | Тип | Описание | Пример |
|------|-----|---------|--------|
| **FHRSID** | int | Уникальный ID | 1234567 |
| **BusinessName** | string | Название заведения | "Kinross Residential Care Home" |
| **BusinessTypeID** | string | ID типа (7835 = care homes) | "7835" |
| **PostCode** | string | Почтовый индекс | "PO6 1EE" |
| **RatingValue** | string | Рейтинг 0-5 (или Pass/Improvement Required для Scotland) | "5" |
| **RatingDate** | datetime | Дата последней инспекции (ISO format) | "2024-06-15T00:00:00" |
| **scores.Hygiene** | int | Гигиена (0-20, ниже лучше) | 5 |
| **scores.Structural** | int | Структура (0-20, ниже лучше) | 8 |
| **scores.ConfidenceInManagement** | int | Управление (0-30, ниже лучше) | 10 |
| **geocode.latitude** | float | Широта | 50.8435 |
| **geocode.longitude** | float | Долгота | -1.0365 |
| **SchemeType** | string | Тип схемы: FHRS (England/Wales) или FHIS (Scotland) | "FHRS" |
| **RightToReply** | string | Ответ оператора на отчёт | "We fully agree..." |
| **LocalAuthorityName** | string | Название местного органа | "Portsmouth" |

### Структура meta

| Поле | Значение |
|------|----------|
| **dataSource** | "ElasticSearch" |
| **itemCount** | Количество элементов в текущем ответе |
| **returncode** | "OK" (успех) или код ошибки |
| **totalCount** | Всего результатов в базе |

---

## Flow использования

### Шаг 1: ПОИСК (получить FHRSID)

```
Вход: название заведения или координаты
↓
Запрос: GET /Establishments?name=Kinross
↓
Ответ: список заведений с FHRSID
↓
Выход: FHRSID (например: 1234567)
```

**Проверяем:**
- ✓ returncode = "OK"
- ✓ totalCount > 0
- ✓ establishments не пусто
- ✓ FHRSID присутствует

### Шаг 2: ПАРСИНГ РЕЗУЛЬТАТОВ ПОИСКА

```
Вход:響 массив establishments из результата поиска
↓
Действия:
  • Извлечь FHRSID
  • Проверить RatingValue (0-5)
  • Проверить RatingDate (дата инспекции)
  • Сравнить с другими результатами
↓
Выход: FHRSID выбранного заведения
```

### Шаг 3: ПОЛУЧЕНИЕ ДЕТАЛЕЙ (использовать FHRSID)

```
Вход: FHRSID (например: 1234567)
↓
Запрос: GET /Establishments/1234567
↓
Ответ: полная информация включая:
  • scores (Hygiene, Structural, ConfidenceInManagement)
  • geocode (latitude, longitude)
  • RightToReply
  • Phone
↓
Выход: полные данные для анализа
```

### Шаг 4: АНАЛИЗ SCORES

**Интерпретация баллов (помните: НИЖЕ = ЛУЧШЕ!):**

```
Hygiene (0-20):
  • 0-5:    Отлично
  • 6-10:   Хорошо
  • 11-15:  Удовлетворительно
  • 16-20:  Плохо

Structural (0-20):
  • 0-5:    Отлично
  • 6-10:   Хорошо
  • 11-15:  Удовлетворительно
  • 16-20:  Плохо

ConfidenceInManagement (0-30):
  • 0-10:   Отлично
  • 11-20:  Хорошо
  • 21-30:  Требует внимания

RatingValue (0-5):
  • 5: Excellent
  • 4: Good
  • 3: Acceptable
  • 2: Needs Improvement
  • 1: Urgent Improvement Required
  • 0: Awaiting Inspection
```

### Шаг 5: РАССЧИТАТЬ FSA HEALTH SCORE ДЛЯ RIGHTCAREHOME

```
Formula:
  Hygiene_normalized = (20 - Hygiene_score) / 20 * 100
  Structural_normalized = (20 - Structural_score) / 20 * 100
  Management_normalized = (30 - ConfidenceInManagement_score) / 30 * 100

  FSA_Score = (
    Hygiene_normalized * 0.40 +
    Structural_normalized * 0.30 +
    Management_normalized * 0.30
  )

  Final_Score = Round(FSA_Score, 0)
```

**Интерпретация Final Score:**
```
80-100: EXCELLENT - Выше среднего
60-79:  GOOD - Среднее
40-59:  FAIR - Ниже среднего
0-39:   POOR - Требует внимания
```

---

## Примеры с реальными домами

### 1. Kinross Residential Care Home (Portsmouth)

**Адрес:**
```
201 Havant Road
Drayton
Portsmouth, Hampshire
PO6 1EE
```

**Координаты:** 50.8435, -1.0365

**Backend запрос:**
```bash
curl "http://127.0.0.1:8000/api/fsa/search?name=Kinross%20Residential%20Care%20Home"
```

**Прямой FSA запрос:**
```bash
curl -X GET "https://api.ratings.food.gov.uk/Establishments?name=Kinross" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

**Ожидаемый ответ (примерно):**
```json
{
  "meta": {
    "totalCount": 1,
    "itemCount": 1,
    "returncode": "OK"
  },
  "establishments": [
    {
      "FHRSID": 1234567,
      "BusinessName": "Kinross Residential Care Home",
      "PostCode": "PO6 1EE",
      "RatingValue": "5",
      "RatingDate": "2024-06-15T00:00:00",
      "scores": {
        "Hygiene": 5,
        "Structural": 8,
        "ConfidenceInManagement": 10
      }
    }
  ]
}
```

---

### 2. Meadows House Residential and Nursing Home (London)

**Адрес:**
```
Cullum Welch Court
London
SE3 0PW
```

**Координаты:** 51.4769, -0.0205

**Backend запрос:**
```bash
curl "http://127.0.0.1:8000/api/fsa/search?name=Meadows%20House"
```

**Прямой FSA запрос:**
```bash
curl -X GET "https://api.ratings.food.gov.uk/Establishments?name=Meadows%20House" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

---

### 3. Roborough House (Plymouth)

**Адрес:**
```
Tamerton Road
Woolwell
Plymouth, Devon
PL6 7BQ
```

**Координаты:** 50.3755, -4.1427

**Backend запрос:**
```bash
curl "http://127.0.0.1:8000/api/fsa/search?name=Roborough%20House"
```

**Прямой FSA запрос:**
```bash
curl -X GET "https://api.ratings.food.gov.uk/Establishments?name=Roborough%20House" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

---

## Критичные поля для RightCareHome

### Для основной функциональности (обязательно)

```
✓ FHRSID              - уникальный идентификатор заведения
✓ BusinessName        - название для отображения
✓ RatingValue         - основной рейтинг (0-5)
✓ RatingDate          - когда была последняя инспекция
✓ PostCode            - для геолокации
```

### Для анализа пищевой безопасности

```
✓ scores.Hygiene              - КРИТИЧНЫЙ параметр
✓ scores.Structural           - ВАЖНЫЙ параметр
✓ scores.ConfidenceInManagement - ВАЖНЫЙ параметр
✓ LocalAuthorityName          - контекст
```

### Для анализа пригодности для диабетиков

```
✓ BusinessName                    - для парсинга (содержит ли "diabetic friendly")
✓ scores.Hygiene                  - критично для людей с диабетом
✓ scores.ConfidenceInManagement   - управление рисками питания
✓ RatingDate                      - актуальность данных
```

### Для геолокации и навигации

```
✓ geocode.latitude   - точная координата
✓ geocode.longitude  - точная координата
✓ PostCode          - для отображения
✓ AddressLine1-3    - полный адрес
```

### Для связи

```
✓ Phone              - если доступен
✓ AddressLine1       - для писем
✓ PostCode           - для почты
```

---

## Сравнение Backend vs FSA Direct

| Критерий | Backend API | FSA Direct API |
|----------|-------------|----------------|
| **По названию** | ✓ Поддерживается | ✓ Поддерживается |
| **По геолокации** | ✓ max_distance | ✓ maxDistanceLimit |
| **По типу + городу** | ✗ Не поддерживается | ✓ businessTypeId + localAuthorityId |
| **Diabetes Score** | ✓ /diabetes-score endpoint | ✗ Не поддерживается |
| **Регистрация** | ✗ Не требуется | ✗ Не требуется |
| **API ключ** | ✗ Не требуется | ✗ Не требуется |
| **Lимиты** | Зависит от backend | ~200 requests/hour рекомендуется |
| **Скорость** | Может быть кэширована | Всегда свежие данные |
| **Надёжность** | Зависит от вашего backend | 99.9% uptime |

---

## Python примеры

### Через Backend API

```python
import requests

# Поиск по названию
response = requests.get(
    "http://127.0.0.1:8000/api/fsa/search",
    params={"name": "Kinross Residential Care Home"}
)
data = response.json()
print(data['establishments'])

# Получить детали
fhrs_id = data['establishments'][0]['FHRSID']
details = requests.get(
    f"http://127.0.0.1:8000/api/fsa/establishment/{fhrs_id}"
).json()
print(details['scores'])
```

### Через прямой FSA API

```python
import requests

headers = {
    "x-api-version": "2",
    "Accept": "application/json"
}

# Поиск
response = requests.get(
    "https://api.ratings.food.gov.uk/Establishments",
    params={"name": "Kinross"},
    headers=headers
)
data = response.json()

# Получить детали
fhrs_id = data['establishments'][0]['FHRSID']
details = requests.get(
    f"https://api.ratings.food.gov.uk/Establishments/{fhrs_id}",
    headers=headers
).json()
print(details['establishments'][0]['scores'])
```

---

## Чек-лист для тестирования

### FSA API тестирование

- [ ] Поиск по названию возвращает результаты
- [ ] FHRSID присутствует в результатах
- [ ] RatingValue находится в диапазоне 0-5
- [ ] RatingDate имеет корректный формат
- [ ] Детальный запрос по FHRSID работает
- [ ] scores присутствуют (Hygiene, Structural, Management)
- [ ] geocode заполнены (latitude, longitude)
- [ ] Поиск по геолокации работает
- [ ] Поиск по типу + городу работает

### RightCareHome интеграция

- [ ] FSA Score рассчитывается корректно (0-100)
- [ ] Diabetes Score доступен
- [ ] Данные кэшируются
- [ ] Rate limiting работает
- [ ] Error handling реализован
- [ ] Логирование настроено

---

*Документ: Полный анализ FSA FHRS API*  
*Дата: November 2025*  
*Версия: 2.0*

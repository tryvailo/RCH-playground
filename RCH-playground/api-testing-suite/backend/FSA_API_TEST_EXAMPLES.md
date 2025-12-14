# FSA FHRS API - Примеры запросов для тестирования

## 1. Запросы через наш Backend API

### Поиск по названию заведения

```bash
# Поиск "Kinross Residential Care Home"
curl -X GET "http://127.0.0.1:8000/api/fsa/search?name=Kinross%20Residential%20Care%20Home" \
  -H "Accept: application/json"

# Поиск "Meadows House Residential and Nursing Home"
curl -X GET "http://127.0.0.1:8000/api/fsa/search?name=Meadows%20House%20Residential%20and%20Nursing%20Home" \
  -H "Accept: application/json"

# Поиск "Roborough House"
curl -X GET "http://127.0.0.1:8000/api/fsa/search?name=Roborough%20House" \
  -H "Accept: application/json"

# Поиск по частичному названию (например, "Kinross")
curl -X GET "http://127.0.0.1:8000/api/fsa/search?name=Kinross" \
  -H "Accept: application/json"
```

### Поиск по геолокации

```bash
# Поиск в районе Portsmouth (координаты для Kinross Residential Care Home)
curl -X GET "http://127.0.0.1:8000/api/fsa/search?latitude=50.8435&longitude=-1.0365&max_distance=5.0" \
  -H "Accept: application/json"

# Поиск в районе London (координаты для Meadows House)
curl -X GET "http://127.0.0.1:8000/api/fsa/search?latitude=51.4769&longitude=-0.0205&max_distance=5.0" \
  -H "Accept: application/json"

# Поиск в районе Plymouth (координаты для Roborough House)
curl -X GET "http://127.0.0.1:8000/api/fsa/search?latitude=50.3755&longitude=-4.1427&max_distance=5.0" \
  -H "Accept: application/json"
```

### Получение деталей заведения по FHRS ID

```bash
# Замените {fhrs_id} на реальный ID из результатов поиска
curl -X GET "http://127.0.0.1:8000/api/fsa/establishment/{fhrs_id}" \
  -H "Accept: application/json"

# Пример с Diabetes Score
curl -X GET "http://127.0.0.1:8000/api/fsa/establishment/{fhrs_id}/diabetes-score" \
  -H "Accept: application/json"
```

---

## 2. Прямые запросы к FSA FHRS API

### Поиск по названию (прямой запрос к FSA API)

```bash
# Поиск "Kinross Residential Care Home"
curl -X GET "http://api.ratings.food.gov.uk/Establishments?name=Kinross%20Residential%20Care%20Home" \
  -H "x-api-version: 2" \
  -H "Accept-Language: en-GB" \
  -H "Accept: application/json"

# Поиск "Meadows House"
curl -X GET "http://api.ratings.food.gov.uk/Establishments?name=Meadows%20House" \
  -H "x-api-version: 2" \
  -H "Accept-Language: en-GB" \
  -H "Accept: application/json"

# Поиск "Roborough House"
curl -X GET "http://api.ratings.food.gov.uk/Establishments?name=Roborough%20House" \
  -H "x-api-version: 2" \
  -H "Accept-Language: en-GB" \
  -H "Accept: application/json"

# Поиск по частичному названию (более широкий поиск)
curl -X GET "http://api.ratings.food.gov.uk/Establishments?name=Kinross" \
  -H "x-api-version: 2" \
  -H "Accept-Language: en-GB" \
  -H "Accept: application/json"

# Поиск "Care Home" в Portsmouth
curl -X GET "http://api.ratings.food.gov.uk/Establishments?name=Care%20Home&localAuthorityId=197" \
  -H "x-api-version: 2" \
  -H "Accept-Language: en-GB" \
  -H "Accept: application/json"
```

### Поиск по геолокации (прямой запрос к FSA API)

```bash
# Поиск в районе Portsmouth (координаты приблизительные)
curl -X GET "http://api.ratings.food.gov.uk/Establishments?latitude=50.8435&longitude=-1.0365&maxDistanceLimit=5.0" \
  -H "x-api-version: 2" \
  -H "Accept-Language: en-GB" \
  -H "Accept: application/json"

# Поиск в районе London
curl -X GET "http://api.ratings.food.gov.uk/Establishments?latitude=51.4769&longitude=-0.0205&maxDistanceLimit=5.0" \
  -H "x-api-version: 2" \
  -H "Accept-Language: en-GB" \
  -H "Accept: application/json"
```

### Поиск по типу бизнеса (Care Homes)

```bash
# Поиск всех заведений типа "Hospitals/Childcare/Caring Premises" (ID: 7835)
curl -X GET "http://api.ratings.food.gov.uk/Establishments?businessTypeId=7835&pageSize=10" \
  -H "x-api-version: 2" \
  -H "Accept-Language: en-GB" \
  -H "Accept: application/json"

# Поиск care homes в конкретном районе (Portsmouth)
curl -X GET "http://api.ratings.food.gov.uk/Establishments?businessTypeId=7835&localAuthorityId=197&pageSize=20" \
  -H "x-api-version: 2" \
  -H "Accept-Language: en-GB" \
  -H "Accept: application/json"
```

### Получение деталей заведения по FHRS ID

```bash
# Замените {fhrs_id} на реальный ID
curl -X GET "http://api.ratings.food.gov.uk/Establishments/{fhrs_id}" \
  -H "x-api-version: 2" \
  -H "Accept-Language: en-GB" \
  -H "Accept: application/json"
```

---

## 3. Примеры для Python

### Поиск через наш Backend

```python
import requests

# Поиск по названию
response = requests.get(
    "http://127.0.0.1:8000/api/fsa/search",
    params={"name": "Kinross Residential Care Home"}
)
print(response.json())

# Поиск по геолокации
response = requests.get(
    "http://127.0.0.1:8000/api/fsa/search",
    params={
        "latitude": 50.8435,
        "longitude": -1.0365,
        "max_distance": 5.0
    }
)
print(response.json())
```

### Прямой запрос к FSA API

```python
import requests

headers = {
    "x-api-version": "2",
    "Accept-Language": "en-GB",
    "Accept": "application/json"
}

# Поиск по названию
response = requests.get(
    "http://api.ratings.food.gov.uk/Establishments",
    params={"name": "Kinross Residential Care Home"},
    headers=headers
)
print(response.json())

# Поиск по геолокации
response = requests.get(
    "http://api.ratings.food.gov.uk/Establishments",
    params={
        "latitude": 50.8435,
        "longitude": -1.0365,
        "maxDistanceLimit": 5.0
    },
    headers=headers
)
print(response.json())
```

---

## 4. Важные замечания

### Обязательные заголовки для FSA API:
- `x-api-version: 2` - **ОБЯЗАТЕЛЕН!** Без него API вернет ошибку
- `Accept-Language: en-GB` - рекомендуется
- `Accept: application/json` - рекомендуется

### BusinessTypeId для Care Homes:
- `7835` = "Hospitals/Childcare/Caring Premises" (включает care homes)

### Local Authority IDs (примеры):
- `197` = Portsmouth
- `204` = Greenwich (London)
- `207` = Plymouth

### Формат ответа:
```json
{
  "establishments": [
    {
      "FHRSID": 123456,
      "BusinessName": "Care Home Name",
      "BusinessType": "Hospitals/Childcare/Caring Premises",
      "BusinessTypeID": "7835",
      "AddressLine1": "123 Street",
      "AddressLine2": "Area",
      "AddressLine3": "City",
      "PostCode": "PO6 1EE",
      "RatingValue": "5",
      "RatingDate": "2024-01-15T00:00:00",
      "LocalAuthorityName": "Portsmouth",
      "LocalAuthorityCode": "197",
      "scores": {
        "Hygiene": 0,
        "Structural": 0,
        "ConfidenceInManagement": 0
      }
    }
  ],
  "meta": {
    "dataSource": "ElasticSearch",
    "itemCount": 1,
    "returncode": "OK",
    "totalCount": 1
  }
}
```

---

## 5. Быстрый тест

```bash
# Самый простой тест - поиск "Kinross"
curl -X GET "http://api.ratings.food.gov.uk/Establishments?name=Kinross" \
  -H "x-api-version: 2" \
  -H "Accept: application/json" | python3 -m json.tool
```

Этот запрос должен вернуть список заведений с названием, содержащим "Kinross".


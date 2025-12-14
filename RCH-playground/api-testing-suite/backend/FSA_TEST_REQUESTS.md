# FSA API - Примеры запросов с заведениями из настроек

## Тестовые данные из `test_data.json`:

1. **Kinross Residential Care Home**
   - Адрес: 201 Havant Road, Drayton, Portsmouth, Hampshire, PO6 1EE
   - Город: Portsmouth
   - Почтовый индекс: PO6 1EE

2. **Meadows House Residential and Nursing Home**
   - Адрес: Cullum Welch Court, London, SE3 0PW
   - Город: London
   - Почтовый индекс: SE3 0PW

3. **Roborough House**
   - Адрес: Tamerton Road, Woolwell, Plymouth, Devon, PL6 7BQ
   - Город: Plymouth
   - Почтовый индекс: PL6 7BQ

---

## Примеры запросов через наш Backend API

### 1. Kinross Residential Care Home

```bash
# Полный запрос через наш backend
curl -X GET "http://127.0.0.1:8000/api/fsa/search?name=Kinross%20Residential%20Care%20Home" \
  -H "Accept: application/json"

# Краткая версия
curl "http://127.0.0.1:8000/api/fsa/search?name=Kinross%20Residential%20Care%20Home"

# Поиск по частичному названию (может найти больше результатов)
curl "http://127.0.0.1:8000/api/fsa/search?name=Kinross"

# Поиск по геолокации Portsmouth (координаты приблизительные)
curl "http://127.0.0.1:8000/api/fsa/search?latitude=50.8435&longitude=-1.0365&max_distance=5.0"
```

### 2. Meadows House Residential and Nursing Home

```bash
# Полный запрос
curl -X GET "http://127.0.0.1:8000/api/fsa/search?name=Meadows%20House%20Residential%20and%20Nursing%20Home" \
  -H "Accept: application/json"

# Краткая версия
curl "http://127.0.0.1:8000/api/fsa/search?name=Meadows%20House%20Residential%20and%20Nursing%20Home"

# Поиск по частичному названию
curl "http://127.0.0.1:8000/api/fsa/search?name=Meadows%20House"

# Поиск по геолокации London (координаты Greenwich)
curl "http://127.0.0.1:8000/api/fsa/search?latitude=51.4769&longitude=-0.0205&max_distance=5.0"
```

### 3. Roborough House

```bash
# Полный запрос
curl -X GET "http://127.0.0.1:8000/api/fsa/search?name=Roborough%20House" \
  -H "Accept: application/json"

# Краткая версия
curl "http://127.0.0.1:8000/api/fsa/search?name=Roborough%20House"

# Поиск по геолокации Plymouth
curl "http://127.0.0.1:8000/api/fsa/search?latitude=50.3755&longitude=-4.1427&max_distance=5.0"
```

---

## Прямые запросы к FSA API (без нашего backend)

### 1. Kinross Residential Care Home

```bash
# Прямой запрос к FSA API
curl -X GET "http://api.ratings.food.gov.uk/Establishments?name=Kinross%20Residential%20Care%20Home" \
  -H "x-api-version: 2" \
  -H "Accept-Language: en-GB" \
  -H "Accept: application/json"

# Поиск по частичному названию
curl -X GET "http://api.ratings.food.gov.uk/Establishments?name=Kinross" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"

# Поиск care homes в Portsmouth (Local Authority ID: 197)
curl -X GET "http://api.ratings.food.gov.uk/Establishments?businessTypeId=7835&localAuthorityId=197&name=Kinross" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

### 2. Meadows House Residential and Nursing Home

```bash
# Прямой запрос к FSA API
curl -X GET "http://api.ratings.food.gov.uk/Establishments?name=Meadows%20House%20Residential%20and%20Nursing%20Home" \
  -H "x-api-version: 2" \
  -H "Accept-Language: en-GB" \
  -H "Accept: application/json"

# Поиск по частичному названию
curl -X GET "http://api.ratings.food.gov.uk/Establishments?name=Meadows%20House" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"

# Поиск care homes в Greenwich, London (Local Authority ID: 204)
curl -X GET "http://api.ratings.food.gov.uk/Establishments?businessTypeId=7835&localAuthorityId=204&name=Meadows" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

### 3. Roborough House

```bash
# Прямой запрос к FSA API
curl -X GET "http://api.ratings.food.gov.uk/Establishments?name=Roborough%20House" \
  -H "x-api-version: 2" \
  -H "Accept-Language: en-GB" \
  -H "Accept: application/json"

# Поиск care homes в Plymouth (Local Authority ID: 207)
curl -X GET "http://api.ratings.food.gov.uk/Establishments?businessTypeId=7835&localAuthorityId=207&name=Roborough" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

---

## Примеры для Python

### Через наш Backend

```python
import requests

# Kinross Residential Care Home
response = requests.get(
    "http://127.0.0.1:8000/api/fsa/search",
    params={"name": "Kinross Residential Care Home"}
)
print(response.json())

# Meadows House
response = requests.get(
    "http://127.0.0.1:8000/api/fsa/search",
    params={"name": "Meadows House Residential and Nursing Home"}
)
print(response.json())

# Roborough House
response = requests.get(
    "http://127.0.0.1:8000/api/fsa/search",
    params={"name": "Roborough House"}
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

# Kinross Residential Care Home
response = requests.get(
    "http://api.ratings.food.gov.uk/Establishments",
    params={"name": "Kinross Residential Care Home"},
    headers=headers
)
print(response.json())

# Meadows House
response = requests.get(
    "http://api.ratings.food.gov.uk/Establishments",
    params={"name": "Meadows House Residential and Nursing Home"},
    headers=headers
)
print(response.json())
```

---

## Быстрый тест (готовый к использованию)

```bash
# Самый простой тест - проверка работы API
curl "http://127.0.0.1:8000/api/fsa/search?name=Kinross" | python3 -m json.tool
```

---

## Примечания

1. **Важно**: Заголовок `x-api-version: 2` обязателен для прямых запросов к FSA API
2. **BusinessTypeId 7835** = "Hospitals/Childcare/Caring Premises" (care homes)
3. **Local Authority IDs**:
   - Portsmouth: 197
   - Greenwich (London): 204
   - Plymouth: 207
4. Если точное название не найдено, попробуйте частичный поиск (например, "Kinross" вместо "Kinross Residential Care Home")


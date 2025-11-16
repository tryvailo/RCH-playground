# 🧪 Руководство по тестированию FSA FHRS и Companies House API

## 📋 Содержание

1. [FSA FHRS API - Тестирование](#fsa-fhrs-api-тестирование)
2. [Companies House API - Тестирование](#companies-house-api-тестирование)
3. [Готовые примеры запросов](#готовые-примеры-запросов)
4. [Ожидаемые результаты](#ожидаемые-результаты)
5. [Troubleshooting](#troubleshooting)

---

## FSA FHRS API - Тестирование

### ✅ Преимущества
- **БЕЗ регистрации** и API ключей
- **БЕЗ лимитов** (рекомендуется ≤200 requests/hour)
- Полное покрытие UK
- Актуальные данные (обновляется ежедневно)

### 🔑 Обязательные параметры
```
Base URL: https://api.ratings.food.gov.uk
Заголовок: x-api-version: 2 (КРИТИЧНО!)
Формат: Accept: application/json
BusinessTypeId для care homes: 7835
```

### 🧪 Тестовые запросы

#### Тест 1: Manor House
```bash
curl -X GET "https://api.ratings.food.gov.uk/Establishments?name=Manor%20House&businessTypeId=7835&pageSize=10" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

**Что проверяем:**
- ✓ Возвращаются ли результаты поиска
- ✓ Есть ли FHRSID для каждого результата
- ✓ Присутствуют ли RatingValue и RatingDate
- ✓ Доступны ли scores (Hygiene, Structural, Management)

**Ожидаемый результат:**
```json
{
  "meta": {
    "totalCount": 45,
    "pageNumber": 1
  },
  "establishments": [
    {
      "FHRSID": 123456,
      "BusinessName": "Manor House Care Home",
      "RatingValue": "5",
      "RatingDate": "2024-10-23",
      "scores": {
        "Hygiene": 5,
        "Structural": 5,
        "ConfidenceInManagement": 5
      }
    }
  ]
}
```

#### Тест 2: Edgbaston Manor
```bash
curl -X GET "https://api.ratings.food.gov.uk/Establishments?name=Edgbaston%20Manor&businessTypeId=7835&pageSize=10" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

#### Тест 3: Care Home Birmingham
```bash
curl -X GET "https://api.ratings.food.gov.uk/Establishments?name=Care%20Home%20Birmingham&businessTypeId=7835&pageSize=10" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

#### Тест 4: Получение деталей по FHRSID
После получения FHRSID из предыдущих запросов:

```bash
curl -X GET "https://api.ratings.food.gov.uk/Establishments/ЗАМЕНИТЕ_НА_РЕАЛЬНЫЙ_FHRSID" \
  -H "x-api-version: 2" \
  -H "Accept: application/json"
```

**Что проверяем:**
- ✓ Детальная информация о заведении
- ✓ Полный адрес и телефон
- ✓ Детальные scores
- ✓ Геокоординаты
- ✓ Right to Reply (если есть)

---

## Companies House API - Тестирование

### ⚠️ Требования
- **ТРЕБУЕТСЯ регистрация** и API ключ
- Бесплатный доступ с лимитом: 600 requests/5 минут
- Только публичная информация о компаниях UK

### 📝 Получение API ключа

#### Шаг 1: Регистрация
1. Перейдите: https://developer.company-information.service.gov.uk/
2. Нажмите "Sign in / Register"
3. Создайте аккаунт (бесплатно, требуется email)

#### Шаг 2: Создание приложения
1. После входа нажмите "Add an application"
2. Заполните форму:
   - **Application name**: RightCareHome
   - **Description**: Care home analysis platform for RightCareHome product
   - **Environment**: Live (для production) или Sandbox (для тестов)
3. Нажмите "Create"

#### Шаг 3: Получение API ключа
1. Откройте созданное приложение
2. Скопируйте **API key** (выглядит как: `abc123xyz_456def789...`)
3. **ВАЖНО**: Сохраните ключ в безопасном месте (он показывается только один раз!)

### 🧪 Тестовые запросы

#### Тест 1: Manor House Care Limited
```bash
curl -u "ВАШ_API_КЛЮЧ:" \
  "https://api.company-information.service.gov.uk/search/companies?q=Manor%20House%20Care%20Limited&items_per_page=10"
```

**Что проверяем:**
- ✓ Работает ли API ключ
- ✓ Возвращаются ли результаты поиска
- ✓ Есть ли company_number для каждого результата
- ✓ Присутствует ли company_status и date_of_creation

**Ожидаемый результат:**
```json
{
  "total_results": 15,
  "items": [
    {
      "company_number": "12345678",
      "title": "MANOR HOUSE CARE LIMITED",
      "company_status": "active",
      "company_type": "ltd",
      "date_of_creation": "2015-06-15",
      "address_snippet": "Manor House, Birmingham, B15 2TT"
    }
  ]
}
```

#### Тест 2: Care Home + название города
```bash
curl -u "ВАШ_API_КЛЮЧ:" \
  "https://api.company-information.service.gov.uk/search/companies?q=Care%20Home%20Birmingham&items_per_page=10"
```

#### Тест 3: Получение деталей компании
После получения company_number из предыдущих запросов:

```bash
curl -u "ВАШ_API_КЛЮЧ:" \
  "https://api.company-information.service.gov.uk/company/ЗАМЕНИТЕ_НА_РЕАЛЬНЫЙ_COMPANY_NUMBER"
```

**Что проверяем:**
- ✓ Детальная информация о компании
- ✓ Registered office address
- ✓ Accounts information (last_accounts, next_due, overdue)
- ✓ Confirmation statement status
- ✓ SIC codes

**Ожидаемый результат:**
```json
{
  "company_number": "12345678",
  "company_name": "MANOR HOUSE CARE LIMITED",
  "company_status": "active",
  "type": "ltd",
  "date_of_creation": "2015-06-15",
  "accounts": {
    "last_accounts": {
      "made_up_to": "2024-06-30"
    },
    "next_due": "2025-03-31",
    "overdue": false
  },
  "confirmation_statement": {
    "last_made_up_to": "2024-06-15",
    "next_due": "2025-06-29"
  }
}
```

---

## Готовые примеры запросов

### Python (используя готовые скрипты)

#### FSA FHRS API
```python
# Запустите в терминале:
python3 fsa_api_test.py

# Или используйте в своём коде:
from rightcarehome_fsa_integration import FSARightCareHomeIntegration

fsa = FSARightCareHomeIntegration()

# Поиск по названию
results = fsa.find_care_home_by_name("Manor House")

# Поиск по координатам
results = fsa.find_care_homes_near_location(
    latitude=52.4862,
    longitude=-1.8904,
    radius_miles=5
)

# Получить детали
details = fsa.get_care_home_details(fhrsid=123456)
```

#### Companies House API
```python
# Создайте тестовый скрипт:
from companies_house_test import CompaniesHouseAPITester

api = CompaniesHouseAPITester(api_key="ВАШ_API_КЛЮЧ")

# Поиск компаний
results = api.test_search_companies("Manor House Care Limited")

# Получить детали
details = api.test_get_company_details("12345678")

# Рассчитать financial stability score
score = api.calculate_financial_stability_score(details)
print(f"Financial Stability Score: {score}/100")
```

### Postman

1. Импортируйте **FSA_FHRS_Postman_Collection.json**
2. Откройте коллекцию "FSA FHRS API Tests"
3. Запустите запросы по очереди
4. Для Companies House: создайте новую коллекцию и добавьте Authorization (Basic Auth с API ключом как username)

---

## Ожидаемые результаты

### FSA FHRS API - Критичные поля для RightCareHome

**Обязательные:**
- `FHRSID` (int) - уникальный идентификатор
- `BusinessName` (string) - название
- `RatingValue` (string) - "0" до "5" (или "Pass"/"Improvement Required" для Scotland)
- `RatingDate` (datetime) - дата последней инспекции

**Критичные для анализа:**
- `scores.Hygiene` (int, 0-20) - **чем ниже, тем лучше!**
- `scores.Structural` (int, 0-20) - **чем ниже, тем лучше!**
- `scores.ConfidenceInManagement` (int, 0-30) - **чем ниже, тем лучше!**

**Дополнительные:**
- `PostCode` (string) - почтовый индекс
- `geocode.latitude` / `longitude` (float) - координаты
- `RightToReply` (string) - ответ оператора
- `SchemeType` (string) - "FHRS" (England/Wales) или "FHIS" (Scotland)

### Companies House API - Критичные поля для Financial Stability Score

**Обязательные:**
- `company_number` (string) - уникальный номер
- `company_name` (string) - название
- `company_status` (string) - "active", "dissolved", "liquidation" и т.д.
- `date_of_creation` (date) - дата регистрации

**Критичные для расчёта score:**
- `accounts.overdue` (boolean) - просрочены ли accounts
- `accounts.last_accounts.made_up_to` (date) - дата последних accounts
- `confirmation_statement.next_due` (date) - следующий confirmation statement
- `type` (string) - тип компании ("ltd", "plc" и т.д.)

---

## Financial Stability Score Algorithm

```
РАСЧЁТ (0-100):

1. Статус компании (30 баллов):
   • active = 30
   • dissolved/liquidation = 0
   • другие = 15

2. Актуальность Accounts (25 баллов):
   • overdue = false: 25
   • overdue = true: 0

3. Confirmation Statement (15 баллов):
   • next_due существует и не просрочен: 15
   • иначе: 0

4. Возраст компании (20 баллов):
   • >= 5 лет: 20
   • >= 2 года: 15
   • >= 1 год: 10
   • < 1 года: 5

5. Тип компании (10 баллов):
   • ltd или plc: 10
   • другие: 5

ИНТЕРПРЕТАЦИЯ:
• 90-100: EXCELLENT - Финансово стабильна
• 70-89:  GOOD - Стабильна с minor issues
• 50-69:  FAIR - Требует внимания
• 30-49:  POOR - Серьёзные проблемы
• 0-29:   CRITICAL - Высокий риск
```

---

## Troubleshooting

### FSA FHRS API

**Проблема: "HTTP 400 Bad Request"**
- ✓ Проверьте заголовок `x-api-version: 2` (ОБЯЗАТЕЛЕН!)
- ✓ Проверьте URL encoding параметров (пробелы = `%20`)

**Проблема: Пустые результаты**
- ✓ Попробуйте более короткий запрос ("Manor" вместо "Manor House Care Home")
- ✓ Уберите фильтр businessTypeId и проверьте, есть ли вообще результаты
- ✓ Попробуйте поиск по postcode вместо названия

**Проблема: Нет scores в ответе**
- ✓ Используйте `/Establishments/{fhrsid}` вместо `/Establishments?name=...`
- ✓ Некоторые заведения могут не иметь scores (ожидают инспекции)

### Companies House API

**Проблема: "HTTP 401 Unauthorized"**
- ✓ Проверьте формат авторизации: `curl -u "API_KEY:"`
- ✓ Убедитесь, что API ключ скопирован полностью (без пробелов)
- ✓ Проверьте, что приложение в статусе "Live"

**Проблема: "HTTP 429 Too Many Requests"**
- ✓ Превышен лимит 600 requests/5 минут
- ✓ Подождите 5 минут
- ✓ Реализуйте rate limiting в коде

**Проблема: Пустые результаты**
- ✓ Попробуйте более короткий запрос
- ✓ Companies House содержит ТОЧНЫЕ названия (как зарегистрированы)
- ✓ Используйте company_number вместо названия, если знаете его

---

## 📝 Чек-лист успешного тестирования

### FSA FHRS API
- [ ] Запрос по названию "Manor House" вернул результаты
- [ ] Каждый результат содержит FHRSID
- [ ] RatingValue находится в диапазоне 0-5 (или Pass/Improvement Required)
- [ ] Детальный запрос по FHRSID вернул scores (Hygiene, Structural, Management)
- [ ] Геокоординаты присутствуют (latitude, longitude)

### Companies House API
- [ ] API ключ получен успешно
- [ ] Запрос по названию "Manor House Care Limited" вернул результаты
- [ ] Каждый результат содержит company_number
- [ ] company_status = "active" для активных компаний
- [ ] Детальный запрос по company_number вернул accounts и confirmation_statement
- [ ] Financial stability score рассчитывается корректно (0-100)

---

## 🎯 Следующие шаги после успешного тестирования

1. **FSA Integration:**
   - Используйте `rightcarehome_fsa_integration.py` как основу
   - Реализуйте кэширование (Redis) с TTL 7 дней
   - Добавьте rate limiting (max 100-200 requests/hour)
   - Интегрируйте в UI RightCareHome

2. **Companies House Integration:**
   - Создайте аналогичный класс для Companies House
   - Реализуйте financial stability score algorithm
   - Добавьте кэширование (данные меняются редко)
   - Комбинируйте с FSA + CQC данными

3. **Unified Scoring:**
   - CQC Rating (50%)
   - FSA Food Hygiene (30%)
   - Companies House Financial Stability (20%)
   - = **RightCareHome Trust Score (0-100)**

---

*Документ создан: November 2025*  
*Для: RightCareHome Platform Testing*  
*Версия: 1.0*

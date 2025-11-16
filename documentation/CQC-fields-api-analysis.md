# Полная структура данных CQC API 2024-2025 для Care Homes

## Критический апдейт: миграция API в 2024-2025

**CQC провела миграцию API-инфраструктуры** с введением обязательной аутентификации. Теперь требуется регистрация на новом портале разработчиков:
- **Старый URL:** `https://api.cqc.org.uk/public/v1/` (пока работает, но deprecated)
- **Новый URL:** `https://api.service.cqc.org.uk/` (требует authentication key)
- **Портал регистрации:** https://api-portal.service.cqc.org.uk/
- **Контакт для вопросов:** syndicationapi@cqc.org.uk

**Rate limiting:** До 2000 запросов/минуту с partnerCode; без него – жёсткий throttling (HTTP 429).

---

## 1. Полная структура JSON response от `/public/v1/locations/{locationId}`

### Top-level поля (40+ полей)

| Поле | Тип | Описание | Заполненность |
|------|------|----------|---------------|
| **locationId** | String | Уникальный ID локации (формат "1-XXXXXXXXX") | ✅ Всегда |
| **providerId** | String | ID родительской организации | ✅ Всегда |
| **organisationType** | String | Тип: "Location" | ✅ Всегда |
| **type** | String | Тип сервиса (напр., "Social Care Org") | ✅ Всегда |
| **name** | String | Название локации | ✅ Всегда |
| **alsoKnownAs** | String | Альтернативное название | ⚠️ Иногда |
| **brandId** | String | ID бренда (для NHS) | ⚠️ Редко |
| **brandName** | String | Название бренда | ⚠️ Редко |
| **website** | String | URL сайта | ⚠️ Часто null |
| **odsCode** | String | Organisation Data Service code | ⚠️ Для GP/NHS |
| **uprn** | String | Unique Property Reference Number | ✅ Обычно есть |

### Адресные поля

| Поле | Тип | Описание | Заполненность |
|------|------|----------|---------------|
| **postalAddressLine1** | String | Первая строка адреса | ✅ Всегда |
| **postalAddressLine2** | String | Вторая строка адреса | ⚠️ Опционально |
| **postalAddressTownCity** | String | Город | ✅ Всегда |
| **postalAddressCounty** | String | Графство | ⚠️ Опционально |
| **postalCode** | String | Почтовый индекс | ✅ Всегда |
| **mainPhoneNumber** | String | Основной телефон | ✅ Обычно есть |

### Географические/административные поля

| Поле | Тип | Описание | Заполненность |
|------|------|----------|---------------|
| **region** | String | Регион CQC (напр., "London", "North West") | ✅ Всегда |
| **constituency** | String | Парламентский округ | ✅ Всегда |
| **localAuthority** | String | Местная администрация | ✅ Всегда |
| **onspdLatitude** | Number | Широта (decimal degrees) | ✅ Обычно есть |
| **onspdLongitude** | Number | Долгота (decimal degrees) | ✅ Обычно есть |
| **onspdCcgCode** | String | ONS CCG код | ⚠️ Для healthcare |
| **onspdCcgName** | String | ONS CCG название | ⚠️ Для healthcare |
| **odsCcgCode** | String | ODS CCG код | ⚠️ Для healthcare |
| **odsCcgName** | String | ODS CCG название | ⚠️ Для healthcare |

### Care home специфичные поля

| Поле | Тип | Описание | Заполненность |
|------|------|----------|---------------|
| **careHome** | String | "Y" или "N" - флаг care home | ✅ Всегда |
| **numberOfBeds** | Integer | Количество мест | ✅ Для care homes |
| **inspectionDirectorate** | String | Директорат инспекции (напр., "Adult social care") | ✅ Всегда |

### Статусы и даты регистрации

| Поле | Тип | Описание | Заполненность |
|------|------|----------|---------------|
| **registrationStatus** | String | "Registered", "Deregistered" и т.д. | ✅ Всегда |
| **registrationDate** | String | Дата регистрации "YYYY-MM-DD" | ✅ Всегда |
| **deregistrationDate** | String | Дата дерегистрации (если применимо) | ⚠️ Если закрыт |

### Инспекции и отчеты

| Поле | Тип | Структура | Заполненность |
|------|------|-----------|---------------|
| **lastInspection** | Object | `{ "date": "YYYY-MM-DD" }` | ✅ Обычно есть |
| **lastReport** | Object | `{ "publicationDate": "YYYY-MM-DD" }` | ✅ Обычно есть |

---

### Полная структура currentRatings (критически важный объект)

```json
"currentRatings": {
  "reportDate": "2016-02-04",
  "overall": {
    "rating": "Good",  // Outstanding | Good | Requires improvement | Inadequate
    "reportDate": "2016-02-04",
    "reportLinkId": "79727ce9-7eee-4ac2-98df-05d110f02f39",
    "useOfResources": {},  // часто пустой объект
    "keyQuestionRatings": [
      {
        "name": "Safe",
        "rating": "Good",
        "reportDate": "2016-02-04",
        "reportLinkId": "79727ce9-7eee-4ac2-98df-05d110f02f39"
      },
      {
        "name": "Effective",
        "rating": "Good",
        "reportDate": "2016-02-04",
        "reportLinkId": "79727ce9-7eee-4ac2-98df-05d110f02f39"
      },
      {
        "name": "Caring",
        "rating": "Good",
        "reportDate": "2016-02-04",
        "reportLinkId": "79727ce9-7eee-4ac2-98df-05d110f02f39"
      },
      {
        "name": "Responsive",
        "rating": "Good",
        "reportDate": "2016-02-04",
        "reportLinkId": "79727ce9-7eee-4ac2-98df-05d110f02f39"
      },
      {
        "name": "Well-led",
        "rating": "Good",
        "reportDate": "2016-02-04",
        "reportLinkId": "79727ce9-7eee-4ac2-98df-05d110f02f39"
      }
    ]
  },
  "serviceRatings": [
    {
      "name": "old",  // inspection area ID
      "rating": "Good",
      "reportDate": "2016-02-04",
      "reportLinkId": "79727ce9-7eee-4ac2-98df-05d110f02f39"
    }
    // ... другие service ratings по population groups
  ]
}
```

**Важно:** Система рейтингов CQC:
- **Outstanding** (88-100%): Выдающееся качество
- **Good** (63-87%): Соответствует ожиданиям
- **Requires improvement** (39-62%): Не соответствует стандартам
- **Inadequate** (≤38%): Неприемлемое качество

**5 ключевых вопросов (KLOEs)** - все одинаково важны:
1. **Safe** - защита от вреда
2. **Effective** - evidence-based уход
3. **Caring** - сострадание и уважение
4. **Responsive** - индивидуальный подход
5. **Well-led** - лидерство и управление

---

### Структура historicRatings (массив предыдущих рейтингов)

```json
"historicRatings": [
  {
    "reportLinkId": "ebb60a35-1a38-4d39-81f0-f89699d365a8",
    "reportDate": "2014-09-17",
    "overall": {
      "rating": "No published rating",
      "keyQuestionRatings": [
        {
          "name": "Safe",
          "rating": "Do not include in report"
        }
        // ... другие key questions
      ]
    }
  }
]
```

---

### Структура reports (массив всех отчётов)

```json
"reports": [
  {
    "linkId": "79727ce9-7eee-4ac2-98df-05d110f02f39",
    "reportDate": "2016-02-04",
    "reportUri": "/reports/79727ce9-7eee-4ac2-98df-05d110f02f39",
    "firstVisitDate": "2015-11-05",
    "reportType": "Location",
    "relatedDocuments": [
      {
        "documentUri": "/documents/...",
        "documentType": "Use of Resources"
      }
    ]
  }
]
```

---

### Структура regulatedActivities (критически важна для специализаций)

```json
"regulatedActivities": [
  {
    "name": "Accommodation for persons who require nursing or personal care",
    "code": "RA1",
    "contacts": [
      {
        "personTitle": "Dr",
        "personGivenName": "John Michael",
        "personFamilyName": "Smith",
        "personRoles": ["Registered Manager"]
      }
    ]
  },
  {
    "name": "Treatment of disease, disorder or injury",
    "code": "RA5",
    "contacts": [...]
  }
]
```

**Важные коды для care homes:**
- **RA1** - Accommodation for persons who require nursing or personal care (основная для всех care homes)
- **RA5** - Treatment of disease, disorder or injury
- **RA8** - Diagnostic and screening procedures
- **RA11** - Maternity and midwifery services

---

### Структура specialisms (ключевая для подбора)

```json
"specialisms": [
  {
    "name": "Dementia"
  },
  {
    "name": "Learning disabilities"
  },
  {
    "name": "Mental health conditions"
  },
  {
    "name": "Older people"
  },
  {
    "name": "Physical disabilities"
  },
  {
    "name": "Sensory impairments"
  }
]
```

**Service User Bands (specialisms) для care homes:**
- Older people (65+)
- Dementia
- Learning disabilities
- Mental health conditions
- Physical disabilities
- Sensory impairments
- Substance misuse
- Eating disorders

---

### Структура gacServiceTypes

```json
"gacServiceTypes": [
  {
    "name": "Care home with nursing",
    "description": "Care home with nursing beds"
  }
]
```

---

### Структура locationTypes

```json
"locationTypes": [
  {
    "type": "Care home service with nursing"
  }
]
```

**Для care homes ожидаются:**
- "Care home service with nursing"
- "Care home service without nursing"

---

### Структура inspectionCategories

```json
"inspectionCategories": [
  {
    "code": "H1",
    "primary": "true",
    "name": "Community health services"
  }
]
```

---

### Структура inspectionAreas (population groups)

```json
"inspectionAreas": [
  {
    "inspectionAreaId": "old",
    "inspectionAreaName": "Older people",
    "status": "Active"
  },
  {
    "inspectionAreaId": "problems",
    "inspectionAreaName": "People experiencing poor mental health (including people with dementia)",
    "status": "Active"
  }
]
```

---

### Структура relationships (связи с другими организациями)

```json
"relationships": []  // часто пустой массив
```

---

## 2. Сравнение с вашим Python скриптом

### Ваш Priority 1 - ЧТО ИЗВЛЕКАЕТ СКРИПТ

```python
Priority 1: 
- organisation_type          ✅ Есть в API как "type"
- location_sector            ❓ Нет напрямую - вычисляется из type/inspectionDirectorate
- also_known_as              ✅ Есть в API как "alsoKnownAs"
- registration_status        ✅ Есть в API как "registrationStatus"
- registration_date          ✅ Есть в API как "registrationDate"
- deregistration_date        ✅ Есть в API как "deregistrationDate"
- registered_manager_absent_date  ❌ НЕТ в locations API (нужен provider API или contacts)
- last_inspection_date       ✅ Есть в API как "lastInspection.date"
```

### Ваш Priority 2 - ЧТО ИЗВЛЕКАЕТ СКРИПТ

```python
Priority 2:
- relationships              ✅ Есть в API как "relationships" (массив)
- location_types             ✅ Есть в API как "locationTypes" (массив)
- regulated_activities_enhanced  ✅ Есть в API как "regulatedActivities" с contacts
- service_ratings            ✅ Есть в API как "currentRatings.serviceRatings"
- key_question_ratings_with_dates  ✅ Есть в API как "currentRatings.overall.keyQuestionRatings"
```

### ✅ Ваш скрипт ИЗВЛЕКАЕТ эти поля - это ХОРОШАЯ БАЗА

---

## 3. MISSING критичные поля для RightCareHome

### 🔴 КРИТИЧЕСКИ ОТСУТСТВУЮЩИЕ (Priority 1)

Ваш скрипт НЕ извлекает эти критически важные поля:

| Поле | Зачем нужно | Как извлечь |
|------|-------------|-------------|
| **name** | Название care home (основное!) | `location['name']` |
| **postalCode** | Поиск по локации | `location['postalCode']` |
| **postalAddressLine1** | Полный адрес для карты | `location['postalAddressLine1']` |
| **postalAddressTownCity** | Город для фильтрации | `location['postalAddressTownCity']` |
| **region** | Региональная фильтрация | `location['region']` |
| **onspdLatitude** | Расчёт расстояния | `location['onspdLatitude']` |
| **onspdLongitude** | Построение карты | `location['onspdLongitude']` |
| **mainPhoneNumber** | Контактная информация | `location['mainPhoneNumber']` |
| **website** | Ссылка на сайт | `location.get('website')` |
| **numberOfBeds** | Вместимость (ключевая метрика) | `location['numberOfBeds']` |
| **careHome** | Фильтр care homes vs other services | `location['careHome']` |
| **currentRatings.overall.rating** | ГЛАВНЫЙ рейтинг | `location['currentRatings']['overall']['rating']` |
| **currentRatings.reportDate** | Актуальность рейтинга | `location['currentRatings']['reportDate']` |
| **currentRatings.overall.reportLinkId** | Ссылка на отчёт | `location['currentRatings']['overall']['reportLinkId']` |
| **specialisms** | Специализации (dementia, diabetes и т.д.) | `location['specialisms']` |
| **providerId** | Связь с провайдером (для группового анализа) | `location['providerId']` |

### ⚠️ ВАЖНЫЕ ОТСУТСТВУЮЩИЕ (Priority 2)

| Поле | Зачем нужно | Как извлечь |
|------|-------------|-------------|
| **inspectionDirectorate** | Тип инспектирующего органа | `location['inspectionDirectorate']` |
| **constituency** | Парламентский округ | `location['constituency']` |
| **localAuthority** | Для funding queries | `location['localAuthority']` |
| **lastReport.publicationDate** | Дата публикации отчёта | `location['lastReport']['publicationDate']` |
| **gacServiceTypes** | Государственная классификация услуг | `location['gacServiceTypes']` |
| **inspectionAreas** | Population groups для рейтингов | `location['inspectionAreas']` |
| **historicRatings** | Тренд качества (улучшение/ухудшение) | `location['historicRatings']` |
| **reports** | Все доступные отчёты | `location['reports']` |
| **uprn** | Unique Property Reference Number | `location.get('uprn')` |

### 📊 ДОПОЛНИТЕЛЬНЫЕ ДЛЯ АНАЛИТИКИ (Priority 3)

| Поле | Зачем нужно | Источник |
|------|-------------|----------|
| **Percentage scores** | Новая детальная оценка CQC (2024+) | API (если доступно) |
| **Manager name/status** | Стабильность управления | Contacts в regulatedActivities |
| **Provider name** | Название группы/организации | Provider API `/providers/{providerId}` |
| **Bed availability** | Текущие свободные места | ❌ НЕТ в CQC - нужен provider portal |
| **Pricing/fees** | Стоимость услуг | ❌ НЕТ в CQC - нужен provider portal |
| **User reviews** | Отзывы пользователей | ❌ НЕТ в CQC - нужна интеграция с carehome.co.uk |
| **Photos/videos** | Визуальный контент | ❌ НЕТ в CQC - нужен provider portal |

---

## 4. Примеры ACTUAL API responses

### Пример 1: List endpoint (paginated search)

**Request:** 
```
GET /locations?page=1&perPage=5&careHome=Y&region=North%20East&region=North%20West
```

**Response:**
```json
{
   "total": 4690,
   "page": 1,
   "perPage": 5,
   "totalPages": 938,
   "firstPageUri": "/locations?page=1&perPage=5&careHome=Y&region=North+West...",
   "nextPageUri": "/locations?page=2&perPage=5&careHome=Y&region=North+West...",
   "lastPageUri": "/locations?page=938&perPage=5&careHome=Y&region=North+West...",
   "locations": [
      {
         "locationId": "1-1000711804",
         "locationName": "Belmont Grange Nursing and Residential Home",
         "postalCode": "DH1 2QW"
      },
      {
         "locationId": "1-1004589685",
         "locationName": "The Spinney Nursing Home",
         "postalCode": "WN8 0PY"
      },
      {
         "locationId": "1-1034321453",
         "locationName": "Manchester House Nursing Home",
         "postalCode": "PR9 9LN"
      }
   ]
}
```

**⚠️ Важно:** List endpoint возвращает ТОЛЬКО `locationId`, `locationName`, `postalCode` - детальные данные требуют отдельных запросов для каждого locationId.

---

### Пример 2: Detailed location response (РЕАЛЬНЫЙ пример из CQC)

**Request:**
```
GET /locations/1-545611283
```

**Response:** (сокращённая версия с ключевыми полями для care home)

```json
{
  "locationId": "1-545611283",
  "providerId": "1-199747506",
  "organisationType": "Location",
  "type": "Primary Medical Services",
  "name": "Morden Hall Medical Centre",
  "registrationStatus": "Registered",
  "registrationDate": "2013-04-01",
  "numberOfBeds": 0,
  "careHome": "N",
  
  "postalAddressLine1": "256 Morden Road",
  "postalAddressTownCity": "London",
  "postalCode": "SW19 3DA",
  "region": "London",
  "localAuthority": "Merton",
  "constituency": "Wimbledon",
  
  "onspdLatitude": 51.404562,
  "onspdLongitude": -0.192098,
  "uprn": "48130060",
  
  "mainPhoneNumber": "02085400585",
  "inspectionDirectorate": "Primary medical services",
  
  "lastInspection": {
    "date": "2015-11-05"
  },
  "lastReport": {
    "publicationDate": "2016-02-04"
  },
  
  "locationTypes": [
    {"type": "GP Practice"}
  ],
  
  "regulatedActivities": [
    {
      "name": "Treatment of disease, disorder or injury",
      "code": "RA5",
      "contacts": [
        {
          "personTitle": "Dr",
          "personGivenName": "fn mn",
          "personFamilyName": "ln",
          "personRoles": ["Registered Manager"]
        }
      ]
    }
  ],
  
  "specialisms": [
    {"name": "Services for everyone"}
  ],
  
  "gacServiceTypes": [
    {
      "name": "Doctors/Gps",
      "description": "Doctors consultation service"
    }
  ],
  
  "inspectionAreas": [
    {
      "inspectionAreaId": "old",
      "inspectionAreaName": "Older people",
      "status": "Active"
    },
    {
      "inspectionAreaId": "problems",
      "inspectionAreaName": "People experiencing poor mental health (including people with dementia)",
      "status": "Active"
    }
  ],
  
  "currentRatings": {
    "overall": {
      "rating": "Good",
      "reportDate": "2016-02-04",
      "reportLinkId": "79727ce9-7eee-4ac2-98df-05d110f02f39",
      "useOfResources": {},
      "keyQuestionRatings": [
        {
          "name": "Safe",
          "rating": "Good",
          "reportDate": "2016-02-04",
          "reportLinkId": "79727ce9-7eee-4ac2-98df-05d110f02f39"
        },
        {
          "name": "Well-led",
          "rating": "Good",
          "reportDate": "2016-02-04",
          "reportLinkId": "79727ce9-7eee-4ac2-98df-05d110f02f39"
        },
        {
          "name": "Caring",
          "rating": "Good",
          "reportDate": "2016-02-04",
          "reportLinkId": "79727ce9-7eee-4ac2-98df-05d110f02f39"
        },
        {
          "name": "Responsive",
          "rating": "Good",
          "reportDate": "2016-02-04",
          "reportLinkId": "79727ce9-7eee-4ac2-98df-05d110f02f39"
        },
        {
          "name": "Effective",
          "rating": "Good",
          "reportDate": "2016-02-04",
          "reportLinkId": "79727ce9-7eee-4ac2-98df-05d110f02f39"
        }
      ]
    },
    "reportDate": "2016-02-04",
    "serviceRatings": [
      {
        "name": "conditions",
        "rating": "Good",
        "reportDate": "2016-02-04",
        "reportLinkId": "79727ce9-7eee-4ac2-98df-05d110f02f39"
      },
      {
        "name": "old",
        "rating": "Good",
        "reportDate": "2016-02-04",
        "reportLinkId": "79727ce9-7eee-4ac2-98df-05d110f02f39"
      }
    ]
  },
  
  "historicRatings": [
    {
      "reportLinkId": "ebb60a35-1a38-4d39-81f0-f89699d365a8",
      "reportDate": "2014-09-17",
      "overall": {
        "rating": "No published rating",
        "keyQuestionRatings": [
          {
            "name": "Safe",
            "rating": "Do not include in report"
          }
        ]
      }
    }
  ],
  
  "reports": [
    {
      "linkId": "79727ce9-7eee-4ac2-98df-05d110f02f39",
      "reportDate": "2016-02-04",
      "reportUri": "/reports/79727ce9-7eee-4ac2-98df-05d110f02f39",
      "firstVisitDate": "2015-11-05",
      "reportType": "Location"
    }
  ],
  
  "relationships": []
}
```

---

## 5. Best Practices для извлечения данных

### 🎯 Критические поля (НЕЛЬЗЯ запускать без них)

**Tier 1 - Blocking issues:**
1. `locationId` - уникальный идентификатор
2. `name` - название care home
3. `postalCode`, `postalAddressLine1`, `postalAddressTownCity` - адрес
4. `onspdLatitude`, `onspdLongitude` - координаты для карты
5. `currentRatings.overall.rating` - главный рейтинг CQC
6. `currentRatings.overall.keyQuestionRatings` - 5 key questions
7. `locationTypes` - тип сервиса (nursing vs residential)
8. `specialisms` - специализации (dementia, diabetes и т.д.)
9. `mainPhoneNumber` - контакты
10. `currentRatings.overall.reportLinkId` - ссылка на отчёт

**Tier 2 - Significant quality issues (стоит задержать запуск):**
11. `numberOfBeds` - вместимость
12. `lastInspection.date` - актуальность рейтинга
13. `registrationStatus` - активен/закрыт
14. `website` - дополнительная информация
15. `careHome` - флаг "Y"/"N" для фильтрации

---

### 📋 Рекомендации по обработке полей

#### 1. Handling NULL values

```python
# Безопасное извлечение опциональных полей
website = location.get('website', None)  # может быть null
postalAddressLine2 = location.get('postalAddressLine2', '')
numberOfBeds = location.get('numberOfBeds', 0)

# Nested fields с проверкой
last_inspection_date = None
if 'lastInspection' in location and location['lastInspection']:
    last_inspection_date = location['lastInspection'].get('date')

# Ratings могут отсутствовать для новых location
overall_rating = None
if 'currentRatings' in location and 'overall' in location['currentRatings']:
    overall_rating = location['currentRatings']['overall'].get('rating')
```

#### 2. Extracting key question ratings

```python
def extract_key_question_ratings(location):
    """Извлечение рейтингов по 5 ключевым вопросам"""
    ratings = {}
    
    if ('currentRatings' in location and 
        'overall' in location['currentRatings'] and
        'keyQuestionRatings' in location['currentRatings']['overall']):
        
        for kq in location['currentRatings']['overall']['keyQuestionRatings']:
            ratings[kq['name']] = {
                'rating': kq.get('rating'),
                'reportDate': kq.get('reportDate'),
                'reportLinkId': kq.get('reportLinkId')
            }
    
    return ratings

# Результат:
# {
#   'Safe': {'rating': 'Good', 'reportDate': '2016-02-04', ...},
#   'Effective': {'rating': 'Good', ...},
#   'Caring': {'rating': 'Good', ...},
#   'Responsive': {'rating': 'Good', ...},
#   'Well-led': {'rating': 'Good', ...}
# }
```

#### 3. Extracting specialisms

```python
def extract_specialisms(location):
    """Извлечение специализаций как список строк"""
    specialisms = []
    
    if 'specialisms' in location and location['specialisms']:
        specialisms = [s['name'] for s in location['specialisms']]
    
    return specialisms

# Результат: ['Dementia', 'Learning disabilities', 'Older people']
```

#### 4. Extracting regulated activities с контактами

```python
def extract_regulated_activities_enhanced(location):
    """Извлечение regulated activities с информацией о менеджере"""
    activities = []
    
    if 'regulatedActivities' in location:
        for activity in location['regulatedActivities']:
            activity_data = {
                'name': activity['name'],
                'code': activity['code'],
                'contacts': []
            }
            
            if 'contacts' in activity:
                for contact in activity['contacts']:
                    activity_data['contacts'].append({
                        'title': contact.get('personTitle'),
                        'givenName': contact.get('personGivenName'),
                        'familyName': contact.get('personFamilyName'),
                        'roles': contact.get('personRoles', [])
                    })
            
            activities.append(activity_data)
    
    return activities
```

#### 5. Checking for registered manager

```python
def has_registered_manager(location):
    """Проверка наличия зарегистрированного менеджера"""
    if 'regulatedActivities' not in location:
        return False
    
    for activity in location['regulatedActivities']:
        if 'contacts' in activity:
            for contact in activity['contacts']:
                if 'Registered Manager' in contact.get('personRoles', []):
                    return True
    
    return False

def get_registered_manager_info(location):
    """Получение информации о зарегистрированном менеджере"""
    for activity in location.get('regulatedActivities', []):
        for contact in activity.get('contacts', []):
            if 'Registered Manager' in contact.get('personRoles', []):
                return {
                    'title': contact.get('personTitle'),
                    'name': f"{contact.get('personGivenName', '')} {contact.get('personFamilyName', '')}".strip(),
                    'full_name': f"{contact.get('personTitle', '')} {contact.get('personGivenName', '')} {contact.get('personFamilyName', '')}".strip()
                }
    return None
```

#### 6. Calculating rating recency

```python
from datetime import datetime, timedelta

def get_rating_recency_flag(location):
    """Проверка актуальности рейтинга"""
    if 'currentRatings' not in location:
        return 'no_rating'
    
    report_date_str = location['currentRatings'].get('reportDate')
    if not report_date_str:
        return 'no_date'
    
    report_date = datetime.strptime(report_date_str, '%Y-%m-%d')
    days_old = (datetime.now() - report_date).days
    
    if days_old <= 365:
        return 'fresh'  # меньше года
    elif days_old <= 730:
        return 'recent'  # 1-2 года
    else:
        return 'outdated'  # больше 2 лет

def get_days_since_inspection(location):
    """Количество дней с последней инспекции"""
    if 'lastInspection' not in location or not location['lastInspection']:
        return None
    
    inspection_date_str = location['lastInspection'].get('date')
    if not inspection_date_str:
        return None
    
    inspection_date = datetime.strptime(inspection_date_str, '%Y-%m-%d')
    return (datetime.now() - inspection_date).days
```

#### 7. Building report URLs

```python
def get_report_url(report_link_id, base_url='https://api.cqc.org.uk/public/v1'):
    """Построение URL для получения отчёта"""
    return f"{base_url}/reports/{report_link_id}"

def get_all_report_urls(location, base_url='https://api.cqc.org.uk/public/v1'):
    """Получение всех URL отчётов"""
    urls = []
    
    if 'reports' in location:
        for report in location['reports']:
            urls.append({
                'linkId': report['linkId'],
                'reportDate': report.get('reportDate'),
                'url': f"{base_url}{report.get('reportUri', f'/reports/{report[\"linkId\"]}')}"
            })
    
    return urls
```

---

### 🔄 Стратегия обновления данных

#### 1. Initial full data pull

```python
import requests
import time

def fetch_all_care_homes(base_url='https://api.cqc.org.uk/public/v1', 
                         partner_code='YourCode'):
    """Полная выгрузка всех care homes"""
    all_locations = []
    page = 1
    
    while True:
        # Получить страницу списка
        list_response = requests.get(
            f"{base_url}/locations",
            params={
                'careHome': 'Y',
                'page': page,
                'perPage': 100,
                'partnerCode': partner_code
            }
        )
        
        data = list_response.json()
        location_ids = [loc['locationId'] for loc in data['locations']]
        
        # Получить детали для каждой локации
        for loc_id in location_ids:
            detail_response = requests.get(
                f"{base_url}/locations/{loc_id}",
                params={'partnerCode': partner_code}
            )
            all_locations.append(detail_response.json())
            time.sleep(0.03)  # rate limiting: 2000/min ≈ 33/sec
        
        if page >= data['totalPages']:
            break
        
        page += 1
        time.sleep(0.5)  # дополнительная пауза между страницами
    
    return all_locations
```

#### 2. Incremental updates using Changes API

```python
def fetch_changes_since(timestamp, base_url='https://api.cqc.org.uk/public/v1',
                       partner_code='YourCode'):
    """Получить изменения с определённой даты"""
    changes_response = requests.get(
        f"{base_url}/changes/location",
        params={
            'startTimestamp': timestamp,  # ISO 8601 format
            'partnerCode': partner_code
        }
    )
    
    changes = changes_response.json()
    
    # Обновить только изменённые локации
    updated_locations = []
    for change in changes.get('changes', []):
        loc_id = change['locationId']
        detail_response = requests.get(
            f"{base_url}/locations/{loc_id}",
            params={'partnerCode': partner_code}
        )
        updated_locations.append(detail_response.json())
    
    return updated_locations

# Использование:
# last_sync = '2024-11-14T00:00:00Z'
# updates = fetch_changes_since(last_sync)
```

#### 3. Recommended refresh schedule

```python
# Ежедневное обновление (CQC обновляет данные раз в день)
REFRESH_SCHEDULE = {
    'full_sync': 'weekly',     # Полная синхронизация раз в неделю
    'incremental': 'daily',     # Инкрементальные обновления каждый день
    'critical_fields': 'realtime'  # Для availability/pricing через provider portal
}
```

---

### ⚠️ Handling API migration

```python
# Поддержка обоих API endpoints
def get_cqc_client(use_new_api=False):
    """Фабрика для CQC API client"""
    if use_new_api:
        return CQCClientV2(
            base_url='https://api.service.cqc.org.uk',
            subscription_key='YOUR_KEY_FROM_PORTAL'
        )
    else:
        return CQCClientV1(
            base_url='https://api.cqc.org.uk/public/v1',
            partner_code='YOUR_PARTNER_CODE'
        )

# Graceful fallback
def fetch_location_with_fallback(location_id):
    """Попытка с новым API, fallback на старый"""
    try:
        client_v2 = get_cqc_client(use_new_api=True)
        return client_v2.get_location(location_id)
    except Exception as e:
        print(f"V2 API failed: {e}, trying V1")
        client_v1 = get_cqc_client(use_new_api=False)
        return client_v1.get_location(location_id)
```

---

### 🎨 Validation и data quality checks

```python
def validate_care_home_data(location):
    """Валидация критически важных полей"""
    errors = []
    warnings = []
    
    # Критичные поля
    required_fields = [
        'locationId', 'name', 'postalCode', 
        'onspdLatitude', 'onspdLongitude'
    ]
    
    for field in required_fields:
        if field not in location or not location[field]:
            errors.append(f"Missing required field: {field}")
    
    # Проверка careHome флага
    if location.get('careHome') != 'Y':
        warnings.append("careHome flag is not 'Y'")
    
    # Проверка наличия рейтинга
    if 'currentRatings' not in location:
        warnings.append("No current ratings available")
    
    # Проверка актуальности рейтинга
    recency = get_rating_recency_flag(location)
    if recency == 'outdated':
        warnings.append("Rating is more than 2 years old")
    
    # Проверка numberOfBeds
    beds = location.get('numberOfBeds', 0)
    if beds == 0:
        warnings.append("numberOfBeds is 0 or missing")
    
    # Проверка specialisms
    if 'specialisms' not in location or not location['specialisms']:
        warnings.append("No specialisms defined")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }
```

---

### 📊 Mapping rating values

```python
# Маппинг рейтингов для удобства
RATING_MAPPING = {
    'Outstanding': {
        'numeric': 4,
        'percentage_range': (88, 100),
        'color': '#00a33b',  # зелёный
        'description': 'Выдающееся качество услуг'
    },
    'Good': {
        'numeric': 3,
        'percentage_range': (63, 87),
        'color': '#3db5e6',  # голубой
        'description': 'Соответствует ожиданиям'
    },
    'Requires improvement': {
        'numeric': 2,
        'percentage_range': (39, 62),
        'color': '#f9a825',  # оранжевый
        'description': 'Не соответствует стандартам'
    },
    'Inadequate': {
        'numeric': 1,
        'percentage_range': (0, 38),
        'color': '#d32f2f',  # красный
        'description': 'Неприемлемое качество'
    }
}

def get_rating_info(rating_string):
    """Получение расширенной информации о рейтинге"""
    return RATING_MAPPING.get(rating_string, {
        'numeric': 0,
        'color': '#999999',
        'description': 'Нет данных'
    })
```

---

## 6. Итоговая таблица критичности полей

### Сводная таблица: Что ОБЯЗАТЕЛЬНО добавить в скрипт

| Критичность | Поле | Есть в скрипте? | Путь в JSON | Use Case |
|-------------|------|-----------------|-------------|----------|
| 🔴 CRITICAL | name | ❌ НЕТ | `['name']` | Отображение названия |
| 🔴 CRITICAL | postalCode | ❌ НЕТ | `['postalCode']` | Поиск по локации |
| 🔴 CRITICAL | postalAddressLine1 | ❌ НЕТ | `['postalAddressLine1']` | Полный адрес |
| 🔴 CRITICAL | postalAddressTownCity | ❌ НЕТ | `['postalAddressTownCity']` | Город |
| 🔴 CRITICAL | region | ❌ НЕТ | `['region']` | Региональный фильтр |
| 🔴 CRITICAL | onspdLatitude | ❌ НЕТ | `['onspdLatitude']` | Карта/расстояние |
| 🔴 CRITICAL | onspdLongitude | ❌ НЕТ | `['onspdLongitude']` | Карта/расстояние |
| 🔴 CRITICAL | mainPhoneNumber | ❌ НЕТ | `['mainPhoneNumber']` | Контакты |
| 🔴 CRITICAL | numberOfBeds | ❌ НЕТ | `['numberOfBeds']` | Вместимость |
| 🔴 CRITICAL | careHome | ❌ НЕТ | `['careHome']` | Фильтр care homes |
| 🔴 CRITICAL | currentRatings.overall.rating | ⚠️ Частично | `['currentRatings']['overall']['rating']` | Главный рейтинг |
| 🔴 CRITICAL | currentRatings.reportDate | ❌ НЕТ | `['currentRatings']['reportDate']` | Актуальность |
| 🔴 CRITICAL | currentRatings.overall.reportLinkId | ❌ НЕТ | `['currentRatings']['overall']['reportLinkId']` | Ссылка на отчёт |
| 🔴 CRITICAL | specialisms | ❌ НЕТ | `['specialisms']` | Специализации |
| 🔴 CRITICAL | providerId | ❌ НЕТ | `['providerId']` | Связь с провайдером |
| 🟡 IMPORTANT | website | ❌ НЕТ | `['website']` | Доп. информация |
| 🟡 IMPORTANT | inspectionDirectorate | ❌ НЕТ | `['inspectionDirectorate']` | Тип инспекции |
| 🟡 IMPORTANT | localAuthority | ❌ НЕТ | `['localAuthority']` | Funding queries |
| 🟡 IMPORTANT | constituency | ❌ НЕТ | `['constituency']` | Административное деление |
| 🟡 IMPORTANT | lastReport.publicationDate | ❌ НЕТ | `['lastReport']['publicationDate']` | Дата публикации отчёта |
| 🟡 IMPORTANT | gacServiceTypes | ❌ НЕТ | `['gacServiceTypes']` | Классификация услуг |
| 🟡 IMPORTANT | inspectionAreas | ❌ НЕТ | `['inspectionAreas']` | Population groups |
| 🟡 IMPORTANT | historicRatings | ❌ НЕТ | `['historicRatings']` | Тренд качества |
| 🟡 IMPORTANT | reports | ❌ НЕТ | `['reports']` | Все отчёты |
| ✅ ЕСТЬ | organisation_type | ✅ ДА | `['type']` | Тип организации |
| ✅ ЕСТЬ | registration_status | ✅ ДА | `['registrationStatus']` | Статус регистрации |
| ✅ ЕСТЬ | registration_date | ✅ ДА | `['registrationDate']` | Дата регистрации |
| ✅ ЕСТЬ | deregistration_date | ✅ ДА | `['deregistrationDate']` | Дата закрытия |
| ✅ ЕСТЬ | also_known_as | ✅ ДА | `['alsoKnownAs']` | Альтернативное название |
| ✅ ЕСТЬ | last_inspection_date | ✅ ДА | `['lastInspection']['date']` | Дата инспекции |
| ✅ ЕСТЬ | relationships | ✅ ДА | `['relationships']` | Связи |
| ✅ ЕСТЬ | location_types | ✅ ДА | `['locationTypes']` | Типы локации |
| ✅ ЕСТЬ | regulated_activities | ✅ ДА | `['regulatedActivities']` | Regulated activities |
| ✅ ЕСТЬ | service_ratings | ✅ ДА | `['currentRatings']['serviceRatings']` | Service ratings |
| ✅ ЕСТЬ | key_question_ratings | ✅ ДА | `['currentRatings']['overall']['keyQuestionRatings']` | 5 key questions |

---

## 7. Рекомендуемая структура базы данных

### Основная таблица: care_homes

```sql
CREATE TABLE care_homes (
    -- Identifiers
    location_id VARCHAR(50) PRIMARY KEY,
    provider_id VARCHAR(50),
    
    -- Basic Info
    name VARCHAR(500) NOT NULL,
    also_known_as VARCHAR(500),
    care_home_flag CHAR(1) DEFAULT 'Y',
    organisation_type VARCHAR(100),
    
    -- Address
    postal_address_line1 VARCHAR(500),
    postal_address_line2 VARCHAR(500),
    town_city VARCHAR(200),
    county VARCHAR(200),
    postcode VARCHAR(20) NOT NULL,
    
    -- Geographic
    region VARCHAR(100),
    constituency VARCHAR(200),
    local_authority VARCHAR(200),
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    uprn VARCHAR(50),
    
    -- Contact
    main_phone_number VARCHAR(50),
    website VARCHAR(500),
    
    -- Operational
    number_of_beds INTEGER,
    inspection_directorate VARCHAR(200),
    
    -- Registration
    registration_status VARCHAR(50),
    registration_date DATE,
    deregistration_date DATE,
    
    -- Inspection
    last_inspection_date DATE,
    last_report_publication_date DATE,
    
    -- Current Rating
    overall_rating VARCHAR(50),
    overall_rating_report_date DATE,
    overall_rating_report_link_id VARCHAR(100),
    
    -- Key Question Ratings
    rating_safe VARCHAR(50),
    rating_effective VARCHAR(50),
    rating_caring VARCHAR(50),
    rating_responsive VARCHAR(50),
    rating_well_led VARCHAR(50),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_sync_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_postcode ON care_homes(postcode);
CREATE INDEX idx_region ON care_homes(region);
CREATE INDEX idx_overall_rating ON care_homes(overall_rating);
CREATE INDEX idx_location ON care_homes(latitude, longitude);
CREATE INDEX idx_registration_status ON care_homes(registration_status);
```

### Связанные таблицы

```sql
-- Specialisms (Many-to-Many)
CREATE TABLE care_home_specialisms (
    id SERIAL PRIMARY KEY,
    location_id VARCHAR(50) REFERENCES care_homes(location_id),
    specialism_name VARCHAR(200),
    UNIQUE(location_id, specialism_name)
);

CREATE INDEX idx_specialism_name ON care_home_specialisms(specialism_name);

-- Regulated Activities
CREATE TABLE care_home_regulated_activities (
    id SERIAL PRIMARY KEY,
    location_id VARCHAR(50) REFERENCES care_homes(location_id),
    activity_name VARCHAR(500),
    activity_code VARCHAR(20),
    registered_manager_name VARCHAR(200),
    UNIQUE(location_id, activity_code)
);

-- Location Types
CREATE TABLE care_home_location_types (
    id SERIAL PRIMARY KEY,
    location_id VARCHAR(50) REFERENCES care_homes(location_id),
    location_type VARCHAR(200),
    UNIQUE(location_id, location_type)
);

-- Service Ratings (для population groups)
CREATE TABLE care_home_service_ratings (
    id SERIAL PRIMARY KEY,
    location_id VARCHAR(50) REFERENCES care_homes(location_id),
    service_name VARCHAR(200),
    rating VARCHAR(50),
    report_date DATE,
    report_link_id VARCHAR(100),
    UNIQUE(location_id, service_name)
);

-- Historic Ratings
CREATE TABLE care_home_historic_ratings (
    id SERIAL PRIMARY KEY,
    location_id VARCHAR(50) REFERENCES care_homes(location_id),
    report_date DATE,
    report_link_id VARCHAR(100),
    overall_rating VARCHAR(50),
    rating_safe VARCHAR(50),
    rating_effective VARCHAR(50),
    rating_caring VARCHAR(50),
    rating_responsive VARCHAR(50),
    rating_well_led VARCHAR(50)
);

CREATE INDEX idx_historic_report_date ON care_home_historic_ratings(location_id, report_date DESC);

-- Inspection Reports
CREATE TABLE care_home_reports (
    id SERIAL PRIMARY KEY,
    location_id VARCHAR(50) REFERENCES care_homes(location_id),
    report_link_id VARCHAR(100) UNIQUE,
    report_date DATE,
    report_uri VARCHAR(500),
    first_visit_date DATE,
    report_type VARCHAR(50)
);
```

---

## 8. Финальные рекомендации

### ✅ Немедленные действия (Priority 1)

1. **Добавить в Python скрипт извлечение этих полей:**
   ```python
   critical_fields = [
       'name', 'postalCode', 'postalAddressLine1', 'postalAddressTownCity',
       'region', 'onspdLatitude', 'onspdLongitude', 'mainPhoneNumber',
       'numberOfBeds', 'careHome', 'providerId', 'website',
       'currentRatings.overall.rating', 'currentRatings.reportDate',
       'currentRatings.overall.reportLinkId', 'specialisms'
   ]
   ```

2. **Зарегистрироваться на новом API портале:**
   - Перейти на https://api-portal.service.cqc.org.uk/
   - Получить subscription key
   - Подготовиться к миграции с legacy API

3. **Реализовать валидацию данных:**
   - Проверять наличие критичных полей
   - Флагировать outdated ratings (>2 years)
   - Проверять наличие registered manager

### 🔄 Краткосрочные улучшения (Priority 2)

4. **Добавить извлечение исторических данных:**
   - `historicRatings` для trend analysis
   - `reports` для всех доступных отчётов
   - `inspectionAreas` для детального профиля

5. **Реализовать incremental updates:**
   - Использовать Changes API для ежедневных обновлений
   - Хранить timestamp последней синхронизации
   - Обновлять только изменённые записи

6. **Расширить контактную информацию:**
   - Извлекать manager details из `regulatedActivities.contacts`
   - Добавлять `inspectionDirectorate`, `localAuthority`

### 🎯 Среднесрочные задачи (Priority 3)

7. **Дополнить данные из других источников:**
   - Создать provider portal для самообслуживания
   - Интегрировать с carehome.co.uk API для reviews
   - Добавить pricing data (вручную или через provider portal)

8. **Реализовать вычисляемые метрики:**
   - Days since last inspection
   - Rating recency flag
   - Quality trend (improving/declining)
   - Distance from user location (runtime calculation)

9. **Добавить visual content:**
   - Фото через provider upload
   - Virtual tours links
   - Staff profiles

### 📈 Долгосрочная стратегия

10. **Построить differentiation layer:**
    - Персонализированные рекомендации на основе AI
    - Real-time availability tracking через provider engagement
    - Advanced comparison tools
    - Integration с local authority funding systems

11. **Мониторинг качества данных:**
    - Dashboard для data completeness rate
    - Алерты на outdated ratings
    - Tracking provider engagement (profile updates)

---

## Заключение

**Ваш текущий Python скрипт извлекает хорошую базовую информацию (Priority 1 и Priority 2), но КРИТИЧЕСКИ не хватает:**

🔴 **Для базового функционала (нельзя запустить без этого):**
- Название care home (`name`)
- Полный адрес и координаты (`postalCode`, `onspdLatitude/Longitude`)
- Контакты (`mainPhoneNumber`, `website`)
- Вместимость (`numberOfBeds`)
- Специализации (`specialisms`)
- Полная структура рейтингов (`currentRatings` полностью)

🟡 **Для качественного продукта (добавить в ближайшее время):**
- Исторические рейтинги (`historicRatings`)
- Все отчёты (`reports`)
- Детали провайдера
- Административные поля

⚪ **Для конкурентоспособности (стратегический уровень):**
- Availability (из provider portal)
- Pricing (из provider portal или manual)
- Reviews (external integration)
- Photos/videos (provider-supplied)

**Главный вывод:** CQC API предоставляет отличную foundation, но **gap между "функциональным" и "best-in-class" требует дополнительных источников данных**, особенно для availability, pricing, reviews и визуального контента. Фазированный подход позволит быстро запустить MVP, систематически наращивая конкурентные преимущества.
# Как Получить API Доступы: Пошаговая Инструкция
**Для физических лиц и стартапов**

---

## 📋 Обзор - Что Нужно Получить

| API | Физлицо? | Требует Payment? | Сложность | Время |
|-----|----------|------------------|-----------|-------|
| **CQC API** | ✅ Да | ❌ Нет | 🟢 Легко | 5 мин |
| **FSA FHRS** | ✅ Да | ❌ Нет | 🟢 Легко | 0 мин |
| **Companies House** | ✅ Да | ❌ Нет | 🟢 Легко | 10 мин |
| **Google Places** | ✅ Да | ⚠️ Да* | 🟡 Средне | 20 мин |
| **Places Insights** | ⚠️ Сложнее | ⚠️ Да* | 🔴 Сложно | 1-3 дня |
| **Perplexity** | ✅ Да | ✅ Да | 🟢 Легко | 5 мин |
| **Autumna Proxies** | ✅ Да | ✅ Да | 🟡 Средне | 15 мин |

*Есть free tier или trial период

---

## 🏛️ 1. CQC API (Care Quality Commission)

### ✅ Доступно для физлиц: ДА
### 💰 Стоимость: БЕСПЛАТНО
### ⏱️ Время: 5-10 минут

### Шаги:

#### Вариант 1: Простой (Без Partner Code)
```
Статус: Можно использовать сразу!
Ограничение: Rate limiting (меньше запросов/мин)
URL: https://api.cqc.org.uk/public/v1

Пример запроса:
curl "https://api.cqc.org.uk/public/v1/locations?perPage=10&careHome=true"
```

**Плюсы**: Работает сразу, без регистрации  
**Минусы**: Возможен throttling при высокой нагрузке

#### Вариант 2: С Partner Code (Рекомендуется)
```
1. Перейти: https://api-portal.service.cqc.org.uk/
2. Нажать "Sign Up" в правом верхнем углу
3. Заполнить форму:
   - Organisation name: "Your Name / Startup Name"
   - Email: ваш email
   - Describe usage: "Building care home comparison platform"
   
4. После регистрации:
   - Login → My Applications → Create Application
   - Application Name: "RightCareHome Testing"
   - Description: "Care home data integration testing"
   
5. Получите Partner Code (будет показан на экране)

6. Использование:
   https://api.cqc.org.uk/public/v1/locations?perPage=100&partnerCode=YOUR_CODE
```

**Преимущества Partner Code:**
- 2000 requests/min (вместо ~100)
- Priority support
- Уведомления об изменениях в API

### ⚠️ Важно:
- CQC может попросить подтвердить email
- Partner Code выдается обычно в течение 1-2 дней (иногда сразу)
- Если статус "pending", можно использовать API без кода пока

### 📧 Если Проблемы:
Email: syndicationapi@cqc.org.uk  
Тема: "Partner Code Request for Care Home Platform"

---

## 🍽️ 2. FSA FHRS API (Food Hygiene)

### ✅ Доступно для физлиц: ДА
### 💰 Стоимость: БЕСПЛАТНО
### ⏱️ Время: 0 минут (без регистрации!)

### Шаги:

```bash
# Просто используйте! Никакой регистрации не нужна.

# Пример запроса:
curl -X GET "http://api.ratings.food.gov.uk/Establishments?name=Manor+House" \
  -H "x-api-version: 2" \
  -H "Accept-Language: en-GB"
```

### Требования:
- **ОБЯЗАТЕЛЬНО**: Header `x-api-version: 2`
- Опционально: `Accept-Language: en-GB` (или cy-GB для Welsh)

### Rate Limits:
- ~1 request/second рекомендуется
- При превышении возможен HTTP 403 (throttling)
- Решение: добавьте `time.sleep(2)` между запросами

### Документация:
https://api.ratings.food.gov.uk/help

### ⚠️ Важно:
- API работает сразу из коробки
- Нет API keys, нет регистрации
- Данные публичные (Open Government License)

### Альтернатива (если нужен bulk download):
- Скачать полный датасет XML: https://ratings.food.gov.uk/open-data/en-GB
- ~500MB файл со всеми establishments в UK

---

## 🏢 3. Companies House API

### ✅ Доступно для физлиц: ДА
### 💰 Стоимость: БЕСПЛАТНО
### ⏱️ Время: 10 минут

### Шаги:

#### 1. Создать аккаунт
```
URL: https://developer.company-information.service.gov.uk/

1. Нажать "Sign in / Register"
2. Если нет аккаунта Government Gateway:
   - Нажать "Create sign in details"
   - Email + password
   - Подтвердить email
   
3. После входа:
   - Автоматически попадете в Developer Hub
```

#### 2. Создать Application
```
1. Dashboard → "Your applications"
2. Нажать "Create an application"
3. Заполнить:
   - Application name: "RightCareHome Testing"
   - Description: "Care home financial data research"
   - Application URL: http://localhost (если нет сайта)
   
4. Нажать "Create"
```

#### 3. Сгенерировать API Key
```
1. В списке applications нажать на название
2. Секция "API keys"
3. Нажать "Create new key"
4. Key name: "Testing Key"
5. Нажать "Create"

⚠️ ВАЖНО: Скопируйте ключ сразу! Показывается только один раз.
```

#### 4. Тестирование
```bash
# Замените YOUR_API_KEY на ваш ключ
curl -u YOUR_API_KEY: \
  "https://api.company-information.service.gov.uk/company/06790962"

# Обратите внимание на формат auth: "api_key:" (двоеточие в конце!)
```

### 📝 Пример для Python:
```python
import requests
from requests.auth import HTTPBasicAuth

api_key = "your_api_key_here"
company_number = "06790962"

url = f"https://api.company-information.service.gov.uk/company/{company_number}"
response = requests.get(url, auth=HTTPBasicAuth(api_key, ''))

print(response.json())
```

### Rate Limits:
- Официально не указаны
- Рекомендуется: <600 requests/min
- Обычно достаточно для тестирования и небольших проектов

### ⚠️ Важно:
- API key бесплатный, unlimited keys
- Можно создать несколько приложений
- Данные публичные (Open Government License)

### 📧 Support:
Email: enquiries@companieshouse.gov.uk

---

## 🗺️ 4. Google Places API & Places Insights

### ✅ Доступно для физлиц: ДА
### 💰 Стоимость: $200 FREE credits/месяц, затем pay-as-you-go
### ⏱️ Время: 20-30 минут

### Часть A: Google Places API (Базовый)

#### 1. Создать Google Cloud Project
```
URL: https://console.cloud.google.com/

1. Войти с Google аккаунтом (личный email подойдет)
2. Согласиться с Terms of Service
3. Нажать "Select a project" → "NEW PROJECT"
4. Project name: "RightCareHome Testing"
5. Organization: оставить "No organization" (для физлица)
6. Нажать "CREATE"
```

#### 2. Enable Billing
```
⚠️ ТРЕБУЕТСЯ КРЕДИТНАЯ КАРТА (но не списывается сразу)

1. Navigation Menu (☰) → Billing
2. Нажать "Link a billing account"
3. Если нет billing account:
   - "CREATE ACCOUNT"
   - Country: United Kingdom
   - Account type: Individual (для физлица)
   - Card details
   - Налоговая информация (если требуется)
   
4. ВАЖНО: Установите budget alert!
   - Billing → Budget & alerts
   - Create Budget
   - Set amount: £50/month
   - Alert thresholds: 50%, 90%, 100%
   - Email notifications: ваш email

💡 FREE TIER: $200 бесплатных credits каждый месяц покрывают:
   - ~6,000 Place Details requests
   - или ~12,000 Place Search requests
   - Достаточно для тестирования!
```

#### 3. Enable Places API
```
1. Navigation Menu → APIs & Services → Library
2. Search: "Places API"
3. Выбрать "Places API (New)" (рекомендуется) или "Places API"
4. Нажать "ENABLE"
5. Подождать 1-2 минуты
```

#### 4. Create API Key
```
1. APIs & Services → Credentials
2. "+ CREATE CREDENTIALS" → API key
3. API key создан! (копируем)

⚠️ ОБЯЗАТЕЛЬНО: Restrict API key!
4. Нажать "Edit API key" (иконка карандаша)
5. API restrictions:
   - Выбрать "Restrict key"
   - Отметить: "Places API"
6. Application restrictions (опционально):
   - IP addresses (если известен ваш IP)
   - или HTTP referrers (если для веб-сайта)
7. Нажать "SAVE"
```

#### 5. Тестирование
```bash
# Замените YOUR_API_KEY
curl "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=Manor%20House%20Care%20Brighton&inputtype=textquery&fields=place_id,name&key=YOUR_API_KEY"

# Если работает - увидите JSON с place_id
```

### Часть B: Google Places Insights (BigQuery) 🔴

#### ⚠️ ВАЖНО: Сложнее для физлиц!

**Требования:**
1. Google Cloud Project (уже создали выше)
2. Billing enabled (уже сделали)
3. **Request Access** к Places Insights (может занять 1-3 дня)

#### Шаги:

##### 1. Request Access к Places Insights
```
URL: https://developers.google.com/maps/documentation/placesinsights/cloud-setup

1. Заполнить форму "Sign up for Places Insights"
2. Google Form спросит:
   - Company/Organization: можно написать "Individual Developer" или название стартапа
   - Use case: "Building care home intelligence platform"
   - Expected query volume: "Low (testing phase, <1000 queries/month)"
   - Email: ваш email от Google Cloud
   
3. Submit и ждать approval (обычно 1-3 рабочих дня)
```

##### 2. Enable Required APIs (пока ждете approval)
```
1. Google Cloud Console → APIs & Services → Library
2. Enable следующие APIs:
   - BigQuery API ✅
   - Analytics Hub API ✅
```

##### 3. Setup IAM Roles
```
1. IAM & Admin → IAM
2. Найти ваш email (principal)
3. Нажать Edit (pencil icon)
4. Add roles:
   - BigQuery User
   - Analytics Hub Subscription Owner
5. SAVE
```

##### 4. После Approval: Subscribe to Dataset
```
1. Google Cloud Console → Analytics Hub → Search Listings
2. Search: "Places Insights - United Kingdom"
3. Нажать на listing
4. "SUBSCRIBE"
5. Dataset будет создан в вашем проекте:
   - Project: your-project-id
   - Dataset: places_insights___uk
```

##### 5. Тестирование
```sql
-- В BigQuery Console → SQL Workspace
SELECT WITH AGGREGATION_THRESHOLD
  COUNT(*) as care_home_count
FROM `your-project-id.places_insights___uk.places`
WHERE primary_type IN ('nursing_home', 'senior_care')
  AND business_status = 'OPERATIONAL'
LIMIT 10
```

### 💰 Costs для Places Insights:

**During Preview (сейчас):**
- Places Insights data: БЕСПЛАТНО
- BigQuery compute: ~£10-20/месяц для умеренного использования
- Storage: минимальная

**After GA (General Availability):**
- Ожидается ~£200-300/месяц (пока неизвестно точно)

### ⚠️ Альтернатива для Физлиц:

Если Google не одобрит Places Insights (бывает редко):
1. Используйте только базовый Places API (reviews, ratings)
2. Footfall data можно аппроксимировать через:
   - Review velocity (новые отзывы/неделя)
   - Popular times (доступно в Places API)
3. Predictive models строить на основе других источников

### 📧 Support:
- General: https://developers.google.com/maps/support
- Places Insights: places-insights-support@google.com

---

## 🔍 5. Perplexity API

### ✅ Доступно для физлиц: ДА
### 💰 Стоимость: $10 минимум (pay-as-you-go)
### ⏱️ Время: 5 минут

### Шаги:

#### 1. Создать аккаунт
```
URL: https://www.perplexity.ai/

1. Sign up с email или Google account
2. Подтвердить email
```

#### 2. Add Credits
```
1. Settings → API
   или прямая ссылка: https://www.perplexity.ai/settings/api
   
2. Секция "Billing"
3. "Add credits"
4. Минимум: $10 (хватит на ~2000 requests с sonar-pro)
5. Ввести card details
6. Purchase credits

💡 TIP: Начните с $10, всегда можно добавить
```

#### 3. Generate API Key
```
1. В той же странице (Settings → API)
2. Секция "API Keys"
3. "Create New API Key"
4. Name: "RightCareHome Testing"
5. Нажать "Create"
6. СКОПИРУЙТЕ ключ сразу!
```

#### 4. Тестирование
```bash
curl -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sonar-pro",
    "messages": [
      {
        "role": "user",
        "content": "What is the capital of France?"
      }
    ],
    "max_tokens": 100
  }'
```

### Pricing:
- **sonar-pro** (с web search): $0.005/request (recommended)
- **sonar** (базовый): $0.001/request

### Monthly Budget для Testing:
- $10 = 2,000 requests (sonar-pro)
- Достаточно для мониторинга 100 домов с 20 queries/дом

### ⚠️ Важно:
- Credits не истекают
- No monthly fees (платишь только за использование)
- Usage dashboard показывает потребление в реальном времени

### 📧 Support:
Email: help@perplexity.ai

---

## 🌐 6. Proxies для Web Scraping (Autumna)

### ✅ Доступно для физлиц: ДА
### 💰 Стоимость: £30-100/месяц (trial £10)
### ⏱️ Время: 15 минут

### Зачем Нужны Proxies?
Web scraping без proxies приведет к:
- IP ban после 10-20 requests
- CAPTCHA challenges
- Rate limiting

### Рекомендуемые Сервисы:

#### Вариант 1: Bright Data (Лучший, но дороже)
```
URL: https://brightdata.com/

1. Sign up (можно trial $50)
2. Products → Residential Proxies
3. Plan: Pay-as-you-go или Starter ($50/month)
4. Setup:
   - Zone name: "autumna_scraping"
   - Country: United Kingdom (важно!)
   - Bandwidth: начать с 1GB (~£10)
   
5. Credentials:
   - Username: customer-YOUR_ID-zone-autumna_scraping
   - Password: (будет показан)
   - Proxy host: brd.superproxy.io:22225
   
6. Connection format:
   http://username:password@brd.superproxy.io:22225
```

**Плюсы**: Высокое качество, residential IPs, редкие блокировки  
**Минусы**: Дороже (£50-100/месяц для регулярного использования)  
**Trial**: $50 free credits при регистрации

#### Вариант 2: SmartProxy (Средний)
```
URL: https://smartproxy.com/

1. Sign up
2. Plan: Starter £28/month (3GB)
3. Setup:
   - Proxy type: Residential
   - Location: UK
   
4. Get credentials from dashboard:
   - Host: gate.smartproxy.com
   - Port: 7000
   - Username: your-username
   - Password: your-password
   
5. Connection format:
   http://username:password@gate.smartproxy.com:7000
```

**Плюсы**: Хорошее соотношение цена/качество  
**Минусы**: Качество чуть ниже чем Bright Data  
**Trial**: £10 trial plan (1GB)

#### Вариант 3: Webshare (Дешевле, но качество ниже)
```
URL: https://www.webshare.io/

1. Sign up (есть free tier!)
2. Plan: 
   - Free: 10 proxies (datacenter, не residential)
   - Residential Starter: £25/month
   
3. Dashboard → Proxy → List
4. Download proxy list или API access

5. Format:
   http://username:password@proxy-server:port
```

**Плюсы**: Есть free tier для тестирования  
**Минусы**: Datacenter proxies блокируются чаще  
**Free tier**: 10 proxies бесплатно (но не residential)

### 🎯 Рекомендация для Старта:

**Для тестирования (1-2 недели):**
- Webshare Free Tier (datacenter proxies)
- Попробовать scraping без proxy сначала (может работать при low volume)

**Для Production:**
- SmartProxy £28/month (лучший баланс)
- или Bright Data если budget позволяет

### Пример Использования:
```python
import requests

# Proxy credentials
proxy_url = "http://username:password@gate.smartproxy.com:7000"

proxies = {
    "http": proxy_url,
    "https": proxy_url
}

# Use proxy
response = requests.get(
    "https://www.autumna.care/care-homes",
    proxies=proxies
)
```

### ⚠️ Best Practices:
- Rotate proxies каждые 50-100 requests
- Rate limiting: 1 request/3 seconds минимум
- User-Agent rotation
- Respect robots.txt

---

## 📊 СВОДНАЯ ТАБЛИЦА: Быстрый Старт

### ✅ Можно начать СРАЗУ (0-10 мин):

| API | Action | Credentials |
|-----|--------|-------------|
| **FSA FHRS** | None | None needed! |
| **CQC (no code)** | None | None needed! |

### 🟢 Легко получить (10-30 мин):

| API | Time | Cost |
|-----|------|------|
| **CQC Partner Code** | 10 мин | FREE |
| **Companies House** | 10 мин | FREE |
| **Perplexity** | 5 мин | $10 |

### 🟡 Средняя сложность (30-60 мин):

| API | Time | Cost |
|-----|------|------|
| **Google Places** | 30 мин | FREE ($200 credits) |
| **Proxies** | 15 мин | £10-30 |

### 🔴 Требует одобрения (1-3 дня):

| API | Time | Cost |
|-----|------|------|
| **Places Insights** | 1-3 дня | FREE (preview) |

---

## 🚀 РЕКОМЕНДУЕМЫЙ ПОРЯДОК

### Day 1 (1 час):
```
✅ 1. FSA FHRS - используй сразу (0 мин)
✅ 2. CQC без Partner Code - используй сразу (0 мин)
✅ 3. Companies House - регистрация (10 мин)
✅ 4. Perplexity - add $10 credits (5 мин)
✅ 5. Google Cloud - создать project (20 мин)
✅ 6. Google Places API - enable & create key (10 мин)

ИТОГ: 6 из 7 API работают!
```

### Day 1 (вечер):
```
✅ 7. Submit request для Places Insights approval
✅ 8. Тестирование первых 6 APIs
✅ 9. Построить first comprehensive profile
```

### Day 2-3:
```
⏳ Ждать approval Places Insights
✅ Тестировать остальные APIs
✅ Build test database (100 homes)
```

### Day 3-4:
```
✅ Places Insights approved → setup BigQuery
✅ Полная интеграция всех источников
```

---

## 💳 РЕАЛЬНЫЕ COSTS ДЛЯ ТЕСТИРОВАНИЯ

### Setup (One-time):
```
CQC Partner Code:        £0
Companies House:         £0
Perplexity credits:      $10 (~£8)
Google Cloud setup:      £0
Proxies trial:           £10
───────────────────────────
TOTAL SETUP:            ~£18
```

### Monthly Testing (100 homes):
```
CQC + FSA + CH:          £0
Google Places:           £0 ($200 credits покрывают)
Perplexity:              £5 (minimal usage)
Proxies:                 £28
───────────────────────────
TOTAL MONTHLY:          £33
```

### 💡 Можно начать за £18!

---

## ⚠️ TROUBLESHOOTING

### Проблема: Google требует бизнес-аккаунт
**Решение**: 
- Указать "Individual Developer" в формах
- В billing выбрать "Individual" account type
- Для Places Insights: объяснить use case (research/testing)

### Проблема: Places Insights не одобрили
**Решение**:
- Написать на places-insights-support@google.com
- Объяснить: "Building care home comparison platform for UK market"
- Альтернатива: использовать только базовый Places API

### Проблема: Карта отклонена
**Решение**:
- Google/Perplexity принимают Visa/Mastercard
- Prepaid cards могут не работать
- Виртуальные карты (Revolut, Wise) обычно работают

### Проблема: Proxies блокируются
**Решение**:
- Переключиться на residential proxies (не datacenter)
- Увеличить delay между requests (3-5 sec)
- Rotate user agents

### Проблема: Budget concerns
**Решение**:
- Начать с FREE APIs (CQC, FSA, Companies House)
- Google дает $200 free credits
- Proxies можно попробовать без (low volume)
- Perplexity можно заменить на ручной поиск (временно)

---

## 📞 CONTACTS ДЛЯ ПОМОЩИ

### API Support:
- **CQC**: syndicationapi@cqc.org.uk
- **FSA**: data@food.gov.uk
- **Companies House**: enquiries@companieshouse.gov.uk
- **Google**: https://developers.google.com/maps/support
- **Perplexity**: help@perplexity.ai

### Community:
- **Stack Overflow**: Tags по каждому API
- **Google Cloud Community**: https://www.googlecloudcommunity.com/

---

## ✅ CHECKLIST: Готов к Тестированию?

Отметьте когда получите:

### Обязательные (для базового тестирования):
- [ ] CQC API access (с или без Partner Code)
- [ ] FSA FHRS (работает из коробки)
- [ ] Companies House API key
- [ ] Google Places API key

### Желательные:
- [ ] Perplexity API key ($10 credits)
- [ ] Proxies account

### Для Advanced Features:
- [ ] Places Insights approval (может занять дни)
- [ ] BigQuery setup

---

## 🎉 NEXT STEPS

После получения доступов:

1. **Создать .env file**:
```bash
CQC_PARTNER_CODE=your_code_or_leave_empty
COMPANIES_HOUSE_API_KEY=your_key
GOOGLE_PLACES_API_KEY=your_key
GOOGLE_CLOUD_PROJECT=your-project-id
PERPLEXITY_API_KEY=your_key_or_skip
PROXY_URL=your_proxy_or_skip
```

2. **Run Quick Tests**:
```bash
python test_apis.py
```

3. **Build First Profile**:
```python
from api_clients import DataIntegrator
integrator = DataIntegrator()
profile = integrator.build_comprehensive_profile("Manor House Care", "Brighton")
```

4. **Follow Week 1 Roadmap** из главного плана

---

**Удачи с получением доступов! 🚀**

*Если возникнут проблемы - пишите, помогу разобраться.*

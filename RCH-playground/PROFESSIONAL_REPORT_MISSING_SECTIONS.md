# Professional Report - Недостающие Секции и Источники Данных

**Дата**: 2025-01-XX  
**Статус**: 📋 АНАЛИЗ ТЕКУЩЕЙ РЕАЛИЗАЦИИ

---

## ОБЗОР

Этот документ описывает все секции и источники данных, которые должны быть реализованы для полного Professional Report согласно ТЗ (`PROFESSIONAL_Report_Complete.md`).

---

## ТЕКУЩЕЕ СОСТОЯНИЕ

### ✅ Реализовано

1. **Базовый 156-point matching алгоритм**
   - 8 категорий scoring
   - Dynamic weights система
   - Mock enriched_data структура

2. **Частично реализованные секции:**
   - CQC detailed ratings (базовые поля)
   - FSA ratings (базовые поля)
   - Financial data (базовые поля)
   - Staff data (базовые поля)
   - Google Places (базовые поля)

### ❌ Отсутствует

1. **Реальная интеграция API** (все данные сейчас mock)
2. **Детальные секции в PDF отчете**
3. **Supporting Analysis секции**
4. **Детальные данные для каждой секции**

---

## PART 2: TOP 5 STRATEGIC RECOMMENDATIONS (20 pages)

Каждый дом должен включать **4 страницы** детального анализа:

### Страница 1: Home Details & Match Score Breakdown ✅ (Частично)

**Текущее состояние**: Базовая структура есть

**Необходимо добавить:**
- [ ] Capacity: total beds, available beds
- [ ] Type: residential/nursing/dementia/mixed (детализация)
- [ ] Contact: phone, email, website (полные данные)
- [ ] Match Score Breakdown с детализацией по 8 категориям
- [ ] Визуализация scores (графики, прогресс-бары)

---

### Страница 2: CQC Deep Dive (1 page) ⚠️ (Частично)

**Текущее состояние**: Базовые поля есть в `enriched_data['cqc_detailed']`

**Необходимо добавить:**

#### 1. Overall Rating + Trend (3-5 years)
- [ ] Historical ratings за 3-5 лет
- [ ] Trend visualization (график улучшения/ухудшения)
- [ ] Trend analysis: "Improving", "Declining", "Stable"
- [ ] Inspection dates timeline

#### 2. 5 Detailed Ratings с деталями
- [ ] **Safe rating**: rating + detailed explanation
- [ ] **Effective rating**: rating + detailed explanation  
- [ ] **Caring rating**: rating + detailed explanation
- [ ] **Responsive rating**: rating + detailed explanation
- [ ] **Well-Led rating**: rating + detailed explanation

**Источник данных**: CQC Detailed API
```python
# Необходимо интегрировать:
- GET /api/care-providers/{provider_id}/locations/{location_id}/ratings
- Historical ratings endpoint
- Action plans endpoint
```

#### 3. Active Improvement Plans
- [ ] Список активных планов улучшения
- [ ] Сроки выполнения
- [ ] Статус выполнения
- [ ] Детали требований CQC

**Источник данных**: CQC API - action plans endpoint

---

### Страница 3: Financial Stability Analysis (1 page) ⚠️ (Частично)

**Текущее состояние**: Базовые поля есть в `enriched_data['financial_data']`

**Необходимо добавить:**

#### 1. 3-Year Financial Summary
- [ ] **Revenue trend** (график за 3 года)
- [ ] **Profitability** (net margin за каждый год)
- [ ] **Working capital** (current ratio за каждый год)
- [ ] **Debt levels** (total liabilities, debt-to-equity ratio)
- [ ] **Assets & Liabilities** breakdown

**Источник данных**: Companies House API
```python
# Необходимо интегрировать:
- GET /company/{company_number}/accounts
- GET /company/{company_number}/filing-history
- 3-year financial data extraction
```

#### 2. Bankruptcy Risk Score (0-100)
- [ ] **Altman Z-score calculation** (уже частично есть)
- [ ] Risk level: Safe/Gray Zone/High Risk
- [ ] Risk score 0-100 (где >60 = high risk)
- [ ] Explanation of risk factors

**Формула Altman Z-score:**
```
Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
Where:
- X1 = Working Capital / Total Assets
- X2 = Retained Earnings / Total Assets
- X3 = EBIT / Total Assets
- X4 = Market Value of Equity / Book Value of Liabilities
- X5 = Sales / Total Assets

Risk zones:
- Z > 2.99: Safe (score 0-30)
- 1.81-2.99: Gray zone (score 31-60)
- Z < 1.81: High risk (score 61-100)
```

#### 3. Comparison to UK Average
- [ ] Revenue vs UK care home average
- [ ] Profitability vs UK average
- [ ] Working capital vs UK average
- [ ] Industry benchmarks

**Источник данных**: 
- Companies House API для данных дома
- UK care home industry benchmarks (из исследований или базы данных)

#### 4. Red Flags Detection
- [ ] Late filing detection
- [ ] Negative working capital
- [ ] Director changes (frequent turnover)
- [ ] Declining revenue trend
- [ ] Increasing debt levels

**Источник данных**: Companies House API
```python
# Необходимо интегрировать:
- Filing timeliness check
- Director turnover analysis
- Financial trend analysis
```

---

### Страница 4: Staff Quality Report (1 page) ⚠️ (Частично)

**Текущее состояние**: Базовые поля есть в `enriched_data['staff_data']`

**Необходимо добавить:**

#### 1. Glassdoor Rating + Staff Size
- [ ] Employee satisfaction rating (1-5)
- [ ] Review count
- [ ] Work-life balance score
- [ ] Management score
- [ ] Salary reviews
- [ ] Staff size (total employees)

**Источник данных**: Glassdoor (через Perplexity AI research)
```python
# Необходимо реализовать:
- Perplexity AI query: "{company_name} care home glassdoor rating employee reviews"
- Parse rating, review count, sentiment
- Extract management score, work-life balance
```

#### 2. Turnover Rate % (Annual Staff Changes)
- [ ] Annual turnover percentage
- [ ] Department breakdown turnover
- [ ] Comparison to industry average (UK care home avg: ~25-30%)
- [ ] Turnover trend (increasing/decreasing/stable)

**Источник данных**: 
- Job Boards (активные вакансии = turnover signal)
- LinkedIn (staff changes over time)
- Perplexity AI research

#### 3. Average Tenure (Years)
- [ ] Average years at home
- [ ] Department breakdown tenure
- [ ] Longest-serving staff
- [ ] Tenure distribution

**Источник данных**: LinkedIn (через Perplexity AI)
```python
# Необходимо реализовать:
- Perplexity AI query: "{home_name} care home staff linkedin employees tenure"
- Extract staff count, average tenure, certifications
- Estimate turnover rate
```

#### 4. Department Breakdown
- [ ] Nursing staff count
- [ ] Care staff count
- [ ] Support staff count
- [ ] Management staff count
- [ ] Staff-to-resident ratio

**Источник данных**: 
- LinkedIn (через Perplexity AI)
- CQC registration data
- Job boards (department-specific listings)

#### 5. Hiring Trends
- [ ] Active job listings count
- [ ] Hiring frequency (posts per month)
- [ ] Department needs (which departments hiring)
- [ ] Salary ranges advertised

**Источник данных**: Job Boards API
```python
# Необходимо интегрировать:
- Job boards scraping/API
- Active job listings per home
- Job title & salary range
- Hiring frequency analysis
```

#### 6. Staff Sentiment (Positive vs Negative Reviews)
- [ ] Sentiment analysis of Glassdoor reviews
- [ ] Positive review percentage
- [ ] Negative review percentage
- [ ] Common themes (positive/negative)
- [ ] Management response rate

**Источник данных**: Glassdoor (через Perplexity AI)

---

### Страница 5: Operational Deep Dive (1 page) ⚠️ (Частично)

**Текущее состояние**: Базовые поля есть

**Необходимо добавить:**

#### 1. FSA FHRS Rating + Trends
- [ ] Overall rating (5/4/3/2/1/0)
- [ ] **3 sub-scores**:
  - Hygiene handling score
  - Cleanliness score
  - Management score
- [ ] Historical ratings trend (3-5 years)
- [ ] Date of last inspection
- [ ] Specific compliance notes
- [ ] Special dietary considerations

**Источник данных**: FSA FHRS API
```python
# Необходимо интегрировать:
- FSA FHRS API endpoint
- GET /api/food-hygiene-rating/{business_id}
- Historical ratings endpoint
- 3-score breakdown extraction
```

#### 2. Google Places Rating + Review Count
- [ ] Rating (1-5 stars)
- [ ] Review count & trend
- [ ] Review sentiment analysis (ML-based)
- [ ] Photo gallery
- [ ] Opening hours & contact

**Источник данных**: Google Places API
```python
# Необходимо интегрировать:
- Google Places API (Places API)
- Review sentiment analysis (ML model или API)
- Photo extraction
```

#### 3. Notable Reviews (Positive & Concerning)
- [ ] Top 3 positive reviews (extracted highlights)
- [ ] Top 3 concerning reviews (extracted highlights)
- [ ] Common themes in reviews
- [ ] Review response rate (home management)

**Источник данных**: Google Places API reviews

#### 4. Medical Capabilities Match
- [ ] Staff qualifications vs resident needs
- [ ] Specialist capabilities verification:
  - Dementia care specialists
  - Diabetes management
  - Cardiac care
  - Mobility support
- [ ] Medical equipment availability
- [ ] Medication management protocols
- [ ] Emergency response capabilities

**Источник данных**: 
- CQC registration data
- LinkedIn staff qualifications (через Perplexity AI)
- Care protocols from CQC

#### 5. Pricing Detail (Weekly Cost + Inclusions)
- [ ] Weekly cost breakdown
- [ ] Included services list
- [ ] Additional fees
- [ ] Care package options
- [ ] Price trends (historical pricing)
- [ ] Comparison to market average

**Источник данных**: Autumna API
```python
# Необходимо интегрировать:
- Autumna pricing API
- Current & historical pricing
- Price changes & trends
- Hidden fees identification
```

#### 6. Visitor Patterns (Google Places Insights)
- [ ] Dwell time (average minutes)
- [ ] Repeat visitor rate
- [ ] Footfall analytics
- [ ] Visitor engagement score

**Источник данных**: Google Places Insights API
```python
# Необходимо исследовать:
- Google Places Insights API availability
- Visitor patterns API
- Footfall analytics API
```

---

## PART 3: SUPPORTING ANALYSIS (5-10 pages)

### Секция 1: Funding Optimization (2 pages) ❌ (Отсутствует полностью)

**Необходимо реализовать:**

#### 1. CHC Eligibility Calculator
- [ ] CHC (Continuing Healthcare) eligibility assessment
- [ ] Scoring based on:
  - Nature (health needs)
  - Complexity (care complexity)
  - Intensity (care frequency)
  - Unpredictability (care variability)
- [ ] Eligibility probability score
- [ ] Estimated funding amount

**Источник данных**: 
- NHS CHC guidelines
- CHC assessment framework
- Local authority funding rules

#### 2. LA Funding Availability
- [ ] Local Authority funding eligibility
- [ ] Funding thresholds
- [ ] Means testing calculator
- [ ] Top-up fees explanation

**Источник данных**: 
- Local authority funding rules (per LA)
- MSIF (Market Sustainability Improvement Fund) data
- Fair Cost Gap calculations

#### 3. DPA Considerations
- [ ] Deprivation of Assets rules
- [ ] 6-month lookback period
- [ ] Gifting rules
- [ ] Property disregard rules

**Источник данных**: 
- DPA legislation
- Local authority guidance

#### 4. Estimated Funding Outcomes
- [ ] CHC funding estimate
- [ ] LA funding estimate
- [ ] Self-funding estimate
- [ ] Combined funding scenarios

#### 5. Cost Projections (5-year)
- [ ] 5-year cost projection
- [ ] Inflation adjustments
- [ ] Price increase assumptions
- [ ] Total cost over 5 years
- [ ] Funding gap analysis

**Источник данных**: 
- Historical pricing trends (Autumna)
- Inflation rates
- Care home price increase patterns

---

### Секция 2: Comparative Analysis (2 pages) ❌ (Отсутствует полностью)

**Необходимо реализовать:**

#### 1. Side-by-Side Comparison Table (5 homes)
- [ ] Match score rankings
- [ ] Price comparison
- [ ] CQC ratings comparison
- [ ] FSA ratings comparison
- [ ] Financial stability comparison
- [ ] Staff quality comparison
- [ ] Distance comparison
- [ ] Key differentiators

**Формат**: Таблица с 5 колонками (по одному дому) и строками для каждого критерия

#### 2. Match Score Rankings
- [ ] Visual ranking (1-5)
- [ ] Score breakdown comparison
- [ ] Category-by-category comparison

#### 3. Price Comparison
- [ ] Weekly cost comparison
- [ ] Annual cost comparison
- [ ] 5-year cost comparison
- [ ] Value-for-money analysis

#### 4. Key Differentiators
- [ ] Unique strengths per home
- [ ] Unique concerns per home
- [ ] Best match for specific needs

---

### Секция 3: Red Flags & Risk Assessment (2 pages) ❌ (Отсутствует полностью)

**Необходимо реализовать:**

#### 1. Concerning Signals
- [ ] Financial stability warnings
- [ ] CQC compliance issues
- [ ] Staff turnover concerns
- [ ] Pricing increases history
- [ ] Negative review trends
- [ ] Regulatory actions

**Источник данных**: 
- Companies House (financial red flags)
- CQC (compliance issues)
- Glassdoor/LinkedIn (staff turnover)
- Autumna (pricing trends)
- Google Places (review trends)
- Perplexity AI (regulatory actions)

#### 2. Financial Stability Warnings
- [ ] Bankruptcy risk >60
- [ ] Declining revenue
- [ ] Negative working capital
- [ ] Late filings
- [ ] Director turnover

#### 3. CQC Compliance Issues
- [ ] Requires Improvement rating
- [ ] Inadequate rating
- [ ] Declining trend
- [ ] Active improvement plans
- [ ] Safeguarding incidents

#### 4. Staff Turnover Concerns
- [ ] Turnover rate >30%
- [ ] Frequent hiring
- [ ] Low Glassdoor rating
- [ ] Negative staff sentiment

#### 5. Pricing Increases History
- [ ] Historical price increases
- [ ] Above-market increases
- [ ] Hidden fees
- [ ] Contract terms concerns

---

### Секция 4: Negotiation Strategy (2 pages) ❌ (Отсутствует полностью)

**Необходимо реализовать:**

#### 1. Market-Rate Analysis
- [ ] Market average pricing
- [ ] Price range for similar homes
- [ ] Value positioning
- [ ] Competitive pricing analysis

**Источник данных**: 
- Autumna pricing data
- Market analysis
- Local authority pricing bands

#### 2. Discount Negotiation Points
- [ ] Long-term commitment discounts
- [ ] Self-funding discounts
- [ ] Off-peak placement discounts
- [ ] Referral discounts
- [ ] Trial period discounts

#### 3. Contract Review Checklist
- [ ] Key contract terms to review
- [ ] Hidden fees to watch for
- [ ] Cancellation terms
- [ ] Price increase clauses
- [ ] Trial period terms
- [ ] Additional services pricing

#### 4. Questions to Ask at Visit
- [ ] Medical care questions
- [ ] Staff qualification questions
- [ ] Recent CQC feedback questions
- [ ] Financial stability questions
- [ ] Trial period questions
- [ ] Cancellation terms questions

#### 5. Email Templates for Inquiry
- [ ] Initial inquiry template
- [ ] Follow-up template
- [ ] Negotiation template
- [ ] Contract review template

---

## PART 4: NEXT STEPS (1 page) ⚠️ (Частично)

**Текущее состояние**: Базовая структура есть

**Необходимо добавить:**

#### 1. Recommended Actions per Home
- [ ] Home 1: "Visit within 2 weeks, ask about..."
- [ ] Home 2: "Call to discuss funding..."
- [ ] Home 3: "Review contract for..."
- [ ] Home 4: "Clarify medical support..."
- [ ] Home 5: "Request staff references..."

#### 2. Questions for Home Manager
- [ ] Medical care provision
- [ ] Staff qualifications
- [ ] Recent CQC feedback
- [ ] Financial stability
- [ ] Trial period availability
- [ ] Cancellation terms

#### 3. Premium Upgrade Offer
- [ ] "Upgrade to PREMIUM for £249"
- [ ] "Get 7-week monitoring"
- [ ] "Real-time alert system"
- [ ] "Deep research per home"

---

## ИСТОЧНИКИ ДАННЫХ ДЛЯ ИНТЕГРАЦИИ

### 1. CQC Detailed API ⚠️ (Частично интегрирован)

**Необходимые endpoints:**
- [ ] GET `/api/care-providers/{provider_id}/locations/{location_id}/ratings`
- [ ] GET `/api/care-providers/{provider_id}/locations/{location_id}/ratings/history`
- [ ] GET `/api/care-providers/{provider_id}/locations/{location_id}/action-plans`

**Данные для извлечения:**
- [ ] 5 detailed ratings (Safe, Effective, Caring, Responsive, Well-Led)
- [ ] Historical ratings (3-5 years)
- [ ] Action plans
- [ ] Inspection dates
- [ ] Trend analysis

---

### 2. FSA FHRS API ⚠️ (Частично интегрирован)

**Необходимые endpoints:**
- [ ] GET `/api/food-hygiene-rating/{business_id}`
- [ ] GET `/api/food-hygiene-rating/{business_id}/history`

**Данные для извлечения:**
- [ ] Overall rating (5/4/3/2/1/0)
- [ ] 3 sub-scores (Hygiene, Cleanliness, Management)
- [ ] Inspection date
- [ ] Compliance notes
- [ ] Historical ratings

---

### 3. Companies House API ✅ (Уже интегрирован, но нужно расширить)

**Текущее состояние**: Базовый клиент есть (`companies_house_client.py`)

**Необходимо добавить:**
- [ ] 3-year financial data extraction
- [ ] Altman Z-score calculation (уже частично есть)
- [ ] Bankruptcy risk scoring (0-100)
- [ ] Filing timeliness check
- [ ] Director turnover analysis
- [ ] Financial trend analysis
- [ ] UK industry benchmarks comparison

**Endpoints:**
- [x] GET `/company/{company_number}` (есть)
- [x] GET `/company/{company_number}/accounts` (есть)
- [ ] GET `/company/{company_number}/filing-history` (нужно расширить)
- [ ] GET `/company/{company_number}/officers` (нужно расширить)

---

### 4. Google Places API ⚠️ (Частично интегрирован)

**Необходимые endpoints:**
- [ ] Places API - Place Details
- [ ] Places API - Reviews
- [ ] Places API - Photos
- [ ] **Places Insights API** (нужно исследовать доступность)

**Данные для извлечения:**
- [ ] Rating & review count
- [ ] Review sentiment analysis
- [ ] Photo gallery
- [ ] Opening hours
- [ ] Visitor patterns (dwell time, repeat visitor rate)
- [ ] Footfall analytics

**Примечание**: Google Places Insights API может быть недоступен или платным. Нужно исследовать альтернативы или использовать Perplexity AI для visitor insights.

---

### 5. Glassdoor ⚠️ (Через Perplexity AI)

**Текущее состояние**: Нет интеграции

**Необходимо реализовать:**
- [ ] Perplexity AI research function для Glassdoor
- [ ] Query: "{company_name} care home glassdoor rating employee reviews"
- [ ] Parse rating, review count, sentiment
- [ ] Extract management score, work-life balance
- [ ] Store в `staff_data` table

**Пример реализации:**
```python
async def fetch_glassdoor_data(home_name: str, company_name: str):
    query = f"{company_name} {home_name} care home glassdoor rating employee reviews"
    result = await perplexity_client.research(query)
    # Parse result and extract:
    # - Employee satisfaction rating
    # - Review count
    # - Management score
    # - Work-life balance score
    # - Staff comments & sentiment
```

---

### 6. LinkedIn ⚠️ (Через Perplexity AI)

**Текущее состояние**: Нет интеграции

**Необходимо реализовать:**
- [ ] Perplexity AI research function для LinkedIn
- [ ] Query: "{home_name} care home staff linkedin employees tenure"
- [ ] Extract staff count, average tenure, certifications
- [ ] Estimate turnover rate
- [ ] Store в `staff_data` table

**Пример реализации:**
```python
async def fetch_linkedin_data(home_name: str):
    query = f"{home_name} care home staff linkedin employees tenure certifications"
    result = await perplexity_client.research(query)
    # Parse result and extract:
    # - Staff count
    # - Average tenure
    # - Certifications
    # - Department organization
    # - Hiring patterns
```

---

### 7. Job Boards ⚠️ (Нет интеграции)

**Необходимо реализовать:**
- [ ] Job board scraping/API integration
- [ ] Active job listings per home
- [ ] Job title & salary range
- [ ] Hiring frequency analysis
- [ ] Department needs analysis

**Источники:**
- Indeed API
- Reed API
- Totaljobs API
- Или web scraping (с соблюдением ToS)

---

### 8. Autumna API ⚠️ (Нет интеграции)

**Необходимо реализовать:**
- [ ] Autumna pricing API integration
- [ ] Current & historical pricing
- [ ] Price changes & trends
- [ ] Hidden fees identification
- [ ] Care package options

**Примечание**: Нужно проверить доступность Autumna API или использовать альтернативные источники.

---

### 9. Perplexity AI ✅ (Уже интегрирован)

**Текущее состояние**: Базовый клиент есть

**Необходимо использовать для:**
- [ ] Glassdoor data research
- [ ] LinkedIn data research
- [ ] Deep research on home (media mentions, incidents)
- [ ] Owner/operator background
- [ ] Regulatory actions

---

## ПРИОРИТЕТЫ РЕАЛИЗАЦИИ

### 🔴 КРИТИЧЕСКИЙ ПРИОРИТЕТ (Phase 1)

1. **CQC Detailed API Integration**
   - Получение 5 detailed ratings
   - Historical ratings (3-5 years)
   - Action plans

2. **FSA Detailed API Integration**
   - 3 sub-scores extraction
   - Historical ratings

3. **Companies House Enhancement**
   - 3-year financial data
   - Altman Z-score calculation (завершить)
   - Bankruptcy risk scoring (0-100)

4. **Google Places API Integration**
   - Place Details
   - Reviews & sentiment analysis
   - Photos

### 🟡 ВЫСОКИЙ ПРИОРИТЕТ (Phase 2)

5. **Glassdoor Integration (Perplexity AI)**
   - Employee satisfaction data
   - Management score
   - Staff sentiment

6. **LinkedIn Integration (Perplexity AI)**
   - Staff tenure
   - Certifications
   - Turnover estimates

7. **Autumna Pricing Integration**
   - Current & historical pricing
   - Price trends

8. **Supporting Analysis Sections**
   - Funding Optimization
   - Comparative Analysis
   - Red Flags & Risk Assessment
   - Negotiation Strategy

### 🟢 СРЕДНИЙ ПРИОРИТЕТ (Phase 3)

9. **Job Boards Integration**
   - Turnover signals
   - Hiring patterns

10. **Google Places Insights API**
    - Visitor patterns
    - Footfall analytics

11. **PDF Template Enhancement**
    - Все секции в PDF
    - Визуализации (графики, таблицы)
    - Professional styling

---

## СЛЕДУЮЩИЕ ШАГИ

1. **Изучить доступность API:**
   - Google Places Insights API
   - Autumna API
   - Job Boards APIs

2. **Создать интеграционные модули:**
   - CQC Detailed API client
   - FSA Detailed API client (расширить существующий)
   - Glassdoor research (Perplexity AI)
   - LinkedIn research (Perplexity AI)
   - Autumna API client

3. **Реализовать Supporting Analysis секции:**
   - Funding Optimization calculator
   - Comparative Analysis generator
   - Red Flags detector
   - Negotiation Strategy generator

4. **Обновить PDF template:**
   - Добавить все секции
   - Визуализации
   - Professional styling

---

## ССЫЛКИ НА ДОКУМЕНТАЦИЮ

- `input/PROFESSIONAL_Report_Complete.md` - Полное ТЗ
- `PROFESSIONAL_REPORT_IMPLEMENTATION_PLAN.md` - План реализации
- `input/TECHNICAL_PROFESSIONAL_Dynamic_Weights_v2.md` - Dynamic weights
- `input/TECHNICAL_PROFESSIONAL_Matching_Logic (1).md` - Matching logic

---

**End of Document**


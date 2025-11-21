# План реализации недостающего функционала FREE Report

**Дата:** 2025-01-XX  
**Версия:** 1.0  
**Статус:** 📋 План реализации

---

## 📊 Анализ текущего состояния

### ✅ Уже реализовано (Frontend)

1. **UI компоненты:**
   - ✅ FreeReportViewer с hero header и WOW эффектом
   - ✅ QuestionLoader для загрузки JSON анкет
   - ✅ ReportRenderer с 8 секциями отчёта
   - ✅ LoadingAnimation с прогресс-баром (~30 сек)
   - ✅ FreeReportPDF для генерации PDF
   - ✅ Mobile responsive дизайн

2. **Функционал:**
   - ✅ Загрузка sample questionnaires (3 файла)
   - ✅ Drag & drop для своих JSON
   - ✅ Валидация questionnaire данных
   - ✅ Отображение Fair Cost Gap (эмоциональный блок)
   - ✅ Отображение 3 домов с деталями
   - ✅ PDF экспорт (8 страниц)
   - ✅ Error handling с fallback на mock данные
   - ✅ Тесты на 3 дефолтных JSON

3. **Интеграция:**
   - ✅ TanStack Query для API запросов
   - ✅ Хук useFreeReport с fallback логикой
   - ✅ Вызов MSIF API для Fair Cost Gap
   - ✅ Маршрутизация `/free-report`

### ❌ Не реализовано (Backend + Integration)

1. **50-Point Matching Algorithm** ❌
2. **Database Schema** ❌
3. **Email отправка** ❌
4. **S3 upload для PDF** ❌
5. **Caching strategy (Redis)** ❌
6. **Performance optimization** ❌
7. **Monitoring & Analytics** ❌

---

## 🎯 План реализации по приоритетам

### PHASE 1: Backend Core (Week 1) 🔴 КРИТИЧНО

#### 1.1 Database Schema (PostgreSQL + PostGIS)

**Файлы:**
- `api-testing-suite/backend/migrations/001_create_free_report_tables.sql`
- `api-testing-suite/backend/models/free_report.py`

**Таблицы:**
```sql
- questionnaires (id, postcode, care_type, budget_max, email, created_at)
- care_homes (id, name, postcode, location GEOGRAPHY, weekly_price_avg, care_types[], beds_available)
- cqc_ratings (id, care_home_id, overall_rating, last_updated)
- google_data (id, care_home_id, rating, review_count, last_fetched)
- free_reports (id, questionnaire_id, home_ids[], pdf_s3_url, generated_at)
```

**Индексы:**
- GIST индекс на location для geo-queries
- Индексы на postcode, price, care_types

**Оценка:** 4-6 часов

---

#### 1.2 50-Point Matching Algorithm

**Файл:** `api-testing-suite/backend/services/matching_service.py`

**Функции:**
```python
def calculate_50_point_score(home, user_inputs) -> int:
    """
    Location: 20 points (≤5mi=20, ≤10mi=15, ≤15mi=10, >15mi=5)
    CQC Rating: 25 points (Outstanding=25, Good=20, RI=10, Inadequate=0)
    Budget Match: 20 points (within=20, +£50-100=15, +£100-200=10, +£200+=0)
    Care Type Match: 15 points (perfect=15, close=10, general=5)
    Availability: 10 points (available=10, <4wks=5, 4+wks=0)
    Google Reviews: 10 points (≥4.5=10, ≥4.0=7, ≥3.5=4, <3.5=0)
    """

def select_3_strategic_homes(candidates, user_inputs) -> List[CareHome]:
    """
    Strategy 1: Safe Bet (highest CQC within 10 miles)
    Strategy 2: Best Reputation (highest Google rating with 20+ reviews)
    Strategy 3: Smart Value (best quality/price ratio)
    """
```

**Тесты:**
- Unit тесты для каждого scoring category
- Integration тесты для select_3_strategic_homes
- Тесты на edge cases (нет кандидатов, дубликаты)

**Оценка:** 8-12 часов

---

#### 1.3 API Endpoint `/api/free-report` (Enhanced)

**Файл:** `api-testing-suite/backend/main.py` (улучшить существующий)

**Текущее состояние:**
- ✅ Базовый endpoint существует
- ❌ Не использует 50-point algorithm
- ❌ Не сохраняет в БД
- ❌ Не отправляет email

**Требуется:**
```python
@app.post("/api/free-report")
async def generate_free_report(request: Dict[str, Any]):
    """
    1. Сохранить questionnaire в БД
    2. Фильтровать кандидатов (geo query)
    3. Рассчитать 50-point scores
    4. Выбрать 3 strategic homes
    5. Fetch детальные данные (CQC, FSA, Google)
    6. Сгенерировать PDF
    7. Upload в S3
    8. Сохранить report record
    9. Отправить email с download link
    10. Вернуть report_id и download_url
    """
```

**Оценка:** 6-8 часов

---

### PHASE 2: Data Sources Integration (Week 1-2) 🟡 ВАЖНО

#### 2.1 CQC API Integration

**Файл:** `api-testing-suite/backend/services/cqc_service.py`

**Функции:**
```python
async def fetch_cqc_rating(location_id: str) -> CQCRating:
    """
    - Cache: 48 hours (Redis)
    - Rate limit: 60/min
    - Fallback: cached data или mock
    """

async def fetch_cqc_details(location_id: str) -> CQCDetails:
    """
    - Overall rating
    - 5 category ratings
    - Last inspection date
    - Trends (3-year history)
    """
```

**Оценка:** 4-6 часов

---

#### 2.2 FSA FHRS API Integration

**Файл:** `api-testing-suite/backend/services/fsa_service.py`

**Функции:**
```python
async def fetch_fsa_rating(business_id: str) -> FSARating:
    """
    - Cache: 7 days (Redis)
    - Rate limit: 10/sec
    - Returns: Overall rating + sub-scores
    """

async def fetch_fsa_detailed_analysis(business_id: str) -> FSADetailed:
    """
    Для Professional Peek:
    - Hygienic food handling (5/5)
    - Cleanliness & condition (5/5)
    - Management of food safety (5/5)
    - 3-year trend
    - Health implications
    """
```

**Оценка:** 4-6 часов

---

#### 2.3 Google Places API Integration

**Файл:** `api-testing-suite/backend/services/google_places_service.py`

**Функции:**
```python
async def fetch_google_places_data(place_id: str) -> GooglePlacesData:
    """
    - Cache: 24 hours (Redis)
    - Cost: £0.005/call
    - Returns: rating, review_count, review highlights
    """

async def fetch_google_insights(place_id: str) -> GoogleInsights:
    """
    Для Professional tier:
    - Visitor analytics (footfall, dwell time)
    - Sentiment analysis
    - Review themes
    """
```

**Оценка:** 4-6 часов

---

#### 2.4 Autumna API Integration (Optional)

**Файл:** `api-testing-suite/backend/services/autumna_service.py`

**Функции:**
```python
async def fetch_autumna_pricing(care_home_id: str) -> AutumnaPricing:
    """
    - Cache: 30 days (Redis)
    - Free API
    - Returns: pricing data, availability
    """
```

**Оценка:** 2-4 часа

---

### PHASE 3: PDF & Email (Week 2) 🟡 ВАЖНО

#### 3.1 PDF Generation Enhancement

**Текущее:** ✅ Базовый PDF через @react-pdf/renderer

**Требуется:**
- Backend PDF generation (WeasyPrint или Playwright)
- HTML template с Jinja2
- 8 страниц точно как в спецификации:
  1. Cover + Introduction
  2-4. 3 Strategic Homes (по странице)
  5. Professional Peek (FSA Analysis для 1 дома)
  6. Explicit Gap List
  7. Thompson Story + ROI Calculator
  8. Decision Framework + CTA

**Файлы:**
- `api-testing-suite/backend/services/pdf_generator.py`
- `api-testing-suite/backend/templates/free_report.html`

**Оценка:** 8-12 часов

---

#### 3.2 S3 Upload

**Файл:** `api-testing-suite/backend/services/s3_service.py`

**Функции:**
```python
async def upload_pdf_to_s3(pdf_bytes: bytes, report_id: str) -> str:
    """
    - Upload в S3 bucket
    - Generate presigned URL (7 days expiry)
    - Return public URL
    """
```

**Оценка:** 2-3 часа

---

#### 3.3 Email Service (SendGrid)

**Файл:** `api-testing-suite/backend/services/email_service.py`

**Функции:**
```python
async def send_free_report_email(email: str, download_url: str, report_id: str):
    """
    Subject: "Your RightCareHome Shortlist"
    Template: free_report_email.html
    Includes: download link, report_id, CTA to Professional
    """

async def send_error_email(email: str, error_message: str):
    """
    Subject: "Issue with your report"
    Template: error_email.html
    """
```

**Email Sequence (3 emails):**
- Day 1 (5 hours): "Here's your shortlist"
- Day 3: "Here's what you're missing"
- Day 5: "See the full analysis"

**Оценка:** 6-8 часов

---

### PHASE 4: Caching & Performance (Week 2) 🟢 ОПТИМИЗАЦИЯ

#### 4.1 Redis Caching Strategy

**Файл:** `api-testing-suite/backend/services/cache_service.py`

**Cache Layers:**
```python
# Layer 1: Query Cache
cache_key = f"query:{postcode}:{radius}:{care_type}:{budget}"
TTL: 1 hour
Hit rate target: 75-80%

# Layer 2: API Cache
- CQC: 48 hours
- FSA: 7 days
- Google: 24 hours
- Autumna: 30 days
```

**Оценка:** 4-6 часов

---

#### 4.2 Performance Optimization

**Targets:**
- Questionnaire submit: <200ms ✅
- Filter candidates: <15ms
- Calculate scores: <10ms
- Generate HTML: <3s
- Render PDF: <30s
- Upload S3: <3s
- Send email: <5s
- **TOTAL: <60s** (target: 48-52s)

**Оптимизации:**
- Database query optimization (индексы)
- Parallel API calls (asyncio.gather)
- PDF generation в background task
- Connection pooling

**Оценка:** 6-8 часов

---

### PHASE 5: Monitoring & Analytics (Week 3) 🟢 МОНИТОРИНГ

#### 5.1 Metrics & Monitoring

**Файл:** `api-testing-suite/backend/monitoring/metrics.py`

**Prometheus Metrics:**
```python
- rightcarehome_free_reports_generated_total
- rightcarehome_free_report_generation_seconds (histogram)
- rightcarehome_free_api_errors_total (by source)
- rightcarehome_free_cache_hit_rate
- rightcarehome_free_email_sent_total
- rightcarehome_free_conversion_to_pro_total
```

**Alerts:**
- Generation time >60 seconds
- API error rate >5%
- Email delivery failure
- Cache hit rate <70%

**Оценка:** 4-6 часов

---

#### 5.2 Analytics Tracking

**Интеграция:**
- Mixpanel для user events
- Google Analytics для conversion tracking
- Custom dashboard для бизнес метрик

**Events:**
- questionnaire_started
- questionnaire_completed
- report_generated
- pdf_downloaded
- email_opened
- professional_cta_clicked
- professional_converted

**Оценка:** 4-6 часов

---

## 📋 Детальный чеклист реализации

### Backend Core ✅/❌

- [ ] Database schema (PostgreSQL + PostGIS)
- [ ] 50-point matching algorithm
- [ ] select_3_strategic_homes функция
- [ ] Enhanced `/api/free-report` endpoint
- [ ] Database models (SQLAlchemy)
- [ ] Migration scripts

### Data Sources ✅/❌

- [ ] CQC API integration
- [ ] FSA FHRS API integration
- [ ] Google Places API integration
- [ ] Autumna API integration (optional)
- [ ] Error handling для каждого API
- [ ] Fallback на cached/mock данные

### PDF & Email ✅/❌

- [ ] Backend PDF generation (WeasyPrint/Playwright)
- [ ] HTML template (Jinja2) - 8 страниц
- [ ] Professional Peek секция (FSA для 1 дома)
- [ ] Explicit Gap List секция
- [ ] Thompson Story секция
- [ ] S3 upload service
- [ ] SendGrid email integration
- [ ] Email templates (3 последовательности)

### Caching & Performance ✅/❌

- [ ] Redis setup и connection
- [ ] Query cache layer
- [ ] API cache layer
- [ ] Cache invalidation strategy
- [ ] Performance optimization (parallel calls)
- [ ] Database query optimization

### Monitoring ✅/❌

- [ ] Prometheus metrics
- [ ] Grafana dashboard
- [ ] Alerting rules
- [ ] Analytics tracking (Mixpanel)
- [ ] Error logging (Sentry)

### Testing ✅/❌

- [ ] Unit тесты для matching algorithm
- [ ] Integration тесты для API endpoints
- [ ] E2E тесты для полного flow
- [ ] Load testing (100 concurrent users)
- [ ] Performance benchmarking

---

## 🚀 Приоритеты и Timeline

### Week 1: Critical Path
1. **Database Schema** (Day 1-2)
2. **50-Point Algorithm** (Day 2-4)
3. **Enhanced API Endpoint** (Day 4-5)
4. **CQC + FSA Integration** (Day 5-6)

### Week 2: Core Features
1. **Google Places Integration** (Day 1-2)
2. **PDF Generation** (Day 2-4)
3. **S3 Upload** (Day 4-5)
4. **Email Service** (Day 5-6)

### Week 3: Optimization
1. **Redis Caching** (Day 1-2)
2. **Performance Optimization** (Day 2-4)
3. **Monitoring Setup** (Day 4-5)
4. **Testing & QA** (Day 5-6)

---

## 📊 Метрики успеха

### Technical Metrics
- ✅ Report generation: <60s (target: 48-52s)
- ✅ API error rate: <5%
- ✅ Cache hit rate: >75%
- ✅ Email delivery: >95%
- ✅ Uptime: >99.5%

### Business Metrics
- ✅ FREE reports: 300/week (Week 1)
- ✅ Conversion to PRO: 18-25% (target: 20%)
- ✅ User rating: 4.5+/5.0
- ✅ PDF download rate: >60%

---

## 🔧 Технические детали

### Tech Stack (Backend)

- **Language:** Python 3.11+
- **Framework:** FastAPI
- **Database:** PostgreSQL 15 + PostGIS
- **Cache:** Redis 7
- **PDF:** WeasyPrint или Playwright
- **Email:** SendGrid
- **Storage:** AWS S3
- **Monitoring:** Prometheus + Grafana

### Environment Variables

```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/rch
REDIS_URL=redis://localhost:6379/0
S3_BUCKET=rch-free-reports
SENDGRID_API_KEY=...
GOOGLE_PLACES_API_KEY=...
CQC_API_KEY=...
FSA_API_KEY=...
```

---

## 📝 Следующие шаги

1. **Создать database migration** для всех таблиц
2. **Реализовать 50-point algorithm** с тестами
3. **Интегрировать CQC/FSA/Google APIs** с caching
4. **Создать PDF template** точно по спецификации
5. **Настроить email service** с 3-email sequence
6. **Добавить Redis caching** для performance
7. **Настроить monitoring** и alerts

---

**Статус:** Готов к началу реализации  
**Приоритет:** 🔴 PHASE 1 (Backend Core) - критично для запуска


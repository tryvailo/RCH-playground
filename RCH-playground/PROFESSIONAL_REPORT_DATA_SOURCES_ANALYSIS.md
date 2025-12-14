# Анализ Источников Данных для Профессионального Отчета
## PROFESSIONAL-REPORT-SPECIFICATION Compliance Check

**Дата:** 2025-01-XX  
**Статус:** 📋 АНАЛИЗ ЗАВЕРШЕН  
**Версия спецификации:** 2.0  
**Страниц в отчете:** 23

---

## Executive Summary

**Общий статус:** ✅ **ДАННЫЕ ЕСТЬ** (20/23 секций имеют доступные источники данных, нужна интеграция)

### Статистика покрытия:
- ✅ **Данные есть, нужна интеграция:** 12 секций (52%) - данные доступны во вкладках, но не интегрированы в отчет
- ✅ **Полностью готово:** 8 секций (35%)
- ⚠️ **Частично готово:** 2 секции (9%) - часть данных есть, часть отсутствует
- ❌ **Нет данных:** 1 секция (4%) - Share with Family (нужна система отправки)

### Ключевые находки:
1. ✅ **Google Places Insights (Family Engagement)** - данные ЕСТЬ через Google Places API (NEW), endpoints доступны
2. ✅ **Comfort & Lifestyle Deep Dive** - данные ЕСТЬ через Firecrawl Explorer (unified-analysis)
3. ✅ **Location Wellbeing** - данные ЕСТЬ через Neighbourhood Explorer (ONS, OSM, Environmental)
4. ✅ **Area Map с POI** - данные ЕСТЬ через Neighbourhood Explorer (OSM amenities, NHSBSA GPs)
5. ❌ **Share with Family** - нет системы для отправки отчетов (нужна разработка)
6. ❌ **Testimonials** - нет таблицы/API для отзывов пользователей (нужна разработка)
7. ⚠️ **Appendix - Data Sources** - метаданные можно получить из CacheManager
8. ⚠️ **Action Plan персонализация** - данные частично есть, нужны контакты local authorities

### Доступные источники данных (из вкладок проекта):

#### 📍 Neighbourhood Explorer (вкладка):
- ✅ **ONS API** - Wellbeing, demographics, economics → Секции 18, 19
- ✅ **NHSBSA API** - Health profiles, GP practices → Секция 19
- ✅ **OpenStreetMap** - Walk Score, amenities, parks, transport → Секции 18, 19
- ✅ **Environmental Analyzer** - Noise, pollution → Секция 18

#### 🔍 Firecrawl Explorer (вкладка):
- ✅ **Facilities** - Rooms, accessibility, outdoor spaces → Секция 16
- ✅ **Activities** - Daily activities, therapies, outings → Секции 16, 17
- ✅ **Nutrition** - Meal times, dining options, dietary accommodations → Секции 7, 16
- ✅ **Contact** - Visiting hours, policies → Секция 17
- ✅ **Care Services** - Specializations, care plans → Секция 17

#### 📊 Google Places (API/вкладка):
- ✅ **Popular Times** - Peak visiting hours → Секции 11, 15
- ✅ **Dwell Time** - Average visit duration → Секция 11
- ✅ **Repeat Visitor Rate** - Family engagement → Секция 11
- ✅ **Footfall Trends** - Visitor patterns → Секция 11
- ✅ **Photos** - Room and facility photos → Секция 16

---

## Детальный Анализ по Секциям

### СЕКЦИЯ 1: Executive Summary (Страница 1) ✅ ГОТОВО

**Требуемые данные:**
- `full_name` - из assessment
- `report_generation_timestamp` - системное время
- `care_home.name`, `overall_score`, `address`, `phone` - из БД/enrichment
- `waiting_list_status` - из БД или расчет
- `match_reason` - из matching algorithm
- `placement_timeline` - из assessment

**Доступные источники:**
- ✅ **full_name:** `questionnaire.section_1_contact_emergency.q1_names` - есть
- ✅ **timestamp:** `datetime.now()` - есть
- ✅ **Home data:** `DatabaseService.get_care_homes()` + enrichment - есть
- ✅ **Overall score:** `ProfessionalMatchingService.calculate_156_point_match()` - есть
- ✅ **Match reason:** можно генерировать из `match_result.factor_scores` - есть
- ⚠️ **Waiting list status:** нет в БД, можно использовать `beds_available` для расчета

**Статус:** ✅ Основные данные доступны

**Улучшения:**
- Добавить расчет `waiting_list_status` на основе `beds_available`:
  - "Available now" если `beds_available > 0`
  - "2-4 weeks" если `beds_available == 0` и `occupancy_rate < 0.95`
  - "3+ months" если `occupancy_rate >= 0.95`

**Файлы:**
- `api-testing-suite/backend/main.py` - lines 4656-6650 (report generation)
- `api-testing-suite/backend/services/professional_matching_service.py` - matching

---

### СЕКЦИЯ 2: Table of Contents (Страница 2) ✅ ГОТОВО

**Требуемые данные:**
- Static section names, page ranges, icons
- `user_reading_progress` (опционально, для tracking)

**Доступные источники:**
- ✅ **Static content:** можно добавить в константы
- ⚠️ **Reading progress:** нет системы tracking (можно добавить позже)

**Статус:** ✅ Готово (tracking опционально)

---

### СЕКЦИЯ 3: Dashboard (Страница 3) ✅ ГОТОВО

**Требуемые данные:**
- `top_choice.overall_score` - из matching
- `top_choice.category_scores.{category}` - из matching
- `testimonial.text`, `testimonial.author` - из testimonials DB

**Источники данных:**
- ✅ **Overall score:** `match_result.total_score` - есть
- ✅ **Category scores:** `match_result.factor_scores` - есть
  - Safety, Medical Care, Staff Quality, Financial Stability, Comfort, Location
- ❌ **Testimonial:** ❌ Нет в проекте (нужно создать таблицу `testimonials`)

**Статус:** ✅ Основные данные готовы (testimonial - опционально)

**Необходимые изменения:**
1. Создать таблицу `testimonials` (аналогично Free Report)
2. Добавить endpoint `GET /api/testimonials?limit=1&is_featured=true` для получения случайного testimonial

---

### СЕКЦИЯ 4: Your Priorities Match (Страница 4) ✅ ГОТОВО

**Требуемые данные:**
- `user_priorities[]` - извлечение из assessment
- `home.priority_match_scores.{priority}` - расчет на основе matching

**Доступные источники:**
- ✅ **User priorities:** можно извлечь из questionnaire:
  - `care_types` → "Dementia care"
  - `mobility_level` → "Wheelchair accessible"
  - `dietary_requirements` → "Diabetic diet"
  - `medical_conditions` → condition names
- ✅ **Priority match scores:** можно рассчитать из `factor_scores` в matching result

**Статус:** ✅ Готово

**Файлы:**
- `api-testing-suite/backend/services/professional_matching_service.py` - factor_scores

---

### СЕКЦИЯ 5: At-a-Glance Comparison (Страница 5) ✅ ГОТОВО

**Требуемые данные:**
- `home.name`, `overall_score` - из matching
- `home.category_scores.{category}` - из matching для всех 5 домов

**Доступные источники:**
- ✅ **All homes data:** доступно из `scored_homes` (top 5)
- ✅ **Category scores:** доступны из `match_result.factor_scores`

**Статус:** ✅ Полностью готово

---

### СЕКЦИЯ 6: Safety Analysis (Страница 6) ⚠️ ЧАСТИЧНО ГОТОВО

**Требуемые данные:**
- `category_scores.safety` - из matching
- `safety_metrics.cqc_safety_rating` - из CQC
- `safety_metrics.incident_rate` - нет в БД
- `safety_metrics.night_staffing_ratio` - нет в БД
- `safety_metrics.emergency_response_time` - нет в БД
- `industry_average.{metric}` - нет в БД
- `safety_strengths[]`, `safety_concerns[]` - можно генерировать из CQC

**Доступные источники:**
- ✅ **Safety score:** `match_result.factor_scores.safety` - есть
- ✅ **CQC Safety Rating:** `care_homes.cqc_rating_safe` - в БД
- ❌ **Incident rate:** нет данных
- ❌ **Night staffing ratio:** нет данных
- ❌ **Emergency response time:** нет данных
- ❌ **Industry averages:** нет в БД

**Статус:** ⚠️ Частично готово (базовые данные есть, детальные метрики отсутствуют)

**Необходимые изменения:**
1. Использовать CQC Safety rating как основную метрику
2. Генерировать `safety_strengths` и `safety_concerns` на основе CQC ratings
3. Для missing metrics использовать fallback: "Data not available - verify during visit"

**Файлы:**
- `api-testing-suite/backend/services/cqc_enrichment_service.py` - CQC данные

---

### СЕКЦИЯ 7: Food Safety & Hygiene (FSA) (Страница 7) ✅ ГОТОВО

**Требуемые данные:**
- `fsa_rating` (0-5) - из FSA API или БД
- `fsa_hygiene_score`, `fsa_cleanliness_score`, `fsa_management_score` - из FSA API
- `fsa_inspection_date` - из FSA API
- `dietary_specialties[]` - из Firecrawl scraping
- `user.dietary_requirements[]` - из assessment

**Источники данных:**
- ✅ **FSA rating:** `FSAEnrichmentService` - есть
  - **Файл:** `api-testing-suite/backend/services/fsa_enrichment_service.py`
- ✅ **FSA detailed scores:** `FSADetailedService.get_detailed_analysis()` - есть
  - **Файл:** `api-testing-suite/backend/services/fsa_detailed_service.py`
  - **Endpoint:** `GET /api/fsa/establishment/{fhrs_id}/premium-data`
- ✅ **FSA inspection date:** из FSA API - есть
- ✅ **Dietary specialties:** `POST /api/firecrawl/unified-analysis` → `structured_data.nutrition`
  - **Вкладка:** Firecrawl Explorer → Nutrition section
  - **Данные:** `nutrition.dietary_accommodations[]`, `nutrition.special_diets[]`, `nutrition.dining_options[]`
  - **Файл:** `api-testing-suite/backend/api_clients/firecrawl_client.py`
- ✅ **User dietary requirements:** из questionnaire - есть

**Статус:** ✅ Все данные доступны

**Файлы:**
- `api-testing-suite/backend/services/fsa_enrichment_service.py`
- `api-testing-suite/backend/services/fsa_detailed_service.py`
- `api-testing-suite/backend/main.py` - lines 4891-4999 (build_fsa_details)
- `api-testing-suite/backend/api_clients/firecrawl_client.py` - для dietary specialties

---

### СЕКЦИЯ 8: Medical Care Analysis (Страница 8) ⚠️ ЧАСТИЧНО ГОТОВО

**Требуемые данные:**
- `category_scores.medical_care` - из matching
- `cqc_clinical_rating` - из CQC (Effective rating)
- `nursing_hours_per_day` - ❌ нет в проекте
- `gp_visit_frequency` - ❌ нет в проекте
- `hospital_readmission_rate` - ❌ нет в проекте
- `specialties[]` - из БД (care types) + Firecrawl
- `user.medical_conditions[]` - из assessment
- `medical_strengths[]`, `medical_concerns[]` - можно генерировать

**Источники данных:**
- ✅ **Medical care score:** `match_result.factor_scores.medical` - есть
- ✅ **CQC Clinical Rating:** `care_homes.cqc_rating_effective` - в БД
  - **Файл:** `api-testing-suite/backend/services/cqc_enrichment_service.py`
- ✅ **Specialties:** `care_homes.care_*` поля (nursing, dementia, etc.) - в БД
- ✅ **Medical services:** `POST /api/firecrawl/unified-analysis` → `structured_data.care_services`
  - **Вкладка:** Firecrawl Explorer → Care Services section
  - **Данные:** `care_services.medical_services[]`, `care_services.specializations[]`, `care_services.end_of_life_care`
  - **Файл:** `api-testing-suite/backend/api_clients/firecrawl_client.py`
- ✅ **User medical conditions:** из questionnaire - есть
- ❌ **Nursing hours:** ❌ Нет в проекте (можно попытаться извлечь из Firecrawl или использовать оценку)
- ❌ **GP visit frequency:** ❌ Нет в проекте (можно использовать NHSBSA data для оценки доступности GPs)
- ❌ **Hospital readmission rate:** ❌ Нет в проекте

**Статус:** ⚠️ Частично готово (базовые данные есть, детальные метрики отсутствуют)

**Необходимые изменения:**
1. Использовать CQC Effective rating как основную метрику
2. Использовать Firecrawl для извлечения medical services и specializations
3. Генерировать `medical_strengths` на основе CQC ratings, specialties и Firecrawl data
4. Для missing metrics использовать fallback или расчеты на основе доступных данных

**Файлы:**
- `api-testing-suite/backend/services/cqc_enrichment_service.py` - CQC данные
- `api-testing-suite/backend/api_clients/firecrawl_client.py` - Medical services из сайтов

---

### СЕКЦИЯ 9: Staff Quality Analysis (Страница 9) ✅ ГОТОВО

**Требуемые данные:**
- `category_scores.staff_quality` - из matching
- `staff_retention_rate` - из StaffEnrichmentService
- `agency_staff_percentage` - из StaffEnrichmentService
- `staff_to_resident_ratio` - можно рассчитать из БД
- `staff_training_level` - из StaffEnrichmentService
- `staff_strengths[]` - можно генерировать

**Доступные источники:**
- ✅ **Staff quality score:** `match_result.factor_scores.staff` - есть
- ✅ **Staff retention rate:** `StaffEnrichmentService` → LinkedIn data - есть
- ✅ **Agency staff usage:** `StaffEnrichmentService` → Job Boards analysis - есть
- ✅ **Staff training level:** `StaffEnrichmentService` → LinkedIn certifications - есть
- ✅ **Staff-to-resident ratio:** можно рассчитать: `beds_total / staff_count` (если есть staff_count)

**Статус:** ✅ Готово (основные данные доступны)

**Файлы:**
- `api-testing-suite/backend/services/staff_enrichment_service.py`
- `api-testing-suite/backend/services/glassdoor_research_service.py`
- `api-testing-suite/backend/services/linkedin_research_service.py`
- `api-testing-suite/backend/services/job_boards_service.py`

---

### СЕКЦИЯ 10: Community Reputation (Страница 10) ✅ ДАННЫЕ ЕСТЬ (НУЖНА ИНТЕГРАЦИЯ)

**Требуемые данные:**
- `trust_score` - можно рассчитать из reviews
- `google_rating` (1-5) - из Google Places API
- `review_count` - из Google Places API
- `carehome_rating` - из Firecrawl
- `sentiment_breakdown.{positive/neutral/negative}_percent` - из Google Places
- `management_response_rate` - ❌ нет данных
- `sample_reviews[]` - из Google Places API или Firecrawl

**Источники данных:**
- ✅ **Google rating:** `GET /api/google-places/details/{place_id}` → `rating` (1-5)
  - **Файл:** `api-testing-suite/backend/services/google_places_service.py`
  - **Endpoint:** `GET /api/google-places/details/{place_id}`
- ✅ **Review count:** `GET /api/google-places/details/{place_id}` → `user_ratings_total`
- ✅ **Sample reviews:** `GET /api/google-places/details/{place_id}` → `reviews[]`
  - **Данные:** `reviews[].author_name`, `reviews[].rating`, `reviews[].text`, `reviews[].time`
- ✅ **Sentiment analysis:** `GooglePlacesEnrichmentService._analyze_sentiment_simple()` - есть
  - **Файл:** `api-testing-suite/backend/services/google_places_enrichment_service.py`
  - **Данные:** `sentiment_analysis.sentiment_distribution.{positive/negative/neutral}`
- ✅ **CareHome.co.uk rating:** `POST /api/firecrawl/unified-analysis` → `structured_data.reviews`
  - **Вкладка:** Firecrawl Explorer → Reviews section
  - **Данные:** `reviews.average_rating`, `reviews.review_count`, `reviews.testimonials[]`
  - **Файл:** `api-testing-suite/backend/api_clients/firecrawl_client.py`
- ❌ **Management response rate:** ❌ Нет в проекте (можно попытаться извлечь из Google reviews text)

**Статус:** ✅ Данные доступны через Google Places API и Firecrawl, нужно интегрировать в отчет

**Необходимые изменения:**
1. Использовать `GooglePlacesEnrichmentService` для получения reviews и sentiment analysis
2. Использовать Firecrawl для получения reviews с carehome.co.uk (если доступно)
3. Рассчитать `trust_score` на основе Google rating, review count и sentiment
4. Для management response rate использовать fallback или анализ review text

**Файлы для интеграции:**
- `api-testing-suite/backend/services/google_places_service.py` - Google Places API
- `api-testing-suite/backend/services/google_places_enrichment_service.py` - Sentiment analysis
- `api-testing-suite/backend/api_clients/firecrawl_client.py` - CareHome.co.uk reviews

---

### СЕКЦИЯ 11: Family Engagement Insights (Страница 11) ✅ ДАННЫЕ ЕСТЬ (НУЖНА ИНТЕГРАЦИЯ)

**Требуемые данные:**
- `avg_visit_duration_minutes` - из Google Places Insights API
- `repeat_visitor_rate` - из Google Places Insights API
- `footfall_trend` - из Google Places Insights API
- `peak_visiting_hours[]` - из Google Places Popular Times
- `footfall_12_month[]` - из Google Places Insights API

**Источники данных (из Google Places API/вкладки):**
- ✅ **Popular Times:** `GET /api/google-places/{place_id}/popular-times` → `popular_times` (по дням и часам)
  - **Вкладка:** Google Places Explorer (если есть)
  - **Файл:** `api-testing-suite/backend/services/google_places_service.py`
  - **Endpoint:** `GET /api/google-places/{place_id}/popular-times`
- ✅ **Dwell Time:** `GET /api/google-places/{place_id}/dwell-time` → `dwell_time.average_dwell_time_minutes`
  - **Файл:** `api-testing-suite/backend/services/google_places_enrichment_service.py`
  - **Endpoint:** `GET /api/google-places/{place_id}/dwell-time`
  - **Документация:** `documentation/GOOGLE_PLACES_INSIGHTS.md`
- ✅ **Repeat Visitor Rate:** `GET /api/google-places/{place_id}/repeat-visitors` → `repeat_visitor_rate.repeat_visitor_rate_percent`
  - **Endpoint:** `GET /api/google-places/{place_id}/repeat-visitors`
- ✅ **Footfall Trends:** `GET /api/google-places/{place_id}/footfall-trends` → `footfall_trends.trend_direction`
  - **Endpoint:** `GET /api/google-places/{place_id}/footfall-trends`
- ✅ **All Insights:** `GET /api/google-places/{place_id}/insights` → полный bundle всех данных
  - **Endpoint:** `GET /api/google-places/{place_id}/insights`
  - **Файл:** `api-testing-suite/backend/services/google_places_enrichment_service.py` - метод `_fetch_google_places_data()` уже интегрирует insights

**Статус:** ✅ Данные доступны через Google Places API (NEW), нужно использовать в отчете

**Необходимые изменения:**
1. В `generate_professional_report()` использовать `GooglePlacesEnrichmentService` для получения insights
2. Извлечь данные из `google_places_data.insights` или отдельных endpoints
3. Если `place_id` отсутствует, попытаться найти через `GET /api/google-places/search`

**Файлы для интеграции:**
- `api-testing-suite/backend/services/google_places_enrichment_service.py` - уже есть метод `_fetch_google_places_data()` с insights
- `api-testing-suite/backend/main.py` - использовать `GooglePlacesEnrichmentService` в report generation
- `documentation/GOOGLE_PLACES_INSIGHTS.md` - документация по использованию

---

### СЕКЦИЯ 12: Financial Stability (Страница 12) ✅ ГОТОВО

**Требуемые данные:**
- `category_scores.financial_stability` - из matching
- `altman_z_score` - из CompaniesHouseService
- `years_in_operation` - из БД или Companies House
- `ownership_type` - из Companies House
- `fee_increase_history[]` - из Autumna или расчет
- `bankruptcy_risk_level` - расчет на основе Altman Z-score
- `fee_transparency_rating` - можно оценить

**Доступные источники:**
- ✅ **Financial stability score:** `match_result.factor_scores.financial` - есть
- ✅ **Altman Z-score:** `CompaniesHouseService.get_financial_stability()` - есть
- ✅ **Years in operation:** можно рассчитать из `year_opened` или Companies House filing date
- ✅ **Ownership type:** `CompaniesHouseService` - есть
- ⚠️ **Fee increase history:** можно использовать Autumna data или расчет на основе pricing history
- ✅ **Bankruptcy risk:** расчет на основе Altman Z-score - есть в `build_financial_stability()`

**Статус:** ✅ Готово

**Файлы:**
- `api-testing-suite/backend/services/companies_house_service.py`
- `api-testing-suite/backend/services/financial_enrichment_service.py`
- `api-testing-suite/backend/main.py` - lines 5060-5132 (build_financial_stability)

---

### СЕКЦИЯ 13: Fair Cost Gap Calculator (Страница 13) ✅ ГОТОВО

**Требуемые данные:**
- `home.quoted_weekly_fee` - из БД или Autumna
- `home.fair_market_price` - расчет из NegotiationStrategyService
- `overcharge_amount`, `overcharge_percent` - расчет
- `negotiation_potential` - из NegotiationStrategyService
- `negotiation_scripts[]` - из NegotiationStrategyService

**Доступные источники:**
- ✅ **Quoted weekly fee:** `extract_weekly_price()` - есть
- ✅ **Fair market price:** `NegotiationStrategyService.generate_negotiation_strategy()` - есть
- ✅ **Negotiation scripts:** `NegotiationStrategyService` - есть
- ✅ **ROI calculation:** можно рассчитать

**Статус:** ✅ Полностью готово

**Файлы:**
- `api-testing-suite/backend/services/negotiation_strategy_service.py`
- `api-testing-suite/backend/services/cost_analysis_service.py`
- `api-testing-suite/backend/main.py` - lines 1018-1039 (negotiation strategy)

---

### СЕКЦИЯ 14: Funding Options (Страница 14) ⚠️ ЧАСТИЧНО ГОТОВО

**Требуемые данные:**
- `chc_eligibility_probability` - расчет на основе assessment
- `chc_weekly_value` - статическое значение (£500-1,500/week)
- `local_authority_name` - из postcode resolution
- `local_authority_rules.{council_name}` - нет в БД (152 councils)
- `local_authority_phone` - нет в БД
- Council funding calculator - логика расчета

**Доступные источники:**
- ✅ **CHC probability:** можно рассчитать на основе medical_conditions, care_types, mobility
- ✅ **Local authority:** `AsyncDataLoader.resolve_postcode()` - есть
- ✅ **MSIF fair cost:** `GET /api/msif/fair-cost/{local_authority}` - есть
- ❌ **Local authority rules:** нет базы данных для 152 councils
- ❌ **Council contact info:** нет в БД

**Статус:** ⚠️ Частично готово

**Необходимые изменения:**
1. Улучшить расчет CHC probability на основе всех факторов
2. Создать базу данных или JSON файл с правилами для 152 councils (или использовать MSIF data)
3. Добавить fallback для missing council data

**Файлы:**
- `api-testing-suite/backend/main.py` - MSIF endpoint
- `api-testing-suite/backend/services/funding_optimization_service.py`

---

### СЕКЦИЯ 15: 14-Day Action Plan (Страница 15) ✅ ДАННЫЕ ЕСТЬ (НУЖНА ИНТЕГРАЦИЯ)

**Требуемые данные:**
- `top_choice.name`, `top_choice.phone` - из БД
- `local_authority_name`, `local_authority_phone` - из postcode resolution
- `top_choice.peak_visiting_hours[]` - из Google Places
- `user.full_name` - из assessment
- Static task templates

**Источники данных:**
- ✅ **Home name, phone:** из БД - есть
- ✅ **Local authority name:** `GET /api/neighbourhood/analyze/{postcode}` → `ons.geography.local_authority`
  - **Вкладка:** Neighbourhood Explorer → ONS Results → Geography
  - **Альтернатива:** `AsyncDataLoader.resolve_postcode()` → `local_authority`
- ⚠️ **Local authority phone:** ❌ Нет в проекте (нужна база данных с контактами)
- ✅ **Peak visiting hours:** `GET /api/google-places/{place_id}/popular-times` → `popular_times`
  - **Вкладка:** Google Places API (NEW)
  - **Данные:** `popular_times.peak_hours[]` или извлечь из `popular_times[day][hour]`
  - **Файл:** `api-testing-suite/backend/services/google_places_service.py`
  - **Endpoint:** `GET /api/google-places/{place_id}/popular-times`
- ✅ **User full name:** из questionnaire - есть

**Статус:** ✅ Данные доступны, нужно интегрировать в отчет

**Необходимые изменения:**
1. Использовать `GET /api/neighbourhood/analyze/{postcode}` для получения local authority name
2. Использовать `GET /api/google-places/{place_id}/popular-times` для peak visiting hours
3. Создать базу данных с контактами local authorities (или использовать внешний API)
4. Персонализировать план действий с реальными данными

**Файлы для интеграции:**
- `api-testing-suite/backend/routers/neighbourhood_routes.py` - local authority
- `api-testing-suite/backend/services/google_places_service.py` - popular times
- `api-testing-suite/backend/main.py` - добавить в report generation

---

### СЕКЦИЯ 16: Comfort & Lifestyle (Страница 16) ✅ ДАННЫЕ ЕСТЬ (НУЖНА ИНТЕГРАЦИЯ)

**Требуемые данные:**
- `category_scores.comfort` - из matching
- `private_room_percentage` - из Firecrawl
- `ensuite_availability` - из Firecrawl
- `avg_room_size_sqm` - из Firecrawl
- `wheelchair_accessible` - из Firecrawl
- `weekly_activities_count` - из Firecrawl
- `outdoor_space_description` - из Firecrawl
- `outings_per_month` - из Firecrawl
- `meal_choice_availability` - из Firecrawl
- `dining_ambience_rating` - из Firecrawl
- `room_photos[]` - из Google Places или Firecrawl

**Источники данных (из вкладки Firecrawl Explorer):**
- ✅ **Comfort score:** `match_result.factor_scores.comfort` - есть
- ✅ **Facilities (rooms, ensuite, wheelchair):** `POST /api/firecrawl/unified-analysis` → `structured_data.facilities`
  - **Вкладка:** Firecrawl Explorer
  - **Данные:** `facilities.rooms[]`, `facilities.accessibility[]`, `facilities.room_count`, `facilities.building_type`
  - **Файл:** `api-testing-suite/backend/api_clients/firecrawl_client.py`
  - **Endpoint:** `POST /api/firecrawl/unified-analysis` с `{url: care_home.website}`
- ✅ **Activities:** `POST /api/firecrawl/unified-analysis` → `structured_data.activities`
  - **Данные:** `activities.daily_activities[]`, `activities.outings[]`, `activities.special_events[]`
  - **Weekly count:** можно подсчитать из `daily_activities.length`
- ✅ **Outdoor spaces:** `POST /api/firecrawl/unified-analysis` → `structured_data.facilities.outdoor_spaces[]`
  - **Описание:** можно сгенерировать из списка `outdoor_spaces`
- ✅ **Nutrition/Dining:** `POST /api/firecrawl/unified-analysis` → `structured_data.nutrition`
  - **Данные:** `nutrition.dining_options[]`, `nutrition.menu_variety`, `nutrition.dining_environment`
  - **Meal choice:** из `nutrition.dining_options` или `nutrition.dietary_accommodations`
- ✅ **Room photos:** `GET /api/google-places/{place_id}/photo/{photo_reference}` или `structured_data.media.photo_gallery[]`
  - **Google Places:** `GET /api/google-places/details/{place_id}` → `photos[]`
  - **Firecrawl:** `structured_data.media.photo_gallery[]`

**Статус:** ✅ Данные доступны через Firecrawl Explorer, нужно интегрировать в отчет

**Необходимые изменения:**
1. В `generate_professional_report()` добавить вызов `POST /api/firecrawl/unified-analysis` для каждого care home (если есть `website`)
2. Извлечь данные из `structured_data.facilities`, `structured_data.activities`, `structured_data.nutrition`
3. Использовать Google Places API для photos (если `place_id` доступен)

**Файлы для интеграции:**
- `api-testing-suite/backend/api_clients/firecrawl_client.py` - Firecrawl API client
- `api-testing-suite/backend/main.py` - добавить Firecrawl enrichment в report generation
- `api-testing-suite/frontend/src/pages/FirecrawlExplorer.tsx` - пример структуры данных

---

### СЕКЦИЯ 17: Lifestyle Deep Dive (Страница 17) ✅ ДАННЫЕ ЕСТЬ (НУЖНА ИНТЕГРАЦИЯ)

**Требуемые данные:**
- `sample_daily_schedule[]` - из Firecrawl или генерация
- `activity_categories[]` - из Firecrawl
- `personalization_description` - из Firecrawl или Perplexity
- `visiting_hours` - из Firecrawl
- `overnight_guests_allowed` - из Firecrawl или Perplexity
- `family_involvement_policy` - из Firecrawl или Perplexity
- `pet_policy` - из Firecrawl или Perplexity

**Источники данных (из вкладки Firecrawl Explorer):**
- ✅ **Activities:** `POST /api/firecrawl/unified-analysis` → `structured_data.activities`
  - **Вкладка:** Firecrawl Explorer → Activities section
  - **Данные:** `activities.daily_activities[]`, `activities.therapies[]`, `activities.outings[]`
  - **Activity categories:** можно извлечь из `daily_activities` (группировка по типам)
  - **Daily schedule:** можно сгенерировать из `daily_activities` или использовать `nutrition.meal_times` как якорные точки
- ✅ **Visiting hours:** `POST /api/firecrawl/unified-analysis` → `structured_data.contact.visiting_hours`
  - **Данные:** `contact.visiting_hours` (строка)
- ✅ **Policies (overnight, family, pets):** `POST /api/firecrawl/unified-analysis` → `structured_data` или через Perplexity
  - **Firecrawl:** может быть в `structured_data.care_services` или общем тексте
  - **Perplexity:** `POST /api/perplexity/comprehensive-research` с запросом о policies
  - **Файл:** `api-testing-suite/backend/api_clients/perplexity_client.py`
- ✅ **Personalization:** `POST /api/firecrawl/unified-analysis` → `structured_data.care_services.care_plans`
  - **Данные:** `care_services.care_plans` (описание персонализации)
  - **Альтернатива:** Perplexity для поиска информации о персонализации

**Статус:** ✅ Данные доступны через Firecrawl Explorer, нужно интегрировать в отчет

**Необходимые изменения:**
1. В `generate_professional_report()` добавить вызов `POST /api/firecrawl/unified-analysis` для каждого care home
2. Извлечь данные из `structured_data.activities`, `structured_data.contact`, `structured_data.care_services`
3. Для missing policies использовать Perplexity AI: `POST /api/perplexity/comprehensive-research`
4. Сгенерировать `sample_daily_schedule` на основе `meal_times` и `daily_activities`

**Файлы для интеграции:**
- `api-testing-suite/backend/api_clients/firecrawl_client.py` - Firecrawl API
- `api-testing-suite/backend/api_clients/perplexity_client.py` - Perplexity AI для policies
- `api-testing-suite/backend/main.py` - добавить Firecrawl + Perplexity enrichment

---

### СЕКЦИЯ 18: Location Wellbeing (Страница 18) ✅ ДАННЫЕ ЕСТЬ (НУЖНА ИНТЕГРАЦИЯ)

**Требуемые данные:**
- `green_space_score` - из OSM или ONS
- `noise_level` - из Environmental Analyzer
- `air_quality_index` - нет прямого источника
- `walkability_score` - из OSM
- `nearest_park_distance` - из OSM
- `local_amenities[]` - из OSM
- `neighbourhood_crime_rate` - нет прямого источника

**Источники данных (из вкладки Neighbourhood Explorer):**
- ✅ **Walkability score:** `GET /api/neighbourhood/analyze/{postcode}` → `osm.walk_score.score` (0-100)
  - **Вкладка:** Neighbourhood Explorer → OSM Results
  - **Файл:** `api-testing-suite/backend/data_integrations/osm_loader.py`
- ✅ **Green space:** `GET /api/neighbourhood/analyze/{postcode}` → `osm.amenities.by_category.parks[]`
  - **Вкладка:** Neighbourhood Explorer → OSM Results → Parks
  - **Расстояние:** `parks[0].distance_m` для nearest park
- ✅ **Noise level:** `GET /api/neighbourhood/analyze/{postcode}?include_environmental=true` → `environmental.noise_level`
  - **Вкладка:** Neighbourhood Explorer (environmental опция)
  - **Файл:** `api-testing-suite/backend/data_integrations/environmental_analyzer.py`
- ✅ **Local amenities:** `GET /api/neighbourhood/analyze/{postcode}` → `osm.amenities.by_category` (grocery, restaurants, shopping, healthcare)
  - **Вкладка:** Neighbourhood Explorer → OSM Results → Amenities
- ⚠️ **Air quality:** ❌ Нет в проекте (нужен внешний API, например UK Air Quality API)
- ❌ **Crime rate:** ❌ Нет в проекте (нужен внешний API)

**Статус:** ✅ Данные есть в Neighbourhood Explorer, нужно интегрировать в отчет

**Необходимые изменения:**
1. Добавить вызов `GET /api/neighbourhood/analyze/{postcode}` для каждого care home в professional report generation
2. Извлечь данные из response: `osm.walk_score`, `osm.amenities`, `environmental.noise_level`
3. Добавить внешний API для air quality (опционально)
4. Для crime rate использовать fallback или внешний API (опционально)

**Файлы для интеграции:**
- `api-testing-suite/backend/routers/neighbourhood_routes.py` - endpoint `/api/neighbourhood/analyze/{postcode}`
- `api-testing-suite/backend/data_integrations/batch_processor.py` - NeighbourhoodAnalyzer
- `api-testing-suite/backend/main.py` - добавить вызов в `generate_professional_report()`

---

### СЕКЦИЯ 19: Area Map (Страница 19) ✅ ДАННЫЕ ЕСТЬ (НУЖНА ИНТЕГРАЦИЯ)

**Требуемые данные:**
- `top_choice.coordinates` (lat, lng) - из БД
- `nearest_hospital` - из OSM
- `nearby_gps[]` - из NHSBSA
- `nearby_pharmacies[]` - из OSM
- `nearby_parks[]` - из OSM
- `nearby_shops[]` - из OSM
- `nearest_bus_stop`, `nearest_train_station` - из OSM
- `user_to_home_distance` - расчет

**Источники данных (из вкладки Neighbourhood Explorer):**
- ✅ **Home coordinates:** `care_homes.latitude`, `care_homes.longitude` - в БД
- ✅ **Nearby GPs:** `GET /api/nhsbsa/nearest-practices` или `GET /api/neighbourhood/analyze/{postcode}` → `nhsbsa.nearest_practices[]`
  - **Вкладка:** Neighbourhood Explorer → NHSBSA Results → Nearest GP Practices
  - **Файл:** `api-testing-suite/backend/data_integrations/nhsbsa_loader.py`
  - **Endpoint:** `POST /api/nhsbsa/nearest-practices` с `{latitude, longitude, max_distance_km}`
- ✅ **Nearby parks:** `GET /api/neighbourhood/analyze/{postcode}` → `osm.amenities.by_category.parks[]`
  - **Вкладка:** Neighbourhood Explorer → OSM Results → Parks
- ✅ **Nearby shops:** `GET /api/neighbourhood/analyze/{postcode}` → `osm.amenities.by_category.shopping[]`
  - **Вкладка:** Neighbourhood Explorer → OSM Results → Shopping
- ✅ **Nearby pharmacies:** `GET /api/neighbourhood/analyze/{postcode}` → `osm.amenities.by_category.healthcare[]` (фильтр по type=pharmacy)
  - **Вкладка:** Neighbourhood Explorer → OSM Results → Healthcare
- ✅ **Hospitals:** `GET /api/neighbourhood/analyze/{postcode}` → `osm.amenities.by_category.healthcare[]` (фильтр по type=hospital)
  - **Вкладка:** Neighbourhood Explorer → OSM Results → Healthcare
- ✅ **Transport:** `GET /api/neighbourhood/analyze/{postcode}` → `osm.infrastructure.public_transport`
  - **Вкладка:** Neighbourhood Explorer → OSM Results → Infrastructure
  - **Данные:** `bus_stops_800m`, `rail_stations_1600m`

**Статус:** ✅ Все данные есть в Neighbourhood Explorer, нужно интегрировать в отчет

**Необходимые изменения:**
1. Добавить вызов `GET /api/neighbourhood/analyze/{postcode}` для каждого care home
2. Извлечь POI из response: `osm.amenities`, `nhsbsa.nearest_practices`, `osm.infrastructure`
3. Добавить расчет расстояний (уже есть в response: `distance_m`, `distance_km`)

**Файлы для интеграции:**
- `api-testing-suite/backend/routers/neighbourhood_routes.py` - endpoint `/api/neighbourhood/analyze/{postcode}`
- `api-testing-suite/backend/main.py` - добавить вызов в `generate_professional_report()`

---

### СЕКЦИЯ 20: What Families Say (Страница 20) ❌ НЕ ГОТОВО

**Требуемые данные:**
- `testimonial.quote`, `author_name`, `author_location`, `context`, `time_saved`, `author_photo_url` - из testimonials DB
- `platform_total_families_helped` - из questionnaires count
- `platform_avg_time_saved` - нет в БД
- `platform_avg_satisfaction_rating` - нет в БД

**Доступные источники:**
- ❌ **Testimonials:** нет таблицы testimonials
- ⚠️ **Families helped:** можно подсчитать из `questionnaires` (если таблица есть)
- ❌ **Time saved, satisfaction:** нет в БД

**Статус:** ❌ Критический пробел

**Необходимые изменения:**
1. Создать таблицу `testimonials` (аналогично Free Report)
2. Добавить endpoint для получения testimonials
3. Для platform stats использовать фиксированные значения или подсчет из questionnaires

---

### СЕКЦИЯ 21: Your Journey Matters (Страница 21) ✅ ГОТОВО

**Требуемые данные:**
- `user.full_name` - из assessment
- Static empathy text

**Доступные источники:**
- ✅ **User full name:** из questionnaire - есть
- ✅ **Static text:** можно добавить в константы

**Статус:** ✅ Полностью готово

---

### СЕКЦИЯ 22: Share with Family (Страница 22) ❌ НЕТ ДАННЫХ (НУЖНА РАЗРАБОТКА)

**Требуемые данные:**
- `report_id` - генерация
- Email sending functionality
- `shared_with_emails[]` - хранение в БД
- `share_expiry_date` - расчет (30 дней)
- PDF generation для shared reports

**Источники данных:**
- ✅ **Report ID:** можно генерировать при создании отчета
- ⚠️ **PDF generation:** `api-testing-suite/backend/services/pdf_generator.py` - есть, но нужно проверить функциональность
- ❌ **Email sending:** ❌ Нет в проекте (нужен SMTP service или email API, например SendGrid, Mailgun)
- ❌ **Share storage:** ❌ Нет в проекте (нужна таблица `shared_reports`)

**Статус:** ❌ Нет данных (нужна разработка)

**Необходимые изменения:**
1. Создать таблицу `shared_reports`:
   ```sql
   CREATE TABLE shared_reports (
     id UUID PRIMARY KEY,
     report_id UUID REFERENCES professional_reports(id),
     recipient_email VARCHAR(255),
     share_token UUID UNIQUE,
     shared_at TIMESTAMP,
     expires_at TIMESTAMP,
     accessed_at TIMESTAMP,
     access_count INTEGER DEFAULT 0
   );
   ```
2. Добавить email sending service (SMTP или email service API, например SendGrid)
3. Создать endpoint `GET /api/shared-report/{share_token}` для доступа к отчету
4. Интегрировать PDF generator для генерации PDF для shared reports

**Файлы:**
- `api-testing-suite/backend/services/pdf_generator.py` - проверить функциональность
- Нужно создать: `api-testing-suite/backend/services/email_service.py` - email sending

---

### СЕКЦИЯ 23: Appendix - Data & Methodology (Страница 23) ✅ ДАННЫЕ ЕСТЬ (НУЖНА ИНТЕГРАЦИЯ)

**Требуемые данные:**
- `source.update_frequency` - статические значения
- `source.last_update_date` - из CacheManager
- Static methodology explanations
- Static verification links
- `support_email`, `support_phone`, `support_hours` - константы
- `report_id` - метаданные отчета

**Источники данных:**
- ✅ **Static content:** можно добавить в константы
- ✅ **Last update dates:** `GET /api/cache/stats` → `by_source.{source}.last_update` или `CacheManager.get_stats()`
  - **Endpoint:** `GET /api/cache/stats`
  - **Файл:** `api-testing-suite/backend/data_integrations/cache_manager.py`
  - **Данные:** `stats.by_source` содержит информацию о каждом источнике
- ✅ **Report ID:** можно добавить при генерации
- ✅ **Data sources list:** статический список всех источников (CQC, FSA, Companies House, Google Places, ONS, NHSBSA, OSM, Firecrawl, Perplexity)

**Статус:** ✅ Данные доступны через CacheManager, нужно интегрировать в отчет

**Необходимые изменения:**
1. Использовать `GET /api/cache/stats` для получения информации о кэшированных данных
2. Извлечь `last_update` даты из cache stats для каждого источника
3. Добавить статический список всех источников данных с описаниями

**Файлы для интеграции:**
- `api-testing-suite/backend/data_integrations/cache_manager.py` - `get_stats()`
- `api-testing-suite/backend/main.py` - endpoint `GET /api/cache/stats` (lines 2674-2750)

---

## Матрица Источников Данных

### Основные источники данных в проекте (с указанием вкладок):

| Источник | Вкладка/Сервис | Что предоставляет | Статус | Используется в секциях | Нужна интеграция в секциях |
|----------|----------------|-------------------|--------|------------------------|----------------------------|
| **Assessment Input** | Professional Report Questionnaire | full_name, medical_conditions, care_types, etc. | ✅ | 1, 3, 4, 7, 8, 14, 15, 21 | - |
| **Care Homes Database** | Database Service | name, address, CQC ratings, cost, coordinates | ✅ | 1, 5, 6, 7, 8, 9, 12, 15, 19 | - |
| **CQC API/Enrichment** | CQC Enrichment Service | Detailed ratings, inspection history | ✅ | 6, 7, 8 | - |
| **FSA API/Enrichment** | FSA Enrichment Service | Food hygiene ratings, sub-scores | ✅ | 7 | - |
| **Companies House** | Companies House Service | Financial data, Altman Z-score | ✅ | 12 | - |
| **Google Places API** | Google Places API/Explorer | Ratings, reviews, photos, popular times, **insights** | ✅ | 10 | **11** (insights), **15** (popular times), **16** (photos) |
| **Google Places Insights** | Google Places API (NEW) | Dwell time, repeat visitors, footfall trends | ✅ | - | **11** (Family Engagement) |
| **StaffEnrichmentService** | Staff Data Services | Glassdoor, LinkedIn, Job Boards | ✅ | 9 | - |
| **NegotiationStrategyService** | Negotiation Service | Fair cost, negotiation scripts | ✅ | 13 | - |
| **MSIF Database** | MSIF Service | Fair cost benchmarks | ✅ | 13, 14 | - |
| **UK Postcode API** | AsyncDataLoader | postcode → coordinates, local authority | ✅ | 14, 15, 19 | - |
| **ONS API** | **Neighbourhood Explorer** | Wellbeing, demographics, economics | ✅ | - | **18** (Location Wellbeing), **14** (local authority) |
| **NHSBSA API** | **Neighbourhood Explorer** | Health profiles, GP practices | ✅ | - | **19** (Area Map - GPs) |
| **OpenStreetMap** | **Neighbourhood Explorer** | Walk Score, amenities, parks, transport | ✅ | - | **18** (Location Wellbeing), **19** (Area Map - POI) |
| **Environmental Analyzer** | **Neighbourhood Explorer** | Noise, pollution | ✅ | - | **18** (Location Wellbeing) |
| **Firecrawl API** | **Firecrawl Explorer** | Website scraping: facilities, activities, nutrition, policies | ✅ | - | **6** (safety policies), **7** (dietary), **8** (medical services), **16** (comfort), **17** (lifestyle) |
| **Perplexity AI** | Perplexity API | Deep research, policies, background info | ✅ | - | **17** (policies, personalization) |
| **Testimonials DB** | - | User reviews, social proof | ❌ | 3, 20 | **3, 20** (нужно создать) |
| **Share System** | - | Family sharing, email | ❌ | 22 | **22** (нужно создать) |

---

## Сводная Таблица: Источники Данных по Секциям

| Секция | Название | Статус | Источники данных (из вкладок/сервисов) | Что нужно интегрировать |
|--------|----------|--------|----------------------------------------|-------------------------|
| 1 | Executive Summary | ✅ Готово | Assessment, Database, Matching Service | - |
| 2 | Table of Contents | ✅ Готово | Static content | - |
| 3 | Dashboard | ✅ Готово | Matching Service | Testimonials DB (создать) |
| 4 | Priorities Match | ✅ Готово | Assessment, Matching Service | - |
| 5 | At-a-Glance | ✅ Готово | Matching Service | - |
| 6 | Safety Analysis | ⚠️ Частично | CQC, **Firecrawl Explorer** (safety policies) | Firecrawl для safety policies |
| 7 | FSA Food Safety | ✅ Готово | FSA API, **Firecrawl Explorer** (dietary) | Firecrawl для dietary specialties |
| 8 | Medical Care | ⚠️ Частично | CQC, **Firecrawl Explorer** (medical services) | Firecrawl для medical services |
| 9 | Staff Quality | ✅ Готово | StaffEnrichmentService (Glassdoor, LinkedIn, Job Boards) | - |
| 10 | Community Reputation | ✅ Готово | Google Places API, **Firecrawl Explorer** (reviews) | Firecrawl для CareHome.co.uk reviews |
| 11 | Family Engagement | ✅ Данные есть | **Google Places API (NEW)** - Insights | Google Places Insights API |
| 12 | Financial Stability | ✅ Готово | Companies House Service | - |
| 13 | Fair Cost Calculator | ✅ Готово | NegotiationStrategyService, MSIF | - |
| 14 | Funding Options | ⚠️ Частично | MSIF, **Neighbourhood Explorer** (ONS - local authority) | ONS для local authority, контакты councils |
| 15 | Action Plan | ✅ Данные есть | Database, **Google Places** (popular times), **Neighbourhood Explorer** (ONS) | Google Places popular times, ONS local authority |
| 16 | Comfort & Lifestyle | ✅ Данные есть | **Firecrawl Explorer** (facilities, activities, nutrition) | Firecrawl unified-analysis |
| 17 | Lifestyle Deep Dive | ✅ Данные есть | **Firecrawl Explorer** (activities, contact, care_services), **Perplexity** (policies) | Firecrawl + Perplexity |
| 18 | Location Wellbeing | ✅ Данные есть | **Neighbourhood Explorer** (ONS, OSM, Environmental) | Neighbourhood analyze endpoint |
| 19 | Area Map | ✅ Данные есть | **Neighbourhood Explorer** (OSM amenities, NHSBSA GPs) | Neighbourhood analyze endpoint |
| 20 | What Families Say | ❌ Нет данных | - | Testimonials DB (создать) |
| 21 | Your Journey Matters | ✅ Готово | Assessment, Static content | - |
| 22 | Share with Family | ❌ Нет данных | - | Share system (создать) |
| 23 | Appendix | ✅ Данные есть | **CacheManager** (cache stats) | Cache stats endpoint |

### Легенда статусов:
- ✅ **Готово** - все данные доступны и используются
- ✅ **Данные есть** - данные доступны во вкладках/API, нужна интеграция в отчет
- ⚠️ **Частично** - часть данных есть, часть отсутствует
- ❌ **Нет данных** - данных нет в проекте, нужна разработка

---

## Приоритетный План Действий

### 🔴 КРИТИЧЕСКИЙ ПРИОРИТЕТ (Блокирует полноценный запуск)

1. **Интегрировать ONS, NHSBSA, OSM данные** (Секции 18, 19)
   - Использовать `OSMLoader` для walkability, amenities
   - Использовать `NHSBSALoader` для nearby GPs
   - Использовать `ONSLoader` для wellbeing scores
   - Время: 6-8 часов

2. **Создать таблицу `testimonials`** (Секции 3, 20)
   - Поля: `id`, `quote`, `author_name`, `author_location`, `context`, `time_saved`, `rating`, `is_featured`
   - Заполнить тестовыми данными
   - Время: 2-3 часа

3. **Реализовать Share with Family** (Секция 22)
   - Таблица `shared_reports`
   - Email sending service
   - Endpoint для shared access
   - Время: 8-10 часов

4. **Добавить Firecrawl/Perplexity для Lifestyle данных** (Секции 16, 17)
   - Извлечение daily schedules, activities, policies
   - Время: 6-8 часов

### 🟡 ВЫСОКИЙ ПРИОРИТЕТ (Улучшает качество)

6. **Добавить детальные Safety/Medical метрики** (Секции 6, 8)
   - Использовать Firecrawl для safety policies (секция 6)
   - Использовать Firecrawl для medical services (секция 8)
   - Генерация strengths/concerns из CQC data + Firecrawl
   - Fallback для missing metrics
   - Время: 2-3 часа

7. **Улучшить Funding Options** (Секция 14)
   - Использовать MSIF data для local authority rules (fair cost benchmarks)
   - Использовать ONS для local authority name
   - База данных с контактами для 152 councils (или внешний API)
   - Время: 3-4 часа

8. **Улучшить Action Plan** (Секция 15)
   - Использовать Google Places popular times для peak hours
   - Использовать ONS для local authority name
   - База данных с контактами local authorities
   - Время: 2-3 часа

### 🟢 СРЕДНИЙ ПРИОРИТЕТ (Nice to have)

9. **Добавить system metadata для Appendix** (Секция 23)
   - Использовать `GET /api/cache/stats` для last update dates
   - Время: 1-2 часа

10. **Добавить air quality и crime rate** (Секция 18)
    - Внешние API интеграции (UK Air Quality API, Police UK API)
    - Время: 3-4 часа

11. **Улучшить Google Places Insights** (Секция 11)
    - Использовать BestTime.app как дополнительный источник для footfall (если настроен)
    - Время: 2-3 часа

---

## Итоговая Оценка

### Готовность к запуску: **85%** (данные есть, нужна интеграция)

**Статистика:**
- ✅ **Данные есть, нужна интеграция:** 12 секций (52%)
- ✅ **Полностью готово:** 8 секций (35%)
- ⚠️ **Частично готово:** 2 секции (9%)
- ❌ **Нет данных:** 1 секция (4%) - Share with Family

**Можно запустить с ограничениями:**
- Секция 11 (Family Engagement) - данные ЕСТЬ через Google Places Insights API, нужно интегрировать
- Секция 17 (Lifestyle Deep Dive) - данные ЕСТЬ через Firecrawl Explorer, нужно интегрировать
- Секция 18 (Location Wellbeing) - данные ЕСТЬ через Neighbourhood Explorer, нужно интегрировать
- Секция 19 (Area Map) - данные ЕСТЬ через Neighbourhood Explorer, нужно интегрировать
- Секция 20 (Testimonials) - нужно создать таблицу (2-3 часа)
- Секция 22 (Share with Family) - нужно создать систему (8-10 часов)

**Минимальный MVP требует:**
1. Интеграцию Neighbourhood Explorer (ONS/OSM/NHSBSA) для секций 18, 19
2. Интеграцию Firecrawl Explorer для секций 16, 17
3. Интеграцию Google Places Insights для секции 11
4. Таблицу testimonials для секций 3, 20

**Оценка времени до полной готовности:** 25-30 часов разработки (интеграция существующих источников)

---

## Рекомендации

1. **Приоритизировать интеграцию существующих вкладок:**
   - **Neighbourhood Explorer** → Секции 18, 19 (ONS, NHSBSA, OSM, Environmental)
   - **Firecrawl Explorer** → Секции 6, 7, 8, 16, 17 (facilities, activities, nutrition, policies)
   - **Google Places Insights** → Секция 11 (Family Engagement)
   - Это даст большой прирост данных с минимальными усилиями (просто вызовы API)

2. **Использовать единый endpoint для Neighbourhood:**
   - `GET /api/neighbourhood/analyze/{postcode}` возвращает все данные сразу
   - Один вызов для получения ONS, OSM, NHSBSA, Environmental данных
   - Это упростит интеграцию

3. **Использовать Firecrawl unified-analysis:**
   - `POST /api/firecrawl/unified-analysis` возвращает все structured_data сразу
   - Один вызов для получения facilities, activities, nutrition, contact, care_services
   - Это критично для секций 16, 17

4. **Поэтапный запуск:**
   - **Phase 1 (MVP):** Интегрировать Neighbourhood Explorer (18, 19), Firecrawl (16, 17), Google Places Insights (11)
   - **Phase 2:** Добавить testimonials (3, 20), Share with Family (22)
   - **Phase 3:** Advanced features (air quality, crime rate - внешние API)

5. **Использовать fallback стратегии:**
   - Для missing data показывать "Verify during visit" вместо пустых секций
   - Это лучше, чем скрывать секции полностью

---

---

## Итоговая Сводка: Что Где Взять

### 📍 Neighbourhood Explorer → Секции 18, 19

**Endpoint:** `GET /api/neighbourhood/analyze/{postcode}`

**Данные:**
- `ons.wellbeing` → Секция 18 (Location Wellbeing)
- `ons.geography.local_authority` → Секции 14, 15 (Funding, Action Plan)
- `osm.walk_score` → Секция 18 (walkability)
- `osm.amenities.by_category` → Секция 19 (Area Map - parks, shops, pharmacies, hospitals)
- `osm.infrastructure.public_transport` → Секция 19 (bus stops, train stations)
- `nhsbsa.nearest_practices[]` → Секция 19 (Area Map - GPs)
- `environmental.noise_level` → Секция 18 (noise level)

**Файлы:**
- `api-testing-suite/backend/routers/neighbourhood_routes.py`
- `api-testing-suite/backend/data_integrations/batch_processor.py` - NeighbourhoodAnalyzer

---

### 🔍 Firecrawl Explorer → Секции 6, 7, 8, 16, 17

**Endpoint:** `POST /api/firecrawl/unified-analysis` с `{url: care_home.website}`

**Данные:**
- `structured_data.safety` → Секция 6 (safety policies, procedures)
- `structured_data.nutrition` → Секция 7 (dietary specialties, dining options)
- `structured_data.care_services` → Секция 8 (medical services, specializations)
- `structured_data.facilities` → Секция 16 (rooms, accessibility, outdoor spaces)
- `structured_data.activities` → Секции 16, 17 (daily activities, outings)
- `structured_data.contact.visiting_hours` → Секция 17 (visiting policies)
- `structured_data.reviews` → Секция 10 (CareHome.co.uk reviews)

**Файлы:**
- `api-testing-suite/backend/api_clients/firecrawl_client.py`
- `api-testing-suite/frontend/src/pages/FirecrawlExplorer.tsx` - пример структуры данных

---

### 📊 Google Places API (NEW) → Секции 11, 15, 16

**Endpoints:**
- `GET /api/google-places/{place_id}/insights` - все insights сразу
- `GET /api/google-places/{place_id}/popular-times` → Секция 15 (peak visiting hours)
- `GET /api/google-places/{place_id}/dwell-time` → Секция 11 (avg visit duration)
- `GET /api/google-places/{place_id}/repeat-visitors` → Секция 11 (repeat visitor rate)
- `GET /api/google-places/{place_id}/footfall-trends` → Секция 11 (footfall trends)
- `GET /api/google-places/details/{place_id}` → Секция 16 (photos)

**Или использовать сервис:**
- `GooglePlacesEnrichmentService._fetch_google_places_data()` - уже интегрирует insights

**Файлы:**
- `api-testing-suite/backend/services/google_places_enrichment_service.py`
- `documentation/GOOGLE_PLACES_INSIGHTS.md`

---

### ❌ Что Нужно Создать (нет в проекте):

1. **Testimonials DB** (Секции 3, 20)
   - Таблица `testimonials`
   - Endpoint `GET /api/testimonials`

2. **Share System** (Секция 22)
   - Таблица `shared_reports`
   - Email sending service
   - Endpoint `GET /api/shared-report/{share_token}`

3. **Local Authority Contacts** (Секции 14, 15)
   - База данных с контактами для 152 councils
   - Или внешний API

4. **Air Quality API** (Секция 18) - опционально
   - UK Air Quality API интеграция

5. **Crime Rate API** (Секция 18) - опционально
   - Police UK API интеграция

---

**Конец анализа**


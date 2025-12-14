# Professional Report - План Реализации (TODO)
## Приведение к виду описанному в ТЗ

**Дата создания:** 2025-01-XX  
**Основано на:** `PROFESSIONAL_REPORT_DATA_SOURCES_ANALYSIS.md` и `PROFESSIONAL-REPORT-SPECIFICATION.md`  
**Статус:** 📋 ПЛАН РАЗРАБОТКИ

---

## Executive Summary

**Текущее состояние:**
- ✅ Базовая генерация отчета работает (`/api/professional-report`)
- ✅ 156-point matching алгоритм реализован
- ✅ Базовые данные из БД и enrichment services
- ⚠️ Большинство секций используют mock данные или не реализованы
- ❌ Нет интеграции с Neighbourhood Explorer, Firecrawl Explorer, Google Places Insights

**Цель:**
Привести все 23 секции отчета к виду, описанному в ТЗ, используя реальные данные из доступных источников.

**Оценка времени:** 25-30 часов разработки

---

## 🔴 КРИТИЧЕСКИЙ ПРИОРИТЕТ (Блокирует MVP)

### 1. Интеграция Neighbourhood Explorer (Секции 18, 19)

**Цель:** Добавить данные о Location Wellbeing и Area Map с POI

**Задачи:**
- [ ] **1.1** Добавить вызов `GET /api/neighbourhood/analyze/{postcode}` в `generate_professional_report()`
  - Файл: `api-testing-suite/backend/main.py`
  - Место: после получения care homes, для каждого home
  - Время: 2 часа
  
- [ ] **1.2** Извлечь данные для Секции 18 (Location Wellbeing):
  - `osm.walk_score.score` → walkability_score
  - `osm.amenities.by_category.parks[]` → green_space_score, nearest_park_distance
  - `environmental.noise_level` → noise_level (если `include_environmental=true`)
  - `osm.amenities.by_category` → local_amenities[]
  - Файл: `api-testing-suite/backend/main.py` (функция `build_location_wellbeing`)
  - Время: 2 часа

- [ ] **1.3** Извлечь данные для Секции 19 (Area Map):
  - `nhsbsa.nearest_practices[]` → nearby_gps[]
  - `osm.amenities.by_category.parks[]` → nearby_parks[]
  - `osm.amenities.by_category.shopping[]` → nearby_shops[]
  - `osm.amenities.by_category.healthcare[]` → nearby_pharmacies[], nearest_hospital
  - `osm.infrastructure.public_transport` → nearest_bus_stop, nearest_train_station
  - Файл: `api-testing-suite/backend/main.py` (функция `build_area_map`)
  - Время: 2 часа

**Файлы для изменения:**
- `api-testing-suite/backend/main.py` - добавить вызовы neighbourhood API
- `api-testing-suite/backend/routers/neighbourhood_routes.py` - проверить endpoints

**Оценка времени:** 6 часов

---

### 2. Интеграция Firecrawl Explorer (Секции 6, 7, 8, 16, 17)

**Цель:** Добавить данные о facilities, activities, nutrition, policies

**Задачи:**
- [ ] **2.1** Добавить вызов `POST /api/firecrawl/unified-analysis` в `generate_professional_report()`
  - Условие: только если у care home есть `website`
  - Файл: `api-testing-suite/backend/main.py`
  - Место: после enrichment, для каждого home
  - Время: 1 час

- [ ] **2.2** Извлечь данные для Секции 6 (Safety Analysis):
  - `structured_data.safety.safeguarding_policies[]` → safety_strengths[]
  - `structured_data.safety.emergency_procedures` → safety_metrics
  - `structured_data.safety.security_features[]` → safety_features[]
  - Файл: `api-testing-suite/backend/main.py` (функция `build_safety_analysis`)
  - Время: 1 час

- [ ] **2.3** Извлечь данные для Секции 7 (FSA Food Safety):
  - `structured_data.nutrition.dietary_accommodations[]` → dietary_specialties[]
  - `structured_data.nutrition.dining_options[]` → meal_choice_availability
  - Файл: `api-testing-suite/backend/main.py` (функция `build_fsa_details`)
  - Время: 1 час

- [ ] **2.4** Извлечь данные для Секции 8 (Medical Care):
  - `structured_data.care_services.medical_services[]` → specialties[]
  - `structured_data.care_services.specializations[]` → medical_strengths[]
  - Файл: `api-testing-suite/backend/main.py` (функция `build_medical_care_analysis`)
  - Время: 1 час

- [ ] **2.5** Извлечь данные для Секции 16 (Comfort & Lifestyle):
  - `structured_data.facilities.rooms[]` → private_room_percentage, ensuite_availability
  - `structured_data.facilities.accessibility[]` → wheelchair_accessible
  - `structured_data.facilities.outdoor_spaces[]` → outdoor_space_description
  - `structured_data.activities.daily_activities[]` → weekly_activities_count
  - `structured_data.activities.outings[]` → outings_per_month
  - `structured_data.nutrition.dining_options[]` → meal_choice_availability
  - `structured_data.media.photo_gallery[]` → room_photos[]
  - Файл: `api-testing-suite/backend/main.py` (функция `build_comfort_lifestyle`)
  - Время: 2 часа

- [ ] **2.6** Извлечь данные для Секции 17 (Lifestyle Deep Dive):
  - `structured_data.activities.daily_activities[]` → sample_daily_schedule[], activity_categories[]
  - `structured_data.contact.visiting_hours` → visiting_hours
  - `structured_data.care_services.care_plans` → personalization_description
  - Генерация policies через Perplexity (если нет в Firecrawl)
  - Файл: `api-testing-suite/backend/main.py` (функция `build_lifestyle_deep_dive`)
  - Время: 2 часа

**Файлы для изменения:**
- `api-testing-suite/backend/main.py` - добавить вызовы Firecrawl API
- `api-testing-suite/backend/api_clients/firecrawl_client.py` - проверить API

**Оценка времени:** 8 часов

---

### 3. Интеграция Google Places Insights (Секция 11)

**Цель:** Добавить данные о Family Engagement (dwell time, repeat visitors, footfall)

**Задачи:**
- [ ] **3.1** Использовать `GooglePlacesEnrichmentService._fetch_google_places_data()` для получения insights
  - Файл: `api-testing-suite/backend/main.py`
  - Место: в функции enrichment для каждого home
  - Время: 1 час

- [ ] **3.2** Извлечь данные для Секции 11 (Family Engagement):
  - `google_places_data.insights.dwell_time.average_dwell_time_minutes` → avg_visit_duration_minutes
  - `google_places_data.insights.repeat_visitor_rate.repeat_visitor_rate_percent` → repeat_visitor_rate
  - `google_places_data.insights.footfall_trends.trend_direction` → footfall_trend
  - `google_places_data.insights.popular_times` → peak_visiting_hours[]
  - Файл: `api-testing-suite/backend/main.py` (функция `build_family_engagement`)
  - Время: 2 часа

**Файлы для изменения:**
- `api-testing-suite/backend/main.py` - использовать GooglePlacesEnrichmentService
- `api-testing-suite/backend/services/google_places_enrichment_service.py` - проверить метод

**Оценка времени:** 3 часа

---


## 🟡 ВЫСОКИЙ ПРИОРИТЕТ (Улучшает качество)

### 5. Улучшение Секции 1 (Executive Summary)

**Задачи:**
- [ ] **5.1** Добавить расчет `waiting_list_status` на основе `beds_available`
  - Логика: "Available now" если `beds_available > 0`, "2-4 weeks" если `beds_available == 0` и `occupancy_rate < 0.95`, "3+ months" если `occupancy_rate >= 0.95`
  - Файл: `api-testing-suite/backend/main.py` (функция `build_executive_summary`)
  - Время: 1 час

- [ ] **5.2** Улучшить генерацию `match_reason` из `factor_scores`
  - Создать функцию для генерации текста на основе top 2-3 категорий
  - Файл: `api-testing-suite/backend/main.py`
  - Время: 1 час

**Оценка времени:** 2 часа

---

### 6. Улучшение Секции 10 (Community Reputation)

**Задачи:**
- [ ] **6.1** Использовать Firecrawl для получения CareHome.co.uk reviews
  - `structured_data.reviews.testimonials[]` → sample_reviews[]
  - `structured_data.reviews.average_rating` → carehome_rating
  - Файл: `api-testing-suite/backend/main.py` (функция `build_community_reputation`)
  - Время: 1 час

- [ ] **6.2** Улучшить sentiment analysis
  - Использовать `GooglePlacesEnrichmentService._analyze_sentiment_simple()`
  - Файл: `api-testing-suite/backend/main.py`
  - Время: 1 час

**Оценка времени:** 2 часа

---

### 7. Улучшение Секции 14 (Funding Options)

**Задачи:**
- [ ] **7.1** Использовать ONS для получения local authority name
  - `GET /api/neighbourhood/analyze/{postcode}` → `ons.geography.local_authority`
  - Файл: `api-testing-suite/backend/main.py` (функция `build_funding_options`)
  - Время: 1 час

- [ ] **7.2** Использовать MSIF data для local authority rules (fair cost benchmarks)
  - Уже используется, но можно улучшить отображение
  - Файл: `api-testing-suite/backend/main.py`
  - Время: 1 час

- [ ] **7.3** Создать базу данных с контактами local authorities (опционально)
  - Или использовать внешний API
  - Время: 2-3 часа (если нужно)

**Оценка времени:** 2-4 часа

---

### 8. Улучшение Секции 15 (Action Plan)

**Задачи:**
- [ ] **8.1** Использовать Google Places popular times для peak visiting hours
  - `GET /api/google-places/{place_id}/popular-times` → `peak_visiting_hours[]`
  - Файл: `api-testing-suite/backend/main.py` (функция `build_action_plan`)
  - Время: 1 час

- [ ] **8.2** Использовать ONS для local authority name
  - `GET /api/neighbourhood/analyze/{postcode}` → `ons.geography.local_authority`
  - Время: 0.5 часа

**Оценка времени:** 1.5 часа

---

### 9. Улучшение Секции 23 (Appendix - Data Sources)

**Задачи:**
- [ ] **9.1** Использовать `GET /api/cache/stats` для получения last update dates
  - Извлечь `last_update` даты для каждого источника
  - Файл: `api-testing-suite/backend/main.py` (функция `build_appendix`)
  - Время: 1 час

- [ ] **9.2** Добавить статический список всех источников данных с описаниями
  - Создать константу с метаданными источников
  - Файл: `api-testing-suite/backend/main.py` или отдельный файл
  - Время: 1 час

**Оценка времени:** 2 часа

---

## 🟢 СРЕДНИЙ ПРИОРИТЕТ (Nice to have)


### 11. Добавление Air Quality и Crime Rate (Секция 18)

**Задачи:**
- [ ] **11.1** Интегрировать UK Air Quality API
  - Endpoint для получения air quality index по координатам
  - Файл: создать `api-testing-suite/backend/api_clients/air_quality_client.py`
  - Время: 2 часа

- [ ] **11.2** Интегрировать Police UK API для crime rate
  - Endpoint для получения crime statistics по postcode
  - Файл: создать `api-testing-suite/backend/api_clients/police_uk_client.py`
  - Время: 2 часа

**Оценка времени:** 4 часа

---

## 📋 ФРОНТЕНД ЗАДАЧИ

### 12. Создание/Обновление React Компонентов

**Задачи:**
- [ ] **12.1** Создать компонент `LocationWellbeingSection.tsx` (Секция 18)
  - Отображает walkability, green spaces, noise level, amenities
  - Файл: `api-testing-suite/frontend/src/features/professional-report/components/`
  - Время: 2 часа

- [ ] **12.2** Создать компонент `AreaMapSection.tsx` (Секция 19)
  - Отображает карту с POI (GPs, parks, shops, pharmacies, hospitals)
  - Использовать карту (Google Maps или Leaflet)
  - Файл: `api-testing-suite/frontend/src/features/professional-report/components/`
  - Время: 3 часа

- [ ] **12.3** Обновить компонент `FamilyEngagementSection.tsx` (Секция 11)
  - Добавить отображение dwell time, repeat visitors, footfall trends
  - Файл: `api-testing-suite/frontend/src/features/professional-report/components/`
  - Время: 2 часа

- [ ] **12.4** Обновить компонент `ComfortLifestyleSection.tsx` (Секция 16)
  - Добавить отображение facilities, activities, nutrition из Firecrawl
  - Файл: `api-testing-suite/frontend/src/features/professional-report/components/`
  - Время: 2 часа

- [ ] **12.5** Создать компонент `LifestyleDeepDiveSection.tsx` (Секция 17)
  - Отображает daily schedule, activities, policies
  - Файл: `api-testing-suite/frontend/src/features/professional-report/components/`
  - Время: 2 часа

- [ ] **12.6** Обновить компонент `TestimonialsSection.tsx` (Секция 20)
  - Использовать данные из testimonials API
  - Файл: `api-testing-suite/frontend/src/features/professional-report/components/`
  - Время: 1 час

- [ ] **12.7** Создать компонент `ShareWithFamilySection.tsx` (Секция 22)
  - Форма для ввода email адресов, кнопка отправки
  - Файл: `api-testing-suite/frontend/src/features/professional-report/components/`
  - Время: 2 часа

- [ ] **12.8** Обновить компонент `AppendixSection.tsx` (Секция 23)
  - Отображать last update dates из cache stats
  - Файл: `api-testing-suite/frontend/src/features/professional-report/components/`
  - Время: 1 час

**Оценка времени:** 15 часов

---

## 📊 ИТОГОВАЯ ОЦЕНКА

### Время на реализацию:

**Критический приоритет (MVP):**
- Neighbourhood Explorer: 6 часов
- Firecrawl Explorer: 8 часов
- Google Places Insights: 3 часа
- **Итого:** 17 часов

**Высокий приоритет:**
- Executive Summary: 2 часа
- Community Reputation: 2 часа
- Funding Options: 2-4 часа
- Action Plan: 1.5 часа
- Appendix: 2 часа
- **Итого:** 9.5-11.5 часов

**Средний приоритет:**
- Share with Family: 9 часов
- Air Quality/Crime Rate: 4 часа
- **Итого:** 13 часов

**Фронтенд:**
- React компоненты: 15 часов

**Общая оценка:** 45.5-47.5 часов разработки

---

## 🎯 ПРИОРИТИЗАЦИЯ

### Phase 1 (MVP) - 17 часов:
1. ✅ Neighbourhood Explorer (6ч)
2. ✅ Firecrawl Explorer (8ч)
3. ✅ Google Places Insights (3ч)

### Phase 2 (Улучшения) - 11.5 часов:
5. Executive Summary (2ч)
6. Community Reputation (2ч)
7. Funding Options (2-4ч)
8. Action Plan (1.5ч)
9. Appendix (2ч)

### Phase 3 (Дополнительно) - 4 часа:
10. Air Quality/Crime Rate (4ч)

### Phase 4 (Фронтенд) - 15 часов:
12. React компоненты (15ч)

---

## 📝 ЗАМЕТКИ

- Все задачи должны быть выполнены с учетом fallback стратегий (если данные недоступны)
- Приоритет отдается интеграции существующих источников данных
- Новые API интеграции (air quality, crime rate) можно отложить на Phase 3
- Фронтенд задачи можно выполнять параллельно с бэкенд задачами

---

**Конец плана**


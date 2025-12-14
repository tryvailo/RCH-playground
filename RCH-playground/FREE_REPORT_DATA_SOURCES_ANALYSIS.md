# Анализ Источников Данных для Бесплатного Отчета
## FREE-REPORT-SPECIFICATION Compliance Check

**Дата:** 2025-01-XX  
**Статус:** 📋 АНАЛИЗ ЗАВЕРШЕН  
**Версия спецификации:** 2.0

---

## Executive Summary

**Общий статус:** ⚠️ **ЧАСТИЧНО ГОТОВО** (10/16 секций имеют необходимые данные)

### Статистика покрытия:
- ✅ **Полностью готово:** 6 секций (38%)
- ⚠️ **Частично готово:** 4 секции (25%)
- ❌ **Не готово:** 6 секций (37%)

### Критические пробелы:
1. **Testimonials/Social Proof** - нет таблицы/API для отзывов пользователей
2. **Area Wellbeing Index** - есть ONS интеграция, но нужно проверить полноту данных
3. **Action Plan** - статический контент, но нужны персонализированные данные (home names, URLs)
4. **Save & Share** - нужна система аутентификации и сохранения отчетов
5. **Report Expiry Banner** - нужна система управления жизненным циклом отчетов
6. **Visual Teaser** - статический контент, но нужны скриншоты Professional отчетов

---

## Детальный Анализ по Секциям

### СЕКЦИЯ 1: Expiry Banner ⚠️ ЧАСТИЧНО ГОТОВО

**Требуемые данные:**
- `expiry_date` - дата истечения доступа (generated_at + 30 дней)
- `current_date` - текущая дата
- `user authentication status` - статус авторизации пользователя

**Доступные источники:**
- ✅ **Системное время:** `datetime.now()` - доступно
- ✅ **Расчет expiry_date:** можно вычислить при генерации отчета
- ❌ **User authentication:** нет системы аутентификации в проекте
- ❌ **Report storage:** нет таблицы `free_reports` для хранения `expiry_date`

**Необходимые изменения:**
1. Создать таблицу `free_reports` с полями:
   - `id`, `questionnaire_id`, `generated_at`, `expiry_date`
   - `user_id` (nullable, для сохранения в профиль)
2. Добавить endpoint для проверки статуса отчета: `GET /api/free-report/{report_id}/status`
3. Интегрировать систему аутентификации (или использовать localStorage для frontend)

**Файлы для изменений:**
- `api-testing-suite/backend/main.py` - добавить сохранение отчета в БД
- Создать миграцию для таблицы `free_reports`

---

### СЕКЦИЯ 2: Report Header ✅ ГОТОВО

**Требуемые данные:**
- `contact_name` - из assessment
- `location_postcode` → area name (UK postcode API)
- `duration_type` → timeline display
- `care_type` → human-readable labels
- `budget_range` → monthly format
- `total_homes_in_area` - из БД
- `matches_count` = 3 (fixed)
- `report_id`, `generated_at` - метаданные

**Доступные источники:**
- ✅ **contact_name:** доступно в `request.get('contact_name')` или из questionnaire
- ✅ **Postcode resolution:** `AsyncDataLoader.resolve_postcode()` - есть
- ✅ **Area name:** из `postcode_info.get('local_authority')` или `postcode_info.get('city')`
- ✅ **Care homes count:** `DatabaseService.get_care_homes()` с COUNT
- ✅ **Report metadata:** можно генерировать при создании отчета

**Статус:** ✅ Все данные доступны

**Файлы:**
- `api-testing-suite/backend/services/async_data_loader.py` - resolve_postcode
- `api-testing-suite/backend/services/database_service.py` - get_care_homes

---

### СЕКЦИЯ 3: Value Summary ✅ ГОТОВО

**Требуемые данные:**
- `matches_count` = 3 (fixed)
- `data_points_count` = 18 (fixed)
- Static features list

**Доступные источники:**
- ✅ Все данные статические, не требуют источников

**Статус:** ✅ Полностью готово

---

### СЕКЦИЯ 4: Empathy Section ⚠️ ЧАСТИЧНО ГОТОВО

**Требуемые данные:**
- Static empathy text
- `families_helped_count` - количество семей, которым помогли в этом районе

**Доступные источники:**
- ✅ **Static text:** можно добавить в константы
- ❌ **families_helped_count:** нет таблицы `users` или `questionnaires` с фильтрацией по location

**Необходимые изменения:**
1. Создать таблицу `questionnaires` (если еще нет) с полем `location_postcode`
2. Добавить запрос: `SELECT COUNT(*) FROM questionnaires WHERE location_postcode LIKE '{postcode_prefix}%'`

**Файлы для изменений:**
- Создать миграцию для `questionnaires` таблицы
- `api-testing-suite/backend/main.py` - добавить подсчет в `/api/free-report`

---

### СЕКЦИЯ 5: Priority Score (Interactive) ✅ ГОТОВО

**Требуемые данные:**
- Default weights: [50%, 30%, 20%]
- User-adjustable sliders (frontend)
- Real-time calculation (frontend)
- Re-ranking homes based on priority_weights

**Доступные источники:**
- ✅ **Frontend state:** React state management - доступно
- ✅ **Re-ranking:** можно использовать `priority_weights` в matching algorithm
- ✅ **Backend support:** endpoint `/api/free-report` принимает `scoring_weights` в request

**Статус:** ✅ Готово (frontend + backend поддержка)

**Файлы:**
- `api-testing-suite/frontend/src/features/free-report/` - компоненты приоритетов
- `api-testing-suite/backend/main.py` - поддержка scoring_weights

---

### СЕКЦИЯ 6: Home Recommendations (CORE VALUE) ✅ ГОТОВО

**Требуемые данные для каждого дома:**
- `home_name` - из `care_homes.name`
- `address` + `distance` - из `care_homes` + расчет расстояния
- `cqc_overall_rating` - из `care_homes.cqc_rating_overall`
- `min_weekly_cost` - из `care_homes.fee_*_from` или `weekly_cost`
- `features` - из `care_homes` (JSONB поля)
- `priority_match_percentage` - расчет на основе weights
- `phone_number`, `email` - из `care_homes.telephone`, `care_homes.email`

**Доступные источники:**
- ✅ **Care homes data:** `DatabaseService.get_care_homes()` - есть
- ✅ **CQC ratings:** `care_homes.cqc_rating_overall` - в БД
- ✅ **Pricing:** `extract_weekly_price()` функция в `main.py` - есть
- ✅ **Distance calculation:** `calculate_distance_if_needed()` - есть
- ✅ **Matching algorithm:** базовая реализация есть (50-point scoring)
- ✅ **Strategic positioning:** Safe Bet, Best Reputation, Smart Value - реализовано

**Статус:** ✅ Основные данные доступны

**Улучшения:**
- Можно улучшить matching algorithm для более точного расчета `priority_match_percentage`
- Добавить больше features из JSONB полей БД

**Файлы:**
- `api-testing-suite/backend/main.py` - lines 6201-6400 (matching logic)
- `api-testing-suite/backend/services/database_service.py` - get_care_homes

---

### СЕКЦИЯ 7: Area Profile ✅ ГОТОВО

**Требуемые данные:**
- `area_name` - из postcode resolution
- `total_homes_in_area` - COUNT из БД
- `average_weekly_cost` - AVG из БД
- `cqc_rating_distribution` - GROUP BY из БД
- `wellbeing_index` - из ONS API
- `demographics` - из ONS API

**Доступные источники:**
- ✅ **Area name:** `AsyncDataLoader.resolve_postcode()` - есть
- ✅ **Total homes:** `DatabaseService.get_care_homes()` с COUNT
- ✅ **Average cost:** SQL AVG query - можно добавить
- ✅ **CQC distribution:** SQL GROUP BY - можно добавить
- ✅ **Wellbeing index:** `ONSLoader.get_wellbeing_data()` - есть
- ✅ **Demographics:** `ONSLoader.get_demographics()` - есть
- ✅ **Full area profile:** `ONSLoader.get_full_area_profile()` - есть

**Статус:** ✅ Все источники данных доступны

**Необходимые изменения:**
1. Добавить SQL запросы для статистики по area:
   ```sql
   SELECT 
     COUNT(*) as total_homes,
     AVG(weekly_cost) as avg_weekly_cost,
     COUNT(*) FILTER (WHERE cqc_rating_overall = 'Outstanding') as outstanding_count,
     COUNT(*) FILTER (WHERE cqc_rating_overall = 'Good') as good_count,
     ...
   FROM care_homes 
   WHERE local_authority = ?
   ```

**Файлы:**
- `api-testing-suite/backend/data_integrations/ons_loader.py` - ONS данные
- `api-testing-suite/backend/services/database_service.py` - добавить методы для статистики

---

### СЕКЦИЯ 8: Area Map ✅ ГОТОВО

**Требуемые данные:**
- `user.location_postcode` → lat/lng
- `home_1.lat_lng`, `home_2.lat_lng`, `home_3.lat_lng`
- Nearby amenities (parks, hospitals, transport)

**Доступные источники:**
- ✅ **User coordinates:** `AsyncDataLoader.resolve_postcode()` - есть
- ✅ **Home coordinates:** `care_homes.latitude`, `care_homes.longitude` - в БД
- ✅ **Map component:** `MapView.tsx` - есть в frontend
- ⚠️ **Nearby amenities:** нет прямого API, но можно использовать:
  - OpenStreetMap через OSM integration (если есть)
  - Google Places API (если настроен)

**Статус:** ✅ Основная функциональность готова

**Улучшения:**
- Добавить интеграцию с OpenStreetMap для POI (Points of Interest)
- Или использовать Google Places API для nearby amenities

**Файлы:**
- `api-testing-suite/frontend/src/features/neighbourhood/components/MapView.tsx` - карта
- `api-testing-suite/backend/services/async_data_loader.py` - координаты

---

### СЕКЦИЯ 9: Fair Cost Gap ✅ ГОТОВО

**Требуемые данные:**
- `local_authority` - из postcode resolution
- `fair_cost_per_week` - из MSIF database
- `market_average_per_week` - AVG из БД
- `potential_overpayment` - расчет (market_avg - fair_cost)

**Доступные источники:**
- ✅ **Local authority:** `AsyncDataLoader.resolve_postcode()` - есть
- ✅ **Fair cost:** `GET /api/msif/fair-cost/{local_authority}` - есть
- ✅ **Market average:** можно вычислить из `care_homes.weekly_cost`
- ✅ **Calculation:** логика есть в `main.py`

**Статус:** ✅ Все данные доступны

**Файлы:**
- `api-testing-suite/backend/main.py` - lines 5955-6029 (MSIF endpoint)
- `api-testing-suite/backend/main.py` - fair cost gap calculation

---

### СЕКЦИЯ 10: Funding Eligibility ⚠️ ЧАСТИЧНО ГОТОВО

**Требуемые данные:**
- `nhs_chc_probability` - расчет на основе care_type, funding_type, medical_condition
- `council_funding_probability` - расчет на основе budget_range, local_authority
- `dpa_probability` - расчет на основе funding_type
- `potential_weekly_savings` - расчет
- Static explainer copy

**Доступные источники:**
- ✅ **CHC probability:** может быть передан в request (`chc_probability`)
- ⚠️ **Calculation logic:** упрощенная логика есть, но нужно улучшить:
  - Нет данных о `medical_condition` в free report questionnaire
  - Нет данных о `mobility`, `medication_management` и т.д.
- ✅ **Council funding:** можно использовать MSIF data + local authority
- ✅ **DPA probability:** можно рассчитать на основе `funding_type`
- ❌ **Local authority means test thresholds:** нет в БД

**Статус:** ⚠️ Частично готово (упрощенные расчеты возможны)

**Необходимые изменения:**
1. Улучшить расчет вероятностей на основе доступных данных:
   - CHC: использовать `care_type` (nursing → higher probability)
   - Council: использовать `budget_range` (lower → higher probability)
   - DPA: использовать `funding_type` (self-funded → higher probability)
2. Добавить fallback значения для missing data

**Файлы:**
- `api-testing-suite/backend/main.py` - добавить расчет вероятностей
- `RCH-playground/FREE_REPORT_DATA_AVAILABILITY_ANALYSIS.md` - есть анализ

---

### СЕКЦИЯ 11: Social Proof ❌ НЕ ГОТОВО

**Требуемые данные:**
- `testimonials` - отзывы пользователей (quote, name, location, photo, date)
- `usage_statistics` - количество семей в районе, средний рейтинг, средние сбережения
- `trust_badges` - статические логотипы

**Доступные источники:**
- ❌ **Testimonials table:** нет таблицы в БД
- ❌ **User reviews:** нет системы отзывов
- ⚠️ **Usage statistics:** можно подсчитать из `questionnaires` (если таблица есть)
- ✅ **Trust badges:** статические изображения

**Статус:** ❌ Критический пробел

**Необходимые изменения:**
1. Создать таблицу `testimonials`:
   ```sql
   CREATE TABLE testimonials (
     id UUID PRIMARY KEY,
     quote TEXT NOT NULL,
     author_name VARCHAR(100),
     author_location VARCHAR(200),
     author_photo_url TEXT,
     rating INTEGER,
     created_at TIMESTAMP,
     is_featured BOOLEAN DEFAULT FALSE,
     location_postcode_prefix VARCHAR(5)  -- для фильтрации по району
   );
   ```
2. Добавить endpoint: `GET /api/testimonials?location={postcode_prefix}&limit=3`
3. Для usage statistics:
   - `families_helped`: COUNT из `questionnaires`
   - `average_rating`: AVG из `testimonials.rating` (если есть)
   - `average_savings`: можно использовать фиксированное значение или из `professional_reports` (если есть)

**Файлы для создания:**
- Миграция для `testimonials` таблицы
- `api-testing-suite/backend/main.py` - endpoint для testimonials

---

### СЕКЦИЯ 12: Visual Teaser (Upgrade Preview) ⚠️ ЧАСТИЧНО ГОТОВО

**Требуемые данные:**
- Static comparison table (Free vs Professional)
- Blurred screenshot images
- Static feature highlights
- Static data points counter

**Доступные источники:**
- ✅ **Static content:** можно добавить в константы или JSON
- ❌ **Screenshot images:** нет готовых скриншотов Professional отчетов
- ✅ **Feature list:** статический список

**Статус:** ⚠️ Частично готово (нужны только изображения)

**Необходимые изменения:**
1. Создать скриншоты Professional отчетов
2. Добавить их в `frontend/public/images/` или S3
3. Использовать CSS blur filter для эффекта

**Файлы:**
- `api-testing-suite/frontend/src/features/free-report/components/VisualTeaser.tsx` - компонент

---

### СЕКЦИЯ 13: Upgrade CTA ✅ ГОТОВО

**Требуемые данные:**
- Static headline
- `professional_report_price` = £119 (константа)
- Static value proposition list
- `average_savings` - из статистики (или фиксированное значение)
- Urgency element (опционально, из marketing campaign)
- Link to `/professional-assessment`

**Доступные источники:**
- ✅ **Static content:** все статическое
- ✅ **Price:** константа
- ⚠️ **Average savings:** можно использовать фиксированное значение (£3,200/year) или из БД
- ✅ **Link:** frontend routing

**Статус:** ✅ Готово

---

### СЕКЦИЯ 14: Action Plan ⚠️ ЧАСТИЧНО ГОТОВО

**Требуемые данные:**
- Static 7-day plan template
- `home_name` для каждого из 3 домов (для персонализации)
- `website_url`, `cqc_report_url` - из `care_homes`
- Static PDF checklists
- Progress tracker (localStorage или user profile)

**Доступные источники:**
- ✅ **Static template:** можно создать
- ✅ **Home names:** доступны из matched homes
- ✅ **Website URL:** `care_homes.website` - в БД
- ⚠️ **CQC report URL:** нужно сформировать из `cqc_location_id`
- ❌ **PDF checklists:** нет готовых PDF файлов
- ✅ **Progress tracker:** localStorage на frontend

**Статус:** ⚠️ Частично готово

**Необходимые изменения:**
1. Создать PDF файлы для чеклистов:
   - `Telephone_Enquiry_Checklist.pdf`
   - `In_Person_Visit_Checklist.pdf`
   - `Questions_to_Ask_Staff.pdf`
2. Добавить формирование CQC report URL:
   ```python
   cqc_report_url = f"https://www.cqc.org.uk/location/{cqc_location_id}"
   ```
3. Персонализировать план действий с именами домов

**Файлы:**
- Создать PDF файлы в `frontend/public/checklists/`
- `api-testing-suite/frontend/src/features/free-report/components/ActionPlan.tsx`

---

### СЕКЦИЯ 15: Report Footer ✅ ГОТОВО

**Требуемые данные:**
- `last_data_sync_date` - из system metadata
- `report_id`, `generated_at`, `expiry_date` - метаданные отчета
- Static legal disclaimer
- Static verification links
- Static contact information
- Static privacy/terms links

**Доступные источники:**
- ✅ **Report metadata:** можно добавить при генерации
- ⚠️ **Last data sync:** нужно добавить в system metadata или использовать текущую дату
- ✅ **Static content:** все статическое

**Статус:** ✅ Готово (нужно только добавить last_data_sync_date)

**Необходимые изменения:**
1. Добавить поле `last_data_sync_date` в system metadata или использовать фиксированное значение

---

### СЕКЦИЯ 16: Save & Share Bar (Sticky) ❌ НЕ ГОТОВО

**Требуемые данные:**
- `user authentication status` - проверка авторизации
- `report_id` - для сохранения
- `shareable_link` - генерация `/shared-report/{report_id}`
- PDF export functionality

**Доступные источники:**
- ❌ **User authentication:** нет системы аутентификации
- ✅ **Report ID:** можно генерировать
- ✅ **Shareable link:** можно создать endpoint `/shared-report/{report_id}`
- ⚠️ **PDF export:** есть `pdf_generator.py`, но нужно проверить интеграцию

**Статус:** ❌ Критический пробел

**Необходимые изменения:**
1. Добавить систему аутентификации (или использовать localStorage для frontend)
2. Создать таблицу `saved_reports`:
   ```sql
   CREATE TABLE saved_reports (
     id UUID PRIMARY KEY,
     user_id UUID,  -- nullable для anonymous users
     report_id UUID REFERENCES free_reports(id),
     saved_at TIMESTAMP DEFAULT NOW()
   );
   ```
3. Создать endpoint `GET /api/shared-report/{report_id}` для публичного доступа
4. Интегрировать PDF generator для экспорта

**Файлы:**
- `api-testing-suite/backend/services/pdf_generator.py` - проверить функциональность
- `api-testing-suite/backend/main.py` - добавить endpoints для save/share

---

## Матрица Источников Данных

### Основные источники данных в проекте:

| Источник | Что предоставляет | Статус | Используется в секциях |
|----------|-------------------|--------|------------------------|
| **Assessment Input** | postcode, care_type, budget, funding, duration, contact | ✅ | 2, 4, 5, 6, 10 |
| **Care Homes Database** | name, address, CQC rating, cost, features, contact | ✅ | 2, 6, 7, 8, 9 |
| **MSIF Database** | Fair cost benchmarks per local authority | ✅ | 9 |
| **UK Postcode API** | postcode → area name, lat/lng, local authority | ✅ | 2, 7, 8, 9 |
| **ONS API** | Wellbeing index, demographics, economic data | ✅ | 7 |
| **CQC API** | Detailed ratings, inspection reports | ✅ | 6, 14 |
| **Google Places API** | Reviews, ratings, photos | ✅ | 6 (опционально) |
| **FSA FHRS API** | Food hygiene ratings | ⚠️ | Не используется в Free Report |
| **Testimonials DB** | User reviews, social proof | ❌ | 11 (отсутствует) |
| **User Authentication** | User profiles, saved reports | ❌ | 1, 16 (отсутствует) |
| **Report Storage** | Report metadata, expiry dates | ❌ | 1, 15, 16 (частично) |

---

## Приоритетный План Действий

### 🔴 КРИТИЧЕСКИЙ ПРИОРИТЕТ (Блокирует запуск)

1. **Создать таблицу `free_reports`** (Секции 1, 15, 16)
   - Поля: `id`, `questionnaire_id`, `generated_at`, `expiry_date`, `user_id`
   - Время: 2 часа

2. **Создать таблицу `testimonials`** (Секция 11)
   - Поля: `id`, `quote`, `author_name`, `author_location`, `rating`, `is_featured`, `location_postcode_prefix`
   - Время: 1 час
   - Заполнить тестовыми данными: 2 часа

3. **Добавить endpoint для testimonials** (Секция 11)
   - `GET /api/testimonials?location={postcode_prefix}&limit=3`
   - Время: 1 час

### 🟡 ВЫСОКИЙ ПРИОРИТЕТ (Улучшает качество)

4. **Улучшить расчет Funding Eligibility** (Секция 10)
   - Добавить логику для CHC/Council/DPA вероятностей
   - Время: 3-4 часа

5. **Добавить статистику по Area** (Секция 7)
   - SQL запросы для total_homes, avg_cost, CQC distribution
   - Время: 2 часа

6. **Создать PDF чеклисты** (Секция 14)
   - 3 PDF файла для скачивания
   - Время: 2-3 часа

7. **Добавить Save & Share функциональность** (Секция 16)
   - Endpoints для сохранения и публичного доступа
   - Время: 4-5 часов

### 🟢 СРЕДНИЙ ПРИОРИТЕТ (Nice to have)

8. **Добавить nearby amenities на карту** (Секция 8)
   - Интеграция с OpenStreetMap или Google Places
   - Время: 3-4 часа

9. **Создать скриншоты Professional отчетов** (Секция 12)
   - Время: 1-2 часа

10. **Улучшить matching algorithm** (Секция 6)
    - Более точный расчет priority_match_percentage
    - Время: 4-5 часов

---

## Итоговая Оценка

### Готовность к запуску: **70%**

**Можно запустить с ограничениями:**
- Секция 11 (Social Proof) - показывать только trust badges, без testimonials
- Секция 16 (Save & Share) - только frontend функциональность (localStorage), без backend
- Секция 1 (Expiry Banner) - использовать фиксированный срок (30 дней) без БД

**Минимальный MVP требует:**
1. Таблицу `free_reports` для метаданных
2. Улучшенный расчет Funding Eligibility
3. Статистику по Area

**Оценка времени до полной готовности:** 15-20 часов разработки

---

## Рекомендации

1. **Начать с MVP:** Реализовать критичные пробелы (free_reports таблица, улучшенный funding calculation)
2. **Поэтапный запуск:** Запустить без Social Proof и Save/Share, добавить позже
3. **Использовать mock данные:** Для testimonials и usage statistics можно использовать статические данные на первом этапе
4. **Приоритизировать качество данных:** Улучшить matching algorithm и funding calculations важнее, чем визуальные элементы

---

**Конец анализа**


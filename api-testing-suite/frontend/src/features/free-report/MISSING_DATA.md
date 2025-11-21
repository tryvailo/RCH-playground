# 📋 Недостающие данные для реализации FREE Report

**Дата:** 2025-01-XX  
**Статус:** Требуется для реализации

---

## 🔴 КРИТИЧНО - Без этого невозможно запустить

### 1. Database Schema (PostgreSQL + PostGIS)

**Статус:** ✅ БАЗА ДАННЫХ ЕСТЬ (`care_homes_db`)

**Известно:**
- ✅ База данных называется `care_homes_db`
- ✅ Есть таблица `care_homes` (судя по документации, содержит location_id, name, postcode, latitude, longitude, overall_rating и др.)
- ✅ Есть таблица `msif_fees_2025` (используется для MSIF данных)

**Требуется проверить:**
- ❓ Какие таблицы уже существуют в `care_homes_db`?
- ❓ Есть ли таблицы `questionnaires`, `free_reports`, `google_data`?
- ❓ Есть ли PostGIS расширение установлено?
- ❓ Какой connection string (DATABASE_URL)? Формат: `postgresql://user:pass@host:port/care_homes_db`
- ❓ Нужно ли создать недостающие таблицы или использовать существующую схему?

---

### 2. 50-Point Matching Algorithm

**Статус:** ⚠️ ЧАСТИЧНО (есть базовый MatchingService, но не полный алгоритм)

**Что есть:**
- ✅ Базовый MatchingService с Safe Bet, Best Value, Premium
- ✅ Расчёт расстояния (Haversine)
- ✅ Базовый scoring по CQC rating

**Чего не хватает:**
- ❌ Полный 50-point scoring по 6 категориям:
  - Location (20 points) - есть частично
  - CQC Rating (25 points) - есть частично
  - Budget Match (20 points) - НЕТ
  - Care Type Match (15 points) - НЕТ
  - Availability (10 points) - НЕТ данных о beds_available
  - Google Reviews (10 points) - НЕТ интеграции

**Вопросы:**
- Откуда брать данные о `beds_available`? (CQC API, Autumna, или mock?)
- Как интегрировать Google Places reviews в matching?
- Нужно ли сохранять scores в БД для аналитики?

---

### 3. Google Places Reviews Integration

**Статус:** ✅ API ЕСТЬ И РАБОТАЕТ

**Что есть:**
- ✅ GooglePlacesAPIClient с Redis caching
- ✅ Методы `find_place()` и `get_place_details()` возвращают:
  - `rating` (decimal 2,1)
  - `user_ratings_total` (review_count)
  - `reviews` (review highlights)
- ✅ API key хранится в `config.json` → `google_places.api_key`
- ✅ Кэширование работает (24 часа TTL)

**Чего не хватает:**
- ❌ Интеграция Google reviews в 50-point matching algorithm
- ❌ Сохранение Google data в БД (таблица `google_data`) для offline доступа
- ❌ Использование Google rating в scoring (10 points из 100)

**Что нужно сделать:**
1. Добавить вызов GooglePlacesAPIClient в `_fetch_care_homes()` для каждого дома
2. Интегрировать Google rating в `calculate_50_point_score()`
3. Создать таблицу `google_data` для кэширования в БД (опционально)

---

### 4. Availability Data (Beds Available)

**Статус:** ❌ НЕТ

**Требуется:**
- Данные о доступности мест (`beds_available`)
- Waiting list информация (`waiting_list_weeks`)

**Вопросы:**
- Откуда брать данные о доступности?
  - CQC API? (не предоставляет)
  - Autumna API? (есть ли там?)
  - Собственный scraping?
  - Mock данные для FREE tier?
- Нужно ли обновлять availability в реальном времени или достаточно кэша?

---

### 5. Email Service (SendGrid)

**Статус:** ❌ НЕТ

**Требуется:**
- SendGrid API key
- Email templates для:
  - Free report delivery (Day 1)
  - "What you're missing" (Day 3)
  - "See full analysis" (Day 5)
- Error email template

**Вопросы:**
- Есть ли SendGrid аккаунт?
- Какой API key?
- Нужно ли использовать другой email сервис (AWS SES, Mailgun)?
- Какой sender email address?

---

### 6. S3 Storage для PDF

**Статус:** ❌ НЕТ

**Требуется:**
- AWS S3 bucket для хранения PDF
- AWS credentials (access_key, secret_key)
- Bucket name и region
- CORS настройки для frontend доступа
- Presigned URLs для безопасного доступа

**Вопросы:**
- Есть ли AWS аккаунт?
- Какой bucket name?
- Какой region?
- Нужно ли использовать другой storage (Google Cloud Storage, Azure Blob)?

---

### 7. Backend PDF Generation

**Статус:** ⚠️ ЧАСТИЧНО (есть frontend PDF через @react-pdf/renderer, но нет backend)

**Что есть:**
- ✅ Frontend PDF generation (FreeReportPDF.tsx)
- ✅ 8-страничная структура

**Чего не хватает:**
- ❌ Backend PDF generation (WeasyPrint или Playwright)
- ❌ HTML template (Jinja2) для backend
- ❌ Интеграция с S3 upload

**Вопросы:**
- Какой библиотекой генерировать PDF на backend?
  - WeasyPrint (HTML → PDF, проще)
  - Playwright (renders React, сложнее но точнее)
  - ReportLab (Python native, но требует переписывания)
- Нужно ли использовать тот же дизайн что и frontend PDF?

---

## 🟡 ВАЖНО - Для production качества

### 8. PostGIS для Geo-Queries

**Статус:** ❌ НЕТ

**Требуется:**
- PostGIS расширение в PostgreSQL
- GEOGRAPHY(POINT) тип для location
- GIST индекс для быстрых geo-queries
- Функции для расчёта расстояния (ST_Distance)

**Вопросы:**
- Есть ли PostGIS установлен?
- Нужно ли создавать миграцию для PostGIS?

---

### 9. Redis Configuration

**Статус:** ✅ ЕСТЬ (частично)

**Что есть:**
- ✅ CacheManager с Redis поддержкой
- ✅ Environment variables (REDIS_HOST, REDIS_PORT)

**Чего не хватает:**
- ❌ Подтверждение что Redis запущен
- ❌ Настройка TTL для разных типов кэша:
  - Query cache: 1 hour
  - CQC: 48 hours
  - FSA: 7 days
  - Google: 24 hours

**Вопросы:**
- Запущен ли Redis локально?
- Какой Redis URL для production?
- Нужна ли Redis password?

---

### 10. Email Templates

**Статус:** ❌ НЕТ

**Требуется:**
- HTML templates для:
  1. Free report delivery (с download link)
  2. "What you're missing" (gap list)
  3. "See full analysis" (Professional CTA)
  4. Error email

**Вопросы:**
- Какой стиль email (HTML, plain text, или оба)?
- Нужны ли изображения в email?
- Какой branding использовать?

---

### 11. Performance Monitoring

**Статус:** ❌ НЕТ

**Требуется:**
- Prometheus metrics
- Grafana dashboard
- Alerting rules

**Вопросы:**
- Есть ли Prometheus/Grafana setup?
- Какие метрики критичны для мониторинга?
- Нужны ли custom dashboards?

---

## 🟢 ОПЦИОНАЛЬНО - Для улучшения

### 12. Autumna API Integration

**Статус:** ⚠️ ЧАСТИЧНО (есть AutumnaScraper, но не используется для pricing/availability)

**Вопросы:**
- Есть ли Autumna API key?
- Предоставляет ли Autumna данные о availability?
- Нужно ли использовать для FREE tier или только для Professional?

---

### 13. Database Seeding

**Статус:** ❌ НЕТ

**Требуется:**
- Скрипт для заполнения care_homes из CQC API
- Регулярное обновление данных

**Вопросы:**
- Нужно ли seed базу данных из CQC API?
- Как часто обновлять данные?
- Сколько care homes нужно загрузить (все UK или только регионы)?

---

## 📝 Сводная таблица недостающих данных

| # | Компонент | Статус | Приоритет | Вопросы |
|---|-----------|--------|-----------|---------|
| 1 | PostgreSQL + PostGIS | ❌ НЕТ | 🔴 КРИТИЧНО | Connection string? PostGIS установлен? |
| 2 | 50-Point Algorithm | ⚠️ ЧАСТИЧНО | 🔴 КРИТИЧНО | Откуда beds_available? Google reviews интеграция? |
| 3 | Google Reviews | ⚠️ ЧАСТИЧНО | 🔴 КРИТИЧНО | API key? Лимиты? Review highlights? |
| 4 | Availability Data | ❌ НЕТ | 🔴 КРИТИЧНО | Откуда брать? CQC/Autumna/Mock? |
| 5 | SendGrid | ❌ НЕТ | 🔴 КРИТИЧНО | API key? Sender email? Templates? |
| 6 | S3 Storage | ❌ НЕТ | 🔴 КРИТИЧНО | AWS credentials? Bucket name? Region? |
| 7 | Backend PDF | ⚠️ ЧАСТИЧНО | 🔴 КРИТИЧНО | WeasyPrint/Playwright? Template? |
| 8 | PostGIS Setup | ❌ НЕТ | 🟡 ВАЖНО | Установлен? Миграция? |
| 9 | Redis Config | ✅ ЕСТЬ | 🟡 ВАЖНО | Запущен? URL? Password? |
| 10 | Email Templates | ❌ НЕТ | 🟡 ВАЖНО | HTML/Text? Branding? |
| 11 | Monitoring | ❌ НЕТ | 🟡 ВАЖНО | Prometheus/Grafana? |
| 12 | Autumna API | ⚠️ ЧАСТИЧНО | 🟢 ОПЦИОНАЛЬНО | API key? Availability? |
| 13 | Database Seeding | ❌ НЕТ | 🟢 ОПЦИОНАЛЬНО | Seed script? Update frequency? |

---

## 🎯 Следующие шаги

1. **Определить Database setup:**
   - PostgreSQL connection string
   - PostGIS установка
   - Миграции

2. **Получить API keys:**
   - Google Places API key
   - SendGrid API key
   - AWS credentials (если S3)

3. **Реализовать недостающие компоненты:**
   - 50-point algorithm
   - Google reviews интеграция
   - Availability data source
   - Email service
   - S3 upload
   - Backend PDF generation

4. **Настроить инфраструктуру:**
   - Redis
   - Monitoring
   - Email templates

---

**Готов к началу реализации после получения ответов на вопросы выше.**


# 📋 Что осталось реализовать из ТЗ

**Дата:** 2025-01-XX  
**Статус:** Анализ ТЗ и текущей реализации

---

## ✅ Что уже реализовано

### FREE Report (50-point matching)
- ✅ 50-point matching algorithm (Location, CQC, Budget, Care Type, Availability, Google Reviews)
- ✅ CQC API интеграция
- ✅ Google Places API интеграция
- ✅ MatchingService с динамическими scoring настройками
- ✅ Frontend с ScoringSettings sidebar
- ✅ Fair Cost Gap модуль
- ✅ PDF генерация (frontend)
- ✅ Mock данные для тестирования

### API Clients (есть в `api-testing-suite/backend/api_clients/`)
- ✅ CQC API Client (`cqc_client.py`)
- ✅ FSA API Client (`fsa_client.py`)
- ✅ Companies House API Client (`companies_house_client.py`)
- ✅ Google Places API Client (`google_places_client.py`)
- ✅ Perplexity API Client (`perplexity_client.py`)
- ✅ Autumna Scraper (`autumna_scraper.py`)
- ✅ Firecrawl Client (`firecrawl_client.py`)

---

## ❌ Что НЕ реализовано для FREE Report

### 1. 🔴 FSA FHRS интеграция в FREE Report

**Требование из ТЗ:**
- FSA FHRS API должен использоваться для получения food hygiene ratings
- Данные должны кэшироваться (7 дней TTL)
- Должны отображаться в отчете (цветовая индикация: green/yellow/red)

**Текущий статус:**
- ✅ FSA API Client существует (`api_clients/fsa_client.py`)
- ✅ Endpoints есть в `main.py` (`/api/fsa/*`)
- ❌ **НЕ используется в FREE Report генерации**
- ❌ **НЕ интегрирован в MatchingService**
- ❌ **НЕ отображается в ReportRenderer**

**Что нужно сделать:**
1. Добавить вызов FSA API в `_fetch_care_homes()` или `DatabaseService`
2. Сохранять FSA rating в данные дома
3. Использовать FSA rating в scoring (опционально, не в 50-point, но для отображения)
4. Отображать FSA color badge в `ReportRenderer.tsx`

---

### 2. 🔴 Autumna API интеграция для pricing

**Требование из ТЗ:**
- Autumna API должен использоваться для получения актуальных цен
- Кэширование 30 дней
- Fallback на данные из БД если API недоступен

**Текущий статус:**
- ✅ Autumna Scraper существует (`api_clients/autumna_scraper.py`)
- ❌ **НЕ используется в FREE Report**
- ❌ **НЕ интегрирован в процесс получения цен**

**Что нужно сделать:**
1. Добавить вызов Autumna API для получения цен
2. Использовать как primary source для pricing
3. Fallback на БД данные если недоступно

---

### 3. 🟡 Backend PDF генерация (WeasyPrint)

**Требование из ТЗ:**
- Backend должен генерировать PDF используя WeasyPrint
- HTML шаблон на Jinja2
- Загрузка в S3
- Отправка email с ссылкой

**Текущий статус:**
- ✅ Frontend PDF генерация (`@react-pdf/renderer`)
- ❌ **Backend PDF генерация НЕ реализована**
- ❌ **WeasyPrint не установлен**
- ❌ **HTML шаблоны не созданы**
- ❌ **S3 upload не реализован**
- ❌ **Email отправка не реализована**

**Что нужно сделать:**
1. Установить WeasyPrint
2. Создать Jinja2 HTML шаблон для FREE Report
3. Реализовать PDF генерацию в backend
4. Настроить S3 upload
5. Интегрировать SendGrid для email

---

### 4. 🟡 Database Service полная интеграция

**Требование из ТЗ:**
- PostgreSQL + PostGIS для хранения данных
- Оптимизированные SQL запросы с индексами
- Кэширование запросов

**Текущий статус:**
- ✅ `DatabaseService` существует (`services/database_service.py`)
- ⚠️ **Частично используется в FREE Report**
- ❌ **Не все поля заполняются из БД**
- ❌ **Нет полной интеграции с FSA/Autumna данными**

**Что нужно сделать:**
1. Убедиться что все данные из БД используются
2. Добавить сохранение FSA данных в БД
3. Добавить сохранение Autumna pricing в БД
4. Оптимизировать SQL запросы

---

## ❌ Что НЕ реализовано для PROFESSIONAL Report (156-point)

### 5. 🔴 156-Point Matching Algorithm

**Требование из ТЗ:**
- 8 категорий scoring:
  - Medical Capabilities (30 points)
  - Safety & Quality (25 points) - CQC + FSA + incidents
  - Location & Access (15 points)
  - Cultural & Social (15 points) - Visitor analytics
  - Financial Stability (20 points) - Companies House
  - Staff Quality (20 points) - Glassdoor + LinkedIn
  - CQC Compliance (20 points) - Historical trends
  - Additional Services (11 points)

**Текущий статус:**
- ❌ **156-point algorithm НЕ реализован**
- ❌ **Только 50-point для FREE Report**

**Что нужно сделать:**
1. Создать `ProfessionalMatchingService` с 156-point алгоритмом
2. Реализовать все 8 категорий scoring
3. Интегрировать все 15+ data sources

---

### 6. 🔴 Companies House Financial Analysis

**Требование из ТЗ:**
- 3-year financial analysis
- Altman Z-score calculation
- Red flags detection (late filings, negative working capital, director changes)
- Financial stability score (0-20 points)

**Текущий статус:**
- ✅ Companies House API Client существует
- ✅ Endpoints есть (`/api/companies-house/*`)
- ✅ `calculate_financial_stability_score()` реализован
- ❌ **НЕ используется в FREE Report**
- ❌ **НЕ используется в PROFESSIONAL Report**

**Что нужно сделать:**
1. Интегрировать Companies House в PROFESSIONAL Report
2. Добавить financial stability в 156-point scoring
3. Отображать financial analysis в отчете

---

### 7. 🔴 Glassdoor + LinkedIn Staff Quality Analysis

**Требование из ТЗ:**
- Glassdoor reviews для employee satisfaction
- LinkedIn для staff tenure & stability
- Job boards для turnover signals
- Staff quality score (0-20 points)

**Текущий статус:**
- ❌ **Glassdoor API НЕ интегрирован**
- ❌ **LinkedIn API НЕ интегрирован**
- ❌ **Job boards scraping НЕ реализован**

**Что нужно сделать:**
1. Исследовать Glassdoor API / scraping возможности
2. Исследовать LinkedIn API / scraping возможности
3. Реализовать staff quality scoring
4. Интегрировать в PROFESSIONAL Report

---

### 8. 🔴 Google Places Insights (Visitor Analytics)

**Требование из ТЗ:**
- Google Places Insights API для footfall, dwell time
- Visitor patterns analysis
- Cultural & Social score (0-15 points)

**Текущий статус:**
- ✅ Google Places API Client существует
- ✅ Basic Places API используется
- ❌ **Places Insights API НЕ используется**
- ❌ **Visitor analytics НЕ реализованы**

**Что нужно сделать:**
1. Изучить Google Places Insights API
2. Реализовать visitor analytics
3. Добавить в Cultural & Social scoring

---

### 9. 🔴 Medical Capabilities Verification

**Требование из ТЗ:**
- Condition-specific care match
- Staff qualifications verification
- Care protocols analysis
- Medical capabilities score (0-30 points)

**Текущий статус:**
- ❌ **Medical matching НЕ реализован**
- ❌ **Только базовый care_type matching**

**Что нужно сделать:**
1. Реализовать детальный medical capabilities matching
2. Интегрировать с CQC registration data
3. Добавить в PROFESSIONAL Report

---

### 10. 🔴 CQC Historical Compliance Analysis

**Требование из ТЗ:**
- Historical CQC ratings trends
- Compliance history analysis
- CQC Compliance score (0-20 points)

**Текущий статус:**
- ✅ CQC API Client существует
- ✅ CQC changes endpoint есть (`/api/cqc/changes`)
- ❌ **Historical analysis НЕ реализован**
- ❌ **Trends calculation НЕ реализован**

**Что нужно сделать:**
1. Реализовать CQC historical data fetching
2. Рассчитать trends (improving/declining)
3. Добавить в CQC Compliance scoring

---

## 📊 Сводная таблица

| Компонент | FREE Report | PROFESSIONAL Report | Статус |
|-----------|------------|---------------------|--------|
| 50-point matching | ✅ | N/A | ✅ Реализовано |
| 156-point matching | N/A | ❌ | ❌ Не реализовано |
| CQC API | ✅ | ✅ | ✅ Реализовано |
| Google Places API | ✅ | ✅ | ✅ Реализовано |
| FSA FHRS API | ❌ | ✅ | ⚠️ Client есть, не интегрирован |
| Companies House API | ❌ | ✅ | ⚠️ Client есть, не интегрирован |
| Autumna API | ❌ | ✅ | ⚠️ Client есть, не интегрирован |
| Glassdoor API | N/A | ❌ | ❌ Не реализовано |
| LinkedIn API | N/A | ❌ | ❌ Не реализовано |
| Google Places Insights | N/A | ❌ | ❌ Не реализовано |
| Medical Capabilities | N/A | ❌ | ❌ Не реализовано |
| CQC Historical | N/A | ❌ | ❌ Не реализовано |
| Backend PDF (WeasyPrint) | ❌ | ✅ | ❌ Не реализовано |
| S3 Upload | ❌ | ✅ | ❌ Не реализовано |
| Email (SendGrid) | ❌ | ✅ | ❌ Не реализовано |

---

## 🎯 Приоритеты реализации

### Phase 1: FREE Report Completion (Week 1-2)
1. **FSA FHRS интеграция** - добавить в FREE Report
2. **Autumna pricing** - использовать для получения цен
3. **Backend PDF генерация** - WeasyPrint + S3 + Email

### Phase 2: PROFESSIONAL Report Foundation (Week 3-4)
4. **156-point matching algorithm** - базовый алгоритм
5. **Companies House integration** - financial stability scoring
6. **CQC Historical analysis** - trends calculation

### Phase 3: PROFESSIONAL Report Advanced (Week 5-6)
7. **Google Places Insights** - visitor analytics
8. **Medical Capabilities** - detailed matching
9. **Staff Quality** - Glassdoor/LinkedIn (если возможно)

---

## 📝 Рекомендации

1. **Начать с FREE Report доработки:**
   - FSA и Autumna уже имеют API clients, нужно только интегрировать
   - Backend PDF можно реализовать параллельно

2. **PROFESSIONAL Report:**
   - Начать с 156-point алгоритма (расширение 50-point)
   - Добавлять data sources постепенно
   - Некоторые источники (Glassdoor, LinkedIn) могут требовать scraping вместо API

3. **Медицинский матчинг:**
   - Это отдельная большая задача
   - Требует детального анализа CQC registration data
   - Может потребовать дополнительных источников данных

---

**Вывод:** Основная работа по FREE Report почти завершена, но нужно интегрировать FSA и Autumna. PROFESSIONAL Report требует значительной дополнительной работы, особенно по 156-point алгоритму и дополнительным data sources.


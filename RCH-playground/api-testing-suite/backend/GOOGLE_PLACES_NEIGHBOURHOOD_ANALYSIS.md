# Google Places & Neighbourhood Analysis - Usage Analysis

## 📋 Обзор

Анализ использования Google Places New API и Neighbourhood Explorer логики для обогащения данных топ-5 домов в профессиональном отчете.

---

## ✅ Google Places New API

### Статус: ✅ ИСПОЛЬЗУЕТСЯ для топ-5 домов

**Файл:** `routers/report_routes.py`  
**Строки:** 1723-1808

**Реализация:**
```python
# STEP: Enrich Google Places data for all homes (parallel) - uses GooglePlacesEnrichmentService
print(f"STEP: GOOGLE PLACES API ENRICHMENT (Sections 10, 11, 15, 16)")

# Prepare Google Places enrichment tasks
google_places_enrichment_tasks = {}
for scored in top_5_homes:  # ✅ ТОЛЬКО для топ-5 домов
    home = scored['home']
    # ... подготовка данных ...
    google_places_enrichment_tasks[home_name] = {...}

# Execute Google Places enrichment in parallel
google_places_enriched_data = await enrich_all_google_places()
```

**Используется для:**
- **Section 10:** Community Reputation (Google Reviews, Rating)
- **Section 11:** Social Activities & Engagement
- **Section 15:** Location & Accessibility
- **Section 16:** Nearby Amenities

**Сервис:** `GooglePlacesEnrichmentService`
- Использует Google Places API (New API)
- Кэширование: 24 часа (86400 секунд)
- Параллельное выполнение для всех топ-5 домов

**Данные, которые получаются:**
- `rating` - Google рейтинг
- `user_ratings_total` - количество отзывов
- `reviews` - детальные отзывы
- `sentiment_analysis` - анализ тональности
- `insights` - Google Places Insights (если доступно)
- `formatted_address` - адрес
- `formatted_phone_number` - телефон
- `website` - веб-сайт
- `photo_url` - фото

---

## ✅ Neighbourhood Analysis (Neighbourhood Explorer Logic)

### Статус: ✅ ИСПОЛЬЗУЕТСЯ для топ-5 домов

**Файл:** `routers/report_routes.py`  
**Строки:** 2050-2125

**Реализация:**
```python
# STEP: Enrich Neighbourhood data for all homes (parallel)
print(f"STEP: NEIGHBOURHOOD ANALYSIS ENRICHMENT (Section 18 - Location Wellbeing)")

neighbourhood_enrichment_tasks = {}
for scored in top_5_homes:  # ✅ ТОЛЬКО для топ-5 домов
    home = scored['home']
    if home_postcode:
        neighbourhood_enrichment_tasks[home_name] = {
            'home_name': home_name,
            'postcode': home_postcode,
            'latitude': home_lat,
            'longitude': home_lon
        }

# Execute Neighbourhood enrichment
neighbourhood_enriched_data = await enrich_all_neighbourhood()
```

**Используется для:**
- **Section 18:** Location Wellbeing (Location Wellbeing Analysis)
- **Section 11:** Safety Analysis (частично)
- **Section 15:** Area Map (частично)

**Сервис:** `NeighbourhoodAnalyzer` (из `data_integrations/batch_processor.py`)

**Источники данных:**
- ✅ **ONS (Office for National Statistics)** - включен
  - Wellbeing scores
  - Economic indicators
  - Demographics
  - Geography data
  
- ✅ **OSM (OpenStreetMap)** - включен
  - Walk score
  - Nearby amenities
  - Accessibility
  
- ❌ **OS Places** - отключен (`include_os_places=False`)
  - Причина: "Skip for speed"
  
- ❌ **NHSBSA** - отключен (`include_nhsbsa=False`)
  - Причина: "Temporarily disabled"
  
- ❌ **Environmental** - отключен (`include_environmental=False`)
  - Причина: "Skip for speed"

**Параметры вызова:**
```python
analyzer.analyze(
    postcode=task_data['postcode'],
    lat=task_data['latitude'],
    lon=task_data['longitude'],
    include_os_places=False,      # Отключено для скорости
    include_ons=True,              # ✅ Включено
    include_osm=True,              # ✅ Включено
    include_nhsbsa=False,          # Отключено (временно)
    include_environmental=False    # Отключено для скорости
)
```

**Timeout:** 15 секунд на дом

---

## 🔍 Сравнение: Neighbourhood Explorer vs Report Routes

### Neighbourhood Explorer (Frontend)

**Компонент:** `frontend/src/features/neighbourhood/NeighbourhoodExplorer.tsx`

**API Endpoint:** `/api/neighbourhood/analyze` (предположительно)

**Источники данных (по умолчанию):**
- ✅ OS Places: `include_os_places: true`
- ✅ ONS: `include_ons: true`
- ✅ OSM: `include_osm: true`
- ✅ NHSBSA: `include_nhsbsa: true`
- ❌ Environmental: `include_environmental: false` (disabled by default)

### Report Routes (Backend)

**Сервис:** `NeighbourhoodAnalyzer.analyze()`

**Источники данных (текущие):**
- ❌ OS Places: `include_os_places: False` ⚠️ **ОТЛИЧИЕ**
- ✅ ONS: `include_ons: True`
- ✅ OSM: `include_osm: True`
- ❌ NHSBSA: `include_nhsbsa: False` ⚠️ **ОТЛИЧИЕ**
- ❌ Environmental: `include_environmental: False`

---

## ⚠️ Обнаруженные различия

### 1. OS Places отключен в Report Routes

**В Neighbourhood Explorer:**
- `include_os_places: true` - включен

**В Report Routes:**
- `include_os_places: False` - отключен
- Комментарий: "Skip for speed"

**Влияние:**
- Отсутствуют точные координаты из OS Places
- Отсутствует UPRN (Unique Property Reference Number)
- Отсутствуют детальные адресные данные

**Рекомендация:**
- OS Places - быстрый API (бесплатный)
- Можно включить для топ-5 домов без значительного влияния на скорость

### 2. NHSBSA отключен в Report Routes

**В Neighbourhood Explorer:**
- `include_nhsbsa: true` - включен

**В Report Routes:**
- `include_nhsbsa: False` - отключен
- Комментарий: "Temporarily disabled"

**Влияние:**
- Отсутствуют данные о здоровье населения
- Отсутствуют данные о доступе к GP
- Отсутствуют данные о NHS services

**Рекомендация:**
- NHSBSA может быть медленным API
- Для топ-5 домов можно включить, но с timeout

---

## 📊 Текущая архитектура

### Уровень 1: Матчинг (топ-30 кандидатов)
- ❌ Google Places - **НЕ используется** (только для топ-5)
- ❌ Neighbourhood Analysis - **НЕ используется** (только для топ-5)
- ✅ CQC API - используется (бесплатный)
- ✅ Companies House - используется (бесплатный)
- ✅ FSA API - **НЕ используется** (только для топ-5)

### Уровень 2: Финальный отчет (топ-5 домов)
- ✅ Google Places - **ИСПОЛЬЗУЕТСЯ**
- ✅ Neighbourhood Analysis - **ИСПОЛЬЗУЕТСЯ**
- ✅ CQC API - используется
- ✅ Companies House - используется
- ✅ FSA API - используется
- ✅ Staff Quality (Perplexity) - используется

---

## ✅ Выводы

### Google Places New API
- ✅ **Используется** для топ-5 домов
- ✅ Правильно интегрирован через `GooglePlacesEnrichmentService`
- ✅ Кэширование работает (24 часа)
- ✅ Параллельное выполнение

### Neighbourhood Analysis
- ✅ **Используется** для топ-5 домов
- ✅ Использует `NeighbourhoodAnalyzer` (та же логика, что и Explorer)
- ⚠️ **Отличия в источниках данных:**
  - OS Places отключен (в Explorer включен)
  - NHSBSA отключен (в Explorer включен)
- ✅ ONS и OSM включены (как в Explorer)

---

## 🎯 Рекомендации

### 1. Включить OS Places для топ-5 домов
**Причина:** Быстрый API, улучшает качество данных
```python
include_os_places=True,  # Включить для топ-5
```

### 2. Рассмотреть включение NHSBSA для топ-5 домов
**Причина:** Важные данные о здоровье, но может быть медленным
```python
include_nhsbsa=True,  # Включить с timeout
```

### 3. Оставить Environmental отключенным
**Причина:** Медленный API, не критично для отчета

---

## 📝 Итоговая таблица

| API/Источник | Neighbourhood Explorer | Report Routes (Top-5) | Статус |
|--------------|------------------------|----------------------|--------|
| **Google Places** | N/A (не используется) | ✅ Используется | ✅ Правильно |
| **OS Places** | ✅ Включен | ❌ Отключен | ⚠️ Различие |
| **ONS** | ✅ Включен | ✅ Включен | ✅ Совпадает |
| **OSM** | ✅ Включен | ✅ Включен | ✅ Совпадает |
| **NHSBSA** | ✅ Включен | ❌ Отключен | ⚠️ Различие |
| **Environmental** | ❌ Отключен | ❌ Отключен | ✅ Совпадает |

---

**Дата анализа:** 2025-01-XX  
**Статус:** ✅ Google Places используется, ⚠️ Neighbourhood Analysis используется с ограничениями


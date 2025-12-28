# Анализ Пропущенных Enrichment Services

**Дата анализа:** 2025-01-XX  
**Статус:** 🔍 Анализ завершен

---

## 📋 Executive Summary

После изучения старой версии профессионального отчета обнаружены **2 критических enrichment services**, которые были пропущены:

1. ✅ **CQC Deep Dive Enrichment** - детальный анализ CQC данных
2. ✅ **Neighbourhood/Area Analysis Enrichment** - анализ близлежащей территории

---

## 1. CQC Deep Dive Enrichment Service

### Статус: ❌ ПРОПУЩЕН

### Описание:
CQC Deep Dive предоставляет расширенный анализ данных Care Quality Commission, включая:
- История инспекций (5+ лет)
- Enforcement actions (предупреждения, условия)
- Provider-level pattern detection
- Rating trends (Improving/Stable/Declining)
- Regulated activities детальный анализ

### Использование в отчете:
- **Section 6:** Safety Analysis (CQC Deep Dive)
- **Section 8:** Medical Care Analysis (CQC ratings)
- **Matching Algorithm:** CQC compliance scoring

### Источники данных:
- **CQC API Client** (`api_clients/cqc_client.py`)
  - `get_location_inspection_history(location_id)` - история инспекций
  - `get_location_enforcement_actions(location_id)` - enforcement actions
  - `get_provider_locations(provider_id)` - все локации провайдера
  - `get_location_historical_ratings(location_id)` - исторические рейтинги

### Структура данных (из Python):
```python
@dataclass
class CQCDeepDive:
    # Current Ratings (6 доменов)
    overall: str  # "Outstanding" / "Good" / "Requires improvement" / "Inadequate"
    safe: str
    effective: str
    caring: str
    responsive: str
    well_led: str
    
    # Dates
    last_inspection_date: Optional[date]
    publication_date: Optional[date]
    report_url: Optional[str]
    
    # Regulated Activities
    regulated_activities: List[RegulatedActivity]
    
    # License flags
    has_nursing_care_license: bool
    has_personal_care_license: bool
    has_surgical_procedures_license: bool
    has_treatment_license: bool
    has_diagnostic_license: bool
    
    # Derived
    days_since_inspection: Optional[int]
    rating_trend: str  # "Improving" / "Stable" / "Declining" / "Insufficient data"
    
    # Enrichment from CQC API
    inspection_history: List[Dict[str, Any]]  # Full history 5+ years
    enforcement_actions: List[Dict[str, Any]]  # Warning notices, conditions
    provider_locations: Optional[List[Dict[str, Any]]]  # All provider locations
```

### Файлы в старой версии:
- `services/cqc_deep_dive_service.py` - основной сервис
- `api_clients/cqc_client.py` - CQC API клиент
- `routers/report_routes.py` - строки 1583-1721 (enrichment вызов)

### Необходимые компоненты для реализации:
1. **CQC API Client** (TypeScript)
   - Аутентификация через API key
   - Методы для получения inspection history, enforcement actions, provider locations
   - Rate limiting и retry механизмы

2. **CQC Deep Dive Service** (TypeScript)
   - Расчет rating trend
   - Парсинг regulated activities
   - Объединение данных из БД и API

3. **Интеграция в EnrichmentOrchestrator**
   - Добавить в список services
   - Настроить параллельную загрузку

---

## 2. Neighbourhood/Area Analysis Enrichment Service

### Статус: ❌ ПРОПУЩЕН

### Описание:
Neighbourhood Analysis предоставляет комплексный анализ близлежащей территории care home, включая:
- **OS Places** (Ordnance Survey) - координаты, UPRN, адреса
- **ONS** (Office for National Statistics) - wellbeing, demographics, economics
- **OpenStreetMap (OSM)** - walkability, amenities, parks, transport
- **NHSBSA** - health profiles, GP practices
- **Environmental** - noise, pollution (опционально)

### Использование в отчете:
- **Section 18:** Location Wellbeing Analysis
  - Walkability score
  - Green space score
  - Noise level
  - Local amenities
  - Social wellbeing (ONS)
  
- **Section 19:** Area Map (POI - Points of Interest)
  - Nearby GPs (NHSBSA)
  - Nearby parks (OSM)
  - Nearby shops, pharmacies (OSM)
  - Nearest hospital, transport (OSM)
  - Walkability infrastructure

### Источники данных:

#### 2.1 OS Places (Ordnance Survey)
- **API:** OS Places API (`https://api.os.uk/places/v1`)
- **Данные:**
  - Coordinates (latitude, longitude)
  - UPRN (Unique Property Reference Number)
  - Address details
  - Postcode resolution
- **Файл в старой версии:** `data_integrations/os_places_loader.py`

#### 2.2 ONS (Office for National Statistics)
- **API:** ONS API
- **Данные:**
  - Wellbeing scores
  - Economic indicators
  - Demographics (over 65%, etc.)
  - LSOA (Lower Layer Super Output Area) codes
  - Local authority data
- **Файл в старой версии:** `data_integrations/ons_loader.py`

#### 2.3 OpenStreetMap (OSM)
- **API:** Overpass API или Nominatim
- **Данные:**
  - Walkability score
  - Nearby amenities (parks, shops, pharmacies, hospitals)
  - Public transport (bus stops, train stations)
  - Infrastructure (roads, accessibility)
- **Файл в старой версии:** `data_integrations/osm_loader.py`

#### 2.4 NHSBSA (NHS Business Services Authority)
- **API:** NHSBSA API
- **Данные:**
  - Health profiles
  - GP practices nearby
  - Prescribing patterns
- **Файл в старой версии:** `data_integrations/nhsbsa_loader.py`

#### 2.5 Environmental Analyzer
- **API:** OS Features API (опционально)
- **Данные:**
  - Noise levels
  - Pollution data
  - Major roads nearby
- **Файл в старой версии:** `data_integrations/environmental_analyzer.py`

### Структура данных (из Python NeighbourhoodAnalyzer):
```typescript
interface NeighbourhoodAnalysis {
  postcode: string;
  coordinates: {
    latitude: number;
    longitude: number;
  };
  
  // OS Places
  os_places?: {
    uprn?: string;
    address?: string;
    centroid?: {
      latitude: number;
      longitude: number;
    };
  };
  
  // ONS Data
  social?: {
    geography: {
      lsoa_code: string;
      local_authority: string;
    };
    wellbeing: {
      score: number; // 0-100
      rating: 'Excellent' | 'Good' | 'Average' | 'Poor';
    };
    economic: {
      score: number;
      rating: string;
    };
    demographics: {
      over_65_percent: number;
    };
  };
  
  // OSM Data
  walkability?: {
    score: number; // 0-100
    rating: string;
    care_home_relevance: {
      score: number;
      rating: string;
    };
  };
  
  osm?: {
    amenities: {
      by_category: {
        parks: Array<{
          name: string;
          coordinates: { lat: number; lng: number };
          distance_m: number;
        }>;
        shopping: Array<{...}>;
        healthcare: Array<{...}>;
      };
    };
    infrastructure: {
      public_transport: {
        bus_stops_800m: Array<{...}>;
        rail_stations_1600m: Array<{...}>;
      };
    };
  };
  
  // NHSBSA Data
  health?: {
    index: {
      score: number;
      rating: string;
    };
    practices_nearby: number;
    nearest_practices: Array<{
      name: string;
      coordinates: { lat: number; lng: number };
      distance_km: number;
    }>;
  };
  
  // Environmental (опционально)
  environmental?: {
    noise_level: {
      score: number; // 0-100 (lower is better)
      rating: string;
    };
    major_roads_nearby: boolean;
  };
  
  // Overall
  overall?: {
    score: number; // 0-100
    rating: string;
    breakdown: Array<{
      name: string;
      score: number;
      weight: string;
    }>;
  };
}
```

### Файлы в старой версии:
- `data_integrations/batch_processor.py` - `NeighbourhoodAnalyzer` класс
- `routers/neighbourhood_routes.py` - API endpoints
- `routers/report_routes.py` - строки 2050-2125 (enrichment вызов)

### Необходимые компоненты для реализации:
1. **OS Places Client** (TypeScript)
   - Аутентификация через API key
   - Postcode resolution
   - Address lookup by coordinates
   - UPRN lookup

2. **ONS Client** (TypeScript)
   - LSOA lookup
   - Wellbeing data fetching
   - Demographics data

3. **OSM Client** (TypeScript)
   - Overpass API или Nominatim integration
   - Amenities search
   - Walkability calculation
   - Public transport search

4. **NHSBSA Client** (TypeScript)
   - GP practices search
   - Health profiles

5. **Environmental Analyzer** (TypeScript, опционально)
   - Noise level calculation
   - Road proximity analysis

6. **Neighbourhood Analysis Service** (TypeScript)
   - Объединение данных из всех источников
   - Расчет composite scores
   - Форматирование для отчета

7. **Интеграция в EnrichmentOrchestrator**
   - Добавить в список services
   - Настроить параллельную загрузку

---

## 📊 Сравнительная таблица

| Enrichment Service | Статус | Используется в секциях | Приоритет |
|-------------------|--------|------------------------|-----------|
| FSA Enrichment | ✅ Реализован | Section 7 | High |
| Financial Enrichment | ✅ Реализован | Section 12 | High |
| Google Places Enrichment | ✅ Реализован | Sections 10, 11, 15, 16 | High |
| Staff Enrichment | ✅ Реализован | Section 9 | High |
| **CQC Deep Dive** | ❌ **Пропущен** | **Sections 6, 8** | **Critical** |
| **Neighbourhood Analysis** | ❌ **Пропущен** | **Sections 18, 19** | **Critical** |

---

## 🎯 План реализации

### Шаг 6.1: CQC Deep Dive Enrichment Service
1. Создать `lib/data-engine/enrichment/services/cqc-client.ts`
2. Создать `lib/data-engine/enrichment/services/cqc.ts`
3. Добавить unit тесты
4. Интегрировать в `EnrichmentOrchestrator`

### Шаг 6.2: Neighbourhood Analysis Enrichment Service
1. Создать клиенты для каждого источника:
   - `lib/data-engine/enrichment/services/os-places-client.ts`
   - `lib/data-engine/enrichment/services/ons-client.ts`
   - `lib/data-engine/enrichment/services/osm-client.ts`
   - `lib/data-engine/enrichment/services/nhsbsa-client.ts`
   - `lib/data-engine/enrichment/services/environmental-client.ts` (опционально)
2. Создать `lib/data-engine/enrichment/services/neighbourhood.ts`
3. Добавить unit тесты
4. Интегрировать в `EnrichmentOrchestrator`

### Шаг 6.3: Обновление EnrichmentOrchestrator
1. Добавить новые services в список
2. Обновить типы и интерфейсы
3. Обновить документацию

---

## 📝 Примечания

1. **CQC Deep Dive** критически важен для Sections 6 и 8, так как предоставляет детальную информацию о безопасности и медицинском уходе.

2. **Neighbourhood Analysis** критически важен для Sections 18 и 19, так как предоставляет информацию о локации и близлежащих удобствах.

3. Оба enrichment services используются в **matching algorithm** для расчета scores.

4. В старой версии эти enrichment services вызываются **параллельно** для топ-5 домов после матчинга.

5. **OS Places** может быть отключен для скорости (`include_os_places=False`), но рекомендуется включить для топ-5 домов.

---

## ✅ Следующие шаги

1. Реализовать CQC Deep Dive Enrichment Service
2. Реализовать Neighbourhood Analysis Enrichment Service
3. Интегрировать в EnrichmentOrchestrator
4. Обновить Professional Report Generator для использования новых enrichment данных
5. Добавить unit тесты
6. Обновить документацию




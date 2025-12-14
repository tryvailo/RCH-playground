# Professional Report - Отсутствующие UI Компоненты

**Дата:** 2025-01-XX  
**Статус:** ⚠️ ТРЕБУЕТСЯ РЕАЛИЗАЦИЯ

## Резюме

После реализации Phase 2 (улучшение бэкенда), мы добавили множество новых полей данных, но они **не отображаются** в интерфейсе. Нужно создать/обновить React компоненты для отображения этих данных.

---

## ✅ Что УЖЕ отображается

### Executive Summary
- ✅ Match Score
- ✅ Weekly Price
- ✅ CQC Rating
- ✅ Key Strengths
- ✅ Why Chosen
- ❌ **ОТСУТСТВУЕТ:** `matchReason` (улучшенная причина совпадения)
- ❌ **ОТСУТСТВУЕТ:** `waitingListStatus` (статус очереди)

### Care Home Details
- ✅ FSA Detailed Ratings
- ✅ Financial Stability
- ✅ Google Places Insights (NEW API)
- ✅ CQC Deep Dive
- ✅ Match Score Radar Chart
- ❌ **ОТСУТСТВУЕТ:** `communityReputation` (Section 10)
- ❌ **ОТСУТСТВУЕТ:** `safetyAnalysis` (Section 6)
- ❌ **ОТСУТСТВУЕТ:** `locationWellbeing` (Section 18)
- ❌ **ОТСУТСТВУЕТ:** `areaMap` (Section 19)
- ❌ **ОТСУТСТВУЕТ:** `medicalCare` (Section 8)
- ❌ **ОТСУТСТВУЕТ:** `comfortLifestyle` (Section 16)
- ❌ **ОТСУТСТВУЕТ:** `lifestyleDeepDive` (Section 17)

### Action Plan (Next Steps)
- ✅ Recommended Actions (хардкод)
- ✅ Questions for Home Manager
- ❌ **ОТСУТСТВУЕТ:** `peakVisitingHours` из Google Places
- ❌ **ОТСУТСТВУЕТ:** `localAuthority` из ONS

### Funding Options
- ✅ CHC Eligibility
- ✅ LA Funding
- ✅ Fair Cost Gap Analysis (базовое)
- ❌ **ОТСУТСТВУЕТ:** улучшенные MSIF data детали
- ❌ **ОТСУТСТВУЕТ:** local authority contact info

### Appendix
- ❌ **ОТСУТСТВУЕТ:** `appendix` секция полностью

---

## ❌ Что НУЖНО добавить

### 1. Executive Summary - Новые поля

**Файл:** `components/ExecutiveSummaryDashboard.tsx` или `ProfessionalReportViewer.tsx`

**Добавить отображение:**
- `home.matchReason` - улучшенная причина совпадения (текст)
- `home.waitingListStatus` - статус очереди ("Available now", "2-4 weeks", "3+ months")

**Пример:**
```tsx
{home.matchReason && (
  <div className="mt-2 p-2 bg-blue-50 rounded">
    <p className="text-sm font-semibold">Match Reason:</p>
    <p className="text-sm text-gray-700">{home.matchReason}</p>
  </div>
)}
{home.waitingListStatus && (
  <div className="mt-2">
    <span className="text-xs text-gray-500">Availability: </span>
    <span className={`text-xs font-semibold ${
      home.waitingListStatus === 'Available now' ? 'text-green-600' :
      home.waitingListStatus === '2-4 weeks' ? 'text-yellow-600' :
      'text-red-600'
    }`}>
      {home.waitingListStatus}
    </span>
  </div>
)}
```

---

### 2. Section 10: Community Reputation

**Файл:** Создать `components/CommunityReputationSection.tsx`

**Данные:** `home.communityReputation`

**Структура данных:**
```typescript
{
  google_rating: number;
  google_review_count: number;
  carehome_rating: number;
  trust_score: number;
  sentiment_analysis: {
    average_sentiment: number;
    sentiment_label: string;
    total_reviews: number;
    positive_reviews: number;
    negative_reviews: number;
    sentiment_distribution: { positive, negative, neutral }
  };
  sample_reviews: Array<{
    text: string;
    rating: number;
    author: string;
    source: string;
    date: string;
  }>;
}
```

**Что отображать:**
- Trust Score (0-100)
- Sentiment Analysis (график/таблица)
- Sample Reviews (топ 5)
- Google Rating vs CareHome.co.uk Rating

---

### 3. Section 6: Safety Analysis

**Файл:** Создать `components/SafetyAnalysisSection.tsx`

**Данные:** `home.safetyAnalysis`

**Структура данных:**
```typescript
{
  safety_score: number;
  safety_rating: string;
  pedestrian_safety: string;
  public_transport: {
    nearest_bus_stop: { distance, name };
    nearest_train_station: { distance, name };
  };
  accessibility: {
    wheelchair_accessible: boolean;
    accessible_entrances: number;
  };
}
```

**Что отображать:**
- Safety Score и Rating
- Pedestrian Safety
- Public Transport доступность
- Accessibility features

---

### 4. Section 18: Location Wellbeing

**Файл:** Создать `components/LocationWellbeingSection.tsx`

**Данные:** `home.locationWellbeing`

**Структура данных:**
```typescript
{
  walkability_score: number;
  green_space_score: number;
  nearest_park_distance: number;
  noise_level: string;
  local_amenities: Array<{ type, name, distance }>;
}
```

**Что отображать:**
- Walkability Score (0-100)
- Green Space Score
- Nearest Park
- Noise Level
- Local Amenities (список)

---

### 5. Section 19: Area Map

**Файл:** Создать `components/AreaMapSection.tsx`

**Данные:** `home.areaMap`

**Структура данных:**
```typescript
{
  nearby_gps: Array<{ name, distance, address }>;
  nearby_parks: Array<{ name, distance }>;
  nearby_shops: Array<{ name, distance, type }>;
  nearby_pharmacies: Array<{ name, distance }>;
  nearest_hospital: { name, distance };
  nearest_bus_stop: { name, distance };
  nearest_train_station: { name, distance };
}
```

**Что отображать:**
- Интерактивная карта (Google Maps или Leaflet)
- POI markers (GPs, parks, shops, pharmacies, hospitals, transport)
- Список ближайших объектов с расстояниями

---

### 6. Section 8: Medical Care

**Файл:** Создать `components/MedicalCareSection.tsx`

**Данные:** `home.medicalCare`

**Структура данных:**
```typescript
{
  medical_specialisms: string[];
  regulated_activities: string[];
  care_residential: boolean;
  care_nursing: boolean;
  care_dementia: boolean;
  service_types: string[];
}
```

**Что отображать:**
- Medical Specialisms (список)
- Regulated Activities
- Care Types (badges)
- Service Types

---

### 7. Section 16: Comfort & Lifestyle

**Файл:** Создать `components/ComfortLifestyleSection.tsx`

**Данные:** `home.comfortLifestyle`

**Структура данных:**
```typescript
{
  facilities: {
    general_amenities: string[];
    medical_facilities: string[];
    social_facilities: string[];
    safety_features: string[];
    outdoor_spaces: string[];
  };
  activities: {
    daily_activities: string[];
    weekly_programs: string[];
    therapy_programs: string[];
    outings: string[];
    weekly_activities_count: number;
    outings_per_month: number;
  };
  nutrition: {
    dietary_options: string[];
    dietary_options_by_category: object;
  };
  private_room_percentage: number;
  ensuite_availability: boolean;
  wheelchair_accessible: boolean;
  outdoor_space_description: string;
  wifi_available: boolean;
  parking_onsite: boolean;
  secure_garden: boolean;
  room_photos: string[];
}
```

**Что отображать:**
- Facilities (категории)
- Activities (списки)
- Nutrition options
- Room photos (галерея)
- Accessibility features

---

### 8. Section 17: Lifestyle Deep Dive

**Файл:** Создать `components/LifestyleDeepDiveSection.tsx`

**Данные:** `home.lifestyleDeepDive`

**Структура данных:**
```typescript
{
  daily_schedule: Array<{ time, activity }>;
  activity_categories: string[];
  visiting_hours: string;
  personalization: string;
  policies: Array<{ title, description }>;
  activities_summary: string;
}
```

**Что отображать:**
- Daily Schedule (timeline)
- Activity Categories
- Visiting Hours
- Personalization description
- Policies (список)

---

### 9. Action Plan - Улучшения

**Файл:** `ProfessionalReportViewer.tsx` (секция Next Steps)

**Исправить:**
- Использовать `report.nextSteps.recommendedActions[].peakVisitingHours` вместо хардкода
- Использовать `report.nextSteps.recommendedActions[].localAuthority` вместо хардкода
- Использовать `report.nextSteps.localAuthority` для контекста

**Текущий код (строка ~1704):**
```tsx
// Хардкод - нужно заменить на данные из report.nextSteps
let action = '';
let timeline = 'Within 2 weeks';
```

**Нужно заменить на:**
```tsx
{report.nextSteps?.recommendedActions?.map((actionItem, index) => (
  <div key={index}>
    <p>{actionItem.action}</p>
    {actionItem.peakVisitingHours && (
      <p className="text-xs text-gray-500">
        Best times: {actionItem.peakVisitingHours.join(', ')}
      </p>
    )}
    {actionItem.localAuthority && (
      <p className="text-xs text-gray-500">
        Local Authority: {actionItem.localAuthority}
      </p>
    )}
  </div>
))}
```

---

### 10. Funding Options - Улучшения

**Файл:** `ProfessionalReportViewer.tsx` (секция Funding Optimization)

**Добавить отображение:**
- `report.fairCostGapAnalysis.msif_data` - детали MSIF
- `report.fairCostGapAnalysis.local_authority_info` - контактная информация
- `report.fairCostGapAnalysis.why_gap_exists.msif_context` - контекст MSIF

---

### 11. Appendix - Полная секция

**Файл:** Создать `components/AppendixSection.tsx`

**Данные:** `report.appendix`

**Структура данных:**
```typescript
{
  data_sources: Array<{
    name: string;
    description: string;
    data_types: string[];
    update_frequency: string;
    official_url: string;
    last_update: {
      cached_entries?: number;
      cache_hits?: number;
      status: string;
    };
  }>;
  cache_statistics: {
    total_cached_entries: number;
    valid_entries: number;
    expired_entries: number;
    cache_size_mb: number;
    sources_with_cache: number;
  };
  report_metadata: {
    generated_at: string;
    report_id: string;
    total_sources: number;
    data_quality_note: string;
  };
}
```

**Что отображать:**
- Список всех источников данных с описаниями
- Last update dates из cache stats
- Cache statistics
- Report metadata

---

## 📋 Обновление типов

**Файл:** `types.ts`

**Добавить в `ProfessionalCareHome`:**
```typescript
matchReason?: string;
waitingListStatus?: string;
communityReputation?: {
  google_rating: number;
  google_review_count: number;
  carehome_rating?: number;
  trust_score: number;
  sentiment_analysis: {...};
  sample_reviews: Array<{...}>;
};
safetyAnalysis?: {
  safety_score: number;
  safety_rating: string;
  pedestrian_safety: string;
  public_transport: {...};
  accessibility: {...};
};
locationWellbeing?: {
  walkability_score: number;
  green_space_score: number;
  nearest_park_distance: number;
  noise_level: string;
  local_amenities: Array<{...}>;
};
areaMap?: {
  nearby_gps: Array<{...}>;
  nearby_parks: Array<{...}>;
  nearby_shops: Array<{...}>;
  nearby_pharmacies: Array<{...}>;
  nearest_hospital: {...};
  nearest_bus_stop: {...};
  nearest_train_station: {...};
};
medicalCare?: {
  medical_specialisms: string[];
  regulated_activities: string[];
  care_residential: boolean;
  care_nursing: boolean;
  care_dementia: boolean;
  service_types: string[];
};
comfortLifestyle?: {
  facilities: {...};
  activities: {...};
  nutrition: {...};
  private_room_percentage: number;
  ensuite_availability: boolean;
  wheelchair_accessible: boolean;
  // ... и т.д.
};
lifestyleDeepDive?: {
  daily_schedule: Array<{...}>;
  activity_categories: string[];
  visiting_hours: string;
  personalization: string;
  policies: Array<{...}>;
  activities_summary: string;
};
```

**Добавить в `NextSteps`:**
```typescript
recommendedActions: Array<{
  homeName: string;
  homeRank: number;
  action: string;
  timeline: string;
  priority: 'high' | 'medium' | 'low';
  peakVisitingHours?: string[];  // НОВОЕ
  localAuthority?: string;       // НОВОЕ
}>;
localAuthority?: string;  // НОВОЕ
```

**Добавить в `FairCostGapAnalysis`:**
```typescript
local_authority_code?: string;  // НОВОЕ
region?: string;                // НОВОЕ
msif_data?: {                   // НОВОЕ
  fair_cost_weekly: number;
  source: string;
  year: string;
  care_type_display: string;
  local_authority_verified: boolean;
};
local_authority_info?: {        // НОВОЕ
  name: string;
  code?: string;
  region?: string;
  contact_note: string;
  website_hint: string;
};
why_gap_exists: {
  // ... существующие поля
  msif_context?: string;         // НОВОЕ
};
```

**Добавить в `ProfessionalReportData`:**
```typescript
appendix?: {                     // НОВОЕ
  data_sources: Array<{...}>;
  cache_statistics: {...};
  report_metadata: {...};
};
```

---

## 🎯 Приоритеты реализации

### 🔴 КРИТИЧЕСКИЙ ПРИОРИТЕТ
1. **Обновить типы** (`types.ts`) - добавить все новые поля
2. **Executive Summary** - добавить `matchReason` и `waitingListStatus`
3. **Action Plan** - использовать реальные данные вместо хардкода

### 🟡 ВЫСОКИЙ ПРИОРИТЕТ
4. **Community Reputation** (Section 10) - компонент
5. **Medical Care** (Section 8) - компонент
6. **Comfort & Lifestyle** (Section 16) - компонент
7. **Lifestyle Deep Dive** (Section 17) - компонент

### 🟢 СРЕДНИЙ ПРИОРИТЕТ
8. **Safety Analysis** (Section 6) - компонент
9. **Location Wellbeing** (Section 18) - компонент
10. **Area Map** (Section 19) - компонент с картой
11. **Appendix** (Section 23) - компонент
12. **Funding Options** - улучшения MSIF data

---

## 📝 Заметки

- Все компоненты должны обрабатывать случаи, когда данные отсутствуют (fallback UI)
- Использовать существующие стили и паттерны из `ProfessionalReportViewer.tsx`
- Компоненты должны быть переиспользуемыми и модульными
- Добавить loading states для асинхронных данных (если нужно)

---

**Конец документа**


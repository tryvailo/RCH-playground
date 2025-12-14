# Static Data Documentation

This document describes all static/hardcoded data in the Free Report Viewer feature and how they relate to real data sources.

## Overview

All data in the Free Report should be calculated from real sources (databases, APIs) whenever possible. Static data is only used as fallback when:
1. Real data sources are unavailable
2. For development/testing purposes
3. As default values when specific data is missing

---

## 1. Frontend Static Data

### 1.1 Mock Care Homes (`useFreeReport.ts`)

**Location:** `api-testing-suite/frontend/src/features/free-report/hooks/useFreeReport.ts`

**Purpose:** Fallback data when backend API is unavailable

**Static Fields:**
- `name`: Mock care home names (Sunshine Care Home, Greenfield Manor, Elmwood House)
- `photo`: Unsplash placeholder images
- `address`, `city`, `postcode`: Mock addresses
- `features`: Hardcoded feature lists
- `why_this_home`: Template texts based on match_type (see below)

**When Used:**
- Backend API returns 404/500/network error
- Connection timeout (>30 seconds)
- All API calls fail

**Real Data Sources (when available):**
- Backend `/api/free-report` endpoint → Database (`care_homes` table) → CQC API → Google Places API → FSA FHRS API

---

### 1.2 `why_this_home` Text Templates

**Location:** `api-testing-suite/frontend/src/features/free-report/hooks/useFreeReport.ts` (lines 177-181)

**Current Implementation:**
```typescript
const whyTexts: Record<string, string> = {
  'Safe Bet': 'Excellent balance of price and quality. High CQC rating and close location make this home a safe choice.',
  'Best Value': 'Best price-to-quality ratio. Affordable price while maintaining high care standards.',
  'Premium': 'Premium option with outstanding CQC rating. Perfect choice for those seeking the highest quality of care.',
};
```

**Status:** ⚠️ **STATIC TEMPLATES** - Should be generated from real data

**How It Should Work:**
1. **Backend generates** `why_this_home` based on:
   - Actual CQC rating
   - Actual distance
   - Actual price vs budget
   - Actual features
   - Match type (Safe Bet/Best Value/Premium)
2. **Frontend uses** backend-provided text if available, falls back to templates

**Recommended Backend Implementation:**
```python
def generate_why_this_home(home: Dict, match_type: str, user_budget: float) -> str:
    """Generate explanation text based on real home data"""
    reasons = []
    
    if home.get('rating') in ['Outstanding', 'Good']:
        reasons.append(f"High CQC rating ({home['rating']})")
    
    if home.get('distance_km', 999) < 5:
        reasons.append(f"close location ({home['distance_km']:.1f} km)")
    
    if home.get('weekly_cost', 0) <= user_budget:
        reasons.append("within your budget")
    elif home.get('weekly_cost', 0) <= user_budget * 1.1:
        reasons.append("slightly above budget but excellent value")
    
    if match_type == 'Safe Bet':
        return f"Safe choice with {', '.join(reasons)}."
    elif match_type == 'Best Value':
        return f"Best value option: {', '.join(reasons)}."
    elif match_type == 'Premium':
        return f"Premium care home with {', '.join(reasons)}."
    
    return "Recommended based on quality, price, and location."
```

---

### 1.3 MSIF Fallback Values

**Location:** `api-testing-suite/frontend/src/features/free-report/hooks/useFreeReport.ts` (lines 73-79)

**Static Values:**
```typescript
const fallbackValues: Record<string, number> = {
  residential: 700,
  nursing: 1048,
  residential_dementia: 800,
  nursing_dementia: 1048,
};
```

**When Used:**
- MSIF API (`/api/msif/fair-cost/{local_authority}`) fails
- Network error or timeout

**Real Data Source:**
- Database table `msif_fees_2025` → Column `fair_cost_gbp_week`
- Filtered by `local_authority` and `care_type`

**Status:** ✅ **CORRECT** - These are reasonable fallbacks based on typical MSIF values

---

### 1.4 Postcode → Local Authority Mapping

**Location:** `api-testing-suite/frontend/src/features/free-report/hooks/useFreeReport.ts` (lines 8-42)

**Static Mapping:**
```typescript
// London postcodes → Westminster
if (postcodeUpper.match(/^(SW|SE|NW|NE|E|W|N|WC|EC)/)) {
  return 'Westminster';
}
// Manchester → M
// Birmingham → B
// etc.
```

**When Used:**
- Frontend needs to call MSIF API before backend response
- Postcode resolver API unavailable

**Real Data Source:**
- Backend `postcode_resolver` service → Real UK postcode database
- Database table with postcode → local_authority mapping

**Status:** ⚠️ **SIMPLIFIED** - Should use backend postcode resolver for accuracy

---

## 2. Backend Static Data

### 2.1 Mock Care Homes (`_create_mock_homes`)

**Location:** `api-testing-suite/backend/main.py` (lines ~4340-4390)

**Purpose:** Fallback when no care homes found from database/CQC API

**Static Fields:**
- Names: "Oakwood Care Centre", "Maple Grove Residential", "Riverside Manor"
- Addresses: Mock addresses with provided postcode
- Features: Hardcoded lists
- Prices: Calculated from `market_avg` with variations

**When Used:**
- Database query returns 0 results
- CQC API returns 0 results
- Matching algorithm finds no suitable homes

**Real Data Sources (priority order):**
1. Database `care_homes` table (PostGIS geo-queries)
2. CQC API (`/api/cqc/search`)
3. Google Places API (enrichment)
4. FSA FHRS API (enrichment)

**Status:** ✅ **CORRECT** - Only used as last resort fallback

---

### 2.2 Price Variation (`weekly_cost` calculation)

**Location:** `api-testing-suite/backend/main.py` (lines 3903-3908)

**Static Logic:**
```python
if home.get("weekly_cost") is None:
    variation = random.uniform(0.85, 1.15)  # ±15% variation
    home["weekly_cost"] = round(market_avg * variation, 2)
```

**When Used:**
- Care home from CQC API doesn't have price data
- Database `weekly_cost` is NULL

**Real Data Sources:**
1. Database `care_homes.weekly_cost` (from PricingService)
2. Database `fee_residential_from`, `fee_nursing_from` (care-type specific)
3. Firecrawl scraping (from care home website)
4. Autumna API (if available)

**Status:** ⚠️ **TEMPORARY** - Should fetch from real pricing sources

---

### 2.3 Fair Cost Gap Text

**Location:** `api-testing-suite/backend/main.py` (line 3890)

**Current:**
```python
gap_text = f"Overpayment £{gap_year:,.0f} per year = £{gap_5year:,.0f} over 5 years"
```

**Status:** ✅ **DYNAMIC** - Calculated from real `market_avg` and `msif_lower_bound`

**Real Data Sources:**
- `market_avg`: PricingService → Database → Real market data
- `msif_lower_bound`: Database `msif_fees_2025` table → Real MSIF data

---

### 2.4 Recommendations List

**Location:** `api-testing-suite/backend/main.py` (lines 4053-4058)

**Static List:**
```python
"recommendations": [
    "Consider applying for Continuing Healthcare (CHC) funding",
    "Discuss top-up fee arrangements with family members",
    "Explore local authority discretionary funding options",
    "Review eligibility for Attendance Allowance or other benefits"
]
```

**Status:** ✅ **STATIC BUT APPROPRIATE** - These are general recommendations, not data-dependent

**Future Enhancement:**
- Could be personalized based on `chc_probability`
- Could include local authority-specific funding options

---

## 3. Data Flow Summary

### Real Data Sources (Priority Order)

1. **Care Homes:**
   - Database `care_homes` table (PostGIS queries)
   - CQC API (`/api/cqc/search`)
   - Google Places API (enrichment: rating, reviews, photos)
   - FSA FHRS API (enrichment: food hygiene ratings)

2. **Pricing:**
   - Database `care_homes.weekly_cost`
   - PricingService → `market_avg` calculation
   - MSIF Database → `msif_fees_2025.fair_cost_gbp_week`

3. **Fair Cost Gap:**
   - Calculated: `market_avg - msif_lower_bound`
   - All values derived from real data

4. **Matching:**
   - 50-point algorithm uses real:
     - Distance (Haversine from real coordinates)
     - CQC rating (from database/CQC API)
     - Price (from database/PricingService)
     - Google reviews (from Google Places API)
     - FSA rating (from FSA FHRS API)

### Fallback Chain

```
Real Data Sources
    ↓ (if unavailable)
Database Cache
    ↓ (if unavailable)
Mock Data (Frontend)
    ↓ (if unavailable)
Hardcoded Fallbacks
```

---

## 4. Recommendations

### High Priority

1. **Generate `why_this_home` in Backend**
   - Create function `generate_why_this_home()` in `matching_service.py`
   - Use real home data (rating, distance, price, features)
   - Return to frontend in API response

2. **Remove Frontend Postcode Mapping**
   - Always use backend `postcode_resolver`
   - Frontend should not guess local authority

3. **Fetch Real Prices**
   - Prioritize database `weekly_cost`
   - Use Firecrawl scraping as fallback
   - Remove random variation logic

### Medium Priority

1. **Personalize Recommendations**
   - Based on `chc_probability`
   - Based on `care_type`
   - Include local authority-specific options

2. **Cache Mock Data**
   - Store mock homes in database for testing
   - Use same structure as real homes

### Low Priority

1. **Improve Mock Home Data**
   - Use realistic names from actual care homes
   - Use real postcodes (anonymized)
   - Match features to care types

---

## 5. Testing with Real Data

To ensure all data comes from real sources:

1. **Database Setup:**
   ```sql
   -- Check care_homes table has data
   SELECT COUNT(*) FROM care_homes WHERE local_authority = 'Camden';
   
   -- Check MSIF data
   SELECT * FROM msif_fees_2025 WHERE local_authority = 'Camden' LIMIT 5;
   ```

2. **API Testing:**
   ```bash
   # Test CQC API
   curl http://localhost:8000/api/cqc/search?postcode=SW1A1AA
   
   # Test MSIF API
   curl http://localhost:8000/api/msif/fair-cost/Camden?care_type=nursing
   
   # Test Free Report (should use real data)
   curl -X POST http://localhost:8000/api/free-report \
     -H "Content-Type: application/json" \
     -d '{"postcode": "SW1A 1AA", "budget": 1200, "care_type": "nursing"}'
   ```

3. **Verify No Mock Data:**
   - Check backend logs for "using mock" messages
   - Verify `care_homes` array contains real names/addresses
   - Verify `fair_cost_gap` uses real `market_avg` and `msif_lower_bound`

---

## Summary

✅ **Good:** Fair Cost Gap calculations, MSIF fallbacks, matching algorithm  
⚠️ **Needs Improvement:** `why_this_home` generation, price fetching, postcode mapping  
✅ **Acceptable:** Mock homes (only as fallback), static recommendations

**Key Principle:** All user-facing data should be calculated from real sources. Static data is only acceptable as fallback when real sources are unavailable.


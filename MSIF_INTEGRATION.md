# MSIF Integration Guide

## Overview

Production-ready integration of MSIF (Market Sustainability and Improvement Fund) data into RightCareHome FastAPI project.

## Features

- ✅ **Automatic download** of MSIF Excel files (2025-2026 priority, fallback to 2024-2025)
- ✅ **In-memory caching** + file caching
- ✅ **FastAPI endpoints** for Fair Cost Gap calculation
- ✅ **Integration** with PricingService
- ✅ **Zero cost** (only requests + pandas)

## Structure

```
src/
  msif/
    __init__.py
    loader.py          # MSIF data loader
  api/
    routers/
      msif.py          # FastAPI router
```

## API Endpoints

### 1. Get Fair Cost for Local Authority

```bash
GET /api/msif/fair-cost/{local_authority}?care_type=nursing
```

**Example:**
```bash
curl "http://localhost:8000/api/msif/fair-cost/Camden?care_type=nursing"
```

**Response:**
```json
{
  "local_authority": "Camden",
  "care_type": "nursing",
  "fair_cost_gbp_week": 1048.0
}
```

### 2. Calculate Fair Cost Gap

```bash
GET /api/msif/fair-cost-gap?market_price=1912&local_authority=Camden&care_type=nursing_dementia
```

**Example:**
```bash
curl "http://localhost:8000/api/msif/fair-cost-gap?market_price=1912&local_authority=Camden&care_type=nursing_dementia"
```

**Response:**
```json
{
  "msif_lower_bound": 1048.0,
  "market_price": 1912.0,
  "gap_weekly": 864.0,
  "gap_annual": 44928.0,
  "gap_5year": 224640.0,
  "gap_percent": 82.4
}
```

### 3. List All Authorities

```bash
GET /api/msif/authorities
```

### 4. Get All MSIF Data

```bash
GET /api/msif/data
```

## Usage in Code

### Direct Function Call

```python
from msif.loader import get_fair_cost, calculate_fair_cost_gap

# Get fair cost
cost = get_fair_cost("Camden", "nursing")
print(f"MSIF lower bound: £{cost}/week")

# Calculate gap
gap_data = calculate_fair_cost_gap(
    market_price=1912.0,
    local_authority="Camden",
    care_type="nursing_dementia"
)
print(f"5-year gap: £{gap_data['gap_5year']:,}")
```

### Integration in Free Report Endpoint

The `/api/free-report` endpoint automatically uses MSIF loader:

```python
# In generate_free_report endpoint
from msif.loader import get_fair_cost

msif_lower_bound = get_fair_cost(local_authority, care_type)
gap_week = market_avg - msif_lower_bound
```

## Startup Warmup

MSIF data is automatically preloaded on FastAPI startup (see `lifespan` function in `main.py`):

```python
from msif.loader import get_msif_data
msif_data = get_msif_data()  # Preloads on startup
```

## Care Types Supported

- `"residential"` → 65+ Residential Care Home Fees
- `"nursing"` → 65+ Nursing Care Home Fees
- `"residential_dementia"` → 65+ Residential Dementia Care Home Fees
- `"nursing_dementia"` → 65+ Nursing Dementia Care Home Fees

## Data Sources

- **2025-2026**: https://assets.publishing.service.gov.uk/media/68a3021cf49bec79d23d2940/market-sustainability-and-improvement-fund-fees-2025-to-2026.xlsx
- **2024-2025**: https://assets.publishing.service.gov.uk/media/6703d7cc3b919067bb482d39/market-sustainability-and-improvement-fund-fees-2024-to-2025.xlsx

## Caching

- **File cache**: Excel files saved to `data/msif/`
- **Memory cache**: Data loaded once, reused for all requests
- **Automatic refresh**: Downloads new file if missing

## Error Handling

- Falls back to 2024-2025 if 2025-2026 unavailable
- Returns HTTPException with 404 if local authority not found
- Falls back to db_utils if MSIF loader fails

## Testing

```bash
# Test endpoints
curl "http://localhost:8000/api/msif/authorities"
curl "http://localhost:8000/api/msif/fair-cost/Camden?care_type=nursing"
curl "http://localhost:8000/api/msif/fair-cost-gap?market_price=1912&local_authority=Camden&care_type=nursing_dementia"
```

## Real Data Example (Camden, November 2025)

```python
gap = calculate_fair_cost_gap(
    market_price=1912,
    local_authority="Camden",
    care_type="nursing_dementia"
)
# Result:
# gap_weekly ≈ £864
# gap_5year ≈ £224,640
```

## Integration Status

- ✅ MSIF loader module created
- ✅ FastAPI router registered
- ✅ Startup warmup implemented
- ✅ Integrated in `/api/free-report` endpoint
- ✅ Fallback to db_utils if MSIF loader fails
- ✅ CORS updated for Streamlit (localhost:8501)

## Dependencies

- `pandas>=2.0.0`
- `requests>=2.31.0`
- `openpyxl>=3.1.0`

## Notes

- Files are cached locally after first download
- Data is loaded once and cached in memory
- Supports both 2025-2026 and 2024-2025 datasets
- Production-ready and tested on real data (November 2025)


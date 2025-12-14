# MSIF Loader Module

## Overview

Production-ready module for loading MSIF (Market Sustainability and Improvement Fund) fees data from UK government Excel files (2025-2026 and 2024-2025).

## Features

- ✅ **Automatic download** of MSIF Excel files from gov.uk
- ✅ **Local caching** - files stored in `data/msif/`
- ✅ **Fallback support** - tries 2025-2026 first, then 2024-2025
- ✅ **Clean parsing** - converts Excel to structured dict
- ✅ **Fair Cost Gap calculation** - ready-to-use function

## Installation

```bash
pip install pandas requests openpyxl
```

## Usage

### Basic Usage

```python
from msif_loader import get_fair_cost_lower_bound, calculate_fair_cost_gap

# Get MSIF lower bound for a local authority
msif_lower = get_fair_cost_lower_bound("Camden", "nursing")
print(f"MSIF lower bound: £{msif_lower}/week")

# Calculate Fair Cost Gap
gap_data = calculate_fair_cost_gap(
    market_price=1912.0,
    local_authority="Camden",
    care_type="nursing_dementia"
)
print(gap_data)
```

### Integration with db_utils.py

The module is automatically integrated into `db_utils.py` with priority:

1. **msif_loader.py** (downloads from gov.uk) - **Preferred**
2. Database (msif_fees_2025 table) - Fallback
3. Mock data - Last resort

### Care Types Supported

- `"residential"` → residential_median
- `"nursing"` → nursing_median
- `"residential_dementia"` → residential_dementia_median
- `"nursing_dementia"` → nursing_dementia_median

## File Structure

```
data/
  msif/
    msif_fees_2025-2026.xlsx  # Auto-downloaded
    msif_fees_2024-2025.xlsx  # Fallback
```

## Functions

### `download_msif_file(year_key: str) -> Path`

Downloads MSIF Excel file from gov.uk and saves locally.

**Parameters:**
- `year_key`: "2025-2026" or "2024-2025"

**Returns:**
- Path to downloaded file

### `load_msif_data(year_key: str) -> Dict[str, Dict[str, float]]`

Parses MSIF Excel file into structured dictionary.

**Returns:**
```python
{
    "Camden": {
        "residential_median": 842.0,
        "nursing_median": 1048.0,
        "residential_dementia_median": 965.0,
        "nursing_dementia_median": 1171.0
    },
    ...
}
```

### `get_msif_data() -> Dict[str, Dict[str, float]]`

Gets cached MSIF data (loads once, reuses).

**Returns:**
- Dictionary of all local authorities and their MSIF fees

### `get_fair_cost_lower_bound(local_authority: str, care_type: str) -> Optional[float]`

Gets MSIF lower bound for specific local authority and care type.

**Parameters:**
- `local_authority`: e.g., "Camden", "Westminster"
- `care_type`: "residential", "nursing", "residential_dementia", "nursing_dementia"

**Returns:**
- MSIF lower bound (float) or None if not found

### `calculate_fair_cost_gap(market_price: float, local_authority: str, care_type: str) -> Dict`

Calculates complete Fair Cost Gap breakdown.

**Returns:**
```python
{
    "msif_lower_bound": 1048.0,
    "market_price": 1912.0,
    "gap_weekly": 864.0,
    "gap_annual": 44928.0,
    "gap_5year": 224640.0,
    "gap_percent": 82.4
}
```

## Data Sources

- **2025-2026**: https://assets.publishing.service.gov.uk/media/68a3021cf49bec79d23d2940/market-sustainability-and-improvement-fund-fees-2025-to-2026.xlsx
- **2024-2025**: https://assets.publishing.service.gov.uk/media/6703d7cc3b919067bb482d39/market-sustainability-and-improvement-fund-fees-2024-to-2025.xlsx

## Error Handling

The module gracefully handles:
- Network errors (falls back to cached files)
- Missing columns (tries multiple column name variations)
- Invalid data (skips problematic rows)
- Missing local authorities (returns None)

## Testing

```python
if __name__ == "__main__":
    data = get_msif_data()
    print("Camden nursing:", get_fair_cost_lower_bound("Camden", "nursing"))
    print(calculate_fair_cost_gap(1912, "Camden", "nursing_dementia"))
```

## Integration Points

### db_utils.py

Automatically used by `get_msif_fee()` function:

```python
from free_report_viewer.db_utils import get_msif_fee

msif_data = get_msif_fee("Camden", "nursing")
msif_lower_bound = msif_data.get("msif_lower_bound")
```

### API Endpoint

Used in `/api/free-report` endpoint for Fair Cost Gap calculation:

```python
msif_data = get_msif_fee(local_authority, care_type)
msif_lower_bound = msif_data.get("msif_lower_bound", 700.0)
gap_week = market_avg - msif_lower_bound
```

## Notes

- Files are cached locally after first download
- Data is loaded once and cached in memory
- Supports both 2025-2026 and 2024-2025 datasets
- Handles variations in Excel column names
- Production-ready and tested on real data (November 2025)


# NHSBSA Integration (English Prescribing Dataset)

## Overview

NHSBSA (NHS Business Services Authority) provides access to the English Prescribing Dataset (EPD) - comprehensive data on NHS prescription dispensing.

This integration enables:
- **Area Health Profiling**: Analyze health patterns based on GP prescribing
- **Proximity Matching**: Find nearest GP practices to care homes
- **Care Home Considerations**: Identify health needs relevant to care homes

## Features

### 1. Area Health Profile
Builds a health profile for an area by analyzing prescribing patterns from nearby GP practices.

### 2. Proximity Matching
Efficient geographic matching using Haversine distance and grid-based indexing.

### 3. Care Home Considerations
Identifies specific care capabilities needed based on local health patterns.

---

## API Endpoints

### Check Status
```
GET /api/nhsbsa/status
```

### Get Health Profile
```
GET /api/nhsbsa/health-profile/{postcode}?radius_km=5.0
```

Response:
```json
{
  "practices_analyzed": 12,
  "total_patients": 85000,
  "health_indicators": {
    "dementia": {
      "items_per_1000_patients": 45.2,
      "national_average": 38.5,
      "vs_national_percent": 17.4,
      "significance": "Higher than average"
    },
    "cardiovascular": {...},
    "diabetes": {...}
  },
  "health_index": {
    "score": 62,
    "rating": "Average",
    "interpretation": "Area has typical prescribing patterns"
  },
  "care_home_considerations": [
    {
      "category": "Dementia Care",
      "finding": "Area has higher dementia medication prescribing",
      "implication": "Care homes may need strong dementia care capabilities",
      "priority": "high"
    }
  ]
}
```

### Get Top Medications
```
GET /api/nhsbsa/top-medications/{postcode}?limit=10
```

### Compare to National Average
```
GET /api/nhsbsa/vs-national-average/{postcode}
```

### Find Nearest GP Practices
```
POST /api/nhsbsa/nearest-practices
Content-Type: application/json

{
  "latitude": 52.4862,
  "longitude": -1.8904,
  "max_distance_km": 5.0
}
```

### Get Care Home Considerations
```
GET /api/nhsbsa/care-home-considerations/{postcode}
```

---

## Health Index Calculation

The Health Index (0-100) is a composite score based on prescribing patterns:

### Category Weights
```python
weights = {
    'dementia': 0.15,
    'cardiovascular': 0.15,
    'diabetes': 0.15,
    'mental_health': 0.15,
    'respiratory': 0.10,
    'pain': 0.10,
    'antibiotics': 0.10,
    'nutrition': 0.05,
    'incontinence': 0.03,
    'pressure_sores': 0.02
}
```

### Scoring Logic
- **Lower prescribing** relative to national average = **higher score**
- Indicates potentially healthier population
- Score ≥70: Good
- Score 50-69: Average
- Score 30-49: Below Average
- Score <30: Needs Attention

---

## Proximity Matching

### How It Works
1. Entities (GP practices) are indexed using a geographic grid
2. For queries, only relevant grid cells are searched
3. Haversine formula calculates precise distances
4. Results sorted by distance

### Usage
```python
from data_integrations import create_proximity_index

# Create index
practices = [
    {'id': 'Y00001', 'name': 'GP 1', 'latitude': 52.48, 'longitude': -1.89},
    {'id': 'Y00002', 'name': 'GP 2', 'latitude': 52.50, 'longitude': -1.90}
]
matcher = create_proximity_index(practices)

# Find nearest
nearest = matcher.find_nearest(52.4862, -1.8904, max_results=5)

# Find within radius
within_5km = matcher.find_within_radius(52.4862, -1.8904, radius_km=5)
```

---

## BNF Categories

British National Formulary categories tracked for care home relevance:

| Category | BNF Codes | Relevance |
|----------|-----------|-----------|
| Dementia | 0411, 0412 | Essential for memory care |
| Pain | 0407 | Pain management needs |
| Diabetes | 0601 | Chronic condition management |
| Cardiovascular | 0201-0206 | Heart and blood pressure |
| Respiratory | 0301-0303 | Breathing conditions |
| Mental Health | 0401-0403 | Depression, anxiety |
| Antibiotics | 0501 | Infection rates |
| Nutrition | 0906, 0907 | Nutritional needs |

---

## Caching

- **TTL**: 30 days (data updates monthly)
- **Cache key format**: `nhsbsa_{endpoint}_{params}`
- **Storage**: SQLite (shared with other integrations)

```
GET /api/nhsbsa/cache/stats
POST /api/nhsbsa/cache/clear
```

---

## Python Usage

```python
from data_integrations import NHSBSALoader

async with NHSBSALoader() as loader:
    # Get area health profile
    profile = await loader.get_area_health_profile("B1 1BB", radius_km=5.0)
    
    print(f"Health Index: {profile['health_index']['score']}")
    print(f"Rating: {profile['health_index']['rating']}")
    
    for consideration in profile['care_home_considerations']:
        print(f"[{consideration['priority']}] {consideration['category']}")
        print(f"  {consideration['implication']}")
    
    # Find nearest practices to a care home
    nearest = await loader.find_nearest_practices_to_care_home(
        care_home_lat=52.4862,
        care_home_lon=-1.8904,
        max_distance_km=5.0
    )
    
    print(f"Healthcare Access: {nearest['healthcare_access_rating']['rating']}")
```

---

## Data Sources

- **NHSBSA Open Data Portal**: https://opendata.nhsbsa.net
- **NHS Digital ODS**: GP Practice data
- **Postcodes.io**: Postcode to coordinates

## Rate Limits

- No authentication required
- Fair use policy applies
- All responses cached for 30 days

---

## Care Home Use Cases

### 1. Pre-placement Assessment
- Understand local health patterns
- Identify if specialized care needed (dementia, nursing)

### 2. Healthcare Access Evaluation
- Check proximity to GP practices
- Assess emergency healthcare availability

### 3. Population Health Insights
- Compare areas for care home suitability
- Understand chronic disease prevalence

### 4. Family Decision Support
- Provide evidence-based area analysis
- Highlight care considerations

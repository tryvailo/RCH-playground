# ONS & OpenStreetMap Integration

## Overview

Two powerful data sources for neighborhood analysis:
- **ONS (Office for National Statistics)**: UK statistical data including wellbeing, economics, demographics
- **OpenStreetMap**: Points of Interest, Walk Score, infrastructure data

## ONS Integration

### Features
- Postcode to LSOA (Lower Layer Super Output Area) conversion
- Wellbeing data (happiness, life satisfaction, anxiety)
- Economic profile (employment, income, deprivation)
- Demographics (age structure, elderly population)
- Social Wellbeing Index calculation

### Endpoints

#### Get LSOA
```
GET /api/ons/lsoa/{postcode}
```

#### Get Wellbeing Data
```
GET /api/ons/wellbeing/{postcode}
```

Response:
```json
{
  "indicators": {
    "happiness": { "value": 7.5, "national_average": 7.4 },
    "life_satisfaction": { "value": 7.6, "national_average": 7.5 },
    "anxiety": { "value": 3.2, "national_average": 3.3 }
  },
  "social_wellbeing_index": {
    "score": 75,
    "rating": "Good"
  }
}
```

#### Get Economic Profile
```
GET /api/ons/economic-profile/{postcode}
```

#### Get Demographics
```
GET /api/ons/demographics/{postcode}
```

#### Get Full Area Profile
```
GET /api/ons/area-profile/{postcode}
```

Returns comprehensive profile combining all data sources.

---

## OpenStreetMap Integration

### Features
- Walk Score calculation (0-100)
- Nearby amenities by category
- Healthcare facilities nearby
- Parks and green spaces
- Infrastructure report (transport, safety)
- Care Home Relevance scoring

### Endpoints

#### Get Walk Score
```
GET /api/osm/walk-score/{lat}/{lon}
```

Response:
```json
{
  "walk_score": 78,
  "rating": "Very Walkable",
  "description": "Most errands can be accomplished on foot",
  "category_breakdown": {
    "grocery": { "score": 85, "count": 5 },
    "healthcare": { "score": 90, "count": 3 },
    "parks": { "score": 70, "count": 2 }
  },
  "care_home_relevance": {
    "score": 82,
    "rating": "Excellent for Care Homes",
    "healthcare_access": "Good",
    "outdoor_spaces": "Available"
  }
}
```

#### Get Nearby Amenities
```
GET /api/osm/nearby-amenities/{lat}/{lon}?radius_m=1600&categories=healthcare,parks
```

#### Get Infrastructure Report
```
GET /api/osm/infrastructure-report/{lat}/{lon}
```

#### Get Healthcare Facilities
```
GET /api/osm/healthcare/{lat}/{lon}
```

#### Get Parks
```
GET /api/osm/parks/{lat}/{lon}
```

---

## Walk Score Methodology

### Scoring (0-100)
| Score | Rating | Description |
|-------|--------|-------------|
| 90-100 | Walker's Paradise | Daily errands do not require a car |
| 70-89 | Very Walkable | Most errands can be accomplished on foot |
| 50-69 | Somewhat Walkable | Some errands can be accomplished on foot |
| 25-49 | Car-Dependent | Most errands require a car |
| 0-24 | Almost All Errands Require a Car | Minimal infrastructure |

### Category Weights
```python
CATEGORY_WEIGHTS = {
    'grocery': 3,
    'restaurants': 2,
    'shopping': 2,
    'healthcare': 3,  # Higher weight for care homes
    'parks': 2,
    'banks': 1,
    'coffee': 1,
    'entertainment': 1
}
```

### Distance Decay
- ≤400m (5 min walk): Full score
- ≤800m (10 min walk): 50-80% score
- ≤1600m (20 min walk): 20-50% score
- >1600m: Minimal score

---

## Care Home Relevance Score

Specifically designed for care home evaluation:

```python
relevance_score = (
    healthcare_score * 0.4 +  # Most important
    parks_score * 0.3 +       # Outdoor activities
    restaurants_score * 0.3   # Family visits
)
```

### Ratings
- **Excellent for Care Homes**: Score ≥70
- **Good for Care Homes**: Score ≥50
- **Adequate**: Score ≥30
- **Limited Walkability**: Score <30

---

## Caching

Both integrations use SQLite caching:

| Source | TTL |
|--------|-----|
| ONS | 90 days |
| OSM | 7 days |

```
GET /api/ons/cache/stats
GET /api/osm/cache/stats
POST /api/ons/cache/clear
POST /api/osm/cache/clear
```

---

## Python Usage

### ONS
```python
from data_integrations import ONSLoader

async with ONSLoader() as loader:
    # Get LSOA
    lsoa = await loader.postcode_to_lsoa("SW1A 1AA")
    
    # Get full profile
    profile = await loader.get_full_area_profile("B1 1BB")
    print(f"Wellbeing Score: {profile['wellbeing']['social_wellbeing_index']['score']}")
```

### OSM
```python
from data_integrations import OSMLoader

async with OSMLoader() as loader:
    # Calculate Walk Score
    score = await loader.calculate_walk_score(52.4862, -1.8904)
    print(f"Walk Score: {score['walk_score']}")
    print(f"Care Home Rating: {score['care_home_relevance']['rating']}")
    
    # Get nearby healthcare
    amenities = await loader.get_nearby_amenities(
        52.4862, -1.8904,
        categories=['healthcare']
    )
```

---

## Rate Limits

### ONS (via postcodes.io)
- No authentication required
- Fair use policy

### OpenStreetMap Overpass API
- No authentication required
- Fair use: avoid >10,000 requests/day
- Built-in backup endpoint for rate limiting

---

## Data Sources

### ONS
- Postcodes.io (LSOA mapping)
- Personal Well-being Estimates
- Labour Market Statistics
- Census 2021

### OpenStreetMap
- Overpass API
- Categories: amenity, healthcare, leisure
- Updated by community contributors

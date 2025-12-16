# Neighbourhood Analysis Integration

## Overview

The Neighbourhood Analysis module provides a unified interface for analyzing care home locations using all four data sources:
- **OS Places**: Coordinates, UPRN, address data
- **ONS**: Social wellbeing, economics, demographics
- **OpenStreetMap**: Walk Score, amenities, infrastructure
- **NHSBSA**: Health profile, GP access, prescribing patterns

## Key Features

### 1. Unified Analysis
Single endpoint that combines all data sources into one comprehensive report.

### 2. Batch Processing
Process up to 100 care homes concurrently with progress tracking.

### 3. Comparison
Compare neighbourhoods across multiple postcodes with rankings.

### 4. Composite Scoring
Overall neighbourhood score (0-100) weighted across all dimensions.

---

## API Endpoints

### Analyze Single Postcode
```
GET /api/neighbourhood/analyze/{postcode}
```

Returns comprehensive analysis:
```json
{
  "postcode": "B1 1BB",
  "coordinates": {"latitude": 52.48, "longitude": -1.89},
  "social": {
    "geography": {"lsoa_code": "E01008391", "local_authority": "Birmingham"},
    "wellbeing": {"score": 72, "rating": "Good"},
    "economic": {"score": 65, "rating": "Good"},
    "demographics": {"over_65_percent": 15.5}
  },
  "walkability": {
    "score": 78,
    "rating": "Very Walkable",
    "care_home_relevance": {"score": 75, "rating": "Excellent for Care Homes"}
  },
  "health": {
    "index": {"score": 68, "rating": "Average"},
    "practices_nearby": 8,
    "care_home_considerations": [...]
  },
  "overall": {
    "score": 71,
    "rating": "Good Neighbourhood",
    "breakdown": [
      {"name": "Social Wellbeing", "score": 72, "weight": "25%"},
      {"name": "Walkability", "score": 78, "weight": "20%"},
      {"name": "Care Home Suitability", "score": 75, "weight": "25%"},
      {"name": "Area Health", "score": 68, "weight": "30%"}
    ]
  }
}
```

### Get Summary
```
GET /api/neighbourhood/summary/{postcode}
```

Quick summary for cards/lists:
```json
{
  "postcode": "B1 1BB",
  "overall_score": 71,
  "overall_rating": "Good Neighbourhood",
  "walk_score": 78,
  "health_score": 68,
  "wellbeing_score": 72,
  "gp_practices_nearby": 8,
  "key_considerations": ["Dementia Care"]
}
```

### Batch Processing
```
POST /api/neighbourhood/batch
Content-Type: application/json

{
  "care_homes": [
    {"postcode": "B1 1BB", "name": "Home 1"},
    {"postcode": "SW1A 1AA", "name": "Home 2"}
  ],
  "include_os_places": true,
  "include_ons": true,
  "include_osm": true,
  "include_nhsbsa": true
}
```

Returns job ID for async processing:
```json
{
  "job_id": "abc12345",
  "status": "running",
  "total_homes": 2,
  "message": "Check progress at /api/neighbourhood/batch/abc12345"
}
```

### Check Batch Status
```
GET /api/neighbourhood/batch/{job_id}
```

### Compare Neighbourhoods
```
POST /api/neighbourhood/compare?postcodes=B1%201BB&postcodes=SW1A%201AA
```

Returns ranked comparison:
```json
{
  "rankings": [
    {"rank": 1, "postcode": "SW1A 1AA", "overall_score": 82},
    {"rank": 2, "postcode": "B1 1BB", "overall_score": 71}
  ],
  "recommendation": "SW1A 1AA ranks highest with an excellent score of 82"
}
```

### Enrich Single Home
```
GET /api/neighbourhood/enrich?postcode=B1%201BB&name=Test%20Home
```

---

## Composite Scoring

### Score Calculation
```python
weights = {
    'Social Wellbeing (ONS)': 0.25,
    'Walkability (OSM)': 0.20,
    'Care Home Suitability (OSM)': 0.25,
    'Area Health (NHSBSA)': 0.30
}
```

### Rating Scale
| Score | Rating |
|-------|--------|
| 75+ | Excellent Neighbourhood |
| 60-74 | Good Neighbourhood |
| 45-59 | Average Neighbourhood |
| <45 | Below Average Neighbourhood |

### Confidence Levels
- **High**: 3-4 data sources available
- **Medium**: 2 data sources available
- **Low**: 1 data source available

---

## Batch Processing

### Configuration
```python
BatchProcessor(
    max_concurrent=5,    # Concurrent API calls
    chunk_size=100,      # Process in chunks
    retry_failed=True,   # Retry on failure
    max_retries=2        # Max retry attempts
)
```

### Progress Tracking
```python
processor.set_progress_callback(lambda p: print(
    f"{p.percent_complete}% ({p.completed}/{p.total})"
))
```

### Memory Efficiency
- Processes in configurable chunks
- Results streamed, not held in memory
- Progress saved incrementally

---

## Python Usage

### Single Analysis
```python
from data_integrations import NeighbourhoodAnalyzer

async with NeighbourhoodAnalyzer() as analyzer:
    result = await analyzer.analyze("B1 1BB")
    
    print(f"Overall Score: {result['overall']['score']}")
    print(f"Rating: {result['overall']['rating']}")
    
    for item in result['overall']['breakdown']:
        print(f"  {item['name']}: {item['score']} ({item['weight']})")
```

### Batch Processing
```python
from data_integrations import BatchProcessor

processor = BatchProcessor(max_concurrent=10)

# Progress callback
processor.set_progress_callback(lambda p: 
    print(f"Progress: {p.percent_complete}% - {p.current_item}")
)

# Process homes
care_homes = [
    {'postcode': 'B1 1BB', 'name': 'Home 1'},
    {'postcode': 'M1 1AA', 'name': 'Home 2'},
    # ... up to thousands of homes
]

results = await processor.process_care_homes(care_homes)

print(f"Completed: {results['statistics']['completed']}")
print(f"Failed: {results['statistics']['failed']}")
print(f"Speed: {results['statistics']['items_per_second']} homes/sec")
```

### Enriching Care Home Data
```python
from data_integrations import BatchProcessor

processor = BatchProcessor()

home = {
    'id': '12345',
    'name': 'Sunrise Care Home',
    'postcode': 'B1 1BB'
}

enriched = await processor.enrich_care_home(home)

# Now home has neighbourhood data
print(enriched['data']['osm']['walk_score'])
print(enriched['data']['nhsbsa']['health_index'])
print(enriched['data']['composite_score'])
```

---

## Caching

All analyses are cached:
- Individual data sources: source-specific TTL
- Full neighbourhood analyses: 7 days

Clear cache:
```
POST /api/neighbourhood/cache/clear
```

---

## Performance

### Benchmarks (typical)
- Single analysis: 2-5 seconds
- Batch of 100: 30-60 seconds (with caching)
- First-time batch: 2-3 minutes (API calls)

### Optimization Tips
1. Use batch processing for multiple homes
2. Leverage cache for repeated queries
3. Adjust `max_concurrent` based on rate limits
4. Use `include_*` flags to skip unneeded data

---

## Use Cases

### 1. Care Home Search
Add neighbourhood context to search results:
```
GET /api/neighbourhood/summary/{postcode}
```

### 2. Comparison Tool
Let families compare locations:
```
POST /api/neighbourhood/compare
```

### 3. Report Generation
Include neighbourhood analysis in reports:
```
GET /api/neighbourhood/analyze/{postcode}
```

### 4. Bulk Enrichment
Enrich entire care home database:
```
POST /api/neighbourhood/batch
```

---

## Error Handling

### Partial Success
If some data sources fail, others still return:
```json
{
  "success": true,
  "data": {
    "ons": {...},
    "osm_error": "Rate limited",
    "nhsbsa": {...}
  }
}
```

### Batch Errors
Errors tracked per-item:
```json
{
  "results": [...],
  "errors": [
    {"item": "Home 5", "error": "Invalid postcode"}
  ]
}
```

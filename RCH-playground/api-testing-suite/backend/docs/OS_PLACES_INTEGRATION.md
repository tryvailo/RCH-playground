# OS Places API Integration

## Overview

OS Places API provides access to AddressBase Premium data from Ordnance Survey - the definitive source of UK address data.

## Features

- **Postcode to Coordinates**: Convert UK postcodes to latitude/longitude
- **Address Lookup**: Get detailed address information including UPRN
- **UPRN Resolution**: Look up addresses by Unique Property Reference Number
- **Free-text Search**: Search addresses using natural language
- **Batch Processing**: Process multiple postcodes in one request

## Configuration

Add your OS Data Hub API key to `config.json`:

```json
{
  "os_places": {
    "api_key": "YOUR_API_KEY",
    "api_secret": "YOUR_API_SECRET",
    "places_endpoint": "https://api.os.uk/search/places/v1/",
    "features_endpoint": "https://api.os.uk/features/v1/wfs"
  }
}
```

## API Endpoints

### Check Status
```
GET /api/os-places/status
```

Returns API configuration status and cache statistics.

### Get Address by Postcode
```
GET /api/os-places/address/{postcode}?max_results=100
```

Returns all addresses at the given postcode with full details.

**Response:**
```json
{
  "postcode": "SW1A 1AA",
  "address_count": 5,
  "addresses": [
    {
      "uprn": "100071417680",
      "address": "BUCKINGHAM PALACE, LONDON, SW1A 1AA",
      "latitude": 51.5014,
      "longitude": -0.1419,
      "local_authority": "Westminster"
    }
  ],
  "centroid": {
    "latitude": 51.5014,
    "longitude": -0.1419
  }
}
```

### Get Coordinates
```
GET /api/os-places/coordinates/{postcode}
```

Simple endpoint to get just latitude/longitude for a postcode.

**Response:**
```json
{
  "postcode": "SW1A 1AA",
  "latitude": 51.5014,
  "longitude": -0.1419
}
```

### Get Address by UPRN
```
GET /api/os-places/uprn/{uprn}
```

Look up address details using Unique Property Reference Number.

### Search Address
```
POST /api/os-places/search
Content-Type: application/json

{
  "query": "10 Downing Street London",
  "max_results": 25
}
```

Free-text address search.

### Batch Coordinates
```
POST /api/os-places/batch
Content-Type: application/json

{
  "postcodes": ["SW1A 1AA", "B1 1BB", "M1 1AE"]
}
```

Get coordinates for multiple postcodes at once (max 50).

### Cache Management
```
GET /api/os-places/cache/stats    # Get cache statistics
POST /api/os-places/cache/clear   # Clear OS Places cache
```

## Caching

All responses are cached in SQLite with 30-day TTL:
- Database: `backend/data/cache.db`
- Source key: `os_places`

## Python Usage

```python
from data_integrations import OSPlacesLoader

async def example():
    async with OSPlacesLoader() as loader:
        # Get coordinates
        coords = await loader.get_coordinates("SW1A 1AA")
        print(f"Lat: {coords['latitude']}, Lon: {coords['longitude']}")
        
        # Get full address details
        result = await loader.get_address_by_postcode("B1 1BB")
        for addr in result['addresses']:
            print(f"UPRN: {addr['uprn']}, Address: {addr['address']}")
        
        # Search by text
        search = await loader.search_address("10 Downing Street")
        for r in search['results']:
            print(f"Match: {r['address']}")
```

## Rate Limits

- Premium API: Subject to your subscription tier
- Recommended: Max 10 requests/second
- All responses are cached to minimize API calls

## Error Handling

| HTTP Code | Meaning |
|-----------|---------|
| 401 | Invalid API key |
| 404 | Postcode/UPRN not found |
| 503 | API not configured |

## Use Cases in RCH

1. **Coordinate Resolution**: Get exact coordinates for care homes
2. **UPRN Linking**: Connect care homes to other datasets via UPRN
3. **Address Standardization**: Normalize addresses for comparison
4. **Distance Calculations**: Calculate distances between locations

## Documentation

- [OS Data Hub](https://osdatahub.os.uk/)
- [OS Places API Docs](https://osdatahub.os.uk/docs/places/overview)
- [AddressBase Premium](https://www.ordnancesurvey.co.uk/products/addressbase-premium)

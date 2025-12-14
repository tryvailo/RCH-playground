# API Routers

This directory contains domain-specific routers extracted from `main.py` to improve modularity and maintainability.

## Structure

- `config_routes.py` - API credentials and configuration management
- `test_data_routes.py` - Test data endpoints
- `cqc_routes.py` - CQC (Care Quality Commission) API endpoints
- `fsa_routes.py` - FSA (Food Standards Agency) API endpoints
- `companies_house_routes.py` - Companies House API endpoints
- `google_places_routes.py` - Google Places API endpoints
- `perplexity_routes.py` - Perplexity API endpoints
- `firecrawl_routes.py` - Firecrawl API endpoints
- `test_routes.py` - API testing endpoints
- `report_routes.py` - Report generation endpoints
- `analytics_routes.py` - Analytics endpoints

## Usage

All routers are registered in `main.py`:

```python
from routers import config_routes, cqc_routes, fsa_routes, ...

app.include_router(config_routes.router)
app.include_router(cqc_routes.router)
app.include_router(fsa_routes.router)
# ... etc
```

## Benefits

1. **Modularity**: Each domain has its own router file
2. **Maintainability**: Easier to find and modify domain-specific code
3. **Testability**: Routers can be tested independently
4. **Scalability**: New domains can be added without cluttering main.py


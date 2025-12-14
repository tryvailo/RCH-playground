# Staff Data Services - Documentation

## Overview

This directory contains services for enriching care home data with staff-related information from multiple sources:

1. **Glassdoor Research** (via Perplexity AI)
2. **LinkedIn Research** (via Perplexity AI)
3. **Job Boards Integration**
4. **Staff Enrichment Service** (combines all sources)

## Services

### 1. GlassdoorResearchService

**File**: `glassdoor_research_service.py`

Uses Perplexity AI to research Glassdoor employee reviews and ratings.

**Features**:
- Employee satisfaction rating (1-5)
- Review count
- Management score
- Work-life balance score
- Culture score
- Career opportunities score
- Compensation score
- Sentiment analysis (positive/negative/neutral)
- Key themes extraction
- Turnover mentions detection

**Usage**:
```python
from services.glassdoor_research_service import GlassdoorResearchService
from api_clients.perplexity_client import PerplexityAPIClient

perplexity_client = PerplexityAPIClient(api_key="your-key")
glassdoor_service = GlassdoorResearchService(perplexity_client)

data = await glassdoor_service.research_glassdoor_data(
    home_name="Sunshine Care Home",
    company_name="Sunshine Care Ltd",
    location="London"
)
```

### 2. LinkedInResearchService

**File**: `linkedin_research_service.py`

Uses Perplexity AI to research LinkedIn staff data.

**Features**:
- Staff count
- Average tenure (years)
- Certifications list
- Qualification levels
- Department breakdown
- Hiring frequency
- Recent hires count
- Turnover rate estimate
- Key positions
- Career progression patterns

**Usage**:
```python
from services.linkedin_research_service import LinkedInResearchService
from api_clients.perplexity_client import PerplexityAPIClient

perplexity_client = PerplexityAPIClient(api_key="your-key")
linkedin_service = LinkedInResearchService(perplexity_client)

data = await linkedin_service.research_linkedin_data(
    home_name="Sunshine Care Home",
    company_name="Sunshine Care Ltd",
    location="London"
)
```

### 3. JobBoardsService

**File**: `job_boards_service.py`

Analyzes job board listings to identify hiring patterns and turnover signals.

**Features**:
- Active job listings count
- Job titles & salary ranges
- Hiring frequency analysis
- Department needs breakdown
- Turnover signals detection
- Urgency indicators

**Supported Job Boards**:
- Indeed (API integration - requires setup)
- Reed (API integration - requires setup)
- Totaljobs (API integration - requires setup)

**Note**: Currently returns structure ready for API integration. Actual API calls require API keys configuration.

**Usage**:
```python
from services.job_boards_service import JobBoardsService

job_boards_service = JobBoardsService()

data = await job_boards_service.analyze_job_listings(
    home_name="Sunshine Care Home",
    company_name="Sunshine Care Ltd",
    location="London",
    postcode="SW1A 1AA"
)
```

### 4. StaffEnrichmentService

**File**: `staff_enrichment_service.py`

Combines all staff data sources into unified analysis.

**Features**:
- Integrates Glassdoor, LinkedIn, and Job Boards data
- Combined analysis with unified metrics
- Turnover rate estimation from multiple sources
- Data quality assessment
- Staff quality metrics extraction

**Usage**:
```python
from services.staff_enrichment_service import StaffEnrichmentService
from api_clients.perplexity_client import PerplexityAPIClient

perplexity_client = PerplexityAPIClient(api_key="your-key")
staff_service = StaffEnrichmentService(perplexity_client=perplexity_client)

enriched_home = await staff_service.enrich_staff_data(
    home={
        "name": "Sunshine Care Home",
        "company_name": "Sunshine Care Ltd",
        "location": "London",
        "postcode": "SW1A 1AA"
    },
    use_perplexity=True
)

# Access enriched data
staff_data = enriched_home.get('staff_data', {})
staff_quality = enriched_home.get('staffQuality', {})
```

## Integration with Professional Report

These services are designed to be integrated into the Professional Report generation pipeline:

1. **Glassdoor data** → Used in Staff Quality scoring (8 points)
2. **LinkedIn data** → Used for tenure analysis (7 points) and turnover (5 points)
3. **Job Boards data** → Used for turnover signals and hiring patterns

## Data Quality Levels

All services return a `data_quality` field indicating:
- `high`: Multiple reliable sources with citations
- `medium`: Some reliable data available
- `low`: Limited data available
- `very_low`: No reliable data found

## Error Handling

All services include robust error handling:
- Returns default/empty data structures on failure
- Logs errors for debugging
- Continues processing even if one source fails

## Configuration

### Perplexity AI Setup

Requires Perplexity API key in `config.json`:
```json
{
  "perplexity": {
    "api_key": "your-perplexity-api-key"
  }
}
```

### Job Boards API Setup (Future)

For full Job Boards integration, configure API keys:
- Indeed: https://ads.indeed.com/jobroll/xmlfeed
- Reed: https://www.reed.co.uk/api/
- Totaljobs: (check their API documentation)

## Notes

- **Perplexity AI**: Uses web search and AI to extract structured data from unstructured sources
- **Rate Limiting**: Perplexity API has rate limits - implement caching for production
- **Cost**: Perplexity API calls cost ~$0.005 per request (sonar-pro model)
- **Job Boards**: Currently returns structure ready for API integration. Actual implementation requires API keys and may involve web scraping with ToS compliance

## Related Services

- `professional_matching_service.py`: Uses staff data for scoring
- `red_flags_service.py`: Uses staff data for risk assessment
- `comparative_analysis_service.py`: Includes staff metrics in comparison


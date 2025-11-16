# Firecrawl API v2.5: Technical implementation guide and validation

**The parameter is `prompt`, not `crawlPrompt`**—a critical correction for semantic crawling. Firecrawl v2.5 brings infrastructure upgrades with no breaking changes, maintaining full backward compatibility while delivering enhanced quality through a custom browser stack and Semantic Index serving 40% of requests.

## What's genuinely new in v2.5 versus v2.0

Firecrawl v2.5 focuses on **infrastructure quality over new features**. Released October 30, 2025, v2.5 represents a major architectural upgrade rather than an API expansion. The version is fully backward compatible—all v2.0 code continues working without modification.

### Custom browser stack replaces generic tools

Firecrawl built a proprietary browser fleet from the ground up, replacing dependencies on Playwright/Puppeteer. The stack automatically detects rendering methods for each page and handles PDFs, paginated tables, JavaScript apps, and Excel files uniformly. **Excel (.xlsx) scraping** is the only new content type added in v2.5, building on existing PDF, ODT, and RTF support from v2.3.0.

### Semantic Index serves 40% of API calls

The new Semantic Index caches full page snapshots with embeddings and structural metadata. It provides dual-mode access: "as of now" for fresh data or "as of last known good copy" for cached snapshots. The `maxAge` parameter controls freshness, defaulting to 4 hours for scrape endpoints (changed from 2 days in v2.0). Set `maxAge: 0` to force fresh scrapes.

### NUQ concurrency system improves throughput

The New Unified Queue (NUQ) tracking system implements per-owner and per-group concurrency limiting with dynamic calculation. This delivers better queue fairness across large workloads and reduces Redis memory usage by 16x for crawl operations.

### Performance improvements without code changes

Search costs dropped 5x (2 credits per 10 results). The Map endpoint runs 15x faster and supports up to 100k URLs. Crawl throughput improved through better architecture. Most significantly, **zero breaking changes** mean v2.5 upgrades happen automatically without touching your code.

## Correcting the parameter names for your care home scraper

### The semantic crawling parameter is `prompt`, not `crawlPrompt`

**Your code needs correction.** The crawl endpoint accepts `prompt` as the parameter name for natural language crawl configuration:

```python
from firecrawl import Firecrawl

firecrawl = Firecrawl(api_key="fc-YOUR-API-KEY")

# CORRECT: Use "prompt" parameter
crawl_result = firecrawl.crawl(
    url="https://care-home-directory.com",
    prompt="Extract care home listings with contact details and facility information",
    limit=100,
    scrape_options={
        "formats": ["markdown"]
    }
)
```

The API reference explicitly documents this as `prompt: string` - "A prompt to use to generate the crawler options (all the parameters below) from natural language." The system derives includePaths, excludePaths, and other parameters from your natural language description.

### Preview derived parameters before crawling

Use the `/v2/crawl/params-preview` endpoint to verify how Firecrawl interprets your prompt:

```python
import requests

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer fc-YOUR-API-KEY'
}

data = {
    "url": "https://care-home-directory.com",
    "prompt": "Extract care home listings with contact details"
}

response = requests.post(
    "https://api.firecrawl.dev/v2/crawl/params-preview",
    headers=headers,
    json=data
)

# Returns derived parameters Firecrawl will use
print(response.json())
```

This preview shows the generated `includePaths`, `excludePaths`, `maxDiscoveryDepth`, and other parameters before committing to a full crawl. Explicitly set parameters override AI-generated equivalents.

## Search endpoint sources parameter: Your format is correct

**Validation: `sources: ["images"]` and `sources: ["news"]` are correct.**

The search endpoint supports multiple source types with this exact array syntax:

```python
# CORRECT format for search sources
search_result = firecrawl.search(
    query="care home facilities",
    sources=["web", "images", "news"],
    limit=10,
    scrape_options={
        "formats": ["markdown"]
    }
)
```

### Available source types

- **`"web"`**: Standard web search results
- **`"images"`**: Image search with imageUrl, imageWidth, imageHeight, position
- **`"news"`**: News articles with date, snippet, imageUrl fields
- **`"pdf"`**: PDF documents (added v2.4 via categories parameter)

### Response structure organized by source

The v2 response format groups results by source type rather than returning a flat list:

```json
{
  "success": true,
  "data": {
    "web": [
      {
        "title": "Care Home Directory",
        "url": "https://example.com",
        "description": "...",
        "markdown": "...",
        "metadata": {...}
      }
    ],
    "images": [
      {
        "title": "Care facility photo",
        "imageUrl": "https://...",
        "imageWidth": 1920,
        "imageHeight": 1080,
        "url": "https://source-page.com",
        "position": 1
      }
    ],
    "news": [
      {
        "title": "New care standards announced",
        "snippet": "...",
        "date": "2024-11-15",
        "url": "https://news-site.com",
        "markdown": "...",
        "metadata": {...}
      }
    ]
  }
}
```

Include `scrapeOptions` with formats to get full content for each result. Without scrapeOptions, you receive only SERP metadata (url, title, description).

### Categories parameter for specialized searches

Use `categories` to filter specific content types:

```python
# Search GitHub repos and research papers
search_result = firecrawl.search(
    query="care management systems",
    categories=[{"type": "github"}, {"type": "research"}],
    limit=10
)
```

Available categories: `"github"`, `"research"` (arXiv, Nature, IEEE, PubMed), `"pdf"`.

## Extract API schema format: Use JSON Schema in formats array

**Your extract schema format needs adjustment for v2.**

### Correct v2 scrape endpoint with JSON extraction

The v2 scrape endpoint embeds the schema directly inside the formats array as an object:

```python
from firecrawl import Firecrawl
from pydantic import BaseModel

firecrawl = Firecrawl(api_key="fc-YOUR-API-KEY")

# Define extraction schema
class CareHome(BaseModel):
    name: str
    address: str
    phone: str
    capacity: int
    care_types: list[str]
    rating: float

# CORRECT v2 format
result = firecrawl.scrape(
    'https://care-home-listing.com/facility',
    formats=[{
        "type": "json",
        "schema": CareHome.model_json_schema(),
        "prompt": "Extract care home details including contact info and ratings"
    }]
)

# Access extracted data
care_home_data = result['data']['json']
```

### Key format parameters

- **`type`**: Set to `"json"` for structured extraction
- **`schema`**: JSON Schema object (use `model_json_schema()` with Pydantic)
- **`prompt`**: Optional natural language guidance for extraction

### Extract without schema using prompt only

You can extract structured data without defining a rigid schema:

```python
result = firecrawl.scrape(
    'https://care-home-listing.com/facility',
    formats=[{
        "type": "json",
        "prompt": "Extract the care home name, contact details, and available services"
    }]
)

# LLM chooses the structure based on your prompt
```

The AI model determines the output structure semantically. This works well for exploratory extraction or when schema requirements aren't fully defined.

## Dedicated extract endpoint for multiple URLs

For extracting from multiple care home pages simultaneously, use the `/v2/extract` endpoint:

```python
# Extract from multiple URLs with web search fallback
extract_result = firecrawl.extract(
    urls=["https://care-home-directory.com/*"],  # Wildcard supported
    prompt="Extract care home information including name, address, phone, services, and ratings",
    schema={
        "type": "object",
        "properties": {
            "care_homes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "address": {"type": "string"},
                        "phone": {"type": "string"},
                        "services": {"type": "array", "items": {"type": "string"}},
                        "rating": {"type": "number"}
                    },
                    "required": ["name", "address"]
                }
            }
        },
        "required": ["care_homes"]
    },
    enable_web_search=True  # Find additional context from related pages
)
```

The extract endpoint supports wildcards (`/*`) to automatically crawl and parse all discovered URLs in a domain, then extract the requested data structure.

## Optimal v2.5 approach for care home website scraping

**Recommendation: Use batch_scrape with Pydantic schemas for structured list crawling.**

### Two-phase extraction pattern for care home directories

Phase 1 extracts the list of care homes. Phase 2 fetches detailed information for each facility.

#### Phase 1: Extract care home list

```python
from firecrawl import Firecrawl
from pydantic import BaseModel, Field
from typing import List

firecrawl = Firecrawl(api_key="fc-YOUR-API-KEY")

# Define list schema
class CareHomeListing(BaseModel):
    name: str = Field(description="Care home name")
    url: str = Field(description="Full URL to care home detail page")
    location: str = Field(description="City or region")

class CareHomeList(BaseModel):
    care_homes: List[CareHomeListing]

# Generate URLs for pagination (adjust range for full dataset)
listing_urls = [
    f"https://care-home-directory.com/listings?page={p}&per_page=50"
    for p in range(1, 11)
]

# Batch scrape with schema
list_result = firecrawl.batch_scrape(
    listing_urls,
    formats=[{"type": "json", "schema": CareHomeList}]
)

# Collect all care homes
all_care_homes = []
for page_data in list_result.data:
    all_care_homes.extend(page_data.json['care_homes'])

print(f"Found {len(all_care_homes)} care homes")
```

#### Phase 2: Extract detailed profiles

```python
# Define detailed schema
class CareHomeDetails(BaseModel):
    name: str
    full_address: str
    phone: str
    email: str
    website: str
    capacity: int
    care_types: List[str]
    amenities: List[str]
    ratings: float
    inspection_date: str
    description: str

# Get detail URLs from Phase 1
detail_urls = [home['url'] for home in all_care_homes]

# Extract detailed information
detail_result = firecrawl.batch_scrape(
    detail_urls,
    formats=[{"type": "json", "schema": CareHomeDetails}]
)

detailed_profiles = []
for page_data in detail_result.data:
    detailed_profiles.append(page_data.json)

print(f"Extracted {len(detailed_profiles)} detailed profiles")
```

### Why batch_scrape outperforms traditional approaches

**Zero selector maintenance**: HTML structure changes don't break your scraper. The AI adapts to redesigns, A/B tests, and seasonal layout changes automatically.

**JavaScript rendering included**: Modern care home directories load content dynamically. Batch_scrape handles JavaScript execution without requiring Selenium or Playwright configuration.

**Anti-bot handling built-in**: Proxy rotation, rate limiting, and CAPTCHA avoidance happen transparently. You don't manage infrastructure.

**Database-ready output**: Pydantic schemas enforce type validation. The extracted data maps directly to database tables or API responses without post-processing.

### Semantic crawl alternative for discovery

If you don't know the pagination structure, use semantic crawling:

```python
crawl_result = firecrawl.crawl(
    url="https://care-home-directory.com",
    prompt="Find all care home facility pages with detailed information",
    limit=500,
    scrape_options={
        "formats": [{
            "type": "json",
            "schema": CareHomeDetails.model_json_schema()
        }]
    }
)

# Results include extracted data for each discovered page
for page in crawl_result.data:
    care_home = page.json
    print(f"{care_home['name']}: {care_home['phone']}")
```

The crawler discovers relevant pages automatically based on your natural language prompt, then extracts structured data using the provided schema.

## Caching mechanisms and maxAge parameter

### Semantic Index caching controls

The `maxAge` parameter specifies cache freshness in milliseconds:

```python
# Use cache if available (up to 4 hours old)
result = firecrawl.scrape(
    'https://care-home.com/facility',
    formats=["markdown"],
    max_age=14400000  # 4 hours in milliseconds
)

# Force fresh scrape, bypass cache
result = firecrawl.scrape(
    'https://care-home.com/facility',
    formats=["markdown"],
    max_age=0  # Always fetch fresh
)
```

The Semantic Index stores full page snapshots with embeddings and structural metadata. When `maxAge` allows, Firecrawl returns cached data instantly instead of re-scraping. This delivers 40% of v2.5 API calls from cache, significantly improving response times.

### Cache defaults by endpoint

- **Scrape endpoint**: `maxAge` defaults to 4 hours (14400000 ms)
- **Crawl endpoint**: Respects scrapeOptions.maxAge for each page
- **Search endpoint**: Results cached based on query and parameters

Cache benefits compound with the 5x cheaper search pricing introduced in v2.5.

## Python SDK usage patterns

### Import and initialization for v2

```python
from firecrawl import Firecrawl
from firecrawl.types import ScrapeOptions

# Initialize (reads fc-YOUR-API-KEY from environment if not specified)
firecrawl = Firecrawl(api_key="fc-YOUR-API-KEY")
```

### Synchronous operations with automatic waiting

```python
# Scrape single URL
scrape_result = firecrawl.scrape(
    'https://care-home.com',
    formats=['markdown', 'html']
)

# Crawl with automatic waiting for completion
crawl_result = firecrawl.crawl(
    'https://care-home-directory.com',
    limit=100,
    scrape_options=ScrapeOptions(formats=['markdown']),
    poll_interval=30  # Check status every 30 seconds
)
```

The `crawl()` method is a waiter—it blocks until the crawl completes. Use `start_crawl()` for asynchronous operation.

### Asynchronous crawl management

```python
# Start crawl without waiting
crawl_job = firecrawl.start_crawl(
    'https://care-home-directory.com',
    limit=100,
    scrape_options=ScrapeOptions(formats=['markdown'])
)

print(f"Crawl started: {crawl_job.id}")

# Check status later
status = firecrawl.get_crawl_status(crawl_job.id)
print(f"Status: {status.status}, Completed: {status.completed}/{status.total}")

# Cancel if needed
cancel_result = firecrawl.cancel_crawl(crawl_job.id)
```

### Async/await support with AsyncFirecrawl

```python
from firecrawl import AsyncFirecrawl
import asyncio

async def scrape_care_homes():
    firecrawl = AsyncFirecrawl(api_key="fc-YOUR-API-KEY")
    
    # Async scrape
    result = await firecrawl.scrape('https://care-home.com')
    
    # Start crawl and watch progress with WebSockets
    started = await firecrawl.start_crawl("https://care-home-directory.com", limit=50)
    
    async for snapshot in firecrawl.watcher(started.id, kind="crawl", poll_interval=2):
        if snapshot.status == "completed":
            print(f"Done: {len(snapshot.data)} pages")
            break
        print(f"Progress: {snapshot.completed}/{snapshot.total}")

asyncio.run(scrape_care_homes())
```

WebSocket watching provides real-time updates without polling. The `watcher()` method yields snapshots as the crawl progresses.

### Method name changes from v1 to v2

| v1 Method | v2 Method | Notes |
|-----------|-----------|-------|
| `scrape_url()` | `scrape()` | Simplified naming |
| `crawl_url()` | `crawl()` | Waiter method (blocks until complete) |
| `async_crawl_url()` | `start_crawl()` | Non-blocking, returns job ID |
| `check_crawl_status()` | `get_crawl_status()` | Status polling |
| `batch_scrape_urls()` | `batch_scrape()` | Waiter method |
| `async_batch_scrape_urls()` | `start_batch_scrape()` | Non-blocking |
| `map_url()` | `map()` | URL discovery |

V2 maintains full backward compatibility through `firecrawl.v1` namespace for legacy code.

## Request and response formats for key endpoints

### Scrape endpoint structure

**Request:**

```python
POST https://api.firecrawl.dev/v2/scrape
Authorization: Bearer fc-YOUR-API-KEY
Content-Type: application/json

{
  "url": "https://care-home.com/facility",
  "formats": ["markdown", "html", {"type": "json", "schema": {...}}],
  "onlyMainContent": true,
  "includeTags": ["h1", "p", ".facility-info"],
  "excludeTags": ["#ads", ".navigation"],
  "maxAge": 14400000,
  "waitFor": 1000,
  "timeout": 30000
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "markdown": "# Care Home Name\n\n...",
    "html": "<html>...",
    "json": {
      "name": "Sunshine Care Home",
      "address": "123 Main St"
    },
    "metadata": {
      "title": "Sunshine Care Home",
      "description": "...",
      "sourceURL": "https://care-home.com/facility",
      "statusCode": 200
    }
  }
}
```

### Crawl endpoint structure

**Request:**

```python
POST https://api.firecrawl.dev/v2/crawl
Authorization: Bearer fc-YOUR-API-KEY

{
  "url": "https://care-home-directory.com",
  "prompt": "Find care home facility pages",
  "limit": 500,
  "maxDiscoveryDepth": 3,
  "sitemap": "include",
  "crawlEntireDomain": false,
  "ignoreQueryParameters": true,
  "scrapeOptions": {
    "formats": ["markdown"],
    "onlyMainContent": true,
    "maxAge": 0
  }
}
```

**Response:**

```json
{
  "success": true,
  "id": "crawl-123-abc-789",
  "url": "https://api.firecrawl.dev/v2/crawl/crawl-123-abc-789"
}
```

Poll the status URL to retrieve results:

```python
GET https://api.firecrawl.dev/v2/crawl/crawl-123-abc-789

{
  "status": "completed",
  "total": 150,
  "completed": 150,
  "creditsUsed": 150,
  "data": [
    {
      "markdown": "...",
      "metadata": {
        "sourceURL": "https://care-home-directory.com/facility-1",
        "statusCode": 200
      }
    },
    ...
  ],
  "next": null
}
```

If results exceed 10MB, the response includes a `next` URL for pagination.

### Extract endpoint structure

**Request:**

```python
POST https://api.firecrawl.dev/v2/extract
Authorization: Bearer fc-YOUR-API-KEY

{
  "urls": ["https://care-home-directory.com/*"],
  "prompt": "Extract care home listings with contact details",
  "schema": {
    "type": "object",
    "properties": {
      "care_homes": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "address": {"type": "string"},
            "phone": {"type": "string"}
          }
        }
      }
    }
  },
  "enableWebSearch": false,
  "includeSubdomains": true,
  "showSources": true
}
```

**Response:**

```json
{
  "success": true,
  "id": "extract-456-def-012"
}
```

Poll for results using the extract status endpoint. The extract endpoint uses the FIRE-1 agent model for advanced reasoning during extraction.

## List crawling implementation best practices

### Design Pydantic schemas with descriptive fields

Field descriptions guide the AI extraction process:

```python
from pydantic import BaseModel, Field

class CareHome(BaseModel):
    name: str = Field(description="Official care home facility name")
    license_number: str = Field(description="State license or registration number")
    address: str = Field(description="Complete street address including zip code")
    phone: str = Field(description="Primary contact phone number")
    capacity: int = Field(description="Maximum resident capacity")
```

The more specific your descriptions, the more accurate the extraction. Mention format expectations (e.g., "ISO date format" or "Phone with area code").

### Optimize pagination for minimal API calls

Set `per_page` parameters to maximum values the site supports:

```python
# Efficient: 10 requests for 1000 items at 100/page
listing_urls = [
    f"https://directory.com/listings?page={p}&per_page=100"
    for p in range(1, 11)
]

# Inefficient: 50 requests for 1000 items at 20/page
listing_urls = [
    f"https://directory.com/listings?page={p}&per_page=20"
    for p in range(1, 51)
]
```

Fewer requests reduce costs and complete faster while respecting site rate limits.

### Save intermediate results for resilience

Persist data after each phase to avoid re-scraping on failures:

```python
import json

# After Phase 1
with open('care_homes_list.json', 'w') as f:
    json.dump(all_care_homes, f, indent=2)

# After Phase 2
with open('care_homes_detailed.json', 'w') as f:
    json.dump(detailed_profiles, f, indent=2)
```

Resume from saved data rather than starting over if errors occur during large extractions.

### Test schemas on small samples first

Validate schema accuracy before scaling:

```python
# Test with 5 pages
test_urls = listing_urls[:5]
test_result = firecrawl.batch_scrape(
    test_urls,
    formats=[{"type": "json", "schema": CareHomeList}]
)

# Inspect results
for page in test_result.data:
    print(page.json)

# Iterate on schema if needed, then scale up
```

This workflow catches schema design issues early, saving credits on full-scale extractions.

## Breaking changes and deprecated features: None

**Firecrawl v2.5 introduces zero breaking changes.** All v2.0 code continues working without modification. The SDK maintains full compatibility, requiring no version-specific adjustments.

### What hasn't changed

- All API endpoints remain identical (`/v2/scrape`, `/v2/crawl`, `/v2/search`, `/v2/extract`)
- Parameter names stay the same (except defaults like `maxAge`)
- Response formats maintain consistency
- Authentication uses the same Bearer token approach
- SDKs (Python, JavaScript/TypeScript) work without updates

### No deprecated features in v2.5

Firecrawl hasn't removed or deprecated any v2.0 functionality. The release focuses exclusively on infrastructure improvements and quality enhancements. Feature additions in v2.5:

- Excel (.xlsx) file scraping support
- Enhanced Semantic Index coverage
- Improved NUQ concurrency system

These are additive capabilities. Existing workflows continue unchanged.

### Upgrading from v1 to v2

If migrating from v1, review the v2 migration guide at docs.firecrawl.dev. Key changes from v1→v2:

- `sitemap` changed from boolean to enum (`"include"`, `"skip"`)
- `maxDepth` renamed to `maxDiscoveryDepth`
- `crawlEntireDomain` replaces `allowBackwardCrawling`
- Response formats organized by source type for search
- JSON extraction moved from `jsonOptions` to `formats` array

The v1 API remains available through `firecrawl.v1` namespace for legacy code.

## Practical care home scraper example

Here's production-ready code implementing the two-phase pattern with error handling and incremental saves:

```python
from firecrawl import Firecrawl
from pydantic import BaseModel, Field
from typing import List, Optional
import json
from pathlib import Path

# Initialize
firecrawl = Firecrawl(api_key="fc-YOUR-API-KEY")

# Phase 1 Schema
class CareHomeListing(BaseModel):
    name: str = Field(description="Care home facility name")
    url: str = Field(description="Full URL to detail page")
    city: str = Field(description="City location")
    state: str = Field(description="Two-letter state code")

class CareHomeListPage(BaseModel):
    care_homes: List[CareHomeListing]

# Phase 2 Schema
class CareHomeDetails(BaseModel):
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    phone: str
    email: Optional[str]
    website: Optional[str]
    administrator: Optional[str]
    capacity: int
    care_types: List[str] = Field(description="Types of care provided")
    amenities: List[str] = Field(description="Facility amenities")
    accepts_medicaid: bool
    accepts_medicare: bool
    rating: Optional[float] = Field(description="Overall rating out of 5")
    inspection_date: Optional[str] = Field(description="Last inspection date")
    violations: Optional[int] = Field(description="Number of violations")

def extract_care_home_listings(base_url: str, total_pages: int) -> List[dict]:
    """Phase 1: Extract list of care homes from directory pages."""
    
    # Generate pagination URLs
    listing_urls = [
        f"{base_url}/listings?page={p}&per_page=50"
        for p in range(1, total_pages + 1)
    ]
    
    print(f"Phase 1: Extracting listings from {len(listing_urls)} pages...")
    
    # Batch scrape with schema
    result = firecrawl.batch_scrape(
        listing_urls,
        formats=[{"type": "json", "schema": CareHomeListPage}]
    )
    
    # Aggregate results
    all_listings = []
    for page_data in result.data:
        if 'care_homes' in page_data.json:
            all_listings.extend(page_data.json['care_homes'])
    
    # Save checkpoint
    Path('output').mkdir(exist_ok=True)
    with open('output/care_homes_list.json', 'w') as f:
        json.dump(all_listings, f, indent=2)
    
    print(f"✓ Extracted {len(all_listings)} care home listings")
    return all_listings

def extract_care_home_details(listings: List[dict], batch_size: int = 50) -> List[dict]:
    """Phase 2: Extract detailed information for each care home."""
    
    detail_urls = [listing['url'] for listing in listings]
    all_details = []
    
    # Process in batches for incremental saves
    for i in range(0, len(detail_urls), batch_size):
        batch_urls = detail_urls[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        print(f"Phase 2: Extracting batch {batch_num} ({len(batch_urls)} facilities)...")
        
        try:
            result = firecrawl.batch_scrape(
                batch_urls,
                formats=[{"type": "json", "schema": CareHomeDetails}]
            )
            
            # Collect batch results
            batch_details = [page.json for page in result.data]
            all_details.extend(batch_details)
            
            # Save batch checkpoint
            with open(f'output/care_homes_batch_{batch_num}.json', 'w') as f:
                json.dump(batch_details, f, indent=2)
            
            print(f"✓ Completed batch {batch_num}")
            
        except Exception as e:
            print(f"✗ Error in batch {batch_num}: {e}")
            continue
    
    # Save complete dataset
    with open('output/care_homes_complete.json', 'w') as f:
        json.dump(all_details, f, indent=2)
    
    print(f"✓ Extracted {len(all_details)} detailed profiles")
    return all_details

# Execute extraction
if __name__ == "__main__":
    BASE_URL = "https://care-home-directory.com"
    TOTAL_PAGES = 20
    
    # Phase 1: Get listings
    listings = extract_care_home_listings(BASE_URL, TOTAL_PAGES)
    
    # Phase 2: Get details
    details = extract_care_home_details(listings, batch_size=50)
    
    print(f"\n✅ Complete! Extracted {len(details)} care home profiles")
    print(f"Results saved to output/ directory")
```

This implementation handles pagination efficiently, processes data in batches with checkpoints, and provides clear progress feedback. The batch size of 50 balances API efficiency with incremental saves for resilience.

## Advanced configuration options

### Control discovery depth and domain scope

```python
crawl_result = firecrawl.crawl(
    url="https://care-home-directory.com/region/california",
    maxDiscoveryDepth=2,  # Only follow links 2 levels deep
    crawlEntireDomain=False,  # Stay within /region/california path
    sitemap="include",  # Use sitemap but also discover unlisted pages
    ignoreQueryParameters=True,  # Treat /page?id=1 and /page?id=2 as same
    limit=500
)
```

**`maxDiscoveryDepth`** defines crawl depth from the starting URL and sitemapped pages (which have depth 0). Setting `maxDiscoveryDepth=1` with `sitemap="skip"` crawls only the start URL plus pages it links to directly.

**`crawlEntireDomain=true`** allows following links to sibling and parent URLs, not just child paths. Use false to restrict crawling to deeper paths only (e.g., /features/feature-1 → /features/feature-1/tips ✅, but not /pricing ❌).

### Filter URLs with regex patterns

```python
crawl_result = firecrawl.crawl(
    url="https://care-home-directory.com",
    includePaths=[r"^/facilities/.*$", r"^/locations/.*$"],
    excludePaths=[r"^/blog/.*$", r"^/admin/.*$", r"^/api/.*$"],
    limit=1000
)
```

Patterns match against the URL pathname. For base URL `https://example.com`, the pattern `blog/.*` excludes `https://example.com/blog/post-1` and all other `/blog/*` paths.

### Control concurrent requests and delays

```python
crawl_result = firecrawl.crawl(
    url="https://care-home-directory.com",
    maxConcurrency=5,  # Limit to 5 concurrent scrapes
    delay=2,  # Wait 2 seconds between requests
    limit=200
)
```

The `delay` parameter respects website rate limits. `maxConcurrency` sets per-crawl limits; if unspecified, your team's account-level concurrency applies.

### Execute actions before scraping

Interact with pages before extracting content:

```python
result = firecrawl.scrape(
    'https://care-home-search.com',
    formats=["markdown"],
    actions=[
        {
            "type": "click",
            "selector": "#accept-cookies"
        },
        {
            "type": "wait",
            "milliseconds": 2000
        },
        {
            "type": "click",
            "selector": "#show-more-results"
        },
        {
            "type": "scroll",
            "direction": "down"
        }
    ]
)
```

Available action types: `wait`, `click`, `scroll`, `input`, `screenshot`. Actions execute sequentially before content extraction.

This comprehensive validation confirms your search parameter formats are correct but your crawl parameter needs correction from `crawlPrompt` to `prompt`. Firecrawl v2.5's batch_scrape with Pydantic schemas provides the optimal approach for extracting structured care home data, combining zero-selector resilience with JavaScript handling and database-ready output.
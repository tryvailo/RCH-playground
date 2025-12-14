"""
Pydantic Models for API Testing Suite
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ApiStatus(str, Enum):
    """API Status Enum"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    TESTING = "testing"
    ERROR = "error"


# ==================== Credentials Models ====================

class CQCCredentials(BaseModel):
    """CQC API Credentials"""
    partner_code: Optional[str] = None
    use_without_code: bool = Field(default=True, description="Use API without partner code")
    primary_subscription_key: Optional[str] = None
    secondary_subscription_key: Optional[str] = None
    
    class Config:
        populate_by_name = True  # Pydantic v2
        allow_population_by_field_name = True  # Pydantic v1 compatibility
    
    def __init__(self, **data):
        # Normalize both camelCase and snake_case to snake_case
        normalized_data = {}
        field_mapping = {
            'partnerCode': 'partner_code',
            'useWithoutCode': 'use_without_code',
            'primarySubscriptionKey': 'primary_subscription_key',
            'secondarySubscriptionKey': 'secondary_subscription_key',
        }
        
        for key, value in data.items():
            if key in field_mapping:
                # Map camelCase to snake_case
                snake_key = field_mapping[key]
                # Use the value if snake_case key doesn't exist or camelCase value is not None
                if snake_key not in normalized_data or value is not None:
                    normalized_data[snake_key] = value
            elif key in ['partner_code', 'use_without_code', 'primary_subscription_key', 'secondary_subscription_key']:
                # Keep snake_case as is
                normalized_data[key] = value
        
        super().__init__(**normalized_data)


class CompaniesHouseCredentials(BaseModel):
    """Companies House API Credentials"""
    api_key: Optional[str] = Field(None, alias="apiKey")
    apiKey: Optional[str] = None  # Support camelCase from frontend
    
    class Config:
        allow_population_by_field_name = True
    
    def __init__(self, **data):
        # Normalize camelCase to snake_case
        if 'apiKey' in data and 'api_key' not in data:
            data['api_key'] = data.pop('apiKey')
        super().__init__(**data)


class GooglePlacesCredentials(BaseModel):
    """Google Places API Credentials"""
    api_key: Optional[str] = None
    
    class Config:
        populate_by_name = True  # Pydantic v2
        allow_population_by_field_name = True  # Pydantic v1 compatibility
    
    def __init__(self, **data):
        # Normalize both camelCase and snake_case to snake_case
        normalized_data = {}
        
        # Handle both formats
        if 'apiKey' in data:
            normalized_data['api_key'] = data['apiKey']
        elif 'api_key' in data:
            normalized_data['api_key'] = data['api_key']
        
        super().__init__(**normalized_data)


class GooglePlacesInsightsCredentials(BaseModel):
    """Google Places Insights Credentials"""
    project_id: Optional[str] = Field(None, alias="projectId")
    projectId: Optional[str] = None  # Support camelCase from frontend
    dataset_id: Optional[str] = Field(None, alias="datasetId")
    datasetId: Optional[str] = None  # Support camelCase from frontend
    
    class Config:
        allow_population_by_field_name = True


class PerplexityCredentials(BaseModel):
    """Perplexity API Credentials"""
    api_key: Optional[str] = Field(None, alias="apiKey")
    apiKey: Optional[str] = None  # Support camelCase from frontend
    
    class Config:
        allow_population_by_field_name = True
    
    def __init__(self, **data):
        # Normalize camelCase to snake_case
        if 'apiKey' in data and 'api_key' not in data:
            data['api_key'] = data.pop('apiKey')
        super().__init__(**data)


class BestTimeCredentials(BaseModel):
    """BestTime.app API Credentials"""
    private_key: Optional[str] = Field(None, alias="privateKey")
    privateKey: Optional[str] = None  # Support camelCase from frontend
    public_key: Optional[str] = Field(None, alias="publicKey")
    publicKey: Optional[str] = None  # Support camelCase from frontend
    
    class Config:
        allow_population_by_field_name = True
    
    def __init__(self, **data):
        # Normalize camelCase to snake_case
        if 'privateKey' in data and 'private_key' not in data:
            data['private_key'] = data.pop('privateKey')
        if 'publicKey' in data and 'public_key' not in data:
            data['public_key'] = data.pop('publicKey')
        super().__init__(**data)


class AutumnaCredentials(BaseModel):
    """Autumna Scraping Credentials"""
    proxy_url: Optional[str] = Field(None, alias="proxyUrl")
    proxyUrl: Optional[str] = None  # Support camelCase from frontend
    use_proxy: bool = Field(default=False, alias="useProxy")
    useProxy: Optional[bool] = None  # Support camelCase from frontend
    
    class Config:
        allow_population_by_field_name = True
    
    def __init__(self, **data):
        # Normalize camelCase to snake_case
        if 'proxyUrl' in data and 'proxy_url' not in data:
            data['proxy_url'] = data.pop('proxyUrl')
        if 'useProxy' in data and 'use_proxy' not in data:
            data['use_proxy'] = data.pop('useProxy')
        super().__init__(**data)


class OpenAICredentials(BaseModel):
    """OpenAI API Credentials"""
    api_key: Optional[str] = None
    
    class Config:
        populate_by_name = True  # Pydantic v2
        allow_population_by_field_name = True  # Pydantic v1 compatibility
    
    def __init__(self, **data):
        # Normalize both camelCase and snake_case to snake_case
        normalized_data = {}
        
        # Handle both formats
        if 'apiKey' in data:
            normalized_data['api_key'] = data['apiKey']
        elif 'api_key' in data:
            normalized_data['api_key'] = data['api_key']
        
        super().__init__(**normalized_data)


class FirecrawlCredentials(BaseModel):
    """Firecrawl API Credentials"""
    api_key: Optional[str] = Field(None, alias="apiKey")
    apiKey: Optional[str] = None  # Support camelCase from frontend
    
    class Config:
        allow_population_by_field_name = True
    
    def __init__(self, **data):
        # Normalize camelCase to snake_case
        if 'apiKey' in data and 'api_key' not in data:
            data['api_key'] = data.pop('apiKey')
        super().__init__(**data)

class AnthropicCredentials(BaseModel):
    """Anthropic Claude API Credentials"""
    api_key: Optional[str] = Field(None, alias="apiKey")
    apiKey: Optional[str] = None  # Support camelCase from frontend
    
    class Config:
        allow_population_by_field_name = True


class OSPlacesCredentials(BaseModel):
    """Ordnance Survey Places API Credentials"""
    api_key: Optional[str] = Field(None, alias="apiKey")
    apiKey: Optional[str] = None  # Support camelCase from frontend
    api_secret: Optional[str] = Field(None, alias="apiSecret")
    apiSecret: Optional[str] = None  # Support camelCase from frontend
    places_endpoint: str = Field("https://api.os.uk/search/places/v1/", alias="placesEndpoint")
    placesEndpoint: Optional[str] = None  # Support camelCase from frontend
    features_endpoint: str = Field("https://api.os.uk/features/v1/wfs", alias="featuresEndpoint")
    featuresEndpoint: Optional[str] = None  # Support camelCase from frontend
    
    class Config:
        allow_population_by_field_name = True


class ApiCredentials(BaseModel):
    """Complete API Credentials"""
    cqc: Optional[CQCCredentials] = None
    fsa: Optional[Dict[str, Any]] = Field(default_factory=dict, description="FSA doesn't need credentials")
    companies_house: Optional[CompaniesHouseCredentials] = Field(None, alias="companiesHouse")
    companiesHouse: Optional[CompaniesHouseCredentials] = None  # Support camelCase from frontend
    google_places: Optional[GooglePlacesCredentials] = None
    google_places_insights: Optional[GooglePlacesInsightsCredentials] = Field(None, alias="googlePlacesInsights")
    googlePlacesInsights: Optional[GooglePlacesInsightsCredentials] = None  # Support camelCase from frontend
    perplexity: Optional[PerplexityCredentials] = None
    besttime: Optional[BestTimeCredentials] = None
    autumna: Optional[AutumnaCredentials] = None
    openai: Optional[OpenAICredentials] = None
    firecrawl: Optional[FirecrawlCredentials] = None
    anthropic: Optional[AnthropicCredentials] = None
    os_places: Optional[OSPlacesCredentials] = Field(None, alias="osPlaces")
    osPlaces: Optional[OSPlacesCredentials] = None  # Support camelCase from frontend
    
    class Config:
        allow_population_by_field_name = True
    
    def __init__(self, **data):
        # Normalize camelCase to snake_case for top-level fields
        normalized_data = {}
        field_mapping = {
            'companiesHouse': 'companies_house',
            'googlePlaces': 'google_places',
            'googlePlacesInsights': 'google_places_insights',
            'osPlaces': 'os_places',
        }
        
        for key, value in data.items():
            if key in field_mapping:
                # Map camelCase to snake_case
                normalized_data[field_mapping[key]] = value
            elif key not in ['companiesHouse', 'googlePlaces', 'googlePlacesInsights', 'osPlaces']:
                # Keep snake_case as is
                normalized_data[key] = value
        
        super().__init__(**normalized_data)


# ==================== Test Request Models ====================

class HomeData(BaseModel):
    """Care Home Data"""
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class TestRequest(BaseModel):
    """Individual API Test Request"""
    home_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    region: Optional[str] = None
    company_name: Optional[str] = None
    query: Optional[str] = None
    max_distance: Optional[float] = Field(default=1.0, description="Max distance in km")
    limit: Optional[int] = Field(default=10, description="Result limit")


class PerplexityResearchRequest(BaseModel):
    """Perplexity Research Request"""
    home_name: str
    address: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    location: Optional[str] = None  # For reputation endpoint compatibility
    date_range: Optional[str] = Field(default="last_7_days", description="Date range: last_7_days, last_30_days, month, year")
    
    class Config:
        # Allow None values to be converted to empty strings
        json_encoders = {
            type(None): lambda v: None
        }


class PerplexitySearchRequest(BaseModel):
    """Perplexity Custom Search Request"""
    query: str
    model: str = "sonar-pro"
    max_tokens: int = 1000
    search_recency_filter: str = "month"


class ComprehensiveTestRequest(BaseModel):
    """Comprehensive Test Request"""
    home_name: Optional[str] = None
    homeName: Optional[str] = None  # Support camelCase from frontend
    address: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    apis_to_test: Optional[List[str]] = Field(
        default_factory=lambda: ["cqc", "fsa", "companies_house", "google_places", "perplexity", "besttime", "autumna"],
        description="List of APIs to test"
    )
    apisToTest: Optional[List[str]] = None  # Support camelCase from frontend
    
    class Config:
        allow_population_by_field_name = True
    
    def __init__(self, **data):
        # Normalize field names: prefer snake_case, fallback to camelCase
        if "homeName" in data and "home_name" not in data:
            data["home_name"] = data.pop("homeName")
        if "apisToTest" in data and "apis_to_test" not in data:
            data["apis_to_test"] = data.pop("apisToTest")
        super().__init__(**data)


# ==================== Test Response Models ====================

class DataQuality(BaseModel):
    """Data Quality Metrics"""
    completeness: float = Field(ge=0, le=100, description="Completeness percentage")
    accuracy: float = Field(ge=0, le=100, description="Accuracy percentage")
    freshness: str = Field(description="Data freshness indicator")


class ApiTestResult(BaseModel):
    """Individual API Test Result"""
    api_name: str
    status: str = Field(description="success, failure, or partial")
    response_time: float = Field(description="Response time in seconds")
    data_returned: bool
    data_quality: DataQuality
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    raw_response: Dict[str, Any] = Field(default_factory=dict)
    cost_incurred: float = Field(default=0.0, description="Cost in GBP")


class ComprehensiveTestResponse(BaseModel):
    """Comprehensive Test Response"""
    job_id: str
    status: str = Field(description="running, completed, or failed")
    message: str


class TestResults(BaseModel):
    """Complete Test Results"""
    job_id: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    results: Dict[str, ApiTestResult]
    fusion_analysis: Optional[Dict[str, Any]] = None
    total_cost: float = 0.0
    progress: int = Field(ge=0, le=100)


# ==================== Analytics Models ====================

class ApiStatusInfo(BaseModel):
    """API Status Information"""
    name: str
    status: ApiStatus
    last_tested: Optional[datetime] = None
    success_rate: float = Field(ge=0, le=100)
    avg_response_time: float = Field(ge=0)


class QuickStats(BaseModel):
    """Quick Statistics"""
    total_apis: int
    connected_apis: int
    total_costs: float
    tests_passed: int


class DashboardView(BaseModel):
    """Dashboard View Model"""
    apis: List[ApiStatusInfo]
    recent_tests: List[TestResults]
    quick_stats: QuickStats


# ==================== Cost Models ====================

class CostBreakdown(BaseModel):
    """Cost Breakdown"""
    api: str
    calls: int
    cost_per_call: float
    total_cost: float
    currency: str = "GBP"


# ==================== Export Models ====================

class ExportRequest(BaseModel):
    """Export Request"""
    job_id: str
    format: str = Field(description="csv, json, or pdf")
    include_raw_data: bool = Field(default=False)


class FirecrawlAnalyzeRequest(BaseModel):
    """Firecrawl Analyze Request"""
    url: str
    care_home_name: Optional[str] = None


class FirecrawlUnifiedAnalysisRequest(BaseModel):
    """Firecrawl Unified Analysis Request"""
    care_home_name: str
    website_url: str
    address: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None


class FirecrawlBatchAnalyzeRequest(BaseModel):
    """Batch analyze multiple care homes"""
    care_homes: List[Dict[str, str]] = Field(
        description="List of care homes with name and url",
        example=[
            {"name": "Manor House", "url": "https://manorhouse.com"},
            {"name": "Sunshine Care", "url": "https://sunshinecare.com"}
        ]
    )
    
    class Config:
        schema_extra = {
            "example": {
                "care_homes": [
                    {"name": "Manor House", "url": "https://manorhouse.com"},
                    {"name": "Sunshine Care", "url": "https://sunshinecare.com"}
                ]
            }
        }


class FirecrawlSearchRequest(BaseModel):
    """Firecrawl Web Search Request"""
    query: str = Field(description="Search query")
    limit: int = Field(default=10, ge=1, le=100, description="Number of results")
    sources: Optional[List[str]] = Field(
        default=None,
        description="Result types: web, news, images"
    )
    categories: Optional[List[str]] = Field(
        default=None,
        description="Categories: github, research, pdf"
    )
    location: Optional[str] = Field(
        default=None,
        description="Location filter for search results"
    )
    tbs: Optional[str] = Field(
        default=None,
        description="Time-based search filter (e.g., 'qdr:d' for past day)"
    )
    timeout: Optional[int] = Field(
        default=None,
        ge=1,
        le=300,
        description="Timeout in seconds for search operation"
    )
    scrape_options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Options for scraping search results (formats, etc.)"
    )


class PerplexityAcademicResearchRequest(BaseModel):
    """Perplexity Academic Research Request"""
    topics: List[str] = Field(description="List of research topics to search for")


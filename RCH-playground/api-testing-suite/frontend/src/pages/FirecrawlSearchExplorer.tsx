import { useState } from 'react';
import { Search, Globe, FileText, TrendingUp, AlertCircle, CheckCircle, Loader, Image, Newspaper, Code, BookOpen, Calendar, Zap, PoundSterling, Info } from 'lucide-react';
import axios from 'axios';

interface SearchResult {
  url: string;
  title: string;
  description?: string;
  position?: number;
  category?: string;
}

interface SearchResponse {
  web?: SearchResult[];
  images?: Array<{
    title: string;
    imageUrl: string;
    imageWidth?: number;
    imageHeight?: number;
    url: string;
    position?: number;
  }>;
  news?: Array<{
    title: string;
    url: string;
    snippet?: string;
    date?: string;
    position?: number;
  }>;
}

interface PricingBreakdown {
  meals_included?: boolean | null;
  activities_included?: boolean | null;
  activities_cost?: number | null;
  transport_included?: boolean | null;
  transport_cost?: number | null;
  additional_services?: string[];
}

interface PricingData {
  fee_residential_from?: number | null;
  fee_residential_to?: number | null;
  fee_nursing_from?: number | null;
  fee_nursing_to?: number | null;
  fee_dementia_residential_from?: number | null;
  fee_dementia_residential_to?: number | null;
  fee_dementia_nursing_from?: number | null;
  fee_dementia_nursing_to?: number | null;
  fee_respite_from?: number | null;
  fee_respite_to?: number | null;
  pricing_breakdown?: PricingBreakdown;
  pricing_notes?: string;
  pricing_confidence?: number;
  currency?: string;
  billing_period?: string;
}

interface PricingResult {
  care_home_name: string;
  website_url: string;
  postcode?: string;
  extraction_method: string;
  scraped_at: string;
  pricing: PricingData;
}

interface TestSearchExample {
  label: string;
  query: string;
  limit?: number;
  sources?: string[];
  categories?: string[];
  location?: string;
  tbs?: string;
  description?: string;
}

const TEST_SEARCH_EXAMPLES: Record<string, TestSearchExample[]> = {
  'Metchley Manor': [
    {
      label: 'Базовый поиск',
      query: 'Metchley Manor care home Birmingham',
      limit: 10,
      sources: ['web'],
      location: 'Birmingham',
      description: 'Общий поиск информации о доме'
    },
    {
      label: 'Новости',
      query: 'Metchley Manor care home news Birmingham',
      limit: 10,
      sources: ['news'],
      tbs: 'qdr:m',
      description: 'Последние новости за месяц'
    },
    {
      label: 'Отзывы',
      query: 'Metchley Manor care home reviews Birmingham',
      limit: 10,
      sources: ['web'],
      description: 'Отзывы и рейтинги'
    },
    {
      label: 'Изображения',
      query: 'Metchley Manor care home Birmingham images photos',
      limit: 8,
      sources: ['images'],
      description: 'Фотографии и визуальный контент'
    },
    {
      label: 'CQC отчет',
      query: 'Metchley Manor CQC inspection report PDF',
      limit: 10,
      categories: ['pdf'],
      description: 'Официальные отчеты CQC'
    },
    {
      label: 'Extract Pricing',
      query: 'Metchley Manor care home pricing fees Birmingham',
      limit: 10,
      sources: ['web'],
      description: 'Извлечение цен с сайта'
    }
  ],
  'Clare Court': [
    {
      label: 'Базовый поиск',
      query: 'Clare Court care home Birmingham',
      limit: 10,
      sources: ['web'],
      location: 'Birmingham',
      description: 'Общий поиск информации о доме'
    },
    {
      label: 'Новости',
      query: 'Clare Court Avery Healthcare news Birmingham',
      limit: 10,
      sources: ['news'],
      tbs: 'qdr:m',
      description: 'Последние новости за месяц'
    },
    {
      label: 'Отзывы',
      query: 'Clare Court care home reviews Birmingham',
      limit: 10,
      sources: ['web'],
      description: 'Отзывы и рейтинги'
    },
    {
      label: 'Изображения',
      query: 'Clare Court care home Birmingham photos',
      limit: 8,
      sources: ['images'],
      description: 'Фотографии и визуальный контент'
    },
    {
      label: 'CQC отчет',
      query: 'Clare Court CQC inspection report PDF',
      limit: 10,
      categories: ['pdf'],
      description: 'Официальные отчеты CQC'
    },
    {
      label: 'Extract Pricing',
      query: 'Clare Court care home pricing fees Birmingham',
      limit: 10,
      sources: ['web'],
      description: 'Извлечение цен с сайта'
    }
  ],
  'Bartley Green': [
    {
      label: 'Базовый поиск',
      query: 'Bartley Green Lodge care home Birmingham',
      limit: 10,
      sources: ['web'],
      location: 'Birmingham',
      description: 'Общий поиск информации о доме'
    },
    {
      label: 'Новости',
      query: 'Bartley Green Sanctuary Care news',
      limit: 10,
      sources: ['news'],
      tbs: 'qdr:m',
      description: 'Последние новости за месяц'
    },
    {
      label: 'Отзывы',
      query: 'Bartley Green Lodge care home reviews',
      limit: 10,
      sources: ['web'],
      description: 'Отзывы и рейтинги'
    },
    {
      label: 'Изображения',
      query: 'Bartley Green Lodge care home photos',
      limit: 8,
      sources: ['images'],
      description: 'Фотографии и визуальный контент'
    },
    {
      label: 'CQC отчет',
      query: 'Bartley Green Lodge CQC report PDF',
      limit: 10,
      categories: ['pdf'],
      description: 'Официальные отчеты CQC'
    },
    {
      label: 'Extract Pricing',
      query: 'Bartley Green Lodge care home pricing fees',
      limit: 10,
      sources: ['web'],
      description: 'Извлечение цен с сайта'
    }
  ],
  'Inglewood': [
    {
      label: 'Базовый поиск',
      query: 'Inglewood care home Birmingham',
      limit: 10,
      sources: ['web'],
      location: 'Birmingham',
      description: 'Общий поиск информации о доме'
    },
    {
      label: 'Новости',
      query: 'Inglewood Care UK news Birmingham',
      limit: 10,
      sources: ['news'],
      tbs: 'qdr:m',
      description: 'Последние новости за месяц'
    },
    {
      label: 'Отзывы',
      query: 'Inglewood care home reviews Birmingham',
      limit: 10,
      sources: ['web'],
      description: 'Отзывы и рейтинги'
    },
    {
      label: 'Изображения',
      query: 'Inglewood care home Birmingham images',
      limit: 8,
      sources: ['images'],
      description: 'Фотографии и визуальный контент'
    },
    {
      label: 'CQC отчет',
      query: 'Inglewood care home CQC inspection PDF',
      limit: 10,
      categories: ['pdf'],
      description: 'Официальные отчеты CQC'
    },
    {
      label: 'Extract Pricing',
      query: 'Inglewood care home pricing fees Birmingham',
      limit: 10,
      sources: ['web'],
      description: 'Извлечение цен с сайта'
    }
  ]
};

export default function FirecrawlSearchExplorer() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SearchResponse | null>(null);
  const [cost, setCost] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  
  // Pricing extraction state
  const [loadingPricing, setLoadingPricing] = useState<string | null>(null);
  const [pricingResults, setPricingResults] = useState<Map<string, PricingResult>>(new Map());
  const [pricingError, setPricingError] = useState<string | null>(null);

  // Search form
  const [searchForm, setSearchForm] = useState({
    query: '',
    limit: 10,
    sources: [] as string[],
    categories: [] as string[],
    location: '',
    tbs: '',
    timeout: '',
    enableScraping: false,
  });

  const handleSearch = async () => {
    if (!searchForm.query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setPricingResults(new Map());
    setPricingError(null);
    
    try {
      const payload: any = {
        query: searchForm.query.trim(),
        limit: searchForm.limit,
      };

      if (searchForm.sources.length > 0) {
        payload.sources = searchForm.sources;
      }
      if (searchForm.categories.length > 0) {
        payload.categories = searchForm.categories;
      }
      if (searchForm.location.trim()) {
        payload.location = searchForm.location.trim();
      }
      if (searchForm.tbs) {
        payload.tbs = searchForm.tbs;
      }
      if (searchForm.timeout) {
        payload.timeout = parseInt(searchForm.timeout);
      }
      if (searchForm.enableScraping) {
        payload.scrape_options = {
          formats: ['markdown', 'links']
        };
      }

      const response = await axios.post('/api/firecrawl/search', payload);

      if (response.data.status === 'success') {
        setResult(response.data.data);
        setCost(response.data.cost || 0);
      } else {
        setError(response.data.message || 'Search failed');
      }
    } catch (error: any) {
      console.error('Firecrawl search error:', error);
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Unknown error occurred';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const toggleSource = (source: string) => {
    setSearchForm(prev => ({
      ...prev,
      sources: prev.sources.includes(source)
        ? prev.sources.filter(s => s !== source)
        : [...prev.sources, source]
    }));
  };

  const toggleCategory = (category: string) => {
    setSearchForm(prev => ({
      ...prev,
      categories: prev.categories.includes(category)
        ? prev.categories.filter(c => c !== category)
        : [...prev.categories, category]
    }));
  };

  const loadExample = async (example: TestSearchExample) => {
    // Update form first
    const newForm = {
      query: example.query,
      limit: example.limit || 10,
      sources: example.sources || [],
      categories: example.categories || [],
      location: example.location || '',
      tbs: example.tbs || '',
      timeout: '',
      enableScraping: false,
    };
    setSearchForm(newForm);
    
    // Automatically trigger search after a short delay to ensure form is updated
    setTimeout(async () => {
      setLoading(true);
      setError(null);
      setResult(null);
      setPricingResults(new Map());
      setPricingError(null);
      
      try {
        const payload: any = {
          query: newForm.query.trim(),
          limit: newForm.limit,
        };

        if (newForm.sources.length > 0) {
          payload.sources = newForm.sources;
        }
        if (newForm.categories.length > 0) {
          payload.categories = newForm.categories;
        }
        if (newForm.location.trim()) {
          payload.location = newForm.location.trim();
        }
        if (newForm.tbs) {
          payload.tbs = newForm.tbs;
        }
        if (newForm.timeout) {
          payload.timeout = parseInt(newForm.timeout);
        }
        if (newForm.enableScraping) {
          payload.scrape_options = {
            formats: ['markdown', 'links']
          };
        }

        const response = await axios.post('/api/firecrawl/search', payload);

        if (response.data.status === 'success') {
          setResult(response.data.data);
          setCost(response.data.cost || 0);
        } else {
          setError(response.data.message || 'Search failed');
        }
      } catch (error: any) {
        console.error('Firecrawl search error:', error);
        const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Unknown error occurred';
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    }, 100);
  };

  const handleExtractPricing = async (url: string, title?: string) => {
    if (loadingPricing) return;
    
    setLoadingPricing(url);
    setPricingError(null);
    
    try {
      const response = await axios.post('/api/firecrawl/search/extract-pricing', {
        url: url,
        care_home_name: title || undefined,
        postcode: undefined
      });
      
      if (response.data.status === 'success') {
        setPricingResults(prev => {
          const newMap = new Map(prev);
          newMap.set(url, response.data.data);
          return newMap;
        });
      } else {
        setPricingError(response.data.message || 'Pricing extraction failed');
      }
    } catch (error: any) {
      console.error('Pricing extraction error:', error);
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Unknown error occurred';
      setPricingError(errorMessage);
    } finally {
      setLoadingPricing(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Globe className="w-6 h-6 text-primary" />
              Firecrawl Search Explorer
            </h1>
            <p className="text-gray-600 mt-1">
              Search the web and find information about care homes using Firecrawl Search API
            </p>
          </div>
          {cost > 0 && (
            <div className="text-right">
              <div className="text-sm text-gray-500">Total Cost</div>
              <div className="text-2xl font-bold text-primary">£{cost.toFixed(4)}</div>
            </div>
          )}
        </div>

        {/* Test Examples */}
        <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Zap className="w-4 h-4 text-blue-600" />
            Быстрые тестовые примеры
          </h3>
          <div className="space-y-4">
            {Object.entries(TEST_SEARCH_EXAMPLES).map(([homeName, examples]) => (
              <div key={homeName} className="bg-white rounded-lg p-3 border border-gray-200">
                <div className="font-semibold text-gray-900 mb-2 text-sm">{homeName}</div>
                <div className="flex flex-wrap gap-2">
                  {examples.map((example, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => loadExample(example)}
                      className="text-left px-3 py-2 bg-gray-50 hover:bg-primary hover:text-white rounded-lg border border-gray-200 hover:border-primary transition-all group text-xs"
                      title={example.description}
                    >
                      <div className="font-medium">{example.label}</div>
                      {example.description && (
                        <div className="text-gray-500 group-hover:text-white/80 text-xs mt-0.5">
                          {example.description}
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-600 mt-3">
            💡 Кликните на пример для автоматического заполнения формы
          </p>
        </div>

        {/* Search Form */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Search Query *
            </label>
            <input
              type="text"
              value={searchForm.query}
              onChange={(e) => setSearchForm(prev => ({ ...prev, query: e.target.value }))}
              placeholder="e.g., care homes Birmingham, nursing homes UK, dementia care facilities"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Results Limit
              </label>
              <input
                type="number"
                min="1"
                max="100"
                value={searchForm.limit}
                onChange={(e) => setSearchForm(prev => ({ ...prev, limit: parseInt(e.target.value) || 10 }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Location (optional)
              </label>
              <input
                type="text"
                value={searchForm.location}
                onChange={(e) => setSearchForm(prev => ({ ...prev, location: e.target.value }))}
                placeholder="e.g., UK, Birmingham, London"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
          </div>

          {/* Sources */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Result Types (optional)
            </label>
            <div className="flex flex-wrap gap-2">
              {['web', 'news', 'images'].map(source => (
                <button
                  key={source}
                  type="button"
                  onClick={() => toggleSource(source)}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 ${
                    searchForm.sources.includes(source)
                      ? 'bg-primary text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {source === 'web' && <Globe className="w-4 h-4" />}
                  {source === 'news' && <Newspaper className="w-4 h-4" />}
                  {source === 'images' && <Image className="w-4 h-4" />}
                  {source.charAt(0).toUpperCase() + source.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Categories */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Categories (optional)
            </label>
            <div className="flex flex-wrap gap-2">
              {[
                { value: 'github', label: 'GitHub', icon: Code },
                { value: 'research', label: 'Research', icon: BookOpen },
                { value: 'pdf', label: 'PDF', icon: FileText }
              ].map(({ value, label, icon: Icon }) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => toggleCategory(value)}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 ${
                    searchForm.categories.includes(value)
                      ? 'bg-primary text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Time Filter */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Time Filter (optional)
              </label>
              <select
                value={searchForm.tbs}
                onChange={(e) => setSearchForm(prev => ({ ...prev, tbs: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              >
                <option value="">All time</option>
                <option value="qdr:h">Past hour</option>
                <option value="qdr:d">Past 24 hours</option>
                <option value="qdr:w">Past week</option>
                <option value="qdr:m">Past month</option>
                <option value="qdr:y">Past year</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Timeout (ms, optional)
              </label>
              <input
                type="number"
                value={searchForm.timeout}
                onChange={(e) => setSearchForm(prev => ({ ...prev, timeout: e.target.value }))}
                placeholder="e.g., 30000"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
          </div>

          {/* Scraping Option */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="enableScraping"
              checked={searchForm.enableScraping}
              onChange={(e) => setSearchForm(prev => ({ ...prev, enableScraping: e.target.checked }))}
              className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
            />
            <label htmlFor="enableScraping" className="text-sm font-medium text-gray-700">
              Enable content scraping for search results (retrieve full content from URLs)
            </label>
          </div>

          <button
            type="button"
            onClick={handleSearch}
            disabled={loading}
            className="w-full bg-primary text-white py-3 px-6 rounded-lg font-medium hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                Searching...
              </>
            ) : (
              <>
                <Search className="w-5 h-5" />
                Search
              </>
            )}
          </button>
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <div className="font-medium text-red-800 mb-1">Error</div>
              <div className="text-sm text-red-700">{error}</div>
              {(error.includes('credentials') || error.includes('not configured') || error.includes('Firecrawl')) ? (
                <div className="mt-2 text-xs text-red-600">
                  💡 Please configure Firecrawl API key in the API Config section.
                </div>
              ) : null}
            </div>
          </div>
        )}
        
        {pricingError && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <div className="font-medium text-red-800 mb-1">Pricing Extraction Error</div>
              <div className="text-sm text-red-700">{pricingError}</div>
            </div>
          </div>
        )}
      </div>

      {/* Results */}
      {result && (
        <div className="bg-white rounded-lg shadow p-6 space-y-6">
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-primary" />
            Search Results
          </h2>

          {/* Web Results */}
          {result.web && result.web.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Globe className="w-5 h-5 text-primary" />
                Web Results ({result.web.length})
              </h3>
              <div className="space-y-4">
                {result.web.map((item, index) => {
                  const pricingResult = pricingResults.get(item.url);
                  const isExtractingPricing = loadingPricing === item.url;
                  
                  return (
                    <div key={index} className="border border-gray-200 rounded-lg p-4 hover:border-primary transition-colors">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-medium text-gray-500 bg-gray-100 px-2 py-1 rounded">
                              #{item.position || index + 1}
                            </span>
                            {item.category && (
                              <span className="text-xs font-medium text-primary bg-blue-100 px-2 py-1 rounded">
                                {item.category}
                              </span>
                            )}
                          </div>
                          <a
                            href={item.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-lg font-semibold text-primary hover:underline flex items-center gap-2"
                          >
                            {item.title}
                            <FileText className="w-4 h-4" />
                          </a>
                          <p className="text-sm text-gray-600 mt-1 line-clamp-2">{item.description}</p>
                          <a
                            href={item.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-gray-500 hover:text-primary mt-2 inline-block break-all"
                          >
                            {item.url}
                          </a>
                          
                          {/* Extract Pricing Button */}
                          <div className="mt-3">
                            <button
                              type="button"
                              onClick={() => handleExtractPricing(item.url, item.title)}
                              disabled={isExtractingPricing || !!pricingResult}
                              className="px-3 py-1.5 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                            >
                              {isExtractingPricing ? (
                                <>
                                  <Loader className="w-4 h-4 animate-spin" />
                                  Extracting...
                                </>
                              ) : pricingResult ? (
                                <>
                                  <CheckCircle className="w-4 h-4" />
                                  Pricing Extracted
                                </>
                              ) : (
                                <>
                                  <PoundSterling className="w-4 h-4" />
                                  Extract Pricing
                                </>
                              )}
                            </button>
                          </div>
                          
                          {/* Pricing Results */}
                          {pricingResult && (() => {
                            // Validation: Reasonable price ranges for UK care homes (weekly in GBP)
                            const MIN_PRICE = 300;
                            const MAX_PRICE = 4000;
                            
                            const isValidPrice = (value: number | null | undefined): boolean => {
                              if (value === null || value === undefined) return false;
                              return value >= MIN_PRICE && value <= MAX_PRICE;
                            };
                            
                            const validatePriceRange = (
                              from: number | null | undefined,
                              to: number | null | undefined
                            ): { from: number | null; to: number | null; isValid: boolean } => {
                              const validFrom = from !== null && from !== undefined && isValidPrice(from) ? from : null;
                              const validTo = to !== null && to !== undefined && isValidPrice(to) ? to : null;
                              
                              // Ensure from <= to
                              if (validFrom !== null && validTo !== null && validFrom > validTo) {
                                return { from: validTo, to: validFrom, isValid: true };
                              }
                              
                              return { from: validFrom, to: validTo, isValid: validFrom !== null || validTo !== null };
                            };
                            
                            const residential = validatePriceRange(
                              pricingResult.pricing.fee_residential_from,
                              pricingResult.pricing.fee_residential_to
                            );
                            const nursing = validatePriceRange(
                              pricingResult.pricing.fee_nursing_from,
                              pricingResult.pricing.fee_nursing_to
                            );
                            const dementiaResidential = validatePriceRange(
                              pricingResult.pricing.fee_dementia_residential_from,
                              pricingResult.pricing.fee_dementia_residential_to
                            );
                            const dementiaNursing = validatePriceRange(
                              pricingResult.pricing.fee_dementia_nursing_from,
                              pricingResult.pricing.fee_dementia_nursing_to
                            );
                            const respite = validatePriceRange(
                              pricingResult.pricing.fee_respite_from,
                              pricingResult.pricing.fee_respite_to
                            );
                            
                            const hasValidPrices = residential.isValid || nursing.isValid || 
                                                   dementiaResidential.isValid || dementiaNursing.isValid || 
                                                   respite.isValid;
                            
                            return (
                            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                              <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                                <PoundSterling className="w-4 h-4 text-green-600" />
                                Pricing Information
                              </h4>
                              
                              {!hasValidPrices && (
                                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                                  <div className="text-sm text-red-700 flex items-center gap-2">
                                    <AlertCircle className="w-4 h-4" />
                                    <span>No valid pricing data found. Prices may be outside reasonable range (£{MIN_PRICE}-£{MAX_PRICE}/week).</span>
                                  </div>
                                </div>
                              )}
                              
                              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mb-4">
                                {/* Residential Care */}
                                {residential.isValid && (
                                  <div className="bg-white rounded-lg p-3 border border-green-200">
                                    <div className="text-xs font-medium text-gray-600 mb-1">Residential Care</div>
                                    <div className="font-bold text-green-700 text-lg">
                                      {residential.from !== null ? (
                                        <>
                                          £{residential.from.toLocaleString()}
                                          {residential.to !== null && residential.to !== residential.from && (
                                            <> - £{residential.to.toLocaleString()}</>
                                          )}
                                        </>
                                      ) : residential.to !== null ? (
                                        <>£{residential.to.toLocaleString()}</>
                                      ) : null}
                                    </div>
                                    <div className="text-xs text-gray-500 mt-1">per week</div>
                                  </div>
                                )}
                                
                                {/* Nursing Care */}
                                {nursing.isValid && (
                                  <div className="bg-white rounded-lg p-3 border border-green-200">
                                    <div className="text-xs font-medium text-gray-600 mb-1">Nursing Care</div>
                                    <div className="font-bold text-green-700 text-lg">
                                      {nursing.from !== null ? (
                                        <>
                                          £{nursing.from.toLocaleString()}
                                          {nursing.to !== null && nursing.to !== nursing.from && (
                                            <> - £{nursing.to.toLocaleString()}</>
                                          )}
                                        </>
                                      ) : nursing.to !== null ? (
                                        <>£{nursing.to.toLocaleString()}</>
                                      ) : null}
                                    </div>
                                    <div className="text-xs text-gray-500 mt-1">per week</div>
                                  </div>
                                )}
                                
                                {/* Dementia Residential Care */}
                                {dementiaResidential.isValid && (
                                  <div className="bg-white rounded-lg p-3 border border-green-200">
                                    <div className="text-xs font-medium text-gray-600 mb-1">Dementia Residential</div>
                                    <div className="font-bold text-green-700 text-lg">
                                      {dementiaResidential.from !== null ? (
                                        <>
                                          £{dementiaResidential.from.toLocaleString()}
                                          {dementiaResidential.to !== null && dementiaResidential.to !== dementiaResidential.from && (
                                            <> - £{dementiaResidential.to.toLocaleString()}</>
                                          )}
                                        </>
                                      ) : dementiaResidential.to !== null ? (
                                        <>£{dementiaResidential.to.toLocaleString()}</>
                                      ) : null}
                                    </div>
                                    <div className="text-xs text-gray-500 mt-1">per week</div>
                                  </div>
                                )}
                                
                                {/* Dementia Nursing Care */}
                                {dementiaNursing.isValid && (
                                  <div className="bg-white rounded-lg p-3 border border-green-200">
                                    <div className="text-xs font-medium text-gray-600 mb-1">Dementia Nursing</div>
                                    <div className="font-bold text-green-700 text-lg">
                                      {dementiaNursing.from !== null ? (
                                        <>
                                          £{dementiaNursing.from.toLocaleString()}
                                          {dementiaNursing.to !== null && dementiaNursing.to !== dementiaNursing.from && (
                                            <> - £{dementiaNursing.to.toLocaleString()}</>
                                          )}
                                        </>
                                      ) : dementiaNursing.to !== null ? (
                                        <>£{dementiaNursing.to.toLocaleString()}</>
                                      ) : null}
                                    </div>
                                    <div className="text-xs text-gray-500 mt-1">per week</div>
                                  </div>
                                )}
                                
                                {/* Respite Care */}
                                {respite.isValid && (
                                  <div className="bg-white rounded-lg p-3 border border-green-200">
                                    <div className="text-xs font-medium text-gray-600 mb-1">Respite Care</div>
                                    <div className="font-bold text-green-700 text-lg">
                                      {respite.from !== null ? (
                                        <>
                                          £{respite.from.toLocaleString()}
                                          {respite.to !== null && respite.to !== respite.from && (
                                            <> - £{respite.to.toLocaleString()}</>
                                          )}
                                        </>
                                      ) : respite.to !== null ? (
                                        <>£{respite.to.toLocaleString()}</>
                                      ) : null}
                                    </div>
                                    <div className="text-xs text-gray-500 mt-1">per week</div>
                                  </div>
                                )}
                              </div>
                              
                              {pricingResult.pricing.pricing_breakdown && (
                                <div className="mb-3 text-sm">
                                  <div className="font-medium text-gray-700 mb-1">What's Included:</div>
                                  <div className="flex flex-wrap gap-2">
                                    {pricingResult.pricing.pricing_breakdown.meals_included !== undefined && (
                                      <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
                                        Meals {pricingResult.pricing.pricing_breakdown.meals_included ? '✓' : '✗'}
                                      </span>
                                    )}
                                    {pricingResult.pricing.pricing_breakdown.activities_included !== undefined && (
                                      <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
                                        Activities {pricingResult.pricing.pricing_breakdown.activities_included ? '✓' : '✗'}
                                      </span>
                                    )}
                                  </div>
                                </div>
                              )}
                              
                              {/* Pricing Notes */}
                              {pricingResult.pricing.pricing_notes && (
                                <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                                  <div className="text-xs font-medium text-gray-700 mb-1 flex items-center gap-1">
                                    <Info className="w-3 h-3" />
                                    Pricing Notes
                                  </div>
                                  <div className="text-sm text-gray-700">
                                    {pricingResult.pricing.pricing_notes}
                                  </div>
                                </div>
                              )}
                              
                              {/* Confidence Score */}
                              {pricingResult.pricing.pricing_confidence !== undefined && (
                                <div className="mt-3 flex items-center justify-between">
                                  <div className="text-xs font-medium text-gray-600">Confidence Score:</div>
                                  <div className="flex items-center gap-2">
                                    <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                                      <div 
                                        className={`h-full ${
                                          pricingResult.pricing.pricing_confidence >= 90 ? 'bg-green-600' :
                                          pricingResult.pricing.pricing_confidence >= 70 ? 'bg-yellow-600' :
                                          'bg-red-600'
                                        }`}
                                        style={{ width: `${pricingResult.pricing.pricing_confidence}%` }}
                                      />
                                    </div>
                                    <span className={`text-xs font-bold ${
                                      pricingResult.pricing.pricing_confidence >= 90 ? 'text-green-700' :
                                      pricingResult.pricing.pricing_confidence >= 70 ? 'text-yellow-700' :
                                      'text-red-700'
                                    }`}>
                                      {pricingResult.pricing.pricing_confidence}/100
                                    </span>
                                  </div>
                                </div>
                              )}
                              
                              {/* Metadata */}
                              <div className="mt-3 pt-3 border-t border-gray-200 text-xs text-gray-500">
                                <div>Extraction Method: {pricingResult.extraction_method}</div>
                                <div>Scraped At: {new Date(pricingResult.scraped_at).toLocaleString()}</div>
                                {pricingResult.pricing.currency && <div>Currency: {pricingResult.pricing.currency}</div>}
                                {pricingResult.pricing.billing_period && <div>Billing Period: {pricingResult.pricing.billing_period}</div>}
                              </div>
                            </div>
                            );
                          })()}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* News Results */}
          {result.news && result.news.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Newspaper className="w-5 h-5 text-primary" />
                News Results ({result.news.length})
              </h3>
              <div className="space-y-4">
                {result.news.map((item, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 hover:border-primary transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-medium text-gray-500 bg-gray-100 px-2 py-1 rounded">
                            #{item.position || index + 1}
                          </span>
                          {item.date && (
                            <span className="text-xs text-gray-500 flex items-center gap-1">
                              <Calendar className="w-3 h-3" />
                              {item.date}
                            </span>
                          )}
                        </div>
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-lg font-semibold text-primary hover:underline flex items-center gap-2"
                        >
                          {item.title}
                          <Newspaper className="w-4 h-4" />
                        </a>
                        {item.snippet && (
                          <p className="text-sm text-gray-600 mt-1 line-clamp-2">{item.snippet}</p>
                        )}
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-gray-500 hover:text-primary mt-2 inline-block break-all"
                        >
                          {item.url}
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Image Results */}
          {result.images && result.images.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Image className="w-5 h-5 text-primary" />
                Image Results ({result.images.length})
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {result.images.map((item, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg overflow-hidden hover:border-primary transition-colors">
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block"
                    >
                      <img
                        src={item.imageUrl}
                        alt={item.title}
                        className="w-full h-48 object-cover"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23ddd" width="200" height="200"/%3E%3Ctext fill="%23999" font-family="sans-serif" font-size="14" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3EImage%3C/text%3E%3C/svg%3E';
                        }}
                      />
                      <div className="p-2">
                        <p className="text-xs font-medium text-gray-900 line-clamp-2">{item.title}</p>
                        {item.imageWidth && item.imageHeight && (
                          <p className="text-xs text-gray-500 mt-1">
                            {item.imageWidth} × {item.imageHeight}
                          </p>
                        )}
                      </div>
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* No Results */}
          {(!result.web || result.web.length === 0) &&
           (!result.news || result.news.length === 0) &&
           (!result.images || result.images.length === 0) && (
            <div className="text-center py-8 text-gray-500">
              <AlertCircle className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <p>No results found. Try adjusting your search query or filters.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}


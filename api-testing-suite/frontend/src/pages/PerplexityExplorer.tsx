import { useState } from 'react';
import { Search, FileText, TrendingUp, AlertCircle, CheckCircle, X, ExternalLink, Sparkles, Shield, BookOpen } from 'lucide-react';
import axios from 'axios';

interface ResearchResult {
  home_name: string;
  location?: string;
  content: string;
  citations: string[];
  cost: number;
}

interface AdvancedMonitoringResult {
  home_name: string;
  location?: string;
  content: string;
  citations: string[];
  red_flags: Array<{
    home: string;
    headline: string;
    source: string;
    severity: string;
    keywords_found: string[];
    date?: string;
    flagged_content?: string[];
  }>;
  alert_level: string;
  red_flags_count: number;
  high_severity_count: number;
  date_range: string;
  search_query: string;
  cost: number;
}

type ResearchMode = 'reputation' | 'comprehensive' | 'custom' | 'advanced' | 'academic';

export default function PerplexityExplorer() {
  const [researchMode, setResearchMode] = useState<ResearchMode>('reputation');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ResearchResult | AdvancedMonitoringResult | null>(null);
  const [cost, setCost] = useState<number>(0);

  // Reputation search form
  const [reputationForm, setReputationForm] = useState({
    home_name: '',
    location: '',
  });

  // Comprehensive research form
  const [comprehensiveForm, setComprehensiveForm] = useState({
    home_name: '',
    address: '',
    city: '',
    postcode: '',
  });

  // Custom search form
  const [customForm, setCustomForm] = useState({
    query: '',
    model: 'sonar-pro',
    max_tokens: 1000,
    search_recency_filter: 'month',
  });

  // Advanced monitoring form
  const [advancedForm, setAdvancedForm] = useState({
    home_name: '',
    location: '',
    date_range: 'last_7_days',
  });

  // Academic research form
  const [academicForm, setAcademicForm] = useState({
    topics: ['dementia care', 'staff retention'],
  });

  const handleReputationSearch = async () => {
    if (!reputationForm.home_name.trim()) {
      alert('Please enter a care home name');
      return;
    }

    setLoading(true);
    setResult(null);
    try {
      // Build request payload, excluding undefined/empty values
      const payload: any = {
        home_name: reputationForm.home_name,
      };
      if (reputationForm.location && reputationForm.location.trim()) {
        payload.location = reputationForm.location.trim();
      }
      
      const response = await axios.post('/api/perplexity/reputation', payload);

      if (response.data.status === 'success') {
        setResult({
          home_name: response.data.home_name,
          location: response.data.location,
          content: response.data.content,
          citations: response.data.citations || [],
          cost: response.data.cost || 0,
        });
        setCost(response.data.cost || 0);
      }
    } catch (error: any) {
      console.error('Perplexity reputation error:', error);
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Unknown error occurred';
      alert(`Error: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const handleComprehensiveResearch = async () => {
    if (!comprehensiveForm.home_name.trim()) {
      alert('Please enter a care home name');
      return;
    }

    setLoading(true);
    setResult(null);
    try {
      // Build request payload, excluding undefined/empty values
      const payload: any = {
        home_name: comprehensiveForm.home_name,
      };
      if (comprehensiveForm.address && comprehensiveForm.address.trim()) {
        payload.address = comprehensiveForm.address.trim();
      }
      if (comprehensiveForm.city && comprehensiveForm.city.trim()) {
        payload.city = comprehensiveForm.city.trim();
      }
      if (comprehensiveForm.postcode && comprehensiveForm.postcode.trim()) {
        payload.postcode = comprehensiveForm.postcode.trim();
      }
      
      const response = await axios.post('/api/perplexity/comprehensive-research', payload);

      if (response.data.status === 'success') {
        setResult({
          home_name: response.data.home_name,
          location: response.data.location,
          content: response.data.content,
          citations: response.data.citations || [],
          cost: response.data.cost || 0,
        });
        setCost(response.data.cost || 0);
      }
    } catch (error: any) {
      console.error('Perplexity comprehensive research error:', error);
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Unknown error occurred';
      alert(`Error: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCustomSearch = async () => {
    if (!customForm.query.trim()) {
      alert('Please enter a search query');
      return;
    }

    setLoading(true);
    setResult(null);
    try {
      const response = await axios.post('/api/perplexity/search', {
        query: customForm.query,
        model: customForm.model,
        max_tokens: customForm.max_tokens,
        search_recency_filter: customForm.search_recency_filter,
      });

      if (response.data.status === 'success') {
        setResult({
          home_name: '',
          content: response.data.content,
          citations: response.data.citations || [],
          cost: response.data.cost || 0,
        });
        setCost(response.data.cost || 0);
      }
    } catch (error: any) {
      console.error('Perplexity custom search error:', error);
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Unknown error occurred';
      alert(`Error: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAdvancedMonitoring = async () => {
    if (!advancedForm.home_name.trim()) {
      alert('Please enter a care home name');
      return;
    }

    setLoading(true);
    setResult(null);
    try {
      const payload: any = {
        home_name: advancedForm.home_name,
        date_range: advancedForm.date_range,
      };
      if (advancedForm.location && advancedForm.location.trim()) {
        payload.location = advancedForm.location.trim();
      }
      
      const response = await axios.post('/api/perplexity/advanced-monitoring', payload);

      if (response.data.status === 'success') {
        setResult({
          home_name: response.data.home_name,
          location: response.data.location,
          content: response.data.content,
          citations: response.data.citations || [],
          red_flags: response.data.red_flags || [],
          alert_level: response.data.alert_level,
          red_flags_count: response.data.red_flags_count || 0,
          high_severity_count: response.data.high_severity_count || 0,
          date_range: response.data.date_range,
          search_query: response.data.search_query,
          cost: response.data.cost || 0,
        } as AdvancedMonitoringResult);
        setCost(response.data.cost || 0);
      }
    } catch (error: any) {
      console.error('Perplexity advanced monitoring error:', error);
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Unknown error occurred';
      alert(`Error: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAcademicResearch = async () => {
    if (!academicForm.topics || academicForm.topics.length === 0) {
      alert('Please enter at least one research topic');
      return;
    }

    setLoading(true);
    setResult(null);
    try {
      const response = await axios.post('/api/perplexity/academic-research', {
        topics: academicForm.topics,
      });

      if (response.data.status === 'success') {
        // Format academic research results
        const researchResults = response.data.research_results;
        const formattedContent = Object.entries(researchResults)
          .map(([topic, data]: [string, any]) => {
            return `## ${topic}\n\n${data.summary || 'No summary available'}\n\n**Academic Papers Found:** ${data.total_papers || 0}`;
          })
          .join('\n\n---\n\n');

        setResult({
          home_name: 'Academic Research',
          content: formattedContent,
          citations: [],
          cost: response.data.cost || 0,
        });
        setCost(response.data.cost || 0);
      }
    } catch (error: any) {
      console.error('Perplexity academic research error:', error);
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Unknown error occurred';
      alert(`Error: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    if (researchMode === 'reputation') {
      handleReputationSearch();
    } else if (researchMode === 'comprehensive') {
      handleComprehensiveResearch();
    } else if (researchMode === 'advanced') {
      handleAdvancedMonitoring();
    } else if (researchMode === 'academic') {
      handleAcademicResearch();
    } else {
      handleCustomSearch();
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Perplexity Research Explorer</h1>
        <p className="mt-2 text-gray-600">
          Get comprehensive information about care homes - news, reputation, awards, and more
        </p>
      </div>

      {/* Mode Selection */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex gap-4">
          <button
            onClick={() => {
              setResearchMode('reputation');
              setResult(null);
            }}
            className={`flex items-center px-4 py-2 rounded-md font-medium ${
              researchMode === 'reputation'
                ? 'bg-primary text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <TrendingUp className="w-4 h-4 mr-2" />
            Reputation Monitor
          </button>
          <button
            onClick={() => {
              setResearchMode('comprehensive');
              setResult(null);
            }}
            className={`flex items-center px-4 py-2 rounded-md font-medium ${
              researchMode === 'comprehensive'
                ? 'bg-primary text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <FileText className="w-4 h-4 mr-2" />
            Comprehensive Research
          </button>
          <button
            onClick={() => {
              setResearchMode('custom');
              setResult(null);
            }}
            className={`flex items-center px-4 py-2 rounded-md font-medium ${
              researchMode === 'custom'
                ? 'bg-primary text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Sparkles className="w-4 h-4 mr-2" />
            Custom Search
          </button>
          <button
            onClick={() => {
              setResearchMode('advanced');
              setResult(null);
            }}
            className={`flex items-center px-4 py-2 rounded-md font-medium ${
              researchMode === 'advanced'
                ? 'bg-primary text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Shield className="w-4 h-4 mr-2" />
            Advanced Monitoring
          </button>
          <button
            onClick={() => {
              setResearchMode('academic');
              setResult(null);
            }}
            className={`flex items-center px-4 py-2 rounded-md font-medium ${
              researchMode === 'academic'
                ? 'bg-primary text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <BookOpen className="w-4 h-4 mr-2" />
            Academic Research
          </button>
        </div>
      </div>

      {/* Search Forms */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Research Parameters</h2>

        {researchMode === 'reputation' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Care Home Name *
              </label>
              <input
                type="text"
                value={reputationForm.home_name}
                onChange={(e) =>
                  setReputationForm({ ...reputationForm, home_name: e.target.value })
                }
                placeholder="e.g., Manor House Care Home"
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              />
              <div className="mt-2">
                <p className="text-xs text-gray-500 mb-2">Quick test examples (click to use - real UK care homes from CQC registry):</p>
                <div className="flex flex-wrap gap-2">
                  {[
                    { name: 'Westgate House Care Home', location: 'London' },
                    { name: 'The Orchards Care Home', location: 'Birmingham' },
                    { name: 'Trowbridge Oaks Care Home', location: 'Trowbridge' },
                    { name: 'Lynde House Care Home', location: 'London' }
                  ].map((example) => (
                    <button
                      key={example.name}
                      type="button"
                      onClick={() => {
                        setReputationForm({
                          home_name: example.name,
                          location: example.location
                        });
                      }}
                      className="px-3 py-1 text-xs bg-blue-50 text-blue-700 border border-blue-200 rounded-md hover:bg-blue-100 transition-colors"
                      title={`${example.name}, ${example.location}`}
                    >
                      {example.name}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
              <input
                type="text"
                value={reputationForm.location}
                onChange={(e) =>
                  setReputationForm({ ...reputationForm, location: e.target.value })
                }
                placeholder="e.g., Brighton, UK"
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              />
            </div>
            <p className="text-sm text-gray-500">
              Searches for recent news, complaints, and concerns about the care home in the last 3
              months
            </p>
          </div>
        )}

        {researchMode === 'comprehensive' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Care Home Name *
              </label>
              <input
                type="text"
                value={comprehensiveForm.home_name}
                onChange={(e) =>
                  setComprehensiveForm({ ...comprehensiveForm, home_name: e.target.value })
                }
                placeholder="e.g., Manor House Care Home"
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              />
              <div className="mt-2">
                <p className="text-xs text-gray-500 mb-2">Quick test examples (click to use - real UK care homes from CQC registry):</p>
                <div className="flex flex-wrap gap-2">
                  {[
                    { name: 'Westgate House Care Home', address: '178 Romford Road, Forest Gate', city: 'London', postcode: 'E7 9HY' },
                    { name: 'The Orchards Care Home', address: '164 Shard End Crescent, Shard End', city: 'Birmingham', postcode: 'B34 7BP' },
                    { name: 'Trowbridge Oaks Care Home', address: 'West Ashton Road, West Ashton', city: 'Trowbridge', postcode: 'BA14 6DW' },
                    { name: 'Lynde House Care Home', address: 'The Embankment', city: 'Twickenham, London', postcode: 'TW1 3DY' }
                  ].map((example) => (
                    <button
                      key={example.name}
                      type="button"
                      onClick={() => {
                        setComprehensiveForm({
                          home_name: example.name,
                          address: example.address,
                          city: example.city,
                          postcode: example.postcode
                        });
                      }}
                      className="px-3 py-1 text-xs bg-blue-50 text-blue-700 border border-blue-200 rounded-md hover:bg-blue-100 transition-colors"
                      title={`${example.name}, ${example.address}, ${example.city}, ${example.postcode}`}
                    >
                      {example.name}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                <input
                  type="text"
                  value={comprehensiveForm.address}
                  onChange={(e) =>
                    setComprehensiveForm({ ...comprehensiveForm, address: e.target.value })
                  }
                  placeholder="Street address"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                <input
                  type="text"
                  value={comprehensiveForm.city}
                  onChange={(e) =>
                    setComprehensiveForm({ ...comprehensiveForm, city: e.target.value })
                  }
                  placeholder="e.g., Brighton"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Postcode</label>
                <input
                  type="text"
                  value={comprehensiveForm.postcode}
                  onChange={(e) =>
                    setComprehensiveForm({ ...comprehensiveForm, postcode: e.target.value })
                  }
                  placeholder="e.g., BN1 1AB"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
            </div>
            <p className="text-sm text-gray-500">
              Comprehensive research including news, awards, complaints, reputation, personnel
              changes, and more
            </p>
          </div>
        )}

        {researchMode === 'custom' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Search Query *
              </label>
              <textarea
                value={customForm.query}
                onChange={(e) => setCustomForm({ ...customForm, query: e.target.value })}
                placeholder="Enter your research question..."
                rows={4}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Model</label>
                <select
                  value={customForm.model}
                  onChange={(e) => setCustomForm({ ...customForm, model: e.target.value })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="sonar-pro">Sonar Pro (Recommended)</option>
                  <option value="sonar">Sonar</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Tokens
                </label>
                <input
                  type="number"
                  value={customForm.max_tokens}
                  onChange={(e) =>
                    setCustomForm({
                      ...customForm,
                      max_tokens: parseInt(e.target.value) || 1000,
                    })
                  }
                  min="100"
                  max="4000"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Recency Filter
                </label>
                <select
                  value={customForm.search_recency_filter}
                  onChange={(e) =>
                    setCustomForm({ ...customForm, search_recency_filter: e.target.value })
                  }
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="day">Last Day</option>
                  <option value="week">Last Week</option>
                  <option value="month">Last Month</option>
                  <option value="year">Last Year</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {researchMode === 'advanced' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Care Home Name *
              </label>
              <input
                type="text"
                value={advancedForm.home_name}
                onChange={(e) =>
                  setAdvancedForm({ ...advancedForm, home_name: e.target.value })
                }
                placeholder="e.g., Manor House Care Home"
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
              <input
                type="text"
                value={advancedForm.location}
                onChange={(e) =>
                  setAdvancedForm({ ...advancedForm, location: e.target.value })
                }
                placeholder="e.g., Brighton, UK"
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
              <select
                value={advancedForm.date_range}
                onChange={(e) =>
                  setAdvancedForm({ ...advancedForm, date_range: e.target.value })
                }
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              >
                <option value="last_7_days">Last 7 Days</option>
                <option value="last_30_days">Last 30 Days</option>
                <option value="month">Last Month</option>
                <option value="year">Last Year</option>
              </select>
            </div>
            <p className="text-sm text-gray-500">
              Advanced monitoring with RED FLAGS detection, domain filtering, and real-time alerts
            </p>
          </div>
        )}

        {researchMode === 'academic' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Research Topics * (one per line)
              </label>
              <textarea
                value={academicForm.topics.join('\n')}
                onChange={(e) =>
                  setAcademicForm({
                    ...academicForm,
                    topics: e.target.value.split('\n').filter((t) => t.trim()),
                  })
                }
                placeholder="dementia care&#10;staff retention&#10;preventable hospital admissions"
                rows={5}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              />
              <p className="text-xs text-gray-500 mt-1">
                Enter one research topic per line. Examples: dementia care, staff retention, infection control
              </p>
            </div>
            <p className="text-sm text-gray-500">
              Find latest academic research papers from trusted sources (BMJ, Lancet, PubMed, etc.)
            </p>
          </div>
        )}

        <div className="mt-4">
          <button
            onClick={handleSearch}
            disabled={loading}
            className="inline-flex items-center px-6 py-3 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-purple-700 disabled:opacity-50"
          >
            <Search className="w-4 h-4 mr-2" />
            {loading ? 'Researching...' : 'Start Research'}
          </button>
        </div>
      </div>

      {/* Cost Display */}
      {cost > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <strong>Estimated API Cost:</strong> £{cost.toFixed(4)}
          </p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Research Results</h2>
              {result.home_name && (
                <span className="text-sm text-gray-600">{result.home_name}</span>
              )}
            </div>
          </div>
          <div className="p-6">
            {/* Advanced Monitoring Results with RED FLAGS */}
            {'red_flags' in result && (
              <div className="mb-6">
                <div className={`inline-flex items-center px-4 py-2 rounded-md font-medium mb-4 ${
                  result.alert_level === 'HIGH' 
                    ? 'bg-red-100 text-red-800' 
                    : result.alert_level === 'MEDIUM'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-green-100 text-green-800'
                }`}>
                  <AlertCircle className="w-5 h-5 mr-2" />
                  Alert Level: {result.alert_level} ({result.red_flags_count} red flags, {result.high_severity_count} high severity)
                </div>
                
                {result.red_flags && result.red_flags.length > 0 && (
                  <div className="space-y-3 mb-6">
                    <h3 className="text-md font-semibold text-gray-900">🚨 RED FLAGS DETECTED</h3>
                    {result.red_flags.map((flag: any, index: number) => (
                      <div
                        key={index}
                        className={`border-l-4 p-4 rounded ${
                          flag.severity === 'HIGH'
                            ? 'border-red-500 bg-red-50'
                            : 'border-yellow-500 bg-yellow-50'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="font-semibold text-gray-900">{flag.headline}</h4>
                            <p className="text-sm text-gray-600 mt-1">Source: {flag.source}</p>
                            {flag.keywords_found && flag.keywords_found.length > 0 && (
                              <div className="mt-2">
                                <span className="text-xs font-medium text-gray-700">Keywords: </span>
                                {flag.keywords_found.map((kw: string, i: number) => (
                                  <span
                                    key={i}
                                    className="inline-block px-2 py-1 mr-1 mt-1 text-xs bg-gray-200 text-gray-700 rounded"
                                  >
                                    {kw}
                                  </span>
                                ))}
                              </div>
                            )}
                            {flag.flagged_content && (
                              <div className="mt-2 text-sm text-gray-700">
                                {flag.flagged_content.map((content: string, i: number) => (
                                  <p key={i} className="italic">"{content}"</p>
                                ))}
                              </div>
                            )}
                          </div>
                          <span
                            className={`px-2 py-1 text-xs font-semibold rounded ${
                              flag.severity === 'HIGH'
                                ? 'bg-red-200 text-red-800'
                                : 'bg-yellow-200 text-yellow-800'
                            }`}
                          >
                            {flag.severity}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
            
            {/* Content */}
            <div className="prose max-w-none mb-6">
              <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
                {result.content}
              </div>
            </div>

            {/* Citations */}
            {result.citations && result.citations.length > 0 && (
              <div className="border-t pt-6">
                <h3 className="font-semibold mb-3 flex items-center">
                  <ExternalLink className="w-5 h-5 mr-1" />
                  Sources & Citations ({result.citations.length})
                </h3>
                <div className="space-y-2">
                  {result.citations.map((citation, idx) => (
                    <div key={idx} className="flex items-start">
                      <span className="text-sm text-gray-500 mr-2">{idx + 1}.</span>
                      <a
                        href={citation}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:underline break-all"
                      >
                        {citation}
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* No Citations Warning */}
            {(!result.citations || result.citations.length === 0) && (
              <div className="border-t pt-6">
                <div className="flex items-center text-yellow-700 bg-yellow-50 p-3 rounded">
                  <AlertCircle className="w-5 h-5 mr-2" />
                  <span className="text-sm">No citations available for this research</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}


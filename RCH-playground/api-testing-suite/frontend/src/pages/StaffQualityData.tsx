import { useState } from 'react';
import { Users, Search, AlertCircle, CheckCircle, Info, Building2, Star, MessageSquare, Loader2 } from 'lucide-react';
import axios from 'axios';
import { 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar, 
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Cell
} from 'recharts';

interface CareHome {
  id: string;
  name: string;
  address?: string;
  postcode?: string;
  localAuthority?: string;
  locationId?: string;
}

interface CQCRating {
  wellLed: 'Outstanding' | 'Good' | 'Requires Improvement' | 'Inadequate' | null;
  effective: 'Outstanding' | 'Good' | 'Requires Improvement' | 'Inadequate' | null;
  lastInspectionDate?: string;
  staffSentiment?: {
    positive: number;
    neutral: number;
    negative: number;
    score: number;
  };
}

interface EmployeeReview {
  source: 'Indeed' | 'Indeed UK' | 'Google' | 'CareHome.co.uk';
  rating: number;
  sentiment: 'POSITIVE' | 'MIXED' | 'NEGATIVE' | 'NEUTRAL';
  text?: string;
  date?: string;
  author?: string;
  reviewerType?: string;  // e.g., "Son of Resident", "Daughter of Resident"
  llm_analyzed?: boolean;
  sentiment_confidence?: number;
}

interface StaffQualityScore {
  overallScore: number;
  category: 'EXCELLENT' | 'GOOD' | 'ADEQUATE' | 'CONCERNING' | 'POOR';
  confidence: 'high' | 'medium' | 'low' | 'High' | 'Medium' | 'Low';
  components: {
    cqcWellLed: { score: number | null; weight: number; rating: string | null; note?: string };
    cqcEffective: { score: number | null; weight: number; rating: string | null; note?: string };
    cqcStaffSentiment: { score: number | null; weight: number; note?: string };
    employeeSentiment: { score: number | null; weight: number; reviewCount: number; source?: string };
  };
  flags: Array<{ type: 'red' | 'yellow'; message: string }>;
  themes: {
    positive: string[];
    negative: string[];
  };
  dataQuality: {
    cqcDataAge: string;
    reviewCount: number;
    hasInsufficientData: boolean;
    dataCompleteness?: {
      hasCqcWellLed: boolean;
      hasCqcEffective: boolean;
      hasCqcStaffSentiment: boolean;
      hasEmployeeReviews: boolean;
      employeeReviewCount: number;
    };
  };
}

interface PerplexityResearch {
  summary: string;
  raw_content: string;
  citations: string[];
  has_negative_findings: boolean;
  source: string;
  cost: number;
}

interface KeyFindingsSummary {
  summary: string;
  review_count: number;
  overall_score: number;
  category: string;
  generated: boolean;
}

interface EnforcementSignals {
  has_enforcement_actions: boolean;
  count: number;
  actions?: Array<{
    type: string;
    date?: string;
    description?: string;
  }>;
  severity?: 'HIGH' | 'MEDIUM' | 'LOW';
}

interface CompanySignals {
  company_name: string;
  company_number: string;
  company_status: string;
  company_age_years: number;
  director_stability: {
    active_directors: number;
    resignations_last_year: number;
    resignations_last_2_years: number;
    average_tenure_years: number;
    stability_label: string;
    issues: string[];
  };
  financial_risk: {
    risk_level: string;
    risk_score: number;
    issues: string[];
  };
  staff_quality_impact: {
    level: 'POSITIVE' | 'NEUTRAL' | 'NEGATIVE' | 'CRITICAL';
    score_adjustment: number;
    flags: string[];
  };
}

interface CareHomeAnalysis {
  careHome: CareHome;
  cqcData: CQCRating;
  reviews: EmployeeReview[];
  staffQualityScore: StaffQualityScore;
  perplexityResearch?: PerplexityResearch;
  keyFindingsSummary?: KeyFindingsSummary;
  enforcementSignals?: EnforcementSignals;
  companySignals?: CompanySignals;
}

// Preset care homes with verified CQC location_id for full analysis (CQC + CareHome.co.uk + Google)
const PRESET_CARE_HOMES: CareHome[] = [
  {
    id: 'preset-1',
    name: 'Westgate House Care Home',
    address: '178 Romford Road, Forest Gate',
    postcode: 'E7 9HY',
    localAuthority: 'Newham',
    locationId: '1-125863016', // CQC location ID
  },
  {
    id: 'preset-2',
    name: 'The Orchards Care Home',
    address: '164 Shard End Crescent, Shard End',
    postcode: 'B34 7BP',
    localAuthority: 'Birmingham',
    locationId: '1-320755658', // CQC location ID - The Orchards, Birmingham
  },
  {
    id: 'preset-3',
    name: 'Trowbridge Oaks Care Home',
    address: 'West Ashton Road, West Ashton',
    postcode: 'BA14 6DW',
    localAuthority: 'Wiltshire',
    locationId: '1-130120824', // CQC location ID
  },
  {
    id: 'preset-4',
    name: 'Lynde House Care Home',
    address: 'The Embankment',
    postcode: 'TW1 3DY',
    localAuthority: 'Richmond upon Thames',
    locationId: '1-125856379', // CQC location ID
  },
];

// Generate analysis from API
const generateAnalysis = async (home: CareHome): Promise<CareHomeAnalysis> => {
  try {
    // Call real API endpoint
    const response = await axios.post('/api/staff-quality/analyze', {
      name: home.name,
      location_id: home.locationId,
      postcode: home.postcode,
      address: home.address,
    });
    
    const data = response.data;
    
    // Transform API response to match frontend interface
    return {
      careHome: {
        id: home.id,
        name: data.care_home.name || home.name,
        address: data.care_home.address || home.address,
        postcode: data.care_home.postcode || home.postcode,
        localAuthority: data.care_home.local_authority || home.localAuthority,
        locationId: data.care_home.id || home.locationId,
      },
      cqcData: {
        wellLed: data.cqc_data.well_led || null,
        effective: data.cqc_data.effective || null,
        lastInspectionDate: data.cqc_data.last_inspection_date || undefined,
        staffSentiment: data.cqc_data.staff_sentiment ? {
          positive: data.cqc_data.staff_sentiment.positive || 0,
          neutral: data.cqc_data.staff_sentiment.neutral || 0,
          negative: data.cqc_data.staff_sentiment.negative || 0,
          score: data.cqc_data.staff_sentiment.score || 50,
        } : undefined,
      },
      reviews: (data.reviews || []).map((r: any) => ({
        source: (
          r.source === 'CareHome.co.uk' ? 'CareHome.co.uk' :
          r.source === 'Indeed UK' ? 'Indeed UK' : 
          r.source === 'Indeed' ? 'Indeed' : 'Google'
        ) as 'Indeed' | 'Indeed UK' | 'Google' | 'CareHome.co.uk',
        rating: typeof r.rating === 'number' ? r.rating : parseFloat(r.rating) || 0,
        sentiment: (r.sentiment || 'NEUTRAL') as 'POSITIVE' | 'MIXED' | 'NEGATIVE' | 'NEUTRAL',
        text: r.text || '',
        date: r.date || undefined,
        author: r.author || undefined,
        reviewerType: r.reviewer_type || undefined,
        llm_analyzed: r.llm_analyzed || false,
        sentiment_confidence: r.sentiment_confidence || undefined,
      })),
      staffQualityScore: {
        overallScore: data.staff_quality_score.overall_score,
        category: data.staff_quality_score.category,
        confidence: data.staff_quality_score.confidence,
        components: {
          cqcWellLed: {
            score: data.staff_quality_score.components.cqc_well_led.score,
            weight: data.staff_quality_score.components.cqc_well_led.weight,
            rating: data.staff_quality_score.components.cqc_well_led.rating,
          },
          cqcEffective: {
            score: data.staff_quality_score.components.cqc_effective.score,
            weight: data.staff_quality_score.components.cqc_effective.weight,
            rating: data.staff_quality_score.components.cqc_effective.rating,
          },
          cqcStaffSentiment: {
            score: data.staff_quality_score.components.cqc_staff_sentiment.score,
            weight: data.staff_quality_score.components.cqc_staff_sentiment.weight,
          },
          employeeSentiment: {
            score: data.staff_quality_score.components.employee_sentiment.score,
            weight: data.staff_quality_score.components.employee_sentiment.weight,
            reviewCount: data.staff_quality_score.components.employee_sentiment.review_count,
          },
        },
        flags: data.staff_quality_score.flags || [],
        themes: {
          positive: data.staff_quality_score.themes.positive || [],
          negative: data.staff_quality_score.themes.negative || [],
        },
        dataQuality: {
          cqcDataAge: data.staff_quality_score.data_quality.cqc_data_age,
          reviewCount: data.staff_quality_score.data_quality.review_count,
          hasInsufficientData: data.staff_quality_score.data_quality.has_insufficient_data,
          dataCompleteness: data.staff_quality_score.data_quality.data_completeness ? {
            hasCqcWellLed: data.staff_quality_score.data_quality.data_completeness.has_cqc_well_led || false,
            hasCqcEffective: data.staff_quality_score.data_quality.data_completeness.has_cqc_effective || false,
            hasCqcStaffSentiment: data.staff_quality_score.data_quality.data_completeness.has_cqc_staff_sentiment || false,
            hasEmployeeReviews: data.staff_quality_score.data_quality.data_completeness.has_employee_reviews || false,
            employeeReviewCount: data.staff_quality_score.data_quality.data_completeness.employee_review_count || 0,
          } : undefined,
        },
      },
      perplexityResearch: data.perplexity_research ? {
        summary: data.perplexity_research.summary || '',
        raw_content: data.perplexity_research.raw_content || '',
        citations: data.perplexity_research.citations || [],
        has_negative_findings: data.perplexity_research.has_negative_findings || false,
        source: data.perplexity_research.source || 'Perplexity AI',
        cost: data.perplexity_research.cost || 0,
      } : undefined,
      keyFindingsSummary: data.key_findings_summary ? {
        summary: data.key_findings_summary.summary || '',
        review_count: data.key_findings_summary.review_count || 0,
        overall_score: data.key_findings_summary.overall_score || 0,
        category: data.key_findings_summary.category || '',
        generated: data.key_findings_summary.generated || false,
      } : undefined,
      enforcementSignals: data.enforcement_signals ? {
        has_enforcement_actions: data.enforcement_signals.has_enforcement_actions || false,
        count: data.enforcement_signals.count || 0,
        actions: data.enforcement_signals.actions || [],
        severity: data.enforcement_signals.severity || 'MEDIUM',
      } : undefined,
      companySignals: data.company_signals ? {
        company_name: data.company_signals.company_name || '',
        company_number: data.company_signals.company_number || '',
        company_status: data.company_signals.company_status || '',
        company_age_years: data.company_signals.company_age_years || 0,
        director_stability: data.company_signals.director_stability || {
          active_directors: 0,
          resignations_last_year: 0,
          resignations_last_2_years: 0,
          average_tenure_years: 0,
          stability_label: 'Unknown',
          issues: [],
        },
        financial_risk: data.company_signals.financial_risk || {
          risk_level: 'Unknown',
          risk_score: 0,
          issues: [],
        },
        staff_quality_impact: data.company_signals.staff_quality_impact || {
          level: 'NEUTRAL',
          score_adjustment: 0,
          flags: [],
        },
      } : undefined,
    };
  } catch (error: any) {
    console.error('Error fetching staff quality data:', error);
    
    // Throw error instead of using mock data
    const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch staff quality data';
    throw new Error(errorMessage);
  }
};

export default function StaffQualityData() {
  const [searchQuery, setSearchQuery] = useState('');
  const [analyses, setAnalyses] = useState<Record<string, CareHomeAnalysis>>({});
  const [loading, setLoading] = useState<Record<string, boolean>>({});
  const [expandedHome, setExpandedHome] = useState<string | null>(null);
  
  // Use preset care homes with verified location_id
  const exampleHomes = PRESET_CARE_HOMES;

  const handleAnalyzeHome = async (home: CareHome) => {
    if (loading[home.id] || analyses[home.id]) return;
    
    setLoading(prev => ({ ...prev, [home.id]: true }));
    try {
      // Show warning if searching by name without location_id
      if (!home.locationId && home.name && !home.postcode) {
        console.warn('Searching by name only may be slow. Consider providing a postcode or location_id for faster results.');
      }
      
      const analysis = await generateAnalysis(home);
      setAnalyses(prev => ({ ...prev, [home.id]: analysis }));
      setExpandedHome(home.id);
    } catch (error: any) {
      console.error('Error analyzing care home:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to analyze care home. Please try again.';
      
      // Show more helpful error messages
      let userMessage = errorMessage;
      if (errorMessage.includes('not found') || errorMessage.includes('No care homes')) {
        userMessage = `Care home not found: ${errorMessage}\n\nTip: Try using a more specific name or provide a postcode for better results.`;
      } else if (errorMessage.includes('timeout') || errorMessage.includes('timed out')) {
        userMessage = `Search timed out: ${errorMessage}\n\nTip: Try using a postcode or location_id instead of name for faster search.`;
      }
      
      alert(`Error: ${userMessage}`);
    } finally {
      setLoading(prev => ({ ...prev, [home.id]: false }));
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    const homeId = `search-${Date.now()}`;
    const newHome: CareHome = {
      id: homeId,
      name: searchQuery,
      address: '',
      postcode: '',
    };
    
    await handleAnalyzeHome(newHome);
    setSearchQuery('');
  };

  const handleRemoveAnalysis = (homeId: string) => {
    const newAnalyses = { ...analyses };
    delete newAnalyses[homeId];
    setAnalyses(newAnalyses);
    if (expandedHome === homeId) {
      setExpandedHome(null);
    }
  };

  const getCategoryColor = (category: StaffQualityScore['category']) => {
    switch (category) {
      case 'EXCELLENT': return 'text-green-600 bg-green-50 border-green-200';
      case 'GOOD': return 'text-green-600 bg-green-50 border-green-200';
      case 'ADEQUATE': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'CONCERNING': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'POOR': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getCategoryIcon = (category: StaffQualityScore['category']) => {
    switch (category) {
      case 'EXCELLENT':
      case 'GOOD':
        return <CheckCircle className="w-5 h-5" />;
      case 'ADEQUATE':
      case 'CONCERNING':
        return <AlertCircle className="w-5 h-5" />;
      case 'POOR':
        return <AlertCircle className="w-5 h-5" />;
      default:
        return <Info className="w-5 h-5" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Staff Quality Data</h1>
          <p className="mt-2 text-gray-600">
            Analyze staff quality scores based on CQC ratings, employee reviews, and sentiment analysis
          </p>
        </div>
      </div>

      {/* Search Section */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
        <div className="flex gap-3">
          <div className="flex-1">
            <label htmlFor="care-home-search" className="block text-sm font-medium text-gray-700 mb-2">
              Search Care Home
            </label>
            <div className="flex gap-2">
              <input
                id="care-home-search"
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Enter care home name or location ID..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#1E2A44] focus:border-[#1E2A44]"
              />
              <button
                onClick={handleSearch}
                disabled={!searchQuery.trim()}
                className="px-6 py-2 bg-[#1E2A44] text-white rounded-lg hover:bg-[#2a3a5a] disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <Search className="w-4 h-4" />
                Search
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Preset Care Homes Cards */}
      {Object.keys(analyses).length === 0 && (
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Select a care home to analyze:
          </h2>
          <p className="text-sm text-gray-600 mb-4">
            These are real care homes with verified CQC location IDs for fast analysis
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {exampleHomes.map((home) => (
              <div
                key={home.id}
                onClick={() => handleAnalyzeHome(home)}
                className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 cursor-pointer hover:shadow-xl hover:border-[#1E2A44] transition-all"
              >
                <div className="flex items-start gap-3 mb-3">
                  <Building2 className="w-6 h-6 text-gray-400 flex-shrink-0 mt-1" />
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-semibold text-gray-900 truncate">{home.name}</h3>
                    {home.address && (
                      <p className="text-sm text-gray-600 mt-1">{home.address}</p>
                    )}
                    {home.postcode && (
                      <p className="text-xs text-gray-500 mt-1">
                        {home.postcode} {home.localAuthority && `• ${home.localAuthority}`}
                      </p>
                    )}
                  </div>
                </div>
                {loading[home.id] ? (
                  <div className="flex items-center justify-center gap-2 text-[#1E2A44]">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-sm">Analyzing...</span>
                  </div>
                ) : (
                  <button className="w-full mt-4 px-4 py-2 bg-[#1E2A44] text-white rounded-lg hover:bg-[#2a3a5a] transition-colors">
                    Analyze Staff Quality
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Care Homes Analysis Results */}
      {Object.keys(analyses).length > 0 && (
        <div className="space-y-4">
          {Object.values(analyses).map((analysis) => {
            const { careHome, staffQualityScore } = analysis;
            const isExpanded = expandedHome === careHome.id;

            return (
              <div
                key={careHome.id}
                className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden"
              >
                {/* Header */}
                <div className="p-6 border-b border-gray-200">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <Building2 className="w-5 h-5 text-gray-400" />
                        <h2 className="text-xl font-semibold text-gray-900">{careHome.name}</h2>
                      </div>
                      {careHome.address && (
                        <p className="text-sm text-gray-500 ml-8">{careHome.address}</p>
                      )}
                      {careHome.postcode && (
                        <p className="text-sm text-gray-500 ml-8">
                          {careHome.postcode} {careHome.localAuthority && `• ${careHome.localAuthority}`}
                        </p>
                      )}
                    </div>
                    <div className="flex items-center gap-4">
                      {/* Overall Score */}
                      <div className={`px-4 py-2 rounded-lg border-2 ${getCategoryColor(staffQualityScore.category)}`}>
                        <div className="flex items-center gap-2">
                          {getCategoryIcon(staffQualityScore.category)}
                          <div>
                            <div className="text-2xl font-bold">{staffQualityScore.overallScore}/100</div>
                            <div className="text-xs font-medium">{staffQualityScore.category}</div>
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => setExpandedHome(isExpanded ? null : careHome.id)}
                        className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg"
                      >
                        {isExpanded ? 'Collapse' : 'Expand'}
                      </button>
                      <button
                        onClick={() => handleRemoveAnalysis(careHome.id)}
                        className="px-4 py-2 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="p-6 space-y-6 bg-gray-50">
                    {/* Component Breakdown */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Component Breakdown</h3>
                      
                      {/* Radar Chart for Components */}
                      <div className="bg-white p-6 rounded-lg border border-gray-200 mb-6">
                        <h4 className="text-md font-semibold text-gray-700 mb-4">Component Score Visualization</h4>
                        <ResponsiveContainer width="100%" height={350}>
                          <RadarChart data={[
                            { 
                              component: 'Well-Led', 
                              score: staffQualityScore.components.cqcWellLed.score, 
                              ideal: 100,
                              fullMark: 100 
                            },
                            { 
                              component: 'Effective', 
                              score: staffQualityScore.components.cqcEffective.score, 
                              ideal: 100,
                              fullMark: 100 
                            },
                            { 
                              component: 'CQC Sentiment', 
                              score: staffQualityScore.components.cqcStaffSentiment.score, 
                              ideal: 100,
                              fullMark: 100 
                            },
                            { 
                              component: 'Employee\nSentiment', 
                              score: staffQualityScore.components.employeeSentiment.score || 0, 
                              ideal: 100,
                              fullMark: 100 
                            },
                          ]}>
                            <PolarGrid stroke="#e5e7eb" />
                            <PolarAngleAxis 
                              dataKey="component" 
                              tick={{ fill: '#374151', fontSize: 12, fontWeight: 500 }}
                            />
                            <PolarRadiusAxis 
                              angle={90} 
                              domain={[0, 100]} 
                              tick={{ fill: '#6b7280', fontSize: 11 }}
                              tickCount={6}
                            />
                            <Radar 
                              name="Current Score" 
                              dataKey="score" 
                              stroke="#1E2A44" 
                              fill="#1E2A44" 
                              fillOpacity={0.6}
                              strokeWidth={2}
                            />
                            <Radar 
                              name="Ideal Score" 
                              dataKey="ideal" 
                              stroke="#10b981" 
                              fill="#10b981" 
                              fillOpacity={0.2}
                              strokeWidth={1}
                              strokeDasharray="5 5"
                            />
                            <Tooltip 
                              formatter={(value: number) => `${value.toFixed(1)}/100`}
                              contentStyle={{ 
                                backgroundColor: 'white', 
                                border: '1px solid #e5e7eb',
                                borderRadius: '6px',
                                fontSize: '12px'
                              }}
                            />
                            <Legend 
                              wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }}
                              iconType="line"
                            />
                          </RadarChart>
                        </ResponsiveContainer>
                        <p className="text-xs text-gray-500 mt-2 text-center">
                          Solid line: Current Score | Dashed line: Ideal Score (100)
                        </p>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="bg-white p-4 rounded-lg border border-gray-200">
                          <div className="flex justify-between items-center mb-2">
                            <span className="text-sm font-medium text-gray-700">CQC Well-Led</span>
                            <span className="text-xs text-gray-500">
                              {staffQualityScore.components.cqcWellLed.score !== null 
                                ? `${((staffQualityScore.components.cqcWellLed.weight || 0) * 100).toFixed(0)}%`
                                : 'N/A'}
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="text-2xl font-bold text-gray-900">
                              {staffQualityScore.components.cqcWellLed.score !== null 
                                ? staffQualityScore.components.cqcWellLed.score.toFixed(0)
                                : 'N/A'}
                            </div>
                            {staffQualityScore.components.cqcWellLed.rating && (
                              <span className="text-sm text-gray-600">
                                ({staffQualityScore.components.cqcWellLed.rating})
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="bg-white p-4 rounded-lg border border-gray-200">
                          <div className="flex justify-between items-center mb-2">
                            <span className="text-sm font-medium text-gray-700">CQC Effective</span>
                            <span className="text-xs text-gray-500">
                              {staffQualityScore.components.cqcEffective.score !== null
                                ? `${((staffQualityScore.components.cqcEffective.weight || 0) * 100).toFixed(0)}%`
                                : 'N/A'}
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="text-2xl font-bold text-gray-900">
                              {staffQualityScore.components.cqcEffective.score !== null
                                ? staffQualityScore.components.cqcEffective.score.toFixed(0)
                                : 'N/A'}
                            </div>
                            {staffQualityScore.components.cqcEffective.rating && (
                              <span className="text-sm text-gray-600">
                                ({staffQualityScore.components.cqcEffective.rating})
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="bg-white p-4 rounded-lg border border-gray-200">
                          <div className="flex justify-between items-center mb-2">
                            <span className="text-sm font-medium text-gray-700">CQC Staff Sentiment</span>
                            <span className="text-xs text-gray-500">
                              {staffQualityScore.components.cqcStaffSentiment.score !== null
                                ? `${((staffQualityScore.components.cqcStaffSentiment.weight || 0) * 100).toFixed(0)}%`
                                : 'N/A'}
                            </span>
                          </div>
                          <div className="text-2xl font-bold text-gray-900">
                            {staffQualityScore.components.cqcStaffSentiment.score !== null
                              ? staffQualityScore.components.cqcStaffSentiment.score.toFixed(0)
                              : 'N/A'}
                          </div>
                        </div>
                        <div className="bg-white p-4 rounded-lg border border-gray-200">
                          <div className="flex justify-between items-center mb-2">
                            <span className="text-sm font-medium text-gray-700">Employee Reviews</span>
                            <span className="text-xs text-gray-500">
                              {staffQualityScore.components.employeeSentiment.score !== null
                                ? `${(staffQualityScore.components.employeeSentiment.weight * 100).toFixed(0)}%`
                                : 'N/A'}
                            </span>
                          </div>
                          <div className="text-2xl font-bold text-gray-900">
                            {staffQualityScore.components.employeeSentiment.score !== null
                              ? `${staffQualityScore.components.employeeSentiment.score.toFixed(0)}`
                              : 'Insufficient Data'}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            {staffQualityScore.components.employeeSentiment.reviewCount} reviews found
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Flags */}
                    {staffQualityScore.flags.length > 0 && (
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Flags & Warnings</h3>
                        <div className="space-y-2">
                          {staffQualityScore.flags.map((flag, idx) => (
                            <div
                              key={idx}
                              className={`p-3 rounded-lg border ${
                                flag.type === 'red'
                                  ? 'bg-red-50 border-red-200 text-red-800'
                                  : 'bg-yellow-50 border-yellow-200 text-yellow-800'
                              }`}
                            >
                              <div className="flex items-start gap-2">
                                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                                <span className="text-sm">{flag.message}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Themes */}
                    {(staffQualityScore.themes.positive.length > 0 || staffQualityScore.themes.negative.length > 0) && (
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Themes from Reviews</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {staffQualityScore.themes.positive.length > 0 && (
                            <div>
                              <h4 className="text-sm font-medium text-green-700 mb-2">Positive Themes</h4>
                              <ul className="space-y-1">
                                {staffQualityScore.themes.positive.map((theme, idx) => (
                                  <li key={idx} className="text-sm text-gray-700 flex items-center gap-2">
                                    <CheckCircle className="w-4 h-4 text-green-600" />
                                    {theme}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {staffQualityScore.themes.negative.length > 0 && (
                            <div>
                              <h4 className="text-sm font-medium text-red-700 mb-2">Concerns</h4>
                              <ul className="space-y-1">
                                {staffQualityScore.themes.negative.map((theme, idx) => (
                                  <li key={idx} className="text-sm text-gray-700 flex items-center gap-2">
                                    <AlertCircle className="w-4 h-4 text-red-600" />
                                    {theme}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Data Quality */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Quality</h3>
                      <div className="bg-white p-4 rounded-lg border border-gray-200">
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="text-sm text-gray-600">Confidence Level</span>
                            <span className={`text-sm font-medium ${
                              staffQualityScore.confidence === 'High' ? 'text-green-600' :
                              staffQualityScore.confidence === 'Medium' ? 'text-yellow-600' :
                              'text-red-600'
                            }`}>
                              {staffQualityScore.confidence}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm text-gray-600">CQC Data Age</span>
                            <span className="text-sm font-medium text-gray-900">
                              {staffQualityScore.dataQuality.cqcDataAge}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm text-gray-600">Employee Reviews Found</span>
                            <span className="text-sm font-medium text-gray-900">
                              {staffQualityScore.dataQuality.reviewCount}
                            </span>
                          </div>
                          {staffQualityScore.dataQuality.hasInsufficientData && (
                            <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                              <p className="text-sm font-medium text-yellow-900 mb-2">
                                ⚠️ Insufficient Data for Accurate Assessment
                              </p>
                              <ul className="text-sm text-yellow-800 space-y-1 list-disc list-inside">
                                {staffQualityScore.dataQuality.reviewCount < 3 && (
                                  <li>Only {staffQualityScore.dataQuality.reviewCount} employee review(s) found. Need at least 3 for sentiment analysis.</li>
                                )}
                                {!analysis.cqcData.wellLed && (
                                  <li>Missing CQC Well-Led rating</li>
                                )}
                                {!analysis.cqcData.effective && (
                                  <li>Missing CQC Effective rating</li>
                                )}
                                {(() => {
                                  const ageMatch = staffQualityScore.dataQuality.cqcDataAge.match(/(\d+)\s*months?/i);
                                  const ageMonths = ageMatch ? parseInt(ageMatch[1]) : 0;
                                  return ageMonths > 24;
                                })() && (
                                  <li>CQC data is {staffQualityScore.dataQuality.cqcDataAge} - may be outdated</li>
                                )}
                              </ul>
                              <p className="text-sm text-yellow-800 mt-2">
                                <strong>Recommendation:</strong> For complete assessment, verify data with direct staff interviews during site visit.
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Key Findings Summary Section */}
                    {analysis.keyFindingsSummary && (
                      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg border border-blue-200">
                        <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                          <Info className="w-5 h-5 text-blue-600" />
                          Key Findings
                        </h3>
                        <p className="text-gray-700 leading-relaxed">
                          {analysis.keyFindingsSummary.summary}
                        </p>
                        <div className="mt-3 flex items-center gap-4 text-xs text-gray-500">
                          <span>Based on {analysis.keyFindingsSummary.review_count} reviews</span>
                          <span>•</span>
                          <span>Score: {analysis.keyFindingsSummary.overall_score}/100 ({analysis.keyFindingsSummary.category})</span>
                        </div>
                      </div>
                    )}

                    {/* Perplexity Online Research Section - Simplified */}
                    {analysis.perplexityResearch && (
                      <div className={`p-4 rounded-lg border ${
                        analysis.perplexityResearch.has_negative_findings 
                          ? 'bg-yellow-50 border-yellow-200' 
                          : 'bg-green-50 border-green-200'
                      }`}>
                        <h4 className="text-sm font-semibold text-gray-800 mb-2 flex items-center gap-2">
                          <svg className="w-4 h-4 text-purple-600" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" fill="none" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          </svg>
                          Online Staff Reputation Research
                          {!analysis.perplexityResearch.has_negative_findings && (
                            <CheckCircle className="w-4 h-4 text-green-600" />
                          )}
                        </h4>
                        <p className="text-sm text-gray-700">
                          {analysis.perplexityResearch.summary || 'No specific online data found about staff. No negative reports identified.'}
                        </p>
                        {analysis.perplexityResearch.citations && analysis.perplexityResearch.citations.length > 0 && (
                          <details className="mt-2">
                            <summary className="text-xs text-blue-600 cursor-pointer hover:underline">
                              View sources ({analysis.perplexityResearch.citations.length})
                            </summary>
                            <div className="mt-2 space-y-1">
                              {analysis.perplexityResearch.citations.slice(0, 5).map((citation, idx) => (
                                <a
                                  key={idx}
                                  href={typeof citation === 'string' ? citation : '#'}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="block text-xs text-blue-600 hover:underline truncate"
                                >
                                  {typeof citation === 'string' ? citation : JSON.stringify(citation)}
                                </a>
                              ))}
                            </div>
                          </details>
                        )}
                      </div>
                    )}

                    {/* CQC Enforcement Actions Section */}
                    {analysis.enforcementSignals && (
                      <div className={`p-4 rounded-lg border ${
                        analysis.enforcementSignals.has_enforcement_actions 
                          ? 'bg-red-50 border-red-300' 
                          : 'bg-green-50 border-green-200'
                      }`}>
                        <h4 className="text-sm font-semibold text-gray-800 mb-2 flex items-center gap-2">
                          <AlertCircle className={`w-4 h-4 ${
                            analysis.enforcementSignals.has_enforcement_actions ? 'text-red-600' : 'text-green-600'
                          }`} />
                          CQC Enforcement Actions
                          {!analysis.enforcementSignals.has_enforcement_actions && (
                            <CheckCircle className="w-4 h-4 text-green-600" />
                          )}
                        </h4>
                        {analysis.enforcementSignals.has_enforcement_actions ? (
                          <div>
                            <p className="text-sm text-red-700 font-medium">
                              ⚠️ {analysis.enforcementSignals.count} enforcement action(s) on record
                              {analysis.enforcementSignals.severity && ` (Severity: ${analysis.enforcementSignals.severity})`}
                            </p>
                            {analysis.enforcementSignals.actions && analysis.enforcementSignals.actions.length > 0 && (
                              <ul className="mt-2 space-y-1">
                                {analysis.enforcementSignals.actions.slice(0, 3).map((action, idx) => (
                                  <li key={idx} className="text-xs text-red-600">
                                    • {action.type}{action.date && ` (${action.date})`}
                                  </li>
                                ))}
                              </ul>
                            )}
                          </div>
                        ) : (
                          <p className="text-sm text-green-700">
                            ✅ No enforcement actions on record - positive indicator
                          </p>
                        )}
                      </div>
                    )}

                    {/* Company Stability Signals Section */}
                    {analysis.companySignals && (
                      <div className={`p-4 rounded-lg border ${
                        analysis.companySignals.staff_quality_impact.level === 'NEGATIVE' || analysis.companySignals.staff_quality_impact.level === 'CRITICAL'
                          ? 'bg-amber-50 border-amber-300'
                          : analysis.companySignals.staff_quality_impact.level === 'POSITIVE'
                          ? 'bg-green-50 border-green-200'
                          : 'bg-gray-50 border-gray-200'
                      }`}>
                        <h4 className="text-sm font-semibold text-gray-800 mb-3 flex items-center gap-2">
                          <Building2 className="w-4 h-4 text-blue-600" />
                          Company Stability Analysis
                          <span className="text-xs font-normal text-gray-500">
                            ({analysis.companySignals.company_name})
                          </span>
                        </h4>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          {/* Director Stability */}
                          <div className="bg-white p-3 rounded border">
                            <div className="text-xs text-gray-500 mb-1">Director Stability</div>
                            <div className={`text-sm font-semibold ${
                              analysis.companySignals.director_stability.stability_label === 'Excellent' ? 'text-green-600' :
                              analysis.companySignals.director_stability.stability_label === 'Good' ? 'text-blue-600' :
                              analysis.companySignals.director_stability.stability_label === 'Concerning' ? 'text-amber-600' :
                              'text-red-600'
                            }`}>
                              {analysis.companySignals.director_stability.stability_label}
                            </div>
                            <div className="text-xs text-gray-500 mt-1">
                              {analysis.companySignals.director_stability.active_directors} active directors
                              {analysis.companySignals.director_stability.resignations_last_year > 0 && (
                                <span className="text-amber-600"> • {analysis.companySignals.director_stability.resignations_last_year} resigned (1yr)</span>
                              )}
                            </div>
                            {analysis.companySignals.director_stability.average_tenure_years > 0 && (
                              <div className="text-xs text-gray-500">
                                Avg tenure: {analysis.companySignals.director_stability.average_tenure_years.toFixed(1)} years
                              </div>
                            )}
                          </div>
                          
                          {/* Financial Risk */}
                          <div className="bg-white p-3 rounded border">
                            <div className="text-xs text-gray-500 mb-1">Financial Risk</div>
                            <div className={`text-sm font-semibold ${
                              analysis.companySignals.financial_risk.risk_level === 'Very Low' ? 'text-green-600' :
                              analysis.companySignals.financial_risk.risk_level === 'Low' ? 'text-blue-600' :
                              analysis.companySignals.financial_risk.risk_level === 'Medium' ? 'text-amber-600' :
                              'text-red-600'
                            }`}>
                              {analysis.companySignals.financial_risk.risk_level}
                            </div>
                            <div className="text-xs text-gray-500 mt-1">
                              Risk Score: {analysis.companySignals.financial_risk.risk_score}/100
                            </div>
                            <div className="text-xs text-gray-500">
                              Company age: {analysis.companySignals.company_age_years.toFixed(1)} years
                            </div>
                          </div>
                          
                          {/* Staff Impact */}
                          <div className="bg-white p-3 rounded border">
                            <div className="text-xs text-gray-500 mb-1">Staff Quality Impact</div>
                            <div className={`text-sm font-semibold ${
                              analysis.companySignals.staff_quality_impact.level === 'POSITIVE' ? 'text-green-600' :
                              analysis.companySignals.staff_quality_impact.level === 'NEUTRAL' ? 'text-gray-600' :
                              analysis.companySignals.staff_quality_impact.level === 'NEGATIVE' ? 'text-amber-600' :
                              'text-red-600'
                            }`}>
                              {analysis.companySignals.staff_quality_impact.level}
                            </div>
                            {analysis.companySignals.staff_quality_impact.score_adjustment !== 0 && (
                              <div className={`text-xs ${analysis.companySignals.staff_quality_impact.score_adjustment > 0 ? 'text-green-600' : 'text-red-600'}`}>
                                Score adjustment: {analysis.companySignals.staff_quality_impact.score_adjustment > 0 ? '+' : ''}{analysis.companySignals.staff_quality_impact.score_adjustment}
                              </div>
                            )}
                          </div>
                        </div>
                        
                        {/* Flags/Issues */}
                        {analysis.companySignals.staff_quality_impact.flags.length > 0 && (
                          <div className="mt-3 pt-3 border-t">
                            <div className="text-xs text-gray-600 space-y-1">
                              {analysis.companySignals.staff_quality_impact.flags.map((flag, idx) => (
                                <div key={idx} className="flex items-start gap-1">
                                  <span className={
                                    analysis.companySignals!.staff_quality_impact.level === 'POSITIVE' ? '✅' :
                                    analysis.companySignals!.staff_quality_impact.level === 'NEGATIVE' || analysis.companySignals!.staff_quality_impact.level === 'CRITICAL' ? '⚠️' : '•'
                                  }></span>
                                  <span>{flag}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Reviews */}
                    {analysis.reviews.length > 0 && (
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Employee Reviews</h3>
                        
                        {/* Sentiment Bar Chart */}
                        <div className="bg-white p-6 rounded-lg border border-gray-200 mb-6">
                          <h4 className="text-md font-semibold text-gray-700 mb-4">Review Sentiment Distribution</h4>
                          <ResponsiveContainer width="100%" height={300}>
                            <BarChart
                              data={(() => {
                                const sentimentCounts = analysis.reviews.reduce((acc, review) => {
                                  acc[review.sentiment] = (acc[review.sentiment] || 0) + 1;
                                  return acc;
                                }, {} as Record<string, number>);
                                
                                const colors: Record<string, string> = {
                                  'POSITIVE': '#10b981',
                                  'NEUTRAL': '#6b7280',
                                  'MIXED': '#f59e0b',
                                  'NEGATIVE': '#ef4444',
                                };
                                
                                return [
                                  { sentiment: 'POSITIVE', count: sentimentCounts['POSITIVE'] || 0, color: colors['POSITIVE'] },
                                  { sentiment: 'NEUTRAL', count: sentimentCounts['NEUTRAL'] || 0, color: colors['NEUTRAL'] },
                                  { sentiment: 'MIXED', count: sentimentCounts['MIXED'] || 0, color: colors['MIXED'] },
                                  { sentiment: 'NEGATIVE', count: sentimentCounts['NEGATIVE'] || 0, color: colors['NEGATIVE'] },
                                ];
                              })()}
                              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                            >
                              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                              <XAxis 
                                dataKey="sentiment" 
                                tick={{ fill: '#374151', fontSize: 12 }}
                              />
                              <YAxis 
                                tick={{ fill: '#6b7280', fontSize: 12 }}
                                label={{ value: 'Number of Reviews', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#6b7280', fontSize: 12 } }}
                              />
                              <Tooltip 
                                contentStyle={{ 
                                  backgroundColor: 'white', 
                                  border: '1px solid #e5e7eb',
                                  borderRadius: '6px',
                                  fontSize: '12px'
                                }}
                                formatter={(value: number) => [`${value} review${value !== 1 ? 's' : ''}`, 'Count']}
                              />
                              <Bar 
                                dataKey="count" 
                                radius={[8, 8, 0, 0]}
                              >
                                {(() => {
                                  const sentimentCounts = analysis.reviews.reduce((acc, review) => {
                                    acc[review.sentiment] = (acc[review.sentiment] || 0) + 1;
                                    return acc;
                                  }, {} as Record<string, number>);
                                  
                                  const colors: Record<string, string> = {
                                    'POSITIVE': '#10b981',
                                    'NEUTRAL': '#6b7280',
                                    'MIXED': '#f59e0b',
                                    'NEGATIVE': '#ef4444',
                                  };
                                  
                                  const data = [
                                    { sentiment: 'POSITIVE', count: sentimentCounts['POSITIVE'] || 0 },
                                    { sentiment: 'NEUTRAL', count: sentimentCounts['NEUTRAL'] || 0 },
                                    { sentiment: 'MIXED', count: sentimentCounts['MIXED'] || 0 },
                                    { sentiment: 'NEGATIVE', count: sentimentCounts['NEGATIVE'] || 0 },
                                  ];
                                  
                                  return data.map((item, index) => (
                                    <Cell key={`cell-${index}`} fill={colors[item.sentiment]} />
                                  ));
                                })()}
                              </Bar>
                            </BarChart>
                          </ResponsiveContainer>
                          <div className="mt-4 flex flex-wrap gap-4 justify-center text-xs">
                            <div className="flex items-center gap-2">
                              <div className="w-3 h-3 rounded bg-green-500"></div>
                              <span className="text-gray-600">Positive</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <div className="w-3 h-3 rounded bg-gray-500"></div>
                              <span className="text-gray-600">Neutral</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <div className="w-3 h-3 rounded bg-yellow-500"></div>
                              <span className="text-gray-600">Mixed</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <div className="w-3 h-3 rounded bg-red-500"></div>
                              <span className="text-gray-600">Negative</span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="space-y-3">
                          {analysis.reviews.map((review, idx) => (
                            <div key={idx} className="bg-white p-4 rounded-lg border border-gray-200">
                              <div className="flex justify-between items-start mb-2">
                                <div className="flex items-center gap-2">
                                  <MessageSquare className="w-4 h-4 text-gray-400" />
                                  <span className="text-sm font-medium text-gray-700">{review.source}</span>
                                  <div className="flex items-center gap-1">
                                    {[...Array(5)].map((_, i) => (
                                      <Star
                                        key={i}
                                        className={`w-4 h-4 ${
                                          i < Math.floor(review.rating || 0)
                                            ? 'text-yellow-400 fill-current'
                                            : 'text-gray-300'
                                        }`}
                                      />
                                    ))}
                                    <span className="text-sm text-gray-600 ml-1">{(review.rating || 0).toFixed(1)}</span>
                                  </div>
                                </div>
                                <span className={`px-2 py-1 rounded text-xs font-medium ${
                                  review.sentiment === 'POSITIVE' ? 'bg-green-100 text-green-700' :
                                  review.sentiment === 'MIXED' ? 'bg-yellow-100 text-yellow-700' :
                                  review.sentiment === 'NEGATIVE' ? 'bg-red-100 text-red-700' :
                                  'bg-gray-100 text-gray-700'
                                }`}>
                                  {review.sentiment}
                                </span>
                              </div>
                              {review.text && (
                                <p className="text-sm text-gray-700 mb-2">{review.text}</p>
                              )}
                              {review.date && (
                                <p className="text-xs text-gray-500">{review.date}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Empty State */}
      {Object.keys(analyses).length === 0 && !Object.values(loading).some(l => l) && (
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-12 text-center">
          <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No analysis results yet. Search for a care home or select an example above to start.</p>
        </div>
      )}
    </div>
  );
}

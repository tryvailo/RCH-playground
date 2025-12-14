import { useState, useRef } from 'react';
import { Search, Globe, FileText, Users, Building, DollarSign, Activity, Phone, Mail, Star, TrendingUp, CheckCircle, AlertCircle, Loader, Zap, UtensilsCrossed, Award, Shield, Car, Image, FileText as FileTextIcon, Calendar, HelpCircle, Info, PoundSterling } from 'lucide-react';
import axios from 'axios';

interface TestCareHome {
  name: string;
  website: string;
  status: string;
  bestFor: string;
  address?: string;
  city?: string;
  postcode?: string;
}

const TEST_CARE_HOMES: TestCareHome[] = [
  {
    name: "Metchley Manor",
    website: "careuk.com/homes/metchley-manor",
    status: "✅ Активный",
    bestFor: "Крупный провайдер",
    address: "Metchley Lane",
    city: "Birmingham",
    postcode: "B15 2QX"
  },
  {
    name: "Clare Court",
    website: "averyhealthcare.co.uk/our-homes/clare-court",
    status: "✅ Активный",
    bestFor: "Diversity extraction",
    address: "Clare Court",
    city: "Birmingham",
    postcode: "B15 2QX"
  },
  {
    name: "Bartley Green",
    website: "sanctuary-care.co.uk/care-homes/bartley-green-lodge",
    status: "✅ Активный",
    bestFor: "Activity analysis",
    address: "Bartley Green",
    city: "Birmingham",
    postcode: "B32 3QJ"
  },
  {
    name: "Inglewood",
    website: "careuk.com",
    status: "✅ Активный",
    bestFor: "Price aggregation",
    address: "Inglewood Road",
    city: "Birmingham",
    postcode: "B17 9DJ"
  }
];

interface FirecrawlAnalysis {
  care_home_name: string;
  website_url: string;
  extraction_method?: string;
  scraped_at: string;
  map_summary?: {
    total_urls_found: number;
    classified_categories: Record<string, number>;
  };
  crawl_summary?: {
    pages_crawled: number;
  };
  structured_data: {
    staff?: {
      team_size?: string;
      qualifications?: string[];
      specialist_roles?: string[];
      key_staff?: Array<{
        name?: string;
        role?: string;
        qualifications?: string;
        bio?: string;
      }>;
      training_programs?: string[];
      staff_ratios?: string;
    };
    facilities?: {
      rooms?: string[];
      communal_areas?: string[];
      outdoor_spaces?: string[];
      special_facilities?: string[];
      accessibility?: string[];
      room_count?: string;
      capacity?: string;
      building_type?: string;
      year_built?: string;
      recent_renovations?: string[];
    };
    care_services?: {
      care_types?: string[];
      specializations?: string[];
      medical_services?: string[];
      end_of_life_care?: boolean;
      respite_care?: boolean;
      day_care?: boolean;
      emergency_admissions?: boolean;
      care_plans?: string;
    };
    pricing?: {
      weekly_rate_range?: string;
      included_services?: string[];
      additional_fees?: Array<{
        service?: string;
        cost?: string;
        frequency?: string;
      }>;
      funding_options?: string[];
      deposit_required?: string;
      payment_methods?: string[];
      price_transparency?: string;
    };
    activities?: {
      daily_activities?: string[];
      therapies?: string[];
      outings?: string[];
      special_events?: string[];
      activity_coordinator?: string;
      visitor_programs?: string[];
    };
    contact?: {
      phone?: string;
      email?: string;
      address?: string;
      visiting_hours?: string;
      website?: string;
      emergency_contact?: string;
      postcode?: string;
      coordinates?: {
        latitude?: string;
        longitude?: string;
      };
    };
    registration?: {
      cqc_provider_id?: string;
      cqc_location_id?: string;
      registered_manager?: string;
      registration_date?: string;
      last_inspection_date?: string;
      cqc_rating?: string;
    };
    nutrition?: {
      meal_times?: string;
      dining_options?: string[];
      dietary_accommodations?: string[];
      menu_variety?: string;
      snacks_available?: boolean;
      special_diets?: string[];
      dining_environment?: string;
      nutritional_planning?: string;
    };
    reviews?: {
      testimonials?: Array<{
        author?: string;
        relationship?: string;
        rating?: string;
        comment?: string;
        date?: string;
      }>;
      average_rating?: string;
      review_count?: string;
      review_sources?: string[];
    };
    awards?: {
      awards_list?: Array<{
        name?: string;
        year?: string;
        organization?: string;
      }>;
      accreditations?: string[];
      certifications?: string[];
      memberships?: string[];
    };
    safety?: {
      safeguarding_policies?: string[];
      emergency_procedures?: string;
      security_features?: string[];
      fire_safety?: string;
      infection_control?: string;
      medication_management?: string;
      risk_assessment?: string;
    };
    transport?: {
      parking_available?: boolean;
      parking_spaces?: string;
      public_transport?: string[];
      accessibility_by_car?: string;
      nearby_amenities?: string[];
      directions?: string;
    };
    media?: {
      photo_gallery?: string[];
      videos?: string[];
      virtual_tour?: string;
      brochure_download?: string;
      social_media?: {
        facebook?: string;
        twitter?: string;
        instagram?: string;
      };
    };
    policies?: {
      admission_policy?: string;
      visiting_policy?: string;
      complaints_procedure?: string;
      privacy_policy?: string;
      terms_and_conditions?: string;
      safeguarding_policy?: string;
    };
    events?: {
      upcoming_events?: Array<{
        title?: string;
        date?: string;
        description?: string;
      }>;
      news_updates?: string[];
      announcements?: string[];
    };
    faq?: {
      questions?: Array<{
        question?: string;
        answer?: string;
      }>;
    };
    about?: {
      history?: string;
      years_in_operation?: string;
      mission_statement?: string;
      values?: string[];
      description?: string;
      owner_operator?: string;
    };
    // Legacy fields for backward compatibility
    staff_qualifications?: string[];
    facilities?: string[];
    services?: string[];
    pricing_info?: string | null;
    activities?: string[];
    contact_info?: {
      phone?: string | null;
      email?: string | null;
      address?: string | null;
    };
  };
  completeness?: {
    staff?: boolean;
    facilities?: boolean;
    services?: boolean;
    pricing?: boolean;
    activities?: boolean;
    contact?: boolean;
    nutrition?: boolean;
    reviews?: boolean;
    awards?: boolean;
    safety?: boolean;
    transport?: boolean;
    media?: boolean;
    policies?: boolean;
    events?: boolean;
    faq?: boolean;
    about?: boolean;
  };
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

export default function FirecrawlExplorer() {
  const [loading, setLoading] = useState(false);
  const [loadingDementia, setLoadingDementia] = useState(false);
  const [loadingPricing, setLoadingPricing] = useState(false);
  
  // Form state
  const [careHomeName, setCareHomeName] = useState('');
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [postcode, setPostcode] = useState('');
  
  // Results
  const [firecrawlResult, setFirecrawlResult] = useState<FirecrawlAnalysis | null>(null);
  const [pricingResult, setPricingResult] = useState<PricingResult | null>(null);
  const [cost, setCost] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  
  // Refs for scrolling to results
  const resultsRef = useRef<HTMLDivElement>(null);

  const handleFirecrawlAnalysis = async () => {
    if (!websiteUrl.trim()) {
      setError('Please enter a website URL');
      return;
    }

    if (loading || loadingDementia) {
      return; // Prevent multiple simultaneous calls
    }

    setLoading(true);
    setLoadingDementia(false); // Ensure dementia loading is false
    setError(null);
    setFirecrawlResult(null);
    
    try {
      // Ensure URL has protocol
      let url = websiteUrl.trim();
      if (!url.startsWith('http://') && !url.startsWith('https://')) {
        url = 'https://' + url;
      }
      
      const response = await axios.post('/api/firecrawl/analyze', {
        url: url,
        care_home_name: careHomeName.trim() || undefined
      });
      
      console.log('Firecrawl response:', response.data);
      
      if (response.data.status === 'success') {
        setFirecrawlResult(response.data.data);
        setCost((prev) => prev + (response.data.cost_estimate || 0));
        // Scroll to results after a short delay
        setTimeout(() => {
          resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
      } else {
        setError(response.data.message || 'Analysis failed');
      }
    } catch (error: any) {
      console.error('Firecrawl analysis error:', error);
      console.error('Error details:', error.response?.data);
      
      let errorMessage = 'Unknown error occurred';
      
      if (error.response) {
        // Server responded with error
        const detail = error.response.data?.detail;
        if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (error.response.data?.message) {
          errorMessage = error.response.data.message;
        } else if (error.response.data?.error) {
          errorMessage = typeof error.response.data.error === 'string' 
            ? error.response.data.error 
            : JSON.stringify(error.response.data.error);
        }
      } else if (error.request) {
        errorMessage = 'No response from server. Please check your connection.';
      } else {
        errorMessage = error.message || 'Unknown error';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleDementiaCareAnalysis = async () => {
    if (!websiteUrl.trim()) {
      setError('Please enter a website URL');
      return;
    }

    if (loading || loadingDementia) {
      return; // Prevent multiple simultaneous calls
    }

    setLoadingDementia(true);
    setLoading(false); // Ensure regular loading is false
    setError(null);
    setFirecrawlResult(null);
    
    try {
      // Ensure URL has protocol
      let url = websiteUrl.trim();
      if (!url.startsWith('http://') && !url.startsWith('https://')) {
        url = 'https://' + url;
      }
      
      const response = await axios.post('/api/firecrawl/dementia-care-analysis', {
        url: url,
        care_home_name: careHomeName.trim() || undefined
      }, {
        timeout: 300000  // 5 minutes timeout
      });
      
      console.log('Dementia Care Analysis response:', response.data);
      
      if (response.data.status === 'success') {
        // Ensure data is properly formatted
        const resultData = response.data.data || {};
        setFirecrawlResult(resultData);
        setCost((prev) => prev + (response.data.cost_estimate || 0));
        // Scroll to results after a short delay
        setTimeout(() => {
          resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
      } else {
        setError(response.data.message || 'Analysis failed');
      }
    } catch (error: any) {
      console.error('Dementia care analysis error:', error);
      
      let errorMessage = 'Unknown error occurred';
      
      if (error.response) {
        const detail = error.response.data?.detail;
        if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (error.response.data?.message) {
          errorMessage = error.response.data.message;
        }
      } else if (error.request) {
        errorMessage = 'No response from server. Please check your connection.';
      } else {
        errorMessage = error.message || 'Unknown error';
      }
      
      setError(errorMessage);
    } finally {
      setLoadingDementia(false);
    }
  };

  const handleExtractPricing = async () => {
    if (!websiteUrl.trim()) {
      setError('Please enter a website URL');
      return;
    }

    if (loading || loadingDementia || loadingPricing) {
      return; // Prevent multiple simultaneous calls
    }

    setLoadingPricing(true);
    setLoading(false);
    setLoadingDementia(false);
    setError(null);
    setPricingResult(null);
    
    try {
      // Ensure URL has protocol
      let url = websiteUrl.trim();
      if (!url.startsWith('http://') && !url.startsWith('https://')) {
        url = 'https://' + url;
      }
      
      const response = await axios.post('/api/firecrawl/extract-pricing', {
        url: url,
        care_home_name: careHomeName.trim() || undefined,
        postcode: postcode.trim() || undefined
      }, {
        timeout: 180000  // 3 minutes timeout
      });
      
      console.log('Pricing extraction response:', response.data);
      
      if (response.data.status === 'success') {
        setPricingResult(response.data.data);
        setCost((prev) => prev + (response.data.cost_estimate || 0));
        // Scroll to results after a short delay
        setTimeout(() => {
          resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
      } else {
        setError(response.data.message || 'Pricing extraction failed');
      }
    } catch (error: any) {
      console.error('Pricing extraction error:', error);
      
      let errorMessage = 'Unknown error occurred';
      
      if (error.response) {
        const detail = error.response.data?.detail;
        if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (error.response.data?.message) {
          errorMessage = error.response.data.message;
        }
      } else if (error.request) {
        errorMessage = 'No response from server. Please check your connection.';
      } else {
        errorMessage = error.message || 'Unknown error';
      }
      
      setError(errorMessage);
    } finally {
      setLoadingPricing(false);
    }
  };

  const handleSubmit = (e?: React.MouseEvent) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    handleFirecrawlAnalysis();
  };

  const handleSelectTestHome = (home: TestCareHome) => {
    setCareHomeName(home.name);
    setWebsiteUrl(home.website);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Globe className="w-6 h-6 text-primary" />
              Firecrawl Explorer
            </h1>
            <p className="text-gray-600 mt-1">
              Analyze care home websites using Firecrawl 4-phase universal semantic crawling
            </p>
          </div>
          {cost > 0 && (
            <div className="text-right">
              <div className="text-sm text-gray-500">Total Cost</div>
              <div className="text-2xl font-bold text-primary">£{cost.toFixed(2)}</div>
            </div>
          )}
        </div>

        {/* Test Care Homes */}
        <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Zap className="w-4 h-4 text-blue-600" />
            Тестовые дома престарелых
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {TEST_CARE_HOMES.map((home, index) => (
              <button
                key={index}
                onClick={() => handleSelectTestHome(home)}
                className="text-left p-3 bg-white rounded-lg border border-gray-200 hover:border-primary hover:shadow-md transition-all group"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="font-semibold text-gray-900 group-hover:text-primary transition-colors">
                      {home.name}
                    </div>
                    <div className="text-xs text-gray-600 mt-1 font-mono break-all">
                      {home.website}
                    </div>
                    {(home.address || home.city || home.postcode) && (
                      <div className="text-xs text-gray-500 mt-1">
                        {[home.address, home.city, home.postcode].filter(Boolean).join(', ')}
                      </div>
                    )}
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-xs text-green-700">{home.status}</span>
                      <span className="text-xs text-gray-500">•</span>
                      <span className="text-xs text-gray-600">{home.bestFor}</span>
                    </div>
                  </div>
                  <Globe className="w-4 h-4 text-gray-400 group-hover:text-primary transition-colors flex-shrink-0 ml-2" />
                </div>
              </button>
            ))}
          </div>
          <p className="text-xs text-gray-600 mt-3">
            💡 Кликните на дом для автоматического заполнения формы
          </p>
        </div>

        {/* Form */}
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Care Home Name (optional)
              </label>
              <input
                type="text"
                value={careHomeName}
                onChange={(e) => setCareHomeName(e.target.value)}
                placeholder="e.g., Manor House Care Home"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Website URL *
              </label>
              <input
                type="text"
                value={websiteUrl}
                onChange={(e) => setWebsiteUrl(e.target.value)}
                placeholder="e.g., www.manorhousecare.co.uk"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Postcode (optional)
              </label>
              <input
                type="text"
                value={postcode}
                onChange={(e) => setPostcode(e.target.value)}
                placeholder="e.g., SW1A 1AA"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                if (!loading && !loadingDementia && !loadingPricing) {
                  handleFirecrawlAnalysis();
                }
              }}
              disabled={loading || loadingDementia || loadingPricing}
              className="flex-1 bg-primary text-white py-3 px-6 rounded-lg font-medium hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  Analyze Website
                </>
              )}
            </button>
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                if (!loading && !loadingDementia && !loadingPricing) {
                  handleDementiaCareAnalysis();
                }
              }}
              disabled={loading || loadingDementia || loadingPricing}
              className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loadingDementia ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Users className="w-5 h-5" />
                  Dementia Care Analysis
                </>
              )}
            </button>
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                if (!loading && !loadingDementia && !loadingPricing) {
                  handleExtractPricing();
                }
              }}
              disabled={loading || loadingDementia || loadingPricing}
              className="flex-1 bg-green-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loadingPricing ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Extracting...
                </>
              ) : (
                <>
                  <PoundSterling className="w-5 h-5" />
                  Extract Pricing
                </>
              )}
            </button>
          </div>
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
      </div>

      {/* Firecrawl Results */}
      {firecrawlResult && (
        <div ref={resultsRef} className="bg-white rounded-lg shadow p-6 space-y-6">
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <FileText className="w-5 h-5 text-primary" />
            {firecrawlResult.analysis_type === 'dementia_care_quality' 
              ? 'Dementia Care Quality Analysis' 
              : 'Firecrawl Analysis Results'}
          </h2>

          {/* Dementia Care Analysis Results */}
          {firecrawlResult.analysis_type === 'dementia_care_quality' && firecrawlResult.dementia_care_analysis && (
            <div className="space-y-4 border-t pt-6">
              <h3 className="text-lg font-semibold text-gray-900">Dementia Care Quality Assessment</h3>
              
              {firecrawlResult.dementia_care_analysis.dementia_care_quality_score !== undefined ? (
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600 mb-1">Overall Quality Score</div>
                  <div className="text-4xl font-bold text-blue-700">
                    {firecrawlResult.dementia_care_analysis.dementia_care_quality_score}/10
                  </div>
                  {firecrawlResult.dementia_care_analysis.rating_reasoning && (
                    <div className="mt-2 text-sm text-gray-700">
                      {firecrawlResult.dementia_care_analysis.rating_reasoning}
                    </div>
                  )}
                </div>
              ) : firecrawlResult.dementia_care_analysis.analysis_text ? (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600 mb-2">Analysis</div>
                  <div className="text-sm text-gray-700 whitespace-pre-wrap">
                    {firecrawlResult.dementia_care_analysis.analysis_text}
                  </div>
                </div>
              ) : null}

              {firecrawlResult.dementia_care_analysis.raw_content && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600 mb-2">Extracted Content</div>
                  <div className="text-xs text-gray-700 whitespace-pre-wrap max-h-96 overflow-y-auto">
                    {firecrawlResult.dementia_care_analysis.raw_content}
                  </div>
                </div>
              )}

              {firecrawlResult.dementia_care_analysis.note && (
                <div className="bg-yellow-50 border border-yellow-200 p-3 rounded-lg">
                  <div className="text-xs text-yellow-800">{firecrawlResult.dementia_care_analysis.note}</div>
                </div>
              )}

              {/* Detailed breakdown if available */}
              {firecrawlResult.dementia_care_analysis.specialist_team && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                  {['specialist_team', 'unit_design', 'activity_programs', 'family_involvement', 
                    'staff_ratio', 'behavioral_support', 'end_of_life_care'].map((category) => {
                    const categoryData = firecrawlResult.dementia_care_analysis[category];
                    if (!categoryData) return null;
                    return (
                      <div key={category} className="border border-gray-200 rounded-lg p-3">
                        <div className="text-sm font-semibold text-gray-900 capitalize mb-2">
                          {category.replace(/_/g, ' ')}
                        </div>
                        {categoryData.score !== undefined && (
                          <div className="text-2xl font-bold text-blue-600 mb-2">
                            {categoryData.score}/10
                          </div>
                        )}
                        {categoryData.details && (
                          <div className="text-xs text-gray-600 mb-2">{categoryData.details}</div>
                        )}
                        {categoryData.strengths && categoryData.strengths.length > 0 && (
                          <div className="text-xs text-green-700">
                            <strong>Strengths:</strong> {categoryData.strengths.join(', ')}
                          </div>
                        )}
                        {categoryData.gaps && categoryData.gaps.length > 0 && (
                          <div className="text-xs text-red-700 mt-1">
                            <strong>Gaps:</strong> {categoryData.gaps.join(', ')}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}

              {firecrawlResult.dementia_care_analysis.recommendations && (
                <div className="mt-4 bg-green-50 p-4 rounded-lg">
                  <div className="text-sm font-semibold text-gray-900 mb-2">Recommendations</div>
                  <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                    {firecrawlResult.dementia_care_analysis.recommendations.map((rec: string, idx: number) => (
                      <li key={idx}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Overview - Only show for regular analysis, not dementia care */}
          {firecrawlResult.analysis_type !== 'dementia_care_quality' && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {firecrawlResult.map_summary && (
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">URLs Found</div>
                <div className="text-2xl font-bold text-blue-700">{firecrawlResult.map_summary.total_urls_found}</div>
              </div>
            )}
            {firecrawlResult.crawl_summary && (
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Pages Crawled</div>
                <div className="text-2xl font-bold text-green-700">{firecrawlResult.crawl_summary.pages_crawled}</div>
              </div>
            )}
            {firecrawlResult.extraction_method && (
              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Method</div>
                <div className="text-sm font-bold text-purple-700 break-words">{firecrawlResult.extraction_method}</div>
              </div>
            )}
            {firecrawlResult.completeness && (
              <div className="bg-orange-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Categories Filled</div>
                <div className="text-2xl font-bold text-orange-700">
                  {Object.values(firecrawlResult.completeness).filter(Boolean).length}/{Object.keys(firecrawlResult.completeness).length}
                </div>
              </div>
            )}
            {/* Legacy fields */}
            {(firecrawlResult as any).pages_scraped !== undefined && (
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Pages Scraped</div>
                <div className="text-2xl font-bold text-blue-700">{(firecrawlResult as any).pages_scraped}</div>
              </div>
            )}
            {(firecrawlResult as any).urls_found !== undefined && (
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">URLs Found</div>
                <div className="text-2xl font-bold text-green-700">{(firecrawlResult as any).urls_found}</div>
              </div>
            )}
            {(firecrawlResult as any).total_content_length !== undefined && (
              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Content Length</div>
                <div className="text-2xl font-bold text-purple-700">
                  {((firecrawlResult as any).total_content_length / 1000).toFixed(1)}K
                </div>
              </div>
            )}
          </div>
          )}

          {/* Completeness Overview - Full Width */}
          {firecrawlResult.analysis_type !== 'dementia_care_quality' && firecrawlResult.completeness && (
            <div className="w-full border border-gray-200 rounded-lg p-6 bg-white">
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-primary" />
                Data Completeness
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
                {Object.entries(firecrawlResult.completeness).map(([category, filled]) => (
                  <div
                    key={category}
                    className={`p-3 rounded-lg text-center transition-colors ${
                      filled ? 'bg-green-100 text-green-800 border-2 border-green-300' : 'bg-gray-100 text-gray-500 border-2 border-gray-200'
                    }`}
                  >
                    <div className="text-xs font-medium capitalize mb-1">{category}</div>
                    <div className="text-xl mt-1">{filled ? '✅' : '❌'}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Structured Data - Expanded Schema - Only show for regular analysis */}
          {firecrawlResult.analysis_type !== 'dementia_care_quality' && (
            <div className="space-y-4">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Extracted Data Categories</h3>
              {(() => {
                const sd = firecrawlResult.structured_data;
                const categories: JSX.Element[] = [];
                
                // Staff
                if (sd.staff) {
                  if (sd.staff.qualifications && sd.staff.qualifications.length > 0) {
                    categories.push(
                      <div key="staff-qualifications" className="border border-gray-200 rounded-lg p-4">
                        <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                          <Users className="w-5 h-5 text-primary" />
                          Staff Qualifications
                        </h4>
                        <ul className="space-y-1">
                          {sd.staff.qualifications.map((qual, idx) => (
                            <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                              <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" />
                              <span>{qual}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    );
                  }
                  if (sd.staff.key_staff && sd.staff.key_staff.length > 0) {
                    categories.push(
                      <div key="key-staff" className="border border-gray-200 rounded-lg p-4">
                        <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                          <Users className="w-5 h-5 text-primary" />
                          Key Staff ({sd.staff.key_staff.length})
                        </h4>
                        <div className="space-y-2">
                          {sd.staff.key_staff.map((staff, idx) => (
                            <div key={idx} className="text-sm text-gray-700">
                              {staff.name && <strong>{staff.name}</strong>}
                              {staff.role && <span className="ml-2 text-gray-600">- {staff.role}</span>}
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  }
                  if (sd.staff.team_size) {
                    categories.push(
                      <div key="team-size" className="border border-gray-200 rounded-lg p-4">
                        <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                          <Users className="w-5 h-5 text-primary" />
                          Team Size
                        </h4>
                        <div className="text-sm text-gray-700">{sd.staff.team_size}</div>
                      </div>
                    );
                  }
                }
                
                // Facilities
                if (sd.facilities) {
                  const facilityItems: string[] = [];
                  if (sd.facilities.rooms) facilityItems.push(...sd.facilities.rooms);
                  if (sd.facilities.communal_areas) facilityItems.push(...sd.facilities.communal_areas);
                  if (sd.facilities.outdoor_spaces) facilityItems.push(...sd.facilities.outdoor_spaces);
                  if (sd.facilities.special_facilities) facilityItems.push(...sd.facilities.special_facilities);
                  
                  if (facilityItems.length > 0) {
                    categories.push(
                      <div key="facilities" className="border border-gray-200 rounded-lg p-4">
                        <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                          <Building className="w-5 h-5 text-primary" />
                          Facilities
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {facilityItems.map((facility, idx) => (
                            <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                              {facility}
                            </span>
                          ))}
                        </div>
                      </div>
                    );
                  }
                  if (sd.facilities.room_count || sd.facilities.capacity) {
                    categories.push(
                      <div key="facility-capacity" className="border border-gray-200 rounded-lg p-4">
                        <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                          <Building className="w-5 h-5 text-primary" />
                          Capacity
                        </h4>
                        <div className="text-sm text-gray-700">
                          {sd.facilities.room_count && <div>Rooms: {sd.facilities.room_count}</div>}
                          {sd.facilities.capacity && <div>Capacity: {sd.facilities.capacity}</div>}
                        </div>
                      </div>
                    );
                  }
                }
                
                // Care Services
                if (sd.care_services) {
                  const services: string[] = [];
                  if (sd.care_services.care_types) services.push(...sd.care_services.care_types);
                  if (sd.care_services.specializations) services.push(...sd.care_services.specializations);
                  if (sd.care_services.medical_services) services.push(...sd.care_services.medical_services);
                  
                  if (services.length > 0) {
                    categories.push(
                      <div key="care-services" className="border border-gray-200 rounded-lg p-4">
                        <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                          <Activity className="w-5 h-5 text-primary" />
                          Care Services
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {services.map((service, idx) => (
                            <span key={idx} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                              {service}
                            </span>
                          ))}
                        </div>
                      </div>
                    );
                  }
                }
                
                // Pricing
                if (sd.pricing) {
                  if (sd.pricing.weekly_rate_range) {
                    categories.push(
                      <div key="pricing" className="border border-gray-200 rounded-lg p-4">
                        <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                          <DollarSign className="w-5 h-5 text-primary" />
                          Pricing
                        </h4>
                        <div className="text-sm text-gray-700">
                          <div className="font-semibold">{sd.pricing.weekly_rate_range}</div>
                          {sd.pricing.included_services && sd.pricing.included_services.length > 0 && (
                            <div className="mt-2">
                              <div className="text-xs text-gray-600 mb-1">Included:</div>
                              <div className="flex flex-wrap gap-1">
                                {sd.pricing.included_services.map((service, idx) => (
                                  <span key={idx} className="px-2 py-0.5 bg-green-100 text-green-800 rounded text-xs">
                                    {service}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  }
                }
                
                // Activities
                if (sd.activities) {
                  const activityItems: string[] = [];
                  if (sd.activities.daily_activities) activityItems.push(...sd.activities.daily_activities);
                  if (sd.activities.therapies) activityItems.push(...sd.activities.therapies);
                  if (sd.activities.outings) activityItems.push(...sd.activities.outings);
                  
                  if (activityItems.length > 0) {
                    categories.push(
                      <div key="activities" className="border border-gray-200 rounded-lg p-4">
                        <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                          <Activity className="w-5 h-5 text-primary" />
                          Activities
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {activityItems.map((activity, idx) => (
                            <span key={idx} className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">
                              {activity}
                            </span>
                          ))}
                        </div>
                      </div>
                    );
                  }
                }
                
                // Contact
                if (sd.contact && (sd.contact.phone || sd.contact.email || sd.contact.address)) {
                  categories.push(
                    <div key="contact" className="border border-gray-200 rounded-lg p-4">
                      <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                        <Phone className="w-5 h-5 text-primary" />
                        Contact Information
                      </h4>
                      <div className="text-sm text-gray-700 space-y-1">
                        {sd.contact.phone && <div>📞 {sd.contact.phone}</div>}
                        {sd.contact.email && <div>✉️ {sd.contact.email}</div>}
                        {sd.contact.address && <div>📍 {sd.contact.address}</div>}
                      </div>
                    </div>
                  );
                }
                
                // Legacy fields (backward compatibility)
                if (sd.staff_qualifications && Array.isArray(sd.staff_qualifications) && sd.staff_qualifications.length > 0) {
                  categories.push(
                    <div key="staff-qualifications-legacy" className="border border-gray-200 rounded-lg p-4">
                      <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                        <Users className="w-5 h-5 text-primary" />
                        Staff Qualifications (Legacy)
                      </h4>
                      <ul className="space-y-1">
                        {sd.staff_qualifications.map((qual, idx) => (
                          <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                            <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" />
                            <span>{qual}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  );
                }
                if (sd.facilities && Array.isArray(sd.facilities) && sd.facilities.length > 0) {
                  categories.push(
                    <div key="facilities-legacy" className="border border-gray-200 rounded-lg p-4">
                      <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                        <Building className="w-5 h-5 text-primary" />
                        Facilities (Legacy)
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {sd.facilities.map((facility, idx) => (
                          <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                            {facility}
                          </span>
                        ))}
                      </div>
                    </div>
                  );
                }
                
                if (categories.length === 0) {
                  return (
                    <div className="border border-gray-200 rounded-lg p-6 text-center text-gray-500">
                      <AlertCircle className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                      <p>No extracted data categories found in the structured data.</p>
                      <p className="text-xs mt-2">Check the raw JSON below for available data.</p>
                    </div>
                  );
                }
                
                return (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {categories}
                  </div>
                );
              })()}
            </div>
          )}
        </div>
      )}

      {/* Pricing Results */}
      {pricingResult && (
        <div className="bg-white rounded-lg shadow p-6 space-y-6">
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <PoundSterling className="w-5 h-5 text-green-600" />
            Pricing Information
          </h2>

          {(() => {
            const p = pricingResult.pricing;
            const hasAnyPrice = 
              (p.fee_residential_from != null && p.fee_residential_from > 0) ||
              (p.fee_residential_to != null && p.fee_residential_to > 0) ||
              (p.fee_nursing_from != null && p.fee_nursing_from > 0) ||
              (p.fee_nursing_to != null && p.fee_nursing_to > 0) ||
              (p.fee_dementia_residential_from != null && p.fee_dementia_residential_from > 0) ||
              (p.fee_dementia_residential_to != null && p.fee_dementia_residential_to > 0) ||
              (p.fee_dementia_nursing_from != null && p.fee_dementia_nursing_from > 0) ||
              (p.fee_dementia_nursing_to != null && p.fee_dementia_nursing_to > 0) ||
              (p.fee_respite_from != null && p.fee_respite_from > 0) ||
              (p.fee_respite_to != null && p.fee_respite_to > 0);

            if (!hasAnyPrice && p.pricing_confidence !== undefined) {
              return (
                <div className="border border-yellow-200 rounded-lg p-6 bg-yellow-50">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertCircle className="w-5 h-5 text-yellow-600" />
                    <h3 className="font-semibold text-yellow-900">No Pricing Data Found</h3>
                  </div>
                  <p className="text-sm text-yellow-800 mb-4">
                    The extraction process completed, but no specific pricing information was found on the website.
                  </p>
                  {p.pricing_confidence !== undefined && (
                    <div className="border border-gray-200 rounded-lg p-4 bg-white">
                      <h4 className="font-semibold text-gray-900 mb-2">Extraction Confidence</h4>
                      <div className="text-2xl font-bold text-gray-700">
                        {p.pricing_confidence}%
                      </div>
                      <div className="text-xs text-gray-600 mt-1">extraction accuracy</div>
                    </div>
                  )}
                  {p.pricing_notes && (
                    <div className="mt-4 text-sm text-yellow-800">
                      <strong>Notes:</strong> {p.pricing_notes}
                    </div>
                  )}
                </div>
              );
            }

            return (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Residential Care */}
                {((p.fee_residential_from != null && p.fee_residential_from > 0) || (p.fee_residential_to != null && p.fee_residential_to > 0)) && (
                  <div className="border border-gray-200 rounded-lg p-4 bg-green-50">
                    <h3 className="font-semibold text-gray-900 mb-2">Residential Care</h3>
                    <div className="text-2xl font-bold text-green-700">
                      {p.fee_residential_from != null && p.fee_residential_from > 0 ? (
                        <>
                          £{p.fee_residential_from.toLocaleString()}
                          {p.fee_residential_to != null && p.fee_residential_to > 0 && p.fee_residential_to !== p.fee_residential_from && (
                            <> - £{p.fee_residential_to.toLocaleString()}</>
                          )}
                        </>
                      ) : p.fee_residential_to != null && p.fee_residential_to > 0 ? (
                        <>£{p.fee_residential_to.toLocaleString()}</>
                      ) : (
                        'N/A'
                      )}
                    </div>
                    <div className="text-xs text-gray-600 mt-1">per week</div>
                  </div>
                )}

                {/* Nursing Care */}
                {((p.fee_nursing_from != null && p.fee_nursing_from > 0) || (p.fee_nursing_to != null && p.fee_nursing_to > 0)) && (
                  <div className="border border-gray-200 rounded-lg p-4 bg-blue-50">
                    <h3 className="font-semibold text-gray-900 mb-2">Nursing Care</h3>
                    <div className="text-2xl font-bold text-blue-700">
                      {p.fee_nursing_from != null && p.fee_nursing_from > 0 ? (
                        <>
                          £{p.fee_nursing_from.toLocaleString()}
                          {p.fee_nursing_to != null && p.fee_nursing_to > 0 && p.fee_nursing_to !== p.fee_nursing_from && (
                            <> - £{p.fee_nursing_to.toLocaleString()}</>
                          )}
                        </>
                      ) : p.fee_nursing_to != null && p.fee_nursing_to > 0 ? (
                        <>£{p.fee_nursing_to.toLocaleString()}</>
                      ) : (
                        'N/A'
                      )}
                    </div>
                    <div className="text-xs text-gray-600 mt-1">per week</div>
                  </div>
                )}

                {/* Dementia Residential Care */}
                {((p.fee_dementia_residential_from != null && p.fee_dementia_residential_from > 0) || (p.fee_dementia_residential_to != null && p.fee_dementia_residential_to > 0)) && (
                  <div className="border border-gray-200 rounded-lg p-4 bg-purple-50">
                    <h3 className="font-semibold text-gray-900 mb-2">Dementia Residential</h3>
                    <div className="text-2xl font-bold text-purple-700">
                      {p.fee_dementia_residential_from != null && p.fee_dementia_residential_from > 0 ? (
                        <>
                          £{p.fee_dementia_residential_from.toLocaleString()}
                          {p.fee_dementia_residential_to != null && p.fee_dementia_residential_to > 0 && p.fee_dementia_residential_to !== p.fee_dementia_residential_from && (
                            <> - £{p.fee_dementia_residential_to.toLocaleString()}</>
                          )}
                        </>
                      ) : p.fee_dementia_residential_to != null && p.fee_dementia_residential_to > 0 ? (
                        <>£{p.fee_dementia_residential_to.toLocaleString()}</>
                      ) : (
                        'N/A'
                      )}
                    </div>
                    <div className="text-xs text-gray-600 mt-1">per week</div>
                  </div>
                )}

                {/* Dementia Nursing Care */}
                {((p.fee_dementia_nursing_from != null && p.fee_dementia_nursing_from > 0) || (p.fee_dementia_nursing_to != null && p.fee_dementia_nursing_to > 0)) && (
                  <div className="border border-gray-200 rounded-lg p-4 bg-indigo-50">
                    <h3 className="font-semibold text-gray-900 mb-2">Dementia Nursing</h3>
                    <div className="text-2xl font-bold text-indigo-700">
                      {p.fee_dementia_nursing_from != null && p.fee_dementia_nursing_from > 0 ? (
                        <>
                          £{p.fee_dementia_nursing_from.toLocaleString()}
                          {p.fee_dementia_nursing_to != null && p.fee_dementia_nursing_to > 0 && p.fee_dementia_nursing_to !== p.fee_dementia_nursing_from && (
                            <> - £{p.fee_dementia_nursing_to.toLocaleString()}</>
                          )}
                        </>
                      ) : p.fee_dementia_nursing_to != null && p.fee_dementia_nursing_to > 0 ? (
                        <>£{p.fee_dementia_nursing_to.toLocaleString()}</>
                      ) : (
                        'N/A'
                      )}
                    </div>
                    <div className="text-xs text-gray-600 mt-1">per week</div>
                  </div>
                )}

                {/* Respite Care */}
                {((p.fee_respite_from != null && p.fee_respite_from > 0) || (p.fee_respite_to != null && p.fee_respite_to > 0)) && (
                  <div className="border border-gray-200 rounded-lg p-4 bg-orange-50">
                    <h3 className="font-semibold text-gray-900 mb-2">Respite Care</h3>
                    <div className="text-2xl font-bold text-orange-700">
                      {p.fee_respite_from != null && p.fee_respite_from > 0 ? (
                        <>
                          £{p.fee_respite_from.toLocaleString()}
                          {p.fee_respite_to != null && p.fee_respite_to > 0 && p.fee_respite_to !== p.fee_respite_from && (
                            <> - £{p.fee_respite_to.toLocaleString()}</>
                          )}
                        </>
                      ) : p.fee_respite_to != null && p.fee_respite_to > 0 ? (
                        <>£{p.fee_respite_to.toLocaleString()}</>
                      ) : (
                        'N/A'
                      )}
                    </div>
                    <div className="text-xs text-gray-600 mt-1">per week</div>
                  </div>
                )}

                {/* Confidence Score */}
                {p.pricing_confidence !== undefined && (
                  <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                    <h3 className="font-semibold text-gray-900 mb-2">Confidence</h3>
                    <div className="text-2xl font-bold text-gray-700">
                      {p.pricing_confidence}%
                    </div>
                    <div className="text-xs text-gray-600 mt-1">extraction accuracy</div>
                  </div>
                )}
              </div>
            );
          })()}

          {/* Pricing Breakdown */}
          {pricingResult.pricing.pricing_breakdown && (
            <div className="border border-gray-200 rounded-lg p-4 bg-blue-50">
              <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <Info className="w-4 h-4" />
                What's Included & Additional Costs
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {pricingResult.pricing.pricing_breakdown.meals_included !== undefined && (
                  <div className="flex items-center gap-2">
                    {pricingResult.pricing.pricing_breakdown.meals_included ? (
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    ) : (
                      <X className="w-4 h-4 text-red-600" />
                    )}
                    <span className="text-sm text-gray-700">
                      Meals {pricingResult.pricing.pricing_breakdown.meals_included ? 'Included' : 'Not Included'}
                    </span>
                  </div>
                )}
                {pricingResult.pricing.pricing_breakdown.activities_included !== undefined && (
                  <div className="flex items-center gap-2">
                    {pricingResult.pricing.pricing_breakdown.activities_included ? (
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    ) : (
                      <X className="w-4 h-4 text-red-600" />
                    )}
                    <span className="text-sm text-gray-700">
                      Activities {pricingResult.pricing.pricing_breakdown.activities_included ? 'Included' : 'Not Included'}
                      {pricingResult.pricing.pricing_breakdown.activities_cost && (
                        <span className="text-gray-600 ml-1">(£{pricingResult.pricing.pricing_breakdown.activities_cost}/week extra)</span>
                      )}
                    </span>
                  </div>
                )}
                {pricingResult.pricing.pricing_breakdown.transport_included !== undefined && (
                  <div className="flex items-center gap-2">
                    {pricingResult.pricing.pricing_breakdown.transport_included ? (
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    ) : (
                      <X className="w-4 h-4 text-red-600" />
                    )}
                    <span className="text-sm text-gray-700">
                      Transport {pricingResult.pricing.pricing_breakdown.transport_included ? 'Included' : 'Not Included'}
                      {pricingResult.pricing.pricing_breakdown.transport_cost && (
                        <span className="text-gray-600 ml-1">(£{pricingResult.pricing.pricing_breakdown.transport_cost}/week extra)</span>
                      )}
                    </span>
                  </div>
                )}
                {pricingResult.pricing.pricing_breakdown.additional_services && pricingResult.pricing.pricing_breakdown.additional_services.length > 0 && (
                  <div className="md:col-span-2">
                    <div className="text-sm font-medium text-gray-700 mb-1">Additional Paid Services:</div>
                    <div className="flex flex-wrap gap-2">
                      {pricingResult.pricing.pricing_breakdown.additional_services.map((service, idx) => (
                        <span key={idx} className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">
                          {service}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Pricing Notes */}
          {pricingResult.pricing.pricing_notes && (
            <div className="border border-gray-200 rounded-lg p-4 bg-yellow-50">
              <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                <Info className="w-4 h-4" />
                Pricing Notes
              </h3>
              <p className="text-sm text-gray-700">{pricingResult.pricing.pricing_notes}</p>
            </div>
          )}

          {/* Metadata */}
          <div className="border-t pt-4 text-xs text-gray-500 space-y-1">
            <div>Extraction Method: {pricingResult.extraction_method}</div>
            <div>Scraped At: {new Date(pricingResult.scraped_at).toLocaleString()}</div>
            {pricingResult.postcode && <div>Postcode: {pricingResult.postcode}</div>}
            {pricingResult.pricing.currency && <div>Currency: {pricingResult.pricing.currency}</div>}
            {pricingResult.pricing.billing_period && <div>Billing Period: {pricingResult.pricing.billing_period}</div>}
          </div>
        </div>
      )}
    </div>
  );
}


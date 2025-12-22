import { useState } from 'react';
import { Calculator, DollarSign, TrendingUp, AlertCircle, CheckCircle, Heart, BookOpen, Info, MapPin, Database } from 'lucide-react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import LegalDisclaimer from '../components/LegalDisclaimer';
import FundingCalculatorGuide from '../components/FundingCalculatorGuide';
import FundingLLMInsights from '../components/FundingLLMInsights';
import LocalAuthorityContactCard from '../components/LocalAuthorityContactCard';

interface FundingResult {
  chc_eligibility: {
    probability_percent: number;
    is_likely_eligible: boolean;
    threshold_category: string;
    reasoning: string;
    key_factors?: string[];
    domain_scores?: Record<string, number>;
    bonuses_applied?: string[];
  };
  la_support: {
    top_up_probability_percent: number;
    full_support_probability_percent: number;
    capital_assessed: number;
    tariff_income_gbp_week: number;
    weekly_contribution?: number;
    is_fully_funded: boolean;
    reasoning: string;
  };
  dpa_eligibility: {
    is_eligible: boolean;
    property_disregarded: boolean;
    reasoning: string;
  };
  savings: {
    weekly_savings: number;
    annual_gbp: number;
    five_year_gbp: number;
    lifetime_gbp?: number;
  };
  recommendations?: string[];
  local_authority_contact?: {
    council_name: string;
    region?: string;
    authority_type?: string;
    asc_phone?: string | null;
    asc_email?: string | null;
    asc_website_url?: string | null;
    assessment_url?: string | null;
    office_address?: string | null;
    opening_hours?: string | null;
    emergency_phone?: string | null;
    note?: string;
  };
  llmInsights?: {
    generated_at: string;
    model: string;
    method: string;
    insights: {
      overall_explanation: {
        summary: string;
        key_findings: string[];
        confidence_level: 'high' | 'medium' | 'moderate';
      };
      chc_explanation: {
        what_it_means: string;
        eligibility_factors: string[];
        next_steps?: string[];
        important_notes?: string[];
      };
      la_funding_explanation: {
        what_it_means: string;
        means_test_summary: string;
        contribution_explanation?: string;
        tips?: string[];
      };
      dpa_explanation: {
        what_it_means: string;
        property_status: string;
        benefits?: string[];
        considerations?: string[];
      };
      expert_advice: {
        funding_strategy: string;
        maximizing_eligibility?: string[];
        common_mistakes?: string[];
        when_to_reassess?: string;
      };
      actionable_next_steps: Array<{
        step: string;
        priority: 'high' | 'medium' | 'low';
        timeline: string;
        details?: string;
      }>;
    };
  };
  _means_test_breakdown?: {
    raw_capital_assets: number;
    asset_disregards: number;
    adjusted_capital_assets: number;
    raw_weekly_income: number;
    income_disregards: number;
    adjusted_weekly_income: number;
    tariff_income: number;
    personal_expenses_allowance: number;
    minimum_income_guarantee: number;
    upper_capital_limit: number;
    lower_capital_limit: number;
  };
}

interface ErrorDetails {
  message: string;
  type: 'network' | 'server' | 'validation' | 'service' | 'unknown';
  userMessage: string;
  helpText?: string;
  canRetry: boolean;
  supportContact?: string;
}

// Helper function to safely format numbers
const safeToFixed = (value: number | null | undefined, decimals: number = 2): string => {
  if (value === null || value === undefined || isNaN(value)) {
    return '0.00';
  }
  return value.toFixed(decimals);
};

// Helper function to safely format numbers with locale
const safeToLocaleString = (value: number | null | undefined): string => {
  if (value === null || value === undefined || isNaN(value)) {
    return '0';
  }
  return value.toLocaleString();
};

export default function FundingCalculator() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<FundingResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [errorDetails, setErrorDetails] = useState<ErrorDetails | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [laLookupLoading, setLaLookupLoading] = useState(false);
  const [previewLaContact, setPreviewLaContact] = useState<FundingResult['local_authority_contact'] | null>(null);
  const [dataSourcesContent, setDataSourcesContent] = useState<string | null>(null);
  const [showDataSources, setShowDataSources] = useState(false);
  const [loadingDataSources, setLoadingDataSources] = useState(false);

  const [formData, setFormData] = useState({
    age: 80,
    has_primary_health_need: false,
    requires_nursing_care: false,
    has_dementia: false,
    capital_assets: 0,
    weekly_income: 0,
    care_cost_per_week: 1200,
    care_type: 'residential',
    postcode: '',
    has_property: false,
    property_value: 0,
    is_main_residence: true,
    has_qualifying_relative: false,
    has_partner_residing: false,
    has_relative_60plus_residing: false,
    has_incapacitated_relative: false,
    has_child_under_18: false,
    has_third_party_occupation: false,
    third_party_occupation_details: '',
    // 12 DST Domains
    domain_breathing: 'no',
    domain_nutrition: 'no',
    domain_continence: 'no',
    domain_skin: 'no',
    domain_mobility: 'no',
    domain_communication: 'no',
    domain_psychological: 'no',
    domain_cognition: 'no',
    domain_behaviour: 'no',
    domain_drug_therapies: 'no',
    domain_altered_states: 'no',
    domain_other: 'no',
    // Complex therapies
    has_peg_feeding: false,
    has_tracheostomy: false,
    requires_injections: false,
    requires_ventilator: false,
    requires_dialysis: false,
    // Unpredictability indicators
    has_unpredictable_needs: false,
    has_fluctuating_condition: false,
    has_high_risk_behaviours: false,
    // Income disregards - Fully disregarded (100%)
    income_dla_mobility: 0,
    income_pip_mobility: 0,
    income_war_disablement_pension: 0,
    income_war_widow_pension: 0,
    income_afip: 0,
    income_afcs_guaranteed: 0,
    income_earnings: 0,
    income_direct_payments: 0,
    income_child_benefit: 0,
    income_child_tax_credit: 0,
    income_housing_benefit: 0,
    income_council_tax_reduction: 0,
    income_winter_fuel_payment: 0,
    // Income disregards - Partially disregarded or with DRE
    income_attendance_allowance: 0,
    income_pip_daily_living: 0,
    income_dla_care: 0,
    income_constant_attendance_allowance: 0,
    income_savings_credit: 0,
    // Disability-Related Expenditure (DRE)
    disability_related_expenditure: 0,
    // Asset disregards - Mandatory (fully disregarded)
    asset_personal_possessions: 0,
    asset_life_insurance: 0,
    asset_investment_bonds_life: 0,
    asset_personal_injury_trust: 0,
    asset_personal_injury_compensation: 0,
    asset_infected_blood_compensation: 0,
    // Asset disregards - Discretionary
    asset_business_assets: 0,
    // Temporary disregards
    weeks_in_care: 0,
    personal_injury_compensation_weeks: 0,
  });

  // Enhanced error handling function
  const handleError = (err: any, context: string = 'calculation'): ErrorDetails => {
    // Log error for debugging
    console.error(`[Funding Calculator Error] ${context}:`, {
      message: err.message,
      code: err.code,
      status: err.response?.status,
      statusText: err.response?.statusText,
      data: err.response?.data,
      stack: err.stack,
      timestamp: new Date().toISOString(),
    });

    // Network errors
    if (err.code === 'ERR_NETWORK' || err.message === 'Network Error' || !err.response) {
      return {
        message: err.message || 'Network error',
        type: 'network',
        userMessage: 'Unable to connect to the server',
        helpText: 'Please check your internet connection and try again. If the problem persists, the server may be temporarily unavailable.',
        canRetry: true,
        supportContact: 'support@rightcarehome.co.uk',
      };
    }

    // Connection refused
    if (err.code === 'ECONNREFUSED' || err.message?.includes('ERR_CONNECTION_REFUSED')) {
      return {
        message: err.message || 'Connection refused',
        type: 'network',
        userMessage: 'Server is not responding',
        helpText: 'The backend server appears to be offline. Please try again in a few moments, or contact support if the issue continues.',
        canRetry: true,
        supportContact: 'support@rightcarehome.co.uk',
      };
    }

    // Timeout errors
    if (err.code === 'ETIMEDOUT' || err.message?.includes('timeout') || err.response?.status === 408) {
      return {
        message: err.message || 'Request timeout',
        type: 'network',
        userMessage: 'Request took too long to complete',
        helpText: 'The calculation is taking longer than expected. This may happen during high traffic. Please try again.',
        canRetry: true,
        supportContact: 'support@rightcarehome.co.uk',
      };
    }

    // Service unavailable (503)
    if (err.response?.status === 503 || err.response?.data?.detail?.includes('not available')) {
      return {
        message: err.response?.data?.detail || 'Service unavailable',
        type: 'service',
        userMessage: 'Funding calculator service is temporarily unavailable',
        helpText: 'The funding calculator module is currently being updated or is experiencing issues. Please try again in a few minutes.',
        canRetry: true,
        supportContact: 'support@rightcarehome.co.uk',
      };
    }

    // Not found (404)
    if (err.response?.status === 404) {
      return {
        message: err.response?.data?.detail || 'Endpoint not found',
        type: 'server',
        userMessage: 'The requested service could not be found',
        helpText: 'This appears to be a configuration issue. Please contact support with this error message.',
        canRetry: false,
        supportContact: 'support@rightcarehome.co.uk',
      };
    }

    // Validation errors (400)
    if (err.response?.status === 400) {
      const detail = err.response?.data?.detail || err.response?.data?.message || 'Invalid request';
      return {
        message: detail,
        type: 'validation',
        userMessage: 'Please check your input values',
        helpText: 'Some of the information you entered may be invalid. Please review your entries, especially financial amounts and domain assessments.',
        canRetry: false,
        supportContact: 'support@rightcarehome.co.uk',
      };
    }

    // Server errors (500, 502, 504)
    if ([500, 502, 504].includes(err.response?.status || 0)) {
      return {
        message: err.response?.data?.detail || 'Server error',
        type: 'server',
        userMessage: 'An error occurred on our server',
        helpText: 'We encountered an unexpected error while processing your request. Our team has been notified. Please try again in a few moments.',
        canRetry: true,
        supportContact: 'support@rightcarehome.co.uk',
      };
    }

    // Rate limiting (429)
    if (err.response?.status === 429) {
      return {
        message: 'Too many requests',
        type: 'service',
        userMessage: 'Too many requests. Please wait a moment',
        helpText: 'You have made too many requests in a short time. Please wait a few minutes before trying again.',
        canRetry: true,
        supportContact: 'support@rightcarehome.co.uk',
      };
    }

    // Unknown error
    const errorMessage = err.response?.data?.detail || err.response?.data?.message || err.message || 'An unexpected error occurred';
    return {
      message: errorMessage,
      type: 'unknown',
      userMessage: 'Something went wrong',
      helpText: 'We encountered an unexpected error. Please try again, or contact support if the problem persists.',
      canRetry: true,
      supportContact: 'support@rightcarehome.co.uk',
    };
  };

  // Retry logic with exponential backoff
  const retryRequest = async (requestData: any, maxRetries: number = 3): Promise<any> => {
    let lastError: any = null;
    
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        if (attempt > 0) {
          // Exponential backoff: 1s, 2s, 4s
          const delay = Math.pow(2, attempt - 1) * 1000;
          await new Promise(resolve => setTimeout(resolve, delay));
        }
        
        const response = await axios.post('/api/rch-data/funding/calculate', requestData, {
          timeout: 40000, // 40 second timeout (backend has 30s timeout for calculation)
        });
        
        // Debug: Log response structure
        console.log('🔍 [Funding Calculator] Response received:', {
          status: response.status,
          headers: response.headers,
          dataKeys: Object.keys(response.data || {}),
          hasLlmInsights: 'llmInsights' in (response.data || {}),
          llmInsightsType: typeof (response.data || {}).llmInsights,
          llmInsightsLength: (response.data || {}).llmInsights ? Object.keys((response.data || {}).llmInsights).length : 0,
        });
        
        // Ensure llmInsights is returned as-is
        const rawData = response.data;
        console.log('🔍 [Funding Calculator] Raw data llmInsights:', rawData.llmInsights ? 'PRESENT' : 'MISSING');
        
        return rawData;
      } catch (err: any) {
        lastError = err;
        const errorInfo = handleError(err, `attempt ${attempt + 1}`);
        
        // Don't retry on validation errors or 404
        if (!errorInfo.canRetry || err.response?.status === 400 || err.response?.status === 404) {
          throw err;
        }
        
        // Log retry attempt
        console.warn(`[Funding Calculator] Retry attempt ${attempt + 1}/${maxRetries}`, errorInfo);
      }
    }
    
    throw lastError;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setErrorDetails(null);
    setResult(null);
    setRetryCount(0);

    try {
      // Build domain assessments for all 12 DST domains
      const domain_assessments: Record<string, any> = {};
      
      const domainMapping: Record<string, string> = {
        domain_breathing: 'breathing',
        domain_nutrition: 'nutrition',
        domain_continence: 'continence',
        domain_skin: 'skin',
        domain_mobility: 'mobility',
        domain_communication: 'communication',
        domain_psychological: 'psychological',
        domain_cognition: 'cognition',
        domain_behaviour: 'behaviour',
        domain_drug_therapies: 'drug_therapies',
        domain_altered_states: 'altered_states',
        domain_other: 'other',
      };
      
      const domainDescriptions: Record<string, string> = {
        breathing: 'Breathing difficulties and respiratory needs',
        nutrition: 'Nutritional needs and eating difficulties',
        continence: 'Continence management needs',
        skin: 'Skin integrity and pressure care needs',
        mobility: 'Mobility and movement needs',
        communication: 'Communication needs',
        psychological: 'Psychological and emotional needs',
        cognition: 'Cognitive needs and mental capacity',
        behaviour: 'Behavioural challenges',
        drug_therapies: 'Medication and drug therapy needs',
        altered_states: 'Altered states of consciousness',
        other: 'Other significant care needs',
      };
      
      for (const [formKey, domainKey] of Object.entries(domainMapping)) {
        const level = formData[formKey as keyof typeof formData] as string;
        if (level && level !== 'no') {
          domain_assessments[domainKey.toUpperCase()] = {
            level: level.toUpperCase(),
            description: domainDescriptions[domainKey] || `${domainKey} needs`,
          };
        }
      }

      // Calculate adjusted capital assets (after disregards)
      const adjusted_capital_assets = Math.max(0, 
        formData.capital_assets - 
        (formData.asset_personal_possessions || 0) - 
        (formData.asset_life_insurance || 0) - 
        (formData.asset_business_assets || 0)
      );
      
      // Income disregards are now handled in the backend calculation
      // We send all income disregards separately for proper calculation
      
      const requestData = {
        age: formData.age,
        domain_assessments,
        has_primary_health_need: formData.has_primary_health_need,
        requires_nursing_care: formData.requires_nursing_care,
        has_peg_feeding: formData.has_peg_feeding,
        has_tracheostomy: formData.has_tracheostomy,
        requires_injections: formData.requires_injections,
        requires_ventilator: formData.requires_ventilator,
        requires_dialysis: formData.requires_dialysis,
        has_unpredictable_needs: formData.has_unpredictable_needs,
        has_fluctuating_condition: formData.has_fluctuating_condition,
        has_high_risk_behaviours: formData.has_high_risk_behaviours,
        capital_assets: formData.capital_assets, // Base capital before disregards
        weekly_income: formData.weekly_income, // Base income before disregards
        care_type: formData.care_type,
        is_permanent_care: true,
        postcode: formData.postcode || undefined,
        property: formData.has_property
          ? {
              value: formData.property_value,
              is_main_residence: formData.is_main_residence,
              has_qualifying_relative: formData.has_qualifying_relative,
              has_partner_residing: formData.has_partner_residing || false,
              has_relative_60plus_residing: formData.has_relative_60plus_residing || false,
              has_incapacitated_relative: formData.has_incapacitated_relative || false,
              has_child_under_18: formData.has_child_under_18 || false,
              is_non_residential_care: formData.care_type === 'residential' ? false : true, // Non-residential care if not residential
              has_third_party_occupation: formData.has_third_party_occupation || false,
              third_party_occupation_details: formData.third_party_occupation_details || null,
            }
          : null,
        // Asset disregards - Mandatory
        asset_personal_possessions: formData.asset_personal_possessions || 0,
        asset_life_insurance: formData.asset_life_insurance || 0,
        asset_investment_bonds_life: formData.asset_investment_bonds_life || 0,
        asset_personal_injury_trust: formData.asset_personal_injury_trust || 0,
        asset_personal_injury_compensation: formData.asset_personal_injury_compensation || 0,
        asset_infected_blood_compensation: formData.asset_infected_blood_compensation || 0,
        // Asset disregards - Discretionary
        asset_business_assets: formData.asset_business_assets || 0,
        // Temporary disregards
        weeks_in_care: formData.weeks_in_care || 0,
        personal_injury_compensation_weeks: formData.personal_injury_compensation_weeks || 0,
        // Income disregards - Fully disregarded
        income_dla_mobility: formData.income_dla_mobility || 0,
        income_pip_mobility: formData.income_pip_mobility || 0,
        income_war_disablement_pension: formData.income_war_disablement_pension || 0,
        income_war_widow_pension: formData.income_war_widow_pension || 0,
        income_afip: formData.income_afip || 0,
        income_afcs_guaranteed: formData.income_afcs_guaranteed || 0,
        income_earnings: formData.income_earnings || 0,
        income_direct_payments: formData.income_direct_payments || 0,
        income_child_benefit: formData.income_child_benefit || 0,
        income_child_tax_credit: formData.income_child_tax_credit || 0,
        income_housing_benefit: formData.income_housing_benefit || 0,
        income_council_tax_reduction: formData.income_council_tax_reduction || 0,
        income_winter_fuel_payment: formData.income_winter_fuel_payment || 0,
        // Income disregards - Partially disregarded or with DRE
        income_attendance_allowance: formData.income_attendance_allowance || 0,
        income_pip_daily_living: formData.income_pip_daily_living || 0,
        income_dla_care: formData.income_dla_care || 0,
        income_constant_attendance_allowance: formData.income_constant_attendance_allowance || 0,
        income_savings_credit: formData.income_savings_credit || 0,
        // Disability-Related Expenditure
        disability_related_expenditure: formData.disability_related_expenditure || 0,
        // Include raw values for display
        _raw_capital_assets: formData.capital_assets,
        _raw_weekly_income: formData.weekly_income,
        _asset_disregards: formData.asset_personal_possessions + formData.asset_life_insurance + formData.asset_business_assets,
      };

      // Use retry logic for network/server errors
      const resultData = await retryRequest(requestData);
      
      // CRITICAL DEBUG: Log the raw response before any modifications
      console.log('🔍 [CRITICAL] Raw resultData immediately after API call:', {
        hasLlmInsights: 'llmInsights' in resultData,
        allKeys: Object.keys(resultData),
        llmInsightsValue: resultData.llmInsights,
      });
      
      // Add means test breakdown for display
      if (resultData.la_support) {
        resultData._means_test_breakdown = {
          raw_capital_assets: requestData._raw_capital_assets || requestData.capital_assets,
          asset_disregards: requestData._asset_disregards || 0,
          adjusted_capital_assets: requestData.capital_assets,
          raw_weekly_income: requestData._raw_weekly_income || requestData.weekly_income,
          income_disregards: requestData._income_disregards || 0,
          adjusted_weekly_income: requestData.weekly_income,
          tariff_income: resultData.la_support.tariff_income_gbp_week || 0,
          personal_expenses_allowance: 28.25, // 2025-2026
          minimum_income_guarantee: 189.60, // 2025-2026
          upper_capital_limit: 23250,
          lower_capital_limit: 14250,
        };
      }
      
      // Debug: Log LLM insights if present
      console.log('🔍 [DEBUG] After modifications, before setState:', {
        hasLlmInsights: 'llmInsights' in resultData,
        allKeys: Object.keys(resultData),
      });
      
      if (resultData.llmInsights) {
        console.log('✅ LLM Insights received:', resultData.llmInsights);
      } else {
        console.log('⚠️ No LLM Insights in response. Available keys:', Object.keys(resultData));
      }
      
      // Create a fresh copy with all properties to ensure nothing is lost
      const resultToSet = { ...resultData };
      console.log('🔍 [FINAL] About to setState with resultToSet:', {
        hasLlmInsights: 'llmInsights' in resultToSet,
        resultDataHasIt: 'llmInsights' in resultData,
        isSameObject: resultToSet === resultData,
      });
      
      setResult(resultToSet);
      setRetryCount(0); // Reset retry count on success
    } catch (err: any) {
      const errorInfo = handleError(err, 'funding calculation');
      setError(errorInfo.userMessage);
      setErrorDetails(errorInfo);
      setRetryCount(prev => prev + 1);
    } finally {
      setLoading(false);
    }
  };

  const [showGuide, setShowGuide] = useState(false);

  // Lookup Local Authority by postcode
  const lookupLocalAuthority = async (postcode: string) => {
    if (!postcode || postcode.trim().length < 5) {
      return;
    }

    setLaLookupLoading(true);
    try {
      const response = await axios.get(`/api/rch-data/funding/la/${encodeURIComponent(postcode.trim())}`);
      if (response.data && response.data.local_authority) {
        setPreviewLaContact(response.data.local_authority);
      }
    } catch (err: any) {
      console.warn('LA lookup failed:', err);
      // Don't show error to user - it's optional
      setPreviewLaContact(null);
    } finally {
      setLaLookupLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Heart className="w-8 h-8" />
            <h1 className="text-3xl font-bold text-gray-900">
              Funding Eligibility Calculator
            </h1>
          </div>
          <button
            onClick={() => setShowGuide(!showGuide)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <BookOpen className="w-5 h-5" />
            {showGuide ? 'Hide Guide' : 'Show Guide'}
          </button>
        </div>
        <p className="mt-2 text-gray-600">
          Advanced CHC & LA Funding Assessment Tool (2025-2026)
        </p>
        <div className="mt-3 bg-blue-50 border border-blue-200 rounded-lg p-3">
          <p className="text-sm text-blue-800">
            <strong>⚠️ Important:</strong> This calculator provides estimates only. Actual eligibility is determined by official NHS and Local Authority assessments. 
            <a href="#disclaimer" className="ml-1 underline hover:text-blue-900">See full disclaimer below</a>.
          </p>
        </div>
      </div>

      {/* Guide Section */}
      {showGuide && (
        <div className="mb-6">
          <FundingCalculatorGuide />
        </div>
      )}

      {error && errorDetails && (
        <div className={`rounded-lg p-4 border ${
          errorDetails.type === 'network' ? 'bg-yellow-50 border-yellow-200' :
          errorDetails.type === 'validation' ? 'bg-orange-50 border-orange-200' :
          errorDetails.type === 'server' ? 'bg-red-50 border-red-200' :
          'bg-red-50 border-red-200'
        }`}>
          <div className="flex items-start gap-3">
            <AlertCircle className={`w-5 h-5 flex-shrink-0 mt-0.5 ${
              errorDetails.type === 'network' ? 'text-yellow-600' :
              errorDetails.type === 'validation' ? 'text-orange-600' :
              'text-red-600'
            }`} />
            <div className="flex-1">
              <div className={`font-semibold mb-1 ${
                errorDetails.type === 'network' ? 'text-yellow-800' :
                errorDetails.type === 'validation' ? 'text-orange-800' :
                'text-red-800'
              }`}>
                {error}
              </div>
              {errorDetails.helpText && (
                <div className={`text-sm mb-3 ${
                  errorDetails.type === 'network' ? 'text-yellow-700' :
                  errorDetails.type === 'validation' ? 'text-orange-700' :
                  'text-red-700'
                }`}>
                  {errorDetails.helpText}
                </div>
              )}
              <div className="flex flex-wrap gap-2 items-center">
                {errorDetails.canRetry && (
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      handleSubmit(e);
                    }}
                    disabled={loading}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
                  >
                    {loading ? 'Retrying...' : 'Try Again'}
                  </button>
                )}
                {errorDetails.supportContact && (
                  <a
                    href={`mailto:${errorDetails.supportContact}?subject=Funding Calculator Error&body=Error Type: ${errorDetails.type}%0D%0AError Message: ${errorDetails.message}%0D%0ATimestamp: ${new Date().toISOString()}`}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm font-medium"
                  >
                    Contact Support
                  </a>
                )}
              </div>
              {retryCount > 0 && (
                <div className="mt-2 text-xs text-gray-500">
                  Retry attempts: {retryCount}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Age</label>
              <input
                type="number"
                min="0"
                max="120"
                value={formData.age}
                onChange={(e) => setFormData({ ...formData, age: parseInt(e.target.value) || 0 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Care Type</label>
              <select
                value={formData.care_type}
                onChange={(e) => setFormData({ ...formData, care_type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="residential">Residential</option>
                <option value="nursing">Nursing</option>
                <option value="residential_dementia">Residential Dementia</option>
                <option value="nursing_dementia">Nursing Dementia</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Capital Assets (GBP)
              </label>
              <input
                type="number"
                min="0"
                step="1000"
                value={formData.capital_assets}
                onChange={(e) =>
                  setFormData({ ...formData, capital_assets: parseFloat(e.target.value) || 0 })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Weekly Income (GBP)
              </label>
              <input
                type="number"
                min="0"
                step="10"
                value={formData.weekly_income}
                onChange={(e) =>
                  setFormData({ ...formData, weekly_income: parseFloat(e.target.value) || 0 })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Postcode (Optional)
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={formData.postcode}
                  onChange={(e) => {
                    setFormData({ ...formData, postcode: e.target.value });
                    setPreviewLaContact(null); // Clear preview when postcode changes
                  }}
                  onBlur={async (e) => {
                    // Auto-lookup LA when user leaves the field (if postcode is valid)
                    const postcode = e.target.value.trim();
                    if (postcode && postcode.length >= 5) {
                      await lookupLocalAuthority(postcode);
                    }
                  }}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="e.g., B15 2HQ"
                />
                <button
                  type="button"
                  onClick={() => formData.postcode && lookupLocalAuthority(formData.postcode)}
                  disabled={laLookupLoading || !formData.postcode}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
                  title="Lookup Local Authority contact information"
                >
                  {laLookupLoading ? '...' : 'Find LA'}
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Enter your postcode to see your Local Authority contact information
              </p>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="has_primary_health_need"
                checked={formData.has_primary_health_need}
                onChange={(e) =>
                  setFormData({ ...formData, has_primary_health_need: e.target.checked })
                }
                className="w-4 h-4"
              />
              <label htmlFor="has_primary_health_need" className="text-sm text-gray-700">
                Has Primary Health Need
              </label>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="requires_nursing_care"
                checked={formData.requires_nursing_care}
                onChange={(e) =>
                  setFormData({ ...formData, requires_nursing_care: e.target.checked })
                }
                className="w-4 h-4"
              />
              <label htmlFor="requires_nursing_care" className="text-sm text-gray-700">
                Requires Nursing Care
              </label>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="has_property"
                checked={formData.has_property}
                onChange={(e) => setFormData({ ...formData, has_property: e.target.checked })}
                className="w-4 h-4"
              />
              <label htmlFor="has_property" className="text-sm text-gray-700">
                Has Property
              </label>
            </div>
          </div>

          {formData.has_property && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 border-t pt-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Property Value (GBP)
                </label>
                <input
                  type="number"
                  min="0"
                  step="10000"
                  value={formData.property_value}
                  onChange={(e) =>
                    setFormData({ ...formData, property_value: parseFloat(e.target.value) || 0 })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>

              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="is_main_residence"
                    checked={formData.is_main_residence}
                    onChange={(e) =>
                      setFormData({ ...formData, is_main_residence: e.target.checked })
                    }
                    className="w-4 h-4"
                  />
                  <label htmlFor="is_main_residence" className="text-sm text-gray-700">
                    Is Main Residence
                  </label>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="has_qualifying_relative"
                    checked={formData.has_qualifying_relative}
                    onChange={(e) =>
                      setFormData({ ...formData, has_qualifying_relative: e.target.checked })
                    }
                    className="w-4 h-4"
                  />
                  <label htmlFor="has_qualifying_relative" className="text-sm text-gray-700">
                    Has Qualifying Relative (60+) Living There
                  </label>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="has_partner_residing"
                    checked={formData.has_partner_residing}
                    onChange={(e) =>
                      setFormData({ ...formData, has_partner_residing: e.target.checked })
                    }
                    className="w-4 h-4"
                  />
                  <label htmlFor="has_partner_residing" className="text-sm text-gray-700">
                    Has Partner/Spouse Residing
                  </label>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="has_relative_60plus_residing"
                    checked={formData.has_relative_60plus_residing}
                    onChange={(e) =>
                      setFormData({ ...formData, has_relative_60plus_residing: e.target.checked })
                    }
                    className="w-4 h-4"
                  />
                  <label htmlFor="has_relative_60plus_residing" className="text-sm text-gray-700">
                    Has Relative 60+ Residing (lived there before care)
                  </label>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="has_incapacitated_relative"
                    checked={formData.has_incapacitated_relative}
                    onChange={(e) =>
                      setFormData({ ...formData, has_incapacitated_relative: e.target.checked })
                    }
                    className="w-4 h-4"
                  />
                  <label htmlFor="has_incapacitated_relative" className="text-sm text-gray-700">
                    Has Incapacitated Relative (AA/DLA/PIP) Residing
                  </label>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="has_child_under_18"
                    checked={formData.has_child_under_18}
                    onChange={(e) =>
                      setFormData({ ...formData, has_child_under_18: e.target.checked })
                    }
                    className="w-4 h-4"
                  />
                  <label htmlFor="has_child_under_18" className="text-sm text-gray-700">
                    Has Child Under 18 Residing
                  </label>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="has_third_party_occupation"
                    checked={formData.has_third_party_occupation}
                    onChange={(e) =>
                      setFormData({ ...formData, has_third_party_occupation: e.target.checked })
                    }
                    className="w-4 h-4"
                  />
                  <label htmlFor="has_third_party_occupation" className="text-sm text-gray-700">
                    Has Third Party Occupation (discretionary)
                  </label>
                </div>
              </div>
              
              {formData.has_third_party_occupation && (
                <div className="mt-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Third Party Occupation Details
                  </label>
                  <textarea
                    value={formData.third_party_occupation_details || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, third_party_occupation_details: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    placeholder="Describe the third party occupation (e.g., friend/carer with no other home)"
                    rows={2}
                  />
                </div>
              )}
            </div>
          )}

          {/* 12 DST Domains Section */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold mb-4">DST Domain Assessments (12 Domains)</h3>
            <p className="text-sm text-gray-600 mb-4">
              Assess each domain based on NHS Decision Support Tool (DST) 2025 framework
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[
                { key: 'domain_breathing', label: 'Breathing', desc: 'Respiratory needs' },
                { key: 'domain_nutrition', label: 'Nutrition', desc: 'Eating and nutritional needs' },
                { key: 'domain_continence', label: 'Continence', desc: 'Bladder and bowel management' },
                { key: 'domain_skin', label: 'Skin Integrity', desc: 'Pressure care and skin health' },
                { key: 'domain_mobility', label: 'Mobility', desc: 'Movement and positioning' },
                { key: 'domain_communication', label: 'Communication', desc: 'Speech and communication' },
                { key: 'domain_psychological', label: 'Psychological', desc: 'Emotional and mental health' },
                { key: 'domain_cognition', label: 'Cognition', desc: 'Memory and mental capacity' },
                { key: 'domain_behaviour', label: 'Behaviour', desc: 'Challenging behaviours' },
                { key: 'domain_drug_therapies', label: 'Drug Therapies', desc: 'Medication management' },
                { key: 'domain_altered_states', label: 'Altered States', desc: 'Consciousness changes' },
                { key: 'domain_other', label: 'Other Needs', desc: 'Other significant care needs' },
              ].map(({ key, label, desc }) => (
                <div key={key}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                  <p className="text-xs text-gray-500 mb-2">{desc}</p>
                  <select
                    value={formData[key as keyof typeof formData] as string}
                    onChange={(e) => setFormData({ ...formData, [key]: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  >
                    <option value="no">No Needs</option>
                    <option value="low">Low</option>
                    <option value="moderate">Moderate</option>
                    <option value="high">High</option>
                    <option value="severe">Severe</option>
                    <option value="priority">Priority</option>
                  </select>
                </div>
              ))}
            </div>
          </div>

          {/* Complex Therapies Section */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold mb-4">Complex Therapies</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                { key: 'has_peg_feeding', label: 'PEG/PEJ/NJ Feeding', desc: 'Tube feeding required' },
                { key: 'has_tracheostomy', label: 'Tracheostomy', desc: 'Tracheostomy in place' },
                { key: 'requires_injections', label: 'Regular Injections', desc: 'Requires regular injections' },
                { key: 'requires_ventilator', label: 'Ventilator Support', desc: 'CPAP/BiPAP or ventilator' },
                { key: 'requires_dialysis', label: 'Dialysis', desc: 'Requires dialysis treatment' },
              ].map(({ key, label, desc }) => (
                <div key={key} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id={key}
                    checked={formData[key as keyof typeof formData] as boolean}
                    onChange={(e) =>
                      setFormData({ ...formData, [key]: e.target.checked })
                    }
                    className="w-4 h-4"
                  />
                  <div>
                    <label htmlFor={key} className="text-sm font-medium text-gray-700">
                      {label}
                    </label>
                    <p className="text-xs text-gray-500">{desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Unpredictability Indicators Section */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold mb-4">Unpredictability Indicators</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { key: 'has_unpredictable_needs', label: 'Unpredictable Needs', desc: 'Needs change unpredictably' },
                { key: 'has_fluctuating_condition', label: 'Fluctuating Condition', desc: 'Condition varies significantly' },
                { key: 'has_high_risk_behaviours', label: 'High Risk Behaviours', desc: 'High risk of harm' },
              ].map(({ key, label, desc }) => (
                <div key={key} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id={key}
                    checked={formData[key as keyof typeof formData] as boolean}
                    onChange={(e) =>
                      setFormData({ ...formData, [key]: e.target.checked })
                    }
                    className="w-4 h-4"
                  />
                  <div>
                    <label htmlFor={key} className="text-sm font-medium text-gray-700">
                      {label}
                    </label>
                    <p className="text-xs text-gray-500">{desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Income Disregards Section */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold mb-4">Income Disregards</h3>
            <p className="text-sm text-gray-600 mb-4">
              Enter any income that should be disregarded from the means test calculation. Fully disregarded income is not counted at all. Partially disregarded income may be counted after deductions.
            </p>
            
            <h4 className="text-md font-semibold mt-4 mb-3 text-green-700">Fully Disregarded (100% - Not Counted)</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[
                { key: 'income_dla_mobility', label: 'DLA Mobility Component', desc: 'Disability Living Allowance Mobility (standard/enhanced)' },
                { key: 'income_pip_mobility', label: 'PIP Mobility Component', desc: 'Personal Independence Payment Mobility (standard/enhanced)' },
                { key: 'income_war_disablement_pension', label: 'War Disablement Pension', desc: 'War Pension Scheme payments (except Constant Attendance)' },
                { key: 'income_war_widow_pension', label: 'War Widow/Widower Pension', desc: 'Special payments to war widows/widowers' },
                { key: 'income_afip', label: 'Armed Forces Independence Payment', desc: 'AFIP for veterans with GIP Bands A-C' },
                { key: 'income_afcs_guaranteed', label: 'Guaranteed Income Payments (AFCS)', desc: 'Payments under Armed Forces Compensation Scheme' },
                { key: 'income_earnings', label: 'Earnings from Employment', desc: 'All employed and self-employed earnings' },
                { key: 'income_direct_payments', label: 'Direct Payments', desc: 'Direct payments from Local Authority' },
                { key: 'income_child_benefit', label: 'Child Benefit', desc: 'Child Benefit payments' },
                { key: 'income_child_tax_credit', label: 'Child Tax Credit', desc: 'Child Tax Credit payments' },
                { key: 'income_housing_benefit', label: 'Housing Benefit', desc: 'Housing Benefit payments' },
                { key: 'income_council_tax_reduction', label: 'Council Tax Reduction', desc: 'Council Tax Reduction payments' },
                { key: 'income_winter_fuel_payment', label: 'Winter Fuel Payments', desc: 'Winter Fuel Payment' },
              ].map((item) => (
                <div key={item.key}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {item.label} (£/week)
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={(formData as any)[item.key] || 0}
                    onChange={(e) => setFormData({ ...formData, [item.key]: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                  <p className="text-xs text-gray-500 mt-1">{item.desc}</p>
                </div>
              ))}
            </div>
            
            <h4 className="text-md font-semibold mt-6 mb-3 text-amber-700">Partially Disregarded (DRE Deductions Apply)</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                { key: 'income_attendance_allowance', label: 'Attendance Allowance', desc: 'Included as assessable income but DRE must be deducted' },
                { key: 'income_pip_daily_living', label: 'PIP Daily Living Component', desc: 'Included as assessable income with DRE deductions' },
                { key: 'income_dla_care', label: 'DLA Care Component', desc: 'Included as assessable income with DRE deductions' },
                { key: 'income_constant_attendance_allowance', label: 'Constant Attendance Allowance', desc: 'Not disregarded for care home residents' },
                { key: 'income_savings_credit', label: 'Savings Credit (Pension Credit)', desc: 'Partial disregard: £6.95/week single, £10.40/week couple' },
              ].map((item) => (
                <div key={item.key}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {item.label} (£/week)
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={(formData as any)[item.key] || 0}
                    onChange={(e) => setFormData({ ...formData, [item.key]: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                  <p className="text-xs text-gray-500 mt-1">{item.desc}</p>
                </div>
              ))}
            </div>
            
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Disability-Related Expenditure (DRE) (£/week)
              </label>
              <input
                type="number"
                min="0"
                step="0.01"
                value={formData.disability_related_expenditure || 0}
                onChange={(e) => setFormData({ ...formData, disability_related_expenditure: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
              <p className="text-xs text-gray-500 mt-1">
                DRE is deducted from assessable disability benefits (Attendance Allowance, PIP Daily Living, DLA Care)
              </p>
            </div>
          </div>

          {/* Asset Disregards Section */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold mb-4">Asset Disregards</h3>
            <p className="text-sm text-gray-600 mb-4">
              Enter any assets that should be disregarded from the capital assessment. Mandatory disregards are always excluded. Discretionary disregards depend on Local Authority discretion.
            </p>
            
            <h4 className="text-md font-semibold mt-4 mb-3 text-green-700">Mandatory Disregards (Always Excluded)</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[
                { key: 'asset_personal_possessions', label: 'Personal Possessions', desc: 'Furniture, clothing, jewelry, etc.' },
                { key: 'asset_life_insurance', label: 'Life Insurance Surrender Value', desc: 'Surrender value of any life insurance policy' },
                { key: 'asset_investment_bonds_life', label: 'Investment Bonds with Life Element', desc: 'Bonds with cashing-in rights via surrender' },
                { key: 'asset_personal_injury_trust', label: 'Personal Injury Trust', desc: 'Must be held in trust or administered by court' },
                { key: 'asset_infected_blood_compensation', label: 'Infected Blood Compensation', desc: 'IBCA, Macfarlane Trust, Eileen Trust, Skipton Fund, Caxton Foundation' },
              ].map((item) => (
                <div key={item.key}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {item.label} (£)
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="100"
                    value={(formData as any)[item.key] || 0}
                    onChange={(e) => setFormData({ ...formData, [item.key]: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                  <p className="text-xs text-gray-500 mt-1">{item.desc}</p>
                </div>
              ))}
            </div>
            
            <h4 className="text-md font-semibold mt-6 mb-3 text-amber-700">Temporary Disregards</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Personal Injury Compensation (£)
                </label>
                <input
                  type="number"
                  min="0"
                  step="100"
                  value={formData.asset_personal_injury_compensation || 0}
                  onChange={(e) => setFormData({ ...formData, asset_personal_injury_compensation: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
                <p className="text-xs text-gray-500 mt-1">Disregarded for 52 weeks from receipt</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Weeks Since Receiving Compensation
                </label>
                <input
                  type="number"
                  min="0"
                  max="52"
                  value={formData.personal_injury_compensation_weeks || 0}
                  onChange={(e) => setFormData({ ...formData, personal_injury_compensation_weeks: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
                <p className="text-xs text-gray-500 mt-1">Enter weeks since receiving compensation (0-52)</p>
              </div>
            </div>
            
            <h4 className="text-md font-semibold mt-6 mb-3 text-blue-700">Discretionary Disregards</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Business Assets (£)
                </label>
                <input
                  type="number"
                  min="0"
                  step="100"
                  value={formData.asset_business_assets || 0}
                  onChange={(e) => setFormData({ ...formData, asset_business_assets: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
                <p className="text-xs text-gray-500 mt-1">Disregarded while reasonable steps being taken to dispose</p>
              </div>
            </div>
            
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Weeks Since Entering Permanent Residential Care
              </label>
              <input
                type="number"
                min="0"
                value={formData.weeks_in_care || 0}
                onChange={(e) => setFormData({ ...formData, weeks_in_care: parseInt(e.target.value) || 0 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
              <p className="text-xs text-gray-500 mt-1">
                Property is disregarded for first 12 weeks of permanent residential care
              </p>
            </div>
          </div>

          {/* Preview LA Contact (before calculation) */}
          {previewLaContact && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-sm font-semibold text-blue-900">Your Local Authority</h4>
                <button
                  type="button"
                  onClick={() => setPreviewLaContact(null)}
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  Hide
                </button>
              </div>
              <LocalAuthorityContactCard 
                contact={previewLaContact}
                postcode={formData.postcode}
              />
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full px-4 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Calculating...
              </>
            ) : (
              <>
                <Calculator className="w-5 h-5" />
                Calculate Funding Eligibility
              </>
            )}
          </button>
        </form>
      </div>

      {result && (
        <div className="bg-white rounded-lg shadow p-6 space-y-6">
          {/* Debug: Log result state */}
          {(() => {
            console.log('🔍 [RENDER] Result state:', {
              hasLlmInsights: 'llmInsights' in result,
              resultKeys: Object.keys(result),
            });
            return null;
          })()}
          
          <div className="flex items-center gap-2 text-green-600">
            <CheckCircle className="w-5 h-5" />
            <span className="font-semibold">Funding eligibility calculated!</span>
          </div>

          {/* CHC Eligibility */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Heart className="w-5 h-5" />
              CHC Eligibility Assessment
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">CHC Probability</div>
                <div className="text-2xl font-bold">{result.chc_eligibility.probability_percent}%</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Threshold Category</div>
                <div className="text-lg font-semibold">
                  {result.chc_eligibility.threshold_category.replace('_', ' ')}
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Likely Eligible</div>
                <div className="text-lg font-semibold">
                  {result.chc_eligibility.is_likely_eligible ? '✅ Yes' : '❌ No'}
                </div>
              </div>
            </div>
            <div className="mt-4">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    result.chc_eligibility.probability_percent >= 70
                      ? 'bg-green-500'
                      : result.chc_eligibility.probability_percent >= 50
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                  }`}
                  style={{ width: `${result.chc_eligibility.probability_percent}%` }}
                />
              </div>
            </div>
            <div className="mt-4 bg-blue-50 rounded-lg p-4">
              <div className="text-sm text-gray-700">{result.chc_eligibility.reasoning}</div>
            </div>
            
            {/* CHC Domain Scores */}
            {result.chc_eligibility.domain_scores && Object.keys(result.chc_eligibility.domain_scores).length > 0 && (
              <div className="mt-4">
                <h4 className="text-md font-semibold mb-2">Domain Scores</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {Object.entries(result.chc_eligibility.domain_scores).map(([domain, score]) => (
                    <div key={domain} className="bg-white rounded p-2 border">
                      <div className="text-xs text-gray-600 capitalize">{domain.replace('_', ' ')}</div>
                      <div className="text-sm font-semibold">+{score}%</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* CHC Bonuses */}
            {result.chc_eligibility.bonuses_applied && result.chc_eligibility.bonuses_applied.length > 0 && (
              <div className="mt-4">
                <h4 className="text-md font-semibold mb-2">Bonuses Applied</h4>
                <div className="flex flex-wrap gap-2">
                  {result.chc_eligibility.bonuses_applied.map((bonus, idx) => (
                    <span key={idx} className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                      {bonus.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {/* Key Factors */}
            {result.chc_eligibility.key_factors && result.chc_eligibility.key_factors.length > 0 && (
              <div className="mt-4">
                <h4 className="text-md font-semibold mb-2">Key Factors</h4>
                <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                  {result.chc_eligibility.key_factors.map((factor, idx) => (
                    <li key={idx}>{factor}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* LA Support */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold mb-4">Local Authority Support</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Top-up Probability</div>
                <div className="text-2xl font-bold">
                  {result.la_support.top_up_probability_percent}%
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Full Support Probability</div>
                <div className="text-2xl font-bold">
                  {result.la_support.full_support_probability_percent}%
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Capital Assessed</div>
                <div className="text-2xl font-bold">
                  £{safeToFixed(result.la_support.capital_assessed)}
                </div>
              </div>
            </div>
            <div className="mt-4 bg-blue-50 rounded-lg p-4">
              <div className="text-sm text-gray-700">{result.la_support.reasoning}</div>
            </div>

            {/* Means Test Breakdown */}
            {result._means_test_breakdown && (
              <div className="mt-6 border-t pt-6">
                <h4 className="text-md font-semibold mb-4">Means Test Breakdown (2025-2026)</h4>
                <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-gray-600">Raw Capital Assets</div>
                      <div className="text-lg font-semibold">
                        £{safeToLocaleString(result._means_test_breakdown.raw_capital_assets)}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Asset Disregards</div>
                      <div className="text-lg font-semibold text-green-600">
                        -£{safeToLocaleString(result._means_test_breakdown.asset_disregards)}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Adjusted Capital Assets</div>
                      <div className="text-lg font-semibold">
                        £{safeToLocaleString(result._means_test_breakdown.adjusted_capital_assets)}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Tariff Income</div>
                      <div className="text-lg font-semibold">
                        £{safeToFixed(result.la_support.tariff_income_gbp_week)}/week
                      </div>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 mt-4">
                    <div>
                      <div className="text-sm text-gray-600">Raw Weekly Income</div>
                      <div className="text-lg font-semibold">
                        £{safeToFixed(result._means_test_breakdown.raw_weekly_income)}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Income Disregards</div>
                      <div className="text-lg font-semibold text-green-600">
                        -£{safeToFixed(result._means_test_breakdown.income_disregards)}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Adjusted Weekly Income</div>
                      <div className="text-lg font-semibold">
                        £{safeToFixed(result._means_test_breakdown.adjusted_weekly_income)}
                      </div>
                    </div>
                    {result.la_support.weekly_contribution != null && (
                      <div>
                        <div className="text-sm text-gray-600">Weekly Contribution Required</div>
                        <div className="text-lg font-semibold text-red-600">
                          £{safeToFixed(result.la_support.weekly_contribution)}
                        </div>
                      </div>
                    )}
                  </div>
                  <div className="mt-4 pt-4 border-t">
                    <div className="text-xs text-gray-500 space-y-1">
                      <div>Upper Capital Limit: £{safeToLocaleString(result._means_test_breakdown.upper_capital_limit)}</div>
                      <div>Lower Capital Limit: £{safeToLocaleString(result._means_test_breakdown.lower_capital_limit)}</div>
                      <div>Personal Expenses Allowance: £{safeToFixed(result._means_test_breakdown.personal_expenses_allowance)}/week</div>
                      <div>Minimum Income Guarantee: £{safeToFixed(result._means_test_breakdown.minimum_income_guarantee)}/week</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Savings */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <DollarSign className="w-5 h-5" />
              Potential Savings
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-green-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Weekly Savings</div>
                <div className="text-xl font-bold text-green-600">
                  £{safeToFixed(result.savings.weekly_savings)}
                </div>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Annual Savings</div>
                <div className="text-xl font-bold text-green-600">
                  £{safeToFixed(result.savings.annual_gbp, 0)}
                </div>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">5-Year Savings</div>
                <div className="text-xl font-bold text-green-600">
                  £{safeToFixed(result.savings.five_year_gbp, 0)}
                </div>
              </div>
              {result.savings.lifetime_gbp != null && (
                <div className="bg-green-50 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Lifetime Estimate</div>
                  <div className="text-xl font-bold text-green-600">
                    £{safeToFixed(result.savings.lifetime_gbp, 0)}
                  </div>
                </div>
              )}
            </div>
            {result.savings.annual_gbp > 10000 && (
              <div className="mt-4 bg-green-100 border border-green-300 rounded-lg p-4">
                <div className="text-lg font-semibold text-green-800">
                  🎉 Potential annual savings: £{safeToFixed(result.savings.annual_gbp, 0)}
                </div>
              </div>
            )}
          </div>

          {/* Recommendations */}
          {result.recommendations && result.recommendations.length > 0 && (
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold mb-4">Recommendations</h3>
              <ul className="space-y-2">
                {result.recommendations.map((rec, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                    <span className="text-gray-700">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Local Authority Contact Section */}
          {result.local_authority_contact && (
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <MapPin className="w-5 h-5" />
                Your Local Authority
              </h3>
              <LocalAuthorityContactCard 
                contact={result.local_authority_contact}
                postcode={formData.postcode}
              />
            </div>
          )}
          
          {/* Show helpful message if LA contact lookup failed but postcode is available */}
          {!result.local_authority_contact && formData.postcode && (
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <MapPin className="w-5 h-5" />
                Your Local Authority
              </h3>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-800 mb-2">
                  We couldn't automatically identify your Local Authority from the postcode.
                </p>
                <p className="text-sm text-blue-700">
                  Please contact your local council's Adult Social Care department directly for funding assessment information.
                </p>
              </div>
            </div>
          )}

          {/* LLM Insights Section - Always show, even if empty */}
          <div className="border-t pt-6">
            {(() => {
              console.log('🔍 [RENDER LLM Section] Checking llmInsights:', {
                resultLLMInsights: result.llmInsights,
                isPresent: 'llmInsights' in result,
                type: typeof result.llmInsights,
                keys: result.llmInsights ? Object.keys(result.llmInsights) : [],
              });
              return null;
            })()}
            
            {result.llmInsights ? (
              <FundingLLMInsights insights={result.llmInsights} />
            ) : (
              <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <div className="flex items-center gap-2 mb-2">
                  <Info className="w-5 h-5 text-gray-500" />
                  <p className="text-sm font-semibold text-gray-700">Expert Insights</p>
                </div>
                <p className="text-sm text-gray-600">
                  Insights are being generated. Please refresh or try again in a moment.
                </p>
                {process.env.NODE_ENV === 'development' && (
                  <div className="mt-2 p-2 bg-gray-100 rounded text-xs text-gray-500">
                    <div>Debug Info:</div>
                    <div>llmInsights: {result.llmInsights ? '✅ present' : '❌ missing'}</div>
                    <div>Result keys: {Object.keys(result).join(', ')}</div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Data Sources & References Section */}
          <div className="border-t pt-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Database className="w-5 h-5 text-gray-600" />
                <h3 className="text-lg font-semibold text-gray-900">Data Sources & References</h3>
              </div>
              <button
                onClick={async () => {
                  if (!showDataSources) {
                    if (!dataSourcesContent) {
                      setLoadingDataSources(true);
                      try {
                        const response = await axios.get('/api/rch-data/funding/data-sources');
                        setDataSourcesContent(response.data.content);
                      } catch (error) {
                        console.error('Error loading data sources:', error);
                        alert('Failed to load data sources. Please try again.');
                      } finally {
                        setLoadingDataSources(false);
                      }
                    }
                    setShowDataSources(true);
                  } else {
                    setShowDataSources(false);
                  }
                }}
                disabled={loadingDataSources}
                className="px-4 py-2 text-sm text-[#1E2A44] hover:bg-gray-50 rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {loadingDataSources ? (
                  <>
                    <div className="w-4 h-4 border-2 border-[#1E2A44] border-t-transparent rounded-full animate-spin"></div>
                    Loading...
                  </>
                ) : showDataSources ? (
                  <>
                    <Info className="w-4 h-4" />
                    Hide Sources
                  </>
                ) : (
                  <>
                    <BookOpen className="w-4 h-4" />
                    Show Sources
                  </>
                )}
              </button>
            </div>
            
            {showDataSources && dataSourcesContent && (
              <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
                <div className="flex items-center gap-3 mb-4">
                  <BookOpen className="w-6 h-6 text-blue-600" />
                  <h4 className="text-xl font-bold text-gray-900">
                    Funding Eligibility Calculator - Data Sources & References
                  </h4>
                </div>
                <p className="text-sm text-gray-600 mb-4">
                  Complete list of official sources, legal citations, and verification guides for the Funding Eligibility Calculator.
                </p>
                <div className="bg-white rounded-lg p-6 border border-blue-200 max-h-[600px] overflow-y-auto">
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown>{dataSourcesContent}</ReactMarkdown>
                  </div>
                </div>
              </div>
            )}
            
            {showDataSources && !dataSourcesContent && !loadingDataSources && (
              <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-yellow-600" />
                  <p className="text-sm text-yellow-800">
                    Unable to load data sources. Please try again later.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Legal Disclaimer */}
      <div id="disclaimer">
        <LegalDisclaimer className="mt-8" />
      </div>
    </div>
  );
}


import { useState, useEffect } from 'react';
import { Search, Building2, Users, TrendingDown, TrendingUp, AlertCircle, CheckCircle, X, Eye, FileText, Lock, Unlock, Bell, Shield, DollarSign } from 'lucide-react';
import axios from 'axios';

interface Company {
  company_number: string;
  title: string;
  company_status?: string;
  company_type?: string;
  address_snippet?: string;
  date_of_creation?: string;
  description?: string;
  [key: string]: any;
}

interface FinancialStability {
  company_name: string;
  company_number: string;
  score: number;
  risk_level: string;
  risk_label?: string;
  risk_description?: string;
  issues: string[];
  company_status: string;
  breakdown?: string[];
  max_score?: number;
}

interface CompanyDetails {
  profile: any;
  officers: any[];
  charges: any[];
  financial_stability: FinancialStability;
}

interface MonitoringAlert {
  type: 'critical' | 'warning' | 'info';
  message: string;
  severity: 'high' | 'medium' | 'low';
  date: string;
}

interface HistoricalTrend {
  date: string;
  score: number;
  risk_level: string;
}

interface PremiumData {
  financial_stability: FinancialStability;
  profile: any;
  officers: any[];
  charges: any[];
  monitoring_alerts: MonitoringAlert[];
  historical_trends: HistoricalTrend[];
  monitoring_status: string;
  last_check: string;
  next_check: string;
}

interface RiskSignal {
  type: string;
  weight: number;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  message: string;
  timeline: string;
  detail?: string;
}

interface RiskAssessment {
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  total_weight: number;
  signal_count: number;
  signals: RiskSignal[];
  calculated_at: string;
}

interface FinancialHealthData {
  company_number: string;
  company_name: string;
  analysis_date: string;
  risk_assessment: RiskAssessment;
  data_summary: {
    company_status: string;
    accounts_overdue: boolean;
    total_charges: number;
    active_directors: number;
    ownership_type: string;
  };
  recommendations: string[];
  raw_data: {
    profile: any;
    filing_count: number;
    charge_count: number;
    officer_count: number;
    psc_count: number;
  };
}

type ReportTier = 'free' | 'professional' | 'premium';

export default function CompaniesHouseExplorer() {
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState<Company[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<CompanyDetails | null>(null);
  const [premiumData, setPremiumData] = useState<PremiumData | null>(null);
  const [financialHealthData, setFinancialHealthData] = useState<FinancialHealthData | null>(null);
  const [reportTier, setReportTier] = useState<ReportTier>('free');
  const [itemsPerPage, setItemsPerPage] = useState(20);
  const [shouldScrollToDetails, setShouldScrollToDetails] = useState(false);

  // Auto-scroll to details when company is selected
  useEffect(() => {
    if (selectedCompany && shouldScrollToDetails) {
      const scrollToDetails = () => {
        const detailsElement = document.getElementById('company-details');
        if (detailsElement) {
          const elementPosition = detailsElement.getBoundingClientRect().top;
          const offsetPosition = elementPosition + window.pageYOffset - 20; // 20px offset for header
          
          window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
          });
          setShouldScrollToDetails(false); // Reset flag
        }
      };
      
      // Small delay to ensure DOM is fully rendered
      const timer = setTimeout(scrollToDetails, 150);
      return () => clearTimeout(timer);
    }
  }, [selectedCompany, shouldScrollToDetails]);

  const handleSearch = async (queryOverride?: string) => {
    const queryToUse = queryOverride || searchQuery;
    
    if (!queryToUse.trim()) {
      alert('Please enter a company name or number');
      return;
    }

    setLoading(true);
    setSelectedCompany(null);
    setPremiumData(null);
    setReportTier('free');
    setShouldScrollToDetails(false); // Reset scroll flag on new search
    
    try {
      const response = await axios.get('/api/companies-house/search', {
        params: {
          query: queryToUse,
          items_per_page: itemsPerPage,
        },
      });

      if (response.data.status === 'success') {
        setResults(response.data.companies || []);
      } else {
        setResults([]);
        alert('No companies found');
      }
    } catch (error: any) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleViewCompanyDetails = async (companyNumber: string) => {
    if (!companyNumber) {
      alert('Company number is required');
      return;
    }
    
    setLoading(true);
    setReportTier('free');
    setPremiumData(null);
    setSelectedCompany(null); // Clear previous selection
    
    try {
      console.log('Loading company details for:', companyNumber);
      const response = await axios.get(`/api/companies-house/company/${companyNumber}`);
      
      if (response.data.status === 'success') {
        setSelectedCompany(response.data);
        // Trigger scroll via useEffect
        setShouldScrollToDetails(true);
      } else {
        alert('Failed to load company details');
      }
    } catch (error: any) {
      console.error('Error loading company details:', error);
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadProfessionalData = async (companyNumber: string) => {
    setReportTier('professional');
    setLoading(true);
    
    try {
      // Load comprehensive financial health data
      const response = await axios.get(`/api/companies-house/company/${companyNumber}/financial-health`);
      if (response.data.status === 'success') {
        setFinancialHealthData(response.data.data);
      }
    } catch (error: any) {
      console.error('Error loading professional data:', error);
      // Fallback to basic data if financial health fails
      alert(`Error loading professional data: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadPremiumData = async (companyNumber: string) => {
    setReportTier('premium');
    setLoading(true);
    
    try {
      // Load both premium data and financial health data
      const [premiumResponse, healthResponse] = await Promise.all([
        axios.get(`/api/companies-house/company/${companyNumber}/premium-data`),
        axios.get(`/api/companies-house/company/${companyNumber}/financial-health`)
      ]);
      
      if (premiumResponse.data.status === 'success') {
        setPremiumData(premiumResponse.data);
        // Update selected company with premium financial stability data
        if (selectedCompany) {
          setSelectedCompany({
            ...selectedCompany,
            financial_stability: premiumResponse.data.financial_stability
          });
        }
      }
      
      if (healthResponse.data.status === 'success') {
        setFinancialHealthData(healthResponse.data.data);
      }
    } catch (error: any) {
      alert(`Error loading premium data: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel.toUpperCase()) {
      case 'MINIMAL':
        return 'text-green-600';
      case 'LOW':
        return 'text-green-600';
      case 'MEDIUM':
        return 'text-yellow-600';
      case 'HIGH':
        return 'text-red-600';
      case 'CRITICAL':
        return 'text-red-800';
      default:
        return 'text-gray-600';
    }
  };

  const getRiskBgColor = (riskLevel: string) => {
    switch (riskLevel.toUpperCase()) {
      case 'MINIMAL':
        return 'bg-green-100 text-green-800';
      case 'LOW':
        return 'bg-green-100 text-green-800';
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800';
      case 'HIGH':
        return 'bg-red-100 text-red-800';
      case 'CRITICAL':
        return 'bg-red-200 text-red-900';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status?: string) => {
    if (!status) return 'bg-gray-100 text-gray-800';
    if (status.toLowerCase() === 'active') {
      return 'bg-green-100 text-green-800';
    }
    return 'bg-red-100 text-red-800';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Companies House Explorer</h1>
        <p className="mt-2 text-gray-600">
          Analyze financial stability of care home companies - risk assessment, officers, charges, and monitoring
        </p>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Search Companies</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Company Name or Number *
            </label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="e.g., Manor House Care Ltd or 12345678"
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <div className="mt-2">
              <p className="text-xs text-gray-500 mb-2">Quick test examples (click to use):</p>
              <div className="flex flex-wrap gap-2">
                {[
                  { name: 'care home', label: 'Care Home (General)', description: 'Search for care homes', direct: false },
                  { name: 'Barchester Healthcare', label: 'Barchester Healthcare', description: 'Major care home operator - #02792285', direct: false },
                  { name: 'Four Seasons Health Care', label: 'Four Seasons', description: 'Large care provider - #05165301', direct: false },
                  { name: '02792285', label: 'Barchester (#02792285)', description: 'Direct: Barchester Healthcare Limited', direct: true },
                  { name: '07495895', label: 'Test Company (#07495895)', description: 'Direct: Known test company', direct: true }
                ].map((example) => (
                  <button
                    key={example.name}
                    type="button"
                    onClick={() => {
                      if (example.direct && /^\d+$/.test(example.name)) {
                        // If it's a company number, directly load details
                        handleViewCompanyDetails(example.name);
                      } else {
                        // Otherwise, search
                        setSearchQuery(example.name);
                        handleSearch(example.name);
                      }
                    }}
                    className="px-3 py-1 text-xs bg-blue-50 text-blue-700 border border-blue-200 rounded-md hover:bg-blue-100 transition-colors"
                    title={example.description}
                  >
                    {example.label}
                  </button>
                ))}
              </div>
            </div>
            <p className="mt-1 text-xs text-gray-500">
              Tip: Search will automatically add "care home" keywords if not present
            </p>
          </div>
          <div className="w-64">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Results per Page
            </label>
            <input
              type="number"
              value={itemsPerPage}
              onChange={(e) => setItemsPerPage(parseInt(e.target.value) || 20)}
              min="1"
              max="100"
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>
          <button
            type="button"
            onClick={handleSearch}
            disabled={loading}
            className="inline-flex items-center px-6 py-3 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-purple-700 disabled:opacity-50"
          >
            <Search className="w-4 h-4 mr-2" />
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold">Results ({results.length})</h2>
          </div>
          <div className="divide-y divide-gray-200">
            {results.map((company) => (
              <div key={company.company_number} className="p-6 hover:bg-gray-50">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0">
                        <Building2 className="w-8 h-8 text-gray-400" />
                      </div>
                      <div className="flex-1">
                        <h3 className="text-lg font-medium text-gray-900">{company.title}</h3>
                        <div className="mt-2 space-y-1 text-sm text-gray-600">
                          <div className="flex items-center gap-2">
                            <span className="font-medium">Company Number:</span>
                            <span className="font-mono">{company.company_number}</span>
                          </div>
                          {company.company_status && (
                            <div className="flex items-center gap-2">
                              <span className="font-medium">Status:</span>
                              <span
                                className={`px-2 py-1 rounded text-xs ${getStatusColor(
                                  company.company_status
                                )}`}
                              >
                                {company.company_status}
                              </span>
                            </div>
                          )}
                          {company.company_type && (
                            <div className="flex items-center gap-2">
                              <span className="font-medium">Type:</span>
                              <span>{company.company_type}</span>
                            </div>
                          )}
                          {company.address_snippet && (
                            <div className="flex items-center">
                              <span className="font-medium mr-2">Address:</span>
                              <span>{company.address_snippet}</span>
                            </div>
                          )}
                          {company.date_of_creation && (
                            <div className="flex items-center gap-2">
                              <span className="font-medium">Incorporated:</span>
                              <span>{new Date(company.date_of_creation).toLocaleDateString()}</span>
                            </div>
                          )}
                          {company.description && (
                            <div className="mt-2 text-xs text-gray-500">
                              {company.description}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="ml-4">
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        handleViewCompanyDetails(company.company_number);
                      }}
                      className="inline-flex items-center px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      View Details
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Company Details */}
      {selectedCompany && (
        <div id="company-details" className="space-y-6">
          {/* Report Tier Selector */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold mb-4">{selectedCompany.financial_stability.company_name}</h2>
            
            {/* Tier Selection */}
            <div className="mb-6 border-b pb-4">
              <p className="text-sm text-gray-600 mb-3">Select Report Tier:</p>
              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={() => {
                    setReportTier('free');
                    setPremiumData(null);
                  }}
                  className={`px-4 py-2 rounded-md font-medium flex items-center gap-2 ${
                    reportTier === 'free'
                      ? 'bg-green-100 text-green-800 border-2 border-green-500'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <Unlock className="w-4 h-4" />
                  FREE Tier
                </button>
                <button
                  type="button"
                  onClick={() => handleLoadProfessionalData(selectedCompany.financial_stability.company_number)}
                  className={`px-4 py-2 rounded-md font-medium flex items-center gap-2 ${
                    reportTier === 'professional'
                      ? 'bg-blue-100 text-blue-800 border-2 border-blue-500'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <FileText className="w-4 h-4" />
                  Professional (£119)
                </button>
                <button
                  type="button"
                  onClick={() => handleLoadPremiumData(selectedCompany.financial_stability.company_number)}
                  className={`px-4 py-2 rounded-md font-medium flex items-center gap-2 ${
                    reportTier === 'premium'
                      ? 'bg-purple-100 text-purple-800 border-2 border-purple-500'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <Bell className="w-4 h-4" />
                  Premium (£299)
                </button>
              </div>
            </div>
          </div>

          {/* FREE Tier Report */}
          {reportTier === 'free' && (
            <div className="bg-white rounded-lg shadow p-6 border-2 border-green-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold flex items-center gap-2">
                  <Unlock className="w-5 h-5 text-green-600" />
                  FREE Tier Report
                </h3>
                <span className="text-sm text-gray-500">Basic Financial Status</span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Financial Health</p>
                  <div className="flex items-center gap-3">
                    <span className={`text-4xl font-bold ${getRiskColor(selectedCompany.financial_stability.risk_level)}`}>
                      {selectedCompany.financial_stability.score}
                    </span>
                    <div>
                      <p className={`font-semibold ${getRiskColor(selectedCompany.financial_stability.risk_level)}`}>
                        {selectedCompany.financial_stability.risk_label || selectedCompany.financial_stability.risk_level}
                      </p>
                      <p className="text-sm text-gray-500">
                        {selectedCompany.financial_stability.risk_description || 'Financial stability assessment'}
                      </p>
                    </div>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Company Status</p>
                  <span className={`px-3 py-1 rounded text-sm font-medium ${getStatusColor(selectedCompany.financial_stability.company_status)}`}>
                    {selectedCompany.financial_stability.company_status}
                  </span>
                  <p className="text-sm text-gray-500 mt-2">
                    Company Number: {selectedCompany.financial_stability.company_number}
                  </p>
                </div>
              </div>
              
              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                <p className="text-sm text-blue-800">
                  💡 <strong>Upgrade to Professional</strong> for detailed breakdown scores and comprehensive financial analysis
                </p>
              </div>
            </div>
          )}

          {/* Professional Tier Report */}
          {reportTier === 'professional' && (
            <div className="space-y-6">
              <div className="bg-white rounded-lg shadow p-6 border-2 border-blue-200">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold flex items-center gap-2">
                    <FileText className="w-5 h-5 text-blue-600" />
                    Professional Tier Report (£119)
                  </h3>
                  <span className="text-sm text-gray-500">Detailed Financial Analysis</span>
                </div>

                {/* Financial Health Assessment */}
                {financialHealthData && financialHealthData.risk_assessment && (
                  <>
                    {/* Risk Score & Level */}
                    <div className="mb-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border border-blue-200">
                      <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                        <Shield className="w-5 h-5 text-green-600" />
                        Financial Health Assessment
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
                        <div>
                          <p className="text-sm text-gray-600 mb-2">Risk Score</p>
                          <div className={`text-5xl font-bold ${getRiskColor(financialHealthData.risk_assessment.risk_level)}`}>
                            {financialHealthData.risk_assessment.risk_score}
                          </div>
                          <p className="text-sm text-gray-500 mt-1">out of 100</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600 mb-2">Risk Level</p>
                          <div className={`inline-block px-4 py-2 rounded-lg text-lg font-semibold ${getRiskBgColor(financialHealthData.risk_assessment.risk_level)}`}>
                            {financialHealthData.risk_assessment.risk_level}
                          </div>
                          <p className="text-sm text-gray-500 mt-2">
                            Total Weight: {financialHealthData.risk_assessment.total_weight} | 
                            Signals: {financialHealthData.risk_assessment.signal_count}
                          </p>
                        </div>
                      </div>
                      
                      {/* Risk Score Progress Bar */}
                      <div className="mt-4">
                        <div className="flex justify-between mb-1">
                          <span className="text-sm font-semibold">Risk Score</span>
                          <span className="text-sm text-gray-600">{financialHealthData.risk_assessment.risk_score}/100</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-4">
                          <div
                            className={`h-4 rounded-full ${
                              financialHealthData.risk_assessment.risk_score >= 70 ? 'bg-red-500' :
                              financialHealthData.risk_assessment.risk_score >= 40 ? 'bg-yellow-500' :
                              'bg-green-500'
                            }`}
                            style={{ width: `${financialHealthData.risk_assessment.risk_score}%` }}
                          />
                        </div>
                      </div>
                    </div>

                    {/* Risk Signals */}
                    {financialHealthData.risk_assessment.signals && financialHealthData.risk_assessment.signals.length > 0 && (
                      <div className="mb-6">
                        <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                          <AlertCircle className="w-5 h-5" />
                          Risk Signals ({financialHealthData.risk_assessment.signals.length})
                        </h4>
                        <div className="space-y-3">
                          {financialHealthData.risk_assessment.signals.map((signal, idx) => (
                            <div
                              key={idx}
                              className={`p-4 rounded-lg border-l-4 ${
                                signal.severity === 'CRITICAL' ? 'bg-red-50 border-red-500' :
                                signal.severity === 'HIGH' ? 'bg-orange-50 border-orange-500' :
                                signal.severity === 'MEDIUM' ? 'bg-yellow-50 border-yellow-500' :
                                'bg-blue-50 border-blue-500'
                              }`}
                            >
                              <div className="flex items-start justify-between mb-2">
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-1">
                                    <span className={`font-semibold ${
                                      signal.severity === 'CRITICAL' ? 'text-red-800' :
                                      signal.severity === 'HIGH' ? 'text-orange-800' :
                                      signal.severity === 'MEDIUM' ? 'text-yellow-800' :
                                      'text-blue-800'
                                    }`}>
                                      {signal.severity}
                                    </span>
                                    <span className="text-xs px-2 py-1 bg-gray-200 rounded">
                                      Weight: {signal.weight}
                                    </span>
                                  </div>
                                  <p className="text-sm font-medium text-gray-900 mb-1">{signal.message}</p>
                                  {signal.detail && (
                                    <p className="text-xs text-gray-600 mb-1">{signal.detail}</p>
                                  )}
                                  <p className="text-xs text-gray-500">Timeline: {signal.timeline}</p>
                                </div>
                                <span className="text-xs text-gray-400 ml-2">{signal.type}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Data Summary */}
                    <div className="mb-6">
                      <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                        <Building2 className="w-5 h-5" />
                        Data Summary
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <div className="border border-gray-200 rounded-lg p-4">
                          <p className="text-sm text-gray-600 mb-1">Company Status</p>
                          <p className={`font-semibold ${getStatusColor(financialHealthData.data_summary.company_status)} inline-block px-2 py-1 rounded`}>
                            {financialHealthData.data_summary.company_status}
                          </p>
                        </div>
                        <div className="border border-gray-200 rounded-lg p-4">
                          <p className="text-sm text-gray-600 mb-1">Accounts Overdue</p>
                          <p className={`font-semibold ${financialHealthData.data_summary.accounts_overdue ? 'text-red-600' : 'text-green-600'}`}>
                            {financialHealthData.data_summary.accounts_overdue ? 'Yes' : 'No'}
                          </p>
                        </div>
                        <div className="border border-gray-200 rounded-lg p-4">
                          <p className="text-sm text-gray-600 mb-1">Total Charges</p>
                          <p className="font-semibold text-gray-900">{financialHealthData.data_summary.total_charges}</p>
                        </div>
                        <div className="border border-gray-200 rounded-lg p-4">
                          <p className="text-sm text-gray-600 mb-1">Active Directors</p>
                          <p className="font-semibold text-gray-900">{financialHealthData.data_summary.active_directors}</p>
                        </div>
                        <div className="border border-gray-200 rounded-lg p-4">
                          <p className="text-sm text-gray-600 mb-1">Ownership Type</p>
                          <p className="font-semibold text-gray-900">{financialHealthData.data_summary.ownership_type}</p>
                        </div>
                        <div className="border border-gray-200 rounded-lg p-4">
                          <p className="text-sm text-gray-600 mb-1">Analysis Date</p>
                          <p className="text-xs text-gray-500">{new Date(financialHealthData.analysis_date).toLocaleString()}</p>
                        </div>
                      </div>
                    </div>

                    {/* Recommendations */}
                    {financialHealthData.recommendations && financialHealthData.recommendations.length > 0 && (
                      <div className="mb-6">
                        <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                          <CheckCircle className="w-5 h-5 text-green-600" />
                          Recommendations
                        </h4>
                        <div className="space-y-2">
                          {financialHealthData.recommendations.map((rec, idx) => (
                            <div key={idx} className="p-3 bg-green-50 border-l-4 border-green-500 rounded">
                              <p className="text-sm text-gray-800">{rec}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                )}

                {/* Financial Stability Score */}
                <div className="mb-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border border-blue-200">
                  <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                    <DollarSign className="w-5 h-5 text-green-600" />
                    Financial Stability Score
                  </h4>
                  <div className="flex items-center gap-4 mb-4">
                    <div className="text-center">
                      <div className={`text-5xl font-bold ${getRiskColor(selectedCompany.financial_stability.risk_level)}`}>
                        {selectedCompany.financial_stability.score}
                      </div>
                      <div className="text-sm text-gray-600">out of {selectedCompany.financial_stability.max_score || 100}</div>
                    </div>
                    <div className="flex-1">
                      <div className="mb-2">
                        <div className="flex justify-between mb-1">
                          <span className="text-sm font-semibold">
                            {selectedCompany.financial_stability.risk_label || selectedCompany.financial_stability.risk_level}
                          </span>
                          <span className="text-sm text-gray-600">{selectedCompany.financial_stability.score}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                          <div
                            className={`h-3 rounded-full ${
                              selectedCompany.financial_stability.score >= 70 ? 'bg-green-500' :
                              selectedCompany.financial_stability.score >= 50 ? 'bg-yellow-500' :
                              selectedCompany.financial_stability.score >= 30 ? 'bg-orange-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${selectedCompany.financial_stability.score}%` }}
                          />
                        </div>
                      </div>
                      <p className="text-sm text-gray-700 mt-2">
                        {selectedCompany.financial_stability.risk_description || 'Financial stability assessment'}
                      </p>
                    </div>
                  </div>
                  
                  {/* Breakdown */}
                  {selectedCompany.financial_stability.breakdown && selectedCompany.financial_stability.breakdown.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-blue-200">
                      <p className="text-sm font-semibold mb-2">Score Breakdown:</p>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {selectedCompany.financial_stability.breakdown.map((detail, idx) => (
                          <li key={idx}>• {detail}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* Issues */}
                {selectedCompany.financial_stability.issues.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-lg font-semibold mb-3 flex items-center gap-2 text-red-700">
                      <AlertCircle className="w-5 h-5" />
                      Issues Identified
                    </h4>
                    <div className="space-y-2">
                      {selectedCompany.financial_stability.issues.map((issue, idx) => (
                        <div key={idx} className="p-3 bg-red-50 border-l-4 border-red-500 rounded">
                          <p className="text-sm text-red-800">{issue}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Officers Summary */}
                {selectedCompany.officers && selectedCompany.officers.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      <Users className="w-5 h-5" />
                      Directors & Officers ({selectedCompany.officers.filter((o: any) => !o.resigned_on).length} active)
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {selectedCompany.officers.slice(0, 6).map((officer: any, idx: number) => (
                        <div key={idx} className="border border-gray-200 rounded p-3">
                          <div className="font-medium">{officer.name}</div>
                          <div className="text-sm text-gray-600">
                            {officer.officer_role && <span className="mr-3">Role: {officer.officer_role}</span>}
                            {officer.appointed_on && (
                              <span>Appointed: {new Date(officer.appointed_on).toLocaleDateString()}</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Charges Summary */}
                {selectedCompany.charges && selectedCompany.charges.length > 0 && (
                  <div>
                    <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      <Shield className="w-5 h-5" />
                      Charges & Mortgages ({selectedCompany.charges.filter((c: any) => !c.satisfied_on).length} outstanding)
                    </h4>
                    <div className="space-y-2">
                      {selectedCompany.charges.slice(0, 5).map((charge: any, idx: number) => (
                        <div key={idx} className="border border-gray-200 rounded p-3">
                          <div className="font-medium">{charge.charge_code || 'Charge'}</div>
                          <div className="text-sm text-gray-600">
                            {charge.created && (
                              <span className="mr-3">Created: {new Date(charge.created).toLocaleDateString()}</span>
                            )}
                            {charge.satisfied_on ? (
                              <span className="text-green-600">Satisfied</span>
                            ) : (
                              <span className="text-red-600">Outstanding</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Premium Tier Report */}
          {reportTier === 'premium' && premiumData && (
            <div className="space-y-6">
              <div className="bg-white rounded-lg shadow p-6 border-2 border-purple-200">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold flex items-center gap-2">
                    <Bell className="w-5 h-5 text-purple-600" />
                    Premium Tier Report (£299)
                  </h3>
                  <span className="text-sm text-gray-500">Full Monitoring & Intelligence</span>
                </div>

                {/* Financial Health Assessment (Enhanced) */}
                {financialHealthData && financialHealthData.risk_assessment && (
                  <>
                    {/* Risk Score & Level */}
                    <div className="mb-6 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-6 border border-purple-200">
                      <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                        <Shield className="w-5 h-5 text-purple-600" />
                        Comprehensive Financial Health Assessment
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-4">
                        <div className="text-center">
                          <p className="text-sm text-gray-600 mb-2">Risk Score</p>
                          <div className={`text-6xl font-bold ${getRiskColor(financialHealthData.risk_assessment.risk_level)}`}>
                            {financialHealthData.risk_assessment.risk_score}
                          </div>
                          <p className="text-sm text-gray-500 mt-1">out of 100</p>
                        </div>
                        <div className="text-center">
                          <p className="text-sm text-gray-600 mb-2">Risk Level</p>
                          <div className={`inline-block px-6 py-3 rounded-lg text-xl font-semibold ${getRiskBgColor(financialHealthData.risk_assessment.risk_level)}`}>
                            {financialHealthData.risk_assessment.risk_level}
                          </div>
                        </div>
                        <div className="text-center">
                          <p className="text-sm text-gray-600 mb-2">Risk Signals</p>
                          <div className="text-4xl font-bold text-gray-900">{financialHealthData.risk_assessment.signal_count}</div>
                          <p className="text-sm text-gray-500 mt-1">Total Weight: {financialHealthData.risk_assessment.total_weight}</p>
                        </div>
                      </div>
                      
                      {/* Risk Score Progress Bar */}
                      <div className="mt-4">
                        <div className="flex justify-between mb-2">
                          <span className="text-sm font-semibold">Risk Score Visualization</span>
                          <span className="text-sm text-gray-600">{financialHealthData.risk_assessment.risk_score}/100</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-5">
                          <div
                            className={`h-5 rounded-full transition-all ${
                              financialHealthData.risk_assessment.risk_score >= 70 ? 'bg-red-500' :
                              financialHealthData.risk_assessment.risk_score >= 40 ? 'bg-yellow-500' :
                              'bg-green-500'
                            }`}
                            style={{ width: `${financialHealthData.risk_assessment.risk_score}%` }}
                          />
                        </div>
                      </div>
                    </div>

                    {/* Risk Signals (Enhanced) */}
                    {financialHealthData.risk_assessment.signals && financialHealthData.risk_assessment.signals.length > 0 && (
                      <div className="mb-6">
                        <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                          <AlertCircle className="w-5 h-5" />
                          Detailed Risk Signals Analysis ({financialHealthData.risk_assessment.signals.length})
                        </h4>
                        <div className="space-y-3">
                          {financialHealthData.risk_assessment.signals.map((signal, idx) => (
                            <div
                              key={idx}
                              className={`p-5 rounded-lg border-l-4 shadow-sm ${
                                signal.severity === 'CRITICAL' ? 'bg-red-50 border-red-600' :
                                signal.severity === 'HIGH' ? 'bg-orange-50 border-orange-600' :
                                signal.severity === 'MEDIUM' ? 'bg-yellow-50 border-yellow-600' :
                                'bg-blue-50 border-blue-600'
                              }`}
                            >
                              <div className="flex items-start justify-between mb-2">
                                <div className="flex-1">
                                  <div className="flex items-center gap-3 mb-2">
                                    <span className={`font-bold text-lg ${
                                      signal.severity === 'CRITICAL' ? 'text-red-800' :
                                      signal.severity === 'HIGH' ? 'text-orange-800' :
                                      signal.severity === 'MEDIUM' ? 'text-yellow-800' :
                                      'text-blue-800'
                                    }`}>
                                      {signal.severity}
                                    </span>
                                    <span className="text-xs px-3 py-1 bg-white rounded-full border font-semibold">
                                      Weight: {signal.weight}
                                    </span>
                                    <span className="text-xs px-2 py-1 bg-gray-200 rounded text-gray-600">
                                      {signal.type}
                                    </span>
                                  </div>
                                  <p className="text-base font-semibold text-gray-900 mb-2">{signal.message}</p>
                                  {signal.detail && (
                                    <p className="text-sm text-gray-700 mb-2 bg-white p-2 rounded">{signal.detail}</p>
                                  )}
                                  <div className="flex items-center gap-2">
                                    <span className="text-xs font-medium text-gray-600">Timeline:</span>
                                    <span className="text-xs text-gray-800 bg-white px-2 py-1 rounded">{signal.timeline}</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Enhanced Data Summary */}
                    <div className="mb-6">
                      <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                        <Building2 className="w-5 h-5" />
                        Comprehensive Data Summary
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <div className="border border-purple-200 rounded-lg p-4 bg-purple-50">
                          <p className="text-sm text-gray-600 mb-1">Company Status</p>
                          <p className={`font-semibold ${getStatusColor(financialHealthData.data_summary.company_status)} inline-block px-3 py-1 rounded`}>
                            {financialHealthData.data_summary.company_status}
                          </p>
                        </div>
                        <div className={`border rounded-lg p-4 ${financialHealthData.data_summary.accounts_overdue ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}>
                          <p className="text-sm text-gray-600 mb-1">Accounts Overdue</p>
                          <p className={`font-semibold text-lg ${financialHealthData.data_summary.accounts_overdue ? 'text-red-600' : 'text-green-600'}`}>
                            {financialHealthData.data_summary.accounts_overdue ? '⚠️ Yes' : '✅ No'}
                          </p>
                        </div>
                        <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                          <p className="text-sm text-gray-600 mb-1">Total Charges</p>
                          <p className="font-semibold text-2xl text-gray-900">{financialHealthData.data_summary.total_charges}</p>
                        </div>
                        <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                          <p className="text-sm text-gray-600 mb-1">Active Directors</p>
                          <p className="font-semibold text-2xl text-gray-900">{financialHealthData.data_summary.active_directors}</p>
                        </div>
                        <div className="border border-purple-200 rounded-lg p-4 bg-purple-50">
                          <p className="text-sm text-gray-600 mb-1">Ownership Type</p>
                          <p className="font-semibold text-lg text-gray-900">{financialHealthData.data_summary.ownership_type}</p>
                        </div>
                        <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                          <p className="text-sm text-gray-600 mb-1">Raw Data Points</p>
                          <div className="text-xs text-gray-600 space-y-1">
                            <p>Filings: {financialHealthData.raw_data.filing_count}</p>
                            <p>Charges: {financialHealthData.raw_data.charge_count}</p>
                            <p>Officers: {financialHealthData.raw_data.officer_count}</p>
                            <p>PSCs: {financialHealthData.raw_data.psc_count}</p>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Recommendations (Enhanced) */}
                    {financialHealthData.recommendations && financialHealthData.recommendations.length > 0 && (
                      <div className="mb-6">
                        <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                          <CheckCircle className="w-5 h-5 text-green-600" />
                          Actionable Recommendations
                        </h4>
                        <div className="space-y-3">
                          {financialHealthData.recommendations.map((rec, idx) => (
                            <div key={idx} className="p-4 bg-gradient-to-r from-green-50 to-blue-50 border-l-4 border-green-500 rounded-lg shadow-sm">
                              <div className="flex items-start gap-3">
                                <span className="text-green-600 font-bold">{idx + 1}.</span>
                                <p className="text-sm font-medium text-gray-800 flex-1">{rec}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                )}

                {/* Monitoring Status */}
                <div className="mb-6 p-4 bg-purple-50 rounded-lg border border-purple-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold text-purple-900">Active Monitoring</p>
                      <p className="text-sm text-purple-700">
                        Last checked: {new Date(premiumData.last_check).toLocaleString()}
                      </p>
                      <p className="text-sm text-purple-700">
                        Next check: {new Date(premiumData.next_check).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 text-green-600">
                      <CheckCircle className="w-5 h-5" />
                      <span className="font-semibold">Active</span>
                    </div>
                  </div>
                </div>

                {/* Alerts */}
                {premiumData.monitoring_alerts && premiumData.monitoring_alerts.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      <AlertCircle className="w-5 h-5" />
                      Monitoring Alerts
                    </h4>
                    <div className="space-y-2">
                      {premiumData.monitoring_alerts.map((alert, idx) => (
                        <div
                          key={idx}
                          className={`p-3 rounded-lg border-l-4 ${
                            alert.severity === 'high' ? 'bg-red-50 border-red-500' :
                            alert.severity === 'medium' ? 'bg-yellow-50 border-yellow-500' :
                            'bg-blue-50 border-blue-500'
                          }`}
                        >
                          <div className="flex items-start justify-between">
                            <div>
                              <p className={`font-semibold ${
                                alert.severity === 'high' ? 'text-red-800' :
                                alert.severity === 'medium' ? 'text-yellow-800' :
                                'text-blue-800'
                              }`}>
                                {alert.type === 'critical' ? '🚨 Critical' :
                                 alert.type === 'warning' ? '⚠️ Warning' : 'ℹ️ Info'}
                              </p>
                              <p className="text-sm text-gray-700 mt-1">{alert.message}</p>
                            </div>
                            <span className="text-xs text-gray-500">
                              {new Date(alert.date).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* All Professional Tier Content */}
                <div className="mb-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border border-blue-200">
                  <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                    <DollarSign className="w-5 h-5 text-green-600" />
                    Financial Stability Score
                  </h4>
                  <div className="flex items-center gap-4 mb-4">
                    <div className="text-center">
                      <div className={`text-5xl font-bold ${getRiskColor(premiumData.financial_stability.risk_level)}`}>
                        {premiumData.financial_stability.score}
                      </div>
                      <div className="text-sm text-gray-600">out of {premiumData.financial_stability.max_score || 100}</div>
                    </div>
                    <div className="flex-1">
                      <div className="mb-2">
                        <div className="flex justify-between mb-1">
                          <span className="text-sm font-semibold">
                            {premiumData.financial_stability.risk_label || premiumData.financial_stability.risk_level}
                          </span>
                          <span className="text-sm text-gray-600">{premiumData.financial_stability.score}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                          <div
                            className={`h-3 rounded-full ${
                              premiumData.financial_stability.score >= 70 ? 'bg-green-500' :
                              premiumData.financial_stability.score >= 50 ? 'bg-yellow-500' :
                              premiumData.financial_stability.score >= 30 ? 'bg-orange-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${premiumData.financial_stability.score}%` }}
                          />
                        </div>
                      </div>
                      <p className="text-sm text-gray-700 mt-2">
                        {premiumData.financial_stability.risk_description || 'Financial stability assessment'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Historical Trends */}
                {premiumData.historical_trends && premiumData.historical_trends.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      <TrendingUp className="w-5 h-5" />
                      Historical Trend Analysis ({premiumData.historical_trends.length} data points)
                    </h4>
                    <div className="space-y-3">
                      {premiumData.historical_trends.map((trend, idx) => (
                        <div key={idx} className="border-l-4 border-purple-300 pl-4 py-2 bg-gray-50 rounded">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="font-semibold">
                                {new Date(trend.date).toLocaleDateString()}
                              </p>
                              <p className="text-sm text-gray-600">
                                Risk Level: {trend.risk_level}
                              </p>
                            </div>
                            <div className={`text-2xl font-bold ${getRiskColor(trend.risk_level)}`}>
                              {trend.score}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Full Officers List */}
                {premiumData.officers && premiumData.officers.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      <Users className="w-5 h-5" />
                      All Directors & Officers ({premiumData.officers.filter((o: any) => !o.resigned_on).length} active)
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {premiumData.officers.map((officer: any, idx: number) => (
                        <div key={idx} className={`border rounded p-3 ${officer.resigned_on ? 'bg-gray-50 opacity-60' : ''}`}>
                          <div className="font-medium">{officer.name}</div>
                          <div className="text-sm text-gray-600">
                            {officer.officer_role && <span className="mr-3">Role: {officer.officer_role}</span>}
                            {officer.appointed_on && (
                              <span>Appointed: {new Date(officer.appointed_on).toLocaleDateString()}</span>
                            )}
                          </div>
                          {officer.resigned_on && (
                            <div className="text-xs text-red-600 mt-1">
                              Resigned: {new Date(officer.resigned_on).toLocaleDateString()}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Full Charges List */}
                {premiumData.charges && premiumData.charges.length > 0 && (
                  <div>
                    <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      <Shield className="w-5 h-5" />
                      All Charges & Mortgages ({premiumData.charges.filter((c: any) => !c.satisfied_on).length} outstanding)
                    </h4>
                    <div className="space-y-2">
                      {premiumData.charges.map((charge: any, idx: number) => (
                        <div key={idx} className={`border rounded p-3 ${charge.satisfied_on ? 'bg-gray-50' : 'bg-red-50'}`}>
                          <div className="font-medium">{charge.charge_code || 'Charge'}</div>
                          <div className="text-sm text-gray-600">
                            {charge.created && (
                              <span className="mr-3">Created: {new Date(charge.created).toLocaleDateString()}</span>
                            )}
                            {charge.satisfied_on ? (
                              <span className="text-green-600">Satisfied: {new Date(charge.satisfied_on).toLocaleDateString()}</span>
                            ) : (
                              <span className="text-red-600 font-semibold">Outstanding</span>
                            )}
                          </div>
                          {charge.particulars && charge.particulars.description && (
                            <div className="text-xs text-gray-500 mt-1">
                              {charge.particulars.description}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

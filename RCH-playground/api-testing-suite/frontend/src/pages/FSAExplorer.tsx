import { useState, useEffect } from 'react';
import { Search, Shield, TrendingUp, History, Star, AlertCircle, CheckCircle, Lock, Unlock, Bell, FileText } from 'lucide-react';
import axios from 'axios';

interface Establishment {
  fhrsId: number;
  businessName: string;
  ratingValue?: number;
  ratingKey?: string;
  ratingDate?: string;
  addressLine1?: string;
  addressLine2?: string;
  postcode?: string;
  [key: string]: any;
}

interface BreakdownScores {
  hygiene?: number;
  structural?: number;
  confidence_in_management?: number;
  hygiene_label?: string;
  structural_label?: string;
  confidence_label?: string;
}

interface EstablishmentDetails extends Establishment {
  breakdown_scores?: BreakdownScores;
  scores?: any;
}

interface InspectionHistory {
  date: string;
  rating: number;
  rating_key?: string;
  breakdown_scores?: BreakdownScores;
  local_authority?: string;
  inspection_type?: string;
}

interface Trends {
  current_rating?: number;
  rating_date?: string;
  trend: string;
  history_count: number;
  consistency: string;
  breakdown_scores?: BreakdownScores;
  prediction: {
    predicted_rating?: number;
    predicted_label?: string;
    confidence: string;
  };
}

interface DiabetesScore {
  score: number;
  label: string;
  recommendation: string;
  breakdown: string[];
  max_score: number;
}

interface MonitoringAlert {
  type: 'critical' | 'warning' | 'info';
  message: string;
  severity: 'high' | 'medium' | 'low';
  date: string;
}

interface PremiumData {
  enhanced_history: InspectionHistory[];
  monitoring_alerts: MonitoringAlert[];
  trends: Trends;
  diabetes_score: DiabetesScore;
  monitoring_status: string;
  last_check: string;
  next_check: string;
}

type ReportTier = 'free' | 'professional' | 'premium';

export default function FSAExplorer() {
  const [loading, setLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<Establishment[]>([]);
  const [selectedEstablishment, setSelectedEstablishment] = useState<EstablishmentDetails | null>(null);
  const [inspectionHistory, setInspectionHistory] = useState<InspectionHistory[]>([]);
  const [trends, setTrends] = useState<Trends | null>(null);
  const [diabetesScore, setDiabetesScore] = useState<DiabetesScore | null>(null);
  const [premiumData, setPremiumData] = useState<PremiumData | null>(null);
  const [reportTier, setReportTier] = useState<ReportTier>('free');
  
  const [searchType, setSearchType] = useState<'name' | 'location'>('name');
  const [searchName, setSearchName] = useState('');
  const [searchLat, setSearchLat] = useState('');
  const [searchLng, setSearchLng] = useState('');
  const [maxDistance, setMaxDistance] = useState('1.0');

  const handleSearch = async (nameOverride?: string) => {
    setLoading(true);
    setSelectedEstablishment(null);
    setInspectionHistory([]);
    setTrends(null);
    
    try {
      const params: any = {};
      
      if (searchType === 'name') {
        // Ensure nameToUse is a string
        const nameToUse = String(nameOverride || searchName || '').trim();
        if (!nameToUse) {
          alert('Please enter a business name');
          setLoading(false);
          return;
        }
        params.name = nameToUse;
      } else {
        if (!searchLat || !searchLng) {
          alert('Please enter latitude and longitude');
          setLoading(false);
          return;
        }
        params.latitude = parseFloat(searchLat);
        params.longitude = parseFloat(searchLng);
        params.max_distance = parseFloat(maxDistance);
      }
      
      const response = await axios.get('/api/fsa/search', { params });
      const establishments = response.data.establishments || [];
      
      // Normalize field names from FSA API (PascalCase to camelCase)
      const normalizedEstablishments = establishments.map((est: any) => ({
        fhrsId: est.fhrsId || est.FHRSID || est.FhrsId,
        businessName: est.businessName || est.BusinessName || est.business_name,
        ratingValue: est.ratingValue !== undefined ? est.ratingValue : (est.RatingValue !== undefined ? parseInt(est.RatingValue) : undefined),
        ratingKey: est.ratingKey || est.RatingKey || est.rating_key,
        ratingDate: est.ratingDate || est.RatingDate || est.rating_date,
        addressLine1: est.addressLine1 || est.AddressLine1 || est.address_line1,
        addressLine2: est.addressLine2 || est.AddressLine2 || est.address_line2,
        postcode: est.postcode || est.PostCode || est.post_code,
        ...est // Keep all other fields
      }));
      
      // Debug: log first item structure if available
      if (normalizedEstablishments.length > 0) {
        console.log('FSA API response sample (original):', establishments[0]);
        console.log('FSA API response sample (normalized):', normalizedEstablishments[0]);
      }
      
      setSearchResults(normalizedEstablishments);
      
      // Show message if no results found
      if (normalizedEstablishments.length === 0 && response.data.message) {
        // Don't show alert for "no results" - it's not an error
        console.log(response.data.message);
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Unknown error occurred';
      alert(`Error: ${errorMessage}`);
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  // Auto-initialize search for testing "Meadows House Residential and Nursing Home"
  useEffect(() => {
    const testName = 'Meadows House Residential and Nursing Home';
    setSearchName(testName);
    // Small delay to ensure component is fully mounted and handleSearch is available
    const timer = setTimeout(() => {
      handleSearch(testName);
    }, 500);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Run only on mount - handleSearch is stable

  const handleViewDetails = async (fhrsId: number) => {
    setLoading(true);
    setReportTier('free'); // Reset to free tier
    setDiabetesScore(null);
    setPremiumData(null);
    
    try {
      const [detailsResponse, historyResponse, trendsResponse] = await Promise.all([
        axios.get(`/api/fsa/establishment/${fhrsId}`),
        axios.get(`/api/fsa/establishment/${fhrsId}/history`),
        axios.get(`/api/fsa/establishment/${fhrsId}/trends`)
      ]);
      
      // Normalize establishment data from PascalCase to camelCase
      const establishmentRaw = detailsResponse.data.establishment || detailsResponse.data;
      
      if (!establishmentRaw) {
        throw new Error('No establishment data received from API');
      }
      
      const normalizedEstablishment: EstablishmentDetails = {
        fhrsId: establishmentRaw.fhrsId || establishmentRaw.FHRSID || establishmentRaw.FhrsId || fhrsId,
        businessName: establishmentRaw.businessName || establishmentRaw.BusinessName || establishmentRaw.business_name || 'Unknown Business',
        ratingValue: establishmentRaw.ratingValue !== undefined 
          ? establishmentRaw.ratingValue 
          : (establishmentRaw.RatingValue !== undefined ? parseInt(String(establishmentRaw.RatingValue)) : undefined),
        ratingKey: establishmentRaw.ratingKey || establishmentRaw.RatingKey || establishmentRaw.rating_key,
        ratingDate: establishmentRaw.ratingDate || establishmentRaw.RatingDate || establishmentRaw.rating_date,
        addressLine1: establishmentRaw.addressLine1 || establishmentRaw.AddressLine1 || establishmentRaw.address_line1 || '',
        addressLine2: establishmentRaw.addressLine2 || establishmentRaw.AddressLine2 || establishmentRaw.address_line2 || '',
        postcode: establishmentRaw.postcode || establishmentRaw.PostCode || establishmentRaw.post_code || '',
        breakdown_scores: establishmentRaw.breakdown_scores || establishmentRaw.breakdownScores,
        scores: establishmentRaw.scores || establishmentRaw.Scores,
        ...establishmentRaw // Keep all other fields
      };
      
      // Debug: log establishment structure
      console.log('FSA Establishment details (original):', establishmentRaw);
      console.log('FSA Establishment details (normalized):', normalizedEstablishment);
      console.log('FSA History:', historyResponse.data.history);
      console.log('FSA Trends:', trendsResponse.data.trends);
      
      if (!normalizedEstablishment.fhrsId) {
        console.warn('Warning: fhrsId is missing in normalized establishment data');
      }
      
      setSelectedEstablishment(normalizedEstablishment);
      setInspectionHistory(historyResponse.data.history || []);
      setTrends(trendsResponse.data.trends || null);
    } catch (error: any) {
      console.error('Error loading establishment details:', error);
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadProfessionalData = async (fhrsId: number) => {
    if (reportTier !== 'professional' && reportTier !== 'premium') {
      setReportTier('professional');
    }
    
    setLoading(true);
    try {
      const response = await axios.get(`/api/fsa/establishment/${fhrsId}/diabetes-score`);
      setDiabetesScore(response.data.diabetes_score);
    } catch (error: any) {
      alert(`Error loading professional data: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadPremiumData = async (fhrsId: number) => {
    setReportTier('premium');
    setLoading(true);
    try {
      const response = await axios.get(`/api/fsa/establishment/${fhrsId}/premium-data`);
      setPremiumData(response.data);
      setDiabetesScore(response.data.diabetes_score);
      setTrends(response.data.trends);
      setInspectionHistory(response.data.enhanced_history || []);
    } catch (error: any) {
      alert(`Error loading premium data: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getRatingColor = (rating?: number) => {
    if (!rating) return 'text-gray-500';
    if (rating >= 5) return 'text-green-600';
    if (rating >= 4) return 'text-blue-600';
    if (rating >= 3) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getRatingLabel = (rating?: number) => {
    if (!rating) return 'Not Rated';
    if (rating === 5) return 'Excellent';
    if (rating === 4) return 'Good';
    if (rating === 3) return 'Satisfactory';
    if (rating === 2) return 'Needs Improvement';
    if (rating === 1) return 'Needs Significant Improvement';
    return 'Needs Urgent Improvement';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">FSA FHRS Explorer</h1>
        <p className="mt-2 text-gray-600">Search and analyze Food Hygiene Rating Scheme data for care homes</p>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="mb-4">
          <div className="flex gap-4 mb-4">
            <button
              onClick={() => setSearchType('name')}
              className={`px-4 py-2 rounded-md font-medium ${
                searchType === 'name'
                  ? 'bg-primary text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Search by Name
            </button>
            <button
              onClick={() => setSearchType('location')}
              className={`px-4 py-2 rounded-md font-medium ${
                searchType === 'location'
                  ? 'bg-primary text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Search by Location
            </button>
          </div>
        </div>

        {searchType === 'name' ? (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Business Name
              </label>
              <input
                type="text"
                value={searchName}
                onChange={(e) => setSearchName(e.target.value)}
                placeholder="e.g., Manor House Care"
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <div className="mt-2">
                <p className="text-xs text-gray-500 mb-2">Quick test examples (click to use - real UK care homes from CQC registry):</p>
                <div className="flex flex-wrap gap-2">
                  {[
                    { name: 'Kinross Residential Care Home', address: '201 Havant Road, Drayton, Portsmouth, Hampshire, PO6 1EE' },
                    { name: 'Meadows House Residential and Nursing Home', address: 'Cullum Welch Court, London, SE3 0PW' },
                    { name: 'Roborough House', address: 'Tamerton Road, Woolwell, Plymouth, Devon, PL6 7BQ' },
                    { name: 'Westgate House', address: '178 Romford Road, Forest Gate, London, E7 9HY' },
                    { name: 'Trowbridge Oaks', address: 'West Ashton Road, Trowbridge, Wiltshire, BA14 6DW' }
                  ].map((example) => (
                    <button
                      key={example.name}
                      type="button"
                      onClick={() => {
                        const name = String(example.name || '').trim();
                        if (name) {
                          setSearchName(name);
                          handleSearch(name);
                        }
                      }}
                      className="px-3 py-1 text-xs bg-blue-50 text-blue-700 border border-blue-200 rounded-md hover:bg-blue-100 transition-colors"
                      title={example.address}
                    >
                      {example.name}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Latitude
              </label>
              <input
                type="number"
                step="any"
                value={searchLat}
                onChange={(e) => setSearchLat(e.target.value)}
                placeholder="e.g., 52.4862"
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Longitude
              </label>
              <input
                type="number"
                step="any"
                value={searchLng}
                onChange={(e) => setSearchLng(e.target.value)}
                placeholder="e.g., -1.8904"
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Distance (km)
              </label>
              <input
                type="number"
                step="0.1"
                value={maxDistance}
                onChange={(e) => setMaxDistance(e.target.value)}
                placeholder="1.0"
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              />
            </div>
          </div>
        )}

        <button
          onClick={() => handleSearch()}
          disabled={loading}
          className="mt-4 w-full bg-primary text-white px-4 py-2 rounded-md hover:bg-primary-dark disabled:opacity-50 flex items-center justify-center"
        >
          <Search className="w-4 h-4 mr-2" />
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {/* Search Results */}
      {searchResults.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold">Search Results ({searchResults.length})</h2>
          </div>
          <div className="divide-y">
            {searchResults.map((establishment) => {
              // Handle different field name variations from FSA API
              const fhrsId = establishment.fhrsId || establishment.FHRSID || establishment.FhrsId;
              const businessName = establishment.businessName 
                || establishment.BusinessName 
                || establishment.business_name
                || 'Unknown Business';
              const addressLine1 = establishment.addressLine1 
                || establishment.AddressLine1 
                || establishment.address_line1
                || '';
              const addressLine2 = establishment.addressLine2 
                || establishment.AddressLine2 
                || establishment.address_line2
                || '';
              const postcode = establishment.postcode 
                || establishment.PostCode 
                || establishment.post_code
                || '';
              const ratingValue = establishment.ratingValue !== undefined 
                ? establishment.ratingValue 
                : (establishment.RatingValue !== undefined ? parseInt(establishment.RatingValue) : undefined);
              const ratingDate = establishment.ratingDate 
                || establishment.RatingDate 
                || establishment.rating_date;
              
              return (
                <div
                  key={fhrsId || Math.random()}
                  className="p-6 hover:bg-gray-50 cursor-pointer"
                  onClick={() => fhrsId && handleViewDetails(fhrsId)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {businessName}
                      </h3>
                      {(addressLine1 || postcode) && (
                        <p className="text-sm text-gray-600 mt-1">
                          {addressLine1}
                          {addressLine2 && `, ${addressLine2}`}
                          {postcode && `, ${postcode}`}
                        </p>
                      )}
                    </div>
                    {ratingValue !== undefined && (
                      <div className="ml-4 text-right">
                        <div className={`text-2xl font-bold ${getRatingColor(ratingValue)}`}>
                          {ratingValue}/5
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {getRatingLabel(ratingValue)}
                        </div>
                        {ratingDate && (
                          <div className="text-xs text-gray-400 mt-1">
                            {new Date(ratingDate).toLocaleDateString()}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Establishment Details */}
      {selectedEstablishment && (
        <div className="space-y-6">
          {/* Report Tier Selector */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold mb-4">{selectedEstablishment.businessName}</h2>
            
            {/* Tier Selection */}
            <div className="mb-6 border-b pb-4">
              <p className="text-sm text-gray-600 mb-3">Select Report Tier:</p>
              <div className="flex gap-4">
                <button
                  onClick={() => {
                    setReportTier('free');
                    setDiabetesScore(null);
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
                  onClick={() => handleLoadProfessionalData(selectedEstablishment.fhrsId)}
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
                  onClick={() => handleLoadPremiumData(selectedEstablishment.fhrsId)}
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
                <span className="text-sm text-gray-500">Basic Information</span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Food Hygiene Rating</p>
                  <div className="flex items-center gap-3">
                    <span className={`text-4xl font-bold ${getRatingColor(selectedEstablishment.ratingValue)}`}>
                      {selectedEstablishment.ratingValue}/5
                    </span>
                    <div>
                      <p className="font-semibold">{getRatingLabel(selectedEstablishment.ratingValue)}</p>
                      {selectedEstablishment.ratingDate && (
                        <p className="text-sm text-gray-500">
                          Inspected: {new Date(selectedEstablishment.ratingDate).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Address</p>
                  <p className="font-medium">
                    {selectedEstablishment.addressLine1}
                    {selectedEstablishment.addressLine2 && `, ${selectedEstablishment.addressLine2}`}
                    {selectedEstablishment.postcode && `, ${selectedEstablishment.postcode}`}
                  </p>
                </div>
              </div>
              
              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                <p className="text-sm text-blue-800">
                  💡 <strong>Upgrade to Professional</strong> for detailed breakdown scores and diabetes suitability analysis
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
                  <span className="text-sm text-gray-500">Detailed Analysis</span>
                </div>

                {/* Basic Rating (same as FREE) */}
                <div className="mb-6">
                  <p className="text-sm text-gray-600 mb-1">Food Hygiene Rating</p>
                  <div className="flex items-center gap-3">
                    <span className={`text-4xl font-bold ${getRatingColor(selectedEstablishment.ratingValue)}`}>
                      {selectedEstablishment.ratingValue}/5
                    </span>
                    <div>
                      <p className="font-semibold">{getRatingLabel(selectedEstablishment.ratingValue)}</p>
                      {selectedEstablishment.ratingDate && (
                        <p className="text-sm text-gray-500">
                          Inspected: {new Date(selectedEstablishment.ratingDate).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Breakdown Scores */}
                {selectedEstablishment.breakdown_scores && (
                  <div className="mb-6">
                    <h4 className="text-lg font-semibold mb-3">Detailed Breakdown Scores</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="border-l-4 border-blue-500 pl-4">
                        <p className="text-sm text-gray-600 mb-1">Hygiene</p>
                        <p className="text-2xl font-bold text-blue-600">
                          {selectedEstablishment.breakdown_scores.hygiene != null && typeof selectedEstablishment.breakdown_scores.hygiene === 'number'
                            ? `${selectedEstablishment.breakdown_scores.hygiene}/20`
                            : 'N/A'}
                        </p>
                        {selectedEstablishment.breakdown_scores.hygiene_label && (
                          <p className="text-sm text-gray-600 mt-1">
                            {selectedEstablishment.breakdown_scores.hygiene_label}
                          </p>
                        )}
                      </div>
                      <div className="border-l-4 border-green-500 pl-4">
                        <p className="text-sm text-gray-600 mb-1">Structural</p>
                        <p className="text-2xl font-bold text-green-600">
                          {selectedEstablishment.breakdown_scores.structural != null && typeof selectedEstablishment.breakdown_scores.structural === 'number'
                            ? `${selectedEstablishment.breakdown_scores.structural}/20`
                            : 'N/A'}
                        </p>
                        {selectedEstablishment.breakdown_scores.structural_label && (
                          <p className="text-sm text-gray-600 mt-1">
                            {selectedEstablishment.breakdown_scores.structural_label}
                          </p>
                        )}
                      </div>
                      <div className="border-l-4 border-purple-500 pl-4">
                        <p className="text-sm text-gray-600 mb-1">Management</p>
                        <p className="text-2xl font-bold text-purple-600">
                          {selectedEstablishment.breakdown_scores.confidence_in_management != null && typeof selectedEstablishment.breakdown_scores.confidence_in_management === 'number'
                            ? `${selectedEstablishment.breakdown_scores.confidence_in_management}/30`
                            : 'N/A'}
                        </p>
                        {selectedEstablishment.breakdown_scores.confidence_label && (
                          <p className="text-sm text-gray-600 mt-1">
                            {selectedEstablishment.breakdown_scores.confidence_label}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Diabetes Suitability Score */}
                {diabetesScore && (
                  <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border border-blue-200">
                    <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      <Star className="w-5 h-5 text-yellow-500" />
                      Diabetes Suitability Score
                    </h4>
                    <div className="flex items-center gap-4 mb-4">
                      <div className="text-center">
                        <div className="text-5xl font-bold text-blue-600">
                          {diabetesScore.score}
                        </div>
                        <div className="text-sm text-gray-600">out of {diabetesScore.max_score}</div>
                      </div>
                      <div className="flex-1">
                        <div className="mb-2">
                          <div className="flex justify-between mb-1">
                            <span className="text-sm font-semibold">{diabetesScore.label}</span>
                            <span className="text-sm text-gray-600">{diabetesScore.score}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-3">
                            <div
                              className={`h-3 rounded-full ${
                                diabetesScore.score >= 75 ? 'bg-green-500' :
                                diabetesScore.score >= 60 ? 'bg-blue-500' :
                                diabetesScore.score >= 45 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${diabetesScore.score}%` }}
                            />
                          </div>
                        </div>
                        <p className="text-sm text-gray-700 mt-2">{diabetesScore.recommendation}</p>
                      </div>
                    </div>
                    {diabetesScore.breakdown && diabetesScore.breakdown.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-blue-200">
                        <p className="text-sm font-semibold mb-2">Score Breakdown:</p>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {diabetesScore.breakdown.map((detail, idx) => (
                            <li key={idx}>• {detail}</li>
                          ))}
                        </ul>
                      </div>
                    )}
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
                {diabetesScore && (
                  <div className="mb-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border border-blue-200">
                    <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      <Star className="w-5 h-5 text-yellow-500" />
                      Diabetes Suitability Score
                    </h4>
                    <div className="flex items-center gap-4 mb-4">
                      <div className="text-center">
                        <div className="text-5xl font-bold text-blue-600">
                          {diabetesScore.score}
                        </div>
                        <div className="text-sm text-gray-600">out of {diabetesScore.max_score}</div>
                      </div>
                      <div className="flex-1">
                        <div className="mb-2">
                          <div className="flex justify-between mb-1">
                            <span className="text-sm font-semibold">{diabetesScore.label}</span>
                            <span className="text-sm text-gray-600">{diabetesScore.score}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-3">
                            <div
                              className={`h-3 rounded-full ${
                                diabetesScore.score >= 75 ? 'bg-green-500' :
                                diabetesScore.score >= 60 ? 'bg-blue-500' :
                                diabetesScore.score >= 45 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${diabetesScore.score}%` }}
                            />
                          </div>
                        </div>
                        <p className="text-sm text-gray-700 mt-2">{diabetesScore.recommendation}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Enhanced History */}
                {premiumData.enhanced_history && premiumData.enhanced_history.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      <History className="w-5 h-5" />
                      Historical Trend Analysis ({premiumData.enhanced_history.length} inspections)
                    </h4>
                    <div className="space-y-3">
                      {premiumData.enhanced_history.map((inspection, idx) => (
                        <div key={idx} className="border-l-4 border-purple-300 pl-4 py-2 bg-gray-50 rounded">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="font-semibold">
                                {inspection.date ? new Date(inspection.date).toLocaleDateString() : 'Unknown Date'}
                              </p>
                              <p className="text-sm text-gray-600">
                                {inspection.inspection_type || 'Inspection'}
                                {inspection.local_authority && ` • ${inspection.local_authority}`}
                              </p>
                            </div>
                            {inspection.rating !== undefined && (
                              <div className={`text-2xl font-bold ${getRatingColor(inspection.rating)}`}>
                                {inspection.rating}/5
                              </div>
                            )}
                          </div>
                          {inspection.breakdown_scores && (
                            <div className="mt-2 grid grid-cols-3 gap-4 text-sm">
                              {inspection.breakdown_scores.hygiene != null && typeof inspection.breakdown_scores.hygiene === 'number' && (
                                <div>
                                  <span className="text-gray-600">Hygiene: </span>
                                  <span className="font-semibold">{inspection.breakdown_scores.hygiene}/20</span>
                                </div>
                              )}
                              {inspection.breakdown_scores.structural != null && typeof inspection.breakdown_scores.structural === 'number' && (
                                <div>
                                  <span className="text-gray-600">Structural: </span>
                                  <span className="font-semibold">{inspection.breakdown_scores.structural}/20</span>
                                </div>
                              )}
                              {inspection.breakdown_scores.confidence_in_management != null && typeof inspection.breakdown_scores.confidence_in_management === 'number' && (
                                <div>
                                  <span className="text-gray-600">Management: </span>
                                  <span className="font-semibold">{inspection.breakdown_scores.confidence_in_management}/30</span>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Trends & Predictions */}
                {premiumData.trends && (
                  <div className="bg-white rounded-lg shadow p-6">
                    <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
                      <TrendingUp className="w-5 h-5" />
                      Trend Analysis & Predictions
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <p className="text-sm text-gray-600 mb-2">Current Status</p>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span>Trend:</span>
                            <span className={`font-semibold ${
                              premiumData.trends.trend === 'improving' ? 'text-green-600' :
                              premiumData.trends.trend === 'declining' ? 'text-red-600' : 'text-gray-600'
                            }`}>
                              {premiumData.trends.trend.charAt(0).toUpperCase() + premiumData.trends.trend.slice(1)}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span>Consistency:</span>
                            <span className="font-semibold">{premiumData.trends.consistency}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>History Records:</span>
                            <span className="font-semibold">{premiumData.trends.history_count}</span>
                          </div>
                        </div>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 mb-2">Prediction</p>
                        {premiumData.trends.prediction.predicted_rating !== undefined ? (
                          <div className="space-y-2">
                            <div className="flex justify-between">
                              <span>Next Rating:</span>
                              <span className="text-xl font-bold">
                                {premiumData.trends.prediction.predicted_rating}/5
                              </span>
                            </div>
                            {premiumData.trends.prediction.predicted_label && (
                              <div className="flex justify-between">
                                <span>Label:</span>
                                <span className="font-semibold">{premiumData.trends.prediction.predicted_label}</span>
                              </div>
                            )}
                            <div className="flex justify-between">
                              <span>Confidence:</span>
                              <span className={`font-semibold ${
                                premiumData.trends.prediction.confidence === 'high' ? 'text-green-600' :
                                premiumData.trends.prediction.confidence === 'medium' ? 'text-yellow-600' : 'text-gray-600'
                              }`}>
                                {premiumData.trends.prediction.confidence.charAt(0).toUpperCase() + premiumData.trends.prediction.confidence.slice(1)}
                              </span>
                            </div>
                          </div>
                        ) : (
                          <p className="text-gray-500">Insufficient data for prediction</p>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Basic Info (shown for all tiers) */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-semibold mb-4">Basic Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Address</p>
                <p className="font-medium">
                  {selectedEstablishment.addressLine1}
                  {selectedEstablishment.addressLine2 && `, ${selectedEstablishment.addressLine2}`}
                  {selectedEstablishment.postcode && `, ${selectedEstablishment.postcode}`}
                </p>
              </div>
              {selectedEstablishment.ratingValue !== undefined && (
                <div>
                  <p className="text-sm text-gray-600">Overall Rating</p>
                  <div className="flex items-center gap-2">
                    <span className={`text-3xl font-bold ${getRatingColor(selectedEstablishment.ratingValue)}`}>
                      {selectedEstablishment.ratingValue}/5
                    </span>
                    <span className="text-gray-600">({getRatingLabel(selectedEstablishment.ratingValue)})</span>
                  </div>
                  {selectedEstablishment.ratingDate && (
                    <p className="text-sm text-gray-500 mt-1">
                      Last inspection: {new Date(selectedEstablishment.ratingDate).toLocaleDateString()}
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


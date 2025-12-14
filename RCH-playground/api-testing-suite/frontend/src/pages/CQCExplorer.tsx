import { useState, useEffect } from 'react';
import { Search, MapPin, FileText, Users, Calendar, Filter, X, Eye } from 'lucide-react';
import axios from 'axios';

interface Location {
  locationId: string;
  name: string;
  postcode?: string;
  address?: string;
  overallRating?: string;
  [key: string]: any;
}

interface Provider {
  providerId: string;
  name: string;
  postcode?: string;
  [key: string]: any;
}

interface LocationDetails {
  locationId: string;
  name: string;
  address?: string;
  postcode?: string;
  overallRating?: string;
  currentRatings?: any;
  specialisms?: any[];
  [key: string]: any;
}

type SearchMode = 'locations' | 'providers' | 'changes';

interface CQCModeInfo {
  mode: 'sandbox' | 'production';
  partner_code: string | null;
  rate_limit: string;
  description: string;
}

export default function CQCExplorer() {
  const [searchMode, setSearchMode] = useState<SearchMode>('locations');
  const [locationViewMode, setLocationViewMode] = useState<'region' | 'details'>('region');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<Location[] | Provider[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<LocationDetails | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [modeInfo, setModeInfo] = useState<CQCModeInfo | null>(null);
  
  // Location details search
  const [locationIdSearch, setLocationIdSearch] = useState('');
  
  // Location search filters
  const [locationFilters, setLocationFilters] = useState({
    careHome: undefined as boolean | undefined,
    localAuthority: '',
    region: '',
    postcode: '',
    overallRating: '',
    inspectionDirectorate: '',
    constituency: '',
    onspdCcgCode: '',
    onspdCcgName: '',
    odsCcgCode: '',
    odsCcgName: '',
    gacServiceTypeDescription: '',
    primaryInspectionCategoryCode: '',
    primaryInspectionCategoryName: '',
    nonPrimaryInspectionCategoryCode: '',
    nonPrimaryInspectionCategoryName: '',
    regulatedActivity: '',
    reportType: '',
    pageSize: 100,
  });

  // Provider search filters
  const [providerFilters, setProviderFilters] = useState({
    localAuthority: '',
    region: '',
    overallRating: '',
    inspectionDirectorate: '',
    pageSize: 100,
  });

  // Changes filters
  const [changesFilters, setChangesFilters] = useState({
    organisationType: 'location',
    startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0],
  });

  // Load CQC mode info on component mount
  useEffect(() => {
    const loadModeInfo = async () => {
      try {
        const response = await axios.get('/api/cqc/status');
        if (response.data.status === 'success') {
          setModeInfo({
            mode: response.data.mode,
            partner_code: response.data.partner_code,
            rate_limit: response.data.rate_limit,
            description: response.data.description
          });
        }
      } catch (error) {
        console.error('Failed to load CQC mode info:', error);
      }
    };
    loadModeInfo();
  }, []);

  const handleLocationSearch = async () => {
    setLoading(true);
    setSelectedLocation(null);
    setResults([]); // Clear previous results before new search
    try {
      const params: any = {
        page_size: locationFilters.pageSize,
      };
      
      if (locationFilters.careHome !== undefined) {
        params.care_home = locationFilters.careHome;
      }
      if (locationFilters.localAuthority) params.local_authority = locationFilters.localAuthority;
      if (locationFilters.region) params.region = locationFilters.region;
      if (locationFilters.postcode) params.postcode = locationFilters.postcode;
      if (locationFilters.overallRating) params.overall_rating = locationFilters.overallRating;
      if (locationFilters.inspectionDirectorate) params.inspection_directorate = locationFilters.inspectionDirectorate;
      if (locationFilters.constituency) params.constituency = locationFilters.constituency;
      if (locationFilters.onspdCcgCode) params.onspd_ccg_code = locationFilters.onspdCcgCode;
      if (locationFilters.onspdCcgName) params.onspd_ccg_name = locationFilters.onspdCcgName;
      if (locationFilters.odsCcgCode) params.ods_ccg_code = locationFilters.odsCcgCode;
      if (locationFilters.odsCcgName) params.ods_ccg_name = locationFilters.odsCcgName;
      if (locationFilters.gacServiceTypeDescription) params.gac_service_type_description = locationFilters.gacServiceTypeDescription;
      if (locationFilters.primaryInspectionCategoryCode) params.primary_inspection_category_code = locationFilters.primaryInspectionCategoryCode;
      if (locationFilters.primaryInspectionCategoryName) params.primary_inspection_category_name = locationFilters.primaryInspectionCategoryName;
      if (locationFilters.nonPrimaryInspectionCategoryCode) params.non_primary_inspection_category_code = locationFilters.nonPrimaryInspectionCategoryCode;
      if (locationFilters.nonPrimaryInspectionCategoryName) params.non_primary_inspection_category_name = locationFilters.nonPrimaryInspectionCategoryName;
      if (locationFilters.regulatedActivity) params.regulated_activity = locationFilters.regulatedActivity;
      if (locationFilters.reportType) params.report_type = locationFilters.reportType;

      const response = await axios.get('/api/cqc/locations/search', { params });
      const locations = response.data.locations || [];
      
      // Debug: log first item structure if available
      if (locations.length > 0) {
        console.log('CQC API response sample:', locations[0]);
      }
      
      setResults(locations);
      // Update mode info from response
      if (response.data.mode) {
        setModeInfo({
          mode: response.data.mode,
          partner_code: response.data.partner_code,
          rate_limit: response.data.rate_limit,
          description: response.data.mode === 'production' 
            ? 'Production mode with Partner Code - Higher rate limits and priority support'
            : 'Sandbox mode without Partner Code - Limited rate limits, suitable for testing'
        });
      }
    } catch (error: any) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleProviderSearch = async () => {
    setLoading(true);
    setSelectedLocation(null);
    try {
      const params: any = {
        page_size: providerFilters.pageSize,
      };
      
      if (providerFilters.localAuthority) params.local_authority = providerFilters.localAuthority;
      if (providerFilters.region) params.region = providerFilters.region;
      if (providerFilters.overallRating) params.overall_rating = providerFilters.overallRating;
      if (providerFilters.inspectionDirectorate) params.inspection_directorate = providerFilters.inspectionDirectorate;

      const response = await axios.get('/api/cqc/providers/search', { params });
      setResults(response.data.providers || []);
      // Update mode info from response
      if (response.data.mode) {
        setModeInfo({
          mode: response.data.mode,
          partner_code: response.data.partner_code,
          rate_limit: response.data.rate_limit,
          description: response.data.mode === 'production' 
            ? 'Production mode with Partner Code - Higher rate limits and priority support'
            : 'Sandbox mode without Partner Code - Limited rate limits, suitable for testing'
        });
      }
    } catch (error: any) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleChangesSearch = async () => {
    setLoading(true);
    setSelectedLocation(null);
    try {
      const response = await axios.get('/api/cqc/changes', {
        params: {
          organisation_type: changesFilters.organisationType,
          start_date: changesFilters.startDate,
          end_date: changesFilters.endDate,
        },
      });
      setResults(response.data.changes || []);
    } catch (error: any) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleViewLocationDetails = async (locationId: string) => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/cqc/locations/${locationId}`);
      setSelectedLocation(response.data.location);
      setResults([]); // Clear region search results when viewing details
    } catch (error: any) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLocationIdSearch = async () => {
    if (!locationIdSearch.trim()) {
      alert('Please enter a Location ID');
      return;
    }
    await handleViewLocationDetails(locationIdSearch.trim());
  };

  const handleViewReports = async (locationId: string) => {
    try {
      const response = await axios.get(`/api/cqc/locations/${locationId}/reports`);
      if (response.data.reports && response.data.reports.length > 0) {
        // CQC API uses 'linkId' field, not 'inspectionReportLinkId'
        const reportId = response.data.reports[0].linkId || response.data.reports[0].inspectionReportLinkId;
        if (reportId) {
          window.open(`/api/cqc/reports/${reportId}?plain_text=true`, '_blank');
        } else {
          alert('Report ID not found in response');
        }
      } else {
        alert('No reports available for this location');
      }
    } catch (error: any) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleSearch = () => {
    if (searchMode === 'locations') {
      handleLocationSearch();
    } else if (searchMode === 'providers') {
      handleProviderSearch();
    } else {
      handleChangesSearch();
    }
  };

  const clearFilters = () => {
    if (searchMode === 'locations') {
      setLocationFilters({
        careHome: undefined,
        localAuthority: '',
        region: '',
        postcode: '',
        overallRating: '',
        inspectionDirectorate: '',
        constituency: '',
        onspdCcgCode: '',
        onspdCcgName: '',
        odsCcgCode: '',
        odsCcgName: '',
        gacServiceTypeDescription: '',
        primaryInspectionCategoryCode: '',
        primaryInspectionCategoryName: '',
        nonPrimaryInspectionCategoryCode: '',
        nonPrimaryInspectionCategoryName: '',
        regulatedActivity: '',
        reportType: '',
        pageSize: 100,
      });
    } else if (searchMode === 'providers') {
      setProviderFilters({
        localAuthority: '',
        region: '',
        overallRating: '',
        inspectionDirectorate: '',
        pageSize: 100,
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">CQC Explorer</h1>
          {modeInfo && (
            <div className={`px-4 py-2 rounded-lg ${
              modeInfo.mode === 'production' 
                ? 'bg-green-100 text-green-800 border border-green-300' 
                : 'bg-yellow-100 text-yellow-800 border border-yellow-300'
            }`}>
              <div className="flex items-center gap-2">
                <span className="font-semibold">
                  {modeInfo.mode === 'production' ? '🔒 Production Mode' : '🧪 Sandbox Mode'}
                </span>
                <span className="text-sm">({modeInfo.rate_limit})</span>
              </div>
              {modeInfo.mode === 'sandbox' && (
                <div className="text-xs mt-1">
                  Partner Code is required. Register at{' '}
                  <a 
                    href="https://api-portal.service.cqc.org.uk/" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    CQC API Portal
                  </a>
                  {' '}to get access, then add it in API Config.
                </div>
              )}
            </div>
          )}
        </div>
        <p className="mt-2 text-gray-600">Search and explore CQC locations, providers, and changes</p>
      </div>

      {/* Mode Selection */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex gap-4">
          <button
            onClick={() => {
              setSearchMode('locations');
              setResults([]);
              setSelectedLocation(null);
            }}
            className={`flex items-center px-4 py-2 rounded-md font-medium ${
              searchMode === 'locations'
                ? 'bg-primary text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <MapPin className="w-4 h-4 mr-2" />
            Locations
          </button>
          <button
            onClick={() => {
              setSearchMode('providers');
              setResults([]);
              setSelectedLocation(null);
            }}
            className={`flex items-center px-4 py-2 rounded-md font-medium ${
              searchMode === 'providers'
                ? 'bg-primary text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Users className="w-4 h-4 mr-2" />
            Providers
          </button>
          <button
            onClick={() => {
              setSearchMode('changes');
              setResults([]);
              setSelectedLocation(null);
            }}
            className={`flex items-center px-4 py-2 rounded-md font-medium ${
              searchMode === 'changes'
                ? 'bg-primary text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Calendar className="w-4 h-4 mr-2" />
            Changes
          </button>
        </div>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Search Filters</h2>
          <div className="flex gap-2">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
            >
              <Filter className="w-4 h-4 mr-1" />
              {showFilters ? 'Hide' : 'Show'} Filters
            </button>
            <button
              onClick={clearFilters}
              className="flex items-center px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
            >
              <X className="w-4 h-4 mr-1" />
              Clear
            </button>
          </div>
        </div>

        {searchMode === 'locations' && (
          <div className="space-y-4">
            {/* View Mode Toggle */}
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setLocationViewMode('region');
                    setSelectedLocation(null);
                    setResults([]);
                  }}
                  className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    locationViewMode === 'region'
                      ? 'bg-primary text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <MapPin className="w-4 h-4 inline mr-2" />
                  Search by Region
                </button>
                <button
                  onClick={() => {
                    setLocationViewMode('details');
                    setResults([]);
                  }}
                  className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    locationViewMode === 'details'
                      ? 'bg-primary text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <Eye className="w-4 h-4 inline mr-2" />
                  Location Details
                </button>
              </div>
            </div>

            {locationViewMode === 'region' ? (
              /* Region Search */
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-blue-900 mb-3">
                  <MapPin className="w-4 h-4 inline mr-1" />
                  Search All Care Homes by Region
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Region or City Name
                    </label>
                    <input
                      type="text"
                      value={locationFilters.region}
                      onChange={(e) =>
                        setLocationFilters({ ...locationFilters, region: e.target.value })
                      }
                      placeholder="e.g., Birmingham, London, West Midlands, South East"
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-primary focus:border-primary"
                      onKeyPress={(e) => e.key === 'Enter' && handleLocationSearch()}
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Enter region name (e.g., "West Midlands") or city name (e.g., "Birmingham")
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Postcode (Optional)
                    </label>
                    <input
                      type="text"
                      value={locationFilters.postcode}
                      onChange={(e) =>
                        setLocationFilters({ ...locationFilters, postcode: e.target.value })
                      }
                      placeholder="e.g., B1 1AA, SW1A 1AA"
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-primary focus:border-primary"
                      onKeyPress={(e) => e.key === 'Enter' && handleLocationSearch()}
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Enter UK postcode (with or without spaces)
                    </p>
                  </div>
                </div>
                
                {/* Quick Test Examples for Region Search */}
                <div className="mt-4 pt-4 border-t border-blue-300">
                  <p className="text-xs text-gray-600 mb-2 font-medium">
                    Quick test examples - Search all care homes in region (click to search):
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {[
                      { region: 'Birmingham', description: 'All care homes in Birmingham' },
                      { region: 'London', description: 'All care homes in London' },
                      { region: 'West Midlands', description: 'All care homes in West Midlands' },
                      { region: 'South East', description: 'All care homes in South East' },
                      { region: 'Manchester', description: 'All care homes in Manchester' }
                    ].map((example) => (
                      <button
                        key={example.region}
                        type="button"
                        onClick={async () => {
                          // Use localAuthority for Birmingham, region for others
                          if (example.region === 'Birmingham') {
                            setLocationFilters({
                              ...locationFilters,
                              localAuthority: 'Birmingham',
                              region: '',
                              postcode: '',
                              careHome: true
                            });
                          } else {
                            setLocationFilters({
                              ...locationFilters,
                              region: example.region,
                              localAuthority: '',
                              postcode: '',
                              careHome: true
                            });
                          }
                          // Small delay to ensure state is updated
                          await new Promise(resolve => setTimeout(resolve, 50));
                          handleLocationSearch();
                        }}
                        className="px-3 py-1 text-xs bg-white text-blue-700 border border-blue-300 rounded-md hover:bg-blue-100 transition-colors shadow-sm"
                        title={example.description}
                      >
                        {example.region}
                      </button>
                    ))}
                  </div>
                </div>
                
                <div className="mt-4 flex justify-end">
                  <button
                    onClick={handleLocationSearch}
                    disabled={loading}
                    className="inline-flex items-center px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary-dark disabled:opacity-50"
                  >
                    <Search className="w-4 h-4 mr-2" />
                    {loading ? 'Searching...' : 'Search All Care Homes'}
                  </button>
                </div>
              </div>
            ) : (
              /* Location Details Search */
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-green-900 mb-3">
                  <Eye className="w-4 h-4 inline mr-1" />
                  Get Detailed Information for a Specific Care Home
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Location ID *
                    </label>
                    <input
                      type="text"
                      value={locationIdSearch}
                      onChange={(e) => setLocationIdSearch(e.target.value)}
                      placeholder="e.g., 1-12345678901 (CQC Location ID)"
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-primary focus:border-primary"
                      onKeyPress={(e) => e.key === 'Enter' && handleLocationIdSearch()}
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Enter CQC Location ID (format: 1-XXXXXXXXXXX). You can find Location ID in search results.
                    </p>
                  </div>

                  {/* Quick Test Examples for Location Details */}
                  <div className="pt-4 border-t border-green-300">
                    <p className="text-xs text-gray-600 mb-2 font-medium">
                      Quick test examples - Get details for specific care homes (click to load):
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {[
                        { 
                          locationId: '1-10224972832', 
                          name: 'Westgate House Care Home',
                          description: 'London care home - Barchester Healthcare'
                        },
                        { 
                          locationId: '1-135968358', 
                          name: 'The Orchards Care Home',
                          description: 'Birmingham care home - HC-One'
                        },
                        { 
                          locationId: '1-126668028', 
                          name: 'Trowbridge Oaks Care Home',
                          description: 'Trowbridge care home - Bupa'
                        },
                        { 
                          locationId: '1-10363767558', 
                          name: 'Lynde House Care Home',
                          description: 'Twickenham care home - Barchester Healthcare'
                        }
                      ].map((example) => (
                        <button
                          key={example.locationId}
                          type="button"
                          onClick={() => {
                            setLocationIdSearch(example.locationId);
                            handleViewLocationDetails(example.locationId);
                          }}
                          className="px-3 py-1 text-xs bg-white text-green-700 border border-green-300 rounded-md hover:bg-green-100 transition-colors shadow-sm"
                          title={`${example.name} - ${example.description}`}
                        >
                          {example.name}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="flex justify-end">
                    <button
                      onClick={handleLocationIdSearch}
                      disabled={loading || !locationIdSearch.trim()}
                      className="inline-flex items-center px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Eye className="w-4 h-4 mr-2" />
                      {loading ? 'Loading...' : 'Get Details'}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {showFilters && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Care Home Type
                  </label>
                  <select
                    value={locationFilters.careHome === undefined ? '' : locationFilters.careHome.toString()}
                    onChange={(e) =>
                      setLocationFilters({
                        ...locationFilters,
                        careHome: e.target.value === '' ? undefined : e.target.value === 'true',
                      })
                    }
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="">All Locations</option>
                    <option value="true">Care Homes Only</option>
                    <option value="false">Exclude Care Homes</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Local Authority
                  </label>
                  <input
                    type="text"
                    value={locationFilters.localAuthority}
                    onChange={(e) =>
                      setLocationFilters({ ...locationFilters, localAuthority: e.target.value })
                    }
                    placeholder="e.g., Birmingham City Council"
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Overall Rating
                  </label>
                  <select
                    value={locationFilters.overallRating}
                    onChange={(e) =>
                      setLocationFilters({ ...locationFilters, overallRating: e.target.value })
                    }
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="">Any Rating</option>
                    <option value="Outstanding">Outstanding</option>
                    <option value="Good">Good</option>
                    <option value="Requires improvement">Requires improvement</option>
                    <option value="Inadequate">Inadequate</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Inspection Directorate
                  </label>
                  <select
                    value={locationFilters.inspectionDirectorate}
                    onChange={(e) =>
                      setLocationFilters({
                        ...locationFilters,
                        inspectionDirectorate: e.target.value,
                      })
                    }
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="">Any</option>
                    <option value="Adult social care">Adult social care</option>
                    <option value="Hospitals">Hospitals</option>
                    <option value="Primary medical services">Primary medical services</option>
                    <option value="Unspecified">Unspecified</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Constituency
                  </label>
                  <input
                    type="text"
                    value={locationFilters.constituency}
                    onChange={(e) =>
                      setLocationFilters({ ...locationFilters, constituency: e.target.value })
                    }
                    placeholder="Parliamentary constituency"
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    ONSPD CCG Code
                  </label>
                  <input
                    type="text"
                    value={locationFilters.onspdCcgCode}
                    onChange={(e) =>
                      setLocationFilters({ ...locationFilters, onspdCcgCode: e.target.value })
                    }
                    placeholder="e.g., 09A"
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    ONSPD CCG Name
                  </label>
                  <input
                    type="text"
                    value={locationFilters.onspdCcgName}
                    onChange={(e) =>
                      setLocationFilters({ ...locationFilters, onspdCcgName: e.target.value })
                    }
                    placeholder="Clinical Commissioning Group name"
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    ODS CCG Code
                  </label>
                  <input
                    type="text"
                    value={locationFilters.odsCcgCode}
                    onChange={(e) =>
                      setLocationFilters({ ...locationFilters, odsCcgCode: e.target.value })
                    }
                    placeholder="ODS CCG code"
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    ODS CCG Name
                  </label>
                  <input
                    type="text"
                    value={locationFilters.odsCcgName}
                    onChange={(e) =>
                      setLocationFilters({ ...locationFilters, odsCcgName: e.target.value })
                    }
                    placeholder="ODS CCG name"
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    GAC Service Type
                  </label>
                  <input
                    type="text"
                    value={locationFilters.gacServiceTypeDescription}
                    onChange={(e) =>
                      setLocationFilters({ ...locationFilters, gacServiceTypeDescription: e.target.value })
                    }
                    placeholder="Service type description"
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Primary Inspection Category Code
                  </label>
                  <input
                    type="text"
                    value={locationFilters.primaryInspectionCategoryCode}
                    onChange={(e) =>
                      setLocationFilters({ ...locationFilters, primaryInspectionCategoryCode: e.target.value })
                    }
                    placeholder="e.g., H1"
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Primary Inspection Category Name
                  </label>
                  <input
                    type="text"
                    value={locationFilters.primaryInspectionCategoryName}
                    onChange={(e) =>
                      setLocationFilters({ ...locationFilters, primaryInspectionCategoryName: e.target.value })
                    }
                    placeholder="Category name"
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Non-Primary Inspection Category Code
                  </label>
                  <input
                    type="text"
                    value={locationFilters.nonPrimaryInspectionCategoryCode}
                    onChange={(e) =>
                      setLocationFilters({ ...locationFilters, nonPrimaryInspectionCategoryCode: e.target.value })
                    }
                    placeholder="Category code"
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Non-Primary Inspection Category Name
                  </label>
                  <input
                    type="text"
                    value={locationFilters.nonPrimaryInspectionCategoryName}
                    onChange={(e) =>
                      setLocationFilters({ ...locationFilters, nonPrimaryInspectionCategoryName: e.target.value })
                    }
                    placeholder="Category name"
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Regulated Activity
                  </label>
                  <input
                    type="text"
                    value={locationFilters.regulatedActivity}
                    onChange={(e) =>
                      setLocationFilters({ ...locationFilters, regulatedActivity: e.target.value })
                    }
                    placeholder="Regulated activity type"
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Report Type
                  </label>
                  <select
                    value={locationFilters.reportType}
                    onChange={(e) =>
                      setLocationFilters({ ...locationFilters, reportType: e.target.value })
                    }
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="">Any</option>
                    <option value="Location">Location</option>
                    <option value="Provider">Provider</option>
                    <option value="CoreService">Core Service</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Results per Page
                  </label>
                  <input
                    type="number"
                    value={locationFilters.pageSize}
                    onChange={(e) =>
                      setLocationFilters({
                        ...locationFilters,
                        pageSize: parseInt(e.target.value) || 100,
                      })
                    }
                    min="1"
                    max="500"
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
              </div>
            )}
          </div>
        )}

        {searchMode === 'providers' && (
          <div className="space-y-4">
            {showFilters && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Local Authority
                  </label>
                  <input
                    type="text"
                    value={providerFilters.localAuthority}
                    onChange={(e) =>
                      setProviderFilters({ ...providerFilters, localAuthority: e.target.value })
                    }
                    placeholder="e.g., Tower Hamlets"
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Region</label>
                  <input
                    type="text"
                    value={providerFilters.region}
                    onChange={(e) =>
                      setProviderFilters({ ...providerFilters, region: e.target.value })
                    }
                    placeholder="e.g., London"
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Overall Rating
                  </label>
                  <select
                    value={providerFilters.overallRating}
                    onChange={(e) =>
                      setProviderFilters({ ...providerFilters, overallRating: e.target.value })
                    }
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="">Any Rating</option>
                    <option value="Outstanding">Outstanding</option>
                    <option value="Good">Good</option>
                    <option value="Requires improvement">Requires improvement</option>
                    <option value="Inadequate">Inadequate</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Inspection Directorate
                  </label>
                  <select
                    value={providerFilters.inspectionDirectorate}
                    onChange={(e) =>
                      setProviderFilters({
                        ...providerFilters,
                        inspectionDirectorate: e.target.value,
                      })
                    }
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="">Any</option>
                    <option value="Adult social care">Adult social care</option>
                    <option value="Hospitals">Hospitals</option>
                    <option value="Primary medical services">Primary medical services</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Results per Page
                  </label>
                  <input
                    type="number"
                    value={providerFilters.pageSize}
                    onChange={(e) =>
                      setProviderFilters({
                        ...providerFilters,
                        pageSize: parseInt(e.target.value) || 100,
                      })
                    }
                    min="1"
                    max="500"
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
              </div>
            )}
            
            {/* Quick Test Examples for Providers */}
            <div className="mt-4 pt-4 border-t border-purple-300">
              <p className="text-xs text-gray-600 mb-2 font-medium">
                Quick test examples - Search providers by region (click to search):
              </p>
              <div className="flex flex-wrap gap-2">
                {[
                  { region: 'London', description: 'All providers in London' },
                  { region: 'West Midlands', description: 'All providers in West Midlands' },
                  { region: 'South East', description: 'All providers in South East' },
                  { region: 'North West', description: 'All providers in North West' },
                  { localAuthority: 'Birmingham', description: 'All providers in Birmingham' },
                  { localAuthority: 'Manchester', description: 'All providers in Manchester' },
                ].map((example, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={async () => {
                      if (example.region) {
                        setProviderFilters({
                          ...providerFilters,
                          region: example.region,
                          localAuthority: '',
                        });
                      } else if (example.localAuthority) {
                        setProviderFilters({
                          ...providerFilters,
                          localAuthority: example.localAuthority,
                          region: '',
                        });
                      }
                      await new Promise(resolve => setTimeout(resolve, 50));
                      handleProviderSearch();
                    }}
                    className="px-3 py-1 text-xs bg-white text-purple-700 border border-purple-300 rounded-md hover:bg-purple-100 transition-colors shadow-sm"
                    title={example.description}
                  >
                    {example.region || example.localAuthority}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {searchMode === 'changes' && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Organisation Type
                </label>
                <select
                  value={changesFilters.organisationType}
                  onChange={(e) =>
                    setChangesFilters({
                      ...changesFilters,
                      organisationType: e.target.value,
                    })
                  }
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="location">Location</option>
                  <option value="provider">Provider</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Start Date
                </label>
                <input
                  type="date"
                  value={changesFilters.startDate}
                  onChange={(e) =>
                    setChangesFilters({ ...changesFilters, startDate: e.target.value })
                  }
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                <input
                  type="date"
                  value={changesFilters.endDate}
                  onChange={(e) =>
                    setChangesFilters({ ...changesFilters, endDate: e.target.value })
                  }
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
            </div>
            
            {/* Quick Test Examples for Changes */}
            <div className="mt-4 pt-4 border-t border-orange-300">
              <p className="text-xs text-gray-600 mb-2 font-medium">
                Quick test examples - Search changes by time period (click to search):
              </p>
              <div className="flex flex-wrap gap-2">
                {[
                  { 
                    days: 7, 
                    description: 'Changes in last 7 days',
                    getDates: () => {
                      const endDate = new Date();
                      const startDate = new Date();
                      startDate.setDate(startDate.getDate() - 7);
                      return {
                        startDate: startDate.toISOString().split('T')[0],
                        endDate: endDate.toISOString().split('T')[0]
                      };
                    }
                  },
                  { 
                    days: 30, 
                    description: 'Changes in last 30 days',
                    getDates: () => {
                      const endDate = new Date();
                      const startDate = new Date();
                      startDate.setDate(startDate.getDate() - 30);
                      return {
                        startDate: startDate.toISOString().split('T')[0],
                        endDate: endDate.toISOString().split('T')[0]
                      };
                    }
                  },
                  { 
                    days: 90, 
                    description: 'Changes in last 90 days',
                    getDates: () => {
                      const endDate = new Date();
                      const startDate = new Date();
                      startDate.setDate(startDate.getDate() - 90);
                      return {
                        startDate: startDate.toISOString().split('T')[0],
                        endDate: endDate.toISOString().split('T')[0]
                      };
                    }
                  },
                  { 
                    days: 180, 
                    description: 'Changes in last 6 months',
                    getDates: () => {
                      const endDate = new Date();
                      const startDate = new Date();
                      startDate.setDate(startDate.getDate() - 180);
                      return {
                        startDate: startDate.toISOString().split('T')[0],
                        endDate: endDate.toISOString().split('T')[0]
                      };
                    }
                  },
                ].map((example) => (
                  <button
                    key={example.days}
                    type="button"
                    onClick={async () => {
                      const dates = example.getDates();
                      setChangesFilters({
                        ...changesFilters,
                        startDate: dates.startDate,
                        endDate: dates.endDate,
                      });
                      await new Promise(resolve => setTimeout(resolve, 50));
                      handleChangesSearch();
                    }}
                    className="px-3 py-1 text-xs bg-white text-orange-700 border border-orange-300 rounded-md hover:bg-orange-100 transition-colors shadow-sm"
                    title={example.description}
                  >
                    Last {example.days} days
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        <div className="mt-4">
          <button
            onClick={handleSearch}
            disabled={loading}
            className="inline-flex items-center px-6 py-3 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-purple-700 disabled:opacity-50"
          >
            <Search className="w-4 h-4 mr-2" />
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </div>

      {/* Results - Region Search */}
      {locationViewMode === 'region' && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold">
              Care Homes Found ({results.length})
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              Showing all care homes in {locationFilters.region || locationFilters.localAuthority || 'selected region'}
            </p>
          </div>
          {loading && (
            <div className="p-8 text-center text-gray-500">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              <p className="mt-2">Searching...</p>
            </div>
          )}
          {!loading && results.length === 0 && (
            <div className="p-8 text-center text-gray-500">
              <p>No care homes found. Try adjusting your search filters.</p>
            </div>
          )}
          {!loading && results.length > 0 && (
          <div className="divide-y divide-gray-200">
            {results.map((item: any, index: number) => {
              // Handle different field name variations from CQC API
              // CQC API typically uses camelCase: locationName, locationId, etc.
              const locationName = item.name 
                || item.locationName 
                || item.location?.name 
                || item.location?.locationName
                || JSON.stringify(item).substring(0, 100) // Fallback: show raw data preview
                || 'Unknown';
              const locationId = item.locationId 
                || item.location?.locationId 
                || item.id;
              const providerId = item.providerId 
                || item.provider?.providerId;
              const address = item.address 
                || item.locationAddress 
                || item.location?.address
                || item.postalAddress
                || item.location?.postalAddress;
              const postcode = item.postcode 
                || item.location?.postcode
                || item.postalCode
                || item.location?.postalCode;
              const overallRating = item.overallRating 
                || item.location?.overallRating 
                || item.currentRatings?.overall?.rating
                || item.ratings?.overall?.rating;
              
              return (
                <div key={locationId || providerId || index} className="p-6 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-medium text-gray-900">
                        {locationName}
                      </h3>
                      <div className="mt-2 space-y-1 text-sm text-gray-600">
                        {(postcode || address) && (
                          <div className="flex items-center">
                            <MapPin className="w-4 h-4 mr-1" />
                            {address && <span>{address}</span>}
                            {postcode && <span className="ml-1">{postcode}</span>}
                          </div>
                        )}
                        {overallRating && (
                          <div className="flex items-center">
                            <span className="font-medium">Rating:</span>
                            <span className={`ml-2 px-2 py-1 rounded text-xs ${
                              overallRating === 'Outstanding' ? 'bg-green-100 text-green-800' :
                              overallRating === 'Good' ? 'bg-blue-100 text-blue-800' :
                              overallRating === 'Requires improvement' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {overallRating}
                            </span>
                          </div>
                        )}
                        {locationId && (
                          <div className="text-xs text-gray-500">
                            ID: {locationId}
                          </div>
                        )}
                        {providerId && (
                          <div className="text-xs text-gray-500">
                            Provider ID: {providerId}
                          </div>
                        )}
                      </div>
                    </div>
                    {locationId && (
                      <div className="flex gap-2 ml-4">
                        <button
                          onClick={() => handleViewLocationDetails(locationId)}
                          className="inline-flex items-center px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
                        >
                          <Eye className="w-4 h-4 mr-1" />
                          Details
                        </button>
                        <button
                          onClick={() => handleViewReports(locationId)}
                          className="inline-flex items-center px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
                        >
                          <FileText className="w-4 h-4 mr-1" />
                          Reports
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
          )}
        </div>
      )}

      {/* Location Details Modal */}
      {selectedLocation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold">Care Home Details</h2>
                <p className="text-sm text-gray-500 mt-1">
                  Location ID: {selectedLocation.locationId}
                </p>
              </div>
              <button
                onClick={() => setSelectedLocation(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <h3 className="text-lg font-medium mb-2">{selectedLocation.name}</h3>
                {selectedLocation.address && (
                  <p className="text-gray-600">{selectedLocation.address}</p>
                )}
                {selectedLocation.postcode && (
                  <p className="text-gray-600">{selectedLocation.postcode}</p>
                )}
              </div>
              
              {selectedLocation.overallRating && (
                <div>
                  <span className="text-sm font-medium text-gray-700">Overall Rating: </span>
                  <span className={`px-2 py-1 rounded text-sm ${
                    selectedLocation.overallRating === 'Outstanding' ? 'bg-green-100 text-green-800' :
                    selectedLocation.overallRating === 'Good' ? 'bg-blue-100 text-blue-800' :
                    selectedLocation.overallRating === 'Requires improvement' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {selectedLocation.overallRating}
                  </span>
                </div>
              )}

              {selectedLocation.currentRatings && (
                <div>
                  <h4 className="font-medium mb-2">Current Ratings</h4>
                  <pre className="bg-gray-50 p-4 rounded text-sm overflow-auto">
                    {JSON.stringify(selectedLocation.currentRatings, null, 2)}
                  </pre>
                </div>
              )}

              {selectedLocation.specialisms && selectedLocation.specialisms.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">Specialisms</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedLocation.specialisms.map((spec: any, idx: number) => (
                      <span
                        key={idx}
                        className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm"
                      >
                        {spec.name || spec}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <h4 className="font-medium mb-2">Full Details</h4>
                <pre className="bg-gray-50 p-4 rounded text-sm overflow-auto max-h-96">
                  {JSON.stringify(selectedLocation, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


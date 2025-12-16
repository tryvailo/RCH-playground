import { useState, useMemo } from 'react';
import { 
  MapPin, 
  Search, 
  AlertCircle, 
  CheckCircle, 
  Building2, 
  Heart, 
  TreePine, 
  Activity,
  Globe,
  BarChart3,
  RefreshCw,
  Sparkles
} from 'lucide-react';
import axios from 'axios';

// Shared components
import { CollapsibleSection, InfoCard, LoadingSpinner } from '../../shared/components';
import { getScoreColor, getRatingColor } from '../../shared/utils';

// Feature-specific components
import { OSPlacesResults, ONSResults, OSMResults, NHSBSAResults } from './components';
import type { NeighbourhoodAnalysisResult } from './types';

// Test locations for quick selection (cities/areas)
const TEST_LOCATIONS = [
  { name: 'Birmingham City Centre', postcode: 'B1 1BB', lat: 52.480145, lon: -1.9028891, region: 'West Midlands' },
  { name: 'London - Westminster', postcode: 'SW1A 1AA', lat: 51.5014, lon: -0.1419, region: 'London' },
  { name: 'Manchester City Centre', postcode: 'M1 1AA', lat: 53.4808, lon: -2.2426, region: 'North West' },
  { name: 'Leeds City Centre', postcode: 'LS1 4DY', lat: 53.8008, lon: -1.5491, region: 'Yorkshire' },
  { name: 'Bristol City Centre', postcode: 'BS1 5TR', lat: 51.4545, lon: -2.5879, region: 'South West' },
  { name: 'Edinburgh City Centre', postcode: 'EH1 1YZ', lat: 55.9533, lon: -3.1883, region: 'Scotland' },
  { name: 'Cardiff City Centre', postcode: 'CF10 3AT', lat: 51.4816, lon: -3.1791, region: 'Wales' },
  { name: 'Belfast City Centre', postcode: 'BT1 5GS', lat: 54.5973, lon: -5.9301, region: 'Northern Ireland' },
  { name: 'Cambridge City Centre', postcode: 'CB2 1TN', lat: 52.2053, lon: 0.1218, region: 'East of England' },
  { name: 'Oxford City Centre', postcode: 'OX1 1DP', lat: 51.7520, lon: -1.2577, region: 'South East' },
  { name: 'Warwick', postcode: 'CV34 5EH', lat: 52.287611, lon: -1.566073, region: 'West Midlands' },
  { name: 'Brighton City Centre', postcode: 'BN1 1AL', lat: 50.8225, lon: -0.1372, region: 'South East' },
];

// Pre-configured care homes for analysis
const CARE_HOMES = [
  {
    id: '1',
    name: 'Kinross Residential Care Home',
    address: '201 Havant Road, Drayton',
    city: 'Portsmouth',
    postcode: 'PO6 1EE',
    county: 'Hampshire',
    lat: 50.8500,
    lon: -1.0333,
    region: 'South East'
  },
  {
    id: '2',
    name: 'Meadows House Residential and Nursing Home',
    address: 'Cullum Welch Court',
    city: 'London',
    postcode: 'SE3 0PW',
    county: 'Greater London',
    lat: 51.4700,
    lon: 0.0200,
    region: 'London'
  },
  {
    id: '3',
    name: 'Roborough House',
    address: 'Tamerton Road, Woolwell',
    city: 'Plymouth',
    postcode: 'PL6 7BQ',
    county: 'Devon',
    lat: 50.3772,
    lon: -4.1000,
    region: 'South West'
  },
  {
    id: '4',
    name: 'Westgate House',
    address: '178 Romford Road, Forest Gate',
    city: 'London',
    postcode: 'E7 9HY',
    county: 'Greater London',
    lat: 51.5412,
    lon: -0.0185,
    region: 'London'
  },
  {
    id: '5',
    name: 'Trowbridge Oaks',
    address: 'West Ashton Road',
    city: 'Trowbridge',
    postcode: 'BA14 6DW',
    county: 'Wiltshire',
    lat: 51.3343,
    lon: -2.1877,
    region: 'South West'
  },
  {
    id: '6',
    name: 'Meadow Rose Nursing Home',
    address: 'Meadow Rose',
    city: 'Birmingham',
    postcode: 'B31 2TX',
    county: 'West Midlands',
    lat: 52.399843,
    lon: -1.989241,
    region: 'West Midlands'
  },
  {
    id: '7',
    name: 'Petersfield Care Home',
    address: 'Petersfield',
    city: 'Birmingham',
    postcode: 'B20 3RP',
    county: 'West Midlands',
    lat: 52.508024,
    lon: -1.912955,
    region: 'West Midlands'
  },
  {
    id: '8',
    name: 'Beech Hill Grange',
    address: 'Beech Hill',
    city: 'Sutton Coldfield',
    postcode: 'B72 1DU',
    county: 'West Midlands',
    lat: 52.5600,
    lon: -1.8200,
    region: 'West Midlands'
  }
];

export default function NeighbourhoodExplorer() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<NeighbourhoodAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    overall: true,
    os_places: true,
    ons: true,
    osm: true,
    nhsbsa: true,
  });

  const [inputMode, setInputMode] = useState<'postcode' | 'care_home'>('postcode');
  const [formData, setFormData] = useState({
    postcode: 'B1 1BB',
    include_os_places: true,
    include_ons: true,
    include_osm: true,
    include_nhsbsa: true,
  });
  const [selectedTestLocation, setSelectedTestLocation] = useState<string | null>(null);
  const [selectedCareHome, setSelectedCareHome] = useState<string | null>(null);

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  // Transform old API structure (social, health) to new structure (ons, nhsbsa) for display
  const transformedData = useMemo(() => {
    if (!result) return { onsData: null, nhsbsaData: null };
    
    // Transform ONS data
    const onsData = result.ons || (result.social ? {
      postcode: result.postcode,
      geography: result.social.geography || {},
      wellbeing: result.social.wellbeing ? {
        area: result.social.geography?.lsoa_name || result.social.geography?.local_authority || '',
        lsoa_code: result.social.geography?.lsoa_code || null,
        data_level: 'LSOA',
        period: '2020-2022',
        indicators: {
          happiness: { 
            value: result.social.wellbeing.components?.happiness_contribution || 0, 
            description: 'Happiness indicator', 
            national_average: 7.5, 
            vs_national: result.social.wellbeing.percentile ? 
              (result.social.wellbeing.percentile > 50 ? '+' : '') + 
              ((result.social.wellbeing.percentile - 50) * 2).toFixed(1) + '%' : '' 
          },
          life_satisfaction: { 
            value: result.social.wellbeing.components?.satisfaction_contribution || 0, 
            description: 'Life satisfaction', 
            national_average: 7.5, 
            vs_national: '' 
          },
          anxiety: { 
            value: result.social.wellbeing.components?.low_anxiety_contribution || 0, 
            description: 'Low anxiety (higher is better)', 
            national_average: 7.5, 
            vs_national: '' 
          },
          worthwhile: { 
            value: result.social.wellbeing.components?.worthwhile_contribution || 0, 
            description: 'Worthwhile', 
            national_average: 7.5, 
            vs_national: '' 
          }
        },
        social_wellbeing_index: result.social.wellbeing,
        source: 'ONS',
        methodology: 'Personal Wellbeing Survey',
        fetched_at: result.analyzed_at || result.social.geography?.fetched_at || new Date().toISOString()
      } : undefined,
      economic: result.social.economic ? {
        area: result.social.geography?.local_authority || '',
        postcode: result.postcode,
        lsoa_code: result.social.geography?.lsoa_code || null,
        indicators: {
          employment_rate: { value: 0, unit: '%', description: '', trend: 'stable' },
          median_income: { value: 0, unit: '£', description: '', trend: 'stable' },
          imd_decile: { value: 0, unit: '', description: '', interpretation: '' },
          economic_activity_rate: { value: 0, unit: '%', description: '', trend: 'stable' }
        },
        economic_stability_index: result.social.economic,
        source: 'ONS',
        period: '2020-2022',
        fetched_at: result.analyzed_at || new Date().toISOString()
      } : undefined,
      demographics: result.social.demographics ? {
        area: result.social.geography?.lsoa_name || '',
        postcode: result.postcode,
        population: { total: 0, density_per_km2: 0 },
        age_structure: {
          under_18: { percent: 0, count: 0 },
          '18_to_64': { percent: 0, count: 0 },
          '65_to_79': { percent: 0, count: 0 },
          '80_plus': { percent: 0, count: 0 }
        },
        elderly_care_context: result.social.demographics,
        household_composition: {
          single_person_over_65: { percent: 0 },
          couples_over_65: { percent: 0 }
        },
        source: 'ONS',
        fetched_at: result.analyzed_at || new Date().toISOString()
      } : undefined,
      summary: {
        area_name: result.social.geography?.local_authority || '',
        region: result.social.geography?.region || '',
        social_wellbeing_score: result.social.wellbeing?.score || 0,
        economic_stability_score: result.social.economic?.score || 0,
        elderly_population_percent: result.social.demographics?.over_65_percent || 0,
        overall_rating: 'Good'
      },
      fetched_at: result.analyzed_at || result.social.geography?.fetched_at || new Date().toISOString()
    } : null);

    // Transform NHSBSA data
    const nhsbsaData = result.nhsbsa || (result.health ? {
      location: result.coordinates || { latitude: 0, longitude: 0 },
      practices_analyzed: result.health.practices_nearby || 0,
      total_patients: 0,
      nearest_practice: null,
      health_indicators: {},
      top_medications: result.health.top_medications || [],
      health_index: result.health.index || { score: 0, rating: '', interpretation: '', percentile: 0 },
      care_home_considerations: result.health.care_home_considerations || [],
      data_period: '2023-2024',
      methodology: 'Based on prescribing patterns from nearby GP practices',
      fetched_at: result.analyzed_at || new Date().toISOString()
    } : null);

    return { onsData, nhsbsaData };
  }, [result]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      let postcode: string;
      let lat: number | undefined;
      let lon: number | undefined;

      // Determine postcode and coordinates based on input mode
      let addressName: string | undefined;
      if (inputMode === 'care_home') {
        if (!selectedCareHome) {
          setError('Please select a care home');
          setLoading(false);
          return;
        }
        const careHome = CARE_HOMES.find(ch => ch.id === selectedCareHome);
        if (!careHome) {
          setError('Selected care home not found');
          setLoading(false);
          return;
        }
        postcode = careHome.postcode;
        lat = careHome.lat;
        lon = careHome.lon;
        addressName = careHome.name; // Pass care home name for OS Places
      } else {
        postcode = formData.postcode.trim().replace(/\s+/g, ' ');
        if (!postcode) {
          setError('Please enter a postcode');
          setLoading(false);
          return;
        }
      }
      
      // Build query parameters for selected data sources
      const params = new URLSearchParams();
      params.append('include_os_places', formData.include_os_places.toString());
      params.append('include_ons', formData.include_ons.toString());
      params.append('include_osm', formData.include_osm.toString());
      params.append('include_nhsbsa', formData.include_nhsbsa.toString());
      
      // Add coordinates if available (from care home selection)
      if (lat !== undefined && lon !== undefined) {
        params.append('lat', lat.toString());
        params.append('lon', lon.toString());
      }
      
      // Add address name if available (for care home mode)
      if (addressName) {
        params.append('address_name', addressName);
      }
      
      const response = await axios.get(
        `/api/neighbourhood/analyze/${encodeURIComponent(postcode)}?${params.toString()}`
      );
      setResult(response.data);
    } catch (err: any) {
      console.error('Error analyzing neighbourhood:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to analyze neighbourhood';
      
      if (err.response?.status === 404) {
        setError('Postcode not found or neighbourhood analysis endpoint not available.');
      } else if (err.response?.status === 500) {
        setError(`Server error: ${errorMessage}`);
      } else if (!err.response) {
        setError('Cannot connect to backend. Please ensure the server is running on http://localhost:8000');
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <Globe className="w-8 h-8 text-primary" />
          Neighbourhood Analysis
        </h1>
        <p className="mt-2 text-gray-600">
          Comprehensive neighbourhood analysis using OS Places, ONS, OpenStreetMap, and NHSBSA data sources
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
          <span className="text-red-800">{error}</span>
        </div>
      )}

      {/* Input Form */}
      <div className="bg-white rounded-lg shadow p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Mode Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Select Input Mode
            </label>
            <div className="flex gap-4">
              <button
                type="button"
                onClick={() => {
                  setInputMode('postcode');
                  setSelectedCareHome(null);
                  setSelectedTestLocation(null);
                }}
                className={`flex-1 px-4 py-3 rounded-lg border-2 transition-all ${
                  inputMode === 'postcode'
                    ? 'bg-blue-50 border-blue-500 text-blue-700 font-medium'
                    : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center justify-center gap-2">
                  <MapPin className="w-5 h-5" />
                  <span>Enter Postcode</span>
                </div>
              </button>
              <button
                type="button"
                onClick={() => {
                  setInputMode('care_home');
                  setSelectedTestLocation(null);
                }}
                className={`flex-1 px-4 py-3 rounded-lg border-2 transition-all ${
                  inputMode === 'care_home'
                    ? 'bg-blue-50 border-blue-500 text-blue-700 font-medium'
                    : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center justify-center gap-2">
                  <Building2 className="w-5 h-5" />
                  <span>Select Care Home</span>
                </div>
              </button>
            </div>
          </div>

          {/* Postcode Input Mode */}
          {inputMode === 'postcode' && (
            <>
              {/* Quick Test Locations */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Sparkles className="w-4 h-4 inline mr-1" />
                  Quick Test Locations (Optional)
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                  {TEST_LOCATIONS.map((location) => (
                    <button
                      key={location.postcode}
                      type="button"
                      onClick={() => {
                        setFormData({ ...formData, postcode: location.postcode });
                        setSelectedTestLocation(location.postcode);
                      }}
                      className={`px-3 py-2 text-sm rounded-lg border transition-all ${
                        selectedTestLocation === location.postcode
                          ? 'bg-blue-50 border-blue-500 text-blue-700 font-medium'
                          : 'bg-gray-50 border-gray-300 text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      <div className="font-medium">{location.name}</div>
                      <div className="text-xs font-mono text-gray-500">{location.postcode}</div>
                    </button>
                  ))}
                </div>
                {selectedTestLocation && (
                  <p className="text-xs text-gray-500 mt-2">
                    Selected: {TEST_LOCATIONS.find(l => l.postcode === selectedTestLocation)?.name} ({selectedTestLocation})
                  </p>
                )}
              </div>

              {/* Postcode Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <MapPin className="w-4 h-4 inline mr-1" />
                  Enter Postcode <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.postcode}
                  onChange={(e) => {
                    setFormData({ ...formData, postcode: e.target.value.toUpperCase() });
                    setSelectedTestLocation(null);
                  }}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg text-lg font-mono"
                  placeholder="e.g., B1 1BB, SW1A 1AA"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Enter a UK postcode to analyze the neighbourhood
                </p>
              </div>
            </>
          )}

          {/* Care Home Selection Mode */}
          {inputMode === 'care_home' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Building2 className="w-4 h-4 inline mr-1" />
                Select Care Home <span className="text-red-500">*</span>
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {CARE_HOMES.map((careHome) => (
                  <button
                    key={careHome.id}
                    type="button"
                    onClick={() => setSelectedCareHome(careHome.id)}
                    className={`p-4 rounded-lg border-2 text-left transition-all ${
                      selectedCareHome === careHome.id
                        ? 'bg-blue-50 border-blue-500 shadow-md'
                        : 'bg-white border-gray-300 hover:border-blue-300 hover:bg-blue-50/50'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <div className={`font-semibold mb-1 ${
                          selectedCareHome === careHome.id ? 'text-blue-700' : 'text-gray-900'
                        }`}>
                          {careHome.name}
                        </div>
                        <div className="text-sm text-gray-600 mb-1">{careHome.address}</div>
                        <div className="text-xs text-gray-500">
                          {careHome.city}, {careHome.county}
                        </div>
                        <div className="text-xs font-mono text-gray-600 mt-1">
                          {careHome.postcode}
                        </div>
                      </div>
                      {selectedCareHome === careHome.id && (
                        <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0" />
                      )}
                    </div>
                  </button>
                ))}
              </div>
              {selectedCareHome && (
                <p className="text-xs text-gray-500 mt-2">
                  Selected: {CARE_HOMES.find(ch => ch.id === selectedCareHome)?.name} ({CARE_HOMES.find(ch => ch.id === selectedCareHome)?.postcode})
                </p>
              )}
            </div>
          )}

          {/* Data Source Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Data Sources to Include
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <SourceToggle
                checked={formData.include_os_places}
                onChange={(checked) => setFormData({ ...formData, include_os_places: checked })}
                icon={<Building2 className="w-5 h-5 text-blue-600" />}
                label="OS Places"
                description="Coordinates, UPRN, Address"
                color="blue"
              />
              
              <SourceToggle
                checked={formData.include_ons}
                onChange={(checked) => setFormData({ ...formData, include_ons: checked })}
                icon={<BarChart3 className="w-5 h-5 text-purple-600" />}
                label="ONS"
                description="Wellbeing, Economics, Demographics"
                color="purple"
              />
              
              <SourceToggle
                checked={formData.include_osm}
                onChange={(checked) => setFormData({ ...formData, include_osm: checked })}
                icon={<TreePine className="w-5 h-5 text-green-600" />}
                label="OpenStreetMap"
                description="Walk Score, Amenities"
                color="green"
              />
              
              <SourceToggle
                checked={formData.include_nhsbsa}
                onChange={(checked) => setFormData({ ...formData, include_nhsbsa: checked })}
                icon={<Heart className="w-5 h-5 text-red-600" />}
                label="NHSBSA"
                description="Health Profile, GP Access"
                color="red"
              />
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || (inputMode === 'care_home' && !selectedCareHome)}
            className="w-full px-4 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark disabled:opacity-50 flex items-center justify-center gap-2 text-lg font-medium transition-colors"
          >
            {loading ? (
              <LoadingSpinner label="Analyzing neighbourhood..." inline />
            ) : (
              <>
                <Search className="w-5 h-5" />
                Analyze Neighbourhood
              </>
            )}
          </button>
        </form>
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Overall Score Section */}
          {result.overall && (
            <CollapsibleSection
              title="Overall Neighbourhood Score"
              icon={<Activity className="w-5 h-5 text-primary" />}
              badge={
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  <span className="text-sm text-gray-600">Analysis complete</span>
                </div>
              }
              expanded={expandedSections.overall}
              onToggle={() => toggleSection('overall')}
            >
              <OverallScoreContent result={result} getScoreColor={getScoreColor} getRatingColor={getRatingColor} />
            </CollapsibleSection>
          )}

          {/* OS Places Section */}
          {result.os_places && (
            <CollapsibleSection
              title="OS Places - Location Data"
              icon={<Building2 className="w-5 h-5 text-blue-600" />}
              color="blue"
              expanded={expandedSections.os_places}
              onToggle={() => toggleSection('os_places')}
            >
              <OSPlacesResults data={result.os_places} />
            </CollapsibleSection>
          )}

          {/* ONS Section - Support both old (social) and new (ons) structure */}
          {transformedData.onsData && (
            <CollapsibleSection
              title="ONS - Social & Economic Data"
              icon={<BarChart3 className="w-5 h-5 text-purple-600" />}
              color="purple"
              expanded={expandedSections.ons}
              onToggle={() => toggleSection('ons')}
            >
              <ONSResults data={transformedData.onsData} />
            </CollapsibleSection>
          )}

          {/* OSM Section */}
          {result.osm && (
            <CollapsibleSection
              title="OpenStreetMap - Walkability & Amenities"
              icon={<TreePine className="w-5 h-5 text-green-600" />}
              color="green"
              expanded={expandedSections.osm}
              onToggle={() => toggleSection('osm')}
            >
              <OSMResults 
                walkScore={result.osm.walk_score}
                amenities={result.osm.amenities}
                infrastructure={result.osm.infrastructure}
              />
            </CollapsibleSection>
          )}

          {/* NHSBSA Section - Support both old (health) and new (nhsbsa) structure */}
          {transformedData.nhsbsaData && (
            <CollapsibleSection
              title="NHSBSA - Health Profile"
              icon={<Heart className="w-5 h-5 text-red-600" />}
              color="red"
              expanded={expandedSections.nhsbsa}
              onToggle={() => toggleSection('nhsbsa')}
            >
              <NHSBSAResults healthProfile={transformedData.nhsbsaData} />
            </CollapsibleSection>
          )}

          {/* Errors */}
          {result.errors && Object.keys(result.errors).length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h3 className="font-medium text-yellow-800 mb-2 flex items-center gap-2">
                <AlertCircle className="w-4 h-4" />
                Some data sources had errors
              </h3>
              <ul className="text-sm text-yellow-700 space-y-1">
                {Object.entries(result.errors).map(([source, error]) => (
                  <li key={source}>• <strong className="capitalize">{source}:</strong> {error}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Raw JSON */}
          <details className="bg-gray-50 rounded-lg p-4">
            <summary className="cursor-pointer text-sm font-medium text-gray-600 flex items-center gap-2">
              <RefreshCw className="w-4 h-4" />
              View Raw JSON Response
            </summary>
            <pre className="mt-4 text-xs overflow-x-auto bg-gray-900 text-gray-100 p-4 rounded max-h-96">
              {JSON.stringify(result, null, 2)}
            </pre>
          </details>
        </div>
      )}

      {/* Info Box */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-medium text-gray-800 mb-4">Data Sources Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <InfoCard
            icon={<Building2 className="w-6 h-6 text-blue-600" />}
            title="OS Places"
            items={['Coordinates (lat/lon)', 'UPRN (unique ID)', 'Standardized address', 'Local authority']}
          />
          <InfoCard
            icon={<BarChart3 className="w-6 h-6 text-purple-600" />}
            title="ONS"
            items={['Social wellbeing index', 'Economic stability', 'Demographics', 'LSOA/MSOA codes']}
          />
          <InfoCard
            icon={<TreePine className="w-6 h-6 text-green-600" />}
            title="OpenStreetMap"
            items={['Walk Score (0-100)', 'Nearby amenities', 'Infrastructure', 'Care home suitability']}
          />
          <InfoCard
            icon={<Heart className="w-6 h-6 text-red-600" />}
            title="NHSBSA"
            items={['Health index', 'GP access rating', 'Prescribing patterns', 'Care considerations']}
          />
        </div>
      </div>
    </div>
  );
}// Helper Components

function SourceToggle({
  checked,
  onChange,
  icon,
  label,
  description,
  color
}: {
  checked: boolean;
  onChange: (checked: boolean) => void;
  icon: React.ReactNode;
  label: string;
  description: string;
  color: string;
}) {
  const colorClasses: Record<string, string> = {
    blue: 'border-blue-300 bg-blue-50',
    purple: 'border-purple-300 bg-purple-50',
    green: 'border-green-300 bg-green-50',
    red: 'border-red-300 bg-red-50',
  };
  
  return (
    <label className={`
      flex flex-col p-4 border-2 rounded-lg cursor-pointer transition-all
      ${checked ? colorClasses[color] : 'border-gray-200 bg-white hover:bg-gray-50'}
    `}>
      <div className="flex items-center gap-3">
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          className="w-4 h-4"
        />
        {icon}
        <span className="font-medium">{label}</span>
      </div>
      <span className="text-xs text-gray-500 mt-2 ml-7">{description}</span>
    </label>
  );
}

function OverallScoreContent({
  result,
  getScoreColor,
  getRatingColor
}: {
  result: NeighbourhoodAnalysisResult;
  getScoreColor: (score: number | undefined) => string;
  getRatingColor: (rating: string | undefined) => string;
}) {
  if (!result.overall) return null;
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Main Score */}
      <div className="text-center">
        <div className={`inline-block px-8 py-6 rounded-2xl ${getScoreColor(result.overall.score)}`}>
          <div className="text-5xl font-bold">{result.overall.score}</div>
          <div className="text-sm font-medium mt-1">out of 100</div>
        </div>
        <div className={`mt-3 text-xl font-semibold ${getRatingColor(result.overall.rating)}`}>
          {result.overall.rating}
        </div>
        <div className="text-sm text-gray-500 mt-1">
          Confidence: {result.overall.confidence}
        </div>
      </div>
      
      {/* Score Breakdown */}
      <div className="md:col-span-2">
        <h3 className="text-sm font-medium text-gray-700 mb-4">Score Breakdown</h3>
        <div className="space-y-4">
          {result.overall.breakdown?.map((item, index) => (
            <div key={index} className="flex items-center gap-4">
              <div className="w-36 text-sm text-gray-600">{item.name}</div>
              <div className="flex-1">
                <div className="h-5 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full transition-all ${
                      item.score >= 75 ? 'bg-green-500' :
                      item.score >= 60 ? 'bg-blue-500' :
                      item.score >= 45 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${item.score}%` }}
                  />
                </div>
              </div>
              <div className="w-20 text-right">
                <span className="text-lg font-bold">{item.score}</span>
                <span className="text-xs text-gray-500 ml-1">({item.weight})</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}



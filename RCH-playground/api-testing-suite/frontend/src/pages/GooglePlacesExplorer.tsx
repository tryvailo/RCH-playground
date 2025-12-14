import { useState } from 'react';
import { Search, MapPin, Star, Phone, Globe, Clock, Image, Users, MessageSquare, X, Eye, Navigation, TrendingUp, BarChart3, Map } from 'lucide-react';
import axios from 'axios';

interface Place {
  place_id: string;
  name: string;
  rating?: number;
  user_ratings_total?: number;
  formatted_address?: string;
  formatted_phone_number?: string;
  website?: string;
  opening_hours?: {
    weekday_text?: string[];
    open_now?: boolean;
  };
  photos?: Array<{
    photo_reference: string;
    height: number;
    width: number;
  }>;
  reviews?: Array<{
    author_name: string;
    rating: number;
    text: string;
    time: number;
    relative_time_description: string;
  }>;
  geometry?: {
    location: {
      lat: number;
      lng: number;
    };
  };
  types?: string[];
  business_status?: string;
  vicinity?: string;
  sentiment_analysis?: {
    average_sentiment: number;
    sentiment_label: string;
    total_reviews: number;
  };
  _api_version?: string;
  _api_source?: string;
  _fallback_reason?: string;
}

type SearchMode = 'name' | 'nearby';

export default function GooglePlacesExplorer() {
  const [searchMode, setSearchMode] = useState<SearchMode>('name');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<Place[]>([]);
  const [selectedPlace, setSelectedPlace] = useState<Place | null>(null);
  const [cost, setCost] = useState<number>(0);
  const [insights, setInsights] = useState<any>(null);
  const [loadingInsights, setLoadingInsights] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState<any>(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [individualInsights, setIndividualInsights] = useState<{
    popularTimes?: any;
    dwellTime?: any;
    repeatVisitors?: any;
    visitorGeography?: any;
    footfallTrends?: any;
    loading: { [key: string]: boolean };
  }>({ loading: {} });

  // Name search form
  const [nameSearch, setNameSearch] = useState({
    query: '',
    city: '',
    postcode: '',
  });

  // Nearby search form
  const [nearbySearch, setNearbySearch] = useState({
    latitude: '',
    longitude: '',
    radius: '5000',
    keyword: 'care home',
  });

  const handleNameSearch = async (queryOverride?: string, cityOverride?: string, postcodeOverride?: string) => {
    const queryToUse = queryOverride || nameSearch.query;
    const cityToUse = cityOverride !== undefined ? cityOverride : nameSearch.city;
    const postcodeToUse = postcodeOverride !== undefined ? postcodeOverride : nameSearch.postcode;
    
    if (!String(queryToUse).trim()) {
      alert('Please enter a care home name or address');
      return;
    }

    setLoading(true);
    setSelectedPlace(null);
    try {
      const params: any = { query: String(queryToUse).trim() };
      if (cityToUse && String(cityToUse).trim()) params.city = String(cityToUse).trim();
      if (postcodeToUse && String(postcodeToUse).trim()) params.postcode = String(postcodeToUse).trim();

      const response = await axios.get('/api/google-places/search', { params });
      
      if (response.data.status === 'success' && response.data.place) {
        // Ensure place_id exists and is valid
        if (!response.data.place.place_id) {
          alert('Error: Place ID is missing from response');
          return;
        }
        setResults([response.data.place]);
        setCost(response.data.cost || 0);
      } else {
        setResults([]);
        setCost(response.data.cost || 0);
        const errorMsg = response.data.message || 'No care home found';
        const suggestion = response.data.suggestion || '';
        alert(`${errorMsg}${suggestion ? '\n\n' + suggestion : ''}`);
      }
    } catch (error: any) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleNearbySearch = async () => {
    if (!nearbySearch.latitude || !nearbySearch.longitude) {
      alert('Please enter latitude and longitude');
      return;
    }

    setLoading(true);
    setSelectedPlace(null);
    try {
      const params: any = {
        latitude: parseFloat(nearbySearch.latitude),
        longitude: parseFloat(nearbySearch.longitude),
        radius: parseInt(nearbySearch.radius) || 5000,
      };
      if (nearbySearch.keyword) params.keyword = nearbySearch.keyword;

      const response = await axios.get('/api/google-places/nearby', { params });
      
      if (response.data.status === 'success') {
        const places = response.data.places || [];
        // Validate that all places have place_id
        const validPlaces = places.filter((place: Place) => place.place_id && place.place_id.trim());
        if (validPlaces.length !== places.length) {
          console.warn('Some places are missing place_id');
        }
        setResults(validPlaces);
        setCost(response.data.cost || 0);
      } else {
        setResults([]);
        alert('No care homes found nearby');
      }
    } catch (error: any) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (placeId: string) => {
    if (!placeId || !placeId.trim()) {
      alert('Error: Place ID is missing');
      return;
    }
    
    setInsights(null); // Reset insights when viewing new place
    setIndividualInsights({ loading: {} }); // Reset individual insights
    try {
      // Encode place_id to handle special characters
      const encodedPlaceId = encodeURIComponent(placeId.trim());
      const response = await axios.get(`/api/google-places/details/${encodedPlaceId}`);
      if (response.data.status === 'success') {
        const place = response.data.place;
        // Ensure place_id is preserved
        if (!place.place_id) {
          console.warn('Place ID missing from response, using original:', placeId);
          place.place_id = placeId.trim();
        }
        console.log('Setting selected place with place_id:', place.place_id);
        setSelectedPlace(place);
        setCost((prev) => prev + (response.data.cost || 0));
      } else {
        alert(`Error: ${response.data.message || 'Failed to load place details'}`);
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Unknown error';
      alert(`Error loading place details: ${errorMessage}`);
      console.error('Error loading place details:', error);
    }
  };

  const getPhotoUrl = (photoReference: string, maxWidth: number = 200) => {
    return `/api/google-places/photo/${photoReference}?maxwidth=${maxWidth}`;
  };

  const handleLoadInsights = async (placeId: string) => {
    if (!placeId || !placeId.trim()) {
      alert('Error: Place ID is missing');
      return;
    }
    
    setLoadingInsights(true);
    try {
      // Encode place_id to handle special characters
      const encodedPlaceId = encodeURIComponent(placeId.trim());
      const response = await axios.get(`/api/google-places/${encodedPlaceId}/insights`);
      if (response.data.status === 'success') {
        setInsights(response.data.insights);
        setCost((prev) => prev + (response.data.cost || 0));
      } else {
        alert(`Error: ${response.data.message || 'Failed to load insights'}`);
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Unknown error';
      alert(`Error loading insights: ${errorMessage}`);
      console.error('Error loading insights:', error);
    } finally {
      setLoadingInsights(false);
    }
  };

  const handleLoadPopularTimes = async (placeId: string) => {
    if (!placeId || !placeId.trim()) {
      alert('Error: Place ID is missing');
      return;
    }
    
    setIndividualInsights((prev) => ({ ...prev, loading: { ...prev.loading, popularTimes: true } }));
    try {
      const encodedPlaceId = encodeURIComponent(placeId.trim());
      const response = await axios.get(`/api/google-places/${encodedPlaceId}/popular-times`);
      if (response.data.status === 'success') {
        setIndividualInsights((prev) => ({ ...prev, popularTimes: response.data.popular_times }));
        setCost((prev) => prev + (response.data.cost || 0));
      } else {
        alert(`Error: ${response.data.message || 'Failed to load popular times'}`);
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Unknown error';
      alert(`Error loading popular times: ${errorMessage}`);
      console.error('Error loading popular times:', error);
    } finally {
      setIndividualInsights((prev) => ({ ...prev, loading: { ...prev.loading, popularTimes: false } }));
    }
  };

  const handleLoadDwellTime = async (placeId: string) => {
    if (!placeId || !placeId.trim()) {
      alert('Error: Place ID is missing');
      return;
    }
    
    setIndividualInsights((prev) => ({ ...prev, loading: { ...prev.loading, dwellTime: true } }));
    try {
      const encodedPlaceId = encodeURIComponent(placeId.trim());
      const response = await axios.get(`/api/google-places/${encodedPlaceId}/dwell-time`);
      if (response.data.status === 'success') {
        setIndividualInsights((prev) => ({ ...prev, dwellTime: response.data.dwell_time }));
        setCost((prev) => prev + (response.data.cost || 0));
      } else {
        alert(`Error: ${response.data.message || 'Failed to load dwell time'}`);
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Unknown error';
      alert(`Error loading dwell time: ${errorMessage}`);
      console.error('Error loading dwell time:', error);
    } finally {
      setIndividualInsights((prev) => ({ ...prev, loading: { ...prev.loading, dwellTime: false } }));
    }
  };

  const handleLoadRepeatVisitors = async (placeId: string) => {
    if (!placeId || !placeId.trim()) {
      alert('Error: Place ID is missing');
      return;
    }
    
    setIndividualInsights((prev) => ({ ...prev, loading: { ...prev.loading, repeatVisitors: true } }));
    try {
      const encodedPlaceId = encodeURIComponent(placeId.trim());
      const response = await axios.get(`/api/google-places/${encodedPlaceId}/repeat-visitors`);
      if (response.data.status === 'success') {
        setIndividualInsights((prev) => ({ ...prev, repeatVisitors: response.data.repeat_visitor_rate }));
        setCost((prev) => prev + (response.data.cost || 0));
      } else {
        alert(`Error: ${response.data.message || 'Failed to load repeat visitors'}`);
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Unknown error';
      alert(`Error loading repeat visitors: ${errorMessage}`);
      console.error('Error loading repeat visitors:', error);
    } finally {
      setIndividualInsights((prev) => ({ ...prev, loading: { ...prev.loading, repeatVisitors: false } }));
    }
  };

  const handleLoadVisitorGeography = async (placeId: string) => {
    if (!placeId || !placeId.trim()) {
      alert('Error: Place ID is missing');
      return;
    }
    
    setIndividualInsights((prev) => ({ ...prev, loading: { ...prev.loading, visitorGeography: true } }));
    try {
      const encodedPlaceId = encodeURIComponent(placeId.trim());
      const response = await axios.get(`/api/google-places/${encodedPlaceId}/visitor-geography`);
      if (response.data.status === 'success') {
        setIndividualInsights((prev) => ({ ...prev, visitorGeography: response.data.visitor_geography }));
        setCost((prev) => prev + (response.data.cost || 0));
      } else {
        alert(`Error: ${response.data.message || 'Failed to load visitor geography'}`);
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Unknown error';
      alert(`Error loading visitor geography: ${errorMessage}`);
      console.error('Error loading visitor geography:', error);
    } finally {
      setIndividualInsights((prev) => ({ ...prev, loading: { ...prev.loading, visitorGeography: false } }));
    }
  };

  const handleLoadFootfallTrends = async (placeId: string) => {
    if (!placeId || !placeId.trim()) {
      alert('Error: Place ID is missing');
      return;
    }
    
    setIndividualInsights((prev) => ({ ...prev, loading: { ...prev.loading, footfallTrends: true } }));
    try {
      const encodedPlaceId = encodeURIComponent(placeId.trim());
      const response = await axios.get(`/api/google-places/${encodedPlaceId}/footfall-trends?months=12`);
      if (response.data.status === 'success') {
        setIndividualInsights((prev) => ({ ...prev, footfallTrends: response.data.footfall_trends }));
        setCost((prev) => prev + (response.data.cost || 0));
      } else {
        alert(`Error: ${response.data.message || 'Failed to load footfall trends'}`);
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Unknown error';
      alert(`Error loading footfall trends: ${errorMessage}`);
      console.error('Error loading footfall trends:', error);
    } finally {
      setIndividualInsights((prev) => ({ ...prev, loading: { ...prev.loading, footfallTrends: false } }));
    }
  };

  const handleGenerateAnalysis = async () => {
    if (!selectedPlace || !selectedPlace.place_id) {
      alert('Error: Place ID is missing. Please view place details first.');
      return;
    }
    
    if (!insights) {
      alert('Error: Please load insights first before generating analysis.');
      return;
    }
    
    setLoadingAnalysis(true);
    try {
      const encodedPlaceId = encodeURIComponent(selectedPlace.place_id.trim());
      const response = await axios.post(`/api/google-places/${encodedPlaceId}/analyze`);
      if (response.data.status === 'success') {
        setAiAnalysis(response.data);
      } else {
        alert(`Error: ${response.data.message || 'Failed to generate analysis'}`);
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Unknown error';
      alert(`Error generating analysis: ${errorMessage}`);
      console.error('Error generating analysis:', error);
    } finally {
      setLoadingAnalysis(false);
    }
  };

  const calculateReviewVelocity = (reviews?: Array<any>) => {
    if (!reviews || reviews.length === 0) return null;
    
    // Calculate reviews per week based on most recent review
    const now = Date.now() / 1000;
    const oldestReview = Math.min(...reviews.map(r => r.time));
    const daysDiff = (now - oldestReview) / 86400;
    const weeksDiff = daysDiff / 7;
    
    if (weeksDiff === 0) return null;
    
    const reviewsPerWeek = reviews.length / weeksDiff;
    
    return {
      reviewsPerWeek: reviewsPerWeek.toFixed(2),
      totalReviews: reviews.length,
      weeksTracked: weeksDiff.toFixed(1),
      interpretation: reviewsPerWeek > 2 
        ? 'Growing visibility - good reputation' 
        : reviewsPerWeek > 0.5 
        ? 'Stable review rate' 
        : 'Low review rate - potential decline'
    };
  };

  const renderStars = (rating?: number) => {
    if (!rating) return null;
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`w-4 h-4 ${
              star <= Math.round(rating)
                ? 'fill-yellow-400 text-yellow-400'
                : 'text-gray-300'
            }`}
          />
        ))}
        <span className="ml-1 text-sm text-gray-600">{rating.toFixed(1)}</span>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Google Places Explorer</h1>
        <p className="mt-2 text-gray-600">Search and explore care homes using Google Places API</p>
      </div>

      {/* Mode Selection */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex gap-4">
          <button
            onClick={() => {
              setSearchMode('name');
              setResults([]);
              setSelectedPlace(null);
            }}
            className={`flex items-center px-4 py-2 rounded-md font-medium ${
              searchMode === 'name'
                ? 'bg-primary text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Search className="w-4 h-4 mr-2" />
            Search by Name/Address
          </button>
          <button
            onClick={() => {
              setSearchMode('nearby');
              setResults([]);
              setSelectedPlace(null);
            }}
            className={`flex items-center px-4 py-2 rounded-md font-medium ${
              searchMode === 'nearby'
                ? 'bg-primary text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <MapPin className="w-4 h-4 mr-2" />
            Search Nearby
          </button>
        </div>
      </div>

      {/* Search Forms */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Search Parameters</h2>

        {searchMode === 'name' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Care Home Name or Address *
              </label>
              <input
                type="text"
                value={nameSearch.query}
                onChange={(e) => setNameSearch({ ...nameSearch, query: e.target.value })}
                placeholder="e.g., Manor House Care Home"
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                onKeyPress={(e) => e.key === 'Enter' && handleNameSearch()}
              />
              <div className="mt-2">
                <p className="text-xs text-gray-500 mb-2">Quick test examples (click to use - real UK care homes from CQC registry):</p>
                <div className="flex flex-wrap gap-2">
                  {[
                    { name: 'Westgate House Care Home', city: 'London', postcode: 'E7 9HY' },
                    { name: 'The Orchards Care Home', city: 'Birmingham', postcode: 'B34 7BP' },
                    { name: 'Trowbridge Oaks Care Home', city: 'Trowbridge', postcode: 'BA14 6DW' },
                    { name: 'Lynde House Care Home', city: 'Twickenham', postcode: 'TW1 3DY' }
                  ].map((example) => (
                    <button
                      key={example.name}
                      type="button"
                      onClick={() => {
                        // Update state for display
                        setNameSearch({
                          query: example.name,
                          city: example.city,
                          postcode: example.postcode
                        });
                        // Trigger search immediately with direct parameters
                        handleNameSearch(example.name, example.city, example.postcode);
                      }}
                      className="px-3 py-1 text-xs bg-blue-50 text-blue-700 border border-blue-200 rounded-md hover:bg-blue-100 transition-colors"
                      title={`${example.name}, ${example.city}, ${example.postcode}`}
                    >
                      {example.name}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                <input
                  type="text"
                  value={nameSearch.city}
                  onChange={(e) => setNameSearch({ ...nameSearch, city: e.target.value })}
                  placeholder="e.g., Brighton"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Postcode</label>
                <input
                  type="text"
                  value={nameSearch.postcode}
                  onChange={(e) => setNameSearch({ ...nameSearch, postcode: e.target.value })}
                  placeholder="e.g., BN1 1AB"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
            </div>
            <button
              onClick={handleNameSearch}
              disabled={loading}
              className="inline-flex items-center px-6 py-3 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-purple-700 disabled:opacity-50"
            >
              <Search className="w-4 h-4 mr-2" />
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        )}

        {searchMode === 'nearby' && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Latitude *
                </label>
                <input
                  type="number"
                  step="any"
                  value={nearbySearch.latitude}
                  onChange={(e) =>
                    setNearbySearch({ ...nearbySearch, latitude: e.target.value })
                  }
                  placeholder="e.g., 50.8225"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
                <div className="mt-2">
                  <p className="text-xs text-gray-500 mb-2">Quick test coordinates:</p>
                  <div className="flex flex-wrap gap-2">
                    {[
                      { name: 'Westgate House', lat: '51.5412', lng: '-0.0185' },
                      { name: 'The Orchards', lat: '52.5098', lng: '-1.8512' },
                      { name: 'Trowbridge Oaks', lat: '51.3343', lng: '-2.1877' },
                      { name: 'Lynde House', lat: '51.4425', lng: '-0.3251' }
                    ].map((example) => (
                      <button
                        key={example.name}
                        type="button"
                        onClick={() => {
                          setNearbySearch({
                            ...nearbySearch,
                            latitude: example.lat,
                            longitude: example.lng
                          });
                          // Trigger search immediately
                          setTimeout(() => {
                            handleNearbySearch();
                          }, 100);
                        }}
                        className="px-3 py-1 text-xs bg-green-50 text-green-700 border border-green-200 rounded-md hover:bg-green-100 transition-colors"
                        title={`${example.name}: ${example.lat}, ${example.lng}`}
                      >
                        {example.name}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Longitude *
                </label>
                <input
                  type="number"
                  step="any"
                  value={nearbySearch.longitude}
                  onChange={(e) =>
                    setNearbySearch({ ...nearbySearch, longitude: e.target.value })
                  }
                  placeholder="e.g., -0.1372"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Search Radius (meters)
                </label>
                <input
                  type="number"
                  value={nearbySearch.radius}
                  onChange={(e) =>
                    setNearbySearch({ ...nearbySearch, radius: e.target.value })
                  }
                  min="1"
                  max="50000"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Keyword
                </label>
                <input
                  type="text"
                  value={nearbySearch.keyword}
                  onChange={(e) =>
                    setNearbySearch({ ...nearbySearch, keyword: e.target.value })
                  }
                  placeholder="e.g., care home"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
            </div>
            <button
              onClick={handleNearbySearch}
              disabled={loading}
              className="inline-flex items-center px-6 py-3 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-purple-700 disabled:opacity-50"
            >
              <MapPin className="w-4 h-4 mr-2" />
              {loading ? 'Searching...' : 'Search Nearby'}
            </button>
          </div>
        )}
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
      {results.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold">
              Results ({results.length})
            </h2>
          </div>
          <div className="divide-y divide-gray-200">
            {results.map((place) => (
              <div key={place.place_id} className="p-6 hover:bg-gray-50">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-start gap-4">
                      {place.photos && place.photos.length > 0 && place.photos[0].photo_reference && (
                        <div className="flex-shrink-0">
                          <img
                            src={getPhotoUrl(place.photos[0].photo_reference, 100)}
                            alt={place.name}
                            className="w-20 h-20 object-cover rounded-lg"
                            onError={(e) => {
                              (e.target as HTMLImageElement).style.display = 'none';
                            }}
                          />
                        </div>
                      )}
                      <div className="flex-1">
                        <h3 className="text-lg font-medium text-gray-900">{place.name}</h3>
                        <div className="mt-2 space-y-1 text-sm text-gray-600">
                          {place.formatted_address && (
                            <div className="flex items-center">
                              <MapPin className="w-4 h-4 mr-1" />
                              {place.formatted_address}
                            </div>
                          )}
                          {place.rating && (
                            <div className="flex items-center">
                              {renderStars(place.rating)}
                              {place.user_ratings_total && (
                                <span className="ml-2 text-gray-500">
                                  ({place.user_ratings_total} reviews)
                                </span>
                              )}
                            </div>
                          )}
                          {place.formatted_phone_number && (
                            <div className="flex items-center">
                              <Phone className="w-4 h-4 mr-1" />
                              {place.formatted_phone_number}
                            </div>
                          )}
                          {place.website && (
                            <div className="flex items-center">
                              <Globe className="w-4 h-4 mr-1" />
                              <a
                                href={place.website}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-600 hover:underline"
                              >
                                Website
                              </a>
                            </div>
                          )}
                          {place.business_status && (
                            <div className="flex items-center">
                              <span
                                className={`text-xs px-2 py-1 rounded ${
                                  place.business_status === 'OPERATIONAL'
                                    ? 'bg-green-100 text-green-800'
                                    : 'bg-gray-100 text-gray-800'
                                }`}
                              >
                                {place.business_status}
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="ml-4 flex flex-col items-end gap-2">
                    {place._api_version && (
                      <span className={`text-xs px-2 py-1 rounded ${
                        place._api_version === 'Places API (New)'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-yellow-100 text-yellow-700'
                      }`}>
                        {place._api_version === 'Places API (New)' ? '✓ New API' : 'Legacy API'}
                      </span>
                    )}
                    <button
                      onClick={() => {
                        if (!place.place_id || !place.place_id.trim()) {
                          alert('Error: Place ID is missing');
                          console.error('Place object:', place);
                          return;
                        }
                        handleViewDetails(place.place_id);
                      }}
                      className="inline-flex items-center px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
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


      {/* Place Details Modal */}
      {selectedPlace && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-semibold">Care Home Details</h2>
              <button
                onClick={() => setSelectedPlace(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="p-6 space-y-6">
              {/* API Version Info */}
              {selectedPlace._api_version && (
                <div className={`p-3 rounded-lg border-l-4 ${
                  selectedPlace._api_version === 'Places API (New)' 
                    ? 'bg-green-50 border-green-500' 
                    : 'bg-yellow-50 border-yellow-500'
                }`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold">
                        <span className={selectedPlace._api_version === 'Places API (New)' ? 'text-green-700' : 'text-yellow-700'}>
                          {selectedPlace._api_version}
                        </span>
                      </p>
                      {selectedPlace._api_source && (
                        <p className="text-xs text-gray-600 mt-1">
                          Source: {selectedPlace._api_source}
                        </p>
                      )}
                      {selectedPlace._fallback_reason && (
                        <p className="text-xs text-yellow-700 mt-1">
                          ⚠️ Fallback reason: {selectedPlace._fallback_reason}
                        </p>
                      )}
                    </div>
                    {selectedPlace._api_version === 'Places API (New)' && (
                      <span className="px-2 py-1 text-xs font-semibold bg-green-100 text-green-800 rounded">
                        ✓ Latest
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Header Info */}
              <div>
                <h3 className="text-2xl font-bold mb-2">{selectedPlace.name}</h3>
                {selectedPlace.formatted_address && (
                  <p className="text-gray-600 flex items-center">
                    <MapPin className="w-4 h-4 mr-1" />
                    {selectedPlace.formatted_address}
                  </p>
                )}
              </div>

              {/* Rating and Reviews */}
              {selectedPlace.rating && (
                <div className="border-t pt-4">
                  <h4 className="font-semibold mb-2 flex items-center">
                    <Star className="w-5 h-5 mr-1 text-yellow-400 fill-yellow-400" />
                    Rating & Reviews
                  </h4>
                  <div className="flex items-center gap-4">
                    {renderStars(selectedPlace.rating)}
                    {selectedPlace.user_ratings_total && (
                      <span className="text-gray-600">
                        {selectedPlace.user_ratings_total} reviews
                      </span>
                    )}
                  </div>
                  {selectedPlace.sentiment_analysis && (
                    <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                      <p className="text-sm">
                        <strong>Sentiment Analysis:</strong>{' '}
                        <span className={`font-semibold ${
                          selectedPlace.sentiment_analysis.sentiment_label === 'Positive' ? 'text-green-700' :
                          selectedPlace.sentiment_analysis.sentiment_label === 'Negative' ? 'text-red-700' :
                          'text-gray-700'
                        }`}>
                          {selectedPlace.sentiment_analysis.sentiment_label}
                        </span>
                        {' '}({selectedPlace.sentiment_analysis.average_sentiment.toFixed(2)})
                      </p>
                    </div>
                  )}
                  {selectedPlace.reviews && calculateReviewVelocity(selectedPlace.reviews) && (
                    <div className="mt-3 p-3 bg-purple-50 rounded-lg">
                      <p className="text-sm">
                        <strong>Review Velocity:</strong>{' '}
                        {calculateReviewVelocity(selectedPlace.reviews)?.reviewsPerWeek} reviews/week
                        {' '}({calculateReviewVelocity(selectedPlace.reviews)?.totalReviews} total reviews over {calculateReviewVelocity(selectedPlace.reviews)?.weeksTracked} weeks)
                      </p>
                      <p className="text-xs mt-1 text-gray-600">
                        {calculateReviewVelocity(selectedPlace.reviews)?.interpretation}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Contact Information */}
              {(selectedPlace.formatted_phone_number || selectedPlace.website) && (
                <div className="border-t pt-4">
                  <h4 className="font-semibold mb-2 flex items-center">
                    <Phone className="w-5 h-5 mr-1" />
                    Contact Information
                  </h4>
                  <div className="space-y-2">
                    {selectedPlace.formatted_phone_number && (
                      <p className="text-gray-700">
                        <strong>Phone:</strong>{' '}
                        <a
                          href={`tel:${selectedPlace.formatted_phone_number}`}
                          className="text-blue-600 hover:underline"
                        >
                          {selectedPlace.formatted_phone_number}
                        </a>
                      </p>
                    )}
                    {selectedPlace.website && (
                      <p className="text-gray-700">
                        <strong>Website:</strong>{' '}
                        <a
                          href={selectedPlace.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline"
                        >
                          {selectedPlace.website}
                        </a>
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* Opening Hours */}
              {selectedPlace.opening_hours && (
                <div className="border-t pt-4">
                  <h4 className="font-semibold mb-2 flex items-center">
                    <Clock className="w-5 h-5 mr-1" />
                    Opening Hours
                  </h4>
                  {selectedPlace.opening_hours.open_now !== undefined && (
                    <p className="mb-2">
                      <span
                        className={`px-2 py-1 rounded text-sm ${
                          selectedPlace.opening_hours.open_now
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {selectedPlace.opening_hours.open_now ? 'Open Now' : 'Closed'}
                      </span>
                    </p>
                  )}
                  {selectedPlace.opening_hours.weekday_text && (
                    <ul className="space-y-1 text-sm">
                      {selectedPlace.opening_hours.weekday_text.map((day, idx) => (
                        <li key={idx} className="text-gray-700">
                          {day}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}

              {/* Reviews */}
              {selectedPlace.reviews && selectedPlace.reviews.length > 0 && (
                <div className="border-t pt-4">
                  <h4 className="font-semibold mb-3 flex items-center">
                    <MessageSquare className="w-5 h-5 mr-1" />
                    Recent Reviews ({selectedPlace.reviews.length})
                  </h4>
                  <div className="space-y-4">
                    {selectedPlace.reviews.slice(0, 5).map((review, idx) => (
                      <div key={idx} className="border-l-4 border-blue-200 pl-4">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium">{review.author_name}</span>
                          <div className="flex items-center gap-2">
                            {renderStars(review.rating)}
                            <span className="text-xs text-gray-500">
                              {review.relative_time_description}
                            </span>
                          </div>
                        </div>
                        <p className="text-sm text-gray-700 mt-1">{review.text}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Photos */}
              {selectedPlace.photos && selectedPlace.photos.length > 0 && (
                <div className="border-t pt-4">
                  <h4 className="font-semibold mb-3 flex items-center">
                    <Image className="w-5 h-5 mr-1" />
                    Photos ({selectedPlace.photos.length})
                  </h4>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {selectedPlace.photos
                      .filter((photo) => photo.photo_reference)
                      .slice(0, 6)
                      .map((photo, idx) => (
                        <img
                          key={idx}
                          src={getPhotoUrl(photo.photo_reference, 200)}
                          alt={`${selectedPlace.name} photo ${idx + 1}`}
                          className="w-full h-32 object-cover rounded-lg"
                          onError={(e) => {
                            (e.target as HTMLImageElement).style.display = 'none';
                          }}
                        />
                      ))}
                  </div>
                </div>
              )}

              {/* Location */}
              {selectedPlace.geometry && (
                <div className="border-t pt-4">
                  <h4 className="font-semibold mb-2 flex items-center">
                    <Navigation className="w-5 h-5 mr-1" />
                    Location
                  </h4>
                  <p className="text-sm text-gray-600">
                    Latitude: {selectedPlace.geometry.location.lat.toFixed(6)}, Longitude:{' '}
                    {selectedPlace.geometry.location.lng.toFixed(6)}
                  </p>
                  <a
                    href={`https://www.google.com/maps/search/?api=1&query=${selectedPlace.geometry.location.lat},${selectedPlace.geometry.location.lng}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline text-sm mt-2 inline-block"
                  >
                    View on Google Maps
                  </a>
                </div>
              )}

              {/* Types */}
              {selectedPlace.types && (
                <div className="border-t pt-4">
                  <h4 className="font-semibold mb-2">Categories</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedPlace.types
                      .filter((type) => !type.startsWith('establishment'))
                      .slice(0, 5)
                      .map((type, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                        >
                          {type.replace(/_/g, ' ')}
                        </span>
                      ))}
                  </div>
                </div>
              )}

              {/* Google Places Insights */}
              <div className="border-t pt-4">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="font-semibold flex items-center">
                    <BarChart3 className="w-5 h-5 mr-1" />
                    Google Places Insights
                  </h4>
                  <div className="flex gap-2">
                    {!insights && (
                      <button
                        onClick={() => {
                          if (!selectedPlace || !selectedPlace.place_id) {
                            alert('Error: Place ID is missing. Please view place details first.');
                            console.error('Selected place:', selectedPlace);
                            return;
                          }
                          handleLoadInsights(selectedPlace.place_id);
                        }}
                        disabled={loadingInsights || !selectedPlace?.place_id}
                        className="inline-flex items-center px-4 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 bg-blue-50 text-blue-700"
                      >
                        {loadingInsights ? 'Loading...' : 'Load All Insights'}
                      </button>
                    )}
                    {insights && !aiAnalysis && (
                      <button
                        onClick={handleGenerateAnalysis}
                        disabled={loadingAnalysis || !selectedPlace?.place_id}
                        className="inline-flex items-center px-4 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 bg-green-50 text-green-700"
                      >
                        {loadingAnalysis ? 'Analyzing...' : '🤖 Generate AI Analysis'}
                      </button>
                    )}
                  </div>
                </div>

                {/* Individual Insight Buttons */}
                {!insights && (
                  <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                    <p className="text-xs text-gray-600 mb-2">Or load individual insights:</p>
                    <div className="flex flex-wrap gap-2">
                      <button
                        onClick={() => {
                          if (!selectedPlace?.place_id) {
                            alert('Error: Place ID is missing');
                            return;
                          }
                          handleLoadPopularTimes(selectedPlace.place_id);
                        }}
                        disabled={individualInsights.loading.popularTimes || !selectedPlace?.place_id}
                        className="px-3 py-1 text-xs border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
                      >
                        {individualInsights.loading.popularTimes ? 'Loading...' : 'Popular Times'}
                      </button>
                      <button
                        onClick={() => {
                          if (!selectedPlace?.place_id) {
                            alert('Error: Place ID is missing');
                            return;
                          }
                          handleLoadDwellTime(selectedPlace.place_id);
                        }}
                        disabled={individualInsights.loading.dwellTime || !selectedPlace?.place_id}
                        className="px-3 py-1 text-xs border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
                      >
                        {individualInsights.loading.dwellTime ? 'Loading...' : 'Dwell Time'}
                      </button>
                      <button
                        onClick={() => {
                          if (!selectedPlace?.place_id) {
                            alert('Error: Place ID is missing');
                            return;
                          }
                          handleLoadRepeatVisitors(selectedPlace.place_id);
                        }}
                        disabled={individualInsights.loading.repeatVisitors || !selectedPlace?.place_id}
                        className="px-3 py-1 text-xs border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
                      >
                        {individualInsights.loading.repeatVisitors ? 'Loading...' : 'Repeat Visitors'}
                      </button>
                      <button
                        onClick={() => {
                          if (!selectedPlace?.place_id) {
                            alert('Error: Place ID is missing');
                            return;
                          }
                          handleLoadVisitorGeography(selectedPlace.place_id);
                        }}
                        disabled={individualInsights.loading.visitorGeography || !selectedPlace?.place_id}
                        className="px-3 py-1 text-xs border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
                      >
                        {individualInsights.loading.visitorGeography ? 'Loading...' : 'Visitor Geography'}
                      </button>
                      <button
                        onClick={() => {
                          if (!selectedPlace?.place_id) {
                            alert('Error: Place ID is missing');
                            return;
                          }
                          handleLoadFootfallTrends(selectedPlace.place_id);
                        }}
                        disabled={individualInsights.loading.footfallTrends || !selectedPlace?.place_id}
                        className="px-3 py-1 text-xs border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
                      >
                        {individualInsights.loading.footfallTrends ? 'Loading...' : 'Footfall Trends'}
                      </button>
                    </div>
                  </div>
                )}

                {insights && (
                  <div className="space-y-6">
                    {/* Summary */}
                    {insights.summary && (
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <h5 className="font-semibold mb-2">Summary</h5>
                        <div className="space-y-2 text-sm">
                          <div>
                            <strong>Family Engagement Score:</strong>{' '}
                            {insights.summary.family_engagement_score}/100
                          </div>
                          <div>
                            <strong>Quality Indicator:</strong>{' '}
                            {insights.summary.quality_indicator}
                          </div>
                          {insights.summary.recommendations && insights.summary.recommendations.length > 0 && (
                            <div>
                              <strong>Recommendations:</strong>
                              <ul className="list-disc list-inside mt-1">
                                {insights.summary.recommendations.map((rec: string, idx: number) => (
                                  <li key={idx}>{rec}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Dwell Time */}
                    {(insights?.dwell_time || individualInsights.dwellTime) && (
                      <div className="border-l-4 border-blue-500 pl-4">
                        <h5 className="font-semibold mb-2 flex items-center">
                          <Clock className="w-4 h-4 mr-1" />
                          Dwell Time (Average Visit Duration)
                        </h5>
                        {(() => {
                          const dwellTime = insights?.dwell_time || individualInsights.dwellTime;
                          return (
                            <div className="space-y-2 text-sm">
                              <div className="flex items-center gap-4">
                                <div>
                                  <strong>Average:</strong>{' '}
                                  <span className="text-lg font-bold text-blue-600">
                                    {dwellTime.average_dwell_time_minutes} minutes
                                  </span>
                                  {dwellTime.vs_uk_average !== undefined && (
                                    <span className={`ml-2 text-xs ${
                                      dwellTime.vs_uk_average > 0 ? 'text-green-600' : 'text-gray-600'
                                    }`}>
                                      ({dwellTime.vs_uk_average > 0 ? '+' : ''}
                                      {dwellTime.vs_uk_average} vs UK average of 30 min)
                                    </span>
                                  )}
                                </div>
                              </div>
                              {dwellTime.median_dwell_time_minutes && (
                                <div>
                                  <strong>Median:</strong> {dwellTime.median_dwell_time_minutes} minutes
                                </div>
                              )}
                              <div className="p-2 bg-blue-50 rounded">
                                <strong>Interpretation:</strong>{' '}
                                <span className={dwellTime.average_dwell_time_minutes >= 45 ? 'text-green-700 font-semibold' : 
                                                 dwellTime.average_dwell_time_minutes >= 35 ? 'text-blue-700' : 'text-gray-700'}>
                                  {dwellTime.interpretation}
                                </span>
                              </div>
                              {dwellTime.distribution && (
                                <div className="mt-3">
                                  <strong>Visit Duration Distribution:</strong>
                                  <div className="mt-2 space-y-2">
                                    {Object.entries(dwellTime.distribution).map(([key, value]) => {
                                      const percentage = Number(value);
                                      return (
                                        <div key={key} className="flex items-center gap-2">
                                          <div className="w-24 text-xs">{key}:</div>
                                          <div className="flex-1 bg-gray-200 rounded-full h-4">
                                            <div 
                                              className="bg-blue-500 h-4 rounded-full"
                                              style={{ width: `${percentage}%` }}
                                            />
                                          </div>
                                          <div className="w-12 text-xs text-right">{percentage}%</div>
                                        </div>
                                      );
                                    })}
                                  </div>
                                </div>
                              )}
                            </div>
                          );
                        })()}
                      </div>
                    )}

                    {/* Repeat Visitor Rate */}
                    {(insights?.repeat_visitor_rate || individualInsights.repeatVisitors) && (
                      <div className="border-l-4 border-green-500 pl-4">
                        <h5 className="font-semibold mb-2 flex items-center">
                          <Users className="w-4 h-4 mr-1" />
                          Repeat Visitor Rate (Loyalty)
                        </h5>
                        {(() => {
                          const repeatRate = insights?.repeat_visitor_rate || individualInsights.repeatVisitors;
                          return (
                            <div className="space-y-2 text-sm">
                              <div className="flex items-center gap-4">
                                <div>
                                  <strong>Rate:</strong>{' '}
                                  <span className="text-lg font-bold text-green-600">
                                    {repeatRate.repeat_visitor_rate_percent}%
                                  </span>
                                  {repeatRate.vs_uk_average !== undefined && (
                                    <span className={`ml-2 text-xs ${
                                      repeatRate.vs_uk_average > 0 ? 'text-green-600' : 'text-gray-600'
                                    }`}>
                                      ({repeatRate.vs_uk_average > 0 ? '+' : ''}
                                      {repeatRate.vs_uk_average} vs UK average of 45%)
                                    </span>
                                  )}
                                </div>
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-6">
                                <div 
                                  className={`h-6 rounded-full flex items-center justify-center text-white text-xs font-semibold ${
                                    repeatRate.repeat_visitor_rate_percent >= 70 ? 'bg-green-600' :
                                    repeatRate.repeat_visitor_rate_percent >= 55 ? 'bg-green-500' :
                                    repeatRate.repeat_visitor_rate_percent >= 45 ? 'bg-yellow-500' :
                                    'bg-orange-500'
                                  }`}
                                  style={{ width: `${repeatRate.repeat_visitor_rate_percent}%` }}
                                >
                                  {repeatRate.repeat_visitor_rate_percent}%
                                </div>
                              </div>
                              <div className="p-2 bg-green-50 rounded">
                                <strong>Interpretation:</strong>{' '}
                                <span className={repeatRate.repeat_visitor_rate_percent >= 70 ? 'text-green-700 font-semibold' : 
                                                 repeatRate.repeat_visitor_rate_percent >= 55 ? 'text-green-700' : 'text-gray-700'}>
                                  {repeatRate.interpretation}
                                </span>
                              </div>
                              {repeatRate.trend && (
                                <div className="text-xs text-gray-600">
                                  Trend: <span className="capitalize">{repeatRate.trend}</span>
                                </div>
                              )}
                            </div>
                          );
                        })()}
                      </div>
                    )}

                    {/* Visitor Geography */}
                    {(insights?.visitor_geography || individualInsights.visitorGeography) && (
                      <div className="border-l-4 border-purple-500 pl-4">
                        <h5 className="font-semibold mb-2 flex items-center">
                          <Map className="w-4 h-4 mr-1" />
                          Visitor Geography (Distance Distribution)
                        </h5>
                        {(() => {
                          const geography = insights?.visitor_geography || individualInsights.visitorGeography;
                          return (
                            <div className="space-y-3 text-sm">
                              <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                  <span><strong>Within 5 miles (Local):</strong></span>
                                  <span className="font-semibold">{geography.within_5_miles_percent}%</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-4">
                                  <div 
                                    className="bg-purple-500 h-4 rounded-full"
                                    style={{ width: `${geography.within_5_miles_percent}%` }}
                                  />
                                </div>
                              </div>
                              <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                  <span><strong>5-15 miles (Regional):</strong></span>
                                  <span className="font-semibold">{geography['5_15_miles_percent']}%</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-4">
                                  <div 
                                    className="bg-purple-400 h-4 rounded-full"
                                    style={{ width: `${geography['5_15_miles_percent']}%` }}
                                  />
                                </div>
                              </div>
                              <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                  <span><strong>15+ miles (Far):</strong></span>
                                  <span className="font-semibold">{geography['15_plus_miles_percent']}%</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-4">
                                  <div 
                                    className="bg-purple-300 h-4 rounded-full"
                                    style={{ width: `${geography['15_plus_miles_percent']}%` }}
                                  />
                                </div>
                              </div>
                              <div className="p-2 bg-purple-50 rounded mt-3">
                                <strong>Interpretation:</strong>{' '}
                                <span className={geography['15_plus_miles_percent'] >= 10 ? 'text-purple-700 font-semibold' : 'text-gray-700'}>
                                  {geography.interpretation}
                                </span>
                              </div>
                            </div>
                          );
                        })()}
                      </div>
                    )}

                    {/* Footfall Trends */}
                    {(insights?.footfall_trends || individualInsights.footfallTrends) && (
                      <div className="border-l-4 border-orange-500 pl-4">
                        <h5 className="font-semibold mb-2 flex items-center">
                          <TrendingUp className="w-4 h-4 mr-1" />
                          Footfall Trends (12 months)
                        </h5>
                        {(() => {
                          const footfall = insights?.footfall_trends || individualInsights.footfallTrends;
                          const isGrowing = footfall.trend_direction === 'growing';
                          const isDeclining = footfall.trend_direction === 'declining';
                          
                          return (
                            <div className="space-y-3 text-sm">
                              <div className="flex items-center gap-4">
                                <div>
                                  <strong>Trend:</strong>{' '}
                                  <span className={`text-lg font-bold ${
                                    isGrowing ? 'text-green-600' :
                                    isDeclining ? 'text-red-600' : 'text-gray-600'
                                  }`}>
                                    {footfall.trend_direction.charAt(0).toUpperCase() + footfall.trend_direction.slice(1)}
                                  </span>
                                </div>
                                {footfall.monthly_change_percent !== undefined && (
                                  <div className={`text-sm ${
                                    footfall.monthly_change_percent > 0 ? 'text-green-600' : 
                                    footfall.monthly_change_percent < 0 ? 'text-red-600' : 'text-gray-600'
                                  }`}>
                                    {footfall.monthly_change_percent > 0 ? '+' : ''}
                                    {footfall.monthly_change_percent}% monthly change
                                  </div>
                                )}
                              </div>
                              <div>
                                <strong>Current Index:</strong>{' '}
                                <span className="font-semibold">{footfall.current_index}</span>
                                {' '}(Baseline: {footfall.baseline_index})
                              </div>
                              {footfall.monthly_data && footfall.monthly_data.length > 0 && (
                                <div className="mt-3">
                                  <strong>12-Month Trend:</strong>
                                  <div className="mt-2 flex items-end gap-1 h-32">
                                    {footfall.monthly_data.map((month: any, idx: number) => {
                                      const height = (month.index / footfall.baseline_index) * 100;
                                      return (
                                        <div key={idx} className="flex-1 flex flex-col items-center">
                                          <div 
                                            className={`w-full rounded-t ${
                                              month.index > footfall.baseline_index ? 'bg-green-500' :
                                              month.index < footfall.baseline_index ? 'bg-red-500' :
                                              'bg-gray-400'
                                            }`}
                                            style={{ height: `${Math.max(10, height)}%` }}
                                            title={`Month ${month.month}: ${month.index} (${month.change_from_baseline > 0 ? '+' : ''}${month.change_from_baseline})`}
                                          />
                                          <div className="text-xs text-gray-500 mt-1 transform -rotate-45 origin-top-left whitespace-nowrap">
                                            M{month.month}
                                          </div>
                                        </div>
                                      );
                                    })}
                                  </div>
                                </div>
                              )}
                              <div className={`p-2 rounded mt-3 ${
                                isGrowing ? 'bg-green-50' :
                                isDeclining ? 'bg-red-50' :
                                'bg-gray-50'
                              }`}>
                                <strong>Interpretation:</strong>{' '}
                                <span className={isGrowing ? 'text-green-700' : isDeclining ? 'text-red-700' : 'text-gray-700'}>
                                  {footfall.interpretation}
                                </span>
                                {isDeclining && footfall.monthly_change_percent && Math.abs(footfall.monthly_change_percent) > 0.3 && (
                                  <div className="mt-2 p-2 bg-yellow-100 border border-yellow-300 rounded text-xs">
                                    ⚠️ <strong>Early Warning:</strong> Significant decline may indicate emerging issues. Monitor closely.
                                  </div>
                                )}
                              </div>
                            </div>
                          );
                        })()}
                      </div>
                    )}

                    {/* Popular Times */}
                    {(insights?.popular_times || individualInsights.popularTimes) && (
                      <div className="border-l-4 border-pink-500 pl-4">
                        <h5 className="font-semibold mb-2 flex items-center">
                          <Clock className="w-4 h-4 mr-1" />
                          Popular Times
                        </h5>
                        {(() => {
                          const popularTimes = insights?.popular_times || individualInsights.popularTimes;
                          const times = popularTimes?.popular_times;
                          if (!times) return null;
                          
                          const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
                          
                          return (
                            <div className="text-sm space-y-3">
                              <div>
                                <strong>Peak Day:</strong> {popularTimes.peak_day}
                              </div>
                              <div>
                                <strong>Peak Hours:</strong>{' '}
                                {popularTimes.peak_hours?.map((h: number) => `${h}:00`).join(', ')}
                              </div>
                              <div className="mt-3">
                                <strong>Weekly Pattern:</strong>
                                <div className="mt-2 space-y-2">
                                  {days.map((day) => {
                                    const dayData = times[day];
                                    if (!dayData) return null;
                                    
                                    const maxPop = Math.max(...Object.values(dayData));
                                    const avgPop = Object.values(dayData).reduce((a: number, b: number) => a + b, 0) / Object.values(dayData).length;
                                    
                                    return (
                                      <div key={day} className="flex items-center gap-2">
                                        <div className="w-20 text-xs">{day.substring(0, 3)}:</div>
                                        <div className="flex-1 flex items-center gap-1">
                                          {[10, 12, 14, 16, 18].map((hour) => {
                                            const pop = dayData[hour] || 0;
                                            const height = (pop / maxPop) * 100;
                                            return (
                                              <div key={hour} className="flex-1 flex flex-col items-center">
                                                <div className="w-full bg-gray-200 rounded-t" style={{ height: '40px', position: 'relative' }}>
                                                  <div 
                                                    className="bg-pink-500 rounded-t w-full"
                                                    style={{ 
                                                      height: `${Math.max(5, height)}%`,
                                                      position: 'absolute',
                                                      bottom: 0
                                                    }}
                                                    title={`${hour}:00 - ${pop}%`}
                                                  />
                                                </div>
                                                <div className="text-xs text-gray-500 mt-1">{hour}:00</div>
                                              </div>
                                            );
                                          })}
                                        </div>
                                        <div className="w-16 text-xs text-gray-600">
                                          Avg: {avgPop.toFixed(0)}%
                                        </div>
                                      </div>
                                    );
                                  })}
                                </div>
                              </div>
                            </div>
                          );
                        })()}
                      </div>
                    )}
                  </div>
                )}

                {/* Individual Insights Display (when loaded separately) */}
                {!insights && (
                  <div className="space-y-6">
                    {/* Popular Times */}
                    {individualInsights.popularTimes && (
                      <div className="border-l-4 border-pink-500 pl-4">
                        <h5 className="font-semibold mb-2 flex items-center">
                          <Clock className="w-4 h-4 mr-1" />
                          Popular Times
                        </h5>
                        {(() => {
                          const popularTimes = individualInsights.popularTimes;
                          const times = popularTimes?.popular_times;
                          if (!times) return null;
                          
                          const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
                          
                          return (
                            <div className="text-sm space-y-3">
                              <div>
                                <strong>Peak Day:</strong> {popularTimes.peak_day}
                              </div>
                              <div>
                                <strong>Peak Hours:</strong>{' '}
                                {popularTimes.peak_hours?.map((h: number) => `${h}:00`).join(', ')}
                              </div>
                              <div className="mt-3">
                                <strong>Weekly Pattern:</strong>
                                <div className="mt-2 space-y-2">
                                  {days.map((day) => {
                                    const dayData = times[day];
                                    if (!dayData) return null;
                                    
                                    const maxPop = Math.max(...Object.values(dayData));
                                    const avgPop = Object.values(dayData).reduce((a: number, b: number) => a + b, 0) / Object.values(dayData).length;
                                    
                                    return (
                                      <div key={day} className="flex items-center gap-2">
                                        <div className="w-20 text-xs">{day.substring(0, 3)}:</div>
                                        <div className="flex-1 flex items-center gap-1">
                                          {[10, 12, 14, 16, 18].map((hour) => {
                                            const pop = dayData[hour] || 0;
                                            const height = (pop / maxPop) * 100;
                                            return (
                                              <div key={hour} className="flex-1 flex flex-col items-center">
                                                <div className="w-full bg-gray-200 rounded-t" style={{ height: '40px', position: 'relative' }}>
                                                  <div 
                                                    className="bg-pink-500 rounded-t w-full"
                                                    style={{ 
                                                      height: `${Math.max(5, height)}%`,
                                                      position: 'absolute',
                                                      bottom: 0
                                                    }}
                                                    title={`${hour}:00 - ${pop}%`}
                                                  />
                                                </div>
                                                <div className="text-xs text-gray-500 mt-1">{hour}:00</div>
                                              </div>
                                            );
                                          })}
                                        </div>
                                        <div className="w-16 text-xs text-gray-600">
                                          Avg: {avgPop.toFixed(0)}%
                                        </div>
                                      </div>
                                    );
                                  })}
                                </div>
                              </div>
                            </div>
                          );
                        })()}
                      </div>
                    )}

                    {/* Dwell Time */}
                    {individualInsights.dwellTime && (
                      <div className="border-l-4 border-blue-500 pl-4">
                        <h5 className="font-semibold mb-2 flex items-center">
                          <Clock className="w-4 h-4 mr-1" />
                          Dwell Time (Average Visit Duration)
                        </h5>
                        {(() => {
                          const dwellTime = individualInsights.dwellTime;
                          return (
                            <div className="space-y-2 text-sm">
                              <div className="flex items-center gap-4">
                                <div>
                                  <strong>Average:</strong>{' '}
                                  <span className="text-lg font-bold text-blue-600">
                                    {dwellTime.average_dwell_time_minutes} minutes
                                  </span>
                                  {dwellTime.vs_uk_average !== undefined && (
                                    <span className={`ml-2 text-xs ${
                                      dwellTime.vs_uk_average > 0 ? 'text-green-600' : 'text-gray-600'
                                    }`}>
                                      ({dwellTime.vs_uk_average > 0 ? '+' : ''}
                                      {dwellTime.vs_uk_average} vs UK average of 30 min)
                                    </span>
                                  )}
                                </div>
                              </div>
                              {dwellTime.median_dwell_time_minutes && (
                                <div>
                                  <strong>Median:</strong> {dwellTime.median_dwell_time_minutes} minutes
                                </div>
                              )}
                              <div className="p-2 bg-blue-50 rounded">
                                <strong>Interpretation:</strong>{' '}
                                <span className={dwellTime.average_dwell_time_minutes >= 45 ? 'text-green-700 font-semibold' : 
                                                 dwellTime.average_dwell_time_minutes >= 35 ? 'text-blue-700' : 'text-gray-700'}>
                                  {dwellTime.interpretation}
                                </span>
                              </div>
                              {dwellTime.distribution && (
                                <div className="mt-3">
                                  <strong>Visit Duration Distribution:</strong>
                                  <div className="mt-2 space-y-2">
                                    {Object.entries(dwellTime.distribution).map(([key, value]) => {
                                      const percentage = Number(value);
                                      return (
                                        <div key={key} className="flex items-center gap-2">
                                          <div className="w-24 text-xs">{key}:</div>
                                          <div className="flex-1 bg-gray-200 rounded-full h-4">
                                            <div 
                                              className="bg-blue-500 h-4 rounded-full"
                                              style={{ width: `${percentage}%` }}
                                            />
                                          </div>
                                          <div className="w-12 text-xs text-right">{percentage}%</div>
                                        </div>
                                      );
                                    })}
                                  </div>
                                </div>
                              )}
                            </div>
                          );
                        })()}
                      </div>
                    )}

                    {/* Repeat Visitor Rate */}
                    {individualInsights.repeatVisitors && (
                      <div className="border-l-4 border-green-500 pl-4">
                        <h5 className="font-semibold mb-2 flex items-center">
                          <Users className="w-4 h-4 mr-1" />
                          Repeat Visitor Rate (Loyalty)
                        </h5>
                        {(() => {
                          const repeatRate = individualInsights.repeatVisitors;
                          return (
                            <div className="space-y-2 text-sm">
                              <div className="flex items-center gap-4">
                                <div>
                                  <strong>Rate:</strong>{' '}
                                  <span className="text-lg font-bold text-green-600">
                                    {repeatRate.repeat_visitor_rate_percent}%
                                  </span>
                                  {repeatRate.vs_uk_average !== undefined && (
                                    <span className={`ml-2 text-xs ${
                                      repeatRate.vs_uk_average > 0 ? 'text-green-600' : 'text-gray-600'
                                    }`}>
                                      ({repeatRate.vs_uk_average > 0 ? '+' : ''}
                                      {repeatRate.vs_uk_average} vs UK average of 45%)
                                    </span>
                                  )}
                                </div>
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-6">
                                <div 
                                  className={`h-6 rounded-full flex items-center justify-center text-white text-xs font-semibold ${
                                    repeatRate.repeat_visitor_rate_percent >= 70 ? 'bg-green-600' :
                                    repeatRate.repeat_visitor_rate_percent >= 55 ? 'bg-green-500' :
                                    repeatRate.repeat_visitor_rate_percent >= 45 ? 'bg-yellow-500' :
                                    'bg-orange-500'
                                  }`}
                                  style={{ width: `${repeatRate.repeat_visitor_rate_percent}%` }}
                                >
                                  {repeatRate.repeat_visitor_rate_percent}%
                                </div>
                              </div>
                              <div className="p-2 bg-green-50 rounded">
                                <strong>Interpretation:</strong>{' '}
                                <span className={repeatRate.repeat_visitor_rate_percent >= 70 ? 'text-green-700 font-semibold' : 
                                                 repeatRate.repeat_visitor_rate_percent >= 55 ? 'text-green-700' : 'text-gray-700'}>
                                  {repeatRate.interpretation}
                                </span>
                              </div>
                              {repeatRate.trend && (
                                <div className="text-xs text-gray-600">
                                  Trend: <span className="capitalize">{repeatRate.trend}</span>
                                </div>
                              )}
                            </div>
                          );
                        })()}
                      </div>
                    )}

                    {/* Visitor Geography */}
                    {individualInsights.visitorGeography && (
                      <div className="border-l-4 border-purple-500 pl-4">
                        <h5 className="font-semibold mb-2 flex items-center">
                          <Map className="w-4 h-4 mr-1" />
                          Visitor Geography (Distance Distribution)
                        </h5>
                        {(() => {
                          const geography = individualInsights.visitorGeography;
                          return (
                            <div className="space-y-3 text-sm">
                              <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                  <span><strong>Within 5 miles (Local):</strong></span>
                                  <span className="font-semibold">{geography.within_5_miles_percent}%</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-4">
                                  <div 
                                    className="bg-purple-500 h-4 rounded-full"
                                    style={{ width: `${geography.within_5_miles_percent}%` }}
                                  />
                                </div>
                              </div>
                              <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                  <span><strong>5-15 miles (Regional):</strong></span>
                                  <span className="font-semibold">{geography['5_15_miles_percent']}%</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-4">
                                  <div 
                                    className="bg-purple-400 h-4 rounded-full"
                                    style={{ width: `${geography['5_15_miles_percent']}%` }}
                                  />
                                </div>
                              </div>
                              <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                  <span><strong>15+ miles (Far):</strong></span>
                                  <span className="font-semibold">{geography['15_plus_miles_percent']}%</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-4">
                                  <div 
                                    className="bg-purple-300 h-4 rounded-full"
                                    style={{ width: `${geography['15_plus_miles_percent']}%` }}
                                  />
                                </div>
                              </div>
                              <div className="p-2 bg-purple-50 rounded mt-3">
                                <strong>Interpretation:</strong>{' '}
                                <span className={geography['15_plus_miles_percent'] >= 10 ? 'text-purple-700 font-semibold' : 'text-gray-700'}>
                                  {geography.interpretation}
                                </span>
                              </div>
                            </div>
                          );
                        })()}
                      </div>
                    )}

                    {/* Footfall Trends */}
                    {individualInsights.footfallTrends && (
                      <div className="border-l-4 border-orange-500 pl-4">
                        <h5 className="font-semibold mb-2 flex items-center">
                          <TrendingUp className="w-4 h-4 mr-1" />
                          Footfall Trends (12 months)
                        </h5>
                        {(() => {
                          const footfall = individualInsights.footfallTrends;
                          const isGrowing = footfall.trend_direction === 'growing';
                          const isDeclining = footfall.trend_direction === 'declining';
                          
                          return (
                            <div className="space-y-3 text-sm">
                              <div className="flex items-center gap-4">
                                <div>
                                  <strong>Trend:</strong>{' '}
                                  <span className={`text-lg font-bold ${
                                    isGrowing ? 'text-green-600' :
                                    isDeclining ? 'text-red-600' : 'text-gray-600'
                                  }`}>
                                    {footfall.trend_direction.charAt(0).toUpperCase() + footfall.trend_direction.slice(1)}
                                  </span>
                                </div>
                                {footfall.monthly_change_percent !== undefined && (
                                  <div className={`text-sm ${
                                    footfall.monthly_change_percent > 0 ? 'text-green-600' : 
                                    footfall.monthly_change_percent < 0 ? 'text-red-600' : 'text-gray-600'
                                  }`}>
                                    {footfall.monthly_change_percent > 0 ? '+' : ''}
                                    {footfall.monthly_change_percent}% monthly change
                                  </div>
                                )}
                              </div>
                              <div>
                                <strong>Current Index:</strong>{' '}
                                <span className="font-semibold">{footfall.current_index}</span>
                                {' '}(Baseline: {footfall.baseline_index})
                              </div>
                              {footfall.monthly_data && footfall.monthly_data.length > 0 && (
                                <div className="mt-3">
                                  <strong>12-Month Trend:</strong>
                                  <div className="mt-2 flex items-end gap-1 h-32">
                                    {footfall.monthly_data.map((month: any, idx: number) => {
                                      const height = (month.index / footfall.baseline_index) * 100;
                                      return (
                                        <div key={idx} className="flex-1 flex flex-col items-center">
                                          <div 
                                            className={`w-full rounded-t ${
                                              month.index > footfall.baseline_index ? 'bg-green-500' :
                                              month.index < footfall.baseline_index ? 'bg-red-500' :
                                              'bg-gray-400'
                                            }`}
                                            style={{ height: `${Math.max(10, height)}%` }}
                                            title={`Month ${month.month}: ${month.index} (${month.change_from_baseline > 0 ? '+' : ''}${month.change_from_baseline})`}
                                          />
                                          <div className="text-xs text-gray-500 mt-1 transform -rotate-45 origin-top-left whitespace-nowrap">
                                            M{month.month}
                                          </div>
                                        </div>
                                      );
                                    })}
                                  </div>
                                </div>
                              )}
                              <div className={`p-2 rounded mt-3 ${
                                isGrowing ? 'bg-green-50' :
                                isDeclining ? 'bg-red-50' :
                                'bg-gray-50'
                              }`}>
                                <strong>Interpretation:</strong>{' '}
                                <span className={isGrowing ? 'text-green-700' : isDeclining ? 'text-red-700' : 'text-gray-700'}>
                                  {footfall.interpretation}
                                </span>
                                {isDeclining && footfall.monthly_change_percent && Math.abs(footfall.monthly_change_percent) > 0.3 && (
                                  <div className="mt-2 p-2 bg-yellow-100 border border-yellow-300 rounded text-xs">
                                    ⚠️ <strong>Early Warning:</strong> Significant decline may indicate emerging issues. Monitor closely.
                                  </div>
                                )}
                              </div>
                            </div>
                          );
                        })()}
                      </div>
                    )}
                  </div>
                )}

                {/* AI Analysis Section - Inside Modal */}
                {aiAnalysis && (
                  <div className="border-t pt-6 mt-6">
                    <div className="bg-gradient-to-r from-purple-50 via-blue-50 to-indigo-50 p-6 rounded-lg border-2 border-purple-200 shadow-lg">
                      <div className="flex items-center justify-between mb-6">
                        <h4 className="font-bold flex items-center text-2xl text-gray-800">
                          🤖 AI-Powered Analysis
                        </h4>
                      </div>
                      
                      {aiAnalysis.analysis?.executive_summary ? (
                        <>
                          {/* Executive Summary Card - Prominent Display */}
                          <div className="bg-white rounded-xl shadow-md p-6 mb-6 border-l-4 border-purple-500">
                            <div className="flex items-start justify-between mb-4">
                              <div className="flex-1">
                                <h5 className="font-bold text-xl mb-3 text-gray-800">Executive Summary</h5>
                                {aiAnalysis.analysis.executive_summary.overview && (
                                  <p className="text-gray-700 text-lg leading-relaxed mb-4">
                                    {aiAnalysis.analysis.executive_summary.overview}
                                  </p>
                                )}
                                
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                                  {aiAnalysis.analysis.executive_summary.overall_score !== null && aiAnalysis.analysis.executive_summary.overall_score !== undefined && (
                                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg">
                                      <div className="text-sm text-gray-600 mb-1">Overall Score</div>
                                      <div className="text-3xl font-bold text-blue-700">
                                        {aiAnalysis.analysis.executive_summary.overall_score}/100
                                      </div>
                                      <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                                        <div 
                                          className={`h-2 rounded-full ${
                                            aiAnalysis.analysis.executive_summary.overall_score >= 80 ? 'bg-green-500' :
                                            aiAnalysis.analysis.executive_summary.overall_score >= 60 ? 'bg-yellow-500' :
                                            'bg-red-500'
                                          }`}
                                          style={{ width: `${aiAnalysis.analysis.executive_summary.overall_score}%` }}
                                        />
                                      </div>
                                    </div>
                                  )}
                                  
                                  {aiAnalysis.analysis.executive_summary.recommendation && (
                                    <div className={`p-4 rounded-lg ${
                                      aiAnalysis.analysis.executive_summary.recommendation === 'RECOMMEND' ? 'bg-gradient-to-br from-green-50 to-green-100 border-2 border-green-300' :
                                      aiAnalysis.analysis.executive_summary.recommendation === 'CONSIDER' ? 'bg-gradient-to-br from-yellow-50 to-yellow-100 border-2 border-yellow-300' :
                                      'bg-gradient-to-br from-red-50 to-red-100 border-2 border-red-300'
                                    }`}>
                                      <div className="text-sm text-gray-600 mb-1">Recommendation</div>
                                      <div className={`text-xl font-bold ${
                                        aiAnalysis.analysis.executive_summary.recommendation === 'RECOMMEND' ? 'text-green-700' :
                                        aiAnalysis.analysis.executive_summary.recommendation === 'CONSIDER' ? 'text-yellow-700' :
                                        'text-red-700'
                                      }`}>
                                        {aiAnalysis.analysis.executive_summary.recommendation}
                                      </div>
                                    </div>
                                  )}
                                  
                                  {aiAnalysis.analysis.executive_summary.key_highlight && (
                                    <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg">
                                      <div className="text-sm text-gray-600 mb-1">Key Highlight</div>
                                      <div className="text-sm font-semibold text-purple-700">
                                        {aiAnalysis.analysis.executive_summary.key_highlight}
                                      </div>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Detailed Analysis Sections */}
                          <div className="space-y-4">
                            {aiAnalysis.analysis.detailed_analysis && (
                              <div className="bg-white p-5 rounded-lg shadow">
                                <h5 className="font-bold text-lg mb-3 text-gray-800">Detailed Analysis</h5>
                                <div className="space-y-4">
                                  {Object.entries(aiAnalysis.analysis.detailed_analysis).map(([key, value]: [string, any]) => (
                                    <div key={key} className="border-l-4 border-blue-400 pl-4">
                                      <div className="flex items-center justify-between mb-2">
                                        <h6 className="font-semibold text-gray-700 capitalize">
                                          {key.replace(/_/g, ' ')}
                                        </h6>
                                        {value.score !== null && value.score !== undefined && (
                                          <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                                            value.score >= 80 ? 'bg-green-100 text-green-700' :
                                            value.score >= 60 ? 'bg-yellow-100 text-yellow-700' :
                                            'bg-red-100 text-red-700'
                                          }`}>
                                            {value.score}/100
                                          </span>
                                        )}
                                      </div>
                                      {value.analysis && (
                                        <p className="text-gray-600 text-sm mb-2">{value.analysis}</p>
                                      )}
                                      {value.interpretation && (
                                        <p className="text-gray-500 text-xs italic">{value.interpretation}</p>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Key Insights */}
                            {aiAnalysis.analysis.key_insights && Array.isArray(aiAnalysis.analysis.key_insights) && aiAnalysis.analysis.key_insights.length > 0 && (
                              <div className="bg-white p-5 rounded-lg shadow border-l-4 border-green-500">
                                <h5 className="font-bold text-lg mb-3 text-gray-800">Key Insights</h5>
                                <ul className="space-y-2">
                                  {aiAnalysis.analysis.key_insights.map((insight: string, idx: number) => (
                                    <li key={idx} className="flex items-start text-gray-700">
                                      <span className="text-green-500 mr-2">✓</span>
                                      <span>{insight}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {/* Recommendations */}
                            {aiAnalysis.analysis.recommendations && (
                              <div className="bg-white p-5 rounded-lg shadow border-l-4 border-yellow-500">
                                <h5 className="font-bold text-lg mb-3 text-gray-800">Recommendations</h5>
                                {aiAnalysis.analysis.recommendations.for_families && Array.isArray(aiAnalysis.analysis.recommendations.for_families) && aiAnalysis.analysis.recommendations.for_families.length > 0 && (
                                  <div className="mb-4">
                                    <h6 className="font-semibold text-gray-700 mb-2">For Families:</h6>
                                    <ul className="space-y-2">
                                      {aiAnalysis.analysis.recommendations.for_families.map((rec: string, idx: number) => (
                                        <li key={idx} className="flex items-start text-gray-700">
                                          <span className="text-yellow-500 mr-2">→</span>
                                          <span>{rec}</span>
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                                {aiAnalysis.analysis.recommendations.for_management && Array.isArray(aiAnalysis.analysis.recommendations.for_management) && aiAnalysis.analysis.recommendations.for_management.length > 0 && (
                                  <div>
                                    <h6 className="font-semibold text-gray-700 mb-2">For Management:</h6>
                                    <ul className="space-y-2">
                                      {aiAnalysis.analysis.recommendations.for_management.map((rec: string, idx: number) => (
                                        <li key={idx} className="flex items-start text-gray-700">
                                          <span className="text-yellow-500 mr-2">→</span>
                                          <span>{rec}</span>
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                              </div>
                            )}

                            {/* Risk Assessment */}
                            {aiAnalysis.analysis.risk_assessment && (
                              <div className={`bg-white p-5 rounded-lg shadow border-l-4 ${
                                aiAnalysis.analysis.risk_assessment.level === 'LOW' ? 'border-green-500' :
                                aiAnalysis.analysis.risk_assessment.level === 'MEDIUM' ? 'border-yellow-500' :
                                'border-red-500'
                              }`}>
                                <div className="flex items-center justify-between mb-3">
                                  <h5 className="font-bold text-lg text-gray-800">Risk Assessment</h5>
                                  <span className={`px-4 py-1 rounded-full text-sm font-bold ${
                                    aiAnalysis.analysis.risk_assessment.level === 'LOW' ? 'bg-green-100 text-green-700' :
                                    aiAnalysis.analysis.risk_assessment.level === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700' :
                                    'bg-red-100 text-red-700'
                                  }`}>
                                    {aiAnalysis.analysis.risk_assessment.level} RISK
                                  </span>
                                </div>
                                {aiAnalysis.analysis.risk_assessment.score !== null && aiAnalysis.analysis.risk_assessment.score !== undefined && (
                                  <div className="mb-3">
                                    <div className="text-sm text-gray-600 mb-1">Risk Score: {aiAnalysis.analysis.risk_assessment.score}/100</div>
                                    <div className="w-full bg-gray-200 rounded-full h-2">
                                      <div 
                                        className={`h-2 rounded-full ${
                                          aiAnalysis.analysis.risk_assessment.score <= 30 ? 'bg-green-500' :
                                          aiAnalysis.analysis.risk_assessment.score <= 60 ? 'bg-yellow-500' :
                                          'bg-red-500'
                                        }`}
                                        style={{ width: `${aiAnalysis.analysis.risk_assessment.score}%` }}
                                      />
                                    </div>
                                  </div>
                                )}
                                {aiAnalysis.analysis.risk_assessment.explanation && (
                                  <p className="text-gray-700 mb-3">{aiAnalysis.analysis.risk_assessment.explanation}</p>
                                )}
                                {aiAnalysis.analysis.risk_assessment.concerns && Array.isArray(aiAnalysis.analysis.risk_assessment.concerns) && aiAnalysis.analysis.risk_assessment.concerns.length > 0 && (
                                  <div>
                                    <h6 className="font-semibold text-red-700 mb-2">Concerns:</h6>
                                    <ul className="space-y-1">
                                      {aiAnalysis.analysis.risk_assessment.concerns.map((concern: string, idx: number) => (
                                        <li key={idx} className="flex items-start text-red-600 text-sm">
                                          <span className="mr-2">⚠️</span>
                                          <span>{concern}</span>
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        </>
                      ) : aiAnalysis.raw_text ? (
                        <div className="bg-white p-6 rounded-lg shadow">
                          <div className="prose prose-sm max-w-none">
                            <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
                              {aiAnalysis.raw_text}
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="text-gray-600">Analysis data is being processed...</div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


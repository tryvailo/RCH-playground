import { useState, useEffect } from 'react';
import { MapPin, Filter, TrendingUp, AlertCircle, RefreshCw } from 'lucide-react';
import axios from 'axios';

interface LocationData {
  local_authority: string;
  region: string;
  care_type: string;
  fair_cost_lower_bound_gbp: number | null;
  private_average_gbp: number;
  affordability_band: string;
  band_confidence_percent: number;
  fair_cost_gap_gbp: number;
  fair_cost_gap_percent: number;
}

export default function AllLocations() {
  const [loading, setLoading] = useState(false);
  const [locations, setLocations] = useState<LocationData[]>([]);
  const [filteredLocations, setFilteredLocations] = useState<LocationData[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [regions, setRegions] = useState<string[]>([]);
  const [careTypes, setCareTypes] = useState<string[]>([]);

  const [filters, setFilters] = useState({
    care_type: '',
    region: '',
    band: '',
    min_fair_cost: '',
    max_fair_cost: '',
  });

  useEffect(() => {
    fetchData();
    fetchRegions();
    fetchCareTypes();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [locations, filters]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get('/api/rch-data/pricing/locations');
      setLocations(response.data.data || []);
    } catch (err: any) {
      console.error('Error fetching locations:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch locations';
      
      // Provide more helpful error messages
      if (errorMessage.includes('not available') || errorMessage.includes('503')) {
        setError(
          'Pricing calculator module is not available. Please ensure RCH-data package is installed: pip install -e ../RCH-data'
        );
      } else if (err.response?.status === 404) {
        setError('API endpoint not found. Please check that the backend server is running.');
      } else if (err.response?.status === 500) {
        setError(`Server error: ${errorMessage}. Check backend logs for details.`);
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchRegions = async () => {
    try {
      const response = await axios.get('/api/rch-data/pricing/regions');
      setRegions(response.data.regions || []);
    } catch (err) {
      console.error('Failed to fetch regions:', err);
    }
  };

  const fetchCareTypes = async () => {
    try {
      const response = await axios.get('/api/rch-data/pricing/care-types');
      setCareTypes(response.data.care_types || []);
    } catch (err) {
      console.error('Failed to fetch care types:', err);
    }
  };

  const applyFilters = () => {
    let filtered = [...locations];

    if (filters.care_type) {
      filtered = filtered.filter((loc) => loc.care_type === filters.care_type);
    }

    if (filters.region) {
      filtered = filtered.filter((loc) => loc.region === filters.region);
    }

    if (filters.band) {
      filtered = filtered.filter((loc) => loc.affordability_band === filters.band);
    }

    if (filters.min_fair_cost) {
      const min = parseFloat(filters.min_fair_cost);
      filtered = filtered.filter(
        (loc) => loc.fair_cost_lower_bound_gbp && loc.fair_cost_lower_bound_gbp >= min
      );
    }

    if (filters.max_fair_cost) {
      const max = parseFloat(filters.max_fair_cost);
      filtered = filtered.filter(
        (loc) => loc.fair_cost_lower_bound_gbp && loc.fair_cost_lower_bound_gbp <= max
      );
    }

    setFilteredLocations(filtered);
  };

  const bandColors: Record<string, string> = {
    A: 'bg-green-100 text-green-800',
    B: 'bg-green-100 text-green-800',
    C: 'bg-yellow-100 text-yellow-800',
    D: 'bg-orange-100 text-orange-800',
    E: 'bg-red-100 text-red-800',
  };

  const stats = {
    total: filteredLocations.length,
    avgFairCost:
      filteredLocations
        .filter((loc) => loc.fair_cost_lower_bound_gbp)
        .reduce((sum, loc) => sum + (loc.fair_cost_lower_bound_gbp || 0), 0) /
      filteredLocations.filter((loc) => loc.fair_cost_lower_bound_gbp).length || 0,
    avgPrivate:
      filteredLocations.reduce((sum, loc) => sum + loc.private_average_gbp, 0) /
      filteredLocations.length || 0,
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <MapPin className="w-8 h-8" />
          All Locations Pricing Table
        </h1>
        <p className="mt-2 text-gray-600">
          Pricing data for all UK Local Authorities with affordability bands
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <span className="text-red-800">{error}</span>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-5 h-5 text-gray-600" />
          <h2 className="text-lg font-semibold">Filters</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Care Type</label>
            <select
              value={filters.care_type}
              onChange={(e) => setFilters({ ...filters, care_type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">All</option>
              {careTypes.map((ct) => (
                <option key={ct} value={ct}>
                  {ct.replace('_', ' ')}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Region</label>
            <select
              value={filters.region}
              onChange={(e) => setFilters({ ...filters, region: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">All</option>
              {regions.map((region) => (
                <option key={region} value={region}>
                  {region}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Affordability Band</label>
            <select
              value={filters.band}
              onChange={(e) => setFilters({ ...filters, band: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">All</option>
              <option value="A">A - Excellent</option>
              <option value="B">B - Good</option>
              <option value="C">C - Fair</option>
              <option value="D">D - Premium</option>
              <option value="E">E - Very Expensive</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Min Fair Cost (£/week)
            </label>
            <input
              type="number"
              value={filters.min_fair_cost}
              onChange={(e) => setFilters({ ...filters, min_fair_cost: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="Min"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Fair Cost (£/week)
            </label>
            <input
              type="number"
              value={filters.max_fair_cost}
              onChange={(e) => setFilters({ ...filters, max_fair_cost: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="Max"
            />
          </div>
        </div>

        <div className="mt-4 flex items-center gap-2">
          <button
            onClick={fetchData}
            disabled={loading}
            className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4" />
            )}
            Refresh Data
          </button>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Total Locations</div>
          <div className="text-2xl font-bold">{stats.total}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Avg Fair Cost</div>
          <div className="text-2xl font-bold">
            £{stats.avgFairCost > 0 ? stats.avgFairCost.toFixed(2) : '0.00'}/week
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Avg Private</div>
          <div className="text-2xl font-bold">
            £{stats.avgPrivate > 0 ? stats.avgPrivate.toFixed(2) : '0.00'}/week
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto text-gray-400" />
            <p className="mt-2 text-gray-600">Loading data...</p>
          </div>
        ) : filteredLocations.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Local Authority
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Region
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Care Type
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Fair Cost (£/week)
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Private Avg (£/week)
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Gap
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Gap %
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Band
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Confidence
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredLocations.map((loc, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium">{loc.local_authority}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{loc.region}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {loc.care_type.replace('_', ' ')}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      {loc.fair_cost_lower_bound_gbp
                        ? `£${loc.fair_cost_lower_bound_gbp.toFixed(2)}`
                        : 'N/A'}
                    </td>
                    <td className="px-4 py-3 text-sm">£{loc.private_average_gbp.toFixed(2)}</td>
                    <td className="px-4 py-3 text-sm">
                      <span
                        className={
                          loc.fair_cost_gap_gbp < 0
                            ? 'text-green-600'
                            : loc.fair_cost_gap_gbp > 0
                            ? 'text-red-600'
                            : 'text-gray-600'
                        }
                      >
                        £{loc.fair_cost_gap_gbp.toFixed(2)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span
                        className={
                          loc.fair_cost_gap_percent < 0
                            ? 'text-green-600'
                            : loc.fair_cost_gap_percent > 0
                            ? 'text-red-600'
                            : 'text-gray-600'
                        }
                      >
                        {loc.fair_cost_gap_percent.toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span
                        className={`inline-block px-2 py-1 rounded text-xs font-semibold ${
                          bandColors[loc.affordability_band] || 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {loc.affordability_band}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">{loc.band_confidence_percent}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-8 text-center text-gray-500">No locations found</div>
        )}
      </div>
    </div>
  );
}


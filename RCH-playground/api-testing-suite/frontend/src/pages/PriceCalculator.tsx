import { useState } from 'react';
import { Calculator, DollarSign, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';
import axios from 'axios';

interface PricingResult {
  postcode: string;
  local_authority: string;
  region: string;
  care_type: string;
  fair_cost_lower_bound_gbp: number | null;  // MSIF lower bound
  private_average_gbp: number;  // Final price / Lottie average
  expected_range_min_gbp: number;
  expected_range_max_gbp: number;
  affordability_band: string;
  band_confidence_percent: number;
  fair_cost_gap_gbp: number;
  fair_cost_gap_percent: number;
  negotiation_leverage_text: string;
  sources_used?: string[];
  cqc_rating?: string | null;
  facilities_score?: number | null;
  bed_count?: number | null;
  is_chain?: boolean;
}

export default function PriceCalculator() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PricingResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    postcode: 'B15 2HQ',
    care_type: 'residential',
    cqc_rating: '',
    facilities_score: 10,
    bed_count: 25,
    is_chain: false,
    scraped_price: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post('/api/rch-data/pricing/calculate', {
        postcode: formData.postcode,
        care_type: formData.care_type,
        cqc_rating: formData.cqc_rating || undefined,
        facilities_score: formData.facilities_score > 0 ? formData.facilities_score : undefined,
        bed_count: formData.bed_count > 0 ? formData.bed_count : undefined,
        is_chain: formData.is_chain,
        scraped_price: formData.scraped_price ? parseFloat(formData.scraped_price) : undefined,
      });

      setResult(response.data);
    } catch (err: any) {
      console.error('Error calculating pricing:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to calculate pricing';
      
      // Provide more helpful error messages
      if (errorMessage.includes('not available') || errorMessage.includes('503')) {
        setError(
          'Pricing calculator module is not available. Please ensure RCH-data package is installed: pip install -e ../RCH-data'
        );
      } else if (err.response?.status === 404) {
        setError('API endpoint not found. Please check that the backend server is running.');
      } else if (err.response?.status === 400) {
        setError(`Invalid request: ${errorMessage}`);
      } else if (err.response?.status === 500) {
        setError(`Server error: ${errorMessage}. Check backend logs for details.`);
      } else if (!err.response) {
        setError('Cannot connect to backend server. Please ensure the server is running on http://localhost:8000');
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  const bandColors: Record<string, string> = {
    A: 'bg-green-100 text-green-800',
    B: 'bg-green-100 text-green-800',
    C: 'bg-yellow-100 text-yellow-800',
    D: 'bg-orange-100 text-orange-800',
    E: 'bg-red-100 text-red-800',
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <Calculator className="w-8 h-8" />
          Price Calculator
        </h1>
        <p className="mt-2 text-gray-600">
          Calculate pricing and Affordability Bands using MSIF and Lottie data
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <span className="text-red-800">{error}</span>
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Postcode
              </label>
              <input
                type="text"
                value={formData.postcode}
                onChange={(e) => setFormData({ ...formData, postcode: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="e.g., B15 2HQ"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Care Type
              </label>
              <select
                value={formData.care_type}
                onChange={(e) => setFormData({ ...formData, care_type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="residential">Residential</option>
                <option value="nursing">Nursing</option>
                <option value="residential_dementia">Residential Dementia</option>
                <option value="nursing_dementia">Nursing Dementia</option>
                <option value="respite">Respite</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                CQC Rating (Optional)
              </label>
              <select
                value={formData.cqc_rating}
                onChange={(e) => setFormData({ ...formData, cqc_rating: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="">Not specified</option>
                <option value="Outstanding">Outstanding</option>
                <option value="Good">Good</option>
                <option value="Requires Improvement">Requires Improvement</option>
                <option value="Inadequate">Inadequate</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Facilities Score (0-20)
              </label>
              <input
                type="range"
                min="0"
                max="20"
                value={formData.facilities_score}
                onChange={(e) =>
                  setFormData({ ...formData, facilities_score: parseInt(e.target.value) })
                }
                className="w-full"
              />
              <div className="text-sm text-gray-500 text-center mt-1">
                {formData.facilities_score}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Bed Count (Optional)
              </label>
              <input
                type="number"
                min="1"
                max="200"
                value={formData.bed_count}
                onChange={(e) =>
                  setFormData({ ...formData, bed_count: parseInt(e.target.value) || 0 })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Scraped Price (Optional - Overrides Calculation)
              </label>
              <input
                type="number"
                min="0"
                step="10"
                value={formData.scraped_price}
                onChange={(e) => setFormData({ ...formData, scraped_price: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="GBP/week"
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is_chain"
              checked={formData.is_chain}
              onChange={(e) => setFormData({ ...formData, is_chain: e.target.checked })}
              className="w-4 h-4"
            />
            <label htmlFor="is_chain" className="text-sm text-gray-700">
              Is part of a chain
            </label>
          </div>

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
                Calculate Pricing
              </>
            )}
          </button>
        </form>
      </div>

      {result && (
        <div className="bg-white rounded-lg shadow p-6 space-y-6">
          <div className="flex items-center gap-2 text-green-600">
            <CheckCircle className="w-5 h-5" />
            <span className="font-semibold">Pricing calculated successfully!</span>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-600">Final Price</div>
              <div className="text-2xl font-bold">
                £{result.private_average_gbp.toFixed(2)}/week
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-600">MSIF Lower Bound</div>
              <div className="text-2xl font-bold">
                {result.fair_cost_lower_bound_gbp
                  ? `£${result.fair_cost_lower_bound_gbp.toFixed(2)}/week`
                  : 'N/A'}
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-600">Expected Range</div>
              <div className="text-lg font-semibold">
                £{result.expected_range_min_gbp.toFixed(2)} - £{result.expected_range_max_gbp.toFixed(2)}/week
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-600">Fair Cost Gap</div>
              <div className="text-2xl font-bold">
                £{result.fair_cost_gap_gbp.toFixed(2)}
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-600">Gap %</div>
              <div className="text-2xl font-bold">{result.fair_cost_gap_percent.toFixed(1)}%</div>
            </div>
          </div>

          {/* Affordability Band */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Affordability Band
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <div
                  className={`inline-block px-4 py-2 rounded-lg font-bold text-lg mb-2 ${
                    bandColors[result.affordability_band] || 'bg-gray-100 text-gray-800'
                  }`}
                >
                  Band {result.affordability_band}
                </div>
                <div className="mt-2">
                  <div className="text-sm text-gray-600 mb-1">Confidence</div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        result.band_confidence_percent >= 80
                          ? 'bg-green-500'
                          : result.band_confidence_percent >= 70
                          ? 'bg-yellow-500'
                          : 'bg-red-500'
                      }`}
                      style={{ width: `${result.band_confidence_percent}%` }}
                    />
                  </div>
                  <div className="text-sm text-gray-500 mt-1">
                    {result.band_confidence_percent}% confidence
                  </div>
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600 mb-2">Location Info</div>
                <div className="space-y-1 text-sm">
                  <div>
                    <span className="font-medium">Postcode:</span> {result.postcode}
                  </div>
                  <div>
                    <span className="font-medium">Local Authority:</span> {result.local_authority}
                  </div>
                  <div>
                    <span className="font-medium">Region:</span> {result.region}
                  </div>
                  <div>
                    <span className="font-medium">Care Type:</span>{' '}
                    {result.care_type.replace('_', ' ')}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Negotiation Leverage Text */}
          {result.negotiation_leverage_text && (
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                <DollarSign className="w-5 h-5" />
                Negotiation Leverage Text
              </h3>
              <textarea
                readOnly
                value={result.negotiation_leverage_text}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                rows={6}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}


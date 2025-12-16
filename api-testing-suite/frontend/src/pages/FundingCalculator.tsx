import { useState } from 'react';
import { Calculator, DollarSign, TrendingUp, AlertCircle, CheckCircle, Heart } from 'lucide-react';
import axios from 'axios';

interface FundingResult {
  chc_eligibility: {
    probability_percent: number;
    is_likely_eligible: boolean;
    threshold_category: string;
    reasoning: string;
    key_factors?: string[];
  };
  la_support: {
    top_up_probability_percent: number;
    full_support_probability_percent: number;
    capital_assessed: number;
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
}

export default function FundingCalculator() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<FundingResult | null>(null);
  const [error, setError] = useState<string | null>(null);

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
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Build domain assessments (simplified - in full version would have 12 domains)
      const domain_assessments: Record<string, any> = {};
      
      // Simplified: just mark if has primary health need
      if (formData.has_primary_health_need) {
        domain_assessments['BREATHING'] = {
          level: 'MODERATE',
          description: 'Primary health need identified',
        };
      }

      const requestData = {
        age: formData.age,
        domain_assessments,
        has_primary_health_need: formData.has_primary_health_need,
        requires_nursing_care: formData.requires_nursing_care,
        capital_assets: formData.capital_assets,
        weekly_income: formData.weekly_income,
        care_type: formData.care_type,
        is_permanent_care: true,
        postcode: formData.postcode || undefined,
        property: formData.has_property
          ? {
              value: formData.property_value,
              is_main_residence: formData.is_main_residence,
              has_qualifying_relative: formData.has_qualifying_relative,
            }
          : null,
      };

      const response = await axios.post('/api/rch-data/funding/calculate', requestData);
      setResult(response.data);
    } catch (err: any) {
      console.error('Error calculating funding:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to calculate funding eligibility';
      
      if (errorMessage.includes('not available') || err.response?.status === 503) {
        setError(
          'Funding calculator module is not available. Please ensure RCH-data package is installed: pip install -e ../RCH-data'
        );
      } else if (!err.response) {
        setError('Cannot connect to backend server. Please ensure the server is running on http://localhost:8000');
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <Heart className="w-8 h-8" />
          Funding Eligibility Calculator
        </h1>
        <p className="mt-2 text-gray-600">
          Advanced CHC & LA Funding Assessment Tool (2025-2026)
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
              <input
                type="text"
                value={formData.postcode}
                onChange={(e) => setFormData({ ...formData, postcode: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="e.g., B15 2HQ"
              />
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
                    Has Qualifying Relative Living There
                  </label>
                </div>
              </div>
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
                  £{result.la_support.capital_assessed.toFixed(2)}
                </div>
              </div>
            </div>
            <div className="mt-4 bg-blue-50 rounded-lg p-4">
              <div className="text-sm text-gray-700">{result.la_support.reasoning}</div>
            </div>
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
                  £{result.savings.weekly_savings.toFixed(2)}
                </div>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Annual Savings</div>
                <div className="text-xl font-bold text-green-600">
                  £{result.savings.annual_gbp.toFixed(0)}
                </div>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">5-Year Savings</div>
                <div className="text-xl font-bold text-green-600">
                  £{result.savings.five_year_gbp.toFixed(0)}
                </div>
              </div>
              {result.savings.lifetime_gbp && (
                <div className="bg-green-50 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Lifetime Estimate</div>
                  <div className="text-xl font-bold text-green-600">
                    £{result.savings.lifetime_gbp.toFixed(0)}
                  </div>
                </div>
              )}
            </div>
            {result.savings.annual_gbp > 10000 && (
              <div className="mt-4 bg-green-100 border border-green-300 rounded-lg p-4">
                <div className="text-lg font-semibold text-green-800">
                  🎉 Potential annual savings: £{result.savings.annual_gbp.toFixed(0)}
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
        </div>
      )}
    </div>
  );
}


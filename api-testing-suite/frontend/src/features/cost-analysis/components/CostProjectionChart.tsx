import { useState } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import type { EnhancedProjections, HomeProjectionEnhanced } from '../types';

interface CostProjectionChartProps {
  projections: EnhancedProjections | null | undefined;
  selectedHomeId?: string;
}

// Safe number helper
const safeNumber = (value: unknown, defaultValue = 0): number => {
  if (value === null || value === undefined) return defaultValue;
  const num = Number(value);
  return isNaN(num) ? defaultValue : num;
};

export default function CostProjectionChart({ projections, selectedHomeId }: CostProjectionChartProps) {
  const [viewMode, setViewMode] = useState<'cumulative' | 'annual'>('cumulative');
  const [showHiddenFees, setShowHiddenFees] = useState(true);

  // Handle null/undefined projections
  if (!projections?.projections || projections.projections.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg border border-gray-200 p-4 text-center text-gray-500">
        No cost projections available
      </div>
    );
  }

  const selectedHome = selectedHomeId
    ? projections.projections.find(p => p?.home_id === selectedHomeId)
    : projections.projections[0];

  if (!selectedHome) {
    return (
      <div className="bg-gray-50 rounded-lg border border-gray-200 p-4 text-center text-gray-500">
        Selected home projection not found
      </div>
    );
  }
  
  // Safe access to years array
  const years = selectedHome.years || [];
  const summary = selectedHome.summary || {};
  const overallSummary = projections.overall_summary || { inflation_rate_used: 4 };

  const formatCurrency = (value: number) => `£${value.toLocaleString()}`;
  const formatCurrencyShort = (value: number) => `£${(value / 1000).toFixed(0)}k`;

  const chartData = years.map(year => ({
    year: `Year ${safeNumber(year?.year, 0)}`,
    yearNumber: safeNumber(year?.year, 0),
    'Advertised Cost': viewMode === 'cumulative' 
      ? safeNumber(year?.cumulative_advertised) 
      : safeNumber(year?.advertised_annual),
    'True Cost': viewMode === 'cumulative' 
      ? safeNumber(year?.cumulative_true) 
      : safeNumber(year?.true_annual),
    'Hidden Fees': viewMode === 'cumulative' 
      ? safeNumber(year?.cumulative_hidden) 
      : safeNumber(year?.hidden_fees_annual),
    inflationFactor: safeNumber(year?.inflation_factor, 1)
  }));

  const totalDifference = safeNumber(summary.total_5_year_true) - safeNumber(summary.total_5_year_advertised);

  return (
    <div className="space-y-4">
      {/* Header with Summary */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h4 className="font-semibold text-lg text-gray-900">{selectedHome.home_name}</h4>
            <p className="text-sm text-gray-500">5-Year Cost Projection with Hidden Fees</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode('cumulative')}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${
                viewMode === 'cumulative'
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Cumulative
            </button>
            <button
              onClick={() => setViewMode('annual')}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${
                viewMode === 'annual'
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Annual
            </button>
          </div>
        </div>

        {/* Key Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-xs text-gray-500 mb-1">5-Year Advertised</div>
            <div className="text-lg font-bold text-gray-900">
              {formatCurrency(safeNumber(summary.total_5_year_advertised))}
            </div>
          </div>
          <div className="bg-red-50 rounded-lg p-3">
            <div className="text-xs text-gray-500 mb-1">5-Year True Cost</div>
            <div className="text-lg font-bold text-red-600">
              {formatCurrency(safeNumber(summary.total_5_year_true))}
            </div>
          </div>
          <div className="bg-amber-50 rounded-lg p-3">
            <div className="text-xs text-gray-500 mb-1">Total Hidden Fees</div>
            <div className="text-lg font-bold text-amber-600">
              +{formatCurrency(safeNumber(summary.total_5_year_hidden))}
            </div>
          </div>
          <div className="bg-purple-50 rounded-lg p-3">
            <div className="text-xs text-gray-500 mb-1">Hidden Fee Impact</div>
            <div className="text-lg font-bold text-purple-600">
              +{safeNumber(summary.hidden_fees_percent)}%
            </div>
          </div>
        </div>

        {/* Toggle Hidden Fees */}
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showHiddenFees}
              onChange={(e) => setShowHiddenFees(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-600">Show Hidden Fees Breakdown</span>
          </label>
        </div>
      </div>

      {/* Main Chart */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h5 className="text-sm font-semibold text-gray-900 mb-4">
          {viewMode === 'cumulative' ? 'Cumulative' : 'Annual'} Cost Comparison
        </h5>
        <ResponsiveContainer width="100%" height={350}>
          {showHiddenFees ? (
            <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 20, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis 
                dataKey="year" 
                stroke="#6B7280"
                style={{ fontSize: '12px' }}
              />
              <YAxis 
                stroke="#6B7280"
                style={{ fontSize: '12px' }}
                tickFormatter={formatCurrencyShort}
              />
              <Tooltip 
                formatter={(value: number, name: string) => [formatCurrency(value), name]}
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                  fontSize: '12px'
                }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              <Area
                type="monotone"
                dataKey="Advertised Cost"
                stackId="1"
                stroke="#6B7280"
                fill="#E5E7EB"
                fillOpacity={0.6}
              />
              <Area
                type="monotone"
                dataKey="Hidden Fees"
                stackId="1"
                stroke="#F59E0B"
                fill="#FDE68A"
                fillOpacity={0.8}
              />
            </AreaChart>
          ) : (
            <LineChart data={chartData} margin={{ top: 10, right: 30, left: 20, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis 
                dataKey="year" 
                stroke="#6B7280"
                style={{ fontSize: '12px' }}
              />
              <YAxis 
                stroke="#6B7280"
                style={{ fontSize: '12px' }}
                tickFormatter={formatCurrencyShort}
              />
              <Tooltip 
                formatter={(value: number, name: string) => [formatCurrency(value), name]}
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                  fontSize: '12px'
                }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              <Line
                type="monotone"
                dataKey="Advertised Cost"
                stroke="#6B7280"
                strokeWidth={2}
                dot={{ r: 4 }}
              />
              <Line
                type="monotone"
                dataKey="True Cost"
                stroke="#EF4444"
                strokeWidth={2}
                dot={{ r: 4 }}
              />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>

      {/* Year-by-Year Breakdown Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="p-4 border-b border-gray-100">
          <h5 className="text-sm font-semibold text-gray-900">Year-by-Year Breakdown</h5>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Year</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">Advertised/Week</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">True Cost/Week</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">Annual Advertised</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">Annual True</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">Hidden Fees</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">Cumulative True</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {years.filter(Boolean).map((year, i) => (
                <tr key={safeNumber(year?.year, i)} className={i === 0 ? 'bg-blue-50' : 'hover:bg-gray-50'}>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">Year {safeNumber(year?.year)}</span>
                      {i === 0 && (
                        <span className="text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded">
                          +Move-in fees
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-gray-500">
                      Inflation: {((safeNumber(year?.inflation_factor, 1) - 1) * 100).toFixed(1)}%
                    </div>
                  </td>
                  <td className="text-right py-3 px-4 text-gray-600">
                    {formatCurrency(safeNumber(year?.advertised_weekly))}
                  </td>
                  <td className="text-right py-3 px-4 font-medium text-gray-900">
                    {formatCurrency(safeNumber(year?.true_weekly))}
                  </td>
                  <td className="text-right py-3 px-4 text-gray-600">
                    {formatCurrency(safeNumber(year?.advertised_annual))}
                  </td>
                  <td className="text-right py-3 px-4 font-medium text-gray-900">
                    {formatCurrency(safeNumber(year?.true_annual))}
                  </td>
                  <td className="text-right py-3 px-4 text-amber-600 font-medium">
                    +{formatCurrency(safeNumber(year?.hidden_fees_annual))}
                  </td>
                  <td className="text-right py-3 px-4 font-bold text-red-600">
                    {formatCurrency(safeNumber(year?.cumulative_true))}
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot className="bg-gray-100">
              <tr>
                <td className="py-3 px-4 font-bold text-gray-900">5-Year Total</td>
                <td className="text-right py-3 px-4">—</td>
                <td className="text-right py-3 px-4">—</td>
                <td className="text-right py-3 px-4 font-bold text-gray-700">
                  {formatCurrency(safeNumber(summary.total_5_year_advertised))}
                </td>
                <td className="text-right py-3 px-4 font-bold text-gray-900">
                  {formatCurrency(safeNumber(summary.total_5_year_true))}
                </td>
                <td className="text-right py-3 px-4 font-bold text-amber-600">
                  +{formatCurrency(safeNumber(summary.total_5_year_hidden))}
                </td>
                <td className="text-right py-3 px-4 font-bold text-red-600">
                  {formatCurrency(safeNumber(summary.total_5_year_true))}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      {/* Inflation Note */}
      <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-600">
        <span className="font-medium">Note:</span> Projections assume {safeNumber(overallSummary.inflation_rate_used, 4)}% annual 
        inflation based on UK care home cost trends. Actual costs may vary.
      </div>
    </div>
  );
}

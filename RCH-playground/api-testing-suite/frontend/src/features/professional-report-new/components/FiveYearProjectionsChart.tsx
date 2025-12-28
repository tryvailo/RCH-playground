import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { FiveYearProjection } from '../types';

interface FiveYearProjectionsChartProps {
  projections: FiveYearProjection[];
}

export default function FiveYearProjectionsChart({ projections }: FiveYearProjectionsChartProps) {
  if (!projections || projections.length === 0) {
    return null;
  }

  // Use first home's projections for the chart (or combine all homes)
  const firstHome = projections[0];
  const scenarioProjections = firstHome.scenario_projections;

  // Prepare data for cumulative cost chart (year by year)
  const cumulativeData = firstHome.year_by_year.map((yearData) => {
    const dataPoint: any = {
      year: `Year ${yearData.year_number}`,
      yearNumber: yearData.year_number,
      yearValue: yearData.year
    };

    // Add cumulative costs for each scenario
    Object.entries(yearData.scenarios).forEach(([key, scenario]) => {
      dataPoint[scenario.scenario_name] = scenario.cumulative_cost;
    });

    return dataPoint;
  });

  // Prepare data for annual cost comparison chart
  const annualData = firstHome.year_by_year.map((yearData) => {
    const dataPoint: any = {
      year: `Year ${yearData.year_number}`,
      yearNumber: yearData.year_number
    };

    // Add annual costs for each scenario
    Object.entries(yearData.scenarios).forEach(([key, scenario]) => {
      dataPoint[scenario.scenario_name] = scenario.annual_cost;
    });

    return dataPoint;
  });

  // Colors for scenarios

  const colors = {
    'CHC Funding': '#10B981', // Green
    'LA Funding': '#3B82F6', // Blue
    'Self-Funding': '#EF4444', // Red
    'DPA Deferral': '#F59E0B', // Orange
    'Recommended': '#8B5CF6' // Purple
  };

  const getColor = (scenarioName: string) => {
    return colors[scenarioName as keyof typeof colors] || '#6B7280';
  };

  // Format currency for tooltip
  const formatCurrency = (value: number) => {
    return `£${value.toLocaleString()}`;
  };

  return (
    <div className="space-y-6">
      {/* Cumulative Costs Line Chart */}
      <div className="bg-white rounded-lg p-4 border border-gray-200">
        <h5 className="text-sm font-semibold text-gray-900 mb-4">5-Year Cumulative Cost Comparison</h5>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={cumulativeData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis 
              dataKey="year" 
              stroke="#6B7280"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#6B7280"
              style={{ fontSize: '12px' }}
              tickFormatter={(value) => `£${(value / 1000).toFixed(0)}k`}
            />
            <Tooltip 
              formatter={(value: number) => formatCurrency(value)}
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #E5E7EB',
                borderRadius: '6px',
                fontSize: '12px'
              }}
            />
            <Legend 
              wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }}
            />
            {Object.entries(scenarioProjections).map(([key, scenario]) => {
              if (!scenario) return null;
              const scenarioName = scenario.scenario_name;
              return (
                <Line
                  key={key}
                  type="monotone"
                  dataKey={scenarioName}
                  stroke={getColor(scenarioName)}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
              );
            })}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Annual Costs Bar Chart */}
      <div className="bg-white rounded-lg p-4 border border-gray-200">
        <h5 className="text-sm font-semibold text-gray-900 mb-4">Annual Cost Comparison by Year</h5>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={annualData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis 
              dataKey="year" 
              stroke="#6B7280"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#6B7280"
              style={{ fontSize: '12px' }}
              tickFormatter={(value) => `£${(value / 1000).toFixed(0)}k`}
            />
            <Tooltip 
              formatter={(value: number) => formatCurrency(value)}
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #E5E7EB',
                borderRadius: '6px',
                fontSize: '12px'
              }}
            />
            <Legend 
              wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }}
            />
            {Object.entries(scenarioProjections).map(([key, scenario]) => {
              if (!scenario) return null;
              const scenarioName = scenario.scenario_name;
              return (
                <Bar
                  key={key}
                  dataKey={scenarioName}
                  fill={getColor(scenarioName)}
                  radius={[4, 4, 0, 0]}
                />
              );
            })}
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Scenario Summary Table */}
      <div className="bg-white rounded-lg p-4 border border-gray-200">
        <h5 className="text-sm font-semibold text-gray-900 mb-3">5-Year Total Cost Summary</h5>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 px-2 text-gray-700 font-semibold">Scenario</th>
                <th className="text-right py-2 px-2 text-gray-700 font-semibold">5-Year Total</th>
                <th className="text-right py-2 px-2 text-gray-700 font-semibold">Avg Annual</th>
                <th className="text-right py-2 px-2 text-gray-700 font-semibold">Savings vs Self</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(scenarioProjections).map(([key, scenario]) => {
                if (!scenario) return null;
                const savings = scenario.total_savings_vs_self;
                const savingsPercent = firstHome.summary.scenario_summaries[key]?.savings_percent;
                
                return (
                  <tr key={key} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-2 px-2">
                      <div className="flex items-center">
                        <div 
                          className="w-3 h-3 rounded-full mr-2" 
                          style={{ backgroundColor: getColor(scenario.scenario_name) }}
                        />
                        <span className="font-medium text-gray-900">{scenario.scenario_name}</span>
                        {key === 'recommended' && (
                          <span className="ml-2 text-xs px-1.5 py-0.5 bg-purple-100 text-purple-700 rounded">
                            Recommended
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="text-right py-2 px-2 font-semibold text-gray-900">
                      £{scenario.total_5_year_cost.toLocaleString()}
                    </td>
                    <td className="text-right py-2 px-2 text-gray-600">
                      £{scenario.average_annual_cost.toLocaleString()}
                    </td>
                    <td className="text-right py-2 px-2">
                      {savings && savings > 0 ? (
                        <span className="text-green-600 font-semibold">
                          £{savings.toLocaleString()}
                          {savingsPercent && (
                            <span className="text-gray-500 ml-1">({savingsPercent}%)</span>
                          )}
                        </span>
                      ) : (
                        <span className="text-gray-400">—</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}


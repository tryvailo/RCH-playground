import React from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import type { FinancialStability } from '../types';

interface FinancialStabilityChartProps {
  financialData: FinancialStability;
  homeName: string;
}

export default function FinancialStabilityChart({ financialData, homeName }: FinancialStabilityChartProps) {
  if (!financialData?.three_year_summary) {
    return (
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 text-center text-xs text-gray-500">
        Financial data not available
      </div>
    );
  }

  // Prepare data for 3-year financial summary
  const summary = financialData.three_year_summary;
  
  // If we have year-by-year data, use it; otherwise create synthetic data
  const chartData = [
    {
      year: 'Year 1',
      revenue: summary.revenue_year_1 || summary.average_revenue || 0,
      profit: summary.profit_year_1 || summary.average_profit || 0,
      margin: summary.net_margin_3yr_avg ? summary.net_margin_3yr_avg * 100 : 0
    },
    {
      year: 'Year 2',
      revenue: summary.revenue_year_2 || summary.average_revenue || 0,
      profit: summary.profit_year_2 || summary.average_profit || 0,
      margin: summary.net_margin_3yr_avg ? summary.net_margin_3yr_avg * 100 : 0
    },
    {
      year: 'Year 3',
      revenue: summary.revenue_year_3 || summary.average_revenue || 0,
      profit: summary.profit_year_3 || summary.average_profit || 0,
      margin: summary.net_margin_3yr_avg ? summary.net_margin_3yr_avg * 100 : 0
    }
  ];

  const formatCurrency = (value: number) => {
    if (value >= 1000000) return `£${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `£${(value / 1000).toFixed(0)}k`;
    return `£${value}`;
  };

  return (
    <div className="space-y-4">
      {/* Revenue & Profit Trend */}
      <div className="bg-white rounded-lg p-4 border border-gray-200">
        <h5 className="text-xs font-semibold text-gray-900 mb-3">
          Revenue & Profit Trend - {homeName}
        </h5>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis 
              dataKey="year" 
              stroke="#6B7280"
              style={{ fontSize: '11px' }}
            />
            <YAxis 
              stroke="#6B7280"
              style={{ fontSize: '11px' }}
              tickFormatter={formatCurrency}
            />
            <Tooltip 
              formatter={(value: number) => formatCurrency(value)}
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #E5E7EB',
                borderRadius: '6px',
                fontSize: '11px'
              }}
            />
            <Legend 
              wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }}
            />
            <Line 
              type="monotone" 
              dataKey="revenue" 
              stroke="#3B82F6" 
              strokeWidth={2}
              name="Revenue"
              dot={{ r: 4 }}
            />
            <Line 
              type="monotone" 
              dataKey="profit" 
              stroke="#10B981" 
              strokeWidth={2}
              name="Profit"
              dot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Profit Margin Bar Chart */}
      <div className="bg-white rounded-lg p-4 border border-gray-200">
        <h5 className="text-xs font-semibold text-gray-900 mb-3">Net Margin %</h5>
        <ResponsiveContainer width="100%" height={150}>
          <BarChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis 
              dataKey="year" 
              stroke="#6B7280"
              style={{ fontSize: '11px' }}
            />
            <YAxis 
              stroke="#6B7280"
              style={{ fontSize: '11px' }}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip 
              formatter={(value: number) => `${value.toFixed(1)}%`}
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #E5E7EB',
                borderRadius: '6px',
                fontSize: '11px'
              }}
            />
            <Bar dataKey="margin" fill="#8B5CF6" radius={[4, 4, 0, 0]}>
              {chartData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={entry.margin > 10 ? '#10B981' : entry.margin > 5 ? '#F59E0B' : '#EF4444'} 
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Bankruptcy Risk Gauge */}
      {financialData.bankruptcy_risk_score !== null && financialData.bankruptcy_risk_score !== undefined && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-xs font-semibold text-gray-900 mb-3">Bankruptcy Risk Score</h5>
          <div className="relative">
            <div className="w-full bg-gray-200 rounded-full h-6">
              <div
                className={`h-6 rounded-full transition-all duration-500 ${
                  financialData.bankruptcy_risk_score < 30 ? 'bg-green-500' :
                  financialData.bankruptcy_risk_score < 60 ? 'bg-yellow-500' :
                  'bg-red-500'
                }`}
                style={{ width: `${Math.min(financialData.bankruptcy_risk_score, 100)}%` }}
              ></div>
            </div>
            <div className="flex justify-between mt-2 text-xs">
              <span className="text-gray-600">Low Risk</span>
              <span className={`font-semibold ${
                financialData.bankruptcy_risk_score < 30 ? 'text-green-600' :
                financialData.bankruptcy_risk_score < 60 ? 'text-yellow-600' :
                'text-red-600'
              }`}>
                {financialData.bankruptcy_risk_score}/100
              </span>
              <span className="text-gray-600">High Risk</span>
            </div>
            <div className="text-xs text-center mt-1 text-gray-500">
              {financialData.bankruptcy_risk_level || 'N/A'}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


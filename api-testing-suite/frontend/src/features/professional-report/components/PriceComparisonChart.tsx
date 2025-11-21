import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import type { ProfessionalCareHome } from '../types';

interface PriceComparisonChartProps {
  homes: ProfessionalCareHome[];
}

export default function PriceComparisonChart({ homes }: PriceComparisonChartProps) {
  if (!homes || homes.length === 0) {
    return null;
  }

  // Prepare data for bar chart
  const chartData = homes.slice(0, 5).map((home, idx) => ({
    name: home.name.length > 20 ? home.name.substring(0, 20) + '...' : home.name,
    fullName: home.name,
    price: home.weeklyPrice,
    matchScore: home.matchScore,
    rank: idx + 1
  }));

  // Color based on match score
  const getBarColor = (matchScore: number) => {
    if (matchScore >= 80) return '#10B981'; // Green
    if (matchScore >= 60) return '#3B82F6'; // Blue
    if (matchScore >= 40) return '#F59E0B'; // Orange
    return '#EF4444'; // Red
  };

  return (
    <div className="bg-white rounded-lg p-4 border border-gray-200">
      <h5 className="text-xs font-semibold text-gray-900 mb-3">Weekly Price Comparison</h5>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 60 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis 
            dataKey="name" 
            angle={-45}
            textAnchor="end"
            height={80}
            stroke="#6B7280"
            style={{ fontSize: '10px' }}
          />
          <YAxis 
            stroke="#6B7280"
            style={{ fontSize: '11px' }}
            tickFormatter={(value) => `£${value}`}
          />
          <Tooltip 
            formatter={(value: number, payload: any) => {
              const data = payload?.payload;
              return [
                `£${value.toLocaleString()}/week`,
                `Match: ${data?.matchScore.toFixed(1)}%`
              ];
            }}
            labelFormatter={(label) => `Home: ${label}`}
            contentStyle={{ 
              backgroundColor: 'white', 
              border: '1px solid #E5E7EB',
              borderRadius: '6px',
              fontSize: '12px'
            }}
          />
          <Bar dataKey="price" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getBarColor(entry.matchScore)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="mt-3 flex items-center justify-center gap-4 text-xs">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-green-500"></div>
          <span className="text-gray-600">High Match (80%+)</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-blue-500"></div>
          <span className="text-gray-600">Good Match (60-79%)</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-orange-500"></div>
          <span className="text-gray-600">Fair Match (40-59%)</span>
        </div>
      </div>
    </div>
  );
}


import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { FSADetailed } from '../types';

interface FSARatingTrendChartProps {
  fsaData: FSADetailed;
  homeName: string;
}

const getRatingColor = (rating: number | null | undefined): string => {
  if (rating === null || rating === undefined) return '#6B7280';
  if (rating >= 4) return '#10B981'; // Green
  if (rating >= 3) return '#F59E0B'; // Yellow
  return '#EF4444'; // Red
};

const getRatingLabel = (rating: number | null | undefined): string => {
  if (rating === null || rating === undefined) return 'N/A';
  if (rating === 5) return '5 - Very Good';
  if (rating === 4) return '4 - Good';
  if (rating === 3) return '3 - Generally Satisfactory';
  if (rating === 2) return '2 - Improvement Needed';
  if (rating === 1) return '1 - Major Improvement Needed';
  if (rating === 0) return '0 - Awaiting Inspection';
  return `${rating}`;
};

export default function FSARatingTrendChart({ fsaData, homeName }: FSARatingTrendChartProps) {
  if (!fsaData?.historical_ratings || fsaData.historical_ratings.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 text-center text-xs text-gray-500">
        Historical FSA rating data not available
      </div>
    );
  }

  // Prepare data for chart - last 5 years
  const allRatings = [...(fsaData.historical_ratings || [])];
  
  // Add current rating if available and not already in historical
  if (fsaData.rating && !allRatings.some(r => {
    const ratingDate = r.date || r.rating_date;
    if (!ratingDate) return false;
    const date = new Date(ratingDate);
    const currentDate = new Date();
    return Math.abs(date.getTime() - currentDate.getTime()) < 90 * 24 * 60 * 60 * 1000; // Within 90 days
  })) {
    allRatings.unshift({
      date: new Date().toISOString().split('T')[0],
      rating: typeof fsaData.rating === 'number' ? fsaData.rating : parseInt(String(fsaData.rating)) || 0,
      rating_date: fsaData.rating_date
    });
  }

  // Sort by date (newest first) and take last 5 years
  const sortedRatings = allRatings
    .filter(r => r.date || r.rating_date)
    .sort((a, b) => {
      const dateA = new Date(a.date || a.rating_date || '').getTime();
      const dateB = new Date(b.date || b.rating_date || '').getTime();
      return dateB - dateA; // Newest first
    });

  // Get ratings from last 5 years
  const fiveYearsAgo = new Date();
  fiveYearsAgo.setFullYear(fiveYearsAgo.getFullYear() - 5);
  
  const recentRatings = sortedRatings.filter(r => {
    const ratingDate = new Date(r.date || r.rating_date || '');
    return ratingDate >= fiveYearsAgo;
  }).slice(0, 10); // Limit to 10 most recent

  // Prepare chart data
  const chartData = recentRatings
    .map((rating) => {
      const date = new Date(rating.date || rating.rating_date || '');
      const year = date.getFullYear();
      const month = date.getMonth() + 1;
      const ratingValue = typeof rating.rating === 'number' ? rating.rating : parseInt(String(rating.rating)) || 0;
      
      return {
        year: year.toString(),
        month: month,
        date: date.toISOString().split('T')[0],
        fullDate: date.toLocaleDateString('en-GB', { year: 'numeric', month: 'short', day: 'numeric' }),
        rating: ratingValue,
        ratingLabel: getRatingLabel(ratingValue),
        breakdown_scores: rating.breakdown_scores || {}
      };
    })
    .reverse(); // Oldest to newest for chart

  if (chartData.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 text-center text-xs text-gray-500">
        No historical FSA rating data available for the last 5 years
      </div>
    );
  }

  const currentRating = chartData[chartData.length - 1]?.rating || fsaData.rating;
  const ratingColor = getRatingColor(currentRating);

  return (
    <div className="bg-white rounded-lg p-4 border border-gray-200">
      <h5 className="text-xs font-semibold text-gray-900 mb-3">
        FSA Rating Trend - {homeName}
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
            domain={[0, 5]}
            tickFormatter={(value) => value.toString()}
          />
          <Tooltip 
            formatter={(value: number, payload: any) => {
              const data = payload?.payload;
              return data?.ratingLabel || getRatingLabel(value);
            }}
            labelFormatter={(label) => {
              const data = chartData.find(d => d.year === label);
              return data ? `Date: ${data.fullDate}` : `Year: ${label}`;
            }}
            contentStyle={{ 
              backgroundColor: 'white', 
              border: '1px solid #E5E7EB',
              borderRadius: '6px',
              fontSize: '11px'
            }}
          />
          <Line
            type="monotone"
            dataKey="rating"
            stroke={ratingColor}
            strokeWidth={2}
            dot={{ r: 5, fill: ratingColor }}
            activeDot={{ r: 7 }}
          />
        </LineChart>
      </ResponsiveContainer>
      
      {fsaData.trend_analysis && fsaData.trend_analysis.trend && (
        <div className="mt-2 text-center">
          <span className={`text-xs font-semibold ${
            fsaData.trend_analysis.trend.toLowerCase().includes('improving') ? 'text-green-600' :
            fsaData.trend_analysis.trend.toLowerCase().includes('declining') ? 'text-red-600' :
            'text-gray-600'
          }`}>
            Trend: {fsaData.trend_analysis.trend}
          </span>
        </div>
      )}

      {/* Inspection Timeline */}
      {recentRatings.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <h6 className="text-xs font-semibold text-gray-700 mb-2">Inspection History (Last 5 Years)</h6>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {recentRatings.slice(0, 5).map((rating, idx) => {
              const date = new Date(rating.date || rating.rating_date || '');
              const ratingValue = typeof rating.rating === 'number' ? rating.rating : parseInt(String(rating.rating)) || 0;
              const ratingColorValue = getRatingColor(ratingValue);
              
              return (
                <div key={idx} className="flex items-center justify-between text-xs bg-gray-50 rounded p-2">
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-2 h-2 rounded-full" 
                      style={{ backgroundColor: ratingColorValue }}
                    />
                    <span className="text-gray-600">
                      {date.toLocaleDateString('en-GB', { year: 'numeric', month: 'short', day: 'numeric' })}
                    </span>
                  </div>
                  <span 
                    className="font-semibold px-2 py-0.5 rounded"
                    style={{ 
                      color: ratingColorValue,
                      backgroundColor: `${ratingColorValue}20`
                    }}
                  >
                    {getRatingLabel(ratingValue)}
                  </span>
                </div>
              );
            })}
          </div>
          {recentRatings.length > 5 && (
            <p className="text-xs text-gray-500 mt-2 text-center">
              +{recentRatings.length - 5} more inspections
            </p>
          )}
        </div>
      )}
    </div>
  );
}


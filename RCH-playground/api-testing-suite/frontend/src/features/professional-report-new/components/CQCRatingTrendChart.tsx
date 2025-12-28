import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Clock, Building2 } from 'lucide-react';
import type { CQCDeepDive } from '../types';

interface CQCRatingTrendChartProps {
  cqcData: CQCDeepDive;
  homeName: string;
}

const ratingToNumber = (rating: string): number => {
  const ratingMap: { [key: string]: number } = {
    'Outstanding': 4,
    'Good': 3,
    'Requires improvement': 2,
    'Inadequate': 1
  };
  return ratingMap[rating] || 0;
};

const numberToRating = (num: number): string => {
  const ratingMap: { [key: number]: string } = {
    4: 'Outstanding',
    3: 'Good',
    2: 'Requires improvement',
    1: 'Inadequate'
  };
  return ratingMap[num] || 'Unknown';
};

export default function CQCRatingTrendChart({ cqcData, homeName }: CQCRatingTrendChartProps) {
  if (!cqcData?.historical_ratings || cqcData.historical_ratings.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 text-center text-xs text-gray-500">
        Historical rating data not available
      </div>
    );
  }

  // Prepare data for chart - last 5 years with proper date handling
  const allRatings = [...(cqcData.historical_ratings || [])];
  
  // Add current rating if available and not already in historical
  if (cqcData.overall_rating && !allRatings.some(r => {
    const ratingDate = r.date || r.inspection_date;
    if (!ratingDate) return false;
    const date = new Date(ratingDate);
    const currentDate = new Date();
    return Math.abs(date.getTime() - currentDate.getTime()) < 90 * 24 * 60 * 60 * 1000; // Within 90 days
  })) {
    allRatings.unshift({
      date: new Date().toISOString().split('T')[0],
      overall_rating: cqcData.overall_rating,
      rating: cqcData.overall_rating
    });
  }

  // Sort by date (newest first) and take last 5 years
  const sortedRatings = allRatings
    .filter(r => r.date || r.inspection_date)
    .sort((a, b) => {
      const dateA = new Date(a.date || a.inspection_date || '').getTime();
      const dateB = new Date(b.date || b.inspection_date || '').getTime();
      return dateB - dateA; // Newest first
    });

  // Get ratings from last 5 years
  const fiveYearsAgo = new Date();
  fiveYearsAgo.setFullYear(fiveYearsAgo.getFullYear() - 5);
  
  const recentRatings = sortedRatings.filter(r => {
    const ratingDate = new Date(r.date || r.inspection_date || '');
    return ratingDate >= fiveYearsAgo;
  }).slice(0, 10); // Limit to 10 most recent

  // Prepare chart data
  const chartData = recentRatings
    .map((rating) => {
      const date = new Date(rating.date || rating.inspection_date || '');
      const year = date.getFullYear();
      const month = date.getMonth() + 1;
      return {
        year: year.toString(),
        month: month,
        date: date.toISOString().split('T')[0],
        fullDate: date.toLocaleDateString('en-GB', { year: 'numeric', month: 'short', day: 'numeric' }),
        rating: ratingToNumber(rating.rating || rating.overall_rating || ''),
        ratingLabel: rating.rating || rating.overall_rating || 'Unknown',
        keyQuestionRatings: rating.key_question_ratings || {}
      };
    })
    .reverse(); // Oldest to newest for chart

  const getRatingColor = (rating: string): string => {
    switch (rating) {
      case 'Outstanding': return '#10B981';
      case 'Good': return '#3B82F6';
      case 'Requires improvement': return '#F59E0B';
      case 'Inadequate': return '#EF4444';
      default: return '#6B7280';
    }
  };

  const daysSinceInspection = cqcData.days_since_inspection;
  const providerLocationsCount = cqcData.provider_locations_count;

  const getInspectionUrgencyColor = (days?: number | null) => {
    if (!days) return 'text-gray-500';
    if (days <= 365) return 'text-green-600';
    if (days <= 730) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getInspectionUrgencyLabel = (days?: number | null) => {
    if (!days) return 'Unknown';
    if (days <= 365) return 'Recent';
    if (days <= 730) return 'Due Soon';
    return 'Overdue';
  };

  return (
    <div className="bg-white rounded-lg p-4 border border-gray-200">
      <h5 className="text-xs font-semibold text-gray-900 mb-3">
        CQC Rating Trend - {homeName}
      </h5>

      {/* Inspection Status & Provider Info */}
      {(daysSinceInspection !== undefined || providerLocationsCount !== undefined) && (
        <div className="grid grid-cols-2 gap-3 mb-4">
          {daysSinceInspection !== undefined && daysSinceInspection !== null && (
            <div className={`flex items-center gap-2 p-2 rounded-lg ${
              daysSinceInspection <= 365 ? 'bg-green-50 border border-green-100' :
              daysSinceInspection <= 730 ? 'bg-yellow-50 border border-yellow-100' :
              'bg-red-50 border border-red-100'
            }`}>
              <Clock className={`w-4 h-4 ${getInspectionUrgencyColor(daysSinceInspection)}`} />
              <div>
                <div className="text-xs text-gray-600">Last Inspection</div>
                <div className={`text-sm font-semibold ${getInspectionUrgencyColor(daysSinceInspection)}`}>
                  {daysSinceInspection} days ago
                  <span className="ml-1 text-xs font-normal">
                    ({getInspectionUrgencyLabel(daysSinceInspection)})
                  </span>
                </div>
              </div>
            </div>
          )}
          {providerLocationsCount !== undefined && providerLocationsCount !== null && (
            <div className="flex items-center gap-2 p-2 rounded-lg bg-blue-50 border border-blue-100">
              <Building2 className="w-4 h-4 text-blue-600" />
              <div>
                <div className="text-xs text-gray-600">Provider Network</div>
                <div className="text-sm font-semibold text-blue-700">
                  {providerLocationsCount} location{providerLocationsCount !== 1 ? 's' : ''}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

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
            domain={[0, 4]}
            tickFormatter={(value) => numberToRating(value)}
          />
          <Tooltip 
            formatter={(value: number, payload: any) => {
              const data = payload?.payload;
              return data?.ratingLabel || numberToRating(value);
            }}
            labelFormatter={(label) => `Year: ${label}`}
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
            stroke={getRatingColor(chartData[chartData.length - 1]?.ratingLabel || 'Good')}
            strokeWidth={2}
            dot={{ r: 5, fill: getRatingColor(chartData[chartData.length - 1]?.ratingLabel || 'Good') }}
            activeDot={{ r: 7 }}
          />
        </LineChart>
      </ResponsiveContainer>
      {cqcData.trend && (
        <div className="mt-2 text-center">
          <span className={`text-xs font-semibold ${
            cqcData.trend.toLowerCase().includes('improving') ? 'text-green-600' :
            cqcData.trend.toLowerCase().includes('declining') ? 'text-red-600' :
            'text-gray-600'
          }`}>
            Trend: {cqcData.trend}
          </span>
        </div>
      )}

      {/* Inspection Timeline */}
      {recentRatings.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <h6 className="text-xs font-semibold text-gray-700 mb-2">Inspection History (Last 5 Years)</h6>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {recentRatings.slice(0, 5).map((rating, idx) => {
              const date = new Date(rating.date || rating.inspection_date || '');
              const ratingValue = rating.rating || rating.overall_rating || 'Unknown';
              const ratingColor = getRatingColor(ratingValue);
              
              return (
                <div key={idx} className="flex items-center justify-between text-xs bg-gray-50 rounded p-2">
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-2 h-2 rounded-full" 
                      style={{ backgroundColor: ratingColor }}
                    />
                    <span className="text-gray-600">
                      {date.toLocaleDateString('en-GB', { year: 'numeric', month: 'short', day: 'numeric' })}
                    </span>
                  </div>
                  <span 
                    className="font-semibold px-2 py-0.5 rounded"
                    style={{ 
                      color: ratingColor,
                      backgroundColor: `${ratingColor}20`
                    }}
                  >
                    {ratingValue}
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

      {/* Rating Changes */}
      {cqcData.rating_changes && cqcData.rating_changes.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <h6 className="text-xs font-semibold text-gray-700 mb-2">Recent Rating Changes</h6>
          <div className="space-y-1">
            {cqcData.rating_changes.slice(0, 3).map((change: any, idx: number) => (
              <div key={idx} className="text-xs text-gray-600 flex items-center gap-2">
                <span className="text-gray-400">
                  {change.date ? new Date(change.date).toLocaleDateString('en-GB', { year: 'numeric', month: 'short' }) : 'N/A'}
                </span>
                <span className="text-gray-500">→</span>
                <span className={`font-medium ${
                  change.to_rating === 'Outstanding' || change.to_rating === 'Good' ? 'text-green-600' :
                  change.to_rating === 'Requires improvement' ? 'text-yellow-600' :
                  'text-red-600'
                }`}>
                  {change.from_rating || 'Unknown'} → {change.to_rating || 'Unknown'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}


import React from 'react';
import type { FSADetailed } from '../types';

interface FSAInspectionHistoryProps {
  fsaData: FSADetailed;
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

export default function FSAInspectionHistory({ fsaData }: FSAInspectionHistoryProps) {
  if (!fsaData?.historical_ratings || fsaData.historical_ratings.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 text-center text-xs text-gray-500">
        Historical FSA rating data not available
      </div>
    );
  }

  // Prepare data - last 5 years
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
  }).slice(0, 5); // Limit to 5 most recent

  if (recentRatings.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 text-center text-xs text-gray-500">
        No historical FSA rating data available for the last 5 years
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg p-4 border border-gray-200">
      <h6 className="text-xs font-semibold text-gray-700 mb-3">Inspection History (Last 5 Years)</h6>
      <div className="space-y-2 max-h-48 overflow-y-auto">
        {recentRatings.map((rating, idx) => {
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
      {allRatings.length > 5 && (
        <p className="text-xs text-gray-500 mt-2 text-center">
          +{allRatings.length - 5} more inspections
        </p>
      )}
    </div>
  );
}


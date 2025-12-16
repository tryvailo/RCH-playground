import React from 'react';
import { TrendingUp, TrendingDown, Minus, Users, Clock, MapPin, BarChart3 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import type { GooglePlacesData } from '../types';

interface FootfallTrendsSectionProps {
  googlePlacesData: GooglePlacesData;
  homeName: string;
}

export default function FootfallTrendsSection({ googlePlacesData, homeName }: FootfallTrendsSectionProps) {
  const insights = googlePlacesData?.insights;
  const footfallTrend = googlePlacesData?.footfall_trend || insights?.footfall_trends?.trend_direction;
  const dwellTime = googlePlacesData?.average_dwell_time_minutes || insights?.dwell_time?.average_dwell_time_minutes;
  const repeatVisitorRate = googlePlacesData?.repeat_visitor_rate;
  const popularTimes = googlePlacesData?.popular_times || insights?.popular_times;
  const visitorGeography = insights?.visitor_geography;

  const hasAnyData = footfallTrend || dwellTime || repeatVisitorRate || popularTimes || visitorGeography;

  if (!hasAnyData) {
    return (
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-gray-400" />
          <p className="text-sm text-gray-500">Footfall and visitor insights not available</p>
        </div>
      </div>
    );
  }

  const getTrendIcon = (trend?: string) => {
    if (!trend) return <Minus className="w-5 h-5 text-gray-400" />;
    const lower = trend.toLowerCase();
    if (lower === 'growing' || lower.includes('increas')) {
      return <TrendingUp className="w-5 h-5 text-green-600" />;
    }
    if (lower === 'declining' || lower.includes('decreas')) {
      return <TrendingDown className="w-5 h-5 text-red-600" />;
    }
    return <Minus className="w-5 h-5 text-yellow-600" />;
  };

  const getTrendColor = (trend?: string) => {
    if (!trend) return { bg: 'bg-gray-50', border: 'border-gray-200', text: 'text-gray-600' };
    const lower = trend.toLowerCase();
    if (lower === 'growing' || lower.includes('increas')) {
      return { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-700' };
    }
    if (lower === 'declining' || lower.includes('decreas')) {
      return { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700' };
    }
    return { bg: 'bg-yellow-50', border: 'border-yellow-200', text: 'text-yellow-700' };
  };

  const trendColors = getTrendColor(footfallTrend);

  const preparePopularTimesData = () => {
    if (!popularTimes) return [];
    
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const chartData: { day: string; avgBusyness: number }[] = [];
    
    for (const day of days) {
      const dayData = popularTimes[day.toLowerCase()] || popularTimes[day];
      if (dayData && typeof dayData === 'object') {
        const hours = Object.values(dayData as Record<string, number>);
        const avg = hours.length > 0 ? hours.reduce((a, b) => a + b, 0) / hours.length : 0;
        chartData.push({ day: day.slice(0, 3), avgBusyness: Math.round(avg) });
      }
    }
    
    return chartData;
  };

  const popularTimesChartData = preparePopularTimesData();
  const peakDay = popularTimes?.peak_day;

  const getDwellTimeInterpretation = (minutes?: number) => {
    if (!minutes) return 'Unknown';
    if (minutes >= 60) return 'Long visits - strong family engagement';
    if (minutes >= 30) return 'Moderate visits - good family involvement';
    return 'Short visits - may indicate limited engagement';
  };

  const getRepeatVisitorInterpretation = (rate?: number) => {
    if (!rate) return 'Unknown';
    const percent = rate * 100;
    if (percent >= 50) return 'High repeat rate - families visit regularly';
    if (percent >= 30) return 'Moderate repeat rate - reasonable family engagement';
    return 'Low repeat rate - may need investigation';
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <BarChart3 className="w-5 h-5 text-indigo-600" />
        <h4 className="text-lg font-semibold text-gray-900">Footfall & Visitor Insights</h4>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {footfallTrend && (
          <div className={`${trendColors.bg} ${trendColors.border} border rounded-lg p-3`}>
            <div className="flex items-center gap-2 mb-1">
              {getTrendIcon(footfallTrend)}
              <span className="text-xs font-semibold text-gray-600">Footfall Trend</span>
            </div>
            <div className={`text-lg font-bold capitalize ${trendColors.text}`}>
              {footfallTrend}
            </div>
            {insights?.footfall_trends?.monthly_change_percent && (
              <div className="text-xs text-gray-500 mt-1">
                {insights.footfall_trends.monthly_change_percent > 0 ? '+' : ''}
                {insights.footfall_trends.monthly_change_percent.toFixed(1)}% monthly
              </div>
            )}
          </div>
        )}

        {dwellTime && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-1">
              <Clock className="w-4 h-4 text-blue-600" />
              <span className="text-xs font-semibold text-gray-600">Avg Visit Duration</span>
            </div>
            <div className="text-lg font-bold text-blue-700">
              {dwellTime} min
            </div>
            <div className="text-xs text-blue-600 mt-1">
              {getDwellTimeInterpretation(dwellTime).split(' - ')[0]}
            </div>
          </div>
        )}

        {repeatVisitorRate !== undefined && repeatVisitorRate !== null && (
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-1">
              <Users className="w-4 h-4 text-purple-600" />
              <span className="text-xs font-semibold text-gray-600">Repeat Visitors</span>
            </div>
            <div className="text-lg font-bold text-purple-700">
              {(repeatVisitorRate * 100).toFixed(0)}%
            </div>
            <div className="text-xs text-purple-600 mt-1">
              {getRepeatVisitorInterpretation(repeatVisitorRate).split(' - ')[0]}
            </div>
          </div>
        )}

        {visitorGeography?.local_percent !== undefined && (
          <div className="bg-teal-50 border border-teal-200 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-1">
              <MapPin className="w-4 h-4 text-teal-600" />
              <span className="text-xs font-semibold text-gray-600">Local Visitors</span>
            </div>
            <div className="text-lg font-bold text-teal-700">
              {visitorGeography.local_percent}%
            </div>
            <div className="text-xs text-teal-600 mt-1">
              From local area
            </div>
          </div>
        )}
      </div>

      {popularTimesChartData.length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3">
            Weekly Visitor Pattern
            {peakDay && (
              <span className="ml-2 text-xs font-normal text-gray-500">
                (Peak: {peakDay})
              </span>
            )}
          </h5>
          <ResponsiveContainer width="100%" height={150}>
            <BarChart data={popularTimesChartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis 
                dataKey="day" 
                stroke="#6B7280" 
                style={{ fontSize: '10px' }}
              />
              <YAxis 
                stroke="#6B7280" 
                style={{ fontSize: '10px' }}
                domain={[0, 100]}
              />
              <Tooltip
                formatter={(value: number) => [`${value}%`, 'Busyness']}
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #E5E7EB',
                  borderRadius: '6px',
                  fontSize: '11px'
                }}
              />
              <Bar dataKey="avgBusyness" radius={[4, 4, 0, 0]}>
                {popularTimesChartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.avgBusyness >= 70 ? '#10B981' : entry.avgBusyness >= 40 ? '#6366F1' : '#9CA3AF'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {insights?.summary && (
        <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
          <h5 className="text-sm font-semibold text-indigo-900 mb-2">Family Engagement Score</h5>
          <div className="flex items-center gap-4">
            {insights.summary.family_engagement_score !== undefined && (
              <div className="text-3xl font-bold text-indigo-700">
                {insights.summary.family_engagement_score}
                <span className="text-sm font-normal text-indigo-500">/100</span>
              </div>
            )}
            {insights.summary.quality_indicator && (
              <span className={`px-3 py-1 text-sm font-semibold rounded-full ${
                insights.summary.quality_indicator.toLowerCase().includes('excellent')
                  ? 'bg-green-100 text-green-800'
                  : insights.summary.quality_indicator.toLowerCase().includes('good')
                  ? 'bg-blue-100 text-blue-800'
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {insights.summary.quality_indicator}
              </span>
            )}
          </div>
          {insights.summary.recommendations && insights.summary.recommendations.length > 0 && (
            <div className="mt-3 pt-3 border-t border-indigo-200">
              <p className="text-xs font-semibold text-indigo-800 mb-1">Recommendations:</p>
              <ul className="text-xs text-indigo-700 space-y-1">
                {insights.summary.recommendations.slice(0, 3).map((rec, idx) => (
                  <li key={idx} className="flex items-start gap-1">
                    <span className="text-indigo-400">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="text-xs text-gray-500 mt-3 p-3 bg-gray-50 rounded-lg">
        <strong>Why track footfall?</strong> Visitor patterns indicate family engagement levels. 
        High repeat visitor rates and longer dwell times suggest families are actively involved 
        in their loved one's care - a positive quality indicator.
      </div>
    </div>
  );
}

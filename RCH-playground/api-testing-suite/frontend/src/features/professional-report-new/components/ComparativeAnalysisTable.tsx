import React from 'react';
import { TrendingUp, Award, DollarSign, MapPin, Shield, Star } from 'lucide-react';
import type { ComparativeAnalysis } from '../types';

interface ComparativeAnalysisTableProps {
  analysis: ComparativeAnalysis;
}

export default function ComparativeAnalysisTable({ analysis }: ComparativeAnalysisTableProps) {
  if (!analysis || !analysis.comparison_table || analysis.comparison_table.length === 0) {
    return null;
  }

  // Safety checks for nested objects
  const rankings = analysis.rankings || {};
  const rankingsStats = rankings.statistics || {
    highest_score: 0,
    lowest_score: 0,
    average_score: 0
  };

  const priceComparison = analysis.price_comparison || {};
  const priceStats = priceComparison.statistics || {
    highest_weekly: 0,
    lowest_weekly: 0,
    average_weekly: 0
  };

  const homes = analysis.comparison_table[0]?.homes ? Object.keys(analysis.comparison_table[0].homes) : [];
  const homeCount = homes.length;

  const getBadgeClass = (badge?: string) => {
    switch (badge) {
      case 'excellent':
        return 'bg-green-100 text-green-800';
      case 'very_good':
        return 'bg-blue-100 text-blue-800';
      case 'good':
        return 'bg-emerald-100 text-emerald-800';
      case 'fair':
        return 'bg-yellow-100 text-yellow-800';
      case 'poor':
        return 'bg-red-100 text-red-800';
      case 'warning':
        return 'bg-orange-100 text-orange-800';
      case 'high_risk':
        return 'bg-red-100 text-red-800';
      case 'medium_risk':
        return 'bg-yellow-100 text-yellow-800';
      case 'low_risk':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'Match Score':
        return <TrendingUp className="w-4 h-4" />;
      case 'Pricing':
        return <DollarSign className="w-4 h-4" />;
      case 'CQC Ratings':
        return <Shield className="w-4 h-4" />;
      case 'Reviews':
        return <Star className="w-4 h-4" />;
      case 'Basic Information':
        return <MapPin className="w-4 h-4" />;
      default:
        return <Award className="w-4 h-4" />;
    }
  };

  // Group rows by category
  const groupedRows: { [key: string]: typeof analysis.comparison_table } = {};
  analysis.comparison_table.forEach(row => {
    if (!groupedRows[row.category]) {
      groupedRows[row.category] = [];
    }
    groupedRows[row.category].push(row);
  });

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">Match Score Range</div>
          <div className="text-lg font-semibold text-gray-900">
            {rankingsStats.highest_score}% - {rankingsStats.lowest_score}%
          </div>
          <div className="text-xs text-gray-400 mt-1">
            Avg: {rankingsStats.average_score}%
          </div>
        </div>
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">Price Range (Weekly)</div>
          {priceStats.lowest_weekly > 0 && priceStats.highest_weekly > 0 ? (
            <>
              <div className="text-lg font-semibold text-gray-900">
                £{priceStats.lowest_weekly.toLocaleString()} - £{priceStats.highest_weekly.toLocaleString()}
              </div>
              <div className="text-xs text-gray-400 mt-1">
                Avg: £{priceStats.average_weekly.toLocaleString()}
              </div>
            </>
          ) : (
            <div className="text-sm text-gray-400">Price data not available</div>
          )}
        </div>
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">Best Value</div>
          {priceComparison.best_value ? (
            <>
              <div className="text-lg font-semibold text-green-700">
                {analysis.price_comparison.best_value.home_name}
              </div>
              <div className="text-xs text-gray-400 mt-1">
                Score: {analysis.price_comparison.best_value.match_score}% • £{analysis.price_comparison.best_value.weekly_price.toLocaleString()}/week
              </div>
            </>
          ) : (
            <div className="text-sm text-gray-400">N/A</div>
          )}
        </div>
      </div>

      {/* Comparison Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left py-3 px-4 font-semibold text-gray-900 sticky left-0 bg-gray-50 z-10 min-w-[200px]">
                  Metric
                </th>
                {homes.map((homeKey, idx) => (
                  <th key={homeKey} className="text-center py-3 px-3 font-semibold text-gray-900 min-w-[150px]">
                    <div className="flex flex-col items-center">
                      <span className="text-xs font-bold">#{idx + 1}</span>
                      <span className="text-xs text-gray-600 mt-1">
                        {analysis.comparison_table.find(r => r.metric === 'Name')?.homes[homeKey]?.value || `Home ${idx + 1}`}
                      </span>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Object.entries(groupedRows).map(([category, rows]) => (
                <React.Fragment key={category}>
                  {/* Category Header */}
                  <tr className="bg-gray-100 border-b border-gray-200">
                    <td colSpan={homeCount + 1} className="py-2 px-4">
                      <div className="flex items-center font-semibold text-gray-900">
                        {getCategoryIcon(category)}
                        <span className="ml-2">{category}</span>
                      </div>
                    </td>
                  </tr>
                  {/* Category Rows */}
                  {rows.map((row, rowIdx) => {
                    return (
                    <tr key={`${category}-${rowIdx}`} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-2 px-4 font-medium text-gray-700 sticky left-0 bg-white z-10">
                        {row.metric}
                      </td>
                      {homes.map((homeKey) => {
                        const cellData = row.homes[homeKey];
                        const value = cellData?.value || 'N/A';
                        const highlight = cellData?.highlight || false;
                        const badge = cellData?.badge;
                        
                        return (
                          <td key={homeKey} className={`py-2 px-3 text-center ${highlight ? 'font-semibold' : ''}`}>
                            <div className="flex flex-col items-center">
                              {badge ? (
                                <span className={`text-xs px-2 py-0.5 rounded-full ${getBadgeClass(badge)}`}>
                                  {value}
                                </span>
                              ) : (
                                <span className={highlight ? 'text-gray-900' : 'text-gray-700'}>
                                  {typeof value === 'string' && value.length > 30 
                                    ? `${value.substring(0, 30)}...` 
                                    : value}
                                </span>
                              )}
                            </div>
                          </td>
                        );
                      })}
                    </tr>
                    );
                  })}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Key Differentiators */}
      {analysis.key_differentiators && analysis.key_differentiators.length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
            <Award className="w-4 h-4 mr-2 text-purple-600" />
            Key Differentiators
          </h5>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {analysis.key_differentiators.map((diff, idx) => (
              <div 
                key={idx} 
                className={`p-3 rounded-lg border ${
                  diff.importance === 'high' 
                    ? 'bg-purple-50 border-purple-200' 
                    : diff.importance === 'medium'
                    ? 'bg-blue-50 border-blue-200'
                    : 'bg-gray-50 border-gray-200'
                }`}
              >
                <div className="flex items-start justify-between mb-1">
                  <span className={`text-xs font-semibold ${
                    diff.importance === 'high' ? 'text-purple-900' : 'text-gray-900'
                  }`}>
                    {diff.title}
                  </span>
                  {diff.importance === 'high' && (
                    <span className="text-xs px-1.5 py-0.5 bg-purple-200 text-purple-800 rounded">
                      Important
                    </span>
                  )}
                </div>
                <div className="text-xs text-gray-700 mt-1">
                  {diff.description}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {diff.home_name}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Rankings Summary */}
      {analysis.rankings && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3">Match Score Rankings</h5>
          <div className="space-y-2">
            {analysis.rankings.rankings.map((ranking) => (
              <div key={ranking.home_id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <div className="flex items-center">
                  <span className="text-xs font-bold text-gray-900 w-8">#{ranking.rank}</span>
                  <span className="text-xs font-medium text-gray-900">{ranking.home_name}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs font-semibold text-gray-900">
                    {ranking.match_score}%
                  </span>
                  {ranking.rank === 1 && (
                    <span className="text-xs px-2 py-0.5 bg-green-100 text-green-800 rounded">
                      Top Match
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendation */}
      {analysis.summary && analysis.summary.recommendation && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-2">Recommendation</h5>
          <p className="text-xs text-gray-700 leading-relaxed">
            {analysis.summary.recommendation}
          </p>
        </div>
      )}
    </div>
  );
}


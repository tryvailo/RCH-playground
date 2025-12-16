import { useState } from 'react';
import type { HiddenFeesAnalysis, HiddenFee } from '../types';

interface HiddenFeesDetectorProps {
  analysis: HiddenFeesAnalysis | null | undefined;
  showDetails?: boolean;
}

// Safe number formatter
const safeNumber = (value: unknown, defaultValue = 0): number => {
  if (value === null || value === undefined) return defaultValue;
  const num = Number(value);
  return isNaN(num) ? defaultValue : num;
};

export default function HiddenFeesDetector({ analysis, showDetails = true }: HiddenFeesDetectorProps) {
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null);
  const [showAllFees, setShowAllFees] = useState(false);

  // Handle null/undefined analysis
  if (!analysis) {
    return (
      <div className="bg-gray-50 rounded-lg border border-gray-200 p-4 text-center text-gray-500">
        No hidden fees analysis available
      </div>
    );
  }

  const getRiskColor = (risk: 'high' | 'medium' | 'low') => {
    switch (risk) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      case 'medium': return 'text-amber-600 bg-amber-50 border-amber-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
    }
  };

  const getRiskBadge = (risk: 'high' | 'medium' | 'low') => {
    switch (risk) {
      case 'high': return 'bg-red-100 text-red-700';
      case 'medium': return 'bg-amber-100 text-amber-700';
      case 'low': return 'bg-green-100 text-green-700';
    }
  };

  const formatCurrency = (amount: unknown) => `£${safeNumber(amount).toLocaleString()}`;
  
  const formatFrequency = (freq: string | undefined | null) => {
    switch (freq) {
      case 'one_time': return 'One-time';
      case 'weekly': return '/week';
      case 'monthly': return '/month';
      case 'annual_percent': return '% annually';
      case 'per_occurrence': return '/occurrence';
      default: return freq;
    }
  };

  // Safe access to arrays with fallbacks
  const detectedFees = analysis.detected_fees || [];
  const summary = analysis.summary || {};
  const riskAssessment = analysis.risk_assessment || { overall_risk: 'low', transparency_score: 100, predictability_score: 100 };
  const warnings = analysis.warnings || [];
  const negotiationTips = analysis.negotiation_tips || [];
  const questionsToAsk = analysis.questions_to_ask || [];
  const feesByCategory = analysis.fees_by_category || {};

  const highRiskFees = detectedFees.filter(f => f?.risk_level === 'high');
  const negotiableFees = detectedFees.filter(f => f?.negotiable);

  return (
    <div className="space-y-4">
      {/* Summary Header */}
      <div className={`rounded-lg border p-4 ${getRiskColor(riskAssessment.overall_risk as 'high' | 'medium' | 'low')}`}>
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-semibold text-lg">{analysis.home_name || 'Unknown Home'}</h4>
            <p className="text-sm opacity-80">
              Advertised: {formatCurrency(analysis.advertised_weekly_price)}/week
            </p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">
              {formatCurrency(summary.true_weekly_cost)}/week
            </div>
            <div className="text-sm">
              True cost (+{safeNumber(summary.hidden_fee_percent)}%)
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-white rounded-lg border border-gray-200 p-3 text-center">
          <div className="text-lg font-bold text-gray-900">
            {formatCurrency(summary.total_weekly_hidden)}
          </div>
          <div className="text-xs text-gray-500">Hidden Fees/Week</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-3 text-center">
          <div className="text-lg font-bold text-gray-900">
            {formatCurrency(summary.total_annual_hidden)}
          </div>
          <div className="text-xs text-gray-500">Hidden Fees/Year</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-3 text-center">
          <div className="text-lg font-bold text-gray-900">
            {formatCurrency(summary.total_one_time_fees)}
          </div>
          <div className="text-xs text-gray-500">Move-In Costs</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-3 text-center">
          <div className="text-lg font-bold text-green-600">
            {formatCurrency(summary.potential_negotiation_savings)}
          </div>
          <div className="text-xs text-gray-500">Potential Savings</div>
        </div>
      </div>

      {/* Warnings */}
      {warnings.length > 0 && (
        <div className="space-y-2">
          {warnings.map((warning, i) => (
            <div
              key={i}
              className={`flex items-start gap-2 p-3 rounded-lg border ${
                warning.severity === 'high' 
                  ? 'bg-red-50 border-red-200' 
                  : 'bg-amber-50 border-amber-200'
              }`}
            >
              <span className="text-lg">
                {warning.severity === 'high' ? '⚠️' : '⚡'}
              </span>
              <div>
                <div className="font-medium text-sm">{warning.title}</div>
                <div className="text-xs text-gray-600">{warning.message}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Risk Scores */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h5 className="font-semibold text-sm mb-3">Risk Assessment</h5>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-gray-600">Overall Risk</span>
              <span className={`text-xs px-2 py-0.5 rounded ${getRiskBadge(riskAssessment.overall_risk as 'high' | 'medium' | 'low')}`}>
                {(riskAssessment.overall_risk || 'low').toUpperCase()}
              </span>
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-600 mb-1">Transparency</div>
            <div className="flex items-center gap-2">
              <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-blue-500 rounded-full"
                  style={{ width: `${safeNumber(riskAssessment.transparency_score, 100)}%` }}
                />
              </div>
              <span className="text-xs font-medium">{safeNumber(riskAssessment.transparency_score, 100)}%</span>
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-600 mb-1">Predictability</div>
            <div className="flex items-center gap-2">
              <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-purple-500 rounded-full"
                  style={{ width: `${safeNumber(riskAssessment.predictability_score, 100)}%` }}
                />
              </div>
              <span className="text-xs font-medium">{safeNumber(riskAssessment.predictability_score, 100)}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* High Risk Fees Alert */}
      {highRiskFees.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h5 className="font-semibold text-sm text-red-800 mb-2">
            ⚠️ High Impact Fees ({highRiskFees.length})
          </h5>
          <div className="space-y-2">
            {highRiskFees.map(fee => (
              <div key={fee.fee_id} className="flex justify-between items-center text-sm">
                <div>
                  <span className="font-medium text-red-700">{fee.display_name}</span>
                  {fee.negotiable && (
                    <span className="ml-2 text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded">
                      Negotiable
                    </span>
                  )}
                </div>
                <div className="text-red-800 font-semibold">
                  {formatCurrency(fee.annual_impact)}/year
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Fees by Category */}
      {showDetails && (
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="p-4 border-b border-gray-100">
            <div className="flex items-center justify-between">
              <h5 className="font-semibold text-sm">Detected Fees by Category</h5>
              <button
                onClick={() => setShowAllFees(!showAllFees)}
                className="text-xs text-blue-600 hover:text-blue-800"
              >
                {showAllFees ? 'Show Less' : 'Show All'}
              </button>
            </div>
          </div>
          
          <div className="divide-y divide-gray-100">
            {Object.entries(feesByCategory).map(([categoryKey, category]) => (
              <div key={categoryKey}>
                <button
                  onClick={() => setExpandedCategory(expandedCategory === categoryKey ? null : categoryKey)}
                  className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{category.icon || '📋'}</span>
                    <span className="font-medium text-sm">{category.display_name}</span>
                    <span className="text-xs text-gray-500">({category.fees.length} fees)</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-semibold text-gray-900">
                      {formatCurrency(category.total_annual)}/year
                    </span>
                    <svg
                      className={`w-4 h-4 text-gray-400 transition-transform ${
                        expandedCategory === categoryKey ? 'rotate-180' : ''
                      }`}
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </button>
                
                {expandedCategory === categoryKey && (
                  <div className="px-4 pb-3 space-y-2">
                    {(category.fees || []).map((fee: HiddenFee) => (
                      <div
                        key={fee.fee_id}
                        className="flex items-center justify-between p-2 bg-gray-50 rounded text-sm"
                      >
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-medium">{fee.display_name}</span>
                            {fee.negotiable && (
                              <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded">
                                Negotiable
                              </span>
                            )}
                            {fee.refundable && (
                              <span className="text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded">
                                Refundable
                              </span>
                            )}
                            {fee.included_sometimes && (
                              <span className="text-xs bg-purple-100 text-purple-700 px-1.5 py-0.5 rounded">
                                Sometimes included
                              </span>
                            )}
                          </div>
                          <div className="text-xs text-gray-500 mt-0.5">
                            {fee.description}
                          </div>
                          <div className="text-xs text-gray-400 mt-0.5">
                            Likelihood: {fee.likelihood}%
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold">
                            {formatCurrency(fee.estimated_amount)}
                            <span className="text-xs font-normal text-gray-500 ml-1">
                              {formatFrequency(fee.frequency)}
                            </span>
                          </div>
                          <div className="text-xs text-gray-500">
                            Range: {formatCurrency(fee.range_low)} - {formatCurrency(fee.range_high)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Negotiation Tips */}
      {negotiableFees.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h5 className="font-semibold text-sm text-green-800 mb-2">
            💡 Negotiation Opportunities
          </h5>
          <div className="space-y-2">
            {negotiationTips.slice(0, 3).map((tip, i) => (
              <div key={i} className="text-sm">
                <span className="font-medium text-green-700">{tip?.title || 'Tip'}:</span>
                <span className="text-green-600 ml-1">{tip?.tip || ''}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Questions to Ask */}
      {questionsToAsk.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h5 className="font-semibold text-sm text-blue-800 mb-2">
            📝 Questions to Ask the Care Home
          </h5>
          <ul className="text-sm text-blue-700 space-y-1">
            {questionsToAsk.slice(0, 5).map((q, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-blue-500">•</span>
                {q}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

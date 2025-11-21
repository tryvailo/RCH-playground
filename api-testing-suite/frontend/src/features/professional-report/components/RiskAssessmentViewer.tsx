import React from 'react';
import { AlertTriangle, TrendingDown, Shield, Users, DollarSign, AlertCircle, CheckCircle2, Info } from 'lucide-react';
import type { RiskAssessment, RedFlag, Warning } from '../types';

interface RiskAssessmentViewerProps {
  assessment: RiskAssessment;
}

export default function RiskAssessmentViewer({ assessment }: RiskAssessmentViewerProps) {
  if (!assessment || !assessment.homes_assessment || assessment.homes_assessment.length === 0) {
    return null;
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high':
        return <AlertTriangle className="w-5 h-5 text-red-600" />;
      case 'medium':
        return <AlertCircle className="w-5 h-5 text-yellow-600" />;
      case 'low':
        return <Info className="w-5 h-5 text-blue-600" />;
      default:
        return <Info className="w-5 h-5 text-gray-600" />;
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'high':
        return 'bg-red-50 border-red-200';
      case 'medium':
        return 'bg-yellow-50 border-yellow-200';
      case 'low':
        return 'bg-green-50 border-green-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const getCategoryIcon = (type: string) => {
    switch (type) {
      case 'financial':
        return <TrendingDown className="w-4 h-4" />;
      case 'cqc':
        return <Shield className="w-4 h-4" />;
      case 'staff':
        return <Users className="w-4 h-4" />;
      case 'pricing':
        return <DollarSign className="w-4 h-4" />;
      default:
        return <AlertCircle className="w-4 h-4" />;
    }
  };

  const summary = assessment.summary;

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">Total Red Flags</div>
          <div className="text-2xl font-bold text-red-600">
            {summary.total_red_flags}
          </div>
          <div className="text-xs text-gray-400 mt-1">
            Across {summary.total_homes_assessed} homes
          </div>
        </div>
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">High Risk Homes</div>
          <div className="text-2xl font-bold text-red-600">
            {summary.risk_distribution.high}
          </div>
          <div className="text-xs text-gray-400 mt-1">
            {summary.risk_distribution.medium} medium, {summary.risk_distribution.low} low
          </div>
        </div>
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">Financial Flags</div>
          <div className="text-xl font-semibold text-gray-900">
            {summary.flags_by_category.financial}
          </div>
        </div>
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">CQC Issues</div>
          <div className="text-xl font-semibold text-gray-900">
            {summary.flags_by_category.cqc}
          </div>
        </div>
      </div>

      {/* Overall Assessment */}
      {summary.overall_assessment && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-2 flex items-center">
            <Info className="w-4 h-4 mr-2 text-blue-600" />
            Overall Risk Assessment
          </h5>
          <p className="text-xs text-gray-700 leading-relaxed">
            {summary.overall_assessment}
          </p>
        </div>
      )}

      {/* Highest Risk Homes */}
      {summary.highest_risk_homes && summary.highest_risk_homes.length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3">Highest Risk Homes</h5>
          <div className="space-y-2">
            {summary.highest_risk_homes.map((home, idx) => (
              <div key={idx} className={`p-3 rounded-lg border ${getRiskLevelColor(home.risk_level)}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <span className="text-xs font-bold text-gray-900 mr-2">#{idx + 1}</span>
                    <span className="text-xs font-semibold text-gray-900">{home.home_name}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-semibold text-gray-700">
                      Risk Score: {home.risk_score}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded-full ${getSeverityColor(home.risk_level)}`}>
                      {home.risk_level.toUpperCase()}
                    </span>
                    <span className="text-xs text-red-600 font-semibold">
                      {home.red_flag_count} flag{home.red_flag_count !== 1 ? 's' : ''}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Home-by-Home Assessment */}
      <div className="space-y-4">
        <h5 className="text-sm font-semibold text-gray-900">Detailed Risk Assessment by Home</h5>
        {assessment.homes_assessment.map((homeAssessment) => (
          <div key={homeAssessment.home_id} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            {/* Home Header */}
            <div className={`p-4 border-b ${getRiskLevelColor(homeAssessment.overall_risk_level)}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <h6 className="text-sm font-semibold text-gray-900">{homeAssessment.home_name}</h6>
                  <span className={`ml-3 text-xs px-2 py-1 rounded-full ${getSeverityColor(homeAssessment.overall_risk_level)}`}>
                    {homeAssessment.overall_risk_level.toUpperCase()} RISK
                  </span>
                </div>
                <div className="flex items-center gap-4 text-xs">
                  <span className="text-gray-600">
                    Risk Score: <span className="font-semibold">{homeAssessment.risk_score}</span>
                  </span>
                  <span className="text-red-600 font-semibold">
                    {homeAssessment.red_flags.length} Red Flag{homeAssessment.red_flags.length !== 1 ? 's' : ''}
                  </span>
                  <span className="text-yellow-600 font-semibold">
                    {homeAssessment.warnings.length} Warning{homeAssessment.warnings.length !== 1 ? 's' : ''}
                  </span>
                </div>
              </div>
            </div>

            {/* Red Flags */}
            {homeAssessment.red_flags.length > 0 && (
              <div className="p-4 border-b border-gray-100">
                <h6 className="text-xs font-semibold text-red-900 mb-3 flex items-center">
                  <AlertTriangle className="w-4 h-4 mr-2" />
                  Red Flags ({homeAssessment.red_flags.length})
                </h6>
                <div className="space-y-3">
                  {homeAssessment.red_flags.map((flag, idx) => (
                    <div key={idx} className="bg-red-50 rounded-lg p-3 border border-red-200">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center">
                          {getCategoryIcon(flag.type)}
                          <span className="ml-2 text-xs font-semibold text-red-900">{flag.title}</span>
                        </div>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${getSeverityColor(flag.severity)}`}>
                          {flag.severity.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-xs text-gray-700 mb-2">{flag.description}</p>
                      <div className="text-xs text-gray-600 mb-1">
                        <span className="font-semibold">Impact:</span> {flag.impact}
                      </div>
                      <div className="text-xs text-gray-600">
                        <span className="font-semibold">Recommendation:</span> {flag.recommendation}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Warnings */}
            {homeAssessment.warnings.length > 0 && (
              <div className="p-4 border-b border-gray-100">
                <h6 className="text-xs font-semibold text-yellow-900 mb-3 flex items-center">
                  <AlertCircle className="w-4 h-4 mr-2" />
                  Warnings ({homeAssessment.warnings.length})
                </h6>
                <div className="space-y-2">
                  {homeAssessment.warnings.map((warning, idx) => (
                    <div key={idx} className="bg-yellow-50 rounded-lg p-3 border border-yellow-200">
                      <div className="flex items-start justify-between mb-1">
                        <div className="flex items-center">
                          {getCategoryIcon(warning.type)}
                          <span className="ml-2 text-xs font-semibold text-yellow-900">{warning.title}</span>
                        </div>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${getSeverityColor(warning.severity)}`}>
                          {warning.severity.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-xs text-gray-700 mb-1">{warning.description}</p>
                      <div className="text-xs text-gray-600">
                        <span className="font-semibold">Recommendation:</span> {warning.recommendation}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Category Breakdown */}
            <div className="p-4 bg-gray-50">
              <h6 className="text-xs font-semibold text-gray-900 mb-2">Risk Breakdown by Category</h6>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                <div>
                  <div className="text-gray-500">Financial</div>
                  <div className="font-semibold text-gray-900">
                    {homeAssessment.financial_assessment.risk_score} pts
                  </div>
                  <div className="text-gray-400">
                    {homeAssessment.financial_assessment.red_flags.length} flags
                  </div>
                </div>
                <div>
                  <div className="text-gray-500">CQC</div>
                  <div className="font-semibold text-gray-900">
                    {homeAssessment.cqc_assessment.risk_score} pts
                  </div>
                  <div className="text-gray-400">
                    {homeAssessment.cqc_assessment.red_flags.length} flags
                  </div>
                </div>
                <div>
                  <div className="text-gray-500">Staff</div>
                  <div className="font-semibold text-gray-900">
                    {homeAssessment.staff_assessment.risk_score} pts
                  </div>
                  <div className="text-gray-400">
                    {homeAssessment.staff_assessment.red_flags.length} flags
                  </div>
                </div>
                <div>
                  <div className="text-gray-500">Pricing</div>
                  <div className="font-semibold text-gray-900">
                    {homeAssessment.pricing_assessment.risk_score} pts
                  </div>
                  <div className="text-gray-400">
                    {homeAssessment.pricing_assessment.red_flags.length} flags
                  </div>
                </div>
              </div>
            </div>

            {/* No Issues Message */}
            {homeAssessment.red_flags.length === 0 && homeAssessment.warnings.length === 0 && (
              <div className="p-4 text-center">
                <CheckCircle2 className="w-8 h-8 text-green-500 mx-auto mb-2" />
                <p className="text-xs text-gray-600">No red flags or warnings identified for this home.</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}


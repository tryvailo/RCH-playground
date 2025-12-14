import React from 'react';
import { TrendingUp, Shield, DollarSign, Users, AlertCircle, Award, MapPin, Star } from 'lucide-react';
import PriceComparisonChart from './PriceComparisonChart';
import type { ProfessionalReportData } from '../types';

interface ExecutiveSummaryDashboardProps {
  report: ProfessionalReportData;
}

export default function ExecutiveSummaryDashboard({ report }: ExecutiveSummaryDashboardProps) {
  const topHome = report.careHomes[0];
  const avgMatchScore = report.careHomes.length > 0
    ? report.careHomes.reduce((sum, h) => sum + h.matchScore, 0) / report.careHomes.length
    : 0;
  
  const avgPrice = report.careHomes.length > 0
    ? report.careHomes.reduce((sum, h) => sum + h.weeklyPrice, 0) / report.careHomes.length
    : 0;

  const highRiskHomes = report.riskAssessment?.summary?.risk_distribution?.high || 0;
  const totalRedFlags = report.riskAssessment?.summary?.total_red_flags || 0;

  // Calculate funding savings potential
  const fundingSavings = report.fundingOptimization?.five_year_projections?.summary?.potential_5_year_savings || 0;

  return (
    <div className="space-y-6">
      {/* Key Metrics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            <span className="text-xs text-blue-600 font-semibold">Top Match</span>
          </div>
          <div className="text-2xl font-bold text-blue-900">
            {topHome?.matchScore.toFixed(1)}%
          </div>
          <div className="text-xs text-blue-700 mt-1">
            {topHome?.name}
          </div>
          {topHome?.matchReason && (
            <div className="text-xs text-blue-600 mt-1 italic">
              {topHome.matchReason}
            </div>
          )}
          {topHome?.waitingListStatus && (
            <div className={`text-xs mt-1 font-semibold ${
              topHome.waitingListStatus === 'Available now' 
                ? 'text-green-700' 
                : topHome.waitingListStatus === '2-4 weeks'
                ? 'text-yellow-700'
                : 'text-red-700'
            }`}>
              {topHome.waitingListStatus}
            </div>
          )}
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
          <div className="flex items-center justify-between mb-2">
            <DollarSign className="w-5 h-5 text-green-600" />
            <span className="text-xs text-green-600 font-semibold">Avg Price</span>
          </div>
          <div className="text-2xl font-bold text-green-900">
            £{Math.round(avgPrice).toLocaleString()}
          </div>
          <div className="text-xs text-green-700 mt-1">
            per week
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4 border border-purple-200">
          <div className="flex items-center justify-between mb-2">
            <Shield className="w-5 h-5 text-purple-600" />
            <span className="text-xs text-purple-600 font-semibold">Risk Level</span>
          </div>
          <div className="text-2xl font-bold text-purple-900">
            {highRiskHomes === 0 ? 'Low' : highRiskHomes <= 1 ? 'Medium' : 'High'}
          </div>
          <div className="text-xs text-purple-700 mt-1">
            {totalRedFlags} red flags
          </div>
        </div>

        <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4 border border-orange-200">
          <div className="flex items-center justify-between mb-2">
            <Award className="w-5 h-5 text-orange-600" />
            <span className="text-xs text-orange-600 font-semibold">Savings</span>
          </div>
          <div className="text-2xl font-bold text-orange-900">
            £{Math.round(fundingSavings / 1000)}k
          </div>
          <div className="text-xs text-orange-700 mt-1">
            5-year potential
          </div>
        </div>
      </div>

      {/* Price Comparison Chart */}
      <div className="bg-white rounded-lg p-4 border border-gray-200">
        <PriceComparisonChart homes={report.careHomes} />
      </div>

      {/* Quick Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        <div className="bg-white rounded-lg p-3 border border-gray-200">
          <div className="flex items-center gap-2 mb-1">
            <Users className="w-4 h-4 text-gray-500" />
            <span className="text-xs text-gray-500">Homes Analyzed</span>
          </div>
          <div className="text-lg font-bold text-gray-900">
            {report.analysisSummary.totalHomesAnalyzed}
          </div>
        </div>

        <div className="bg-white rounded-lg p-3 border border-gray-200">
          <div className="flex items-center gap-2 mb-1">
            <Star className="w-4 h-4 text-gray-500" />
            <span className="text-xs text-gray-500">Avg Match Score</span>
          </div>
          <div className="text-lg font-bold text-gray-900">
            {avgMatchScore.toFixed(1)}%
          </div>
        </div>

        <div className="bg-white rounded-lg p-3 border border-gray-200">
          <div className="flex items-center gap-2 mb-1">
            <MapPin className="w-4 h-4 text-gray-500" />
            <span className="text-xs text-gray-500">Location</span>
          </div>
          <div className="text-lg font-bold text-gray-900">
            {report.city}
          </div>
        </div>
      </div>
    </div>
  );
}


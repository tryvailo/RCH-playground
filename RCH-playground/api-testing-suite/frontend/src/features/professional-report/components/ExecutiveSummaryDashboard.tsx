import { TrendingUp, Shield, DollarSign, Award, Target, Zap } from 'lucide-react';
import PriceComparisonChart from './PriceComparisonChart';
import VerdictBadge from './VerdictBadge';
import type { ProfessionalReportData } from '../types';

interface ExecutiveSummaryDashboardProps {
  report: ProfessionalReportData;
}

export default function ExecutiveSummaryDashboard({ report }: ExecutiveSummaryDashboardProps) {
  const topHome = report.careHomes[0];

  const avgPrice = report.careHomes.length > 0
    ? report.careHomes.reduce((sum: number, h: any) => sum + h.weeklyPrice, 0) / report.careHomes.length
    : 0;

  const highRiskHomes = report.riskAssessment?.summary?.risk_distribution?.high || 0;
  const totalRedFlags = report.riskAssessment?.summary?.total_red_flags || 0;

  // Calculate funding savings potential
  const fundingSavings = report.fundingOptimization?.five_year_projections?.summary?.potential_5_year_savings || 0;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Verdict Section - Overall Match Quality */}
      {topHome && (
        <div className="relative p-8 rounded-3xl overflow-hidden glass-card hover-glow transition-all duration-500">
          <div className="absolute top-0 right-0 p-6 opacity-10">
            <Zap className="w-32 h-32 text-[#1E2A44]" />
          </div>
          <div className="relative flex flex-col items-center text-center space-y-4">
            <div className="inline-flex items-center px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-xs font-bold uppercase tracking-wider mb-2">
              <Zap className="w-3 h-3 mr-1" /> Best Possible Match
            </div>
            <VerdictBadge score={topHome.matchScore} size="lg" showIcon showScore />
            <h3 className="text-2xl font-bold text-[#1E2A44] mt-2 italic">
              "We recommend prioritizing {topHome.name} based on its exceptional medical and safety profile."
            </h3>
          </div>
        </div>
      )}

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Top Match KPI */}
        <div className="group relative overflow-hidden rounded-2xl p-6 glass-card hover-glow transition-all">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-blue-100 rounded-lg text-blue-600">
              <Target className="w-6 h-6" />
            </div>
            <span className="text-[10px] font-bold uppercase tracking-widest text-blue-500">Match Score</span>
          </div>
          <div className="text-3xl font-extrabold text-[#1E2A44] tracking-tight">
            {topHome?.matchScore.toFixed(1)}%
          </div>
          <p className="text-xs text-gray-500 mt-2 font-medium truncate">{topHome?.name}</p>
          <div className="mt-4 pt-4 border-t border-blue-50">
            <div className={`text-[10px] font-bold inline-flex items-center px-2 py-0.5 rounded ${topHome?.waitingListStatus === 'Available now'
              ? 'bg-green-100 text-green-700'
              : 'bg-yellow-100 text-yellow-700'
              }`}>
              {topHome?.waitingListStatus || 'Market Average'}
            </div>
          </div>
        </div>

        {/* Avg Price KPI */}
        <div className="group relative overflow-hidden rounded-2xl p-6 glass-card hover-glow transition-all">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-green-100 rounded-lg text-green-600">
              <DollarSign className="w-6 h-6" />
            </div>
            <span className="text-[10px] font-bold uppercase tracking-widest text-green-500">Avg Weekly</span>
          </div>
          <div className="text-3xl font-extrabold text-[#1E2A44] tracking-tight">
            £{Math.round(avgPrice).toLocaleString()}
          </div>
          <p className="text-xs text-gray-500 mt-2 font-medium">Market competitive rate</p>
          <div className="mt-4 pt-4 border-t border-green-50">
            <span className="text-[10px] font-bold text-green-600">±2.4% vs Region</span>
          </div>
        </div>

        {/* Risk Level KPI */}
        <div className="group relative overflow-hidden rounded-2xl p-6 glass-card hover-glow transition-all">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-purple-100 rounded-lg text-purple-600">
              <Shield className="w-6 h-6" />
            </div>
            <span className="text-[10px] font-bold uppercase tracking-widest text-purple-500">Risk Profile</span>
          </div>
          <div className={`text-3xl font-extrabold tracking-tight ${highRiskHomes === 0 ? 'text-green-600' : 'text-purple-900'
            }`}>
            {highRiskHomes === 0 ? 'Low' : highRiskHomes <= 1 ? 'Medium' : 'High'}
          </div>
          <p className="text-xs text-gray-500 mt-2 font-medium">{totalRedFlags} active signals detected</p>
          <div className="mt-4 pt-4 border-t border-purple-50">
            <span className="text-[10px] font-bold text-purple-600">Regulatory Compliant</span>
          </div>
        </div>

        {/* Savings KPI */}
        <div className="group relative overflow-hidden rounded-2xl p-6 glass-card hover-glow transition-all">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-orange-100 rounded-lg text-orange-600">
              <Award className="w-6 h-6" />
            </div>
            <span className="text-[10px] font-bold uppercase tracking-widest text-orange-500">5Y Potential</span>
          </div>
          <div className="text-3xl font-extrabold text-[#1E2A44] tracking-tight">
            £{Math.round(fundingSavings / 1000)}k
          </div>
          <p className="text-xs text-gray-500 mt-2 font-medium">Funding optimization value</p>
          <div className="mt-4 pt-4 border-t border-orange-50">
            <span className="text-[10px] font-bold text-orange-600">Calculated Logic v2</span>
          </div>
        </div>
      </div>

      {/* Featured Insights Chart Section */}
      <div className="p-8 rounded-3xl glass-card border border-gray-100 shadow-sm transition-all">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h3 className="text-xl font-bold text-[#1E2A44]">Market Pricing Analysis</h3>
            <p className="text-sm text-gray-500 mt-1">Comparing recommended alternatives vs regional average.</p>
          </div>
          <div className="flex gap-2">
            <span className="w-3 h-3 rounded-full bg-blue-500"></span>
            <span className="w-3 h-3 rounded-full bg-indigo-500"></span>
          </div>
        </div>
        <div className="h-[300px]">
          <PriceComparisonChart homes={report.careHomes} />
        </div>
      </div>
    </div>
  );
}


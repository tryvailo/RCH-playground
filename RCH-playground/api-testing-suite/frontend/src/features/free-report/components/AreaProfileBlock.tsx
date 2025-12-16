/**
 * Area Profile Block
 * Shows local area context: total homes, average costs, CQC distribution, demographics
 * ТЗ Section 7: Local Area Context
 * 
 * REUSES: ScoreCard from shared components
 */
import { 
  MapPin, 
  Home, 
  TrendingUp, 
  TrendingDown,
  Users,
  Heart,
  TreePine,
  Building2
} from 'lucide-react';
import { ScoreCard } from '../../../shared/components/ScoreCard';
import type { AreaProfile } from '../types';

interface AreaProfileBlockProps {
  areaProfile: AreaProfile;
  className?: string;
}

function CQCDistributionBar({ distribution }: { distribution: AreaProfile['cqc_distribution'] }) {
  const total = distribution.outstanding + distribution.good + distribution.requires_improvement + distribution.inadequate;
  
  const getPercentage = (value: number) => total > 0 ? ((value / total) * 100).toFixed(0) : '0';
  
  return (
    <div className="space-y-3">
      <h4 className="text-sm font-semibold text-gray-700">CQC Rating Distribution</h4>
      
      {/* Visual Bar */}
      <div className="h-4 rounded-full overflow-hidden flex bg-gray-200">
        {distribution.outstanding > 0 && (
          <div 
            className="bg-emerald-500 transition-all duration-500"
            style={{ width: `${getPercentage(distribution.outstanding)}%` }}
            title={`Outstanding: ${getPercentage(distribution.outstanding)}%`}
          />
        )}
        {distribution.good > 0 && (
          <div 
            className="bg-blue-500 transition-all duration-500"
            style={{ width: `${getPercentage(distribution.good)}%` }}
            title={`Good: ${getPercentage(distribution.good)}%`}
          />
        )}
        {distribution.requires_improvement > 0 && (
          <div 
            className="bg-yellow-500 transition-all duration-500"
            style={{ width: `${getPercentage(distribution.requires_improvement)}%` }}
            title={`Requires Improvement: ${getPercentage(distribution.requires_improvement)}%`}
          />
        )}
        {distribution.inadequate > 0 && (
          <div 
            className="bg-red-500 transition-all duration-500"
            style={{ width: `${getPercentage(distribution.inadequate)}%` }}
            title={`Inadequate: ${getPercentage(distribution.inadequate)}%`}
          />
        )}
      </div>
      
      {/* Legend */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-full bg-emerald-500" />
          <span className="text-gray-600">Outstanding: {getPercentage(distribution.outstanding)}%</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-full bg-blue-500" />
          <span className="text-gray-600">Good: {getPercentage(distribution.good)}%</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-full bg-yellow-500" />
          <span className="text-gray-600">Requires Imp: {getPercentage(distribution.requires_improvement)}%</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <span className="text-gray-600">Inadequate: {getPercentage(distribution.inadequate)}%</span>
        </div>
      </div>
    </div>
  );
}

function WellbeingGauge({ score }: { score: number }) {
  const getColor = () => {
    if (score >= 75) return 'text-emerald-500';
    if (score >= 50) return 'text-blue-500';
    if (score >= 25) return 'text-yellow-500';
    return 'text-red-500';
  };
  
  const getLabel = () => {
    if (score >= 75) return 'Excellent';
    if (score >= 50) return 'Good';
    if (score >= 25) return 'Fair';
    return 'Needs Improvement';
  };
  
  return (
    <div className="text-center">
      <div className="relative inline-flex items-center justify-center">
        <svg className="w-24 h-24 transform -rotate-90">
          <circle
            cx="48"
            cy="48"
            r="40"
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            className="text-gray-200"
          />
          <circle
            cx="48"
            cy="48"
            r="40"
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            strokeDasharray={`${score * 2.51} 251`}
            className={getColor()}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`text-2xl font-bold ${getColor()}`}>{score}</span>
        </div>
      </div>
      <p className="text-sm text-gray-600 mt-1">Wellbeing Index</p>
      <p className={`text-xs font-semibold ${getColor()}`}>{getLabel()}</p>
    </div>
  );
}

export function AreaProfileBlock({ areaProfile, className = '' }: AreaProfileBlockProps) {
  const costTrend = areaProfile.cost_vs_national;
  const isAboveAverage = costTrend > 0;
  
  return (
    <div className={`bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden ${className}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-[#1E2A44] to-[#2D3E5F] px-6 py-5">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white/10 rounded-lg">
            <MapPin className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl md:text-2xl font-bold text-white">
              Care Homes in {areaProfile.area_name}
            </h2>
            <p className="text-gray-300 text-sm">Local Area Analysis</p>
          </div>
        </div>
      </div>
      
      <div className="p-6">
        {/* Key Stats Grid - Using ScoreCard from shared components */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <ScoreCard
            title="Care Homes in Area"
            score={areaProfile.total_homes}
            color="blue"
            icon={<Home className="w-4 h-4" />}
            size="md"
          />
          
          <ScoreCard
            title="Average Cost/Week"
            score={`£${areaProfile.average_weekly_cost.toLocaleString()}`}
            color="green"
            icon={<Building2 className="w-4 h-4" />}
            size="md"
          />
          
          <ScoreCard
            title="vs UK Average"
            score={`${isAboveAverage ? '+' : ''}${costTrend}%`}
            color={isAboveAverage ? 'red' : 'green'}
            icon={isAboveAverage ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
            size="md"
          />
          
          {/* Wellbeing Index */}
          {areaProfile.wellbeing_index !== undefined && (
            <div className="bg-gray-50 rounded-xl p-4 flex items-center justify-center">
              <WellbeingGauge score={areaProfile.wellbeing_index} />
            </div>
          )}
        </div>
        
        {/* CQC Distribution */}
        <div className="bg-gray-50 rounded-xl p-4 mb-6">
          <CQCDistributionBar distribution={areaProfile.cqc_distribution} />
        </div>
        
        {/* Demographics */}
        {areaProfile.demographics && (
          <div className="border-t border-gray-200 pt-6">
            <h4 className="text-sm font-semibold text-gray-700 mb-4">Demographics Snapshot</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Population 65+ */}
              <div className="flex items-center gap-3 bg-gray-50 rounded-lg p-3">
                <Users className="w-5 h-5 text-blue-500" />
                <div>
                  <p className="text-sm font-semibold text-gray-900">
                    {areaProfile.demographics.population_65_plus}%
                  </p>
                  <p className="text-xs text-gray-500">Population 65+</p>
                </div>
              </div>
              
              {/* Average Income */}
              {areaProfile.demographics.average_income && (
                <div className="flex items-center gap-3 bg-gray-50 rounded-lg p-3">
                  <Building2 className="w-5 h-5 text-green-500" />
                  <div>
                    <p className="text-sm font-semibold text-gray-900">
                      £{areaProfile.demographics.average_income.toLocaleString()}
                    </p>
                    <p className="text-xs text-gray-500">Average Income</p>
                  </div>
                </div>
              )}
              
              {/* Green Spaces */}
              {areaProfile.demographics.green_spaces && (
                <div className="flex items-center gap-3 bg-gray-50 rounded-lg p-3">
                  <TreePine className={`w-5 h-5 ${
                    areaProfile.demographics.green_spaces === 'high' ? 'text-emerald-500' :
                    areaProfile.demographics.green_spaces === 'medium' ? 'text-yellow-500' :
                    'text-gray-400'
                  }`} />
                  <div>
                    <p className="text-sm font-semibold text-gray-900 capitalize">
                      {areaProfile.demographics.green_spaces}
                    </p>
                    <p className="text-xs text-gray-500">Green Spaces</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
        
        {/* Info Note */}
        <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-100">
          <div className="flex items-start gap-2">
            <Heart className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
            <p className="text-xs text-blue-700">
              This area analysis helps you understand the local care home market. 
              A higher concentration of "Good" and "Outstanding" rated homes indicates 
              a competitive market with better care options.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

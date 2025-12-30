/**
 * Area Profile Block
 * Shows local area context: area suitability, elderly population, quality of life
 * ТЗ Section 7: Local Area Context
 */
import { 
  MapPin, 
  TrendingUp, 
  Users,
  Heart,
  TreePine,
  Building2,
  Star,
  AlertCircle,
  ArrowRight,
  Sparkles
} from 'lucide-react';
import type { AreaProfile } from '../types';

interface AreaProfileBlockProps {
  areaProfile: AreaProfile;
  className?: string;
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
  // Debug logging - FULL structure
  console.log('🔍 ========== AreaProfileBlock DEBUG ==========');
  console.log('🔍 Full areaProfile object:', areaProfile);
  console.log('🔍 areaProfile keys:', Object.keys(areaProfile));
  console.log('🔍 area_suitability_score:', areaProfile.area_suitability_score);
  console.log('🔍 area_suitability_rating:', areaProfile.area_suitability_rating);
  console.log('🔍 elderly_population:', areaProfile.elderly_population);
  console.log('🔍 wellbeing_details:', areaProfile.wellbeing_details);
  console.log('🔍 economic:', areaProfile.economic);
  console.log('🔍 top_highlights:', areaProfile.top_highlights);
  console.log('🔍 Full areaProfile JSON:', JSON.stringify(areaProfile, null, 2));
  console.log('🔍 ============================================');
  
  return (
    <div className={`bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden ${className}`}>
      <div className="p-6 space-y-6">
        {/* 1. Area Overview Card */}
        {areaProfile.area_suitability_score !== undefined && (
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border-2 border-blue-100">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <MapPin className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">
                    {areaProfile.area_name} Area Overview
                  </h3>
                  <p className="text-sm text-gray-600">Area Suitability Assessment</p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-blue-600">
                  {areaProfile.area_suitability_score}/100
                </div>
                <div className="flex items-center gap-1 mt-1">
                  {Array.from({ length: 5 }).map((_, i) => {
                    const rating = areaProfile.area_suitability_rating || 'Average';
                    const stars = rating === 'Excellent' ? 5 : rating === 'Good' ? 4 : rating === 'Average' ? 3 : 2;
                    return (
                      <Star
                        key={i}
                        className={`w-4 h-4 ${
                          i < stars ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
                        }`}
                      />
                    );
                  })}
                </div>
              </div>
            </div>
            
            <div className="mb-4">
              <p className="text-base font-semibold text-gray-900 mb-2">
                Rating: {areaProfile.area_suitability_rating || 'Average'} Area for Elderly Care
              </p>
            </div>
            
            {/* Highlights */}
            {areaProfile.top_highlights && areaProfile.top_highlights.length > 0 && (
              <div className="space-y-2 mb-4">
                {areaProfile.top_highlights.map((highlight, idx) => (
                  <div key={idx} className="flex items-start gap-2">
                    <span className="text-green-500 mt-0.5">✅</span>
                    <span className="text-sm text-gray-700">{highlight}</span>
                  </div>
                ))}
              </div>
            )}
            
            {/* Considerations */}
            {areaProfile.considerations && areaProfile.considerations.length > 0 && (
              <div className="space-y-2 mb-4">
                {areaProfile.considerations.map((consideration, idx) => (
                  <div key={idx} className="flex items-start gap-2">
                    <AlertCircle className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-gray-700">{consideration}</span>
                  </div>
                ))}
              </div>
            )}
            
            {/* Call-to-action */}
            <div className="mt-4 pt-4 border-t border-blue-200">
              <button
                onClick={() => {
                  // Scroll to upgrade section or trigger upgrade modal
                  window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
                }}
                className="flex items-center gap-2 text-sm font-semibold text-blue-600 hover:text-blue-700 transition-colors"
              >
                <span>💡 Want detailed analysis?</span>
                <span>See Professional Report</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
        
        {/* 2. Elderly Population & Demand */}
        {areaProfile.elderly_population && (
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Users className="w-5 h-5 text-blue-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900">Elderly Population in Area</h3>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {areaProfile.elderly_population.over_65_percent?.toFixed(1)}%
                </p>
                <p className="text-xs text-gray-600">Over 65</p>
                {areaProfile.elderly_population.vs_national_average !== undefined && (
                  <p className={`text-xs mt-1 ${
                    areaProfile.elderly_population.vs_national_average > 0 ? 'text-green-600' : 'text-gray-600'
                  }`}>
                    {areaProfile.elderly_population.vs_national_average > 0 ? '+' : ''}
                    {areaProfile.elderly_population.vs_national_average.toFixed(1)}% vs average
                  </p>
                )}
              </div>
              
              {areaProfile.elderly_population.over_80_percent !== undefined && (
                <div>
                  <p className="text-2xl font-bold text-gray-900">
                    {areaProfile.elderly_population.over_80_percent.toFixed(1)}%
                  </p>
                  <p className="text-xs text-gray-600">Over 80</p>
                </div>
              )}
              
              {areaProfile.elderly_population.elderly_population_trend && (
                <div>
                  <p className="text-lg font-semibold text-gray-900 capitalize">
                    {areaProfile.elderly_population.elderly_population_trend === 'Growing' ? '↗ Growing' :
                     areaProfile.elderly_population.elderly_population_trend === 'Stable' ? '→ Stable' :
                     '↘ Declining'}
                  </p>
                  <p className="text-xs text-gray-600">Trend</p>
                </div>
              )}
              
              {areaProfile.elderly_population.care_home_demand_indicator && (
                <div>
                  <p className="text-lg font-semibold text-gray-900 capitalize">
                    {areaProfile.elderly_population.care_home_demand_indicator}
                  </p>
                  <p className="text-xs text-gray-600">Demand</p>
                </div>
              )}
            </div>
            
            {areaProfile.elderly_population.projected_over_65_2030 !== undefined && (
              <div className="bg-blue-50 rounded-lg p-3 mb-4">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-blue-600" />
                  <p className="text-sm text-gray-700">
                    <span className="font-semibold">Projected 2030:</span>{' '}
                    {areaProfile.elderly_population.projected_over_65_2030.toFixed(1)}%
                  </p>
                </div>
              </div>
            )}
            
            <button
              onClick={() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })}
              className="flex items-center gap-2 text-xs text-blue-600 hover:text-blue-700 transition-colors"
            >
              <span>💡 See detailed health needs analysis in Professional Report</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        )}
        
        {/* 3. Quality of Life */}
        {areaProfile.wellbeing_details && (
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Sparkles className="w-5 h-5 text-purple-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900">Quality of Life in Area</h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              {areaProfile.wellbeing_index !== undefined && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <WellbeingGauge score={areaProfile.wellbeing_index} />
                </div>
              )}
              
              <div>
                <p className="text-sm text-gray-600 mb-1">Life Satisfaction</p>
                <p className="text-lg font-semibold text-gray-900">
                  {areaProfile.wellbeing_details.life_satisfaction !== undefined
                    ? areaProfile.wellbeing_details.life_satisfaction >= 7.5 ? 'High' :
                      areaProfile.wellbeing_details.life_satisfaction >= 6.5 ? 'Medium' : 'Low'
                    : 'N/A'}
                </p>
                {areaProfile.wellbeing_details.life_satisfaction !== undefined && (
                  <p className="text-xs text-gray-500 mt-1">
                    {areaProfile.wellbeing_details.life_satisfaction.toFixed(1)}/10
                  </p>
                )}
              </div>
              
              <div>
                <p className="text-sm text-gray-600 mb-1">Anxiety Level</p>
                <p className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  {areaProfile.wellbeing_details.anxiety_level !== undefined
                    ? areaProfile.wellbeing_details.anxiety_level <= 3.0 ? 'Low ✅' :
                      areaProfile.wellbeing_details.anxiety_level <= 4.0 ? 'Medium' : 'High'
                    : 'N/A'}
                </p>
                {areaProfile.wellbeing_details.anxiety_level !== undefined && (
                  <p className="text-xs text-gray-500 mt-1">
                    {areaProfile.wellbeing_details.anxiety_level.toFixed(1)}/10 (lower is better)
                  </p>
                )}
              </div>
            </div>
            
            {areaProfile.wellbeing_details.wellbeing_highlights && areaProfile.wellbeing_details.wellbeing_highlights.length > 0 && (
              <div className="space-y-2 mb-4">
                {areaProfile.wellbeing_details.wellbeing_highlights.map((highlight, idx) => (
                  <div key={idx} className="flex items-start gap-2">
                    <span className="text-green-500 mt-0.5">✅</span>
                    <span className="text-sm text-gray-700">{highlight}</span>
                  </div>
                ))}
              </div>
            )}
            
            <button
              onClick={() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })}
              className="flex items-center gap-2 text-xs text-blue-600 hover:text-blue-700 transition-colors"
            >
              <span>💡 See detailed wellbeing analysis in Professional Report</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        )}
        
        {/* Demographics Snapshot (existing, enhanced) */}
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

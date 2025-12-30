/**
 * Neighbourhood Section for Free Report
 * Displays ONS data (demographics, wellbeing, economic) for the user's area
 * Similar to the Neighbourhood tab but adapted for the Free Report context
 */
import { useState, useEffect } from 'react';
import {
  MapPin,
  Users,
  Heart,
  TrendingUp,
  TrendingDown,
  Minus,
  Smile,
  Frown,
  BarChart3,
  Info,
  Loader2,
  AlertCircle,
  Star,
  ArrowRight
} from 'lucide-react';
import axios from 'axios';

interface ONSData {
  postcode: string;
  geography?: {
    local_authority: string;
    region: string;
    lsoa_name: string;
  };
  wellbeing?: {
    social_wellbeing_index?: {
      score: number;
      rating: string;
      percentile: number;
    };
    indicators?: {
      happiness?: { value: number; national_average: number; vs_national: string };
      life_satisfaction?: { value: number; national_average: number; vs_national: string };
      anxiety?: { value: number; national_average: number; vs_national: string };
      worthwhile?: { value: number; national_average: number; vs_national: string };
    };
  };
  economic?: {
    economic_stability_index?: {
      score: number;
      rating: string;
      factors: string[];
    };
    indicators?: {
      employment_rate?: { value: number; trend: string };
      median_income?: { value: number; trend: string };
      imd_decile?: { value: number; interpretation: string };
    };
  };
  demographics?: {
    population?: {
      total: number;
      density_per_km2: number;
    };
    elderly_care_context?: {
      over_65_percent: number;
      over_80_percent: number;
      elderly_population_trend: string;
      projected_over_65_2030: number;
      care_home_demand_indicator: string;
    };
    age_structure?: {
      under_18?: { percent: number };
      '18_to_64'?: { percent: number };
      '65_to_79'?: { percent: number };
      '80_plus'?: { percent: number };
    };
  };
  summary?: {
    area_name: string;
    region: string;
    social_wellbeing_score: number;
    economic_stability_score: number;
    elderly_population_percent: number;
    overall_rating: string;
  };
  error?: string;
}

interface NeighbourhoodSectionProps {
  postcode: string;
  className?: string;
}

export function NeighbourhoodSection({ postcode, className = '' }: NeighbourhoodSectionProps) {
  const [onsData, setOnsData] = useState<ONSData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchONSData = async () => {
      if (!postcode) {
        setError('No postcode provided');
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response = await axios.get(
          `/api/neighbourhood/analyze/${encodeURIComponent(postcode)}?include_ons=true&include_os_places=false&include_osm=false&include_nhsbsa=false`
        );
        
        if (response.data?.ons) {
          setOnsData(response.data.ons);
        } else {
          setError('ONS data not available for this area');
        }
      } catch (err: any) {
        console.error('Error fetching ONS data:', err);
        setError(err.response?.data?.detail || 'Failed to load neighbourhood data');
      } finally {
        setLoading(false);
      }
    };

    fetchONSData();
  }, [postcode]);

  if (loading) {
    return (
      <div className={`bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden ${className}`}>
        <div className="bg-gradient-to-r from-[#1E2A44] to-[#2D3E5F] px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/10 rounded-lg">
              <MapPin className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Neighbourhood Analysis</h2>
              <p className="text-gray-300 text-sm">Loading ONS data for {postcode}...</p>
            </div>
          </div>
        </div>
        <div className="p-12 flex flex-col items-center justify-center">
          <Loader2 className="w-8 h-8 text-blue-500 animate-spin mb-4" />
          <p className="text-gray-600">Fetching neighbourhood statistics...</p>
        </div>
      </div>
    );
  }

  if (error || !onsData) {
    return (
      <div className={`bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden ${className}`}>
        <div className="bg-gradient-to-r from-[#1E2A44] to-[#2D3E5F] px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/10 rounded-lg">
              <MapPin className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Neighbourhood Analysis</h2>
              <p className="text-gray-300 text-sm">Area profile for {postcode}</p>
            </div>
          </div>
        </div>
        <div className="p-6">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-yellow-800 font-medium">Neighbourhood data temporarily unavailable</p>
              <p className="text-yellow-700 text-sm mt-1">{error || 'Please try again later'}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const summary = onsData.summary;
  const wellbeing = onsData.wellbeing;
  const economic = onsData.economic;
  const demographics = onsData.demographics;
  const geography = onsData.geography;

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
              Neighbourhood: {summary?.area_name || geography?.local_authority || postcode}
            </h2>
            <p className="text-gray-300 text-sm">
              {geography?.region || 'UK'} • ONS Statistics
            </p>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <ScoreCard
              title="Social Wellbeing"
              score={summary.social_wellbeing_score}
              maxScore={100}
              color="purple"
            />
            <ScoreCard
              title="Economic Stability"
              score={summary.economic_stability_score}
              maxScore={100}
              color="green"
            />
            <ScoreCard
              title="Over 65 Population"
              score={summary.elderly_population_percent}
              suffix="%"
              color="blue"
            />
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-600 mb-1">Overall Rating</div>
              <div className={`text-xl font-bold ${getRatingColor(summary.overall_rating)}`}>
                {summary.overall_rating || 'N/A'}
              </div>
              <div className="flex items-center gap-1 mt-1">
                {Array.from({ length: 5 }).map((_, i) => {
                  const stars = summary.overall_rating === 'Excellent' ? 5 :
                               summary.overall_rating === 'Good' ? 4 :
                               summary.overall_rating === 'Average' ? 3 : 2;
                  return (
                    <Star
                      key={i}
                      className={`w-3 h-3 ${
                        i < stars ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
                      }`}
                    />
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Demographics Section */}
        {demographics && (
          <div className="bg-white border rounded-xl p-5">
            <h4 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <Users className="w-5 h-5 text-blue-500" />
              Demographics & Elderly Care Context
            </h4>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              {demographics.population && (
                <>
                  <div className="bg-blue-50 rounded-lg p-3">
                    <div className="text-xs text-blue-600">Total Population</div>
                    <div className="text-lg font-bold">{demographics.population.total?.toLocaleString()}</div>
                  </div>
                  <div className="bg-blue-50 rounded-lg p-3">
                    <div className="text-xs text-blue-600">Density</div>
                    <div className="text-lg font-bold">{demographics.population.density_per_km2?.toLocaleString()}/km²</div>
                  </div>
                </>
              )}
              {demographics.elderly_care_context && (
                <>
                  <div className="bg-orange-50 rounded-lg p-3">
                    <div className="text-xs text-orange-600">Over 65</div>
                    <div className="text-lg font-bold">{demographics.elderly_care_context.over_65_percent}%</div>
                  </div>
                  <div className="bg-orange-50 rounded-lg p-3">
                    <div className="text-xs text-orange-600">Over 80</div>
                    <div className="text-lg font-bold">{demographics.elderly_care_context.over_80_percent}%</div>
                  </div>
                </>
              )}
            </div>

            {/* Age Structure Bar */}
            {demographics.age_structure && (
              <div className="mb-4">
                <div className="text-sm text-gray-600 mb-2">Age Structure</div>
                <div className="flex h-6 rounded-full overflow-hidden">
                  <div 
                    className="bg-green-400" 
                    style={{ width: `${demographics.age_structure.under_18?.percent || 0}%` }}
                    title={`Under 18: ${demographics.age_structure.under_18?.percent}%`}
                  />
                  <div 
                    className="bg-blue-400" 
                    style={{ width: `${demographics.age_structure['18_to_64']?.percent || 0}%` }}
                    title={`18-64: ${demographics.age_structure['18_to_64']?.percent}%`}
                  />
                  <div 
                    className="bg-orange-400" 
                    style={{ width: `${demographics.age_structure['65_to_79']?.percent || 0}%` }}
                    title={`65-79: ${demographics.age_structure['65_to_79']?.percent}%`}
                  />
                  <div 
                    className="bg-red-400" 
                    style={{ width: `${demographics.age_structure['80_plus']?.percent || 0}%` }}
                    title={`80+: ${demographics.age_structure['80_plus']?.percent}%`}
                  />
                </div>
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Under 18 ({demographics.age_structure.under_18?.percent}%)</span>
                  <span>18-64 ({demographics.age_structure['18_to_64']?.percent}%)</span>
                  <span>65-79 ({demographics.age_structure['65_to_79']?.percent}%)</span>
                  <span>80+ ({demographics.age_structure['80_plus']?.percent}%)</span>
                </div>
              </div>
            )}

            {/* Care Home Demand Context */}
            {demographics.elderly_care_context && (
              <div className="bg-orange-50 rounded-lg p-4">
                <div className="text-sm font-medium text-orange-800 mb-2">Care Home Demand Context</div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                  <div>
                    <div className="text-orange-600">Elderly Trend</div>
                    <div className="font-medium flex items-center gap-1">
                      <TrendIndicator trend={demographics.elderly_care_context.elderly_population_trend} />
                      {demographics.elderly_care_context.elderly_population_trend}
                    </div>
                  </div>
                  <div>
                    <div className="text-orange-600">Projected 65+ (2030)</div>
                    <div className="font-medium">{demographics.elderly_care_context.projected_over_65_2030}%</div>
                  </div>
                  <div>
                    <div className="text-orange-600">Demand Indicator</div>
                    <div className="font-medium capitalize">{demographics.elderly_care_context.care_home_demand_indicator}</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Wellbeing Section */}
        {wellbeing && wellbeing.social_wellbeing_index && (
          <div className="bg-white border rounded-xl p-5">
            <h4 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <Heart className="w-5 h-5 text-pink-500" />
              Quality of Life Indicators
            </h4>
            
            {/* Wellbeing Index */}
            <div className="mb-4 p-4 bg-pink-50 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-sm text-pink-800">Social Wellbeing Index</span>
                <div className="flex items-center gap-2">
                  <span className="text-2xl font-bold text-pink-600">
                    {wellbeing.social_wellbeing_index.score}
                  </span>
                  <span className="px-2 py-0.5 text-xs rounded-full bg-pink-200 text-pink-800">
                    {wellbeing.social_wellbeing_index.rating}
                  </span>
                </div>
              </div>
              <div className="mt-2 text-xs text-pink-600">
                Percentile: {wellbeing.social_wellbeing_index.percentile}th
              </div>
            </div>
            
            {/* Individual Indicators */}
            {wellbeing.indicators && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {wellbeing.indicators.happiness && (
                  <IndicatorCard
                    icon={<Smile className="w-4 h-4 text-yellow-500" />}
                    label="Happiness"
                    value={wellbeing.indicators.happiness.value}
                    maxValue={10}
                    vsNational={wellbeing.indicators.happiness.vs_national}
                  />
                )}
                {wellbeing.indicators.life_satisfaction && (
                  <IndicatorCard
                    icon={<Heart className="w-4 h-4 text-red-500" />}
                    label="Life Satisfaction"
                    value={wellbeing.indicators.life_satisfaction.value}
                    maxValue={10}
                    vsNational={wellbeing.indicators.life_satisfaction.vs_national}
                  />
                )}
                {wellbeing.indicators.anxiety && (
                  <IndicatorCard
                    icon={<Frown className="w-4 h-4 text-blue-500" />}
                    label="Anxiety (lower is better)"
                    value={wellbeing.indicators.anxiety.value}
                    maxValue={10}
                    vsNational={wellbeing.indicators.anxiety.vs_national}
                    inverse
                  />
                )}
                {wellbeing.indicators.worthwhile && (
                  <IndicatorCard
                    icon={<TrendingUp className="w-4 h-4 text-green-500" />}
                    label="Worthwhile"
                    value={wellbeing.indicators.worthwhile.value}
                    maxValue={10}
                    vsNational={wellbeing.indicators.worthwhile.vs_national}
                  />
                )}
              </div>
            )}
          </div>
        )}

        {/* Upgrade CTA */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-5 border border-blue-100">
          <div className="flex items-start gap-4">
            <div className="p-2 bg-blue-100 rounded-lg">
              <BarChart3 className="w-6 h-6 text-blue-600" />
            </div>
            <div className="flex-1">
              <h4 className="font-semibold text-gray-900 mb-1">Want more detailed analysis?</h4>
              <p className="text-sm text-gray-600 mb-3">
                Our Professional Report includes walkability scores, healthcare access, amenities analysis, and environmental data.
              </p>
              <button
                onClick={() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
              >
                <span>View Professional Report</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Data Source Note */}
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <Info className="w-3 h-3" />
          Data source: Office for National Statistics (ONS)
        </div>
      </div>
    </div>
  );
}

// Helper Components

function ScoreCard({ 
  title, 
  score, 
  maxScore, 
  suffix = '', 
  color 
}: { 
  title: string; 
  score?: number; 
  maxScore?: number;
  suffix?: string;
  color: string;
}) {
  const colorClasses: Record<string, string> = {
    purple: 'bg-purple-50 text-purple-600',
    green: 'bg-green-50 text-green-600',
    blue: 'bg-blue-50 text-blue-600',
  };
  
  return (
    <div className={`rounded-lg p-4 ${colorClasses[color] || 'bg-gray-50'}`}>
      <div className="text-sm mb-1">{title}</div>
      <div className="text-2xl font-bold">
        {score !== undefined && score !== null ? `${Math.round(score)}${suffix}` : 'N/A'}
        {maxScore && score !== undefined && <span className="text-sm font-normal">/{maxScore}</span>}
      </div>
    </div>
  );
}

function IndicatorCard({
  icon,
  label,
  value,
  maxValue,
  vsNational,
  inverse = false
}: {
  icon: React.ReactNode;
  label: string;
  value?: number;
  maxValue: number;
  vsNational?: string;
  inverse?: boolean;
}) {
  const percentage = value !== undefined ? (value / maxValue) * 100 : 0;
  
  return (
    <div className="bg-gray-50 rounded-lg p-3">
      <div className="flex items-center gap-2 text-xs text-gray-600 mb-1">
        {icon}
        <span className="truncate">{label}</span>
      </div>
      <div className="text-lg font-bold">{value?.toFixed(1) ?? '-'}/{maxValue}</div>
      <div className="mt-1 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div 
          className={`h-full ${inverse ? 'bg-red-400' : 'bg-green-400'}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {vsNational && (
        <div className={`text-xs mt-1 ${vsNational.startsWith('+') ? 'text-green-600' : vsNational.startsWith('-') ? 'text-red-600' : 'text-gray-500'}`}>
          vs national: {vsNational}
        </div>
      )}
    </div>
  );
}

function TrendIndicator({ trend }: { trend?: string }) {
  if (!trend) return null;
  
  const icons: Record<string, React.ReactNode> = {
    increasing: <TrendingUp className="w-3 h-3 text-green-500" />,
    decreasing: <TrendingDown className="w-3 h-3 text-red-500" />,
    stable: <Minus className="w-3 h-3 text-gray-500" />,
  };
  
  return icons[trend.toLowerCase()] || null;
}

function getRatingColor(rating?: string): string {
  if (!rating) return 'text-gray-600';
  const lower = rating.toLowerCase();
  if (lower === 'excellent') return 'text-green-600';
  if (lower === 'good') return 'text-blue-600';
  if (lower === 'average') return 'text-yellow-600';
  return 'text-red-600';
}

export default NeighbourhoodSection;

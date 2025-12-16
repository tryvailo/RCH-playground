import { 
  BarChart3, 
  MapPin, 
  Users, 
  TrendingUp, 
  TrendingDown,
  Minus,
  Heart,
  Smile,
  Frown,
  DollarSign,
  Clock,
  Info
} from 'lucide-react';
import type { ONSFullProfile } from '../types';

interface Props {
  data: ONSFullProfile;
}

export default function ONSResults({ data }: Props) {
  if (data.error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-800">Error: {data.error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Geography Section */}
      <GeographySection geography={data.geography} />
      
      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <ScoreCard
          title="Social Wellbeing"
          score={data.summary?.social_wellbeing_score}
          maxScore={100}
          color="purple"
        />
        <ScoreCard
          title="Economic Stability"
          score={data.summary?.economic_stability_score}
          maxScore={100}
          color="green"
        />
        <ScoreCard
          title="Over 65 Population"
          score={data.summary?.elderly_population_percent}
          suffix="%"
          color="blue"
        />
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-sm text-gray-600 mb-1">Overall Rating</div>
          <div className={`text-xl font-bold ${getRatingColor(data.summary?.overall_rating)}`}>
            {data.summary?.overall_rating || 'N/A'}
          </div>
        </div>
      </div>

      {/* Wellbeing Section */}
      {data.wellbeing && <WellbeingSection wellbeing={data.wellbeing} />}
      
      {/* Economic Section */}
      {data.economic && <EconomicSection economic={data.economic} />}
      
      {/* Demographics Section */}
      {data.demographics && <DemographicsSection demographics={data.demographics} />}

      {/* Metadata */}
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <Clock className="w-4 h-4" />
        Fetched: {new Date(data.fetched_at).toLocaleString()}
      </div>
    </div>
  );
}

function GeographySection({ geography }: { geography: ONSFullProfile['geography'] }) {
  return (
    <div className="bg-purple-50 rounded-lg p-4">
      <h4 className="font-medium text-purple-800 mb-3 flex items-center gap-2">
        <MapPin className="w-4 h-4" />
        Geography
      </h4>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        <div>
          <div className="text-purple-600">LSOA Code</div>
          <div className="font-mono">{geography?.lsoa_code || '-'}</div>
        </div>
        <div>
          <div className="text-purple-600">LSOA Name</div>
          <div>{geography?.lsoa_name || '-'}</div>
        </div>
        <div>
          <div className="text-purple-600">Local Authority</div>
          <div>{geography?.local_authority || '-'}</div>
        </div>
        <div>
          <div className="text-purple-600">Region</div>
          <div>{geography?.region || '-'}</div>
        </div>
        <div>
          <div className="text-purple-600">MSOA Code</div>
          <div className="font-mono">{geography?.msoa_code || '-'}</div>
        </div>
        <div>
          <div className="text-purple-600">MSOA Name</div>
          <div>{geography?.msoa_name || '-'}</div>
        </div>
        <div>
          <div className="text-purple-600">Country</div>
          <div>{geography?.country || '-'}</div>
        </div>
        <div>
          <div className="text-purple-600">IMD Rank</div>
          <div>{geography?.imd_rank || '-'}</div>
        </div>
      </div>
    </div>
  );
}

function WellbeingSection({ wellbeing }: { wellbeing: ONSFullProfile['wellbeing'] }) {
  const indicators = wellbeing.indicators;
  
  return (
    <div className="bg-white border rounded-lg p-4">
      <h4 className="font-medium text-gray-800 mb-4 flex items-center gap-2">
        <Heart className="w-4 h-4 text-pink-500" />
        Wellbeing Indicators
        <span className="text-xs font-normal text-gray-500">({wellbeing.period})</span>
      </h4>
      
      {/* Wellbeing Index */}
      <div className="mb-4 p-3 bg-pink-50 rounded-lg">
        <div className="flex items-center justify-between">
          <span className="text-sm text-pink-800">Social Wellbeing Index</span>
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold text-pink-600">
              {wellbeing.social_wellbeing_index?.score}
            </span>
            <span className="px-2 py-0.5 text-xs rounded-full bg-pink-200 text-pink-800">
              {wellbeing.social_wellbeing_index?.rating}
            </span>
          </div>
        </div>
        <div className="mt-2 text-xs text-pink-600">
          Percentile: {wellbeing.social_wellbeing_index?.percentile}th
        </div>
      </div>
      
      {/* Individual Indicators */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <IndicatorCard
          icon={<Smile className="w-4 h-4 text-yellow-500" />}
          label="Happiness"
          value={indicators?.happiness?.value}
          maxValue={10}
          national={indicators?.happiness?.national_average}
          vsNational={indicators?.happiness?.vs_national}
        />
        <IndicatorCard
          icon={<Heart className="w-4 h-4 text-red-500" />}
          label="Life Satisfaction"
          value={indicators?.life_satisfaction?.value}
          maxValue={10}
          national={indicators?.life_satisfaction?.national_average}
          vsNational={indicators?.life_satisfaction?.vs_national}
        />
        <IndicatorCard
          icon={<Frown className="w-4 h-4 text-blue-500" />}
          label="Anxiety (lower is better)"
          value={indicators?.anxiety?.value}
          maxValue={10}
          national={indicators?.anxiety?.national_average}
          vsNational={indicators?.anxiety?.vs_national}
          inverse
        />
        <IndicatorCard
          icon={<TrendingUp className="w-4 h-4 text-green-500" />}
          label="Worthwhile"
          value={indicators?.worthwhile?.value}
          maxValue={10}
          national={indicators?.worthwhile?.national_average}
          vsNational={indicators?.worthwhile?.vs_national}
        />
      </div>
      
      <div className="mt-3 text-xs text-gray-500 flex items-center gap-1">
        <Info className="w-3 h-3" />
        Source: {wellbeing.source} ({wellbeing.methodology})
      </div>
    </div>
  );
}

function EconomicSection({ economic }: { economic: ONSFullProfile['economic'] }) {
  const indicators = economic.indicators;
  
  return (
    <div className="bg-white border rounded-lg p-4">
      <h4 className="font-medium text-gray-800 mb-4 flex items-center gap-2">
        <DollarSign className="w-4 h-4 text-green-500" />
        Economic Profile
        <span className="text-xs font-normal text-gray-500">({economic.period})</span>
      </h4>
      
      {/* Economic Stability Index */}
      <div className="mb-4 p-3 bg-green-50 rounded-lg">
        <div className="flex items-center justify-between">
          <span className="text-sm text-green-800">Economic Stability Index</span>
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold text-green-600">
              {economic.economic_stability_index?.score}
            </span>
            <span className="px-2 py-0.5 text-xs rounded-full bg-green-200 text-green-800">
              {economic.economic_stability_index?.rating}
            </span>
          </div>
        </div>
        {economic.economic_stability_index?.factors && (
          <ul className="mt-2 text-xs text-green-700 space-y-1">
            {economic.economic_stability_index.factors.map((factor, i) => (
              <li key={i}>• {factor}</li>
            ))}
          </ul>
        )}
      </div>
      
      {/* Economic Indicators */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-50 rounded p-3">
          <div className="text-xs text-gray-500">Employment Rate</div>
          <div className="text-lg font-bold">{indicators?.employment_rate?.value}%</div>
          <TrendIndicator trend={indicators?.employment_rate?.trend} />
        </div>
        <div className="bg-gray-50 rounded p-3">
          <div className="text-xs text-gray-500">Median Income</div>
          <div className="text-lg font-bold">£{indicators?.median_income?.value?.toLocaleString()}</div>
          <TrendIndicator trend={indicators?.median_income?.trend} />
        </div>
        <div className="bg-gray-50 rounded p-3">
          <div className="text-xs text-gray-500">IMD Decile</div>
          <div className="text-lg font-bold">{indicators?.imd_decile?.value}/10</div>
          <div className="text-xs text-gray-500">{indicators?.imd_decile?.interpretation}</div>
        </div>
        <div className="bg-gray-50 rounded p-3">
          <div className="text-xs text-gray-500">Economic Activity</div>
          <div className="text-lg font-bold">{indicators?.economic_activity_rate?.value}%</div>
        </div>
      </div>
    </div>
  );
}

function DemographicsSection({ demographics }: { demographics: ONSFullProfile['demographics'] }) {
  return (
    <div className="bg-white border rounded-lg p-4">
      <h4 className="font-medium text-gray-800 mb-4 flex items-center gap-2">
        <Users className="w-4 h-4 text-blue-500" />
        Demographics
      </h4>
      
      {/* Population Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div className="bg-blue-50 rounded p-3">
          <div className="text-xs text-blue-600">Total Population</div>
          <div className="text-lg font-bold">{demographics.population?.total?.toLocaleString()}</div>
        </div>
        <div className="bg-blue-50 rounded p-3">
          <div className="text-xs text-blue-600">Density</div>
          <div className="text-lg font-bold">{demographics.population?.density_per_km2?.toLocaleString()}/km²</div>
        </div>
        <div className="bg-orange-50 rounded p-3">
          <div className="text-xs text-orange-600">Over 65</div>
          <div className="text-lg font-bold">{demographics.elderly_care_context?.over_65_percent}%</div>
        </div>
        <div className="bg-orange-50 rounded p-3">
          <div className="text-xs text-orange-600">Over 80</div>
          <div className="text-lg font-bold">{demographics.elderly_care_context?.over_80_percent}%</div>
        </div>
      </div>
      
      {/* Age Structure Bar */}
      <div className="mb-4">
        <div className="text-sm text-gray-600 mb-2">Age Structure</div>
        <div className="flex h-6 rounded-full overflow-hidden">
          <div 
            className="bg-green-400" 
            style={{ width: `${demographics.age_structure?.under_18?.percent}%` }}
            title={`Under 18: ${demographics.age_structure?.under_18?.percent}%`}
          />
          <div 
            className="bg-blue-400" 
            style={{ width: `${demographics.age_structure?.['18_to_64']?.percent}%` }}
            title={`18-64: ${demographics.age_structure?.['18_to_64']?.percent}%`}
          />
          <div 
            className="bg-orange-400" 
            style={{ width: `${demographics.age_structure?.['65_to_79']?.percent}%` }}
            title={`65-79: ${demographics.age_structure?.['65_to_79']?.percent}%`}
          />
          <div 
            className="bg-red-400" 
            style={{ width: `${demographics.age_structure?.['80_plus']?.percent}%` }}
            title={`80+: ${demographics.age_structure?.['80_plus']?.percent}%`}
          />
        </div>
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>Under 18 ({demographics.age_structure?.under_18?.percent}%)</span>
          <span>18-64 ({demographics.age_structure?.['18_to_64']?.percent}%)</span>
          <span>65-79 ({demographics.age_structure?.['65_to_79']?.percent}%)</span>
          <span>80+ ({demographics.age_structure?.['80_plus']?.percent}%)</span>
        </div>
      </div>
      
      {/* Care Home Context */}
      <div className="bg-orange-50 rounded-lg p-3">
        <div className="text-sm font-medium text-orange-800 mb-2">Care Home Demand Context</div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
          <div>
            <div className="text-orange-600">Elderly Trend</div>
            <div className="font-medium">{demographics.elderly_care_context?.elderly_population_trend}</div>
          </div>
          <div>
            <div className="text-orange-600">Projected 65+ (2030)</div>
            <div className="font-medium">{demographics.elderly_care_context?.projected_over_65_2030}%</div>
          </div>
          <div>
            <div className="text-orange-600">Single Over 65</div>
            <div className="font-medium">{demographics.household_composition?.single_person_over_65?.percent}%</div>
          </div>
          <div>
            <div className="text-orange-600">Demand Indicator</div>
            <div className="font-medium capitalize">{demographics.elderly_care_context?.care_home_demand_indicator}</div>
          </div>
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
        {score !== undefined ? `${score}${suffix}` : 'N/A'}
        {maxScore && <span className="text-sm font-normal">/{maxScore}</span>}
      </div>
    </div>
  );
}

function IndicatorCard({
  icon,
  label,
  value,
  maxValue,
  national,
  vsNational,
  inverse = false
}: {
  icon: React.ReactNode;
  label: string;
  value?: number;
  maxValue: number;
  national?: number;
  vsNational?: string;
  inverse?: boolean;
}) {
  const percentage = value !== undefined ? (value / maxValue) * 100 : 0;
  
  return (
    <div className="bg-gray-50 rounded p-3">
      <div className="flex items-center gap-2 text-xs text-gray-600 mb-1">
        {icon}
        {label}
      </div>
      <div className="text-lg font-bold">{value ?? '-'}/{maxValue}</div>
      <div className="mt-1 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div 
          className={`h-full ${inverse ? 'bg-red-400' : 'bg-green-400'}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {vsNational && (
        <div className={`text-xs mt-1 ${vsNational.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
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
  
  return (
    <div className="flex items-center gap-1 text-xs text-gray-500 mt-1">
      {icons[trend] || null}
      <span className="capitalize">{trend}</span>
    </div>
  );
}

function getRatingColor(rating?: string): string {
  if (!rating) return 'text-gray-600';
  const lower = rating.toLowerCase();
  if (lower === 'excellent') return 'text-green-600';
  if (lower === 'good') return 'text-blue-600';
  if (lower === 'average') return 'text-yellow-600';
  return 'text-red-600';
}

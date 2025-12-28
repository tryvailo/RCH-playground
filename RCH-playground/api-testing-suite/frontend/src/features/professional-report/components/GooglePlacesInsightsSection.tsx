import { Clock, TrendingUp, Users, MapPin, Activity, Star } from 'lucide-react';
import type { ProfessionalCareHome } from '../types';

interface GooglePlacesInsightsSectionProps {
  home: ProfessionalCareHome;
}

export default function GooglePlacesInsightsSection({ home }: GooglePlacesInsightsSectionProps) {
  // Get insights data from various possible locations
  const insights = home.insights || home.googlePlaces?.insights;
  const dwellTime = home.average_dwell_time_minutes || insights?.dwell_time?.average_dwell_time_minutes;
  const repeatVisitorRate = home.repeat_visitor_rate || insights?.repeat_visitor_rate?.repeat_visitor_rate_percent;
  const footfallTrend = home.footfall_trend || insights?.footfall_trends?.trend_direction;
  const popularTimes = home.popular_times || insights?.popular_times;
  const familyEngagementScore = home.family_engagement_score || insights?.summary?.family_engagement_score;
  const qualityIndicator = home.quality_indicator || insights?.summary?.quality_indicator;

  // Check if we have any data to display
  const hasData = dwellTime !== null && dwellTime !== undefined ||
                  repeatVisitorRate !== null && repeatVisitorRate !== undefined ||
                  footfallTrend !== null && footfallTrend !== undefined ||
                  familyEngagementScore !== null && familyEngagementScore !== undefined ||
                  qualityIndicator !== null && qualityIndicator !== undefined;

  if (!hasData) {
    return (
      <div className="glass-card rounded-2xl p-8 border border-gray-100 text-center text-xs text-gray-400 italic">
        Google Places New API insights data not available for this care home.
      </div>
    );
  }

  const getFootfallTrendColor = (trend: string | null | undefined) => {
    if (!trend) return 'text-gray-500';
    switch (trend.toLowerCase()) {
      case 'growing':
        return 'text-emerald-600';
      case 'stable':
        return 'text-amber-600';
      case 'declining':
        return 'text-rose-600';
      default:
        return 'text-gray-500';
    }
  };

  const getFootfallTrendIcon = (trend: string | null | undefined) => {
    if (!trend) return null;
    switch (trend.toLowerCase()) {
      case 'growing':
        return <TrendingUp className="w-4 h-4 text-emerald-600" />;
      case 'stable':
        return <Activity className="w-4 h-4 text-amber-600" />;
      case 'declining':
        return <TrendingUp className="w-4 h-4 text-rose-600 rotate-180" />;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-2 px-2">
        <div>
          <h5 className="text-sm font-bold text-[#1E2A44] uppercase tracking-wider">
            Google Places New API - Behavioral Insights
          </h5>
          <p className="text-[10px] text-gray-400 font-medium">Visitor behavior and family engagement analytics for {home.name}</p>
        </div>
        <div className="flex gap-2 mt-2 md:mt-0">
          <div className="flex items-center gap-1.5 px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-[10px] font-bold border border-blue-100">
            <Activity className="w-3 h-3" /> Real-time Analytics
          </div>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Dwell Time Card */}
        {dwellTime !== null && dwellTime !== undefined && (
          <div className="glass-card rounded-2xl p-5 border border-blue-100/50 bg-gradient-to-br from-blue-50/30 to-transparent shadow-sm hover:shadow-md transition-all">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-blue-100 rounded-xl text-blue-600">
                <Clock className="w-4 h-4" />
              </div>
              <span className="text-[10px] font-bold text-blue-400 tracking-widest uppercase">Dwell Time</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-black text-[#1E2A44]">
                {Math.round(dwellTime)}
              </span>
              <span className="text-sm font-bold text-gray-300">min</span>
            </div>
            <div className="mt-2 text-[10px] font-semibold text-blue-600/70">
              {insights?.dwell_time?.interpretation || 'Average visit duration'}
            </div>
          </div>
        )}

        {/* Repeat Visitor Rate Card */}
        {repeatVisitorRate !== null && repeatVisitorRate !== undefined && (
          <div className="glass-card rounded-2xl p-5 border border-purple-100/50 bg-gradient-to-br from-purple-50/30 to-transparent shadow-sm hover:shadow-md transition-all">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-purple-100 rounded-xl text-purple-600">
                <Users className="w-4 h-4" />
              </div>
              <span className="text-[10px] font-bold text-purple-400 tracking-widest uppercase">Repeat Visitors</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-black text-[#1E2A44]">
                {typeof repeatVisitorRate === 'number' 
                  ? (repeatVisitorRate > 1 ? Math.round(repeatVisitorRate) : Math.round(repeatVisitorRate * 100))
                  : 'N/A'}
              </span>
              <span className="text-sm font-bold text-gray-300">
                {typeof repeatVisitorRate === 'number' && repeatVisitorRate <= 1 ? '%' : ''}
              </span>
            </div>
            <div className="mt-2 text-[10px] font-semibold text-purple-600/70">
              {insights?.repeat_visitor_rate?.interpretation || 'Family loyalty indicator'}
            </div>
          </div>
        )}

        {/* Footfall Trend Card */}
        {footfallTrend && (
          <div className={`glass-card rounded-2xl p-5 border shadow-sm hover:shadow-md transition-all ${
            footfallTrend === 'growing' ? 'border-emerald-100/50 bg-gradient-to-br from-emerald-50/30' :
            footfallTrend === 'stable' ? 'border-amber-100/50 bg-gradient-to-br from-amber-50/30' :
            'border-rose-100/50 bg-gradient-to-br from-rose-50/30'
          } to-transparent`}>
            <div className="flex items-center justify-between mb-4">
              <div className={`p-2 rounded-xl ${
                footfallTrend === 'growing' ? 'bg-emerald-100 text-emerald-600' :
                footfallTrend === 'stable' ? 'bg-amber-100 text-amber-600' :
                'bg-rose-100 text-rose-600'
              }`}>
                {getFootfallTrendIcon(footfallTrend) || <Activity className="w-4 h-4" />}
              </div>
              <span className={`text-[10px] font-bold tracking-widest uppercase ${
                footfallTrend === 'growing' ? 'text-emerald-500' :
                footfallTrend === 'stable' ? 'text-amber-500' :
                'text-rose-500'
              }`}>Footfall</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-black text-[#1E2A44] capitalize">
                {footfallTrend}
              </span>
            </div>
            <div className="mt-2 text-[10px] font-semibold text-gray-400">
              {insights?.footfall_trends?.interpretation || 'Visitor trend analysis'}
            </div>
          </div>
        )}

        {/* Family Engagement Score Card */}
        {familyEngagementScore !== null && familyEngagementScore !== undefined && (
          <div className="glass-card rounded-2xl p-5 border border-indigo-100/50 bg-gradient-to-br from-indigo-50/30 to-transparent shadow-sm hover:shadow-md transition-all">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-indigo-100 rounded-xl text-indigo-600">
                <Star className="w-4 h-4 fill-indigo-600" />
              </div>
              <span className="text-[10px] font-bold text-indigo-400 tracking-widest uppercase">Engagement</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-black text-[#1E2A44]">
                {Math.round(familyEngagementScore)}
              </span>
              <span className="text-sm font-bold text-gray-300">/100</span>
            </div>
            <div className="mt-2 text-[10px] font-semibold text-indigo-600/70">Family engagement score</div>
          </div>
        )}
      </div>

      {/* Additional Insights */}
      {(qualityIndicator || insights?.summary?.recommendations) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Quality Indicator */}
          {qualityIndicator && (
            <div className="glass-card rounded-3xl p-6 border border-gray-50">
              <div className="flex items-center justify-between mb-6">
                <h6 className="text-[10px] font-bold text-gray-400 uppercase tracking-[0.2em]">Quality Indicator</h6>
                <MapPin className="w-4 h-4 text-gray-200" />
              </div>
              <div className="p-4 bg-white/40 border border-white/60 rounded-2xl">
                <p className="text-sm font-semibold text-[#1E2A44]">{qualityIndicator}</p>
              </div>
            </div>
          )}

          {/* Recommendations */}
          {insights?.summary?.recommendations && insights.summary.recommendations.length > 0 && (
            <div className="glass-card rounded-3xl p-6 border border-gray-50">
              <div className="flex items-center justify-between mb-6">
                <h6 className="text-[10px] font-bold text-gray-400 uppercase tracking-[0.2em]">Insights</h6>
                <Activity className="w-4 h-4 text-gray-200" />
              </div>
              <div className="space-y-3">
                {insights.summary.recommendations.map((rec, idx) => (
                  <div key={idx} className="p-3 bg-white/40 border border-white/60 rounded-xl text-xs text-gray-700">
                    • {rec}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Visitor Geography */}
      {insights?.visitor_geography && (
        <div className="glass-card rounded-3xl p-6 border border-gray-50">
          <div className="flex items-center justify-between mb-6">
            <h6 className="text-[10px] font-bold text-gray-400 uppercase tracking-[0.2em]">Visitor Geography</h6>
            <MapPin className="w-4 h-4 text-gray-200" />
          </div>
          <div className="grid grid-cols-3 gap-4">
            {insights.visitor_geography.local_percent !== undefined && (
              <div className="text-center p-3 bg-white/40 rounded-xl border border-white/60">
                <div className="text-2xl font-black text-[#1E2A44]">
                  {Math.round(insights.visitor_geography.local_percent)}%
                </div>
                <div className="text-[10px] font-semibold text-gray-600 mt-1">Local</div>
              </div>
            )}
            {insights.visitor_geography.regional_percent !== undefined && (
              <div className="text-center p-3 bg-white/40 rounded-xl border border-white/60">
                <div className="text-2xl font-black text-[#1E2A44]">
                  {Math.round(insights.visitor_geography.regional_percent)}%
                </div>
                <div className="text-[10px] font-semibold text-gray-600 mt-1">Regional</div>
              </div>
            )}
            {insights.visitor_geography.national_percent !== undefined && (
              <div className="text-center p-3 bg-white/40 rounded-xl border border-white/60">
                <div className="text-2xl font-black text-[#1E2A44]">
                  {Math.round(insights.visitor_geography.national_percent)}%
                </div>
                <div className="text-[10px] font-semibold text-gray-600 mt-1">National</div>
              </div>
            )}
          </div>
          {insights.visitor_geography.interpretation && (
            <div className="mt-4 p-3 bg-gray-50/50 rounded-xl text-xs text-gray-600 italic">
              {insights.visitor_geography.interpretation}
            </div>
          )}
        </div>
      )}
    </div>
  );
}


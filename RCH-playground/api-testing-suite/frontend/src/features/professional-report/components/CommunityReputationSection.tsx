import { Star, MessageSquare, TrendingUp, Shield, Users, Activity } from 'lucide-react';
import type { ProfessionalCareHome } from '../types';

interface CommunityReputationSectionProps {
  home: ProfessionalCareHome;
}

export default function CommunityReputationSection({ home }: CommunityReputationSectionProps) {
  const reputation = home.communityReputation;

  if (!reputation) {
    return (
      <div className="glass-card rounded-2xl p-8 border border-gray-100 text-center text-xs text-gray-400 italic">
        Community reputation and sentiment intelligence data not available for this entity.
      </div>
    );
  }

  const sentimentLabel = reputation.sentiment_analysis?.sentiment_label || 'neutral';

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Reputation Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-2 px-2">
        <div>
          <h5 className="text-sm font-bold text-[#1E2A44] uppercase tracking-wider">
            Public Sentiment & Trust Audit
          </h5>
          <p className="text-[10px] text-gray-400 font-medium">Cross-platform reputation analysis for {home.name}</p>
        </div>
        <div className="flex gap-2 mt-2 md:mt-0">
          <div className="flex items-center gap-1.5 px-3 py-1 bg-purple-50 text-purple-700 rounded-full text-[10px] font-bold border border-purple-100">
            <Shield className="w-3 h-3" /> Trust Certified
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1 bg-emerald-50 text-emerald-700 rounded-full text-[10px] font-bold border border-emerald-100">
            <Activity className="w-3 h-3" /> Real-time Data
          </div>
        </div>
      </div>

      {/* Trust Score and Ratings Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Trust Score Card */}
        {reputation.trust_score !== null && reputation.trust_score !== undefined && (
          <div className="glass-card rounded-2xl p-5 border border-purple-100/50 bg-gradient-to-br from-purple-50/30 to-transparent shadow-sm hover:shadow-md transition-all">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-purple-100 rounded-xl text-purple-600">
                <Shield className="w-4 h-4" />
              </div>
              <span className="text-[10px] font-bold text-purple-400 tracking-widest uppercase">Trust Index</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-black text-[#1E2A44]">
                {reputation.trust_score.toFixed(0)}
              </span>
              <span className="text-sm font-bold text-gray-300">/100</span>
            </div>
            <div className="mt-2 text-[10px] font-semibold text-purple-600/70">Verified Aggregate</div>
          </div>
        )}

        {/* Google Rating Card */}
        {reputation.google_rating !== null && (
          <div className="glass-card rounded-2xl p-5 border border-amber-100/50 bg-gradient-to-br from-amber-50/30 to-transparent shadow-sm hover:shadow-md transition-all">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-amber-100 rounded-xl text-amber-600">
                <Star className="w-4 h-4 fill-amber-600" />
              </div>
              <span className="text-[10px] font-bold text-amber-400 tracking-widest uppercase">Google</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-black text-[#1E2A44]">
                {reputation.google_rating.toFixed(1)}
              </span>
              <span className="text-sm font-bold text-gray-300">★</span>
            </div>
            <div className="mt-2 text-[10px] font-semibold text-amber-600/70">{reputation.google_review_count} verified reviews</div>
          </div>
        )}

        {/* CareHome Card */}
        {reputation.carehome_rating != null && (
          <div className="glass-card rounded-2xl p-5 border border-blue-100/50 bg-gradient-to-br from-blue-50/30 to-transparent shadow-sm hover:shadow-md transition-all">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-blue-100 rounded-xl text-blue-600">
                <Activity className="w-4 h-4" />
              </div>
              <span className="text-[10px] font-bold text-blue-400 tracking-widest uppercase">CareHome</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-black text-[#1E2A44]">
                {reputation.carehome_rating.toFixed(1)}
              </span>
              <span className="text-sm font-bold text-gray-300">/10</span>
            </div>
            <div className="mt-2 text-[10px] font-semibold text-blue-600/70">Platform score</div>
          </div>
        )}

        {/* Overall Sentiment Card */}
        {reputation.sentiment_analysis && (
          <div className={`glass-card rounded-2xl p-5 border shadow-sm hover:shadow-md transition-all ${sentimentLabel === 'positive' ? 'border-emerald-100/50 bg-gradient-to-br from-emerald-50/30' :
            sentimentLabel === 'negative' ? 'border-rose-100/50 bg-gradient-to-br from-rose-50/30' :
              'border-amber-100/50 bg-gradient-to-br from-amber-50/30'
            } to-transparent`}>
            <div className="flex items-center justify-between mb-4">
              <div className={`p-2 rounded-xl ${sentimentLabel === 'positive' ? 'bg-emerald-100 text-emerald-600' :
                sentimentLabel === 'negative' ? 'bg-rose-100 text-rose-600' :
                  'bg-amber-100 text-amber-600'
                }`}>
                <TrendingUp className="w-4 h-4" />
              </div>
              <span className={`text-[10px] font-bold tracking-widest uppercase ${sentimentLabel === 'positive' ? 'text-emerald-500' :
                sentimentLabel === 'negative' ? 'text-rose-500' :
                  'text-amber-500'
                }`}>Sentiment</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-black text-[#1E2A44]">
                {reputation.sentiment_analysis.average_sentiment !== null && reputation.sentiment_analysis.average_sentiment !== undefined
                  ? (reputation.sentiment_analysis.average_sentiment * 100).toFixed(0)
                  : 'N/A'}%
              </span>
              <span className="text-xs font-bold text-gray-400 uppercase tracking-tighter">{sentimentLabel}</span>
            </div>
            <div className="mt-2 text-[10px] font-semibold text-gray-400 capitalize">AI analyzed voice</div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sentiment Distribution Visual */}
        {reputation.sentiment_analysis.sentiment_distribution && (
          <div className="glass-card rounded-3xl p-6 border border-gray-50 flex flex-col justify-center">
            <div className="flex items-center justify-between mb-6">
              <h6 className="text-[10px] font-bold text-gray-400 uppercase tracking-[0.2em]">Emotional Footprint</h6>
              <Activity className="w-4 h-4 text-gray-200" />
            </div>

            <div className="space-y-5">
              {[
                { label: 'Positive', value: reputation.sentiment_analysis.sentiment_distribution.positive, color: 'bg-emerald-500', text: 'text-emerald-600' },
                { label: 'Neutral', value: reputation.sentiment_analysis.sentiment_distribution.neutral, color: 'bg-amber-500', text: 'text-amber-600' },
                { label: 'Negative', value: reputation.sentiment_analysis.sentiment_distribution.negative, color: 'bg-rose-500', text: 'text-rose-600' }
              ].map((item) => (
                <div key={item.label} className="group">
                  <div className="flex justify-between items-center text-[11px] mb-2">
                    <span className="font-bold text-gray-500 uppercase tracking-tighter">{item.label}</span>
                    <span className={`font-black ${item.text}`}>{item.value}%</span>
                  </div>
                  <div className="w-full bg-gray-100/50 rounded-full h-2.5 overflow-hidden shadow-inner">
                    <div
                      className={`${item.color} h-full rounded-full transition-all duration-1000 ease-out shadow-sm group-hover:brightness-110`}
                      style={{ width: `${item.value}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8 flex items-center gap-3 p-3 bg-gray-50/50 rounded-2xl border border-gray-100">
              <div className="w-8 h-8 rounded-full bg-white shadow-sm flex items-center justify-center">
                <Users className="w-4 h-4 text-gray-400" />
              </div>
              <p className="text-[11px] text-gray-500 font-medium italic">
                Analysis based on <span className="font-bold text-gray-700">{reputation.sentiment_analysis.total_reviews}</span> individual patient and family testimonies.
              </p>
            </div>
          </div>
        )}

        {/* Sample Reviews Scroller */}
        {reputation.sample_reviews && reputation.sample_reviews.length > 0 && (
          <div className="glass-card rounded-3xl p-6 border border-gray-50 overflow-hidden flex flex-col">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-indigo-500" />
                <h6 className="text-[10px] font-bold text-gray-400 uppercase tracking-[0.2em]">Live Testimonials</h6>
              </div>
              <span className="text-[10px] font-bold text-gray-300">Filtered for quality</span>
            </div>

            <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
              {reputation.sample_reviews.map((review, idx) => (
                <div key={idx} className="p-4 bg-white/40 border border-white/60 rounded-2xl shadow-sm hover:border-indigo-100 hover:bg-white/60 transition-all duration-300 group">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className="flex items-center gap-0.5">
                        {[...Array(5)].map((_, i) => (
                          <Star
                            key={i}
                            className={`w-2.5 h-2.5 ${i < review.rating ? 'text-amber-400 fill-amber-400' : 'text-gray-200'
                              }`}
                          />
                        ))}
                      </div>
                      <span className="text-[10px] font-bold text-[#1E2A44] tracking-tight">{review.author}</span>
                    </div>
                    <span className="text-[9px] font-bold text-indigo-400 uppercase tracking-tighter bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-100/50">
                      {review.source}
                    </span>
                  </div>
                  <p className="text-[11px] leading-relaxed text-gray-600 line-clamp-3 group-hover:line-clamp-none transition-all duration-500">
                    "{review.text}"
                  </p>
                  {review.date && (
                    <div className="mt-2 text-[9px] text-gray-400 font-medium text-right">
                      Source updated: {review.date}
                    </div>
                  )}
                </div>
              ))}
            </div>

            <button className="mt-4 w-full py-2.5 bg-gradient-to-r from-gray-50/50 to-gray-100/50 text-gray-400 text-[10px] font-bold uppercase tracking-widest rounded-xl hover:text-gray-600 transition-colors">
              View All {reputation.total_reviews_analyzed} Insights
            </button>
          </div>
        )}
      </div>
    </div>
  );
}


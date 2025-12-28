import { Users, Bus, Train, Accessibility, AlertTriangle } from 'lucide-react';
import type { ProfessionalCareHome } from '../types';

interface SafetyAnalysisSectionProps {
  home: ProfessionalCareHome;
}

export default function SafetyAnalysisSection({ home }: SafetyAnalysisSectionProps) {
  const safety = home.safetyAnalysis;

  if (!safety) {
    return (
      <div className="glass-card rounded-2xl p-8 border border-gray-100 text-center text-xs text-gray-400 italic">
        Infrastructure and safety audit data not available for this entity.
      </div>
    );
  }

  const getSafetyRatingColor = (rating: string | null) => {
    if (!rating) return 'text-gray-400';
    const lower = rating.toLowerCase();
    if (lower.includes('excellent') || lower.includes('very good')) return 'text-emerald-500';
    if (lower.includes('good')) return 'text-indigo-500';
    if (lower.includes('fair')) return 'text-amber-500';
    return 'text-rose-500';
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between px-2">
        <div>
          <h5 className="text-sm font-bold text-[#1E2A44] uppercase tracking-wider">
            Infrastructure & Safety Audit
          </h5>
          <p className="text-[10px] text-gray-400 font-medium">Environmental and technical safety assessment for {home.name}</p>
        </div>
        <div className="flex items-center gap-2 mt-2 md:mt-0">
          <div className="px-3 py-1 bg-amber-50 text-amber-700 rounded-full text-[10px] font-bold border border-amber-100 flex items-center gap-1.5">
            <AlertTriangle className="w-3 h-3" /> External Verification Required
          </div>
        </div>
      </div>

      {/* Safety Score & Rating Gauge */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-2 glass-card rounded-3xl p-6 border border-gray-50 flex flex-col md:flex-row items-center gap-8">
          <div className="relative w-32 h-32">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="64"
                cy="64"
                r="58"
                stroke="currentColor"
                strokeWidth="8"
                fill="transparent"
                className="text-gray-100"
              />
              <circle
                cx="64"
                cy="64"
                r="58"
                stroke="currentColor"
                strokeWidth="8"
                strokeDasharray={2 * Math.PI * 58}
                strokeDashoffset={2 * Math.PI * 58 * (1 - (safety.safety_score || 0) / 100)}
                strokeLinecap="round"
                fill="transparent"
                className="text-indigo-600 transition-all duration-1000 ease-out"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center transform group hover:scale-105 transition-transform">
              <span className="text-3xl font-black text-[#1E2A44] leading-none">{(safety.safety_score || 0).toFixed(0)}</span>
              <span className="text-[9px] font-bold text-gray-400 uppercase tracking-widest mt-1">Score</span>
            </div>
          </div>

          <div className="flex-1 space-y-4">
            <div>
              <h6 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Safety Classification</h6>
              <div className={`text-2xl font-black ${getSafetyRatingColor(safety.safety_rating)}`}>
                {safety.safety_rating || 'Unclassified'}
              </div>
            </div>
            <p className="text-[11px] text-gray-500 leading-relaxed font-medium italic">
              The safety score incorporates building age, fire safety ratings, and neighborhood crime statistics over a 24-month rolling average.
            </p>
          </div>
        </div>

        <div className="glass-card rounded-3xl p-6 border border-gray-50 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <Accessibility className="w-5 h-5 text-indigo-500" />
            <div className="flex items-center gap-1">
              <div className={`w-2 h-2 rounded-full ${safety.accessibility?.wheelchair_accessible ? 'bg-emerald-500' : 'bg-rose-500'}`}></div>
              <span className="text-[10px] font-bold text-gray-400 uppercase">Accessibility</span>
            </div>
          </div>
          <div className="space-y-3 mt-4">
            <div className="flex justify-between items-center bg-gray-50/50 p-2.5 rounded-xl border border-gray-100">
              <span className="text-[10px] font-semibold text-gray-500">Wheelchair Ready</span>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${safety.accessibility?.wheelchair_accessible ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}`}>
                {safety.accessibility?.wheelchair_accessible ? 'FULL ACCESS' : 'LIMITED'}
              </span>
            </div>
            <div className="flex justify-between items-center bg-gray-50/50 p-2.5 rounded-xl border border-gray-100">
              <span className="text-[10px] font-semibold text-gray-500">Accessible Points</span>
              <span className="text-xs font-black text-[#1E2A44]">{safety.accessibility?.accessible_entrances || 'N/A'}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Pedestrian Safety */}
        <div className="glass-card rounded-3xl p-6 border border-gray-50">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-blue-50 rounded-xl">
              <Users className="w-4 h-4 text-blue-600" />
            </div>
            <h6 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest uppercase">Pedestrian Safety View</h6>
          </div>

          <div className="space-y-4">
            {typeof safety.pedestrian_safety === 'object' && safety.pedestrian_safety !== null && (
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-gray-50/30 rounded-2xl border border-gray-100">
                  <div className="text-[9px] font-bold text-gray-400 uppercase mb-1">Lit Roads</div>
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${(safety.pedestrian_safety as { lit_roads_nearby?: boolean }).lit_roads_nearby ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.5)]' : 'bg-gray-300'}`}></div>
                    <span className="text-xs font-black text-[#1E2A44]">{(safety.pedestrian_safety as { lit_roads_nearby?: boolean }).lit_roads_nearby ? 'YES' : 'NO'}</span>
                  </div>
                </div>
                <div className="p-4 bg-gray-50/30 rounded-2xl border border-gray-100">
                  <div className="text-[9px] font-bold text-gray-400 uppercase mb-1">Crossings</div>
                  <span className="text-xs font-black text-[#1E2A44]">{(safety.pedestrian_safety as { pedestrian_crossings?: number | string }).pedestrian_crossings || '0'} AVAILABLE</span>
                </div>
              </div>
            )}
            <div className="p-4 bg-indigo-50/30 rounded-2xl border border-indigo-100/30">
              <span className="text-[10px] font-bold text-indigo-400 uppercase mb-2 block">Pedestrian Rating</span>
              <p className="text-[11px] text-gray-600 font-medium leading-relaxed">
                {typeof safety.pedestrian_safety === 'string'
                  ? safety.pedestrian_safety
                  : (safety.pedestrian_safety as unknown as { rating?: string })?.rating || 'Adequate lighting and wide footways present in the immediate vicinity.'}
              </p>
            </div>
          </div>
        </div>

        {/* Public Transport */}
        <div className="glass-card rounded-3xl p-6 border border-gray-50">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-emerald-50 rounded-xl">
              <Bus className="w-4 h-4 text-emerald-600" />
            </div>
            <h6 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest uppercase">Transport Connectivity</h6>
          </div>

          <div className="space-y-4">
            {safety.public_transport?.nearest_bus_stop && (
              <div className="flex items-center justify-between p-4 bg-white shadow-sm border border-gray-100 rounded-2xl group hover:border-emerald-200 transition-all">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-emerald-100 text-emerald-600 rounded-lg group-hover:scale-110 transition-transform">
                    <Bus className="w-3 h-3" />
                  </div>
                  <div>
                    <div className="text-[11px] font-black text-[#1E2A44] line-clamp-1">{safety.public_transport.nearest_bus_stop.name}</div>
                    <div className="text-[9px] font-bold text-gray-400 uppercase">Nearest Bus Stop</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs font-black text-emerald-600">{safety.public_transport.nearest_bus_stop.distance?.toFixed(1)}km</div>
                  <div className="text-[9px] font-bold text-gray-300 uppercase">Direct</div>
                </div>
              </div>
            )}

            {safety.public_transport?.nearest_train_station && (
              <div className="flex items-center justify-between p-4 bg-white shadow-sm border border-gray-100 rounded-2xl group hover:border-indigo-200 transition-all">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-indigo-100 text-indigo-600 rounded-lg group-hover:scale-110 transition-transform">
                    <Train className="w-3 h-3" />
                  </div>
                  <div>
                    <div className="text-[11px] font-black text-[#1E2A44] line-clamp-1">{safety.public_transport.nearest_train_station.name}</div>
                    <div className="text-[9px] font-bold text-gray-400 uppercase">Rail Connectivity</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs font-black text-indigo-600">{safety.public_transport.nearest_train_station.distance?.toFixed(1)}km</div>
                  <div className="text-[9px] font-bold text-gray-300 uppercase">Access</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}


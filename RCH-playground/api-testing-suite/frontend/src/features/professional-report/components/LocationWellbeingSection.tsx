import { MapPin, TreePine, Volume2, ShoppingBag, Sparkles, Activity, Navigation } from 'lucide-react';
import type { ProfessionalCareHome } from '../types';

interface LocationWellbeingSectionProps {
  home: ProfessionalCareHome;
}

export default function LocationWellbeingSection({ home }: LocationWellbeingSectionProps) {
  const wellbeing = home.locationWellbeing;

  if (!wellbeing) {
    return (
      <div className="glass-card rounded-2xl p-8 border border-gray-100 text-center text-xs text-gray-400 italic">
        Local environment and wellbeing metrics not available for this coordinate set.
      </div>
    );
  }

  const getWalkabilityColor = (score: number | null) => {
    if (score === null) return 'text-gray-400';
    if (score >= 80) return 'text-emerald-500';
    if (score >= 60) return 'text-indigo-500';
    if (score >= 40) return 'text-amber-500';
    return 'text-rose-500';
  };

  const getNoiseLevelColor = (level: string | null) => {
    if (!level) return 'text-gray-400';
    const lower = level.toLowerCase();
    if (lower.includes('quiet') || lower.includes('low')) return 'text-emerald-500';
    if (lower.includes('moderate')) return 'text-amber-500';
    return 'text-rose-500';
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between px-2">
        <div>
          <h5 className="text-sm font-bold text-[#1E2A44] uppercase tracking-wider">
            Location Wellbeing Analysis
          </h5>
          <p className="text-[10px] text-gray-400 font-medium">Environmental health and lifestyle accessibility for {home.name}</p>
        </div>
        <div className="flex items-center gap-2 mt-2 md:mt-0">
          <div className="px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-[10px] font-bold border border-indigo-100 flex items-center gap-1.5">
            <Sparkles className="w-3 h-3" /> Lifestyle Optimized
          </div>
        </div>
      </div>

      {/* Scores Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Walkability */}
        {wellbeing.walkability_score !== null && (
          <div className="glass-card rounded-3xl p-5 border border-blue-50/50 bg-gradient-to-br from-blue-50/30 shadow-sm transition-all hover:scale-[1.02]">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-blue-100 rounded-xl text-blue-600">
                <Navigation className="w-4 h-4" />
              </div>
              <span className="text-[9px] font-bold text-blue-400 uppercase tracking-widest">Walkability</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className={`text-3xl font-black ${getWalkabilityColor(wellbeing.walkability_score)}`}>
                {wellbeing.walkability_score.toFixed(0)}
              </span>
              <span className="text-xs font-bold text-gray-300">/100</span>
            </div>
          </div>
        )}

        {/* Green Space */}
        {wellbeing.green_space_score !== null && (
          <div className="glass-card rounded-3xl p-5 border border-emerald-50/50 bg-gradient-to-br from-emerald-50/30 shadow-sm transition-all hover:scale-[1.02]">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-emerald-100 rounded-xl text-emerald-600">
                <TreePine className="w-4 h-4" />
              </div>
              <span className="text-[9px] font-bold text-emerald-400 uppercase tracking-widest">Nature Access</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-black text-emerald-600">
                {wellbeing.green_space_score.toFixed(0)}
              </span>
              <span className="text-xs font-bold text-gray-300">/100</span>
            </div>
          </div>
        )}

        {/* Noise Level */}
        <div className="glass-card rounded-3xl p-5 border border-gray-50 bg-white/40 shadow-sm transition-all hover:scale-[1.02]">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-gray-100 rounded-xl text-gray-600">
              <Volume2 className="w-4 h-4" />
            </div>
            <span className="text-[9px] font-bold text-gray-400 uppercase tracking-widest">Acoustics</span>
          </div>
          <div className="flex items-baseline gap-1">
            <span className={`text-xl font-black uppercase ${getNoiseLevelColor(wellbeing.noise_level)}`}>
              {wellbeing.noise_level || 'Normal'}
            </span>
          </div>
        </div>

        {/* Park Distance */}
        {wellbeing.nearest_park_distance !== null && (
          <div className="glass-card rounded-3xl p-5 border border-teal-50/50 bg-gradient-to-br from-teal-50/30 shadow-sm transition-all hover:scale-[1.02]">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-teal-100 rounded-xl text-teal-600">
                <MapPin className="w-4 h-4" />
              </div>
              <span className="text-[9px] font-bold text-teal-400 uppercase tracking-widest">Nearest Park</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-black text-[#1E2A44]">
                {wellbeing.nearest_park_distance.toFixed(1)}
              </span>
              <span className="text-[10px] font-bold text-gray-400 uppercase">km away</span>
            </div>
          </div>
        )}
      </div>

      {/* Local Amenities Matrix */}
      {wellbeing.local_amenities && wellbeing.local_amenities.length > 0 && (
        <div className="glass-card rounded-[2.5rem] p-8 border border-gray-50">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-indigo-50 rounded-2xl">
                <ShoppingBag className="w-5 h-5 text-indigo-600" />
              </div>
              <div>
                <h6 className="text-[10px] font-bold text-indigo-400 uppercase tracking-[0.2em] mb-0.5">Lifestyle Grid</h6>
                <h4 className="text-lg font-black text-[#1E2A44]">Amenity & Service Matrix</h4>
              </div>
            </div>
            <Activity className="w-5 h-5 text-gray-200" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {wellbeing.local_amenities.slice(0, 8).map((amenity, idx) => (
              <div key={idx} className="group p-4 bg-gray-50/50 rounded-2xl border border-gray-100/50 hover:bg-white hover:border-indigo-100 hover:shadow-md transition-all duration-300">
                <div className="flex items-center justify-between mb-3 text-[10px] font-bold text-indigo-400 uppercase tracking-tighter">
                  <span className="bg-white/80 px-2 py-0.5 rounded-full border border-gray-100">{amenity.type}</span>
                  {amenity.distance && (
                    <span className="text-indigo-600 font-black">{amenity.distance.toFixed(1)} km</span>
                  )}
                </div>
                <div className="text-xs font-black text-[#1E2A44] line-clamp-1 mb-1 group-hover:text-indigo-600 transition-colors">
                  {amenity.name}
                </div>
                <div className="w-full bg-gray-200/50 h-1 rounded-full mt-3 overflow-hidden">
                  <div
                    className="bg-indigo-500 h-full rounded-full transition-all duration-1000"
                    style={{ width: `${Math.max(100 - (amenity.distance || 0) * 20, 10)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

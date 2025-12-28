import { MapPin, Stethoscope, TreePine, ShoppingBag, Pill, Building2, Bus, Train, Navigation, Activity } from 'lucide-react';
import type { ProfessionalCareHome } from '../types';

interface AreaMapSectionProps {
  home: ProfessionalCareHome;
}

export default function AreaMapSection({ home }: AreaMapSectionProps) {
  const areaMap = home.areaMap;

  if (!areaMap) {
    return (
      <div className="glass-card rounded-2xl p-8 border border-gray-100 text-center text-xs text-gray-400 italic">
        Geospatial and nearby amenities data not available for this location.
      </div>
    );
  }

  const getIcon = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'gp':
      case 'doctor':
        return <Stethoscope className="w-3.5 h-3.5 text-blue-600" />;
      case 'park':
        return <TreePine className="w-3.5 h-3.5 text-emerald-600" />;
      case 'shop':
      case 'store':
        return <ShoppingBag className="w-3.5 h-3.5 text-purple-600" />;
      case 'pharmacy':
        return <Pill className="w-3.5 h-3.5 text-rose-600" />;
      default:
        return <MapPin className="w-3.5 h-3.5 text-indigo-600" />;
    }
  };

  const getCategoryColor = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'gp': return 'bg-blue-50/50 border-blue-100 text-blue-700';
      case 'park': return 'bg-emerald-50/50 border-emerald-100 text-emerald-700';
      case 'shop': return 'bg-purple-50/50 border-purple-100 text-purple-700';
      case 'pharmacy': return 'bg-rose-50/50 border-rose-100 text-rose-700';
      default: return 'bg-indigo-50/50 border-indigo-100 text-indigo-700';
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between px-2">
        <div>
          <h5 className="text-sm font-bold text-[#1E2A44] uppercase tracking-wider">
            Geospatial & Amenities Map
          </h5>
          <p className="text-[10px] text-gray-400 font-medium">Proximity analysis of essential services for {home.name}</p>
        </div>
        <div className="flex items-center gap-2 mt-2 md:mt-0">
          <div className="px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-[10px] font-bold border border-indigo-100 flex items-center gap-1.5">
            <Navigation className="w-3.5 h-3.5" /> GPS Accuracy Verified
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Essential Medical Prox */}
        <div className="glass-card rounded-[2rem] p-6 border border-gray-50 flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <h6 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Medical Proximity</h6>
            <Activity className="w-4 h-4 text-gray-200" />
          </div>

          <div className="space-y-3">
            {/* Hospitals */}
            {areaMap.nearest_hospital && (
              <div className="p-4 bg-rose-50/30 border border-rose-100/50 rounded-2xl group hover:bg-rose-50 transition-colors">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center gap-2">
                    <Building2 className="w-4 h-4 text-rose-600" />
                    <span className="text-[11px] font-black text-[#1E2A44]">{areaMap.nearest_hospital.name}</span>
                  </div>
                  <span className="text-[10px] font-black text-rose-600">{areaMap.nearest_hospital.distance?.toFixed(1)} km</span>
                </div>
                <div className="text-[9px] font-bold text-rose-400 uppercase tracking-tighter">Nearest General Hospital</div>
              </div>
            )}

            {/* GPs */}
            {areaMap.nearby_gps?.slice(0, 3).map((gp, idx) => (
              <div key={idx} className="flex items-center justify-between p-4 bg-white/40 border border-white rounded-2xl group hover:border-blue-200 transition-all">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-50 text-blue-600 rounded-xl group-hover:scale-110 transition-transform">
                    <Stethoscope className="w-3.5 h-3.5" />
                  </div>
                  <div>
                    <div className="text-[11px] font-bold text-[#1E2A44] line-clamp-1">{gp.name}</div>
                    <div className="text-[9px] font-bold text-gray-400 uppercase">{gp.address ? 'GP Practice' : 'Registered Provider'}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs font-black text-blue-600">{gp.distance?.toFixed(1)} km</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Transport & Lifestyle */}
        <div className="space-y-6">
          <div className="glass-card rounded-[2rem] p-6 border border-gray-50 bg-gradient-to-br from-white to-gray-50">
            <h6 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-6 px-1">Infrastructure Access</h6>
            <div className="grid grid-cols-2 gap-4 text-sm">
              {areaMap.nearest_bus_stop && (
                <div className="p-4 bg-white border border-gray-100 rounded-2xl shadow-sm">
                  <div className="flex items-center gap-2 mb-2">
                    <Bus className="w-3.5 h-3.5 text-blue-600" />
                    <span className="text-[11px] font-black text-[#1E2A44] line-clamp-1">{areaMap.nearest_bus_stop.name}</span>
                  </div>
                  <div className="flex justify-between items-center text-[10px] font-bold">
                    <span className="text-gray-400 uppercase tracking-tighter">Bus Access</span>
                    <span className="text-blue-600">{areaMap.nearest_bus_stop.distance?.toFixed(1)} km</span>
                  </div>
                </div>
              )}
              {areaMap.nearest_train_station && (
                <div className="p-4 bg-white border border-gray-100 rounded-2xl shadow-sm">
                  <div className="flex items-center gap-2 mb-2">
                    <Train className="w-3.5 h-3.5 text-emerald-600" />
                    <span className="text-[11px] font-black text-[#1E2A44] line-clamp-1">{areaMap.nearest_train_station.name}</span>
                  </div>
                  <div className="flex justify-between items-center text-[10px] font-bold">
                    <span className="text-gray-400 uppercase tracking-tighter">Rail Access</span>
                    <span className="text-emerald-600">{areaMap.nearest_train_station.distance?.toFixed(1)} km</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="glass-card rounded-[2rem] p-6 border border-gray-50 flex-1">
            <h6 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-6 px-1">Local Amenities Matrix</h6>
            <div className="flex flex-wrap gap-2">
              {areaMap.nearby_parks?.slice(0, 3).map((park, i) => (
                <div key={`park-${i}`} className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-[10px] font-bold ${getCategoryColor('park')}`}>
                  <TreePine className="w-3 h-3" />
                  <span>{park.name} ({park.distance?.toFixed(1)}km)</span>
                </div>
              ))}
              {areaMap.nearby_shops?.slice(0, 3).map((shop, i) => (
                <div key={`shop-${i}`} className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-[10px] font-bold ${getCategoryColor('shop')}`}>
                  <ShoppingBag className="w-3 h-3" />
                  <span>{shop.name} ({shop.distance?.toFixed(1)}km)</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

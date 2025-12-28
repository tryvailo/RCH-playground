import { Stethoscope, Award, Activity, Heart, ShieldCheck, Zap } from 'lucide-react';
import type { ProfessionalCareHome } from '../types';

interface MedicalCareSectionProps {
  home: ProfessionalCareHome;
}

export default function MedicalCareSection({ home }: MedicalCareSectionProps) {
  const medical = home.medicalCare;

  if (!medical) {
    return (
      <div className="glass-card rounded-2xl p-8 border border-gray-100 text-center text-xs text-gray-400 italic">
        Medical capability and regulated activity data not available for this entity.
      </div>
    );
  }

  const Badge = ({ children, icon: Icon, colorClass }: { children: React.ReactNode, icon: any, colorClass: string }) => (
    <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-[10px] font-bold transition-all hover:scale-105 ${colorClass}`}>
      <Icon className="w-3.5 h-3.5" />
      <span className="tracking-tight">{children}</span>
    </div>
  );

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between px-2">
        <div>
          <h5 className="text-sm font-bold text-[#1E2A44] uppercase tracking-wider">
            Medical & Clinical Capabilities
          </h5>
          <p className="text-[10px] text-gray-400 font-medium">Regulated activities and specialized care provisions for {home.name}</p>
        </div>
        <div className="flex items-center gap-2 mt-2 md:mt-0">
          <div className="px-3 py-1 bg-emerald-50 text-emerald-700 rounded-full text-[10px] font-bold border border-emerald-100 flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5" /> Verified CQC Scope
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Core Care Types */}
        <div className="lg:col-span-2 glass-card rounded-[2rem] p-6 border border-gray-50 bg-gradient-to-br from-white to-indigo-50/20">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-indigo-50 rounded-2xl">
              <Heart className="w-5 h-5 text-indigo-600" />
            </div>
            <h6 className="text-[10px] font-bold text-indigo-400 uppercase tracking-[0.2em]">Service Framework</h6>
          </div>

          <div className="flex flex-wrap gap-3">
            {medical.care_types.map((type, idx) => (
              <Badge key={idx} icon={Zap} colorClass="bg-indigo-50 border-indigo-100 text-indigo-700">
                {type}
              </Badge>
            ))}
          </div>

          <div className="mt-8 pt-6 border-t border-indigo-100/50">
            <h6 className="text-[9px] font-bold text-gray-400 uppercase tracking-widest mb-4">Regulated Activities</h6>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {medical.regulated_activities.map((activity, idx) => (
                <div key={idx} className="flex items-start gap-2 p-3 bg-white/60 border border-white rounded-2xl shadow-sm group hover:border-indigo-200 transition-all">
                  <div className="p-1.5 bg-emerald-50 text-emerald-600 rounded-lg group-hover:scale-110 transition-transform">
                    <Activity className="w-3 h-3" />
                  </div>
                  <span className="text-[11px] font-bold text-[#1E2A44] leading-tight">{activity}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Specialisms & Services */}
        <div className="space-y-6">
          <div className="glass-card rounded-[2rem] p-6 border border-gray-50">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-purple-50 rounded-2xl">
                <Stethoscope className="w-5 h-5 text-purple-600" />
              </div>
              <h6 className="text-[10px] font-bold text-purple-400 uppercase tracking-[0.2em]">Clinical Specialisms</h6>
            </div>
            <div className="space-y-2">
              {medical.medical_specialisms.map((specialism, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-purple-50/30 border border-purple-100/30 rounded-xl group hover:bg-purple-50 transition-colors">
                  <span className="text-[11px] font-bold text-[#1E2A44]">{specialism}</span>
                  <Award className="w-3 h-3 text-purple-300 group-hover:text-purple-500" />
                </div>
              ))}
            </div>
          </div>

          <div className="glass-card rounded-[2rem] p-6 border border-gray-50 flex-1">
            <div className="flex items-center justify-between mb-4">
              <h6 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Provider Scope</h6>
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            </div>
            <p className="text-[11px] text-gray-500 leading-relaxed font-medium italic">
              This facility is registered with the CQC for the above listed regulated activities. Clinical specialisms are updated based on recent provider declarations.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

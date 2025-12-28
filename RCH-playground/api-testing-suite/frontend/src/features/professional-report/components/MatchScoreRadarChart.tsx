import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts';
import type { ProfessionalCareHome } from '../types';

interface MatchScoreRadarChartProps {
  home: ProfessionalCareHome;
}

export default function MatchScoreRadarChart({ home }: MatchScoreRadarChartProps) {
  // Validate factorScores
  if (!home.factorScores || !Array.isArray(home.factorScores) || home.factorScores.length === 0) {
    return null;
  }

  // Prepare data for radar chart with error handling
  const radarData = home.factorScores
    .filter((factor) => {
      // Filter out invalid factors
      return factor &&
        typeof factor.score === 'number' &&
        typeof factor.maxScore === 'number' &&
        factor.maxScore > 0 &&
        factor.category;
    })
    .map((factor) => {
      const score = Number(factor.score) || 0;
      const maxScore = Number(factor.maxScore) || 1;
      const percentage = maxScore > 0 ? (score / maxScore) * 100 : 0;

      return {
        category: (factor.category || 'Unknown').replace(' & ', ' &\n'),
        fullScore: 100,
        score: Math.round(Math.max(0, Math.min(100, percentage))), // Clamp between 0-100
      };
    });

  // If no valid data after filtering, return null
  if (radarData.length === 0) {
    return null;
  }

  // Color based on match score
  const getScoreColor = (matchScore: number | undefined) => {
    const score = typeof matchScore === 'number' ? matchScore : 0;
    if (score >= 80) return '#10B981'; // Teal
    if (score >= 60) return '#6366F1'; // Indigo
    if (score >= 40) return '#F59E0B'; // Amber
    return '#EF4444'; // Red
  };

  // Safe match score
  const matchScore = typeof home.matchScore === 'number' ? home.matchScore : 0;
  const mainColor = getScoreColor(matchScore);

  return (
    <div className="glass-card rounded-2xl p-6 border border-gray-100 shadow-sm animate-fade-in group">
      <div className="text-center mb-6">
        <h5 className="text-sm font-bold text-[#1E2A44] uppercase tracking-wider">
          Performance Matrix
        </h5>
        <p className="text-[10px] text-gray-400 font-medium">Factor breakdown for {home.name}</p>
      </div>

      <div className="relative">
        <ResponsiveContainer width="100%" height={320}>
          <RadarChart data={radarData} margin={{ top: 20, right: 30, bottom: 20, left: 30 }}>
            <PolarGrid stroke="#E2E8F0" />
            <PolarAngleAxis
              dataKey="category"
              tick={{ fontSize: 9, fill: '#475569', fontWeight: 600 }}
              style={{ fontFamily: 'Inter, sans-serif' }}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 100]}
              tick={false}
              axisLine={false}
            />
            <Radar
              name="Capability"
              dataKey="score"
              stroke={mainColor}
              fill={mainColor}
              fillOpacity={0.3}
              strokeWidth={3}
              animationBegin={200}
              animationDuration={1500}
            />
            <Tooltip
              formatter={(value: number) => [`${value}%`, 'Score']}
              contentStyle={{
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                backdropFilter: 'blur(8px)',
                border: '1px solid #E2E8F0',
                borderRadius: '12px',
                fontSize: '12px',
                fontWeight: 600,
                boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
              }}
            />
          </RadarChart>
        </ResponsiveContainer>

        {/* Center Score Overlay */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="w-16 h-16 rounded-full bg-white/50 backdrop-blur-md border border-white/80 flex items-center justify-center shadow-inner">
            <span className="text-lg font-black" style={{ color: mainColor }}>
              {Math.round(matchScore)}
            </span>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap justify-center gap-4 mt-6">
        {radarData.slice(0, 4).map((d, i) => (
          <div key={i} className="flex flex-col items-center">
            <div className="w-1 h-1 rounded-full mb-1" style={{ backgroundColor: mainColor }}></div>
            <span className="text-[9px] font-bold text-gray-500 uppercase tracking-tighter">{d.category.split('\n')[0]}</span>
            <span className="text-xs font-bold text-[#1E2A44]">{d.score}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}


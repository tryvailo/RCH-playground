import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend, Tooltip, Cell } from 'recharts';
import type { ProfessionalCareHome } from '../types';

interface MatchScoreRadarChartProps {
  home: ProfessionalCareHome;
}

export default function MatchScoreRadarChart({ home }: MatchScoreRadarChartProps) {
  if (!home.factorScores || home.factorScores.length === 0) {
    return null;
  }

  // Prepare data for radar chart
  const radarData = home.factorScores.map((factor) => {
    const percentage = (factor.score / factor.maxScore) * 100;
    return {
      category: factor.category.replace(' & ', ' &\n'),
      score: Math.round(percentage),
      maxScore: 100
    };
  });

  // Color based on match score
  const getScoreColor = (matchScore: number) => {
    if (matchScore >= 80) return '#10B981'; // Green
    if (matchScore >= 60) return '#3B82F6'; // Blue
    if (matchScore >= 40) return '#F59E0B'; // Orange
    return '#EF4444'; // Red
  };

  return (
    <div className="bg-white rounded-lg p-4 border border-gray-200">
      <h5 className="text-xs font-semibold text-gray-900 mb-3 text-center">
        {home.name} - Score Breakdown
      </h5>
      <ResponsiveContainer width="100%" height={280}>
        <RadarChart data={radarData} margin={{ top: 20, right: 30, bottom: 20, left: 30 }}>
          <PolarGrid stroke="#E5E7EB" />
          <PolarAngleAxis 
            dataKey="category" 
            tick={{ fontSize: 10, fill: '#6B7280' }}
            style={{ fontSize: '10px' }}
          />
          <PolarRadiusAxis 
            angle={90} 
            domain={[0, 100]} 
            tick={{ fontSize: 10, fill: '#6B7280' }}
            style={{ fontSize: '10px' }}
          />
          <Radar
            name="Score %"
            dataKey="score"
            stroke={getScoreColor(home.matchScore)}
            fill={getScoreColor(home.matchScore)}
            fillOpacity={0.6}
            strokeWidth={2}
          />
          <Tooltip 
            formatter={(value: number) => `${value}%`}
            contentStyle={{ 
              backgroundColor: 'white', 
              border: '1px solid #E5E7EB',
              borderRadius: '6px',
              fontSize: '12px'
            }}
          />
          <Legend 
            wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }}
          />
        </RadarChart>
      </ResponsiveContainer>
      <div className="text-center mt-2">
        <span className="text-xs text-gray-500">Overall Match: </span>
        <span className={`text-sm font-semibold ${getScoreColor(home.matchScore).replace('#', 'text-[')}`}>
          {home.matchScore.toFixed(1)}%
        </span>
      </div>
    </div>
  );
}


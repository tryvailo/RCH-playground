import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend, Tooltip, Cell } from 'recharts';
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
        score: Math.round(Math.max(0, Math.min(100, percentage))), // Clamp between 0-100
        maxScore: 100
      };
    });

  // If no valid data after filtering, return null
  if (radarData.length === 0) {
    return null;
  }

  // Color based on match score
  const getScoreColor = (matchScore: number | undefined) => {
    const score = typeof matchScore === 'number' ? matchScore : 0;
    if (score >= 80) return '#10B981'; // Green
    if (score >= 60) return '#3B82F6'; // Blue
    if (score >= 40) return '#F59E0B'; // Orange
    return '#EF4444'; // Red
  };

  // Safe match score
  const matchScore = typeof home.matchScore === 'number' ? home.matchScore : 0;

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
            stroke={getScoreColor(matchScore)}
            fill={getScoreColor(matchScore)}
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
        <span className="text-sm font-semibold" style={{ color: getScoreColor(matchScore) }}>
          {matchScore.toFixed(1)}%
        </span>
      </div>
    </div>
  );
}


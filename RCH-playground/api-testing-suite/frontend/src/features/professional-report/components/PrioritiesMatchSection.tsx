import React from 'react';
import { Target, CheckCircle2, AlertTriangle, XCircle, Star, Info } from 'lucide-react';
import type { ProfessionalReportData, ProfessionalQuestionnaireResponse } from '../types';

interface PrioritiesMatchSectionProps {
  report: ProfessionalReportData;
  questionnaire?: ProfessionalQuestionnaireResponse;
}

interface UserPriority {
  id: string;
  label: string;
  source: string;
  weight: number;
  icon?: string;
}

interface PriorityMatch {
  score: number;
  status: 'full' | 'partial' | 'none';
  note?: string;
}

interface HomeMatch {
  homeId: string;
  homeName: string;
  homeRank: number;
  priorityScores: Record<string, PriorityMatch>;
  overallPriorityMatch: number;
}

const getStatusIcon = (status: 'full' | 'partial' | 'none') => {
  switch (status) {
    case 'full':
      return <CheckCircle2 className="w-5 h-5 text-green-600" />;
    case 'partial':
      return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
    case 'none':
      return <XCircle className="w-5 h-5 text-red-500" />;
  }
};

const getStatusBgClass = (status: 'full' | 'partial' | 'none') => {
  switch (status) {
    case 'full':
      return 'bg-green-50';
    case 'partial':
      return 'bg-yellow-50';
    case 'none':
      return 'bg-red-50';
  }
};

const extractUserPriorities = (questionnaire?: ProfessionalQuestionnaireResponse): UserPriority[] => {
  const priorities: UserPriority[] = [];

  if (!questionnaire) {
    return [
      { id: 'care_quality', label: 'Quality of Care', source: 'default', weight: 10 },
      { id: 'safety', label: 'Safety & Security', source: 'default', weight: 9 },
      { id: 'location', label: 'Convenient Location', source: 'default', weight: 8 },
      { id: 'price', label: 'Affordable Pricing', source: 'default', weight: 7 },
      { id: 'facilities', label: 'Good Facilities', source: 'default', weight: 6 },
    ];
  }

  // Extract from care_types
  const careTypes = questionnaire.section_3_medical_needs?.q8_care_types || [];
  careTypes.forEach(careType => {
    const labels: Record<string, string> = {
      'general_residential': 'Residential Care',
      'medical_nursing': 'Nursing Care',
      'specialised_dementia': 'Dementia Specialist Care',
      'temporary_respite': 'Respite Care'
    };
    priorities.push({
      id: `care_${careType}`,
      label: labels[careType] || careType,
      source: 'care_types',
      weight: 10
    });
  });

  // Extract from medical_conditions
  const conditions = questionnaire.section_3_medical_needs?.q9_medical_conditions || [];
  conditions.forEach(condition => {
    if (condition === 'no_serious_medical') return;
    const labels: Record<string, string> = {
      'dementia_alzheimers': 'Dementia/Alzheimer\'s Care',
      'mobility_problems': 'Mobility Support',
      'diabetes': 'Diabetes Management',
      'heart_conditions': 'Heart Condition Monitoring'
    };
    priorities.push({
      id: `medical_${condition}`,
      label: labels[condition] || condition,
      source: 'medical_conditions',
      weight: 9
    });
  });

  // Extract from mobility_level
  const mobility = questionnaire.section_3_medical_needs?.q10_mobility_level;
  if (mobility && mobility !== 'fully_mobile') {
    const labels: Record<string, string> = {
      'walking_aids': 'Walking Aid Support',
      'wheelchair_sometimes': 'Wheelchair Accessibility',
      'wheelchair_permanent': 'Full Wheelchair Accessibility'
    };
    priorities.push({
      id: 'mobility_access',
      label: labels[mobility] || 'Mobility Support',
      source: 'mobility_level',
      weight: 9
    });
  }

  // Extract from dietary_requirements
  const dietary = questionnaire.section_4_safety_special_needs?.q15_dietary_requirements || [];
  dietary.forEach(diet => {
    if (diet === 'no_special_requirements') return;
    const labels: Record<string, string> = {
      'diabetic_diet': 'Diabetic Diet',
      'pureed_soft_food': 'Modified Texture Food',
      'vegetarian_vegan': 'Vegetarian/Vegan Options'
    };
    priorities.push({
      id: `diet_${diet}`,
      label: labels[diet] || diet,
      source: 'dietary_requirements',
      weight: 7
    });
  });

  // Extract from location preference
  const city = questionnaire.section_2_location_budget?.q5_preferred_city;
  if (city) {
    priorities.push({
      id: 'location',
      label: `Near ${city}`,
      source: 'preferred_location',
      weight: 8
    });
  }

  // Sort by weight and take top 5
  return priorities.sort((a, b) => b.weight - a.weight).slice(0, 5);
};

const calculateHomeMatches = (
  priorities: UserPriority[],
  homes: ProfessionalReportData['careHomes'],
  questionnaire?: ProfessionalQuestionnaireResponse
): HomeMatch[] => {
  return homes.slice(0, 3).map((home, index) => {
    const priorityScores: Record<string, PriorityMatch> = {};
    let totalScore = 0;
    let totalWeight = 0;

    priorities.forEach(priority => {
      let match: PriorityMatch = { score: 0, status: 'none' };

      // Check based on priority source
      if (priority.source === 'care_types') {
        // Check if home has matching care type
        const cqcRating = home.cqcRating?.toLowerCase();
        if (cqcRating === 'outstanding' || cqcRating === 'good') {
          match = { score: 10, status: 'full' };
        } else if (cqcRating === 'requires improvement') {
          match = { score: 5, status: 'partial', note: 'CQC rating indicates room for improvement' };
        } else {
          match = { score: 3, status: 'partial', note: 'Verify care type availability' };
        }
      } else if (priority.source === 'medical_conditions') {
        // Check medical capabilities from home data
        const matchScore = home.matchScore;
        if (matchScore >= 85) {
          match = { score: 10, status: 'full' };
        } else if (matchScore >= 70) {
          match = { score: 7, status: 'partial', note: 'Verify specialist capabilities' };
        } else {
          match = { score: 4, status: 'partial', note: 'Ask about experience with this condition' };
        }
      } else if (priority.source === 'mobility_level') {
        // Check accessibility
        const hasAccessibility = home.safetyAnalysis?.accessibility?.wheelchair_accessible;
        if (hasAccessibility) {
          match = { score: 10, status: 'full' };
        } else {
          match = { score: 5, status: 'partial', note: 'Verify accessibility during visit' };
        }
      } else if (priority.source === 'dietary_requirements') {
        // FSA rating indicates food quality
        const fsaRating = home.fsaDetailed?.rating;
        if (fsaRating && fsaRating >= 4) {
          match = { score: 9, status: 'full' };
        } else if (fsaRating && fsaRating >= 3) {
          match = { score: 6, status: 'partial', note: 'Discuss dietary needs with kitchen staff' };
        } else {
          match = { score: 4, status: 'partial', note: 'Request sample menus' };
        }
      } else if (priority.source === 'preferred_location') {
        // Check distance
        const distance = parseFloat(home.distance?.replace(/[^0-9.]/g, '') || '0');
        if (distance <= 5) {
          match = { score: 10, status: 'full' };
        } else if (distance <= 15) {
          match = { score: 7, status: 'partial', note: `${distance.toFixed(1)} km away` };
        } else {
          match = { score: 4, status: 'partial', note: `${distance.toFixed(1)} km - consider transport options` };
        }
      } else {
        // Default scoring based on match score
        const score = Math.min(10, Math.round(home.matchScore / 10));
        if (score >= 8) {
          match = { score, status: 'full' };
        } else if (score >= 5) {
          match = { score, status: 'partial' };
        } else {
          match = { score, status: 'none' };
        }
      }

      priorityScores[priority.id] = match;
      totalScore += match.score * priority.weight;
      totalWeight += priority.weight * 10;
    });

    const overallPriorityMatch = totalWeight > 0 ? Math.round((totalScore / totalWeight) * 100) : 0;

    return {
      homeId: home.id,
      homeName: home.name,
      homeRank: index + 1,
      priorityScores,
      overallPriorityMatch
    };
  });
};

export default function PrioritiesMatchSection({ report, questionnaire }: PrioritiesMatchSectionProps) {
  const priorities = extractUserPriorities(questionnaire);
  const homeMatches = calculateHomeMatches(priorities, report.careHomes, questionnaire);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full flex items-center justify-center">
          <Target className="w-5 h-5 text-indigo-600" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-gray-900">Your Priorities Match</h3>
          <p className="text-sm text-gray-600">How our Top 3 match your specific needs</p>
        </div>
      </div>

      {/* User Priorities Cloud */}
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-4 border border-indigo-200">
        <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <Star className="w-4 h-4 text-indigo-600" />
          Your Top Priorities (Based on Your Assessment)
        </h4>
        <div className="flex flex-wrap gap-2">
          {priorities.map((priority, idx) => (
            <div
              key={priority.id}
              className={`px-3 py-1.5 rounded-full border font-medium text-sm transition-colors ${
                idx === 0
                  ? 'bg-indigo-100 text-indigo-800 border-indigo-300'
                  : idx === 1
                  ? 'bg-purple-100 text-purple-800 border-purple-300'
                  : 'bg-gray-100 text-gray-700 border-gray-300'
              }`}
              title={`Weight: ${priority.weight}/10`}
            >
              {priority.label}
            </div>
          ))}
        </div>
        <p className="text-xs text-gray-500 mt-3 flex items-center gap-1">
          <Info className="w-3 h-3" />
          We weighted our analysis based on what matters most to you
        </p>
      </div>

      {/* Comparison Matrix */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider sticky left-0 bg-gray-50 z-10">
                  Care Home
                </th>
                {priorities.map(priority => (
                  <th
                    key={priority.id}
                    scope="col"
                    className="px-3 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider min-w-[100px]"
                  >
                    <div className="truncate" title={priority.label}>
                      {priority.label.length > 15 ? `${priority.label.slice(0, 15)}...` : priority.label}
                    </div>
                  </th>
                ))}
                <th scope="col" className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider bg-indigo-50">
                  Overall Match
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {homeMatches.map((homeMatch, idx) => (
                <tr key={homeMatch.homeId} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                  <td className="px-4 py-3 whitespace-nowrap sticky left-0 z-10" style={{ backgroundColor: idx % 2 === 0 ? 'white' : '#f9fafb' }}>
                    <div className="flex items-center gap-2">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                        homeMatch.homeRank === 1
                          ? 'bg-yellow-400 text-white'
                          : homeMatch.homeRank === 2
                          ? 'bg-gray-300 text-gray-800'
                          : 'bg-orange-300 text-orange-900'
                      }`}>
                        #{homeMatch.homeRank}
                      </div>
                      <div>
                        <div className="font-semibold text-gray-900 text-sm">{homeMatch.homeName}</div>
                      </div>
                    </div>
                  </td>
                  {priorities.map(priority => {
                    const match = homeMatch.priorityScores[priority.id];
                    return (
                      <td
                        key={priority.id}
                        className={`px-3 py-3 text-center ${getStatusBgClass(match?.status || 'none')}`}
                      >
                        <div className="flex flex-col items-center gap-1">
                          {getStatusIcon(match?.status || 'none')}
                          {match?.note && (
                            <span className="text-xs text-gray-500 max-w-[80px] truncate" title={match.note}>
                              {match.note}
                            </span>
                          )}
                        </div>
                      </td>
                    );
                  })}
                  <td className="px-4 py-3 text-center bg-indigo-50">
                    <div className="font-bold text-lg text-indigo-700">
                      {homeMatch.overallPriorityMatch}%
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
        <span className="font-semibold">Legend:</span>
        <div className="flex items-center gap-1">
          <CheckCircle2 className="w-4 h-4 text-green-600" />
          <span>Full Match</span>
        </div>
        <div className="flex items-center gap-1">
          <AlertTriangle className="w-4 h-4 text-yellow-600" />
          <span>Partial Match</span>
        </div>
        <div className="flex items-center gap-1">
          <XCircle className="w-4 h-4 text-red-500" />
          <span>Not Matched</span>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {homeMatches.map(homeMatch => (
          <div
            key={homeMatch.homeId}
            className={`rounded-xl p-4 border-2 ${
              homeMatch.homeRank === 1
                ? 'bg-gradient-to-br from-yellow-50 to-amber-50 border-yellow-300'
                : homeMatch.homeRank === 2
                ? 'bg-gradient-to-br from-gray-50 to-slate-50 border-gray-300'
                : 'bg-gradient-to-br from-orange-50 to-amber-50 border-orange-300'
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                  homeMatch.homeRank === 1
                    ? 'bg-yellow-400 text-white'
                    : homeMatch.homeRank === 2
                    ? 'bg-gray-300 text-gray-800'
                    : 'bg-orange-300 text-orange-900'
                }`}>
                  #{homeMatch.homeRank}
                </div>
                <span className="font-semibold text-gray-900">{homeMatch.homeName}</span>
              </div>
            </div>
            <div className="text-center mb-3">
              <div className="text-3xl font-bold text-indigo-700">{homeMatch.overallPriorityMatch}%</div>
              <div className="text-xs text-gray-500">Priority Match Score</div>
            </div>
            <div className="flex justify-center gap-2">
              {Object.values(homeMatch.priorityScores).filter(m => m.status === 'full').length > 0 && (
                <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded-full">
                  {Object.values(homeMatch.priorityScores).filter(m => m.status === 'full').length} ✓
                </span>
              )}
              {Object.values(homeMatch.priorityScores).filter(m => m.status === 'partial').length > 0 && (
                <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded-full">
                  {Object.values(homeMatch.priorityScores).filter(m => m.status === 'partial').length} ⚠
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

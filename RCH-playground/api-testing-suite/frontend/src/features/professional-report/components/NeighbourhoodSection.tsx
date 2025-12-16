import React from 'react';
import { MapPin, Home, Heart, Users, TrendingUp, Building2, Activity, CheckCircle2, AlertCircle } from 'lucide-react';
import type { NeighbourhoodData } from '../types';

interface NeighbourhoodSectionProps {
  neighbourhood?: NeighbourhoodData | null;
  homeName: string;
}

const getRatingColor = (rating?: string | null) => {
  if (!rating) return { bg: 'bg-gray-100', text: 'text-gray-800', border: 'border-gray-300' };
  const r = rating.toLowerCase();
  if (r === 'excellent' || r === 'very good') return { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-300' };
  if (r === 'good') return { bg: 'bg-blue-100', text: 'text-blue-800', border: 'border-blue-300' };
  if (r === 'average' || r === 'moderate') return { bg: 'bg-yellow-100', text: 'text-yellow-800', border: 'border-yellow-300' };
  if (r === 'below average' || r === 'poor') return { bg: 'bg-orange-100', text: 'text-orange-800', border: 'border-orange-300' };
  if (r === 'very poor') return { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-300' };
  return { bg: 'bg-gray-100', text: 'text-gray-800', border: 'border-gray-300' };
};

const getScoreColor = (score: number | null | undefined) => {
  if (score === null || score === undefined) return 'bg-gray-200';
  if (score >= 80) return 'bg-green-500';
  if (score >= 60) return 'bg-blue-500';
  if (score >= 40) return 'bg-yellow-500';
  if (score >= 20) return 'bg-orange-500';
  return 'bg-red-500';
};

const getConfidenceLabel = (confidence?: string | null) => {
  switch (confidence) {
    case 'high': return { text: 'High confidence', icon: CheckCircle2, color: 'text-green-600' };
    case 'medium': return { text: 'Medium confidence', icon: AlertCircle, color: 'text-yellow-600' };
    case 'low': return { text: 'Low confidence', icon: AlertCircle, color: 'text-orange-600' };
    default: return { text: 'Unknown', icon: AlertCircle, color: 'text-gray-600' };
  }
};

const getPriorityColor = (priority?: 'high' | 'medium' | 'low') => {
  switch (priority) {
    case 'high': return 'bg-red-100 text-red-700 border-red-200';
    case 'medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
    case 'low': return 'bg-blue-100 text-blue-700 border-blue-200';
    default: return 'bg-gray-100 text-gray-700 border-gray-200';
  }
};

export default function NeighbourhoodSection({ neighbourhood, homeName }: NeighbourhoodSectionProps) {
  if (!neighbourhood) {
    return (
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 text-center text-xs text-gray-500">
        Neighbourhood data not available
      </div>
    );
  }

  const ratingColors = getRatingColor(neighbourhood.overallRating);
  const confidenceInfo = getConfidenceLabel(neighbourhood.confidence);
  const ConfidenceIcon = confidenceInfo.icon;

  return (
    <div className="space-y-4">
      {/* Overall Score Header */}
      <div className="bg-white rounded-lg p-4 border border-gray-200">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <MapPin className="h-4 w-4 text-indigo-600" />
            <h5 className="text-xs font-semibold text-gray-900">
              Neighbourhood Analysis - {homeName}
            </h5>
          </div>
          {neighbourhood.overallRating && (
            <div className={`px-2 py-1 rounded text-xs font-medium ${ratingColors.bg} ${ratingColors.text} ${ratingColors.border} border`}>
              {neighbourhood.overallRating}
            </div>
          )}
        </div>

        {/* Score Gauge */}
        {neighbourhood.overallScore !== null && neighbourhood.overallScore !== undefined && (
          <div className="mb-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-gray-600">Overall Neighbourhood Score</span>
              <span className="text-sm font-semibold text-gray-900">{neighbourhood.overallScore}/100</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all duration-500 ${getScoreColor(neighbourhood.overallScore)}`}
                style={{ width: `${Math.min(neighbourhood.overallScore, 100)}%` }}
              />
            </div>
          </div>
        )}

        {/* Confidence Indicator */}
        {neighbourhood.confidence && (
          <div className={`flex items-center gap-1 text-xs ${confidenceInfo.color}`}>
            <ConfidenceIcon className="h-3 w-3" />
            <span>{confidenceInfo.text}</span>
          </div>
        )}
      </div>

      {/* Score Breakdown */}
      {neighbourhood.breakdown && neighbourhood.breakdown.length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-xs font-semibold text-gray-900 mb-3">Score Breakdown</h5>
          <div className="space-y-3">
            {neighbourhood.breakdown.map((item, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-700">{item.name}</span>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-900">{item.score}/100</span>
                    <span className="text-gray-400 text-[10px]">w:{item.weight}</span>
                  </div>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${getScoreColor(item.score)}`}
                    style={{ width: `${Math.min(item.score, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Walkability Details */}
      {neighbourhood.walkability && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="flex items-center gap-2 mb-3">
            <Home className="h-4 w-4 text-blue-600" />
            <h5 className="text-xs font-semibold text-gray-900">Walkability (OSM)</h5>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {/* Walk Score */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-600">Walk Score</span>
                {neighbourhood.walkability.rating && (
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${getRatingColor(neighbourhood.walkability.rating).bg} ${getRatingColor(neighbourhood.walkability.rating).text}`}>
                    {neighbourhood.walkability.rating}
                  </span>
                )}
              </div>
              {neighbourhood.walkability.score !== null && neighbourhood.walkability.score !== undefined && (
                <div className="text-lg font-semibold text-gray-900">{neighbourhood.walkability.score}/100</div>
              )}
            </div>

            {/* Care Home Relevance */}
            {neighbourhood.walkability.careHomeRelevance && (
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-600">Care Home Relevance</span>
                  {neighbourhood.walkability.careHomeRelevance.rating && (
                    <span className={`text-[10px] px-1.5 py-0.5 rounded ${getRatingColor(neighbourhood.walkability.careHomeRelevance.rating).bg} ${getRatingColor(neighbourhood.walkability.careHomeRelevance.rating).text}`}>
                      {neighbourhood.walkability.careHomeRelevance.rating}
                    </span>
                  )}
                </div>
                {neighbourhood.walkability.careHomeRelevance.score !== null && neighbourhood.walkability.careHomeRelevance.score !== undefined && (
                  <div className="text-lg font-semibold text-gray-900">{neighbourhood.walkability.careHomeRelevance.score}/100</div>
                )}
              </div>
            )}
          </div>

          {/* Care Home Relevance Factors */}
          {neighbourhood.walkability.careHomeRelevance?.factors && neighbourhood.walkability.careHomeRelevance.factors.length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <span className="text-[10px] text-gray-500">Relevance Factors:</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {neighbourhood.walkability.careHomeRelevance.factors.map((factor, i) => (
                  <span key={i} className="text-[10px] bg-blue-50 text-blue-700 px-2 py-0.5 rounded">
                    {factor}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Amenities Nearby */}
          {neighbourhood.walkability.amenitiesNearby && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <span className="text-[10px] text-gray-500 mb-2 block">Amenities Nearby:</span>
              <div className="grid grid-cols-3 gap-2">
                {neighbourhood.walkability.amenitiesNearby.healthcare !== undefined && (
                  <div className="text-center bg-gray-50 p-2 rounded">
                    <div className="text-sm font-semibold text-gray-900">
                      {typeof neighbourhood.walkability.amenitiesNearby.healthcare === 'object' 
                        ? (neighbourhood.walkability.amenitiesNearby.healthcare as { count?: number }).count ?? 0
                        : neighbourhood.walkability.amenitiesNearby.healthcare}
                    </div>
                    <div className="text-[10px] text-gray-500">Healthcare</div>
                  </div>
                )}
                {neighbourhood.walkability.amenitiesNearby.shops !== undefined && (
                  <div className="text-center bg-gray-50 p-2 rounded">
                    <div className="text-sm font-semibold text-gray-900">
                      {typeof neighbourhood.walkability.amenitiesNearby.shops === 'object'
                        ? (neighbourhood.walkability.amenitiesNearby.shops as { count?: number }).count ?? 0
                        : neighbourhood.walkability.amenitiesNearby.shops}
                    </div>
                    <div className="text-[10px] text-gray-500">Shops</div>
                  </div>
                )}
                {neighbourhood.walkability.amenitiesNearby.restaurants !== undefined && (
                  <div className="text-center bg-gray-50 p-2 rounded">
                    <div className="text-sm font-semibold text-gray-900">
                      {typeof neighbourhood.walkability.amenitiesNearby.restaurants === 'object'
                        ? (neighbourhood.walkability.amenitiesNearby.restaurants as { count?: number }).count ?? 0
                        : neighbourhood.walkability.amenitiesNearby.restaurants}
                    </div>
                    <div className="text-[10px] text-gray-500">Restaurants</div>
                  </div>
                )}
                {neighbourhood.walkability.amenitiesNearby.parks !== undefined && (
                  <div className="text-center bg-gray-50 p-2 rounded">
                    <div className="text-sm font-semibold text-gray-900">
                      {typeof neighbourhood.walkability.amenitiesNearby.parks === 'object'
                        ? (neighbourhood.walkability.amenitiesNearby.parks as { count?: number }).count ?? 0
                        : neighbourhood.walkability.amenitiesNearby.parks}
                    </div>
                    <div className="text-[10px] text-gray-500">Parks</div>
                  </div>
                )}
                {neighbourhood.walkability.amenitiesNearby.transport !== undefined && (
                  <div className="text-center bg-gray-50 p-2 rounded">
                    <div className="text-sm font-semibold text-gray-900">
                      {typeof neighbourhood.walkability.amenitiesNearby.transport === 'object'
                        ? (neighbourhood.walkability.amenitiesNearby.transport as { count?: number }).count ?? 0
                        : neighbourhood.walkability.amenitiesNearby.transport}
                    </div>
                    <div className="text-[10px] text-gray-500">Transport</div>
                  </div>
                )}
                {neighbourhood.walkability.amenitiesNearby.total !== undefined && (
                  <div className="text-center bg-indigo-50 p-2 rounded">
                    <div className="text-sm font-semibold text-indigo-700">
                      {typeof neighbourhood.walkability.amenitiesNearby.total === 'object'
                        ? (neighbourhood.walkability.amenitiesNearby.total as { count?: number }).count ?? 0
                        : neighbourhood.walkability.amenitiesNearby.total}
                    </div>
                    <div className="text-[10px] text-indigo-600">Total</div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Social Wellbeing */}
      {neighbourhood.socialWellbeing && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="flex items-center gap-2 mb-3">
            <Users className="h-4 w-4 text-purple-600" />
            <h5 className="text-xs font-semibold text-gray-900">Social Wellbeing (ONS)</h5>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-3">
            {/* Score */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-600">Wellbeing Score</span>
                {neighbourhood.socialWellbeing.rating && (
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${getRatingColor(neighbourhood.socialWellbeing.rating).bg} ${getRatingColor(neighbourhood.socialWellbeing.rating).text}`}>
                    {neighbourhood.socialWellbeing.rating}
                  </span>
                )}
              </div>
              {neighbourhood.socialWellbeing.score !== null && neighbourhood.socialWellbeing.score !== undefined && (
                <div className="text-lg font-semibold text-gray-900">{neighbourhood.socialWellbeing.score}/100</div>
              )}
            </div>

            {/* Local Authority */}
            {neighbourhood.socialWellbeing.localAuthority && (
              <div>
                <span className="text-xs text-gray-600 block mb-1">Local Authority</span>
                <div className="text-sm font-medium text-gray-900">{neighbourhood.socialWellbeing.localAuthority}</div>
              </div>
            )}
          </div>

          {/* Deprivation */}
          {neighbourhood.socialWellbeing.deprivation && (
            <div className="pt-3 border-t border-gray-100">
              <span className="text-[10px] text-gray-500 mb-2 block">Deprivation Index:</span>
              <div className="grid grid-cols-3 gap-2">
                {neighbourhood.socialWellbeing.deprivation.index !== null && neighbourhood.socialWellbeing.deprivation.index !== undefined && (
                  <div className="text-center bg-gray-50 p-2 rounded">
                    <div className="text-sm font-semibold text-gray-900">{neighbourhood.socialWellbeing.deprivation.index.toFixed(2)}</div>
                    <div className="text-[10px] text-gray-500">Index</div>
                  </div>
                )}
                {neighbourhood.socialWellbeing.deprivation.decile !== null && neighbourhood.socialWellbeing.deprivation.decile !== undefined && (
                  <div className="text-center bg-gray-50 p-2 rounded">
                    <div className="text-sm font-semibold text-gray-900">{neighbourhood.socialWellbeing.deprivation.decile}/10</div>
                    <div className="text-[10px] text-gray-500">Decile</div>
                  </div>
                )}
                {neighbourhood.socialWellbeing.deprivation.rank !== null && neighbourhood.socialWellbeing.deprivation.rank !== undefined && (
                  <div className="text-center bg-gray-50 p-2 rounded">
                    <div className="text-sm font-semibold text-gray-900">{neighbourhood.socialWellbeing.deprivation.rank.toLocaleString()}</div>
                    <div className="text-[10px] text-gray-500">Rank</div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Health Profile */}
      {neighbourhood.healthProfile && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="flex items-center gap-2 mb-3">
            <Activity className="h-4 w-4 text-red-600" />
            <h5 className="text-xs font-semibold text-gray-900">Health Profile (NHSBSA)</h5>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-3">
            {/* Score */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-600">Health Score</span>
                {neighbourhood.healthProfile.rating && (
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${getRatingColor(neighbourhood.healthProfile.rating).bg} ${getRatingColor(neighbourhood.healthProfile.rating).text}`}>
                    {neighbourhood.healthProfile.rating}
                  </span>
                )}
              </div>
              {neighbourhood.healthProfile.score !== null && neighbourhood.healthProfile.score !== undefined && (
                <div className="text-lg font-semibold text-gray-900">{neighbourhood.healthProfile.score}/100</div>
              )}
            </div>

            {/* GP Practices */}
            {neighbourhood.healthProfile.gpPracticesNearby !== null && neighbourhood.healthProfile.gpPracticesNearby !== undefined && (
              <div>
                <span className="text-xs text-gray-600 block mb-1">GP Practices Nearby</span>
                <div className="flex items-center gap-2">
                  <Building2 className="h-4 w-4 text-gray-400" />
                  <span className="text-lg font-semibold text-gray-900">{neighbourhood.healthProfile.gpPracticesNearby}</span>
                </div>
              </div>
            )}
          </div>

          {/* Care Home Considerations */}
          {neighbourhood.healthProfile.careHomeConsiderations && neighbourhood.healthProfile.careHomeConsiderations.length > 0 && (
            <div className="pt-3 border-t border-gray-100">
              <span className="text-[10px] text-gray-500 mb-2 block">Care Home Considerations:</span>
              <div className="space-y-2">
                {neighbourhood.healthProfile.careHomeConsiderations.map((consideration, i) => (
                  <div key={i} className={`p-2 rounded border ${getPriorityColor(consideration.priority)}`}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-medium">{consideration.category}</span>
                      {consideration.priority && (
                        <span className="text-[10px] uppercase">{consideration.priority}</span>
                      )}
                    </div>
                    {consideration.description && (
                      <p className="text-[10px] opacity-80">{consideration.description}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Coordinates */}
      {neighbourhood.coordinates && (neighbourhood.coordinates.latitude || neighbourhood.coordinates.longitude) && (
        <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
          <h6 className="text-[10px] font-medium text-gray-700 mb-2">Location Coordinates</h6>
          <div className="flex gap-4 text-[10px] text-gray-500">
            {neighbourhood.coordinates.latitude !== null && neighbourhood.coordinates.latitude !== undefined && (
              <span className="bg-white px-2 py-1 rounded border border-gray-200">
                Lat: {neighbourhood.coordinates.latitude.toFixed(6)}
              </span>
            )}
            {neighbourhood.coordinates.longitude !== null && neighbourhood.coordinates.longitude !== undefined && (
              <span className="bg-white px-2 py-1 rounded border border-gray-200">
                Lng: {neighbourhood.coordinates.longitude.toFixed(6)}
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

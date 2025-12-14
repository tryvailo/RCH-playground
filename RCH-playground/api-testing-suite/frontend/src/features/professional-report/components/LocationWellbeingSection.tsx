import React from 'react';
import { MapPin, TreePine, Volume2, ShoppingBag } from 'lucide-react';
import type { ProfessionalCareHome } from '../types';

interface LocationWellbeingSectionProps {
  home: ProfessionalCareHome;
}

export default function LocationWellbeingSection({ home }: LocationWellbeingSectionProps) {
  const wellbeing = home.locationWellbeing;

  if (!wellbeing) {
    return (
      <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
        <p className="text-sm text-gray-500">Location wellbeing data not available</p>
      </div>
    );
  }

  const getWalkabilityColor = (score: number | null) => {
    if (score === null) return 'text-gray-500';
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-blue-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getNoiseLevelColor = (level: string | null) => {
    if (!level) return 'text-gray-500';
    const lower = level.toLowerCase();
    if (lower.includes('quiet') || lower.includes('low')) return 'text-green-600';
    if (lower.includes('moderate')) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <MapPin className="w-5 h-5 text-emerald-600" />
        <h4 className="text-lg font-semibold text-gray-900">Location Wellbeing</h4>
      </div>

      {/* Scores Grid */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {wellbeing.walkability_score !== null && (
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
            <div className="flex items-center gap-1 mb-1">
              <MapPin className="w-4 h-4 text-blue-600" />
              <span className="text-xs text-blue-600 font-semibold">Walkability Score</span>
            </div>
            <div className={`text-2xl font-bold ${getWalkabilityColor(wellbeing.walkability_score)}`}>
              {wellbeing.walkability_score.toFixed(0)}
            </div>
            <div className="text-xs text-blue-700">out of 100</div>
          </div>
        )}

        {wellbeing.green_space_score !== null && (
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
            <div className="flex items-center gap-1 mb-1">
              <TreePine className="w-4 h-4 text-green-600" />
              <span className="text-xs text-green-600 font-semibold">Green Space Score</span>
            </div>
            <div className="text-2xl font-bold text-green-900">
              {wellbeing.green_space_score.toFixed(0)}
            </div>
            <div className="text-xs text-green-700">out of 100</div>
          </div>
        )}
      </div>

      {/* Nearest Park */}
      {wellbeing.nearest_park_distance !== null && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
            <TreePine className="w-4 h-4 text-green-600" />
            Nearest Park
          </h5>
          <p className="text-sm text-gray-700">
            {wellbeing.nearest_park_distance.toFixed(1)} km away
          </p>
        </div>
      )}

      {/* Noise Level */}
      {wellbeing.noise_level && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
            <Volume2 className="w-4 h-4 text-gray-600" />
            Noise Level
          </h5>
          <p className={`text-sm font-semibold ${getNoiseLevelColor(wellbeing.noise_level)}`}>
            {wellbeing.noise_level}
          </p>
        </div>
      )}

      {/* Local Amenities */}
      {wellbeing.local_amenities && wellbeing.local_amenities.length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <ShoppingBag className="w-4 h-4 text-purple-600" />
            Local Amenities
          </h5>
          <div className="space-y-2">
            {wellbeing.local_amenities.slice(0, 8).map((amenity, idx) => (
              <div key={idx} className="flex items-center justify-between text-sm">
                <span className="text-gray-700 capitalize">{amenity.type}</span>
                <div className="flex items-center gap-2">
                  <span className="text-gray-600 text-xs">{amenity.name}</span>
                  {amenity.distance && (
                    <span className="text-gray-500 text-xs">
                      ({amenity.distance.toFixed(1)} km)
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}


import React from 'react';
import { Shield, Users, Bus, Train, Accessibility } from 'lucide-react';
import type { ProfessionalCareHome } from '../types';

interface SafetyAnalysisSectionProps {
  home: ProfessionalCareHome;
}

export default function SafetyAnalysisSection({ home }: SafetyAnalysisSectionProps) {
  const safety = home.safetyAnalysis;

  if (!safety) {
    return (
      <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
        <p className="text-sm text-gray-500">Safety analysis data not available</p>
      </div>
    );
  }

  const getSafetyRatingColor = (rating: string | null) => {
    if (!rating) return 'text-gray-500';
    const lower = rating.toLowerCase();
    if (lower.includes('excellent') || lower.includes('very good')) return 'text-green-600';
    if (lower.includes('good')) return 'text-blue-600';
    if (lower.includes('fair')) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <Shield className="w-5 h-5 text-orange-600" />
        <h4 className="text-lg font-semibold text-gray-900">Safety & Infrastructure Analysis</h4>
      </div>

      {/* Safety Score & Rating */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {safety.safety_score !== null && (
          <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4 border border-orange-200">
            <div className="flex items-center gap-1 mb-1">
              <Shield className="w-4 h-4 text-orange-600" />
              <span className="text-xs text-orange-600 font-semibold">Safety Score</span>
            </div>
            <div className="text-2xl font-bold text-orange-900">
              {safety.safety_score.toFixed(1)}
            </div>
            <div className="text-xs text-orange-700">out of 100</div>
          </div>
        )}

        {safety.safety_rating && (
          <div className={`bg-gradient-to-br rounded-lg p-4 border ${
            safety.safety_rating.toLowerCase().includes('excellent') || safety.safety_rating.toLowerCase().includes('very good')
              ? 'from-green-50 to-green-100 border-green-200'
              : safety.safety_rating.toLowerCase().includes('good')
              ? 'from-blue-50 to-blue-100 border-blue-200'
              : 'from-yellow-50 to-yellow-100 border-yellow-200'
          }`}>
            <div className="flex items-center gap-1 mb-1">
              <Shield className={`w-4 h-4 ${getSafetyRatingColor(safety.safety_rating)}`} />
              <span className={`text-xs font-semibold ${getSafetyRatingColor(safety.safety_rating)}`}>
                Safety Rating
              </span>
            </div>
            <div className={`text-xl font-bold ${getSafetyRatingColor(safety.safety_rating)}`}>
              {safety.safety_rating}
            </div>
          </div>
        )}
      </div>

      {/* Pedestrian Safety */}
      {safety.pedestrian_safety && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
            <Users className="w-4 h-4 text-blue-600" />
            Pedestrian Safety
          </h5>
          {typeof safety.pedestrian_safety === 'string' ? (
            <p className="text-sm text-gray-700">{safety.pedestrian_safety}</p>
          ) : typeof safety.pedestrian_safety === 'object' && safety.pedestrian_safety !== null ? (
            <div className="space-y-2 text-sm">
              {safety.pedestrian_safety.rating && (
                <div>
                  <span className="font-semibold text-gray-900">Rating: </span>
                  <span className="text-gray-700">{safety.pedestrian_safety.rating}</span>
                </div>
              )}
              {safety.pedestrian_safety.pedestrian_crossings !== undefined && (
                <div>
                  <span className="font-semibold text-gray-900">Pedestrian Crossings: </span>
                  <span className="text-gray-700">{safety.pedestrian_safety.pedestrian_crossings}</span>
                </div>
              )}
              {safety.pedestrian_safety.lit_roads_nearby !== undefined && (
                <div>
                  <span className="font-semibold text-gray-900">Lit Roads Nearby: </span>
                  <span className="text-gray-700">{safety.pedestrian_safety.lit_roads_nearby ? 'Yes' : 'No'}</span>
                </div>
              )}
              {safety.pedestrian_safety.footways && (
                <div>
                  <span className="font-semibold text-gray-900">Footways: </span>
                  <span className="text-gray-700">{safety.pedestrian_safety.footways}</span>
                </div>
              )}
            </div>
          ) : null}
        </div>
      )}

      {/* Public Transport */}
      {safety.public_transport && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3">Public Transport Access</h5>
          <div className="space-y-2">
            {safety.public_transport.nearest_bus_stop && (
              <div className="flex items-center gap-2 text-sm">
                <Bus className="w-4 h-4 text-blue-600" />
                <span className="text-gray-700">
                  <span className="font-semibold">Bus Stop:</span> {safety.public_transport.nearest_bus_stop.name}
                  {safety.public_transport.nearest_bus_stop.distance && (
                    <span className="text-gray-500 ml-1">
                      ({safety.public_transport.nearest_bus_stop.distance.toFixed(1)} km)
                    </span>
                  )}
                </span>
              </div>
            )}
            {safety.public_transport.nearest_train_station && (
              <div className="flex items-center gap-2 text-sm">
                <Train className="w-4 h-4 text-green-600" />
                <span className="text-gray-700">
                  <span className="font-semibold">Train Station:</span> {safety.public_transport.nearest_train_station.name}
                  {safety.public_transport.nearest_train_station.distance && (
                    <span className="text-gray-500 ml-1">
                      ({safety.public_transport.nearest_train_station.distance.toFixed(1)} km)
                    </span>
                  )}
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Accessibility */}
      {safety.accessibility && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Accessibility className="w-4 h-4 text-purple-600" />
            Accessibility Features
          </h5>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <div className="text-gray-600">Wheelchair Accessible</div>
              <div className={`font-semibold ${safety.accessibility.wheelchair_accessible ? 'text-green-700' : 'text-red-700'}`}>
                {safety.accessibility.wheelchair_accessible ? 'Yes' : 'No'}
              </div>
            </div>
            {safety.accessibility.accessible_entrances !== null && (
              <div>
                <div className="text-gray-600">Accessible Entrances</div>
                <div className="font-semibold text-gray-900">
                  {safety.accessibility.accessible_entrances}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}


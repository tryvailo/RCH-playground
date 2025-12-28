/**
 * Area Map Block
 * Interactive map showing user location, recommended homes, and amenities
 * ТЗ Section 8: Geographic Visualization
 * 
 * REUSES: MapView component from neighbourhood feature
 */
import { ExternalLink } from 'lucide-react';
import { MapView } from '../../neighbourhood/components';
import type { AreaMapData } from '../types';

interface AreaMapBlockProps {
  mapData: AreaMapData;
  className?: string;
}

const MATCH_TYPE_COLORS: Record<string, string> = {
  'Safe Bet': '#3B82F6',
  'Best Value': '#10B981',
  'Premium': '#8B5CF6',
};

export function AreaMapBlock({ mapData, className = '' }: AreaMapBlockProps) {
  const markers = [
    {
      lat: mapData.user_location.lat,
      lon: mapData.user_location.lng,
      label: `Your Location (${mapData.user_location.postcode})`,
    },
    ...mapData.homes.map((home, index) => ({
      lat: home.lat,
      lon: home.lng,
      label: `${index + 1}. ${home.name} (${home.match_type}) - ${home.distance_km != null ? home.distance_km.toFixed(1) : 'N/A'}km`,
    })),
  ];

  return (
    <div className={`bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden ${className}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-[#1E2A44] to-[#2D3E5F] px-6 py-5">
        <h2 className="text-xl md:text-2xl font-bold text-white">
          Location Map
        </h2>
        <p className="text-gray-300 text-sm">Your location & recommended homes</p>
      </div>

      {/* Map - Reusing MapView from neighbourhood */}
      <MapView
        latitude={mapData.user_location.lat}
        longitude={mapData.user_location.lng}
        postcode={mapData.user_location.postcode}
        zoom={(mapData as any).suggested_zoom || 12}
        height="400px"
        showMultipleMarkers={markers}
      />

      {/* Distance Legend */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <h4 className="text-sm font-semibold text-gray-700 mb-3">Distance from Your Location</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {mapData.homes.map((home, index) => (
            <div
              key={home.id}
              className="flex items-center gap-3 bg-white rounded-lg p-3 border border-gray-200"
            >
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm"
                style={{ backgroundColor: MATCH_TYPE_COLORS[home.match_type] || '#6B7280' }}
              >
                {index + 1}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">{home.name}</p>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500">
                    {home.distance_km != null ? `${home.distance_km.toFixed(1)} km` : 'Distance N/A'}
                  </span>
                  <span
                    className="text-xs px-2 py-0.5 rounded-full"
                    style={{
                      backgroundColor: `${MATCH_TYPE_COLORS[home.match_type] || '#6B7280'}20`,
                      color: MATCH_TYPE_COLORS[home.match_type] || '#6B7280',
                    }}
                  >
                    {home.match_type}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="px-4 pb-4">
        <div className="flex flex-wrap items-center gap-4 text-xs text-gray-600">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full bg-blue-500 border-2 border-white shadow" />
            <span>Safe Bet</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full bg-emerald-500 border-2 border-white shadow" />
            <span>Best Value</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full bg-purple-500 border-2 border-white shadow" />
            <span>Premium</span>
          </div>
        </div>
      </div>

      {/* Open in Google Maps */}
      <div className="px-4 pb-4">
        <a
          href={`https://www.google.com/maps/search/care+homes/@${mapData.user_location.lat},${mapData.user_location.lng},13z`}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800 hover:underline"
        >
          <ExternalLink className="w-4 h-4" />
          Open in Google Maps
        </a>
      </div>
    </div>
  );
}

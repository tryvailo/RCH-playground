import React from 'react';
import { MapPin, Stethoscope, TreePine, ShoppingBag, Pill, Building2, Bus, Train } from 'lucide-react';
import type { ProfessionalCareHome } from '../types';

interface AreaMapSectionProps {
  home: ProfessionalCareHome;
}

export default function AreaMapSection({ home }: AreaMapSectionProps) {
  const areaMap = home.areaMap;

  if (!areaMap) {
    return (
      <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
        <p className="text-sm text-gray-500">Area map data not available</p>
      </div>
    );
  }

  const getIcon = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'gp':
      case 'doctor':
        return <Stethoscope className="w-4 h-4 text-blue-600" />;
      case 'park':
        return <TreePine className="w-4 h-4 text-green-600" />;
      case 'shop':
      case 'store':
        return <ShoppingBag className="w-4 h-4 text-purple-600" />;
      case 'pharmacy':
        return <Pill className="w-4 h-4 text-red-600" />;
      default:
        return <MapPin className="w-4 h-4 text-gray-600" />;
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <MapPin className="w-5 h-5 text-teal-600" />
        <h4 className="text-lg font-semibold text-gray-900">Area Map & Nearby Services</h4>
      </div>

      {/* Nearby GPs */}
      {areaMap.nearby_gps && areaMap.nearby_gps.length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Stethoscope className="w-4 h-4 text-blue-600" />
            Nearby GP Practices
          </h5>
          <div className="space-y-2">
            {areaMap.nearby_gps.slice(0, 5).map((gp, idx) => (
              <div key={idx} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  {getIcon('gp')}
                  <span className="text-gray-700">{gp.name}</span>
                </div>
                <div className="flex items-center gap-2">
                  {gp.address && (
                    <span className="text-gray-500 text-xs">{gp.address}</span>
                  )}
                  {gp.distance && (
                    <span className="text-gray-500 text-xs">
                      ({gp.distance.toFixed(1)} km)
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Nearby Parks */}
      {areaMap.nearby_parks && areaMap.nearby_parks.length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <TreePine className="w-4 h-4 text-green-600" />
            Nearby Parks
          </h5>
          <div className="space-y-2">
            {areaMap.nearby_parks.slice(0, 5).map((park, idx) => (
              <div key={idx} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  {getIcon('park')}
                  <span className="text-gray-700">{park.name}</span>
                </div>
                {park.distance && (
                  <span className="text-gray-500 text-xs">
                    {park.distance.toFixed(1)} km
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Nearby Shops */}
      {areaMap.nearby_shops && areaMap.nearby_shops.length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <ShoppingBag className="w-4 h-4 text-purple-600" />
            Nearby Shops
          </h5>
          <div className="space-y-2">
            {areaMap.nearby_shops.slice(0, 5).map((shop, idx) => (
              <div key={idx} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  {getIcon(shop.type || 'shop')}
                  <span className="text-gray-700">{shop.name}</span>
                  {shop.type && (
                    <span className="text-xs text-gray-500">({shop.type})</span>
                  )}
                </div>
                {shop.distance && (
                  <span className="text-gray-500 text-xs">
                    {shop.distance.toFixed(1)} km
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Nearby Pharmacies */}
      {areaMap.nearby_pharmacies && areaMap.nearby_pharmacies.length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Pill className="w-4 h-4 text-red-600" />
            Nearby Pharmacies
          </h5>
          <div className="space-y-2">
            {areaMap.nearby_pharmacies.slice(0, 5).map((pharmacy, idx) => (
              <div key={idx} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  {getIcon('pharmacy')}
                  <span className="text-gray-700">{pharmacy.name}</span>
                </div>
                {pharmacy.distance && (
                  <span className="text-gray-500 text-xs">
                    {pharmacy.distance.toFixed(1)} km
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Nearest Hospital */}
      {areaMap.nearest_hospital && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
            <Building2 className="w-4 h-4 text-red-600" />
            Nearest Hospital
          </h5>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-700">{areaMap.nearest_hospital.name}</span>
            {areaMap.nearest_hospital.distance && (
              <span className="text-gray-500 text-xs">
                {areaMap.nearest_hospital.distance.toFixed(1)} km
              </span>
            )}
          </div>
        </div>
      )}

      {/* Transport Summary */}
      <div className="bg-gradient-to-r from-teal-50 to-cyan-50 rounded-lg p-4 border border-teal-200">
        <h5 className="text-sm font-semibold text-gray-900 mb-3">Transport Access</h5>
        <div className="grid grid-cols-2 gap-3">
          {areaMap.nearest_bus_stop && (
            <div className="flex items-center gap-2 text-sm">
              <Bus className="w-4 h-4 text-blue-600" />
              <div>
                <div className="text-gray-700 font-semibold">{areaMap.nearest_bus_stop.name}</div>
                {areaMap.nearest_bus_stop.distance && (
                  <div className="text-xs text-gray-500">
                    {areaMap.nearest_bus_stop.distance.toFixed(1)} km
                  </div>
                )}
              </div>
            </div>
          )}
          {areaMap.nearest_train_station && (
            <div className="flex items-center gap-2 text-sm">
              <Train className="w-4 h-4 text-green-600" />
              <div>
                <div className="text-gray-700 font-semibold">{areaMap.nearest_train_station.name}</div>
                {areaMap.nearest_train_station.distance && (
                  <div className="text-xs text-gray-500">
                    {areaMap.nearest_train_station.distance.toFixed(1)} km
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}


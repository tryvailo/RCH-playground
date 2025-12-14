import React from 'react';
import { Home, UtensilsCrossed, Activity, Wifi, Car, TreePine, Image as ImageIcon, CheckCircle2 } from 'lucide-react';
import type { ProfessionalCareHome } from '../types';

interface ComfortLifestyleSectionProps {
  home: ProfessionalCareHome;
}

export default function ComfortLifestyleSection({ home }: ComfortLifestyleSectionProps) {
  const comfort = home.comfortLifestyle;

  if (!comfort) {
    return (
      <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
        <p className="text-sm text-gray-500">Comfort & lifestyle data not available</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <Home className="w-5 h-5 text-indigo-600" />
        <h4 className="text-lg font-semibold text-gray-900">Comfort & Lifestyle</h4>
      </div>

      {/* Facilities */}
      {comfort.facilities && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3">Facilities & Amenities</h5>
          <div className="space-y-3">
            {comfort.facilities.general_amenities && comfort.facilities.general_amenities.length > 0 && (
              <div>
                <div className="text-xs text-gray-600 mb-1">General Amenities</div>
                <div className="flex flex-wrap gap-2">
                  {comfort.facilities.general_amenities.slice(0, 8).map((amenity, idx) => (
                    <span key={idx} className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs">
                      {amenity}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {comfort.facilities.medical_facilities && comfort.facilities.medical_facilities.length > 0 && (
              <div>
                <div className="text-xs text-gray-600 mb-1">Medical Facilities</div>
                <div className="flex flex-wrap gap-2">
                  {comfort.facilities.medical_facilities.map((facility, idx) => (
                    <span key={idx} className="px-2 py-1 bg-red-50 text-red-700 rounded text-xs">
                      {facility}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {comfort.facilities.social_facilities && comfort.facilities.social_facilities.length > 0 && (
              <div>
                <div className="text-xs text-gray-600 mb-1">Social Facilities</div>
                <div className="flex flex-wrap gap-2">
                  {comfort.facilities.social_facilities.slice(0, 6).map((facility, idx) => (
                    <span key={idx} className="px-2 py-1 bg-green-50 text-green-700 rounded text-xs">
                      {facility}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {comfort.facilities.outdoor_spaces && comfort.facilities.outdoor_spaces.length > 0 && (
              <div>
                <div className="text-xs text-gray-600 mb-1">Outdoor Spaces</div>
                <div className="flex flex-wrap gap-2">
                  {comfort.facilities.outdoor_spaces.map((space, idx) => (
                    <span key={idx} className="px-2 py-1 bg-emerald-50 text-emerald-700 rounded text-xs">
                      {space}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Activities */}
      {comfort.activities && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Activity className="w-4 h-4 text-purple-600" />
            Activities & Programs
          </h5>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {comfort.activities.daily_activities && comfort.activities.daily_activities.length > 0 && (
              <div>
                <div className="text-xs text-gray-600 mb-2">Daily Activities</div>
                <div className="space-y-1">
                  {comfort.activities.daily_activities.slice(0, 5).map((activity, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-xs text-gray-700">
                      <CheckCircle2 className="w-3 h-3 text-green-600 flex-shrink-0" />
                      <span>{activity}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {comfort.activities.weekly_programs && comfort.activities.weekly_programs.length > 0 && (
              <div>
                <div className="text-xs text-gray-600 mb-2">Weekly Programs</div>
                <div className="space-y-1">
                  {comfort.activities.weekly_programs.slice(0, 5).map((program, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-xs text-gray-700">
                      <CheckCircle2 className="w-3 h-3 text-blue-600 flex-shrink-0" />
                      <span>{program}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          <div className="mt-3 pt-3 border-t border-gray-200 grid grid-cols-2 gap-3 text-xs">
            {comfort.activities.weekly_activities_count > 0 && (
              <div>
                <span className="text-gray-600">Weekly Activities:</span>
                <span className="font-semibold text-gray-900 ml-1">
                  {comfort.activities.weekly_activities_count}
                </span>
              </div>
            )}
            {comfort.activities.outings_per_month > 0 && (
              <div>
                <span className="text-gray-600">Outings per Month:</span>
                <span className="font-semibold text-gray-900 ml-1">
                  {comfort.activities.outings_per_month}
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Nutrition */}
      {comfort.nutrition && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <UtensilsCrossed className="w-4 h-4 text-orange-600" />
            Nutrition & Dining
          </h5>
          {comfort.nutrition.dietary_options && comfort.nutrition.dietary_options.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {comfort.nutrition.dietary_options.map((option, idx) => (
                <span key={idx} className="px-2 py-1 bg-orange-50 text-orange-700 rounded text-xs">
                  {option}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Room & Accessibility Features */}
      <div className="bg-white rounded-lg p-4 border border-gray-200">
        <h5 className="text-sm font-semibold text-gray-900 mb-3">Room & Accessibility</h5>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs">
          {comfort.private_room_percentage !== null && (
            <div>
              <div className="text-gray-600">Private Rooms</div>
              <div className="font-semibold text-gray-900">
                {comfort.private_room_percentage}%
              </div>
            </div>
          )}
          <div>
            <div className="text-gray-600">Ensuite Available</div>
            <div className="font-semibold text-gray-900">
              {comfort.ensuite_availability ? 'Yes' : 'No'}
            </div>
          </div>
          <div>
            <div className="text-gray-600">Wheelchair Access</div>
            <div className="font-semibold text-gray-900">
              {comfort.wheelchair_accessible ? 'Yes' : 'No'}
            </div>
          </div>
          <div className="flex items-center gap-1">
            <Wifi className={`w-4 h-4 ${comfort.wifi_available ? 'text-green-600' : 'text-gray-400'}`} />
            <span className={comfort.wifi_available ? 'text-green-700 font-semibold' : 'text-gray-500'}>
              WiFi
            </span>
          </div>
          <div className="flex items-center gap-1">
            <Car className={`w-4 h-4 ${comfort.parking_onsite ? 'text-green-600' : 'text-gray-400'}`} />
            <span className={comfort.parking_onsite ? 'text-green-700 font-semibold' : 'text-gray-500'}>
              Parking
            </span>
          </div>
          <div className="flex items-center gap-1">
            <TreePine className={`w-4 h-4 ${comfort.secure_garden ? 'text-green-600' : 'text-gray-400'}`} />
            <span className={comfort.secure_garden ? 'text-green-700 font-semibold' : 'text-gray-500'}>
              Secure Garden
            </span>
          </div>
        </div>
        {comfort.outdoor_space_description && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <div className="text-xs text-gray-600">Outdoor Space</div>
            <div className="text-xs text-gray-700 mt-1">{comfort.outdoor_space_description}</div>
          </div>
        )}
      </div>

      {/* Room Photos */}
      {comfort.room_photos && comfort.room_photos.length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <ImageIcon className="w-4 h-4 text-gray-600" />
            Room Photos
          </h5>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {comfort.room_photos.slice(0, 6).map((photo, idx) => (
              <div key={idx} className="relative h-32 bg-gray-200 rounded-lg overflow-hidden">
                <img
                  src={photo}
                  alt={`Room ${idx + 1}`}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = 'none';
                  }}
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}


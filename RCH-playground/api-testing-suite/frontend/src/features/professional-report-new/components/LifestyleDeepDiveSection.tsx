import React from 'react';
import { Clock, Calendar, Users, FileText, Sparkles } from 'lucide-react';
import type { ProfessionalCareHome } from '../types';

interface LifestyleDeepDiveSectionProps {
  home: ProfessionalCareHome;
}

export default function LifestyleDeepDiveSection({ home }: LifestyleDeepDiveSectionProps) {
  const lifestyle = home.lifestyleDeepDive;

  if (!lifestyle) {
    return (
      <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
        <p className="text-sm text-gray-500">Lifestyle deep dive data not available</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="w-5 h-5 text-pink-600" />
        <h4 className="text-lg font-semibold text-gray-900">Lifestyle Deep Dive</h4>
      </div>

      {/* Daily Schedule */}
      {lifestyle.daily_schedule && lifestyle.daily_schedule.length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Clock className="w-4 h-4 text-blue-600" />
            Sample Daily Schedule
          </h5>
          <div className="space-y-2">
            {lifestyle.daily_schedule.map((item, idx) => (
              <div key={idx} className="flex items-center gap-3 text-sm">
                <div className="w-16 text-xs font-semibold text-gray-600">{item.time}</div>
                <div className="flex-1 text-gray-700">{item.activity}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Activity Categories */}
      {lifestyle.activity_categories && lifestyle.activity_categories.length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3">Activity Categories</h5>
          <div className="flex flex-wrap gap-2">
            {lifestyle.activity_categories.map((category, idx) => (
              <span key={idx} className="px-3 py-1 bg-pink-50 text-pink-700 rounded-full text-xs font-semibold">
                {category}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Visiting Hours */}
      {lifestyle.visiting_hours && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
            <Calendar className="w-4 h-4 text-green-600" />
            Visiting Hours
          </h5>
          <p className="text-sm text-gray-700">{lifestyle.visiting_hours}</p>
        </div>
      )}

      {/* Personalization */}
      {lifestyle.personalization && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
            <Users className="w-4 h-4 text-purple-600" />
            Personalization & Care Plans
          </h5>
          <p className="text-sm text-gray-700">{lifestyle.personalization}</p>
        </div>
      )}

      {/* Policies */}
      {lifestyle.policies && lifestyle.policies.length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <FileText className="w-4 h-4 text-gray-600" />
            Policies & Procedures
          </h5>
          <div className="space-y-2">
            {lifestyle.policies.map((policy, idx) => (
              <div key={idx} className="border-l-4 border-blue-200 pl-3 py-2 bg-blue-50 rounded-r">
                <div className="text-xs font-semibold text-gray-900 mb-1">{policy.title}</div>
                <div className="text-xs text-gray-700">{policy.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Activities Summary */}
      {lifestyle.activities_summary && (
        <div className="bg-gradient-to-r from-pink-50 to-purple-50 rounded-lg p-4 border border-pink-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-2">Activities Summary</h5>
          {typeof lifestyle.activities_summary === 'string' ? (
            <p className="text-sm text-gray-700">{lifestyle.activities_summary}</p>
          ) : typeof lifestyle.activities_summary === 'object' && lifestyle.activities_summary !== null ? (
            <div className="grid grid-cols-2 gap-3 text-sm">
              {lifestyle.activities_summary.daily_activities_count !== undefined && (
                <div>
                  <span className="font-semibold text-gray-900">Daily Activities: </span>
                  <span className="text-gray-700">{lifestyle.activities_summary.daily_activities_count}</span>
                </div>
              )}
              {lifestyle.activities_summary.weekly_programs_count !== undefined && (
                <div>
                  <span className="font-semibold text-gray-900">Weekly Programs: </span>
                  <span className="text-gray-700">{lifestyle.activities_summary.weekly_programs_count}</span>
                </div>
              )}
              {lifestyle.activities_summary.therapy_programs_count !== undefined && (
                <div>
                  <span className="font-semibold text-gray-900">Therapy Programs: </span>
                  <span className="text-gray-700">{lifestyle.activities_summary.therapy_programs_count}</span>
                </div>
              )}
              {lifestyle.activities_summary.special_events_count !== undefined && (
                <div>
                  <span className="font-semibold text-gray-900">Special Events: </span>
                  <span className="text-gray-700">{lifestyle.activities_summary.special_events_count}</span>
                </div>
              )}
              {lifestyle.activities_summary.one_to_one_available !== undefined && (
                <div className="col-span-2">
                  <span className="font-semibold text-gray-900">One-to-One Available: </span>
                  <span className="text-gray-700">{lifestyle.activities_summary.one_to_one_available ? 'Yes' : 'No'}</span>
                </div>
              )}
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}


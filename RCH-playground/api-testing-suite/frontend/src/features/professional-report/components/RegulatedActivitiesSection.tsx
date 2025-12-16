import React from 'react';
import { BadgeCheck, Stethoscope, Heart, Pill, Activity, FileCheck } from 'lucide-react';
import type { CQCDeepDive } from '../types';

interface RegulatedActivity {
  id?: string;
  name?: string;
  active?: boolean;
  cqc_field?: string;
}

interface LicenseFlags {
  has_nursing_care_license?: boolean;
  has_personal_care_license?: boolean;
  has_surgical_procedures_license?: boolean;
  has_treatment_license?: boolean;
  has_diagnostic_license?: boolean;
}

interface RegulatedActivitiesSectionProps {
  cqcData: CQCDeepDive;
  homeName: string;
}

export default function RegulatedActivitiesSection({ cqcData, homeName }: RegulatedActivitiesSectionProps) {
  const regulatedActivities = (cqcData as any)?.regulated_activities as RegulatedActivity[] | undefined;
  const licenseFlags = (cqcData as any)?.license_flags as LicenseFlags | undefined;

  const hasAnyData = (regulatedActivities && regulatedActivities.length > 0) || licenseFlags;

  if (!hasAnyData) {
    return (
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <div className="flex items-center gap-2">
          <FileCheck className="w-5 h-5 text-gray-400" />
          <p className="text-sm text-gray-500">Regulated activities data not available</p>
        </div>
      </div>
    );
  }

  const getLicenseIcon = (type: string) => {
    switch (type) {
      case 'nursing':
        return <Stethoscope className="w-4 h-4" />;
      case 'personal':
        return <Heart className="w-4 h-4" />;
      case 'treatment':
        return <Pill className="w-4 h-4" />;
      case 'diagnostic':
        return <Activity className="w-4 h-4" />;
      default:
        return <BadgeCheck className="w-4 h-4" />;
    }
  };

  const licenses = [
    {
      key: 'has_nursing_care_license',
      name: 'Nursing Care',
      type: 'nursing',
      description: 'Licensed to provide nursing care by registered nurses',
      value: licenseFlags?.has_nursing_care_license
    },
    {
      key: 'has_personal_care_license',
      name: 'Personal Care',
      type: 'personal',
      description: 'Licensed to provide personal care support',
      value: licenseFlags?.has_personal_care_license
    },
    {
      key: 'has_treatment_license',
      name: 'Treatment of Disease',
      type: 'treatment',
      description: 'Licensed to provide treatment for diseases and disorders',
      value: licenseFlags?.has_treatment_license
    },
    {
      key: 'has_diagnostic_license',
      name: 'Diagnostic Procedures',
      type: 'diagnostic',
      description: 'Licensed to perform diagnostic and screening procedures',
      value: licenseFlags?.has_diagnostic_license
    },
    {
      key: 'has_surgical_procedures_license',
      name: 'Surgical Procedures',
      type: 'surgical',
      description: 'Licensed to perform surgical procedures',
      value: licenseFlags?.has_surgical_procedures_license
    }
  ];

  const activeLicenses = licenses.filter(l => l.value === true);
  const inactiveLicenses = licenses.filter(l => l.value === false);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <BadgeCheck className="w-5 h-5 text-purple-600" />
        <h4 className="text-lg font-semibold text-gray-900">Regulated Activities & Licenses</h4>
      </div>

      {licenseFlags && (
        <div className="space-y-3">
          <h5 className="text-sm font-semibold text-gray-700">CQC License Status</h5>
          
          {activeLicenses.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {activeLicenses.map((license) => (
                <div
                  key={license.key}
                  className="flex items-start gap-3 p-3 bg-green-50 border border-green-200 rounded-lg"
                >
                  <div className="mt-0.5 text-green-600">
                    {getLicenseIcon(license.type)}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-green-800">{license.name}</span>
                      <span className="px-1.5 py-0.5 text-xs font-medium bg-green-100 text-green-700 rounded">
                        Active
                      </span>
                    </div>
                    <p className="text-xs text-green-600 mt-0.5">{license.description}</p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {inactiveLicenses.length > 0 && (
            <div className="mt-3">
              <p className="text-xs text-gray-500 mb-2">Not licensed for:</p>
              <div className="flex flex-wrap gap-2">
                {inactiveLicenses.map((license) => (
                  <span
                    key={license.key}
                    className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full"
                  >
                    {license.name}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {regulatedActivities && regulatedActivities.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <h5 className="text-sm font-semibold text-gray-700 mb-3">Registered Activities</h5>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {regulatedActivities.map((activity, idx) => (
              <div
                key={idx}
                className={`flex items-center justify-between p-2 rounded-lg ${
                  activity.active !== false
                    ? 'bg-blue-50 border border-blue-100'
                    : 'bg-gray-50 border border-gray-100'
                }`}
              >
                <div className="flex items-center gap-2">
                  <BadgeCheck
                    className={`w-4 h-4 ${
                      activity.active !== false ? 'text-blue-600' : 'text-gray-400'
                    }`}
                  />
                  <span className={`text-sm ${
                    activity.active !== false ? 'text-blue-800' : 'text-gray-600'
                  }`}>
                    {activity.name || activity.id || 'Unknown Activity'}
                  </span>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  activity.active !== false
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-gray-100 text-gray-500'
                }`}>
                  {activity.active !== false ? 'Active' : 'Inactive'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="text-xs text-gray-500 mt-3 p-3 bg-gray-50 rounded-lg">
        <strong>Why does this matter?</strong> CQC regulated activities determine what types of care 
        a home is legally permitted to provide. Ensure the home has the appropriate licenses for 
        your loved one's specific care needs.
      </div>
    </div>
  );
}

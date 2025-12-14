import React from 'react';
import { Heart, Stethoscope, Activity, CheckCircle2 } from 'lucide-react';
import type { ProfessionalCareHome } from '../types';

interface MedicalCareSectionProps {
  home: ProfessionalCareHome;
}

export default function MedicalCareSection({ home }: MedicalCareSectionProps) {
  const medicalCare = home.medicalCare;

  if (!medicalCare) {
    return (
      <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
        <p className="text-sm text-gray-500">Medical care data not available</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <Heart className="w-5 h-5 text-red-600" />
        <h4 className="text-lg font-semibold text-gray-900">Medical Care & Specialisms</h4>
      </div>

      {/* Care Types */}
      <div className="bg-white rounded-lg p-4 border border-gray-200">
        <h5 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <Activity className="w-4 h-4 text-blue-600" />
          Care Types Provided
        </h5>
        <div className="flex flex-wrap gap-2">
          {medicalCare.care_residential && (
            <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-semibold">
              Residential Care
            </span>
          )}
          {medicalCare.care_nursing && (
            <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">
              Nursing Care
            </span>
          )}
          {medicalCare.care_dementia && (
            <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-semibold">
              Dementia Care
            </span>
          )}
        </div>
      </div>

      {/* Medical Specialisms */}
      {medicalCare.medical_specialisms && medicalCare.medical_specialisms.length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Stethoscope className="w-4 h-4 text-red-600" />
            Medical Specialisms
          </h5>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {medicalCare.medical_specialisms.map((specialism, idx) => (
              <div key={idx} className="flex items-center gap-2 text-sm text-gray-700">
                <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0" />
                <span>{specialism}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Regulated Activities */}
      {medicalCare.regulated_activities && medicalCare.regulated_activities.length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3">Regulated Activities (CQC)</h5>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {medicalCare.regulated_activities.map((activity, idx) => (
              <div key={idx} className="flex items-center gap-2 text-sm text-gray-700">
                <CheckCircle2 className="w-4 h-4 text-blue-600 flex-shrink-0" />
                <span>{activity}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Service Types */}
      {medicalCare.service_types && medicalCare.service_types.length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3">Service Types</h5>
          <div className="flex flex-wrap gap-2">
            {medicalCare.service_types.map((service, idx) => (
              <span
                key={idx}
                className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
              >
                {service}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}


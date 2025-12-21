/**
 * DomainAssessmentSection - Assessment of 12 DST care domains
 * 
 * Allows user to select assessment level for each of 12 domains:
 * 1. Breathing 2. Mobility 3. Cognitive 4. Continence
 * 5. Skin 6. Eating 7. Safety 8. Behaviour
 * 9. Medications 10. Social 11. Autonomy 12. Relationships
 */

import React from 'react';
import {
  Domain,
  DomainLevel,
  DomainAssessmentSectionProps,
} from '../../types/funding.types';
import { FormSection } from './FormSection';

const DOMAIN_LABELS: Record<Domain, string> = {
  [Domain.Breathing]: 'Breathing & Respiratory Support',
  [Domain.Mobility]: 'Mobility (Moving Around)',
  [Domain.Cognitive]: 'Cognitive (Thinking & Memory)',
  [Domain.Continence]: 'Continence (Toileting)',
  [Domain.Skin]: 'Skin Integrity (Pressure Wounds)',
  [Domain.Eating]: 'Eating & Swallowing',
  [Domain.Safety]: 'Safety (Preventing Harm)',
  [Domain.Behaviour]: 'Behaviour (Managing Self & Others)',
  [Domain.Medications]: 'Medications (Managing Drugs)',
  [Domain.Social]: 'Social (Relationships & Roles)',
  [Domain.Autonomy]: 'Autonomy (Life Decisions)',
  [Domain.Relationships]: 'Relationships & Support',
};

const LEVEL_COLORS: Record<DomainLevel, string> = {
  [DomainLevel.Independent]: 'bg-green-50 border-green-200',
  [DomainLevel.Low]: 'bg-blue-50 border-blue-200',
  [DomainLevel.Medium]: 'bg-yellow-50 border-yellow-200',
  [DomainLevel.High]: 'bg-orange-50 border-orange-200',
  [DomainLevel.Severe]: 'bg-red-50 border-red-200',
  [DomainLevel.Priority]: 'bg-red-100 border-red-400',
};

export function DomainAssessmentSection({
  domains,
  onChange,
  errors,
}: DomainAssessmentSectionProps) {
  const domainList = Object.values(Domain);

  return (
    <FormSection
      title="12 DST Care Domains Assessment"
      description="Select assessment level for each care domain (Independent → Priority)"
    >
      <div className="space-y-4">
        {domainList.map((domain) => (
          <div key={domain} className="space-y-2">
            <label className="text-sm font-medium text-gray-700">
              {DOMAIN_LABELS[domain]}
            </label>
            <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
              {Object.values(DomainLevel).map((level) => (
                <button
                  key={level}
                  onClick={() => onChange(domain, level)}
                  className={`px-2 py-2 text-xs font-medium rounded border transition-colors ${
                    domains[domain] === level
                      ? `${LEVEL_COLORS[level]} ring-2 ring-offset-1 ring-gray-400`
                      : `${LEVEL_COLORS[level]} opacity-50 hover:opacity-100`
                  }`}
                >
                  {level.charAt(0).toUpperCase() + level.slice(1)}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
      {errors?.domains && (
        <p className="text-sm text-red-600 mt-2">{errors.domains}</p>
      )}
    </FormSection>
  );
}

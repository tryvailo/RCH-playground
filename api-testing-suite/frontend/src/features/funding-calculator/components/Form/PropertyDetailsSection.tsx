/**
 * PropertyDetailsSection - Property information for means test
 * 
 * Collects:
 * - Property value
 * - Ownership status
 * - DPA disregard eligibility
 * - Disregard date
 */

import React from 'react';
import { PropertyDetailsSectionProps } from '../../types/funding.types';
import { FormSection } from './FormSection';

export function PropertyDetailsSection({
  details,
  onChange,
  errors,
}: PropertyDetailsSectionProps) {
  const handleChange = (field: string, value: any) => {
    onChange({
      ...details || {
        value: 0,
        ownership: 'sole_owner',
        disregardEligible: false,
      },
      [field]: value,
    } as any);
  };

  return (
    <FormSection
      title="Property Details (for Means Test)"
      description="Information about property value and ownership status"
    >
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Property Value (GBP)
          </label>
          <input
            type="number"
            min="0"
            step="10000"
            value={details?.value || 0}
            onChange={(e) => handleChange('value', parseFloat(e.target.value) || 0)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., 250000"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Ownership Status
          </label>
          <select
            value={details?.ownership || 'sole_owner'}
            onChange={(e) => handleChange('ownership', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="sole_owner">Sole Owner</option>
            <option value="joint">Joint Owner</option>
            <option value="none">No Property</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="dpa_disregard"
            checked={details?.disregardEligible || false}
            onChange={(e) => handleChange('disregardEligible', e.target.checked)}
            className="w-4 h-4 rounded border-gray-300"
          />
          <label htmlFor="dpa_disregard" className="text-sm text-gray-700">
            Eligible for DPA (property disregard)
          </label>
        </div>

        {details?.disregardEligible && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              DPA Disregard Date
            </label>
            <input
              type="date"
              value={details?.disregardDate || ''}
              onChange={(e) => handleChange('disregardDate', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
        )}
      </div>
      {errors?.property && (
        <p className="text-sm text-red-600 mt-2">{errors.property}</p>
      )}
    </FormSection>
  );
}

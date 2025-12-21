/**
 * DPAEligibilityCard - Display DPA (Deferred Payment Agreement) eligibility
 * 
 * Shows:
 * - Is eligible
 * - Property disregarded
 * - Qualifying relatives
 * - Implications
 */

import React from 'react';
import { Home, CheckCircle, XCircle } from 'lucide-react';
import { DPAResult } from '../../types/funding.types';
import { ResultCard } from '../Common/ResultCard';

interface DPAEligibilityCardProps {
  result: DPAResult;
  className?: string;
}

export function DPAEligibilityCard({
  result,
  className = '',
}: DPAEligibilityCardProps) {
  return (
    <ResultCard
      title="Deferred Payment Agreement (DPA)"
      icon={<Home className="w-5 h-5 text-blue-600" />}
      status={result.is_eligible ? 'success' : 'danger'}
      className={className}
    >
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          {result.is_eligible ? (
            <CheckCircle className="w-5 h-5 text-green-600" />
          ) : (
            <XCircle className="w-5 h-5 text-red-600" />
          )}
          <span className="font-semibold text-gray-900">
            {result.is_eligible ? 'Eligible' : 'Not Eligible'}
          </span>
        </div>

        <div className="space-y-2 text-xs">
          <div className="flex items-center justify-between p-2 bg-white/50 rounded border border-gray-200">
            <span>Property Disregarded:</span>
            <span className="font-semibold">
              {result.property_disregarded ? '✓ Yes' : '✗ No'}
            </span>
          </div>

          <div className="flex items-center justify-between p-2 bg-white/50 rounded border border-gray-200">
            <span>Qualifying Relatives:</span>
            <span className="font-semibold">
              {result.qualifying_relatives ? '✓ Yes' : '✗ No'}
            </span>
          </div>
        </div>

        {result.reason && (
          <p className="text-xs text-gray-600 italic border-t border-gray-300 pt-2">
            {result.reason}
          </p>
        )}

        {result.is_eligible && (
          <div className="bg-green-50 border border-green-200 rounded p-2">
            <p className="text-xs text-green-700">
              <strong>Note:</strong> If eligible, home can be disregarded for
              means test under DPA scheme
            </p>
          </div>
        )}
      </div>
    </ResultCard>
  );
}

/**
 * FundingResultsContainer - Orchestrate all result cards
 * 
 * Displays:
 * - CHC eligibility
 * - LA funding
 * - DPA eligibility
 * - Savings
 * - Local Authority info
 * - Loading and error states
 */

import React from 'react';
import { Download, Share2 } from 'lucide-react';
import { FundingEligibilityResult } from '../../types/funding.types';
import { CHCEligibilityCard } from './CHCEligibilityCard';
import { LAFundingCard } from './LAFundingCard';
import { DPAEligibilityCard } from './DPAEligibilityCard';
import { SavingsCard } from './SavingsCard';
import { LocalAuthorityCard } from './LocalAuthorityCard';
import { LoadingSpinner, ErrorAlert } from '../Common';

interface FundingResultsContainerProps {
  result: FundingEligibilityResult | null;
  isLoading?: boolean;
  error?: Error | string | null;
  onBack?: () => void;
  onExport?: () => void;
  onShare?: () => void;
}

export function FundingResultsContainer({
  result,
  isLoading = false,
  error = null,
  onBack,
  onExport,
  onShare,
}: FundingResultsContainerProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-8">
        <LoadingSpinner message="Calculating funding eligibility..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <ErrorAlert error={error} />
      </div>
    );
  }

  if (!result) {
    return null;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">
          Funding Assessment Results
        </h2>
        <div className="flex gap-2">
          {onExport && (
            <button
              onClick={onExport}
              className="px-3 py-2 bg-blue-50 text-blue-600 hover:bg-blue-100 rounded-lg font-medium text-sm flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
          )}
          {onShare && (
            <button
              onClick={onShare}
              className="px-3 py-2 bg-gray-100 text-gray-700 hover:bg-gray-200 rounded-lg font-medium text-sm flex items-center gap-2"
            >
              <Share2 className="w-4 h-4" />
              Share
            </button>
          )}
        </div>
      </div>

      <p className="text-sm text-gray-600">
        Assessment Date:{' '}
        {new Date(result.assessed_at).toLocaleDateString('en-GB', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
        })}
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <CHCEligibilityCard result={result.chc} />
        <LAFundingCard result={result.la} />
        <DPAEligibilityCard result={result.dpa} />
        <SavingsCard result={result.savings} />
      </div>

      <LocalAuthorityCard result={result} />

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-2">Important Notes</h3>
        <ul className="text-sm text-blue-800 space-y-1 ml-4">
          <li>• This calculator provides an estimate based on information provided</li>
          <li>• A formal assessment by NHS/LA is required for final eligibility</li>
          <li>• CHC probability is capped at 98% (never 100% for safety)</li>
          <li>
            • Means test based on 2025-2026 thresholds (may change annually)
          </li>
          <li>• DPA rules can vary between local authorities</li>
        </ul>
      </div>

      {onBack && (
        <button
          onClick={onBack}
          className="px-4 py-2 text-blue-600 hover:text-blue-800 font-medium text-sm"
        >
          ← Back to Form
        </button>
      )}
    </div>
  );
}

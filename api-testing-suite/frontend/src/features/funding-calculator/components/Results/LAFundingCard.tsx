/**
 * LAFundingCard - Display Local Authority funding results
 * 
 * Shows:
 * - Full support probability
 * - Top-up required probability
 * - Funding level determination
 * - Capital assessment
 * - Income assessment
 */

import React from 'react';
import { DollarSign } from 'lucide-react';
import { LASupportResult } from '../../types/funding.types';
import { ResultCard } from '../Common/ResultCard';

interface LAFundingCardProps {
  result: LASupportResult;
  className?: string;
}

const getFundingStatus = (
  level: string
): 'success' | 'warning' | 'danger' => {
  switch (level) {
    case 'FULL':
      return 'success';
    case 'PARTIAL':
      return 'warning';
    default:
      return 'danger';
  }
};

const getFundingLabel = (level: string): string => {
  switch (level) {
    case 'FULL':
      return 'Full Support Available';
    case 'PARTIAL':
      return 'Partial Support (Top-up Required)';
    default:
      return 'No LA Support (Self-Funding)';
  }
};

export function LAFundingCard({
  result,
  className = '',
}: LAFundingCardProps) {
  const fundingStatus = getFundingStatus(result.funding_level);
  const fundingLabel = getFundingLabel(result.funding_level);

  return (
    <ResultCard
      title="Local Authority Funding"
      icon={<DollarSign className="w-5 h-5 text-green-600" />}
      status={fundingStatus}
      className={className}
    >
      <div className="space-y-3">
        <div className="bg-white/50 rounded p-2 border border-current">
          <p className="text-xs font-medium">{fundingLabel}</p>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div>
            <p className="text-xs text-gray-600">Full Support Probability</p>
            <p className="font-semibold text-gray-900">
              {(result.full_support_probability * 100).toFixed(0)}%
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-600">Top-up Probability</p>
            <p className="font-semibold text-gray-900">
              {(result.top_up_probability * 100).toFixed(0)}%
            </p>
          </div>
        </div>

        {result.capital_assessment && (
          <div>
            <p className="text-xs text-gray-600 mb-1">Capital Assessment</p>
            <div className="text-xs bg-white/50 p-2 rounded border border-gray-200">
              <p className="font-medium">
                Level: {result.capital_assessment.level}
              </p>
              <p className="text-gray-600">
                Capital: £
                {(result.capital_assessment.capital || 0).toLocaleString()}
              </p>
            </div>
          </div>
        )}

        {result.income_assessment && (
          <div>
            <p className="text-xs text-gray-600 mb-1">Income Assessment</p>
            <div className="text-xs bg-white/50 p-2 rounded border border-gray-200">
              <p className="font-medium">
                Weekly Income: £
                {(
                  result.income_assessment.total_income || 0
                ).toFixed(2)}
              </p>
              <p className="text-gray-600">
                Tariff Income: £
                {(
                  result.income_assessment.tariff_income || 0
                ).toFixed(2)}/week
              </p>
            </div>
          </div>
        )}

        <div className="text-xs text-gray-500 italic">
          Based on 2025-2026 means test thresholds
        </div>
      </div>
    </ResultCard>
  );
}

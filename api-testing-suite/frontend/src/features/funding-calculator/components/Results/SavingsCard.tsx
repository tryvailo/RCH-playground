/**
 * SavingsCard - Display financial savings calculations
 * 
 * Shows:
 * - Weekly savings
 * - Annual savings
 * - 5-year savings
 * - Lifetime savings
 */

import React from 'react';
import { TrendingUp } from 'lucide-react';
import { SavingsResult } from '../../types/funding.types';
import { ResultCard } from '../Common/ResultCard';

interface SavingsCardProps {
  result: SavingsResult;
  className?: string;
}

const formatCurrency = (value: number): string => {
  return `£${value.toLocaleString('en-GB', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  })}`;
};

export function SavingsCard({
  result,
  className = '',
}: SavingsCardProps) {
  const weeklySavings = result.weekly_savings > 0;

  return (
    <ResultCard
      title="Potential Financial Savings"
      icon={<TrendingUp className="w-5 h-5 text-green-600" />}
      value={weeklySavings ? formatCurrency(result.weekly_savings) : '—'}
      status={weeklySavings ? 'success' : 'info'}
      className={className}
    >
      <div className="space-y-3">
        {weeklySavings ? (
          <>
            <div className="text-xs text-gray-600">
              <p className="font-medium text-gray-900">
                {formatCurrency(result.weekly_savings)} per week
              </p>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div className="bg-white/50 p-2 rounded border border-gray-200">
                <p className="text-xs text-gray-600">Annual</p>
                <p className="font-semibold text-gray-900">
                  {formatCurrency(result.annual_savings)}
                </p>
              </div>

              <div className="bg-white/50 p-2 rounded border border-gray-200">
                <p className="text-xs text-gray-600">5-Year</p>
                <p className="font-semibold text-gray-900">
                  {formatCurrency(result.five_year_savings)}
                </p>
              </div>
            </div>

            {result.lifetime_savings > 0 && (
              <div className="bg-white/50 p-2 rounded border border-gray-200">
                <p className="text-xs text-gray-600">Lifetime (est.)</p>
                <p className="font-semibold text-gray-900">
                  {formatCurrency(result.lifetime_savings)}
                </p>
              </div>
            )}

            <p className="text-xs text-gray-500 italic border-t border-gray-300 pt-2">
              Savings calculated if CHC or LA funding eligible
            </p>
          </>
        ) : (
          <p className="text-xs text-gray-600">
            No savings available based on current assessment
          </p>
        )}
      </div>
    </ResultCard>
  );
}

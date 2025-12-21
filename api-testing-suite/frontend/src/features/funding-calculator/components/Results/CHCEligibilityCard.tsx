/**
 * CHCEligibilityCard - Display NHS CHC eligibility results
 * 
 * Shows:
 * - Probability percentage (0-98%)
 * - Likelihood category
 * - Key factors (Priority/Severe domains)
 * - Domain scores
 * - Recommendation
 */

import React from 'react';
import { Heart, TrendingUp } from 'lucide-react';
import { CHCEligibilityResult } from '../../types/funding.types';
import { ResultCard } from '../Common/ResultCard';

interface CHCEligibilityCardProps {
  result: CHCEligibilityResult;
  className?: string;
}

const getCategoryColor = (
  probability: number
): 'success' | 'warning' | 'danger' | 'info' => {
  if (probability >= 92) return 'danger';
  if (probability >= 70) return 'warning';
  if (probability >= 20) return 'info';
  return 'success';
};

const getCategory = (probability: number): string => {
  if (probability >= 92) return 'Very High';
  if (probability >= 70) return 'High';
  if (probability >= 20) return 'Moderate';
  return 'Low';
};

export function CHCEligibilityCard({
  result,
  className = '',
}: CHCEligibilityCardProps) {
  const category = getCategory(result.probability_percent);
  const status = getCategoryColor(result.probability_percent);

  return (
    <ResultCard
      title="NHS CHC Eligibility"
      icon={<Heart className="w-5 h-5 text-red-600" />}
      value={`${result.probability_percent}%`}
      status={status}
      className={className}
    >
      <div className="space-y-3">
        <div>
          <p className="text-xs text-gray-600">Likelihood Category</p>
          <p className="font-semibold text-gray-900">{category}</p>
        </div>

        {result.is_likely_eligible && (
          <div className="bg-white/50 rounded p-2 border border-green-200">
            <p className="text-xs font-medium text-green-700">
              ✓ Likely CHC Eligible (≥70%)
            </p>
          </div>
        )}

        <div>
          <p className="text-xs text-gray-600 mb-1">Key Factors</p>
          <ul className="space-y-1">
            {result.key_factors.slice(0, 3).map((factor, idx) => (
              <li
                key={idx}
                className="text-xs text-gray-700 flex items-start gap-2"
              >
                <span className="text-blue-600 font-bold mt-0.5">•</span>
                {factor}
              </li>
            ))}
            {result.key_factors.length > 3 && (
              <li className="text-xs text-gray-500">
                +{result.key_factors.length - 3} more factors
              </li>
            )}
          </ul>
        </div>

        <div>
          <p className="text-xs text-gray-600 mb-1">Domain Scores</p>
          <div className="grid grid-cols-2 gap-1">
            {Object.entries(result.domain_scores)
              .slice(0, 4)
              .map(([domain, score]) => (
                <div
                  key={domain}
                  className="text-xs bg-white/50 p-1 rounded border border-gray-200"
                >
                  <span className="font-medium capitalize">{domain}:</span>{' '}
                  {score}%
                </div>
              ))}
          </div>
        </div>

        <p className="text-xs text-gray-600 italic border-t border-gray-300 pt-2">
          {result.reasoning}
        </p>
      </div>
    </ResultCard>
  );
}

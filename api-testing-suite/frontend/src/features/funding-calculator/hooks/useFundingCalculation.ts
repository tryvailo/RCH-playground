/**
 * useFundingCalculation - Handle API calls and calculation logic
 * 
 * Features:
 * - POST to /api/rch-data/funding/calculate
 * - Cache results locally
 * - Handle errors
 * - Loading states
 */

import { useState, useCallback } from 'react';
import axios from 'axios';
import { FormData, FundingEligibilityResult } from '../types/funding.types';

export function useFundingCalculation() {
  const [result, setResult] = useState<FundingEligibilityResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [lastFormData, setLastFormData] = useState<FormData | null>(null);

  const calculate = useCallback(
    async (formData: FormData): Promise<FundingEligibilityResult | null> => {
      setIsLoading(true);
      setError(null);

      try {
        // Build request payload
        const requestData = {
          age: formData.age,
          domain_assessments: formData.domainAssessments,
          capital_assets: formData.capitalAssets,
          weekly_income: formData.weeklyIncome,
          is_couple: formData.isCouple,
          property: formData.propertyDetails
            ? {
                value: formData.propertyDetails.value,
                ownership: formData.propertyDetails.ownership,
                disregard_eligible: formData.propertyDetails.disregardEligible,
              }
            : null,
          income_disregards: formData.incomeDisregards,
          asset_disregards: formData.assetDisregards,
        };

        const response = await axios.post<FundingEligibilityResult>(
          '/api/rch-data/funding/calculate',
          requestData
        );

        setResult(response.data);
        setLastFormData(formData);
        return response.data;
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Calculation failed');
        setError(error);
        console.error('Calculation error:', error);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const clear = useCallback(() => {
    setResult(null);
    setError(null);
    setLastFormData(null);
  }, []);

  const retry = useCallback(async () => {
    if (lastFormData) {
      return calculate(lastFormData);
    }
    return null;
  }, [lastFormData, calculate]);

  return {
    result,
    isLoading,
    error,
    calculate,
    clear,
    retry,
  };
}

export type UseFundingCalculationReturn = ReturnType<
  typeof useFundingCalculation
>;

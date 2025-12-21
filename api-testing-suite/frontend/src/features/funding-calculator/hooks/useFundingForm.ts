/**
 * useFundingForm - Custom hook for funding calculator form state
 * 
 * Manages:
 * - Domain assessments (12 domains)
 * - Property details
 * - Income disregards
 * - Asset disregards
 * - Form validation errors
 * - Form modification tracking
 */

import { useState, useCallback } from 'react';
import {
  FormData,
  FormErrors,
  Domain,
  DomainLevel,
  DomainAssessments,
  PropertyDetails,
  IncomeDisregard,
  AssetDisregard,
} from '../types/funding.types';

// Initial form state
const getInitialFormData = (): FormData => ({
  domainAssessments: {
    [Domain.Breathing]: DomainLevel.Independent,
    [Domain.Mobility]: DomainLevel.Independent,
    [Domain.Cognitive]: DomainLevel.Independent,
    [Domain.Continence]: DomainLevel.Independent,
    [Domain.Skin]: DomainLevel.Independent,
    [Domain.Eating]: DomainLevel.Independent,
    [Domain.Safety]: DomainLevel.Independent,
    [Domain.Behaviour]: DomainLevel.Independent,
    [Domain.Medications]: DomainLevel.Independent,
    [Domain.Social]: DomainLevel.Independent,
    [Domain.Autonomy]: DomainLevel.Independent,
    [Domain.Relationships]: DomainLevel.Independent,
  } as DomainAssessments,
  propertyDetails: null,
  incomeDisregards: [],
  assetDisregards: [],
  isCouple: false,
  age: 65,
  capitalAssets: 0,
  weeklyIncome: 0,
});

export function useFundingForm(initialData?: Partial<FormData>) {
  const [formData, setFormData] = useState<FormData>({
    ...getInitialFormData(),
    ...initialData,
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isModified, setIsModified] = useState(false);

  const updateField = useCallback(
    (field: keyof FormData, value: any) => {
      setFormData((prev) => ({
        ...prev,
        [field]: value,
      }));
      setIsModified(true);
    },
    []
  );

  const updateDomainLevel = useCallback(
    (domain: Domain, level: DomainLevel) => {
      setFormData((prev) => ({
        ...prev,
        domainAssessments: {
          ...prev.domainAssessments,
          [domain]: level,
        },
      }));
      setIsModified(true);
    },
    []
  );

  const updatePropertyDetails = useCallback(
    (details: PropertyDetails) => {
      setFormData((prev) => ({
        ...prev,
        propertyDetails: details,
      }));
      setIsModified(true);
    },
    []
  );

  const updateIncomeDisregards = useCallback(
    (disregards: IncomeDisregard[]) => {
      setFormData((prev) => ({
        ...prev,
        incomeDisregards: disregards,
      }));
      setIsModified(true);
    },
    []
  );

  const updateAssetDisregards = useCallback(
    (disregards: AssetDisregard[]) => {
      setFormData((prev) => ({
        ...prev,
        assetDisregards: disregards,
      }));
      setIsModified(true);
    },
    []
  );

  const reset = useCallback(() => {
    setFormData(getInitialFormData());
    setErrors({});
    setIsModified(false);
  }, []);

  const clearErrors = useCallback(() => {
    setErrors({});
  }, []);

  const setFieldError = useCallback((field: string, error: string | undefined) => {
    setErrors((prev) => ({
      ...prev,
      [field]: error,
    }));
  }, []);

  return {
    formData,
    errors,
    isModified,
    updateField,
    updateDomainLevel,
    updatePropertyDetails,
    updateIncomeDisregards,
    updateAssetDisregards,
    reset,
    setErrors,
    clearErrors,
    setFieldError,
  };
}

export type UseFundingFormReturn = ReturnType<typeof useFundingForm>;

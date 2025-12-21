/**
 * useFormValidation - Form field validation
 * 
 * Validates:
 * - Age: 18-110
 * - Capital: 0-1,000,000
 * - Weekly income: 0-5,000
 * - Property value: 0-5,000,000
 * - At least 1 domain assessed
 */

import { useState, useCallback } from 'react';
import { FormData, FormErrors } from '../types/funding.types';

const VALIDATION_RULES = {
  age: { min: 18, max: 110 },
  capital: { min: 0, max: 1_000_000 },
  income: { min: 0, max: 5_000 },
  property: { min: 0, max: 5_000_000 },
};

export function useFormValidation(formData: FormData) {
  const [errors, setErrors] = useState<FormErrors>({});

  const validateField = useCallback((field: string, value: any): string | undefined => {
    switch (field) {
      case 'age':
        if (value < VALIDATION_RULES.age.min || value > VALIDATION_RULES.age.max) {
          return `Age must be between ${VALIDATION_RULES.age.min} and ${VALIDATION_RULES.age.max}`;
        }
        break;

      case 'capitalAssets':
        if (value < VALIDATION_RULES.capital.min || value > VALIDATION_RULES.capital.max) {
          return `Capital must be between £0 and £${VALIDATION_RULES.capital.max.toLocaleString()}`;
        }
        break;

      case 'weeklyIncome':
        if (value < VALIDATION_RULES.income.min || value > VALIDATION_RULES.income.max) {
          return `Weekly income must be between £0 and £${VALIDATION_RULES.income.max}`;
        }
        break;

      case 'propertyValue':
        if (formData.propertyDetails?.value !== undefined) {
          const val = formData.propertyDetails.value;
          if (val < VALIDATION_RULES.property.min || val > VALIDATION_RULES.property.max) {
            return `Property value must be between £0 and £${VALIDATION_RULES.property.max.toLocaleString()}`;
          }
        }
        break;

      case 'domains':
        const assessedDomains = Object.values(formData.domainAssessments).filter(
          (level) => level !== 'independent'
        ).length;
        if (assessedDomains === 0) {
          return 'At least one domain must be assessed above Independent level';
        }
        break;
    }
    return undefined;
  }, [formData]);

  const validate = useCallback((): boolean => {
    const newErrors: FormErrors = {};

    // Validate age
    const ageError = validateField('age', formData.age);
    if (ageError) newErrors.age = ageError;

    // Validate capital
    const capitalError = validateField('capitalAssets', formData.capitalAssets);
    if (capitalError) newErrors.capital = capitalError;

    // Validate income
    const incomeError = validateField('weeklyIncome', formData.weeklyIncome);
    if (incomeError) newErrors.income = incomeError;

    // Validate property
    if (formData.propertyDetails) {
      const propertyError = validateField('propertyValue', formData.propertyDetails.value);
      if (propertyError) newErrors.property = propertyError;
    }

    // Validate domains
    const domainsError = validateField('domains', null);
    if (domainsError) newErrors.domains = domainsError;

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formData, validateField]);

  return {
    errors,
    isValid: Object.keys(errors).length === 0,
    validate,
    validateField,
    setErrors,
  };
}

export type UseFormValidationReturn = ReturnType<typeof useFormValidation>;

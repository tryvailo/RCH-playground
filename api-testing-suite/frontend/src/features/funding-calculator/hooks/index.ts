/**
 * Funding Calculator Custom Hooks
 * 
 * - useFundingForm: Form state management
 * - useFundingCalculation: API calls & calculation
 * - useFormValidation: Form field validation
 * - useErrorHandling: Error management
 * - useFundingCache: Result caching
 */

export { useFundingForm } from './useFundingForm';
export type { UseFundingFormReturn } from './useFundingForm';

export { useFormValidation } from './useFormValidation';
export type { UseFormValidationReturn } from './useFormValidation';

export { useFundingCalculation } from './useFundingCalculation';
export type { UseFundingCalculationReturn } from './useFundingCalculation';

export { useErrorHandling } from './useErrorHandling';
export type { UseErrorHandlingReturn } from './useErrorHandling';

export { useFundingCache } from './useFundingCache';
export type { UseFundingCacheReturn } from './useFundingCache';

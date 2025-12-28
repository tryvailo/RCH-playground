/**
 * Common Types
 * Shared types across the application
 */

export interface ValidationError {
  field: string;
  message: string;
}

export interface ValidationResult<T> {
  isValid: boolean;
  errors: ValidationError[];
  data?: T;
}

export interface CacheEntry<T> {
  data: T;
  expiresAt: number;
}




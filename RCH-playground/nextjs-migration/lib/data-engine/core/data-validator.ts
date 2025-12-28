/**
 * Data Validator
 * Validates questionnaires and care home data
 */

import { z } from 'zod';
import { CareHome } from '@/lib/shared/types/care-home';
import { ValidationResult, ValidationError } from '@/lib/shared/types/common';

// Questionnaire validation schema
const questionnaireSchema = z.object({
  postcode: z.string().min(6).max(7),
  budget: z.number().min(0).max(10000).optional(),
  care_type: z.enum(['residential', 'nursing', 'dementia', 'respite']).optional(),
  chc_probability: z.number().min(0).max(100).optional(),
  max_distance_km: z.number().min(0).max(100).optional(),
});

export class DataValidator {
  /**
   * Validate questionnaire
   * 
   * @param questionnaire Questionnaire data
   * @throws ZodError if validation fails
   */
  validateQuestionnaire(questionnaire: any): void {
    questionnaireSchema.parse(questionnaire);
  }

  /**
   * Validate care homes
   * 
   * @param homes Array of care homes
   * @returns Validation result with valid and invalid homes
   */
  validateHomes(homes: CareHome[]): ValidationResult<CareHome[]> {
    const validHomes: CareHome[] = [];
    const invalidHomes: CareHome[] = [];
    const errors: ValidationError[] = [];

    for (const home of homes) {
      const validation = this.validateHome(home);
      if (validation.isValid) {
        validHomes.push(home);
      } else {
        invalidHomes.push(home);
        errors.push(...validation.errors);
      }
    }

    return {
      isValid: invalidHomes.length === 0,
      errors,
      data: validHomes,
    };
  }

  /**
   * Validate single care home
   * 
   * @param home Care home to validate
   * @returns Validation result
   */
  private validateHome(home: CareHome): ValidationResult<CareHome> {
    const errors: ValidationError[] = [];

    if (!home.name || typeof home.name !== 'string' || home.name.trim().length === 0) {
      errors.push({ field: 'name', message: 'Missing or invalid name' });
    }

    if (!home.postcode || typeof home.postcode !== 'string' || home.postcode.trim().length === 0) {
      errors.push({ field: 'postcode', message: 'Missing or invalid postcode' });
    }

    // Validate coordinates if present
    if (home.latitude !== undefined || home.longitude !== undefined) {
      if (home.latitude === undefined || home.longitude === undefined) {
        errors.push({ field: 'coordinates', message: 'Both latitude and longitude must be provided' });
      } else {
        if (!(-90 <= home.latitude && home.latitude <= 90)) {
          errors.push({ field: 'latitude', message: 'Latitude must be between -90 and 90' });
        }
        if (!(-180 <= home.longitude && home.longitude <= 180)) {
          errors.push({ field: 'longitude', message: 'Longitude must be between -180 and 180' });
        }
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      data: errors.length === 0 ? home : undefined,
    };
  }
}




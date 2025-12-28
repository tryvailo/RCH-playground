/**
 * Category Calculators
 * Main exports for all calculators
 */

import { MedicalCalculator } from './medical';
import { SafetyCalculator } from './safety';
import { LocationCalculator } from './location';
import { FinancialCalculator } from './financial';
import { StaffCalculator } from './staff';
import { CQCCalculator } from './cqc';
import { SocialCalculator } from './social';
import { ServicesCalculator } from './services';
import { CategoryCalculator } from '../calculator-base';

export {
  MedicalCalculator,
  SafetyCalculator,
  LocationCalculator,
  FinancialCalculator,
  StaffCalculator,
  CQCCalculator,
  SocialCalculator,
  ServicesCalculator,
  CategoryCalculator,
};

// Calculator registry
export const CALCULATORS = {
  medical: new MedicalCalculator(),
  safety: new SafetyCalculator(),
  location: new LocationCalculator(),
  financial: new FinancialCalculator(),
  staff: new StaffCalculator(),
  cqc: new CQCCalculator(),
  social: new SocialCalculator(),
  services: new ServicesCalculator(),
};


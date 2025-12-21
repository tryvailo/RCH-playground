/**
 * Type definitions for Funding Calculator feature
 */

export enum DomainLevel {
  Independent = 'independent',
  Low = 'low',
  Medium = 'medium',
  High = 'high',
  Severe = 'severe',
  Priority = 'priority',
}

export enum Domain {
  Breathing = 'breathing',
  Mobility = 'mobility',
  Cognitive = 'cognitive',
  Continence = 'continence',
  Skin = 'skin',
  Eating = 'eating',
  Safety = 'safety',
  Behaviour = 'behaviour',
  Medications = 'medications',
  Social = 'social',
  Autonomy = 'autonomy',
  Relationships = 'relationships',
}

export interface DomainAssessment {
  domain: Domain;
  level: DomainLevel;
  notes?: string;
}

export type DomainAssessments = Record<Domain, DomainLevel>;

export interface PropertyDetails {
  value: number;
  ownership: 'sole_owner' | 'joint' | 'none';
  disregardEligible: boolean;
  disregardDate?: string;
  notes?: string;
}

export interface IncomeDisregard {
  id: string;
  type: string;
  amount: number;
}

export interface AssetDisregard {
  id: string;
  type: string;
  amount: number;
}

export interface FormData {
  domainAssessments: DomainAssessments;
  propertyDetails: PropertyDetails | null;
  incomeDisregards: IncomeDisregard[];
  assetDisregards: AssetDisregard[];
  isCouple: boolean;
  age: number;
  capitalAssets: number;
  weeklyIncome: number;
}

export interface FormErrors {
  [key: string]: string | undefined;
}

// Result types
export interface CHCEligibilityResult {
  probability_percent: number;
  is_likely_eligible: boolean;
  reasoning: string;
  key_factors: string[];
  domain_scores: Record<string, number>;
}

export interface LASupportResult {
  funding_level: 'FULL' | 'PARTIAL' | 'NONE';
  full_support_probability: number;
  top_up_probability: number;
  capital_assessment?: Record<string, any>;
  income_assessment?: Record<string, any>;
}

export interface DPAResult {
  is_eligible: boolean;
  property_disregarded: boolean;
  qualifying_relatives: boolean;
  reason?: string;
}

export interface SavingsResult {
  weekly_savings: number;
  annual_savings: number;
  five_year_savings: number;
  lifetime_savings: number;
}

export interface FundingEligibilityResult {
  chc: CHCEligibilityResult;
  la: LASupportResult;
  dpa: DPAResult;
  savings: SavingsResult;
  assessed_at: string;
}

// Component props types
export interface FormSectionProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}

export interface DomainAssessmentSectionProps {
  domains: DomainAssessments;
  onChange: (domain: Domain, level: DomainLevel) => void;
  errors?: FormErrors;
}

export interface PropertyDetailsSectionProps {
  details: PropertyDetails | null;
  onChange: (details: PropertyDetails) => void;
  errors?: FormErrors;
}

export interface IncomeDisregardsSectionProps {
  disregards: IncomeDisregard[];
  onChange: (disregards: IncomeDisregard[]) => void;
  errors?: FormErrors;
}

export interface AssetDisregardsSectionProps {
  disregards: AssetDisregard[];
  onChange: (disregards: AssetDisregard[]) => void;
  errors?: FormErrors;
}

export interface FormActionsProps {
  onSubmit: () => void;
  onReset: () => void;
  isLoading?: boolean;
  isValid?: boolean;
  errors?: FormErrors;
}

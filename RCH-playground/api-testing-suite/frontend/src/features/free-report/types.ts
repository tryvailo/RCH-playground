export type CareType = 'residential' | 'nursing' | 'dementia' | 'respite';

export interface QuestionnaireResponse {
  postcode: string;
  budget?: number;
  care_type?: CareType;
  chc_probability?: number;
  address?: string;
  city?: string;
  latitude?: number;
  longitude?: number;
  preferences?: Record<string, any>;
}

export interface CareHome {
  name: string;
  address: string;
  postcode: string;
  city?: string;
  weekly_cost: number;
  care_types?: string[];
  rating?: string;
  distance_km?: number;
  features?: string[];
  contact_phone?: string;
  website?: string;
  band?: number;
  photo_url?: string;
  fsa_color?: 'green' | 'yellow' | 'red';
  fsa_rating?: number | string;
  fsa_rating_key?: string;
  fsa_rating_date?: string;
  fsa_health_score?: {
    score: number;
    label: string;
    description: string;
  };
  match_type?: 'Safe Bet' | 'Best Value' | 'Premium';
  location_id?: string;
}

export interface FairCostGap {
  gap_week: number;
  gap_year: number;
  gap_5year: number;
  market_price: number;
  msif_lower_bound: number;
  local_authority: string;
  care_type: string;
  explanation: string;
  gap_text: string;
  recommendations: string[];
}

export interface FairCostGapData {
  weekly: number;
  annual: number;
  fiveYear: number;
  percent: number;
}

export interface CareHomeData {
  name: string;
  photo?: string;
  band: number;
  price_range: {
    min: number;
    max: number;
  };
  distance: number;
  fsa_color?: 'green' | 'yellow' | 'red';
  fsa_rating?: number | string; // FSA rating value (0-5)
  fsa_rating_key?: string; // FSA rating key (e.g., "fhrs_5_en-gb")
  fsa_rating_date?: string; // FSA inspection date
  fsa_health_score?: {
    score: number;
    label: string;
    description: string;
  };
  match_type: 'Safe Bet' | 'Best Value' | 'Premium';
  why_this_home?: string; // "Why this home" - explanation text
  rating?: string; // CQC rating
  features?: string[];
  care_types?: string[];
  address?: string;
  city?: string;
  postcode?: string;
  contact_phone?: string;
  website?: string;
  [key: string]: any; // For additional fields
}

export interface ComparisonCriteria {
  name: string;
  home1: string | number;
  home2: string | number;
  home3: string | number;
}

export interface FreeReportData {
  homes: CareHomeData[];
  fairCostGap: FairCostGapData;
  chcTeaserPercent: number;
  fundingEligibility?: FundingEligibility;
  areaProfile?: AreaProfile;
  areaMap?: AreaMapData;
}

export interface FundingEligibility {
  chc: {
    probability_range: string; // "68-87%"
    savings_range: string; // "£78,000-£130,000/year"
  };
  la: {
    probability: string; // "72%"
    savings_range: string; // "£20,000-£50,000/year"
  };
  dpa: {
    probability: string; // "85%"
    cash_flow_relief: string; // "£2,000/week deferred"
  };
}

export interface AreaProfile {
  area_name: string;
  total_homes: number;
  average_weekly_cost: number;
  cost_vs_national: number; // percentage above/below national average
  cqc_distribution: {
    outstanding: number;
    good: number;
    requires_improvement: number;
    inadequate: number;
  };
  wellbeing_index?: number; // 0-100
  demographics?: {
    population_65_plus: number; // percentage
    average_income?: number;
    green_spaces?: 'high' | 'medium' | 'low';
  };
}

export interface AreaMapData {
  user_location: {
    lat: number;
    lng: number;
    postcode: string;
  };
  homes: Array<{
    id: string;
    name: string;
    lat: number;
    lng: number;
    distance_km: number;
    match_type: 'Safe Bet' | 'Best Value' | 'Premium';
  }>;
  amenities?: Array<{
    type: 'hospital' | 'park' | 'gp' | 'transport';
    name: string;
    lat: number;
    lng: number;
  }>;
}

export interface FreeReportResponse {
  questionnaire: QuestionnaireResponse;
  care_homes: CareHome[];
  fair_cost_gap: FairCostGap;
  funding_eligibility?: FundingEligibility;
  area_profile?: AreaProfile;
  area_map?: AreaMapData;
  generated_at: string;
  report_id: string;
}


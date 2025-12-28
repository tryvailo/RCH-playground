/**
 * Free Report Types
 * TypeScript types for Free Report
 */

import { CareType } from '@/lib/shared/types/care-home';

export interface FreeReportRequest {
  postcode: string;
  budget?: number;
  care_type?: CareType;
  chc_probability?: number;
  location_postcode?: string;
  timeline?: string;
  medical_conditions?: string[];
  max_distance_km?: number;
  priority_order?: string[];
  priority_weights?: number[];
}

export interface FreeReportCareHome {
  name: string;
  address?: string;
  postcode: string;
  weekly_cost: number;
  rating?: string;
  care_types?: string[];
  distance_km?: number;
  match_type: 'Safe Bet' | 'Best Value' | 'Premium';
  photo_url?: string;
  fsa_rating?: string | number;
}

export interface FairCostGap {
  gap_week: number;
  gap_year: number;
  gap_5year: number;
  gap_percent: number;
  market_price: number;
  msif_lower_bound: number;
  explanation: string;
  gap_text: string;
  recommendations: string[];
}

export interface FreeReportResponse {
  questionnaire: FreeReportRequest;
  care_homes: FreeReportCareHome[];
  fair_cost_gap: FairCostGap;
  area_profile?: any;
  area_map?: any;
  llm_insights?: any;
  generated_at: string;
  report_id: string;
}

export interface MatchedHomes {
  safe_bet: any | null;
  best_value: any | null;
  premium: any | null;
}




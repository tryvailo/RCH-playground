/**
 * Professional Report Types
 * TypeScript types for Professional Report
 */

export interface ProfessionalReportQuestionnaire {
  section_1_personal_info?: any;
  section_2_location_budget?: {
    q4_postcode?: string;
    q5_preferred_city?: string;
    q6_max_distance?: string;
    q7_budget_range?: string;
  };
  section_3_medical_needs?: {
    q8_care_types?: string[];
    q9_medical_conditions?: string[];
    q10_specialist_care?: string[];
  };
  section_4_lifestyle_preferences?: any;
  section_5_priorities?: {
    priority_order?: string[];
    priority_weights?: number[];
  };
  [key: string]: any;
}

export interface ProfessionalReportHome {
  id?: string;
  cqc_location_id?: string;
  name: string;
  address?: string;
  postcode?: string;
  city?: string;
  latitude?: number;
  longitude?: number;
  distance_km?: number;
  rating?: string;
  weekly_price?: number;
  care_types?: string[];
  [key: string]: any;
}

export interface CategoryScores {
  medical: number;
  safety: number;
  location: number;
  financial: number;
  staff: number;
  cqc: number;
  social: number;
  services: number;
}

export interface ScoredHome {
  home: ProfessionalReportHome;
  score: number;
  categoryScores: CategoryScores;
  pointAllocations?: any;
}

export interface ProfessionalReportResponse {
  summary: {
    generated_at: string;
    user_location: string;
    care_type: string;
    total_homes_evaluated: number;
    diversity: {
      unique_providers: number;
      unique_locations: number;
    };
  };
  matching: {
    top_5: Array<{
      rank: number;
      home: {
        id?: string;
        name: string;
        location?: string;
        distance_km?: number;
        rating?: string;
        price_weekly?: number;
        care_types?: string[];
      };
      match: {
        score: number;
        normalized: number;
        category_scores: CategoryScores;
        point_allocations?: any;
      };
      reasoning: {
        summary: string;
        key_strengths: string[];
        considerations?: string[];
      };
      category: string;
    }>;
    category_winners: {
      [category: string]: {
        home_name: string;
        score: number;
        category: string;
      };
    };
  };
  questionnaire: ProfessionalReportQuestionnaire;
  report_id: string;
}




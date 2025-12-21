// Professional Report Types

export interface ProfessionalQuestionnaireResponse {
  profile_description?: string;
  section_1_contact_emergency: {
    q1_names: string;
    q2_email: string;
    q3_phone: string;
    q4_emergency_contact: string;
  };
  section_2_location_budget: {
    q5_preferred_city: string;
    q6_max_distance: 'within_5km' | 'within_15km' | 'within_30km' | 'distance_not_important' | '5km' | '10km' | '15km' | '20km' | '30km';
    q7_budget: 
      | 'under_3000_self' 
      | 'under_3000_local' 
      | '3000_5000_self' 
      | '3000_5000_local' 
      | '5000_7000_self' 
      | '5000_7000_local' 
      | 'over_7000_self' 
      | 'over_7000_local' 
      | 'need_budget_guidance';
  };
  section_3_medical_needs: {
    q8_care_types: Array<'general_residential' | 'medical_nursing' | 'specialised_dementia' | 'temporary_respite'>;
    q9_medical_conditions: Array<'dementia_alzheimers' | 'mobility_problems' | 'diabetes' | 'heart_conditions' | 'no_serious_medical'>;
    q10_mobility_level: 'fully_mobile' | 'walking_aids' | 'wheelchair_sometimes' | 'wheelchair_permanent';
    q11_medication_management: 'none' | 'simple_1_2' | 'several_simple_routine' | 'many_complex_routine';
    q12_age_range: '65_74' | '75_84' | '85_94' | '95_plus';
  };
  section_4_safety_special_needs: {
    q13_fall_history: 'no_falls_occurred' | '1_2_no_serious_injuries' | '3_plus_or_serious_injuries' | 'high_risk_of_falling';
    q14_allergies: Array<'food_allergies' | 'medication_allergies' | 'environmental_allergies' | 'no_allergies'>;
    q15_dietary_requirements: Array<'diabetic_diet' | 'pureed_soft_food' | 'vegetarian_vegan' | 'no_special_requirements'>;
    q16_social_personality: 'very_sociable' | 'moderately_sociable' | 'prefers_quiet';
  };
  section_5_timeline: {
    q17_placement_timeline: 'urgent_2_weeks' | 'next_month' | 'planning_2_3_months' | 'exploring_6_plus_months';
  };
  section_6_priorities?: {
    q18_priority_ranking: {
      priority_order: Array<'quality_reputation' | 'cost_financial' | 'location_social' | 'comfort_amenities'>;
      priority_weights: number[]; // Must sum to 100
    };
  };
}

/**
 * FSA Breakdown Scores - RAW scores from FSA API
 * These are penalty points: lower is better
 * - hygiene: 0-20 (0 = best)
 * - structural: 0-20 (0 = best)
 * - confidence_in_management: 0-30 (0 = best)
 */
export interface FSABreakdownScores {
  hygiene?: number | null;
  structural?: number | null;
  confidence_in_management?: number | null;
  hygiene_label?: string | null;
  structural_label?: string | null;
  confidence_label?: string | null;
}

/**
 * FSA Detailed - UNIFIED format used by both FSA Explorer and Professional Report
 * This is the SINGLE SOURCE OF TRUTH for FSA data
 * All scores are RAW values from FSA API - no normalization
 */
export interface FSADetailed {
  // Core rating data
  rating?: number | null;
  rating_date?: string | null;
  fhrs_id?: string | null;
  
  // Business info
  business_name?: string | null;
  address?: string | null;
  postcode?: string | null;
  
  // RAW breakdown scores - same format as FSA Explorer
  // These are penalty points (lower is better)
  breakdown_scores?: FSABreakdownScores | null;
  
  // Historical ratings (RAW from FSA API)
  historical_ratings?: Array<{
    date?: string;
    rating_date?: string;
    rating?: number | string;
    rating_key?: string;
    breakdown_scores?: FSABreakdownScores;
    local_authority?: string;
    inspection_type?: string;
  }> | null;
  
  // Trend analysis (RAW from FSA API)
  trend_analysis?: {
    trend?: string;
    current_rating?: number;
    history_count?: number;
    consistency?: string;
    prediction?: {
      predicted_rating?: number;
      predicted_label?: string;
      confidence?: string;
    };
  } | null;
  
  // Data source flag
  data_source?: 'fsa_api' | 'fallback' | 'not_available';
  
  // Legacy fields for backward compatibility
  health_score?: {
    score?: number | null;
    label?: string | null;
  } | null;
  detailed_sub_scores?: {
    hygiene?: { raw_score?: number | null; normalized_score?: number | null; max_score: number; label?: string | null; weight: number; };
    cleanliness?: { raw_score?: number | null; normalized_score?: number | null; max_score: number; label?: string | null; weight: number; };
    management?: { raw_score?: number | null; normalized_score?: number | null; max_score: number; label?: string | null; weight: number; };
  } | null;
  data_available?: boolean;
  note?: string;
}

export interface FinancialStability {
  three_year_summary?: {
    revenue_trend?: string | null;
    revenue_3yr_avg?: number | null;
    revenue_growth_rate?: number | null;
    profitability_trend?: string | null;
    net_margin_3yr_avg?: number | null;
    working_capital_trend?: string | null;
    working_capital_3yr_avg?: number | null;
    current_ratio_3yr_avg?: number | null;
  } | null;
  altman_z_score?: number | null;
  bankruptcy_risk_score?: number | null;
  bankruptcy_risk_level?: string | null;
  uk_benchmarks_comparison?: {
    revenue_growth?: string | null;
    net_margin?: string | null;
    current_ratio?: string | null;
  } | null;
  red_flags?: Array<{
    type: string;
    severity: string;
    description: string;
  }> | null;
}

export interface GooglePlacesInsights {
  place_id?: string;
  popular_times?: {
    [day: string]: {
      [hour: string]: number;
    };
    peak_day?: string;
    peak_hours?: number[];
  };
  dwell_time?: {
    average_dwell_time_minutes?: number;
    median_dwell_time_minutes?: number;
    vs_uk_average?: number;
    interpretation?: string;
    distribution?: {
      [range: string]: number;
    };
  };
  repeat_visitor_rate?: {
    repeat_visitor_rate_percent?: number;
    trend?: string;
    interpretation?: string;
  };
  visitor_geography?: {
    local_percent?: number;
    regional_percent?: number;
    national_percent?: number;
    interpretation?: string;
  };
  footfall_trends?: {
    trend_direction?: 'growing' | 'stable' | 'declining';
    monthly_change_percent?: number;
    interpretation?: string;
  };
  summary?: {
    family_engagement_score?: number;
    quality_indicator?: string;
    recommendations?: string[];
  };
}

export interface GooglePlacesData {
  place_id?: string | null;
  rating?: number | null;
  user_ratings_total?: number | null;
  reviews?: Array<{
    author_name?: string;
    rating?: number;
    text?: string;
    time?: string;
  }> | null;
  reviews_count?: number | null;
  sentiment_analysis?: {
    average_sentiment?: number | null;
    sentiment_label?: string | null;
    total_reviews?: number | null;
    positive_reviews?: number | null;
    negative_reviews?: number | null;
    neutral_reviews?: number | null;
    sentiment_distribution?: {
      positive?: number | null;
      negative?: number | null;
      neutral?: number | null;
    } | null;
  } | null;
  // Google Places NEW API Insights
  insights?: GooglePlacesInsights | null;
  average_dwell_time_minutes?: number | null;
  repeat_visitor_rate?: number | null; // Decimal 0-1
  footfall_trend?: 'growing' | 'stable' | 'declining' | null;
  popular_times?: {
    [day: string]: {
      [hour: string]: number;
    };
  } | null;
  family_engagement_score?: number | null;
  quality_indicator?: string | null;
}

export interface StaffQualityComponent {
  score: number | null;
  weight: number;
  rating?: string | null;
  note?: string;
  reviewCount?: number;
  source?: string;
}

export interface StaffQualityData {
  overallScore: number;
  category: 'EXCELLENT' | 'GOOD' | 'ADEQUATE' | 'CONCERNING' | 'POOR' | 'UNKNOWN';
  confidence: 'high' | 'medium' | 'low';
  components: {
    cqc_well_led?: StaffQualityComponent;
    cqc_effective?: StaffQualityComponent;
    cqc_staff_sentiment?: StaffQualityComponent;
    employee_sentiment?: StaffQualityComponent;
  };
  themes?: {
    positive: string[];
    negative: string[];
  };
  dataQuality?: {
    cqc_data_age?: string;
    review_count?: number;
    has_insufficient_data?: boolean;
  };
  cqcData?: {
    well_led?: string | null;
    effective?: string | null;
    last_inspection_date?: string | null;
    staff_sentiment?: {
      positive: number;
      neutral: number;
      negative: number;
      score: number;
    };
  };
  reviewCount?: number;
  reviews?: Array<{
    source: string;
    rating: number;
    sentiment: string;
    text: string;
    date?: string;
    author?: string;
  }>;
  carehomeCoUk?: {
    url?: string;
    review_count?: number;
    average_rating?: number;
    staff_sentiment?: string;
  };
  indeed?: {
    indeed_url?: string;
    review_count?: number;
  };
}

export interface NeighbourhoodWalkability {
  score?: number | null;
  rating?: string | null;
  careHomeRelevance?: {
    score?: number | null;
    rating?: string | null;
    factors?: string[];
  } | null;
  amenitiesNearby?: {
    healthcare?: number | { count?: number; nearest_m?: number | null; within_400m?: number; within_800m?: number };
    shops?: number | { count?: number; nearest_m?: number | null; within_400m?: number; within_800m?: number };
    restaurants?: number | { count?: number; nearest_m?: number | null; within_400m?: number; within_800m?: number };
    parks?: number | { count?: number; nearest_m?: number | null; within_400m?: number; within_800m?: number };
    transport?: number | { count?: number; nearest_m?: number | null; within_400m?: number; within_800m?: number };
    total?: number | { count?: number; nearest_m?: number | null; within_400m?: number; within_800m?: number };
    grocery?: number | { count?: number; nearest_m?: number | null; within_400m?: number; within_800m?: number };
    banks?: number | { count?: number; nearest_m?: number | null; within_400m?: number; within_800m?: number };
  } | null;
}

export interface NeighbourhoodSocialWellbeing {
  score?: number | null;
  rating?: string | null;
  localAuthority?: string | null;
  deprivation?: {
    index?: number | null;
    decile?: number | null;
    rank?: number | null;
  } | null;
}

export interface NeighbourhoodHealthProfile {
  score?: number | null;
  rating?: string | null;
  gpPracticesNearby?: number | null;
  careHomeConsiderations?: Array<{
    category?: string;
    priority?: 'high' | 'medium' | 'low';
    description?: string;
  }> | null;
}

export interface NeighbourhoodData {
  overallScore?: number | null;
  overallRating?: string | null;
  confidence?: 'high' | 'medium' | 'low' | null;
  breakdown?: Array<{
    name: string;
    score: number;
    weight: string;
  }> | null;
  walkability?: NeighbourhoodWalkability | null;
  socialWellbeing?: NeighbourhoodSocialWellbeing | null;
  healthProfile?: NeighbourhoodHealthProfile | null;
  coordinates?: {
    latitude?: number | null;
    longitude?: number | null;
  } | null;
}

export interface EnforcementAction {
  type?: string;
  title?: string;
  description?: string;
  date?: string;
  status?: string;
  severity?: 'high' | 'medium' | 'low';
  link?: string;
}

export interface RegulatedActivity {
  id?: string;
  name?: string;
  active?: boolean;
  cqc_field?: string;
}

export interface LicenseFlags {
  has_nursing_care_license?: boolean;
  has_personal_care_license?: boolean;
  has_surgical_procedures_license?: boolean;
  has_treatment_license?: boolean;
  has_diagnostic_license?: boolean;
}

export interface CQCDeepDive {
  overall_rating?: string | null;
  current_rating?: string | null;
  historical_ratings?: Array<{
    date?: string;
    inspection_date?: string;
    rating?: string;
    overall_rating?: string;
    key_question_ratings?: {
      safe?: string;
      effective?: string;
      caring?: string;
      responsive?: string;
      well_led?: string;
    };
  }> | null;
  trend?: string | null;
  rating_changes?: Array<{
    date?: string;
    from_rating?: string;
    to_rating?: string;
  }> | null;
  action_plans?: Array<{
    title?: string;
    status?: string;
    date?: string;
    due_date?: string;
    description?: string;
  }> | null;
  detailed_ratings?: {
    safe?: { rating?: string; explanation?: string } | null;
    effective?: { rating?: string; explanation?: string } | null;
    caring?: { rating?: string; explanation?: string } | null;
    responsive?: { rating?: string; explanation?: string } | null;
    well_led?: { rating?: string; explanation?: string } | null;
  } | null;
  enforcement_actions?: EnforcementAction[] | null;
  regulated_activities?: RegulatedActivity[] | null;
  license_flags?: LicenseFlags | null;
  days_since_inspection?: number | null;
  rating_trend?: string | null;
  provider_locations_count?: number | null;
}

export interface ProfessionalCareHome {
  id: string;
  name: string;
  location: string;
  postcode: string;
  strategy: string;
  strategyLabel: string;
  cqcRating: string;
  distance: string;
  weeklyPrice: number;
  matchScore: number;
  lastAudited: string;
  dataSource: string[];
  whyChosen: string;
  keyStrengths: string[];
  mustVerify: string[];
  photo?: string; // Photo URL for the care home
  factorScores: Array<{
    category: string;
    score: number;
    maxScore: number;
    weight: number;
    verified: boolean;
    dataQuality: 'verified' | 'medium' | 'low';
  }>;
  contact: {
    phone: string;
    email: string;
  };
  dailyLife?: {
    schedule: string[];
    familyAccess: string[];
  };
  whyAligns: string[];
  // Executive Summary enhancements
  matchReason?: string;
  waitingListStatus?: string;
  bedsAvailable?: number;
  bedsTotal?: number;
  occupancyRate?: number | null;
  // New enriched data fields
  fsaDetailed?: FSADetailed | null;
  financialStability?: FinancialStability | null;
  googlePlaces?: GooglePlacesData | null;
  cqcDeepDive?: CQCDeepDive | null;
  // Section 10: Community Reputation
  communityReputation?: {
    google_rating: number | null;
    google_review_count: number;
    carehome_rating?: number | null;
    trust_score: number;
    sentiment_analysis: {
      average_sentiment: number;
      sentiment_label: string;
      total_reviews: number;
      positive_reviews: number;
      negative_reviews: number;
      neutral_reviews: number;
      sentiment_distribution: {
        positive: number;
        negative: number;
        neutral: number;
      };
    };
    sample_reviews: Array<{
      text: string;
      rating: number;
      author: string;
      source: string;
      date: string;
    }>;
    total_reviews_analyzed: number;
    review_sources: string[];
  } | null;
  // Section 6: Safety Analysis
  safetyAnalysis?: {
    safety_score: number | null;
    safety_rating: string | null;
    pedestrian_safety: string | null;
    public_transport: {
      nearest_bus_stop?: { distance: number; name: string } | null;
      nearest_train_station?: { distance: number; name: string } | null;
    } | null;
    accessibility: {
      wheelchair_accessible: boolean;
      accessible_entrances: number | null;
    } | null;
  } | null;
  // Section 18: Location Wellbeing
  locationWellbeing?: {
    walkability_score: number | null;
    green_space_score: number | null;
    nearest_park_distance: number | null;
    noise_level: string | null;
    local_amenities: Array<{
      type: string;
      name: string;
      distance: number;
    }>;
  } | null;
  // Section 19: Area Map
  areaMap?: {
    nearby_gps: Array<{
      name: string;
      distance: number;
      address?: string;
    }>;
    nearby_parks: Array<{
      name: string;
      distance: number;
    }>;
    nearby_shops: Array<{
      name: string;
      distance: number;
      type?: string;
    }>;
    nearby_pharmacies: Array<{
      name: string;
      distance: number;
    }>;
    nearest_hospital?: {
      name: string;
      distance: number;
    } | null;
    nearest_bus_stop?: {
      name: string;
      distance: number;
    } | null;
    nearest_train_station?: {
      name: string;
      distance: number;
    } | null;
  } | null;
  // Section 8: Medical Care
  medicalCare?: {
    medical_specialisms: string[];
    regulated_activities: string[];
    care_residential: boolean;
    care_nursing: boolean;
    care_dementia: boolean;
    service_types: string[];
  } | null;
  // Section 18: Neighbourhood Analysis
  neighbourhood?: NeighbourhoodData | null;
  // Section 16: Comfort & Lifestyle
  comfortLifestyle?: {
    facilities: {
      general_amenities: string[];
      medical_facilities: string[];
      social_facilities: string[];
      safety_features: string[];
      outdoor_spaces: string[];
      building_type?: string | null;
      capacity?: number | null;
    };
    activities: {
      daily_activities: string[];
      weekly_programs: string[];
      therapy_programs: string[];
      outings: string[];
      special_events?: string[];
      weekly_activities_count: number;
      outings_per_month: number;
    };
    nutrition: {
      dietary_options: string[];
      dietary_options_by_category?: Record<string, string[]>;
    };
    private_room_percentage: number | null;
    ensuite_availability: boolean;
    wheelchair_accessible: boolean;
    outdoor_space_description: string | null;
    wifi_available: boolean;
    parking_onsite: boolean;
    secure_garden: boolean;
    room_photos: string[];
  } | null;
  // Section 17: Lifestyle Deep Dive
  lifestyleDeepDive?: {
    daily_schedule: Array<{
      time: string;
      activity: string;
    }>;
    activity_categories: string[];
    visiting_hours: string | null;
    personalization: string | null;
    policies: Array<{
      title: string;
      description: string;
    }>;
    activities_summary: string | null;
  } | null;
  // Section 11: Family Engagement
  familyEngagement?: {
    data_source: string;
    confidence: string;
    data_coverage: string;
    dwell_time_minutes: number | null;
    repeat_visitor_rate: number | null;
    footfall_trend: 'growing' | 'stable' | 'declining' | null;
    engagement_score: number | null;
    quality_indicator: string | null;
    methodology_note: string | null;
  } | null;
  // Section 14: Funding Options
  fundingOptions?: {
    selfFunding?: boolean;
    localAuthorityFunding?: boolean | {
      available: boolean;
      assessment_required: boolean;
      means_test_required: boolean;
      contribution_amount: number;
    };
    chcEligibility?: {
      eligibility_level: string;
      probability_percent: number;
      primary_health_need_score: number;
      assessment_details: Record<string, any>;
    } | null;
    dpaFunding?: {
      available: boolean;
      eligibility_criteria: string[];
      application_process: string[];
    };
    projections?: {
      year_1: Record<string, any>;
      year_2: Record<string, any>;
      year_3: Record<string, any>;
      year_4: Record<string, any>;
      year_5: Record<string, any>;
    };
    notes?: string;
  } | null;

  // Section 9: Staff Quality
  staffQuality?: StaffQualityData | null;
  
  // Category Winners (NEW)
  is_category_winner?: {
    [categoryKey: string]: boolean;
  };
  category_labels?: string[];
  category_reasoning?: {
    [categoryKey: string]: string[];
  };
  value_ratio?: number; // For Best Cost & Financial
}

export interface ScoringWeights {
  medical: number;
  safety: number;
  location: number;
  social: number;
  financial: number;
  staff: number;
  cqc: number;
  services: number;
}

export interface DSTDomain {
  severity: 'A' | 'B' | 'C';
  level: string;
  description: string;
  score: number;
}

export interface CHCAssessmentDetails {
  priority_domains_count: number;
  severe_domains_count: number;
  priority_domains: string[];
  severe_domains: string[];
  primary_health_need_indicated: boolean;
  assessment_framework: string;
  domains_assessed: number;
  next_assessment_stage: string;
}

export interface CHCEligibility {
  eligibility_probability: number;
  eligibility_level: string;
  severity_score: number;
  primary_health_need_score: number;
  recommendation: string;
  key_factors: string[];
  dst_domains: {
    breathing: DSTDomain;
    nutrition: DSTDomain;
    continence: DSTDomain;
    skin_integrity: DSTDomain;
    mobility: DSTDomain;
    communication: DSTDomain;
    psychological_emotional: DSTDomain;
    cognition: DSTDomain;
    behaviour: DSTDomain;
    drug_therapies: DSTDomain;
    altered_consciousness: DSTDomain;
    other_significant_needs: DSTDomain;
  };
  assessment_details: CHCAssessmentDetails;
  next_steps: string[];
  estimated_annual_savings: {
    if_approved: number;
    probability_adjusted: number;
    weekly_equivalent: number;
  };
  important_notes: string[];
}

export interface LAFunding {
  funding_available: boolean;
  funding_level: string;
  funding_explanation: string;
  property_assessment: {
    property_value: number;
    disregarded: boolean;
    assessment: string;
    assessable_value: number;
  };
  capital_assessment: {
    total_assessable_capital: number;
    assets: number;
    property_value: number;
    threshold: number;
    excess_capital: number;
    eligible: boolean;
    assessment: string;
    tariff_income: number;
  };
  income_assessment: {
    weekly_income: number;
    tariff_income_from_capital: number;
    total_assessed_income: number;
    threshold: number;
    excess_income: number;
    eligible: boolean;
    assessment: string;
    contribution_required: number;
  };
  funding_split: {
    la_contribution_percent: number;
    self_contribution_percent: number;
    estimated_weekly_contribution: number;
    estimated_annual_contribution: number;
    la_weekly_contribution: number;
    la_annual_contribution: number;
  };
  assessment_breakdown: {
    capital_calculation: {
      step1_total_capital: number;
      step2_threshold: number;
      step3_excess: number;
      step4_tariff_income: number;
      explanation: string;
    };
    income_calculation: {
      step1_weekly_income: number;
      step2_tariff_income: number;
      step3_total_assessed: number;
      step4_threshold: number;
      step5_excess: number;
      explanation: string;
    };
    property_status: {
      disregarded: boolean;
      value: number;
      included_in_assessment: boolean;
      reason: string;
    };
  };
  important_notes: string[];
  next_steps: string[];
}

export interface DPAProjection {
  years: number;
  deferred_amount: number;
  interest_accrued: number;
  admin_fees: number;
  total_cost: number;
  within_limit: boolean;
  note?: string;
}

export interface DPAConsiderations {
  dpa_eligible: boolean;
  property_assessment: {
    property_value: number;
    outstanding_mortgage: number;
    equity: number;
    equity_percent: number;
  };
  eligibility: {
    minimum_equity_required: number;
    equity_shortfall: number;
    meets_minimum: boolean;
    assessment: string;
  };
  deferral_limits: {
    maximum_deferral_percent: number;
    available_deferral: number;
    years_coverable: number;
    explanation: string;
  };
  costs: {
    interest_rate_percent: number;
    administration_fee_annual: number;
    administration_fee_weekly: number;
    annual_interest_example: number;
    weekly_interest_example: number;
    total_weekly_cost_deferred: number;
  };
  projections: DPAProjection[];
  comparison: {
    immediate_payment_5yr: number;
    dpa_payment_5yr: number;
    savings_vs_immediate: number;
    note: string;
  };
  key_considerations: string[];
  important_notes: string[];
  next_steps: string[];
}

export interface FundingOutcome {
  home_id: string;
  home_name: string;
  weekly_cost: number;
  annual_cost: number;
  scenarios: {
    chc_funding: {
      available: boolean;
      probability: number;
      weekly_cost: number;
      annual_cost: number;
      savings_weekly: number;
      savings_annual: number;
    };
    la_funding: {
      available: boolean;
      la_contribution_weekly: number;
      self_contribution_weekly: number;
      la_contribution_annual: number;
      self_contribution_annual: number;
    };
    self_funding: {
      weekly_cost: number;
      annual_cost: number;
    };
    dpa_deferral: {
      available: boolean;
      weekly_deferred: number;
      weekly_interest: number;
      annual_deferred: number;
      annual_interest: number;
    };
  };
  recommended_scenario: {
    scenario: string;
    priority: number;
    reason: string;
    weekly_cost: number;
    annual_cost: number;
    note?: string;
  };
}

export interface YearProjection {
  year: number;
  year_number: number;
  weekly_cost: number;
  annual_cost: number;
  cumulative_cost: number;
  la_contribution_weekly?: number | null;
  la_contribution_annual?: number | null;
  inflation_factor: number;
  inflation_rate: number;
  // DPA-specific fields
  deferred_amount?: number;
  cumulative_deferred?: number;
  interest_accrued?: number;
  cumulative_interest?: number;
  admin_fee?: number;
  cumulative_admin_fees?: number;
  total_cost?: number;
  cumulative_total_cost?: number;
  within_dpa_limit?: boolean;
}

export interface ScenarioProjection {
  scenario_name: string;
  scenario_type?: string;
  base_weekly_cost: number;
  base_annual_cost: number;
  projections: YearProjection[];
  total_5_year_cost: number;
  total_5_year_la_contribution?: number | null;
  total_5_year_deferred?: number;
  total_5_year_interest?: number;
  total_5_year_admin_fees?: number;
  average_annual_cost: number;
  average_weekly_cost: number;
  probability?: number;
  total_savings_vs_self?: number | null;
  dpa_limit_reached?: boolean;
  years_covered?: number;
}

export interface YearByYearBreakdown {
  year: number;
  year_number: number;
  scenarios: {
    [key: string]: {
      annual_cost: number;
      cumulative_cost: number;
      scenario_name: string;
    };
  };
}

export interface HomeProjectionSummary {
  scenario_summaries: {
    [key: string]: {
      scenario_name: string;
      total_5_year_cost: number;
      average_annual_cost: number;
      average_weekly_cost: number;
      savings_vs_self?: number;
      savings_percent?: number;
    };
  };
  best_scenario: string;
  best_scenario_cost: number;
  worst_scenario: string;
  worst_scenario_cost: number;
  potential_savings: number;
}

export interface FiveYearProjection {
  home_id: string;
  home_name: string;
  base_weekly_cost: number;
  base_annual_cost: number;
  scenario_projections: {
    chc?: ScenarioProjection;
    la?: ScenarioProjection;
    self: ScenarioProjection;
    dpa?: ScenarioProjection;
    recommended: ScenarioProjection;
  };
  year_by_year: YearByYearBreakdown[];
  summary: HomeProjectionSummary;
}

export interface FundingOptimization {
  chc_eligibility: CHCEligibility;
  la_funding: LAFunding;
  dpa_considerations: DPAConsiderations;
  funding_outcomes: {
    outcomes: FundingOutcome[];
    summary: {
      average_weekly_cost: number;
      average_annual_cost: number;
      best_case_scenario: {
        type: string;
        weekly_cost: number;
        annual_cost: number;
      };
      worst_case_scenario: {
        type: string;
        weekly_cost: number;
        annual_cost: number;
      };
    };
  };
  five_year_projections: {
    projections: FiveYearProjection[];
    summary: {
      average_5_year_cost_self_funding: number;
      average_5_year_cost_recommended: number;
      average_annual_cost_self_funding: number;
      average_annual_cost_recommended: number;
      potential_annual_savings: number;
      potential_5_year_savings: number;
      inflation_rate_percent: number;
      compounded_inflation_5yr: number;
    };
    assumptions: string[];
    inflation_details: {
      annual_rate: number;
      compounded_5_year: number;
      explanation: string;
    };
  };
  generated_at: string;
}

export interface ComparisonTableRow {
  category: string;
  metric: string;
  homes: {
    [key: string]: {
      value: string | number;
      highlight?: boolean;
      sort_value?: number;
      badge?: string;
      is_list?: boolean;
    };
  };
}

export interface MatchScoreRanking {
  rank: number;
  home_id: string;
  home_name: string;
  match_score: number;
  score_difference_from_top: number;
  percentile: number;
}

export interface MatchScoreRankings {
  rankings: MatchScoreRanking[];
  statistics: {
    highest_score: number;
    lowest_score: number;
    average_score: number;
    score_range: number;
    score_variance: number;
  };
  tier_analysis: {
    tier_1_excellent: {
      count: number;
      homes: string[];
      range: string;
    };
    tier_2_very_good: {
      count: number;
      homes: string[];
      range: string;
    };
    tier_3_good: {
      count: number;
      homes: string[];
      range: string;
    };
    tier_4_fair: {
      count: number;
      homes: string[];
      range: string;
    };
  };
}

export interface PriceComparisonItem {
  rank: number;
  home_id: string;
  home_name: string;
  weekly_price: number;
  annual_price: number;
  price_difference_from_lowest: number;
  price_percent_difference: number;
  value_score: number;
}

export interface PriceComparison {
  comparison: PriceComparisonItem[];
  sorted_by_price: PriceComparisonItem[];
  statistics: {
    highest_weekly: number;
    lowest_weekly: number;
    average_weekly: number;
    price_range: number;
    highest_annual: number;
    lowest_annual: number;
    average_annual: number;
  };
  best_value?: {
    home_id: string;
    home_name: string;
    value_score: number;
    match_score: number;
    weekly_price: number;
  };
}

export interface KeyDifferentiator {
  type: string;
  title: string;
  description: string;
  home_name: string;
  value: string | number;
  importance: 'high' | 'medium' | 'low';
}

export interface ComparativeAnalysis {
  comparison_table: ComparisonTableRow[];
  rankings: MatchScoreRankings;
  price_comparison: PriceComparison;
  key_differentiators: KeyDifferentiator[];
  summary: {
    total_homes_compared: number;
    match_score_range: number;
    price_range_weekly: number;
    price_range_annual: number;
    recommendation: string;
  };
  generated_at: string;
}

export interface RedFlag {
  type: 'financial' | 'cqc' | 'staff' | 'pricing';
  severity: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  impact: string;
  recommendation: string;
}

export interface Warning {
  type: 'financial' | 'cqc' | 'staff' | 'pricing';
  severity: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  impact: string;
  recommendation: string;
}

export interface HomeRiskAssessment {
  home_id: string;
  home_name: string;
  red_flags: RedFlag[];
  warnings: Warning[];
  risk_score: number;
  overall_risk_level: 'high' | 'medium' | 'low';
  financial_assessment: {
    red_flags: RedFlag[];
    warnings: Warning[];
    risk_score: number;
    status: string;
    altman_z_score?: number;
    bankruptcy_risk?: number;
  };
  cqc_assessment: {
    red_flags: RedFlag[];
    warnings: Warning[];
    risk_score: number;
    status: string;
    overall_rating?: string;
    detailed_ratings_count?: number;
    active_action_plans?: number;
  };
  staff_assessment: {
    red_flags: RedFlag[];
    warnings: Warning[];
    risk_score: number;
    status: string;
    turnover_rate?: number;
    average_tenure?: number;
    glassdoor_rating?: number;
  };
  pricing_assessment: {
    red_flags: RedFlag[];
    warnings: Warning[];
    risk_score: number;
    status: string;
    pricing_history_available?: boolean;
    total_increase_pct?: number;
    average_increase_pct?: number;
    max_increase_pct?: number;
    increase_count?: number;
  };
}

export interface RiskAssessment {
  homes_assessment: HomeRiskAssessment[];
  summary: {
    total_homes_assessed: number;
    total_red_flags: number;
    risk_distribution: {
      high: number;
      medium: number;
      low: number;
    };
    flags_by_category: {
      financial: number;
      cqc: number;
      staff: number;
      pricing: number;
    };
    highest_risk_homes: Array<{
      home_name: string;
      risk_score: number;
      risk_level: string;
      red_flag_count: number;
    }>;
    overall_assessment: string;
  };
  generated_at: string;
}

export interface NegotiationStrategy {
    market_rate_analysis: {
    uk_average_weekly: number;
    regional_average_weekly: number;
    region: string;
    care_type: string;
    market_price_range: {
      minimum: number;
      maximum: number;
      average: number;
    };
    price_comparison: Array<{
      home_name: string;
      weekly_price: number;
      vs_regional_average: number;
      vs_uk_average: number;
      positioning: string;
      negotiation_potential: {
        potential: 'high' | 'medium' | 'low';
        discount_range: string;
        reasoning: string;
        recommended_approach: string;
      };
    }>;
    value_positioning: {
      best_value: {
        home_name: string;
        match_score: number;
        weekly_price: number;
        value_score: number;
      } | null;
      premium_options: Array<{
        home_name: string;
        weekly_price: number;
        match_score: number;
      }>;
      budget_options: Array<{
        home_name: string;
        weekly_price: number;
        match_score: number;
      }>;
      market_average: number;
    };
    market_insights: string[];
    autumna_data?: {
      source: string;
      sample_size: number;
      market_range: {
        minimum: number;
        maximum: number;
        average: number;
      };
      note: string;
    } | null;
  };
  discount_negotiation_points: {
    available_discounts: Array<{
      type: string;
      title: string;
      description: string;
      potential_discount: string;
      reasoning: string;
      how_to_negotiate: string;
      priority: 'high' | 'medium' | 'low';
    }>;
    total_potential_discount: {
      conservative_range: string;
      optimistic_range: string;
      realistic_expectation: string;
      note: string;
    };
    negotiation_strategy: {
      opening_strategy: string[];
      key_talking_points: string[];
      timing: string;
      approach: string;
      red_flags: string[];
    };
  };
  contract_review_checklist: {
    essential_terms: Array<{
      term: string;
      what_to_check: string;
      red_flags: string[];
    }>;
    recommended_additions: string[];
    negotiation_leverage_points: Array<{
      home_name: string;
      leverage: string;
      suggestion: string;
    }>;
  };
  email_templates: {
    initial_inquiry: {
      template: string;
      when_to_use: string;
      customization_notes: string;
    };
    negotiation_followup: {
      template: string;
      when_to_use: string;
      customization_notes: string;
    };
    contract_clarification: {
      template: string;
      when_to_use: string;
      customization_notes: string;
    };
  };
  questions_to_ask_at_visit: {
    questions_by_category: {
      [category: string]: string[];
    };
    priority_questions: string[];
    red_flag_questions: string[];
  };
  generated_at: string;
}

export interface NextSteps {
  recommendedActions: Array<{
    homeName: string;
    homeRank: number;
    action: string;
    timeline: string;
    priority: 'high' | 'medium' | 'low';
    peakVisitingHours?: string[];
    localAuthority?: string;
  }>;
  questionsForHomeManager: {
    medicalCare: string[];
    staffQualifications: string[];
    cqcFeedback: string[];
    financialStability: string[];
    trialPeriod: string[];
    cancellationTerms: string[];
  };
  premiumUpgradeOffer: {
    title: string;
    price: string;
    features: string[];
    benefits: string[];
    cta: string;
  };
  localAuthority?: string;
  generated_at: string;
}

export interface FairCostGapHome {
  home_id: string;
  home_name: string;
  their_price: number; // Weekly price
  fair_cost_msif: number; // MSIF fair cost lower bound
  gap_weekly: number; // their_price - fair_cost_msif
  gap_annual: number; // gap_weekly * 52
  gap_5year: number; // gap_annual * 5
  gap_percent: number; // (gap_weekly / fair_cost_msif) * 100
}

export interface FairCostGapAnalysis {
  local_authority: string;
  local_authority_code?: string | null;
  region?: string | null;
  care_type: string;
  msif_data?: {
    fair_cost_weekly: number | null;
    source: string;
    year: string;
    care_type_display: string;
    local_authority_verified: boolean;
  };
  local_authority_info?: {
    name: string;
    code?: string | null;
    region?: string | null;
    contact_note: string;
    website_hint: string;
  } | null;
  homes: FairCostGapHome[]; // Per-home gap analysis (5 homes)
  why_gap_exists: {
    title: string;
    explanation: string;
    market_dynamics: string[];
    msif_context?: string;
  };
  strategies_to_reduce_gap: Array<{
    strategy_number: number;
    title: string;
    description: string;
    potential_savings?: string;
    action_items: string[];
  }>;
  average_gap_weekly: number;
  average_gap_annual: number;
  average_gap_5year: number;
}

export interface ProfessionalReportData {
  reportId: string;
  clientName: string;
  postcode: string;
  city: string;
  clientNeeds: {
    medicalConditions: string[];
    mobilityLevel: string;
    languagePreference: string;
    careRequirements: string[];
  };
  analysisSummary: {
    totalHomesAnalyzed: number;
    factorsAnalyzed: number;
    analysisTime: string;
  };
  executiveSummary: {
    personalizedMatching: string;
    precisionMatching: string;
    deepAnalysis: string;
    expertInsights: string;
  };
  appliedWeights: ScoringWeights; // Dynamic weights applied based on client profile
  appliedConditions?: string[]; // Conditions that triggered weight adjustments
  careHomes: ProfessionalCareHome[];
  fairCostGapAnalysis?: FairCostGapAnalysis; // Fair Cost Gap Analysis per home
  fundingOptimization?: FundingOptimization;
  comparativeAnalysis?: ComparativeAnalysis;
  riskAssessment?: RiskAssessment;
  negotiationStrategy?: NegotiationStrategy;
  nextSteps?: NextSteps;
  appendix?: {
    data_sources: Array<{
      name: string;
      description: string;
      data_types: string[];
      update_frequency: string;
      official_url: string;
      last_update: {
        cached_entries?: number;
        cache_hits?: number;
        status: string;
        note?: string;
      };
    }>;
    cache_statistics: {
      total_cached_entries: number;
      valid_entries: number;
      expired_entries: number;
      cache_size_mb: number;
      sources_with_cache: number;
    };
    funding_calculator_data_sources?: string;  // Markdown content for £119 report
    report_metadata: {
      generated_at: string;
      report_id: string;
      total_sources: number;
      data_quality_note: string;
      funding_sources_available?: boolean;
    };
  };
  llmInsights?: {
    generated_at: string;
    model: string;
    method: string;
    insights: {
      overall_explanation: {
        summary: string;
        key_insights: string[];
        confidence_level: 'high' | 'medium' | 'moderate';
      };
      top_home_analysis: Array<{
        home_name: string;
        rank: number;
        why_recommended: string;
        key_strengths: string[];
        considerations?: string[];
        match_score_explanation?: string;
      }>;
      expert_advice: {
        funding_strategy: string;
        decision_timeline: string;
        red_flags_to_watch?: string[];
        negotiation_tips?: string[];
      };
      actionable_next_steps: Array<{
        step: string;
        priority: 'high' | 'medium' | 'low';
        timeline: string;
        details?: string;
      }>;
    };
  };
  generatedAt: string;
}

export interface ProfessionalReportResponse {
  questionnaire: ProfessionalQuestionnaireResponse;
  report: ProfessionalReportData;
  generated_at: string;
  report_id: string;
  job_id?: string;
  status?: 'pending' | 'processing' | 'completed' | 'failed';
}

// ===== NEW TYPES FOR ADDITIONAL SECTIONS =====

// Executive Summary Section (Page 1)
export interface ExecutiveSummaryData {
  fullName: string;
  reportGenerationDate: string;
  topRecommendations: Array<{
    rank: 1 | 2 | 3;
    homeName: string;
    overallScore: number;
    address: string;
    phone: string;
    waitingListStatus: 'Available now' | '2-4 weeks' | '3+ months';
    matchReason: string;
  }>;
  urgencyAlert?: {
    show: boolean;
    message: string;
    topChoicePhone: string;
  };
  actionPlanPageLink: number;
}

// Priorities Match Section (Page 4)
export interface UserPriority {
  id: string;
  label: string;
  source: string;
  weight: number;
}

export interface PriorityMatch {
  score: number;
  status: 'full' | 'partial' | 'none';
  note?: string;
}

export interface HomeMatch {
  homeId: string;
  homeName: string;
  homeRank: number;
  priorityScores: Record<string, PriorityMatch>;
  overallPriorityMatch: number;
}

export interface PrioritiesMatchData {
  userPriorities: UserPriority[];
  comparisonMatrix: HomeMatch[];
}

// Funding Options Section (Page 14)
export interface CHCEligibility {
  probability: 'High' | 'Medium' | 'Low';
  score: number;
  matchedCriteria: string[];
  weeklyValue: string;
  annualValue: string;
  nextSteps: string[];
}

export interface CouncilFunding {
  localAuthorityName: string;
  localAuthorityPhone: string;
  capitalLimit: number;
  lowerLimit: number;
  propertyDisregard: boolean;
  meansTestInfo: string;
  deferredPaymentAvailable: boolean;
  nextSteps: string[];
}

export interface AttendanceAllowance {
  higherRate: string;
  lowerRate: string;
  estimatedRate: 'higher' | 'lower';
  annualValue: string;
}

export interface FundingOptionsData {
  chcEligibility: CHCEligibility;
  councilFunding: CouncilFunding;
  attendanceAllowance: AttendanceAllowance;
  totalPotentialFunding: {
    weeklyMin: number;
    weeklyMax: number;
    annualMin: number;
    annualMax: number;
  };
}

// 14-Day Action Plan Section (Page 15)
export interface ActionTask {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  category: 'call' | 'visit' | 'document' | 'research' | 'decision';
  contactInfo?: {
    name: string;
    phone: string;
    role?: string;
  };
  estimatedTime?: string;
  completed: boolean;
}

export interface DayPlan {
  day: number;
  date?: string;
  tasks: ActionTask[];
}

export interface WeekPlan {
  weekNumber: 1 | 2;
  title: string;
  days: DayPlan[];
}

export interface DocumentItem {
  document: string;
  required: boolean;
  obtained: boolean;
  whereToGet: string;
}

export interface KeyContact {
  type: 'care_home' | 'council' | 'nhs' | 'solicitor';
  name: string;
  phone: string;
  email?: string;
  notes?: string;
}

export interface ActionPlanData {
  weeks: WeekPlan[];
  keyContacts: KeyContact[];
  documentsNeeded: DocumentItem[];
}

// Verdict Badge
export interface VerdictInfo {
  label: 'Excellent Match' | 'Good Match' | 'Fair Match' | 'Limited Match';
  color: string;
  bgClass: string;
  borderClass: string;
  description: string;
}


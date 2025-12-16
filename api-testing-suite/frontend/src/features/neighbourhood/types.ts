/**
 * Types for Neighbourhood Analysis Data Sources
 */

// ============================================================
// OS PLACES TYPES
// ============================================================

export interface OSPlacesAddress {
  uprn: string | null;
  address: string | null;
  building_name: string | null;
  building_number: string | null;
  street: string | null;
  locality: string | null;
  town: string | null;
  postcode: string | null;
  country: string | null;
  latitude: number | null;
  longitude: number | null;
  x_coordinate: number | null;
  y_coordinate: number | null;
  classification_code: string | null;
  classification_description: string | null;
  local_authority: string | null;
}

export interface OSPlacesResult {
  postcode: string;
  address_count: number;
  addresses: OSPlacesAddress[];
  centroid: {
    latitude: number;
    longitude: number;
  } | null;
  header?: Record<string, any>;
  fetched_at: string;
  error?: string;
}

// ============================================================
// ONS TYPES
// ============================================================

export interface ONSGeography {
  postcode: string | null;
  lsoa_code: string | null;
  lsoa_name: string | null;
  msoa_code: string | null;
  msoa_name: string | null;
  local_authority: string | null;
  local_authority_code: string | null;
  region: string | null;
  country: string | null;
  latitude: number | null;
  longitude: number | null;
  imd_rank: number | null;
  fetched_at: string;
  error?: string;
}

export interface ONSWellbeingIndicator {
  value: number;
  description: string;
  national_average: number;
  vs_national: string;
}

export interface ONSWellbeingIndex {
  score: number;
  rating: string;
  percentile: number;
  components: {
    happiness_contribution: number;
    satisfaction_contribution: number;
    low_anxiety_contribution: number;
    worthwhile_contribution: number;
  };
}

export interface ONSWellbeing {
  area: string;
  lsoa_code: string | null;
  data_level: string;
  period: string;
  indicators: {
    happiness: ONSWellbeingIndicator;
    life_satisfaction: ONSWellbeingIndicator;
    anxiety: ONSWellbeingIndicator;
    worthwhile: ONSWellbeingIndicator;
  };
  social_wellbeing_index: ONSWellbeingIndex;
  source: string;
  methodology: string;
  fetched_at: string;
}

export interface ONSEconomicIndicator {
  value: number;
  unit: string;
  national_average?: number;
  trend?: string;
  description?: string;
  interpretation?: string;
}

export interface ONSEconomicProfile {
  area: string;
  postcode: string | null;
  lsoa_code: string | null;
  indicators: {
    employment_rate: ONSEconomicIndicator;
    median_income: ONSEconomicIndicator;
    imd_decile: ONSEconomicIndicator;
    economic_activity_rate: ONSEconomicIndicator;
  };
  economic_stability_index: {
    score: number;
    rating: string;
    factors: string[];
  };
  source: string;
  period: string;
  fetched_at: string;
}

export interface ONSDemographics {
  area: string;
  postcode: string | null;
  population: {
    total: number;
    density_per_km2: number;
  };
  age_structure: {
    under_18: { percent: number; count: number };
    '18_to_64': { percent: number; count: number };
    '65_to_79': { percent: number; count: number };
    '80_plus': { percent: number; count: number };
  };
  elderly_care_context: {
    over_65_percent: number;
    over_80_percent: number;
    elderly_population_trend: string;
    projected_over_65_2030: number;
    care_home_demand_indicator: string;
  };
  household_composition: {
    single_person_over_65: { percent: number };
    couples_over_65: { percent: number };
  };
  source: string;
  fetched_at: string;
}

export interface ONSFullProfile {
  postcode: string;
  geography: ONSGeography;
  wellbeing: ONSWellbeing;
  economic: ONSEconomicProfile;
  demographics: ONSDemographics;
  summary: {
    area_name: string;
    region: string;
    social_wellbeing_score: number;
    economic_stability_score: number;
    elderly_population_percent: number;
    overall_rating: string;
  };
  fetched_at: string;
  error?: string;
}

// ============================================================
// OSM (OpenStreetMap) TYPES
// ============================================================

export interface OSMAmenity {
  name: string;
  type: string;
  distance_m: number;
  lat: number;
  lon: number;
  opening_hours?: string;
  wheelchair?: string;
  website?: string;
}

export interface OSMCategorySummary {
  count: number;
  nearest_m: number | null;
  within_400m: number;
  within_800m: number;
}

export interface OSMAmenitiesResult {
  location: { lat: number; lon: number };
  radius_m: number;
  total_amenities: number;
  by_category: {
    grocery: OSMAmenity[];
    restaurants: OSMAmenity[];
    shopping: OSMAmenity[];
    coffee: OSMAmenity[];
    banks: OSMAmenity[];
    parks: OSMAmenity[];
    schools: OSMAmenity[];
    books: OSMAmenity[];
    entertainment: OSMAmenity[];
    healthcare: OSMAmenity[];
  };
  summary: Record<string, OSMCategorySummary>;
  fetched_at: string;
  error?: string;
}

export interface OSMCategoryScore {
  score: number;
  count: number;
  nearest_m: number | null;
  weight: number;
}

export interface OSMCareHomeRelevance {
  score: number;
  rating: string;
  key_factors: string[];
  healthcare_access: string;
  outdoor_spaces: string;
  dining_options: string;
}

export interface OSMWalkScore {
  location: { lat: number; lon: number };
  walk_score: number;
  rating: string;
  description: string;
  category_breakdown: Record<string, OSMCategoryScore>;
  highlights: string[];
  care_home_relevance: OSMCareHomeRelevance;
  total_amenities: number;
  methodology: string;
  fetched_at: string;
  error?: string;
}

export interface OSMInfrastructure {
  location: { lat: number; lon: number };
  public_transport: {
    bus_stops_800m: number;
    rail_stations_1600m: number;
    rating: string;
  };
  pedestrian_safety: {
    pedestrian_crossings: number;
    lit_roads_nearby: number;
    footways: number;
    rating: string;
  };
  accessibility: {
    benches_nearby: number;
    rest_points: string;
  };
  safety_score: number;
  safety_rating: string;
  fetched_at: string;
  error?: string;
}

// ============================================================
// NHSBSA TYPES
// ============================================================

export interface NHSBSAPractice {
  practice_code: string;
  practice_name: string;
  address_1: string;
  postcode: string;
  latitude: number;
  longitude: number;
  patients_registered: number;
  accepting_patients: boolean;
  distance_km?: number;
}

export interface NHSBSAHealthIndicator {
  items_per_1000_patients: number;
  national_average: number;
  vs_national_percent: number;
  trend: string;
  significance: string;
}

export interface NHSBSATopMedication {
  name: string;
  items: number;
}

export interface NHSBSAHealthIndex {
  score: number;
  rating: string;
  interpretation: string;
  percentile: number;
}

export interface NHSBSACareHomeConsideration {
  category: string;
  finding: string;
  implication: string;
  priority: 'high' | 'medium' | 'low';
}

export interface NHSBSAHealthProfile {
  location: {
    latitude: number;
    longitude: number;
  };
  practices_analyzed: number;
  total_patients: number;
  nearest_practice: NHSBSAPractice | null;
  health_indicators: Record<string, NHSBSAHealthIndicator>;
  top_medications: NHSBSATopMedication[];
  health_index: NHSBSAHealthIndex;
  care_home_considerations: NHSBSACareHomeConsideration[];
  data_period: string;
  methodology: string;
  fetched_at: string;
  error?: string;
}

export interface NHSBSANearestPractices {
  care_home_location: {
    latitude: number;
    longitude: number;
  };
  search_radius_km: number;
  practices_found: number;
  nearest_practices: Array<{
    distance_km: number;
    data: NHSBSAPractice;
  }>;
  healthcare_access_rating: {
    rating: string;
    score: number;
    description: string;
  };
  fetched_at: string;
  error?: string;
}

// ============================================================
// COMBINED NEIGHBOURHOOD ANALYSIS
// ============================================================

export interface NeighbourhoodOverall {
  score: number;
  rating: string;
  confidence: string;
  breakdown: Array<{
    name: string;
    score: number;
    weight: string;
  }>;
}

export interface NeighbourhoodAnalysisResult {
  postcode: string;
  coordinates?: {
    latitude: number;
    longitude: number;
  };
  os_places?: OSPlacesResult;
  ons?: ONSFullProfile;
  osm?: {
    walk_score: OSMWalkScore;
    amenities: OSMAmenitiesResult;
    infrastructure: OSMInfrastructure;
  };
  nhsbsa?: NHSBSAHealthProfile;
  overall?: NeighbourhoodOverall;
  errors?: Record<string, string>;
  fetched_at: string;
}

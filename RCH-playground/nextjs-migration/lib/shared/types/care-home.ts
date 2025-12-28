/**
 * Care Home Types
 * Shared types for care home data structures
 */

export type CareType = 'residential' | 'nursing' | 'dementia' | 'respite';

export interface CareHome {
  // Basic info
  id?: string;
  name: string;
  address?: string;
  postcode: string;
  city?: string;
  
  // Location
  latitude?: number;
  longitude?: number;
  distanceKm?: number;
  
  // Care details
  careTypes?: CareType[];
  cqcRating?: string;
  
  // Pricing
  weeklyPrice?: number;
  weeklyCost?: number;
  priceRange?: {
    min: number;
    max: number;
  };
  
  // Additional fields (flexible for different data sources)
  [key: string]: any;
}

export interface PostcodeInfo {
  postcode: string;
  localAuthority?: string;
  latitude?: number;
  longitude?: number;
  region?: string;
}




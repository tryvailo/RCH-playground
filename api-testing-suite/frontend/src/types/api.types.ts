/**
 * API Types for RightCareHome Testing Suite
 */

export type ApiStatus = 'connected' | 'disconnected' | 'testing' | 'error';

export interface ApiStatusInfo {
  name: string;
  status: ApiStatus;
  lastTested?: Date;
  successRate: number;
  avgResponseTime: number;
}

export interface QuickStats {
  totalAPIs: number;
  connectedAPIs: number;
  totalCosts: number;
  testsPassed: number;
}

export interface DashboardView {
  apis: ApiStatusInfo[];
  recentTests: TestResult[];
  quickStats: QuickStats;
}

export interface ApiCredentials {
  cqc?: {
    partnerCode?: string;
    useWithoutCode: boolean;
    primarySubscriptionKey?: string;
    secondarySubscriptionKey?: string;
  };
  fsa?: Record<string, any>;
  companiesHouse?: {
    apiKey: string;
  };
  googlePlaces?: {
    apiKey: string;
  };
  googlePlacesInsights?: {
    projectId: string;
    datasetId: string;
  };
  perplexity?: {
    apiKey: string;
  };
  besttime?: {
    privateKey: string;
    publicKey: string;
  };
  autumna?: {
    proxyUrl?: string;
    useProxy: boolean;
  };
  openai?: {
    apiKey: string;
  };
  firecrawl?: {
    apiKey: string;
  };
}

export interface DataQuality {
  completeness: number;
  accuracy: number;
  freshness: string;
}

export interface ApiTestResult {
  apiName: string;
  status: 'success' | 'failure' | 'partial';
  responseTime: number;
  dataReturned: boolean;
  dataQuality: DataQuality;
  errors: string[];
  warnings: string[];
  rawResponse: Record<string, any>;
  costIncurred: number;
}

export interface TestResult {
  jobId: string;
  status: 'running' | 'completed' | 'failed';
  startedAt: string;
  completedAt?: string;
  results: Record<string, ApiTestResult>;
  fusionAnalysis?: Record<string, any>;
  totalCost: number;
  progress: number;
}

export interface TestRequest {
  homeName?: string;
  address?: string;
  city?: string;
  postcode?: string;
  latitude?: number;
  longitude?: number;
  region?: string;
  companyName?: string;
  query?: string;
  maxDistance?: number;
  limit?: number;
}

export interface ComprehensiveTestRequest {
  homeName: string;
  address?: string;
  city?: string;
  postcode?: string;
  apisToTest: string[];
}

export interface CostBreakdown {
  api: string;
  calls: number;
  costPerCall: number;
  totalCost: number;
  currency: string;
}

export interface HomeData {
  name: string;
  address?: string;
  city?: string;
  postcode?: string;
  cqcRating?: string;
}

export const TEST_HOMES: HomeData[] = [
  {
    name: "Kinross Residential Care Home",
    address: "201 Havant Road, Drayton",
    city: "Portsmouth",
    postcode: "PO6 1EE",
    cqcRating: "Unknown"
  },
  {
    name: "Meadows House Residential and Nursing Home",
    address: "Cullum Welch Court",
    city: "London",
    postcode: "SE3 0PW",
    cqcRating: "Unknown"
  },
  {
    name: "Roborough House",
    address: "Tamerton Road, Woolwell",
    city: "Plymouth",
    postcode: "PL6 7BQ",
    cqcRating: "Unknown"
  },
  {
    name: "Manor House Care Home",
    address: "123 High Street",
    city: "Brighton",
    postcode: "BN1 1AB",
    cqcRating: "Outstanding"
  },
  {
    name: "Oaklands Nursing Home",
    address: "456 Park Road",
    city: "Manchester",
    postcode: "M1 1AD",
    cqcRating: "Good"
  }
];


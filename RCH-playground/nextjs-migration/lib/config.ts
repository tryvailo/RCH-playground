/**
 * Configuration
 * Feature flags and API endpoints configuration
 */

export const USE_NEW_API = process.env.NEXT_PUBLIC_USE_NEW_API === 'true';

export const API_ENDPOINTS = {
  // Old API (Python/FastAPI)
  OLD_FREE_REPORT: process.env.NEXT_PUBLIC_OLD_API_URL
    ? `${process.env.NEXT_PUBLIC_OLD_API_URL}/api/free-report`
    : 'http://localhost:8000/api/free-report',
  OLD_PROFESSIONAL_REPORT: process.env.NEXT_PUBLIC_OLD_API_URL
    ? `${process.env.NEXT_PUBLIC_OLD_API_URL}/api/professional-report`
    : 'http://localhost:8000/api/professional-report',

  // New API (Next.js)
  NEW_FREE_REPORT: '/api/free-report',
  NEW_PROFESSIONAL_REPORT: '/api/professional-report',
};

export function getApiEndpoint(type: 'free' | 'professional'): string {
  if (USE_NEW_API) {
    return type === 'free'
      ? API_ENDPOINTS.NEW_FREE_REPORT
      : API_ENDPOINTS.NEW_PROFESSIONAL_REPORT;
  } else {
    return type === 'free'
      ? API_ENDPOINTS.OLD_FREE_REPORT
      : API_ENDPOINTS.OLD_PROFESSIONAL_REPORT;
  }
}




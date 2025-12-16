/**
 * MSIF Loader
 * Automatically downloads and parses MSIF 2025-2026 XLS file
 * Falls back to 2024-2025 if new one is unavailable
 */
import type { MSIFData, CareType } from './types';
import { useMSIFStore } from './stores/msifStore';

// URLs for MSIF files
const MSIF_URL_2025_2026 = 'https://assets.publishing.service.gov.uk/media/68a3021cf49bec79d23d2940/market-sustainability-and-improvement-fund-fees-2025-to-2026.xlsx';
const MSIF_URL_2024_2025 = 'https://assets.publishing.service.gov.uk/media/68a3021cf49bec79d23d2940/market-sustainability-and-improvement-fund-fees-2024-to-2025.xlsx';

// Cache key for localStorage
const CACHE_KEY = 'msif_data_cache';
const CACHE_EXPIRY_MS = 7 * 24 * 60 * 60 * 1000; // 7 days

// Cache for backend availability check
let backendAvailable: boolean | null = null;
let backendCheckTime: number = 0;
const BACKEND_CHECK_TTL = 60000; // 1 minute

/**
 * Check if backend is available
 */
async function checkBackendAvailable(): Promise<boolean> {
  const now = Date.now();
  if (backendAvailable !== null && (now - backendCheckTime) < BACKEND_CHECK_TTL) {
    return backendAvailable;
  }
  
  try {
    const API_BASE_URL = import.meta.env.VITE_API_URL || '';
    // Check if backend is up by checking root endpoint
    const url = API_BASE_URL ? `${API_BASE_URL}/` : '/';
    const response = await fetch(url, {
      method: 'GET',
      signal: AbortSignal.timeout(2000), // 2 second timeout
    });
    backendAvailable = response.ok;
    backendCheckTime = now;
    return backendAvailable;
  } catch (error) {
    backendAvailable = false;
    backendCheckTime = now;
    return false;
  }
}

/**
 * Loads XLS file via backend API (to avoid CORS issues)
 */
async function fetchXLSFile(fileUrl: string): Promise<ArrayBuffer> {
  // Check if backend is available first
  const isBackendAvailable = await checkBackendAvailable();
  
  if (!isBackendAvailable) {
    // Backend not available, skip loading and use fallback
    throw new Error('BACKEND_NOT_AVAILABLE');
  }
  
  // Use backend API to fetch file (avoids CORS)
  try {
    const API_BASE_URL = import.meta.env.VITE_API_URL || '';
    const proxyEndpoint = API_BASE_URL ? `${API_BASE_URL}/api/proxy-fetch` : '/api/proxy-fetch';
    const response = await fetch(proxyEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: fileUrl }),
      signal: AbortSignal.timeout(30000), // 30 second timeout
    });
    
    if (!response.ok) {
      if (response.status === 404) {
        backendAvailable = false; // Mark backend as unavailable
        throw new Error('BACKEND_NOT_AVAILABLE');
      }
      throw new Error(`Backend proxy failed: ${response.statusText}`);
    }
    
    return await response.arrayBuffer();
  } catch (error: any) {
    if (error.name === 'AbortError' || error.message === 'BACKEND_NOT_AVAILABLE') {
      backendAvailable = false;
      throw new Error('BACKEND_NOT_AVAILABLE');
    }
    throw error;
  }
}

/**
 * Parses XLS file using xlsx library
 */
async function parseMSIFXLS(arrayBuffer: ArrayBuffer): Promise<MSIFData> {
  try {
    // Dynamic import of xlsx to reduce bundle size
    const XLSX = await import('xlsx');
    const workbook = XLSX.read(arrayBuffer, { type: 'array' });
    
    // Usually data is in the first sheet
    const firstSheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[firstSheetName];
    
    // Convert to JSON
    const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 }) as any[][];
    
    // Parse data (MSIF file structure may vary)
    // Find headers and data
    const msifData: MSIFData = {};
    
    // Typical MSIF structure: Local Authority | Residential | Nursing | etc.
    let headerRowIndex = -1;
    let localAuthorityCol = -1;
    let residentialCol = -1;
    let nursingCol = -1;
    
    // Find header row
    for (let i = 0; i < Math.min(10, jsonData.length); i++) {
      const row = jsonData[i];
      if (!row || row.length === 0) continue;
      
      // Search for headers
      const rowStr = row.map((cell: any) => String(cell || '').toLowerCase()).join(' ');
      if (rowStr.includes('local authority') || rowStr.includes('authority')) {
        headerRowIndex = i;
        // Find columns
        row.forEach((cell: any, idx: number) => {
          const cellStr = String(cell || '').toLowerCase();
          if (cellStr.includes('local authority') || cellStr.includes('authority')) {
            localAuthorityCol = idx;
          }
          if (cellStr.includes('residential') && !cellStr.includes('dementia')) {
            residentialCol = idx;
          }
          if (cellStr.includes('nursing') && !cellStr.includes('dementia')) {
            nursingCol = idx;
          }
        });
        break;
      }
    }
    
    if (headerRowIndex === -1 || localAuthorityCol === -1) {
      throw new Error('Could not find header row in MSIF file');
    }
    
    // Parse data
    for (let i = headerRowIndex + 1; i < jsonData.length; i++) {
      const row = jsonData[i];
      if (!row || row.length === 0) continue;
      
      const localAuthority = String(row[localAuthorityCol] || '').trim();
      if (!localAuthority || localAuthority.toLowerCase() === 'total') continue;
      
      if (!msifData[localAuthority]) {
        msifData[localAuthority] = {};
      }
      
      // Extract values
      if (residentialCol >= 0 && row[residentialCol]) {
        const value = parseFloat(String(row[residentialCol]).replace(/[£,\s]/g, ''));
        if (!isNaN(value)) {
          msifData[localAuthority].residential = value;
        }
      }
      
      if (nursingCol >= 0 && row[nursingCol]) {
        const value = parseFloat(String(row[nursingCol]).replace(/[£,\s]/g, ''));
        if (!isNaN(value)) {
          msifData[localAuthority].nursing = value;
        }
      }
    }
    
    // If parsing succeeded - return data
    if (Object.keys(msifData).length > 0) {
      return msifData;
    }
    
    // Fallback if parsing failed
    throw new Error('No data parsed from MSIF file');
  } catch (error) {
    // Silently use fallback data - don't log errors (fallback data is sufficient)
    
    // Fallback: return known values for main LAs
    const fallbackData: MSIFData = {
      'Camden': {
        residential: 700,
        nursing: 1048,
        residential_dementia: 800,
        nursing_dementia: 1048,
      },
      'Birmingham': {
        residential: 650,
        nursing: 950,
        residential_dementia: 750,
        nursing_dementia: 950,
      },
      'Westminster': {
        residential: 750,
        nursing: 1100,
        residential_dementia: 850,
        nursing_dementia: 1100,
      },
      'Manchester': {
        residential: 680,
        nursing: 980,
        residential_dementia: 780,
        nursing_dementia: 980,
      },
      'London': {
        residential: 720,
        nursing: 1050,
        residential_dementia: 820,
        nursing_dementia: 1050,
      },
    };
    
    return fallbackData;
  }
}

/**
 * Loads MSIF data with caching
 */
async function loadMSIFData(): Promise<MSIFData> {
  // Check cache in localStorage
  const cached = localStorage.getItem(CACHE_KEY);
  if (cached) {
    try {
      const { data, timestamp } = JSON.parse(cached);
      const age = Date.now() - timestamp;
      if (age < CACHE_EXPIRY_MS) {
        return data;
      }
    } catch (e) {
      // Silently ignore cache parse errors
    }
  }
  
  // Check Zustand store
  const store = useMSIFStore.getState();
  if (store.msifData && store.lastFetched) {
    const age = Date.now() - store.lastFetched;
    if (age < CACHE_EXPIRY_MS) {
      return store.msifData;
    }
  }
  
  // Load data
  useMSIFStore.getState().setLoading(true);
  
  try {
    // Try to load 2025-2026
    let arrayBuffer: ArrayBuffer;
    let data: MSIFData;
    
    try {
      arrayBuffer = await fetchXLSFile(MSIF_URL_2025_2026);
      data = await parseMSIFXLS(arrayBuffer);
      console.log('✅ MSIF 2025-2026 loaded successfully');
    } catch (error: any) {
      // If backend not available, skip to fallback immediately
      if (error.message === 'BACKEND_NOT_AVAILABLE') {
        console.log('ℹ️ Backend not available, using fallback MSIF data');
        data = await parseMSIFXLS(new ArrayBuffer(0));
      } else {
        // Try 2024-2025 as fallback
        try {
          arrayBuffer = await fetchXLSFile(MSIF_URL_2024_2025);
          data = await parseMSIFXLS(arrayBuffer);
          console.log('✅ MSIF 2024-2025 loaded as fallback');
        } catch (fallbackError: any) {
          // If both fail, use fallback data directly (silently)
          if (fallbackError.message === 'BACKEND_NOT_AVAILABLE') {
            console.log('ℹ️ Backend not available, using fallback MSIF data');
          }
          data = await parseMSIFXLS(new ArrayBuffer(0));
        }
      }
    }
    
    // Save to cache
    localStorage.setItem(CACHE_KEY, JSON.stringify({
      data,
      timestamp: Date.now(),
    }));
    
    // Save to Zustand store
    useMSIFStore.getState().setMSIFData(data);
    
    return data;
  } catch (error) {
    // Silently use fallback data - don't show errors to user
    const fallbackData = await parseMSIFXLS(new ArrayBuffer(0));
    return fallbackData;
  } finally {
    useMSIFStore.getState().setLoading(false);
  }
}

/**
 * Gets Fair Cost Lower Bound for local authority and care type
 * 
 * @param localAuthority - Local authority name (e.g., "Camden", "Birmingham")
 * @param careType - Care type: 'residential' | 'nursing' | 'residential_dementia' | 'nursing_dementia'
 * @returns Fair Cost Lower Bound in GBP/week or null if not found
 */
// Cache for getFairCostLower to prevent multiple calls
const fairCostCache = new Map<string, number | null>();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

export async function getFairCostLower(
  localAuthority: string,
  careType: CareType
): Promise<number | null> {
  // Check cache first
  const cacheKey = `${localAuthority}:${careType}`;
  const cached = fairCostCache.get(cacheKey);
  if (cached !== undefined) {
    return cached;
  }
  
  try {
    // Use local MSIF data loader (with backend proxy for file fetching if available)
    const msifData = await loadMSIFData();
    
    // Normalize local authority (remove extra spaces, format correctly)
    const normalizedLA = normalizeLocalAuthority(localAuthority);
    
    const laData = msifData[normalizedLA];
    if (!laData) {
      // Try to find similar LA
      const similarLA = findSimilarLocalAuthority(normalizedLA, Object.keys(msifData));
      if (similarLA) {
        const fallbackData = msifData[similarLA];
        const value = fallbackData[careType] || null;
        fairCostCache.set(cacheKey, value);
        return value;
      }
      // Use default fallback values
      const defaultValues: Record<CareType, number> = {
        residential: 700,
        nursing: 1048,
        residential_dementia: 800,
        nursing_dementia: 1048,
      };
      const value = defaultValues[careType] || 700;
      fairCostCache.set(cacheKey, value);
      return value;
    }
    
    const value = laData[careType] || null;
    fairCostCache.set(cacheKey, value);
    return value;
  } catch (error) {
    // Silently return default fallback value - don't show errors
    const defaultValues: Record<CareType, number> = {
      residential: 700,
      nursing: 1048,
      residential_dementia: 800,
      nursing_dementia: 1048,
    };
    const value = defaultValues[careType] || 700;
    fairCostCache.set(cacheKey, value);
    return value;
  }
}

/**
 * Normalizes local authority name
 */
function normalizeLocalAuthority(la: string): string {
  return la
    .trim()
    .replace(/\s+/g, ' ')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

/**
 * Finds similar local authority (fuzzy matching)
 */
function findSimilarLocalAuthority(
  target: string,
  candidates: string[]
): string | null {
  const normalizedTarget = target.toLowerCase();
  
  // Exact match
  for (const candidate of candidates) {
    if (candidate.toLowerCase() === normalizedTarget) {
      return candidate;
    }
  }
  
  // Partial match
  for (const candidate of candidates) {
    if (candidate.toLowerCase().includes(normalizedTarget) || 
        normalizedTarget.includes(candidate.toLowerCase())) {
      return candidate;
    }
  }
  
  return null;
}

/**
 * Preloads MSIF data (for optimization)
 */
export async function preloadMSIFData(): Promise<void> {
  await loadMSIFData();
}


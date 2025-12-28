import axios, { AxiosError } from 'axios';
import type { ProfessionalQuestionnaireResponse, ProfessionalCareHome } from '../types';

/**
 * Enrichment error details for detailed logging
 */
interface EnrichmentError {
  source: string;
  homeName: string;
  error: any;
  errorType: 'network' | 'timeout' | 'server' | 'client' | 'unknown';
  isRetryable: boolean;
  message: string;
  details?: any;
}

/**
 * Health check before enrichment requests
 */
async function checkServerHealth(apiBaseUrl: string): Promise<boolean> {
  try {
    // ✅ FIX: Use relative path through Vite proxy by default
    const healthUrl = apiBaseUrl ? `${apiBaseUrl}/health` : '/health';
    await axios.get(healthUrl, { timeout: 2000 });
    console.log('✅ Server health check passed');
    return true;
  } catch (error) {
    // Health check failed silently - server might be up but health endpoint slow/unavailable
    // This is non-critical, so we continue with enrichment
    console.warn('⚠️ Health check failed (non-critical, continuing anyway)');
    return false;
  }
}

/**
 * Detailed error handler for enrichment requests
 */
function handleEnrichmentError(
  error: any,
  source: string,
  homeName: string,
  url: string
): EnrichmentError {
  const enrichmentError: EnrichmentError = {
    source,
    homeName,
    error,
    errorType: 'unknown',
    isRetryable: false,
    message: 'Unknown error',
  };

  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError;
    
    // Check if request was canceled
    if (axiosError.code === 'ERR_CANCELED' || axiosError.message === 'canceled' || axiosError.name === 'CanceledError') {
      enrichmentError.errorType = 'timeout';
      enrichmentError.isRetryable = true;
      enrichmentError.message = `Request was canceled for ${source}`;
      enrichmentError.details = {
        code: axiosError.code,
        aborted: (axiosError.request as any)?.signal?.aborted,
      };
      return enrichmentError;
    }

    // Network error - server not reachable
    if (axiosError.code === 'ECONNABORTED' || axiosError.code === 'ETIMEDOUT' || axiosError.message.includes('timeout')) {
      enrichmentError.errorType = 'timeout';
      enrichmentError.isRetryable = true;
      enrichmentError.message = `Request timeout for ${source} (${url})`;
      enrichmentError.details = {
        code: axiosError.code,
        timeout: axiosError.config?.timeout,
      };
      return enrichmentError;
    }

    // Network error - no connection
    if (axiosError.code === 'ERR_NETWORK' || axiosError.message.includes('Network Error') || (!axiosError.response && axiosError.code !== 'ERR_CANCELED')) {
      enrichmentError.errorType = 'network';
      enrichmentError.isRetryable = true;
      enrichmentError.message = `Cannot connect to server for ${source} (${url})`;
      enrichmentError.details = {
        code: axiosError.code,
        message: axiosError.message,
      };
      return enrichmentError;
    }

    // Server responded with error
    if (axiosError.response) {
      const status = axiosError.response.status;
      enrichmentError.errorType = status >= 500 ? 'server' : 'client';
      enrichmentError.isRetryable = status >= 500;
      enrichmentError.message = `Server error for ${source}: ${status} ${axiosError.response.statusText}`;
      enrichmentError.details = {
        status,
        statusText: axiosError.response.statusText,
        data: axiosError.response.data,
        url,
      };
      return enrichmentError;
    }

    // Unknown axios error
    enrichmentError.errorType = 'unknown';
    enrichmentError.message = `Unknown axios error for ${source}: ${axiosError.message}`;
    enrichmentError.details = {
      code: axiosError.code,
      message: axiosError.message,
      name: axiosError.name,
    };
    return enrichmentError;
  }

  // Handle abort errors
  if (error instanceof Error && error.name === 'AbortError') {
    enrichmentError.errorType = 'timeout';
    enrichmentError.isRetryable = true;
    enrichmentError.message = `Request aborted for ${source}`;
    return enrichmentError;
  }

  // Generic error
  enrichmentError.message = error instanceof Error ? error.message : String(error);
  return enrichmentError;
}

/**
 * Make enriched API request with detailed error handling and retry logic
 * FIXED: AbortController signal is now properly passed to axios
 */
async function makeEnrichmentRequest<T>(
  source: string,
  homeName: string,
  requestFn: (signal: AbortSignal) => Promise<T>,
  retries: number = 1,
  timeout: number = 15000
): Promise<{ data: T | null; error: EnrichmentError | null }> {
  let lastError: EnrichmentError | null = null;
  
  for (let attempt = 0; attempt <= retries; attempt++) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      controller.abort();
    }, timeout);

    try {
      // ✅ FIX: Pass signal to request function
      const result = await requestFn(controller.signal);
      clearTimeout(timeoutId);
      return { data: result, error: null };
    } catch (error: any) {
      clearTimeout(timeoutId);
      
      const enrichmentError = handleEnrichmentError(
        error,
        source,
        homeName,
        error.config?.url || 'unknown'
      );
      
      lastError = enrichmentError;
      
      // Log detailed error
      console.error(`❌ [${source}] Error for ${homeName} (attempt ${attempt + 1}/${retries + 1}):`, {
        errorType: enrichmentError.errorType,
        message: enrichmentError.message,
        isRetryable: enrichmentError.isRetryable,
        details: enrichmentError.details,
      });

      // If not retryable or last attempt, return error
      if (!enrichmentError.isRetryable || attempt >= retries) {
        break;
      }

      // Exponential backoff: 1s, 2s, 4s
      const delay = Math.pow(2, attempt) * 1000;
      console.log(`⏳ Retrying ${source} for ${homeName} in ${delay}ms...`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  return { data: null, error: lastError };
}

/**
 * Enrich top-30 candidates for matching (CQC + Financial only)
 * This is used BEFORE final top-5 selection to improve match scores
 * Matches old report logic: enrich top-30 → re-score → select top-5
 */
export async function enrichTop30ForMatching(
  homes: ProfessionalCareHome[],
  apiBaseUrl: string
): Promise<ProfessionalCareHome[]> {
  try {
    console.log(`📊 Enriching top ${homes.length} candidates for matching (CQC + Financial only)`);
    
    // Process homes in batches (like old version: batch_size=5 for CQC, batch_size=3 for Financial)
    const CQC_BATCH_SIZE = 5;
    const FINANCIAL_BATCH_SIZE = 3;
    const enrichedHomes: ProfessionalCareHome[] = [];
    
    // Enrich CQC data (batch processing like old version)
    for (let i = 0; i < homes.length; i += CQC_BATCH_SIZE) {
      const batch = homes.slice(i, i + CQC_BATCH_SIZE);
      console.log(`📦 CQC batch ${Math.floor(i / CQC_BATCH_SIZE) + 1}/${Math.ceil(homes.length / CQC_BATCH_SIZE)}`);
      
      const batchPromises = batch.map(async (home) => {
        const enrichedHome = { ...home };
        const homeName = home.name || '';
        const postcode = home.postcode || '';
        const locationId = home.id || (home as any).cqc_location_id;
        
        // CQC enrichment
        if (homeName || locationId) {
          // ✅ FIX: Use relative path through Vite proxy by default
          const cqcUrl = apiBaseUrl ? `${apiBaseUrl}/api/cqc` : '/api/cqc';
          const { data, error } = await makeEnrichmentRequest(
            'CQC',
            homeName,
            (signal) => axios.get(cqcUrl, {
              params: { 
                name: homeName, 
                postcode: postcode,
                location_id: locationId,
                cache: true 
              },
              timeout: 15000,
              signal,
            }),
            1,
            15000
          );
          
          if (data && data.status === 'success' && data.data && Object.keys(data.data).length > 0) {
            enrichedHome.cqcDeepDive = data.data;
          }
        }
        
        return enrichedHome;
      });
      
      const batchResults = await Promise.all(batchPromises);
      enrichedHomes.push(...batchResults);
      
      // Delay between batches (like old version: 1s for CQC)
      if (i + CQC_BATCH_SIZE < homes.length) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    
    // Enrich Financial data (batch processing like old version)
    for (let i = 0; i < enrichedHomes.length; i += FINANCIAL_BATCH_SIZE) {
      const batch = enrichedHomes.slice(i, i + FINANCIAL_BATCH_SIZE);
      console.log(`📦 Financial batch ${Math.floor(i / FINANCIAL_BATCH_SIZE) + 1}/${Math.ceil(enrichedHomes.length / FINANCIAL_BATCH_SIZE)}`);
      
      const batchPromises = batch.map(async (home) => {
        const homeName = home.name || '';
        const postcode = home.postcode || '';
        
        // Financial enrichment
        if (homeName) {
          // ✅ FIX: Use relative path through Vite proxy by default
          const financialUrl = apiBaseUrl ? `${apiBaseUrl}/api/financial` : '/api/financial';
          const { data, error } = await makeEnrichmentRequest(
            'Financial',
            homeName,
            (signal) => axios.get(financialUrl, {
              params: { 
                name: homeName, 
                postcode: postcode,
                cache: true 
              },
              timeout: 15000,
              signal,
            }),
            1,
            15000
          );
          
          if (data && data.status === 'success' && data.data && Object.keys(data.data).length > 0) {
            home.financialStability = data.data;
          }
        }
        
        return home;
      });
      
      const batchResults = await Promise.all(batchPromises);
      // Update enrichedHomes with financial data
      batchResults.forEach((enriched, idx) => {
        enrichedHomes[i + idx] = enriched;
      });
      
      // Delay between batches (like old version: 2s for Financial)
      if (i + FINANCIAL_BATCH_SIZE < enrichedHomes.length) {
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }
    
    console.log(`✅ Enriched ${enrichedHomes.length} candidates for matching`);
    return enrichedHomes;
  } catch (error) {
    console.error('❌ Error enriching top-30 for matching:', error);
    // Return homes without enrichment if error occurs
    return homes;
  }
}

/**
 * Full enrichment with 15+ data sources
 * Matches the backend enrichment pipeline for top-5 finalists
 * Includes comprehensive error handling like old version
 */
export async function enrichHomes(
  homes: ProfessionalCareHome[],
  _questionnaire: ProfessionalQuestionnaireResponse, // ✅ FIX: Prefixed with _ to indicate intentionally unused (may be used in future)
  apiBaseUrl: string
): Promise<ProfessionalCareHome[]> {
  try {
    console.log(`📊 Starting full enrichment for ${homes.length} homes (15+ sources)`);
    
    // ✅ FIX: Health check before starting enrichment - fail early if server unavailable
    const isHealthy = await checkServerHealth(apiBaseUrl);
    if (!isHealthy) {
      console.error('❌ Server health check failed - server may be unavailable');
      throw new Error(
        'Server health check failed. The backend server may be unavailable. ' +
        'Please check if the server is running and try again.'
      );
    }
    
    // ✅ FIX: Process homes in batches to limit parallel requests
    // Batch size: 2 homes at a time to prevent rate limiting
    const BATCH_SIZE = 2;
    const enrichedHomes: ProfessionalCareHome[] = [];
    
    for (let i = 0; i < homes.length; i += BATCH_SIZE) {
      const batch = homes.slice(i, i + BATCH_SIZE);
      console.log(`📦 Processing batch ${Math.floor(i / BATCH_SIZE) + 1}/${Math.ceil(homes.length / BATCH_SIZE)} (${batch.length} homes)`);
      
      // Process batch in parallel
      const batchPromises = batch.map(async (home) => {
      const enrichedHome = { ...home };
      const enrichmentErrors: EnrichmentError[] = [];

      try {
        // Extract location data for enrichment
        const homeName = home.name || '';
        const postcode = home.postcode || '';
        const locationId = home.id || (home as any).cqc_location_id;
        const latitude = (home as any).latitude || (home as any).lat;
        const longitude = (home as any).longitude || (home as any).lon;

        // ============================================
        // CORE ENRICHMENT SOURCES (6 sources)
        // ============================================

        // 1. CQC Deep Dive (Care Quality Commission)
        if (homeName || locationId) {
          // ✅ FIX: Use relative path through Vite proxy by default
          const cqcUrl = apiBaseUrl ? `${apiBaseUrl}/api/cqc` : '/api/cqc';
          const { data, error } = await makeEnrichmentRequest(
            'CQC',
            homeName,
            (signal) => axios.get(cqcUrl, {
              params: { 
                name: homeName, 
                postcode: postcode,
                location_id: locationId,
                cache: true 
              },
              timeout: 15000,
              signal, // ✅ FIX: Pass AbortController signal
            }),
            1, // 1 retry for CQC
            15000
          );
          
          // ✅ FIX: Handle "not_available" status gracefully (like old version)
          if (data && data.data) {
            if (data.status === 'success' && Object.keys(data.data).length > 0) {
              enrichedHome.cqcDeepDive = data.data;
              console.log(`  ✅ CQC data enriched for ${homeName}`);
            } else if (data.status === 'not_available') {
              // API not configured - skip silently (graceful degradation)
              console.log(`  ⏭️  CQC enrichment skipped for ${homeName}: ${data.message || 'API not configured'}`);
            } else if (data.status === 'not_found') {
              // No data found - skip silently (not an error)
              console.log(`  ⏭️  CQC data not found for ${homeName}`);
            }
          } else if (error) {
            // ✅ FIX: Only log as warning, don't treat as critical error
            // Old version continues processing even if enrichment fails
            if (error.errorType === 'client' && error.details?.status === 401) {
              // API not configured - skip silently
              console.log(`  ⏭️  CQC enrichment skipped for ${homeName}: API not configured`);
            } else {
              enrichmentErrors.push(error);
              console.warn(`  ⚠️ CQC enrichment failed for ${homeName}: ${error.message}`);
            }
          }
        }

        // 2. FSA Detailed (Food Standards Agency) - Full data, not just rating
        if (homeName && postcode) {
          // First, search for FSA establishment
          // ✅ FIX: Use relative path through Vite proxy by default
          const fsaSearchUrl = apiBaseUrl ? `${apiBaseUrl}/api/fsa/search` : '/api/fsa/search';
          const { data: searchData, error: searchError } = await makeEnrichmentRequest(
            'FSA Search',
            homeName,
            (signal) => axios.get(fsaSearchUrl, {
              params: { 
                name: homeName,
                postcode: postcode,
                cache: true 
              },
              timeout: 10000,
              signal, // ✅ FIX: Pass AbortController signal
            }),
            1,
            10000
          );

          if (searchError) {
            enrichmentErrors.push(searchError);
            console.warn(`  ⚠️ FSA search failed for ${homeName}: ${searchError.message}`);
          } else if (searchData?.data?.establishments?.[0]?.fhrs_id) {
            const fhrsId = searchData.data.establishments[0].fhrs_id;
            
            // Get detailed FSA data
            // ✅ FIX: Use relative path through Vite proxy by default
            const fsaDetailUrl = apiBaseUrl 
              ? `${apiBaseUrl}/api/fsa/establishment/${fhrsId}` 
              : `/api/fsa/establishment/${fhrsId}`;
            
            const { data: detailData, error: detailError } = await makeEnrichmentRequest(
              'FSA Detail',
              homeName,
              (signal) => axios.get(fsaDetailUrl, {
                params: { include_health_score: true, cache: true },
                timeout: 10000,
                signal, // ✅ FIX: Pass AbortController signal
              }),
              1,
              10000
            );

            if (detailData?.data) {
              enrichedHome.fsaDetailed = detailData.data;
              console.log(`  ✅ FSA Detailed enriched for ${homeName}`);
            } else if (detailError) {
              enrichmentErrors.push(detailError);
              console.warn(`  ⚠️ FSA detail failed for ${homeName}: ${detailError.message}`);
            }
          }
        }

        // 3. Financial Stability (Companies House)
        if (homeName) {
          // ✅ FIX: Use relative path through Vite proxy by default
          const financialUrl = apiBaseUrl ? `${apiBaseUrl}/api/financial` : '/api/financial';
          const { data, error } = await makeEnrichmentRequest(
            'Financial',
            homeName,
            (signal) => axios.get(financialUrl, {
              params: { 
                name: homeName, 
                postcode: postcode,
                cache: true 
              },
              timeout: 15000,
              signal, // ✅ FIX: Pass AbortController signal
            }),
            1,
            15000
          );
          
          // ✅ FIX: Handle "not_available" status gracefully (like old version)
          if (data && data.data) {
            if (data.status === 'success' && Object.keys(data.data).length > 0) {
              enrichedHome.financialStability = data.data;
              console.log(`  ✅ Financial data enriched for ${homeName}`);
            } else if (data.status === 'not_available') {
              // API not configured - skip silently (graceful degradation)
              console.log(`  ⏭️  Financial enrichment skipped for ${homeName}: ${data.message || 'API not configured'}`);
            } else if (data.status === 'not_found') {
              // No data found - skip silently (not an error)
              console.log(`  ⏭️  Financial data not found for ${homeName}`);
            }
          } else if (error) {
            // ✅ FIX: Only log as warning, don't treat as critical error
            // Old version continues processing even if enrichment fails
            if (error.errorType === 'client' && error.details?.status === 401) {
              // API not configured - skip silently
              console.log(`  ⏭️  Financial enrichment skipped for ${homeName}: API not configured`);
            } else {
              enrichmentErrors.push(error);
              console.warn(`  ⚠️ Financial enrichment failed for ${homeName}: ${error.message}`);
            }
          }
        }

        // 4. Google Places (with Insights)
        if (homeName && postcode) {
          // ✅ FIX: Use relative path through Vite proxy by default
          const googleUrl = apiBaseUrl ? `${apiBaseUrl}/api/google-places` : '/api/google-places';
          const { data, error } = await makeEnrichmentRequest(
            'Google Places',
            homeName,
            (signal) => axios.get(googleUrl, {
              params: { 
                name: homeName, 
                postcode: postcode,
                include_insights: true,
                cache: true 
              },
              timeout: 15000,
              signal, // ✅ FIX: Pass AbortController signal
            }),
            1,
            15000
          );
          
          if (data?.data && Object.keys(data.data).length > 0) {
            enrichedHome.googlePlaces = data.data;
            console.log(`  ✅ Google Places enriched for ${homeName}`);
          } else if (error) {
            enrichmentErrors.push(error);
            console.warn(`  ⚠️ Google Places enrichment failed for ${homeName}: ${error.message}`);
          }
        }

        // 5. Staff Quality
        if (locationId) {
          // ✅ FIX: Use relative path through Vite proxy by default
          const staffUrl = apiBaseUrl ? `${apiBaseUrl}/api/staff-quality/analyze` : '/api/staff-quality/analyze';
          
          const { data, error } = await makeEnrichmentRequest(
            'Staff Quality',
            homeName,
            (signal) => axios.post(staffUrl, {
              location_id: locationId,
              home_name: homeName,
            }, {
              params: { cache: true },
              timeout: 15000,
              signal, // ✅ FIX: Pass AbortController signal
            }),
            1,
            15000
          );
          
          if (data?.data && data.data.staff_quality_score) {
            enrichedHome.staffQuality = data.data;
            console.log(`  ✅ Staff Quality enriched for ${homeName}`);
          } else if (error) {
            enrichmentErrors.push(error);
            console.warn(`  ⚠️ Staff Quality enrichment failed for ${homeName}: ${error.message}`);
          }
        }

        // 6. Neighbourhood Analysis (Location Wellbeing)
        if (postcode || (latitude && longitude)) {
          // ✅ FIX: Use relative path through Vite proxy by default
          const neighbourhoodUrl = apiBaseUrl ? `${apiBaseUrl}/api/neighbourhood` : '/api/neighbourhood';
          
          const { data, error } = await makeEnrichmentRequest(
            'Neighbourhood',
            homeName,
            (signal) => axios.get(neighbourhoodUrl, {
              params: { 
                postcode: postcode,
                latitude: latitude,
                longitude: longitude,
                include_ons: true,
                include_osm: true,
                cache: true 
              },
              timeout: 15000,
              signal, // ✅ FIX: Pass AbortController signal
            }),
            1,
            15000
          );
          
          if (data?.data && Object.keys(data.data).length > 0) {
            enrichedHome.neighbourhood = data.data;
            console.log(`  ✅ Neighbourhood enriched for ${homeName}`);
          } else if (error) {
            enrichmentErrors.push(error);
            console.warn(`  ⚠️ Neighbourhood enrichment failed for ${homeName}: ${error.message}`);
          }
        }

        // ============================================
        // ADDITIONAL ENRICHMENT SOURCES (9+ sources)
        // ============================================

        // 7. Community Reputation (from Google Places + additional sources)
        if (enrichedHome.googlePlaces) {
          try {
            const gp = enrichedHome.googlePlaces;
            // Community reputation is derived from Google Places data
            enrichedHome.communityReputation = {
              google_rating: gp.rating || null,
              google_review_count: gp.user_ratings_total || gp.reviews_count || 0,
              carehome_rating: null, // Will be populated from other sources if available
              trust_score: gp.rating ? Math.round((gp.rating / 5) * 100) : 0,
              sentiment_analysis: gp.sentiment_analysis ? {
                average_sentiment: gp.sentiment_analysis.average_sentiment ?? 0,
                sentiment_label: gp.sentiment_analysis.sentiment_label ?? 'Unknown',
                total_reviews: gp.sentiment_analysis.total_reviews ?? 0,
                positive_reviews: gp.sentiment_analysis.positive_reviews ?? 0,
                negative_reviews: gp.sentiment_analysis.negative_reviews ?? 0,
                neutral_reviews: gp.sentiment_analysis.neutral_reviews ?? 0,
                sentiment_distribution: {
                  positive: gp.sentiment_analysis.sentiment_distribution?.positive ?? 0,
                  negative: gp.sentiment_analysis.sentiment_distribution?.negative ?? 0,
                  neutral: gp.sentiment_analysis.sentiment_distribution?.neutral ?? 0,
                },
              } : {
                average_sentiment: 0,
                sentiment_label: 'Unknown',
                total_reviews: 0,
                positive_reviews: 0,
                negative_reviews: 0,
                neutral_reviews: 0,
                sentiment_distribution: {
                  positive: 0,
                  negative: 0,
                  neutral: 0,
                },
              },
              sample_reviews: (gp.reviews || []).slice(0, 5).map((r: any) => ({
                text: r.text || '',
                rating: r.rating || 0,
                author: r.author_name || 'Anonymous',
                source: 'Google Places',
                date: r.time || new Date().toISOString(),
              })),
              total_reviews_analyzed: gp.user_ratings_total || gp.reviews_count || 0,
              review_sources: ['Google Places'],
            };
            console.log(`  ✅ Community Reputation derived for ${homeName}`);
          } catch (error) {
            const err = handleEnrichmentError(error, 'Community Reputation', homeName, 'derived');
            enrichmentErrors.push(err);
          }
        }

        // 8. Medical Care Capabilities (from CQC data)
        if (enrichedHome.cqcDeepDive) {
          try {
            const cqcData = enrichedHome.cqcDeepDive;
            const regulatedActivities = cqcData.regulated_activities || [];
            enrichedHome.medicalCare = {
              medical_specialisms: (cqcData as any).specialisms || [], // ✅ FIX: Use type assertion for optional field
              regulated_activities: regulatedActivities.map((ra: any) => 
                typeof ra === 'string' ? ra : ra.name || ra.id || String(ra)
              ),
              care_residential: regulatedActivities.some((ra: any) => 
                (typeof ra === 'string' ? ra : ra.name || '').toLowerCase().includes('personal care')
              ),
              care_nursing: regulatedActivities.some((ra: any) => 
                (typeof ra === 'string' ? ra : ra.name || '').toLowerCase().includes('nursing')
              ),
              care_dementia: regulatedActivities.some((ra: any) => 
                (typeof ra === 'string' ? ra : ra.name || '').toLowerCase().includes('dementia')
              ),
              service_types: regulatedActivities.map((ra: any) => 
                typeof ra === 'string' ? ra : ra.name || ra.id || String(ra)
              ),
            };
            console.log(`  ✅ Medical Care derived for ${homeName}`);
          } catch (error) {
            const err = handleEnrichmentError(error, 'Medical Care', homeName, 'derived');
            enrichmentErrors.push(err);
          }
        }

        // 9. Safety Analysis (from CQC + FSA data)
        if (enrichedHome.cqcDeepDive || enrichedHome.fsaDetailed) {
          try {
            const cqc = enrichedHome.cqcDeepDive;
            const fsa = enrichedHome.fsaDetailed;
            const safeRating = cqc?.detailed_ratings?.safe?.rating || (cqc as any)?.safe_rating; // ✅ FIX: Use type assertion
            
            // Calculate safety score (0-100)
            let safetyScore = 50; // Base score
            if (safeRating === 'Outstanding') safetyScore = 100;
            else if (safeRating === 'Good') safetyScore = 75;
            else if (safeRating === 'Requires Improvement') safetyScore = 40;
            else if (safeRating === 'Inadequate') safetyScore = 20;
            
            if (fsa?.rating) {
              const fsaScore = (fsa.rating / 5) * 20; // FSA contributes up to 20 points
              safetyScore = Math.min(100, safetyScore + fsaScore);
            }
            
            enrichedHome.safetyAnalysis = {
              safety_score: safetyScore,
              safety_rating: safetyScore >= 80 ? 'Excellent' : 
                           safetyScore >= 60 ? 'Good' : 
                           safetyScore >= 40 ? 'Adequate' : 'Poor',
              pedestrian_safety: null, // Will be populated from neighbourhood if available
              public_transport: null, // Will be populated from neighbourhood if available
              accessibility: {
                wheelchair_accessible: (home as any).wheelchairAccessible || false,
                accessible_entrances: null,
              },
            };
            console.log(`  ✅ Safety Analysis derived for ${homeName}`);
          } catch (error) {
            const err = handleEnrichmentError(error, 'Safety Analysis', homeName, 'derived');
            enrichmentErrors.push(err);
          }
        }

        // 10. Location Wellbeing (from Neighbourhood data)
        if (enrichedHome.neighbourhood) {
          try {
            const nh = enrichedHome.neighbourhood;
            enrichedHome.locationWellbeing = {
              walkability_score: nh.walkability?.score || null,
              green_space_score: null, // Can be derived from parks count
              nearest_park_distance: null, // Can be derived from amenities
              noise_level: null, // Not available from current sources
              local_amenities: [], // Will be populated from walkability data if available
            };
            
            // Populate local_amenities from walkability data
            if (nh.walkability?.amenitiesNearby) {
              const amenities = nh.walkability.amenitiesNearby;
              const amenityList: Array<{ type: string; name: string; distance: number }> = [];
              
              if (amenities.parks && typeof amenities.parks === 'object' && 'nearest_m' in amenities.parks) {
                amenityList.push({ type: 'Park', name: 'Nearest Park', distance: amenities.parks.nearest_m || 0 });
              }
              if (amenities.healthcare && typeof amenities.healthcare === 'object' && 'nearest_m' in amenities.healthcare) {
                amenityList.push({ type: 'Healthcare', name: 'Nearest Healthcare', distance: amenities.healthcare.nearest_m || 0 });
              }
              if (amenities.shops && typeof amenities.shops === 'object' && 'nearest_m' in amenities.shops) {
                amenityList.push({ type: 'Shop', name: 'Nearest Shop', distance: amenities.shops.nearest_m || 0 });
              }
              
              enrichedHome.locationWellbeing.local_amenities = amenityList;
            }
            
            console.log(`  ✅ Location Wellbeing derived for ${homeName}`);
          } catch (error) {
            const err = handleEnrichmentError(error, 'Location Wellbeing', homeName, 'derived');
            enrichmentErrors.push(err);
          }
        }

        // 11. Area Map data (from Neighbourhood data)
        if (enrichedHome.neighbourhood) {
          try {
            const nh = enrichedHome.neighbourhood;
            enrichedHome.areaMap = {
              nearby_gps: [], // Will be populated from healthProfile if available
              nearby_parks: [], // Will be populated from walkability if available
              nearby_shops: [], // Will be populated from walkability if available
              nearby_pharmacies: [], // Will be populated from walkability if available
              nearest_hospital: null,
              nearest_bus_stop: null,
              nearest_train_station: null,
            };
            
            // Populate from walkability data if available
            if (nh.walkability?.amenitiesNearby) {
              const amenities = nh.walkability.amenitiesNearby;
              
              if (amenities.parks && typeof amenities.parks === 'object' && 'nearest_m' in amenities.parks) {
                enrichedHome.areaMap.nearby_parks.push({
                  name: 'Nearest Park',
                  distance: amenities.parks.nearest_m || 0,
                });
              }
              
              if (amenities.shops && typeof amenities.shops === 'object' && 'nearest_m' in amenities.shops) {
                enrichedHome.areaMap.nearby_shops.push({
                  name: 'Nearest Shop',
                  distance: amenities.shops.nearest_m || 0,
                });
              }
            }
            
            // Populate GP practices from healthProfile
            if (nh.healthProfile?.gpPracticesNearby) {
              enrichedHome.areaMap.nearby_gps.push({
                name: 'GP Practice',
                distance: 0, // Distance not available
              });
            }
            
            console.log(`  ✅ Area Map derived for ${homeName}`);
          } catch (error) {
            const err = handleEnrichmentError(error, 'Area Map', homeName, 'derived');
            enrichmentErrors.push(err);
          }
        }

        // 12. CQC Rating Trends (from CQC Deep Dive)
        if (enrichedHome.cqcDeepDive?.historical_ratings) {
          try {
            enrichedHome.cqcRatingTrends = {
              historicalRatings: enrichedHome.cqcDeepDive.historical_ratings,
              trend: enrichedHome.cqcDeepDive.trend || 'Stable',
              ratingChanges: enrichedHome.cqcDeepDive.rating_changes || [],
              currentRating: enrichedHome.cqcDeepDive.current_rating || enrichedHome.cqcDeepDive.overall_rating,
            };
            console.log(`  ✅ CQC Rating Trends derived for ${homeName}`);
          } catch (error) {
            const err = handleEnrichmentError(error, 'CQC Trends', homeName, 'derived');
            enrichmentErrors.push(err);
          }
        }

        // 13. Financial Stability Charts (from Financial data)
        if (enrichedHome.financialStability) {
          try {
            const finData = enrichedHome.financialStability;
            enrichedHome.financialCharts = {
              altmanZScore: finData.altman_z_score,
              bankruptcyRisk: (finData as any).bankruptcy_risk, // ✅ FIX: Use type assertion for optional field
              financialHealth: (finData as any).financial_health, // ✅ FIX: Use type assertion
              redFlags: finData.red_flags || [],
              accountsHistory: (finData as any).accounts_history || [], // ✅ FIX: Use type assertion
            };
            console.log(`  ✅ Financial Charts derived for ${homeName}`);
          } catch (error) {
            const err = handleEnrichmentError(error, 'Financial Charts', homeName, 'derived');
            enrichmentErrors.push(err);
          }
        }

        // 14. Historical Data (aggregated from multiple sources)
        if (enrichedHome.cqcDeepDive || enrichedHome.fsaDetailed) {
          try {
            enrichedHome.historicalData = {
              cqcHistory: enrichedHome.cqcDeepDive?.historical_ratings || [],
              fsaHistory: enrichedHome.fsaDetailed?.historical_ratings || [],
              lastInspectionDate: (enrichedHome.cqcDeepDive as any)?.last_inspection_date, // ✅ FIX: Use type assertion
              lastFSAInspection: enrichedHome.fsaDetailed?.rating_date,
            };
            console.log(`  ✅ Historical Data derived for ${homeName}`);
          } catch (error) {
            const err = handleEnrichmentError(error, 'Historical Data', homeName, 'derived');
            enrichmentErrors.push(err);
          }
        }

        // 15. LLM Insights
        // Note: LLM Insights are generated separately in useReportProcessor after report creation
        // They are not part of home enrichment, but are generated for the entire report
        // This field is kept for consistency but will be populated at report level, not home level

        // Log any enrichment errors (non-critical) with detailed information
        if (enrichmentErrors.length > 0) {
          console.warn(`  ⚠️ ${homeName}: ${enrichmentErrors.length} enrichment errors (non-critical):`);
          enrichmentErrors.forEach((err) => {
            console.warn(`    - [${err.source}] ${err.errorType}: ${err.message}`);
            if (err.details) {
              console.warn(`      Details:`, err.details);
            }
          });
        }

      } catch (error) {
        // Critical error that prevents enrichment
        const criticalError = handleEnrichmentError(error, 'Critical', home.name || 'Unknown', 'unknown');
        console.error(`❌ Critical error enriching ${home.name}:`, {
          errorType: criticalError.errorType,
          message: criticalError.message,
          details: criticalError.details,
        });
        // Don't throw - continue with other homes
      }

      return enrichedHome;
      });
      
      // Wait for batch to complete
      const batchResults = await Promise.all(batchPromises);
      enrichedHomes.push(...batchResults);
    }
    
    // Count successful enrichments and errors
    const enrichmentStats = {
      cqc: enrichedHomes.filter(h => h.cqcDeepDive).length,
      fsa: enrichedHomes.filter(h => h.fsaDetailed).length,
      financial: enrichedHomes.filter(h => h.financialStability).length,
      googlePlaces: enrichedHomes.filter(h => h.googlePlaces).length,
      staffQuality: enrichedHomes.filter(h => h.staffQuality).length,
      neighbourhood: enrichedHomes.filter(h => h.neighbourhood).length,
    };
    
    // Calculate success rates
    const totalHomes = enrichedHomes.length;
    const successRates = {
      cqc: totalHomes > 0 ? ((enrichmentStats.cqc / totalHomes) * 100).toFixed(1) : '0',
      fsa: totalHomes > 0 ? ((enrichmentStats.fsa / totalHomes) * 100).toFixed(1) : '0',
      financial: totalHomes > 0 ? ((enrichmentStats.financial / totalHomes) * 100).toFixed(1) : '0',
      googlePlaces: totalHomes > 0 ? ((enrichmentStats.googlePlaces / totalHomes) * 100).toFixed(1) : '0',
      staffQuality: totalHomes > 0 ? ((enrichmentStats.staffQuality / totalHomes) * 100).toFixed(1) : '0',
      neighbourhood: totalHomes > 0 ? ((enrichmentStats.neighbourhood / totalHomes) * 100).toFixed(1) : '0',
    };
    
    console.log(`✅ Enrichment completed for ${enrichedHomes.length} homes:`);
    console.log(`   📊 CQC: ${enrichmentStats.cqc}/${totalHomes} (${successRates.cqc}%)`);
    console.log(`   📊 FSA: ${enrichmentStats.fsa}/${totalHomes} (${successRates.fsa}%)`);
    console.log(`   📊 Financial: ${enrichmentStats.financial}/${totalHomes} (${successRates.financial}%)`);
    console.log(`   📊 Google Places: ${enrichmentStats.googlePlaces}/${totalHomes} (${successRates.googlePlaces}%)`);
    console.log(`   📊 Staff Quality: ${enrichmentStats.staffQuality}/${totalHomes} (${successRates.staffQuality}%)`);
    console.log(`   📊 Neighbourhood: ${enrichmentStats.neighbourhood}/${totalHomes} (${successRates.neighbourhood}%)`);
    
    return enrichedHomes;
  } catch (error) {
    // Comprehensive error handling for top-level errors
    console.error('❌ Critical enrichment failure:', error);
    
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      console.error('Axios error details:', {
        code: axiosError.code,
        message: axiosError.message,
        name: axiosError.name,
        response: axiosError.response ? {
          status: axiosError.response.status,
          statusText: axiosError.response.statusText,
          data: axiosError.response.data
        } : 'No response',
        request: axiosError.request ? 'Request made but no response' : 'No request made',
        config: {
          timeout: axiosError.config?.timeout,
          url: axiosError.config?.url,
        }
      });
    }
    
    throw error;
  }
}

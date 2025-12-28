import { useMutation } from '@tanstack/react-query';
import type { ProfessionalQuestionnaireResponse, ProfessionalReportData } from '../types';
import { loadCareHomes } from './useDataLoader';
import { enrichTop30ForMatching, enrichHomes } from './useDataEnricher';
import { matchHomesUnenriched } from './useDataMatcherUnenriched';
import { matchHomes } from './useDataMatcher';
import { processForReport } from './useReportProcessor';
import { validateQuestionnaire, sanitizeErrorMessage } from '../utils/dataValidator';
import { handleReportError, logError } from '../utils/errorHandler';

// ✅ FIX: Use relative path through Vite proxy by default (like other features)
// Only use absolute URL if VITE_API_URL is explicitly set
const API_BASE_URL = (import.meta.env as any).VITE_API_URL || '';
const MAX_RETRIES = 3;

/**
 * Sleep utility for retry delays
 */
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Progress callback type for real-time progress updates
 */
export type ProgressCallback = (progress: number, step: string) => void;

/**
 * Main hook for generating professional reports
 * ✅ FIX: Added progress callback support for real progress tracking
 */
export const useProfessionalReportNew = (onProgress?: ProgressCallback) => {
  return useMutation({
    mutationFn: async (questionnaire: ProfessionalQuestionnaireResponse): Promise<ProfessionalReportData> => {
      console.log('🚀 Starting Professional Report generation');
      
      // Validate input
      if (!validateQuestionnaire(questionnaire)) {
        throw new Error('Invalid questionnaire: missing required fields');
      }

      let attempt = 0;
      let lastError: any;

      while (attempt < MAX_RETRIES) {
        try {
          attempt++;
          
          // ✅ REFACTOR: New approach - Match first, then enrich only top-5
          
          // STEP 1: Load homes from database (0-15%)
          onProgress?.(0, 'Loading care homes from database...');
          console.log(`📥 STEP 1: Loading care homes from database... (attempt ${attempt}/${MAX_RETRIES})`);
          const homes = await loadCareHomes(questionnaire, API_BASE_URL);
          
          // ✅ FIX: Check for empty homes immediately
          if (!homes || homes.length === 0) {
            throw new Error('No care homes found');
          }
          onProgress?.(15, `Found ${homes.length} care homes in database`);

          // STEP 2: Match homes WITHOUT enrichment (15-30%)
          // Uses only database data to find top candidates
          onProgress?.(15, 'Matching homes using database data...');
          console.log('🎯 STEP 2: Matching homes WITHOUT enrichment (database-only)...');
          const allMatchedHomes = await matchHomesUnenriched(homes, questionnaire, API_BASE_URL);
          
          // ✅ FIX: Check for empty matched homes
          if (!allMatchedHomes || allMatchedHomes.length === 0) {
            throw new Error('No homes matched after scoring');
          }
          
          // Select top-30 candidates (like old report)
          const top30Candidates = allMatchedHomes
            .filter(h => h.matchResult?.constraints_met !== false)
            .sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0))
            .slice(0, 30);
          
          onProgress?.(30, `Selected top ${top30Candidates.length} candidates for matching enrichment`);

          // STEP 3: Enrich top-30 for matching (CQC + Financial only) (30-45%)
          // This improves match scores before selecting top-5
          onProgress?.(30, 'Enriching top candidates for matching (CQC + Financial)...');
          console.log(`📊 STEP 3: Enriching top ${top30Candidates.length} candidates for matching (CQC + Financial only)...`);
          const enrichedTop30 = await enrichTop30ForMatching(top30Candidates, API_BASE_URL);
          onProgress?.(45, 'Matching enrichment complete');

          // STEP 4: Re-score top-30 with enriched data (45-50%)
          // This is the key difference from old approach - re-scoring improves accuracy
          onProgress?.(45, 'Re-scoring candidates with enriched data...');
          console.log('🔄 STEP 4: Re-scoring top-30 with enriched data...');
          const rescoredTop30 = await matchHomes(enrichedTop30, questionnaire, API_BASE_URL);
          
          // Select top-5 from re-scored results (like old report)
          const top5Candidates = rescoredTop30
            .filter(h => h.matchResult?.constraints_met !== false)
            .sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0))
            .slice(0, 5);
          
          if (!top5Candidates || top5Candidates.length === 0) {
            throw new Error('No homes matched after re-scoring');
          }
          onProgress?.(50, `Selected top ${top5Candidates.length} finalists`);

          // STEP 5: Full enrichment for top-5 finalists (50-75%)
          // Now we enrich only the selected finalists with all sources
          onProgress?.(50, 'Enriching top finalists with all data sources...');
          console.log(`📊 STEP 5: Full enrichment for top ${top5Candidates.length} finalists...`);
          const enrichedHomes = await enrichHomes(top5Candidates, questionnaire, API_BASE_URL);
          onProgress?.(75, 'Full enrichment complete');
          
          // STEP 6: Process for report (75-100%)
          // Enriched homes are already matched, so we use them directly
          onProgress?.(75, 'Generating report...');
          console.log('📄 STEP 6: Processing for report...');
          const report = await processForReport(enrichedHomes, questionnaire, enrichedHomes);
          
          // Validate report
          if (!report || !report.careHomes || report.careHomes.length === 0) {
            throw new Error('Failed to generate valid report');
          }
          
          onProgress?.(100, 'Report generated successfully');
          console.log('✅ Report generated successfully');
          return report;
        } catch (error) {
          lastError = error;
          logError(error, `Report Generation (Attempt ${attempt}/${MAX_RETRIES})`);
          
          // Check if retryable
          const handled = handleReportError(error);
          if (!handled.isRetryable || attempt >= MAX_RETRIES) {
            break;
          }
          
          // Exponential backoff: 1s, 2s, 4s
          const delay = Math.pow(2, attempt - 1) * 1000;
          console.log(`⏳ Retrying in ${delay}ms...`);
          await sleep(delay);
        }
      }

      // All attempts failed
      const errorMessage = sanitizeErrorMessage(lastError);
      console.error('❌ Final error after all retries:', errorMessage);
      throw new Error(errorMessage);
    },
    mutationKey: ['professional-report-new'],
    retry: false, // Handle retries manually for better control
  });
};

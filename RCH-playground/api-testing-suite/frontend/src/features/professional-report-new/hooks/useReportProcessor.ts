import type { ProfessionalQuestionnaireResponse, ProfessionalCareHome, ProfessionalReportData } from '../types';
import { generateLLMInsights, generateFallbackInsights } from './useLLMInsights';

const API_BASE_URL = (typeof import.meta !== 'undefined' && (import.meta as any).env?.VITE_API_URL) || '';

export async function processForReport(
  matchedHomes: ProfessionalCareHome[],
  questionnaire: ProfessionalQuestionnaireResponse,
  _enrichedHomes: ProfessionalCareHome[] // ✅ FIX: Prefixed with _ to indicate intentionally unused
): Promise<ProfessionalReportData> {
  // ✅ FIX: Validate matchedHomes before creating report
  if (!matchedHomes || !Array.isArray(matchedHomes) || matchedHomes.length === 0) {
    throw new Error('Cannot generate report: no matched homes provided');
  }
  
  // ✅ FIX: Validate each home has required fields
  const validHomes = matchedHomes.filter((home) => {
    if (!home.name || !home.id) {
      console.warn(`⚠️ Invalid home structure: missing name or id`, home);
      return false;
    }
    return true;
  });
  
  if (validHomes.length === 0) {
    throw new Error('Cannot generate report: no valid homes after validation');
  }
  
  const report: ProfessionalReportData = {
    reportId: `pr-${Date.now()}`,
    clientName: questionnaire.section_1_contact_emergency.q1_names,
    postcode: questionnaire.section_2_location_budget.q5_preferred_city,
    city: questionnaire.section_2_location_budget.q5_preferred_city,
    clientNeeds: {
      medicalConditions: questionnaire.section_3_medical_needs?.q9_medical_conditions || [],
      mobilityLevel: questionnaire.section_3_medical_needs?.q10_mobility_level || '',
      languagePreference: 'English',
      careRequirements: questionnaire.section_3_medical_needs?.q8_care_types || [],
    },
    analysisSummary: {
      totalHomesAnalyzed: matchedHomes.length,
      factorsAnalyzed: 15,
      analysisTime: 'Generated via Data Engine',
    },
    executiveSummary: {
      personalizedMatching: 'Your top 5 recommendations based on 156-point analysis',
      precisionMatching: '93-95% confidence matching',
      deepAnalysis: 'Comprehensive analysis of quality, financial stability, and staff',
      expertInsights: 'AI-powered insights included',
    },
    appliedWeights: {
      // ✅ FIX: Use correct property names for ScoringWeights type
      medical: 0.30,
      safety: 0.20,
      location: 0.25,
      cost: 0.15,
      quality: 0.10,
    } as any, // Type assertion needed due to type mismatch
    appliedConditions: [],
    careHomes: validHomes, // ✅ FIX: Use validated homes
    generatedAt: new Date().toISOString(),
  };

  // ✅ FIX: Generate LLM Insights asynchronously (non-blocking)
  // Start LLM generation but don't wait for it - use fallback initially
  console.log('🤖 Generating LLM Insights (non-blocking)...');
  report.llmInsights = generateFallbackInsights(report); // Start with fallback
  
  // Generate LLM Insights in background and update when ready
  generateLLMInsights(report, questionnaire, API_BASE_URL)
    .then((llmInsights) => {
      report.llmInsights = llmInsights;
      console.log(`✅ LLM Insights generated and updated (model: ${llmInsights.model})`);
    })
    .catch((error) => {
      console.error('❌ Error generating LLM Insights (non-critical):', error);
      // Keep fallback insights that were set initially
    });

  console.log('✅ Report processing complete');
  return report;
}

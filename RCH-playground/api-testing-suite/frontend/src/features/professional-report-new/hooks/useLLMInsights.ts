import axios, { AxiosError } from 'axios';
import type { ProfessionalQuestionnaireResponse, ProfessionalReportData } from '../types';

const API_BASE_URL = (typeof import.meta !== 'undefined' && (import.meta as any).env?.VITE_API_URL) || '';

/**
 * Generate LLM Insights for professional report
 * Uses backend ReportLLMInsightsService with Anthropic Claude
 * 
 * @param report - Professional report data
 * @param questionnaire - Original questionnaire
 * @param apiBaseUrl - API base URL (optional)
 * @returns LLM Insights or null if generation fails (fallback will be used)
 */
export async function generateLLMInsights(
  report: ProfessionalReportData,
  questionnaire: ProfessionalQuestionnaireResponse,
  apiBaseUrl: string = API_BASE_URL
): Promise<NonNullable<ProfessionalReportData['llmInsights']>> {
  try {
    console.log('🤖 Starting LLM Insights generation...');
    
    // Health check before LLM request
    try {
      const healthUrl = apiBaseUrl ? `${apiBaseUrl}/health` : '/health';
      await axios.get(healthUrl, { timeout: 2000 }).catch(() => {
        console.warn('⚠️ Health check failed (non-critical, continuing anyway)');
      });
    } catch (healthError) {
      // Health check failed silently - continue anyway
    }

    // Prepare request payload
    const payload = {
      report_data: {
        clientName: report.clientName,
        city: report.city,
        postcode: report.postcode,
        analysisSummary: report.analysisSummary,
        executiveSummary: report.executiveSummary,
        careHomes: report.careHomes.map(home => ({
          name: home.name,
          matchScore: home.matchScore,
          location: home.location,
          weeklyPrice: home.weeklyPrice,
          cqcRating: home.cqcRating,
          keyStrengths: home.keyStrengths,
          whyChosen: home.whyChosen,
          // Include enriched data for better insights
          cqcDeepDive: home.cqcDeepDive,
          financialStability: home.financialStability,
          googlePlaces: home.googlePlaces,
          staffQuality: home.staffQuality,
        })),
        fundingOptimization: report.fundingOptimization,
      },
      questionnaire: questionnaire,
    };

    const url = apiBaseUrl 
      ? `${apiBaseUrl}/api/professional-report/llm-insights` 
      : '/api/professional-report/llm-insights';

    console.log(`📡 Calling LLM Insights API: ${url}`);

    // Create AbortController for timeout
    const controller = new AbortController();
    const LLM_TIMEOUT = 35000; // ✅ FIX: Reduced from 60s to 35s for better UX
    const timeoutId = setTimeout(() => {
      console.warn('⏰ LLM Insights request timeout - aborting');
      controller.abort();
    }, LLM_TIMEOUT);

    try {
      const response = await axios.post(url, payload, {
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
        timeout: LLM_TIMEOUT,
      });

      clearTimeout(timeoutId);

      if (!response || !response.data) {
        console.warn('⚠️ LLM Insights: Empty response from server');
        return generateFallbackInsights(report);
      }

      // Validate response structure
      const insights = response.data;
      if (!insights.insights || !insights.generated_at) {
        console.warn('⚠️ LLM Insights: Invalid response structure, using fallback');
        return generateFallbackInsights(report);
      }

      console.log('✅ LLM Insights generated successfully');
      return insights;

    } catch (error) {
      clearTimeout(timeoutId);

      // Handle different error types
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError;

        // Check if request was canceled
        if (axiosError.code === 'ERR_CANCELED' || axiosError.message === 'canceled') {
          console.warn('⚠️ LLM Insights request was canceled (timeout or user action)');
          return generateFallbackInsights(report);
        }

        // Network error - server not reachable
        if (axiosError.code === 'ECONNABORTED' || axiosError.code === 'ETIMEDOUT' || axiosError.message.includes('timeout')) {
          console.warn('⚠️ LLM Insights request timed out - using fallback');
          return generateFallbackInsights(report);
        }

        // Network error - no connection
        if (axiosError.code === 'ERR_NETWORK' || (!axiosError.response && axiosError.code !== 'ERR_CANCELED')) {
          console.warn('⚠️ LLM Insights: Cannot connect to server - using fallback');
          return generateFallbackInsights(report);
        }

        // Server responded with error
        if (axiosError.response) {
          const status = axiosError.response.status;
          const message = (axiosError.response.data as any)?.detail || 
                         (axiosError.response.data as any)?.message || 
                         axiosError.message;
          
          console.warn(`⚠️ LLM Insights server error (${status}): ${message} - using fallback`);
          return generateFallbackInsights(report);
        }
      }

      // Unknown error
      console.warn('⚠️ LLM Insights: Unknown error - using fallback', error);
      return generateFallbackInsights(report);
    }

  } catch (error) {
    console.error('❌ Critical error generating LLM Insights:', error);
    // Always return fallback insights (never null)
    return generateFallbackInsights(report);
  }
}

/**
 * Generate fallback insights when LLM is unavailable
 * Matches the fallback from ReportLLMInsightsService
 * 
 * @param report - Professional report data
 * @returns Fallback LLM Insights
 */
export function generateFallbackInsights(report: ProfessionalReportData): NonNullable<ProfessionalReportData['llmInsights']> {
  console.log('📝 Generating fallback LLM Insights (LLM unavailable)');
  
  const careHomes = report.careHomes || [];
  const topHome = careHomes[0];
  const totalHomes = report.analysisSummary?.totalHomesAnalyzed || careHomes.length;

  return {
    generated_at: new Date().toISOString(),
    model: 'fallback',
    method: 'data_driven_analysis',
    insights: {
      overall_explanation: {
        summary: `This report analyzed ${totalHomes} care homes to find the best matches for your specific needs. The top recommendations are based on a comprehensive 156-point matching algorithm that considers your medical needs, preferences, and care requirements.`,
        key_insights: [
          'Each recommended home has been carefully matched to your specific profile',
          'Match scores reflect how well each home aligns with your needs',
          'All homes meet minimum quality standards (CQC registered)',
        ],
        confidence_level: 'medium' as const,
      },
      top_home_analysis: topHome ? [
        {
          home_name: topHome.name,
          rank: 1,
          why_recommended: topHome.whyChosen || 'Strong match with your requirements based on comprehensive analysis',
          key_strengths: topHome.keyStrengths?.slice(0, 3) || [],
          considerations: [
            'Schedule a visit to see the home in person',
            'Ask about availability and waiting lists',
            'Verify current pricing and any additional fees',
          ],
          match_score_explanation: `Match score of ${topHome.matchScore}% indicates strong alignment with your needs`,
        },
      ] : [],
      expert_advice: {
        funding_strategy: 'Review the funding options section of this report to understand your eligibility for CHC, LA funding, or self-funding options.',
        decision_timeline: 'We recommend visiting top 3 homes within 2-3 weeks to make an informed decision.',
        red_flags_to_watch: [
          'Homes with recent CQC ratings below "Good"',
          'Significant price increases without justification',
          'High staff turnover rates',
        ],
        negotiation_tips: [
          'Ask about introductory rates or discounts for longer commitments',
          'Inquire about what\'s included in the weekly fee',
          'Compare pricing with similar homes in the area',
        ],
      },
      actionable_next_steps: [
        {
          step: 'Review the top 3 recommended homes',
          priority: 'high' as const,
          timeline: 'This week',
          details: 'Read through each home\'s detailed profile and match score breakdown',
        },
        {
          step: 'Schedule visits to top homes',
          priority: 'high' as const,
          timeline: 'Within 2 weeks',
          details: 'Contact homes to arrange personal tours',
        },
        {
          step: 'Review funding options',
          priority: 'medium' as const,
          timeline: 'Before visits',
          details: 'Understand your funding eligibility to discuss during visits',
        },
      ],
    },
  };
}


/**
 * Professional Report API Route
 * POST /api/professional-report
 * 
 * Note: Professional Report generation can take 30-180 seconds,
 * so we use job queue for async processing
 */

import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { ProfessionalReportGenerator } from '@/lib/reports/professional-report/generator';
import { requestLogger } from '@/lib/shared/utils/logger';

// Vercel Pro plan: max 300 seconds (5 minutes)
export const maxDuration = 300;

// Basic questionnaire validation (can be extended)
const questionnaireSchema = z.object({
  section_1_personal_info: z.any().optional(),
  section_2_location_budget: z
    .object({
      q4_postcode: z.string().optional(),
      q5_preferred_city: z.string().optional(),
      q6_max_distance: z.string().optional(),
      q7_budget_range: z.string().optional(),
    })
    .optional(),
  section_3_medical_needs: z
    .object({
      q8_care_types: z.array(z.string()).optional(),
      q9_medical_conditions: z.array(z.string()).optional(),
      q10_specialist_care: z.array(z.string()).optional(),
    })
    .optional(),
  section_4_lifestyle_preferences: z.any().optional(),
  section_5_priorities: z
    .object({
      priority_order: z.array(z.string()).optional(),
      priority_weights: z.array(z.number()).optional(),
    })
    .optional(),
});

export async function POST(request: NextRequest) {
  const requestId = request.headers.get('x-request-id') || crypto.randomUUID();
  const logger = requestLogger(requestId);

  try {
    logger.info('Professional report request received');

    // Parse and validate body
    const body = await request.json();

    // Validate questionnaire
    let validated;
    try {
      validated = questionnaireSchema.parse(body);
    } catch (error) {
      if (error instanceof z.ZodError) {
        logger.warn({ errors: error.issues }, 'Validation failed');
        return NextResponse.json(
          {
            error: 'Validation failed',
            details: error.issues,
            requestId,
          },
          { status: 422 }
        );
      }
      throw error;
    }

    // Generate report
    const generator = new ProfessionalReportGenerator();
    const report = await generator.generate(validated);

    logger.info({
      reportId: report.report_id,
      homesEvaluated: report.summary.total_homes_evaluated,
    }, 'Professional report generated successfully');

    return NextResponse.json(report, {
      headers: {
        'x-request-id': requestId,
      },
    });
  } catch (error) {
    logger.error({
      error: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
    }, 'Professional report generation error');

    // Don't expose internal error details in production
    const isDevelopment = process.env.NODE_ENV === 'development';
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';

    return NextResponse.json(
      {
        error: 'Internal server error',
        message: isDevelopment ? errorMessage : 'An error occurred while generating the report',
        requestId,
      },
      { status: 500 }
    );
  }
}


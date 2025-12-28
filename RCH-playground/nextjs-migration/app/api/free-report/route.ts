/**
 * Free Report API Route
 * POST /api/free-report
 */

import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { FreeReportGenerator } from '@/lib/reports/free-report/generator';
import { requestLogger } from '@/lib/shared/utils/logger';

// Vercel Pro plan: max 300 seconds (5 minutes)
export const maxDuration = 60; // 1 minute should be enough for Free Report

// Request validation schema
const requestSchema = z.object({
  postcode: z.string().min(6).max(7),
  budget: z.number().min(0).max(10000).optional().default(0),
  care_type: z
    .enum(['residential', 'nursing', 'dementia', 'respite'])
    .optional()
    .default('residential'),
  chc_probability: z.number().min(0).max(100).optional().default(35),
  location_postcode: z.string().optional(),
  timeline: z.string().optional(),
  medical_conditions: z.array(z.string()).optional().default([]),
  max_distance_km: z.number().min(0).max(100).optional().default(30),
  priority_order: z.array(z.string()).optional().default(['quality', 'cost', 'proximity']),
  priority_weights: z.array(z.number()).optional().default([40, 35, 25]),
});

export async function POST(request: NextRequest) {
  const requestId = request.headers.get('x-request-id') || crypto.randomUUID();
  const logger = requestLogger(requestId);

  try {
    logger.info('Free report request received');

    // Parse and validate body size
    const body = await request.json();

    // Validate request
    let validated;
    try {
      validated = requestSchema.parse(body);
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

    // Normalize postcode
    const normalizedPostcode = validated.postcode
      .replace(/\s+/g, '')
      .toUpperCase()
      .trim();

    const requestData = {
      ...validated,
      postcode: normalizedPostcode,
    };

    // Generate report
    const generator = new FreeReportGenerator();
    const report = await generator.generate(requestData);

    logger.info({
      reportId: report.report_id,
      careHomesCount: report.care_homes.length,
    }, 'Free report generated successfully');

    return NextResponse.json(report, {
      headers: {
        'x-request-id': requestId,
      },
    });
  } catch (error) {
    logger.error({
      error: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
    }, 'Free report generation error');

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


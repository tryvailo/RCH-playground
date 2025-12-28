/**
 * Next.js Middleware
 * Rate limiting and request validation
 */

import { NextRequest, NextResponse } from 'next/server';
import { createLogger } from './lib/shared/utils/logger';

const logger = createLogger({ module: 'Middleware' });

// Simple in-memory rate limiter (for production, use Redis/Vercel KV)
const rateLimitMap = new Map<string, { count: number; resetAt: number }>();

const RATE_LIMIT = {
  windowMs: 60 * 1000, // 1 minute
  maxRequests: 10, // 10 requests per minute per IP
};

const MAX_BODY_SIZE = 1024 * 1024; // 1MB

/**
 * Rate limiting middleware
 */
function checkRateLimit(ip: string): boolean {
  const now = Date.now();
  const record = rateLimitMap.get(ip);

  if (!record || now > record.resetAt) {
    rateLimitMap.set(ip, {
      count: 1,
      resetAt: now + RATE_LIMIT.windowMs,
    });
    return true;
  }

  if (record.count >= RATE_LIMIT.maxRequests) {
    return false;
  }

  record.count++;
  return true;
}

/**
 * Get client IP
 */
function getClientIP(request: NextRequest): string {
  const forwarded = request.headers.get('x-forwarded-for');
  if (forwarded) {
    return forwarded.split(',')[0].trim();
  }
  const realIP = request.headers.get('x-real-ip');
  if (realIP) {
    return realIP;
  }
  return 'unknown';
}

export async function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname;

  // Only apply to API routes
  if (!path.startsWith('/api/')) {
    return NextResponse.next();
  }

  const ip = getClientIP(request);
  const requestId = crypto.randomUUID();

  // Rate limiting
  if (!checkRateLimit(ip)) {
    logger.warn({ ip, path, requestId }, 'Rate limit exceeded');
    return NextResponse.json(
      {
        error: 'Rate limit exceeded',
        message: `Too many requests. Maximum ${RATE_LIMIT.maxRequests} requests per minute.`,
      },
      { status: 429 }
    );
  }

  // Body size check (for POST requests)
  if (request.method === 'POST') {
    const contentLength = request.headers.get('content-length');
    if (contentLength) {
      const size = parseInt(contentLength, 10);
      if (size > MAX_BODY_SIZE) {
        logger.warn({
          ip,
          path,
          size,
          maxSize: MAX_BODY_SIZE,
          requestId,
        }, 'Request body too large');
        return NextResponse.json(
          {
            error: 'Request too large',
            message: `Request body exceeds maximum size of ${MAX_BODY_SIZE / 1024}KB`,
          },
          { status: 413 }
        );
      }
    }
  }

  // Add request ID to headers for logging
  const response = NextResponse.next();
  response.headers.set('x-request-id', requestId);
  response.headers.set('x-rate-limit-remaining', String(
    RATE_LIMIT.maxRequests - (rateLimitMap.get(ip)?.count || 0)
  ));

  return response;
}

export const config = {
  matcher: '/api/:path*',
};


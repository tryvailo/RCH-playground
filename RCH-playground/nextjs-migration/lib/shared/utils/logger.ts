/**
 * Structured Logging
 * Production-ready logging with Pino
 */

import pino from 'pino';

const isDevelopment = process.env.NODE_ENV === 'development';

export const logger = pino({
  level: process.env.LOG_LEVEL || (isDevelopment ? 'debug' : 'info'),
  transport: isDevelopment
    ? {
        target: 'pino-pretty',
        options: {
          colorize: true,
          translateTime: 'HH:MM:ss Z',
          ignore: 'pid,hostname',
        },
      }
    : undefined,
  base: {
    env: process.env.NODE_ENV,
  },
});

export interface LogContext {
  requestId?: string;
  userId?: string;
  reportId?: string;
  [key: string]: any;
}

/**
 * Create child logger with context
 */
export function createLogger(context: LogContext = {}) {
  return logger.child(context);
}

/**
 * Request logger middleware
 */
export function requestLogger(requestId: string) {
  return createLogger({ requestId });
}




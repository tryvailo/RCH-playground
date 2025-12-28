/**
 * Environment Variable Validation
 * Checks that required API keys and configuration are properly set
 */

import { createLogger } from './logger';

const logger = createLogger({ module: 'EnvValidation' });

interface ApiKeyConfig {
  name: string;
  envVar: string;
  required: boolean;
  service: string;
}

const API_KEY_CONFIGS: ApiKeyConfig[] = [
  {
    name: 'Companies House API',
    envVar: 'COMPANIES_HOUSE_API_KEY',
    required: true,
    service: 'FinancialEnrichment',
  },
  {
    name: 'Google Places API',
    envVar: 'GOOGLE_PLACES_API_KEY',
    required: true,
    service: 'GooglePlacesEnrichment',
  },
  {
    name: 'CQC API',
    envVar: 'CQC_API_KEY',
    required: true,
    service: 'CQCEnrichment',
  },
  {
    name: 'Perplexity API',
    envVar: 'PERPLEXITY_API_KEY',
    required: true,
    service: 'StaffEnrichment',
  },
  {
    name: 'OS Places API',
    envVar: 'OS_PLACES_API_KEY',
    required: false,
    service: 'NeighbourhoodEnrichment (optional)',
  },
];

/**
 * Validation result
 */
export interface ValidationResult {
  isValid: boolean;
  missingRequired: string[];
  missingOptional: string[];
  configured: string[];
  warnings: string[];
}

/**
 * Validate environment variables
 */
export function validateEnvironment(): ValidationResult {
  const result: ValidationResult = {
    isValid: true,
    missingRequired: [],
    missingOptional: [],
    configured: [],
    warnings: [],
  };

  // Check each API key
  for (const config of API_KEY_CONFIGS) {
    const value = process.env[config.envVar];

    if (!value || value === '' || value.includes('your_')) {
      // Not configured
      if (config.required) {
        result.isValid = false;
        result.missingRequired.push(
          `${config.name} (${config.envVar}) - Required for ${config.service}`
        );
      } else {
        result.missingOptional.push(
          `${config.name} (${config.envVar}) - Optional, falls back to OSM`
        );
      }
    } else {
      // Configured
      result.configured.push(`${config.name} - ✅ Configured`);
    }
  }

  // Validate placeholder values
  if (
    process.env.COMPANIES_HOUSE_API_KEY?.includes('your_') ||
    process.env.GOOGLE_PLACES_API_KEY?.includes('your_')
  ) {
    result.warnings.push(
      'Placeholder values detected in API keys. Update .env.local before production deployment.'
    );
  }

  return result;
}

/**
 * Log validation results
 */
export function logValidationResults(result: ValidationResult): void {
  if (result.configured.length > 0) {
    logger.info(
      { count: result.configured.length },
      'Configured API Keys:'
    );
    result.configured.forEach(item => {
      logger.info({}, `  • ${item}`);
    });
  }

  if (result.missingOptional.length > 0) {
    logger.warn(
      { count: result.missingOptional.length },
      'Optional API Keys (Not Configured):'
    );
    result.missingOptional.forEach(item => {
      logger.warn({}, `  • ${item}`);
    });
  }

  if (result.missingRequired.length > 0) {
    logger.error(
      { count: result.missingRequired.length },
      '🚨 MISSING REQUIRED API KEYS:'
    );
    result.missingRequired.forEach(item => {
      logger.error({}, `  ❌ ${item}`);
    });
    logger.error(
      {},
      'Please configure these API keys in .env.local before deploying to production.'
    );
  }

  if (result.warnings.length > 0) {
    logger.warn({ count: result.warnings.length }, 'Warnings:');
    result.warnings.forEach(warning => {
      logger.warn({}, `  ⚠️ ${warning}`);
    });
  }

  if (result.isValid) {
    logger.info({}, '✅ All required API keys are configured!');
  }
}

/**
 * Check environment at startup (call from server initialization)
 */
export function checkEnvironmentAtStartup(): void {
  const result = validateEnvironment();

  logValidationResults(result);

  if (!result.isValid) {
    logger.error(
      {},
      '\n' +
      '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n' +
      'CRITICAL: Environment validation failed!\n' +
      'Please configure the missing API keys before deployment.\n' +
      'See .env.local.example for configuration details.\n' +
      '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
    );

    // In production, we might want to throw an error
    // In development, we log warnings and continue with graceful degradation
    if (process.env.NODE_ENV === 'production') {
      throw new Error(
        'Missing required API keys. Cannot start server in production mode.'
      );
    }
  }
}

/**
 * Get a specific API key with validation
 */
export function getApiKey(keyName: string): string | null {
  const value = process.env[keyName];

  if (!value || value === '' || value.includes('your_')) {
    logger.warn(
      { key: keyName },
      `API key not configured: ${keyName}`
    );
    return null;
  }

  return value;
}

/**
 * Check if specific enrichment service can be used
 */
export function canUseEnrichmentService(serviceName: string): boolean {
  switch (serviceName) {
    case 'financial':
      return !!getApiKey('COMPANIES_HOUSE_API_KEY');
    case 'google':
      return !!getApiKey('GOOGLE_PLACES_API_KEY');
    case 'cqc':
      return !!getApiKey('CQC_API_KEY');
    case 'staff':
      return !!getApiKey('PERPLEXITY_API_KEY');
    case 'neighbourhood':
      // Always works (has OSM fallback)
      return true;
    case 'fsa':
      // Always works (free API)
      return true;
    default:
      return false;
  }
}

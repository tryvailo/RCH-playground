/**
 * Financial Enrichment Service
 * Enriches care homes with financial stability data from Companies House
 * 
 * Uses Companies House API to get financial data, calculate Altman Z-score,
 * and assess bankruptcy risk
 */

import { CareHome } from '@/lib/shared/types/care-home';
import { BaseEnrichmentService } from '../base-enrichment';
import {
  EnrichmentResult,
  EnrichmentContext,
  EnrichmentOptions,
} from '../types';
import {
  CompaniesHouseClient,
  CompanyProfile,
  AccountsData,
  FilingHistory,
} from './companies-house-client';
import {
  analyzeFinancialData,
  FinancialAnalysis,
} from './financial-calculator';

export interface FinancialEnrichmentData {
  company_number: string | null;
  company_name: string | null;
  financial_stability: {
    altman_z_score: number | null;
    bankruptcy_risk: number;
    financial_health: 'stable' | 'at_risk' | 'critical';
  };
  filing_history: Array<{
    date: string;
    type: string;
    status: string;
  }>;
  summary: {
    status: 'available' | 'not_available' | 'partial';
    last_filing: string | null;
    years_of_data: number;
  };
  analysis?: FinancialAnalysis;
}

export class FinancialEnrichmentService extends BaseEnrichmentService {
  serviceName = 'financial';
  private companiesHouseClient: CompaniesHouseClient;
  private cacheTTL: number = 30 * 24 * 60 * 60 * 1000; // 30 days

  constructor(options: EnrichmentOptions = {}) {
    super(options);

    // Companies House API timeout (15 seconds)
    const timeout = options.timeout || 15000;
    const apiKey = process.env.COMPANIES_HOUSE_API_KEY;
    this.companiesHouseClient = new CompaniesHouseClient(apiKey, timeout);

    // Financial data cache TTL = 30 days (financial data обновляется реже)
    if (options.cacheTTL) {
      this.cacheTTL = options.cacheTTL;
    }

    // Initialize logger after serviceName is set
    this.initLogger();
  }

  /**
   * Обогатить care home финансовыми данными
   */
  async enrich(
    home: CareHome,
    context?: EnrichmentContext
  ): Promise<EnrichmentResult> {
    const startTime = Date.now();

    try {
      this.validateHome(home);
      this.logStart(home, context);

      // Проверить доступность
      if (!this.isAvailable()) {
        this.logger.debug('Financial enrichment disabled by feature flag');
        return this.createErrorResult('Financial enrichment disabled by feature flag');
      }

      // Получить company number из home или context
      const companyNumber =
        (home as any).company_number ||
        context?.params?.company_number ||
        null;

      if (!companyNumber) {
        // Попробовать найти company number по названию
        const companyName = home.name || (home as any).provider_name;
        if (companyName) {
          const foundCompany = await this.findCompanyByName(companyName);
          if (foundCompany) {
            return await this.enrichWithCompanyNumber(
              foundCompany.company_number,
              home,
              startTime
            );
          }
        }

        // Нет company number и не удалось найти
        const processingTime = Date.now() - startTime;
        return this.createPartialResult(
          {
            company_number: null,
            company_name: null,
            financial_stability: {
              altman_z_score: null,
              bankruptcy_risk: 0.5,
              financial_health: 'at_risk',
            },
            filing_history: [],
            summary: {
              status: 'not_available',
              last_filing: null,
              years_of_data: 0,
            },
          },
          'No company number provided and could not find company by name',
          {
            sources: [],
            dataQuality: 'low',
          },
          processingTime
        );
      }

      return await this.enrichWithCompanyNumber(companyNumber, home, startTime);
    } catch (error: unknown) {
      const processingTime = Date.now() - startTime;
      const errorObj = error instanceof Error ? error : new Error(String(error));
      this.logError(errorObj, home);

      // Если это timeout или network error, возвращаем partial result
      const errorMessage = error instanceof Error ? error.message : String(error);
      const lowerErrorMessage = errorMessage.toLowerCase();
      if (
        lowerErrorMessage.includes('timeout') ||
        lowerErrorMessage.includes('network') ||
        lowerErrorMessage.includes('econn')
      ) {
        return this.createPartialResult(
          {},
          errorMessage,
          {
            sources: [],
            dataQuality: 'low',
          },
          processingTime
        );
      }

      return this.createErrorResult(errorObj, processingTime);
    }
  }

  /**
   * Найти компанию по названию
   */
  private async findCompanyByName(
    companyName: string
  ): Promise<CompanyProfile | null> {
    try {
      const companies = await this.withRetry(
        () => this.companiesHouseClient.searchCompany(companyName),
        { maxAttempts: 2 }
      );

      if (companies.length === 0) {
        return null;
      }

      // Найти наиболее подходящую компанию
      const normalizedName = companyName.toLowerCase().trim();
      const match = companies.find(
        (c) => c.company_name.toLowerCase().trim() === normalizedName
      );

      return match || companies[0];
    } catch (error) {
      this.logger.warn(
        { error, companyName },
        'Failed to search company by name'
      );
      return null;
    }
  }

  /**
   * Обогатить с известным company number
   */
  private async enrichWithCompanyNumber(
    companyNumber: string,
    home: CareHome,
    startTime: number
  ): Promise<EnrichmentResult> {
    // Получить cache key
    const cacheKey = this.getCacheKey(home, `financial:${companyNumber}`);

    // Проверить кэш
    if (this.cache) {
      const cacheKeyFull = `enrichment:${this.serviceName}:${cacheKey}`;
      const cached = this.cache.get<FinancialEnrichmentData>(cacheKeyFull);

      if (cached) {
        const processingTime = Date.now() - startTime;
        const result = this.createCachedResult(cached, processingTime);
        this.logComplete(result, home);
        return result;
      }
    }

    // Загрузить данные из Companies House (параллельно)
    const [profile, accounts, filingHistory] = await Promise.allSettled([
      this.withRetry(
        () => this.companiesHouseClient.getCompanyProfile(companyNumber),
        { maxAttempts: 2 }
      ),
      this.withRetry(
        () => this.companiesHouseClient.getAccounts(companyNumber),
        { maxAttempts: 2 }
      ),
      this.withRetry(
        () => this.companiesHouseClient.getFilingHistory(companyNumber, 50),
        { maxAttempts: 2 }
      ),
    ]);

    const profileData =
      profile.status === 'fulfilled' ? profile.value : null;
    const accountsData =
      accounts.status === 'fulfilled' ? accounts.value : null;
    const filingHistoryData =
      filingHistory.status === 'fulfilled' ? filingHistory.value : null;

    // Анализ финансовых данных
    const analysis = analyzeFinancialData(
      accountsData,
      profileData,
      filingHistoryData
    );

    // Формирование filing history
    const filingHistoryItems =
      filingHistoryData?.items.slice(0, 10).map((item) => ({
        date: item.date,
        type: item.type,
        status: item.category || 'unknown',
      })) || [];

    // Определить статус
    let status: FinancialEnrichmentData['summary']['status'] = 'available';
    if (!profileData && !accountsData) {
      status = 'not_available';
    } else if (!accountsData) {
      status = 'partial';
    }

    // Определить years of data
    let yearsOfData = 0;
    const lastAccountsDate =
      accountsData?.accounts?.last_accounts?.made_up_to ||
      accountsData?.accounts?.next_accounts?.period_end_on;
    if (lastAccountsDate) {
      const lastAccountDate = new Date(lastAccountsDate);
      const now = new Date();
      yearsOfData = Math.floor(
        (now.getTime() - lastAccountDate.getTime()) /
          (365.25 * 24 * 60 * 60 * 1000)
      );
    }

    const enrichmentData: FinancialEnrichmentData = {
      company_number: companyNumber,
      company_name: profileData?.company_name || null,
      financial_stability: {
        altman_z_score: analysis.altmanZScore,
        bankruptcy_risk: analysis.bankruptcyRisk,
        financial_health:
          analysis.financialHealth === 'safe'
            ? 'stable'
            : analysis.financialHealth === 'gray'
              ? 'at_risk'
              : 'critical',
      },
      filing_history: filingHistoryItems,
      summary: {
        status,
        last_filing:
          filingHistoryItems.length > 0
            ? filingHistoryItems[0].date
            : accountsData?.accounts?.last_accounts?.made_up_to ||
              accountsData?.accounts?.next_accounts?.period_end_on ||
              null,
        years_of_data: yearsOfData,
      },
      analysis,
    };

    // Сохранить в кэш
    if (this.cache) {
      const cacheKeyFull = `enrichment:${this.serviceName}:${cacheKey}`;
      this.cache.set(cacheKeyFull, enrichmentData, this.cacheTTL);
    }

    const processingTime = Date.now() - startTime;
    const result = this.createSuccessResult(
      enrichmentData,
      {
        sources: ['companies_house_api'],
        dataQuality:
          status === 'available' ? 'high' : status === 'partial' ? 'medium' : 'low',
      },
      processingTime
    );

    this.logComplete(result, home);
    return result;
  }
}


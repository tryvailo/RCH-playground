/**
 * Companies House API Client
 * Client for UK Companies House API
 * 
 * API Documentation: https://developer.company-information.service.gov.uk/
 */

export interface CompanyProfile {
  company_number: string;
  company_name: string;
  company_status: string;
  date_of_creation: string;
  registered_office_address?: {
    address_line_1?: string;
    address_line_2?: string;
    locality?: string;
    postal_code?: string;
    country?: string;
  };
  accounts?: {
    next_accounts?: {
      period_end_on: string;
      period_start_on: string;
    };
    last_accounts?: {
      period_end_on: string;
      period_start_on: string;
    };
  };
  sic_codes?: string[];
}

export interface CompanyAccounts {
  company_number: string;
  accounts: {
    accounting_reference_date?: {
      day: number;
      month: number;
    };
    last_accounts?: {
      made_up_to: string;
      type: string;
    };
    next_accounts?: {
      made_up_to: string;
      period_end_on: string;
      period_start_on: string;
    };
    next_due?: string;
    overdue?: boolean;
  };
}

export interface FilingHistoryItem {
  barcode?: string;
  category?: string;
  date: string;
  description?: string;
  description_values?: Record<string, any>;
  subcategory?: string;
  transaction_id: string;
  type: string;
}

export interface FilingHistory {
  etag?: string;
  filing_history_status?: string;
  items: FilingHistoryItem[];
  items_per_page: number;
  kind: string;
  start_index: number;
  total_count: number;
}

export interface AccountsData {
  company_number: string;
  accounts: {
    balance_sheet?: {
      current_assets?: {
        cash_at_bank_and_in_hand?: number;
        debtors?: number;
        total_current_assets?: number;
      };
      fixed_assets?: {
        total_fixed_assets?: number;
      };
      total_assets_less_current_liabilities?: number;
      total_net_assets?: number;
      creditors_amounts_falling_due_within_one_year?: number;
      net_current_assets?: number;
    };
    profit_and_loss?: {
      turnover?: number;
      gross_profit_or_loss?: number;
      profit_or_loss_before_tax?: number;
      profit_or_loss_after_tax?: number;
      total_assets?: number;
    };
    other_accounts?: {
      total_assets?: number;
      total_liabilities?: number;
      shareholders_funds?: number;
    };
    last_accounts?: {
      made_up_to: string;
      type?: string;
    };
    next_accounts?: {
      made_up_to: string;
      period_end_on: string;
      period_start_on: string;
    };
  };
  next_accounts?: {
    period_end_on: string;
    period_start_on: string;
  };
}

/**
 * Companies House API Client
 */
export class CompaniesHouseClient {
  private baseUrl = 'https://api.company-information.service.gov.uk';
  private apiKey: string;
  private timeout: number;

  constructor(apiKey?: string, timeout: number = 15000) {
    this.apiKey = apiKey || process.env.COMPANIES_HOUSE_API_KEY || '';
    this.timeout = timeout;

    if (!this.apiKey) {
      console.warn('Companies House API key not provided. Some features may not work.');
    }
  }

  /**
   * Получить профиль компании
   */
  async getCompanyProfile(companyNumber: string): Promise<CompanyProfile | null> {
    try {
      const response = await this.fetchWithTimeout(
        `${this.baseUrl}/company/${companyNumber}`
      );

      if (response.status === 404) {
        return null;
      }

      if (!response.ok) {
        throw new Error(`Companies House API error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      throw new Error(
        `Failed to get company profile: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  /**
   * Получить историю filings
   */
  async getFilingHistory(
    companyNumber: string,
    itemsPerPage: number = 100
  ): Promise<FilingHistory | null> {
    try {
      const response = await this.fetchWithTimeout(
        `${this.baseUrl}/company/${companyNumber}/filing-history?items_per_page=${itemsPerPage}`
      );

      if (response.status === 404) {
        return null;
      }

      if (!response.ok) {
        throw new Error(`Companies House API error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      throw new Error(
        `Failed to get filing history: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  /**
   * Получить данные accounts
   */
  async getAccounts(companyNumber: string): Promise<AccountsData | null> {
    try {
      const response = await this.fetchWithTimeout(
        `${this.baseUrl}/company/${companyNumber}/accounts`
      );

      if (response.status === 404) {
        return null;
      }

      if (!response.ok) {
        throw new Error(`Companies House API error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      throw new Error(
        `Failed to get accounts: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  /**
   * Поиск компании по названию
   */
  async searchCompany(companyName: string): Promise<CompanyProfile[]> {
    try {
      const response = await this.fetchWithTimeout(
        `${this.baseUrl}/search/companies?q=${encodeURIComponent(companyName)}&items_per_page=10`
      );

      if (!response.ok) {
        throw new Error(`Companies House API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data.items || [];
    } catch (error) {
      throw new Error(
        `Failed to search company: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  /**
   * Fetch с timeout и authentication
   */
  private async fetchWithTimeout(
    url: string,
    options: RequestInit = {}
  ): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      // Basic auth для Companies House API
      // Companies House использует HTTP Basic Auth: API key как username, пустой password
      const authHeader = this.apiKey
        ? `Basic ${Buffer.from(`${this.apiKey}:`).toString('base64')}`
        : '';

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(options.headers as Record<string, string>),
      };

      if (authHeader) {
        headers['Authorization'] = authHeader;
      }

      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers,
      });

      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error(`Companies House API request timeout after ${this.timeout}ms`);
      }
      throw error;
    }
  }
}


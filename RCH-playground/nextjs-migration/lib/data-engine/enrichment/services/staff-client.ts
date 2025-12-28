/**
 * Staff Data Client
 * Client for collecting staff quality data from various sources
 * 
 * Sources:
 * - Glassdoor (scraping/research)
 * - LinkedIn (API/scraping)
 * - Job Boards (scraping)
 * - Perplexity AI (for research)
 */

export interface GlassdoorData {
  company_name: string;
  rating?: number; // 1-5
  reviews_count?: number;
  work_life_balance?: number;
  management_rating?: number;
  culture_values?: number;
  career_opportunities?: number;
  compensation_benefits?: number;
  senior_management?: number;
  reviews?: Array<{
    author: string;
    rating: number;
    title: string;
    text: string;
    date: string;
    pros?: string;
    cons?: string;
  }>;
}

export interface LinkedInData {
  company_name: string;
  employee_count?: number;
  followers?: number;
  recent_posts?: number;
  employee_profiles?: Array<{
    name: string;
    title: string;
    location?: string;
    tenure?: string;
  }>;
}

export interface JobBoardData {
  company_name: string;
  active_jobs?: number;
  job_titles?: string[];
  requirements?: string[];
  salary_ranges?: Array<{
    title: string;
    min: number;
    max: number;
  }>;
  benefits?: string[];
}

export interface PerplexityResearchResult {
  company_name: string;
  summary?: string;
  employee_satisfaction?: {
    rating?: number;
    comments?: string[];
  };
  staff_retention?: {
    turnover_rate?: number;
    average_tenure?: number;
    trend?: 'improving' | 'stable' | 'declining';
  };
  qualifications?: {
    certifications?: string[];
    training_programs?: string[];
  };
  themes?: {
    positive?: string[];
    negative?: string[];
  };
}

/**
 * Staff Data Client
 * Aggregates data from multiple sources
 */
export class StaffDataClient {
  private perplexityApiKey?: string;
  private usePerplexity: boolean;

  constructor(perplexityApiKey?: string, usePerplexity: boolean = true) {
    this.perplexityApiKey = perplexityApiKey || process.env.PERPLEXITY_API_KEY;
    this.usePerplexity = usePerplexity && !!this.perplexityApiKey;
  }

  /**
   * Получить данные Glassdoor (через Perplexity или scraping)
   */
  async getGlassdoorData(companyName: string): Promise<GlassdoorData | null> {
    if (this.usePerplexity) {
      return await this.getGlassdoorViaPerplexity(companyName);
    }

    // Fallback: возвращаем структуру без данных
    return {
      company_name: companyName,
    };
  }

  /**
   * Получить данные Glassdoor через Perplexity AI
   */
  private async getGlassdoorViaPerplexity(
    companyName: string
  ): Promise<GlassdoorData | null> {
    if (!this.perplexityApiKey) {
      return null;
    }

    try {
      const query = `Glassdoor reviews and ratings for ${companyName} care home UK. Include overall rating, work-life balance, management rating, and sample reviews.`;

      const response = await fetch('https://api.perplexity.ai/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.perplexityApiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'llama-3.1-sonar-large-128k-online',
          messages: [
            {
              role: 'user',
              content: query,
            },
          ],
          temperature: 0.2,
          max_tokens: 2000,
        }),
      });

      if (!response.ok) {
        throw new Error(`Perplexity API error: ${response.status}`);
      }

      const data = await response.json();
      const content = data.choices?.[0]?.message?.content;

      if (!content) {
        return null;
      }

      // Parse Perplexity response (упрощенный парсинг)
      // В production нужен более сложный парсинг JSON из текста
      return this.parseGlassdoorFromText(content, companyName);
    } catch (error) {
      console.warn(`Failed to get Glassdoor data via Perplexity: ${error}`);
      return null;
    }
  }

  /**
   * Парсить Glassdoor данные из текста Perplexity ответа
   */
  private parseGlassdoorFromText(
    text: string,
    companyName: string
  ): GlassdoorData {
    // Упрощенный парсинг - в production нужен более сложный
    const ratingMatch = text.match(/rating[:\s]+(\d+\.?\d*)/i);
    const rating = ratingMatch ? parseFloat(ratingMatch[1]) : undefined;

    return {
      company_name: companyName,
      rating,
      reviews_count: undefined,
      work_life_balance: undefined,
      management_rating: undefined,
    };
  }

  /**
   * Получить данные LinkedIn
   */
  async getLinkedInData(companyName: string): Promise<LinkedInData | null> {
    // LinkedIn API требует OAuth и специальную подписку
    // Для MVP возвращаем структуру без данных
    return {
      company_name: companyName,
    };
  }

  /**
   * Получить данные Job Boards
   */
  async getJobBoardData(companyName: string): Promise<JobBoardData | null> {
    // Job boards scraping требует специальной реализации
    // Для MVP возвращаем структуру без данных
    return {
      company_name: companyName,
    };
  }

  /**
   * Получить комплексные данные через Perplexity AI
   */
  async getComprehensiveResearch(
    companyName: string,
    locationId?: string,
    companiesHouseData?: any
  ): Promise<PerplexityResearchResult | null> {
    if (!this.usePerplexity || !this.perplexityApiKey) {
      return null;
    }

    try {
      let query = `Research staff quality, employee satisfaction, and staff retention for ${companyName} care home in UK. `;
      
      if (companiesHouseData?.company_name) {
        query += `The company is registered as ${companiesHouseData.company_name}. `;
      }

      query += `Provide: 1) Employee satisfaction rating (if available), 2) Staff turnover rate, 3) Average tenure, 4) Staff qualifications and certifications, 5) Training programs, 6) Positive and negative themes from employee feedback. Format as structured data.`;

      const response = await fetch('https://api.perplexity.ai/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.perplexityApiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'llama-3.1-sonar-large-128k-online',
          messages: [
            {
              role: 'user',
              content: query,
            },
          ],
          temperature: 0.2,
          max_tokens: 3000,
        }),
      });

      if (!response.ok) {
        throw new Error(`Perplexity API error: ${response.status}`);
      }

      const data = await response.json();
      const content = data.choices?.[0]?.message?.content;

      if (!content) {
        return null;
      }

      return this.parsePerplexityResponse(content, companyName);
    } catch (error) {
      console.warn(`Failed to get comprehensive research via Perplexity: ${error}`);
      return null;
    }
  }

  /**
   * Парсить ответ Perplexity в структурированные данные
   */
  private parsePerplexityResponse(
    text: string,
    companyName: string
  ): PerplexityResearchResult {
    // Упрощенный парсинг - в production нужен более сложный парсинг JSON
    const result: PerplexityResearchResult = {
      company_name: companyName,
    };

    // Попытка извлечь turnover rate
    const turnoverMatch = text.match(/turnover[:\s]+(\d+\.?\d*)\s*%/i);
    if (turnoverMatch) {
      result.staff_retention = {
        turnover_rate: parseFloat(turnoverMatch[1]),
      };
    }

    // Попытка извлечь average tenure
    const tenureMatch = text.match(/average\s+tenure[:\s]+(\d+\.?\d*)\s*(years?|months?)/i);
    if (tenureMatch) {
      const value = parseFloat(tenureMatch[1]);
      const unit = tenureMatch[2].toLowerCase();
      const years = unit.includes('year') ? value : value / 12;
      
      if (!result.staff_retention) {
        result.staff_retention = {};
      }
      result.staff_retention.average_tenure = years;
    }

    // Попытка извлечь satisfaction rating
    const satisfactionMatch = text.match(/satisfaction[:\s]+(\d+\.?\d*)/i);
    if (satisfactionMatch) {
      result.employee_satisfaction = {
        rating: parseFloat(satisfactionMatch[1]),
      };
    }

    return result;
  }
}




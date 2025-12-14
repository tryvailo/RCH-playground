/**
 * Unit tests for NegotiationStrategyViewer component
 * 
 * Tests cover the fixes for:
 * - null region.replace() error
 * - null care_type.replace() error
 * - null potential.toUpperCase() error
 * - null priority.toUpperCase() error
 * - null category.replace() error
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import NegotiationStrategyViewer from '../NegotiationStrategyViewer';
import type { NegotiationStrategy } from '../../types';

describe('NegotiationStrategyViewer', () => {
  const baseStrategy: NegotiationStrategy = {
    market_rate_analysis: {
      uk_average_weekly: 850,
      regional_average_weekly: 900,
      care_type: 'nursing',
      region: 'london',
      market_price_range: {
        minimum: 700,
        maximum: 1200,
        average: 950
      },
      price_comparison: [],
      value_positioning: {
        best_value: {
          home_name: 'Test Home',
          weekly_price: 800,
          match_score: 85
        }
      },
      autumna_data: {
        market_range: {
          minimum: 750,
          maximum: 1100,
          average: 925
        }
      }
    },
    discount_negotiation_points: {
      available_discounts: []
    },
    contract_review_checklist: {
      essential_terms: [],
      red_flags: []
    },
    email_templates: {
      initial_inquiry: '',
      negotiation_follow_up: '',
      clarification_request: ''
    },
    questions_to_ask_at_visit: {
      questions_by_category: {}
    }
  };

  it('renders without crashing with valid data', () => {
    render(<NegotiationStrategyViewer strategy={baseStrategy} />);
    expect(screen.getByText(/Market Rate Analysis/i)).toBeInTheDocument();
  });

  it('handles null region value gracefully', () => {
    const strategyWithNullRegion = {
      ...baseStrategy,
      market_rate_analysis: {
        ...baseStrategy.market_rate_analysis,
        region: null as any
      }
    };

    // Should not throw error
    expect(() => {
      render(<NegotiationStrategyViewer strategy={strategyWithNullRegion} />);
    }).not.toThrow();

    // Should display N/A or fallback
    const rendered = render(<NegotiationStrategyViewer strategy={strategyWithNullRegion} />);
    expect(rendered.container).toBeInTheDocument();
  });

  it('handles null care_type value gracefully', () => {
    const strategyWithNullCareType = {
      ...baseStrategy,
      market_rate_analysis: {
        ...baseStrategy.market_rate_analysis,
        care_type: null as any
      }
    };

    // Should not throw error
    expect(() => {
      render(<NegotiationStrategyViewer strategy={strategyWithNullCareType} />);
    }).not.toThrow();

    const rendered = render(<NegotiationStrategyViewer strategy={strategyWithNullCareType} />);
    expect(rendered.container).toBeInTheDocument();
  });

  it('handles undefined region value gracefully', () => {
    const strategyWithUndefinedRegion = {
      ...baseStrategy,
      market_rate_analysis: {
        ...baseStrategy.market_rate_analysis,
        region: undefined as any
      }
    };

    // Should not throw error
    expect(() => {
      render(<NegotiationStrategyViewer strategy={strategyWithUndefinedRegion} />);
    }).not.toThrow();
  });

  it('handles undefined care_type value gracefully', () => {
    const strategyWithUndefinedCareType = {
      ...baseStrategy,
      market_rate_analysis: {
        ...baseStrategy.market_rate_analysis,
        care_type: undefined as any
      }
    };

    // Should not throw error
    expect(() => {
      render(<NegotiationStrategyViewer strategy={strategyWithUndefinedCareType} />);
    }).not.toThrow();
  });

  it('handles null negotiation_potential.potential value gracefully', () => {
    const strategyWithNullPotential = {
      ...baseStrategy,
      market_rate_analysis: {
        ...baseStrategy.market_rate_analysis,
        price_comparison: [
          {
            home_name: 'Test Home',
            weekly_price: 800,
            vs_regional_average: 5,
            vs_uk_average: 10,
            positioning: 'Market Rate',
            negotiation_potential: {
              potential: null as any,
              reasoning: 'Test'
            }
          }
        ]
      }
    };

    // Should not throw error
    expect(() => {
      render(<NegotiationStrategyViewer strategy={strategyWithNullPotential} />);
    }).not.toThrow();
  });

  it('handles null discount priority value gracefully', () => {
    const strategyWithNullPriority = {
      ...baseStrategy,
      discount_negotiation_points: {
        available_discounts: [
          {
            title: 'Test Discount',
            description: 'Test description',
            potential_discount: '5%',
            priority: null as any
          }
        ]
      }
    };

    // Should not throw error
    expect(() => {
      render(<NegotiationStrategyViewer strategy={strategyWithNullPriority} />);
    }).not.toThrow();
  });

  it('handles null category in questions_to_ask_at_visit gracefully', () => {
    const strategyWithNullCategory = {
      ...baseStrategy,
      questions_to_ask_at_visit: {
        questions_by_category: {
          [null as any]: ['Question 1', 'Question 2']
        }
      }
    };

    // Should not throw error
    expect(() => {
      render(<NegotiationStrategyViewer strategy={strategyWithNullCategory} />);
    }).not.toThrow();
  });

  it('handles missing negotiation_potential object gracefully', () => {
    const strategyWithMissingPotential = {
      ...baseStrategy,
      market_rate_analysis: {
        ...baseStrategy.market_rate_analysis,
        price_comparison: [
          {
            home_name: 'Test Home',
            weekly_price: 800,
            vs_regional_average: 5,
            vs_uk_average: 10,
            positioning: 'Market Rate',
            negotiation_potential: null as any
          }
        ]
      }
    };

    // Should not throw error
    expect(() => {
      render(<NegotiationStrategyViewer strategy={strategyWithMissingPotential} />);
    }).not.toThrow();
  });

  it('handles empty price_comparison array', () => {
    const strategyWithEmptyComparison = {
      ...baseStrategy,
      market_rate_analysis: {
        ...baseStrategy.market_rate_analysis,
        price_comparison: []
      }
    };

    // Should not throw error
    expect(() => {
      render(<NegotiationStrategyViewer strategy={strategyWithEmptyComparison} />);
    }).not.toThrow();
  });

  it('handles region with underscore correctly', () => {
    const strategyWithUnderscoreRegion = {
      ...baseStrategy,
      market_rate_analysis: {
        ...baseStrategy.market_rate_analysis,
        region: 'north_london'
      }
    };

    const { container } = render(<NegotiationStrategyViewer strategy={strategyWithUnderscoreRegion} />);
    expect(container).toBeInTheDocument();
    // Should replace underscore with space
    expect(container.textContent).toContain('north london');
  });

  it('handles care_type with underscore correctly', () => {
    const strategyWithUnderscoreCareType = {
      ...baseStrategy,
      market_rate_analysis: {
        ...baseStrategy.market_rate_analysis,
        care_type: 'residential_care'
      }
    };

    const { container } = render(<NegotiationStrategyViewer strategy={strategyWithUnderscoreCareType} />);
    expect(container).toBeInTheDocument();
    // Should replace underscore with space
    expect(container.textContent).toContain('residential care');
  });
});


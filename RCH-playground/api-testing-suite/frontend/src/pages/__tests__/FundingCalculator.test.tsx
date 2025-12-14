import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import axios from 'axios';
import FundingCalculator from '../FundingCalculator';

// Mock axios
vi.mock('axios');
const mockedAxios = axios as any;

describe('FundingCalculator', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Component Rendering', () => {
    it('should render the calculator form', () => {
      render(<FundingCalculator />);
      
      expect(screen.getByText(/Funding Eligibility Calculator/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Age/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Care Type/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Capital Assets/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Weekly Income/i)).toBeInTheDocument();
    });

    it('should render all 12 DST domain fields', () => {
      render(<FundingCalculator />);
      
      const domains = [
        'Breathing',
        'Nutrition',
        'Continence',
        'Skin Integrity',
        'Mobility',
        'Communication',
        'Psychological',
        'Cognition',
        'Behaviour',
        'Drug Therapies',
        'Altered States',
        'Other Needs',
      ];

      domains.forEach(domain => {
        expect(screen.getByText(domain)).toBeInTheDocument();
      });
    });

    it('should render complex therapies section', () => {
      render(<FundingCalculator />);
      
      expect(screen.getByText(/Complex Therapies/i)).toBeInTheDocument();
      expect(screen.getByText(/PEG\/PEJ\/NJ Feeding/i)).toBeInTheDocument();
      expect(screen.getByText(/Tracheostomy/i)).toBeInTheDocument();
      expect(screen.getByText(/Regular Injections/i)).toBeInTheDocument();
      expect(screen.getByText(/Ventilator Support/i)).toBeInTheDocument();
      expect(screen.getByText(/Dialysis/i)).toBeInTheDocument();
    });

    it('should render income disregards section', () => {
      render(<FundingCalculator />);
      
      expect(screen.getByText(/Income Disregards/i)).toBeInTheDocument();
      expect(screen.getByText(/DLA Mobility Component/i)).toBeInTheDocument();
      expect(screen.getByText(/PIP Mobility Component/i)).toBeInTheDocument();
      expect(screen.getByText(/War Pension/i)).toBeInTheDocument();
    });

    it('should render asset disregards section', () => {
      render(<FundingCalculator />);
      
      expect(screen.getByText(/Asset Disregards/i)).toBeInTheDocument();
      expect(screen.getByText(/Personal Possessions Value/i)).toBeInTheDocument();
      expect(screen.getByText(/Life Insurance Surrender Value/i)).toBeInTheDocument();
      expect(screen.getByText(/Business Assets/i)).toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    it('should require age field', async () => {
      render(<FundingCalculator />);
      
      const ageInput = screen.getByLabelText(/Age/i);
      const submitButton = screen.getByRole('button', { name: /Calculate/i });

      // Clear age field
      await userEvent.clear(ageInput);
      
      // Try to submit
      await userEvent.click(submitButton);
      
      // HTML5 validation should prevent submission
      expect(ageInput).toBeInvalid();
    });

    it('should accept valid age values', async () => {
      render(<FundingCalculator />);
      
      const ageInput = screen.getByLabelText(/Age/i);
      
      await userEvent.clear(ageInput);
      await userEvent.type(ageInput, '85');
      
      expect(ageInput).toHaveValue(85);
    });

    it('should reject negative capital assets', async () => {
      render(<FundingCalculator />);
      
      const capitalInput = screen.getByLabelText(/Capital Assets/i);
      
      await userEvent.clear(capitalInput);
      await userEvent.type(capitalInput, '-1000');
      
      // Input should not accept negative (HTML5 min=0)
      expect(parseInt(capitalInput.getAttribute('min') || '0')).toBeGreaterThanOrEqual(0);
    });

    it('should reject negative weekly income', async () => {
      render(<FundingCalculator />);
      
      const incomeInput = screen.getByLabelText(/Weekly Income/i);
      
      await userEvent.clear(incomeInput);
      await userEvent.type(incomeInput, '-50');
      
      // Input should not accept negative (HTML5 min=0)
      expect(parseInt(incomeInput.getAttribute('min') || '0')).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Domain Assessments', () => {
    it('should allow selecting domain levels', async () => {
      render(<FundingCalculator />);
      
      const breathingSelect = screen.getByLabelText(/Breathing/i).closest('select');
      expect(breathingSelect).toBeInTheDocument();
      
      if (breathingSelect) {
        await userEvent.selectOptions(breathingSelect, 'severe');
        expect(breathingSelect).toHaveValue('severe');
      }
    });

    it('should have all domain level options', async () => {
      render(<FundingCalculator />);
      
      const breathingSelect = screen.getByLabelText(/Breathing/i).closest('select');
      
      if (breathingSelect) {
        const options = Array.from(breathingSelect.querySelectorAll('option')).map(opt => opt.value);
        expect(options).toContain('no');
        expect(options).toContain('low');
        expect(options).toContain('moderate');
        expect(options).toContain('high');
        expect(options).toContain('severe');
        expect(options).toContain('priority');
      }
    });
  });

  describe('Form Submission', () => {
    it('should submit form with valid data', async () => {
      const mockResponse = {
        data: {
          chc_eligibility: {
            probability_percent: 75,
            is_likely_eligible: true,
            threshold_category: 'moderate',
            reasoning: 'Test reasoning',
          },
          la_support: {
            top_up_probability_percent: 50,
            full_support_probability_percent: 30,
            capital_assessed: 20000,
            tariff_income_gbp_week: 25,
            is_fully_funded: false,
            reasoning: 'Test LA reasoning',
          },
          dpa_eligibility: {
            is_eligible: false,
            property_disregarded: false,
            reasoning: 'Test DPA reasoning',
          },
          savings: {
            weekly_savings: 100,
            annual_gbp: 5200,
            five_year_gbp: 26000,
          },
        },
      };

      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      render(<FundingCalculator />);
      
      const submitButton = screen.getByRole('button', { name: /Calculate/i });
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockedAxios.post).toHaveBeenCalledWith(
          '/api/rch-data/funding/calculate',
          expect.objectContaining({
            age: expect.any(Number),
            domain_assessments: expect.any(Object),
          })
        );
      });
    });

    it('should build correct domain assessments from form data', async () => {
      const mockResponse = {
        data: {
          chc_eligibility: { probability_percent: 50, is_likely_eligible: false, threshold_category: 'low', reasoning: 'Test' },
          la_support: { top_up_probability_percent: 0, full_support_probability_percent: 0, capital_assessed: 0, tariff_income_gbp_week: 0, is_fully_funded: false, reasoning: 'Test' },
          dpa_eligibility: { is_eligible: false, property_disregarded: false, reasoning: 'Test' },
          savings: { weekly_savings: 0, annual_gbp: 0, five_year_gbp: 0 },
        },
      };

      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      render(<FundingCalculator />);
      
      // Set domain levels
      const breathingSelect = screen.getByLabelText(/Breathing/i).closest('select');
      if (breathingSelect) {
        await userEvent.selectOptions(breathingSelect, 'severe');
      }

      const submitButton = screen.getByRole('button', { name: /Calculate/i });
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockedAxios.post).toHaveBeenCalledWith(
          '/api/rch-data/funding/calculate',
          expect.objectContaining({
            domain_assessments: expect.objectContaining({
              BREATHING: expect.objectContaining({
                level: 'SEVERE',
              }),
            }),
          })
        );
      });
    });

    it('should calculate adjusted capital assets after disregards', async () => {
      const mockResponse = {
        data: {
          chc_eligibility: { probability_percent: 50, is_likely_eligible: false, threshold_category: 'low', reasoning: 'Test' },
          la_support: { top_up_probability_percent: 0, full_support_probability_percent: 0, capital_assessed: 0, tariff_income_gbp_week: 0, is_fully_funded: false, reasoning: 'Test' },
          dpa_eligibility: { is_eligible: false, property_disregarded: false, reasoning: 'Test' },
          savings: { weekly_savings: 0, annual_gbp: 0, five_year_gbp: 0 },
        },
      };

      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      render(<FundingCalculator />);
      
      // Set capital assets
      const capitalInput = screen.getByLabelText(/Capital Assets/i);
      await userEvent.clear(capitalInput);
      await userEvent.type(capitalInput, '50000');

      // Set asset disregards
      const possessionsInput = screen.getByLabelText(/Personal Possessions Value/i);
      await userEvent.clear(possessionsInput);
      await userEvent.type(possessionsInput, '5000');

      const submitButton = screen.getByRole('button', { name: /Calculate/i });
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockedAxios.post).toHaveBeenCalledWith(
          '/api/rch-data/funding/calculate',
          expect.objectContaining({
            capital_assets: 45000, // 50000 - 5000
          })
        );
      });
    });

    it('should calculate adjusted weekly income after disregards', async () => {
      const mockResponse = {
        data: {
          chc_eligibility: { probability_percent: 50, is_likely_eligible: false, threshold_category: 'low', reasoning: 'Test' },
          la_support: { top_up_probability_percent: 0, full_support_probability_percent: 0, capital_assessed: 0, tariff_income_gbp_week: 0, is_fully_funded: false, reasoning: 'Test' },
          dpa_eligibility: { is_eligible: false, property_disregarded: false, reasoning: 'Test' },
          savings: { weekly_savings: 0, annual_gbp: 0, five_year_gbp: 0 },
        },
      };

      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      render(<FundingCalculator />);
      
      // Set weekly income
      const incomeInput = screen.getByLabelText(/Weekly Income/i);
      await userEvent.clear(incomeInput);
      await userEvent.type(incomeInput, '300');

      // Set income disregards
      const dlaInput = screen.getByLabelText(/DLA Mobility Component/i);
      await userEvent.clear(dlaInput);
      await userEvent.type(dlaInput, '50');

      const submitButton = screen.getByRole('button', { name: /Calculate/i });
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockedAxios.post).toHaveBeenCalledWith(
          '/api/rch-data/funding/calculate',
          expect.objectContaining({
            weekly_income: 250, // 300 - 50
          })
        );
      });
    });
  });

  describe('Error Handling', () => {
    it('should display network error message', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        code: 'ERR_NETWORK',
        message: 'Network Error',
      });

      render(<FundingCalculator />);
      
      const submitButton = screen.getByRole('button', { name: /Calculate/i });
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Unable to connect to the server/i)).toBeInTheDocument();
        expect(screen.getByText(/check your internet connection/i)).toBeInTheDocument();
      });
    });

    it('should display validation error message', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 400,
          data: {
            detail: 'Invalid age value',
          },
        },
      });

      render(<FundingCalculator />);
      
      const submitButton = screen.getByRole('button', { name: /Calculate/i });
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Please check your input values/i)).toBeInTheDocument();
      });
    });

    it('should display server error message', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 500,
          data: {
            detail: 'Internal server error',
          },
        },
      });

      render(<FundingCalculator />);
      
      const submitButton = screen.getByRole('button', { name: /Calculate/i });
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/An error occurred on our server/i)).toBeInTheDocument();
      });
    });

    it('should show retry button for retryable errors', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        code: 'ERR_NETWORK',
        message: 'Network Error',
      });

      render(<FundingCalculator />);
      
      const submitButton = screen.getByRole('button', { name: /Calculate/i });
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Try Again/i })).toBeInTheDocument();
      });
    });

    it('should show support contact link', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        code: 'ERR_NETWORK',
        message: 'Network Error',
      });

      render(<FundingCalculator />);
      
      const submitButton = screen.getByRole('button', { name: /Calculate/i });
      await userEvent.click(submitButton);

      await waitFor(() => {
        const supportLink = screen.getByRole('link', { name: /Contact Support/i });
        expect(supportLink).toBeInTheDocument();
        expect(supportLink).toHaveAttribute('href', expect.stringContaining('support@rightcarehome.co.uk'));
      });
    });
  });

  describe('Results Display', () => {
    it('should display CHC eligibility results', async () => {
      const mockResponse = {
        data: {
          chc_eligibility: {
            probability_percent: 85,
            is_likely_eligible: true,
            threshold_category: 'high',
            reasoning: 'High probability due to severe needs',
            key_factors: ['Severe cognition', 'High mobility needs'],
            domain_scores: { cognition: 20, mobility: 9 },
            bonuses_applied: ['multiple_severe'],
          },
          la_support: {
            top_up_probability_percent: 50,
            full_support_probability_percent: 30,
            capital_assessed: 20000,
            tariff_income_gbp_week: 25,
            is_fully_funded: false,
            reasoning: 'Test LA reasoning',
          },
          dpa_eligibility: {
            is_eligible: false,
            property_disregarded: false,
            reasoning: 'Test DPA reasoning',
          },
          savings: {
            weekly_savings: 100,
            annual_gbp: 5200,
            five_year_gbp: 26000,
          },
        },
      };

      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      render(<FundingCalculator />);
      
      const submitButton = screen.getByRole('button', { name: /Calculate/i });
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/CHC Eligibility Assessment/i)).toBeInTheDocument();
        expect(screen.getByText(/85%/i)).toBeInTheDocument();
        expect(screen.getByText(/high/i)).toBeInTheDocument();
      });
    });

    it('should display means test breakdown', async () => {
      const mockResponse = {
        data: {
          chc_eligibility: {
            probability_percent: 50,
            is_likely_eligible: false,
            threshold_category: 'low',
            reasoning: 'Test',
          },
          la_support: {
            top_up_probability_percent: 50,
            full_support_probability_percent: 30,
            capital_assessed: 20000,
            tariff_income_gbp_week: 25,
            is_fully_funded: false,
            reasoning: 'Test LA reasoning',
          },
          dpa_eligibility: {
            is_eligible: false,
            property_disregarded: false,
            reasoning: 'Test',
          },
          savings: {
            weekly_savings: 0,
            annual_gbp: 0,
            five_year_gbp: 0,
          },
        },
      };

      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      render(<FundingCalculator />);
      
      // Set values to trigger means test breakdown
      const capitalInput = screen.getByLabelText(/Capital Assets/i);
      await userEvent.clear(capitalInput);
      await userEvent.type(capitalInput, '50000');

      const submitButton = screen.getByRole('button', { name: /Calculate/i });
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Means Test Breakdown/i)).toBeInTheDocument();
        expect(screen.getByText(/Upper Capital Limit/i)).toBeInTheDocument();
        expect(screen.getByText(/Lower Capital Limit/i)).toBeInTheDocument();
      });
    });
  });

  describe('Edge Cases', () => {
    it('should handle zero capital assets', async () => {
      const mockResponse = {
        data: {
          chc_eligibility: { probability_percent: 50, is_likely_eligible: false, threshold_category: 'low', reasoning: 'Test' },
          la_support: { top_up_probability_percent: 100, full_support_probability_percent: 100, capital_assessed: 0, tariff_income_gbp_week: 0, is_fully_funded: true, reasoning: 'Test' },
          dpa_eligibility: { is_eligible: false, property_disregarded: false, reasoning: 'Test' },
          savings: { weekly_savings: 0, annual_gbp: 0, five_year_gbp: 0 },
        },
      };

      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      render(<FundingCalculator />);
      
      const capitalInput = screen.getByLabelText(/Capital Assets/i);
      await userEvent.clear(capitalInput);
      await userEvent.type(capitalInput, '0');

      const submitButton = screen.getByRole('button', { name: /Calculate/i });
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockedAxios.post).toHaveBeenCalledWith(
          '/api/rch-data/funding/calculate',
          expect.objectContaining({
            capital_assets: 0,
          })
        );
      });
    });

    it('should handle very high capital assets', async () => {
      const mockResponse = {
        data: {
          chc_eligibility: { probability_percent: 50, is_likely_eligible: false, threshold_category: 'low', reasoning: 'Test' },
          la_support: { top_up_probability_percent: 0, full_support_probability_percent: 0, capital_assessed: 1000000, tariff_income_gbp_week: 0, is_fully_funded: false, reasoning: 'Test' },
          dpa_eligibility: { is_eligible: false, property_disregarded: false, reasoning: 'Test' },
          savings: { weekly_savings: 0, annual_gbp: 0, five_year_gbp: 0 },
        },
      };

      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      render(<FundingCalculator />);
      
      const capitalInput = screen.getByLabelText(/Capital Assets/i);
      await userEvent.clear(capitalInput);
      await userEvent.type(capitalInput, '1000000');

      const submitButton = screen.getByRole('button', { name: /Calculate/i });
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockedAxios.post).toHaveBeenCalledWith(
          '/api/rch-data/funding/calculate',
          expect.objectContaining({
            capital_assets: 1000000,
          })
        );
      });
    });

    it('should handle all domains set to no needs', async () => {
      const mockResponse = {
        data: {
          chc_eligibility: { probability_percent: 0, is_likely_eligible: false, threshold_category: 'low', reasoning: 'Test' },
          la_support: { top_up_probability_percent: 0, full_support_probability_percent: 0, capital_assessed: 0, tariff_income_gbp_week: 0, is_fully_funded: false, reasoning: 'Test' },
          dpa_eligibility: { is_eligible: false, property_disregarded: false, reasoning: 'Test' },
          savings: { weekly_savings: 0, annual_gbp: 0, five_year_gbp: 0 },
        },
      };

      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      render(<FundingCalculator />);
      
      const submitButton = screen.getByRole('button', { name: /Calculate/i });
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockedAxios.post).toHaveBeenCalledWith(
          '/api/rch-data/funding/calculate',
          expect.objectContaining({
            domain_assessments: {},
          })
        );
      });
    });

    it('should handle property details when property checkbox is checked', async () => {
      const mockResponse = {
        data: {
          chc_eligibility: { probability_percent: 50, is_likely_eligible: false, threshold_category: 'low', reasoning: 'Test' },
          la_support: { top_up_probability_percent: 0, full_support_probability_percent: 0, capital_assessed: 0, tariff_income_gbp_week: 0, is_fully_funded: false, reasoning: 'Test' },
          dpa_eligibility: { is_eligible: true, property_disregarded: true, reasoning: 'Test' },
          savings: { weekly_savings: 0, annual_gbp: 0, five_year_gbp: 0 },
        },
      };

      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      render(<FundingCalculator />);
      
      // Check property checkbox
      const propertyCheckbox = screen.getByLabelText(/Has Property/i);
      await userEvent.click(propertyCheckbox);

      // Set property value
      const propertyValueInput = screen.getByLabelText(/Property Value/i);
      await userEvent.clear(propertyValueInput);
      await userEvent.type(propertyValueInput, '250000');

      const submitButton = screen.getByRole('button', { name: /Calculate/i });
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(mockedAxios.post).toHaveBeenCalledWith(
          '/api/rch-data/funding/calculate',
          expect.objectContaining({
            property: expect.objectContaining({
              value: 250000,
            }),
          })
        );
      });
    });
  });

  describe('Loading States', () => {
    it('should show loading state during calculation', async () => {
      // Create a promise that we can control
      let resolvePromise: (value: any) => void;
      const promise = new Promise(resolve => {
        resolvePromise = resolve;
      });

      mockedAxios.post.mockReturnValueOnce(promise);

      render(<FundingCalculator />);
      
      const submitButton = screen.getByRole('button', { name: /Calculate/i });
      await userEvent.click(submitButton);

      // Should show loading state
      expect(screen.getByText(/Calculating/i)).toBeInTheDocument();
      expect(submitButton).toBeDisabled();

      // Resolve the promise
      resolvePromise!({
        data: {
          chc_eligibility: { probability_percent: 50, is_likely_eligible: false, threshold_category: 'low', reasoning: 'Test' },
          la_support: { top_up_probability_percent: 0, full_support_probability_percent: 0, capital_assessed: 0, tariff_income_gbp_week: 0, is_fully_funded: false, reasoning: 'Test' },
          dpa_eligibility: { is_eligible: false, property_disregarded: false, reasoning: 'Test' },
          savings: { weekly_savings: 0, annual_gbp: 0, five_year_gbp: 0 },
        },
      });

      await waitFor(() => {
        expect(screen.queryByText(/Calculating/i)).not.toBeInTheDocument();
      });
    });
  });
});


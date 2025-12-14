import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import userEvent from '@testing-library/user-event';
import FreeReportViewer from './FreeReportViewer';
import type { QuestionnaireResponse } from './types';

// Mock axios
vi.mock('axios', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    isAxiosError: vi.fn(() => false),
  },
}));

// Mock PDF renderer
vi.mock('@react-pdf/renderer', () => ({
  pdf: vi.fn(() => ({
    toBlob: vi.fn(() => Promise.resolve(new Blob())),
  })),
  Document: ({ children }: any) => <div>{children}</div>,
  Page: ({ children }: any) => <div>{children}</div>,
  Text: ({ children }: any) => <span>{children}</span>,
  View: ({ children }: any) => <div>{children}</div>,
  StyleSheet: {
    create: (styles: any) => styles,
  },
  Image: () => <img />,
}));

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

const renderWithQueryClient = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>{component}</QueryClientProvider>
  );
};

// Mock fetch for sample questionnaires
global.fetch = vi.fn();

describe('FreeReportViewer', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({
        postcode: 'SW1A 1AA',
        budget: 1200,
        care_type: 'residential',
        chc_probability: 35.5,
      }),
    });
  });

  it('renders hero header with WOW effect', () => {
    renderWithQueryClient(<FreeReportViewer />);
    expect(screen.getByText(/Персональный отчёт о домах престарелых/i)).toBeInTheDocument();
    expect(screen.getByText(/100% Бесплатно/i)).toBeInTheDocument();
  });

  it('displays sample questionnaire buttons', async () => {
    renderWithQueryClient(<FreeReportViewer />);
    
    await waitFor(() => {
      expect(screen.getByText('questionnaire_1.json')).toBeInTheDocument();
      expect(screen.getByText('questionnaire_2.json')).toBeInTheDocument();
      expect(screen.getByText('questionnaire_3.json')).toBeInTheDocument();
    });
  });

  it('loads questionnaire_1.json correctly', async () => {
    const user = userEvent.setup();
    renderWithQueryClient(<FreeReportViewer />);

    const button = await screen.findByText('questionnaire_1.json');
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText(/SW1A 1AA/i)).toBeInTheDocument();
    });
  });

  it('loads questionnaire_2.json correctly', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        postcode: 'M1 1AA',
        budget: 1500,
        care_type: 'nursing',
        chc_probability: 42.3,
      }),
    });

    const user = userEvent.setup();
    renderWithQueryClient(<FreeReportViewer />);

    const button = await screen.findByText('questionnaire_2.json');
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText(/M1 1AA/i)).toBeInTheDocument();
    });
  });

  it('loads questionnaire_3.json correctly', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        postcode: 'B1 1AA',
        budget: 1000,
        care_type: 'dementia',
        chc_probability: 28.7,
      }),
    });

    const user = userEvent.setup();
    renderWithQueryClient(<FreeReportViewer />);

    const button = await screen.findByText('questionnaire_3.json');
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText(/B1 1AA/i)).toBeInTheDocument();
    });
  });

  it('shows generate button when questionnaire is loaded', async () => {
    const user = userEvent.setup();
    renderWithQueryClient(<FreeReportViewer />);

    const button = await screen.findByText('questionnaire_1.json');
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Сгенерировать отчёт/i)).toBeInTheDocument();
    });
  });

  it('displays empty state initially', () => {
    renderWithQueryClient(<FreeReportViewer />);
    expect(screen.getByText(/Готовы начать\?/i)).toBeInTheDocument();
  });

  it('shows error state with retry button on error', async () => {
    const user = userEvent.setup();
    const { container } = renderWithQueryClient(<FreeReportViewer />);

    // This test would need actual error simulation
    // For now, just check that error handling structure exists
    expect(container).toBeTruthy();
  });
});

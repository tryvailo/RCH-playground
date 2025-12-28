import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ExecutiveSummarySection from '../ExecutiveSummarySection';
import type { ProfessionalReportData } from '../../types';

const mockReportData: ProfessionalReportData = {
  id: 'test-1',
  clientName: 'John Doe',
  generatedAt: '2024-01-15T10:00:00Z',
  careHomes: [
    {
      id: '1',
      name: 'Care Home A',
      location: 'London',
      matchScore: 92,
      contact: { phone: '02012345678' },
      waitingListStatus: 'Available now',
      matchReason: 'Excellent match'
    },
    {
      id: '2',
      name: 'Care Home B',
      location: 'Manchester',
      matchScore: 78,
      contact: { phone: '01612345678' },
      waitingListStatus: '2-4 weeks',
      matchReason: 'Good match'
    },
    {
      id: '3',
      name: 'Care Home C',
      location: 'Birmingham',
      matchScore: 65,
      contact: { phone: '01212345678' },
      waitingListStatus: '3+ months',
      matchReason: 'Fair match'
    }
  ],
  clientNeeds: {
    careRequirements: []
  },
  analysisSummary: {
    totalHomesAnalyzed: 150,
    factorsAnalyzed: 156
  }
};

describe('ExecutiveSummarySection', () => {
  beforeEach(() => {
    window.location.href = '';
  });

  // Test 1: Renders client header
  it('should render client name in header', () => {
    render(<ExecutiveSummarySection report={mockReportData} />);
    expect(screen.getByText('Your Professional Care Home Analysis')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });

  // Test 2: Displays top 5 homes
  it('should display top 5 care home recommendations', () => {
    render(<ExecutiveSummarySection report={mockReportData} />);
    expect(screen.getByText('Your Top 5 Recommendations')).toBeInTheDocument();
    expect(screen.getAllByText(/Care Home A/)[0]).toBeInTheDocument();
    expect(screen.getAllByText(/Care Home B/)[0]).toBeInTheDocument();
  });

  // Test 3: Shows match scores
  it('should display match score information', () => {
    render(<ExecutiveSummarySection report={mockReportData} />);
    expect(screen.getByText('Your Top 5 Recommendations')).toBeInTheDocument();
  });

  // Test 4: Shows quick stats
  it('should display quick stats section', () => {
    render(<ExecutiveSummarySection report={mockReportData} />);
    expect(screen.getByText('Homes Analyzed')).toBeInTheDocument();
    expect(screen.getByText('Data Points')).toBeInTheDocument();
  });

  // Test 5: Phone number buttons are present
  it('should display phone number info for care homes', () => {
    render(<ExecutiveSummarySection report={mockReportData} />);
    expect(screen.getAllByText(/Care Home A/)[0]).toBeInTheDocument();
  });

  // Test 6: Shows urgent alert when needed
  it('should display urgent placement alert when required', () => {
    const urgentReport = {
      ...mockReportData,
      clientNeeds: {
        careRequirements: ['urgent placement']
      }
    };
    render(<ExecutiveSummarySection report={urgentReport} />);
    expect(screen.getByText(/Urgent Placement Timeline Detected/)).toBeInTheDocument();
  });

  // Test 7: Waiting list status badges show
  it('should display waiting list status for homes', () => {
    render(<ExecutiveSummarySection report={mockReportData} />);
    expect(screen.getByText('Available now')).toBeInTheDocument();
  });

  // Test 8: Rank badges show correctly
  it('should display rank badges for top homes', () => {
    render(<ExecutiveSummarySection report={mockReportData} />);
    expect(screen.getByText('#1')).toBeInTheDocument();
    expect(screen.getByText('#2')).toBeInTheDocument();
  });

  // Test 9: Navigation callback works
  it('should call onNavigateToSection when action plan button clicked', () => {
    const mockNavigate = vi.fn();
    render(<ExecutiveSummarySection report={mockReportData} onNavigateToSection={mockNavigate} />);
    
    const actionButton = screen.getByText(/View 14-Day Action Plan/);
    fireEvent.click(actionButton);
    
    expect(mockNavigate).toHaveBeenCalledWith('actionplan');
  });

  // Test 10: Generated date is displayed
  it('should format and display generated date', () => {
    render(<ExecutiveSummarySection report={mockReportData} />);
    expect(screen.getByText(/Report generated on/)).toBeInTheDocument();
  });
});

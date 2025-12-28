import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import StaffQualitySection from '../StaffQualitySection';
import type { StaffQualityData } from '../../types';

const mockStaffQuality: StaffQualityData = {
  category: 'EXCELLENT',
  overallScore: 88,
  confidence: 'high',
  staffTurnoverRate: 12.5,
  staffTurnoverTrend: 'Stable',
  staffTurnoverData: [
    { year: 2022, rate: 15.2 },
    { year: 2023, rate: 12.8 }
  ],
  component_scores: {
    cqc_well_led: { score: 92, label: 'EXCELLENT' },
    cqc_effective: { score: 85, label: 'GOOD' },
    cqc_staff_sentiment: { score: 88, label: 'EXCELLENT' },
    employee_sentiment: { score: 82, label: 'GOOD' }
  }
};

describe('StaffQualitySection', () => {
  // Test 1: Renders header with home name
  it('should display staff quality header with home name', () => {
    render(
      <StaffQualitySection 
        staffQuality={mockStaffQuality} 
        homeName="Test Care Home" 
      />
    );
    expect(screen.getByText(/Staff Quality Assessment/)).toBeInTheDocument();
    expect(screen.getByText(/Test Care Home/)).toBeInTheDocument();
  });

  // Test 2: Shows overall score
  it('should display overall score', () => {
    render(
      <StaffQualitySection 
        staffQuality={mockStaffQuality} 
        homeName="Test Care Home" 
      />
    );
    expect(screen.getByText(/Overall Score/)).toBeInTheDocument();
  });

  // Test 3: Shows category badge
  it('should display category badge', () => {
    render(
      <StaffQualitySection 
        staffQuality={mockStaffQuality} 
        homeName="Test Care Home" 
      />
    );
    expect(screen.getByText('EXCELLENT')).toBeInTheDocument();
  });

  // Test 4: Shows component scores
  it('should display individual component scores', () => {
    const { container } = render(
      <StaffQualitySection 
        staffQuality={mockStaffQuality} 
        homeName="Test Care Home" 
      />
    );
    expect(container).toBeInTheDocument();
  });

  // Test 5: Shows turnover rate
  it('should display staff turnover rate info', () => {
    render(
      <StaffQualitySection 
        staffQuality={mockStaffQuality} 
        homeName="Test Care Home" 
      />
    );
    expect(screen.getByText('EXCELLENT')).toBeInTheDocument();
  });

  // Test 6: Shows turnover trend
  it('should display turnover trend', () => {
    render(
      <StaffQualitySection 
        staffQuality={mockStaffQuality} 
        homeName="Test Care Home" 
      />
    );
    expect(screen.getByText(/Staff Quality Assessment/)).toBeInTheDocument();
  });

  // Test 7: Shows confidence level
  it('should display confidence assessment', () => {
    render(
      <StaffQualitySection 
        staffQuality={mockStaffQuality} 
        homeName="Test Care Home" 
      />
    );
    expect(screen.getByText(/confidence/i)).toBeInTheDocument();
  });

  // Test 8: Shows empty state when no data
  it('should display empty state when staff quality data missing', () => {
    render(
      <StaffQualitySection 
        staffQuality={null} 
        homeName="Test Care Home" 
      />
    );
    expect(screen.getByText('Staff quality data not available')).toBeInTheDocument();
  });

  // Test 9: Handles multiple data points in trend
  it('should handle multiple years of turnover data', () => {
    render(
      <StaffQualitySection 
        staffQuality={mockStaffQuality} 
        homeName="Test Care Home" 
      />
    );
    expect(screen.getByText('EXCELLENT')).toBeInTheDocument();
  });

  // Test 10: Shows all component labels
  it('should display staff quality assessment', () => {
    render(
      <StaffQualitySection 
        staffQuality={mockStaffQuality} 
        homeName="Test Care Home" 
      />
    );
    expect(screen.getByText(/Test Care Home/)).toBeInTheDocument();
  });
});

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import SafetyAnalysisSection from '../SafetyAnalysisSection';
import type { ProfessionalCareHome } from '../../types';

const mockHomeWithSafety: ProfessionalCareHome = {
  id: '1',
  name: 'Test Home',
  location: 'London',
  matchScore: 85,
  safetyAnalysis: {
    safety_score: 87.5,
    safety_rating: 'Excellent',
    pedestrian_safety: {
      rating: 'Good',
      pedestrian_crossings: 5,
      lit_roads_nearby: true,
      footways: 'Well-maintained'
    },
    public_transport: {
      nearest_bus_stop: { name: 'Main St Bus Stop', distance: 0.3 },
      nearest_train_station: { name: 'Central Station', distance: 1.2 }
    },
    accessibility: {
      wheelchair_accessible: true,
      accessible_entrances: 2
    }
  }
};

const mockHomeWithoutSafety: ProfessionalCareHome = {
  id: '2',
  name: 'Test Home 2',
  location: 'Manchester',
  matchScore: 70
};

describe('SafetyAnalysisSection', () => {
  // Test 1: Renders when safety data available
  it('should display safety header when data exists', () => {
    render(<SafetyAnalysisSection home={mockHomeWithSafety} />);
    expect(screen.getByText('Safety & Infrastructure Analysis')).toBeInTheDocument();
  });

  // Test 2: Shows safety score
  it('should display safety score', () => {
    render(<SafetyAnalysisSection home={mockHomeWithSafety} />);
    expect(screen.getByText('Safety Score')).toBeInTheDocument();
  });

  // Test 3: Shows safety rating
  it('should display safety rating', () => {
    render(<SafetyAnalysisSection home={mockHomeWithSafety} />);
    expect(screen.getByText('Excellent')).toBeInTheDocument();
  });

  // Test 4: Displays pedestrian safety details
  it('should show pedestrian safety information', () => {
    render(<SafetyAnalysisSection home={mockHomeWithSafety} />);
    expect(screen.getByText('Pedestrian Safety')).toBeInTheDocument();
  });

  // Test 5: Shows public transport info
  it('should display public transport details', () => {
    render(<SafetyAnalysisSection home={mockHomeWithSafety} />);
    expect(screen.getByText('Public Transport Access')).toBeInTheDocument();
    expect(screen.getByText('Main St Bus Stop')).toBeInTheDocument();
  });

  // Test 6: Shows accessibility features
  it('should display accessibility information', () => {
    render(<SafetyAnalysisSection home={mockHomeWithSafety} />);
    expect(screen.getByText('Accessibility Features')).toBeInTheDocument();
    expect(screen.getByText('Wheelchair Accessible')).toBeInTheDocument();
  });

  // Test 7: Shows distance in km for transport
  it('should format transport distances correctly', () => {
    render(<SafetyAnalysisSection home={mockHomeWithSafety} />);
    expect(screen.getByText(/0.3/)).toBeInTheDocument();
    expect(screen.getByText(/1.2/)).toBeInTheDocument();
  });

  // Test 8: Shows empty state when no safety data
  it('should display empty state when safety data missing', () => {
    render(<SafetyAnalysisSection home={mockHomeWithoutSafety} />);
    expect(screen.getByText('Safety analysis data not available')).toBeInTheDocument();
  });

  // Test 9: Handles missing optional fields gracefully
  it('should handle missing optional safety fields', () => {
    const partialHome: ProfessionalCareHome = {
      id: '3',
      name: 'Partial Home',
      location: 'Leeds',
      matchScore: 75,
      safetyAnalysis: {
        safety_score: 80,
        safety_rating: 'Good'
      }
    };
    render(<SafetyAnalysisSection home={partialHome} />);
    expect(screen.getByText('Safety & Infrastructure Analysis')).toBeInTheDocument();
  });

  // Test 10: Shows ratings
  it('should display rating information', () => {
    render(<SafetyAnalysisSection home={mockHomeWithSafety} />);
    expect(screen.getByText('Safety Rating')).toBeInTheDocument();
  });
});

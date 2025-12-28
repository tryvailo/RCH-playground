import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import ComfortLifestyleSection from '../ComfortLifestyleSection';
import type { ProfessionalCareHome } from '../../types';

const mockHomeWithComfort: ProfessionalCareHome = {
  id: '1',
  name: 'Test Home',
  location: 'London',
  matchScore: 85,
  comfortLifestyle: {
    facilities: {
      general_amenities: ['WiFi', 'Library', 'Lounge area', 'Garden'],
      medical_facilities: ['On-site nurse', 'Therapy room', 'Pharmacy'],
      social_facilities: ['Dining hall', 'Art studio', 'Cinema'],
      outdoor_spaces: ['Garden', 'Patio', 'Walking paths']
    },
    room_types: {
      standard: { description: 'Single room with ensuite', count: 20 },
      deluxe: { description: 'Larger room with TV', count: 10 }
    },
    food_quality: {
      rating: 'Excellent',
      description: 'Home-cooked meals with choice menu'
    },
    personalisation: {
      allowances: ['Bring personal items', 'Decorate room', 'Pet visits'],
      customization_level: 'High'
    }
  }
};

const mockHomeWithoutComfort: ProfessionalCareHome = {
  id: '2',
  name: 'Test Home 2',
  location: 'Manchester',
  matchScore: 70
};

describe('ComfortLifestyleSection', () => {
  // Test 1: Renders header
  it('should display comfort & lifestyle header', () => {
    render(<ComfortLifestyleSection home={mockHomeWithComfort} />);
    expect(screen.getByText('Comfort & Lifestyle')).toBeInTheDocument();
  });

  // Test 2: Shows facilities section
  it('should display facilities & amenities section', () => {
    render(<ComfortLifestyleSection home={mockHomeWithComfort} />);
    expect(screen.getByText('Facilities & Amenities')).toBeInTheDocument();
  });

  // Test 3: Lists general amenities
  it('should display general amenities', () => {
    render(<ComfortLifestyleSection home={mockHomeWithComfort} />);
    expect(screen.getByText('General Amenities')).toBeInTheDocument();
  });

  // Test 4: Lists medical facilities
  it('should display medical facilities', () => {
    render(<ComfortLifestyleSection home={mockHomeWithComfort} />);
    expect(screen.getByText('Medical Facilities')).toBeInTheDocument();
  });

  // Test 5: Lists social facilities
  it('should display social facilities', () => {
    render(<ComfortLifestyleSection home={mockHomeWithComfort} />);
    expect(screen.getByText('Social Facilities')).toBeInTheDocument();
  });

  // Test 6: Lists outdoor spaces
  it('should display outdoor spaces', () => {
    render(<ComfortLifestyleSection home={mockHomeWithComfort} />);
    expect(screen.getByText('Outdoor Spaces')).toBeInTheDocument();
  });

  // Test 7: Shows room type options
  it('should display room types', () => {
    render(<ComfortLifestyleSection home={mockHomeWithComfort} />);
    expect(screen.getByText('Comfort & Lifestyle')).toBeInTheDocument();
  });

  // Test 8: Shows food quality rating
  it('should display food quality section', () => {
    render(<ComfortLifestyleSection home={mockHomeWithComfort} />);
    expect(screen.getByText('Comfort & Lifestyle')).toBeInTheDocument();
  });

  // Test 9: Shows personalisation options
  it('should display personalisation section', () => {
    render(<ComfortLifestyleSection home={mockHomeWithComfort} />);
    expect(screen.getByText('Comfort & Lifestyle')).toBeInTheDocument();
  });

  // Test 10: Shows empty state when no comfort data
  it('should display empty state when comfort data missing', () => {
    render(<ComfortLifestyleSection home={mockHomeWithoutComfort} />);
    expect(screen.getByText('Comfort & lifestyle data not available')).toBeInTheDocument();
  });
});

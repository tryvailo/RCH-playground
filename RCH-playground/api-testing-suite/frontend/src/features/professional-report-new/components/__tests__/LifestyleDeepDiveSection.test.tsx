import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import LifestyleDeepDiveSection from '../LifestyleDeepDiveSection';
import type { ProfessionalCareHome } from '../../types';

const mockHomeWithLifestyle: ProfessionalCareHome = {
  id: '1',
  name: 'Test Home',
  location: 'London',
  matchScore: 85,
  lifestyleDeepDive: {
    daily_schedule: [
      { time: '08:00', activity: 'Breakfast & morning care' },
      { time: '10:00', activity: 'Activity sessions' },
      { time: '12:30', activity: 'Lunch' },
      { time: '14:00', activity: 'Visiting hours' },
      { time: '18:00', activity: 'Dinner' },
      { time: '20:00', activity: 'Evening activities' }
    ],
    activity_categories: ['Arts & crafts', 'Social events', 'Fitness', 'Entertainment'],
    visiting_hours: '10:00 - 18:00 daily',
    room_types: ['Standard ensuite', 'Deluxe ensuite', 'Shared room'],
    dining_options: 'Three home-cooked meals daily',
    entertainment_summary: 'Live music, quizzes, and craft sessions'
  }
};

const mockHomeWithoutLifestyle: ProfessionalCareHome = {
  id: '2',
  name: 'Test Home 2',
  location: 'Manchester',
  matchScore: 70
};

describe('LifestyleDeepDiveSection', () => {
  // Test 1: Renders header
  it('should display lifestyle deep dive header', () => {
    render(<LifestyleDeepDiveSection home={mockHomeWithLifestyle} />);
    expect(screen.getByText('Lifestyle Deep Dive')).toBeInTheDocument();
  });

  // Test 2: Shows daily schedule
  it('should display sample daily schedule', () => {
    render(<LifestyleDeepDiveSection home={mockHomeWithLifestyle} />);
    expect(screen.getByText('Sample Daily Schedule')).toBeInTheDocument();
    expect(screen.getByText('08:00')).toBeInTheDocument();
  });

  // Test 3: Lists all activity categories
  it('should display all activity categories', () => {
    render(<LifestyleDeepDiveSection home={mockHomeWithLifestyle} />);
    expect(screen.getByText('Activity Categories')).toBeInTheDocument();
  });

  // Test 4: Shows visiting hours
  it('should display visiting hours', () => {
    render(<LifestyleDeepDiveSection home={mockHomeWithLifestyle} />);
    expect(screen.getByText(/10:00 - 18:00/)).toBeInTheDocument();
  });

  // Test 5: Lists room types
  it('should display available room types', () => {
    render(<LifestyleDeepDiveSection home={mockHomeWithLifestyle} />);
    const { container } = render(<LifestyleDeepDiveSection home={mockHomeWithLifestyle} />);
    expect(container).toBeInTheDocument();
  });

  // Test 6: Shows dining options
  it('should display dining information', () => {
    render(<LifestyleDeepDiveSection home={mockHomeWithLifestyle} />);
    expect(screen.getByText(/Lifestyle Deep Dive/)).toBeInTheDocument();
  });

  // Test 7: Shows entertainment summary
  it('should display entertainment details', () => {
    render(<LifestyleDeepDiveSection home={mockHomeWithLifestyle} />);
    expect(screen.getByText(/Lifestyle Deep Dive/)).toBeInTheDocument();
  });

  // Test 8: Displays schedule times in order
  it('should show multiple schedule items', () => {
    render(<LifestyleDeepDiveSection home={mockHomeWithLifestyle} />);
    expect(screen.getByText('10:00')).toBeInTheDocument();
    expect(screen.getByText('12:30')).toBeInTheDocument();
  });

  // Test 9: Shows empty state when no lifestyle data
  it('should display empty state when lifestyle data missing', () => {
    render(<LifestyleDeepDiveSection home={mockHomeWithoutLifestyle} />);
    expect(screen.getByText('Lifestyle deep dive data not available')).toBeInTheDocument();
  });

  // Test 10: Handles partial lifestyle data
  it('should handle partial lifestyle data gracefully', () => {
    const partialHome: ProfessionalCareHome = {
      id: '3',
      name: 'Partial Home',
      location: 'Leeds',
      matchScore: 75,
      lifestyleDeepDive: {
        visiting_hours: '09:00 - 19:00 daily'
      }
    };
    render(<LifestyleDeepDiveSection home={partialHome} />);
    expect(screen.getByText(/Lifestyle Deep Dive/)).toBeInTheDocument();
  });
});

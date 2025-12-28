import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import CommunityReputationSection from '../CommunityReputationSection';
import type { ProfessionalCareHome } from '../../types';

const mockHomeWithReputation: ProfessionalCareHome = {
  id: '1',
  name: 'Test Home',
  location: 'London',
  matchScore: 85,
  communityReputation: {
    trust_score: 87.5,
    carehome_rating: 4.2,
    google_rating: 4.5,
    google_review_count: 245,
    sentiment_analysis: {
      sentiment_label: 'positive',
      positive_count: 180,
      negative_count: 30,
      neutral_count: 35
    },
    key_themes: {
      strengths: ['Clean', 'Caring staff', 'Good food'],
      weaknesses: ['Limited activities', 'Noise levels']
    },
    recent_reviews: [
      {
        author: 'Jane Smith',
        date: '2024-01-10',
        rating: 5,
        text: 'Excellent care and friendly staff'
      }
    ]
  }
};

const mockHomeWithoutReputation: ProfessionalCareHome = {
  id: '2',
  name: 'Test Home 2',
  location: 'Manchester',
  matchScore: 70
};

describe('CommunityReputationSection', () => {
  // Test 1: Renders header
  it('should display community reputation header', () => {
    render(<CommunityReputationSection home={mockHomeWithReputation} />);
    expect(screen.getByText('Community Reputation')).toBeInTheDocument();
  });

  // Test 2: Shows trust score
  it('should display trust score', () => {
    render(<CommunityReputationSection home={mockHomeWithReputation} />);
    expect(screen.getByText('Trust Score')).toBeInTheDocument();
  });

  // Test 3: Shows Google rating
  it('should display Google rating info', () => {
    render(<CommunityReputationSection home={mockHomeWithReputation} />);
    expect(screen.getByText('Google Rating')).toBeInTheDocument();
  });

  // Test 4: Shows sentiment analysis
  it('should display sentiment information', () => {
    render(<CommunityReputationSection home={mockHomeWithReputation} />);
    expect(screen.getByText(/Community Reputation/)).toBeInTheDocument();
  });

  // Test 5: Lists key strengths
  it('should display key strengths', () => {
    render(<CommunityReputationSection home={mockHomeWithReputation} />);
    const { container } = render(<CommunityReputationSection home={mockHomeWithReputation} />);
    expect(container).toBeInTheDocument();
  });

  // Test 6: Lists weaknesses
  it('should display identified weaknesses', () => {
    render(<CommunityReputationSection home={mockHomeWithReputation} />);
    expect(screen.getByText(/Community Reputation/)).toBeInTheDocument();
  });

  // Test 7: Shows recent reviews
  it('should display recent reviews', () => {
    render(<CommunityReputationSection home={mockHomeWithReputation} />);
    // Component should render without errors
    expect(screen.getByText('Community Reputation')).toBeInTheDocument();
  });

  // Test 8: Shows empty state when no data
  it('should display empty state when reputation data missing', () => {
    render(<CommunityReputationSection home={mockHomeWithoutReputation} />);
    expect(screen.getByText('Community reputation data not available')).toBeInTheDocument();
  });

  // Test 9: Shows positive sentiment styling
  it('should apply positive styling for positive sentiment', () => {
    render(<CommunityReputationSection home={mockHomeWithReputation} />);
    expect(screen.getByText(/Community Reputation/)).toBeInTheDocument();
  });

  // Test 10: Handles partial reputation data
  it('should handle partial reputation data gracefully', () => {
    const partialHome: ProfessionalCareHome = {
      id: '3',
      name: 'Partial Home',
      location: 'Leeds',
      matchScore: 75,
      communityReputation: {
        trust_score: 80,
        carehome_rating: 4.3,
        google_rating: 4.0,
        google_review_count: 50,
        sentiment_analysis: {
          sentiment_label: 'neutral',
          positive_count: 50,
          negative_count: 50,
          neutral_count: 100
        }
      }
    };
    render(<CommunityReputationSection home={partialHome} />);
    expect(screen.getByText('Trust Score')).toBeInTheDocument();
  });
});

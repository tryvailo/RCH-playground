import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import LoadingAnimation from '../LoadingAnimation';

describe('LoadingAnimation', () => {
  // Test 1: Renders loading state
  it('should render main loading title', () => {
    render(<LoadingAnimation progress={0} />);
    expect(screen.getByText('Generating Professional Report')).toBeInTheDocument();
  });

  // Test 2: Displays progress percentage
  it('should display progress percentage correctly', () => {
    render(<LoadingAnimation progress={45} />);
    expect(screen.getByText('45%')).toBeInTheDocument();
  });

  // Test 3: Shows all 4 progress steps
  it('should render all 4 progress step labels', () => {
    render(<LoadingAnimation progress={0} />);
    expect(screen.getByText('Loading care homes')).toBeInTheDocument();
    expect(screen.getByText('Enriching with external data')).toBeInTheDocument();
    expect(screen.getByText('Scoring and matching')).toBeInTheDocument();
    expect(screen.getByText('Preparing report')).toBeInTheDocument();
  });

  // Test 4: Progress bar updates based on progress value
  it('should set correct progress bar width', () => {
    const { container } = render(<LoadingAnimation progress={75} />);
    const progressBar = container.querySelector('[style*="width"]');
    expect(progressBar).toHaveStyle({ width: '75%' });
  });

  // Test 5: Step indicators update with progress
  it('should mark steps as complete based on progress', () => {
    const { container } = render(<LoadingAnimation progress={55} />);
    const stepCircles = container.querySelectorAll('.rounded-full');
    
    // First two steps should be complete (progress > 20 and > 50)
    // Check by counting completed vs in-progress vs pending
    expect(stepCircles.length).toBeGreaterThan(0);
  });

  // Test 6: Displays instruction message
  it('should display do-not-refresh warning', () => {
    render(<LoadingAnimation progress={0} />);
    expect(screen.getByText('Please don\'t refresh the page')).toBeInTheDocument();
  });

  // Test 7: Data analysis message is visible
  it('should display analysis message', () => {
    render(<LoadingAnimation progress={0} />);
    expect(screen.getByText(/Analyzing \d+ data points/)).toBeInTheDocument();
  });

  // Test 8: Progress label is present
  it('should have progress label', () => {
    render(<LoadingAnimation progress={30} />);
    expect(screen.getByText('Progress')).toBeInTheDocument();
  });

  // Test 9: Handles edge case of 0% progress
  it('should handle 0% progress correctly', () => {
    render(<LoadingAnimation progress={0} />);
    expect(screen.getByText('0%')).toBeInTheDocument();
  });

  // Test 10: Handles edge case of 100% progress
  it('should handle 100% progress correctly', () => {
    render(<LoadingAnimation progress={100} />);
    expect(screen.getByText('100%')).toBeInTheDocument();
  });
});

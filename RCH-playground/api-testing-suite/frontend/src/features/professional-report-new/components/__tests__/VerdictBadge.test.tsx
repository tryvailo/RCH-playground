import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import VerdictBadge, { getVerdictInfo } from '../VerdictBadge';

describe('VerdictBadge', () => {
  // Test 1: Renders with excellent score
  it('should render excellent match verdict for high score', () => {
    render(<VerdictBadge score={90} />);
    expect(screen.getByText('Excellent Match')).toBeInTheDocument();
    expect(screen.getByText('(90%)')).toBeInTheDocument();
  });

  // Test 2: Renders with good score
  it('should render good match verdict for medium-high score', () => {
    render(<VerdictBadge score={75} />);
    expect(screen.getByText('Good Match')).toBeInTheDocument();
    expect(screen.getByText('(75%)')).toBeInTheDocument();
  });

  // Test 3: Renders with fair score
  it('should render fair match verdict for medium score', () => {
    render(<VerdictBadge score={60} />);
    expect(screen.getByText('Fair Match')).toBeInTheDocument();
    expect(screen.getByText('(60%)')).toBeInTheDocument();
  });

  // Test 4: Different sizes render correctly
  it('should apply correct size classes for different sizes', () => {
    const { container: containerSm } = render(<VerdictBadge score={80} size="sm" />);
    const { container: containerLg } = render(<VerdictBadge score={80} size="lg" />);
    
    expect(containerSm.querySelector('[class*="px-3"]')).toBeInTheDocument();
    expect(containerLg.querySelector('[class*="px-6"]')).toBeInTheDocument();
  });

  // Test 5: Hides icon and score when configured
  it('should hide icon and score when showIcon and showScore are false', () => {
    const { container } = render(
      <VerdictBadge score={80} showIcon={false} showScore={false} />
    );
    
    expect(screen.getByText('Good Match')).toBeInTheDocument();
    expect(screen.queryByText('(80%)')).not.toBeInTheDocument();
    // Icon should be hidden - check by structure
    expect(container.querySelectorAll('svg').length).toBe(0);
  });

  // Utility function tests
  describe('getVerdictInfo', () => {
    it('should return excellent verdict for 85+ score', () => {
      const verdict = getVerdictInfo(85);
      expect(verdict.label).toBe('Excellent Match');
      expect(verdict.color).toBe('text-green-800');
    });

    it('should return good verdict for 70-84 score', () => {
      const verdict = getVerdictInfo(70);
      expect(verdict.label).toBe('Good Match');
      expect(verdict.color).toBe('text-blue-800');
    });

    it('should return fair verdict for 50-69 score', () => {
      const verdict = getVerdictInfo(50);
      expect(verdict.label).toBe('Fair Match');
      expect(verdict.color).toBe('text-yellow-800');
    });

    it('should return limited verdict for <50 score', () => {
      const verdict = getVerdictInfo(30);
      expect(verdict.label).toBe('Limited Match');
      expect(verdict.color).toBe('text-orange-800');
    });

    it('should have description for all verdict types', () => {
      const verdicts = [
        getVerdictInfo(85),
        getVerdictInfo(70),
        getVerdictInfo(50),
        getVerdictInfo(30)
      ];
      verdicts.forEach(v => {
        expect(v.description).toBeTruthy();
        expect(v.description.length).toBeGreaterThan(0);
      });
    });
  });
});

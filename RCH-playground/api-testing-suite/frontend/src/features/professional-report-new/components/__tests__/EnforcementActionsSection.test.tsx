import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import EnforcementActionsSection from '../EnforcementActionsSection';
import type { CQCDeepDive } from '../../types';

const mockCQCWithActions: CQCDeepDive = {
  enforcement_actions: [
    {
      type: 'Warning Notice',
      title: 'Staffing Warning',
      description: 'Insufficient staffing levels detected',
      date: '2023-12-01',
      status: 'Active',
      severity: 'high',
      link: 'https://example.com/enforcement/1'
    },
    {
      type: 'Condition',
      title: 'Hygiene Condition',
      description: 'Must maintain hygiene standards',
      date: '2023-11-15',
      status: 'Resolved',
      severity: 'medium',
      link: 'https://example.com/enforcement/2'
    }
  ]
};

const mockCQCNoActions: CQCDeepDive = {};

describe('EnforcementActionsSection', () => {
  // Test 1: Shows positive message when no actions
  it('should display positive message when no enforcement actions', () => {
    render(
      <EnforcementActionsSection 
        cqcData={mockCQCNoActions} 
        homeName="Safe Home" 
      />
    );
    expect(screen.getByText('No Enforcement Actions')).toBeInTheDocument();
    expect(screen.getByText(/no recorded CQC enforcement actions/)).toBeInTheDocument();
  });

  // Test 2: Lists enforcement actions when present
  it('should display enforcement actions list', () => {
    render(
      <EnforcementActionsSection 
        cqcData={mockCQCWithActions} 
        homeName="Test Home" 
      />
    );
    expect(screen.getByText('CQC Enforcement Actions')).toBeInTheDocument();
    expect(screen.getByText('Staffing Warning')).toBeInTheDocument();
    expect(screen.getByText('Hygiene Condition')).toBeInTheDocument();
  });

  // Test 3: Shows action descriptions
  it('should display action descriptions', () => {
    render(
      <EnforcementActionsSection 
        cqcData={mockCQCWithActions} 
        homeName="Test Home" 
      />
    );
    expect(screen.getByText('Insufficient staffing levels detected')).toBeInTheDocument();
    expect(screen.getByText('Must maintain hygiene standards')).toBeInTheDocument();
  });

  // Test 4: Counts active and resolved actions
  it('should count and display active vs resolved actions', () => {
    render(
      <EnforcementActionsSection 
        cqcData={mockCQCWithActions} 
        homeName="Test Home" 
      />
    );
    expect(screen.getByText('1 Active')).toBeInTheDocument();
    expect(screen.getByText('1 Resolved')).toBeInTheDocument();
  });

  // Test 5: Shows severity badges
  it('should display status badges for actions', () => {
    render(
      <EnforcementActionsSection 
        cqcData={mockCQCWithActions} 
        homeName="Test Home" 
      />
    );
    expect(screen.getByText('Active')).toBeInTheDocument();
    expect(screen.getByText('Resolved')).toBeInTheDocument();
  });

  // Test 6: Formats dates correctly
  it('should format dates in GB format', () => {
    render(
      <EnforcementActionsSection 
        cqcData={mockCQCWithActions} 
        homeName="Test Home" 
      />
    );
    // Date should be formatted (exact format depends on locale)
    expect(screen.getByText(/Dec|1 Dec/)).toBeInTheDocument();
  });

  // Test 7: Shows external link icon
  it('should provide external links for actions', () => {
    const { container } = render(
      <EnforcementActionsSection 
        cqcData={mockCQCWithActions} 
        homeName="Test Home" 
      />
    );
    const links = container.querySelectorAll('a[target="_blank"]');
    expect(links.length).toBeGreaterThan(0);
  });

  // Test 8: Handles empty enforcement array
  it('should handle empty enforcement actions array', () => {
    const emptyActionsData: CQCDeepDive = {
      enforcement_actions: []
    };
    render(
      <EnforcementActionsSection 
        cqcData={emptyActionsData} 
        homeName="Safe Home" 
      />
    );
    expect(screen.getByText('No Enforcement Actions')).toBeInTheDocument();
  });

  // Test 9: Shows warning for active actions
  it('should show warning message when active actions exist', () => {
    render(
      <EnforcementActionsSection 
        cqcData={mockCQCWithActions} 
        homeName="Test Home" 
      />
    );
    expect(screen.getByText(/active enforcement actions that require attention/)).toBeInTheDocument();
  });

  // Test 10: Includes informational tooltip
  it('should display explanation of enforcement actions', () => {
    render(
      <EnforcementActionsSection 
        cqcData={mockCQCWithActions} 
        homeName="Test Home" 
      />
    );
    expect(screen.getByText(/What are enforcement actions/)).toBeInTheDocument();
    expect(screen.getByText(/formal regulatory actions/)).toBeInTheDocument();
  });
});

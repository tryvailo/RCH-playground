/**
 * Cypress E2E Tests - Edge Cases
 * Tests boundary conditions and unusual scenarios
 */

describe('Funding Calculator - Edge Cases', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000/funding-calculator');
  });

  it('should handle zero results scenario gracefully', () => {
    // Search with criteria that return no results
    cy.get('[data-testid="postcode-input"]').type('AB99ZZ'); // Valid but rare postcode
    cy.get('[data-testid="beds-input"]').type('500'); // Very high beds
    cy.get('[data-testid="budget-input"]').type('50000'); // Very low budget
    cy.get('[data-testid="submit-button"]').click();

    // Wait and check for no results message
    cy.get('[data-testid="no-results-message"]', { timeout: 30000 })
      .should('be.visible')
      .should('contain', 'No homes found');

    // Should show helpful suggestions
    cy.get('[data-testid="suggestions-panel"]').should('be.visible');
    cy.get('[data-testid="suggestion-item"]').should('have.length.greaterThan', 0);
  });

  it('should handle partial data load with API failure during enrichment', () => {
    // This tests graceful degradation
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('30');
    cy.get('[data-testid="budget-input"]').type('100000');
    cy.get('[data-testid="submit-button"]').click();

    // Wait for partial results
    cy.get('[data-testid="report-container"]', { timeout: 30000 })
      .should('be.visible');

    // Some data should load despite errors
    cy.get('[data-testid="home-card"]').should('have.length.greaterThan', 0);

    // Error notice should appear for failed enrichments
    cy.get('[data-testid="warning-banner"]').should('be.visible');
  });

  it('should handle very high budget values', () => {
    const veryHighBudget = '999999999';

    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="budget-input"]').type(veryHighBudget);
    cy.get('[data-testid="submit-button"]').click();

    // Should process without error
    cy.get('[data-testid="report-container"]', { timeout: 30000 })
      .should('be.visible');

    // Budget display should be readable
    cy.get('[data-testid="budget-display"]')
      .should('be.visible')
      .should('contain', 'Budget');
  });

  it('should handle very low budget values', () => {
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('10');
    cy.get('[data-testid="budget-input"]').type('1');
    cy.get('[data-testid="submit-button"]').click();

    // Should process
    cy.get('[data-testid="report-container"]', { timeout: 30000 })
      .should('be.visible');

    // May show limited results but no error
    cy.get('[data-testid="error-banner"]').should('not.exist');
  });

  it('should handle special characters in postcode', () => {
    cy.get('[data-testid="postcode-input"]').type('SW1A 1AA'); // Space in postcode
    cy.get('[data-testid="beds-input"]').type('30');
    cy.get('[data-testid="budget-input"]').type('100000');

    // Should normalize and accept
    cy.get('[data-testid="submit-button"]').should('not.be.disabled');
  });

  it('should handle maximum bed count', () => {
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('9999');
    cy.get('[data-testid="budget-input"]').type('500000');
    cy.get('[data-testid="submit-button"]').click();

    // Should handle without crashing
    cy.get('[data-testid="report-container"]', { timeout: 30000 })
      .should('exist');
  });

  it('should handle minimum viable input', () => {
    // Just postcode and beds
    cy.get('[data-testid="postcode-input"]').type('M11AA');
    cy.get('[data-testid="beds-input"]').type('1');
    cy.get('[data-testid="budget-input"]').type('10000');
    cy.get('[data-testid="submit-button"]').click();

    // Should process successfully
    cy.get('[data-testid="report-container"]', { timeout: 30000 })
      .should('be.visible');
  });

  it('should handle form submission with Enter key', () => {
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('30');
    cy.get('[data-testid="budget-input"]').type('100000');

    // Submit with Enter key
    cy.get('[data-testid="budget-input"]').type('{enter}');

    // Should submit
    cy.get('[data-testid="loading-spinner"]').should('be.visible');
  });

  it('should handle rapid successive form submissions', () => {
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('30');
    cy.get('[data-testid="budget-input"]').type('100000');

    // Try to click submit multiple times quickly
    cy.get('[data-testid="submit-button"]').click();
    cy.get('[data-testid="submit-button"]').click();
    cy.get('[data-testid="submit-button"]').click();

    // Should only process once (button disabled during processing)
    cy.get('[data-testid="loading-spinner"]').should('be.visible');
  });

  it('should preserve form state when navigation back', () => {
    // Fill form
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('30');
    cy.get('[data-testid="budget-input"]').type('100000');

    // Submit
    cy.get('[data-testid="submit-button"]').click();

    // Wait for report
    cy.get('[data-testid="report-container"]', { timeout: 30000 })
      .should('be.visible');

    // Click back to form
    cy.get('[data-testid="back-to-form-button"]').click();

    // Form values preserved
    cy.get('[data-testid="postcode-input"]').should('have.value', 'SW1A1AA');
  });

  it('should handle whitespace in input fields', () => {
    cy.get('[data-testid="postcode-input"]').type('  SW1A1AA  ');
    cy.get('[data-testid="beds-input"]').type('  30  ');
    cy.get('[data-testid="budget-input"]').type('  100000  ');

    // Should trim and accept
    cy.get('[data-testid="submit-button"]').should('not.be.disabled');
    cy.get('[data-testid="postcode-error"]').should('not.exist');
  });

  it('should handle case-insensitive postcode input', () => {
    cy.get('[data-testid="postcode-input"]').type('sw1a1aa'); // lowercase
    cy.get('[data-testid="beds-input"]').type('30');
    cy.get('[data-testid="budget-input"]').type('100000');
    cy.get('[data-testid="submit-button"]').click();

    // Should accept
    cy.get('[data-testid="loading-spinner"]').should('be.visible');
  });

  it('should handle very long postcode search results display', () => {
    cy.get('[data-testid="postcode-input"]').type('SW1');
    cy.get('[data-testid="beds-input"]').type('20');
    cy.get('[data-testid="budget-input"]').type('100000');
    cy.get('[data-testid="submit-button"]').click();

    // With large area, may get many results
    cy.get('[data-testid="report-container"]', { timeout: 30000 })
      .should('be.visible');

    // Pagination should be present if many results
    cy.get('[data-testid="results-count"]').should('be.visible');
  });

  it('should handle service selection edge cases', () => {
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('30');
    cy.get('[data-testid="budget-input"]').type('100000');

    // Select all services then deselect all
    cy.get('[data-testid="service-nursing"]').click();
    cy.get('[data-testid="service-residential"]').click();
    cy.get('[data-testid="service-nursing"]').click();
    cy.get('[data-testid="service-residential"]').click();

    // Submit with no services selected
    cy.get('[data-testid="submit-button"]').click();

    // Should either work or show clear error
    cy.get('[data-testid="loading-spinner"]').or('[data-testid="services-error"]')
      .should('exist');
  });
});

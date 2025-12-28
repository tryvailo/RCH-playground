/**
 * Cypress E2E Tests - Performance
 * Tests response times and performance metrics
 */

describe('Funding Calculator - Performance', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000/funding-calculator');
  });

  it('should generate report within 15 seconds', () => {
    const maxTime = 15000; // 15 seconds
    const startTime = Date.now();

    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="budget-input"]').type('150000');
    cy.get('[data-testid="submit-button"]').click();

    // Wait for report to fully load
    cy.get('[data-testid="report-container"]', { timeout: 30000 })
      .should('be.visible')
      .then(() => {
        const elapsed = Date.now() - startTime;
        expect(elapsed).to.be.lessThan(maxTime);
        cy.log(`Report generated in ${elapsed}ms`);
      });
  });

  it('should achieve API response time under 500ms', () => {
    cy.intercept('POST', '**/api/**', (req) => {
      const startTime = Date.now();
      req.reply((res) => {
        const elapsed = Date.now() - startTime;
        expect(elapsed).to.be.lessThan(500);
      });
    });

    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="budget-input"]').type('150000');
    cy.get('[data-testid="submit-button"]').click();

    // Verify API response time
    cy.get('[data-testid="api-timing"]').should('exist');
  });

  it('should maintain UI responsiveness during loading', () => {
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="budget-input"]').type('150000');
    cy.get('[data-testid="submit-button"]').click();

    // During loading, UI elements should respond
    cy.get('[data-testid="loading-spinner"]').should('be.visible');

    // Progress indicator should update
    cy.get('[data-testid="progress-indicator"]')
      .should('be.visible');
  });

  it('should load form within 2 seconds', () => {
    const startTime = Date.now();

    cy.visit('http://localhost:3000/funding-calculator');

    cy.get('[data-testid="questionnaire-form"]', { timeout: 5000 })
      .should('exist')
      .then(() => {
        const elapsed = Date.now() - startTime;
        expect(elapsed).to.be.lessThan(2000);
        cy.log(`Form loaded in ${elapsed}ms`);
      });
  });

  it('should render large result sets without lag', () => {
    cy.get('[data-testid="postcode-input"]').type('SW1'); // Broader search
    cy.get('[data-testid="beds-input"]').type('20');
    cy.get('[data-testid="budget-input"]').type('200000');
    cy.get('[data-testid="submit-button"]').click();

    // Wait for results
    cy.get('[data-testid="report-container"]', { timeout: 30000 })
      .should('be.visible');

    // All home cards should render without visible lag
    cy.get('[data-testid="home-card"]').each(($el, index) => {
      cy.wrap($el).should('be.visible');
    });
  });

  it('should handle pagination smoothly', () => {
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('30');
    cy.get('[data-testid="budget-input"]').type('100000');
    cy.get('[data-testid="submit-button"]').click();

    cy.get('[data-testid="pagination"]', { timeout: 30000 })
      .should('be.visible');

    // Measure page navigation time
    const startTime = Date.now();
    cy.get('[data-testid="next-page-button"]').click();

    cy.get('[data-testid="home-card"]')
      .should('have.length.greaterThan', 0)
      .then(() => {
        const elapsed = Date.now() - startTime;
        expect(elapsed).to.be.lessThan(2000); // Should be fast
      });
  });

  it('should cache results for instant re-rendering', () => {
    // First submission
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="budget-input"]').type('150000');
    cy.get('[data-testid="submit-button"]').click();

    cy.get('[data-testid="report-container"]', { timeout: 30000 })
      .should('be.visible');

    // Go back and resubmit same query
    cy.get('[data-testid="new-search-button"]').click();

    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="budget-input"]').type('150000');

    // Second submission should be faster
    const startTime = Date.now();
    cy.get('[data-testid="submit-button"]').click();

    cy.get('[data-testid="report-container"]')
      .should('be.visible')
      .then(() => {
        const elapsed = Date.now() - startTime;
        cy.log(`Cached query executed in ${elapsed}ms`);
        // Cached should be significantly faster
        expect(elapsed).to.be.lessThan(3000);
      });
  });

  it('should display metrics on report', () => {
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="budget-input"]').type('150000');
    cy.get('[data-testid="submit-button"]').click();

    cy.get('[data-testid="report-container"]', { timeout: 30000 })
      .should('be.visible');

    // Verify performance metrics displayed
    cy.get('[data-testid="generation-time"]').should('be.visible');
    cy.get('[data-testid="api-response-time"]').should('be.visible');
  });
});

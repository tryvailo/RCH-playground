/**
 * Cypress E2E Tests - Happy Path Scenarios
 * Tests complete successful workflows for funding calculator
 */

describe('Funding Calculator - Happy Path', () => {
  const API_BASE = Cypress.env('API_BASE') || 'http://localhost:8000';

  beforeEach(() => {
    cy.visit('http://localhost:3000/funding-calculator');
    cy.get('[data-testid="form-title"]').should('be.visible');
  });

  it('should load questionnaire form with all fields', () => {
    // Verify form is rendered
    cy.get('[data-testid="questionnaire-form"]').should('exist');
    
    // Verify all input fields present
    cy.get('[data-testid="postcode-input"]').should('be.visible');
    cy.get('[data-testid="beds-input"]').should('be.visible');
    cy.get('[data-testid="budget-input"]').should('be.visible');
    cy.get('[data-testid="services-select"]').should('be.visible');
    
    // Verify submit button present and enabled
    cy.get('[data-testid="submit-button"]').should('be.visible');
    cy.get('[data-testid="submit-button"]').should('not.be.disabled');
  });

  it('should accept valid postcode input', () => {
    cy.get('[data-testid="postcode-input"]')
      .type('SW1A1AA')
      .should('have.value', 'SW1A1AA');
    
    // Verify no validation error
    cy.get('[data-testid="postcode-error"]').should('not.exist');
  });

  it('should fill all form fields completely', () => {
    const formData = {
      postcode: 'SW1A1AA',
      beds: '50',
      budget: '150000',
      services: ['nursing', 'residential']
    };

    // Fill postcode
    cy.get('[data-testid="postcode-input"]')
      .type(formData.postcode)
      .should('have.value', formData.postcode);

    // Fill beds
    cy.get('[data-testid="beds-input"]')
      .type(formData.beds)
      .should('have.value', formData.beds);

    // Fill budget
    cy.get('[data-testid="budget-input"]')
      .type(formData.budget)
      .should('have.value', formData.budget);

    // Select services
    formData.services.forEach(service => {
      cy.get(`[data-testid="service-${service}"]`).click();
    });

    // Verify all fields filled
    cy.get('[data-testid="submit-button"]').should('be.enabled');
  });

  it('should submit form and show loading animation', () => {
    // Fill form
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="budget-input"]').type('150000');

    // Submit
    cy.get('[data-testid="submit-button"]').click();

    // Verify loading state
    cy.get('[data-testid="loading-spinner"]').should('be.visible');
    cy.get('[data-testid="loading-text"]').should('contain', 'Processing');

    // Wait for completion
    cy.get('[data-testid="loading-spinner"]', { timeout: 30000 })
      .should('not.exist');
  });

  it('should display complete report with all sections', () => {
    // Fill and submit form
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="budget-input"]').type('150000');
    cy.get('[data-testid="submit-button"]').click();

    // Wait for report to load
    cy.get('[data-testid="report-container"]', { timeout: 30000 })
      .should('be.visible');

    // Verify all report sections exist
    cy.get('[data-testid="matches-section"]').should('be.visible');
    cy.get('[data-testid="cqc-analysis-section"]').should('be.visible');
    cy.get('[data-testid="funding-section"]').should('be.visible');
    cy.get('[data-testid="neighbourhood-section"]').should('be.visible');
    cy.get('[data-testid="cost-analysis-section"]').should('be.visible');

    // Verify report content
    cy.get('[data-testid="report-title"]').should('contain', 'Results');
    cy.get('[data-testid="results-count"]').should('be.visible');
  });

  it('should display matched homes with details', () => {
    // Submit form
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="budget-input"]').type('150000');
    cy.get('[data-testid="submit-button"]').click();

    // Wait for results
    cy.get('[data-testid="home-card"]', { timeout: 30000 })
      .should('have.length.greaterThan', 0);

    // Verify home card content
    cy.get('[data-testid="home-card"]').first().within(() => {
      cy.get('[data-testid="home-name"]').should('be.visible');
      cy.get('[data-testid="home-rating"]').should('be.visible');
      cy.get('[data-testid="match-score"]').should('be.visible');
    });
  });

  it('should navigate between pages in paginated results', () => {
    // Submit form with results
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="budget-input"]').type('150000');
    cy.get('[data-testid="submit-button"]').click();

    // Wait for results
    cy.get('[data-testid="pagination"]', { timeout: 30000 })
      .should('be.visible');

    // Click next page
    cy.get('[data-testid="next-page-button"]').click();

    // Verify content changed
    cy.get('[data-testid="home-card"]').should('have.length.greaterThan', 0);
  });

  it('should show detailed info on home card click', () => {
    // Submit form
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="budget-input"]').type('150000');
    cy.get('[data-testid="submit-button"]').click();

    // Wait for results and click a home
    cy.get('[data-testid="home-card"]', { timeout: 30000 })
      .first()
      .click();

    // Verify detail modal/panel appears
    cy.get('[data-testid="home-details-panel"]').should('be.visible');
    cy.get('[data-testid="home-full-details"]').should('be.visible');
  });

  it('should allow form reset to submit new query', () => {
    // Fill initial form
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="submit-button"]').click();

    // Wait for results
    cy.get('[data-testid="report-container"]', { timeout: 30000 })
      .should('be.visible');

    // Click new search
    cy.get('[data-testid="new-search-button"]').click();

    // Verify form reset
    cy.get('[data-testid="postcode-input"]').should('have.value', '');
    cy.get('[data-testid="beds-input"]').should('have.value', '');
  });
});

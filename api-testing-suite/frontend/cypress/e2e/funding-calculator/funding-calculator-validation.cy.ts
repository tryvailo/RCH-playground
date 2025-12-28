/**
 * Cypress E2E Tests - Validation Scenarios
 * Tests form validation and error handling
 */

describe('Funding Calculator - Validation', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000/funding-calculator');
  });

  it('should show error for empty form submission', () => {
    // Try to submit empty form
    cy.get('[data-testid="submit-button"]').click();

    // Verify validation errors appear
    cy.get('[data-testid="postcode-error"]').should('be.visible');
    cy.get('[data-testid="beds-error"]').should('be.visible');
    cy.get('[data-testid="error-summary"]').should('be.visible');
  });

  it('should validate postcode format', () => {
    const invalidPostcodes = ['INVALID', '123', '!@#$'];

    invalidPostcodes.forEach(postcode => {
      cy.get('[data-testid="postcode-input"]').clear();
      cy.get('[data-testid="postcode-input"]').type(postcode);
      cy.get('[data-testid="submit-button"]').click();

      cy.get('[data-testid="postcode-error"]').should('be.visible');
      cy.get('[data-testid="postcode-error"]').should('contain', 'valid');
    });
  });

  it('should reject invalid postcode with clear message', () => {
    cy.get('[data-testid="postcode-input"]').type('INVALID123');
    cy.get('[data-testid="submit-button"]').click();

    cy.get('[data-testid="postcode-error"]')
      .should('be.visible')
      .should('contain', 'valid UK postcode');
  });

  it('should highlight all required fields', () => {
    cy.get('[data-testid="submit-button"]').click();

    // All required fields should show errors
    cy.get('[data-testid="postcode-input"]')
      .parent()
      .should('have.class', 'error');

    cy.get('[data-testid="beds-input"]')
      .parent()
      .should('have.class', 'error');

    cy.get('[data-testid="budget-input"]')
      .parent()
      .should('have.class', 'error');
  });

  it('should show field-level error messages', () => {
    // Empty postcode
    cy.get('[data-testid="postcode-input"]').focus().blur();
    cy.get('[data-testid="postcode-error"]').should('be.visible');
    cy.get('[data-testid="postcode-error"]').should('contain', 'required');

    // Invalid budget
    cy.get('[data-testid="budget-input"]').type('-1000');
    cy.get('[data-testid="budget-input"]').blur();
    cy.get('[data-testid="budget-error"]').should('be.visible');
    cy.get('[data-testid="budget-error"]').should('contain', 'positive');
  });

  it('should display error summary at top of form', () => {
    cy.get('[data-testid="submit-button"]').click();

    cy.get('[data-testid="error-summary"]')
      .should('be.visible')
      .within(() => {
        cy.get('[data-testid="error-item"]').should('have.length.greaterThan', 0);
      });
  });

  it('should validate numeric fields', () => {
    cy.get('[data-testid="beds-input"]').type('abc');
    cy.get('[data-testid="submit-button"]').click();
    cy.get('[data-testid="beds-error"]').should('be.visible');

    cy.get('[data-testid="budget-input"]').type('xyz');
    cy.get('[data-testid="budget-error"]').should('be.visible');
  });

  it('should reject negative bed counts', () => {
    cy.get('[data-testid="beds-input"]').type('-10');
    cy.get('[data-testid="submit-button"]').click();
    cy.get('[data-testid="beds-error"]').should('be.visible');
  });

  it('should reject zero budget', () => {
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('30');
    cy.get('[data-testid="budget-input"]').type('0');
    cy.get('[data-testid="submit-button"]').click();

    cy.get('[data-testid="budget-error"]')
      .should('be.visible')
      .should('contain', 'greater than 0');
  });

  it('should clear errors when valid input provided', () => {
    // Show error
    cy.get('[data-testid="submit-button"]').click();
    cy.get('[data-testid="postcode-error"]').should('be.visible');

    // Provide valid input
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="postcode-input"]').blur();

    // Error should clear
    cy.get('[data-testid="postcode-error"]').should('not.exist');
  });

  it('should enable submit button only when valid', () => {
    // Initially disabled
    cy.get('[data-testid="submit-button"]').should('be.disabled');

    // Fill partial form
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="submit-button"]').should('be.disabled');

    // Fill all required fields
    cy.get('[data-testid="beds-input"]').type('30');
    cy.get('[data-testid="budget-input"]').type('100000');

    // Button enabled
    cy.get('[data-testid="submit-button"]').should('not.be.disabled');
  });

  it('should validate on blur for better UX', () => {
    // Invalid postcode
    cy.get('[data-testid="postcode-input"]').type('INVALID');
    cy.get('[data-testid="postcode-input"]').blur();

    // Error shows immediately
    cy.get('[data-testid="postcode-error"]').should('be.visible');
  });

  it('should show real-time validation feedback', () => {
    cy.get('[data-testid="postcode-input"]').type('S');
    // Should not show error yet
    cy.get('[data-testid="postcode-error"]').should('not.exist');

    cy.get('[data-testid="postcode-input"]').type('W1A1AA');
    // Now check postcode
    cy.get('[data-testid="postcode-input"]').blur();
  });
});

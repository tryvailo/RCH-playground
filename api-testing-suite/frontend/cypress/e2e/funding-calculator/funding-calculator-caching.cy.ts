/**
 * Cypress E2E Tests - Caching Behavior
 * Tests cache functionality and efficiency
 */

describe('Funding Calculator - Caching', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000/funding-calculator');
  });

  it('should load same questionnaire faster second time', () => {
    const timings = { first: 0, second: 0 };

    // First submission - no cache
    let start = Date.now();
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="budget-input"]').type('150000');
    cy.get('[data-testid="submit-button"]').click();

    cy.get('[data-testid="report-container"]', { timeout: 30000 })
      .should('be.visible')
      .then(() => {
        timings.first = Date.now() - start;
        cy.log(`First submission: ${timings.first}ms`);
      });

    // Go back to form
    cy.get('[data-testid="new-search-button"]').click();

    // Second submission - with cache
    start = Date.now();
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="budget-input"]').type('150000');
    cy.get('[data-testid="submit-button"]').click();

    cy.get('[data-testid="report-container"]')
      .should('be.visible')
      .then(() => {
        timings.second = Date.now() - start;
        cy.log(`Second submission: ${timings.second}ms`);
        // Second should be significantly faster
        expect(timings.second).to.be.lessThan(timings.first);
      });
  });

  it('should invalidate cache on data changes', () => {
    // First query
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="budget-input"]').type('150000');
    cy.get('[data-testid="submit-button"]').click();

    cy.get('[data-testid="report-container"]', { timeout: 30000 })
      .should('be.visible');

    // Store first results
    cy.get('[data-testid="home-card"]').then(($cards) => {
      const firstCount = $cards.length;

      // Go back and modify query
      cy.get('[data-testid="new-search-button"]').click();

      cy.get('[data-testid="postcode-input"]').type('M11AA'); // Different postcode
      cy.get('[data-testid="beds-input"]').type('30');
      cy.get('[data-testid="budget-input"]').type('100000');
      cy.get('[data-testid="submit-button"]').click();

      // Results should be different (cache invalidated)
      cy.get('[data-testid="report-container"]', { timeout: 30000 })
        .should('be.visible');

      cy.get('[data-testid="home-card"]').then(($newCards) => {
        // Result sets should be different
        expect($newCards.length).to.not.equal(firstCount);
      });
    });
  });

  it('should clear old cache after 24 hours', () => {
    // This test verifies cache expiration logic
    // Create old cache entry
    const oldTime = new Date();
    oldTime.setHours(oldTime.getHours() - 25); // 25 hours ago

    // Write to localStorage
    const cacheKey = 'funding_calc_cache_SW1A1AA_50_150000';
    const cacheData = {
      timestamp: oldTime.getTime(),
      homes: [1, 2, 3]
    };
    cy.window().then((win) => {
      win.localStorage.setItem(cacheKey, JSON.stringify(cacheData));
    });

    // Query same params
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="budget-input"]').type('150000');
    cy.get('[data-testid="submit-button"]').click();

    // Should fetch fresh data (old cache cleared)
    cy.get('[data-testid="report-container"]', { timeout: 30000 })
      .should('be.visible');

    // Verify old cache was cleared
    cy.window().then((win) => {
      const stored = win.localStorage.getItem(cacheKey);
      const data = JSON.parse(stored);
      // New timestamp should be recent
      expect(Date.now() - data.timestamp).to.be.lessThan(30000);
    });
  });

  it('should persist cache across page reloads', () => {
    // First submission
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="budget-input"]').type('150000');
    cy.get('[data-testid="submit-button"]').click();

    cy.get('[data-testid="report-container"]', { timeout: 30000 })
      .should('be.visible');

    // Get home count
    cy.get('[data-testid="home-card"]').then(($cards) => {
      const firstCount = $cards.length;

      // Reload page
      cy.reload();

      // Submit same query
      cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
      cy.get('[data-testid="beds-input"]').type('50');
      cy.get('[data-testid="budget-input"]').type('150000');
      cy.get('[data-testid="submit-button"]').click();

      // Results should be loaded from cache (same count)
      cy.get('[data-testid="report-container"]', { timeout: 30000 })
        .should('be.visible');

      cy.get('[data-testid="home-card"]').then(($reloadCards) => {
        expect($reloadCards.length).to.equal(firstCount);
      });
    });
  });

  it('should show cache indicator when using cached data', () => {
    // First submission
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="budget-input"]').type('150000');
    cy.get('[data-testid="submit-button"]').click();

    cy.get('[data-testid="report-container"]', { timeout: 30000 })
      .should('be.visible');

    // Should not show cache indicator first time
    cy.get('[data-testid="cache-indicator"]').should('not.exist');

    // Go back and resubmit
    cy.get('[data-testid="new-search-button"]').click();

    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="budget-input"]').type('150000');
    cy.get('[data-testid="submit-button"]').click();

    // Should show cache indicator second time
    cy.get('[data-testid="cache-indicator"]', { timeout: 5000 })
      .should('be.visible')
      .should('contain', 'Cached');
  });

  it('should allow manual cache clear', () => {
    // First submission to cache data
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="budget-input"]').type('150000');
    cy.get('[data-testid="submit-button"]').click();

    cy.get('[data-testid="report-container"]', { timeout: 30000 })
      .should('be.visible');

    // Clear cache via menu/button
    cy.get('[data-testid="clear-cache-button"]').click();

    // Confirm dialog
    cy.get('[data-testid="confirm-clear"]').click();

    // Go back and resubmit same query
    cy.get('[data-testid="new-search-button"]').click();

    const startTime = Date.now();
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="budget-input"]').type('150000');
    cy.get('[data-testid="submit-button"]').click();

    cy.get('[data-testid="report-container"]')
      .should('be.visible')
      .then(() => {
        // Should take longer without cache
        const elapsed = Date.now() - startTime;
        cy.log(`Query after cache clear: ${elapsed}ms`);
      });

    // Cache indicator should not appear
    cy.get('[data-testid="cache-indicator"]').should('not.exist');
  });

  it('should handle cache corruption gracefully', () => {
    // Write corrupted cache data
    cy.window().then((win) => {
      win.localStorage.setItem(
        'funding_calc_cache_SW1A1AA_50_150000',
        'invalid json {{'
      );
    });

    // Submit query
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="budget-input"]').type('150000');
    cy.get('[data-testid="submit-button"]').click();

    // Should recover and fetch fresh data
    cy.get('[data-testid="report-container"]', { timeout: 30000 })
      .should('be.visible');

    // Should not show cache indicator
    cy.get('[data-testid="cache-indicator"]').should('not.exist');
  });

  it('should cache different query variations separately', () => {
    // Query 1
    cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
    cy.get('[data-testid="beds-input"]').type('50');
    cy.get('[data-testid="budget-input"]').type('150000');
    cy.get('[data-testid="submit-button"]').click();

    cy.get('[data-testid="report-container"]', { timeout: 30000 })
      .should('be.visible');

    cy.get('[data-testid="home-card"]').then(($cards1) => {
      const count1 = $cards1.length;

      // Go back
      cy.get('[data-testid="new-search-button"]').click();

      // Query 2 - different postcode
      cy.get('[data-testid="postcode-input"]').type('M11AA');
      cy.get('[data-testid="beds-input"]').type('50');
      cy.get('[data-testid="budget-input"]').type('150000');
      cy.get('[data-testid="submit-button"]').click();

      cy.get('[data-testid="report-container"]', { timeout: 30000 })
        .should('be.visible');

      cy.get('[data-testid="home-card"]').then(($cards2) => {
        const count2 = $cards2.length;

        // Results should differ
        expect(count2).to.not.equal(count1);

        // Go back
        cy.get('[data-testid="new-search-button"]').click();

        // Resubmit Query 1
        cy.get('[data-testid="postcode-input"]').type('SW1A1AA');
        cy.get('[data-testid="beds-input"]').type('50');
        cy.get('[data-testid="budget-input"]').type('150000');
        cy.get('[data-testid="submit-button"]').click();

        // Should get same results as first time (cached)
        cy.get('[data-testid="report-container"]', { timeout: 30000 })
          .should('be.visible');

        cy.get('[data-testid="home-card"]').then(($cards3) => {
          expect($cards3.length).to.equal(count1);
        });
      });
    });
  });
});

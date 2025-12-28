// Learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom'

/**
 * Mock feature flags for testing
 * Enables all enrichment services in test environment
 */
jest.mock('@/lib/shared/config/feature-flags', () => ({
  getFeatureFlags: () => ({
    enrichmentFSA: true,
    enrichmentFinancial: true,
    enrichmentGooglePlaces: true,
    enrichmentStaff: true,
    enrichmentCQC: true,
    enrichmentNeighbourhood: true,
    // Add other flags as needed
    enableFinancialEnrichment: true,
    enableStaffEnrichment: true,
    enableFSAEnrichment: true,
    enableGooglePlacesEnrichment: true,
  }),
  getFlags: () => ({
    enableFinancialEnrichment: true,
    enableStaffEnrichment: true,
    enableFSAEnrichment: true,
    enableGooglePlacesEnrichment: true,
  }),
}))

/**
 * Suppress console errors in tests (optional, for cleaner output)
 */
const originalError = console.error
beforeAll(() => {
  console.error = jest.fn((...args) => {
    // Allow expected errors through
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('Warning:') || args[0].includes('Error:'))
    ) {
      originalError.call(console, ...args)
    }
  })
})

afterAll(() => {
  console.error = originalError
})




/**
 * Shared utility functions for score and rating color styling
 * Used across multiple features: neighbourhood, free-report, professional-report, etc.
 */

/**
 * Get Tailwind CSS classes for score-based backgrounds
 * @param score - Score value (0-100) or undefined
 * @returns Tailwind CSS class string for background and text color
 */
export function getScoreColor(score: number | undefined): string {
  if (score === undefined) return 'bg-gray-100 text-gray-600';
  if (score >= 75) return 'bg-green-100 text-green-800';
  if (score >= 60) return 'bg-blue-100 text-blue-800';
  if (score >= 45) return 'bg-yellow-100 text-yellow-800';
  return 'bg-red-100 text-red-800';
}

/**
 * Get Tailwind CSS text color class for rating strings
 * @param rating - Rating string (e.g., "Excellent", "Good", "Average", etc.)
 * @returns Tailwind CSS class string for text color
 */
export function getRatingColor(rating: string | undefined): string {
  if (!rating) return 'text-gray-600';
  const lower = rating.toLowerCase();
  if (lower.includes('excellent') || lower.includes('very good') || lower.includes('outstanding')) {
    return 'text-green-600';
  }
  if (lower.includes('good')) return 'text-blue-600';
  if (lower.includes('average') || lower.includes('moderate') || lower.includes('adequate')) {
    return 'text-yellow-600';
  }
  return 'text-red-600';
}

/**
 * Get numeric score color for charts and visualizations
 * @param score - Score value (0-100)
 * @returns Hex color string
 */
export function getScoreHexColor(score: number | undefined): string {
  if (score === undefined) return '#9CA3AF'; // gray-400
  if (score >= 75) return '#10B981'; // green-500
  if (score >= 60) return '#3B82F6'; // blue-500
  if (score >= 45) return '#F59E0B'; // yellow-500
  return '#EF4444'; // red-500
}

/**
 * Get CQC rating color
 * @param rating - CQC rating string
 * @returns Tailwind CSS class string for text color
 */
export function getCQCRatingColor(rating: string | undefined): string {
  if (!rating) return 'text-gray-600';
  const lower = rating.toLowerCase();
  switch (lower) {
    case 'outstanding':
      return 'text-green-600';
    case 'good':
      return 'text-blue-600';
    case 'requires improvement':
      return 'text-yellow-600';
    case 'inadequate':
      return 'text-red-600';
    default:
      return 'text-gray-600';
  }
}

/**
 * Get FSA rating color (1-5 scale)
 * @param rating - FSA rating value (1-5)
 * @returns Tailwind CSS class string for text color
 */
export function getFSARatingColor(rating: number | null | undefined): string {
  if (rating === null || rating === undefined) return 'text-gray-500';
  if (rating === 5) return 'text-green-600';
  if (rating === 4) return 'text-green-500';
  if (rating === 3) return 'text-yellow-500';
  if (rating === 2) return 'text-orange-500';
  if (rating === 1) return 'text-red-500';
  return 'text-red-600';
}

/**
 * Get progress bar color based on percentage
 * @param percent - Percentage value (0-100)
 * @returns Tailwind CSS class string for background color
 */
export function getProgressColor(percent: number): string {
  if (percent >= 75) return 'bg-green-500';
  if (percent >= 60) return 'bg-blue-500';
  if (percent >= 45) return 'bg-yellow-500';
  return 'bg-red-500';
}

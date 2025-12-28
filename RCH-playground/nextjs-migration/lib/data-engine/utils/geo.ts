/**
 * Geographic Utilities
 * Ported from Python utils/geo.py
 */

/**
 * Calculate distance between two points using Haversine formula
 * 
 * @param lat1 Latitude of first point (degrees)
 * @param lon1 Longitude of first point (degrees)
 * @param lat2 Latitude of second point (degrees)
 * @param lon2 Longitude of second point (degrees)
 * @returns Distance in kilometers (rounded to 2 decimal places)
 * @throws Error if coordinates are invalid
 */
export function calculateDistanceKm(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  // Validate coordinates
  if (!(-90 <= lat1 && lat1 <= 90) || !(-90 <= lat2 && lat2 <= 90)) {
    throw new Error('Invalid latitude: must be between -90 and 90');
  }
  if (!(-180 <= lon1 && lon1 <= 180) || !(-180 <= lon2 && lon2 <= 180)) {
    throw new Error('Invalid longitude: must be between -180 and 180');
  }

  // Earth radius in kilometers
  const R = 6371.0;

  // Convert degrees to radians
  const dLat = toRadians(lat2 - lat1);
  const dLon = toRadians(lon2 - lon1);

  // Haversine formula
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRadians(lat1)) *
      Math.cos(toRadians(lat2)) *
      Math.sin(dLon / 2) ** 2;

  const c = 2 * Math.asin(Math.sqrt(a));
  const distance = R * c;

  return Math.round(distance * 100) / 100; // Round to 2 decimal places
}

/**
 * Calculate distance between two points in miles
 * 
 * @param lat1 Latitude of first point (degrees)
 * @param lon1 Longitude of first point (degrees)
 * @param lat2 Latitude of second point (degrees)
 * @param lon2 Longitude of second point (degrees)
 * @returns Distance in miles (rounded to 2 decimal places)
 */
export function calculateDistanceMiles(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const distanceKm = calculateDistanceKm(lat1, lon1, lat2, lon2);
  return Math.round(distanceKm * 0.621371 * 100) / 100;
}

/**
 * Validate that coordinates are valid
 * 
 * @param lat Latitude (degrees)
 * @param lon Longitude (degrees)
 * @returns True if coordinates are valid, False otherwise
 */
export function validateCoordinates(
  lat: number | null | undefined,
  lon: number | null | undefined
): boolean {
  if (lat === null || lat === undefined || lon === null || lon === undefined) {
    return false;
  }

  try {
    return -90 <= lat && lat <= 90 && -180 <= lon && lon <= 180;
  } catch {
    return false;
  }
}

/**
 * Convert degrees to radians
 */
function toRadians(degrees: number): number {
  return degrees * (Math.PI / 180);
}




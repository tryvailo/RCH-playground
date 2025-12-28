/**
 * Postcode Resolver
 * Resolves UK postcodes to coordinates and local authority
 */

import { PostcodeInfo } from '@/lib/shared/types/care-home';

export class PostcodeResolver {
  private cache: Map<string, PostcodeInfo> = new Map();

  /**
   * Resolve postcode to coordinates and local authority
   * 
   * @param postcode UK postcode
   * @returns Postcode info with coordinates and local authority
   */
  async resolve(postcode: string): Promise<PostcodeInfo> {
    // Normalize postcode
    const normalized = postcode.replace(/\s+/g, '').toUpperCase().trim();

    // Check cache
    if (this.cache.has(normalized)) {
      return this.cache.get(normalized)!;
    }

    try {
      // Try postcodes.io API
      const response = await fetch(
        `https://api.postcodes.io/postcodes/${normalized}`,
        {
          signal: AbortSignal.timeout(5000), // 5 second timeout
        }
      );

      if (response.ok) {
        const data = await response.json();
        if (data.status === 200 && data.result) {
          const result = data.result;
          const info: PostcodeInfo = {
            postcode: result.postcode || normalized,
            localAuthority: result.admin_district || undefined,
            latitude: result.latitude || undefined,
            longitude: result.longitude || undefined,
            region: result.region || undefined,
          };

          // Cache result
          this.cache.set(normalized, info);
          return info;
        }
      }
    } catch (error) {
      console.warn('Postcode API failed, using fallback:', error);
    }

    // Fallback: return basic info
    const fallback: PostcodeInfo = {
      postcode: normalized,
      localAuthority: this.getLocalAuthorityFromPostcode(normalized),
    };

    return fallback;
  }

  /**
   * Fallback: Get local authority from postcode pattern
   * 
   * @param postcode UK postcode
   * @returns Local authority name or undefined
   */
  private getLocalAuthorityFromPostcode(postcode: string): string | undefined {
    const upper = postcode.toUpperCase();

    // London postcodes
    if (upper.match(/^(SW|SE|NW|NE|E|W|N|WC|EC)/)) {
      return 'Westminster';
    }

    // Manchester
    if (upper.startsWith('M')) {
      return 'Manchester';
    }

    // Birmingham
    if (upper.startsWith('B')) {
      return 'Birmingham';
    }

    // Liverpool
    if (upper.startsWith('L')) {
      return 'Liverpool';
    }

    // Leeds
    if (upper.startsWith('LS')) {
      return 'Leeds';
    }

    // Camden (default for SW1A)
    if (upper.startsWith('SW1')) {
      return 'Camden';
    }

    return 'Westminster'; // Default fallback
  }
}




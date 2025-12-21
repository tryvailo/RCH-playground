/**
 * LocalAuthorityCard - Display identified local authority info
 * 
 * Shows:
 * - LA name (determined from postcode/location)
 * - Contact information
 * - Next steps for citizen
 * - Links to LA resources
 */

import React from 'react';
import { MapPin, Phone, Mail, ExternalLink } from 'lucide-react';
import { FundingEligibilityResult } from '../../types/funding.types';
import { ResultCard } from '../Common/ResultCard';

interface LocalAuthorityCardProps {
  result: FundingEligibilityResult;
  className?: string;
}

export function LocalAuthorityCard({
  result,
  className = '',
}: LocalAuthorityCardProps) {
  // Note: In real implementation, would look up LA from postcode
  const localAuthority = {
    name: 'Example Local Authority',
    phone: '0121 303 1234',
    email: 'chc@example.gov.uk',
    website: 'https://example.gov.uk',
  };

  return (
    <ResultCard
      title="Contact Local Authority"
      icon={<MapPin className="w-5 h-5 text-purple-600" />}
      className={className}
    >
      <div className="space-y-3">
        <div>
          <p className="text-xs text-gray-600">Local Authority</p>
          <p className="font-semibold text-gray-900">{localAuthority.name}</p>
        </div>

        <div className="space-y-2 text-xs">
          <a
            href={`tel:${localAuthority.phone}`}
            className="flex items-center gap-2 text-blue-600 hover:text-blue-800"
          >
            <Phone className="w-4 h-4" />
            {localAuthority.phone}
          </a>

          <a
            href={`mailto:${localAuthority.email}`}
            className="flex items-center gap-2 text-blue-600 hover:text-blue-800"
          >
            <Mail className="w-4 h-4" />
            {localAuthority.email}
          </a>

          <a
            href={localAuthority.website}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-blue-600 hover:text-blue-800"
          >
            <ExternalLink className="w-4 h-4" />
            Visit LA Website
          </a>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded p-2 text-xs text-blue-700">
          <p className="font-medium mb-1">Next Steps:</p>
          <ul className="space-y-1 ml-3">
            <li>• Contact LA with assessment results</li>
            <li>• Request full needs assessment if eligible</li>
            <li>• Discuss funding options and care plan</li>
          </ul>
        </div>
      </div>
    </ResultCard>
  );
}

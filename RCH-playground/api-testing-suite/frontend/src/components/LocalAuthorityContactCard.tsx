import React from 'react';
import { MapPin, Phone, Mail, Globe, Clock, AlertCircle, ExternalLink, Copy, CheckCircle2 } from 'lucide-react';
import { useState } from 'react';

interface LocalAuthorityContact {
  council_name: string;
  region?: string;
  authority_type?: string;
  asc_phone?: string | null;
  asc_email?: string | null;
  asc_website_url?: string | null;
  assessment_url?: string | null;
  office_address?: string | null;
  opening_hours?: string | null;
  emergency_phone?: string | null;
  note?: string;
}

interface LocalAuthorityContactCardProps {
  contact: LocalAuthorityContact;
  postcode?: string;
}

export default function LocalAuthorityContactCard({ contact, postcode }: LocalAuthorityContactCardProps) {
  const [copied, setCopied] = useState<string | null>(null);

  const copyToClipboard = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(type);
      setTimeout(() => setCopied(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const formatPhone = (phone: string | null | undefined): string | null => {
    if (!phone) return null;
    return phone.trim();
  };

  const formatEmail = (email: string | null | undefined): string | null => {
    if (!email) return null;
    return email.trim();
  };

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-2">
          <MapPin className="w-5 h-5 text-blue-600" />
          <h3 className="text-xl font-bold text-gray-900">
            {contact.council_name}
          </h3>
        </div>
        {contact.note && (
          <div className="flex items-center gap-1 text-xs text-yellow-600 bg-yellow-50 px-2 py-1 rounded">
            <AlertCircle className="w-3 h-3" />
            <span>Limited data</span>
          </div>
        )}
      </div>

      {contact.region && (
        <div className="text-sm text-gray-600 mb-4">
          {contact.region}
          {contact.authority_type && ` • ${contact.authority_type}`}
        </div>
      )}

      {contact.note && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
          <p className="text-sm text-yellow-800 mb-2">{contact.note}</p>
          {/* Add helpful link to find council website */}
          <div className="mt-2">
            <a
              href={`https://www.google.com/search?q=${encodeURIComponent(contact.council_name + ' adult social care contact')}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-blue-600 hover:text-blue-700 underline flex items-center gap-1"
            >
              <Globe className="w-4 h-4" />
              Find {contact.council_name} contact information
            </a>
          </div>
        </div>
      )}

      {/* Show message if no contact information available */}
      {!contact.asc_phone && !contact.asc_email && !contact.asc_website_url && !contact.assessment_url && !contact.office_address && !contact.opening_hours && !contact.emergency_phone && !contact.note && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
          <p className="text-sm text-gray-600 mb-2">
            Contact information for {contact.council_name} is not yet available in our database.
          </p>
          <a
            href={`https://www.google.com/search?q=${encodeURIComponent(contact.council_name + ' adult social care contact')}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-blue-600 hover:text-blue-700 underline flex items-center gap-1"
          >
            <Globe className="w-4 h-4" />
            Find contact information on Google
          </a>
        </div>
      )}

      <div className="space-y-4">
        {/* Phone */}
        {contact.asc_phone && (
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Phone className="w-5 h-5 text-gray-500" />
              <div>
                <div className="text-sm text-gray-600">Adult Social Care</div>
                <a
                  href={`tel:${contact.asc_phone.replace(/\s/g, '')}`}
                  className="text-base font-semibold text-blue-600 hover:text-blue-700"
                >
                  {formatPhone(contact.asc_phone)}
                </a>
              </div>
            </div>
            <button
              onClick={() => copyToClipboard(contact.asc_phone!, 'phone')}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
              title="Copy phone number"
            >
              {copied === 'phone' ? (
                <CheckCircle2 className="w-4 h-4 text-green-600" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </button>
          </div>
        )}

        {/* Emergency Phone */}
        {contact.emergency_phone && (
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-500" />
              <div>
                <div className="text-sm text-gray-600">Emergency Contact</div>
                <a
                  href={`tel:${contact.emergency_phone.replace(/\s/g, '')}`}
                  className="text-base font-semibold text-red-600 hover:text-red-700"
                >
                  {formatPhone(contact.emergency_phone)}
                </a>
              </div>
            </div>
            <button
              onClick={() => copyToClipboard(contact.emergency_phone!, 'emergency')}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
              title="Copy emergency number"
            >
              {copied === 'emergency' ? (
                <CheckCircle2 className="w-4 h-4 text-green-600" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </button>
          </div>
        )}

        {/* Email */}
        {contact.asc_email && (
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Mail className="w-5 h-5 text-gray-500" />
              <div>
                <div className="text-sm text-gray-600">Email</div>
                <a
                  href={`mailto:${contact.asc_email}`}
                  className="text-base font-semibold text-blue-600 hover:text-blue-700 break-all"
                >
                  {formatEmail(contact.asc_email)}
                </a>
              </div>
            </div>
            <button
              onClick={() => copyToClipboard(contact.asc_email!, 'email')}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
              title="Copy email"
            >
              {copied === 'email' ? (
                <CheckCircle2 className="w-4 h-4 text-green-600" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </button>
          </div>
        )}

        {/* Website */}
        {contact.asc_website_url && (
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Globe className="w-5 h-5 text-gray-500" />
              <div>
                <div className="text-sm text-gray-600">Website</div>
                <a
                  href={contact.asc_website_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-base font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1"
                >
                  Visit Website
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            </div>
          </div>
        )}

        {/* Assessment URL */}
        {contact.assessment_url && (
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Globe className="w-5 h-5 text-gray-500" />
              <div>
                <div className="text-sm text-gray-600">Book Assessment</div>
                <a
                  href={contact.assessment_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-base font-semibold text-green-600 hover:text-green-700 flex items-center gap-1"
                >
                  Book Online
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            </div>
          </div>
        )}

        {/* Office Address */}
        {contact.office_address && (
          <div className="flex items-start gap-3">
            <MapPin className="w-5 h-5 text-gray-500 mt-0.5" />
            <div>
              <div className="text-sm text-gray-600 mb-1">Office Address</div>
              <div className="text-base text-gray-900">{contact.office_address}</div>
            </div>
          </div>
        )}

        {/* Opening Hours */}
        {contact.opening_hours && (
          <div className="flex items-center gap-3">
            <Clock className="w-5 h-5 text-gray-500" />
            <div>
              <div className="text-sm text-gray-600">Opening Hours</div>
              <div className="text-base text-gray-900">{contact.opening_hours}</div>
            </div>
          </div>
        )}
      </div>

      {/* Copy All Button */}
      {(contact.asc_phone || contact.asc_email || contact.office_address) && (
        <div className="mt-6 pt-4 border-t">
          <button
            onClick={() => {
              const details = [
                contact.council_name,
                contact.asc_phone && `Phone: ${contact.asc_phone}`,
                contact.asc_email && `Email: ${contact.asc_email}`,
                contact.office_address && `Address: ${contact.office_address}`,
                contact.opening_hours && `Hours: ${contact.opening_hours}`,
              ].filter(Boolean).join('\n');
              copyToClipboard(details, 'all');
            }}
            className="w-full px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm font-medium flex items-center justify-center gap-2"
          >
            {copied === 'all' ? (
              <>
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                Copy All Contact Details
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
}


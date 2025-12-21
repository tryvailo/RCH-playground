/**
 * FormSection - Reusable form section wrapper
 * 
 * Provides consistent styling and structure for form sections
 */

import React from 'react';
import { FormSectionProps } from '../../types/funding.types';

export function FormSection({
  title,
  description,
  children,
  className = '',
}: FormSectionProps) {
  return (
    <div className={`space-y-3 ${className}`}>
      <div>
        <h3 className="text-sm font-semibold text-gray-900">{title}</h3>
        {description && (
          <p className="mt-1 text-xs text-gray-600">{description}</p>
        )}
      </div>
      <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
        {children}
      </div>
    </div>
  );
}

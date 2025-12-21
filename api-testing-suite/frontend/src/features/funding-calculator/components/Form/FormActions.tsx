/**
 * FormActions - Form submission and reset buttons
 */

import React from 'react';
import { RotateCcw, Send } from 'lucide-react';
import { FormActionsProps } from '../../types/funding.types';

export function FormActions({
  onSubmit,
  onReset,
  isLoading = false,
  isValid = true,
  errors,
}: FormActionsProps) {
  const hasErrors = errors && Object.values(errors).some((e) => e);

  return (
    <div className="flex gap-3 justify-between items-center">
      <button
        type="button"
        onClick={onReset}
        disabled={isLoading}
        className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 disabled:bg-gray-50 disabled:text-gray-400 rounded-lg font-medium transition-colors flex items-center gap-2"
      >
        <RotateCcw className="w-4 h-4" />
        Reset
      </button>

      {hasErrors && (
        <p className="text-sm text-red-600 font-medium">
          Please fix errors before submitting
        </p>
      )}

      <button
        type="button"
        onClick={onSubmit}
        disabled={isLoading || !isValid || hasErrors}
        className="px-6 py-2 bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed rounded-lg font-medium transition-colors flex items-center gap-2"
      >
        {isLoading ? (
          <>
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            Calculating...
          </>
        ) : (
          <>
            <Send className="w-4 h-4" />
            Calculate Funding
          </>
        )}
      </button>
    </div>
  );
}

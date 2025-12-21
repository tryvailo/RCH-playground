/**
 * ErrorAlert - Display error messages to user
 */

import React from 'react';
import { AlertCircle, X } from 'lucide-react';

interface ErrorAlertProps {
  error: Error | string | null;
  onDismiss?: () => void;
  type?: 'inline' | 'modal' | 'toast';
}

export function ErrorAlert({
  error,
  onDismiss,
  type = 'inline',
}: ErrorAlertProps) {
  if (!error) return null;

  const message =
    error instanceof Error ? error.message : String(error);

  const baseClasses =
    'flex items-start gap-3 p-4 rounded-lg border bg-red-50 border-red-200';

  return (
    <div className={baseClasses}>
      <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
      <div className="flex-1">
        <h3 className="font-semibold text-red-900">Error</h3>
        <p className="text-sm text-red-800 mt-1">{message}</p>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="flex-shrink-0 text-red-600 hover:text-red-900"
        >
          <X className="w-5 h-5" />
        </button>
      )}
    </div>
  );
}

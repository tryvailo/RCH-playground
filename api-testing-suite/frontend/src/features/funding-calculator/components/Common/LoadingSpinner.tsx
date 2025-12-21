/**
 * LoadingSpinner - Show calculation in progress
 */

import React from 'react';

interface LoadingSpinnerProps {
  message?: string;
  size?: 'small' | 'medium' | 'large';
}

const SIZE_MAP = {
  small: 'w-4 h-4',
  medium: 'w-8 h-8',
  large: 'w-12 h-12',
};

export function LoadingSpinner({
  message = 'Loading...',
  size = 'medium',
}: LoadingSpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-8">
      <div
        className={`${SIZE_MAP[size]} border-3 border-blue-200 border-t-blue-600 rounded-full animate-spin`}
      />
      {message && <p className="text-sm text-gray-600">{message}</p>}
    </div>
  );
}

/**
 * ResultCard - Reusable card component for displaying results
 * 
 * Props:
 * - title: Card heading
 * - icon: Optional icon
 * - value: Optional main value/percentage
 * - status: Color indicator (success, warning, danger, info)
 * - children: Card content
 */

import React from 'react';

interface ResultCardProps {
  title: string;
  icon?: React.ReactNode;
  value?: string | number;
  status?: 'success' | 'warning' | 'danger' | 'info';
  children?: React.ReactNode;
  className?: string;
}

const STATUS_COLORS = {
  success: 'bg-green-50 border-green-200',
  warning: 'bg-yellow-50 border-yellow-200',
  danger: 'bg-red-50 border-red-200',
  info: 'bg-blue-50 border-blue-200',
};

const VALUE_COLORS = {
  success: 'text-green-700',
  warning: 'text-yellow-700',
  danger: 'text-red-700',
  info: 'text-blue-700',
};

export function ResultCard({
  title,
  icon,
  value,
  status = 'info',
  children,
  className = '',
}: ResultCardProps) {
  return (
    <div
      className={`${STATUS_COLORS[status]} border rounded-lg p-4 ${className}`}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          {icon && <div className="flex-shrink-0">{icon}</div>}
          <h3 className="text-sm font-semibold text-gray-900">{title}</h3>
        </div>
        {value && (
          <span className={`text-lg font-bold ${VALUE_COLORS[status]}`}>
            {value}
          </span>
        )}
      </div>
      {children && (
        <div className="text-sm text-gray-700 space-y-1">{children}</div>
      )}
    </div>
  );
}

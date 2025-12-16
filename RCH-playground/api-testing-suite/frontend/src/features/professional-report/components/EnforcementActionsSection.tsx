import React from 'react';
import { AlertTriangle, FileWarning, Calendar, ExternalLink } from 'lucide-react';
import type { CQCDeepDive } from '../types';

interface EnforcementAction {
  type?: string;
  title?: string;
  description?: string;
  date?: string;
  status?: string;
  severity?: 'high' | 'medium' | 'low';
  link?: string;
}

interface EnforcementActionsSectionProps {
  cqcData: CQCDeepDive;
  homeName: string;
}

export default function EnforcementActionsSection({ cqcData, homeName }: EnforcementActionsSectionProps) {
  const enforcementActions = (cqcData as any)?.enforcement_actions as EnforcementAction[] | undefined;

  if (!enforcementActions || enforcementActions.length === 0) {
    return (
      <div className="bg-green-50 rounded-lg p-4 border border-green-200">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
            <FileWarning className="w-4 h-4 text-green-600" />
          </div>
          <div>
            <h5 className="text-sm font-semibold text-green-800">No Enforcement Actions</h5>
            <p className="text-xs text-green-600">
              {homeName} has no recorded CQC enforcement actions - a positive indicator
            </p>
          </div>
        </div>
      </div>
    );
  }

  const getSeverityColor = (severity?: string, status?: string) => {
    if (severity === 'high' || status?.toLowerCase().includes('active')) {
      return {
        bg: 'bg-red-50',
        border: 'border-red-200',
        icon: 'text-red-600',
        badge: 'bg-red-100 text-red-800'
      };
    }
    if (severity === 'medium' || status?.toLowerCase().includes('resolved')) {
      return {
        bg: 'bg-yellow-50',
        border: 'border-yellow-200',
        icon: 'text-yellow-600',
        badge: 'bg-yellow-100 text-yellow-800'
      };
    }
    return {
      bg: 'bg-gray-50',
      border: 'border-gray-200',
      icon: 'text-gray-600',
      badge: 'bg-gray-100 text-gray-800'
    };
  };

  const activeActions = enforcementActions.filter(
    a => a.status?.toLowerCase().includes('active') || !a.status
  );
  const resolvedActions = enforcementActions.filter(
    a => a.status?.toLowerCase().includes('resolved') || a.status?.toLowerCase().includes('closed')
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-orange-600" />
          <h4 className="text-lg font-semibold text-gray-900">CQC Enforcement Actions</h4>
        </div>
        <div className="flex items-center gap-2">
          {activeActions.length > 0 && (
            <span className="px-2 py-1 text-xs font-semibold bg-red-100 text-red-800 rounded-full">
              {activeActions.length} Active
            </span>
          )}
          {resolvedActions.length > 0 && (
            <span className="px-2 py-1 text-xs font-semibold bg-green-100 text-green-800 rounded-full">
              {resolvedActions.length} Resolved
            </span>
          )}
        </div>
      </div>

      {activeActions.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-red-600" />
            <span className="text-sm font-semibold text-red-800">Active Enforcement Actions</span>
          </div>
          <p className="text-xs text-red-700">
            This care home has active enforcement actions that require attention before making a decision.
          </p>
        </div>
      )}

      <div className="space-y-3">
        {enforcementActions.map((action, idx) => {
          const colors = getSeverityColor(action.severity, action.status);
          return (
            <div
              key={idx}
              className={`${colors.bg} ${colors.border} border rounded-lg p-4`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div className={`mt-0.5 ${colors.icon}`}>
                    <FileWarning className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h5 className="text-sm font-semibold text-gray-900">
                        {action.title || action.type || 'Enforcement Action'}
                      </h5>
                      {action.status && (
                        <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${colors.badge}`}>
                          {action.status}
                        </span>
                      )}
                    </div>
                    {action.description && (
                      <p className="text-sm text-gray-700 mb-2">{action.description}</p>
                    )}
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      {action.date && (
                        <div className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          <span>{new Date(action.date).toLocaleDateString('en-GB', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric'
                          })}</span>
                        </div>
                      )}
                      {action.type && (
                        <span className="text-gray-400">Type: {action.type}</span>
                      )}
                    </div>
                  </div>
                </div>
                {action.link && (
                  <a
                    href={action.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="text-xs text-gray-500 mt-3 p-3 bg-gray-50 rounded-lg">
        <strong>What are enforcement actions?</strong> These are formal regulatory actions taken by CQC 
        when a care provider fails to meet fundamental standards of care. They can include warning notices, 
        conditions on registration, or in severe cases, cancellation of registration.
      </div>
    </div>
  );
}

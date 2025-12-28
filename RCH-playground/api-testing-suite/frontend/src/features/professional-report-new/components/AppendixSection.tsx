import React, { useState } from 'react';
import { Database, RefreshCw, CheckCircle2, AlertCircle, ExternalLink, BookOpen, ChevronDown, ChevronUp } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import type { ProfessionalReportData } from '../types';

interface AppendixSectionProps {
  report: ProfessionalReportData;
}

export default function AppendixSection({ report }: AppendixSectionProps) {
  const appendix = report.appendix;

  if (!appendix) {
    return (
      <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
        <p className="text-sm text-gray-500">Appendix data not available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <Database className="w-5 h-5 text-gray-600" />
        <h4 className="text-lg font-semibold text-gray-900">Appendix: Data Sources & Metadata</h4>
      </div>

      {/* Report Metadata */}
      {appendix.report_metadata && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3">Report Metadata</h5>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
            <div>
              <div className="text-gray-600">Report ID</div>
              <div className="font-semibold text-gray-900 text-xs">{appendix.report_metadata.report_id}</div>
            </div>
            <div>
              <div className="text-gray-600">Generated At</div>
              <div className="font-semibold text-gray-900 text-xs">
                {new Date(appendix.report_metadata.generated_at).toLocaleString()}
              </div>
            </div>
            <div>
              <div className="text-gray-600">Total Sources</div>
              <div className="font-semibold text-gray-900">{appendix.report_metadata.total_sources}</div>
            </div>
          </div>
          {appendix.report_metadata.data_quality_note && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <div className="flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-yellow-600 flex-shrink-0 mt-0.5" />
                <p className="text-xs text-gray-600">{appendix.report_metadata.data_quality_note}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Cache Statistics */}
      {appendix.cache_statistics && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <RefreshCw className="w-4 h-4 text-blue-600" />
            Cache Statistics
          </h5>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
            <div>
              <div className="text-gray-600">Total Entries</div>
              <div className="font-semibold text-gray-900">
                {appendix.cache_statistics.total_cached_entries.toLocaleString()}
              </div>
            </div>
            <div>
              <div className="text-gray-600">Valid Entries</div>
              <div className="font-semibold text-green-700">
                {appendix.cache_statistics.valid_entries.toLocaleString()}
              </div>
            </div>
            <div>
              <div className="text-gray-600">Expired Entries</div>
              <div className="font-semibold text-yellow-700">
                {appendix.cache_statistics.expired_entries.toLocaleString()}
              </div>
            </div>
            <div>
              <div className="text-gray-600">Cache Size</div>
              <div className="font-semibold text-gray-900">
                {appendix.cache_statistics.cache_size_mb.toFixed(2)} MB
              </div>
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-gray-200 text-xs text-gray-600">
            Sources with cached data: {appendix.cache_statistics.sources_with_cache}
          </div>
        </div>
      )}

      {/* Data Sources */}
      {appendix.data_sources && appendix.data_sources.length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-sm font-semibold text-gray-900 mb-3">Data Sources</h5>
          <div className="space-y-3">
            {appendix.data_sources.map((source, idx) => (
              <div key={idx} className="border-l-4 border-blue-200 pl-4 py-3 bg-blue-50 rounded-r">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h6 className="font-semibold text-gray-900 text-sm">{source.name}</h6>
                    <p className="text-xs text-gray-600 mt-1">{source.description}</p>
                  </div>
                  {source.official_url && (
                    <a
                      href={source.official_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-700 flex-shrink-0 ml-2"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-2 text-xs">
                  <div>
                    <div className="text-gray-600">Data Types</div>
                    <div className="text-gray-700">
                      {source.data_types?.slice(0, 2).join(', ')}
                      {source.data_types && source.data_types.length > 2 && '...'}
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-600">Update Frequency</div>
                    <div className="text-gray-700">{source.update_frequency}</div>
                  </div>
                  {source.last_update && (
                    <>
                      {source.last_update.cached_entries !== undefined && (
                        <div>
                          <div className="text-gray-600">Cached Entries</div>
                          <div className="font-semibold text-gray-900">
                            {source.last_update.cached_entries}
                          </div>
                        </div>
                      )}
                      {source.last_update.cache_hits !== undefined && (
                        <div>
                          <div className="text-gray-600">Cache Hits</div>
                          <div className="font-semibold text-green-700">
                            {source.last_update.cache_hits}
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </div>
                {source.last_update?.status && (
                  <div className="mt-2 flex items-center gap-2">
                    <div className={`flex items-center gap-1 text-xs ${
                      source.last_update.status === 'active' ? 'text-green-700' : 'text-gray-500'
                    }`}>
                      {source.last_update.status === 'active' ? (
                        <CheckCircle2 className="w-3 h-3" />
                      ) : (
                        <AlertCircle className="w-3 h-3" />
                      )}
                      <span>{source.last_update.status}</span>
                    </div>
                    {source.last_update.note && (
                      <span className="text-xs text-gray-500">• {source.last_update.note}</span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Funding Calculator Data Sources (for £119 report) */}
      {appendix.funding_calculator_data_sources && (
        <div className="mt-8 pt-8 border-t-2 border-blue-200">
          <div className="bg-blue-50 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <BookOpen className="w-6 h-6 text-blue-600" />
              <h3 className="text-xl font-bold text-gray-900">
                Funding Eligibility Calculator - Data Sources & References
              </h3>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Complete list of official sources, legal citations, and verification guides for the Funding Eligibility Calculator (£19 standalone product).
            </p>
            <div className="bg-white rounded-lg p-6 border border-blue-200 max-h-[600px] overflow-y-auto">
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown>{appendix.funding_calculator_data_sources}</ReactMarkdown>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


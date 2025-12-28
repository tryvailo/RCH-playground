import React from 'react';
import { Phone, MapPin, Clock, AlertTriangle, ArrowRight, Award, CheckCircle2, Star } from 'lucide-react';
import type { ProfessionalReportData, ProfessionalCareHome } from '../types';

interface ExecutiveSummarySectionProps {
  report: ProfessionalReportData;
  onNavigateToSection?: (sectionId: string) => void;
}

type WaitingListStatus = 'Available now' | '2-4 weeks' | '3+ months';

const getWaitingListBadgeStyle = (status: WaitingListStatus | string | undefined) => {
  if (!status) return 'bg-gray-100 text-gray-700 border-gray-300';
  const lower = status.toLowerCase();
  if (lower.includes('available') || lower.includes('now')) {
    return 'bg-green-100 text-green-800 border-green-300';
  }
  if (lower.includes('2-4') || lower.includes('weeks')) {
    return 'bg-yellow-100 text-yellow-800 border-yellow-300';
  }
  return 'bg-red-100 text-red-800 border-red-300';
};

const getVerdictBadge = (score: number): { label: string; color: string; bgClass: string } => {
  if (score >= 85) {
    return { label: 'Excellent Match', color: 'text-green-800', bgClass: 'bg-green-100 border-green-300' };
  } else if (score >= 70) {
    return { label: 'Good Match', color: 'text-blue-800', bgClass: 'bg-blue-100 border-blue-300' };
  } else {
    return { label: 'Fair Match', color: 'text-yellow-800', bgClass: 'bg-yellow-100 border-yellow-300' };
  }
};

const getRankBadgeStyle = (rank: number) => {
  switch (rank) {
    case 1:
      return 'bg-gradient-to-r from-yellow-400 to-amber-500 text-white';
    case 2:
      return 'bg-gradient-to-r from-gray-300 to-gray-400 text-gray-800';
    case 3:
      return 'bg-gradient-to-r from-orange-300 to-orange-400 text-orange-900';
    default:
      return 'bg-gray-200 text-gray-700';
  }
};

export default function ExecutiveSummarySection({ report, onNavigateToSection }: ExecutiveSummarySectionProps) {
  const topHomes = report.careHomes.slice(0, 5);
  const isUrgent = report.clientNeeds?.careRequirements?.some(
    req => req.toLowerCase().includes('urgent') || req.toLowerCase().includes('immediate')
  );

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  const handlePhoneClick = (phone: string, homeName: string) => {
    window.location.href = `tel:${phone.replace(/\s/g, '')}`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center mb-6">
        <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">
          Your Professional Care Home Analysis
        </h2>
        <p className="text-lg text-gray-600">
          for <span className="font-semibold text-[#1E2A44]">{report.clientName}</span>
        </p>
        <p className="text-sm text-gray-500 mt-2">
          Report generated on {formatDate(report.generatedAt)}
        </p>
      </div>

      {/* Urgency Alert (Conditional) */}
      {isUrgent && topHomes[0] && (
        <div className="bg-gradient-to-r from-amber-50 to-orange-50 border-2 border-amber-300 rounded-xl p-4 shadow-sm">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-amber-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-amber-900 mb-1">Urgent Placement Timeline Detected</h3>
              <p className="text-sm text-amber-800 mb-3">
                Given your urgent timeline, we recommend calling your #1 choice today to check availability.
              </p>
              <button
                onClick={() => handlePhoneClick(topHomes[0].contact.phone, topHomes[0].name)}
                className="inline-flex items-center gap-2 px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors text-sm font-medium"
              >
                <Phone className="w-4 h-4" />
                Call {topHomes[0].name}: {topHomes[0].contact.phone}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Top 5 Recommendations */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <Award className="w-5 h-5 text-[#1E2A44]" />
          Your Top 5 Recommendations
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {topHomes.map((home, index) => {
            const rank = index + 1;
            const verdict = getVerdictBadge(home.matchScore);
            
            return (
              <div
                key={home.id}
                className={`relative bg-white rounded-xl border-2 shadow-sm overflow-hidden transition-all hover:shadow-md ${
                  rank === 1 ? 'border-yellow-400' : rank === 2 ? 'border-gray-300' : 'border-orange-300'
                }`}
              >
                {/* Rank Badge */}
                <div className={`absolute top-3 left-3 w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm shadow-sm ${getRankBadgeStyle(rank)}`}>
                  #{rank}
                </div>

                {/* Content */}
                <div className="p-4 pt-14">
                  {/* Home Name & Score */}
                  <div className="mb-3">
                    <h4 className="font-bold text-gray-900 text-lg leading-tight mb-1">
                      {home.name}
                    </h4>
                    <div className="flex items-center gap-2 flex-wrap">
                      <div className="flex items-center gap-1">
                        <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                        <span className="font-bold text-gray-900">{home.matchScore.toFixed(0)}%</span>
                      </div>
                      <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${verdict.bgClass} ${verdict.color}`}>
                        {verdict.label}
                      </span>
                    </div>
                  </div>

                  {/* Address */}
                  <div className="flex items-start gap-2 text-sm text-gray-600 mb-3">
                    <MapPin className="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" />
                    <span>{home.location}</span>
                  </div>

                  {/* Waiting List Status */}
                  {home.waitingListStatus && (
                    <div className="mb-3">
                      <span className={`inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full border font-medium ${getWaitingListBadgeStyle(home.waitingListStatus)}`}>
                        <Clock className="w-3 h-3" />
                        {home.waitingListStatus}
                      </span>
                    </div>
                  )}

                  {/* Match Reason */}
                  {home.matchReason && (
                    <p className="text-sm text-gray-700 mb-3 italic">
                      "{home.matchReason}"
                    </p>
                  )}

                  {/* Why Recommended - fallback if no matchReason */}
                  {!home.matchReason && home.whyChosen && (
                    <p className="text-sm text-gray-700 mb-3">
                      {home.whyChosen}
                    </p>
                  )}

                  {/* CTA - Phone */}
                  {home.contact?.phone && (
                    <button
                      onClick={() => handlePhoneClick(home.contact.phone, home.name)}
                      className={`w-full flex items-center justify-center gap-2 py-2.5 rounded-lg font-medium text-sm transition-colors ${
                        rank === 1
                          ? 'bg-[#1E2A44] text-white hover:bg-[#2D3E5F]'
                          : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                      }`}
                    >
                      <Phone className="w-4 h-4" />
                      {home.contact.phone}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="bg-gradient-to-r from-gray-50 to-slate-50 rounded-xl p-4 border border-gray-200">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-[#1E2A44]">{report.analysisSummary.totalHomesAnalyzed}</div>
            <div className="text-xs text-gray-600">Homes Analyzed</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-[#1E2A44]">{report.analysisSummary.factorsAnalyzed}+</div>
            <div className="text-xs text-gray-600">Data Points</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-[#1E2A44]">8</div>
            <div className="text-xs text-gray-600">Data Sources</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-600">
              {topHomes[0]?.matchScore?.toFixed(0) || '—'}%
            </div>
            <div className="text-xs text-gray-600">Top Match Score</div>
          </div>
        </div>
      </div>

      {/* CTA to Action Plan */}
      {onNavigateToSection && (
        <div className="text-center">
          <button
            onClick={() => onNavigateToSection('actionplan')}
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-xl font-semibold hover:from-emerald-700 hover:to-teal-700 transition-all shadow-md"
          >
            <CheckCircle2 className="w-5 h-5" />
            View 14-Day Action Plan
            <ArrowRight className="w-5 h-5" />
          </button>
          <p className="text-xs text-gray-500 mt-2">
            Step-by-step guide to secure your placement
          </p>
        </div>
      )}
    </div>
  );
}

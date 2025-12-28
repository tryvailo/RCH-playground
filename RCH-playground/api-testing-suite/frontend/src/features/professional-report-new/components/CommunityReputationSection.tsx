import React from 'react';
import { Star, MessageSquare, TrendingUp, Shield, Users } from 'lucide-react';
import type { ProfessionalCareHome } from '../types';

interface CommunityReputationSectionProps {
  home: ProfessionalCareHome;
}

export default function CommunityReputationSection({ home }: CommunityReputationSectionProps) {
  const reputation = home.communityReputation;

  if (!reputation) {
    return (
      <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
        <p className="text-sm text-gray-500">Community reputation data not available</p>
      </div>
    );
  }

  const sentimentColor = reputation.sentiment_analysis.sentiment_label === 'positive' 
    ? 'text-green-600' 
    : reputation.sentiment_analysis.sentiment_label === 'negative'
    ? 'text-red-600'
    : 'text-yellow-600';

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <Users className="w-5 h-5 text-purple-600" />
        <h4 className="text-lg font-semibold text-gray-900">Community Reputation</h4>
      </div>

      {/* Trust Score and Ratings */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-3 border border-purple-200">
          <div className="flex items-center gap-1 mb-1">
            <Shield className="w-4 h-4 text-purple-600" />
            <span className="text-xs text-purple-600 font-semibold">Trust Score</span>
          </div>
          <div className="text-2xl font-bold text-purple-900">
            {reputation.trust_score.toFixed(1)}
          </div>
          <div className="text-xs text-purple-700">out of 100</div>
        </div>

        {reputation.google_rating !== null && (
          <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-lg p-3 border border-yellow-200">
            <div className="flex items-center gap-1 mb-1">
              <Star className="w-4 h-4 text-yellow-600" />
              <span className="text-xs text-yellow-600 font-semibold">Google Rating</span>
            </div>
            <div className="text-2xl font-bold text-yellow-900">
              {reputation.google_rating.toFixed(1)}
            </div>
            <div className="text-xs text-yellow-700">
              {reputation.google_review_count} reviews
            </div>
          </div>
        )}

        {reputation.carehome_rating !== null && (
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-3 border border-blue-200">
            <div className="flex items-center gap-1 mb-1">
              <Star className="w-4 h-4 text-blue-600" />
              <span className="text-xs text-blue-600 font-semibold">CareHome.co.uk</span>
            </div>
            <div className="text-2xl font-bold text-blue-900">
              {reputation.carehome_rating.toFixed(1)}
            </div>
            <div className="text-xs text-blue-700">Rating</div>
          </div>
        )}

        <div className={`bg-gradient-to-br rounded-lg p-3 border ${
          reputation.sentiment_analysis.sentiment_label === 'positive'
            ? 'from-green-50 to-green-100 border-green-200'
            : reputation.sentiment_analysis.sentiment_label === 'negative'
            ? 'from-red-50 to-red-100 border-red-200'
            : 'from-yellow-50 to-yellow-100 border-yellow-200'
        }`}>
          <div className="flex items-center gap-1 mb-1">
            <TrendingUp className={`w-4 h-4 ${
              reputation.sentiment_analysis.sentiment_label === 'positive' ? 'text-green-600' :
              reputation.sentiment_analysis.sentiment_label === 'negative' ? 'text-red-600' :
              'text-yellow-600'
            }`} />
            <span className={`text-xs font-semibold ${
              reputation.sentiment_analysis.sentiment_label === 'positive' ? 'text-green-600' :
              reputation.sentiment_analysis.sentiment_label === 'negative' ? 'text-red-600' :
              'text-yellow-600'
            }`}>
              Sentiment
            </span>
          </div>
          <div className={`text-2xl font-bold ${
            reputation.sentiment_analysis.sentiment_label === 'positive' ? 'text-green-900' :
            reputation.sentiment_analysis.sentiment_label === 'negative' ? 'text-red-900' :
            'text-yellow-900'
          }`}>
            {(reputation.sentiment_analysis.average_sentiment * 100).toFixed(0)}%
          </div>
          <div className={`text-xs ${
            reputation.sentiment_analysis.sentiment_label === 'positive' ? 'text-green-700' :
            reputation.sentiment_analysis.sentiment_label === 'negative' ? 'text-red-700' :
            'text-yellow-700'
          }`}>
            {reputation.sentiment_analysis.sentiment_label}
          </div>
        </div>
      </div>

      {/* Sentiment Distribution */}
      {reputation.sentiment_analysis.sentiment_distribution && (
        <div className="bg-white rounded-lg p-4 border border-gray-200 mb-4">
          <h5 className="text-sm font-semibold text-gray-900 mb-3">Sentiment Distribution</h5>
          <div className="space-y-2">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-600">Positive</span>
                <span className="font-semibold text-green-700">
                  {reputation.sentiment_analysis.sentiment_distribution.positive}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full"
                  style={{ width: `${reputation.sentiment_analysis.sentiment_distribution.positive}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-600">Neutral</span>
                <span className="font-semibold text-yellow-700">
                  {reputation.sentiment_analysis.sentiment_distribution.neutral}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-yellow-500 h-2 rounded-full"
                  style={{ width: `${reputation.sentiment_analysis.sentiment_distribution.neutral}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-600">Negative</span>
                <span className="font-semibold text-red-700">
                  {reputation.sentiment_analysis.sentiment_distribution.negative}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-red-500 h-2 rounded-full"
                  style={{ width: `${reputation.sentiment_analysis.sentiment_distribution.negative}%` }}
                />
              </div>
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-gray-200 text-xs text-gray-500">
            Based on {reputation.sentiment_analysis.total_reviews} reviews analyzed
          </div>
        </div>
      )}

      {/* Sample Reviews */}
      {reputation.sample_reviews && reputation.sample_reviews.length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="flex items-center gap-2 mb-3">
            <MessageSquare className="w-4 h-4 text-gray-600" />
            <h5 className="text-sm font-semibold text-gray-900">Sample Reviews</h5>
            <span className="text-xs text-gray-500">
              ({reputation.total_reviews_analyzed} total from {reputation.review_sources.join(', ')})
            </span>
          </div>
          <div className="space-y-3">
            {reputation.sample_reviews.slice(0, 5).map((review, idx) => (
              <div key={idx} className="border-l-4 border-blue-200 pl-3 py-2 bg-blue-50 rounded-r">
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <div className="flex items-center">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className={`w-3 h-3 ${
                            i < review.rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'
                          }`}
                        />
                      ))}
                    </div>
                    <span className="text-xs font-semibold text-gray-700">{review.author}</span>
                  </div>
                  <div className="text-xs text-gray-500">
                    {review.source} {review.date && `• ${review.date}`}
                  </div>
                </div>
                <p className="text-xs text-gray-700 line-clamp-3">{review.text}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}


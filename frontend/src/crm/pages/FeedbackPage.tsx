import React, { useState } from 'react';
import { Star, MessageSquare, Clock, CheckCircle } from 'lucide-react';
import { useFeedback, useFeedbackStats } from '../hooks/useFeedback';
import { FeedbackFilters } from '../types/feedback';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function FeedbackPage() {
  const [filters, setFilters] = useState<FeedbackFilters>({ page: 1, size: 20 });
  
  const { data: feedbackData, isLoading: feedbackLoading } = useFeedback(filters);
  const { data: stats, isLoading: statsLoading } = useFeedbackStats(30);

  if (feedbackLoading || statsLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const feedback = feedbackData?.items || [];

  const getSentimentColor = (sentiment: string) => {
    const colors = {
      positive: 'text-green-600 bg-green-100',
      neutral: 'text-yellow-600 bg-yellow-100',
      negative: 'text-red-600 bg-red-100',
    };
    return colors[sentiment as keyof typeof colors] || colors.neutral;
  };

  const getRatingStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`h-4 w-4 ${i < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
      />
    ));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Feedback Management</h1>
        <p className="text-gray-600">Monitor and respond to customer feedback</p>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center">
              <MessageSquare className="h-8 w-8 text-blue-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Total Feedback</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_feedback}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center">
              <Star className="h-8 w-8 text-yellow-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Average Rating</p>
                <p className="text-2xl font-bold text-gray-900">{stats.average_rating.toFixed(1)}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Resolution Rate</p>
                <p className="text-2xl font-bold text-gray-900">{(stats.resolution_rate * 100).toFixed(1)}%</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center">
              <Clock className="h-8 w-8 text-orange-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Pending</p>
                <p className="text-2xl font-bold text-gray-900">{stats.pending_resolution}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Rating Distribution */}
      {stats && (
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Rating Distribution</h3>
          <div className="space-y-3">
            {[5, 4, 3, 2, 1].map((rating) => {
              const count = stats.rating_distribution[rating.toString() as keyof typeof stats.rating_distribution];
              const percentage = stats.total_feedback > 0 ? (count / stats.total_feedback) * 100 : 0;
              
              return (
                <div key={rating} className="flex items-center gap-4">
                  <div className="flex items-center gap-1 w-16">
                    <span className="text-sm font-medium">{rating}</span>
                    <Star className="h-4 w-4 text-yellow-400 fill-current" />
                  </div>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-yellow-400 h-2 rounded-full"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  <span className="text-sm text-gray-600 w-12">{count}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Sentiment Analysis */}
      {stats && (
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Sentiment Analysis</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-center">
                <p className="text-sm font-medium text-green-600">Positive</p>
                <p className="text-3xl font-bold text-green-900">{stats.sentiment_analysis.positive}</p>
                <p className="text-xs text-green-600">
                  {stats.total_feedback > 0 ? ((stats.sentiment_analysis.positive / stats.total_feedback) * 100).toFixed(1) : 0}%
                </p>
              </div>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg">
              <div className="text-center">
                <p className="text-sm font-medium text-yellow-600">Neutral</p>
                <p className="text-3xl font-bold text-yellow-900">{stats.sentiment_analysis.neutral}</p>
                <p className="text-xs text-yellow-600">
                  {stats.total_feedback > 0 ? ((stats.sentiment_analysis.neutral / stats.total_feedback) * 100).toFixed(1) : 0}%
                </p>
              </div>
            </div>
            <div className="bg-red-50 p-4 rounded-lg">
              <div className="text-center">
                <p className="text-sm font-medium text-red-600">Negative</p>
                <p className="text-3xl font-bold text-red-900">{stats.sentiment_analysis.negative}</p>
                <p className="text-xs text-red-600">
                  {stats.total_feedback > 0 ? ((stats.sentiment_analysis.negative / stats.total_feedback) * 100).toFixed(1) : 0}%
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Feedback List */}
      <div className="bg-white rounded-lg border">
        <div className="p-6 border-b">
          <h3 className="text-lg font-medium text-gray-900">Recent Feedback</h3>
        </div>
        <div className="divide-y">
          {feedback.map((item) => (
            <div key={item.id} className="p-6">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1">
                    {getRatingStars(item.rating)}
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getSentimentColor(item.sentiment)}`}>
                    {item.sentiment}
                  </span>
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                    {item.service_type}
                  </span>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-500">
                    {new Date(item.submitted_at).toLocaleDateString()}
                  </p>
                  {item.resolved ? (
                    <span className="inline-flex items-center text-xs text-green-600">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Resolved
                    </span>
                  ) : (
                    <span className="inline-flex items-center text-xs text-orange-600">
                      <Clock className="h-3 w-3 mr-1" />
                      Pending
                    </span>
                  )}
                </div>
              </div>
              
              {item.comments && (
                <p className="text-gray-700 mb-3">{item.comments}</p>
              )}
              
              {item.resolution_notes && (
                <div className="bg-green-50 p-3 rounded-lg">
                  <p className="text-sm font-medium text-green-800 mb-1">Resolution Notes:</p>
                  <p className="text-sm text-green-700">{item.resolution_notes}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
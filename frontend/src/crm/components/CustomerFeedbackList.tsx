import React from 'react';
import { Star, MessageSquare } from 'lucide-react';
import { useFeedback } from '../hooks/useFeedback';
import LoadingSpinner from '../../components/LoadingSpinner';

interface CustomerFeedbackListProps {
  customerId: string;
}

export default function CustomerFeedbackList({ customerId }: CustomerFeedbackListProps) {
  const { data: feedbackData, isLoading } = useFeedback({ customer_id: customerId, size: 50 });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const feedback = feedbackData?.items || [];

  const getRatingStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`h-4 w-4 ${i < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
      />
    ));
  };

  const getSentimentColor = (sentiment: string) => {
    const colors = {
      positive: 'text-green-600 bg-green-100',
      neutral: 'text-yellow-600 bg-yellow-100',
      negative: 'text-red-600 bg-red-100',
    };
    return colors[sentiment as keyof typeof colors] || colors.neutral;
  };

  if (feedback.length === 0) {
    return (
      <div className="text-center py-8">
        <Star className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Feedback Yet</h3>
        <p className="text-gray-600">Customer feedback will appear here once submitted.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Customer Feedback</h3>
      
      <div className="space-y-4">
        {feedback.map((item) => (
          <div key={item.id} className="bg-gray-50 rounded-lg p-4">
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
                    ✓ Resolved
                  </span>
                ) : (
                  <span className="inline-flex items-center text-xs text-orange-600">
                    ⏳ Pending
                  </span>
                )}
              </div>
            </div>
            
            {item.comments && (
              <p className="text-gray-700 mb-3">{item.comments}</p>
            )}
            
            {item.resolution_notes && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <p className="text-sm font-medium text-green-800 mb-1">Resolution:</p>
                <p className="text-sm text-green-700">{item.resolution_notes}</p>
                {item.resolved_at && (
                  <p className="text-xs text-green-600 mt-1">
                    Resolved on {new Date(item.resolved_at).toLocaleDateString()}
                  </p>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
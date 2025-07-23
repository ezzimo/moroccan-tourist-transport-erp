export interface Feedback {
  id: string;
  customer_id: string;
  booking_id?: string;
  service_type: 'Tour' | 'Booking' | 'Support' | 'Transport' | 'Accommodation' | 'General';
  rating: number;
  comments?: string;
  resolved: boolean;
  resolution_notes?: string;
  resolved_by?: string;
  resolved_at?: string;
  is_anonymous: boolean;
  source: string;
  submitted_at: string;
  created_at: string;
  sentiment: 'positive' | 'neutral' | 'negative';
}

export interface FeedbackStats {
  total_feedback: number;
  average_rating: number;
  rating_distribution: {
    '1': number;
    '2': number;
    '3': number;
    '4': number;
    '5': number;
  };
  by_service_type: Record<string, number>;
  sentiment_analysis: {
    positive: number;
    neutral: number;
    negative: number;
  };
  resolution_rate: number;
  pending_resolution: number;
}

export interface CreateFeedbackData {
  customer_id: string;
  booking_id?: string;
  service_type: 'Tour' | 'Booking' | 'Support' | 'Transport' | 'Accommodation' | 'General';
  rating: number;
  comments?: string;
  is_anonymous?: boolean;
  source?: string;
}

export interface FeedbackFilters {
  page?: number;
  size?: number;
  customer_id?: string;
  service_type?: string;
  rating?: number;
  resolved?: boolean;
  booking_id?: string;
}
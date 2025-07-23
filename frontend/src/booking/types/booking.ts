export interface Booking {
  id: string;
  customer_id: string;
  service_type: 'Tour' | 'Transfer' | 'Custom Package' | 'Accommodation' | 'Activity';
  status: 'Pending' | 'Confirmed' | 'Cancelled' | 'Refunded' | 'Expired';
  pax_count: number;
  lead_passenger_name: string;
  lead_passenger_email: string;
  lead_passenger_phone: string;
  start_date: string;
  end_date?: string;
  base_price: number;
  discount_amount: number;
  total_price: number;
  currency: string;
  payment_status: 'Pending' | 'Partial' | 'Paid' | 'Failed' | 'Refunded';
  payment_method?: string;
  payment_reference?: string;
  special_requests?: string;
  internal_notes?: string;
  cancellation_reason?: string;
  cancelled_by?: string;
  cancelled_at?: string;
  created_at: string;
  updated_at: string;
  confirmed_at?: string;
  expires_at?: string;
  customer_name?: string;
  duration_days?: number;
  is_expired: boolean;
}

export interface CreateBookingData {
  customer_id: string;
  service_type: 'Tour' | 'Transfer' | 'Custom Package' | 'Accommodation' | 'Activity';
  pax_count: number;
  lead_passenger_name: string;
  lead_passenger_email: string;
  lead_passenger_phone: string;
  start_date: string;
  end_date?: string;
  base_price: number;
  promo_code?: string;
  payment_method?: string;
  special_requests?: string;
}

export interface BookingFilters {
  page?: number;
  size?: number;
  customer_id?: string;
  status?: string;
  service_type?: string;
  start_date_from?: string;
  start_date_to?: string;
  payment_status?: string;
}

export interface BookingsResponse {
  items: Booking[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ConfirmBookingData {
  payment_reference?: string;
  internal_notes?: string;
}

export interface CancelBookingData {
  reason: string;
  refund_amount?: number;
  internal_notes?: string;
}
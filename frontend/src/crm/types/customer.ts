export interface Customer {
  id: string;
  full_name?: string;
  company_name?: string;
  contact_type: 'Individual' | 'Corporate';
  email: string;
  phone: string;
  nationality?: string;
  region?: string;
  preferred_language: string;
  loyalty_status: 'New' | 'Bronze' | 'Silver' | 'Gold' | 'Platinum' | 'VIP';
  is_active: boolean;
  tags: string[];
  notes?: string;
  created_at: string;
  updated_at: string;
  last_interaction?: string;
}

export interface CustomerSummary extends Customer {
  total_interactions: number;
  total_feedback: number;
  average_rating: number;
  last_feedback_date?: string;
  segments: string[];
  interaction_channels: {
    email: number;
    phone: number;
    chat: number;
  };
  feedback_by_service: {
    Tour: number;
    Transport: number;
  };
}

export interface CustomersResponse {
  items: Customer[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface CustomerFilters {
  page?: number;
  size?: number;
  query?: string;
  contact_type?: string;
  region?: string;
  loyalty_status?: string;
  tags?: string[];
  is_active?: boolean;
}

export interface CreateCustomerData {
  full_name?: string;
  company_name?: string;
  contact_type: 'Individual' | 'Corporate';
  email: string;
  phone: string;
  nationality?: string;
  region?: string;
  preferred_language?: string;
  tags?: string[];
  notes?: string;
}
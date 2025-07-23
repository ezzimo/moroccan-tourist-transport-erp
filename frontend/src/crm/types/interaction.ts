export interface Interaction {
  id: string;
  customer_id: string;
  staff_member_id?: string;
  channel: 'email' | 'phone' | 'chat' | 'in-person' | 'whatsapp' | 'sms';
  subject?: string;
  summary: string;
  duration_minutes?: number;
  follow_up_required: boolean;
  follow_up_date?: string;
  timestamp: string;
  created_at: string;
}

export interface CreateInteractionData {
  customer_id: string;
  staff_member_id?: string;
  channel: 'email' | 'phone' | 'chat' | 'in-person' | 'whatsapp' | 'sms';
  subject?: string;
  summary: string;
  duration_minutes?: number;
  follow_up_required?: boolean;
  follow_up_date?: string;
}

export interface InteractionFilters {
  page?: number;
  size?: number;
  customer_id?: string;
  staff_member_id?: string;
  channel?: string;
  follow_up_required?: boolean;
}
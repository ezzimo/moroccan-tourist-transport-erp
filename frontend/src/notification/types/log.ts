export interface NotificationLog {
  id: string;
  type: string;
  channel: string;
  recipient_id: string;
  recipient_email?: string;
  recipient_phone?: string;
  subject?: string;
  message: string;
  status: string;
  sent_at?: string;
  delivered_at?: string;
  failed_at?: string;
  error_message?: string;
  created_at: string;
}

export interface NotificationLogSummary {
  recipient_id: string;
  period_days: number;
  total_notifications: number;
  by_status: {
    sent: number;
    delivered: number;
    failed: number;
  };
  by_channel: {
    email: number;
    sms: number;
    push: number;
    whatsapp?: number;
  };
  by_type: Record<string, number>;
}

export interface LogFilters {
  type?: string;
  channel?: string;
  status?: string;
  created_from?: string;
  created_to?: string;
}
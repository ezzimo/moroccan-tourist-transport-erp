export interface Notification {
  id: string;
  type: NotificationType;
  channel: NotificationChannel;
  recipient_type: 'USER' | 'CUSTOMER' | 'EMPLOYEE';
  recipient_id?: string;
  recipient_email?: string;
  recipient_phone?: string;
  recipient_name?: string;
  subject?: string;
  message: string;
  payload?: Record<string, any>;
  template_id?: string;
  template_variables?: Record<string, any>;
  status: NotificationStatus;
  retry_count: number;
  max_retries: number;
  priority: number;
  scheduled_at?: string;
  expires_at?: string;
  sent_at?: string;
  delivered_at?: string;
  failed_at?: string;
  error_message?: string;
  source_service?: string;
  group_id?: string;
  created_at: string;
}

export type NotificationType = 
  | 'BOOKING_CONFIRMED'
  | 'BOOKING_CANCELLED'
  | 'TOUR_REMINDER'
  | 'PAYMENT_RECEIVED'
  | 'PAYMENT_FAILED'
  | 'INVOICE_GENERATED'
  | 'MAINTENANCE_DUE'
  | 'DOCUMENT_EXPIRING'
  | 'TRAINING_REMINDER'
  | 'SYSTEM_ALERT'
  | 'WELCOME'
  | 'PASSWORD_RESET';

export type NotificationChannel = 'EMAIL' | 'SMS' | 'PUSH' | 'WHATSAPP';

export type NotificationStatus = 'PENDING' | 'SENT' | 'DELIVERED' | 'FAILED';

export interface NotificationRecipient {
  user_id?: string;
  email?: string;
  phone?: string;
  name?: string;
}

export interface SendNotificationRequest {
  type: NotificationType;
  recipients: NotificationRecipient[];
  template_id?: string;
  template_variables?: Record<string, any>;
  channels: NotificationChannel[];
  priority?: number;
  scheduled_at?: string;
  source_service?: string;
  group_id?: string;
}

export interface SendBulkNotificationRequest {
  type: NotificationType;
  channel: NotificationChannel;
  template_id: string;
  recipients: NotificationRecipient[];
  template_variables?: Record<string, any>;
  priority?: number;
  group_id?: string;
}

export interface NotificationStats {
  total_notifications: number;
  by_status: {
    sent: number;
    delivered: number;
    failed: number;
    pending: number;
  };
  by_channel: {
    email: number;
    sms: number;
    push: number;
    whatsapp?: number;
  };
  delivery_rate: number;
  failed_notifications: number;
  retry_rate: number;
}

export interface NotificationsResponse {
  items: Notification[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface NotificationFilters {
  page?: number;
  size?: number;
  type?: NotificationType;
  channel?: NotificationChannel;
  status?: NotificationStatus;
  recipient_id?: string;
  created_from?: string;
  created_to?: string;
  source_service?: string;
}
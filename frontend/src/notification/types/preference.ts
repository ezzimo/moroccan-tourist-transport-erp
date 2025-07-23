export interface UserPreference {
  id: string;
  user_id: string;
  user_type: string;
  email?: string;
  phone?: string;
  push_token?: string;
  email_enabled: boolean;
  sms_enabled: boolean;
  push_enabled: boolean;
  whatsapp_enabled: boolean;
  notification_preferences?: Record<string, ChannelPreferences>;
  quiet_hours_enabled: boolean;
  quiet_hours_start?: string;
  quiet_hours_end?: string;
  quiet_hours_timezone: string;
  max_emails_per_day?: number;
  max_sms_per_day?: number;
  preferred_language: string;
  preferred_timezone: string;
  is_active: boolean;
  created_at: string;
}

export interface ChannelPreferences {
  email: boolean;
  sms: boolean;
  push: boolean;
  whatsapp?: boolean;
}

export interface UpdatePreferencesRequest {
  email_enabled?: boolean;
  sms_enabled?: boolean;
  push_enabled?: boolean;
  whatsapp_enabled?: boolean;
  notification_preferences?: Record<string, ChannelPreferences>;
  quiet_hours_enabled?: boolean;
  quiet_hours_start?: string;
  quiet_hours_end?: string;
  preferred_language?: string;
  preferred_timezone?: string;
}

export interface UpdateContactRequest {
  email?: string;
  phone?: string;
  push_token?: string;
}
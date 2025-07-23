export interface NotificationTemplate {
  id: string;
  name: string;
  description?: string;
  type: TemplateType;
  channel: NotificationChannel;
  subject?: string;
  body: string;
  variables?: Record<string, TemplateVariable>;
  default_values?: Record<string, any>;
  content_type: string;
  language: string;
  is_active: boolean;
  version: number;
  usage_count: number;
  last_used_at?: string;
  is_validated: boolean;
  validation_errors?: string;
  created_by?: string;
  created_at: string;
}

export type TemplateType = 'TRANSACTIONAL' | 'MARKETING' | 'SYSTEM' | 'ALERT';

export interface TemplateVariable {
  type: 'string' | 'number' | 'boolean' | 'date';
  required: boolean;
  description?: string;
  default_value?: any;
}

export interface CreateTemplateRequest {
  name: string;
  description?: string;
  type: TemplateType;
  channel: NotificationChannel;
  subject?: string;
  body: string;
  variables?: Record<string, TemplateVariable>;
  default_values?: Record<string, any>;
  content_type?: string;
  language?: string;
}

export interface TemplatePreviewRequest {
  template_id: string;
  variables: Record<string, any>;
  recipient_info?: {
    email?: string;
    name?: string;
    phone?: string;
  };
}

export interface TemplatePreviewResponse {
  subject?: string;
  body: string;
  variables_used: Record<string, any>;
  missing_variables: string[];
  validation_errors: string[];
}

export interface TemplatesResponse {
  items: NotificationTemplate[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface TemplateFilters {
  page?: number;
  size?: number;
  type?: TemplateType;
  channel?: NotificationChannel;
  language?: string;
  is_active?: boolean;
}
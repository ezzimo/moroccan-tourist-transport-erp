export interface QualityAudit {
  id: string;
  audit_number: string;
  title: string;
  entity_type: 'TOUR' | 'FLEET' | 'BOOKING' | 'OFFICE' | 'DRIVER' | 'GUIDE' | 'CUSTOMER_SERVICE' | 'SAFETY';
  entity_id?: string;
  entity_name?: string;
  audit_type: 'INTERNAL' | 'EXTERNAL' | 'CUSTOMER_FEEDBACK' | 'REGULATORY' | 'FOLLOW_UP';
  status: 'SCHEDULED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED' | 'OVERDUE';
  auditor_id: string;
  auditor_name: string;
  external_auditor?: string;
  scheduled_date: string;
  pass_score: number;
  checklist: Record<string, any>;
  checklist_responses?: Record<string, any>;
  total_score?: number;
  outcome?: string;
  summary?: string;
  recommendations?: string;
  start_date?: string;
  completion_date?: string;
  requires_follow_up: boolean;
  follow_up_date?: string;
  follow_up_audit_id?: string;
  created_at: string;
  updated_at?: string;
  is_passed: boolean;
  is_overdue: boolean;
  days_overdue: number;
}

export interface CreateQualityAuditData {
  title: string;
  entity_type: 'TOUR' | 'FLEET' | 'BOOKING' | 'OFFICE' | 'DRIVER' | 'GUIDE' | 'CUSTOMER_SERVICE' | 'SAFETY';
  entity_id?: string;
  entity_name?: string;
  audit_type: 'INTERNAL' | 'EXTERNAL' | 'CUSTOMER_FEEDBACK' | 'REGULATORY' | 'FOLLOW_UP';
  auditor_id: string;
  auditor_name: string;
  external_auditor?: string;
  scheduled_date: string;
  pass_score?: number;
  checklist: Record<string, any>;
}

export interface QualityAuditFilters {
  page?: number;
  size?: number;
  query?: string;
  entity_type?: string;
  audit_type?: string;
  status?: string;
  auditor_id?: string;
  scheduled_from?: string;
  scheduled_to?: string;
  outcome?: string;
  requires_follow_up?: boolean;
}

export interface QualityAuditsResponse {
  items: QualityAudit[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface CompleteAuditData {
  responses: Record<string, {
    compliant: boolean;
    notes?: string;
    score: number;
  }>;
}

export interface AuditSummary {
  total_audits: number;
  by_status: Record<string, number>;
  by_entity_type: Record<string, number>;
  by_outcome: Record<string, number>;
  average_score: number;
  pass_rate: number;
  overdue_audits: number;
  upcoming_audits: number;
}
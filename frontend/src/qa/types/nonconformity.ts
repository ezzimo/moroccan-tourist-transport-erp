export interface NonConformity {
  id: string;
  audit_id: string;
  nc_number: string;
  title: string;
  description: string;
  severity: 'MINOR' | 'MAJOR' | 'CRITICAL';
  root_cause?: string;
  contributing_factors?: string;
  corrective_action?: string;
  preventive_action?: string;
  assigned_to?: string;
  due_date?: string;
  target_completion_date?: string;
  actual_completion_date?: string;
  status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'VERIFIED' | 'CLOSED' | 'ESCALATED';
  progress_notes?: string;
  verified_by?: string;
  verification_date?: string;
  verification_notes?: string;
  estimated_cost?: number;
  actual_cost?: number;
  is_recurring: boolean;
  previous_nc_id?: string;
  identified_date: string;
  created_at: string;
  updated_at?: string;
  is_overdue: boolean;
  days_overdue: number;
  age_days: number;
  is_critical_overdue: boolean;
  resolution_time_days?: number;
}

export interface CreateNonConformityData {
  audit_id: string;
  title: string;
  description: string;
  severity: 'MINOR' | 'MAJOR' | 'CRITICAL';
  root_cause?: string;
  contributing_factors?: string;
  corrective_action?: string;
  preventive_action?: string;
  assigned_to?: string;
  due_date?: string;
  target_completion_date?: string;
  estimated_cost?: number;
}

export interface NonConformityFilters {
  page?: number;
  size?: number;
  audit_id?: string;
  severity?: string;
  status?: string;
  assigned_to?: string;
  overdue_only?: boolean;
}

export interface NonConformitiesResponse {
  items: NonConformity[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ResolveNonConformityData {
  corrective_action: string;
  preventive_action?: string;
  actual_completion_date: string;
  actual_cost?: number;
  resolution_notes?: string;
}

export interface VerifyNonConformityData {
  verification_notes: string;
  verified: boolean;
  follow_up_required?: boolean;
  follow_up_notes?: string;
}
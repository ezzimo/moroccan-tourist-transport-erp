export interface Incident {
  id: string;
  driver_id: string;
  assignment_id?: string;
  incident_type: 'Accident' | 'Complaint' | 'Delay' | 'Misconduct' | 'Vehicle Breakdown' | 'Customer Dispute' | 'Safety Violation' | 'Policy Violation' | 'Medical Emergency' | 'Other';
  severity: 'Minor' | 'Moderate' | 'Major' | 'Critical';
  title: string;
  description: string;
  incident_date: string;
  incident_time?: string;
  location?: string;
  reported_by: string;
  reported_at: string;
  witness_names?: string;
  customer_involved: boolean;
  customer_name?: string;
  customer_contact?: string;
  status: 'Reported' | 'Under Investigation' | 'Resolved' | 'Closed' | 'Escalated';
  investigated_by?: string;
  investigation_notes?: string;
  resolution_description?: string;
  corrective_action?: string;
  preventive_measures?: string;
  estimated_cost?: number;
  actual_cost?: number;
  insurance_claim: boolean;
  claim_number?: string;
  follow_up_required: boolean;
  follow_up_date?: string;
  follow_up_notes?: string;
  police_report_filed: boolean;
  police_report_number?: string;
  photos_taken: boolean;
  resolved_at?: string;
  resolved_by?: string;
  created_at: string;
  updated_at: string;
  age_days: number;
  is_overdue: boolean;
  severity_weight: number;
  requires_immediate_attention: boolean;
}

export interface CreateIncidentData {
  driver_id: string;
  assignment_id?: string;
  incident_type: 'Accident' | 'Complaint' | 'Delay' | 'Misconduct' | 'Vehicle Breakdown' | 'Customer Dispute' | 'Safety Violation' | 'Policy Violation' | 'Medical Emergency' | 'Other';
  severity: 'Minor' | 'Moderate' | 'Major' | 'Critical';
  title: string;
  description: string;
  incident_date: string;
  incident_time?: string;
  location?: string;
  reported_by: string;
  witness_names?: string;
  customer_involved?: boolean;
  customer_name?: string;
  customer_contact?: string;
  estimated_cost?: number;
  insurance_claim?: boolean;
  police_report_filed?: boolean;
  police_report_number?: string;
  photos_taken?: boolean;
}

export interface IncidentFilters {
  page?: number;
  size?: number;
  driver_id?: string;
  incident_type?: string;
  severity?: string;
  status?: string;
  incident_date_from?: string;
  incident_date_to?: string;
  requires_attention?: boolean;
}
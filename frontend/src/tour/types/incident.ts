export interface TourIncident {
  id: string;
  tour_instance_id: string;
  reporter_id: string;
  incident_type: 'DELAY' | 'MEDICAL' | 'COMPLAINT' | 'BREAKDOWN' | 'WEATHER' | 'SAFETY' | 'ACCOMMODATION' | 'TRANSPORT' | 'GUIDE_ISSUE' | 'CUSTOMER_ISSUE' | 'OTHER';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  title: string;
  description: string;
  location?: string;
  day_number?: number;
  affected_participants?: number;
  estimated_delay_minutes?: number;
  financial_impact?: number;
  is_resolved: boolean;
  resolution_description?: string;
  resolved_by?: string;
  resolved_at?: string;
  requires_follow_up: boolean;
  follow_up_notes?: string;
  escalated_to?: string;
  reported_at: string;
  created_at: string;
  updated_at?: string;
  priority_score: number;
  is_urgent: boolean;
}

export interface CreateTourIncidentData {
  tour_instance_id: string;
  reporter_id: string;
  incident_type: 'DELAY' | 'MEDICAL' | 'COMPLAINT' | 'BREAKDOWN' | 'WEATHER' | 'SAFETY' | 'ACCOMMODATION' | 'TRANSPORT' | 'GUIDE_ISSUE' | 'CUSTOMER_ISSUE' | 'OTHER';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  title: string;
  description: string;
  location?: string;
  day_number?: number;
  affected_participants?: number;
  estimated_delay_minutes?: number;
  financial_impact?: number;
}

export interface TourIncidentFilters {
  page?: number;
  size?: number;
  tour_instance_id?: string;
  incident_type?: string;
  severity?: string;
  is_resolved?: boolean;
  reporter_id?: string;
  requires_follow_up?: boolean;
}

export interface TourIncidentsResponse {
  items: TourIncident[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ResolveIncidentData {
  resolution_description: string;
  resolved_by: string;
  requires_follow_up?: boolean;
  follow_up_notes?: string;
}

export interface EscalateIncidentData {
  escalated_to: string;
  escalation_reason: string;
  notes?: string;
}

export interface IncidentStats {
  total_incidents: number;
  resolved_incidents: number;
  unresolved_incidents: number;
  by_type: Record<string, number>;
  by_severity: Record<string, number>;
  by_tour: Record<string, number>;
  average_resolution_time_hours: number;
  urgent_incidents: number;
  incidents_requiring_follow_up: number;
}
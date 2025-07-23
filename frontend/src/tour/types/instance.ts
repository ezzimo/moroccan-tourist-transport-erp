export interface TourInstance {
  id: string;
  template_id: string;
  booking_id: string;
  customer_id: string;
  title: string;
  status: 'PLANNED' | 'CONFIRMED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED' | 'POSTPONED';
  start_date: string;
  end_date: string;
  actual_start_date?: string;
  actual_end_date?: string;
  participant_count: number;
  lead_participant_name: string;
  assigned_guide_id?: string;
  assigned_vehicle_id?: string;
  assigned_driver_id?: string;
  language: string;
  special_requirements?: string;
  participant_details?: any;
  internal_notes?: string;
  current_day: number;
  completion_percentage: number;
  created_at: string;
  updated_at?: string;
  confirmed_at?: string;
}

export interface CreateTourInstanceData {
  template_id: string;
  booking_id: string;
  customer_id: string;
  title: string;
  start_date: string;
  end_date: string;
  participant_count: number;
  lead_participant_name: string;
  language?: string;
  special_requirements?: string;
  participant_details?: any;
}

export interface TourInstanceFilters {
  page?: number;
  size?: number;
  template_id?: string;
  booking_id?: string;
  customer_id?: string;
  status?: string;
  assigned_guide_id?: string;
  assigned_vehicle_id?: string;
  start_date_from?: string;
  start_date_to?: string;
  region?: string;
}

export interface TourInstancesResponse {
  items: TourInstance[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface TourAssignment {
  guide_id?: string;
  vehicle_id?: string;
  driver_id?: string;
  notes?: string;
}

export interface TourStatusUpdate {
  status: 'PLANNED' | 'CONFIRMED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED' | 'POSTPONED';
  notes?: string;
  actual_start_date?: string;
  actual_end_date?: string;
}

export interface TourProgressUpdate {
  current_day: number;
  completion_percentage: number;
  notes?: string;
}
export interface DriverAssignment {
  id: string;
  driver_id: string;
  tour_instance_id: string;
  vehicle_id?: string;
  status: 'Assigned' | 'Confirmed' | 'In Progress' | 'Completed' | 'Cancelled' | 'No Show';
  start_date: string;
  end_date: string;
  tour_title?: string;
  pickup_location?: string;
  dropoff_location?: string;
  estimated_duration_hours?: number;
  assigned_by?: string;
  assigned_at: string;
  confirmed_at?: string;
  started_at?: string;
  completed_at?: string;
  actual_start_time?: string;
  actual_end_time?: string;
  customer_rating?: number;
  customer_feedback?: string;
  special_instructions?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  duration_days: number;
  is_active: boolean;
  is_overdue: boolean;
  actual_duration_hours?: number;
  is_on_time: boolean;
}

export interface CreateDriverAssignmentData {
  driver_id: string;
  tour_instance_id: string;
  vehicle_id?: string;
  start_date: string;
  end_date: string;
  tour_title?: string;
  pickup_location?: string;
  dropoff_location?: string;
  estimated_duration_hours?: number;
  special_instructions?: string;
  notes?: string;
}

export interface DriverAssignmentFilters {
  page?: number;
  size?: number;
  driver_id?: string;
  tour_instance_id?: string;
  vehicle_id?: string;
  status?: string;
  start_date_from?: string;
  start_date_to?: string;
}
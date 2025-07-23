export interface VehicleAssignment {
  id: string;
  vehicle_id: string;
  tour_instance_id: string;
  driver_id?: string;
  status: 'Scheduled' | 'Active' | 'Completed' | 'Cancelled';
  start_date: string;
  end_date: string;
  start_odometer?: number;
  end_odometer?: number;
  pickup_location?: string;
  dropoff_location?: string;
  estimated_distance?: number;
  notes?: string;
  special_instructions?: string;
  actual_start_date?: string;
  actual_end_date?: string;
  assigned_by?: string;
  created_at: string;
  updated_at: string;
  duration_days: number;
  distance_traveled?: number;
  is_active: boolean;
}

export interface CreateVehicleAssignmentData {
  vehicle_id: string;
  tour_instance_id: string;
  driver_id?: string;
  start_date: string;
  end_date: string;
  pickup_location?: string;
  dropoff_location?: string;
  estimated_distance?: number;
  notes?: string;
  special_instructions?: string;
  assigned_by?: string;
}

export interface AssignmentFilters {
  page?: number;
  size?: number;
  vehicle_id?: string;
  tour_instance_id?: string;
  driver_id?: string;
  status?: string;
  start_date_from?: string;
  start_date_to?: string;
}
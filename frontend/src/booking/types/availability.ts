export interface AvailabilityRequest {
  resource_type?: 'Vehicle' | 'Guide' | 'Accommodation';
  resource_ids?: string[];
  start_date: string;
  end_date?: string;
  required_capacity?: number;
  service_type?: string;
}

export interface AvailabilityResponse {
  request_date: string;
  end_date?: string;
  required_capacity: number;
  available_resources: AvailableResource[];
  total_available: number;
  has_availability: boolean;
}

export interface AvailableResource {
  resource_id: string;
  resource_name: string;
  resource_type: string;
  date: string;
  total_capacity: number;
  available_capacity: number;
  is_available: boolean;
}
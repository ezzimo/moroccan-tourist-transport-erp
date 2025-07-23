export interface Vehicle {
  id: string;
  license_plate: string;
  vehicle_type: 'Bus' | 'Minibus' | 'SUV/4x4' | 'Sedan' | 'Van' | 'Motorcycle';
  brand: string;
  model: string;
  year: number;
  color?: string;
  seating_capacity: number;
  fuel_type: 'Gasoline' | 'Diesel' | 'Hybrid' | 'Electric' | 'LPG';
  engine_size?: number;
  transmission?: string;
  status: 'Available' | 'In Use' | 'Under Maintenance' | 'Out of Service' | 'Retired';
  current_odometer: number;
  registration_expiry?: string;
  insurance_expiry?: string;
  inspection_expiry?: string;
  purchase_date?: string;
  purchase_price?: number;
  vin_number?: string;
  notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  display_name: string;
  age_years: number;
  compliance_status: {
    registration: ComplianceItem;
    insurance: ComplianceItem;
    inspection: ComplianceItem;
  };
}

export interface ComplianceItem {
  expiry_date?: string;
  days_until_expiry?: number;
  is_expired: boolean;
  needs_attention: boolean;
}

export interface VehicleFilters {
  page?: number;
  size?: number;
  query?: string;
  vehicle_type?: string;
  status?: string;
  fuel_type?: string;
  brand?: string;
  min_seating_capacity?: number;
  max_seating_capacity?: number;
  min_year?: number;
  max_year?: number;
  is_active?: boolean;
  available_from?: string;
  available_to?: string;
}

export interface CreateVehicleData {
  license_plate: string;
  vehicle_type: 'Bus' | 'Minibus' | 'SUV/4x4' | 'Sedan' | 'Van' | 'Motorcycle';
  brand: string;
  model: string;
  year: number;
  color?: string;
  seating_capacity: number;
  fuel_type: 'Gasoline' | 'Diesel' | 'Hybrid' | 'Electric' | 'LPG';
  engine_size?: number;
  transmission?: string;
  current_odometer?: number;
  registration_expiry?: string;
  insurance_expiry?: string;
  inspection_expiry?: string;
  purchase_date?: string;
  purchase_price?: number;
  vin_number?: string;
  notes?: string;
}

export interface VehiclesResponse {
  items: Vehicle[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface VehicleAvailability {
  vehicle_id: string;
  start_date: string;
  end_date: string;
  is_available: boolean;
  conflicting_assignments: string[];
  status: string;
  notes?: string;
}
export interface MaintenanceRecord {
  id: string;
  vehicle_id: string;
  maintenance_type: 'Preventive' | 'Corrective' | 'Emergency' | 'Inspection' | 'Recall';
  description: string;
  date_performed: string;
  provider_name?: string;
  provider_contact?: string;
  cost?: number;
  currency: string;
  odometer_reading?: number;
  parts_replaced?: string;
  labor_hours?: number;
  next_service_date?: string;
  next_service_odometer?: number;
  is_completed: boolean;
  warranty_until?: string;
  notes?: string;
  performed_by?: string;
  approved_by?: string;
  created_at: string;
  updated_at: string;
  is_under_warranty: boolean;
  cost_per_hour?: number;
}

export interface CreateMaintenanceData {
  vehicle_id: string;
  maintenance_type: 'Preventive' | 'Corrective' | 'Emergency' | 'Inspection' | 'Recall';
  description: string;
  date_performed: string;
  provider_name?: string;
  provider_contact?: string;
  cost?: number;
  currency?: string;
  odometer_reading?: number;
  parts_replaced?: string;
  labor_hours?: number;
  next_service_date?: string;
  next_service_odometer?: number;
  warranty_until?: string;
  notes?: string;
  performed_by?: string;
  approved_by?: string;
}

export interface UpcomingMaintenance {
  vehicle_id: string;
  license_plate: string;
  vehicle_display_name: string;
  maintenance_type: string;
  next_service_date: string;
  days_until_service: number;
  last_service_description?: string;
  next_service_odometer?: number;
}

export interface MaintenanceFilters {
  page?: number;
  size?: number;
  vehicle_id?: string;
  maintenance_type?: string;
  date_from?: string;
  date_to?: string;
  is_completed?: boolean;
}
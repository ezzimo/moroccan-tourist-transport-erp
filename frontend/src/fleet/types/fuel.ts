export interface FuelLog {
  id: string;
  vehicle_id: string;
  date: string;
  odometer_reading: number;
  fuel_amount: number;
  fuel_cost: number;
  price_per_liter: number;
  station_name?: string;
  location?: string;
  trip_purpose?: string;
  driver_id?: string;
  distance_since_last_fill?: number;
  fuel_efficiency?: number;
  is_full_tank: boolean;
  receipt_number?: string;
  notes?: string;
  created_at: string;
  created_by?: string;
  cost_per_km?: number;
}

export interface CreateFuelLogData {
  vehicle_id: string;
  date: string;
  odometer_reading: number;
  fuel_amount: number;
  fuel_cost: number;
  price_per_liter: number;
  station_name?: string;
  location?: string;
  trip_purpose?: string;
  driver_id?: string;
  is_full_tank?: boolean;
  receipt_number?: string;
  notes?: string;
  created_by?: string;
}

export interface FuelStats {
  total_fuel_consumed: number;
  total_fuel_cost: number;
  average_price_per_liter: number;
  average_fuel_efficiency: number;
  total_distance: number;
  cost_per_km: number;
  by_month: Record<string, {
    fuel_consumed: number;
    total_cost: number;
    distance: number;
  }>;
  by_vehicle_type: Record<string, {
    fuel_consumed: number;
    total_cost: number;
    distance: number;
  }>;
}

export interface FuelFilters {
  page?: number;
  size?: number;
  vehicle_id?: string;
  date_from?: string;
  date_to?: string;
  driver_id?: string;
}
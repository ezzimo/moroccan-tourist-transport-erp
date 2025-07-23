export interface ReservationItem {
  id: string;
  booking_id: string;
  type: 'Accommodation' | 'Transport' | 'Activity' | 'Guide' | 'Meal' | 'Insurance';
  reference_id?: string;
  name: string;
  description?: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  specifications?: Record<string, any>;
  notes?: string;
  is_confirmed: boolean;
  is_cancelled: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateReservationItemData {
  booking_id: string;
  type: 'Accommodation' | 'Transport' | 'Activity' | 'Guide' | 'Meal' | 'Insurance';
  reference_id?: string;
  name: string;
  description?: string;
  quantity?: number;
  unit_price: number;
  specifications?: Record<string, any>;
  notes?: string;
}
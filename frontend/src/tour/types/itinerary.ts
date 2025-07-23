export interface ItineraryItem {
  id: string;
  tour_instance_id: string;
  day_number: number;
  start_time?: string;
  end_time?: string;
  duration_minutes?: number;
  activity_type: 'VISIT' | 'MEAL' | 'TRANSPORT' | 'ACCOMMODATION' | 'ACTIVITY' | 'FREE_TIME' | 'MEETING_POINT' | 'DEPARTURE' | 'ARRIVAL' | 'BREAK';
  title: string;
  description?: string;
  location_name?: string;
  address?: string;
  coordinates?: [number, number];
  notes?: string;
  cost?: number;
  is_mandatory: boolean;
  is_completed: boolean;
  completed_at?: string;
  completed_by?: string;
  is_cancelled: boolean;
  cancellation_reason?: string;
  created_at: string;
  updated_at?: string;
  display_time?: string;
}

export interface CreateItineraryItemData {
  tour_instance_id: string;
  day_number: number;
  start_time?: string;
  end_time?: string;
  duration_minutes?: number;
  activity_type: 'VISIT' | 'MEAL' | 'TRANSPORT' | 'ACCOMMODATION' | 'ACTIVITY' | 'FREE_TIME' | 'MEETING_POINT' | 'DEPARTURE' | 'ARRIVAL' | 'BREAK';
  title: string;
  description?: string;
  location_name?: string;
  address?: string;
  coordinates?: [number, number];
  notes?: string;
  cost?: number;
  is_mandatory?: boolean;
}

export interface DayItinerary {
  day_number: number;
  date: string;
  items: ItineraryItem[];
  total_items: number;
  completed_items: number;
  estimated_duration_minutes: number;
}

export interface CompleteItineraryItemData {
  notes?: string;
  actual_duration_minutes?: number;
}
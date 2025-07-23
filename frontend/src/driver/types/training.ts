export interface Training {
  id: string;
  driver_id: string;
  training_type: 'First Aid' | 'Defensive Driving' | 'Customer Service' | 'Language' | 'Tourism Law' | 'Safety Procedures';
  training_title: string;
  description?: string;
  scheduled_date: string;
  start_time?: string;
  end_time?: string;
  duration_hours?: number;
  trainer_name?: string;
  training_provider?: string;
  location?: string;
  status: 'Scheduled' | 'In Progress' | 'Completed' | 'Failed' | 'Cancelled';
  attendance_confirmed: boolean;
  score?: number;
  pass_score: number;
  certificate_issued: boolean;
  certificate_number?: string;
  certificate_valid_until?: string;
  certificate_file_path?: string;
  cost?: number;
  currency: string;
  mandatory: boolean;
  trainer_feedback?: string;
  driver_feedback?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  has_passed: boolean;
  is_certificate_valid: boolean;
  days_until_certificate_expiry?: number;
  training_effectiveness?: string;
}

export interface CreateTrainingData {
  driver_id: string;
  training_type: 'First Aid' | 'Defensive Driving' | 'Customer Service' | 'Language' | 'Tourism Law' | 'Safety Procedures';
  training_title: string;
  description?: string;
  scheduled_date: string;
  start_time?: string;
  end_time?: string;
  duration_hours?: number;
  trainer_name?: string;
  training_provider?: string;
  location?: string;
  pass_score?: number;
  cost?: number;
  mandatory?: boolean;
  notes?: string;
}

export interface TrainingFilters {
  page?: number;
  size?: number;
  driver_id?: string;
  training_type?: string;
  status?: string;
  scheduled_date_from?: string;
  scheduled_date_to?: string;
  mandatory?: boolean;
}
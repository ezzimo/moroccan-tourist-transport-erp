export interface TrainingProgram {
  id: string;
  title: string;
  description?: string;
  category: 'SAFETY' | 'TECHNICAL' | 'CUSTOMER_SERVICE' | 'LEADERSHIP' | 'COMPLIANCE' | 'OTHER';
  trainer_name?: string;
  delivery_method: 'IN_PERSON' | 'ONLINE' | 'HYBRID';
  start_date: string;
  end_date: string;
  duration_hours: number;
  max_participants: number;
  cost_per_participant?: number;
  is_mandatory: boolean;
  pass_score: number;
  status: 'PLANNED' | 'ACTIVE' | 'COMPLETED' | 'CANCELLED';
  created_at: string;
}

export interface TrainingEnrollment {
  id: string;
  employee_id: string;
  training_program_id: string;
  enrollment_date: string;
  completion_date?: string;
  final_score?: number;
  attendance_percentage?: number;
  trainer_feedback?: string;
  certificate_issued?: boolean;
  status: 'ENROLLED' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  created_at: string;
}

export interface CreateTrainingProgramData {
  title: string;
  description?: string;
  category: 'SAFETY' | 'TECHNICAL' | 'CUSTOMER_SERVICE' | 'LEADERSHIP' | 'COMPLIANCE' | 'OTHER';
  trainer_name?: string;
  delivery_method: 'IN_PERSON' | 'ONLINE' | 'HYBRID';
  start_date: string;
  end_date: string;
  duration_hours: number;
  max_participants: number;
  cost_per_participant?: number;
  is_mandatory: boolean;
  pass_score: number;
}

export interface EnrollEmployeesData {
  employee_ids: string[];
  training_program_id: string;
  enrollment_date: string;
  notes?: string;
}

export interface CompleteTrainingData {
  completion_date: string;
  final_score: number;
  attendance_percentage: number;
  trainer_feedback?: string;
  issue_certificate: boolean;
}
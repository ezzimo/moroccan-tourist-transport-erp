export interface Employee {
  id: string;
  employee_id: string;
  full_name: string;
  national_id?: string;
  gender?: 'Male' | 'Female' | 'Other';
  birth_date?: string;
  marital_status?: 'Single' | 'Married' | 'Divorced' | 'Widowed';
  email: string;
  phone?: string;
  address?: string;
  department: string;
  position: string;
  employment_type: 'FULL_TIME' | 'PART_TIME' | 'CONTRACT';
  contract_type?: 'PERMANENT' | 'FIXED_TERM' | 'PROBATION';
  hire_date: string;
  base_salary?: number;
  status: 'ACTIVE' | 'PROBATION' | 'SUSPENDED' | 'TERMINATED';
  manager_id?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface EmployeeSummary extends Employee {
  years_of_service: number;
  total_training_hours: number;
  completed_trainings: number;
  certificates_count: number;
  performance_rating?: number;
  manager_name?: string;
  direct_reports_count: number;
}

export interface EmployeesResponse {
  items: Employee[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface EmployeeFilters {
  page?: number;
  size?: number;
  query?: string;
  department?: string;
  position?: string;
  employment_type?: string;
  status?: string;
  is_active?: boolean;
}

export interface CreateEmployeeData {
  employee_id: string;
  full_name: string;
  national_id?: string;
  gender?: 'Male' | 'Female' | 'Other';
  birth_date?: string;
  email: string;
  phone?: string;
  department: string;
  position: string;
  employment_type: 'FULL_TIME' | 'PART_TIME' | 'CONTRACT';
  contract_type?: 'PERMANENT' | 'FIXED_TERM' | 'PROBATION';
  hire_date: string;
  base_salary?: number;
  manager_id?: string;
}

export interface TerminateEmployeeData {
  termination_date: string;
  reason: string;
  final_pay_amount?: number;
  return_company_property?: boolean;
  notes?: string;
}
export interface Driver {
  id: string;
  full_name: string;
  date_of_birth: string;
  gender: 'Male' | 'Female';
  nationality: string;
  national_id: string;
  phone: string;
  email?: string;
  address?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  employee_id?: string;
  employment_type: 'Permanent' | 'Seasonal' | 'Contract' | 'Freelance';
  hire_date: string;
  license_number: string;
  license_type: 'Category B' | 'Category C' | 'Category D' | 'Category D1' | 'Professional';
  license_issue_date: string;
  license_expiry_date: string;
  license_issuing_authority?: string;
  languages_spoken: string[];
  health_certificate_expiry?: string;
  medical_restrictions?: string;
  tour_guide_certified: boolean;
  first_aid_certified: boolean;
  status: 'Active' | 'On Leave' | 'In Training' | 'Suspended' | 'Terminated' | 'Retired';
  performance_rating?: number;
  total_tours_completed: number;
  total_incidents: number;
  notes?: string;
  created_at: string;
  updated_at: string;
  age: number;
  years_of_service: number;
  is_license_expired: boolean;
  days_until_license_expiry?: number;
  is_health_cert_expired: boolean;
  days_until_health_cert_expiry?: number;
  performance_score?: number;
  is_available_for_assignment: boolean;
}

export interface CreateDriverData {
  full_name: string;
  date_of_birth: string;
  gender: 'Male' | 'Female';
  nationality?: string;
  national_id: string;
  phone: string;
  email?: string;
  address?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  employee_id?: string;
  employment_type: 'Permanent' | 'Seasonal' | 'Contract' | 'Freelance';
  hire_date: string;
  license_number: string;
  license_type: 'Category B' | 'Category C' | 'Category D' | 'Category D1' | 'Professional';
  license_issue_date: string;
  license_expiry_date: string;
  license_issuing_authority?: string;
  languages_spoken?: string[];
  health_certificate_expiry?: string;
  medical_restrictions?: string;
  tour_guide_certified?: boolean;
  first_aid_certified?: boolean;
  notes?: string;
}

export interface DriverFilters {
  page?: number;
  size?: number;
  query?: string;
  status?: string;
  employment_type?: string;
  license_type?: string;
  languages?: string[];
  tour_guide_certified?: boolean;
  first_aid_certified?: boolean;
  available_for_assignment?: boolean;
  license_expiring_soon?: boolean;
}

export interface DriversResponse {
  items: Driver[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
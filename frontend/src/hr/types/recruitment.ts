export interface JobApplication {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  position_applied: string;
  department: string;
  source: 'JOB_BOARD' | 'COMPANY_WEBSITE' | 'REFERRAL' | 'SOCIAL_MEDIA' | 'OTHER';
  stage: 'RECEIVED' | 'SCREENING' | 'PHONE_INTERVIEW' | 'IN_PERSON_INTERVIEW' | 'TECHNICAL_TEST' | 'REFERENCE_CHECK' | 'OFFER_MADE' | 'HIRED' | 'REJECTED';
  years_of_experience?: number;
  education_level?: string;
  languages: string[];
  skills: string[];
  expected_salary?: number;
  overall_rating?: number;
  application_date: string;
  interview_date?: string;
  notes?: string;
  is_active: boolean;
  created_at: string;
}

export interface CreateJobApplicationData {
  full_name: string;
  email: string;
  phone: string;
  position_applied: string;
  department: string;
  source: 'JOB_BOARD' | 'COMPANY_WEBSITE' | 'REFERRAL' | 'SOCIAL_MEDIA' | 'OTHER';
  years_of_experience?: number;
  education_level?: string;
  languages: string[];
  skills: string[];
  expected_salary?: number;
}

export interface UpdateApplicationStageData {
  stage: 'RECEIVED' | 'SCREENING' | 'PHONE_INTERVIEW' | 'IN_PERSON_INTERVIEW' | 'TECHNICAL_TEST' | 'REFERENCE_CHECK' | 'OFFER_MADE' | 'HIRED' | 'REJECTED';
  notes?: string;
  interview_date?: string;
}
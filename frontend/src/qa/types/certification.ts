export interface Certification {
  id: string;
  certificate_number: string;
  name: string;
  type: 'ISO_9001' | 'ISO_14001' | 'ISO_45001' | 'TOURISM_QUALITY' | 'SAFETY_CERTIFICATION' | 'DRIVER_LICENSE' | 'GUIDE_LICENSE' | 'BUSINESS_LICENSE' | 'TRANSPORT_PERMIT' | 'OTHER';
  issuing_body: string;
  issuing_authority?: string;
  accreditation_body?: string;
  scope: 'COMPANY_WIDE' | 'DEPARTMENT' | 'INDIVIDUAL' | 'VEHICLE' | 'LOCATION';
  entity_type?: string;
  entity_id?: string;
  entity_name?: string;
  issue_date: string;
  expiry_date?: string;
  effective_date?: string;
  status: 'ACTIVE' | 'EXPIRED' | 'SUSPENDED' | 'PENDING_RENEWAL' | 'CANCELLED';
  document_path?: string;
  document_url?: string;
  verification_url?: string;
  requirements_met?: string;
  conditions?: string;
  restrictions?: string;
  renewable: boolean;
  renewal_process?: string;
  renewal_cost?: number;
  renewal_lead_time_days?: number;
  last_audit_date?: string;
  next_audit_date?: string;
  compliance_verified: boolean;
  certificate_holder?: string;
  responsible_manager?: string;
  description?: string;
  notes?: string;
  created_at: string;
  updated_at?: string;
  is_expired: boolean;
  days_until_expiry?: number;
  needs_renewal: boolean;
  is_valid: boolean;
  validity_period_days?: number;
  renewal_start_date?: string;
}

export interface CreateCertificationData {
  certificate_number: string;
  name: string;
  type: 'ISO_9001' | 'ISO_14001' | 'ISO_45001' | 'TOURISM_QUALITY' | 'SAFETY_CERTIFICATION' | 'DRIVER_LICENSE' | 'GUIDE_LICENSE' | 'BUSINESS_LICENSE' | 'TRANSPORT_PERMIT' | 'OTHER';
  issuing_body: string;
  issuing_authority?: string;
  accreditation_body?: string;
  scope: 'COMPANY_WIDE' | 'DEPARTMENT' | 'INDIVIDUAL' | 'VEHICLE' | 'LOCATION';
  entity_type?: string;
  entity_id?: string;
  entity_name?: string;
  issue_date: string;
  expiry_date?: string;
  effective_date?: string;
  requirements_met?: string;
  conditions?: string;
  restrictions?: string;
  renewable?: boolean;
  renewal_process?: string;
  renewal_cost?: number;
  renewal_lead_time_days?: number;
  certificate_holder?: string;
  responsible_manager?: string;
  description?: string;
  notes?: string;
}

export interface CertificationFilters {
  page?: number;
  size?: number;
  type?: string;
  status?: string;
  scope?: string;
  expiring_soon?: boolean;
  needs_renewal?: boolean;
}

export interface CertificationsResponse {
  items: Certification[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface RenewCertificationData {
  new_certificate_number: string;
  new_issue_date: string;
  new_expiry_date?: string;
  renewal_cost?: number;
  renewal_notes?: string;
}

export interface QADashboard {
  audit_summary: {
    total_audits: number;
    completed_this_month: number;
    pass_rate: number;
    overdue_audits: number;
  };
  nonconformity_summary: {
    total_open: number;
    critical_open: number;
    overdue_actions: number;
    resolved_this_month: number;
  };
  compliance_summary: {
    total_requirements: number;
    compliant: number;
    non_compliant: number;
    pending: number;
    expiring_soon: number;
  };
  certification_summary: {
    total_certifications: number;
    active: number;
    expiring_soon: number;
    expired: number;
  };
}
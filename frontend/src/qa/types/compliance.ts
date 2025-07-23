export interface ComplianceRequirement {
  id: string;
  requirement_code: string;
  title: string;
  description: string;
  domain: 'SAFETY' | 'LABOR' | 'TAX' | 'TOURISM' | 'TRANSPORT' | 'ENVIRONMENTAL' | 'DATA_PROTECTION' | 'HEALTH';
  requirement_type: 'LICENSE' | 'PERMIT' | 'CERTIFICATION' | 'INSPECTION' | 'TRAINING' | 'DOCUMENTATION' | 'PROCEDURE';
  regulatory_body: string;
  regulation_reference?: string;
  legal_basis?: string;
  applies_to_entity: string;
  mandatory: boolean;
  status: 'COMPLIANT' | 'NON_COMPLIANT' | 'PENDING' | 'EXPIRED' | 'NOT_APPLICABLE';
  compliance_date?: string;
  expiry_date?: string;
  renewal_required: boolean;
  renewal_frequency_months?: number;
  next_review_date?: string;
  responsible_person?: string;
  responsible_department?: string;
  evidence_required?: string;
  document_links?: string[];
  compliance_cost?: number;
  estimated_effort_hours?: number;
  risk_level?: string;
  non_compliance_impact?: string;
  notes?: string;
  last_assessment_notes?: string;
  created_at: string;
  updated_at?: string;
  last_reviewed_at?: string;
  is_expired: boolean;
  days_until_expiry?: number;
  needs_renewal: boolean;
  is_overdue_for_review: boolean;
  next_renewal_date?: string;
}

export interface CreateComplianceRequirementData {
  requirement_code: string;
  title: string;
  description: string;
  domain: 'SAFETY' | 'LABOR' | 'TAX' | 'TOURISM' | 'TRANSPORT' | 'ENVIRONMENTAL' | 'DATA_PROTECTION' | 'HEALTH';
  requirement_type: 'LICENSE' | 'PERMIT' | 'CERTIFICATION' | 'INSPECTION' | 'TRAINING' | 'DOCUMENTATION' | 'PROCEDURE';
  regulatory_body: string;
  regulation_reference?: string;
  legal_basis?: string;
  applies_to_entity: string;
  mandatory?: boolean;
  responsible_person?: string;
  responsible_department?: string;
  evidence_required?: string;
  compliance_cost?: number;
  estimated_effort_hours?: number;
  risk_level?: string;
  non_compliance_impact?: string;
  notes?: string;
}

export interface ComplianceRequirementFilters {
  page?: number;
  size?: number;
  domain?: string;
  requirement_type?: string;
  status?: string;
  responsible_person?: string;
  expiring_soon?: boolean;
}

export interface ComplianceRequirementsResponse {
  items: ComplianceRequirement[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface AssessComplianceData {
  status: 'COMPLIANT' | 'NON_COMPLIANT' | 'PENDING' | 'EXPIRED' | 'NOT_APPLICABLE';
  compliance_date?: string;
  assessment_notes: string;
  evidence_provided?: string;
  next_review_date?: string;
}
export interface VehicleDocument {
  id: string;
  vehicle_id: string;
  document_type: 'Registration' | 'Insurance' | 'Inspection' | 'Maintenance' | 'Purchase' | 'Other';
  title: string;
  description?: string;
  file_name: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  issue_date?: string;
  expiry_date?: string;
  issuing_authority?: string;
  document_number?: string;
  is_active: boolean;
  is_verified: boolean;
  uploaded_at: string;
  uploaded_by?: string;
  is_expired: boolean;
  days_until_expiry?: number;
  needs_renewal: boolean;
}

export interface CreateDocumentData {
  vehicle_id: string;
  document_type: 'Registration' | 'Insurance' | 'Inspection' | 'Maintenance' | 'Purchase' | 'Other';
  title: string;
  description?: string;
  issue_date?: string;
  expiry_date?: string;
  issuing_authority?: string;
  document_number?: string;
  file: File;
}

export interface DocumentFilters {
  page?: number;
  size?: number;
  vehicle_id?: string;
  document_type?: string;
  expiring_soon?: boolean;
}
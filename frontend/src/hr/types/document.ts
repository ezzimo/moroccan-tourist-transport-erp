export interface EmployeeDocument {
  id: string;
  employee_id: string;
  document_type: 'CONTRACT' | 'ID_COPY' | 'DIPLOMA' | 'CERTIFICATE' | 'MEDICAL' | 'REFERENCE' | 'OTHER';
  title: string;
  file_name: string;
  file_path: string;
  file_size: number;
  expiry_date?: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'EXPIRED';
  is_confidential: boolean;
  uploaded_at: string;
  uploaded_by?: string;
}

export interface UploadDocumentData {
  employee_id: string;
  document_type: 'CONTRACT' | 'ID_COPY' | 'DIPLOMA' | 'CERTIFICATE' | 'MEDICAL' | 'REFERENCE' | 'OTHER';
  title: string;
  file: File;
  expiry_date?: string;
  is_confidential: boolean;
}
import { apiClient } from '../../api/client';
import {
  EmployeeDocument,
  UploadDocumentData,
} from '../types/document';

export const documentApi = {
  getDocuments: async (filters: any = {}) => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/documents?${params}`);
    return response.data;
  },

  getExpiringDocuments: async (daysAhead = 30) => {
    const response = await apiClient.get(`/documents/expiring?days_ahead=${daysAhead}`);
    return response.data;
  },

  uploadDocument: async (data: UploadDocumentData): Promise<EmployeeDocument> => {
    const formData = new FormData();
    formData.append('employee_id', data.employee_id);
    formData.append('document_type', data.document_type);
    formData.append('title', data.title);
    formData.append('file', data.file);
    formData.append('is_confidential', data.is_confidential.toString());
    
    if (data.expiry_date) {
      formData.append('expiry_date', data.expiry_date);
    }

    const response = await apiClient.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  deleteDocument: async (id: string): Promise<void> => {
    await apiClient.delete(`/documents/${id}`);
  },
};
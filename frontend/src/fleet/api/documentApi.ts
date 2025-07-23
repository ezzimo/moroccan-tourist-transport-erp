import { apiClient } from '../../api/client';
import {
  VehicleDocument,
  CreateDocumentData,
  DocumentFilters,
} from '../types/document';

export const documentApi = {
  getDocuments: async (filters: DocumentFilters = {}) => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/documents/?${params}`);
    return response.data;
  },

  uploadDocument: async (data: CreateDocumentData): Promise<VehicleDocument> => {
    const formData = new FormData();
    formData.append('vehicle_id', data.vehicle_id);
    formData.append('document_type', data.document_type);
    formData.append('title', data.title);
    formData.append('file', data.file);
    
    if (data.description) formData.append('description', data.description);
    if (data.issue_date) formData.append('issue_date', data.issue_date);
    if (data.expiry_date) formData.append('expiry_date', data.expiry_date);
    if (data.issuing_authority) formData.append('issuing_authority', data.issuing_authority);
    if (data.document_number) formData.append('document_number', data.document_number);

    const response = await apiClient.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getExpiringDocuments: async (daysAhead = 30): Promise<VehicleDocument[]> => {
    const response = await apiClient.get('/documents/expiring', {
      params: { days_ahead: daysAhead }
    });
    return response.data;
  },

  deleteDocument: async (id: string): Promise<void> => {
    await apiClient.delete(`/documents/${id}`);
  },
};
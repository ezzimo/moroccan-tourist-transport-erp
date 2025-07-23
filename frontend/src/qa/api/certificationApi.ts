import { apiClient } from '../../api/client';
import {
  Certification,
  CreateCertificationData,
  CertificationFilters,
  CertificationsResponse,
  RenewCertificationData,
  QADashboard,
} from '../types/certification';

export const certificationApi = {
  getCertifications: async (filters: CertificationFilters = {}): Promise<CertificationsResponse> => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/certifications/?${params}`);
    return response.data;
  },

  getCertification: async (id: string): Promise<Certification> => {
    const response = await apiClient.get(`/certifications/${id}`);
    return response.data;
  },

  createCertification: async (data: CreateCertificationData): Promise<Certification> => {
    const response = await apiClient.post('/certifications', data);
    return response.data;
  },

  updateCertification: async (id: string, data: Partial<CreateCertificationData>): Promise<Certification> => {
    const response = await apiClient.put(`/certifications/${id}`, data);
    return response.data;
  },

  renewCertification: async (id: string, data: RenewCertificationData): Promise<Certification> => {
    const response = await apiClient.post(`/certifications/${id}/renew`, data);
    return response.data;
  },

  deleteCertification: async (id: string): Promise<void> => {
    await apiClient.delete(`/certifications/${id}`);
  },

  getDashboard: async (): Promise<QADashboard> => {
    const response = await apiClient.get('/reports/dashboard');
    return response.data;
  },

  exportAuditReport: async (startDate: string, endDate: string, format = 'pdf'): Promise<Blob> => {
    const response = await apiClient.get('/reports/export/audit-report', {
      params: { start_date: startDate, end_date: endDate, format },
      responseType: 'blob'
    });
    return response.data;
  },
};
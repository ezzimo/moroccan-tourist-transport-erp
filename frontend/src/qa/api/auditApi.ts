import { apiClient } from '../../api/client';
import {
  QualityAudit,
  CreateQualityAuditData,
  QualityAuditFilters,
  QualityAuditsResponse,
  CompleteAuditData,
  AuditSummary,
} from '../types/audit';

export const auditApi = {
  getAudits: async (filters: QualityAuditFilters = {}): Promise<QualityAuditsResponse> => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/audits/?${params}`);
    return response.data;
  },

  getAudit: async (id: string): Promise<QualityAudit> => {
    const response = await apiClient.get(`/audits/${id}`);
    return response.data;
  },

  getAuditSummary: async (days = 90): Promise<AuditSummary> => {
    const response = await apiClient.get('/audits/summary', {
      params: { days }
    });
    return response.data;
  },

  createAudit: async (data: CreateQualityAuditData): Promise<QualityAudit> => {
    const response = await apiClient.post('/audits', data);
    return response.data;
  },

  updateAudit: async (id: string, data: Partial<CreateQualityAuditData>): Promise<QualityAudit> => {
    const response = await apiClient.put(`/audits/${id}`, data);
    return response.data;
  },

  startAudit: async (id: string): Promise<QualityAudit> => {
    const response = await apiClient.post(`/audits/${id}/start`);
    return response.data;
  },

  completeAudit: async (id: string, data: CompleteAuditData): Promise<QualityAudit> => {
    const response = await apiClient.post(`/audits/${id}/complete`, data);
    return response.data;
  },

  deleteAudit: async (id: string): Promise<void> => {
    await apiClient.delete(`/audits/${id}`);
  },
};
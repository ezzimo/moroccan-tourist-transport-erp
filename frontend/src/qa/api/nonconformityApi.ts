import { apiClient } from '../../api/client';
import {
  NonConformity,
  CreateNonConformityData,
  NonConformityFilters,
  NonConformitiesResponse,
  ResolveNonConformityData,
  VerifyNonConformityData,
} from '../types/nonconformity';

export const nonconformityApi = {
  getNonConformities: async (filters: NonConformityFilters = {}): Promise<NonConformitiesResponse> => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/nonconformities/?${params}`);
    return response.data;
  },

  getNonConformity: async (id: string): Promise<NonConformity> => {
    const response = await apiClient.get(`/nonconformities/${id}`);
    return response.data;
  },

  createNonConformity: async (data: CreateNonConformityData): Promise<NonConformity> => {
    const response = await apiClient.post('/nonconformities', data);
    return response.data;
  },

  updateNonConformity: async (id: string, data: Partial<CreateNonConformityData>): Promise<NonConformity> => {
    const response = await apiClient.put(`/nonconformities/${id}`, data);
    return response.data;
  },

  resolveNonConformity: async (id: string, data: ResolveNonConformityData): Promise<NonConformity> => {
    const response = await apiClient.post(`/nonconformities/${id}/resolve`, data);
    return response.data;
  },

  verifyNonConformity: async (id: string, data: VerifyNonConformityData): Promise<NonConformity> => {
    const response = await apiClient.post(`/nonconformities/${id}/verify`, data);
    return response.data;
  },

  deleteNonConformity: async (id: string): Promise<void> => {
    await apiClient.delete(`/nonconformities/${id}`);
  },
};
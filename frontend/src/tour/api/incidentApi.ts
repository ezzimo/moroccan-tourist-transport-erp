import { apiClient } from '../../api/client';
import {
  TourIncident,
  CreateTourIncidentData,
  TourIncidentFilters,
  TourIncidentsResponse,
  ResolveIncidentData,
  EscalateIncidentData,
  IncidentStats,
} from '../types/incident';

export const tourIncidentApi = {
  getIncidents: async (filters: TourIncidentFilters = {}): Promise<TourIncidentsResponse> => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const { data } = await apiClient.get(`/tour-incidents/?${params}`);
    return data;
  },

  getIncident: async (id: string): Promise<TourIncident> => {
    const { data } = await apiClient.get(`/tour-incidents/${id}`);
    return data;
  },

  getUrgentIncidents: async (): Promise<TourIncident[]> => {
    const { data } = await apiClient.get('/tour-incidents/urgent');
    return data;
  },

  getIncidentStats: async (days = 30): Promise<IncidentStats> => {
    const { data } = await apiClient.get('/tour-incidents/stats', {
      params: { days }
    });
    return data;
  },

  createIncident: async (data: CreateTourIncidentData): Promise<TourIncident> => {
    const { data: result } = await apiClient.post('/tour-incidents', data);
    return result;
  },

  updateIncident: async (id: string, data: Partial<CreateTourIncidentData>): Promise<TourIncident> => {
    const { data: result } = await apiClient.put(`/tour-incidents/${id}`, data);
    return result;
  },

  resolveIncident: async (id: string, data: ResolveIncidentData): Promise<TourIncident> => {
    const { data: result } = await apiClient.post(`/tour-incidents/${id}/resolve`, data);
    return result;
  },

  escalateIncident: async (id: string, data: EscalateIncidentData): Promise<TourIncident> => {
    const { data: result } = await apiClient.post(`/tour-incidents/${id}/escalate`, data);
    return result;
  },

  deleteIncident: async (id: string): Promise<void> => {
    await apiClient.delete(`/tour-incidents/${id}`);
  },
};
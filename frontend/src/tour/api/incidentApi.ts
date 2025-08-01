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

    const response = await apiClient.get(`/incidents/?${params}`);
    return response.data;
  },

  getIncident: async (id: string): Promise<TourIncident> => {
    const response = await apiClient.get(`/incidents/${id}`);
    return response.data;
  },

  getUrgentIncidents: async (): Promise<TourIncident[]> => {
    const response = await apiClient.get('/incidents/urgent');
    return response.data;
  },

  getIncidentStats: async (days = 30): Promise<IncidentStats> => {
    const response = await apiClient.get('/incidents/stats', {
      params: { days }
    });
    return response.data;
  },

  createIncident: async (data: CreateTourIncidentData): Promise<TourIncident> => {
    const response = await apiClient.post('/incidents', data);
    return response.data;
  },

  updateIncident: async (id: string, data: Partial<CreateTourIncidentData>): Promise<TourIncident> => {
    const response = await apiClient.put(`/incidents/${id}`, data);
    return response.data;
  },

  resolveIncident: async (id: string, data: ResolveIncidentData): Promise<TourIncident> => {
    const response = await apiClient.post(`/incidents/${id}/resolve`, data);
    return response.data;
  },

  escalateIncident: async (id: string, data: EscalateIncidentData): Promise<TourIncident> => {
    const response = await apiClient.post(`/incidents/${id}/escalate`, data);
    return response.data;
  },

  deleteIncident: async (id: string): Promise<void> => {
    await apiClient.delete(`/incidents/${id}`);
  },
};
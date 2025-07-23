import { apiClient } from '../../api/client';
import {
  Incident,
  CreateIncidentData,
  IncidentFilters,
} from '../types/incident';

export const incidentApi = {
  getIncidents: async (filters: IncidentFilters = {}) => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/incidents/?${params}`);
    return response.data;
  },

  createIncident: async (data: CreateIncidentData): Promise<Incident> => {
    const response = await apiClient.post('/incidents/', data);
    return response.data;
  },

  updateIncident: async (id: string, data: Partial<CreateIncidentData>): Promise<Incident> => {
    const response = await apiClient.put(`/incidents/${id}`, data);
    return response.data;
  },

  getDriverIncidents: async (driverId: string) => {
    const response = await apiClient.get('/incidents/', {
      params: { driver_id: driverId }
    });
    return response.data;
  },
};
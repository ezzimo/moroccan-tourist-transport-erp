import { apiClient } from '../../api/client';
import {
  MaintenanceRecord,
  CreateMaintenanceData,
  UpcomingMaintenance,
  MaintenanceFilters,
} from '../types/maintenance';

export const maintenanceApi = {
  getMaintenance: async (filters: MaintenanceFilters = {}) => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/maintenance/?${params}`);
    return response.data;
  },

  createMaintenance: async (data: CreateMaintenanceData): Promise<MaintenanceRecord> => {
    const response = await apiClient.post('/maintenance/', data);
    return response.data;
  },

  updateMaintenance: async (id: string, data: Partial<CreateMaintenanceData>): Promise<MaintenanceRecord> => {
    const response = await apiClient.put(`/maintenance/${id}`, data);
    return response.data;
  },

  getUpcomingMaintenance: async (daysAhead = 30): Promise<UpcomingMaintenance[]> => {
    const response = await apiClient.get('/maintenance/upcoming', {
      params: { days_ahead: daysAhead }
    });
    return response.data;
  },

  getMaintenanceStats: async (days = 365) => {
    const response = await apiClient.get('/maintenance/stats', {
      params: { days }
    });
    return response.data;
  },
};
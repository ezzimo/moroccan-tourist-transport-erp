import { apiClient } from '../../api/client';
import {
  FuelLog,
  CreateFuelLogData,
  FuelStats,
  FuelFilters,
} from '../types/fuel';

export const fuelApi = {
  getFuelLogs: async (filters: FuelFilters = {}) => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/fuel/?${params}`);
    return response.data;
  },

  createFuelLog: async (data: CreateFuelLogData): Promise<FuelLog> => {
    const response = await apiClient.post('/fuel/', data);
    return response.data;
  },

  updateFuelLog: async (id: string, data: Partial<CreateFuelLogData>): Promise<FuelLog> => {
    const response = await apiClient.put(`/fuel/${id}`, data);
    return response.data;
  },

  getFuelStats: async (days = 365, vehicleId?: string): Promise<FuelStats> => {
    const params: any = { days };
    if (vehicleId) params.vehicle_id = vehicleId;

    const response = await apiClient.get('/fuel/stats', { params });
    return response.data;
  },
};
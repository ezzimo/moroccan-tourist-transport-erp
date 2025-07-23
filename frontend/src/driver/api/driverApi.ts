import { apiClient } from '../../api/client';
import {
  Driver,
  DriversResponse,
  DriverFilters,
  CreateDriverData,
} from '../types/driver';

export const driverApi = {
  getDrivers: async (filters: DriverFilters = {}): Promise<DriversResponse> => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        if (Array.isArray(value)) {
          value.forEach(v => params.append(key, v));
        } else {
          params.append(key, value.toString());
        }
      }
    });

    const response = await apiClient.get(`/drivers/?${params}`);
    return response.data;
  },

  getDriver: async (id: string): Promise<Driver> => {
    const response = await apiClient.get(`/drivers/${id}`);
    return response.data;
  },

  createDriver: async (data: CreateDriverData): Promise<Driver> => {
    const response = await apiClient.post('/drivers/', data);
    return response.data;
  },

  updateDriver: async (id: string, data: Partial<CreateDriverData>): Promise<Driver> => {
    const response = await apiClient.put(`/drivers/${id}`, data);
    return response.data;
  },

  deleteDriver: async (id: string): Promise<void> => {
    await apiClient.delete(`/drivers/${id}`);
  },

  getAvailableDrivers: async (startDate: string, endDate: string, filters: Partial<DriverFilters> = {}): Promise<Driver[]> => {
    const allFilters = {
      ...filters,
      available_for_assignment: true,
      start_date_from: startDate,
      start_date_to: endDate,
    };

    const response = await driverApi.getDrivers(allFilters);
    return response.items;
  },
};
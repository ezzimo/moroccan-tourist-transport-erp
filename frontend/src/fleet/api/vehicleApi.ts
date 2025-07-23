import { apiClient } from '../../api/client';
import {
  Vehicle,
  VehiclesResponse,
  VehicleFilters,
  CreateVehicleData,
  VehicleAvailability,
} from '../types/vehicle';

export const vehicleApi = {
  getVehicles: async (filters: VehicleFilters = {}): Promise<VehiclesResponse> => {
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

    const response = await apiClient.get(`/vehicles/?${params}`);
    return response.data;
  },

  getVehicle: async (id: string): Promise<Vehicle> => {
    const response = await apiClient.get(`/vehicles/${id}`);
    return response.data;
  },

  createVehicle: async (data: CreateVehicleData): Promise<Vehicle> => {
    const response = await apiClient.post('/vehicles/', data);
    return response.data;
  },

  updateVehicle: async (id: string, data: Partial<CreateVehicleData>): Promise<Vehicle> => {
    const response = await apiClient.put(`/vehicles/${id}`, data);
    return response.data;
  },

  deleteVehicle: async (id: string): Promise<void> => {
    await apiClient.delete(`/vehicles/${id}`);
  },

  getAvailableVehicles: async (startDate: string, endDate: string, filters: Partial<VehicleFilters> = {}): Promise<Vehicle[]> => {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
    });

    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/vehicles/available?${params}`);
    return response.data;
  },

  checkAvailability: async (vehicleId: string, startDate: string, endDate: string): Promise<VehicleAvailability> => {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
    });

    const response = await apiClient.get(`/vehicles/${vehicleId}/availability?${params}`);
    return response.data;
  },
};
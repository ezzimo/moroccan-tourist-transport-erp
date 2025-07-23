import { apiClient } from '../../api/client';
import {
  VehicleAssignment,
  CreateVehicleAssignmentData,
  AssignmentFilters,
} from '../types/assignment';

export const vehicleAssignmentApi = {
  getAssignments: async (filters: AssignmentFilters = {}) => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/assignments/?${params}`);
    return response.data;
  },

  createAssignment: async (data: CreateVehicleAssignmentData): Promise<VehicleAssignment> => {
    const response = await apiClient.post('/assignments/', data);
    return response.data;
  },

  updateAssignment: async (id: string, data: Partial<CreateVehicleAssignmentData>): Promise<VehicleAssignment> => {
    const response = await apiClient.put(`/assignments/${id}`, data);
    return response.data;
  },

  startAssignment: async (id: string, startOdometer: number): Promise<VehicleAssignment> => {
    const response = await apiClient.post(`/assignments/${id}/start`, null, {
      params: { start_odometer: startOdometer }
    });
    return response.data;
  },

  completeAssignment: async (id: string, endOdometer: number): Promise<VehicleAssignment> => {
    const response = await apiClient.post(`/assignments/${id}/complete`, null, {
      params: { end_odometer: endOdometer }
    });
    return response.data;
  },
};
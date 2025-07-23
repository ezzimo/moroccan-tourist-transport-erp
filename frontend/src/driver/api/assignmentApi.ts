import { apiClient } from '../../api/client';
import {
  DriverAssignment,
  CreateDriverAssignmentData,
  DriverAssignmentFilters,
} from '../types/assignment';

export const driverAssignmentApi = {
  getAssignments: async (filters: DriverAssignmentFilters = {}) => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/assignments/?${params}`);
    return response.data;
  },

  createAssignment: async (data: CreateDriverAssignmentData): Promise<DriverAssignment> => {
    const response = await apiClient.post('/assignments/', data);
    return response.data;
  },

  updateAssignment: async (id: string, data: Partial<CreateDriverAssignmentData>): Promise<DriverAssignment> => {
    const response = await apiClient.put(`/assignments/${id}`, data);
    return response.data;
  },

  getDriverAssignments: async (driverId: string, status?: string) => {
    const params: any = { driver_id: driverId };
    if (status) params.status = status;

    const response = await apiClient.get('/assignments/', { params });
    return response.data;
  },
};
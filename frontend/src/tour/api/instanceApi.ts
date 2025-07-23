import { apiClient } from '../../api/client';
import {
  TourInstance,
  CreateTourInstanceData,
  TourInstanceFilters,
  TourInstancesResponse,
  TourAssignment,
  TourStatusUpdate,
  TourProgressUpdate,
} from '../types/instance';

export const tourInstanceApi = {
  getTourInstances: async (filters: TourInstanceFilters = {}): Promise<TourInstancesResponse> => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/tour-instances/?${params}`);
    return response.data;
  },

  getTourInstance: async (id: string): Promise<TourInstance> => {
    const response = await apiClient.get(`/tour-instances/${id}`);
    return response.data;
  },

  getTourInstanceSummary: async (id: string): Promise<TourInstance> => {
    const response = await apiClient.get(`/tour-instances/${id}/summary`);
    return response.data;
  },

  getActiveTours: async (): Promise<TourInstance[]> => {
    const response = await apiClient.get('/tour-instances/active');
    return response.data;
  },

  createTourInstance: async (data: CreateTourInstanceData): Promise<TourInstance> => {
    const response = await apiClient.post('/tour-instances', data);
    return response.data;
  },

  updateTourInstance: async (id: string, data: Partial<CreateTourInstanceData>): Promise<TourInstance> => {
    const response = await apiClient.put(`/tour-instances/${id}`, data);
    return response.data;
  },

  assignResources: async (id: string, assignment: TourAssignment): Promise<TourInstance> => {
    const response = await apiClient.post(`/tour-instances/${id}/assign`, assignment);
    return response.data;
  },

  updateStatus: async (id: string, statusUpdate: TourStatusUpdate): Promise<TourInstance> => {
    const response = await apiClient.post(`/tour-instances/${id}/status`, statusUpdate);
    return response.data;
  },

  updateProgress: async (id: string, progressUpdate: TourProgressUpdate): Promise<TourInstance> => {
    const response = await apiClient.post(`/tour-instances/${id}/progress`, progressUpdate);
    return response.data;
  },

  deleteTourInstance: async (id: string): Promise<void> => {
    await apiClient.delete(`/tour-instances/${id}`);
  },
};
import { apiClient } from '../../api/client';
import {
  Training,
  CreateTrainingData,
  TrainingFilters,
} from '../types/training';

export const trainingApi = {
  getTraining: async (filters: TrainingFilters = {}) => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/training/?${params}`);
    return response.data;
  },

  createTraining: async (data: CreateTrainingData): Promise<Training> => {
    const response = await apiClient.post('/training/', data);
    return response.data;
  },

  updateTraining: async (id: string, data: Partial<CreateTrainingData>): Promise<Training> => {
    const response = await apiClient.put(`/training/${id}`, data);
    return response.data;
  },

  getDriverTraining: async (driverId: string) => {
    const response = await apiClient.get('/training/', {
      params: { driver_id: driverId }
    });
    return response.data;
  },
};
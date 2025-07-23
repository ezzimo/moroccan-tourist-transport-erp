import { apiClient } from '../../api/client';
import {
  TrainingProgram,
  TrainingEnrollment,
  CreateTrainingProgramData,
  EnrollEmployeesData,
  CompleteTrainingData,
} from '../types/training';

export const trainingApi = {
  getTrainingPrograms: async (filters: any = {}) => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/training/programs?${params}`);
    return response.data;
  },

  getTrainingProgram: async (id: string): Promise<TrainingProgram> => {
    const response = await apiClient.get(`/training/programs/${id}`);
    return response.data;
  },

  createTrainingProgram: async (data: CreateTrainingProgramData): Promise<TrainingProgram> => {
    const response = await apiClient.post('/training/programs', data);
    return response.data;
  },

  updateTrainingProgram: async (id: string, data: Partial<CreateTrainingProgramData>): Promise<TrainingProgram> => {
    const response = await apiClient.put(`/training/programs/${id}`, data);
    return response.data;
  },

  enrollEmployees: async (data: EnrollEmployeesData): Promise<TrainingEnrollment[]> => {
    const response = await apiClient.post('/training/enrollments', data);
    return response.data;
  },

  getEnrollments: async (filters: any = {}) => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/training/enrollments?${params}`);
    return response.data;
  },

  completeTraining: async (trainingId: string, data: CompleteTrainingData): Promise<TrainingEnrollment> => {
    const response = await apiClient.post(`/training/enrollments/${trainingId}/complete`, data);
    return response.data;
  },
};
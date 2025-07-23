import { apiClient } from '../../api/client';
import {
  JobApplication,
  CreateJobApplicationData,
  UpdateApplicationStageData,
} from '../types/recruitment';

export const recruitmentApi = {
  getApplications: async (filters: any = {}) => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/recruitment/applications?${params}`);
    return response.data;
  },

  getApplication: async (id: string): Promise<JobApplication> => {
    const response = await apiClient.get(`/recruitment/applications/${id}`);
    return response.data;
  },

  createApplication: async (data: CreateJobApplicationData): Promise<JobApplication> => {
    const response = await apiClient.post('/recruitment/applications', data);
    return response.data;
  },

  updateApplicationStage: async (id: string, data: UpdateApplicationStageData): Promise<JobApplication> => {
    const response = await apiClient.post(`/recruitment/applications/${id}/stage`, data);
    return response.data;
  },

  deleteApplication: async (id: string): Promise<void> => {
    await apiClient.delete(`/recruitment/applications/${id}`);
  },
};
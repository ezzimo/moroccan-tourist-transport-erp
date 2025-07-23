import { apiClient } from '../../api/client';
import {
  TourTemplate,
  CreateTourTemplateData,
  TourTemplateFilters,
  TourTemplatesResponse,
} from '../types/template';

export const tourTemplateApi = {
  getTourTemplates: async (filters: TourTemplateFilters = {}): Promise<TourTemplatesResponse> => {
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

    const response = await apiClient.get(`/tour-templates/?${params}`);
    return response.data;
  },

  getTourTemplate: async (id: string): Promise<TourTemplate> => {
    const response = await apiClient.get(`/tour-templates/${id}`);
    return response.data;
  },

  getFeaturedTemplates: async (limit = 10): Promise<TourTemplate[]> => {
    const response = await apiClient.get(`/tour-templates/featured?limit=${limit}`);
    return response.data;
  },

  createTourTemplate: async (data: CreateTourTemplateData): Promise<TourTemplate> => {
    const response = await apiClient.post('/tour-templates', data);
    return response.data;
  },

  updateTourTemplate: async (id: string, data: Partial<CreateTourTemplateData>): Promise<TourTemplate> => {
    const response = await apiClient.put(`/tour-templates/${id}`, data);
    return response.data;
  },

  duplicateTourTemplate: async (id: string, newTitle: string): Promise<TourTemplate> => {
    const response = await apiClient.post(`/tour-templates/${id}/duplicate?new_title=${encodeURIComponent(newTitle)}`);
    return response.data;
  },

  deleteTourTemplate: async (id: string): Promise<void> => {
    await apiClient.delete(`/tour-templates/${id}`);
  },
};
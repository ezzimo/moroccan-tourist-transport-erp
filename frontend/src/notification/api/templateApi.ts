import { apiClient } from '../../api/client';
import {
  NotificationTemplate,
  TemplatesResponse,
  TemplateFilters,
  CreateTemplateRequest,
  TemplatePreviewRequest,
  TemplatePreviewResponse,
} from '../types/template';

export const templateApi = {
  getTemplates: async (filters: TemplateFilters = {}): Promise<TemplatesResponse> => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/templates?${params}`);
    return response.data;
  },

  getTemplate: async (id: string): Promise<NotificationTemplate> => {
    const response = await apiClient.get(`/templates/${id}`);
    return response.data;
  },

  createTemplate: async (data: CreateTemplateRequest): Promise<NotificationTemplate> => {
    const response = await apiClient.post('/templates', data);
    return response.data;
  },

  updateTemplate: async (id: string, data: Partial<CreateTemplateRequest>): Promise<NotificationTemplate> => {
    const response = await apiClient.put(`/templates/${id}`, data);
    return response.data;
  },

  deleteTemplate: async (id: string): Promise<void> => {
    await apiClient.delete(`/templates/${id}`);
  },

  previewTemplate: async (data: TemplatePreviewRequest): Promise<TemplatePreviewResponse> => {
    const response = await apiClient.post('/templates/preview', data);
    return response.data;
  },
};
import { apiClient } from '../../api/client';
import {
  Feedback,
  FeedbackStats,
  CreateFeedbackData,
  FeedbackFilters,
} from '../types/feedback';

export const feedbackApi = {
  getFeedback: async (filters: FeedbackFilters = {}) => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/feedback/?${params}`);
    return response.data;
  },

  getFeedbackStats: async (days = 30): Promise<FeedbackStats> => {
    const response = await apiClient.get('/feedback/stats', {
      params: { days }
    });
    return response.data;
  },

  createFeedback: async (data: CreateFeedbackData): Promise<Feedback> => {
    const response = await apiClient.post('/feedback/', data);
    return response.data;
  },

  updateFeedback: async (id: string, data: { resolved?: boolean; resolution_notes?: string; resolved_by?: string }): Promise<Feedback> => {
    const response = await apiClient.put(`/feedback/${id}`, data);
    return response.data;
  },
};
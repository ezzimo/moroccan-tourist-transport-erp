import { apiClient } from '../../api/client';
import {
  Interaction,
  CreateInteractionData,
  InteractionFilters,
} from '../types/interaction';

export const interactionApi = {
  getInteractions: async (filters: InteractionFilters = {}) => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/interactions/?${params}`);
    return response.data;
  },

  getCustomerInteractions: async (customerId: string, page = 1, size = 20) => {
    const response = await apiClient.get(`/interactions/customer/${customerId}`, {
      params: { page, size }
    });
    return response.data;
  },

  createInteraction: async (data: CreateInteractionData): Promise<Interaction> => {
    const response = await apiClient.post('/interactions/', data);
    return response.data;
  },

  updateInteraction: async (id: string, data: Partial<CreateInteractionData>): Promise<Interaction> => {
    const response = await apiClient.put(`/interactions/${id}`, data);
    return response.data;
  },
};
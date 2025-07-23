import { apiClient } from '../../api/client';
import {
  UserPreference,
  UpdatePreferencesRequest,
  UpdateContactRequest,
} from '../types/preference';

export const preferenceApi = {
  getUserPreferences: async (userId: string): Promise<UserPreference> => {
    const response = await apiClient.get(`/preferences/${userId}`);
    return response.data;
  },

  updatePreferences: async (userId: string, data: UpdatePreferencesRequest): Promise<UserPreference> => {
    const response = await apiClient.put(`/preferences/${userId}`, data);
    return response.data;
  },

  updateContact: async (userId: string, data: UpdateContactRequest): Promise<UserPreference> => {
    const response = await apiClient.put(`/preferences/${userId}/contact`, null, {
      params: data
    });
    return response.data;
  },
};
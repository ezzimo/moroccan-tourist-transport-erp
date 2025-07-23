import { apiClient } from '../../api/client';
import {
  NotificationLog,
  NotificationLogSummary,
  LogFilters,
} from '../types/log';

export const logApi = {
  getNotificationHistory: async (recipientId: string, filters: LogFilters = {}): Promise<NotificationLog[]> => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/logs/${recipientId}?${params}`);
    return response.data;
  },

  getNotificationSummary: async (recipientId: string, days = 30): Promise<NotificationLogSummary> => {
    const response = await apiClient.get(`/logs/${recipientId}/summary`, {
      params: { days }
    });
    return response.data;
  },
};
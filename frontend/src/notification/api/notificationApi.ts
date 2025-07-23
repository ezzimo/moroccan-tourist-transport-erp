import { apiClient } from '../../api/client';
import {
  Notification,
  NotificationsResponse,
  NotificationFilters,
  SendNotificationRequest,
  SendBulkNotificationRequest,
  NotificationStats,
} from '../types/notification';

export const notificationApi = {
  getNotifications: async (filters: NotificationFilters = {}): Promise<NotificationsResponse> => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/notifications?${params}`);
    return response.data;
  },

  getNotification: async (id: string): Promise<Notification> => {
    const response = await apiClient.get(`/notifications/${id}`);
    return response.data;
  },

  sendNotification: async (data: SendNotificationRequest): Promise<Notification[]> => {
    const response = await apiClient.post('/notifications/send', data);
    return response.data;
  },

  sendBulkNotification: async (data: SendBulkNotificationRequest): Promise<{
    total_sent: number;
    successful: number;
    failed: number;
    group_id: string;
  }> => {
    const response = await apiClient.post('/notifications/send-bulk', data);
    return response.data;
  },

  getStats: async (days = 30): Promise<NotificationStats> => {
    const response = await apiClient.get('/notifications/stats', {
      params: { days }
    });
    return response.data;
  },
};
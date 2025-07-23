import { apiClient } from '../../api/client';
import { InventoryDashboard, InventoryAnalytics } from '../types/analytics';

export const inventoryAnalyticsApi = {
  getDashboard: async (): Promise<InventoryDashboard> => {
    const response = await apiClient.get('/analytics/dashboard');
    return response.data;
  },

  getAnalytics: async (period = 12): Promise<InventoryAnalytics> => {
    const response = await apiClient.get(`/analytics/detailed?period_months=${period}`);
    return response.data;
  },

  exportReport: async (startDate: string, endDate: string, format = 'pdf') => {
    const response = await apiClient.get('/analytics/export', {
      params: { start_date: startDate, end_date: endDate, format },
      responseType: 'blob',
    });
    return response.data;
  },
};
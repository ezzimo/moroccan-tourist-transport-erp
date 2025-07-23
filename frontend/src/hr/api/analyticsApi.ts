import { apiClient } from '../../api/client';
import { HRDashboard, HRAnalytics } from '../types/analytics';

export const hrAnalyticsApi = {
  getDashboard: async (): Promise<HRDashboard> => {
    const response = await apiClient.get('/analytics/dashboard');
    return response.data;
  },

  getAnalytics: async (period = 12): Promise<HRAnalytics> => {
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
import { useQuery } from '@tanstack/react-query';
import { hrAnalyticsApi } from '../api/analyticsApi';

export function useHRDashboard() {
  return useQuery({
    queryKey: ['hr-dashboard'],
    queryFn: () => hrAnalyticsApi.getDashboard(),
  });
}

export function useHRAnalytics(period = 12) {
  return useQuery({
    queryKey: ['hr-analytics', period],
    queryFn: () => hrAnalyticsApi.getAnalytics(period),
  });
}
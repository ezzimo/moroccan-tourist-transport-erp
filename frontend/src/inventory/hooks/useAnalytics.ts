import { useQuery } from '@tanstack/react-query';
import { inventoryAnalyticsApi } from '../api/analyticsApi';

export function useInventoryDashboard() {
  return useQuery({
    queryKey: ['inventory-dashboard'],
    queryFn: () => inventoryAnalyticsApi.getDashboard(),
  });
}

export function useInventoryAnalytics(period = 12) {
  return useQuery({
    queryKey: ['inventory-analytics', period],
    queryFn: () => inventoryAnalyticsApi.getAnalytics(period),
  });
}
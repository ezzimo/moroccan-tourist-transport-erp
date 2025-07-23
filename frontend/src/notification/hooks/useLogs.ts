import { useQuery } from '@tanstack/react-query';
import { logApi } from '../api/logApi';
import { LogFilters } from '../types/log';

export function useNotificationHistory(recipientId: string, filters: LogFilters = {}) {
  return useQuery({
    queryKey: ['notification-history', recipientId, filters],
    queryFn: () => logApi.getNotificationHistory(recipientId, filters),
    enabled: !!recipientId,
  });
}

export function useNotificationSummary(recipientId: string, days = 30) {
  return useQuery({
    queryKey: ['notification-summary', recipientId, days],
    queryFn: () => logApi.getNotificationSummary(recipientId, days),
    enabled: !!recipientId,
  });
}
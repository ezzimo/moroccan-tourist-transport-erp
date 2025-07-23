import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { notificationApi } from '../api/notificationApi';
import {
  NotificationFilters,
  SendNotificationRequest,
  SendBulkNotificationRequest,
} from '../types/notification';

export function useNotifications(filters: NotificationFilters = {}) {
  return useQuery({
    queryKey: ['notifications', filters],
    queryFn: () => notificationApi.getNotifications(filters),
  });
}

export function useNotification(id: string) {
  return useQuery({
    queryKey: ['notification', id],
    queryFn: () => notificationApi.getNotification(id),
    enabled: !!id,
  });
}

export function useNotificationStats(days = 30) {
  return useQuery({
    queryKey: ['notification-stats', days],
    queryFn: () => notificationApi.getStats(days),
  });
}

export function useSendNotification() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SendNotificationRequest) => notificationApi.sendNotification(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
      queryClient.invalidateQueries({ queryKey: ['notification-stats'] });
    },
  });
}

export function useSendBulkNotification() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SendBulkNotificationRequest) => notificationApi.sendBulkNotification(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
      queryClient.invalidateQueries({ queryKey: ['notification-stats'] });
    },
  });
}
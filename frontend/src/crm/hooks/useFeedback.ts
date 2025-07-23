import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { feedbackApi } from '../api/feedbackApi';
import { FeedbackFilters, CreateFeedbackData } from '../types/feedback';

export function useFeedback(filters: FeedbackFilters = {}) {
  return useQuery({
    queryKey: ['feedback', filters],
    queryFn: () => feedbackApi.getFeedback(filters),
  });
}

export function useFeedbackStats(days = 30) {
  return useQuery({
    queryKey: ['feedback-stats', days],
    queryFn: () => feedbackApi.getFeedbackStats(days),
  });
}

export function useCreateFeedback() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateFeedbackData) => feedbackApi.createFeedback(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feedback'] });
      queryClient.invalidateQueries({ queryKey: ['feedback-stats'] });
    },
  });
}

export function useUpdateFeedback() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: { resolved?: boolean; resolution_notes?: string; resolved_by?: string } }) =>
      feedbackApi.updateFeedback(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feedback'] });
      queryClient.invalidateQueries({ queryKey: ['feedback-stats'] });
    },
  });
}
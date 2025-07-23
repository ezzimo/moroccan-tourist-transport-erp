import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { preferenceApi } from '../api/preferenceApi';
import {
  UpdatePreferencesRequest,
  UpdateContactRequest,
} from '../types/preference';

export function useUserPreferences(userId: string) {
  return useQuery({
    queryKey: ['user-preferences', userId],
    queryFn: () => preferenceApi.getUserPreferences(userId),
    enabled: !!userId,
  });
}

export function useUpdatePreferences() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, data }: { userId: string; data: UpdatePreferencesRequest }) =>
      preferenceApi.updatePreferences(userId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['user-preferences', variables.userId] });
    },
  });
}

export function useUpdateContact() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, data }: { userId: string; data: UpdateContactRequest }) =>
      preferenceApi.updateContact(userId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['user-preferences', variables.userId] });
    },
  });
}
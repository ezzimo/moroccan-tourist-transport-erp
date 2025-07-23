import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { nonconformityApi } from '../api/nonconformityApi';
import { NonConformityFilters, CreateNonConformityData, ResolveNonConformityData, VerifyNonConformityData } from '../types/nonconformity';

export function useNonConformities(filters: NonConformityFilters = {}) {
  return useQuery({
    queryKey: ['nonconformities', filters],
    queryFn: () => nonconformityApi.getNonConformities(filters),
  });
}

export function useNonConformity(id: string) {
  return useQuery({
    queryKey: ['nonconformity', id],
    queryFn: () => nonconformityApi.getNonConformity(id),
    enabled: !!id,
  });
}

export function useCreateNonConformity() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateNonConformityData) => nonconformityApi.createNonConformity(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nonconformities'] });
    },
  });
}

export function useUpdateNonConformity() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateNonConformityData> }) =>
      nonconformityApi.updateNonConformity(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['nonconformities'] });
      queryClient.invalidateQueries({ queryKey: ['nonconformity', variables.id] });
    },
  });
}

export function useResolveNonConformity() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ResolveNonConformityData }) =>
      nonconformityApi.resolveNonConformity(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['nonconformities'] });
      queryClient.invalidateQueries({ queryKey: ['nonconformity', variables.id] });
    },
  });
}

export function useVerifyNonConformity() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: VerifyNonConformityData }) =>
      nonconformityApi.verifyNonConformity(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['nonconformities'] });
      queryClient.invalidateQueries({ queryKey: ['nonconformity', variables.id] });
    },
  });
}
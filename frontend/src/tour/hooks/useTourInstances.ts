import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tourInstanceApi } from '../api/instanceApi';
import { TourInstanceFilters, CreateTourInstanceData, TourAssignment, TourStatusUpdate, TourProgressUpdate } from '../types/instance';

export function useTourInstances(filters: TourInstanceFilters = {}) {
  return useQuery({
    queryKey: ['tour-instances', filters],
    queryFn: () => tourInstanceApi.getTourInstances(filters),
  });
}

export function useTourInstance(id: string) {
  return useQuery({
    queryKey: ['tour-instance', id],
    queryFn: () => tourInstanceApi.getTourInstance(id),
    enabled: !!id,
  });
}

export function useTourInstanceSummary(id: string) {
  return useQuery({
    queryKey: ['tour-instance-summary', id],
    queryFn: () => tourInstanceApi.getTourInstanceSummary(id),
    enabled: !!id,
  });
}

export function useActiveTours() {
  return useQuery({
    queryKey: ['active-tours'],
    queryFn: () => tourInstanceApi.getActiveTours(),
  });
}

export function useCreateTourInstance() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateTourInstanceData) => tourInstanceApi.createTourInstance(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tour-instances'] });
      queryClient.invalidateQueries({ queryKey: ['active-tours'] });
    },
  });
}

export function useUpdateTourInstance() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateTourInstanceData> }) =>
      tourInstanceApi.updateTourInstance(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tour-instances'] });
      queryClient.invalidateQueries({ queryKey: ['tour-instance', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['tour-instance-summary', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['active-tours'] });
    },
  });
}

export function useAssignTourResources() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, assignment }: { id: string; assignment: TourAssignment }) =>
      tourInstanceApi.assignResources(id, assignment),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tour-instances'] });
      queryClient.invalidateQueries({ queryKey: ['tour-instance', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['tour-instance-summary', variables.id] });
    },
  });
}

export function useUpdateTourStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, statusUpdate }: { id: string; statusUpdate: TourStatusUpdate }) =>
      tourInstanceApi.updateStatus(id, statusUpdate),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tour-instances'] });
      queryClient.invalidateQueries({ queryKey: ['tour-instance', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['active-tours'] });
    },
  });
}

export function useUpdateTourProgress() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, progressUpdate }: { id: string; progressUpdate: TourProgressUpdate }) =>
      tourInstanceApi.updateProgress(id, progressUpdate),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tour-instances'] });
      queryClient.invalidateQueries({ queryKey: ['tour-instance', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['tour-instance-summary', variables.id] });
    },
  });
}
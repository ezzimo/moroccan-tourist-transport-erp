import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tourIncidentApi } from '../api/incidentApi';
import { TourIncidentFilters, CreateTourIncidentData, ResolveIncidentData, EscalateIncidentData } from '../types/incident';

export function useIncidents(filters: TourIncidentFilters = {}) {
  return useQuery({
    queryKey: ['tour-incidents', filters],
    queryFn: () => tourIncidentApi.getIncidents(filters),
  });
}

export function useIncident(id: string) {
  return useQuery({
    queryKey: ['tour-incident', id],
    queryFn: () => tourIncidentApi.getIncident(id),
    enabled: !!id,
  });
}

export function useUrgentIncidents() {
  return useQuery({
    queryKey: ['urgent-incidents'],
    queryFn: () => tourIncidentApi.getUrgentIncidents(),
  });
}

export function useIncidentStats(days = 30) {
  return useQuery({
    queryKey: ['incident-stats', days],
    queryFn: () => tourIncidentApi.getIncidentStats(days),
  });
}

export function useCreateIncident() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateTourIncidentData) => tourIncidentApi.createIncident(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tour-incidents'] });
      queryClient.invalidateQueries({ queryKey: ['urgent-incidents'] });
      queryClient.invalidateQueries({ queryKey: ['incident-stats'] });
    },
  });
}

export function useUpdateIncident() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateTourIncidentData> }) =>
      tourIncidentApi.updateIncident(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tour-incidents'] });
      queryClient.invalidateQueries({ queryKey: ['tour-incident', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['urgent-incidents'] });
    },
  });
}

export function useResolveIncident() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ResolveIncidentData }) =>
      tourIncidentApi.resolveIncident(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tour-incidents'] });
      queryClient.invalidateQueries({ queryKey: ['tour-incident', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['urgent-incidents'] });
      queryClient.invalidateQueries({ queryKey: ['incident-stats'] });
    },
  });
}

export function useEscalateIncident() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: EscalateIncidentData }) =>
      tourIncidentApi.escalateIncident(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tour-incidents'] });
      queryClient.invalidateQueries({ queryKey: ['tour-incident', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['urgent-incidents'] });
    },
  });
}
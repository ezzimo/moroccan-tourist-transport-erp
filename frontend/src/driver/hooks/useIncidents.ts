import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { incidentApi } from '../api/incidentApi';
import { IncidentFilters, CreateIncidentData } from '../types/incident';

export function useIncidents(filters: IncidentFilters = {}) {
  return useQuery({
    queryKey: ['incidents', filters],
    queryFn: () => incidentApi.getIncidents(filters),
  });
}

export function useDriverIncidents(driverId: string) {
  return useQuery({
    queryKey: ['driver-incidents', driverId],
    queryFn: () => incidentApi.getDriverIncidents(driverId),
    enabled: !!driverId,
  });
}

export function useCreateIncident() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateIncidentData) => incidentApi.createIncident(data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
      queryClient.invalidateQueries({ queryKey: ['driver-incidents', variables.driver_id] });
    },
  });
}

export function useUpdateIncident() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateIncidentData> }) =>
      incidentApi.updateIncident(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
    },
  });
}
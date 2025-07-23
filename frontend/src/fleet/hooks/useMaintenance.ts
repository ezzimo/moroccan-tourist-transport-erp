import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { maintenanceApi } from '../api/maintenanceApi';
import { MaintenanceFilters, CreateMaintenanceData } from '../types/maintenance';

export function useMaintenance(filters: MaintenanceFilters = {}) {
  return useQuery({
    queryKey: ['maintenance', filters],
    queryFn: () => maintenanceApi.getMaintenance(filters),
  });
}

export function useUpcomingMaintenance(daysAhead = 30) {
  return useQuery({
    queryKey: ['upcoming-maintenance', daysAhead],
    queryFn: () => maintenanceApi.getUpcomingMaintenance(daysAhead),
  });
}

export function useMaintenanceStats(days = 365) {
  return useQuery({
    queryKey: ['maintenance-stats', days],
    queryFn: () => maintenanceApi.getMaintenanceStats(days),
  });
}

export function useCreateMaintenance() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateMaintenanceData) => maintenanceApi.createMaintenance(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['maintenance'] });
      queryClient.invalidateQueries({ queryKey: ['upcoming-maintenance'] });
      queryClient.invalidateQueries({ queryKey: ['maintenance-stats'] });
    },
  });
}

export function useUpdateMaintenance() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateMaintenanceData> }) =>
      maintenanceApi.updateMaintenance(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['maintenance'] });
      queryClient.invalidateQueries({ queryKey: ['upcoming-maintenance'] });
    },
  });
}
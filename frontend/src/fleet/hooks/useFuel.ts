import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fuelApi } from '../api/fuelApi';
import { FuelFilters, CreateFuelLogData } from '../types/fuel';

export function useFuelLogs(filters: FuelFilters = {}) {
  return useQuery({
    queryKey: ['fuel-logs', filters],
    queryFn: () => fuelApi.getFuelLogs(filters),
  });
}

export function useFuelStats(days = 365, vehicleId?: string) {
  return useQuery({
    queryKey: ['fuel-stats', days, vehicleId],
    queryFn: () => fuelApi.getFuelStats(days, vehicleId),
  });
}

export function useCreateFuelLog() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateFuelLogData) => fuelApi.createFuelLog(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fuel-logs'] });
      queryClient.invalidateQueries({ queryKey: ['fuel-stats'] });
    },
  });
}

export function useUpdateFuelLog() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateFuelLogData> }) =>
      fuelApi.updateFuelLog(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fuel-logs'] });
      queryClient.invalidateQueries({ queryKey: ['fuel-stats'] });
    },
  });
}
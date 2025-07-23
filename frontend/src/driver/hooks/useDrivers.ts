import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { driverApi } from '../api/driverApi';
import { DriverFilters, CreateDriverData } from '../types/driver';

export function useDrivers(filters: DriverFilters = {}) {
  return useQuery({
    queryKey: ['drivers', filters],
    queryFn: () => driverApi.getDrivers(filters),
  });
}

export function useDriver(id: string) {
  return useQuery({
    queryKey: ['driver', id],
    queryFn: () => driverApi.getDriver(id),
    enabled: !!id,
  });
}

export function useAvailableDrivers(startDate: string, endDate: string, filters: Partial<DriverFilters> = {}) {
  return useQuery({
    queryKey: ['available-drivers', startDate, endDate, filters],
    queryFn: () => driverApi.getAvailableDrivers(startDate, endDate, filters),
    enabled: !!startDate && !!endDate,
  });
}

export function useCreateDriver() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateDriverData) => driverApi.createDriver(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['drivers'] });
    },
  });
}

export function useUpdateDriver() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateDriverData> }) =>
      driverApi.updateDriver(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['drivers'] });
      queryClient.invalidateQueries({ queryKey: ['driver', variables.id] });
    },
  });
}

export function useDeleteDriver() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => driverApi.deleteDriver(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['drivers'] });
    },
  });
}
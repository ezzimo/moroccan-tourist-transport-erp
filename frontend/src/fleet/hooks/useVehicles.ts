import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { vehicleApi } from '../api/vehicleApi';
import { VehicleFilters, CreateVehicleData } from '../types/vehicle';

export function useVehicles(filters: VehicleFilters = {}) {
  return useQuery({
    queryKey: ['vehicles', filters],
    queryFn: () => vehicleApi.getVehicles(filters),
  });
}

export function useVehicle(id: string) {
  return useQuery({
    queryKey: ['vehicle', id],
    queryFn: () => vehicleApi.getVehicle(id),
    enabled: !!id,
  });
}

export function useAvailableVehicles(startDate: string, endDate: string, filters: Partial<VehicleFilters> = {}) {
  return useQuery({
    queryKey: ['available-vehicles', startDate, endDate, filters],
    queryFn: () => vehicleApi.getAvailableVehicles(startDate, endDate, filters),
    enabled: !!startDate && !!endDate,
  });
}

export function useVehicleAvailability(vehicleId: string, startDate: string, endDate: string) {
  return useQuery({
    queryKey: ['vehicle-availability', vehicleId, startDate, endDate],
    queryFn: () => vehicleApi.checkAvailability(vehicleId, startDate, endDate),
    enabled: !!vehicleId && !!startDate && !!endDate,
  });
}

export function useCreateVehicle() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateVehicleData) => vehicleApi.createVehicle(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehicles'] });
    },
  });
}

export function useUpdateVehicle() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateVehicleData> }) =>
      vehicleApi.updateVehicle(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['vehicles'] });
      queryClient.invalidateQueries({ queryKey: ['vehicle', variables.id] });
    },
  });
}

export function useDeleteVehicle() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => vehicleApi.deleteVehicle(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehicles'] });
    },
  });
}
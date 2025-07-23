import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { driverAssignmentApi } from '../api/assignmentApi';
import { DriverAssignmentFilters, CreateDriverAssignmentData } from '../types/assignment';

export function useDriverAssignments(filters: DriverAssignmentFilters = {}) {
  return useQuery({
    queryKey: ['driver-assignments', filters],
    queryFn: () => driverAssignmentApi.getAssignments(filters),
  });
}

export function useDriverAssignmentsByDriver(driverId: string, status?: string) {
  return useQuery({
    queryKey: ['driver-assignments-by-driver', driverId, status],
    queryFn: () => driverAssignmentApi.getDriverAssignments(driverId, status),
    enabled: !!driverId,
  });
}

export function useCreateDriverAssignment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateDriverAssignmentData) => driverAssignmentApi.createAssignment(data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['driver-assignments'] });
      queryClient.invalidateQueries({ queryKey: ['driver-assignments-by-driver', variables.driver_id] });
    },
  });
}

export function useUpdateDriverAssignment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateDriverAssignmentData> }) =>
      driverAssignmentApi.updateAssignment(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['driver-assignments'] });
    },
  });
}
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { trainingApi } from '../api/trainingApi';
import { TrainingFilters, CreateTrainingData } from '../types/training';

export function useTraining(filters: TrainingFilters = {}) {
  return useQuery({
    queryKey: ['training', filters],
    queryFn: () => trainingApi.getTraining(filters),
  });
}

export function useDriverTraining(driverId: string) {
  return useQuery({
    queryKey: ['driver-training', driverId],
    queryFn: () => trainingApi.getDriverTraining(driverId),
    enabled: !!driverId,
  });
}

export function useCreateTraining() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateTrainingData) => trainingApi.createTraining(data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['training'] });
      queryClient.invalidateQueries({ queryKey: ['driver-training', variables.driver_id] });
    },
  });
}

export function useUpdateTraining() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateTrainingData> }) =>
      trainingApi.updateTraining(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['training'] });
    },
  });
}
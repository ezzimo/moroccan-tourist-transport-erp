import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { trainingApi } from '../api/trainingApi';
import { CreateTrainingProgramData, EnrollEmployeesData, CompleteTrainingData } from '../types/training';

export function useTrainingPrograms(filters: any = {}) {
  return useQuery({
    queryKey: ['training-programs', filters],
    queryFn: () => trainingApi.getTrainingPrograms(filters),
  });
}

export function useTrainingProgram(id: string) {
  return useQuery({
    queryKey: ['training-program', id],
    queryFn: () => trainingApi.getTrainingProgram(id),
    enabled: !!id,
  });
}

export function useCreateTrainingProgram() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateTrainingProgramData) => trainingApi.createTrainingProgram(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['training-programs'] });
    },
  });
}

export function useEnrollEmployees() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: EnrollEmployeesData) => trainingApi.enrollEmployees(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['training-enrollments'] });
    },
  });
}

export function useTrainingEnrollments(filters: any = {}) {
  return useQuery({
    queryKey: ['training-enrollments', filters],
    queryFn: () => trainingApi.getEnrollments(filters),
  });
}

export function useCompleteTraining() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ trainingId, data }: { trainingId: string; data: CompleteTrainingData }) =>
      trainingApi.completeTraining(trainingId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['training-enrollments'] });
    },
  });
}
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { recruitmentApi } from '../api/recruitmentApi';
import { CreateJobApplicationData, UpdateApplicationStageData } from '../types/recruitment';

export function useJobApplications(filters: any = {}) {
  return useQuery({
    queryKey: ['job-applications', filters],
    queryFn: () => recruitmentApi.getApplications(filters),
  });
}

export function useJobApplication(id: string) {
  return useQuery({
    queryKey: ['job-application', id],
    queryFn: () => recruitmentApi.getApplication(id),
    enabled: !!id,
  });
}

export function useCreateJobApplication() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateJobApplicationData) => recruitmentApi.createApplication(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job-applications'] });
    },
  });
}

export function useUpdateApplicationStage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateApplicationStageData }) =>
      recruitmentApi.updateApplicationStage(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['job-applications'] });
      queryClient.invalidateQueries({ queryKey: ['job-application', variables.id] });
    },
  });
}
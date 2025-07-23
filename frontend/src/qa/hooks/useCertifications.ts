import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { certificationApi } from '../api/certificationApi';
import { CertificationFilters, CreateCertificationData, RenewCertificationData } from '../types/certification';

export function useCertifications(filters: CertificationFilters = {}) {
  return useQuery({
    queryKey: ['certifications', filters],
    queryFn: () => certificationApi.getCertifications(filters),
  });
}

export function useCertification(id: string) {
  return useQuery({
    queryKey: ['certification', id],
    queryFn: () => certificationApi.getCertification(id),
    enabled: !!id,
  });
}

export function useQADashboard() {
  return useQuery({
    queryKey: ['qa-dashboard'],
    queryFn: () => certificationApi.getDashboard(),
  });
}

export function useCreateCertification() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateCertificationData) => certificationApi.createCertification(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['certifications'] });
      queryClient.invalidateQueries({ queryKey: ['qa-dashboard'] });
    },
  });
}

export function useUpdateCertification() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateCertificationData> }) =>
      certificationApi.updateCertification(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['certifications'] });
      queryClient.invalidateQueries({ queryKey: ['certification', variables.id] });
    },
  });
}

export function useRenewCertification() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: RenewCertificationData }) =>
      certificationApi.renewCertification(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['certifications'] });
      queryClient.invalidateQueries({ queryKey: ['certification', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['qa-dashboard'] });
    },
  });
}

export function useExportAuditReport() {
  return useMutation({
    mutationFn: ({ startDate, endDate, format }: { startDate: string; endDate: string; format?: string }) =>
      certificationApi.exportAuditReport(startDate, endDate, format),
  });
}
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { auditApi } from '../api/auditApi';
import { QualityAuditFilters, CreateQualityAuditData, CompleteAuditData } from '../types/audit';

export function useAudits(filters: QualityAuditFilters = {}) {
  return useQuery({
    queryKey: ['qa-audits', filters],
    queryFn: () => auditApi.getAudits(filters),
  });
}

export function useAudit(id: string) {
  return useQuery({
    queryKey: ['qa-audit', id],
    queryFn: () => auditApi.getAudit(id),
    enabled: !!id,
  });
}

export function useAuditSummary(days = 90) {
  return useQuery({
    queryKey: ['audit-summary', days],
    queryFn: () => auditApi.getAuditSummary(days),
  });
}

export function useCreateAudit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateQualityAuditData) => auditApi.createAudit(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['qa-audits'] });
      queryClient.invalidateQueries({ queryKey: ['audit-summary'] });
    },
  });
}

export function useUpdateAudit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateQualityAuditData> }) =>
      auditApi.updateAudit(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['qa-audits'] });
      queryClient.invalidateQueries({ queryKey: ['qa-audit', variables.id] });
    },
  });
}

export function useStartAudit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => auditApi.startAudit(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['qa-audits'] });
      queryClient.invalidateQueries({ queryKey: ['qa-audit', id] });
    },
  });
}

export function useCompleteAudit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: CompleteAuditData }) =>
      auditApi.completeAudit(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['qa-audits'] });
      queryClient.invalidateQueries({ queryKey: ['qa-audit', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['audit-summary'] });
    },
  });
}
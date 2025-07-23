import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { complianceApi } from '../api/complianceApi';
import { ComplianceRequirementFilters, CreateComplianceRequirementData, AssessComplianceData } from '../types/compliance';

export function useComplianceRequirements(filters: ComplianceRequirementFilters = {}) {
  return useQuery({
    queryKey: ['compliance-requirements', filters],
    queryFn: () => complianceApi.getComplianceRequirements(filters),
  });
}

export function useComplianceRequirement(id: string) {
  return useQuery({
    queryKey: ['compliance-requirement', id],
    queryFn: () => complianceApi.getComplianceRequirement(id),
    enabled: !!id,
  });
}

export function useCreateComplianceRequirement() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateComplianceRequirementData) => complianceApi.createComplianceRequirement(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['compliance-requirements'] });
    },
  });
}

export function useUpdateComplianceRequirement() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateComplianceRequirementData> }) =>
      complianceApi.updateComplianceRequirement(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['compliance-requirements'] });
      queryClient.invalidateQueries({ queryKey: ['compliance-requirement', variables.id] });
    },
  });
}

export function useAssessCompliance() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: AssessComplianceData }) =>
      complianceApi.assessCompliance(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['compliance-requirements'] });
      queryClient.invalidateQueries({ queryKey: ['compliance-requirement', variables.id] });
    },
  });
}
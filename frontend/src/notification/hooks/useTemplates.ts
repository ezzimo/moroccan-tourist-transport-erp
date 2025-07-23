import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { templateApi } from '../api/templateApi';
import {
  TemplateFilters,
  CreateTemplateRequest,
  TemplatePreviewRequest,
} from '../types/template';

export function useTemplates(filters: TemplateFilters = {}) {
  return useQuery({
    queryKey: ['templates', filters],
    queryFn: () => templateApi.getTemplates(filters),
  });
}

export function useTemplate(id: string) {
  return useQuery({
    queryKey: ['template', id],
    queryFn: () => templateApi.getTemplate(id),
    enabled: !!id,
  });
}

export function useCreateTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateTemplateRequest) => templateApi.createTemplate(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
    },
  });
}

export function useUpdateTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateTemplateRequest> }) =>
      templateApi.updateTemplate(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
      queryClient.invalidateQueries({ queryKey: ['template', variables.id] });
    },
  });
}

export function useDeleteTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => templateApi.deleteTemplate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
    },
  });
}

export function usePreviewTemplate() {
  return useMutation({
    mutationFn: (data: TemplatePreviewRequest) => templateApi.previewTemplate(data),
  });
}
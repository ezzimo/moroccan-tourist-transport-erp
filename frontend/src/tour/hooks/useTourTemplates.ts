import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tourTemplateApi } from '../api/templateApi';
import { TourTemplateFilters, CreateTourTemplateData } from '../types/template';

export function useTourTemplates(filters: TourTemplateFilters = {}) {
  return useQuery({
    queryKey: ['tour-templates', filters],
    queryFn: () => tourTemplateApi.getTourTemplates(filters),
  });
}

export function useTourTemplate(id: string) {
  return useQuery({
    queryKey: ['tour-template', id],
    queryFn: () => tourTemplateApi.getTourTemplate(id),
    enabled: !!id,
  });
}

export function useFeaturedTourTemplates(limit = 10) {
  return useQuery({
    queryKey: ['featured-tour-templates', limit],
    queryFn: () => tourTemplateApi.getFeaturedTemplates(limit),
  });
}

export function useCreateTourTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateTourTemplateData) => tourTemplateApi.createTourTemplate(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tour-templates'] });
      queryClient.invalidateQueries({ queryKey: ['featured-tour-templates'] });
    },
  });
}

export function useUpdateTourTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateTourTemplateData> }) =>
      tourTemplateApi.updateTourTemplate(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tour-templates'] });
      queryClient.invalidateQueries({ queryKey: ['tour-template', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['featured-tour-templates'] });
    },
  });
}

export function useDuplicateTourTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, newTitle }: { id: string; newTitle: string }) =>
      tourTemplateApi.duplicateTourTemplate(id, newTitle),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tour-templates'] });
    },
  });
}
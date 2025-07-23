import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { interactionApi } from '../api/interactionApi';
import { InteractionFilters, CreateInteractionData } from '../types/interaction';

export function useInteractions(filters: InteractionFilters = {}) {
  return useQuery({
    queryKey: ['interactions', filters],
    queryFn: () => interactionApi.getInteractions(filters),
  });
}

export function useCustomerInteractions(customerId: string, page = 1, size = 20) {
  return useQuery({
    queryKey: ['customer-interactions', customerId, page, size],
    queryFn: () => interactionApi.getCustomerInteractions(customerId, page, size),
    enabled: !!customerId,
  });
}

export function useCreateInteraction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateInteractionData) => interactionApi.createInteraction(data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['interactions'] });
      queryClient.invalidateQueries({ queryKey: ['customer-interactions', variables.customer_id] });
      queryClient.invalidateQueries({ queryKey: ['customer-summary', variables.customer_id] });
    },
  });
}
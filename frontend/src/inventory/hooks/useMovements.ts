import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { movementApi } from '../api/movementApi';
import { MovementFilters, CreateMovementData } from '../types/movement';

export function useStockMovements(filters: MovementFilters = {}) {
  return useQuery({
    queryKey: ['stock-movements', filters],
    queryFn: () => movementApi.getMovements(filters),
  });
}

export function useItemMovements(itemId: string) {
  return useQuery({
    queryKey: ['item-movements', itemId],
    queryFn: () => movementApi.getItemMovements(itemId),
    enabled: !!itemId,
  });
}

export function useCreateMovement() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateMovementData) => movementApi.createMovement(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stock-movements'] });
      queryClient.invalidateQueries({ queryKey: ['items'] });
      queryClient.invalidateQueries({ queryKey: ['low-stock-items'] });
    },
  });
}
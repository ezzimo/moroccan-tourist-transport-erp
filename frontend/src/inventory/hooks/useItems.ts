import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { itemApi } from '../api/itemApi';
import { ItemFilters, CreateItemData, StockAdjustmentData } from '../types/item';

export function useItems(filters: ItemFilters = {}) {
  return useQuery({
    queryKey: ['items', filters],
    queryFn: () => itemApi.getItems(filters),
  });
}

export function useItem(id: string) {
  return useQuery({
    queryKey: ['item', id],
    queryFn: () => itemApi.getItem(id),
    enabled: !!id,
  });
}

export function useLowStockItems() {
  return useQuery({
    queryKey: ['low-stock-items'],
    queryFn: () => itemApi.getLowStockItems(),
  });
}

export function useCreateItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateItemData) => itemApi.createItem(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
      queryClient.invalidateQueries({ queryKey: ['low-stock-items'] });
    },
  });
}

export function useUpdateItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateItemData> }) =>
      itemApi.updateItem(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
      queryClient.invalidateQueries({ queryKey: ['item', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['low-stock-items'] });
    },
  });
}

export function useAdjustStock() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: StockAdjustmentData }) =>
      itemApi.adjustStock(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
      queryClient.invalidateQueries({ queryKey: ['item', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['stock-movements'] });
      queryClient.invalidateQueries({ queryKey: ['low-stock-items'] });
    },
  });
}
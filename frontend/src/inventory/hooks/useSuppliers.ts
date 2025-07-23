import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { supplierApi } from '../api/supplierApi';
import { CreateSupplierData } from '../types/supplier';

export function useSuppliers(filters: any = {}) {
  return useQuery({
    queryKey: ['suppliers', filters],
    queryFn: () => supplierApi.getSuppliers(filters),
  });
}

export function useSupplier(id: string) {
  return useQuery({
    queryKey: ['supplier', id],
    queryFn: () => supplierApi.getSupplier(id),
    enabled: !!id,
  });
}

export function useCreateSupplier() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateSupplierData) => supplierApi.createSupplier(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suppliers'] });
    },
  });
}

export function useUpdateSupplier() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateSupplierData> }) =>
      supplierApi.updateSupplier(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['suppliers'] });
      queryClient.invalidateQueries({ queryKey: ['supplier', variables.id] });
    },
  });
}
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { paymentApi } from '../api/paymentApi';
import { PaymentFilters, CreatePaymentData, ReconcilePaymentsData } from '../types/payment';

export function usePayments(filters: PaymentFilters = {}) {
  return useQuery({
    queryKey: ['payments', filters],
    queryFn: () => paymentApi.getPayments(filters),
  });
}

export function usePayment(id: string) {
  return useQuery({
    queryKey: ['payment', id],
    queryFn: () => paymentApi.getPayment(id),
    enabled: !!id,
  });
}

export function useCreatePayment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreatePaymentData) => paymentApi.createPayment(data),
    retry: false,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payments'] });
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
    },
  });
}

export function useConfirmPayment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => paymentApi.confirmPayment(id),
    retry: false,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payments'] });
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
    },
  });
}

export function useReconcilePayments() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ReconcilePaymentsData) => paymentApi.reconcilePayments(data),
    retry: false,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payments'] });
    },
  });
}
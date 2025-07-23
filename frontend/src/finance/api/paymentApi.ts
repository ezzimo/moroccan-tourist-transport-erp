import { apiClient } from '../../api/client';
import {
  Payment,
  CreatePaymentData,
  PaymentFilters,
  ReconcilePaymentsData,
} from '../types/payment';

export const paymentApi = {
  getPayments: async (filters: PaymentFilters = {}) => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/payments/?${params}`);
    return response.data;
  },

  createPayment: async (data: CreatePaymentData): Promise<Payment> => {
    const response = await apiClient.post('/payments/', data);
    return response.data;
  },

  confirmPayment: async (id: string): Promise<Payment> => {
    const response = await apiClient.post(`/payments/${id}/confirm`);
    return response.data;
  },

  reconcilePayments: async (data: ReconcilePaymentsData): Promise<{ message: string }> => {
    const response = await apiClient.post('/payments/reconcile', data);
    return response.data;
  },

  getPayment: async (id: string): Promise<Payment> => {
    const response = await apiClient.get(`/payments/${id}`);
    return response.data;
  },
};
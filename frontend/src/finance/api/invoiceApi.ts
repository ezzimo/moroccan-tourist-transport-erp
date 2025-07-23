import { apiClient } from '../../api/client';
import {
  Invoice,
  InvoicesResponse,
  InvoiceFilters,
  CreateInvoiceData,
  GenerateInvoiceData,
} from '../types/invoice';

export const invoiceApi = {
  getInvoices: async (filters: InvoiceFilters = {}): Promise<InvoicesResponse> => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/invoices/?${params}`);
    return response.data;
  },

  getInvoice: async (id: string): Promise<Invoice> => {
    const response = await apiClient.get(`/invoices/${id}`);
    return response.data;
  },

  createInvoice: async (data: CreateInvoiceData): Promise<Invoice> => {
    const response = await apiClient.post('/invoices/', data);
    return response.data;
  },

  generateInvoice: async (data: GenerateInvoiceData): Promise<Invoice> => {
    const response = await apiClient.post('/invoices/generate', data);
    return response.data;
  },

  sendInvoice: async (id: string): Promise<{ message: string }> => {
    const response = await apiClient.post(`/invoices/${id}/send`);
    return response.data;
  },

  downloadInvoicePDF: async (id: string): Promise<Blob> => {
    const response = await apiClient.get(`/invoices/${id}/pdf`, {
      responseType: 'blob',
    });
    return response.data;
  },

  updateInvoice: async (id: string, data: Partial<CreateInvoiceData>): Promise<Invoice> => {
    const response = await apiClient.put(`/invoices/${id}`, data);
    return response.data;
  },

  deleteInvoice: async (id: string): Promise<void> => {
    await apiClient.delete(`/invoices/${id}`);
  },
};
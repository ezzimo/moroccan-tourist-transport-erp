import { apiClient } from '../../api/client';
import {
  Supplier,
  SuppliersResponse,
  CreateSupplierData,
} from '../types/supplier';

export const supplierApi = {
  getSuppliers: async (filters: any = {}): Promise<SuppliersResponse> => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/suppliers?${params}`);
    return response.data;
  },

  getSupplier: async (id: string): Promise<Supplier> => {
    const response = await apiClient.get(`/suppliers/${id}`);
    return response.data;
  },

  createSupplier: async (data: CreateSupplierData): Promise<Supplier> => {
    const response = await apiClient.post('/suppliers', data);
    return response.data;
  },

  updateSupplier: async (id: string, data: Partial<CreateSupplierData>): Promise<Supplier> => {
    const response = await apiClient.put(`/suppliers/${id}`, data);
    return response.data;
  },

  deleteSupplier: async (id: string): Promise<void> => {
    await apiClient.delete(`/suppliers/${id}`);
  },
};
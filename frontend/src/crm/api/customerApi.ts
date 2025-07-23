import { apiClient } from '../../api/client';
import {
  Customer,
  CustomerSummary,
  CustomersResponse,
  CustomerFilters,
  CreateCustomerData,
} from '../types/customer';

export const customerApi = {
  getCustomers: async (filters: CustomerFilters = {}): Promise<CustomersResponse> => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        if (Array.isArray(value)) {
          value.forEach(v => params.append(key, v));
        } else {
          params.append(key, value.toString());
        }
      }
    });

    const response = await apiClient.get(`/customers/?${params}`);
    return response.data;
  },

  getCustomer: async (id: string): Promise<Customer> => {
    const response = await apiClient.get(`/customers/${id}`);
    return response.data;
  },

  getCustomerSummary: async (id: string): Promise<CustomerSummary> => {
    const response = await apiClient.get(`/customers/${id}/summary`);
    return response.data;
  },

  createCustomer: async (data: CreateCustomerData): Promise<Customer> => {
    const response = await apiClient.post('/customers/', data);
    return response.data;
  },

  updateCustomer: async (id: string, data: Partial<CreateCustomerData>): Promise<Customer> => {
    const response = await apiClient.put(`/customers/${id}`, data);
    return response.data;
  },

  deleteCustomer: async (id: string): Promise<void> => {
    await apiClient.delete(`/customers/${id}`);
  },
};
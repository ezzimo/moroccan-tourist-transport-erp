import { apiClient } from '../../api/client';
import {
  Expense,
  CreateExpenseData,
  ExpenseFilters,
  ApproveExpenseData,
} from '../types/expense';

export const expenseApi = {
  getExpenses: async (filters: ExpenseFilters = {}) => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/expenses/?${params}`);
    return response.data;
  },

  createExpense: async (data: CreateExpenseData): Promise<Expense> => {
    if (data.receipt_file) {
      const formData = new FormData();
      Object.entries(data).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (key === 'receipt_file') {
            formData.append('receipt_file', value as File);
          } else {
            formData.append(key, value.toString());
          }
        }
      });

      const response = await apiClient.post('/expenses/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } else {
      const response = await apiClient.post('/expenses/', data);
      return response.data;
    }
  },

  approveExpense: async (id: string, data: ApproveExpenseData): Promise<Expense> => {
    const response = await apiClient.post(`/expenses/${id}/approve`, data);
    return response.data;
  },

  getExpense: async (id: string): Promise<Expense> => {
    const response = await apiClient.get(`/expenses/${id}`);
    return response.data;
  },

  updateExpense: async (id: string, data: Partial<CreateExpenseData>): Promise<Expense> => {
    const response = await apiClient.put(`/expenses/${id}`, data);
    return response.data;
  },
};
import { apiClient } from '../../api/client';
import {
  InventoryItem,
  ItemsResponse,
  ItemFilters,
  CreateItemData,
  StockAdjustmentData,
} from '../types/item';

export const itemApi = {
  getItems: async (filters: ItemFilters = {}): Promise<ItemsResponse> => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/items?${params}`);
    return response.data;
  },

  getItem: async (id: string): Promise<InventoryItem> => {
    const response = await apiClient.get(`/items/${id}`);
    return response.data;
  },

  createItem: async (data: CreateItemData): Promise<InventoryItem> => {
    const response = await apiClient.post('/items', data);
    return response.data;
  },

  updateItem: async (id: string, data: Partial<CreateItemData>): Promise<InventoryItem> => {
    const response = await apiClient.put(`/items/${id}`, data);
    return response.data;
  },

  adjustStock: async (id: string, data: StockAdjustmentData): Promise<InventoryItem> => {
    const response = await apiClient.post(`/items/${id}/adjust-stock`, data);
    return response.data;
  },

  deleteItem: async (id: string): Promise<void> => {
    await apiClient.delete(`/items/${id}`);
  },

  getLowStockItems: async (): Promise<InventoryItem[]> => {
    const response = await apiClient.get('/items/low-stock');
    return response.data;
  },
};
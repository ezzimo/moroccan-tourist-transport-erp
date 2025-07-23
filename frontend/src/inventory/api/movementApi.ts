import { apiClient } from '../../api/client';
import {
  StockMovement,
  MovementsResponse,
  MovementFilters,
  CreateMovementData,
} from '../types/movement';

export const movementApi = {
  getMovements: async (filters: MovementFilters = {}): Promise<MovementsResponse> => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/movements?${params}`);
    return response.data;
  },

  createMovement: async (data: CreateMovementData): Promise<StockMovement> => {
    const response = await apiClient.post('/movements', data);
    return response.data;
  },

  getItemMovements: async (itemId: string): Promise<StockMovement[]> => {
    const response = await apiClient.get(`/movements?item_id=${itemId}`);
    return response.data.items;
  },
};
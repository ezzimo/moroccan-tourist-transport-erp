import { apiClient } from '../../api/client';
import {
  PurchaseOrder,
  PurchaseOrdersResponse,
  CreatePurchaseOrderData,
  ReceiveItemsData,
} from '../types/purchase';

export const purchaseApi = {
  getPurchaseOrders: async (filters: any = {}): Promise<PurchaseOrdersResponse> => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/purchase-orders?${params}`);
    return response.data;
  },

  getPurchaseOrder: async (id: string): Promise<PurchaseOrder> => {
    const response = await apiClient.get(`/purchase-orders/${id}`);
    return response.data;
  },

  createPurchaseOrder: async (data: CreatePurchaseOrderData): Promise<PurchaseOrder> => {
    const response = await apiClient.post('/purchase-orders', data);
    return response.data;
  },

  approvePurchaseOrder: async (id: string): Promise<PurchaseOrder> => {
    const response = await apiClient.post(`/purchase-orders/${id}/approve`);
    return response.data;
  },

  receiveItems: async (id: string, data: ReceiveItemsData): Promise<PurchaseOrder> => {
    const response = await apiClient.post(`/purchase-orders/${id}/receive`, data);
    return response.data;
  },

  deletePurchaseOrder: async (id: string): Promise<void> => {
    await apiClient.delete(`/purchase-orders/${id}`);
  },
};
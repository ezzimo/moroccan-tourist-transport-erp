import { apiClient } from '../../api/client';
import {
  ReservationItem,
  CreateReservationItemData,
} from '../types/reservation';

export const reservationApi = {
  getReservationItems: async (bookingId: string): Promise<ReservationItem[]> => {
    const response = await apiClient.get(`/reservation-items/booking/${bookingId}`);
    return response.data;
  },

  createReservationItem: async (data: CreateReservationItemData): Promise<ReservationItem> => {
    const response = await apiClient.post('/reservation-items/', data);
    return response.data;
  },

  updateReservationItem: async (id: string, data: Partial<CreateReservationItemData>): Promise<ReservationItem> => {
    const response = await apiClient.put(`/reservation-items/${id}`, data);
    return response.data;
  },

  deleteReservationItem: async (id: string): Promise<void> => {
    await apiClient.delete(`/reservation-items/${id}`);
  },
};
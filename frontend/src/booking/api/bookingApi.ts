import { apiClient } from '../../api/client';
import {
  Booking,
  BookingsResponse,
  BookingFilters,
  CreateBookingData,
  ConfirmBookingData,
  CancelBookingData,
} from '../types/booking';

export const bookingApi = {
  getBookings: async (filters: BookingFilters = {}): Promise<BookingsResponse> => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/bookings/?${params}`);
    return response.data;
  },

  getBooking: async (id: string): Promise<Booking> => {
    const response = await apiClient.get(`/bookings/${id}`);
    return response.data;
  },

  createBooking: async (data: CreateBookingData): Promise<Booking> => {
    const response = await apiClient.post('/bookings/', data);
    return response.data;
  },

  confirmBooking: async (id: string, data: ConfirmBookingData): Promise<Booking> => {
    const response = await apiClient.post(`/bookings/${id}/confirm`, data);
    return response.data;
  },

  cancelBooking: async (id: string, data: CancelBookingData): Promise<Booking> => {
    const response = await apiClient.post(`/bookings/${id}/cancel`, data);
    return response.data;
  },

  downloadVoucher: async (id: string): Promise<Blob> => {
    const response = await apiClient.get(`/bookings/${id}/voucher`, {
      responseType: 'blob',
    });
    return response.data;
  },

  updateBooking: async (id: string, data: Partial<CreateBookingData>): Promise<Booking> => {
    const response = await apiClient.put(`/bookings/${id}`, data);
    return response.data;
  },
};
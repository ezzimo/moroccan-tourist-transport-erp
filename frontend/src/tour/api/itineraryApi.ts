import { apiClient } from '../../api/client';
import {
  ItineraryItem,
  CreateItineraryItemData,
  DayItinerary,
  CompleteItineraryItemData,
} from '../types/itinerary';

export const itineraryApi = {
  getTourItinerary: async (tourInstanceId: string): Promise<ItineraryItem[]> => {
    const response = await apiClient.get(`/itinerary/tour/${tourInstanceId}`);
    return response.data;
  },

  getDayItinerary: async (tourInstanceId: string, dayNumber: number): Promise<DayItinerary> => {
    const response = await apiClient.get(`/itinerary/tour/${tourInstanceId}/day/${dayNumber}`);
    return response.data;
  },

  createItineraryItem: async (data: CreateItineraryItemData): Promise<ItineraryItem> => {
    const response = await apiClient.post('/itinerary/items', data);
    return response.data;
  },

  updateItineraryItem: async (id: string, data: Partial<CreateItineraryItemData>): Promise<ItineraryItem> => {
    const response = await apiClient.put(`/itinerary/items/${id}`, data);
    return response.data;
  },

  completeItineraryItem: async (id: string, data: CompleteItineraryItemData): Promise<ItineraryItem> => {
    const response = await apiClient.post(`/itinerary/items/${id}/complete`, data);
    return response.data;
  },

  reorderDayItems: async (tourInstanceId: string, dayNumber: number, itemIds: string[]): Promise<void> => {
    await apiClient.post(`/itinerary/tour/${tourInstanceId}/day/${dayNumber}/reorder`, itemIds);
  },

  deleteItineraryItem: async (id: string): Promise<void> => {
    await apiClient.delete(`/itinerary/items/${id}`);
  },
};
import { apiClient } from '../../api/client';
import {
  AvailabilityRequest,
  AvailabilityResponse,
} from '../types/availability';

export const availabilityApi = {
  checkAvailability: async (data: AvailabilityRequest): Promise<AvailabilityResponse> => {
    const response = await apiClient.post('/availability/check', data);
    return response.data;
  },

  getResourceAvailability: async (
    resourceType: string,
    startDate: string,
    endDate?: string
  ): Promise<AvailabilityResponse> => {
    const response = await apiClient.post('/availability/check', {
      resource_type: resourceType,
      start_date: startDate,
      end_date: endDate,
    });
    return response.data;
  },
};
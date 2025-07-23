import { useQuery } from '@tanstack/react-query';
import { availabilityApi } from '../api/availabilityApi';
import { AvailabilityRequest } from '../types/availability';

export function useAvailabilityCheck(data: AvailabilityRequest, enabled = true) {
  return useQuery({
    queryKey: ['availability-check', data],
    queryFn: () => availabilityApi.checkAvailability(data),
    enabled: enabled && !!data.start_date,
  });
}

export function useResourceAvailability(
  resourceType: string,
  startDate: string,
  endDate?: string,
  enabled = true
) {
  return useQuery({
    queryKey: ['resource-availability', resourceType, startDate, endDate],
    queryFn: () => availabilityApi.getResourceAvailability(resourceType, startDate, endDate),
    enabled: enabled && !!resourceType && !!startDate,
  });
}
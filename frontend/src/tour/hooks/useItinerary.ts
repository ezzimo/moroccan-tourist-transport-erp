import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { itineraryApi } from '../api/itineraryApi';
import { CreateItineraryItemData, CompleteItineraryItemData } from '../types/itinerary';

export function useTourItinerary(tourInstanceId: string) {
  return useQuery({
    queryKey: ['tour-itinerary', tourInstanceId],
    queryFn: () => itineraryApi.getTourItinerary(tourInstanceId),
    enabled: !!tourInstanceId,
  });
}

export function useDayItinerary(tourInstanceId: string, dayNumber: number) {
  return useQuery({
    queryKey: ['day-itinerary', tourInstanceId, dayNumber],
    queryFn: () => itineraryApi.getDayItinerary(tourInstanceId, dayNumber),
    enabled: !!tourInstanceId && dayNumber > 0,
  });
}

export function useCreateItineraryItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateItineraryItemData) => itineraryApi.createItineraryItem(data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tour-itinerary', variables.tour_instance_id] });
      queryClient.invalidateQueries({ queryKey: ['day-itinerary', variables.tour_instance_id, variables.day_number] });
    },
  });
}

export function useUpdateItineraryItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateItineraryItemData> }) =>
      itineraryApi.updateItineraryItem(id, data),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['tour-itinerary', result.tour_instance_id] });
      queryClient.invalidateQueries({ queryKey: ['day-itinerary', result.tour_instance_id, result.day_number] });
    },
  });
}

export function useCompleteItineraryItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: CompleteItineraryItemData }) =>
      itineraryApi.completeItineraryItem(id, data),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['tour-itinerary', result.tour_instance_id] });
      queryClient.invalidateQueries({ queryKey: ['day-itinerary', result.tour_instance_id, result.day_number] });
      queryClient.invalidateQueries({ queryKey: ['tour-instance', result.tour_instance_id] });
    },
  });
}

export function useReorderDayItems() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ tourInstanceId, dayNumber, itemIds }: { tourInstanceId: string; dayNumber: number; itemIds: string[] }) =>
      itineraryApi.reorderDayItems(tourInstanceId, dayNumber, itemIds),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tour-itinerary', variables.tourInstanceId] });
      queryClient.invalidateQueries({ queryKey: ['day-itinerary', variables.tourInstanceId, variables.dayNumber] });
    },
  });
}
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { reservationApi } from '../api/reservationApi';
import { CreateReservationItemData } from '../types/reservation';

export function useReservationItems(bookingId: string) {
  return useQuery({
    queryKey: ['reservation-items', bookingId],
    queryFn: () => reservationApi.getReservationItems(bookingId),
    enabled: !!bookingId,
  });
}

export function useCreateReservationItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateReservationItemData) => reservationApi.createReservationItem(data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['reservation-items', variables.booking_id] });
      queryClient.invalidateQueries({ queryKey: ['booking', variables.booking_id] });
    },
  });
}

export function useUpdateReservationItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateReservationItemData> }) =>
      reservationApi.updateReservationItem(id, data),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['reservation-items', result.booking_id] });
      queryClient.invalidateQueries({ queryKey: ['booking', result.booking_id] });
    },
  });
}

export function useDeleteReservationItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => reservationApi.deleteReservationItem(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reservation-items'] });
    },
  });
}
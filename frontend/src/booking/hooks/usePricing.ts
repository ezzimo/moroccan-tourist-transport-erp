import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { pricingApi } from '../api/pricingApi';
import { PricingRequest, DiscountRule } from '../types/pricing';

export function usePricingCalculation(data: PricingRequest, enabled = true) {
  return useQuery({
    queryKey: ['pricing-calculation', data],
    queryFn: () => pricingApi.calculatePricing(data),
    enabled: enabled && !!data.service_type && data.base_price > 0 && !!data.pax_count && !!data.start_date,
    retry: false, // Prevent cascading retries on invalid input
    refetchOnWindowFocus: false,
  });
}

export function useDiscountRules() {
  return useQuery({
    queryKey: ['discount-rules'],
    queryFn: () => pricingApi.getDiscountRules(),
  });
}

export function useCreateDiscountRule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<DiscountRule>) => pricingApi.createDiscountRule(data),
    retry: false,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['discount-rules'] });
    },
  });
}

export function useValidatePromoCode() {
  return useMutation({
    mutationFn: ({ code, bookingData }: { code: string; bookingData: Partial<PricingRequest> }) =>
      pricingApi.validatePromoCode(code, bookingData),
    retry: false,
  });
}
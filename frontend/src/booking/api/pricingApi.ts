import { apiClient } from '../../api/client';
import {
  PricingCalculation,
  PricingRequest,
  DiscountRule,
} from '../types/pricing';

export const pricingApi = {
  calculatePricing: async (data: PricingRequest): Promise<PricingCalculation> => {
    const response = await apiClient.post('/pricing/calculate', data);
    return response.data;
  },

  getDiscountRules: async (): Promise<DiscountRule[]> => {
    const response = await apiClient.get('/pricing/rules');
    return response.data;
  },

  createDiscountRule: async (data: Partial<DiscountRule>): Promise<DiscountRule> => {
    const response = await apiClient.post('/pricing/rules', data);
    return response.data;
  },

  updateDiscountRule: async (id: string, data: Partial<DiscountRule>): Promise<DiscountRule> => {
    const response = await apiClient.put(`/pricing/rules/${id}`, data);
    return response.data;
  },

  validatePromoCode: async (code: string, bookingData: Partial<PricingRequest>): Promise<{
    valid: boolean;
    discount_amount?: number;
    message?: string;
  }> => {
    const response = await apiClient.post('/pricing/validate-promo', {
      promo_code: code,
      ...bookingData,
    });
    return response.data;
  },
};
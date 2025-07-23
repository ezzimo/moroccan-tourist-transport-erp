export interface PricingCalculation {
  base_price: number;
  discount_amount: number;
  total_price: number;
  applied_rules: PricingRule[];
  currency: string;
}

export interface PricingRule {
  rule_id: string;
  rule_name: string;
  discount_type: string;
  discount_amount: number;
}

export interface PricingRequest {
  service_type: string;
  base_price: number;
  pax_count: number;
  start_date: string;
  end_date?: string;
  customer_id?: string;
  promo_code?: string;
}

export interface DiscountRule {
  id: string;
  name: string;
  description?: string;
  code?: string;
  discount_type: 'Percentage' | 'Fixed Amount' | 'Buy X Get Y' | 'Early Bird' | 'Group Discount';
  discount_percentage?: number;
  discount_amount?: number;
  conditions: Record<string, any>;
  valid_from: string;
  valid_until: string;
  max_uses?: number;
  max_uses_per_customer: number;
  current_uses: number;
  priority: number;
  is_active: boolean;
  is_combinable: boolean;
  created_at: string;
  updated_at: string;
}
export interface FinancialDashboard {
  total_revenue_mtd: number;
  total_expenses_mtd: number;
  net_profit_mtd: number;
  outstanding_invoices: number;
  overdue_amount: number;
  cash_flow_forecast: {
    next_30_days: number;
    next_60_days: number;
    next_90_days: number;
  };
  top_customers: Array<{
    customer_name: string;
    total_amount: number;
  }>;
  revenue_by_month: Array<{
    month: string;
    revenue: number;
    expenses: number;
    profit: number;
  }>;
}

export interface RevenueAnalytics {
  period_months: number;
  total_revenue: number;
  total_expenses: number;
  net_profit: number;
  profit_margin: number;
  by_month: Record<string, {
    revenue: number;
    expenses: number;
    profit: number;
  }>;
  by_service_type: Record<string, {
    revenue: number;
    bookings_count: number;
  }>;
  currency: string;
}

export interface TaxReport {
  id: string;
  report_number: string;
  tax_type: 'VAT' | 'INCOME_TAX' | 'CORPORATE_TAX';
  period_type: 'MONTHLY' | 'QUARTERLY' | 'YEARLY';
  period_start: string;
  period_end: string;
  total_revenue: number;
  total_expenses: number;
  total_vat_collected: number;
  total_vat_paid: number;
  net_vat_due: number;
  status: 'DRAFT' | 'GENERATED' | 'SUBMITTED' | 'ACCEPTED';
  generated_at?: string;
  submitted_at?: string;
  created_at: string;
}

export interface VATDeclaration {
  period_start: string;
  period_end: string;
  sales_vat: number;
  purchase_vat: number;
  net_vat: number;
  sales_breakdown: {
    standard_rate: number;
    reduced_rate: number;
  };
  purchase_breakdown: {
    deductible: number;
    non_deductible: number;
  };
}
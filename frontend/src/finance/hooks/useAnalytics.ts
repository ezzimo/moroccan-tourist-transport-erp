import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '../api/analyticsApi';

// --- Types only to help us reason locally; you can refine later if you like ---
type RawDashboard = {
  currency?: string;
  current_month?: {
    revenue?: number;      // amount
    expenses?: number;     // amount
    profit?: number;       // amount
    invoice_count?: number;
    expense_count?: number;
  };
  year_to_date?: unknown;

  outstanding?: {
    invoice_count?: number;
    total_amount?: number;   // amount expected by UI as "outstanding_invoices"
    overdue_count?: number;
    overdue_amount?: number; // amount expected by UI as "overdue_amount"
  };

  pending?: { expense_count?: number; total_amount?: number };

  // Some future backend might add this; if not, we synthesize below.
  cash_flow_forecast?: {
    next_30_days?: number;
    next_60_days?: number;
    next_90_days?: number;
  };

  top_customers?: Array<{ customer_name: string; total_amount: number }>;
};

type NormalizedDashboard = {
  total_revenue_mtd: number;
  net_profit_mtd: number;
  outstanding_invoices: number;
  overdue_amount: number;
  top_customers: Array<{ customer_name: string; total_amount: number }>;
  cash_flow_forecast: {
    next_30_days: number;
    next_60_days: number;
    next_90_days: number;
  };
};

type RawRevenue = {
  period?: { start_date?: string; end_date?: string };
  currency?: string;
  summary?: unknown;

  // Backend currently returns monthly_breakdown; UI expects by_month.
  monthly_breakdown?: any[];
  by_month?: any[];

  // UI is tolerant, but we also provide a consistent structure.
  forecast?: { next_30_days?: any[]; next_12_months?: any[] };
};

type NormalizedRevenue = RawRevenue & {
  by_month: any[];
  forecast: { next_30_days: any[]; next_12_months: any[] };
};

// --- Normalizers ---
function normalizeDashboard(raw: RawDashboard | undefined): NormalizedDashboard {
  const cm = raw?.current_month ?? {};
  const out = raw?.outstanding ?? {};
  return {
    total_revenue_mtd: Number(cm.revenue ?? 0),
    net_profit_mtd: Number(cm.profit ?? 0),
    outstanding_invoices: Number(out.total_amount ?? 0),
    overdue_amount: Number(out.overdue_amount ?? 0),
    top_customers: raw?.top_customers ?? [],
    cash_flow_forecast: {
      next_30_days: Number(raw?.cash_flow_forecast?.next_30_days ?? 0),
      next_60_days: Number(raw?.cash_flow_forecast?.next_60_days ?? 0),
      next_90_days: Number(raw?.cash_flow_forecast?.next_90_days ?? 0),
    },
  };
}

function normalizeRevenue(raw: RawRevenue | undefined): NormalizedRevenue {
  const byMonth = (raw?.by_month ?? raw?.monthly_breakdown ?? []) as any[];
  return {
    ...(raw ?? {}),
    by_month: byMonth,
    forecast: {
      next_30_days: raw?.forecast?.next_30_days ?? [],
      next_12_months: raw?.forecast?.next_12_months ?? [],
    },
  };
}

// --- Hooks ---
export function useFinancialDashboard() {
  return useQuery({
    queryKey: ['financial-dashboard'],
    queryFn: async () => {
      const raw = (await analyticsApi.getDashboard()) as RawDashboard;
      return normalizeDashboard(raw);
    },
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });
}

export function useRevenueAnalytics(periodMonths = 12, currency?: string) {
  return useQuery({
    queryKey: ['revenue-analytics', periodMonths, currency],
    queryFn: async () => {
      const raw = (await analyticsApi.getRevenueAnalytics(periodMonths, currency)) as RawRevenue;
      return normalizeRevenue(raw);
    },
  });
}

export function useTaxReports() {
  return useQuery({
    queryKey: ['tax-reports'],
    queryFn: () => analyticsApi.getTaxReports(),
  });
}

export function useVATDeclaration(periodStart: string, periodEnd: string) {
  return useQuery({
    queryKey: ['vat-declaration', periodStart, periodEnd],
    queryFn: () => analyticsApi.getVATDeclaration(periodStart, periodEnd),
    enabled: !!periodStart && !!periodEnd,
  });
}

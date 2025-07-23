import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '../api/analyticsApi';

export function useFinancialDashboard() {
  return useQuery({
    queryKey: ['financial-dashboard'],
    queryFn: () => analyticsApi.getDashboard(),
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });
}

export function useRevenueAnalytics(periodMonths = 12, currency?: string) {
  return useQuery({
    queryKey: ['revenue-analytics', periodMonths, currency],
    queryFn: () => analyticsApi.getRevenueAnalytics(periodMonths, currency),
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
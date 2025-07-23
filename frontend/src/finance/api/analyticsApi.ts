import { apiClient } from '../../api/client';
import {
  FinancialDashboard,
  RevenueAnalytics,
  TaxReport,
  VATDeclaration,
} from '../types/analytics';

export const analyticsApi = {
  getDashboard: async (): Promise<FinancialDashboard> => {
    const response = await apiClient.get('/analytics/dashboard');
    return response.data;
  },

  getRevenueAnalytics: async (periodMonths = 12, currency?: string): Promise<RevenueAnalytics> => {
    const params: any = { period_months: periodMonths };
    if (currency) params.currency = currency;

    const response = await apiClient.get('/analytics/revenue', { params });
    return response.data;
  },

  getTaxReports: async (): Promise<TaxReport[]> => {
    const response = await apiClient.get('/tax-reports');
    return response.data;
  },

  generateTaxReport: async (data: {
    tax_type: 'VAT' | 'INCOME_TAX' | 'CORPORATE_TAX';
    period_type: 'MONTHLY' | 'QUARTERLY' | 'YEARLY';
    period_start: string;
    period_end: string;
    include_draft_transactions?: boolean;
    notes?: string;
  }): Promise<TaxReport> => {
    const response = await apiClient.post('/tax-reports/generate', data);
    return response.data;
  },

  getVATDeclaration: async (periodStart: string, periodEnd: string): Promise<VATDeclaration> => {
    const response = await apiClient.get('/tax-reports/vat/declaration', {
      params: {
        period_start: periodStart,
        period_end: periodEnd,
      },
    });
    return response.data;
  },

  exportProfitLoss: async (startDate: string, endDate: string, format = 'pdf'): Promise<Blob> => {
    const response = await apiClient.get('/analytics/export/profit-loss', {
      params: {
        start_date: startDate,
        end_date: endDate,
        format,
      },
      responseType: 'blob',
    });
    return response.data;
  },
};
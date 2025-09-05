import React from 'react';
import { TrendingUp, DollarSign, FileText, AlertTriangle } from 'lucide-react';
import { useFinancialDashboard, useRevenueAnalytics } from '../hooks/useAnalytics';
import LoadingSpinner from '../../components/LoadingSpinner';
import RevenueChart from '../components/RevenueChart';
import { formatMoney } from '../../utils/number';

export default function FinancialDashboardPage() {
  const { data: dashboard, isLoading: dashboardLoading } = useFinancialDashboard();
  const { data: revenueAnalytics, isLoading: analyticsLoading } = useRevenueAnalytics(12);

  if (dashboardLoading || analyticsLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Financial Dashboard</h1>
        <p className="text-gray-600">Overview of financial performance and key metrics</p>
      </div>

      {/* Key Metrics */}
      {dashboard && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-6 rounded-lg border">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-green-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Revenue (MTD)</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatMoney(dashboard?.total_revenue_mtd)}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg border">
            <div className="flex items-center">
              <DollarSign className="h-8 w-8 text-blue-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Net Profit (MTD)</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatMoney(dashboard?.net_profit_mtd)}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg border">
            <div className="flex items-center">
              <FileText className="h-8 w-8 text-yellow-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Outstanding</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatMoney(dashboard?.outstanding_invoices)}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg border">
            <div className="flex items-center">
              <AlertTriangle className="h-8 w-8 text-red-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Overdue</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatMoney(dashboard?.overdue_amount)}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Revenue Chart */}
      {revenueAnalytics && (
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Revenue Trend</h3>
          <RevenueChart data={revenueAnalytics.by_month} />
        </div>
      )}

      {/* Cash Flow Forecast */}
      {dashboard && (
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Cash Flow Forecast</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm font-medium text-blue-600">Next 30 Days</p>
              <p className="text-2xl font-bold text-blue-900">
                {formatMoney(dashboard?.cash_flow_forecast?.next_30_days)}
              </p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <p className="text-sm font-medium text-green-600">Next 60 Days</p>
              <p className="text-2xl font-bold text-green-900">
                {formatMoney(dashboard?.cash_flow_forecast?.next_60_days)}
              </p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <p className="text-sm font-medium text-purple-600">Next 90 Days</p>
              <p className="text-2xl font-bold text-purple-900">
                {formatMoney(dashboard?.cash_flow_forecast?.next_90_days)}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Top Customers */}
      {dashboard && dashboard.top_customers.length > 0 && (
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Top Customers</h3>
          <div className="space-y-3">
            {dashboard.top_customers.map((customer, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-900">{customer.customer_name}</span>
                <span className="text-lg font-bold text-green-600">
                  {formatMoney(customer?.total_amount)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
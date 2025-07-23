import React from 'react';
import { X } from 'lucide-react';
import { InvoiceFilters } from '../types/invoice';

interface InvoiceFiltersPanelProps {
  filters: InvoiceFilters;
  onFiltersChange: (filters: Partial<InvoiceFilters>) => void;
  onClose: () => void;
}

export default function InvoiceFiltersPanel({
  filters,
  onFiltersChange,
  onClose,
}: InvoiceFiltersPanelProps) {
  const statuses = ['DRAFT', 'SENT', 'PAID', 'OVERDUE', 'CANCELLED'];
  const paymentStatuses = ['PENDING', 'PARTIAL', 'PAID', 'REFUNDED'];
  const currencies = ['MAD', 'EUR', 'USD'];

  return (
    <div className="bg-gray-50 border rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900">Filters</h3>
        <button
          onClick={onClose}
          className="p-1 text-gray-400 hover:text-gray-600"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Status
          </label>
          <select
            value={filters.status || ''}
            onChange={(e) => onFiltersChange({ status: e.target.value || undefined })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">All Statuses</option>
            {statuses.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Payment Status
          </label>
          <select
            value={filters.payment_status || ''}
            onChange={(e) => onFiltersChange({ payment_status: e.target.value || undefined })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">All Payment Statuses</option>
            {paymentStatuses.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Currency
          </label>
          <select
            value={filters.currency || ''}
            onChange={(e) => onFiltersChange({ currency: e.target.value || undefined })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">All Currencies</option>
            {currencies.map((currency) => (
              <option key={currency} value={currency}>
                {currency}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Issue Date From
          </label>
          <input
            type="date"
            value={filters.issue_date_from || ''}
            onChange={(e) => onFiltersChange({ issue_date_from: e.target.value || undefined })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          />
        </div>
      </div>

      <div className="flex items-center gap-4 mt-4">
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={filters.is_overdue || false}
            onChange={(e) => onFiltersChange({ is_overdue: e.target.checked || undefined })}
            className="rounded border-gray-300 text-orange-600 focus:ring-orange-500"
          />
          <span className="ml-2 text-sm text-gray-700">Overdue invoices only</span>
        </label>

        <button
          onClick={() => onFiltersChange({ 
            status: undefined, 
            payment_status: undefined, 
            currency: undefined,
            issue_date_from: undefined,
            issue_date_to: undefined,
            is_overdue: undefined 
          })}
          className="text-sm text-orange-600 hover:text-orange-700"
        >
          Clear filters
        </button>
      </div>
    </div>
  );
}
import React from 'react';
import { X, Package } from 'lucide-react';
import { BookingFilters } from '../types/booking';

interface BookingFiltersPanelProps {
  filters: BookingFilters;
  onFiltersChange: (filters: Partial<BookingFilters>) => void;
  onClose: () => void;
}

export default function BookingFiltersPanel({
  filters,
  onFiltersChange,
  onClose,
}: BookingFiltersPanelProps) {
  const statuses = ['Pending', 'Confirmed', 'Cancelled', 'Refunded', 'Expired'];
  const serviceTypes = ['Tour', 'Transfer', 'Custom Package', 'Accommodation', 'Activity'];
  const paymentStatuses = ['Pending', 'Partial', 'Paid', 'Failed', 'Refunded'];

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
            Service Type
          </label>
          <select
            value={filters.service_type || ''}
            onChange={(e) => onFiltersChange({ service_type: e.target.value || undefined })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">All Service Types</option>
            {serviceTypes.map((type) => (
              <option key={type} value={type}>
                {type}
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
            Start Date From
          </label>
          <input
            type="date"
            value={filters.start_date_from || ''}
            onChange={(e) => onFiltersChange({ start_date_from: e.target.value || undefined })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          />
        </div>
      </div>

      <div className="flex items-center gap-4 mt-4">
        <button
          onClick={() => onFiltersChange({ 
            status: undefined, 
            service_type: undefined, 
            payment_status: undefined,
            start_date_from: undefined,
            start_date_to: undefined
          })}
          className="text-sm text-orange-600 hover:text-orange-700"
        >
          Clear filters
        </button>
      </div>
    </div>
  );
}
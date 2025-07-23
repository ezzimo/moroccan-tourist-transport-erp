import React from 'react';
import { X } from 'lucide-react';
import { CustomerFilters } from '../types/customer';

interface CustomerFiltersPanelProps {
  filters: CustomerFilters;
  onFiltersChange: (filters: Partial<CustomerFilters>) => void;
  onClose: () => void;
}

export default function CustomerFiltersPanel({
  filters,
  onFiltersChange,
  onClose,
}: CustomerFiltersPanelProps) {
  const contactTypes = ['Individual', 'Corporate'];
  const loyaltyStatuses = ['New', 'Bronze', 'Silver', 'Gold', 'Platinum', 'VIP'];
  const regions = ['Casablanca', 'Rabat', 'Marrakech', 'Fez', 'Tangier', 'Agadir'];

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

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Contact Type
          </label>
          <select
            value={filters.contact_type || ''}
            onChange={(e) => onFiltersChange({ contact_type: e.target.value || undefined })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">All Types</option>
            {contactTypes.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Loyalty Status
          </label>
          <select
            value={filters.loyalty_status || ''}
            onChange={(e) => onFiltersChange({ loyalty_status: e.target.value || undefined })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">All Statuses</option>
            {loyaltyStatuses.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Region
          </label>
          <select
            value={filters.region || ''}
            onChange={(e) => onFiltersChange({ region: e.target.value || undefined })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">All Regions</option>
            {regions.map((region) => (
              <option key={region} value={region}>
                {region}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex items-center gap-4 mt-4">
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={filters.is_active !== false}
            onChange={(e) => onFiltersChange({ is_active: e.target.checked ? undefined : false })}
            className="rounded border-gray-300 text-orange-600 focus:ring-orange-500"
          />
          <span className="ml-2 text-sm text-gray-700">Active customers only</span>
        </label>

        <button
          onClick={() => onFiltersChange({ 
            contact_type: undefined, 
            loyalty_status: undefined, 
            region: undefined, 
            is_active: undefined 
          })}
          className="text-sm text-orange-600 hover:text-orange-700"
        >
          Clear filters
        </button>
      </div>
    </div>
  );
}
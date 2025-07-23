import React from 'react';
import { X } from 'lucide-react';
import { ItemFilters } from '../types/item';

interface ItemFiltersPanelProps {
  filters: ItemFilters;
  onFiltersChange: (filters: Partial<ItemFilters>) => void;
  onClose: () => void;
}

export default function ItemFiltersPanel({
  filters,
  onFiltersChange,
  onClose,
}: ItemFiltersPanelProps) {
  const categories = [
    'ENGINE_PARTS',
    'TIRES',
    'FLUIDS',
    'BRAKE_PARTS',
    'ELECTRICAL',
    'BODY_PARTS',
    'TOOLS',
    'CONSUMABLES',
    'OTHER'
  ];
  const statuses = ['ACTIVE', 'INACTIVE', 'DISCONTINUED'];

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
            Category
          </label>
          <select
            value={filters.category || ''}
            onChange={(e) => onFiltersChange({ category: e.target.value || undefined })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">All Categories</option>
            {categories.map((category) => (
              <option key={category} value={category}>
                {category.replace('_', ' ')}
              </option>
            ))}
          </select>
        </div>

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
            Warehouse Location
          </label>
          <input
            type="text"
            value={filters.warehouse_location || ''}
            onChange={(e) => onFiltersChange({ warehouse_location: e.target.value || undefined })}
            placeholder="Filter by location"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            Stock Status
          </label>
          <div className="space-y-1">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={filters.is_low_stock || false}
                onChange={(e) => onFiltersChange({ is_low_stock: e.target.checked || undefined })}
                className="rounded border-gray-300 text-orange-600 focus:ring-orange-500"
              />
              <span className="ml-2 text-sm text-gray-700">Low stock only</span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={filters.is_critical || false}
                onChange={(e) => onFiltersChange({ is_critical: e.target.checked || undefined })}
                className="rounded border-gray-300 text-orange-600 focus:ring-orange-500"
              />
              <span className="ml-2 text-sm text-gray-700">Critical items only</span>
            </label>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4 mt-4">
        <button
          onClick={() => onFiltersChange({ 
            category: undefined, 
            status: undefined, 
            warehouse_location: undefined,
            is_low_stock: undefined,
            is_critical: undefined
          })}
          className="text-sm text-orange-600 hover:text-orange-700"
        >
          Clear filters
        </button>
      </div>
    </div>
  );
}
import React from 'react';
import { X } from 'lucide-react';
import { VehicleFilters } from '../types/vehicle';

interface VehicleFiltersPanelProps {
  filters: VehicleFilters;
  onFiltersChange: (filters: Partial<VehicleFilters>) => void;
  onClose: () => void;
}

export default function VehicleFiltersPanel({
  filters,
  onFiltersChange,
  onClose,
}: VehicleFiltersPanelProps) {
  const vehicleTypes = ['Bus', 'Minibus', 'SUV/4x4', 'Sedan', 'Van', 'Motorcycle'];
  const statuses = ['Available', 'In Use', 'Under Maintenance', 'Out of Service', 'Retired'];
  const fuelTypes = ['Gasoline', 'Diesel', 'Hybrid', 'Electric', 'LPG'];
  const brands = ['Mercedes', 'Volkswagen', 'Ford', 'Toyota', 'Renault', 'Peugeot'];

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
            Vehicle Type
          </label>
          <select
            value={filters.vehicle_type || ''}
            onChange={(e) => onFiltersChange({ vehicle_type: e.target.value || undefined })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">All Types</option>
            {vehicleTypes.map((type) => (
              <option key={type} value={type}>
                {type}
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
            Fuel Type
          </label>
          <select
            value={filters.fuel_type || ''}
            onChange={(e) => onFiltersChange({ fuel_type: e.target.value || undefined })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">All Fuel Types</option>
            {fuelTypes.map((fuel) => (
              <option key={fuel} value={fuel}>
                {fuel}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Brand
          </label>
          <select
            value={filters.brand || ''}
            onChange={(e) => onFiltersChange({ brand: e.target.value || undefined })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">All Brands</option>
            {brands.map((brand) => (
              <option key={brand} value={brand}>
                {brand}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Seating Capacity Range
          </label>
          <div className="flex gap-2">
            <input
              type="number"
              placeholder="Min"
              value={filters.min_seating_capacity || ''}
              onChange={(e) => onFiltersChange({ min_seating_capacity: e.target.value ? parseInt(e.target.value) : undefined })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
            />
            <input
              type="number"
              placeholder="Max"
              value={filters.max_seating_capacity || ''}
              onChange={(e) => onFiltersChange({ max_seating_capacity: e.target.value ? parseInt(e.target.value) : undefined })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Year Range
          </label>
          <div className="flex gap-2">
            <input
              type="number"
              placeholder="From"
              value={filters.min_year || ''}
              onChange={(e) => onFiltersChange({ min_year: e.target.value ? parseInt(e.target.value) : undefined })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
            />
            <input
              type="number"
              placeholder="To"
              value={filters.max_year || ''}
              onChange={(e) => onFiltersChange({ max_year: e.target.value ? parseInt(e.target.value) : undefined })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
            />
          </div>
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
          <span className="ml-2 text-sm text-gray-700">Active vehicles only</span>
        </label>

        <button
          onClick={() => onFiltersChange({ 
            vehicle_type: undefined, 
            status: undefined, 
            fuel_type: undefined,
            brand: undefined,
            min_seating_capacity: undefined,
            max_seating_capacity: undefined,
            min_year: undefined,
            max_year: undefined,
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
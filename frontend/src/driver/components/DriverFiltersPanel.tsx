import React from 'react';
import { X } from 'lucide-react';
import { DriverFilters } from '../types/driver';

interface DriverFiltersPanelProps {
  filters: DriverFilters;
  onFiltersChange: (filters: Partial<DriverFilters>) => void;
  onClose: () => void;
}

export default function DriverFiltersPanel({
  filters,
  onFiltersChange,
  onClose,
}: DriverFiltersPanelProps) {
  const statuses = ['Active', 'On Leave', 'In Training', 'Suspended', 'Terminated', 'Retired'];
  const employmentTypes = ['Permanent', 'Seasonal', 'Contract', 'Freelance'];
  const licenseTypes = ['Category B', 'Category C', 'Category D', 'Category D1', 'Professional'];
  const languages = ['Arabic', 'French', 'English', 'Spanish', 'German', 'Italian'];

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
            Employment Type
          </label>
          <select
            value={filters.employment_type || ''}
            onChange={(e) => onFiltersChange({ employment_type: e.target.value || undefined })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">All Types</option>
            {employmentTypes.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            License Type
          </label>
          <select
            value={filters.license_type || ''}
            onChange={(e) => onFiltersChange({ license_type: e.target.value || undefined })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">All License Types</option>
            {licenseTypes.map((license) => (
              <option key={license} value={license}>
                {license}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Languages
          </label>
          <select
            value={filters.languages?.[0] || ''}
            onChange={(e) => onFiltersChange({ languages: e.target.value ? [e.target.value] : undefined })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">All Languages</option>
            {languages.map((language) => (
              <option key={language} value={language}>
                {language}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex items-center gap-4 mt-4">
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={filters.tour_guide_certified || false}
            onChange={(e) => onFiltersChange({ tour_guide_certified: e.target.checked || undefined })}
            className="rounded border-gray-300 text-orange-600 focus:ring-orange-500"
          />
          <span className="ml-2 text-sm text-gray-700">Tour Guide Certified</span>
        </label>

        <label className="flex items-center">
          <input
            type="checkbox"
            checked={filters.first_aid_certified || false}
            onChange={(e) => onFiltersChange({ first_aid_certified: e.target.checked || undefined })}
            className="rounded border-gray-300 text-orange-600 focus:ring-orange-500"
          />
          <span className="ml-2 text-sm text-gray-700">First Aid Certified</span>
        </label>

        <label className="flex items-center">
          <input
            type="checkbox"
            checked={filters.available_for_assignment || false}
            onChange={(e) => onFiltersChange({ available_for_assignment: e.target.checked || undefined })}
            className="rounded border-gray-300 text-orange-600 focus:ring-orange-500"
          />
          <span className="ml-2 text-sm text-gray-700">Available for Assignment</span>
        </label>

        <button
          onClick={() => onFiltersChange({ 
            status: undefined, 
            employment_type: undefined, 
            license_type: undefined,
            languages: undefined,
            tour_guide_certified: undefined,
            first_aid_certified: undefined,
            available_for_assignment: undefined,
            license_expiring_soon: undefined
          })}
          className="text-sm text-orange-600 hover:text-orange-700"
        >
          Clear filters
        </button>
      </div>
    </div>
  );
}
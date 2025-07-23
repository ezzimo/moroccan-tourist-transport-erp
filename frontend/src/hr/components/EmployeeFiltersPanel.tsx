import React from 'react';
import { X } from 'lucide-react';
import { EmployeeFilters } from '../types/employee';

interface EmployeeFiltersPanelProps {
  filters: EmployeeFilters;
  onFiltersChange: (filters: Partial<EmployeeFilters>) => void;
  onClose: () => void;
}

export default function EmployeeFiltersPanel({
  filters,
  onFiltersChange,
  onClose,
}: EmployeeFiltersPanelProps) {
  const departments = ['Operations', 'Customer Service', 'Administration', 'Finance', 'HR', 'Maintenance'];
  const employmentTypes = ['FULL_TIME', 'PART_TIME', 'CONTRACT'];
  const statuses = ['ACTIVE', 'PROBATION', 'SUSPENDED', 'TERMINATED'];

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
            Department
          </label>
          <select
            value={filters.department || ''}
            onChange={(e) => onFiltersChange({ department: e.target.value || undefined })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">All Departments</option>
            {departments.map((dept) => (
              <option key={dept} value={dept}>
                {dept}
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
                {type.replace('_', ' ')}
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
            Position
          </label>
          <input
            type="text"
            value={filters.position || ''}
            onChange={(e) => onFiltersChange({ position: e.target.value || undefined })}
            placeholder="Filter by position"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          />
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
          <span className="ml-2 text-sm text-gray-700">Active employees only</span>
        </label>

        <button
          onClick={() => onFiltersChange({ 
            department: undefined, 
            employment_type: undefined, 
            status: undefined, 
            position: undefined,
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
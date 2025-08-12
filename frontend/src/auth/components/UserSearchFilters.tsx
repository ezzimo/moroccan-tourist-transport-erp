import React, { memo, useCallback, useState, useEffect } from 'react';
import { Search, X, Calendar, Shield, Filter } from 'lucide-react';
import { UserSearchParams, Role } from '../types/auth';
import { userManagementApi } from '../api/userManagementApi';

interface UserSearchFiltersProps {
  searchParams: UserSearchParams;
  onSearchParamsChange: (params: Partial<UserSearchParams>) => void;
}

const UserSearchFilters = memo(function UserSearchFilters({
  searchParams,
  onSearchParamsChange
}: UserSearchFiltersProps) {
  console.log('🔧 UserSearchFilters: Component initializing', { searchParams });

  const [roles, setRoles] = useState<Role[]>([]);
  const [rolesLoading, setRolesLoading] = useState(true);
  const [localFilters, setLocalFilters] = useState({
    search: searchParams.search || '',
    role_ids: searchParams.role_ids || [],
    is_active: searchParams.is_active,
    is_verified: searchParams.is_verified,
    is_locked: searchParams.is_locked,
    created_after: searchParams.created_after || '',
    created_before: searchParams.created_before || '',
    last_login_after: searchParams.last_login_after || '',
    last_login_before: searchParams.last_login_before || '',
    include_deleted: searchParams.include_deleted || false,
    sort_by: searchParams.sort_by || 'created_at',
    sort_order: searchParams.sort_order || 'desc'
  });

  // Load available roles
  useEffect(() => {
    const loadRoles = async () => {
      try {
        console.log('🔧 UserSearchFilters: Loading roles');
        setRolesLoading(true);
        const rolesData = await userManagementApi.getRoles();
        console.log('🔧 UserSearchFilters: Roles loaded', { count: rolesData.length });
        setRoles(rolesData);
      } catch (error) {
        console.error('🔧 UserSearchFilters: Error loading roles', error);
      } finally {
        setRolesLoading(false);
      }
    };

    loadRoles();
  }, []);

  // Handle local filter changes
  const handleLocalFilterChange = useCallback((key: string, value: any) => {
    console.log('🔧 UserSearchFilters: Local filter changed', { key, value });
    setLocalFilters(prev => ({ ...prev, [key]: value }));
  }, []);

  // Apply filters (debounced for search)
  const applyFilters = useCallback(() => {
    console.log('🔧 UserSearchFilters: Applying filters', localFilters);
    
    // Clean up empty values
    const cleanFilters: Partial<UserSearchParams> = {};
    Object.entries(localFilters).forEach(([key, value]) => {
      if (value !== '' && value !== null && value !== undefined) {
        if (Array.isArray(value) && value.length > 0) {
          cleanFilters[key as keyof UserSearchParams] = value;
        } else if (!Array.isArray(value)) {
          cleanFilters[key as keyof UserSearchParams] = value;
        }
      }
    });

    onSearchParamsChange(cleanFilters);
  }, [localFilters, onSearchParamsChange]);

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (localFilters.search !== searchParams.search) {
        applyFilters();
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [localFilters.search, searchParams.search, applyFilters]);

  // Clear all filters
  const clearFilters = useCallback(() => {
    console.log('🔧 UserSearchFilters: Clearing all filters');
    const clearedFilters = {
      search: '',
      role_ids: [],
      is_active: undefined,
      is_verified: undefined,
      is_locked: undefined,
      created_after: '',
      created_before: '',
      last_login_after: '',
      last_login_before: '',
      include_deleted: false,
      sort_by: 'created_at',
      sort_order: 'desc' as const
    };
    setLocalFilters(clearedFilters);
    onSearchParamsChange(clearedFilters);
  }, [onSearchParamsChange]);

  // Handle role selection
  const handleRoleToggle = useCallback((roleId: string) => {
    console.log('🔧 UserSearchFilters: Role toggled', { roleId });
    const currentRoles = localFilters.role_ids || [];
    const newRoles = currentRoles.includes(roleId)
      ? currentRoles.filter(id => id !== roleId)
      : [...currentRoles, roleId];
    
    handleLocalFilterChange('role_ids', newRoles);
    // Apply immediately for role changes
    setTimeout(() => applyFilters(), 0);
  }, [localFilters.role_ids, handleLocalFilterChange, applyFilters]);

  // Get active filter count
  const getActiveFilterCount = useCallback(() => {
    let count = 0;
    if (localFilters.search) count++;
    if (localFilters.role_ids && localFilters.role_ids.length > 0) count++;
    if (localFilters.is_active !== undefined) count++;
    if (localFilters.is_verified !== undefined) count++;
    if (localFilters.is_locked !== undefined) count++;
    if (localFilters.created_after) count++;
    if (localFilters.created_before) count++;
    if (localFilters.last_login_after) count++;
    if (localFilters.last_login_before) count++;
    if (localFilters.include_deleted) count++;
    return count;
  }, [localFilters]);

  const activeFilterCount = getActiveFilterCount();

  console.log('🔧 UserSearchFilters: Rendering', {
    activeFilterCount,
    rolesCount: roles.length,
    rolesLoading
  });

  return (
    <div className="bg-white rounded-lg border p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <Filter className="h-5 w-5 text-gray-400 mr-2" />
          <h3 className="text-lg font-medium text-gray-900">Search & Filters</h3>
          {activeFilterCount > 0 && (
            <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {activeFilterCount} active
            </span>
          )}
        </div>
        {activeFilterCount > 0 && (
          <button
            onClick={clearFilters}
            className="text-sm text-gray-500 hover:text-gray-700 flex items-center"
          >
            <X className="h-4 w-4 mr-1" />
            Clear all
          </button>
        )}
      </div>

      {/* Search */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          placeholder="Search by name, email, or phone..."
          value={localFilters.search}
          onChange={(e) => handleLocalFilterChange('search', e.target.value)}
          className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      {/* Filter Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Status Filters */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Account Status
          </label>
          <div className="space-y-2">
            <label className="flex items-center">
              <input
                type="radio"
                name="is_active"
                checked={localFilters.is_active === undefined}
                onChange={() => {
                  handleLocalFilterChange('is_active', undefined);
                  setTimeout(() => applyFilters(), 0);
                }}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <span className="ml-2 text-sm text-gray-700">All</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="is_active"
                checked={localFilters.is_active === true}
                onChange={() => {
                  handleLocalFilterChange('is_active', true);
                  setTimeout(() => applyFilters(), 0);
                }}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <span className="ml-2 text-sm text-gray-700">Active</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="is_active"
                checked={localFilters.is_active === false}
                onChange={() => {
                  handleLocalFilterChange('is_active', false);
                  setTimeout(() => applyFilters(), 0);
                }}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <span className="ml-2 text-sm text-gray-700">Inactive</span>
            </label>
          </div>
        </div>

        {/* Verification Status */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Verification Status
          </label>
          <div className="space-y-2">
            <label className="flex items-center">
              <input
                type="radio"
                name="is_verified"
                checked={localFilters.is_verified === undefined}
                onChange={() => {
                  handleLocalFilterChange('is_verified', undefined);
                  setTimeout(() => applyFilters(), 0);
                }}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <span className="ml-2 text-sm text-gray-700">All</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="is_verified"
                checked={localFilters.is_verified === true}
                onChange={() => {
                  handleLocalFilterChange('is_verified', true);
                  setTimeout(() => applyFilters(), 0);
                }}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <span className="ml-2 text-sm text-gray-700">Verified</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="is_verified"
                checked={localFilters.is_verified === false}
                onChange={() => {
                  handleLocalFilterChange('is_verified', false);
                  setTimeout(() => applyFilters(), 0);
                }}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <span className="ml-2 text-sm text-gray-700">Unverified</span>
            </label>
          </div>
        </div>

        {/* Lock Status */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Lock Status
          </label>
          <div className="space-y-2">
            <label className="flex items-center">
              <input
                type="radio"
                name="is_locked"
                checked={localFilters.is_locked === undefined}
                onChange={() => {
                  handleLocalFilterChange('is_locked', undefined);
                  setTimeout(() => applyFilters(), 0);
                }}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <span className="ml-2 text-sm text-gray-700">All</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="is_locked"
                checked={localFilters.is_locked === false}
                onChange={() => {
                  handleLocalFilterChange('is_locked', false);
                  setTimeout(() => applyFilters(), 0);
                }}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <span className="ml-2 text-sm text-gray-700">Unlocked</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="is_locked"
                checked={localFilters.is_locked === true}
                onChange={() => {
                  handleLocalFilterChange('is_locked', true);
                  setTimeout(() => applyFilters(), 0);
                }}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <span className="ml-2 text-sm text-gray-700">Locked</span>
            </label>
          </div>
        </div>
      </div>

      {/* Roles Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          <Shield className="inline h-4 w-4 mr-1" />
          Roles
        </label>
        {rolesLoading ? (
          <div className="text-sm text-gray-500">Loading roles...</div>
        ) : (
          <div className="flex flex-wrap gap-2">
            {roles.map(role => (
              <label key={role.id} className="flex items-center">
                <input
                  type="checkbox"
                  checked={localFilters.role_ids?.includes(role.id) || false}
                  onChange={() => handleRoleToggle(role.id)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">
                  {role.display_name || role.name}
                </span>
              </label>
            ))}
          </div>
        )}
      </div>

      {/* Date Filters */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Created Date Range */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Calendar className="inline h-4 w-4 mr-1" />
            Created Date Range
          </label>
          <div className="grid grid-cols-2 gap-2">
            <input
              type="date"
              placeholder="From"
              value={localFilters.created_after}
              onChange={(e) => {
                handleLocalFilterChange('created_after', e.target.value);
                setTimeout(() => applyFilters(), 0);
              }}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            />
            <input
              type="date"
              placeholder="To"
              value={localFilters.created_before}
              onChange={(e) => {
                handleLocalFilterChange('created_before', e.target.value);
                setTimeout(() => applyFilters(), 0);
              }}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        {/* Last Login Date Range */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Calendar className="inline h-4 w-4 mr-1" />
            Last Login Date Range
          </label>
          <div className="grid grid-cols-2 gap-2">
            <input
              type="date"
              placeholder="From"
              value={localFilters.last_login_after}
              onChange={(e) => {
                handleLocalFilterChange('last_login_after', e.target.value);
                setTimeout(() => applyFilters(), 0);
              }}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            />
            <input
              type="date"
              placeholder="To"
              value={localFilters.last_login_before}
              onChange={(e) => {
                handleLocalFilterChange('last_login_before', e.target.value);
                setTimeout(() => applyFilters(), 0);
              }}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Sorting and Advanced Options */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Sort By */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Sort By
          </label>
          <select
            value={localFilters.sort_by}
            onChange={(e) => {
              handleLocalFilterChange('sort_by', e.target.value);
              setTimeout(() => applyFilters(), 0);
            }}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="created_at">Created Date</option>
            <option value="updated_at">Updated Date</option>
            <option value="last_login_at">Last Login At</option>
            <option value="full_name">Name</option>
            <option value="email">Email</option>
          </select>
        </div>

        {/* Sort Order */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Sort Order
          </label>
          <select
            value={localFilters.sort_order}
            onChange={(e) => {
              handleLocalFilterChange('sort_order', e.target.value as 'asc' | 'desc');
              setTimeout(() => applyFilters(), 0);
            }}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="desc">Newest First</option>
            <option value="asc">Oldest First</option>
          </select>
        </div>

        {/* Advanced Options */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Advanced Options
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={localFilters.include_deleted}
              onChange={(e) => {
                handleLocalFilterChange('include_deleted', e.target.checked);
                setTimeout(() => applyFilters(), 0);
              }}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span className="ml-2 text-sm text-gray-700">Include deleted users</span>
          </label>
        </div>
      </div>
    </div>
  );
});

export default UserSearchFilters;


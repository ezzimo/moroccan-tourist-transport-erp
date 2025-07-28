import React, { useState, useEffect, useCallback } from 'react';
import { Users, Plus, Download, Upload, Search, Filter, RefreshCw } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { userManagementApi } from '../api/userManagementApi';
import { 
  User, 
  UserSearchParams, 
  UserSearchResponse, 
  USER_PERMISSIONS 
} from '../types/auth';
import UserManagementTable from './UserManagementTable';
import UserSearchFilters from './UserSearchFilters';
import CreateUserModal from './CreateUserModal';
import EditUserModal from './EditUserModal';
import UserActivityModal from './UserActivityModal';
import BulkActionsToolbar from './BulkActionsToolbar';

interface AdminUserManagementProps {
  className?: string;
}

export default function AdminUserManagement({ className = '' }: AdminUserManagementProps) {
  console.log('🔧 AdminUserManagement: Component initializing');
  
  const { hasPermission, isAdmin, state: authState } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [searchResponse, setSearchResponse] = useState<UserSearchResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedUsers, setSelectedUsers] = useState<string[]>([]);
  
  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showActivityModal, setShowActivityModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [activityUserId, setActivityUserId] = useState<string | null>(null);
  
  // Search and filter states
  const [searchParams, setSearchParams] = useState<UserSearchParams>({
    skip: 0,
    limit: 25,
    sort_by: 'created_at',
    sort_order: 'desc'
  });
  const [showFilters, setShowFilters] = useState(false);

  console.log('🔧 AdminUserManagement: Current state', {
    usersCount: users.length,
    loading,
    error,
    selectedUsersCount: selectedUsers.length,
    searchParams,
    hasReadPermission: hasPermission('auth', 'read', 'users'),
    isAdmin,
    currentUser: authState.user?.email
  });

  // Check permissions
  const canRead = hasPermission('auth', 'read', 'users');
  const canCreate = hasPermission('auth', 'create', 'users');
  const canUpdate = hasPermission('auth', 'update', 'users');
  const canDelete = hasPermission('auth', 'delete', 'users');
  const canBulkOperations = hasPermission('auth', 'bulk', 'users');
  const canImportExport = hasPermission('auth', 'import_export', 'users');

  console.log('🔧 AdminUserManagement: Permissions check', {
    canRead,
    canCreate,
    canUpdate,
    canDelete,
    canBulkOperations,
    canImportExport,
    isAdmin
  });

  // Load users function with maximum logging
  const loadUsers = useCallback(async (params: UserSearchParams = searchParams) => {
    console.log('🔧 AdminUserManagement: loadUsers called', { params });
    
    if (!canRead) {
      console.warn('🔧 AdminUserManagement: No read permission, skipping load');
      setError('You do not have permission to view users');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      console.log('🔧 AdminUserManagement: Making API call to search users');
      const startTime = performance.now();
      
      const response = await userManagementApi.searchUsers(params);
      
      const endTime = performance.now();
      console.log('🔧 AdminUserManagement: API call completed', {
        duration: `${(endTime - startTime).toFixed(2)}ms`,
        usersReturned: response.users.length,
        total: response.total,
        hasMore: response.has_more
      });

      setUsers(response.users);
      setSearchResponse(response);
      
      console.log('🔧 AdminUserManagement: Users loaded successfully', {
        users: response.users.map(u => ({
          id: u.id,
          email: u.email,
          full_name: u.full_name,
          is_active: u.is_active,
          is_locked: u.is_locked,
          roles: u.roles.map(r => r.name)
        }))
      });

    } catch (err: any) {
      console.error('🔧 AdminUserManagement: Error loading users', {
        error: err.message,
        status: err.response?.status,
        data: err.response?.data
      });
      
      setError(err.response?.data?.detail || 'Failed to load users');
      setUsers([]);
      setSearchResponse(null);
    } finally {
      setLoading(false);
      console.log('🔧 AdminUserManagement: loadUsers completed');
    }
  }, [searchParams, canRead]);

  // Initial load
  useEffect(() => {
    console.log('🔧 AdminUserManagement: useEffect triggered for initial load');
    loadUsers();
  }, [loadUsers]);

  // Handle search parameter changes
  const handleSearchParamsChange = useCallback((newParams: Partial<UserSearchParams>) => {
    console.log('🔧 AdminUserManagement: Search params changing', {
      oldParams: searchParams,
      newParams,
      mergedParams: { ...searchParams, ...newParams, skip: 0 }
    });
    
    const updatedParams = { ...searchParams, ...newParams, skip: 0 };
    setSearchParams(updatedParams);
    setSelectedUsers([]); // Clear selection when search changes
    loadUsers(updatedParams);
  }, [searchParams, loadUsers]);

  // Handle pagination
  const handlePageChange = useCallback((page: number) => {
    const skip = page * searchParams.limit!;
    console.log('🔧 AdminUserManagement: Page changing', {
      page,
      limit: searchParams.limit,
      skip,
      currentSkip: searchParams.skip
    });
    
    const updatedParams = { ...searchParams, skip };
    setSearchParams(updatedParams);
    loadUsers(updatedParams);
  }, [searchParams, loadUsers]);

  // Handle user selection
  const handleUserSelection = useCallback((userIds: string[]) => {
    console.log('🔧 AdminUserManagement: User selection changed', {
      previousSelection: selectedUsers,
      newSelection: userIds,
      selectionCount: userIds.length
    });
    setSelectedUsers(userIds);
  }, [selectedUsers]);

  // Handle user actions
  const handleEditUser = useCallback((user: User) => {
    console.log('🔧 AdminUserManagement: Edit user requested', {
      userId: user.id,
      userEmail: user.email,
      canUpdate
    });
    
    if (!canUpdate) {
      console.warn('🔧 AdminUserManagement: No update permission for edit');
      setError('You do not have permission to edit users');
      return;
    }
    
    setEditingUser(user);
    setShowEditModal(true);
  }, [canUpdate]);

  const handleViewActivity = useCallback((userId: string) => {
    console.log('🔧 AdminUserManagement: View activity requested', {
      userId,
      hasPermission: hasPermission('auth', 'read', 'activity')
    });
    
    setActivityUserId(userId);
    setShowActivityModal(true);
  }, [hasPermission]);

  const handleDeleteUser = useCallback(async (userId: string) => {
    console.log('🔧 AdminUserManagement: Delete user requested', {
      userId,
      canDelete
    });
    
    if (!canDelete) {
      console.warn('🔧 AdminUserManagement: No delete permission');
      setError('You do not have permission to delete users');
      return;
    }

    if (!confirm('Are you sure you want to delete this user?')) {
      console.log('🔧 AdminUserManagement: Delete cancelled by user');
      return;
    }

    try {
      console.log('🔧 AdminUserManagement: Deleting user via API');
      await userManagementApi.deleteUser(userId);
      console.log('🔧 AdminUserManagement: User deleted successfully');
      
      // Reload users
      await loadUsers();
      
      // Remove from selection if selected
      setSelectedUsers(prev => prev.filter(id => id !== userId));
      
    } catch (err: any) {
      console.error('🔧 AdminUserManagement: Error deleting user', {
        error: err.message,
        userId
      });
      setError(err.response?.data?.detail || 'Failed to delete user');
    }
  }, [canDelete, loadUsers]);

  // Handle export
  const handleExport = useCallback(async (format: 'csv' | 'json') => {
    console.log('🔧 AdminUserManagement: Export requested', {
      format,
      canImportExport,
      usersCount: users.length
    });
    
    if (!canImportExport) {
      console.warn('🔧 AdminUserManagement: No import/export permission');
      setError('You do not have permission to export users');
      return;
    }

    try {
      console.log('🔧 AdminUserManagement: Starting export');
      await userManagementApi.downloadExport(format);
      console.log('🔧 AdminUserManagement: Export completed successfully');
    } catch (err: any) {
      console.error('🔧 AdminUserManagement: Export failed', {
        error: err.message,
        format
      });
      setError(err.response?.data?.detail || 'Failed to export users');
    }
  }, [canImportExport, users.length]);

  // Handle refresh
  const handleRefresh = useCallback(() => {
    console.log('🔧 AdminUserManagement: Manual refresh requested');
    loadUsers();
  }, [loadUsers]);

  // Permission check
  if (!canRead && !isAdmin) {
    console.warn('🔧 AdminUserManagement: Access denied - no permissions');
    return (
      <div className={`bg-white rounded-lg border p-8 text-center ${className}`}>
        <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Access Denied</h3>
        <p className="text-gray-500">
          You do not have permission to access user management.
        </p>
      </div>
    );
  }

  console.log('🔧 AdminUserManagement: Rendering component', {
    showFilters,
    showCreateModal,
    showEditModal,
    showActivityModal,
    usersToRender: users.length
  });

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center">
              <Users className="h-8 w-8 text-blue-600 mr-3" />
              User Management
            </h2>
            <p className="text-gray-600 mt-1">
              Manage user accounts, roles, and permissions
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            {/* Refresh Button */}
            <button
              onClick={handleRefresh}
              disabled={loading}
              className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>

            {/* Export Button */}
            {canImportExport && (
              <div className="relative">
                <button
                  onClick={() => handleExport('csv')}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export CSV
                </button>
              </div>
            )}

            {/* Create User Button */}
            {canCreate && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Create User
              </button>
            )}
          </div>
        </div>

        {/* Stats */}
        {searchResponse && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-blue-600">
                {searchResponse.total}
              </div>
              <div className="text-sm text-blue-600">Total Users</div>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-green-600">
                {users.filter(u => u.is_active).length}
              </div>
              <div className="text-sm text-green-600">Active Users</div>
            </div>
            <div className="bg-yellow-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-yellow-600">
                {users.filter(u => u.is_locked).length}
              </div>
              <div className="text-sm text-yellow-600">Locked Users</div>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-purple-600">
                {users.filter(u => !u.is_verified).length}
              </div>
              <div className="text-sm text-purple-600">Unverified</div>
            </div>
          </div>
        )}

        {/* Search and Filters */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`inline-flex items-center px-3 py-2 border rounded-md text-sm font-medium ${
                showFilters
                  ? 'border-blue-300 text-blue-700 bg-blue-50'
                  : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'
              }`}
            >
              <Filter className="h-4 w-4 mr-2" />
              Filters
            </button>
          </div>
          
          {selectedUsers.length > 0 && canBulkOperations && (
            <BulkActionsToolbar
              selectedUserIds={selectedUsers}
              onActionComplete={() => {
                setSelectedUsers([]);
                loadUsers();
              }}
            />
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="text-red-800">{error}</div>
          <button
            onClick={() => setError(null)}
            className="text-red-600 hover:text-red-800 text-sm mt-2"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Search Filters */}
      {showFilters && (
        <UserSearchFilters
          searchParams={searchParams}
          onSearchParamsChange={handleSearchParamsChange}
        />
      )}

      {/* User Table */}
      <UserManagementTable
        users={users}
        loading={loading}
        searchResponse={searchResponse}
        selectedUserIds={selectedUsers}
        onUserSelection={handleUserSelection}
        onEditUser={handleEditUser}
        onDeleteUser={handleDeleteUser}
        onViewActivity={handleViewActivity}
        onPageChange={handlePageChange}
        canUpdate={canUpdate}
        canDelete={canDelete}
      />

      {/* Modals */}
      {showCreateModal && (
        <CreateUserModal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          onUserCreated={() => {
            setShowCreateModal(false);
            loadUsers();
          }}
        />
      )}

      {showEditModal && editingUser && (
        <EditUserModal
          isOpen={showEditModal}
          user={editingUser}
          onClose={() => {
            setShowEditModal(false);
            setEditingUser(null);
          }}
          onUserUpdated={() => {
            setShowEditModal(false);
            setEditingUser(null);
            loadUsers();
          }}
        />
      )}

      {showActivityModal && activityUserId && (
        <UserActivityModal
          isOpen={showActivityModal}
          userId={activityUserId}
          onClose={() => {
            setShowActivityModal(false);
            setActivityUserId(null);
          }}
        />
      )}
    </div>
  );
}


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
import PermissionGate from './PermissionGate';
import ConfirmationModal from './ConfirmationModal';


interface AdminUserManagementProps {
  className?: string;
}

export default function AdminUserManagement({ className = '' }: AdminUserManagementProps) {
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
  const [activityUser, setActivityUser] = useState<User | null>(null);
  const [showDeleteConfirmation, setShowDeleteConfirmation] = useState(false);
  const [deletingUserId, setDeletingUserId] = useState<string | null>(null);
  
  // Search and filter states
  const [searchParams, setSearchParams] = useState<UserSearchParams>({
    skip: 0,
    limit: 25,
    sort_by: 'created_at',
    sort_order: 'desc'
  });
  const [showFilters, setShowFilters] = useState(false);

  // Check permissions
  const canRead = hasPermission('auth', 'read', 'users');
  const canCreate = hasPermission('auth', 'create', 'users');
  const canUpdate = hasPermission('auth', 'update', 'users');
  const canDelete = hasPermission('auth', 'delete', 'users');
  const canBulkOperations = hasPermission('auth', 'bulk', 'users');
  const canImportExport = hasPermission('auth', 'import_export', 'users');

  // Load users function with maximum logging
  const loadUsers = useCallback(async (params: UserSearchParams = searchParams) => {
    if (!canRead) {
      setError('You do not have permission to view users');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await userManagementApi.searchUsers(params);
      
      setUsers(response.users);
      setSearchResponse(response);
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load users');
      setUsers([]);
      setSearchResponse(null);
    } finally {
      setLoading(false);
    }
  }, [searchParams, canRead]);

  // Initial load
  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  // Handle search parameter changes
  const handleSearchParamsChange = useCallback((newParams: Partial<UserSearchParams>) => {
    const updatedParams = { ...searchParams, ...newParams, skip: 0 };
    setSearchParams(updatedParams);
    setSelectedUsers([]); // Clear selection when search changes
    loadUsers(updatedParams);
  }, [searchParams, loadUsers]);

  // Handle pagination
  const handlePageChange = useCallback((page: number) => {
    const skip = page * searchParams.limit!;
    
    const updatedParams = { ...searchParams, skip };
    setSearchParams(updatedParams);
    loadUsers(updatedParams);
  }, [searchParams, loadUsers]);

  // Handle user selection
  const handleUserSelection = useCallback((userIds: string[]) => {
    setSelectedUsers(userIds);
  }, []);

  // Handle user actions
  const handleEditUser = useCallback((user: User) => {
    if (!canUpdate) {
      setError('You do not have permission to edit users');
      return;
    }
    
    setEditingUser(user);
    setShowEditModal(true);
  }, [canUpdate]);

  const handleViewActivity = useCallback((user: User) => {
    setActivityUser(user);
    setShowActivityModal(true);
  }, []);

  const handleDeleteUser = useCallback(async (userId: string) => {
    if (!canDelete) {
      setError('You do not have permission to delete users');
      return;
    }
    setDeletingUserId(userId);
    setShowDeleteConfirmation(true);
  }, [canDelete]);

  const confirmDeleteUser = useCallback(async () => {
    if (!deletingUserId) return;

    try {
      setLoading(true); // You might want a specific loading state for deletion
      await userManagementApi.deleteUser(deletingUserId);
      
      // Reload users
      await loadUsers();
      
      // Remove from selection if selected
      setSelectedUsers(prev => prev.filter(id => id !== deletingUserId));
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete user');
    } finally {
      setShowDeleteConfirmation(false);
      setDeletingUserId(null);
      setLoading(false);
    }
  }, [deletingUserId, loadUsers]);

  // Handle export
  const handleExport = useCallback(async (format: 'csv' | 'json') => {
    // if (!canImportExport) {
    //   setError('You do not have permission to export users');
    //   return;
    // }

    try {
      await userManagementApi.downloadExport(format);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to export users');
    }
  }, []);
  // [canImportExport, users.length]);

  // Handle refresh
  const handleRefresh = useCallback(() => {
    loadUsers();
  }, [loadUsers]);

  // Permission check
  return (
    <PermissionGate
      service="auth"
      action="read"
      resource="users"
      fallback={
        <div className="bg-white rounded-lg border p-8 text-center">
          <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Access Denied</h3>
          <p className="text-gray-500">You do not have permission to access user management.</p>
        </div>
      }
    >
      {/* ✨ The full admin management UI goes here */}
      <div className={`space-y-6 ${className}`}>
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
            {/* {canImportExport && ( */}
            {(
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
                {(users || []).filter(u => u.is_active).length}
              </div>
              <div className="text-sm text-green-600">Active Users</div>
            </div>
            <div className="bg-yellow-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-yellow-600">
                {(users || []).filter(u => u.is_locked).length}
              </div>
              <div className="text-sm text-yellow-600">Locked Users</div>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-purple-600">
                {(users || []).filter(u => !u.is_verified).length}
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
          
          {(selectedUsers || []).length > 0  && (
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

      {showActivityModal && activityUser && (
        <UserActivityModal
          isOpen={showActivityModal}
          user={activityUser}
          onClose={() => {
            setShowActivityModal(false);
            setActivityUser(null);
          }}
        />
      )}

      {showDeleteConfirmation && (
        <ConfirmationModal
          isOpen={showDeleteConfirmation}
          onClose={() => setShowDeleteConfirmation(false)}
          onConfirm={confirmDeleteUser}
          title="Delete User"
          message={`Are you sure you want to delete this user? This action cannot be undone.`}
          confirmText="Delete"
          loading={loading}
        />
      )}
    </div>
      </div>  
    </PermissionGate>
    );
}


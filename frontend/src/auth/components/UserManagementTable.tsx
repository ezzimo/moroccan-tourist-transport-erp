import React, { memo, useCallback } from 'react';
import { 
  Edit, 
  Trash2, 
  Lock, 
  Unlock, 
  Eye, 
  Shield, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { User, UserSearchResponse } from '../types/auth';
import { formatDateTime } from '../../utils/formatters';

interface UserManagementTableProps {
  users: User[];
  loading: boolean;
  searchResponse: UserSearchResponse | null;
  selectedUserIds: string[];
  onUserSelection: (userIds: string[]) => void;
  onEditUser: (user: User) => void;
  onDeleteUser: (userId: string) => void;
  onViewActivity: (user: User) => void;
  onPageChange: (page: number) => void;
  canUpdate: boolean;
  canDelete: boolean;
}

const UserManagementTable = memo(function UserManagementTable({
  users,
  loading,
  searchResponse,
  selectedUserIds,
  onUserSelection,
  onEditUser,
  onDeleteUser,
  onViewActivity,
  onPageChange,
  canUpdate,
  canDelete
}: UserManagementTableProps) {
  // Handle select all checkbox
  const handleSelectAll = useCallback((checked: boolean) => {
    if (checked) {
      onUserSelection(users.map(user => user.id));
    } else {
      onUserSelection([]);
    }
  }, [users, onUserSelection]);

  // Handle individual user selection
  const handleUserSelect = useCallback((userId: string, checked: boolean) => {
    if (checked) {
      onUserSelection([...selectedUserIds, userId]);
    } else {
      onUserSelection(selectedUserIds.filter(id => id !== userId));
    }
  }, [selectedUserIds, onUserSelection]);

  // Handle pagination
  const currentPage = searchResponse ? Math.floor(searchResponse.skip / searchResponse.limit) : 0;
  const totalPages = searchResponse ? Math.ceil(searchResponse.total / searchResponse.limit) : 0;

  const handlePageClick = useCallback((page: number) => {
    onPageChange(page);
  }, [onPageChange]);

  // Get user status badge
  const getUserStatusBadge = useCallback((user: User) => {
    if (!user.is_active) {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
          <XCircle className="h-3 w-3 mr-1" />
          Inactive
        </span>
      );
    }
    if (user.is_locked) {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
          <Lock className="h-3 w-3 mr-1" />
          Locked
        </span>
      );
    }
    if (!user.is_verified) {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
          <AlertCircle className="h-3 w-3 mr-1" />
          Unverified
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
        <CheckCircle className="h-3 w-3 mr-1" />
        Active
      </span>
    );
  }, []);

  // Get user roles display
  const getUserRoles = useCallback((user: User) => {
    if (!user.roles || (user.roles || []).length === 0) {
      return <span className="text-gray-400">No roles</span>;
    }
    
    const displayRoles = (user.roles || []).slice(0, 2);
    const remainingCount = (user.roles || []).length - 2;
    
    return (
      <div className="flex flex-wrap gap-1">
        {displayRoles.map(role => (
          <span
            key={role.id}
            className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800"
          >
            <Shield className="h-3 w-3 mr-1" />
            {role.display_name || role.name}
          </span>
        ))}
        {remainingCount > 0 && (
          <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-600">
            +{remainingCount} more
          </span>
        )}
      </div>
    );
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-lg border">
        <div className="p-8 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-500">Loading users...</p>
        </div>
      </div>
    );
  }

  if ((users || []).length === 0) {
    return (
      <div className="bg-white rounded-lg border">
        <div className="p-8 text-center">
          <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No users found</h3>
          <p className="text-gray-500">
            No users match your current search criteria.
          </p>
        </div>
      </div>
    );
  }

  const isAllSelected = (users || []).length > 0 && (users || []).every(user => (selectedUserIds || []).includes(user.id));
  const isPartiallySelected = (selectedUserIds || []).length > 0 && !isAllSelected;

  return (
    <div className="bg-white rounded-lg border overflow-hidden">
      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left">
                <input
                  type="checkbox"
                  checked={isAllSelected}
                  ref={input => {
                    if (input) input.indeterminate = isPartiallySelected;
                  }}
                  onChange={(e) => handleSelectAll(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                User
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Roles
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Last Login At
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {users.map((user) => (
              <tr
                key={user.id}
                className={`hover:bg-gray-50 ${
                  selectedUserIds.includes(user.id) ? 'bg-blue-50' : ''
                }`}
              >
                <td className="px-6 py-4">
                  <input
                    type="checkbox"
                    checked={selectedUserIds.includes(user.id)}
                    onChange={(e) => handleUserSelect(user.id, e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center">
                    {user.avatar_url ? (
                      <img
                        className="h-10 w-10 rounded-full"
                        src={user.avatar_url}
                        alt={user.full_name}
                      />
                    ) : (
                      <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                        <span className="text-sm font-medium text-gray-700">
                          {user.full_name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                    )}
                    <div className="ml-4">
                      <div className="text-sm font-medium text-gray-900">
                        {user.full_name}
                      </div>
                      <div className="text-sm text-gray-500">{user.email}</div>
                      {user.phone && (
                        <div className="text-xs text-gray-400">{user.phone}</div>
                      )}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  {getUserStatusBadge(user)}
                  {user.must_change_password && (
                    <div className="mt-1">
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                        Password Reset Required
                      </span>
                    </div>
                  )}
                </td>
                <td className="px-6 py-4">
                  {getUserRoles(user)}
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  {user.last_login_at ? (
                    formatDateTime(user.last_login_at)
                  ) : (
                    <span className="text-gray-400">Never</span>
                  )}
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  {formatDateTime(user.created_at)}
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="flex items-center justify-end space-x-2">
                    <button
                      onClick={() => onViewActivity(user)}
                      className="text-gray-400 hover:text-gray-600 p-1"
                      title="View Activity"
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                    {canUpdate && (
                      <button
                        onClick={() => onEditUser(user)}
                        className="text-blue-400 hover:text-blue-600 p-1"
                        title="Edit User"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                    )}
                    {canDelete && (
                      <button
                        onClick={() => onDeleteUser(user.id)}
                        className="text-red-400 hover:text-red-600 p-1"
                        title="Delete User"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {searchResponse && totalPages > 1 && (
        <div className="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
          <div className="flex items-center justify-between">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => handlePageClick(currentPage - 1)}
                disabled={currentPage === 0}
                className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                onClick={() => handlePageClick(currentPage + 1)}
                disabled={currentPage >= totalPages - 1}
                className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700">
                  Showing{' '}
                  <span className="font-medium">
                    {searchResponse.skip + 1}
                  </span>{' '}
                  to{' '}
                  <span className="font-medium">
                    {Math.min(searchResponse.skip + searchResponse.limit, searchResponse.total)}
                  </span>{' '}
                  of{' '}
                  <span className="font-medium">{searchResponse.total}</span>{' '}
                  results
                </p>
              </div>
              <div>
                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                  <button
                    onClick={() => handlePageClick(currentPage - 1)}
                    disabled={currentPage === 0}
                    className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ChevronLeft className="h-5 w-5" />
                  </button>
                  
                  {/* Page numbers */}
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    const pageNum = Math.max(0, Math.min(currentPage - 2 + i, totalPages - 1));
                    return (
                      <button
                        key={pageNum}
                        onClick={() => handlePageClick(pageNum)}
                        className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                          pageNum === currentPage
                            ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                            : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                        }`}
                      >
                        {pageNum + 1}
                      </button>
                    );
                  })}
                  
                  <button
                    onClick={() => handlePageClick(currentPage + 1)}
                    disabled={currentPage >= totalPages - 1}
                    className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ChevronRight className="h-5 w-5" />
                  </button>
                </nav>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
});

export default UserManagementTable;


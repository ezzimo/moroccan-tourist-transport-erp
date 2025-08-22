import React, { memo, useCallback, useState } from 'react';
import { 
  Users, 
  Lock, 
  Unlock, 
  CheckCircle, 
  XCircle, 
  Trash2, 
  Shield,
  AlertTriangle,
  ChevronDown
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { userManagementApi } from '../api/userManagementApi';

interface BulkActionsToolbarProps {
  selectedUserIds: string[];
  onActionComplete: () => void;
}

const BulkActionsToolbar = memo(function BulkActionsToolbar({
  selectedUserIds,
  onActionComplete
}: BulkActionsToolbarProps) {
  console.log('🔧 BulkActionsToolbar: Component initializing', {
    selectedCount: selectedUserIds.length
  });

  const { hasPermission } = useAuth();
  const [loading, setLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Permission checks
  const canBulkUpdate = hasPermission('auth', 'bulk', 'users');
  const canDelete = hasPermission('auth', 'delete', 'users');

  console.log('🔧 BulkActionsToolbar: Permissions', {
    canBulkUpdate,
    canDelete,
    selectedCount: selectedUserIds.length
  });

  // Handle bulk status update
  const handleBulkStatusUpdate = useCallback(async (statusUpdates: Record<string, any>) => {
    if (!canBulkUpdate) {
      console.warn('🔧 BulkActionsToolbar: No bulk update permission');
      setError('You do not have permission to perform bulk operations');
      return;
    }

    console.log('🔧 BulkActionsToolbar: Bulk status update requested', {
      userIds: selectedUserIds,
      statusUpdates
    });

    try {
      setLoading(true);
      setError(null);
      
      const startTime = performance.now();
      const result = await userManagementApi.bulkUpdateStatus({
        user_ids: selectedUserIds,
        status_updates: statusUpdates
      });
      
      const endTime = performance.now();
      console.log('🔧 BulkActionsToolbar: Bulk update completed', {
        duration: `${(endTime - startTime).toFixed(2)}ms`,
        updatedCount: result.updated_count,
        message: result.message
      });

      onActionComplete();
      setShowDropdown(false);
      
    } catch (err: any) {
      console.error('🔧 BulkActionsToolbar: Bulk update failed', {
        error: err.message,
        userIds: selectedUserIds,
        statusUpdates
      });
      setError(err.response?.data?.detail || 'Failed to update users');
    } finally {
      setLoading(false);
    }
  }, [selectedUserIds, canBulkUpdate, onActionComplete]);

  // Handle bulk delete
  const handleBulkDelete = useCallback(async () => {
    if (!canDelete) {
      console.warn('🔧 BulkActionsToolbar: No delete permission');
      setError('You do not have permission to delete users');
      return;
    }

    const confirmMessage = `Are you sure you want to delete ${selectedUserIds.length} user(s)? This action cannot be undone.`;
    if (!confirm(confirmMessage)) {
      console.log('🔧 BulkActionsToolbar: Bulk delete cancelled by user');
      return;
    }

    console.log('🔧 BulkActionsToolbar: Bulk delete requested', {
      userIds: selectedUserIds
    });

    try {
      setLoading(true);
      setError(null);
      
      const startTime = performance.now();
      
      // Delete users one by one (could be optimized with a bulk delete endpoint)
      const deletePromises = selectedUserIds.map(userId => 
        userManagementApi.deleteUser(userId)
      );
      
      await Promise.all(deletePromises);
      
      const endTime = performance.now();
      console.log('🔧 BulkActionsToolbar: Bulk delete completed', {
        duration: `${(endTime - startTime).toFixed(2)}ms`,
        deletedCount: selectedUserIds.length
      });

      onActionComplete();
      setShowDropdown(false);
      
    } catch (err: any) {
      console.error('🔧 BulkActionsToolbar: Bulk delete failed', {
        error: err.message,
        userIds: selectedUserIds
      });
      setError(err.response?.data?.detail || 'Failed to delete users');
    } finally {
      setLoading(false);
    }
  }, [selectedUserIds, canDelete, onActionComplete]);

  // Bulk action handlers
  const bulkActions = [
    {
      id: 'activate',
      label: 'Activate Users',
      icon: CheckCircle,
      color: 'text-green-600',
      action: () => handleBulkStatusUpdate({ is_active: true }),
      requiresPermission: canBulkUpdate
    },
    {
      id: 'deactivate',
      label: 'Deactivate Users',
      icon: XCircle,
      color: 'text-gray-600',
      action: () => handleBulkStatusUpdate({ is_active: false }),
      requiresPermission: canBulkUpdate
    },
    {
      id: 'lock',
      label: 'Lock Users',
      icon: Lock,
      color: 'text-red-600',
      action: () => handleBulkStatusUpdate({ is_locked: true }),
      requiresPermission: canBulkUpdate
    },
    {
      id: 'unlock',
      label: 'Unlock Users',
      icon: Unlock,
      color: 'text-blue-600',
      action: () => handleBulkStatusUpdate({ is_locked: false }),
      requiresPermission: canBulkUpdate
    },
    {
      id: 'verify',
      label: 'Mark as Verified',
      icon: Shield,
      color: 'text-green-600',
      action: () => handleBulkStatusUpdate({ is_verified: true }),
      requiresPermission: canBulkUpdate
    },
    {
      id: 'unverify',
      label: 'Mark as Unverified',
      icon: AlertTriangle,
      color: 'text-yellow-600',
      action: () => handleBulkStatusUpdate({ is_verified: false }),
      requiresPermission: canBulkUpdate
    },
    {
      id: 'force_password_reset',
      label: 'Force Password Reset',
      icon: Shield,
      color: 'text-orange-600',
      action: () => handleBulkStatusUpdate({ must_change_password: true }),
      requiresPermission: canBulkUpdate
    },
    {
      id: 'delete',
      label: 'Delete Users',
      icon: Trash2,
      color: 'text-red-600',
      action: handleBulkDelete,
      requiresPermission: canDelete,
      dangerous: true
    }
  ];

  const availableActions = (bulkActions || []).filter(action => action.requiresPermission);

  if (selectedUserIds.length === 0 || availableActions.length === 0) {
    return null;
  }

  console.log('🔧 BulkActionsToolbar: Rendering toolbar', {
    selectedCount: selectedUserIds.length,
    availableActionsCount: availableActions.length,
    loading,
    showDropdown
  });

  return (
    <div className="flex items-center space-x-3">
      {/* Selected count */}
      <div className="flex items-center text-sm text-gray-600">
        <Users className="h-4 w-4 mr-1" />
        <span className="font-medium">{selectedUserIds.length}</span>
        <span className="ml-1">selected</span>
      </div>

      {/* Bulk actions dropdown */}
      <div className="relative">
        <button
          onClick={() => setShowDropdown(!showDropdown)}
          disabled={loading}
          className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
              Processing...
            </>
          ) : (
            <>
              Bulk Actions
              <ChevronDown className="h-4 w-4 ml-2" />
            </>
          )}
        </button>

        {/* Dropdown menu */}
        {showDropdown && !loading && (
          <div className="absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-10">
            <div className="py-1">
              {availableActions.map((action) => {
                const Icon = action.icon;
                return (
                  <button
                    key={action.id}
                    onClick={() => {
                      console.log('🔧 BulkActionsToolbar: Action triggered', {
                        actionId: action.id,
                        selectedCount: selectedUserIds.length
                      });
                      action.action();
                    }}
                    className={`group flex items-center w-full px-4 py-2 text-sm hover:bg-gray-100 ${
                      action.dangerous ? 'text-red-700 hover:bg-red-50' : 'text-gray-700'
                    }`}
                  >
                    <Icon className={`h-4 w-4 mr-3 ${action.color}`} />
                    {action.label}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Error display */}
      {error && (
        <div className="flex items-center text-sm text-red-600">
          <AlertTriangle className="h-4 w-4 mr-1" />
          <span>{error}</span>
          <button
            onClick={() => setError(null)}
            className="ml-2 text-red-400 hover:text-red-600"
          >
            ×
          </button>
        </div>
      )}

      {/* Click outside to close dropdown */}
      {showDropdown && (
        <div
          className="fixed inset-0 z-0"
          onClick={() => setShowDropdown(false)}
        />
      )}
    </div>
  );
});

export default BulkActionsToolbar;


import React, { memo, useCallback, useState, useEffect } from 'react';
import { X, User, Mail, Phone, Shield, Lock, Unlock, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { userManagementApi } from '../api/userManagementApi';
import { User as UserType, UserUpdateRequest, Role } from '../types/auth';

interface EditUserModalProps {
  isOpen: boolean;
  user: UserType;
  onClose: () => void;
  onUserUpdated: () => void;
}

const EditUserModal = memo(function EditUserModal({
  isOpen,
  user,
  onClose,
  onUserUpdated
}: EditUserModalProps) {
  console.log('🔧 EditUserModal: Component initializing', { 
    isOpen, 
    userId: user?.id,
    userEmail: user?.email 
  });

  const { hasPermission } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [roles, setRoles] = useState<Role[]>([]);
  const [rolesLoading, setRolesLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'basic' | 'roles' | 'status'>('basic');

  const [formData, setFormData] = useState<UserUpdateRequest>({
    full_name: '',
    email: '',
    phone: '',
    is_active: true,
    is_verified: false,
    is_locked: false,
    must_change_password: false,
    avatar_url: '',
    role_ids: []
  });

  // Permission checks
  const canUpdate = hasPermission('auth', 'update', 'users');
  const canManageRoles = hasPermission('auth', 'manage', 'roles');

  console.log('🔧 EditUserModal: Permissions', { canUpdate, canManageRoles });

  // Initialize form data when user changes
  useEffect(() => {
    if (user && isOpen) {
      console.log('🔧 EditUserModal: Initializing form data', {
        userId: user.id,
        userRoles: user.roles?.map(r => r.id)
      });
      
      setFormData({
        full_name: user.full_name || '',
        email: user.email || '',
        phone: user.phone || '',
        is_active: user.is_active,
        is_verified: user.is_verified,
        is_locked: user.is_locked,
        must_change_password: user.must_change_password,
        avatar_url: user.avatar_url || '',
        role_ids: user.roles?.map(role => role.id) || []
      });
      setError(null);
    }
  }, [user, isOpen]);

  // Load roles when modal opens
  useEffect(() => {
    if (isOpen) {
      const loadRoles = async () => {
        try {
          console.log('🔧 EditUserModal: Loading roles');
          setRolesLoading(true);
          const rolesData = await userManagementApi.getRoles();
          console.log('🔧 EditUserModal: Roles loaded', { count: rolesData.length });
          setRoles(rolesData);
        } catch (error) {
          console.error('🔧 EditUserModal: Error loading roles', error);
        } finally {
          setRolesLoading(false);
        }
      };

      loadRoles();
    }
  }, [isOpen]);

  // Handle form field changes
  const handleFieldChange = useCallback((field: keyof UserUpdateRequest, value: any) => {
    console.log('🔧 EditUserModal: Field changed', { field, value });
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(null);
  }, []);

  // Handle role selection
  const handleRoleToggle = useCallback((roleId: string) => {
    console.log('🔧 EditUserModal: Role toggled', { roleId });
    setFormData(prev => ({
      ...prev,
      role_ids: prev.role_ids?.includes(roleId)
        ? prev.role_ids.filter(id => id !== roleId)
        : [...(prev.role_ids || []), roleId]
    }));
  }, []);

  // Handle quick status actions
  const handleQuickAction = useCallback(async (action: string) => {
    if (!canUpdate) {
      setError('You do not have permission to update users');
      return;
    }

    console.log('🔧 EditUserModal: Quick action triggered', { action, userId: user.id });

    try {
      setLoading(true);
      setError(null);

      switch (action) {
        case 'lock':
          await userManagementApi.lockUser(user.id);
          setFormData(prev => ({ ...prev, is_locked: true }));
          break;
        case 'unlock':
          await userManagementApi.unlockUser(user.id);
          setFormData(prev => ({ ...prev, is_locked: false }));
          break;
        case 'reset_password':
          await userManagementApi.resetPassword(user.id);
          setFormData(prev => ({ ...prev, must_change_password: true }));
          break;
        default:
          console.warn('🔧 EditUserModal: Unknown quick action', { action });
      }

      console.log('🔧 EditUserModal: Quick action completed', { action });
      onUserUpdated();
      
    } catch (err: any) {
      console.error('🔧 EditUserModal: Quick action failed', {
        action,
        error: err.message
      });
      setError(err.response?.data?.detail || `Failed to ${action} user`);
    } finally {
      setLoading(false);
    }
  }, [user.id, canUpdate, onUserUpdated]);

  // Validate form
  const validateForm = useCallback(() => {
    const errors: string[] = [];

    if (!formData.full_name?.trim()) {
      errors.push('Full name is required');
    }

    if (!formData.email?.trim()) {
      errors.push('Email is required');
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.push('Please enter a valid email address');
    }

    if (!formData.phone?.trim()) {
      errors.push('Phone number is required');
    }

    console.log('🔧 EditUserModal: Form validation', {
      isValid: errors.length === 0,
      errors
    });

    return errors;
  }, [formData]);

  // Handle form submission
  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!canUpdate) {
      console.warn('🔧 EditUserModal: No update permission');
      setError('You do not have permission to update users');
      return;
    }

    const validationErrors = validateForm();
    if (validationErrors.length > 0) {
      setError(validationErrors.join(', '));
      return;
    }

    console.log('🔧 EditUserModal: Form submission started', {
      userId: user.id,
      formData
    });

    try {
      setLoading(true);
      setError(null);
      
      const startTime = performance.now();
      
      // Update basic user info
      await userManagementApi.updateUser(user.id, formData);
      
      // Update roles if user has permission and roles changed
      if (canManageRoles && formData.role_ids) {
        const currentRoleIds = user.roles?.map(r => r.id) || [];
        const newRoleIds = formData.role_ids;
        
        if (JSON.stringify(currentRoleIds.sort()) !== JSON.stringify(newRoleIds.sort())) {
          console.log('🔧 EditUserModal: Updating roles', {
            currentRoles: currentRoleIds,
            newRoles: newRoleIds
          });
          await userManagementApi.assignRoles(user.id, newRoleIds);
        }
      }
      
      const endTime = performance.now();
      
      console.log('🔧 EditUserModal: User updated successfully', {
        duration: `${(endTime - startTime).toFixed(2)}ms`,
        userId: user.id
      });

      onUserUpdated();
      onClose();
      
    } catch (err: any) {
      console.error('🔧 EditUserModal: User update failed', {
        error: err.message,
        status: err.response?.status,
        data: err.response?.data
      });
      
      setError(err.response?.data?.detail || 'Failed to update user');
    } finally {
      setLoading(false);
    }
  }, [formData, user, canUpdate, canManageRoles, validateForm, onUserUpdated, onClose]);

  if (!isOpen || !user) {
    return null;
  }

  if (!canUpdate) {
    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
        <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
          <div className="text-center">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Access Denied</h3>
            <p className="text-gray-500 mb-4">
              You do not have permission to edit users.
            </p>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  console.log('🔧 EditUserModal: Rendering modal', {
    activeTab,
    loading,
    rolesLoading,
    rolesCount: roles.length
  });

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-10 mx-auto p-5 border w-full max-w-3xl shadow-lg rounded-md bg-white">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <User className="h-5 w-5 mr-2" />
              Edit User: {user.full_name}
            </h3>
            <p className="text-sm text-gray-500 mt-1">{user.email}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Quick Actions */}
        <div className="flex items-center space-x-2 mb-6 p-3 bg-gray-50 rounded-lg">
          <span className="text-sm font-medium text-gray-700">Quick Actions:</span>
          
          <button
            onClick={() => handleQuickAction(user.is_locked ? 'unlock' : 'lock')}
            disabled={loading}
            className={`inline-flex items-center px-3 py-1 rounded text-xs font-medium ${
              user.is_locked
                ? 'bg-green-100 text-green-800 hover:bg-green-200'
                : 'bg-red-100 text-red-800 hover:bg-red-200'
            } disabled:opacity-50`}
          >
            {user.is_locked ? <Unlock className="h-3 w-3 mr-1" /> : <Lock className="h-3 w-3 mr-1" />}
            {user.is_locked ? 'Unlock' : 'Lock'} Account
          </button>

          <button
            onClick={() => handleQuickAction('reset_password')}
            disabled={loading}
            className="inline-flex items-center px-3 py-1 rounded text-xs font-medium bg-orange-100 text-orange-800 hover:bg-orange-200 disabled:opacity-50"
          >
            <AlertTriangle className="h-3 w-3 mr-1" />
            Reset Password
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <div className="text-red-800 text-sm">{error}</div>
          </div>
        )}

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'basic', label: 'Basic Info', icon: User },
              { id: 'roles', label: 'Roles & Permissions', icon: Shield },
              { id: 'status', label: 'Account Status', icon: CheckCircle }
            ].map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-4 w-4 mr-2" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          {/* Basic Info Tab */}
          {activeTab === 'basic' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    <User className="inline h-4 w-4 mr-1" />
                    Full Name *
                  </label>
                  <input
                    type="text"
                    value={formData.full_name || ''}
                    onChange={(e) => handleFieldChange('full_name', e.target.value)}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    <Mail className="inline h-4 w-4 mr-1" />
                    Email Address *
                  </label>
                  <input
                    type="email"
                    value={formData.email || ''}
                    onChange={(e) => handleFieldChange('email', e.target.value)}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    <Phone className="inline h-4 w-4 mr-1" />
                    Phone Number *
                  </label>
                  <input
                    type="tel"
                    value={formData.phone || ''}
                    onChange={(e) => handleFieldChange('phone', e.target.value)}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Avatar URL
                  </label>
                  <input
                    type="url"
                    value={formData.avatar_url || ''}
                    onChange={(e) => handleFieldChange('avatar_url', e.target.value)}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="https://example.com/avatar.jpg"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Roles Tab */}
          {activeTab === 'roles' && (
            <div className="space-y-6">
              {!canManageRoles ? (
                <div className="text-center py-8">
                  <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Access Denied</h3>
                  <p className="text-gray-500">
                    You do not have permission to manage user roles.
                  </p>
                </div>
              ) : rolesLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-500">Loading roles...</p>
                </div>
              ) : (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-4">
                    Assign Roles to User
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-64 overflow-y-auto border border-gray-200 rounded-md p-4">
                    {roles.map(role => (
                      <label key={role.id} className="flex items-start">
                        <input
                          type="checkbox"
                          checked={formData.role_ids?.includes(role.id) || false}
                          onChange={() => handleRoleToggle(role.id)}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-0.5"
                        />
                        <div className="ml-3">
                          <div className="text-sm font-medium text-gray-700">
                            {role.display_name || role.name}
                          </div>
                          {role.description && (
                            <div className="text-xs text-gray-500">
                              {role.description}
                            </div>
                          )}
                        </div>
                      </label>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Status Tab */}
          {activeTab === 'status' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h4 className="text-sm font-medium text-gray-700">Account Status</h4>
                  
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.is_active}
                      onChange={(e) => handleFieldChange('is_active', e.target.checked)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">
                      Account is active (user can login)
                    </span>
                  </label>

                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.is_verified}
                      onChange={(e) => handleFieldChange('is_verified', e.target.checked)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">
                      Email is verified
                    </span>
                  </label>
                </div>

                <div className="space-y-4">
                  <h4 className="text-sm font-medium text-gray-700">Security Settings</h4>
                  
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.is_locked}
                      onChange={(e) => handleFieldChange('is_locked', e.target.checked)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">
                      Account is locked
                    </span>
                  </label>

                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.must_change_password}
                      onChange={(e) => handleFieldChange('must_change_password', e.target.checked)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">
                      Must change password on next login
                    </span>
                  </label>
                </div>
              </div>

              {/* User Stats */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-700 mb-3">User Statistics</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <div className="text-gray-500">Failed Login Attempts</div>
                    <div className="font-medium">{user.failed_login_attempts || 0}</div>
                  </div>
                  <div>
                    <div className="text-gray-500">Last Login</div>
                    <div className="font-medium">
                      {user.last_login_at 
                        ? new Date(user.last_login_at).toLocaleDateString()
                        : 'Never'
                      }
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-500">Created</div>
                    <div className="font-medium">
                      {new Date(user.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-500">Updated</div>
                    <div className="font-medium">
                      {user.updated_at 
                        ? new Date(user.updated_at).toLocaleDateString()
                        : 'Never'
                      }
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-end space-x-3 pt-6 border-t mt-8">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2 inline-block"></div>
                  Updating...
                </>
              ) : (
                'Update User'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
});

export default EditUserModal;


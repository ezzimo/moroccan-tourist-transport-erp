import React, { memo, useCallback, useState, useEffect } from 'react';
import { X, User, Mail, Phone, Lock, Shield, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { userManagementApi } from '../api/userManagementApi';
import { UserCreateRequest, Role } from '../types/auth';

interface CreateUserModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUserCreated: () => void;
}

const CreateUserModal = memo(function CreateUserModal({
  isOpen,
  onClose,
  onUserCreated
}: CreateUserModalProps) {
  console.log('🔧 CreateUserModal: Component initializing', { isOpen });

  const { hasPermission } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [roles, setRoles] = useState<Role[]>([]);
  const [rolesLoading, setRolesLoading] = useState(true);

  const [formData, setFormData] = useState<UserCreateRequest>({
    full_name: '',
    email: '',
    phone: '',
    password: '',
    role_ids: [],
    is_verified: false,
    must_change_password: true,
    avatar_url: ''
  });

  // Permission check
  const canCreate = hasPermission('auth', 'create', 'users');

  console.log('🔧 CreateUserModal: Permissions', { canCreate });

  // Load roles when modal opens
  useEffect(() => {
    if (isOpen) {
      const loadRoles = async () => {
        try {
          console.log('🔧 CreateUserModal: Loading roles');
          setRolesLoading(true);
          const rolesData = await userManagementApi.getRoles();
          console.log('🔧 CreateUserModal: Roles loaded', { count: rolesData.length });
          setRoles(rolesData);
        } catch (error) {
          console.error('🔧 CreateUserModal: Error loading roles', error);
        } finally {
          setRolesLoading(false);
        }
      };

      loadRoles();
    }
  }, [isOpen]);

  // Reset form when modal closes
  useEffect(() => {
    if (!isOpen) {
      console.log('🔧 CreateUserModal: Resetting form');
      setFormData({
        full_name: '',
        email: '',
        phone: '',
        password: '',
        role_ids: [],
        is_verified: false,
        must_change_password: true,
        avatar_url: ''
      });
      setError(null);
      setShowPassword(false);
    }
  }, [isOpen]);

  // Handle form field changes
  const handleFieldChange = useCallback((field: keyof UserCreateRequest, value: any) => {
    console.log('🔧 CreateUserModal: Field changed', { field, value });
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(null); // Clear error when user makes changes
  }, []);

  // Handle role selection
  const handleRoleToggle = useCallback((roleId: string) => {
    console.log('🔧 CreateUserModal: Role toggled', { roleId });
    setFormData(prev => ({
      ...prev,
      role_ids: prev.role_ids?.includes(roleId)
        ? prev.role_ids.filter(id => id !== roleId)
        : [...(prev.role_ids || []), roleId]
    }));
  }, []);

  // Generate random password
  const generatePassword = useCallback(() => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
    const password = Array.from({ length: 12 }, () => chars[Math.floor(Math.random() * chars.length)]).join('');
    console.log('🔧 CreateUserModal: Password generated');
    handleFieldChange('password', password);
    setShowPassword(true);
  }, [handleFieldChange]);

  // Validate form
  const validateForm = useCallback(() => {
    const errors: string[] = [];

    if (!formData.full_name.trim()) {
      errors.push('Full name is required');
    }

    if (!formData.email.trim()) {
      errors.push('Email is required');
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.push('Please enter a valid email address');
    }

    if (!formData.phone.trim()) {
      errors.push('Phone number is required');
    }

    if (!formData.password.trim()) {
      errors.push('Password is required');
    } else if (formData.password.length < 8) {
      errors.push('Password must be at least 8 characters long');
    }

    console.log('🔧 CreateUserModal: Form validation', {
      isValid: errors.length === 0,
      errors
    });

    return errors;
  }, [formData]);

  // Handle form submission
  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!canCreate) {
      console.warn('🔧 CreateUserModal: No create permission');
      setError('You do not have permission to create users');
      return;
    }

    const validationErrors = validateForm();
    if (validationErrors.length > 0) {
      setError(validationErrors.join(', '));
      return;
    }

    console.log('🔧 CreateUserModal: Form submission started', {
      formData: {
        ...formData,
        password: '[REDACTED]'
      }
    });

    try {
      setLoading(true);
      setError(null);
      
      const startTime = performance.now();
      const newUser = await userManagementApi.createUser(formData);
      const endTime = performance.now();
      
      console.log('🔧 CreateUserModal: User created successfully', {
        duration: `${(endTime - startTime).toFixed(2)}ms`,
        userId: newUser.id,
        userEmail: newUser.email
      });

      onUserCreated();
      onClose();
      
    } catch (err: any) {
      console.error('🔧 CreateUserModal: User creation failed', {
        error: err.message,
        status: err.response?.status,
        data: err.response?.data
      });
      
      setError(err.response?.data?.detail || 'Failed to create user');
    } finally {
      setLoading(false);
    }
  }, [formData, canCreate, validateForm, onUserCreated, onClose]);

  if (!isOpen) {
    return null;
  }

  if (!canCreate) {
    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
        <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
          <div className="text-center">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Access Denied</h3>
            <p className="text-gray-500 mb-4">
              You do not have permission to create users.
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

  console.log('🔧 CreateUserModal: Rendering modal', {
    loading,
    rolesLoading,
    rolesCount: roles.length,
    selectedRolesCount: formData.role_ids?.length || 0
  });

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-10 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-medium text-gray-900 flex items-center">
            <User className="h-5 w-5 mr-2" />
            Create New User
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <div className="text-red-800 text-sm">{error}</div>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <User className="inline h-4 w-4 mr-1" />
                Full Name *
              </label>
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => handleFieldChange('full_name', e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter full name"
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
                value={formData.email}
                onChange={(e) => handleFieldChange('email', e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter email address"
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
                value={formData.phone}
                onChange={(e) => handleFieldChange('phone', e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter phone number"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Avatar URL (Optional)
              </label>
              <input
                type="url"
                value={formData.avatar_url}
                onChange={(e) => handleFieldChange('avatar_url', e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="https://example.com/avatar.jpg"
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Lock className="inline h-4 w-4 mr-1" />
              Password *
            </label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={(e) => handleFieldChange('password', e.target.value)}
                className="block w-full px-3 py-2 pr-20 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter password"
                required
              />
              <div className="absolute inset-y-0 right-0 flex items-center space-x-1 pr-3">
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
                <button
                  type="button"
                  onClick={generatePassword}
                  className="text-blue-400 hover:text-blue-600 text-xs"
                  title="Generate Password"
                >
                  Gen
                </button>
              </div>
            </div>
            <p className="mt-1 text-xs text-gray-500">
              Minimum 8 characters. Click "Gen" to generate a secure password.
            </p>
          </div>

          {/* Roles */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Shield className="inline h-4 w-4 mr-1" />
              Roles
            </label>
            {rolesLoading ? (
              <div className="text-sm text-gray-500">Loading roles...</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-32 overflow-y-auto border border-gray-200 rounded-md p-3">
                {roles.map(role => (
                  <label key={role.id} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.role_ids?.includes(role.id) || false}
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

          {/* Account Settings */}
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-gray-700">Account Settings</h4>
            
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.is_verified}
                onChange={(e) => handleFieldChange('is_verified', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-700">
                Mark as verified (user can login immediately)
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
                Require password change on first login
              </span>
            </label>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end space-x-3 pt-6 border-t">
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
                  Creating...
                </>
              ) : (
                'Create User'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
});

export default CreateUserModal;


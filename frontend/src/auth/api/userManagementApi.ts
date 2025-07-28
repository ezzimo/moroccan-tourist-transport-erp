import { client } from '../../api/client';
import {
  User,
  UserSearchParams,
  UserSearchResponse,
  UserActivity,
  UserCreateRequest,
  UserUpdateRequest,
  BulkUserUpdate,
  PasswordResetRequest,
  RoleAssignmentRequest,
  UserStatusUpdate,
  UserImportResult,
  Role,
} from '../types/auth';

export const userManagementApi = {
  // User CRUD operations
  async searchUsers(params: UserSearchParams): Promise<UserSearchResponse> {
    const searchParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          searchParams.append(key, value.join(','));
        } else {
          searchParams.append(key, String(value));
        }
      }
    });

    const response = await client.get(`/users/search?${searchParams.toString()}`);
    return response.data;
  },

  async getUser(userId: string): Promise<User> {
    const response = await client.get(`/users/${userId}`);
    return response.data;
  },

  async createUser(userData: UserCreateRequest): Promise<User> {
    const response = await client.post('/users/', userData);
    return response.data;
  },

  async updateUser(userId: string, userData: UserUpdateRequest): Promise<User> {
    const response = await client.put(`/users/${userId}`, userData);
    return response.data;
  },

  async deleteUser(userId: string, hardDelete: boolean = false): Promise<{ message: string }> {
    const response = await client.delete(`/users/${userId}?hard_delete=${hardDelete}`);
    return response.data;
  },

  // Role management
  async assignRoles(userId: string, roleIds: string[]): Promise<{ message: string }> {
    const response = await client.put(`/users/${userId}/roles`, { role_ids: roleIds });
    return response.data;
  },

  async getRoles(): Promise<Role[]> {
    const response = await client.get('/roles/');
    return response.data;
  },

  // User status management
  async updateUserStatus(userId: string, statusData: UserStatusUpdate): Promise<{ message: string }> {
    const response = await client.put(`/users/${userId}/status`, statusData);
    return response.data;
  },

  async lockUser(userId: string): Promise<{ message: string }> {
    const response = await client.post(`/users/${userId}/lock`);
    return response.data;
  },

  async unlockUser(userId: string): Promise<{ message: string }> {
    const response = await client.post(`/users/${userId}/unlock`);
    return response.data;
  },

  async resetPassword(userId: string, passwordData?: PasswordResetRequest): Promise<{
    message: string;
    temporary_password?: string;
    must_change_password: boolean;
  }> {
    const response = await client.post(`/users/${userId}/reset-password`, passwordData);
    return response.data;
  },

  // Activity and audit
  async getUserActivity(userId: string, limit: number = 50): Promise<UserActivity[]> {
    const response = await client.get(`/users/${userId}/activity?limit=${limit}`);
    return response.data;
  },

  // Bulk operations
  async bulkUpdateStatus(bulkData: BulkUserUpdate): Promise<{
    message: string;
    updated_count: number;
  }> {
    const response = await client.put('/users/bulk-status', bulkData);
    return response.data;
  },

  // Import/Export
  async exportUsers(format: 'csv' | 'json' = 'csv', includeDeleted: boolean = false): Promise<Blob> {
    const response = await client.get(`/users/export?format=${format}&include_deleted=${includeDeleted}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  async importUsers(file: File): Promise<UserImportResult> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await client.post('/users/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Utility functions
  async downloadExport(format: 'csv' | 'json' = 'csv', includeDeleted: boolean = false): Promise<void> {
    const blob = await this.exportUsers(format, includeDeleted);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `users_export.${format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },

  // User statistics
  async getUserStats(): Promise<{
    total_users: number;
    active_users: number;
    locked_users: number;
    unverified_users: number;
    recent_signups: number;
  }> {
    // This would be implemented as a separate endpoint in the backend
    // For now, we'll calculate from search results
    const allUsers = await this.searchUsers({ limit: 10000 });
    const activeUsers = allUsers.users.filter(user => user.is_active);
    const lockedUsers = allUsers.users.filter(user => user.is_locked);
    const unverifiedUsers = allUsers.users.filter(user => !user.is_verified);
    
    // Recent signups (last 30 days)
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    const recentUsers = allUsers.users.filter(user => 
      new Date(user.created_at) > thirtyDaysAgo
    );

    return {
      total_users: allUsers.total,
      active_users: activeUsers.length,
      locked_users: lockedUsers.length,
      unverified_users: unverifiedUsers.length,
      recent_signups: recentUsers.length,
    };
  },
};


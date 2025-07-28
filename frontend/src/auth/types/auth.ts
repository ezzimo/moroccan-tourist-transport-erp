export interface Role {
  id: string;
  name: string;
  display_name: string;
  description?: string;
}

export interface User {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  is_active: boolean;
  is_verified: boolean;
  is_locked: boolean;
  must_change_password: boolean;
  avatar_url?: string;
  failed_login_attempts: number;
  last_login_at?: string;
  created_at: string;
  updated_at?: string;
  deleted_at?: string;
  roles: Role[];
  permissions: string[];
}

export interface UserSearchFilters {
  search?: string;
  role_ids?: string[];
  is_active?: boolean;
  is_verified?: boolean;
  is_locked?: boolean;
  created_after?: string;
  created_before?: string;
  last_login_after?: string;
  last_login_before?: string;
  include_deleted?: boolean;
}

export interface UserSearchParams extends UserSearchFilters {
  skip?: number;
  limit?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface UserSearchResponse {
  users: User[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

export interface UserActivity {
  id: string;
  action: string;
  resource: string;
  description: string;
  actor_email: string;
  target_user_email?: string;
  metadata: Record<string, any>;
  ip_address?: string;
  created_at: string;
}

export interface BulkUserUpdate {
  user_ids: string[];
  status_updates: Record<string, any>;
}

export interface UserCreateRequest {
  full_name: string;
  email: string;
  phone: string;
  password: string;
  role_ids?: string[];
  is_verified?: boolean;
  must_change_password?: boolean;
  avatar_url?: string;
}

export interface UserUpdateRequest {
  full_name?: string;
  email?: string;
  phone?: string;
  is_active?: boolean;
  is_verified?: boolean;
  is_locked?: boolean;
  must_change_password?: boolean;
  avatar_url?: string;
  role_ids?: string[];
}

export interface PasswordResetRequest {
  new_password?: string;
}

export interface RoleAssignmentRequest {
  role_ids: string[];
}

export interface UserStatusUpdate {
  is_active?: boolean;
  is_locked?: boolean;
  is_verified?: boolean;
  must_change_password?: boolean;
}

export interface UserImportResult {
  message: string;
  created_count: number;
  error_count: number;
  errors: string[];
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface UserMeResponse {
  permissions: string[];
  roles: Role[];
}

// Permission constants for user management
export const USER_PERMISSIONS = {
  READ: 'auth:read:users',
  CREATE: 'auth:create:users',
  UPDATE: 'auth:update:users',
  DELETE: 'auth:delete:users',
  MANAGE_ROLES: 'auth:manage:roles',
  VIEW_ACTIVITY: 'auth:read:activity',
  BULK_OPERATIONS: 'auth:bulk:users',
  IMPORT_EXPORT: 'auth:import_export:users',
} as const;

// User status constants
export const USER_STATUS = {
  ACTIVE: 'active',
  INACTIVE: 'inactive',
  LOCKED: 'locked',
  PENDING_VERIFICATION: 'pending_verification',
} as const;

// Activity action constants
export const ACTIVITY_ACTIONS = {
  USER_CREATED: 'user_created',
  USER_UPDATED: 'user_updated',
  USER_DELETED: 'user_deleted',
  USER_LOCKED: 'user_locked',
  USER_UNLOCKED: 'user_unlocked',
  PASSWORD_RESET: 'user_password_reset',
  ROLE_ASSIGNED: 'role_assigned',
  BULK_UPDATE: 'users_bulk_updated',
} as const;
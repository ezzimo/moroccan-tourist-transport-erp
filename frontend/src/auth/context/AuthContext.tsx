import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { authApi } from '../api/authApi';
import { User, AuthState, LoginCredentials } from '../types/auth';

interface AuthContextType {
  state: AuthState;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  refreshUserData: () => Promise<void>;
  hasPermission: (resource: string, action: string, scope?: string) => boolean;
  isAdmin: boolean;
  permissions: string[];
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: { user: User; token: string; expiresIn: number } }
  | { type: 'LOGIN_ERROR'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'SET_USER'; payload: User }
  | { type: 'REFRESH_USER_START' }
  | { type: 'REFRESH_USER_SUCCESS'; payload: User }
  | { type: 'REFRESH_USER_ERROR'; payload: string };

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('access_token'),
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, isLoading: true, error: null };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    case 'LOGIN_ERROR':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      };
    case 'SET_USER':
      return {
        ...state,
        user: action.payload,
        isAuthenticated: true,
        isLoading: false,
      };
    case 'REFRESH_USER_START':
      return { ...state, isLoading: true };
    case 'REFRESH_USER_SUCCESS':
      return {
        ...state,
        user: action.payload,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    case 'REFRESH_USER_ERROR':
      return {
        ...state,
        isLoading: false,
        error: action.payload,
      };
    default:
      return state;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('access_token');
      const tokenExpiry = localStorage.getItem('token_expiry');

      if (token && tokenExpiry && Date.now() < parseInt(tokenExpiry)) {
        try {
          const userData = await authApi.me();
          dispatch({ type: 'SET_USER', payload: userData });
        } catch (error) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('token_expiry');
          dispatch({ type: 'LOGOUT' });
        }
      } else {
        dispatch({ type: 'LOGOUT' });
      }
    };

    initializeAuth();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    dispatch({ type: 'LOGIN_START' });
    try {
      const response = await authApi.login(credentials);
      const { access_token, expires_in, user } = response;

      localStorage.setItem('access_token', access_token);
      localStorage.setItem('token_expiry', (Date.now() + expires_in * 1000).toString());

      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: { user, token: access_token, expiresIn: expires_in },
      });

      // 🔄 Immediately refresh the user context with full role & permission
      // details.  The login response only contains basic user info; the
      // `/auth/me` endpoint returns roles and permissions.  Without this
      // extra call the AuthContext would not populate isAdmin and
      // permission checks correctly until the next page refresh.
      try {
        const userData = await authApi.me();
        dispatch({ type: 'SET_USER', payload: userData as unknown as User });
      } catch (err) {
        console.error('Failed to fetch full user data after login:', err);
      }
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Login failed';
      dispatch({ type: 'LOGIN_ERROR', payload: message });
      throw new Error(message);
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('token_expiry');
      dispatch({ type: 'LOGOUT' });
    }
  };

  const refreshUser = async () => {
    try {
      const userData = await authApi.me();
      dispatch({ type: 'SET_USER', payload: userData });
    } catch (error) {
      console.error('Failed to refresh user:', error);
    }
  };

  const refreshUserData = async () => {
    dispatch({ type: 'REFRESH_USER_START' });
    try {
      const userData = await authApi.me();
      dispatch({ type: 'REFRESH_USER_SUCCESS', payload: userData });
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to refresh user data';
      dispatch({ type: 'REFRESH_USER_ERROR', payload: message });
      console.error('Failed to refresh user data:', error);
    }
  };

  // Check if user has specific permission

  // ✅ UPDATED `hasPermission` in `AuthContext.tsx` to support `resource=all` logic.

  const hasPermission = (service: string, action: string, resource: string = 'all'): boolean => {
    if (!state.user || !state.user.permissions) return false;

    const permissionVariants = [
      `${service}:${action}:${resource}`,       // Exact match
      `${service}:${action}:all`,               // Allow if resource is 'all'
      `${service}:${action}:*`,                 // Wildcard resource
      `${service}:*:${resource}`,               // Wildcard action
      `${service}:*:*`,                         // Full service access
      `*:*:*`                                   // Super admin
    ];

    const result = permissionVariants.some(p => state.user!.permissions.includes(p));

    if (!result) {
      console.warn('[RBAC] ⛔ Permission denied:', {
        attempted: `${service}:${action}:${resource}`,
        user: state.user.email,
        available: state.user.permissions,
      });
    } else {
      console.log('[RBAC] ✅ Permission granted:', `${service}:${action}:${resource}`);
    }

    return result;
  };

  // ✨ Use case in `AdminUserManagement.tsx`
  const canRead = hasPermission('auth', 'read', 'users');
  const canCreate = hasPermission('auth', 'create', 'users');
  // ... etc

  // ✅ This now works properly even if your DB only stores `auth:read:all` or `auth:*:*`
  // and the call uses `hasPermission('auth', 'read', 'users')`

  // const hasPermission = (resource: string, action: string, scope: string = "*"): boolean => {
  //   if (!state.user || !state.user.permissions) {
  //     return false;
  //   }

  //   // Check for exact permission match
  //   const exactPermission = `${resource}:${action}:${scope}`;
  //   if (state.user.permissions.includes(exactPermission)) {
  //     return true;
  //   }

  //   // Check for wildcard scope permission
  //   const wildcardPermission = `${resource}:${action}:*`;
  //   if (state.user.permissions.includes(wildcardPermission)) {
  //     return true;
  //   }

  //   // Check for admin permissions (full access)
  //   const adminPermission = `${resource}:*:*`;
  //   if (state.user.permissions.includes(adminPermission)) {
  //     return true;
  //   }

  //   // Check for super admin (all permissions)
  //   if (state.user.permissions.includes("*:*:*")) {
  //     return true;
  //   }

  //   return false;
  // };

  // Check if user is admin
  const isAdmin = (): boolean => {
    if (!state.user || !state.user.roles) {
      return false;
    }

    const adminRoles = ['super_admin', 'tenant_admin', 'role_manager', 'user_manager'];
    return state.user.roles.some(role => adminRoles.includes(role.name));
  };

  // Get all user permissions
  const permissions = state.user?.permissions || [];

  return (
    <AuthContext.Provider 
      value={{ 
        state, 
        login, 
        logout, 
        refreshUser, 
        refreshUserData,
        hasPermission, 
        isAdmin: isAdmin(), 
        permissions 
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
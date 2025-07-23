export interface User {
  id: string;
  full_name: string;
  email: string;
  is_active: boolean;
  roles: string[];
  permissions?: string[];
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
  roles: string[];
}
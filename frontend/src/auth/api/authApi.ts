import { apiClient } from '../../api/client';
import { LoginCredentials, LoginResponse, User, UserMeResponse } from '../types/auth';

export const authApi = {
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    const response = await apiClient.post('/auth/login', credentials);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout');
  },

  me: async (): Promise<User> => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  sendOtp: async (email: string): Promise<{ message: string; expires_in: number }> => {
    const response = await apiClient.post('/auth/send-otp', { email });
    return response.data;
  },

  verifyOtp: async (email: string, otp_code: string): Promise<{ message: string }> => {
    const response = await apiClient.post('/auth/verify-otp', { email, otp_code });
    return response.data;
  },
};
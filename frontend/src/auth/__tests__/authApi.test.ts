import { describe, it, expect, vi, beforeEach } from 'vitest'
import { authApi } from '../api/authApi'
import apiClient from '../../api/client'

// Mock the API client
vi.mock('../../api/client', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
}))

describe('authApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('login', () => {
    it('should make POST request to login endpoint', async () => {
      const mockResponse = {
        data: {
          access_token: 'mock-token',
          token_type: 'bearer',
          user: {
            id: '1',
            email: 'test@example.com',
            full_name: 'Test User',
            is_active: true,
          },
        },
      }

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse)

      const credentials = {
        email: 'test@example.com',
        password: 'password123',
      }

      const result = await authApi.login(credentials)

      expect(apiClient.post).toHaveBeenCalledWith('/auth/login', credentials)
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle login error', async () => {
      const mockError = new Error('Invalid credentials')
      vi.mocked(apiClient.post).mockRejectedValue(mockError)

      const credentials = {
        email: 'test@example.com',
        password: 'wrongpassword',
      }

      await expect(authApi.login(credentials)).rejects.toThrow('Invalid credentials')
      expect(apiClient.post).toHaveBeenCalledWith('/auth/login', credentials)
    })
  })

  describe('logout', () => {
    it('should make POST request to logout endpoint', async () => {
      const mockResponse = {
        data: { message: 'Successfully logged out' },
      }

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse)

      await authApi.logout()

      expect(apiClient.post).toHaveBeenCalledWith('/auth/logout')
    })

    it('should handle logout error', async () => {
      const mockError = new Error('Logout failed')
      vi.mocked(apiClient.post).mockRejectedValue(mockError)

      await expect(authApi.logout()).rejects.toThrow('Logout failed')
      expect(apiClient.post).toHaveBeenCalledWith('/auth/logout')
    })
  })

  describe('me', () => {
    it('should make GET request to current user endpoint', async () => {
      const mockResponse = {
        data: {
          id: '1',
          email: 'test@example.com',
          full_name: 'Test User',
          is_active: true,
          permissions: ['read:users'],
          roles: ['user'],
        },
      }

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse)

      const result = await authApi.me()

      expect(apiClient.get).toHaveBeenCalledWith('/auth/me')
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle me error', async () => {
      const mockError = new Error('Unauthorized')
      vi.mocked(apiClient.get).mockRejectedValue(mockError)

      await expect(authApi.me()).rejects.toThrow('Unauthorized')
      expect(apiClient.get).toHaveBeenCalledWith('/auth/me')
    })
  })
})


import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, act, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider, useAuth } from '../context/AuthContext'
import { authApi } from '../api/authApi'

// Mock the auth API
vi.mock('../api/authApi', () => ({
  authApi: {
    login: vi.fn(),
    logout: vi.fn(),
    me: vi.fn(),
  },
}))

const TestComponent = () => {
  const { user, isAuthenticated, login, logout, isLoading } = useAuth()
  return (
    <div>
      <div data-testid="auth-status">
        {isAuthenticated ? 'authenticated' : 'not-authenticated'}
      </div>
      <div data-testid="user-email">{user?.email || 'no-user'}</div>
      <div data-testid="loading">{isLoading ? 'loading' : 'not-loading'}</div>
      <button onClick={() => login({ email: 'test@example.com', password: 'password' })}>
        Login
      </button>
      <button onClick={logout}>Logout</button>
    </div>
  )
}

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('provides initial unauthenticated state', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    expect(screen.getByTestId('auth-status')).toHaveTextContent('not-authenticated')
    expect(screen.getByTestId('user-email')).toHaveTextContent('no-user')
  })

  it('handles successful login', async () => {
    const mockLoginResponse = {
      access_token: 'mock-token',
      token_type: 'bearer',
      user: {
        id: '1',
        email: 'test@example.com',
        full_name: 'Test User',
        is_active: true,
      },
    }

    vi.mocked(authApi.login).mockResolvedValue(mockLoginResponse)

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    const loginButton = screen.getByText('Login')
    
    await act(async () => {
      loginButton.click()
    })

    expect(authApi.login).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password',
    })
  })

  it('handles logout', async () => {
    // Set up authenticated state
    localStorage.setItem('token', 'mock-token')
    localStorage.setItem('user', JSON.stringify({
      id: '1',
      email: 'test@example.com',
      full_name: 'Test User',
    }))

    vi.mocked(authApi.logout).mockResolvedValue(undefined)

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    const logoutButton = screen.getByText('Logout')
    
    await act(async () => {
      logoutButton.click()
    })

    expect(authApi.logout).toHaveBeenCalled()
  })

  it('restores authentication state from localStorage', async () => {
    const mockUser = {
      id: '1',
      email: 'test@example.com',
      full_name: 'Test User',
      is_active: true,
      permissions: [],
      roles: [],
    };

    localStorage.setItem('access_token', 'mock-token');
    localStorage.setItem('token_expiry', (Date.now() + 1000 * 60 * 60).toString());

    vi.mocked(authApi.me).mockResolvedValue(mockUser);

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('authenticated');
      expect(screen.getByTestId('user-email')).toHaveTextContent('test@example.com');
    });
  });
})


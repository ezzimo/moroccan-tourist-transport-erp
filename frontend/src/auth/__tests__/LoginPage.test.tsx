import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import LoginPage from '../pages/LoginPage'
import { AuthProvider } from '../context/AuthContext'
import { authApi } from '../api/authApi'

// Mock the auth API
vi.mock('../api/authApi', () => ({
  authApi: {
    login: vi.fn(),
  },
}))

// Mock react-router-dom
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          {children}
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders login form', () => {
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    )

    expect(screen.getByText('Sign In')).toBeInTheDocument()
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })

  it('handles form submission with valid credentials', async () => {
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
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    )

    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(authApi.login).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      })
    })
  })

  it('displays error message on login failure', async () => {
    vi.mocked(authApi.login).mockRejectedValue({ response: { data: { detail: 'Invalid credentials' } } })

    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    )

    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument()
    })
  })

  it('validates required fields', async () => {
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    )

    const submitButton = screen.getByRole('button', { name: /sign in/i })
    fireEvent.click(submitButton)

    await new Promise(r => setTimeout(r, 100));

    expect(await screen.findByTestId('email-error')).toHaveTextContent('Email is required')
    expect(await screen.findByTestId('password-error')).toHaveTextContent('Password is required')
  })
})


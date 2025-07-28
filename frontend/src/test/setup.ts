import '@testing-library/jest-dom'

// Mock environment variables
Object.defineProperty(window, 'location', {
  value: {
    origin: 'http://localhost:3000',
  },
  writable: true,
})

// Mock fetch
global.fetch = vi.fn()

// Setup cleanup after each test
afterEach(() => {
  vi.clearAllMocks()
})


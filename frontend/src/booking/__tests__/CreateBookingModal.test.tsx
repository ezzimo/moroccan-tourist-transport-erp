import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import CreateBookingModal from '../components/CreateBookingModal';
import { useCreateBooking } from '../hooks/useBookings';
import { useCustomers } from '../../crm/hooks/useCustomers';
import { usePricingCalculation } from '../hooks/usePricing';

// Mock the hooks
vi.mock('../hooks/useBookings');
vi.mock('../../crm/hooks/useCustomers');
vi.mock('../hooks/usePricing');

const mockUseCreateBooking = vi.mocked(useCreateBooking);
const mockUseCustomers = vi.mocked(useCustomers);
const mockUsePricingCalculation = vi.mocked(usePricingCalculation);

const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('CreateBookingModal', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    mockUseCreateBooking.mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as any);
    
    mockUseCustomers.mockReturnValue({
      data: {
        items: [
          {
            id: '1',
            full_name: 'Test Customer',
            email: 'test@example.com',
            phone: '+212600000000',
          },
        ],
      },
    } as any);
    
    mockUsePricingCalculation.mockReturnValue({
      data: null,
      error: null,
      isLoading: false,
    } as any);
  });

  it('renders create booking modal', () => {
    render(
      <TestWrapper>
        <CreateBookingModal isOpen={true} onClose={() => {}} />
      </TestWrapper>
    );

    expect(screen.getByText('Create Booking')).toBeInTheDocument();
    expect(screen.getByLabelText(/base price/i)).toBeInTheDocument();
  });

  it('handles base price input without triggering immediate API calls', async () => {
    render(
      <TestWrapper>
        <CreateBookingModal isOpen={true} onClose={() => {}} />
      </TestWrapper>
    );

    const basePriceInput = screen.getByLabelText(/base price/i);
    
    // Type a single digit
    fireEvent.change(basePriceInput, { target: { value: '1' } });
    
    // Should not immediately trigger pricing calculation
    expect(mockUsePricingCalculation).toHaveBeenCalledWith(
      expect.objectContaining({
        base_price: 0, // Should still be 0 until debounce completes
      }),
      false // Should be disabled for incomplete input
    );
  });

  it('validates base price input format', async () => {
    render(
      <TestWrapper>
        <CreateBookingModal isOpen={true} onClose={() => {}} />
      </TestWrapper>
    );

    const basePriceInput = screen.getByLabelText(/base price/i);
    
    // Type invalid characters
    fireEvent.change(basePriceInput, { target: { value: 'abc' } });
    
    // Should show validation error
    await waitFor(() => {
      expect(screen.getByText(/please enter a valid price/i)).toBeInTheDocument();
    });
  });

  it('handles pricing calculation errors gracefully', () => {
    mockUsePricingCalculation.mockReturnValue({
      data: null,
      error: { message: 'Pricing calculation failed' },
      isLoading: false,
    } as any);

    render(
      <TestWrapper>
        <CreateBookingModal isOpen={true} onClose={() => {}} />
      </TestWrapper>
    );

    expect(screen.getByText(/pricing error/i)).toBeInTheDocument();
    expect(screen.getByText(/pricing calculation failed/i)).toBeInTheDocument();
  });

  it('shows loading state during pricing calculation', () => {
    mockUsePricingCalculation.mockReturnValue({
      data: null,
      error: null,
      isLoading: true,
    } as any);

    render(
      <TestWrapper>
        <CreateBookingModal isOpen={true} onClose={() => {}} />
      </TestWrapper>
    );

    expect(screen.getByText(/calculating pricing/i)).toBeInTheDocument();
  });

  it('displays pricing data when calculation succeeds', () => {
    mockUsePricingCalculation.mockReturnValue({
      data: {
        base_price: 100,
        discount_amount: 10,
        total_price: 90,
        currency: 'MAD',
        applied_rules: [],
      },
      error: null,
      isLoading: false,
    } as any);

    render(
      <TestWrapper>
        <CreateBookingModal isOpen={true} onClose={() => {}} />
      </TestWrapper>
    );

    expect(screen.getByText(/pricing calculation/i)).toBeInTheDocument();
    expect(screen.getByText(/100\.00 MAD/)).toBeInTheDocument();
    expect(screen.getByText(/90\.00 MAD/)).toBeInTheDocument();
  });
});
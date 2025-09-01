import React, { useState } from 'react';
import { X, Package } from 'lucide-react';
import { useCreateBooking } from '../hooks/useBookings';
import { useCustomers } from '../../crm/hooks/useCustomers';
import { usePricingCalculation } from '../hooks/usePricing';
import { CreateBookingData } from '../types/booking';
import { useDebounce } from '../../utils/debounce';
import { safeNumber, isValidNumber, formatCurrencyInput, formatMoney } from '../../utils/number';
import { useMemo, useCallback } from 'react';
import ErrorBoundary from '../../components/ErrorBoundary';

interface CreateBookingModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CreateBookingModal({ isOpen, onClose }: CreateBookingModalProps) {
  const createBooking = useCreateBooking();
  const { data: customersData } = useCustomers({ size: 100 });

  const [formData, setFormData] = useState<CreateBookingData>({
    customer_id: '',
    service_type: 'Tour',
    pax_count: 1,
    lead_passenger_name: '',
    lead_passenger_email: '',
    lead_passenger_phone: '',
    start_date: '',
    base_price: 0,
  });

  // Keep base price as string for better input handling
  const [basePriceInput, setBasePriceInput] = useState<string>('');
  const [pricingEnabled, setPricingEnabled] = useState(false);

  // Debounced pricing calculation trigger
  const debouncedEnablePricing = useDebounce(() => {
    const isFormValid = !!(
      formData.service_type &&
      formData.customer_id &&
      formData.start_date &&
      formData.pax_count > 0 &&
      isValidNumber(basePriceInput) &&
      safeNumber(basePriceInput) > 0
    );
    
    if (isFormValid) {
      // Update the numeric value in form data
      setFormData(prev => ({ ...prev, base_price: safeNumber(basePriceInput) }));
      setPricingEnabled(true);
    } else {
      setPricingEnabled(false);
    }
  }, 400);

  // Handle base price input changes
  const handleBasePriceChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const rawValue = e.target.value;
    const cleanedValue = formatCurrencyInput(rawValue);
    
    setBasePriceInput(cleanedValue);
    debouncedEnablePricing();
  }, [debouncedEnablePricing]);


  // Only calculate pricing when all required fields are valid
  const shouldCalculatePricing = useMemo(() => {
    return !!(
      formData.service_type &&
      formData.base_price > 0 &&
      formData.pax_count > 0 &&
      formData.start_date &&
      formData.customer_id
    );
  }, [formData.service_type, formData.base_price, formData.pax_count, formData.start_date, formData.customer_id]);

  // Only calculate pricing when form is valid and enabled
  const pricingRequest = useMemo(() => ({
    service_type: formData.service_type,
    base_price: formData.base_price,
    pax_count: formData.pax_count,
    start_date: formData.start_date,
    customer_id: formData.customer_id,
    promo_code: formData.promo_code,
  }), [formData]);

  const { data: pricingData, error: pricingError, isLoading: pricingLoading } = usePricingCalculation(
    pricingRequest,
    pricingEnabled
  );

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createBooking.mutateAsync(formData);
      console.log('✅ Booking created successfully');
      onClose();
      setFormData({
        customer_id: '',
        service_type: 'Tour',
        pax_count: 1,
        lead_passenger_name: '',
        lead_passenger_email: '',
        lead_passenger_phone: '',
        start_date: '',
        base_price: 0,
      });
    } catch (error) {
      console.error('❌ Failed to create booking:', error);
      
      // Handle typed errors from backend
      const errorType = (error as any)?.type;
      const errorMessage = (error as any)?.message || 'Failed to create booking';
      
      let userMessage = errorMessage;
      
      switch (errorType) {
        case 'customer_not_found':
          userMessage = 'Selected customer not found. Please refresh and try again.';
          break;
        case 'customer_forbidden':
          userMessage = 'Not authorized to access customer information.';
          break;
        case 'customer_service_unreachable':
          userMessage = 'Customer service temporarily unavailable. Please try again.';
          break;
        case 'validation_error':
          userMessage = `Validation error: ${errorMessage}`;
          break;
        case 'booking_create_failed':
          userMessage = 'Unable to create booking. Please try again.';
          break;
        default:
          userMessage = errorMessage;
      }
      
      // You could show this in a toast notification or error state
      // For now, we'll log it and the error will be handled by the mutation error state
      console.warn('User-friendly error message:', userMessage);
    }
  };

  const handleCustomerChange = (customerId: string) => {
    const customer = customersData?.items.find(c => c.id === customerId);
    if (customer) {
      setFormData(prev => ({
        ...prev,
        customer_id: customerId,
        lead_passenger_name: customer.full_name || customer.company_name || '',
        lead_passenger_email: customer.email,
        lead_passenger_phone: customer.phone,
      }));
    }
  };

  const serviceTypes = [
    { value: 'Tour', label: 'Tour' },
    { value: 'Transfer', label: 'Transfer' },
    { value: 'Custom Package', label: 'Custom Package' },
    { value: 'Accommodation', label: 'Accommodation' },
    { value: 'Activity', label: 'Activity' },
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <ErrorBoundary fallback={
        <div className="bg-white rounded-lg max-w-md w-full p-6 text-center">
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Form</h3>
          <p className="text-gray-600 mb-4">There was an error loading the booking form.</p>
          <button onClick={onClose} className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400">
            Close
          </button>
        </div>
      }>
        <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">Create Booking</h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Customer *
            </label>
            <select
              value={formData.customer_id}
              onChange={(e) => handleCustomerChange(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
            >
              <option value="">Select customer</option>
              {customersData?.items.map((customer) => (
                <option key={customer.id} value={customer.id}>
                  {customer.full_name || customer.company_name} - {customer.email}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Service Type *
              </label>
              <select
                value={formData.service_type}
                onChange={(e) => setFormData(prev => ({ ...prev, service_type: e.target.value as any }))}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              >
                {serviceTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Number of Passengers *
              </label>
              <input
                type="number"
                value={formData.pax_count}
                onChange={(e) => setFormData(prev => ({ ...prev, pax_count: parseInt(e.target.value) || 1 }))}
                required
                min="1"
                max="50"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Lead Passenger Name *
              </label>
              <input
                type="text"
                value={formData.lead_passenger_name}
                onChange={(e) => setFormData(prev => ({ ...prev, lead_passenger_name: e.target.value }))}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                placeholder="Full name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email *
              </label>
              <input
                type="email"
                value={formData.lead_passenger_email}
                onChange={(e) => setFormData(prev => ({ ...prev, lead_passenger_email: e.target.value }))}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                placeholder="email@example.com"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Phone *
            </label>
            <input
              type="tel"
              value={formData.lead_passenger_phone}
              onChange={(e) => setFormData(prev => ({ ...prev, lead_passenger_phone: e.target.value }))}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              placeholder="+212612345678"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Start Date *
              </label>
              <input
                type="date"
                value={formData.start_date}
                onChange={(e) => setFormData(prev => ({ ...prev, start_date: e.target.value }))}
                required
                min={new Date().toISOString().split('T')[0]}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                End Date
              </label>
              <input
                type="date"
                value={formData.end_date || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, end_date: e.target.value || undefined }))}
                min={formData.start_date}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Base Price *
              </label>
              <input
                type="number"
                value={basePriceInput}
                onChange={handleBasePriceChange}
                required
                inputMode="decimal"
                pattern="[0-9]*\.?[0-9]*"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                placeholder="0.00"
              />
              {basePriceInput && !isValidNumber(basePriceInput) && (
                <p className="text-red-500 text-sm mt-1">Please enter a valid price</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Promo Code
              </label>
              <input
                type="text"
                value={formData.promo_code || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, promo_code: e.target.value || undefined }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                placeholder="Optional promo code"
              />
            </div>
          </div>

          {pricingLoading && (
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                <span className="text-sm text-gray-600">Calculating pricing...</span>
              </div>
            </div>
          )}

          {pricingData && !pricingLoading && (
            <div className="p-4 bg-blue-50 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-2">Pricing Calculation</h4>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-blue-700">Base Price:</span>
                  <span className="font-medium">{formatMoney(pricingData?.base_price, 2, pricingData?.currency || 'MAD')}</span>
                </div>
                {safeNumber(pricingData?.discount_amount) > 0 && (
                  <div className="flex justify-between">
                    <span className="text-blue-700">Discount:</span>
                    <span className="font-medium text-green-600">-{formatMoney(pricingData?.discount_amount, 2, pricingData?.currency || 'MAD')}</span>
                  </div>
                )}
                <div className="flex justify-between border-t border-blue-200 pt-1">
                  <span className="font-medium text-blue-900">Total:</span>
                  <span className="font-bold text-blue-900">{formatMoney(pricingData?.total_price, 2, pricingData?.currency || 'MAD')}</span>
                </div>
              </div>
            </div>
          )}

          {pricingError && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <h4 className="font-medium text-red-900 mb-2">Pricing Error</h4>
              <p className="text-sm text-red-700">
                {pricingError?.message || 'Unable to calculate pricing. Please check your input values.'}
              </p>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Special Requests
            </label>
            <textarea
              value={formData.special_requests || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, special_requests: e.target.value || undefined }))}
              rows={3}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              placeholder="Any special requests or requirements..."
            />
          </div>

          <div className="flex items-center justify-end gap-4 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createBooking.isPending}
              className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {createBooking.isPending ? 'Creating...' : 'Create Booking'}
            </button>
          </div>
        </form>
      </div>
      </ErrorBoundary>
    </div>
  );
}
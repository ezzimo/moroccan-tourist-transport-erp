import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Calendar, Users, DollarSign, FileText, CheckCircle, X } from 'lucide-react';
import { useBooking } from '../hooks/useBookings';
import { useReservationItems } from '../hooks/useReservations';
import { useConfirmBooking, useCancelBooking } from '../hooks/useBookings';
import LoadingSpinner from '../../components/LoadingSpinner';
import ReservationItemsList from '../components/ReservationItemsList';
import { formatDate } from '../../utils/formatters';
import { formatMoney } from '../../utils/number';

export default function BookingDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [cancelReason, setCancelReason] = useState('');

  const { data: booking, isLoading: bookingLoading } = useBooking(id!);
  const { data: reservationItems, isLoading: itemsLoading } = useReservationItems(id!);
  const confirmBooking = useConfirmBooking();
  const cancelBooking = useCancelBooking();

  if (bookingLoading || itemsLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!booking) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Booking not found</p>
        <Link to="/bookings" className="text-orange-600 hover:text-orange-700 mt-2 inline-block">
          Back to Bookings
        </Link>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    const colors = {
      Pending: 'bg-yellow-100 text-yellow-800',
      Confirmed: 'bg-green-100 text-green-800',
      Cancelled: 'bg-red-100 text-red-800',
      Refunded: 'bg-gray-100 text-gray-800',
      Expired: 'bg-gray-100 text-gray-800',
    };
    return colors[status as keyof typeof colors] || colors.Pending;
  };

  const getPaymentStatusColor = (status: string) => {
    const colors = {
      Pending: 'bg-yellow-100 text-yellow-800',
      Partial: 'bg-blue-100 text-blue-800',
      Paid: 'bg-green-100 text-green-800',
      Failed: 'bg-red-100 text-red-800',
      Refunded: 'bg-gray-100 text-gray-800',
    };
    return colors[status as keyof typeof colors] || colors.Pending;
  };

  const handleConfirm = async () => {
    try {
      await confirmBooking.mutateAsync({
        id: booking.id,
        data: { internal_notes: 'Booking confirmed' },
      });
    } catch (error) {
      console.error('Failed to confirm booking:', error);
    }
  };

  const handleCancel = async () => {
    if (!cancelReason.trim()) return;

    try {
      await cancelBooking.mutateAsync({
        id: booking.id,
        data: { reason: cancelReason },
      });
      setShowCancelModal(false);
      setCancelReason('');
    } catch (error) {
      console.error('Failed to cancel booking:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link
          to="/bookings"
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Booking Details
          </h1>
          <p className="text-gray-600">{booking.lead_passenger_name}</p>
        </div>
      </div>

      {/* Booking Header Card */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex flex-col lg:flex-row gap-6">
          <div className="flex-1 space-y-4">
            <div className="flex items-center gap-4">
              <Calendar className="h-12 w-12 text-orange-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">
                  {booking.service_type} Booking
                </h2>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(booking.status)}`}>
                    {booking.status}
                  </span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPaymentStatusColor(booking.payment_status)}`}>
                    {booking.payment_status}
                  </span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Lead Passenger:</span> {booking.lead_passenger_name}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Email:</span> {booking.lead_passenger_email}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Phone:</span> {booking.lead_passenger_phone}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Passengers:</span> {booking.pax_count}
                </p>
              </div>
              <div className="space-y-2">
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Start Date:</span> {formatDate(booking.start_date)}
                </p>
                {booking.end_date && (
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">End Date:</span> {formatDate(booking.end_date)}
                  </p>
                )}
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Total Price:</span> {formatMoney(booking?.total_price, 2, booking?.currency)}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Created:</span> {formatDate(booking.created_at)}
                </p>
              </div>
            </div>

            {booking.special_requests && (
              <div>
                <p className="text-sm font-medium text-gray-700 mb-1">Special Requests</p>
                <p className="text-sm text-gray-600">{booking.special_requests}</p>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="lg:w-80">
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900">Actions</h3>
              
              {booking.status === 'Pending' && (
                <div className="space-y-2">
                  <button
                    onClick={handleConfirm}
                    disabled={confirmBooking.isPending}
                    className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {confirmBooking.isPending ? 'Confirming...' : 'Confirm Booking'}
                  </button>
                  <button
                    onClick={() => setShowCancelModal(true)}
                    className="w-full bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition-colors"
                  >
                    Cancel Booking
                  </button>
                </div>
              )}

              <button
                onClick={() => {
                  // Download voucher logic
                }}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
              >
                <FileText className="h-4 w-4 mr-2 inline" />
                Download Voucher
              </button>
            </div>

            {/* Pricing Breakdown */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-3">Pricing Breakdown</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Base Price:</span>
                  <span className="font-medium">{formatMoney(booking?.base_price, 2, booking?.currency)}</span>
                </div>
                {(booking?.discount_amount || 0) > 0 && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Discount:</span>
                    <span className="font-medium text-green-600">-{formatMoney(booking?.discount_amount, 2, booking?.currency)}</span>
                  </div>
                )}
                <div className="flex justify-between border-t pt-2">
                  <span className="font-medium text-gray-900">Total:</span>
                  <span className="font-bold text-gray-900">{formatMoney(booking?.total_price, 2, booking?.currency)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Reservation Items */}
      <div className="bg-white rounded-lg border p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Reservation Items</h3>
        <ReservationItemsList bookingId={id!} items={reservationItems || []} />
      </div>

      {/* Cancel Modal */}
      {showCancelModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Cancel Booking</h3>
              <button
                onClick={() => setShowCancelModal(false)}
                className="p-2 text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Cancellation Reason *
              </label>
              <textarea
                value={cancelReason}
                onChange={(e) => setCancelReason(e.target.value)}
                rows={3}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                placeholder="Please provide a reason for cancellation..."
              />
            </div>

            <div className="flex items-center justify-end gap-4">
              <button
                onClick={() => setShowCancelModal(false)}
                className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleCancel}
                disabled={!cancelReason.trim() || cancelBooking.isPending}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {cancelBooking.isPending ? 'Cancelling...' : 'Confirm Cancellation'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
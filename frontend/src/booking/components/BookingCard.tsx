import React from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Users, DollarSign, Package, Clock } from 'lucide-react';
import { Booking } from '../types/booking';
import { formatCurrency, formatDate } from '../../utils/formatters';

interface BookingCardProps {
  booking: Booking;
}

export default function BookingCard({ booking }: BookingCardProps) {
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

  const getServiceTypeColor = (type: string) => {
    const colors = {
      Tour: 'bg-blue-100 text-blue-800',
      Transfer: 'bg-green-100 text-green-800',
      'Custom Package': 'bg-purple-100 text-purple-800',
      Accommodation: 'bg-orange-100 text-orange-800',
      Activity: 'bg-pink-100 text-pink-800',
    };
    return colors[type as keyof typeof colors] || colors.Tour;
  };

  return (
    <Link
      to={`/bookings/${booking.id}`}
      className="block bg-white border rounded-lg p-4 hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <Calendar className="h-10 w-10 text-orange-600" />
          <div>
            <h3 className="font-medium text-gray-900">
              {booking.lead_passenger_name}
            </h3>
            <p className="text-sm text-gray-500">{booking.lead_passenger_email}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getServiceTypeColor(booking.service_type)}`}>
            {booking.service_type}
          </span>
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(booking.status)}`}>
            {booking.status}
          </span>
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPaymentStatusColor(booking.payment_status)}`}>
            {booking.payment_status}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-3">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Users className="h-4 w-4" />
          <span>{booking.pax_count} passenger{booking.pax_count > 1 ? 's' : ''}</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <DollarSign className="h-4 w-4" />
          <span>{formatCurrency(booking.total_price, booking.currency)}</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Calendar className="h-4 w-4" />
          <span>{formatDate(booking.start_date)}</span>
        </div>
        {booking.end_date && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Clock className="h-4 w-4" />
            <span>to {formatDate(booking.end_date)}</span>
          </div>
        )}
      </div>

      {booking.special_requests && (
        <div className="text-sm text-gray-500 mb-2">
          <span className="font-medium">Special Requests:</span> {booking.special_requests}
        </div>
      )}

      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>Created: {formatDate(booking.created_at)}</span>
        {booking.expires_at && booking.status === 'Pending' && (
          <span className={`${booking.is_expired ? 'text-red-600' : 'text-yellow-600'}`}>
            {booking.is_expired ? 'Expired' : `Expires: ${formatDate(booking.expires_at)}`}
          </span>
        )}
      </div>
    </Link>
  );
}
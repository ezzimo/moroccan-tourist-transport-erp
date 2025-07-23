import React from 'react';
import { CreditCard, Calendar, CheckCircle, Clock, X } from 'lucide-react';
import { Payment } from '../types/payment';
import { formatCurrency, formatDate } from '../../utils/formatters';

interface PaymentCardProps {
  payment: Payment;
}

export default function PaymentCard({ payment }: PaymentCardProps) {
  const getStatusColor = (status: string) => {
    const colors = {
      PENDING: 'bg-yellow-100 text-yellow-800',
      CONFIRMED: 'bg-green-100 text-green-800',
      FAILED: 'bg-red-100 text-red-800',
      CANCELLED: 'bg-gray-100 text-gray-800',
    };
    return colors[status as keyof typeof colors] || colors.PENDING;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'CONFIRMED':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'PENDING':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'FAILED':
      case 'CANCELLED':
        return <X className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getPaymentMethodIcon = (method: string) => {
    return <CreditCard className="h-4 w-4" />;
  };

  return (
    <div className="p-4">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          {getStatusIcon(payment.status)}
          <div>
            <h4 className="font-medium text-gray-900">
              {formatCurrency(payment.amount, payment.currency)}
            </h4>
            <div className="flex items-center gap-2 mt-1">
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(payment.status)}`}>
                {payment.status}
              </span>
              <span className="text-sm text-gray-500">{payment.payment_method}</span>
            </div>
          </div>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500">
            {formatDate(payment.payment_date)}
          </p>
          {payment.is_reconciled && (
            <span className="inline-flex items-center text-xs text-green-600">
              ✓ Reconciled
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        {payment.reference_number && (
          <div>
            <p className="font-medium text-gray-700">Reference:</p>
            <p className="text-gray-600">{payment.reference_number}</p>
          </div>
        )}
        {payment.transaction_id && (
          <div>
            <p className="font-medium text-gray-700">Transaction ID:</p>
            <p className="text-gray-600">{payment.transaction_id}</p>
          </div>
        )}
        {payment.processing_fee && (
          <div>
            <p className="font-medium text-gray-700">Processing Fee:</p>
            <p className="text-gray-600">{formatCurrency(payment.processing_fee, payment.currency)}</p>
          </div>
        )}
      </div>

      {payment.description && (
        <div className="mt-3">
          <p className="text-sm text-gray-600">{payment.description}</p>
        </div>
      )}
    </div>
  );
}
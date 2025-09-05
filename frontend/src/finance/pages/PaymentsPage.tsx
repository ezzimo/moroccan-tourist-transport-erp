import React, { useState } from 'react';
import { CreditCard, DollarSign, CheckCircle, Clock } from 'lucide-react';
import { usePayments } from '../hooks/usePayments';
import { PaymentFilters } from '../types/payment';
import LoadingSpinner from '../../components/LoadingSpinner';
import PaymentCard from '../components/PaymentCard';
import CreatePaymentModal from '../components/CreatePaymentModal';
import { toNumber } from '../../utils/number';

export default function PaymentsPage() {
  const [filters, setFilters] = useState<PaymentFilters>({ page: 1, size: 20 });
  const [showCreateModal, setShowCreateModal] = useState(false);

  const { data: paymentsData, isLoading } = usePayments(filters);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const payments = paymentsData?.items || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Payments</h1>
          <p className="text-gray-600">Track and manage customer payments</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
        >
          <CreditCard className="h-5 w-5 mr-2" />
          Record Payment
        </button>
      </div>

      {/* Statistics */}
      {paymentsData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center">
              <DollarSign className="h-8 w-8 text-green-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Total Payments</p>
                <p className="text-2xl font-bold text-gray-900">{paymentsData.total}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Confirmed</p>
                <p className="text-2xl font-bold text-gray-900">
                  {payments.filter(p => p.status === 'CONFIRMED').length}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center">
              <Clock className="h-8 w-8 text-yellow-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Pending</p>
                <p className="text-2xl font-bold text-gray-900">
                  {payments.filter(p => p.status === 'PENDING').length}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center">
              <CreditCard className="h-8 w-8 text-blue-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Total Amount</p>
                <p className="text-2xl font-bold text-gray-900">
                  {payments.reduce((sum, p) => sum + toNumber(p?.amount, 0), 0).toLocaleString()} MAD
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Payment List */}
      <div className="bg-white rounded-lg border">
        <div className="p-6 border-b">
          <h3 className="text-lg font-medium text-gray-900">Recent Payments</h3>
        </div>
        <div className="divide-y">
          {payments.map((payment) => (
            <PaymentCard key={payment.id} payment={payment} />
          ))}
        </div>
      </div>

      {/* Create Payment Modal */}
      <CreatePaymentModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
      />
    </div>
  );
}
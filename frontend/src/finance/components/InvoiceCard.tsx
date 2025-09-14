import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, DollarSign, Calendar, AlertTriangle } from 'lucide-react';
import { Invoice } from '../types/invoice';
import { formatDate } from '../../utils/formatters';
import { formatMoney } from '../../utils/number';

interface InvoiceCardProps {
  invoice: Invoice;
}

export default function InvoiceCard({ invoice }: InvoiceCardProps) {
  const getStatusColor = (status: string) => {
    const colors = {
      DRAFT: 'bg-gray-100 text-gray-800',
      SENT: 'bg-blue-100 text-blue-800',
      PAID: 'bg-green-100 text-green-800',
      OVERDUE: 'bg-red-100 text-red-800',
      CANCELLED: 'bg-gray-100 text-gray-800',
    };
    return colors[status as keyof typeof colors] || colors.DRAFT;
  };

  const getPaymentStatusColor = (status: string) => {
    const colors = {
      PENDING: 'bg-yellow-100 text-yellow-800',
      PARTIAL: 'bg-blue-100 text-blue-800',
      PAID: 'bg-green-100 text-green-800',
      REFUNDED: 'bg-gray-100 text-gray-800',
    };
    return colors[status as keyof typeof colors] || colors.PENDING;
  };

  return (
    <Link
      to={`/invoices/${invoice.id}`}
      className="block bg-white border rounded-lg p-4 hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <FileText className="h-10 w-10 text-blue-600" />
          <div>
            <h3 className="font-medium text-gray-900">
              {invoice.invoice_number}
            </h3>
            <p className="text-sm text-gray-500">{invoice.customer_name}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(invoice.status)}`}>
            {invoice.status}
          </span>
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPaymentStatusColor(invoice.payment_status)}`}>
            {invoice.payment_status}
          </span>
          {invoice.is_overdue && (
            <AlertTriangle className="h-4 w-4 text-red-500" />
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <DollarSign className="h-4 w-4" />
          <span>{formatMoney(invoice?.total_amount, 2, invoice?.currency)}</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Calendar className="h-4 w-4" />
          <span>Due: {formatDate(invoice.due_date)}</span>
        </div>
        <div className="text-sm text-gray-600">
          Issued: {formatDate(invoice.issue_date)}
        </div>
      </div>

      {invoice.items.length > 0 && (
        <div className="text-sm text-gray-500">
          {invoice.items.length} item{invoice.items.length > 1 ? 's' : ''} • {invoice.payment_terms}
        </div>
      )}
    </Link>
  );
}
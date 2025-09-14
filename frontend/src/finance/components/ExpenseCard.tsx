import React from 'react';
import { Receipt, Calendar, CheckCircle, Clock, X, AlertTriangle } from 'lucide-react';
import { Expense } from '../types/expense';
import { useApproveExpense } from '../hooks/useExpenses';
import { formatDate } from '../../utils/formatters';
import { formatMoney } from '../../utils/number';

interface ExpenseCardProps {
  expense: Expense;
}

export default function ExpenseCard({ expense }: ExpenseCardProps) {
  const approveExpense = useApproveExpense();

  const getStatusColor = (status: string) => {
    const colors = {
      DRAFT: 'bg-gray-100 text-gray-800',
      SUBMITTED: 'bg-blue-100 text-blue-800',
      APPROVED: 'bg-green-100 text-green-800',
      REJECTED: 'bg-red-100 text-red-800',
      PAID: 'bg-purple-100 text-purple-800',
    };
    return colors[status as keyof typeof colors] || colors.DRAFT;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'APPROVED':
      case 'PAID':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'SUBMITTED':
        return <Clock className="h-4 w-4 text-blue-500" />;
      case 'REJECTED':
        return <X className="h-4 w-4 text-red-500" />;
      default:
        return <Receipt className="h-4 w-4 text-gray-500" />;
    }
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      FUEL: 'bg-blue-100 text-blue-800',
      MAINTENANCE: 'bg-yellow-100 text-yellow-800',
      SALARIES: 'bg-green-100 text-green-800',
      MARKETING: 'bg-purple-100 text-purple-800',
      OFFICE: 'bg-gray-100 text-gray-800',
      INSURANCE: 'bg-red-100 text-red-800',
      UTILITIES: 'bg-orange-100 text-orange-800',
      TRAVEL: 'bg-indigo-100 text-indigo-800',
      OTHER: 'bg-gray-100 text-gray-800',
    };
    return colors[category as keyof typeof colors] || colors.OTHER;
  };

  const handleApprove = async () => {
    try {
      await approveExpense.mutateAsync({
        id: expense.id,
        data: { status: 'APPROVED', notes: 'Approved for payment' },
      });
    } catch (error) {
      console.error('Failed to approve expense:', error);
    }
  };

  const handleReject = async () => {
    try {
      await approveExpense.mutateAsync({
        id: expense.id,
        data: { status: 'REJECTED', rejected_reason: 'Requires additional documentation' },
      });
    } catch (error) {
      console.error('Failed to reject expense:', error);
    }
  };

  return (
    <div className="bg-white border rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          {getStatusIcon(expense.status)}
          <div>
            <h3 className="font-medium text-gray-900">
              {expense.expense_number}
            </h3>
            <p className="text-sm text-gray-500">{expense.description}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getCategoryColor(expense.category)}`}>
            {expense.category}
          </span>
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(expense.status)}`}>
            {expense.status}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <span className="font-medium">Amount:</span>
          <span>{formatMoney(expense?.amount, 2, expense?.currency)}</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Calendar className="h-4 w-4" />
          <span>{formatDate(expense.expense_date)}</span>
        </div>
        <div className="text-sm text-gray-600">
          <span className="font-medium">Department:</span> {expense.department}
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4 text-sm text-gray-500">
          <span>{expense.cost_center}</span>
          {expense.vendor_name && <span>• {expense.vendor_name}</span>}
          {expense.is_tax_deductible && (
            <span className="inline-flex items-center text-green-600">
              <CheckCircle className="h-3 w-3 mr-1" />
              Tax Deductible
            </span>
          )}
        </div>

        {expense.status === 'SUBMITTED' && (
          <div className="flex items-center gap-2">
            <button
              onClick={handleReject}
              disabled={approveExpense.isPending}
              className="px-3 py-1 text-xs bg-red-100 text-red-800 rounded-full hover:bg-red-200 disabled:opacity-50 transition-colors"
            >
              Reject
            </button>
            <button
              onClick={handleApprove}
              disabled={approveExpense.isPending}
              className="px-3 py-1 text-xs bg-green-100 text-green-800 rounded-full hover:bg-green-200 disabled:opacity-50 transition-colors"
            >
              Approve
            </button>
          </div>
        )}
      </div>

      {expense.receipt_url && (
        <div className="mt-3 pt-3 border-t">
          <a
            href={expense.receipt_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center text-sm text-blue-600 hover:text-blue-700"
          >
            <Receipt className="h-4 w-4 mr-1" />
            View Receipt
          </a>
        </div>
      )}
    </div>
  );
}
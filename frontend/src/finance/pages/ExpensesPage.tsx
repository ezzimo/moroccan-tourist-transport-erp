import React, { useState } from 'react';
import { Plus, Receipt, DollarSign, CheckCircle, Clock } from 'lucide-react';
import { useExpenses } from '../hooks/useExpenses';
import { ExpenseFilters } from '../types/expense';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';
import ExpenseCard from '../components/ExpenseCard';
import CreateExpenseModal from '../components/CreateExpenseModal';

export default function ExpensesPage() {
  const [filters, setFilters] = useState<ExpenseFilters>({ page: 1, size: 20 });
  const [showCreateModal, setShowCreateModal] = useState(false);

  const { data: expensesData, isLoading } = useExpenses(filters);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const expenses = expensesData?.items || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Expenses</h1>
          <p className="text-gray-600">Track and manage business expenses</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
        >
          <Plus className="h-5 w-5 mr-2" />
          Add Expense
        </button>
      </div>

      {/* Statistics */}
      {expensesData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center">
              <Receipt className="h-8 w-8 text-orange-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Total Expenses</p>
                <p className="text-2xl font-bold text-gray-900">{expensesData.total}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Approved</p>
                <p className="text-2xl font-bold text-gray-900">
                  {expenses.filter(e => e.status === 'APPROVED').length}
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
                  {expenses.filter(e => e.status === 'SUBMITTED').length}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center">
              <DollarSign className="h-8 w-8 text-blue-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Total Amount</p>
                <p className="text-2xl font-bold text-gray-900">
                  {expenses.reduce((sum, e) => sum + e.amount, 0).toLocaleString()} MAD
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Expense List */}
      {expenses.length === 0 ? (
        <EmptyState
          icon={Receipt}
          title="No expenses found"
          description="Start tracking business expenses"
          action={{
            label: 'Add Expense',
            onClick: () => setShowCreateModal(true),
          }}
        />
      ) : (
        <div className="bg-white rounded-lg border">
          <div className="grid gap-4 p-4">
            {expenses.map((expense) => (
              <ExpenseCard key={expense.id} expense={expense} />
            ))}
          </div>
        </div>
      )}

      {/* Create Expense Modal */}
      <CreateExpenseModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
      />
    </div>
  );
}
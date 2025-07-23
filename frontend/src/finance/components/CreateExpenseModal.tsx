import React, { useState } from 'react';
import { X, Upload } from 'lucide-react';
import { useCreateExpense } from '../hooks/useExpenses';
import { CreateExpenseData } from '../types/expense';

interface CreateExpenseModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CreateExpenseModal({ isOpen, onClose }: CreateExpenseModalProps) {
  const createExpense = useCreateExpense();
  const [formData, setFormData] = useState<CreateExpenseData>({
    category: 'OTHER',
    cost_center: 'OPERATIONS',
    department: '',
    amount: 0,
    currency: 'MAD',
    description: '',
    expense_date: new Date().toISOString().split('T')[0],
    is_tax_deductible: true,
  });
  const [receiptFile, setReceiptFile] = useState<File | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const submitData = { ...formData };
      if (receiptFile) {
        submitData.receipt_file = receiptFile;
      }
      
      await createExpense.mutateAsync(submitData);
      onClose();
      setFormData({
        category: 'OTHER',
        cost_center: 'OPERATIONS',
        department: '',
        amount: 0,
        currency: 'MAD',
        description: '',
        expense_date: new Date().toISOString().split('T')[0],
        is_tax_deductible: true,
      });
      setReceiptFile(null);
    } catch (error) {
      console.error('Failed to create expense:', error);
    }
  };

  const categories = [
    { value: 'FUEL', label: 'Fuel' },
    { value: 'MAINTENANCE', label: 'Maintenance' },
    { value: 'SALARIES', label: 'Salaries' },
    { value: 'MARKETING', label: 'Marketing' },
    { value: 'OFFICE', label: 'Office Supplies' },
    { value: 'INSURANCE', label: 'Insurance' },
    { value: 'UTILITIES', label: 'Utilities' },
    { value: 'TRAVEL', label: 'Travel' },
    { value: 'OTHER', label: 'Other' },
  ];

  const costCenters = [
    { value: 'OPERATIONS', label: 'Operations' },
    { value: 'SALES', label: 'Sales' },
    { value: 'MARKETING', label: 'Marketing' },
    { value: 'ADMINISTRATION', label: 'Administration' },
    { value: 'HR', label: 'Human Resources' },
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">Add Expense</h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Category *
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value as any }))}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              >
                {categories.map((category) => (
                  <option key={category.value} value={category.value}>
                    {category.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Cost Center *
              </label>
              <select
                value={formData.cost_center}
                onChange={(e) => setFormData(prev => ({ ...prev, cost_center: e.target.value as any }))}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              >
                {costCenters.map((center) => (
                  <option key={center.value} value={center.value}>
                    {center.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Department *
            </label>
            <input
              type="text"
              value={formData.department}
              onChange={(e) => setFormData(prev => ({ ...prev, department: e.target.value }))}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              placeholder="Fleet Management"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Amount *
              </label>
              <input
                type="number"
                value={formData.amount}
                onChange={(e) => setFormData(prev => ({ ...prev, amount: parseFloat(e.target.value) || 0 }))}
                required
                min="0"
                step="0.01"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Currency
              </label>
              <select
                value={formData.currency}
                onChange={(e) => setFormData(prev => ({ ...prev, currency: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              >
                <option value="MAD">MAD</option>
                <option value="EUR">EUR</option>
                <option value="USD">USD</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description *
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              required
              rows={3}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              placeholder="Describe the expense..."
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Vendor Name
              </label>
              <input
                type="text"
                value={formData.vendor_name || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, vendor_name: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                placeholder="Vendor or supplier name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Expense Date *
              </label>
              <input
                type="date"
                value={formData.expense_date}
                onChange={(e) => setFormData(prev => ({ ...prev, expense_date: e.target.value }))}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tax Amount
            </label>
            <input
              type="number"
              value={formData.tax_amount || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, tax_amount: parseFloat(e.target.value) || undefined }))}
              min="0"
              step="0.01"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              placeholder="VAT or tax amount"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Receipt
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={(e) => setReceiptFile(e.target.files?.[0] || null)}
                className="hidden"
                id="receipt-upload"
              />
              <label
                htmlFor="receipt-upload"
                className="cursor-pointer flex flex-col items-center"
              >
                <Upload className="h-8 w-8 text-gray-400 mb-2" />
                <span className="text-sm text-gray-600">
                  {receiptFile ? receiptFile.name : 'Click to upload receipt'}
                </span>
                <span className="text-xs text-gray-500 mt-1">
                  PDF, JPG, PNG up to 10MB
                </span>
              </label>
            </div>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="tax-deductible"
              checked={formData.is_tax_deductible}
              onChange={(e) => setFormData(prev => ({ ...prev, is_tax_deductible: e.target.checked }))}
              className="rounded border-gray-300 text-orange-600 focus:ring-orange-500"
            />
            <label htmlFor="tax-deductible" className="ml-2 text-sm text-gray-700">
              Tax deductible expense
            </label>
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
              disabled={createExpense.isPending}
              className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {createExpense.isPending ? 'Creating...' : 'Create Expense'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
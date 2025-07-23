export interface Expense {
  id: string;
  expense_number: string;
  category: 'FUEL' | 'MAINTENANCE' | 'SALARIES' | 'MARKETING' | 'OFFICE' | 'INSURANCE' | 'UTILITIES' | 'TRAVEL' | 'OTHER';
  cost_center: 'OPERATIONS' | 'SALES' | 'MARKETING' | 'ADMINISTRATION' | 'HR';
  department: string;
  amount: number;
  currency: string;
  description: string;
  vendor_name?: string;
  expense_date: string;
  due_date?: string;
  status: 'DRAFT' | 'SUBMITTED' | 'APPROVED' | 'REJECTED' | 'PAID';
  tax_amount?: number;
  is_tax_deductible: boolean;
  receipt_url?: string;
  submitted_by?: string;
  approved_by?: string;
  approved_at?: string;
  rejected_reason?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateExpenseData {
  category: 'FUEL' | 'MAINTENANCE' | 'SALARIES' | 'MARKETING' | 'OFFICE' | 'INSURANCE' | 'UTILITIES' | 'TRAVEL' | 'OTHER';
  cost_center: 'OPERATIONS' | 'SALES' | 'MARKETING' | 'ADMINISTRATION' | 'HR';
  department: string;
  amount: number;
  currency: string;
  description: string;
  vendor_name?: string;
  expense_date: string;
  due_date?: string;
  tax_amount?: number;
  is_tax_deductible?: boolean;
  receipt_file?: File;
}

export interface ExpenseFilters {
  page?: number;
  size?: number;
  category?: string;
  cost_center?: string;
  department?: string;
  status?: string;
  expense_date_from?: string;
  expense_date_to?: string;
}

export interface ApproveExpenseData {
  status: 'APPROVED' | 'REJECTED';
  notes?: string;
  rejected_reason?: string;
}
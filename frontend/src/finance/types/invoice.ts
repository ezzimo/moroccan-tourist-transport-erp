export interface Invoice {
  id: string;
  invoice_number: string;
  booking_id?: string;
  customer_id: string;
  customer_name: string;
  customer_email: string;
  customer_address?: string;
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  total_amount: number;
  currency: string;
  status: 'DRAFT' | 'SENT' | 'PAID' | 'OVERDUE' | 'CANCELLED';
  payment_status: 'PENDING' | 'PARTIAL' | 'PAID' | 'REFUNDED';
  issue_date: string;
  due_date: string;
  payment_terms: string;
  items: InvoiceItem[];
  notes?: string;
  created_at: string;
  updated_at: string;
  is_overdue: boolean;
  days_overdue?: number;
}

export interface InvoiceItem {
  id?: string;
  description: string;
  quantity: number;
  unit_price: number;
  total_amount: number;
  tax_rate: number;
}

export interface CreateInvoiceData {
  customer_id: string;
  customer_name: string;
  customer_email: string;
  customer_address?: string;
  currency: string;
  tax_rate?: number;
  payment_terms?: string;
  items: Omit<InvoiceItem, 'id' | 'total_amount'>[];
  discount_amount?: number;
  notes?: string;
}

export interface GenerateInvoiceData {
  booking_id: string;
  due_date: string;
  payment_terms?: string;
  notes?: string;
  send_immediately?: boolean;
}

export interface InvoiceFilters {
  page?: number;
  size?: number;
  query?: string;
  customer_id?: string;
  status?: string;
  payment_status?: string;
  currency?: string;
  issue_date_from?: string;
  issue_date_to?: string;
  is_overdue?: boolean;
}

export interface InvoicesResponse {
  items: Invoice[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
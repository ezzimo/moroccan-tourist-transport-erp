export interface Payment {
  id: string;
  invoice_id: string;
  customer_id: string;
  amount: number;
  currency: string;
  payment_method: 'CASH' | 'CREDIT_CARD' | 'BANK_TRANSFER' | 'CHECK' | 'MOBILE_PAYMENT' | 'CRYPTOCURRENCY';
  payment_date: string;
  reference_number?: string;
  transaction_id?: string;
  status: 'PENDING' | 'CONFIRMED' | 'FAILED' | 'CANCELLED';
  is_reconciled: boolean;
  processing_fee?: number;
  description?: string;
  created_at: string;
  updated_at: string;
  confirmed_at?: string;
  reconciled_at?: string;
}

export interface CreatePaymentData {
  invoice_id: string;
  amount: number;
  currency: string;
  payment_method: 'CASH' | 'CREDIT_CARD' | 'BANK_TRANSFER' | 'CHECK' | 'MOBILE_PAYMENT' | 'CRYPTOCURRENCY';
  payment_date: string;
  reference_number?: string;
  transaction_id?: string;
  description?: string;
}

export interface PaymentFilters {
  page?: number;
  size?: number;
  invoice_id?: string;
  payment_method?: string;
  status?: string;
  payment_date_from?: string;
  payment_date_to?: string;
}

export interface ReconcilePaymentsData {
  payment_ids: string[];
  reconciled_by: string;
  notes?: string;
  bank_statement_reference?: string;
}
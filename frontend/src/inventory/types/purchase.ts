export interface PurchaseOrder {
  id: string;
  po_number: string;
  supplier_id: string;
  supplier_name?: string;
  status: 'DRAFT' | 'PENDING' | 'APPROVED' | 'SENT' | 'RECEIVED' | 'CANCELLED';
  subtotal: number;
  total_amount: number;
  order_date: string;
  required_date?: string;
  delivery_address?: string;
  notes?: string;
  items: PurchaseOrderItem[];
  created_at: string;
  approved_by?: string;
  approved_at?: string;
}

export interface PurchaseOrderItem {
  item_id: string;
  item_name?: string;
  item_sku?: string;
  quantity: number;
  unit_cost: number;
  total_cost: number;
}

export interface PurchaseOrdersResponse {
  items: PurchaseOrder[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface CreatePurchaseOrderData {
  supplier_id: string;
  items: {
    item_id: string;
    quantity: number;
    unit_cost: number;
  }[];
  required_date?: string;
  delivery_address?: string;
  notes?: string;
}

export interface ReceiveItemsData {
  items: {
    item_id: string;
    received_quantity: number;
    notes?: string;
  }[];
  received_date: string;
  notes?: string;
}
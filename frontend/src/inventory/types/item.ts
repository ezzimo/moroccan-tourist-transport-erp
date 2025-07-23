export interface InventoryItem {
  id: string;
  name: string;
  description?: string;
  sku: string;
  barcode?: string;
  category: 'ENGINE_PARTS' | 'TIRES' | 'FLUIDS' | 'BRAKE_PARTS' | 'ELECTRICAL' | 'BODY_PARTS' | 'TOOLS' | 'CONSUMABLES' | 'OTHER';
  unit: 'PIECE' | 'LITER' | 'KILOGRAM' | 'METER' | 'SET' | 'GALLON' | 'BOX' | 'ROLL';
  unit_cost: number;
  current_quantity: number;
  reorder_level: number;
  warehouse_location?: string;
  primary_supplier_id?: string;
  status: 'ACTIVE' | 'INACTIVE' | 'DISCONTINUED';
  is_critical: boolean;
  is_low_stock: boolean;
  created_at: string;
  updated_at?: string;
}

export interface ItemsResponse {
  items: InventoryItem[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ItemFilters {
  page?: number;
  size?: number;
  query?: string;
  category?: string;
  status?: string;
  warehouse_location?: string;
  supplier_id?: string;
  is_low_stock?: boolean;
  is_critical?: boolean;
}

export interface CreateItemData {
  name: string;
  description?: string;
  sku: string;
  barcode?: string;
  category: 'ENGINE_PARTS' | 'TIRES' | 'FLUIDS' | 'BRAKE_PARTS' | 'ELECTRICAL' | 'BODY_PARTS' | 'TOOLS' | 'CONSUMABLES' | 'OTHER';
  unit: 'PIECE' | 'LITER' | 'KILOGRAM' | 'METER' | 'SET' | 'GALLON' | 'BOX' | 'ROLL';
  unit_cost: number;
  current_quantity: number;
  reorder_level: number;
  warehouse_location?: string;
  primary_supplier_id?: string;
  is_critical?: boolean;
}

export interface StockAdjustmentData {
  quantity: number;
  reason: string;
  reference_number?: string;
}
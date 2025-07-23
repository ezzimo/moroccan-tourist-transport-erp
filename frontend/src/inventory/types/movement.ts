export interface StockMovement {
  id: string;
  item_id: string;
  movement_type: 'IN' | 'OUT' | 'ADJUST' | 'TRANSFER';
  reason: 'PURCHASE' | 'MAINTENANCE' | 'ADJUSTMENT' | 'SALE' | 'DAMAGE' | 'THEFT' | 'RETURN' | 'TRANSFER' | 'OTHER';
  quantity: number;
  reference_type?: string;
  reference_id?: string;
  performed_by: string;
  movement_date: string;
  notes?: string;
  item_name?: string;
  item_sku?: string;
}

export interface MovementsResponse {
  items: StockMovement[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface MovementFilters {
  page?: number;
  size?: number;
  item_id?: string;
  movement_type?: string;
  date_from?: string;
  date_to?: string;
}

export interface CreateMovementData {
  item_id: string;
  movement_type: 'IN' | 'OUT' | 'ADJUST' | 'TRANSFER';
  reason: 'PURCHASE' | 'MAINTENANCE' | 'ADJUSTMENT' | 'SALE' | 'DAMAGE' | 'THEFT' | 'RETURN' | 'TRANSFER' | 'OTHER';
  quantity: number;
  reference_type?: string;
  reference_id?: string;
  notes?: string;
}
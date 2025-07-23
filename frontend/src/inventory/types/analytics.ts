export interface InventoryDashboard {
  total_items: number;
  low_stock_items: number;
  critical_items: number;
  total_stock_value: number;
  by_category: Record<string, number>;
  recent_movements: StockMovement[];
  top_suppliers: {
    supplier_name: string;
    total_orders: number;
    total_value: number;
  }[];
  pending_orders: number;
}

export interface InventoryAnalytics {
  stock_value_trend: {
    month: string;
    value: number;
  }[];
  category_distribution: {
    category: string;
    count: number;
    value: number;
    percentage: number;
  }[];
  movement_trends: {
    date: string;
    in: number;
    out: number;
  }[];
  supplier_performance: {
    supplier_name: string;
    on_time_delivery: number;
    quality_rating: number;
    total_orders: number;
  }[];
}
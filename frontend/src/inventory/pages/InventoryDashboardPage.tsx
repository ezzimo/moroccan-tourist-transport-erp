import React from 'react';
import { Package, TrendingDown, AlertTriangle, DollarSign, Truck, ShoppingCart } from 'lucide-react';
import { useInventoryDashboard } from '../hooks/useAnalytics';
import { useLowStockItems } from '../hooks/useItems';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function InventoryDashboardPage() {
  const { data: dashboard, isLoading } = useInventoryDashboard();
  const { data: lowStockItems } = useLowStockItems();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Failed to load inventory dashboard</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Inventory Dashboard</h1>
        <p className="text-gray-600">Overview of your inventory management</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg border">
          <div className="flex items-center">
            <Package className="h-8 w-8 text-orange-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Total Items</p>
              <p className="text-2xl font-bold text-gray-900">{dashboard.total_items}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg border">
          <div className="flex items-center">
            <TrendingDown className="h-8 w-8 text-red-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Low Stock Items</p>
              <p className="text-2xl font-bold text-gray-900">{dashboard.low_stock_items}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg border">
          <div className="flex items-center">
            <AlertTriangle className="h-8 w-8 text-yellow-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Critical Items</p>
              <p className="text-2xl font-bold text-gray-900">{dashboard.critical_items}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg border">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Stock Value</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboard.total_stock_value.toLocaleString()} MAD
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Category Distribution */}
      <div className="bg-white rounded-lg border p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Items by Category</h3>
        <div className="space-y-4">
          {Object.entries(dashboard.by_category).map(([category, count]) => {
            const percentage = (count / dashboard.total_items) * 100;
            return (
              <div key={category} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="font-medium text-gray-900">{category.replace('_', ' ')}</span>
                  <span className="text-sm text-gray-500">({count} items)</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-orange-600 h-2 rounded-full"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900 w-12">
                    {percentage.toFixed(1)}%
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recent Activity and Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Movements */}
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Stock Movements</h3>
          {dashboard.recent_movements.length === 0 ? (
            <p className="text-gray-500 text-center py-4">No recent movements</p>
          ) : (
            <div className="space-y-3">
              {dashboard.recent_movements.slice(0, 5).map((movement) => (
                <div key={movement.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{movement.item_name || 'Unknown Item'}</p>
                    <p className="text-sm text-gray-500">
                      {movement.movement_type} • {movement.reason}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className={`font-medium ${
                      movement.movement_type === 'IN' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {movement.movement_type === 'IN' ? '+' : '-'}{movement.quantity}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(movement.movement_date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Alerts */}
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Alerts & Notifications</h3>
          <div className="space-y-3">
            {dashboard.low_stock_items > 0 && (
              <div className="flex items-center gap-3 p-3 bg-red-50 rounded-lg">
                <TrendingDown className="h-5 w-5 text-red-600" />
                <span className="text-sm text-red-800">
                  {dashboard.low_stock_items} items are running low on stock
                </span>
              </div>
            )}
            {dashboard.critical_items > 0 && (
              <div className="flex items-center gap-3 p-3 bg-yellow-50 rounded-lg">
                <AlertTriangle className="h-5 w-5 text-yellow-600" />
                <span className="text-sm text-yellow-800">
                  {dashboard.critical_items} critical items need attention
                </span>
              </div>
            )}
            {dashboard.pending_orders > 0 && (
              <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
                <ShoppingCart className="h-5 w-5 text-blue-600" />
                <span className="text-sm text-blue-800">
                  {dashboard.pending_orders} purchase orders pending approval
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Top Suppliers */}
      {dashboard.top_suppliers.length > 0 && (
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Top Suppliers</h3>
          <div className="space-y-3">
            {dashboard.top_suppliers.map((supplier, index) => (
              <div key={supplier.supplier_name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <span className="w-6 h-6 bg-orange-600 text-white text-xs rounded-full flex items-center justify-center">
                    {index + 1}
                  </span>
                  <span className="font-medium text-gray-900">{supplier.supplier_name}</span>
                </div>
                <div className="text-right">
                  <p className="font-medium text-gray-900">{supplier.total_value.toLocaleString()} MAD</p>
                  <p className="text-sm text-gray-500">{supplier.total_orders} orders</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
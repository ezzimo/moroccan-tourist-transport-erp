import React from 'react';
import { Link } from 'react-router-dom';
import { Package, AlertTriangle, TrendingDown, MapPin, Tag } from 'lucide-react';
import { InventoryItem } from '../types/item';

interface ItemCardProps {
  item: InventoryItem;
}

export default function ItemCard({ item }: ItemCardProps) {
  const getStatusColor = (status: string) => {
    const colors = {
      ACTIVE: 'bg-green-100 text-green-800',
      INACTIVE: 'bg-gray-100 text-gray-800',
      DISCONTINUED: 'bg-red-100 text-red-800',
    };
    return colors[status as keyof typeof colors] || colors.ACTIVE;
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      ENGINE_PARTS: 'bg-blue-100 text-blue-800',
      TIRES: 'bg-purple-100 text-purple-800',
      FLUIDS: 'bg-cyan-100 text-cyan-800',
      BRAKE_PARTS: 'bg-red-100 text-red-800',
      ELECTRICAL: 'bg-yellow-100 text-yellow-800',
      BODY_PARTS: 'bg-green-100 text-green-800',
      TOOLS: 'bg-orange-100 text-orange-800',
      CONSUMABLES: 'bg-pink-100 text-pink-800',
      OTHER: 'bg-gray-100 text-gray-800',
    };
    return colors[category as keyof typeof colors] || colors.OTHER;
  };

  return (
    <Link
      to={`/inventory/items/${item.id}`}
      className="block bg-white border rounded-lg p-4 hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <Package className="h-10 w-10 text-blue-600" />
          <div>
            <h3 className="font-medium text-gray-900">{item.name}</h3>
            <p className="text-sm text-gray-500">SKU: {item.sku}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getCategoryColor(item.category)}`}>
            {item.category.replace('_', ' ')}
          </span>
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(item.status)}`}>
            {item.status}
          </span>
          {item.is_critical && (
            <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded-full">
              Critical
            </span>
          )}
        </div>
      </div>

      {item.description && (
        <p className="text-sm text-gray-600 mb-3">{item.description}</p>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
        <div>
          <p className="text-xs text-gray-500">Current Stock</p>
          <p className={`font-medium ${item.is_low_stock ? 'text-red-600' : 'text-gray-900'}`}>
            {item.current_quantity} {item.unit.toLowerCase()}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Reorder Level</p>
          <p className="font-medium text-gray-900">{item.reorder_level} {item.unit.toLowerCase()}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Unit Cost</p>
          <p className="font-medium text-gray-900">{item.unit_cost.toFixed(2)} MAD</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Total Value</p>
          <p className="font-medium text-gray-900">
            {(item.current_quantity * item.unit_cost).toFixed(2)} MAD
          </p>
        </div>
      </div>

      <div className="flex items-center justify-between text-sm text-gray-500">
        <div className="flex items-center gap-4">
          {item.warehouse_location && (
            <div className="flex items-center gap-1">
              <MapPin className="h-4 w-4" />
              <span>{item.warehouse_location}</span>
            </div>
          )}
          {item.barcode && (
            <div className="flex items-center gap-1">
              <Tag className="h-4 w-4" />
              <span>{item.barcode}</span>
            </div>
          )}
        </div>
        <div className="flex items-center gap-2">
          {item.is_low_stock && (
            <div className="flex items-center gap-1 text-red-600">
              <TrendingDown className="h-4 w-4" />
              <span className="text-xs">Low Stock</span>
            </div>
          )}
          {item.is_critical && (
            <div className="flex items-center gap-1 text-yellow-600">
              <AlertTriangle className="h-4 w-4" />
              <span className="text-xs">Critical</span>
            </div>
          )}
        </div>
      </div>
    </Link>
  );
}
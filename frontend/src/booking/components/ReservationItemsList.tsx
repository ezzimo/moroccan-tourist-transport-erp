import React, { useState } from 'react';
import { Plus, Edit, Trash2 } from 'lucide-react';
import { ReservationItem } from '../types/reservation';
import { useCreateReservationItem, useDeleteReservationItem } from '../hooks/useReservations';
import { formatCurrency } from '../../utils/formatters';

interface ReservationItemsListProps {
  bookingId: string;
  items: ReservationItem[];
}

export default function ReservationItemsList({ bookingId, items }: ReservationItemsListProps) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [newItem, setNewItem] = useState({
    type: 'Transport' as const,
    name: '',
    description: '',
    quantity: 1,
    unit_price: 0,
  });

  const createItem = useCreateReservationItem();
  const deleteItem = useDeleteReservationItem();

  const handleAddItem = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createItem.mutateAsync({
        booking_id: bookingId,
        ...newItem,
      });
      setNewItem({
        type: 'Transport',
        name: '',
        description: '',
        quantity: 1,
        unit_price: 0,
      });
      setShowAddForm(false);
    } catch (error) {
      console.error('Failed to add reservation item:', error);
    }
  };

  const handleDeleteItem = async (itemId: string) => {
    if (confirm('Are you sure you want to delete this item?')) {
      try {
        await deleteItem.mutateAsync(itemId);
      } catch (error) {
        console.error('Failed to delete reservation item:', error);
      }
    }
  };

  const getTypeColor = (type: string) => {
    const colors = {
      Accommodation: 'bg-blue-100 text-blue-800',
      Transport: 'bg-green-100 text-green-800',
      Activity: 'bg-purple-100 text-purple-800',
      Guide: 'bg-orange-100 text-orange-800',
      Meal: 'bg-yellow-100 text-yellow-800',
      Insurance: 'bg-red-100 text-red-800',
    };
    return colors[type as keyof typeof colors] || colors.Transport;
  };

  const itemTypes = [
    { value: 'Accommodation', label: 'Accommodation' },
    { value: 'Transport', label: 'Transport' },
    { value: 'Activity', label: 'Activity' },
    { value: 'Guide', label: 'Guide' },
    { value: 'Meal', label: 'Meal' },
    { value: 'Insurance', label: 'Insurance' },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="font-medium text-gray-900">Items ({items.length})</h4>
        <button
          onClick={() => setShowAddForm(true)}
          className="inline-flex items-center px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="h-4 w-4 mr-1" />
          Add Item
        </button>
      </div>

      {showAddForm && (
        <form onSubmit={handleAddItem} className="p-4 bg-gray-50 rounded-lg space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Type *
              </label>
              <select
                value={newItem.type}
                onChange={(e) => setNewItem(prev => ({ ...prev, type: e.target.value as any }))}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              >
                {itemTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Name *
              </label>
              <input
                type="text"
                value={newItem.name}
                onChange={(e) => setNewItem(prev => ({ ...prev, name: e.target.value }))}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                placeholder="Item name"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <input
              type="text"
              value={newItem.description}
              onChange={(e) => setNewItem(prev => ({ ...prev, description: e.target.value }))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              placeholder="Item description"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Quantity *
              </label>
              <input
                type="number"
                value={newItem.quantity}
                onChange={(e) => setNewItem(prev => ({ ...prev, quantity: parseInt(e.target.value) || 1 }))}
                required
                min="1"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Unit Price *
              </label>
              <input
                type="number"
                value={newItem.unit_price}
                onChange={(e) => setNewItem(prev => ({ ...prev, unit_price: parseFloat(e.target.value) || 0 }))}
                required
                min="0"
                step="0.01"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              />
            </div>
          </div>

          <div className="flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={() => setShowAddForm(false)}
              className="px-3 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createItem.isPending}
              className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {createItem.isPending ? 'Adding...' : 'Add Item'}
            </button>
          </div>
        </form>
      )}

      {items.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No reservation items added yet
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <div key={item.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTypeColor(item.type)}`}>
                    {item.type}
                  </span>
                  <h5 className="font-medium text-gray-900">{item.name}</h5>
                </div>
                {item.description && (
                  <p className="text-sm text-gray-600 mb-1">{item.description}</p>
                )}
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span>Qty: {item.quantity}</span>
                  <span>Unit: {formatCurrency(item.unit_price)}</span>
                  <span className="font-medium">Total: {formatCurrency(item.total_price)}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleDeleteItem(item.id)}
                  disabled={deleteItem.isPending}
                  className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {items.length > 0 && (
        <div className="pt-4 border-t">
          <div className="flex justify-between items-center">
            <span className="font-medium text-gray-900">Total Items Value:</span>
            <span className="text-lg font-bold text-gray-900">
              {formatCurrency(items.reduce((sum, item) => sum + item.total_price, 0))}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
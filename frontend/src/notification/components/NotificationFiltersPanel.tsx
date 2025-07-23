import React from 'react';
import { X } from 'lucide-react';
import { NotificationFilters, NotificationType, NotificationChannel, NotificationStatus } from '../types/notification';

interface NotificationFiltersPanelProps {
  filters: NotificationFilters;
  onFiltersChange: (filters: Partial<NotificationFilters>) => void;
  onClose: () => void;
}

export default function NotificationFiltersPanel({
  filters,
  onFiltersChange,
  onClose,
}: NotificationFiltersPanelProps) {
  const notificationTypes: { value: NotificationType; label: string }[] = [
    { value: 'BOOKING_CONFIRMED', label: 'Booking Confirmed' },
    { value: 'BOOKING_CANCELLED', label: 'Booking Cancelled' },
    { value: 'TOUR_REMINDER', label: 'Tour Reminder' },
    { value: 'PAYMENT_RECEIVED', label: 'Payment Received' },
    { value: 'PAYMENT_FAILED', label: 'Payment Failed' },
    { value: 'INVOICE_GENERATED', label: 'Invoice Generated' },
    { value: 'MAINTENANCE_DUE', label: 'Maintenance Due' },
    { value: 'DOCUMENT_EXPIRING', label: 'Document Expiring' },
    { value: 'TRAINING_REMINDER', label: 'Training Reminder' },
    { value: 'SYSTEM_ALERT', label: 'System Alert' },
    { value: 'WELCOME', label: 'Welcome' },
    { value: 'PASSWORD_RESET', label: 'Password Reset' },
  ];

  const channels: { value: NotificationChannel; label: string }[] = [
    { value: 'EMAIL', label: 'Email' },
    { value: 'SMS', label: 'SMS' },
    { value: 'PUSH', label: 'Push Notification' },
    { value: 'WHATSAPP', label: 'WhatsApp' },
  ];

  const statuses: { value: NotificationStatus; label: string }[] = [
    { value: 'PENDING', label: 'Pending' },
    { value: 'SENT', label: 'Sent' },
    { value: 'DELIVERED', label: 'Delivered' },
    { value: 'FAILED', label: 'Failed' },
  ];

  return (
    <div className="bg-gray-50 border rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900">Filters</h3>
        <button
          onClick={onClose}
          className="p-1 text-gray-400 hover:text-gray-600"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Type
          </label>
          <select
            value={filters.type || ''}
            onChange={(e) => onFiltersChange({ type: e.target.value as NotificationType || undefined })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">All Types</option>
            {notificationTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Channel
          </label>
          <select
            value={filters.channel || ''}
            onChange={(e) => onFiltersChange({ channel: e.target.value as NotificationChannel || undefined })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">All Channels</option>
            {channels.map((channel) => (
              <option key={channel.value} value={channel.value}>
                {channel.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Status
          </label>
          <select
            value={filters.status || ''}
            onChange={(e) => onFiltersChange({ status: e.target.value as NotificationStatus || undefined })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">All Statuses</option>
            {statuses.map((status) => (
              <option key={status.value} value={status.value}>
                {status.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Source Service
          </label>
          <input
            type="text"
            value={filters.source_service || ''}
            onChange={(e) => onFiltersChange({ source_service: e.target.value || undefined })}
            placeholder="e.g., booking_service"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          />
        </div>
      </div>

      <div className="flex items-center gap-4 mt-4">
        <button
          onClick={() => onFiltersChange({ 
            type: undefined, 
            channel: undefined, 
            status: undefined, 
            source_service: undefined 
          })}
          className="text-sm text-orange-600 hover:text-orange-700"
        >
          Clear filters
        </button>
      </div>
    </div>
  );
}
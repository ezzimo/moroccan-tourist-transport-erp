import React from 'react';
import { X } from 'lucide-react';
import { TemplateFilters, TemplateType } from '../types/template';
import { NotificationChannel } from '../types/notification';

interface TemplateFiltersPanelProps {
  filters: TemplateFilters;
  onFiltersChange: (filters: Partial<TemplateFilters>) => void;
  onClose: () => void;
}

export default function TemplateFiltersPanel({
  filters,
  onFiltersChange,
  onClose,
}: TemplateFiltersPanelProps) {
  const templateTypes: { value: TemplateType; label: string }[] = [
    { value: 'TRANSACTIONAL', label: 'Transactional' },
    { value: 'MARKETING', label: 'Marketing' },
    { value: 'SYSTEM', label: 'System' },
    { value: 'ALERT', label: 'Alert' },
  ];

  const channels: { value: NotificationChannel; label: string }[] = [
    { value: 'EMAIL', label: 'Email' },
    { value: 'SMS', label: 'SMS' },
    { value: 'PUSH', label: 'Push Notification' },
    { value: 'WHATSAPP', label: 'WhatsApp' },
  ];

  const languages = [
    { value: 'en', label: 'English' },
    { value: 'fr', label: 'French' },
    { value: 'ar', label: 'Arabic' },
    { value: 'es', label: 'Spanish' },
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
            onChange={(e) => onFiltersChange({ type: e.target.value as TemplateType || undefined })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">All Types</option>
            {templateTypes.map((type) => (
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
            Language
          </label>
          <select
            value={filters.language || ''}
            onChange={(e) => onFiltersChange({ language: e.target.value || undefined })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">All Languages</option>
            {languages.map((lang) => (
              <option key={lang.value} value={lang.value}>
                {lang.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Status
          </label>
          <select
            value={filters.is_active !== undefined ? filters.is_active.toString() : ''}
            onChange={(e) => onFiltersChange({ 
              is_active: e.target.value === '' ? undefined : e.target.value === 'true' 
            })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">All</option>
            <option value="true">Active</option>
            <option value="false">Inactive</option>
          </select>
        </div>
      </div>

      <div className="flex items-center gap-4 mt-4">
        <button
          onClick={() => onFiltersChange({ 
            type: undefined, 
            channel: undefined, 
            language: undefined, 
            is_active: undefined 
          })}
          className="text-sm text-orange-600 hover:text-orange-700"
        >
          Clear filters
        </button>
      </div>
    </div>
  );
}
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Send, ArrowLeft, Plus, X } from 'lucide-react';
import { useSendNotification } from '../hooks/useNotifications';
import { useTemplates } from '../hooks/useTemplates';
import { SendNotificationRequest, NotificationRecipient, NotificationType, NotificationChannel } from '../types/notification';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function SendNotificationPage() {
  const navigate = useNavigate();
  const sendNotification = useSendNotification();
  const { data: templatesData } = useTemplates({ is_active: true });

  const [formData, setFormData] = useState<SendNotificationRequest>({
    type: 'BOOKING_CONFIRMED',
    recipients: [{ email: '', name: '' }],
    channels: ['EMAIL'],
    priority: 5,
    template_variables: {},
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await sendNotification.mutateAsync(formData);
      navigate('/notifications');
    } catch (error) {
      console.error('Failed to send notification:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const addRecipient = () => {
    setFormData(prev => ({
      ...prev,
      recipients: [...prev.recipients, { email: '', name: '' }],
    }));
  };

  const removeRecipient = (index: number) => {
    setFormData(prev => ({
      ...prev,
      recipients: prev.recipients.filter((_, i) => i !== index),
    }));
  };

  const updateRecipient = (index: number, field: keyof NotificationRecipient, value: string) => {
    setFormData(prev => ({
      ...prev,
      recipients: prev.recipients.map((recipient, i) =>
        i === index ? { ...recipient, [field]: value } : recipient
      ),
    }));
  };

  const templates = templatesData?.items || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/notifications')}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Send Notification</h1>
          <p className="text-gray-600">Send notifications to recipients</p>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="bg-white rounded-lg border p-6 space-y-6">
        {/* Notification Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Notification Type *
          </label>
          <select
            value={formData.type}
            onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value as NotificationType }))}
            required
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            {notificationTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        {/* Template Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Template (Optional)
          </label>
          <select
            value={formData.template_id || ''}
            onChange={(e) => setFormData(prev => ({ ...prev, template_id: e.target.value || undefined }))}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">Select a template</option>
            {templates.map((template) => (
              <option key={template.id} value={template.id}>
                {template.name} ({template.channel})
              </option>
            ))}
          </select>
        </div>

        {/* Channels */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Channels *
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {channels.map((channel) => (
              <label key={channel.value} className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.channels.includes(channel.value)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setFormData(prev => ({
                        ...prev,
                        channels: [...prev.channels, channel.value],
                      }));
                    } else {
                      setFormData(prev => ({
                        ...prev,
                        channels: prev.channels.filter(c => c !== channel.value),
                      }));
                    }
                  }}
                  className="rounded border-gray-300 text-orange-600 focus:ring-orange-500"
                />
                <span className="ml-2 text-sm text-gray-700">{channel.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Recipients */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="block text-sm font-medium text-gray-700">
              Recipients *
            </label>
            <button
              type="button"
              onClick={addRecipient}
              className="inline-flex items-center px-3 py-1 text-sm bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
            >
              <Plus className="h-4 w-4 mr-1" />
              Add Recipient
            </button>
          </div>
          <div className="space-y-3">
            {formData.recipients.map((recipient, index) => (
              <div key={index} className="flex items-center gap-3 p-3 border rounded-lg">
                <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-3">
                  <input
                    type="text"
                    placeholder="Name"
                    value={recipient.name || ''}
                    onChange={(e) => updateRecipient(index, 'name', e.target.value)}
                    className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  />
                  <input
                    type="email"
                    placeholder="Email"
                    value={recipient.email || ''}
                    onChange={(e) => updateRecipient(index, 'email', e.target.value)}
                    required
                    className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  />
                </div>
                {formData.recipients.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeRecipient(index)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <X className="h-4 w-4" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Priority */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Priority (1-10)
          </label>
          <input
            type="number"
            min="1"
            max="10"
            value={formData.priority}
            onChange={(e) => setFormData(prev => ({ ...prev, priority: parseInt(e.target.value) }))}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          />
        </div>

        {/* Template Variables */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Template Variables (JSON)
          </label>
          <textarea
            rows={4}
            value={JSON.stringify(formData.template_variables, null, 2)}
            onChange={(e) => {
              try {
                const variables = JSON.parse(e.target.value);
                setFormData(prev => ({ ...prev, template_variables: variables }));
              } catch (error) {
                // Invalid JSON, keep the text as is
              }
            }}
            placeholder='{"customer_name": "John Doe", "booking_reference": "BK-001"}'
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          />
        </div>

        {/* Submit Button */}
        <div className="flex items-center justify-end gap-4 pt-4 border-t">
          <button
            type="button"
            onClick={() => navigate('/notifications')}
            className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting || formData.recipients.length === 0 || formData.channels.length === 0}
            className="inline-flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isSubmitting ? (
              <LoadingSpinner size="sm" className="mr-2" />
            ) : (
              <Send className="h-5 w-5 mr-2" />
            )}
            {isSubmitting ? 'Sending...' : 'Send Notification'}
          </button>
        </div>
      </form>
    </div>
  );
}
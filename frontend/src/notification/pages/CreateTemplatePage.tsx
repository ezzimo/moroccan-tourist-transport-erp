import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Save, Eye } from 'lucide-react';
import { useCreateTemplate, usePreviewTemplate } from '../hooks/useTemplates';
import { CreateTemplateRequest, TemplateType, TemplateVariable } from '../types/template';
import { NotificationChannel } from '../types/notification';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function CreateTemplatePage() {
  const navigate = useNavigate();
  const createTemplate = useCreateTemplate();
  const previewTemplate = usePreviewTemplate();

  const [formData, setFormData] = useState<CreateTemplateRequest>({
    name: '',
    description: '',
    type: 'TRANSACTIONAL',
    channel: 'EMAIL',
    subject: '',
    body: '',
    variables: {},
    default_values: {},
    content_type: 'text',
    language: 'en',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [preview, setPreview] = useState<any>(null);
  const [showPreview, setShowPreview] = useState(false);

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await createTemplate.mutateAsync(formData);
      navigate('/templates');
    } catch (error) {
      console.error('Failed to create template:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePreview = async () => {
    if (!formData.name) return;

    try {
      const result = await previewTemplate.mutateAsync({
        template_id: 'preview', // Special ID for preview
        variables: formData.default_values || {},
      });
      setPreview(result);
      setShowPreview(true);
    } catch (error) {
      console.error('Preview failed:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/templates')}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create Template</h1>
          <p className="text-gray-600">Create a new notification template</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form */}
        <div className="lg:col-span-2">
          <form onSubmit={handleSubmit} className="bg-white rounded-lg border p-6 space-y-6">
            {/* Basic Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Template Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  required
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  placeholder="e.g., booking_confirmation_email"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Type *
                </label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value as TemplateType }))}
                  required
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                >
                  {templateTypes.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Channel *
                </label>
                <select
                  value={formData.channel}
                  onChange={(e) => setFormData(prev => ({ ...prev, channel: e.target.value as NotificationChannel }))}
                  required
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                >
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
                  value={formData.language}
                  onChange={(e) => setFormData(prev => ({ ...prev, language: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                >
                  {languages.map((lang) => (
                    <option key={lang.value} value={lang.value}>
                      {lang.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                rows={2}
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                placeholder="Brief description of this template"
              />
            </div>

            {/* Subject (for email) */}
            {formData.channel === 'EMAIL' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Subject *
                </label>
                <input
                  type="text"
                  value={formData.subject}
                  onChange={(e) => setFormData(prev => ({ ...prev, subject: e.target.value }))}
                  required
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  placeholder="e.g., Booking Confirmation - {booking_reference}"
                />
              </div>
            )}

            {/* Body */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Message Body *
              </label>
              <textarea
                rows={8}
                value={formData.body}
                onChange={(e) => setFormData(prev => ({ ...prev, body: e.target.value }))}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                placeholder="Dear {customer_name}, your booking {booking_reference} has been confirmed..."
              />
              <p className="text-xs text-gray-500 mt-1">
                Use {'{variable_name}'} for dynamic content
              </p>
            </div>

            {/* Variables */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Template Variables (JSON)
              </label>
              <textarea
                rows={4}
                value={JSON.stringify(formData.variables, null, 2)}
                onChange={(e) => {
                  try {
                    const variables = JSON.parse(e.target.value);
                    setFormData(prev => ({ ...prev, variables }));
                  } catch (error) {
                    // Invalid JSON, keep the text as is
                  }
                }}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                placeholder='{"customer_name": {"type": "string", "required": true}}'
              />
            </div>

            {/* Default Values */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Default Values (JSON)
              </label>
              <textarea
                rows={3}
                value={JSON.stringify(formData.default_values, null, 2)}
                onChange={(e) => {
                  try {
                    const defaultValues = JSON.parse(e.target.value);
                    setFormData(prev => ({ ...prev, default_values: defaultValues }));
                  } catch (error) {
                    // Invalid JSON, keep the text as is
                  }
                }}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                placeholder='{"company_name": "Atlas Tours Morocco"}'
              />
            </div>

            {/* Submit Buttons */}
            <div className="flex items-center justify-between pt-4 border-t">
              <button
                type="button"
                onClick={handlePreview}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <Eye className="h-5 w-5 mr-2" />
                Preview
              </button>
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => navigate('/templates')}
                  className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="inline-flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isSubmitting ? (
                    <LoadingSpinner size="sm" className="mr-2" />
                  ) : (
                    <Save className="h-5 w-5 mr-2" />
                  )}
                  {isSubmitting ? 'Creating...' : 'Create Template'}
                </button>
              </div>
            </div>
          </form>
        </div>

        {/* Preview Panel */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg border p-6 sticky top-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Preview</h3>
            {preview ? (
              <div className="space-y-4">
                {preview.subject && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-1">Subject:</p>
                    <p className="text-sm text-gray-900 bg-gray-50 p-2 rounded">{preview.subject}</p>
                  </div>
                )}
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-1">Body:</p>
                  <div className="text-sm text-gray-900 bg-gray-50 p-2 rounded whitespace-pre-wrap">
                    {preview.body}
                  </div>
                </div>
                {preview.missing_variables.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-red-700 mb-1">Missing Variables:</p>
                    <ul className="text-sm text-red-600">
                      {preview.missing_variables.map((variable: string) => (
                        <li key={variable}>• {variable}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-gray-500">Click "Preview" to see how your template will look</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
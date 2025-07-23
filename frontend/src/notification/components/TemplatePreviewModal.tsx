import React, { useState } from 'react';
import { X, Eye } from 'lucide-react';
import { useTemplate, usePreviewTemplate } from '../hooks/useTemplates';
import LoadingSpinner from '../../components/LoadingSpinner';

interface TemplatePreviewModalProps {
  templateId: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function TemplatePreviewModal({ templateId, isOpen, onClose }: TemplatePreviewModalProps) {
  const { data: template, isLoading: templateLoading } = useTemplate(templateId);
  const previewTemplate = usePreviewTemplate();
  const [variables, setVariables] = useState<Record<string, any>>({});
  const [preview, setPreview] = useState<any>(null);

  if (!isOpen) return null;

  const handlePreview = async () => {
    if (!template) return;

    try {
      const result = await previewTemplate.mutateAsync({
        template_id: templateId,
        variables: { ...template.default_values, ...variables },
      });
      setPreview(result);
    } catch (error) {
      console.error('Preview failed:', error);
    }
  };

  const updateVariable = (key: string, value: string) => {
    setVariables(prev => ({ ...prev, [key]: value }));
  };

  if (templateLoading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg p-6">
          <LoadingSpinner size="lg" />
        </div>
      </div>
    );
  }

  if (!template) return null;

  const templateVariables = template.variables || {};

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">Template Preview: {template.name}</h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="p-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Variables Input */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Template Variables</h3>
            <div className="space-y-4">
              {Object.entries(templateVariables).map(([key, variable]) => (
                <div key={key}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {key} {variable.required && <span className="text-red-500">*</span>}
                  </label>
                  <input
                    type="text"
                    value={variables[key] || template.default_values?.[key] || ''}
                    onChange={(e) => updateVariable(key, e.target.value)}
                    placeholder={`Enter ${key}`}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  />
                  {variable.description && (
                    <p className="text-xs text-gray-500 mt-1">{variable.description}</p>
                  )}
                </div>
              ))}
              
              <button
                onClick={handlePreview}
                disabled={previewTemplate.isPending}
                className="inline-flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {previewTemplate.isPending ? (
                  <LoadingSpinner size="sm" className="mr-2" />
                ) : (
                  <Eye className="h-5 w-5 mr-2" />
                )}
                {previewTemplate.isPending ? 'Generating...' : 'Generate Preview'}
              </button>
            </div>
          </div>

          {/* Preview Output */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Preview Output</h3>
            {preview ? (
              <div className="space-y-4">
                {preview.subject && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">Subject:</p>
                    <div className="p-3 bg-gray-50 border rounded-lg">
                      <p className="text-sm text-gray-900">{preview.subject}</p>
                    </div>
                  </div>
                )}
                
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Message Body:</p>
                  <div className="p-3 bg-gray-50 border rounded-lg">
                    <div className="text-sm text-gray-900 whitespace-pre-wrap">
                      {preview.body}
                    </div>
                  </div>
                </div>

                {preview.missing_variables && preview.missing_variables.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-red-700 mb-2">Missing Variables:</p>
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                      <ul className="text-sm text-red-600">
                        {preview.missing_variables.map((variable: string) => (
                          <li key={variable}>• {variable}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {preview.validation_errors && preview.validation_errors.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-red-700 mb-2">Validation Errors:</p>
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                      <ul className="text-sm text-red-600">
                        {preview.validation_errors.map((error: string, index: number) => (
                          <li key={index}>• {error}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-8 text-center text-gray-500 border-2 border-dashed border-gray-300 rounded-lg">
                <Eye className="h-12 w-12 mx-auto mb-3 text-gray-400" />
                <p>Fill in the variables and click "Generate Preview" to see how your template will look</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
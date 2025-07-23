import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Filter, FileText, Eye } from 'lucide-react';
import { useTemplates } from '../hooks/useTemplates';
import { TemplateFilters } from '../types/template';
import LoadingSpinner from '../../components/LoadingSpinner';
import TemplateCard from '../components/TemplateCard';
import TemplateFiltersPanel from '../components/TemplateFiltersPanel';
import TemplatePreviewModal from '../components/TemplatePreviewModal';

export default function TemplatesPage() {
  const [filters, setFilters] = useState<TemplateFilters>({ page: 1, size: 20 });
  const [showFilters, setShowFilters] = useState(false);
  const [previewTemplateId, setPreviewTemplateId] = useState<string | null>(null);

  const { data: templatesData, isLoading } = useTemplates(filters);

  const handleFilterChange = (newFilters: Partial<TemplateFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters, page: 1 }));
  };

  const handlePageChange = (page: number) => {
    setFilters(prev => ({ ...prev, page }));
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const templates = templatesData?.items || [];
  const totalPages = templatesData?.pages || 1;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Notification Templates</h1>
          <p className="text-gray-600">Manage reusable notification templates</p>
        </div>
        <Link
          to="/templates/create"
          className="inline-flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
        >
          <Plus className="h-5 w-5 mr-2" />
          Create Template
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg border p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Filters</h3>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="inline-flex items-center px-3 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Filter className="h-4 w-4 mr-2" />
            {showFilters ? 'Hide' : 'Show'} Filters
          </button>
        </div>

        {showFilters && (
          <TemplateFiltersPanel
            filters={filters}
            onFiltersChange={handleFilterChange}
            onClose={() => setShowFilters(false)}
          />
        )}
      </div>

      {/* Templates Grid */}
      {templates.length === 0 ? (
        <div className="bg-white rounded-lg border p-12 text-center">
          <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-medium text-gray-900 mb-2">No templates found</h3>
          <p className="text-gray-600 mb-6">Create your first notification template to get started</p>
          <Link
            to="/templates/create"
            className="inline-flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
          >
            <Plus className="h-5 w-5 mr-2" />
            Create Template
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {templates.map((template) => (
            <TemplateCard
              key={template.id}
              template={template}
              onPreview={() => setPreviewTemplateId(template.id)}
            />
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between bg-white border rounded-lg px-4 py-3">
          <div className="flex items-center text-sm text-gray-500">
            Showing {((filters.page || 1) - 1) * (filters.size || 20) + 1} to{' '}
            {Math.min((filters.page || 1) * (filters.size || 20), templatesData?.total || 0)} of{' '}
            {templatesData?.total || 0} results
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => handlePageChange((filters.page || 1) - 1)}
              disabled={(filters.page || 1) <= 1}
              className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <span className="px-3 py-1">
              Page {filters.page || 1} of {totalPages}
            </span>
            <button
              onClick={() => handlePageChange((filters.page || 1) + 1)}
              disabled={(filters.page || 1) >= totalPages}
              className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Preview Modal */}
      {previewTemplateId && (
        <TemplatePreviewModal
          templateId={previewTemplateId}
          isOpen={!!previewTemplateId}
          onClose={() => setPreviewTemplateId(null)}
        />
      )}
    </div>
  );
}
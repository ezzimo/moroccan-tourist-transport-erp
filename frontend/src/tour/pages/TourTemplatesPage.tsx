import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search, Filter, Star, Calendar, Users, MapPin } from 'lucide-react';
import { useTourTemplates } from '../hooks/useTourTemplates';
import { TourTemplateFilters } from '../types/template';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';

export default function TourTemplatesPage() {
  const [filters, setFilters] = useState<TourTemplateFilters>({ page: 1, size: 20 });
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  const { data: templatesData, isLoading, error } = useTourTemplates(filters);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setFilters(prev => ({ ...prev, query: searchQuery, page: 1 }));
  };

  const handleFilterChange = (newFilters: Partial<TourTemplateFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters, page: 1 }));
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Failed to load tour templates. Please try again.</p>
      </div>
    );
  }

  const templates = templatesData?.items || [];

  const getDifficultyColor = (level: string) => {
    const colors = {
      EASY: 'bg-green-100 text-green-800',
      MODERATE: 'bg-yellow-100 text-yellow-800',
      CHALLENGING: 'bg-orange-100 text-orange-800',
      EXPERT: 'bg-red-100 text-red-800',
    };
    return colors[level as keyof typeof colors] || colors.EASY;
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      CULTURAL: 'bg-purple-100 text-purple-800',
      ADVENTURE: 'bg-green-100 text-green-800',
      DESERT: 'bg-yellow-100 text-yellow-800',
      COASTAL: 'bg-blue-100 text-blue-800',
      CITY: 'bg-gray-100 text-gray-800',
      CUSTOM: 'bg-indigo-100 text-indigo-800',
    };
    return colors[category as keyof typeof colors] || colors.CUSTOM;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tour Templates</h1>
          <p className="text-gray-600">Create and manage reusable tour templates</p>
        </div>
        <Link
          to="/tours/templates/create"
          className="inline-flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
        >
          <Plus className="h-5 w-5 mr-2" />
          Create Template
        </Link>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg border p-4 space-y-4">
        <form onSubmit={handleSearch} className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search templates by title or description..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
          >
            Search
          </button>
          <button
            type="button"
            onClick={() => setShowFilters(!showFilters)}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Filter className="h-5 w-5" />
          </button>
        </form>

        {showFilters && (
          <div className="bg-gray-50 border rounded-lg p-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                <select
                  value={filters.category || ''}
                  onChange={(e) => handleFilterChange({ category: e.target.value || undefined })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                >
                  <option value="">All Categories</option>
                  <option value="CULTURAL">Cultural</option>
                  <option value="ADVENTURE">Adventure</option>
                  <option value="DESERT">Desert</option>
                  <option value="COASTAL">Coastal</option>
                  <option value="CITY">City</option>
                  <option value="CUSTOM">Custom</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
                <select
                  value={filters.difficulty_level || ''}
                  onChange={(e) => handleFilterChange({ difficulty_level: e.target.value || undefined })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                >
                  <option value="">All Levels</option>
                  <option value="EASY">Easy</option>
                  <option value="MODERATE">Moderate</option>
                  <option value="CHALLENGING">Challenging</option>
                  <option value="EXPERT">Expert</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Duration (days)</label>
                <div className="flex gap-2">
                  <input
                    type="number"
                    placeholder="Min"
                    value={filters.min_duration || ''}
                    onChange={(e) => handleFilterChange({ min_duration: e.target.value ? parseInt(e.target.value) : undefined })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  />
                  <input
                    type="number"
                    placeholder="Max"
                    value={filters.max_duration || ''}
                    onChange={(e) => handleFilterChange({ max_duration: e.target.value ? parseInt(e.target.value) : undefined })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  />
                </div>
              </div>

              <div className="flex items-end">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.is_featured || false}
                    onChange={(e) => handleFilterChange({ is_featured: e.target.checked || undefined })}
                    className="rounded border-gray-300 text-orange-600 focus:ring-orange-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Featured only</span>
                </label>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Templates Grid */}
      {templates.length === 0 ? (
        <EmptyState
          icon={Star}
          title="No tour templates found"
          description="Create your first tour template to get started"
          action={{
            label: 'Create Template',
            onClick: () => window.location.href = '/tours/templates/create',
          }}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {templates.map((template) => (
            <Link
              key={template.id}
              to={`/tours/templates/${template.id}`}
              className="bg-white rounded-lg border hover:shadow-md transition-shadow"
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-1">{template.title}</h3>
                    {template.short_description && (
                      <p className="text-sm text-gray-600 mb-3">{template.short_description}</p>
                    )}
                  </div>
                  {template.is_featured && (
                    <Star className="h-5 w-5 text-yellow-500 fill-current" />
                  )}
                </div>

                <div className="flex flex-wrap gap-2 mb-4">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getCategoryColor(template.category)}`}>
                    {template.category}
                  </span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getDifficultyColor(template.difficulty_level)}`}>
                    {template.difficulty_level}
                  </span>
                </div>

                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4" />
                    <span>{template.duration_days} days</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4" />
                    <span>{template.min_participants}-{template.max_participants} participants</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4" />
                    <span>{template.default_region}</span>
                  </div>
                  {template.base_price && (
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-orange-600">
                        {template.base_price.toLocaleString()} MAD
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Pagination */}
      {templatesData && templatesData.pages > 1 && (
        <div className="flex items-center justify-between border-t bg-white px-4 py-3 rounded-lg">
          <div className="flex items-center text-sm text-gray-500">
            Showing {((filters.page || 1) - 1) * (filters.size || 20) + 1} to{' '}
            {Math.min((filters.page || 1) * (filters.size || 20), templatesData.total)} of{' '}
            {templatesData.total} results
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setFilters(prev => ({ ...prev, page: (prev.page || 1) - 1 }))}
              disabled={(filters.page || 1) <= 1}
              className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <span className="px-3 py-1">
              Page {filters.page || 1} of {templatesData.pages}
            </span>
            <button
              onClick={() => setFilters(prev => ({ ...prev, page: (prev.page || 1) + 1 }))}
              disabled={(filters.page || 1) >= templatesData.pages}
              className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
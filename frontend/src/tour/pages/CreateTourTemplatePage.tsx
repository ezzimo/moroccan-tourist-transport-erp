import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, Save } from 'lucide-react';
import { useCreateTourTemplate } from '../hooks/useTourTemplates';
import { CreateTourTemplateData } from '../types/template';

export default function CreateTourTemplatePage() {
  const navigate = useNavigate();
  const createTemplate = useCreateTourTemplate();
  
  const [formData, setFormData] = useState<CreateTourTemplateData>({
    title: '',
    category: 'CULTURAL',
    duration_days: 1,
    difficulty_level: 'EASY',
    default_region: '',
    min_participants: 1,
    max_participants: 20,
    highlights: [],
    inclusions: [],
    exclusions: [],
  });

  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      await createTemplate.mutateAsync(formData);
      navigate('/tours/templates');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create template');
    }
  };

  const handleChange = (field: keyof CreateTourTemplateData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const addListItem = (field: 'highlights' | 'inclusions' | 'exclusions', item: string) => {
    if (item.trim()) {
      setFormData(prev => ({
        ...prev,
        [field]: [...(prev[field] || []), item.trim()]
      }));
    }
  };

  const removeListItem = (field: 'highlights' | 'inclusions' | 'exclusions', index: number) => {
    setFormData(prev => ({
      ...prev,
      [field]: (prev[field] || []).filter((_, i) => i !== index)
    }));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link
          to="/tours/templates"
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create Tour Template</h1>
          <p className="text-gray-600">Design a reusable tour template</p>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="bg-white rounded-lg border p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Title *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => handleChange('title', e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              placeholder="Imperial Cities Discovery"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Category *
            </label>
            <select
              value={formData.category}
              onChange={(e) => handleChange('category', e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
            >
              <option value="CULTURAL">Cultural</option>
              <option value="ADVENTURE">Adventure</option>
              <option value="DESERT">Desert</option>
              <option value="COASTAL">Coastal</option>
              <option value="CITY">City</option>
              <option value="CUSTOM">Custom</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Duration (days) *
            </label>
            <input
              type="number"
              value={formData.duration_days}
              onChange={(e) => handleChange('duration_days', parseInt(e.target.value) || 1)}
              required
              min="1"
              max="30"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Difficulty Level *
            </label>
            <select
              value={formData.difficulty_level}
              onChange={(e) => handleChange('difficulty_level', e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
            >
              <option value="EASY">Easy</option>
              <option value="MODERATE">Moderate</option>
              <option value="CHALLENGING">Challenging</option>
              <option value="EXPERT">Expert</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Default Region *
            </label>
            <input
              type="text"
              value={formData.default_region}
              onChange={(e) => handleChange('default_region', e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              placeholder="Marrakech"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Base Price (MAD)
            </label>
            <input
              type="number"
              value={formData.base_price || ''}
              onChange={(e) => handleChange('base_price', parseFloat(e.target.value) || undefined)}
              min="0"
              step="0.01"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              placeholder="1200.00"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Description
          </label>
          <textarea
            value={formData.description || ''}
            onChange={(e) => handleChange('description', e.target.value)}
            rows={4}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
            placeholder="Detailed description of the tour..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Short Description
          </label>
          <input
            type="text"
            value={formData.short_description || ''}
            onChange={(e) => handleChange('short_description', e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
            placeholder="Brief summary for listings"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Min Participants
            </label>
            <input
              type="number"
              value={formData.min_participants}
              onChange={(e) => handleChange('min_participants', parseInt(e.target.value) || 1)}
              min="1"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Participants
            </label>
            <input
              type="number"
              value={formData.max_participants}
              onChange={(e) => handleChange('max_participants', parseInt(e.target.value) || 20)}
              min="1"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-4 pt-6 border-t">
          <Link
            to="/tours/templates"
            className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={createTemplate.isPending}
            className="inline-flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Save className="h-4 w-4 mr-2" />
            {createTemplate.isPending ? 'Creating...' : 'Create Template'}
          </button>
        </div>
      </form>
    </div>
  );
}
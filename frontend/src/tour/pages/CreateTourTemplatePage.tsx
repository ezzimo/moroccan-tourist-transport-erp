import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Save, Star, MapPin, Users, Calendar, DollarSign } from 'lucide-react';
import { useCreateTourTemplate } from '../hooks/useTourTemplates';
import { CreateTourTemplateData } from '../types/template';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function CreateTourTemplatePage() {
  const navigate = useNavigate();
  const createTemplate = useCreateTourTemplate();
  
  const [formData, setFormData] = useState<CreateTourTemplateData>({
    title: '',
    description: '',
    short_description: '',
    category: 'CULTURAL',
    duration_days: 1,
    difficulty_level: 'EASY',
    default_language: 'French',
    default_region: '',
    starting_location: '',
    ending_location: '',
    min_participants: 2,
    max_participants: 20,
    base_price: 0,
    highlights: [],
    inclusions: [],
    exclusions: [],
    requirements: '',
  });

  const [errors, setErrors] = useState<Partial<Record<keyof CreateTourTemplateData, string>>>({});
  const [highlightInput, setHighlightInput] = useState('');
  const [inclusionInput, setInclusionInput] = useState('');
  const [exclusionInput, setExclusionInput] = useState('');

  const validateForm = () => {
    const newErrors: Partial<Record<keyof CreateTourTemplateData, string>> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }
    if (!formData.default_region.trim()) {
      newErrors.default_region = 'Region is required';
    }
    if (formData.duration_days < 1 || formData.duration_days > 30) {
      newErrors.duration_days = 'Duration must be between 1 and 30 days';
    }
    if (formData.min_participants < 1) {
      newErrors.min_participants = 'Minimum participants must be at least 1';
    }
    if (formData.max_participants < formData.min_participants) {
      newErrors.max_participants = 'Maximum participants must be greater than minimum';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      await createTemplate.mutateAsync(formData);
      navigate('/tours/templates');
    } catch (error) {
      console.error('Failed to create tour template:', error);
    }
  };

  const handleFieldChange = (field: keyof CreateTourTemplateData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const addToList = (listField: 'highlights' | 'inclusions' | 'exclusions', value: string, setValue: (val: string) => void) => {
    if (value.trim()) {
      const currentList = formData[listField] || [];
      handleFieldChange(listField, [...currentList, value.trim()]);
      setValue('');
    }
  };

  const removeFromList = (listField: 'highlights' | 'inclusions' | 'exclusions', index: number) => {
    const currentList = formData[listField] || [];
    handleFieldChange(listField, currentList.filter((_, i) => i !== index));
  };

  const categories = [
    { value: 'CULTURAL', label: 'Cultural', icon: '🏛️' },
    { value: 'ADVENTURE', label: 'Adventure', icon: '🏔️' },
    { value: 'DESERT', label: 'Desert', icon: '🏜️' },
    { value: 'COASTAL', label: 'Coastal', icon: '🏖️' },
    { value: 'CITY', label: 'City', icon: '🏙️' },
    { value: 'CUSTOM', label: 'Custom', icon: '⚙️' },
  ];

  const difficultyLevels = [
    { value: 'EASY', label: 'Easy', color: 'bg-green-100 text-green-800' },
    { value: 'MODERATE', label: 'Moderate', color: 'bg-yellow-100 text-yellow-800' },
    { value: 'CHALLENGING', label: 'Challenging', color: 'bg-orange-100 text-orange-800' },
    { value: 'EXPERT', label: 'Expert', color: 'bg-red-100 text-red-800' },
  ];

  const moroccanRegions = [
    'Casablanca', 'Rabat', 'Marrakech', 'Fez', 'Tangier', 'Agadir',
    'Meknes', 'Oujda', 'Kenitra', 'Tetouan', 'Safi', 'Mohammedia',
    'Atlas Mountains', 'Sahara Desert', 'Atlantic Coast', 'Mediterranean Coast'
  ];

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

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Basic Information */}
        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-6">Basic Information</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="lg:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tour Title *
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => handleFieldChange('title', e.target.value)}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 ${
                  errors.title ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="e.g., Imperial Cities Discovery"
              />
              {errors.title && <p className="text-red-500 text-sm mt-1">{errors.title}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Category *
              </label>
              <div className="grid grid-cols-2 gap-2">
                {categories.map((category) => (
                  <button
                    key={category.value}
                    type="button"
                    onClick={() => handleFieldChange('category', category.value)}
                    className={`p-3 border rounded-lg text-left transition-colors ${
                      formData.category === category.value
                        ? 'border-orange-500 bg-orange-50 text-orange-700'
                        : 'border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{category.icon}</span>
                      <span className="font-medium">{category.label}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Difficulty Level *
              </label>
              <div className="space-y-2">
                {difficultyLevels.map((level) => (
                  <label key={level.value} className="flex items-center">
                    <input
                      type="radio"
                      name="difficulty_level"
                      value={level.value}
                      checked={formData.difficulty_level === level.value}
                      onChange={(e) => handleFieldChange('difficulty_level', e.target.value)}
                      className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300"
                    />
                    <span className={`ml-3 px-2 py-1 text-xs font-medium rounded-full ${level.color}`}>
                      {level.label}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Duration (Days) *
              </label>
              <input
                type="number"
                value={formData.duration_days}
                onChange={(e) => handleFieldChange('duration_days', parseInt(e.target.value) || 1)}
                min="1"
                max="30"
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 ${
                  errors.duration_days ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.duration_days && <p className="text-red-500 text-sm mt-1">{errors.duration_days}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Default Region *
              </label>
              <select
                value={formData.default_region}
                onChange={(e) => handleFieldChange('default_region', e.target.value)}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 ${
                  errors.default_region ? 'border-red-500' : 'border-gray-300'
                }`}
              >
                <option value="">Select region</option>
                {moroccanRegions.map((region) => (
                  <option key={region} value={region}>
                    {region}
                  </option>
                ))}
              </select>
              {errors.default_region && <p className="text-red-500 text-sm mt-1">{errors.default_region}</p>}
            </div>
          </div>

          <div className="mt-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Short Description
            </label>
            <input
              type="text"
              value={formData.short_description}
              onChange={(e) => handleFieldChange('short_description', e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              placeholder="Brief description for listings"
              maxLength={500}
            />
          </div>

          <div className="mt-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Full Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => handleFieldChange('description', e.target.value)}
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              placeholder="Detailed tour description..."
            />
          </div>
        </div>

        {/* Location & Logistics */}
        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-6">Location & Logistics</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Starting Location
              </label>
              <input
                type="text"
                value={formData.starting_location}
                onChange={(e) => handleFieldChange('starting_location', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                placeholder="e.g., Casablanca Airport"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ending Location
              </label>
              <input
                type="text"
                value={formData.ending_location}
                onChange={(e) => handleFieldChange('ending_location', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                placeholder="e.g., Marrakech Hotel"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Default Language
              </label>
              <select
                value={formData.default_language}
                onChange={(e) => handleFieldChange('default_language', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              >
                <option value="French">French</option>
                <option value="Arabic">Arabic</option>
                <option value="English">English</option>
                <option value="Spanish">Spanish</option>
              </select>
            </div>
          </div>
        </div>

        {/* Capacity & Pricing */}
        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-6">Capacity & Pricing</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Users className="inline h-4 w-4 mr-1" />
                Minimum Participants *
              </label>
              <input
                type="number"
                value={formData.min_participants}
                onChange={(e) => handleFieldChange('min_participants', parseInt(e.target.value) || 1)}
                min="1"
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 ${
                  errors.min_participants ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.min_participants && <p className="text-red-500 text-sm mt-1">{errors.min_participants}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Users className="inline h-4 w-4 mr-1" />
                Maximum Participants *
              </label>
              <input
                type="number"
                value={formData.max_participants}
                onChange={(e) => handleFieldChange('max_participants', parseInt(e.target.value) || 1)}
                min="1"
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 ${
                  errors.max_participants ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.max_participants && <p className="text-red-500 text-sm mt-1">{errors.max_participants}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <DollarSign className="inline h-4 w-4 mr-1" />
                Base Price (MAD)
              </label>
              <input
                type="number"
                value={formData.base_price || ''}
                onChange={(e) => handleFieldChange('base_price', parseFloat(e.target.value) || undefined)}
                min="0"
                step="0.01"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                placeholder="0.00"
              />
            </div>
          </div>
        </div>

        {/* Tour Details */}
        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-6">Tour Details</h2>
          
          {/* Highlights */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Star className="inline h-4 w-4 mr-1" />
              Highlights
            </label>
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                value={highlightInput}
                onChange={(e) => setHighlightInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addToList('highlights', highlightInput, setHighlightInput))}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                placeholder="Add a highlight and press Enter"
              />
              <button
                type="button"
                onClick={() => addToList('highlights', highlightInput, setHighlightInput)}
                className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {(formData.highlights || []).map((highlight, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 bg-orange-100 text-orange-800 text-sm rounded-full"
                >
                  {highlight}
                  <button
                    type="button"
                    onClick={() => removeFromList('highlights', index)}
                    className="ml-2 text-orange-600 hover:text-orange-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Inclusions */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              What's Included
            </label>
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                value={inclusionInput}
                onChange={(e) => setInclusionInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addToList('inclusions', inclusionInput, setInclusionInput))}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                placeholder="Add an inclusion and press Enter"
              />
              <button
                type="button"
                onClick={() => addToList('inclusions', inclusionInput, setInclusionInput)}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {(formData.inclusions || []).map((inclusion, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full"
                >
                  {inclusion}
                  <button
                    type="button"
                    onClick={() => removeFromList('inclusions', index)}
                    className="ml-2 text-green-600 hover:text-green-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Exclusions */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              What's Not Included
            </label>
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                value={exclusionInput}
                onChange={(e) => setExclusionInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addToList('exclusions', exclusionInput, setExclusionInput))}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                placeholder="Add an exclusion and press Enter"
              />
              <button
                type="button"
                onClick={() => addToList('exclusions', exclusionInput, setExclusionInput)}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {(formData.exclusions || []).map((exclusion, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 bg-red-100 text-red-800 text-sm rounded-full"
                >
                  {exclusion}
                  <button
                    type="button"
                    onClick={() => removeFromList('exclusions', index)}
                    className="ml-2 text-red-600 hover:text-red-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Requirements */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Requirements & Notes
            </label>
            <textarea
              value={formData.requirements}
              onChange={(e) => handleFieldChange('requirements', e.target.value)}
              rows={3}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              placeholder="Special requirements, fitness level, what to bring..."
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-4 pt-6 border-t">
          <Link
            to="/tours/templates"
            className="px-6 py-3 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={createTemplate.isPending}
            className="inline-flex items-center px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {createTemplate.isPending ? (
              <>
                <LoadingSpinner size="sm" className="mr-2" />
                Creating...
              </>
            ) : (
              <>
                <Save className="h-5 w-5 mr-2" />
                Create Template
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
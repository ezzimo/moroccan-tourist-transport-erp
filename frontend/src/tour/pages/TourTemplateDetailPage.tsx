import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Star, Calendar, Users, MapPin, Edit } from 'lucide-react';
import { useTourTemplate } from '../hooks/useTourTemplates';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function TourTemplateDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: template, isLoading } = useTourTemplate(id!);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!template) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Tour template not found</p>
        <Link to="/tours/templates" className="text-orange-600 hover:text-orange-700 mt-2 inline-block">
          Back to Templates
        </Link>
      </div>
    );
  }

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
      <div className="flex items-center gap-4">
        <Link
          to="/tours/templates"
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">{template.title}</h1>
            {template.is_featured && (
              <Star className="h-6 w-6 text-yellow-500 fill-current" />
            )}
          </div>
          <p className="text-gray-600">{template.short_description}</p>
        </div>
        <button className="inline-flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors">
          <Edit className="h-4 w-4 mr-2" />
          Edit Template
        </button>
      </div>

      {/* Template Details */}
      <div className="bg-white rounded-lg border p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            {/* Basic Info */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Tour Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getCategoryColor(template.category)}`}>
                    {template.category}
                  </span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getDifficultyColor(template.difficulty_level)}`}>
                    {template.difficulty_level}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Calendar className="h-4 w-4" />
                  <span>{template.duration_days} days</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Users className="h-4 w-4" />
                  <span>{template.min_participants}-{template.max_participants} participants</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <MapPin className="h-4 w-4" />
                  <span>{template.default_region}</span>
                </div>
              </div>
            </div>

            {/* Description */}
            {template.description && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Description</h3>
                <p className="text-gray-700">{template.description}</p>
              </div>
            )}

            {/* Highlights */}
            {template.highlights && template.highlights.length > 0 && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Highlights</h3>
                <ul className="list-disc list-inside space-y-1">
                  {template.highlights.map((highlight, index) => (
                    <li key={index} className="text-gray-700">{highlight}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Inclusions */}
            {template.inclusions && template.inclusions.length > 0 && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">What's Included</h3>
                <ul className="list-disc list-inside space-y-1">
                  {template.inclusions.map((inclusion, index) => (
                    <li key={index} className="text-gray-700">{inclusion}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Exclusions */}
            {template.exclusions && template.exclusions.length > 0 && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">What's Not Included</h3>
                <ul className="list-disc list-inside space-y-1">
                  {template.exclusions.map((exclusion, index) => (
                    <li key={index} className="text-gray-700">{exclusion}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Requirements */}
            {template.requirements && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Requirements</h3>
                <p className="text-gray-700">{template.requirements}</p>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Pricing */}
            {template.base_price && (
              <div className="bg-orange-50 p-4 rounded-lg">
                <h4 className="font-medium text-orange-900 mb-2">Starting Price</h4>
                <p className="text-2xl font-bold text-orange-900">
                  {template.base_price.toLocaleString()} MAD
                </p>
                <p className="text-sm text-orange-700">per person</p>
              </div>
            )}

            {/* Location Details */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-3">Location Details</h4>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="font-medium text-gray-700">Region:</span>
                  <span className="ml-2 text-gray-600">{template.default_region}</span>
                </div>
                {template.starting_location && (
                  <div>
                    <span className="font-medium text-gray-700">Starts:</span>
                    <span className="ml-2 text-gray-600">{template.starting_location}</span>
                  </div>
                )}
                {template.ending_location && (
                  <div>
                    <span className="font-medium text-gray-700">Ends:</span>
                    <span className="ml-2 text-gray-600">{template.ending_location}</span>
                  </div>
                )}
                <div>
                  <span className="font-medium text-gray-700">Language:</span>
                  <span className="ml-2 text-gray-600">{template.default_language}</span>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="space-y-3">
              <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors">
                Create Tour Instance
              </button>
              <button className="w-full bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700 transition-colors">
                Duplicate Template
              </button>
            </div>

            {/* Metadata */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-3">Template Info</h4>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="font-medium text-gray-700">Status:</span>
                  <span className={`ml-2 ${template.is_active ? 'text-green-600' : 'text-red-600'}`}>
                    {template.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Created:</span>
                  <span className="ml-2 text-gray-600">
                    {new Date(template.created_at).toLocaleDateString()}
                  </span>
                </div>
                {template.updated_at && (
                  <div>
                    <span className="font-medium text-gray-700">Updated:</span>
                    <span className="ml-2 text-gray-600">
                      {new Date(template.updated_at).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
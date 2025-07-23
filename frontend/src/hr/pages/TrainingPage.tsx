import React, { useState } from 'react';
import { Plus, Search, Filter, BookOpen, Users, Clock, Award } from 'lucide-react';
import { useTrainingPrograms } from '../hooks/useTraining';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';

export default function TrainingPage() {
  const [filters, setFilters] = useState<any>({ page: 1, size: 20 });
  const [showFilters, setShowFilters] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const { data: trainingData, isLoading, error } = useTrainingPrograms(filters);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setFilters((prev: any) => ({ ...prev, query: searchQuery, page: 1 }));
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
        <p className="text-red-600">Failed to load training programs. Please try again.</p>
      </div>
    );
  }

  const programs = trainingData?.items || [];

  const getStatusColor = (status: string) => {
    const colors = {
      PLANNED: 'bg-blue-100 text-blue-800',
      ACTIVE: 'bg-green-100 text-green-800',
      COMPLETED: 'bg-gray-100 text-gray-800',
      CANCELLED: 'bg-red-100 text-red-800',
    };
    return colors[status as keyof typeof colors] || colors.PLANNED;
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      SAFETY: 'bg-red-100 text-red-800',
      TECHNICAL: 'bg-blue-100 text-blue-800',
      CUSTOMER_SERVICE: 'bg-green-100 text-green-800',
      LEADERSHIP: 'bg-purple-100 text-purple-800',
      COMPLIANCE: 'bg-yellow-100 text-yellow-800',
      OTHER: 'bg-gray-100 text-gray-800',
    };
    return colors[category as keyof typeof colors] || colors.OTHER;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Training Programs</h1>
          <p className="text-gray-600">Manage employee training and development</p>
        </div>
        <button className="inline-flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors">
          <Plus className="h-5 w-5 mr-2" />
          Create Program
        </button>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg border p-4 space-y-4">
        <form onSubmit={handleSearch} className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search training programs..."
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
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <BookOpen className="h-8 w-8 text-orange-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Total Programs</p>
              <p className="text-2xl font-bold text-gray-900">{programs.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <Users className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Active Programs</p>
              <p className="text-2xl font-bold text-gray-900">
                {programs.filter(p => p.status === 'ACTIVE').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <Clock className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Mandatory</p>
              <p className="text-2xl font-bold text-gray-900">
                {programs.filter(p => p.is_mandatory).length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <Award className="h-8 w-8 text-purple-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Completed</p>
              <p className="text-2xl font-bold text-gray-900">
                {programs.filter(p => p.status === 'COMPLETED').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Training Programs List */}
      {programs.length === 0 ? (
        <EmptyState
          icon={BookOpen}
          title="No training programs found"
          description="Create your first training program to get started"
          action={{
            label: 'Create Program',
            onClick: () => {},
          }}
        />
      ) : (
        <div className="bg-white rounded-lg border">
          <div className="divide-y">
            {programs.map((program) => (
              <div key={program.id} className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-gray-900 mb-2">{program.title}</h3>
                    {program.description && (
                      <p className="text-gray-600 mb-3">{program.description}</p>
                    )}
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        {program.duration_hours} hours
                      </span>
                      <span className="flex items-center gap-1">
                        <Users className="h-4 w-4" />
                        Max {program.max_participants} participants
                      </span>
                      {program.trainer_name && (
                        <span>Trainer: {program.trainer_name}</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getCategoryColor(program.category)}`}>
                      {program.category.replace('_', ' ')}
                    </span>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(program.status)}`}>
                      {program.status}
                    </span>
                    {program.is_mandatory && (
                      <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded-full">
                        Mandatory
                      </span>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <div className="flex items-center gap-4">
                    <span>Start: {new Date(program.start_date).toLocaleDateString()}</span>
                    <span>End: {new Date(program.end_date).toLocaleDateString()}</span>
                    <span>Pass Score: {program.pass_score}%</span>
                  </div>
                  {program.cost_per_participant && (
                    <span className="font-medium text-gray-900">
                      {program.cost_per_participant} MAD per participant
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, MapPin, Calendar, Users, Clock } from 'lucide-react';
import { useTourInstances, useActiveTours } from '../hooks/useTourInstances';
import { TourInstanceFilters } from '../types/instance';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';

export default function TourInstancesPage() {
  const [filters, setFilters] = useState<TourInstanceFilters>({ page: 1, size: 20 });
  const [activeTab, setActiveTab] = useState<'all' | 'active' | 'planned'>('all');

  const { data: instancesData, isLoading: instancesLoading } = useTourInstances(filters);
  const { data: activeTours, isLoading: activeLoading } = useActiveTours();

  if (instancesLoading || activeLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const allInstances = instancesData?.items || [];
  const activeInstances = activeTours || [];
  const plannedInstances = allInstances.filter(t => t.status === 'PLANNED');

  const getStatusColor = (status: string) => {
    const colors = {
      PLANNED: 'bg-blue-100 text-blue-800',
      CONFIRMED: 'bg-green-100 text-green-800',
      IN_PROGRESS: 'bg-yellow-100 text-yellow-800',
      COMPLETED: 'bg-gray-100 text-gray-800',
      CANCELLED: 'bg-red-100 text-red-800',
      POSTPONED: 'bg-orange-100 text-orange-800',
    };
    return colors[status as keyof typeof colors] || colors.PLANNED;
  };

  const getCurrentInstances = () => {
    switch (activeTab) {
      case 'active':
        return activeInstances;
      case 'planned':
        return plannedInstances;
      default:
        return allInstances;
    }
  };

  const currentInstances = getCurrentInstances();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tour Instances</h1>
          <p className="text-gray-600">Track active and planned tours</p>
        </div>
        <Link
          to="/tours/templates/create"
          className="inline-flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
        >
          <Plus className="h-5 w-5 mr-2" />
          Create Template
        </Link>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <MapPin className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Total Tours</p>
              <p className="text-2xl font-bold text-gray-900">{allInstances.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <Clock className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Active</p>
              <p className="text-2xl font-bold text-gray-900">{activeInstances.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <Calendar className="h-8 w-8 text-yellow-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Planned</p>
              <p className="text-2xl font-bold text-gray-900">{plannedInstances.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <Users className="h-8 w-8 text-purple-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Total Passengers</p>
              <p className="text-2xl font-bold text-gray-900">
                {allInstances.reduce((sum, t) => sum + t.participant_count, 0)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'all', label: 'All Tours', count: allInstances.length },
            { id: 'active', label: 'Active', count: activeInstances.length },
            { id: 'planned', label: 'Planned', count: plannedInstances.length },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-orange-500 text-orange-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label} ({tab.count})
            </button>
          ))}
        </nav>
      </div>

      {/* Tour Instances List */}
      {currentInstances.length === 0 ? (
        <EmptyState
          icon={MapPin}
          title="No tour instances found"
          description="Tour instances will appear here once created from templates"
          action={{
            label: 'View Templates',
            onClick: () => navigate('/tours/templates'),
          }}
        />
      ) : (
        <div className="bg-white rounded-lg border">
          <div className="divide-y">
            {currentInstances.map((instance) => (
              <Link
                key={instance.id}
                to={`/tours/${instance.id}`}
                className="block p-6 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900 mb-1">{instance.title}</h3>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span className="flex items-center gap-1">
                        <Users className="h-4 w-4" />
                        {instance.participant_count} passengers
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        {new Date(instance.start_date).toLocaleDateString()}
                      </span>
                      <span>{instance.lead_participant_name}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(instance.status)}`}>
                      {instance.status.replace('_', ' ')}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-6 text-sm text-gray-500">
                    <span>Day {instance.current_day}</span>
                    <span>{instance.completion_percentage.toFixed(0)}% complete</span>
                    {instance.language && <span>Language: {instance.language}</span>}
                  </div>
                  <div className="text-sm text-gray-500">
                    {instance.end_date && (
                      <span>Until {new Date(instance.end_date).toLocaleDateString()}</span>
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
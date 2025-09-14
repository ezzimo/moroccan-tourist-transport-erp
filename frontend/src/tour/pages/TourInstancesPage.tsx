import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, MapPin, Calendar, Users, Clock, CheckCircle, AlertTriangle } from 'lucide-react';
import { useTourInstances, useActiveTours } from '../hooks/useTourInstances';
import { TourInstanceFilters } from '../types/instance';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';

export default function TourInstancesPage() {
  const [activeTab, setActiveTab] = useState<'active' | 'planned' | 'completed'>('active');
  const [filters, setFilters] = useState<TourInstanceFilters>({ page: 1, size: 20 });

  // Get data based on active tab
  const getStatusFilter = () => {
    switch (activeTab) {
      case 'active':
        return { status: 'IN_PROGRESS' };
      case 'planned':
        return { status: 'PLANNED' };
      case 'completed':
        return { status: 'COMPLETED' };
      default:
        return {};
    }
  };

  const { data: tourInstancesData, isLoading } = useTourInstances({
    ...filters,
    ...getStatusFilter(),
  });

  const { data: activeTours } = useActiveTours();

  const handleTabChange = (tab: 'active' | 'planned' | 'completed') => {
    setActiveTab(tab);
    setFilters(prev => ({ ...prev, page: 1 }));
  };

  const getStatusColor = (status: string) => {
    const colors = {
      PLANNED: 'bg-blue-100 text-blue-800',
      CONFIRMED: 'bg-green-100 text-green-800',
      IN_PROGRESS: 'bg-yellow-100 text-yellow-800',
      COMPLETED: 'bg-green-100 text-green-800',
      CANCELLED: 'bg-red-100 text-red-800',
      POSTPONED: 'bg-gray-100 text-gray-800',
    };
    return colors[status as keyof typeof colors] || colors.PLANNED;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'IN_PROGRESS':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'CANCELLED':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      default:
        return <Calendar className="h-4 w-4 text-blue-500" />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const tourInstances = tourInstancesData?.items || [];
  const totalPages = tourInstancesData?.pages || 1;

  const tabs = [
    { 
      id: 'active', 
      label: 'Active Tours', 
      count: activeTours?.length || 0,
      color: 'text-yellow-600 bg-yellow-100'
    },
    { 
      id: 'planned', 
      label: 'Planned Tours', 
      count: tourInstances.filter(t => t.status === 'PLANNED').length,
      color: 'text-blue-600 bg-blue-100'
    },
    { 
      id: 'completed', 
      label: 'Completed Tours', 
      count: tourInstances.filter(t => t.status === 'COMPLETED').length,
      color: 'text-green-600 bg-green-100'
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tour Instances</h1>
          <p className="text-gray-600">Track active, planned, and completed tours</p>
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
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {tabs.map((tab) => (
          <div key={tab.id} className="bg-white p-4 rounded-lg border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">{tab.label}</p>
                <p className="text-2xl font-bold text-gray-900">{tab.count}</p>
              </div>
              <div className={`p-3 rounded-lg ${tab.color}`}>
                <MapPin className="h-6 w-6" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleTabChange(tab.id as any)}
              className={`group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-orange-500 text-orange-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <MapPin className="h-5 w-5 mr-2" />
              {tab.label}
              {tab.count > 0 && (
                <span className={`ml-2 px-2 py-1 text-xs font-medium rounded-full ${
                  activeTab === tab.id ? 'bg-orange-100 text-orange-800' : 'bg-gray-100 text-gray-600'
                }`}>
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Tour Instances List */}
      {tourInstances.length === 0 ? (
        <EmptyState
          icon={MapPin}
          title={`No ${activeTab} tours found`}
          description={`${activeTab === 'active' ? 'No tours are currently in progress' : 
            activeTab === 'planned' ? 'No tours are scheduled' : 'No tours have been completed yet'}`}
          action={activeTab === 'planned' ? {
            label: 'Create Template',
            onClick: () => window.location.href = '/tours/templates/create',
          } : undefined}
        />
      ) : (
        <div className="bg-white rounded-lg border">
          <div className="divide-y">
            {tourInstances.map((tour) => (
              <Link
                key={tour.id}
                to={`/tours/instances/${tour.id}`}
                className="block p-6 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      {getStatusIcon(tour.status)}
                      <h3 className="font-medium text-gray-900">{tour.title}</h3>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span className="flex items-center gap-1">
                        <Users className="h-4 w-4" />
                        {tour.participant_count} participants
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        {formatDate(tour.start_date)} - {formatDate(tour.end_date)}
                      </span>
                      <span>Lead: {tour.lead_participant_name}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(tour.status)}`}>
                      {tour.status.replace('_', ' ')}
                    </span>
                    {tour.status === 'IN_PROGRESS' && (
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-900">Day {tour.current_day}</p>
                        <p className="text-xs text-gray-500">{tour.completion_percentage}% complete</p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-6 text-sm text-gray-500">
                    <span>{tour.language}</span>
                    {tour.assigned_guide_id && <span>Guide assigned</span>}
                    {tour.assigned_vehicle_id && <span>Vehicle assigned</span>}
                    {tour.assigned_driver_id && <span>Driver assigned</span>}
                  </div>
                  <div className="text-xs text-gray-400">
                    Created: {formatDate(tour.created_at)}
                    {tour.confirmed_at && (
                      <span className="ml-2">• Confirmed: {formatDate(tour.confirmed_at)}</span>
                    )}
                  </div>
                </div>

                {tour.special_requirements && (
                  <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                    <p className="text-sm text-blue-800">
                      <span className="font-medium">Special Requirements:</span> {tour.special_requirements}
                    </p>
                  </div>
                )}
              </Link>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between border-t px-4 py-3">
              <div className="flex items-center text-sm text-gray-500">
                Showing {((filters.page || 1) - 1) * (filters.size || 20) + 1} to{' '}
                {Math.min((filters.page || 1) * (filters.size || 20), tourInstancesData?.total || 0)} of{' '}
                {tourInstancesData?.total || 0} results
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
                  Page {filters.page || 1} of {totalPages}
                </span>
                <button
                  onClick={() => setFilters(prev => ({ ...prev, page: (prev.page || 1) + 1 }))}
                  disabled={(filters.page || 1) >= totalPages}
                  className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
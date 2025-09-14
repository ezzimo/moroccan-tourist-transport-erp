import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, MapPin, Calendar, Users, Star, Clock } from 'lucide-react';
import { useFeaturedTourTemplates } from '../hooks/useTourTemplates';
import { useActiveTours } from '../hooks/useTourInstances';
import { useIncidentStats } from '../hooks/useIncidents';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function ToursPage() {
  const { data: featuredTemplates, isLoading: templatesLoading } = useFeaturedTourTemplates(6);
  const { data: activeTours, isLoading: toursLoading } = useActiveTours();
  const { data: incidentStats, isLoading: statsLoading, error: incidentStatsError } = useIncidentStats(30);

  if (templatesLoading || toursLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const stats = [
    {
      name: 'Active Tours',
      value: activeTours?.length || 0,
      icon: MapPin,
      color: 'text-blue-600 bg-blue-100',
      href: '/tours/instances',
    },
    {
      name: 'Featured Templates',
      value: featuredTemplates?.length || 0,
      icon: Star,
      color: 'text-yellow-600 bg-yellow-100',
      href: '/tours/templates',
    },
    {
      name: 'Total Incidents',
      value: incidentStatsError ? 0 : (incidentStats?.total_incidents || 0),
      icon: Clock,
      color: 'text-red-600 bg-red-100',
      href: '/tours/incidents',
    },
    {
      name: 'Urgent Issues',
      value: incidentStatsError ? 0 : (incidentStats?.urgent_incidents || 0),
      icon: Users,
      color: 'text-orange-600 bg-orange-100',
      href: '/tours/incidents?urgent=true',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tour Operations</h1>
          <p className="text-gray-600">Manage tour templates, instances, and operations</p>
        </div>
        <div className="flex gap-3">
          <Link
            to="/tours/templates/create"
            className="inline-flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
          >
            <Plus className="h-5 w-5 mr-2" />
            Create Template
          </Link>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Link
              key={stat.name}
              to={stat.href}
              className="bg-white rounded-lg border p-6 hover:shadow-md transition-shadow group"
            >
              <div className="flex items-center">
                <div className={`p-3 rounded-lg ${stat.color}`}>
                  <Icon className="h-6 w-6" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">{stat.name}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </Link>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Featured Templates */}
        <div className="bg-white rounded-lg border">
          <div className="p-6 border-b">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Featured Templates</h3>
              <Link
                to="/tours/templates"
                className="text-sm text-orange-600 hover:text-orange-700"
              >
                View all
              </Link>
            </div>
          </div>
          <div className="p-6">
            {featuredTemplates?.length === 0 ? (
              <p className="text-gray-500 text-center py-4">No featured templates</p>
            ) : (
              <div className="space-y-4">
                {featuredTemplates?.slice(0, 4).map((template) => (
                  <Link
                    key={template.id}
                    to={`/tours/templates/${template.id}`}
                    className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{template.title}</h4>
                      <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
                        <span className="flex items-center gap-1">
                          <Calendar className="h-4 w-4" />
                          {template.duration_days} days
                        </span>
                        <span className="flex items-center gap-1">
                          <Users className="h-4 w-4" />
                          {template.min_participants}-{template.max_participants}
                        </span>
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                          {template.category}
                        </span>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Active Tours */}
        <div className="bg-white rounded-lg border">
          <div className="p-6 border-b">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Active Tours</h3>
              <Link
                to="/tours/instances"
                className="text-sm text-orange-600 hover:text-orange-700"
              >
                View all
              </Link>
            </div>
          </div>
          <div className="p-6">
            {activeTours?.length === 0 ? (
              <p className="text-gray-500 text-center py-4">No active tours</p>
            ) : (
              <div className="space-y-4">
                {activeTours?.slice(0, 4).map((tour) => (
                  <Link
                    key={tour.id}
                    to={`/tours/instances/${tour.id}`}
                    className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{tour.title}</h4>
                      <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
                        <span>{tour.lead_participant_name}</span>
                        <span className="flex items-center gap-1">
                          <Users className="h-4 w-4" />
                          {tour.participant_count}
                        </span>
                        <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                          {tour.status}
                        </span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-500">Day {tour.current_day}</p>
                      <p className="text-xs text-gray-400">{tour.completion_percentage}% complete</p>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Navigation */}
      <div className="bg-white rounded-lg border p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Navigation</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            to="/tours/templates" 
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors group"
          >
            <Star className="h-8 w-8 text-yellow-600" />
            <div className="ml-3">
              <p className="font-medium text-gray-900">Tour Templates</p>
              <p className="text-sm text-gray-500">Create and manage tour templates</p>
            </div>
          </Link>
          
          <Link
            to="/tours/instances"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors group"
          >
            <MapPin className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="font-medium text-gray-900">Tour Instances</p>
              <p className="text-sm text-gray-500">Track active and planned tours</p>
            </div>
          </Link>
          
          <Link
            to="#"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors group"
          >
            <Clock className="h-8 w-8 text-red-600" />
            <div className="ml-3">
              <p className="font-medium text-gray-900">Incidents (Coming Soon)</p>
              <p className="text-sm text-gray-500">Will monitor and resolve issues</p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}
import React, { useState } from 'react';
import { Plus, AlertTriangle, Clock, CheckCircle } from 'lucide-react';
import { useIncidents, useUrgentIncidents, useIncidentStats } from '../hooks/useIncidents';
import { TourIncidentFilters } from '../types/incident';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';

export default function TourIncidentsPage() {
  const [filters, setFilters] = useState<TourIncidentFilters>({ page: 1, size: 20 });
  const [activeTab, setActiveTab] = useState<'all' | 'urgent' | 'unresolved'>('all');

  const { data: incidentsData, isLoading: incidentsLoading } = useIncidents(filters);
  const { data: urgentIncidents, isLoading: urgentLoading } = useUrgentIncidents();
  const { data: stats, isLoading: statsLoading } = useIncidentStats(30);

  if (incidentsLoading || urgentLoading || statsLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const allIncidents = incidentsData?.items || [];
  const unresolvedIncidents = allIncidents.filter(i => !i.is_resolved);

  const getSeverityColor = (severity: string) => {
    const colors = {
      LOW: 'bg-blue-100 text-blue-800',
      MEDIUM: 'bg-yellow-100 text-yellow-800',
      HIGH: 'bg-orange-100 text-orange-800',
      CRITICAL: 'bg-red-100 text-red-800',
    };
    return colors[severity as keyof typeof colors] || colors.LOW;
  };

  const getTypeColor = (type: string) => {
    const colors = {
      DELAY: 'bg-yellow-100 text-yellow-800',
      MEDICAL: 'bg-red-100 text-red-800',
      COMPLAINT: 'bg-orange-100 text-orange-800',
      BREAKDOWN: 'bg-red-100 text-red-800',
      WEATHER: 'bg-blue-100 text-blue-800',
      SAFETY: 'bg-red-100 text-red-800',
      OTHER: 'bg-gray-100 text-gray-800',
    };
    return colors[type as keyof typeof colors] || colors.OTHER;
  };

  const getCurrentIncidents = () => {
    switch (activeTab) {
      case 'urgent':
        return urgentIncidents || [];
      case 'unresolved':
        return unresolvedIncidents;
      default:
        return allIncidents;
    }
  };

  const currentIncidents = getCurrentIncidents();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tour Incidents</h1>
          <p className="text-gray-600">Monitor and resolve tour-related issues</p>
        </div>
        <button className="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
          <Plus className="h-5 w-5 mr-2" />
          Report Incident
        </button>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center">
              <AlertTriangle className="h-8 w-8 text-orange-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Total Incidents</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_incidents}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Resolved</p>
                <p className="text-2xl font-bold text-gray-900">{stats.resolved_incidents}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center">
              <Clock className="h-8 w-8 text-yellow-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Unresolved</p>
                <p className="text-2xl font-bold text-gray-900">{stats.unresolved_incidents}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center">
              <AlertTriangle className="h-8 w-8 text-red-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Urgent</p>
                <p className="text-2xl font-bold text-gray-900">{stats.urgent_incidents}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'all', label: 'All Incidents', count: allIncidents.length },
            { id: 'urgent', label: 'Urgent', count: urgentIncidents?.length || 0 },
            { id: 'unresolved', label: 'Unresolved', count: unresolvedIncidents.length },
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

      {/* Incidents List */}
      {currentIncidents.length === 0 ? (
        <EmptyState
          icon={AlertTriangle}
          title="No incidents found"
          description="Incident reports will appear here when issues are reported"
        />
      ) : (
        <div className="bg-white rounded-lg border">
          <div className="divide-y">
            {currentIncidents.map((incident) => (
              <div key={incident.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-medium text-gray-900">{incident.title}</h3>
                      {incident.is_urgent && (
                        <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded-full">
                          URGENT
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{incident.description}</p>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>Priority: {incident.priority_score}</span>
                      {incident.location && <span>• {incident.location}</span>}
                      {incident.day_number && <span>• Day {incident.day_number}</span>}
                      {incident.affected_participants && (
                        <span>• {incident.affected_participants} affected</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTypeColor(incident.incident_type)}`}>
                      {incident.incident_type}
                    </span>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getSeverityColor(incident.severity)}`}>
                      {incident.severity}
                    </span>
                    {incident.is_resolved ? (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    ) : (
                      <Clock className="h-5 w-5 text-yellow-500" />
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-6 text-sm text-gray-500">
                    <span>Reported: {new Date(incident.reported_at).toLocaleDateString()}</span>
                    {incident.estimated_delay_minutes && (
                      <span>Delay: {incident.estimated_delay_minutes} min</span>
                    )}
                  </div>
                  <div className="text-sm text-gray-500">
                    {incident.is_resolved ? (
                      <span className="text-green-600">
                        Resolved {incident.resolved_at && new Date(incident.resolved_at).toLocaleDateString()}
                      </span>
                    ) : (
                      <span className="text-yellow-600">Pending resolution</span>
                    )}
                  </div>
                </div>

                {incident.resolution_description && (
                  <div className="mt-3 p-3 bg-green-50 rounded-lg">
                    <p className="text-sm font-medium text-green-800 mb-1">Resolution:</p>
                    <p className="text-sm text-green-700">{incident.resolution_description}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
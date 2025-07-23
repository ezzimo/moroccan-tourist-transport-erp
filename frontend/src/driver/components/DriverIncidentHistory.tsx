import React from 'react';
import { AlertTriangle, Clock, CheckCircle, User } from 'lucide-react';
import { useDriverIncidents } from '../hooks/useIncidents';
import LoadingSpinner from '../../components/LoadingSpinner';

interface DriverIncidentHistoryProps {
  driverId: string;
}

export default function DriverIncidentHistory({ driverId }: DriverIncidentHistoryProps) {
  const { data: incidentsData, isLoading } = useDriverIncidents(driverId);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const incidents = incidentsData?.items || [];

  const getSeverityColor = (severity: string) => {
    const colors = {
      Minor: 'text-green-600 bg-green-100',
      Moderate: 'text-yellow-600 bg-yellow-100',
      Major: 'text-orange-600 bg-orange-100',
      Critical: 'text-red-600 bg-red-100',
    };
    return colors[severity as keyof typeof colors] || colors.Minor;
  };

  const getStatusColor = (status: string) => {
    const colors = {
      Reported: 'text-blue-600 bg-blue-100',
      'Under Investigation': 'text-yellow-600 bg-yellow-100',
      Resolved: 'text-green-600 bg-green-100',
      Closed: 'text-gray-600 bg-gray-100',
      Escalated: 'text-red-600 bg-red-100',
    };
    return colors[status as keyof typeof colors] || colors.Reported;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Resolved':
      case 'Closed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'Under Investigation':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'Escalated':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-blue-500" />;
    }
  };

  const getIncidentTypeColor = (type: string) => {
    const colors = {
      Accident: 'text-red-600 bg-red-100',
      Complaint: 'text-yellow-600 bg-yellow-100',
      Delay: 'text-blue-600 bg-blue-100',
      Misconduct: 'text-purple-600 bg-purple-100',
      'Vehicle Breakdown': 'text-orange-600 bg-orange-100',
      'Customer Dispute': 'text-pink-600 bg-pink-100',
      'Safety Violation': 'text-red-600 bg-red-100',
      'Policy Violation': 'text-gray-600 bg-gray-100',
      'Medical Emergency': 'text-red-600 bg-red-100',
      Other: 'text-gray-600 bg-gray-100',
    };
    return colors[type as keyof typeof colors] || colors.Other;
  };

  if (incidents.length === 0) {
    return (
      <div className="text-center py-8">
        <CheckCircle className="h-16 w-16 text-green-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Incidents Reported</h3>
        <p className="text-gray-600">This driver has a clean record with no incidents.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Incident History</h3>
      
      <div className="space-y-4">
        {incidents.map((incident) => (
          <div key={incident.id} className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                {getStatusIcon(incident.status)}
                <div>
                  <h4 className="font-medium text-gray-900">{incident.title}</h4>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getIncidentTypeColor(incident.incident_type)}`}>
                      {incident.incident_type}
                    </span>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getSeverityColor(incident.severity)}`}>
                      {incident.severity}
                    </span>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(incident.status)}`}>
                      {incident.status}
                    </span>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">
                  {new Date(incident.incident_date).toLocaleDateString()}
                </p>
                {incident.requires_immediate_attention && (
                  <span className="inline-flex items-center px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full mt-1">
                    <AlertTriangle className="h-3 w-3 mr-1" />
                    Urgent
                  </span>
                )}
              </div>
            </div>

            <p className="text-sm text-gray-700 mb-3">{incident.description}</p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              {incident.location && (
                <div>
                  <p className="font-medium text-gray-700">Location:</p>
                  <p className="text-gray-600">{incident.location}</p>
                </div>
              )}
              <div>
                <p className="font-medium text-gray-700">Reported:</p>
                <p className="text-gray-600">
                  {new Date(incident.reported_at).toLocaleDateString()}
                </p>
              </div>
            </div>

            {incident.customer_involved && (
              <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                <p className="text-sm font-medium text-blue-800 mb-1">Customer Involved:</p>
                {incident.customer_name && (
                  <p className="text-sm text-blue-700">Name: {incident.customer_name}</p>
                )}
                {incident.customer_contact && (
                  <p className="text-sm text-blue-700">Contact: {incident.customer_contact}</p>
                )}
              </div>
            )}

            {incident.witness_names && (
              <div className="mt-3">
                <p className="text-sm font-medium text-gray-700 mb-1">Witnesses:</p>
                <p className="text-sm text-gray-600">{incident.witness_names}</p>
              </div>
            )}

            {incident.estimated_cost && (
              <div className="mt-3 p-3 bg-yellow-50 rounded-lg">
                <p className="text-sm font-medium text-yellow-800">
                  Estimated Cost: {incident.estimated_cost.toLocaleString()} MAD
                  {incident.actual_cost && (
                    <span className="ml-2">
                      • Actual: {incident.actual_cost.toLocaleString()} MAD
                    </span>
                  )}
                </p>
              </div>
            )}

            {incident.resolution_description && (
              <div className="mt-3 p-3 bg-green-50 rounded-lg">
                <p className="text-sm font-medium text-green-800 mb-1">Resolution:</p>
                <p className="text-sm text-green-700">{incident.resolution_description}</p>
                {incident.resolved_at && (
                  <p className="text-xs text-green-600 mt-1">
                    Resolved on {new Date(incident.resolved_at).toLocaleDateString()}
                  </p>
                )}
              </div>
            )}

            {incident.corrective_action && (
              <div className="mt-3">
                <p className="text-sm font-medium text-gray-700 mb-1">Corrective Action:</p>
                <p className="text-sm text-gray-600">{incident.corrective_action}</p>
              </div>
            )}

            {incident.preventive_measures && (
              <div className="mt-3">
                <p className="text-sm font-medium text-gray-700 mb-1">Preventive Measures:</p>
                <p className="text-sm text-gray-600">{incident.preventive_measures}</p>
              </div>
            )}

            <div className="mt-3 pt-3 border-t border-gray-200 flex items-center justify-between text-xs text-gray-500">
              <span>Age: {incident.age_days} days</span>
              {incident.police_report_filed && (
                <span className="flex items-center gap-1">
                  <User className="h-3 w-3" />
                  Police Report Filed
                  {incident.police_report_number && (
                    <span className="ml-1">#{incident.police_report_number}</span>
                  )}
                </span>
              )}
              {incident.insurance_claim && (
                <span>Insurance Claim Filed</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
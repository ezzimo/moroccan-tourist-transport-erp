import React from 'react';
import { MapPin, Calendar, Star, Clock } from 'lucide-react';
import { useDriverAssignmentsByDriver } from '../hooks/useAssignments';
import LoadingSpinner from '../../components/LoadingSpinner';

interface DriverAssignmentHistoryProps {
  driverId: string;
}

export default function DriverAssignmentHistory({ driverId }: DriverAssignmentHistoryProps) {
  const { data: assignmentsData, isLoading } = useDriverAssignmentsByDriver(driverId);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const assignments = assignmentsData?.items || [];

  const getStatusColor = (status: string) => {
    const colors = {
      Assigned: 'text-blue-600 bg-blue-100',
      Confirmed: 'text-green-600 bg-green-100',
      'In Progress': 'text-yellow-600 bg-yellow-100',
      Completed: 'text-gray-600 bg-gray-100',
      Cancelled: 'text-red-600 bg-red-100',
      'No Show': 'text-red-600 bg-red-100',
    };
    return colors[status as keyof typeof colors] || colors.Assigned;
  };

  if (assignments.length === 0) {
    return (
      <div className="text-center py-8">
        <MapPin className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Assignments</h3>
        <p className="text-gray-600">Assignment history will appear here once created.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Assignment History</h3>
      
      <div className="space-y-4">
        {assignments.map((assignment) => (
          <div key={assignment.id} className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <MapPin className="h-5 w-5 text-orange-600" />
                <div>
                  <h4 className="font-medium text-gray-900">
                    {assignment.tour_title || 'Tour Assignment'}
                  </h4>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(assignment.status)}`}>
                      {assignment.status}
                    </span>
                    <span className="text-sm text-gray-500">
                      {new Date(assignment.start_date).toLocaleDateString()} - {new Date(assignment.end_date).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
              <div className="text-right">
                {assignment.customer_rating && (
                  <div className="flex items-center gap-1">
                    <Star className="h-4 w-4 text-yellow-400 fill-current" />
                    <span className="text-sm font-medium">{assignment.customer_rating.toFixed(1)}</span>
                  </div>
                )}
                {assignment.duration_days > 0 && (
                  <p className="text-xs text-gray-500">
                    {assignment.duration_days} day{assignment.duration_days > 1 ? 's' : ''}
                  </p>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              {assignment.pickup_location && (
                <div>
                  <p className="font-medium text-gray-700">Pickup:</p>
                  <p className="text-gray-600">{assignment.pickup_location}</p>
                </div>
              )}
              {assignment.dropoff_location && (
                <div>
                  <p className="font-medium text-gray-700">Dropoff:</p>
                  <p className="text-gray-600">{assignment.dropoff_location}</p>
                </div>
              )}
            </div>

            {assignment.estimated_duration_hours && (
              <div className="mt-3 flex items-center gap-2 text-sm text-gray-600">
                <Clock className="h-4 w-4" />
                <span>Estimated duration: {assignment.estimated_duration_hours}h</span>
                {assignment.actual_duration_hours && (
                  <span className="ml-2">
                    • Actual: {assignment.actual_duration_hours.toFixed(1)}h
                  </span>
                )}
              </div>
            )}

            {assignment.customer_feedback && (
              <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                <p className="text-sm font-medium text-blue-800 mb-1">Customer Feedback:</p>
                <p className="text-sm text-blue-700">{assignment.customer_feedback}</p>
              </div>
            )}

            {assignment.special_instructions && (
              <div className="mt-3">
                <p className="text-sm font-medium text-gray-700 mb-1">Special Instructions:</p>
                <p className="text-sm text-gray-600">{assignment.special_instructions}</p>
              </div>
            )}

            {assignment.notes && (
              <div className="mt-3">
                <p className="text-sm font-medium text-gray-700 mb-1">Notes:</p>
                <p className="text-sm text-gray-600">{assignment.notes}</p>
              </div>
            )}

            <div className="mt-3 pt-3 border-t border-gray-200 text-xs text-gray-500">
              <div className="flex items-center justify-between">
                <span>Assigned: {new Date(assignment.assigned_at).toLocaleDateString()}</span>
                {assignment.completed_at && (
                  <span>Completed: {new Date(assignment.completed_at).toLocaleDateString()}</span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
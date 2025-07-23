import React from 'react';
import { Award, Calendar, CheckCircle, Clock, X } from 'lucide-react';
import { useDriverTraining } from '../hooks/useTraining';
import LoadingSpinner from '../../components/LoadingSpinner';

interface DriverTrainingHistoryProps {
  driverId: string;
}

export default function DriverTrainingHistory({ driverId }: DriverTrainingHistoryProps) {
  const { data: trainingData, isLoading } = useDriverTraining(driverId);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const training = trainingData?.items || [];

  const getStatusColor = (status: string) => {
    const colors = {
      Scheduled: 'text-blue-600 bg-blue-100',
      'In Progress': 'text-yellow-600 bg-yellow-100',
      Completed: 'text-green-600 bg-green-100',
      Failed: 'text-red-600 bg-red-100',
      Cancelled: 'text-gray-600 bg-gray-100',
    };
    return colors[status as keyof typeof colors] || colors.Scheduled;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'In Progress':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'Failed':
      case 'Cancelled':
        return <X className="h-4 w-4 text-red-500" />;
      default:
        return <Calendar className="h-4 w-4 text-blue-500" />;
    }
  };

  const getTrainingTypeColor = (type: string) => {
    const colors = {
      'First Aid': 'text-red-600 bg-red-100',
      'Defensive Driving': 'text-blue-600 bg-blue-100',
      'Customer Service': 'text-green-600 bg-green-100',
      Language: 'text-purple-600 bg-purple-100',
      'Tourism Law': 'text-yellow-600 bg-yellow-100',
      'Safety Procedures': 'text-orange-600 bg-orange-100',
    };
    return colors[type as keyof typeof colors] || colors['Customer Service'];
  };

  if (training.length === 0) {
    return (
      <div className="text-center py-8">
        <Award className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Training Records</h3>
        <p className="text-gray-600">Training history will appear here once scheduled.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Training History</h3>
      
      <div className="space-y-4">
        {training.map((record) => (
          <div key={record.id} className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                {getStatusIcon(record.status)}
                <div>
                  <h4 className="font-medium text-gray-900">{record.training_title}</h4>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTrainingTypeColor(record.training_type)}`}>
                      {record.training_type}
                    </span>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(record.status)}`}>
                      {record.status}
                    </span>
                    {record.mandatory && (
                      <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs font-medium rounded-full">
                        Mandatory
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">
                  {new Date(record.scheduled_date).toLocaleDateString()}
                </p>
                {record.score !== undefined && (
                  <p className={`text-sm font-medium ${record.has_passed ? 'text-green-600' : 'text-red-600'}`}>
                    Score: {record.score}%
                  </p>
                )}
              </div>
            </div>

            {record.description && (
              <p className="text-sm text-gray-600 mb-3">{record.description}</p>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              {record.trainer_name && (
                <div>
                  <p className="font-medium text-gray-700">Trainer:</p>
                  <p className="text-gray-600">{record.trainer_name}</p>
                </div>
              )}
              {record.training_provider && (
                <div>
                  <p className="font-medium text-gray-700">Provider:</p>
                  <p className="text-gray-600">{record.training_provider}</p>
                </div>
              )}
              {record.duration_hours && (
                <div>
                  <p className="font-medium text-gray-700">Duration:</p>
                  <p className="text-gray-600">{record.duration_hours}h</p>
                </div>
              )}
            </div>

            {record.certificate_issued && (
              <div className="mt-3 p-3 bg-green-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <Award className="h-4 w-4 text-green-600" />
                  <p className="text-sm font-medium text-green-800">
                    Certificate Issued
                    {record.certificate_number && (
                      <span className="ml-2">#{record.certificate_number}</span>
                    )}
                  </p>
                </div>
                {record.certificate_valid_until && (
                  <p className="text-sm text-green-700 mt-1">
                    Valid until: {new Date(record.certificate_valid_until).toLocaleDateString()}
                  </p>
                )}
              </div>
            )}

            {record.trainer_feedback && (
              <div className="mt-3">
                <p className="text-sm font-medium text-gray-700 mb-1">Trainer Feedback:</p>
                <p className="text-sm text-gray-600">{record.trainer_feedback}</p>
              </div>
            )}

            {record.driver_feedback && (
              <div className="mt-3">
                <p className="text-sm font-medium text-gray-700 mb-1">Driver Feedback:</p>
                <p className="text-sm text-gray-600">{record.driver_feedback}</p>
              </div>
            )}

            {record.cost && (
              <div className="mt-3 text-sm text-gray-500">
                Cost: {record.cost.toLocaleString()} {record.currency}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
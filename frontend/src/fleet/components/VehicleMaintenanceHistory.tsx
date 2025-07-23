import React from 'react';
import { Wrench, Calendar, DollarSign } from 'lucide-react';
import { useMaintenance } from '../hooks/useMaintenance';
import LoadingSpinner from '../../components/LoadingSpinner';

interface VehicleMaintenanceHistoryProps {
  vehicleId: string;
}

export default function VehicleMaintenanceHistory({ vehicleId }: VehicleMaintenanceHistoryProps) {
  const { data: maintenanceData, isLoading } = useMaintenance({ vehicle_id: vehicleId, size: 50 });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const maintenance = maintenanceData?.items || [];

  const getMaintenanceTypeColor = (type: string) => {
    const colors = {
      Preventive: 'text-green-600 bg-green-100',
      Corrective: 'text-yellow-600 bg-yellow-100',
      Emergency: 'text-red-600 bg-red-100',
      Inspection: 'text-blue-600 bg-blue-100',
      Recall: 'text-purple-600 bg-purple-100',
    };
    return colors[type as keyof typeof colors] || colors.Preventive;
  };

  if (maintenance.length === 0) {
    return (
      <div className="text-center py-8">
        <Wrench className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Maintenance Records</h3>
        <p className="text-gray-600">Maintenance history will appear here once logged.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Maintenance History</h3>
      
      <div className="space-y-4">
        {maintenance.map((record) => (
          <div key={record.id} className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <Wrench className="h-5 w-5 text-gray-400" />
                <div>
                  <h4 className="font-medium text-gray-900">{record.description}</h4>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getMaintenanceTypeColor(record.maintenance_type)}`}>
                      {record.maintenance_type}
                    </span>
                    <span className="text-sm text-gray-500">
                      {new Date(record.date_performed).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
              <div className="text-right">
                {record.cost && (
                  <p className="text-sm font-medium text-gray-900">
                    {record.cost.toLocaleString()} {record.currency}
                  </p>
                )}
                {record.odometer_reading && (
                  <p className="text-xs text-gray-500">
                    {record.odometer_reading.toLocaleString()} km
                  </p>
                )}
              </div>
            </div>

            {record.parts_replaced && (
              <div className="mb-3">
                <p className="text-sm font-medium text-gray-700 mb-1">Parts Replaced:</p>
                <p className="text-sm text-gray-600">{record.parts_replaced}</p>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              {record.provider_name && (
                <div>
                  <p className="font-medium text-gray-700">Provider:</p>
                  <p className="text-gray-600">{record.provider_name}</p>
                </div>
              )}
              {record.labor_hours && (
                <div>
                  <p className="font-medium text-gray-700">Labor Hours:</p>
                  <p className="text-gray-600">{record.labor_hours}h</p>
                </div>
              )}
              {record.warranty_until && (
                <div>
                  <p className="font-medium text-gray-700">Warranty Until:</p>
                  <p className="text-gray-600">
                    {new Date(record.warranty_until).toLocaleDateString()}
                  </p>
                </div>
              )}
            </div>

            {record.next_service_date && (
              <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-blue-600" />
                  <p className="text-sm font-medium text-blue-800">
                    Next Service: {new Date(record.next_service_date).toLocaleDateString()}
                  </p>
                  {record.next_service_odometer && (
                    <span className="text-sm text-blue-600">
                      at {record.next_service_odometer.toLocaleString()} km
                    </span>
                  )}
                </div>
              </div>
            )}

            {record.notes && (
              <div className="mt-3">
                <p className="text-sm font-medium text-gray-700 mb-1">Notes:</p>
                <p className="text-sm text-gray-600">{record.notes}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
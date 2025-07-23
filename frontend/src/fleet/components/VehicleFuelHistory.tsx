import React from 'react';
import { Fuel, TrendingUp, MapPin } from 'lucide-react';
import { useFuelLogs } from '../hooks/useFuel';
import LoadingSpinner from '../../components/LoadingSpinner';

interface VehicleFuelHistoryProps {
  vehicleId: string;
}

export default function VehicleFuelHistory({ vehicleId }: VehicleFuelHistoryProps) {
  const { data: fuelData, isLoading } = useFuelLogs({ vehicle_id: vehicleId, size: 50 });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const fuelLogs = fuelData?.items || [];

  if (fuelLogs.length === 0) {
    return (
      <div className="text-center py-8">
        <Fuel className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Fuel Records</h3>
        <p className="text-gray-600">Fuel consumption logs will appear here once recorded.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Fuel History</h3>
      
      <div className="space-y-4">
        {fuelLogs.map((log) => (
          <div key={log.id} className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <Fuel className="h-5 w-5 text-blue-600" />
                <div>
                  <h4 className="font-medium text-gray-900">
                    {log.fuel_amount}L - {log.fuel_cost.toLocaleString()} MAD
                  </h4>
                  <p className="text-sm text-gray-500">
                    {new Date(log.date).toLocaleDateString()} • {log.price_per_liter.toFixed(2)} MAD/L
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">
                  {log.odometer_reading.toLocaleString()} km
                </p>
                {log.fuel_efficiency && (
                  <div className="flex items-center gap-1 text-sm text-green-600">
                    <TrendingUp className="h-3 w-3" />
                    <span>{log.fuel_efficiency.toFixed(1)} km/L</span>
                  </div>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              {log.station_name && (
                <div>
                  <p className="font-medium text-gray-700">Station:</p>
                  <p className="text-gray-600">{log.station_name}</p>
                </div>
              )}
              {log.location && (
                <div className="flex items-center gap-1">
                  <MapPin className="h-3 w-3 text-gray-400" />
                  <p className="text-gray-600">{log.location}</p>
                </div>
              )}
              {log.trip_purpose && (
                <div>
                  <p className="font-medium text-gray-700">Purpose:</p>
                  <p className="text-gray-600">{log.trip_purpose}</p>
                </div>
              )}
            </div>

            {log.distance_since_last_fill && (
              <div className="mt-3 p-3 bg-green-50 rounded-lg">
                <p className="text-sm text-green-800">
                  Distance since last fill: {log.distance_since_last_fill.toLocaleString()} km
                  {log.cost_per_km && (
                    <span className="ml-2">
                      • Cost per km: {log.cost_per_km.toFixed(2)} MAD
                    </span>
                  )}
                </p>
              </div>
            )}

            {log.notes && (
              <div className="mt-3">
                <p className="text-sm font-medium text-gray-700 mb-1">Notes:</p>
                <p className="text-sm text-gray-600">{log.notes}</p>
              </div>
            )}

            {log.receipt_number && (
              <div className="mt-2">
                <p className="text-xs text-gray-500">Receipt: {log.receipt_number}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
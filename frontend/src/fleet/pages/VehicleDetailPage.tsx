import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Truck, Fuel, Wrench, FileText, Calendar, AlertTriangle } from 'lucide-react';
import { useVehicle } from '../hooks/useVehicles';
import { useMaintenance } from '../hooks/useMaintenance';
import { useFuelLogs } from '../hooks/useFuel';
import LoadingSpinner from '../../components/LoadingSpinner';
import VehicleMaintenanceHistory from '../components/VehicleMaintenanceHistory';
import VehicleFuelHistory from '../components/VehicleFuelHistory';
import VehicleDocuments from '../components/VehicleDocuments';
import VehicleComplianceStatus from '../components/VehicleComplianceStatus';

export default function VehicleDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState<'overview' | 'maintenance' | 'fuel' | 'documents'>('overview');

  const { data: vehicle, isLoading: vehicleLoading } = useVehicle(id!);
  const { data: maintenanceData } = useMaintenance({ vehicle_id: id, size: 10 });
  const { data: fuelData } = useFuelLogs({ vehicle_id: id, size: 10 });

  if (vehicleLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!vehicle) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Vehicle not found</p>
        <Link to="/fleet" className="text-orange-600 hover:text-orange-700 mt-2 inline-block">
          Back to Fleet
        </Link>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    const colors = {
      Available: 'bg-green-100 text-green-800',
      'In Use': 'bg-blue-100 text-blue-800',
      'Under Maintenance': 'bg-yellow-100 text-yellow-800',
      'Out of Service': 'bg-red-100 text-red-800',
      Retired: 'bg-gray-100 text-gray-800',
    };
    return colors[status as keyof typeof colors] || colors.Available;
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Truck },
    { id: 'maintenance', label: 'Maintenance', icon: Wrench },
    { id: 'fuel', label: 'Fuel Logs', icon: Fuel },
    { id: 'documents', label: 'Documents', icon: FileText },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link
          to="/fleet"
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {vehicle.display_name}
          </h1>
          <p className="text-gray-600">{vehicle.license_plate}</p>
        </div>
      </div>

      {/* Vehicle Header Card */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex flex-col lg:flex-row gap-6">
          <div className="flex-1 space-y-4">
            <div className="flex items-center gap-4">
              <Truck className="h-12 w-12 text-orange-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">
                  {vehicle.brand} {vehicle.model} ({vehicle.year})
                </h2>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(vehicle.status)}`}>
                    {vehicle.status}
                  </span>
                  <span className="text-sm text-gray-500">{vehicle.vehicle_type}</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Seating Capacity:</span> {vehicle.seating_capacity}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Fuel Type:</span> {vehicle.fuel_type}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Transmission:</span> {vehicle.transmission || 'N/A'}
                </p>
              </div>
              <div className="space-y-2">
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Current Odometer:</span> {vehicle.current_odometer.toLocaleString()} km
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Age:</span> {vehicle.age_years} years
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">VIN:</span> {vehicle.vin_number || 'N/A'}
                </p>
              </div>
            </div>

            {vehicle.notes && (
              <div>
                <p className="text-sm font-medium text-gray-700 mb-1">Notes</p>
                <p className="text-sm text-gray-600">{vehicle.notes}</p>
              </div>
            )}
          </div>

          {/* Compliance Status */}
          <div className="lg:w-80">
            <VehicleComplianceStatus vehicle={vehicle} />
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-orange-500 text-orange-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-5 w-5 mr-2" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-lg border p-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Vehicle Details</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Purchase Date:</span>
                    <span className="font-medium">
                      {vehicle.purchase_date ? new Date(vehicle.purchase_date).toLocaleDateString() : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Purchase Price:</span>
                    <span className="font-medium">
                      {vehicle.purchase_price ? `${vehicle.purchase_price.toLocaleString()} MAD` : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Engine Size:</span>
                    <span className="font-medium">{vehicle.engine_size ? `${vehicle.engine_size}L` : 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Color:</span>
                    <span className="font-medium">{vehicle.color || 'N/A'}</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
                <div className="space-y-3">
                  {maintenanceData?.items?.slice(0, 3).map((maintenance) => (
                    <div key={maintenance.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                      <Wrench className="h-5 w-5 text-gray-400" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">{maintenance.description}</p>
                        <p className="text-xs text-gray-500">
                          {new Date(maintenance.date_performed).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  ))}
                  {fuelData?.items?.slice(0, 2).map((fuel) => (
                    <div key={fuel.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                      <Fuel className="h-5 w-5 text-gray-400" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">
                          Fuel: {fuel.fuel_amount}L - {fuel.fuel_cost} MAD
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(fuel.date).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'maintenance' && (
          <VehicleMaintenanceHistory vehicleId={id!} />
        )}

        {activeTab === 'fuel' && (
          <VehicleFuelHistory vehicleId={id!} />
        )}

        {activeTab === 'documents' && (
          <VehicleDocuments vehicleId={id!} />
        )}
      </div>
    </div>
  );
}
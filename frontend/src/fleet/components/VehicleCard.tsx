import React from 'react';
import { Link } from 'react-router-dom';
import { Truck, Users, Fuel, Calendar, AlertTriangle } from 'lucide-react';
import { Vehicle } from '../types/vehicle';

interface VehicleCardProps {
  vehicle: Vehicle;
}

export default function VehicleCard({ vehicle }: VehicleCardProps) {
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

  const hasComplianceIssues = () => {
    return (
      vehicle.compliance_status.registration.needs_attention ||
      vehicle.compliance_status.insurance.needs_attention ||
      vehicle.compliance_status.inspection.needs_attention
    );
  };

  return (
    <Link
      to={`/fleet/vehicles/${vehicle.id}`}
      className="block bg-white border rounded-lg p-4 hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <Truck className="h-10 w-10 text-orange-600" />
          <div>
            <h3 className="font-medium text-gray-900">
              {vehicle.display_name}
            </h3>
            <p className="text-sm text-gray-500">{vehicle.license_plate}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(vehicle.status)}`}>
            {vehicle.status}
          </span>
          {hasComplianceIssues() && (
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Users className="h-4 w-4" />
          <span>{vehicle.seating_capacity} seats</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Fuel className="h-4 w-4" />
          <span>{vehicle.fuel_type}</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Calendar className="h-4 w-4" />
          <span>{vehicle.year}</span>
        </div>
        <div className="text-sm text-gray-600">
          {vehicle.current_odometer.toLocaleString()} km
        </div>
      </div>

      {/* Compliance Status */}
      <div className="flex items-center gap-4 text-xs">
        <div className={`flex items-center gap-1 ${
          vehicle.compliance_status.registration.is_expired ? 'text-red-600' : 
          vehicle.compliance_status.registration.needs_attention ? 'text-yellow-600' : 'text-green-600'
        }`}>
          <span>Registration: {vehicle.compliance_status.registration.days_until_expiry}d</span>
        </div>
        <div className={`flex items-center gap-1 ${
          vehicle.compliance_status.insurance.is_expired ? 'text-red-600' : 
          vehicle.compliance_status.insurance.needs_attention ? 'text-yellow-600' : 'text-green-600'
        }`}>
          <span>Insurance: {vehicle.compliance_status.insurance.days_until_expiry}d</span>
        </div>
        <div className={`flex items-center gap-1 ${
          vehicle.compliance_status.inspection.is_expired ? 'text-red-600' : 
          vehicle.compliance_status.inspection.needs_attention ? 'text-yellow-600' : 'text-green-600'
        }`}>
          <span>Inspection: {vehicle.compliance_status.inspection.days_until_expiry}d</span>
        </div>
      </div>
    </Link>
  );
}
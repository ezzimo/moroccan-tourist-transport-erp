import React from 'react';
import { Link } from 'react-router-dom';
import { User, Phone, Mail, Calendar, Award, AlertTriangle } from 'lucide-react';
import { Driver } from '../types/driver';

interface DriverCardProps {
  driver: Driver;
}

export default function DriverCard({ driver }: DriverCardProps) {
  const getStatusColor = (status: string) => {
    const colors = {
      Active: 'bg-green-100 text-green-800',
      'On Leave': 'bg-yellow-100 text-yellow-800',
      'In Training': 'bg-blue-100 text-blue-800',
      Suspended: 'bg-red-100 text-red-800',
      Terminated: 'bg-gray-100 text-gray-800',
      Retired: 'bg-gray-100 text-gray-800',
    };
    return colors[status as keyof typeof colors] || colors.Active;
  };

  const hasComplianceIssues = () => {
    return driver.is_license_expired || 
           driver.is_health_cert_expired ||
           (driver.days_until_license_expiry && driver.days_until_license_expiry <= 30) ||
           (driver.days_until_health_cert_expiry && driver.days_until_health_cert_expiry <= 30);
  };

  return (
    <Link
      to={`/drivers/${driver.id}`}
      className="block bg-white border rounded-lg p-4 hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <User className="h-10 w-10 text-orange-600" />
          <div>
            <h3 className="font-medium text-gray-900">
              {driver.full_name}
            </h3>
            <p className="text-sm text-gray-500">{driver.license_number}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(driver.status)}`}>
            {driver.status}
          </span>
          {hasComplianceIssues() && (
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
          )}
          {driver.is_available_for_assignment && (
            <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
              Available
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-3">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Phone className="h-4 w-4" />
          <span>{driver.phone}</span>
        </div>
        {driver.email && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Mail className="h-4 w-4" />
            <span className="truncate">{driver.email}</span>
          </div>
        )}
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Calendar className="h-4 w-4" />
          <span>{driver.license_type}</span>
        </div>
        <div className="text-sm text-gray-600">
          {driver.years_of_service.toFixed(1)} years experience
        </div>
      </div>

      {/* Certifications */}
      <div className="flex items-center gap-2 mb-3">
        {driver.tour_guide_certified && (
          <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
            <Award className="h-3 w-3 mr-1" />
            Tour Guide
          </span>
        )}
        {driver.first_aid_certified && (
          <span className="inline-flex items-center px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">
            <Award className="h-3 w-3 mr-1" />
            First Aid
          </span>
        )}
      </div>

      {/* Languages */}
      {driver.languages_spoken.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {driver.languages_spoken.slice(0, 3).map((language) => (
            <span
              key={language}
              className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
            >
              {language}
            </span>
          ))}
          {driver.languages_spoken.length > 3 && (
            <span className="text-xs text-gray-500">+{driver.languages_spoken.length - 3} more</span>
          )}
        </div>
      )}

      {/* Performance Stats */}
      <div className="flex items-center justify-between mt-3 pt-3 border-t text-xs text-gray-500">
        <span>Tours: {driver.total_tours_completed}</span>
        <span>Rating: {driver.performance_rating ? `${driver.performance_rating.toFixed(1)}/5` : 'N/A'}</span>
        <span>Incidents: {driver.total_incidents}</span>
      </div>
    </Link>
  );
}
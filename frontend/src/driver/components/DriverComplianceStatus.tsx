import React from 'react';
import { AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { Driver } from '../types/driver';

interface DriverComplianceStatusProps {
  driver: Driver;
}

export default function DriverComplianceStatus({ driver }: DriverComplianceStatusProps) {
  const getComplianceIcon = (isExpired: boolean, needsAttention: boolean) => {
    if (isExpired) return <AlertTriangle className="h-4 w-4 text-red-500" />;
    if (needsAttention) return <Clock className="h-4 w-4 text-yellow-500" />;
    return <CheckCircle className="h-4 w-4 text-green-500" />;
  };

  const getComplianceColor = (isExpired: boolean, needsAttention: boolean) => {
    if (isExpired) return 'text-red-600';
    if (needsAttention) return 'text-yellow-600';
    return 'text-green-600';
  };

  const licenseNeedsAttention = driver.days_until_license_expiry !== undefined && driver.days_until_license_expiry <= 30;
  const healthCertNeedsAttention = driver.days_until_health_cert_expiry !== undefined && driver.days_until_health_cert_expiry <= 30;

  const complianceItems = [
    {
      label: 'Driving License',
      isExpired: driver.is_license_expired,
      needsAttention: licenseNeedsAttention,
      expiryDate: driver.license_expiry_date,
      daysUntilExpiry: driver.days_until_license_expiry,
    },
    {
      label: 'Health Certificate',
      isExpired: driver.is_health_cert_expired,
      needsAttention: healthCertNeedsAttention,
      expiryDate: driver.health_certificate_expiry,
      daysUntilExpiry: driver.days_until_health_cert_expiry,
    },
  ];

  return (
    <div>
      <h3 className="text-lg font-medium text-gray-900 mb-4">Compliance Status</h3>
      <div className="space-y-3">
        {complianceItems.map(({ label, isExpired, needsAttention, expiryDate, daysUntilExpiry }) => (
          <div key={label} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-2">
              {getComplianceIcon(isExpired, needsAttention)}
              <span className="text-sm font-medium text-gray-900">{label}</span>
            </div>
            <div className="text-right">
              {expiryDate && (
                <p className="text-xs text-gray-500">
                  Expires: {new Date(expiryDate).toLocaleDateString()}
                </p>
              )}
              <p className={`text-sm font-medium ${getComplianceColor(isExpired, needsAttention)}`}>
                {isExpired 
                  ? 'Expired' 
                  : needsAttention && daysUntilExpiry !== undefined
                    ? `${daysUntilExpiry} days left`
                    : expiryDate ? 'Valid' : 'N/A'
                }
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Performance Summary */}
      <div className="mt-6">
        <h4 className="text-md font-medium text-gray-900 mb-3">Performance Summary</h4>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-blue-50 p-3 rounded-lg">
            <p className="text-sm font-medium text-blue-600">Tours Completed</p>
            <p className="text-xl font-bold text-blue-900">{driver.total_tours_completed}</p>
          </div>
          <div className="bg-green-50 p-3 rounded-lg">
            <p className="text-sm font-medium text-green-600">Rating</p>
            <p className="text-xl font-bold text-green-900">
              {driver.performance_rating ? `${driver.performance_rating.toFixed(1)}/5` : 'N/A'}
            </p>
          </div>
          <div className="bg-orange-50 p-3 rounded-lg">
            <p className="text-sm font-medium text-orange-600">Experience</p>
            <p className="text-xl font-bold text-orange-900">{driver.years_of_service.toFixed(1)}y</p>
          </div>
          <div className="bg-red-50 p-3 rounded-lg">
            <p className="text-sm font-medium text-red-600">Incidents</p>
            <p className="text-xl font-bold text-red-900">{driver.total_incidents}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
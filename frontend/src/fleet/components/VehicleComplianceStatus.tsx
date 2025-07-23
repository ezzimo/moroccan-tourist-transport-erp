import React from 'react';
import { AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { Vehicle } from '../types/vehicle';

interface VehicleComplianceStatusProps {
  vehicle: Vehicle;
}

export default function VehicleComplianceStatus({ vehicle }: VehicleComplianceStatusProps) {
  const getComplianceIcon = (item: any) => {
    if (item.is_expired) return <AlertTriangle className="h-4 w-4 text-red-500" />;
    if (item.needs_attention) return <Clock className="h-4 w-4 text-yellow-500" />;
    return <CheckCircle className="h-4 w-4 text-green-500" />;
  };

  const getComplianceColor = (item: any) => {
    if (item.is_expired) return 'text-red-600';
    if (item.needs_attention) return 'text-yellow-600';
    return 'text-green-600';
  };

  const complianceItems = [
    {
      label: 'Registration',
      item: vehicle.compliance_status.registration,
    },
    {
      label: 'Insurance',
      item: vehicle.compliance_status.insurance,
    },
    {
      label: 'Inspection',
      item: vehicle.compliance_status.inspection,
    },
  ];

  return (
    <div>
      <h3 className="text-lg font-medium text-gray-900 mb-4">Compliance Status</h3>
      <div className="space-y-3">
        {complianceItems.map(({ label, item }) => (
          <div key={label} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-2">
              {getComplianceIcon(item)}
              <span className="text-sm font-medium text-gray-900">{label}</span>
            </div>
            <div className="text-right">
              {item.expiry_date && (
                <p className="text-xs text-gray-500">
                  Expires: {new Date(item.expiry_date).toLocaleDateString()}
                </p>
              )}
              <p className={`text-sm font-medium ${getComplianceColor(item)}`}>
                {item.is_expired 
                  ? 'Expired' 
                  : item.needs_attention 
                    ? `${item.days_until_expiry} days left`
                    : 'Valid'
                }
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
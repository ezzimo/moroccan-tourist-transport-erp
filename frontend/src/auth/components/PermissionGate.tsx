import React from 'react';
import { useAuth } from '../context/AuthContext';


interface PermissionGateProps {
  service: string;
  action: string;
  resource?: string;
  fallback?: React.ReactNode;
  children: React.ReactNode;
}

const PermissionGate: React.FC<PermissionGateProps> = ({
  service,
  action,
  resource = 'all',
  fallback = null,
  children
}) => {
  const { hasPermission } = useAuth();

  const allowed = hasPermission(service, action, resource);

  if (!allowed) {
    console.warn(`🚫 [PermissionGate] Access denied for ${service}:${action}:${resource}`);
    return <>{fallback}</>;
  }

  console.info(`✅ [PermissionGate] Access granted for ${service}:${action}:${resource}`);
  return <>{children}</>;
};

export default PermissionGate;

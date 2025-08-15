/**
 * Service configuration for different environments
 * This file manages the base URLs for all microservices
 */

export interface ServiceConfig {
  auth: string;
  crm: string;
  booking: string;
  driver: string;
  fleet: string;
  financial: string;
  hr: string;
  inventory: string;
  notification: string;
  qa: string;
  tour: string;
}

// Development configuration (used with Vite proxy)
const developmentConfig: ServiceConfig = {
  auth: '/api/v1',      // Proxied to localhost:8000
  crm: '/api/v1',       // Proxied to localhost:8001
  booking: '/api/v1',   // Proxied to localhost:8002
  driver: '/api/v1',    // Proxied to localhost:8003
  fleet: '/api/v1',     // Proxied to localhost:8004
  financial: '/api/v1', // Proxied to localhost:8005
  hr: '/api/v1',        // Proxied to localhost:8006
  inventory: '/api/v1', // Proxied to localhost:8007
  notification: '/api/v1', // Proxied to localhost:8008
  qa: '/api/v1',        // Proxied to localhost:8009
  tour: '/api/v1',      // Proxied to localhost:8010
};

// Production configuration (direct service URLs)
const productionConfig: ServiceConfig = {
  auth: 'https://auth.yourdomain.com/api/v1',
  crm: 'https://crm.yourdomain.com/api/v1',
  booking: 'https://booking.yourdomain.com/api/v1',
  driver: 'https://driver.yourdomain.com/api/v1',
  fleet: 'https://fleet.yourdomain.com/api/v1',
  financial: 'https://financial.yourdomain.com/api/v1',
  hr: 'https://hr.yourdomain.com/api/v1',
  inventory: 'https://inventory.yourdomain.com/api/v1',
  notification: 'https://notification.yourdomain.com/api/v1',
  qa: 'https://qa.yourdomain.com/api/v1',
  tour: 'https://tour.yourdomain.com/api/v1',
};

// Docker compose configuration (for container networking)
const dockerConfig: ServiceConfig = {
  auth: 'http://auth_service:8000/api/v1',
  crm: 'http://crm_service:8001/api/v1',
  booking: 'http://booking_service:8002/api/v1',
  driver: 'http://driver_service:8003/api/v1',
  fleet: 'http://fleet_service:8004/api/v1',
  financial: 'http://financial_service:8005/api/v1',
  hr: 'http://hr_service:8006/api/v1',
  inventory: 'http://inventory_service:8007/api/v1',
  notification: 'http://notification_service:8008/api/v1',
  qa: 'http://qa_service:8009/api/v1',
  tour: 'http://tour_service:8010/api/v1',
};

// Environment detection
const getEnvironment = (): 'development' | 'production' | 'docker' => {
  if (import.meta.env.VITE_ENVIRONMENT === 'docker') {
    return 'docker';
  }
  if (import.meta.env.PROD) {
    return 'production';
  }
  return 'development';
};

// Get configuration based on environment
const getServiceConfig = (): ServiceConfig => {
  const env = getEnvironment();
  
  switch (env) {
    case 'docker':
      return dockerConfig;
    case 'production':
      return productionConfig;
    default:
      return developmentConfig;
  }
};

export const serviceConfig = getServiceConfig();

// Service endpoint mappings for easy access
export const serviceEndpoints = {
  // Authentication service
  auth: {
    login: `${serviceConfig.auth}/auth/login`,
    logout: `${serviceConfig.auth}/auth/logout`,
    me: `${serviceConfig.auth}/auth/me`,
    sendOtp: `${serviceConfig.auth}/auth/send-otp`,
    verifyOtp: `${serviceConfig.auth}/auth/verify-otp`,
    users: `${serviceConfig.auth}/users`,
    roles: `${serviceConfig.auth}/roles`,
  },
  
  // CRM service
  crm: {
    customers: `${serviceConfig.crm}/customers`,
    interactions: `${serviceConfig.crm}/interactions`,
    feedback: `${serviceConfig.crm}/feedback`,
    segments: `${serviceConfig.crm}/segments`,
  },
  
  // Booking service
  booking: {
    bookings: `${serviceConfig.booking}/bookings`,
    reservations: `${serviceConfig.booking}/reservations`,
    availability: `${serviceConfig.booking}/availability`,
    pricing: `${serviceConfig.booking}/pricing`,
  },
  
  // Driver service
  driver: {
    drivers: `${serviceConfig.driver}/drivers`,
    assignments: `${serviceConfig.driver}/assignments`,
    incidents: `${serviceConfig.driver}/incidents`,
    training: `${serviceConfig.driver}/training`,
  },
  
  // Fleet service
  fleet: {
    vehicles: `${serviceConfig.fleet}/vehicles`,
    maintenance: `${serviceConfig.fleet}/maintenance`,
    fleet: `${serviceConfig.fleet}/fleet`,
  },
  
  // Financial service
  financial: {
    invoices: `${serviceConfig.financial}/invoices`,
    payments: `${serviceConfig.financial}/payments`,
    expenses: `${serviceConfig.financial}/expenses`,
    analytics: `${serviceConfig.financial}/analytics`,
  },
  
  // HR service
  hr: {
    employees: `${serviceConfig.hr}/employees`,
    schedules: `${serviceConfig.hr}/schedules`,
    payroll: `${serviceConfig.hr}/payroll`,
  },
  
  // Inventory service
  inventory: {
    inventory: `${serviceConfig.inventory}/inventory`,
    parts: `${serviceConfig.inventory}/parts`,
    suppliers: `${serviceConfig.inventory}/suppliers`,
  },
  
  // Notification service
  notification: {
    notifications: `${serviceConfig.notification}/notifications`,
    templates: `${serviceConfig.notification}/templates`,
  },
  
  // QA service
  qa: {
    quality: `${serviceConfig.qa}/quality`,
    audits: `${serviceConfig.qa}/audits`,
    reports: `${serviceConfig.qa}/reports`,
  },
  
  // Tour service
  tour: {
    tours: `${serviceConfig.tour}/tours`,
    packages: `${serviceConfig.tour}/packages`,
    guides: `${serviceConfig.tour}/guides`,
  },
};

export default serviceConfig;


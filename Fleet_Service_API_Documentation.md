# Fleet Management Service API Documentation

## Service Overview

**Service Name**: Fleet Management Service  
**Purpose**: Manages vehicle inventory, maintenance, assignments, fuel consumption, and compliance for the Moroccan Tourist Transport ERP system.  
**Base Path**: `/api/v1`  
**Authentication**: JWT Bearer tokens with RBAC permissions

## Endpoint Reference

### Vehicle Management Endpoints

#### POST /vehicles/
**Purpose**: Register a new vehicle

**Authentication Requirements**: Bearer token with `fleet:create:vehicles` permission

**Request Body Schema**:
```json
{
  "license_plate": "string (unique, max 20 chars, required)",
  "vehicle_type": "string (enum: Bus, Minibus, SUV/4x4, Sedan, Van, Motorcycle, required)",
  "brand": "string (max 50 chars, required)",
  "model": "string (max 50 chars, required)",
  "year": "integer (1990-2030, required)",
  "color": "string (max 30 chars, optional)",
  "seating_capacity": "integer (1-100, required)",
  "fuel_type": "string (enum: Gasoline, Diesel, Hybrid, Electric, LPG, required)",
  "engine_size": "float (optional)",
  "transmission": "string (max 20 chars, optional)",
  "current_odometer": "integer (default: 0)",
  "registration_expiry": "date (optional)",
  "insurance_expiry": "date (optional)",
  "inspection_expiry": "date (optional)",
  "purchase_date": "date (optional)",
  "purchase_price": "float (optional)",
  "vin_number": "string (max 50 chars, optional)",
  "notes": "string (max 2000 chars, optional)"
}
```

**Request Example**:
```bash
curl -X POST "https://api.example.com/v1/vehicles/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "license_plate": "123-A-45",
    "vehicle_type": "Minibus",
    "brand": "Mercedes",
    "model": "Sprinter",
    "year": 2022,
    "color": "White",
    "seating_capacity": 16,
    "fuel_type": "Diesel",
    "engine_size": 2.1,
    "transmission": "Manual",
    "registration_expiry": "2025-06-15",
    "insurance_expiry": "2024-12-31",
    "inspection_expiry": "2024-08-30",
    "purchase_date": "2022-01-15",
    "purchase_price": 450000.00,
    "vin_number": "WDB9066351234567"
  }'
```

**Response Structure**:
```json
{
  "id": "uuid",
  "license_plate": "string",
  "vehicle_type": "string",
  "brand": "string",
  "model": "string",
  "year": "integer",
  "color": "string",
  "seating_capacity": "integer",
  "fuel_type": "string",
  "engine_size": "float",
  "transmission": "string",
  "status": "string (enum: Available, In Use, Under Maintenance, Out of Service, Retired)",
  "current_odometer": "integer",
  "registration_expiry": "date",
  "insurance_expiry": "date",
  "inspection_expiry": "date",
  "purchase_date": "date",
  "purchase_price": "float",
  "vin_number": "string",
  "notes": "string",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime",
  "display_name": "string",
  "age_years": "integer",
  "compliance_status": {
    "registration": {
      "expiry_date": "date",
      "days_until_expiry": "integer",
      "is_expired": "boolean",
      "needs_attention": "boolean"
    },
    "insurance": "object",
    "inspection": "object"
  }
}
```

**Success Status Codes**:
- `201 Created`: Vehicle registered successfully

#### GET /vehicles/
**Purpose**: Get list of vehicles with optional filters

**Authentication Requirements**: Bearer token with `fleet:read:vehicles` permission

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| page | integer | 1 | No | Page number |
| size | integer | 20 | No | Items per page |
| query | string | - | No | Search in license, brand, model |
| vehicle_type | string | - | No | Filter by vehicle type |
| status | string | - | No | Filter by vehicle status |
| fuel_type | string | - | No | Filter by fuel type |
| brand | string | - | No | Filter by brand |
| min_seating_capacity | integer | - | No | Minimum seating capacity |
| max_seating_capacity | integer | - | No | Maximum seating capacity |
| min_year | integer | - | No | Minimum year |
| max_year | integer | - | No | Maximum year |
| is_active | boolean | true | No | Filter by active status |
| available_from | date | - | No | Available from date |
| available_to | date | - | No | Available to date |

#### GET /vehicles/available
**Purpose**: Get available vehicles for a specific period

**Authentication Requirements**: Bearer token with `fleet:read:vehicles` permission

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| start_date | date | - | Yes | Start date (YYYY-MM-DD) |
| end_date | date | - | Yes | End date (YYYY-MM-DD) |
| vehicle_type | string | - | No | Filter by vehicle type |
| min_seating_capacity | integer | - | No | Minimum seating capacity |

**Response Structure**:
```json
[
  {
    "id": "uuid",
    "license_plate": "string",
    "vehicle_type": "string",
    "brand": "string",
    "model": "string",
    "seating_capacity": "integer",
    "status": "string",
    "display_name": "string"
  }
]
```

#### GET /vehicles/{vehicle_id}/availability
**Purpose**: Check vehicle availability for a specific period

**Authentication Requirements**: Bearer token with `fleet:read:vehicles` permission

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| vehicle_id | uuid | Yes | Vehicle identifier |

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| start_date | date | - | Yes | Start date (YYYY-MM-DD) |
| end_date | date | - | Yes | End date (YYYY-MM-DD) |

**Response Structure**:
```json
{
  "vehicle_id": "uuid",
  "start_date": "date",
  "end_date": "date",
  "is_available": "boolean",
  "conflicting_assignments": ["uuid"],
  "status": "string",
  "notes": "string"
}
```

### Maintenance Management Endpoints

#### POST /maintenance/
**Purpose**: Create a new maintenance record

**Authentication Requirements**: Bearer token with `fleet:create:maintenance` permission

**Request Body Schema**:
```json
{
  "vehicle_id": "uuid (required)",
  "maintenance_type": "string (enum: Preventive, Corrective, Emergency, Inspection, Recall, required)",
  "description": "string (max 2000 chars, required)",
  "date_performed": "date (required)",
  "provider_name": "string (max 255 chars, optional)",
  "provider_contact": "string (max 100 chars, optional)",
  "cost": "float (optional)",
  "currency": "string (default: MAD)",
  "odometer_reading": "integer (optional)",
  "parts_replaced": "string (max 1000 chars, optional)",
  "labor_hours": "float (optional)",
  "next_service_date": "date (optional)",
  "next_service_odometer": "integer (optional)",
  "warranty_until": "date (optional)",
  "notes": "string (max 1000 chars, optional)",
  "performed_by": "uuid (optional)",
  "approved_by": "uuid (optional)"
}
```

**Response Structure**:
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "maintenance_type": "string",
  "description": "string",
  "date_performed": "date",
  "provider_name": "string",
  "provider_contact": "string",
  "cost": "float",
  "currency": "string",
  "odometer_reading": "integer",
  "parts_replaced": "string",
  "labor_hours": "float",
  "next_service_date": "date",
  "next_service_odometer": "integer",
  "is_completed": "boolean",
  "warranty_until": "date",
  "notes": "string",
  "performed_by": "uuid",
  "approved_by": "uuid",
  "created_at": "datetime",
  "updated_at": "datetime",
  "is_under_warranty": "boolean",
  "cost_per_hour": "float"
}
```

#### GET /maintenance/upcoming
**Purpose**: Get vehicles with upcoming maintenance

**Authentication Requirements**: Bearer token with `fleet:read:maintenance` permission

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| days_ahead | integer | 30 | No | Days ahead to check |

**Response Structure**:
```json
[
  {
    "vehicle_id": "uuid",
    "license_plate": "string",
    "vehicle_display_name": "string",
    "maintenance_type": "string",
    "next_service_date": "date",
    "days_until_service": "integer",
    "last_service_description": "string",
    "next_service_odometer": "integer"
  }
]
```

### Fuel Management Endpoints

#### POST /fuel/
**Purpose**: Create a new fuel log entry

**Authentication Requirements**: Bearer token with `fleet:create:fuel` permission

**Request Body Schema**:
```json
{
  "vehicle_id": "uuid (required)",
  "date": "date (required)",
  "odometer_reading": "integer (required)",
  "fuel_amount": "float (required)",
  "fuel_cost": "float (required)",
  "price_per_liter": "float (required)",
  "station_name": "string (max 255 chars, optional)",
  "location": "string (max 255 chars, optional)",
  "trip_purpose": "string (max 100 chars, optional)",
  "driver_id": "uuid (optional)",
  "is_full_tank": "boolean (default: true)",
  "receipt_number": "string (max 50 chars, optional)",
  "notes": "string (max 500 chars, optional)",
  "created_by": "uuid (optional)"
}
```

**Response Structure**:
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "date": "date",
  "odometer_reading": "integer",
  "fuel_amount": "float",
  "fuel_cost": "float",
  "price_per_liter": "float",
  "station_name": "string",
  "location": "string",
  "trip_purpose": "string",
  "driver_id": "uuid",
  "distance_since_last_fill": "integer",
  "fuel_efficiency": "float",
  "is_full_tank": "boolean",
  "receipt_number": "string",
  "notes": "string",
  "created_at": "datetime",
  "created_by": "uuid",
  "cost_per_km": "float"
}
```

#### GET /fuel/stats
**Purpose**: Get fuel consumption statistics

**Authentication Requirements**: Bearer token with `fleet:read:fuel` permission

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| days | integer | 365 | No | Number of days for statistics |
| vehicle_id | uuid | - | No | Filter by vehicle |

**Response Structure**:
```json
{
  "total_fuel_consumed": "float",
  "total_fuel_cost": "float",
  "average_price_per_liter": "float",
  "average_fuel_efficiency": "float",
  "total_distance": "integer",
  "cost_per_km": "float",
  "by_month": {
    "2024-01": {
      "fuel_consumed": "float",
      "total_cost": "float",
      "distance": "integer"
    }
  },
  "by_vehicle_type": {
    "Minibus": {
      "fuel_consumed": "float",
      "total_cost": "float",
      "distance": "integer"
    }
  }
}
```

### Assignment Management Endpoints

#### POST /assignments/
**Purpose**: Create a new vehicle assignment

**Authentication Requirements**: Bearer token with `fleet:create:assignments` permission

**Request Body Schema**:
```json
{
  "vehicle_id": "uuid (required)",
  "tour_instance_id": "uuid (required)",
  "driver_id": "uuid (optional)",
  "start_date": "date (required)",
  "end_date": "date (required)",
  "pickup_location": "string (max 255 chars, optional)",
  "dropoff_location": "string (max 255 chars, optional)",
  "estimated_distance": "integer (optional)",
  "notes": "string (max 2000 chars, optional)",
  "special_instructions": "string (max 1000 chars, optional)",
  "assigned_by": "uuid (optional)"
}
```

**Response Structure**:
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "tour_instance_id": "uuid",
  "driver_id": "uuid",
  "status": "string (enum: Scheduled, Active, Completed, Cancelled)",
  "start_date": "date",
  "end_date": "date",
  "start_odometer": "integer",
  "end_odometer": "integer",
  "pickup_location": "string",
  "dropoff_location": "string",
  "estimated_distance": "integer",
  "notes": "string",
  "special_instructions": "string",
  "actual_start_date": "datetime",
  "actual_end_date": "datetime",
  "assigned_by": "uuid",
  "created_at": "datetime",
  "updated_at": "datetime",
  "duration_days": "integer",
  "distance_traveled": "integer",
  "is_active": "boolean"
}
```

#### POST /assignments/{assignment_id}/start
**Purpose**: Start an assignment (mark as active)

**Authentication Requirements**: Bearer token with `fleet:update:assignments` permission

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| start_odometer | integer | - | Yes | Starting odometer reading |

#### POST /assignments/{assignment_id}/complete
**Purpose**: Complete an assignment

**Authentication Requirements**: Bearer token with `fleet:update:assignments` permission

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| end_odometer | integer | - | Yes | Ending odometer reading |

### Document Management Endpoints

#### POST /documents/upload
**Purpose**: Upload a document for a vehicle

**Authentication Requirements**: Bearer token with `fleet:create:documents` permission

**Request Body**: Multipart form data
- `vehicle_id`: uuid (required)
- `document_type`: string (enum: Registration, Insurance, Inspection, Maintenance, Purchase, Other, required)
- `title`: string (required)
- `description`: string (optional)
- `issue_date`: date (optional, YYYY-MM-DD)
- `expiry_date`: date (optional, YYYY-MM-DD)
- `issuing_authority`: string (optional)
- `document_number`: string (optional)
- `file`: file (required)

**Response Structure**:
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "document_type": "string",
  "title": "string",
  "description": "string",
  "file_name": "string",
  "file_path": "string",
  "file_size": "integer",
  "mime_type": "string",
  "issue_date": "date",
  "expiry_date": "date",
  "issuing_authority": "string",
  "document_number": "string",
  "is_active": "boolean",
  "is_verified": "boolean",
  "uploaded_at": "datetime",
  "uploaded_by": "uuid",
  "is_expired": "boolean",
  "days_until_expiry": "integer",
  "needs_renewal": "boolean"
}
```

#### GET /documents/expiring
**Purpose**: Get documents expiring within specified days

**Authentication Requirements**: Bearer token with `fleet:read:documents` permission

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| days_ahead | integer | 30 | No | Days ahead to check |

## Data Models

### Vehicle Model
```json
{
  "id": "uuid",
  "license_plate": "string (unique, max 20 chars)",
  "vehicle_type": "string (enum: Bus, Minibus, SUV/4x4, Sedan, Van, Motorcycle)",
  "brand": "string (max 50 chars)",
  "model": "string (max 50 chars)",
  "year": "integer (1990-2030)",
  "color": "string (max 30 chars, optional)",
  "seating_capacity": "integer (1-100)",
  "fuel_type": "string (enum: Gasoline, Diesel, Hybrid, Electric, LPG)",
  "engine_size": "float (optional)",
  "transmission": "string (max 20 chars, optional)",
  "status": "string (enum: Available, In Use, Under Maintenance, Out of Service, Retired)",
  "current_odometer": "integer (default: 0)",
  "registration_expiry": "date (optional)",
  "insurance_expiry": "date (optional)",
  "inspection_expiry": "date (optional)",
  "purchase_date": "date (optional)",
  "purchase_price": "float (optional)",
  "vin_number": "string (max 50 chars, optional)",
  "notes": "string (max 2000 chars, optional)",
  "is_active": "boolean (default: true)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### MaintenanceRecord Model
```json
{
  "id": "uuid",
  "vehicle_id": "uuid (foreign key)",
  "maintenance_type": "string (enum: Preventive, Corrective, Emergency, Inspection, Recall)",
  "description": "string (max 2000 chars)",
  "date_performed": "date",
  "provider_name": "string (max 255 chars, optional)",
  "provider_contact": "string (max 100 chars, optional)",
  "cost": "float (optional)",
  "currency": "string (default: MAD)",
  "odometer_reading": "integer (optional)",
  "parts_replaced": "string (max 1000 chars, optional)",
  "labor_hours": "float (optional)",
  "next_service_date": "date (optional)",
  "next_service_odometer": "integer (optional)",
  "is_completed": "boolean (default: true)",
  "warranty_until": "date (optional)",
  "notes": "string (max 1000 chars, optional)",
  "performed_by": "uuid (optional)",
  "approved_by": "uuid (optional)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### FuelLog Model
```json
{
  "id": "uuid",
  "vehicle_id": "uuid (foreign key)",
  "date": "date",
  "odometer_reading": "integer",
  "fuel_amount": "float (liters)",
  "fuel_cost": "float (total cost)",
  "price_per_liter": "float",
  "station_name": "string (max 255 chars, optional)",
  "location": "string (max 255 chars, optional)",
  "trip_purpose": "string (max 100 chars, optional)",
  "driver_id": "uuid (optional)",
  "distance_since_last_fill": "integer (optional)",
  "fuel_efficiency": "float (km per liter, optional)",
  "is_full_tank": "boolean (default: true)",
  "receipt_number": "string (max 50 chars, optional)",
  "notes": "string (max 500 chars, optional)",
  "created_at": "datetime",
  "created_by": "uuid (optional)"
}
```

## Frontend Integration Guidelines

### HTTP Client Configuration
```javascript
// Fleet service client configuration
import axios from 'axios';

const fleetClient = axios.create({
  baseURL: 'https://api.example.com/v1',
  timeout: 15000, // Longer timeout for file uploads
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
fleetClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Fleet Management Implementation
```javascript
class FleetService {
  // Register vehicle
  async registerVehicle(vehicleData) {
    const response = await fleetClient.post('/vehicles/', vehicleData);
    return response.data;
  }

  // Get available vehicles
  async getAvailableVehicles(startDate, endDate, filters = {}) {
    const params = {
      start_date: startDate,
      end_date: endDate,
      ...filters
    };

    const response = await fleetClient.get('/vehicles/available', { params });
    return response.data;
  }

  // Check vehicle availability
  async checkVehicleAvailability(vehicleId, startDate, endDate) {
    const params = {
      start_date: startDate,
      end_date: endDate
    };

    const response = await fleetClient.get(`/vehicles/${vehicleId}/availability`, { params });
    return response.data;
  }

  // Get compliance alerts
  async getComplianceAlerts() {
    const response = await fleetClient.get('/vehicles/compliance-alerts');
    return response.data;
  }
}

// Maintenance management
class MaintenanceService {
  // Log maintenance
  async logMaintenance(maintenanceData) {
    const response = await fleetClient.post('/maintenance/', maintenanceData);
    return response.data;
  }

  // Get upcoming maintenance
  async getUpcomingMaintenance(daysAhead = 30) {
    const response = await fleetClient.get('/maintenance/upcoming', {
      params: { days_ahead: daysAhead }
    });
    return response.data;
  }

  // Get maintenance stats
  async getMaintenanceStats(days = 365) {
    const response = await fleetClient.get('/maintenance/stats', {
      params: { days }
    });
    return response.data;
  }
}

// Document management
class DocumentService {
  // Upload document
  async uploadDocument(vehicleId, documentData, file) {
    const formData = new FormData();
    formData.append('vehicle_id', vehicleId);
    formData.append('file', file);
    
    Object.entries(documentData).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        formData.append(key, value);
      }
    });

    const response = await fleetClient.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Get expiring documents
  async getExpiringDocuments(daysAhead = 30) {
    const response = await fleetClient.get('/documents/expiring', {
      params: { days_ahead: daysAhead }
    });
    return response.data;
  }
}
```

### Error Handling Patterns
```javascript
// Fleet-specific error handler
function handleFleetError(error) {
  if (error.response) {
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        if (data.detail?.includes('License plate already exists')) {
          return {
            type: 'duplicate_license_plate',
            message: 'A vehicle with this license plate already exists',
            field: 'license_plate'
          };
        }
        break;
      case 409:
        return {
          type: 'assignment_conflict',
          message: 'Vehicle is already assigned for this period',
          action: 'check_availability'
        };
      case 413:
        return {
          type: 'file_too_large',
          message: 'Document file is too large (max 10MB)',
          action: 'compress_file'
        };
    }
  }
  
  return handleApiError(error);
}
```

### Real-time Fleet Monitoring
```javascript
// Fleet status monitor
class FleetStatusMonitor {
  constructor() {
    this.vehicles = new Map();
    this.updateInterval = null;
  }

  // Start monitoring
  startMonitoring() {
    this.updateInterval = setInterval(async () => {
      try {
        // Get compliance alerts
        const alerts = await fleetClient.get('/vehicles/compliance-alerts');
        this.updateComplianceAlerts(alerts.data);

        // Get upcoming maintenance
        const maintenance = await fleetClient.get('/maintenance/upcoming');
        this.updateMaintenanceAlerts(maintenance.data);
      } catch (error) {
        console.error('Fleet monitoring error:', error);
      }
    }, 300000); // Update every 5 minutes
  }

  // Stop monitoring
  stopMonitoring() {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }
  }

  // Update compliance alerts
  updateComplianceAlerts(alerts) {
    window.dispatchEvent(new CustomEvent('complianceAlertsUpdate', {
      detail: alerts
    }));
  }

  // Update maintenance alerts
  updateMaintenanceAlerts(maintenance) {
    window.dispatchEvent(new CustomEvent('maintenanceAlertsUpdate', {
      detail: maintenance
    }));
  }
}
```

### Rate Limiting
- Vehicle registration: 10 per minute per user
- Document upload: 20 per minute per user
- Availability checks: 100 per minute per user
- Maintenance logging: 50 per minute per user

### CORS Policy
- Allowed origins: Frontend domains (configurable)
- Allowed methods: GET, POST, PUT, DELETE, OPTIONS
- Credentials: Supported

## Testing & Support Tools

### Sample API Calls
```javascript
// Complete fleet management example
const fleetManagementExample = async () => {
  try {
    // 1. Register vehicle
    const vehicle = await fleetClient.post('/vehicles/', {
      license_plate: '123-A-45',
      vehicle_type: 'Minibus',
      brand: 'Mercedes',
      model: 'Sprinter',
      year: 2022,
      seating_capacity: 16,
      fuel_type: 'Diesel',
      registration_expiry: '2025-06-15',
      insurance_expiry: '2024-12-31',
      inspection_expiry: '2024-08-30'
    });

    // 2. Check availability
    const availability = await fleetClient.get(`/vehicles/${vehicle.data.id}/availability`, {
      params: {
        start_date: '2024-03-15',
        end_date: '2024-03-18'
      }
    });

    // 3. Create assignment if available
    if (availability.data.is_available) {
      const assignment = await fleetClient.post('/assignments/', {
        vehicle_id: vehicle.data.id,
        tour_instance_id: 'tour-uuid',
        start_date: '2024-03-15',
        end_date: '2024-03-18',
        pickup_location: 'Marrakech',
        dropoff_location: 'Casablanca'
      });
    }

    // 4. Log fuel consumption
    const fuelLog = await fleetClient.post('/fuel/', {
      vehicle_id: vehicle.data.id,
      date: '2024-03-10',
      odometer_reading: 15000,
      fuel_amount: 60.5,
      fuel_cost: 726.00,
      price_per_liter: 12.00,
      station_name: 'Total Marrakech',
      is_full_tank: true
    });

    return { vehicle: vehicle.data, availability: availability.data, fuelLog: fuelLog.data };
  } catch (error) {
    console.error('Fleet management error:', error);
    throw error;
  }
};
```

### Mock Data Examples
```javascript
// Mock vehicle data
const mockVehicle = {
  id: "123e4567-e89b-12d3-a456-426614174000",
  license_plate: "123-A-45",
  vehicle_type: "Minibus",
  brand: "Mercedes",
  model: "Sprinter",
  year: 2022,
  color: "White",
  seating_capacity: 16,
  fuel_type: "Diesel",
  status: "Available",
  current_odometer: 15000,
  registration_expiry: "2025-06-15",
  insurance_expiry: "2024-12-31",
  inspection_expiry: "2024-08-30",
  is_active: true,
  display_name: "Mercedes Sprinter (123-A-45)",
  age_years: 2,
  compliance_status: {
    registration: {
      expiry_date: "2025-06-15",
      days_until_expiry: 365,
      is_expired: false,
      needs_attention: false
    }
  }
};

// Mock maintenance record
const mockMaintenance = {
  id: "456e7890-e89b-12d3-a456-426614174001",
  vehicle_id: "123e4567-e89b-12d3-a456-426614174000",
  maintenance_type: "Preventive",
  description: "Regular service - oil change, filters, brake check",
  date_performed: "2024-03-01",
  provider_name: "Garage Atlas",
  cost: 1200.00,
  currency: "MAD",
  odometer_reading: 14500,
  parts_replaced: "Engine oil, oil filter, air filter",
  labor_hours: 3.5,
  next_service_date: "2024-09-01",
  is_completed: true,
  is_under_warranty: true,
  cost_per_hour: 342.86
};
```

### Postman Collection Structure
```json
{
  "info": {
    "name": "Fleet Management API",
    "description": "Fleet management and vehicle operations endpoints"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "https://api.example.com/v1"
    },
    {
      "key": "vehicle_id",
      "value": "{{$guid}}"
    }
  ],
  "item": [
    {
      "name": "Vehicles",
      "item": [
        {
          "name": "Register Vehicle",
          "request": {
            "method": "POST",
            "url": "{{base_url}}/vehicles/",
            "body": {
              "mode": "raw",
              "raw": "{\n  \"license_plate\": \"123-A-45\",\n  \"vehicle_type\": \"Minibus\"\n}"
            }
          }
        },
        {
          "name": "Check Availability",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/vehicles/{{vehicle_id}}/availability?start_date=2024-03-15&end_date=2024-03-18"
          }
        }
      ]
    }
  ]
}
```

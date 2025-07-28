# Driver Management Service API Documentation

## Service Overview

**Service Name**: Driver Management Service  
**Purpose**: Manages professional driver profiles, assignments, training, incidents, and compliance for the Moroccan Tourist Transport ERP system.  
**Base Path**: `/api/v1`  
**Authentication**: JWT Bearer tokens with RBAC permissions

## Endpoint Reference

### Driver Management Endpoints

#### POST /drivers/
**Purpose**: Register a new driver

**Authentication Requirements**: Bearer token with `driver:create:drivers` permission

**Request Body Schema**:
```json
{
  "full_name": "string (required)",
  "date_of_birth": "date (YYYY-MM-DD, required)",
  "gender": "string (enum: Male, Female, required)",
  "nationality": "string (default: Moroccan)",
  "national_id": "string (unique, max 20 chars, required)",
  "phone": "string (max 20 chars, required)",
  "email": "string (email format, optional)",
  "address": "string (max 500 chars, optional)",
  "emergency_contact_name": "string (max 255 chars, optional)",
  "emergency_contact_phone": "string (max 20 chars, optional)",
  "employee_id": "string (max 20 chars, optional)",
  "employment_type": "string (enum: Permanent, Seasonal, Contract, Freelance, required)",
  "hire_date": "date (required)",
  "license_number": "string (unique, max 50 chars, required)",
  "license_type": "string (enum: Category B, Category C, Category D, Category D1, Professional, required)",
  "license_issue_date": "date (required)",
  "license_expiry_date": "date (required)",
  "license_issuing_authority": "string (max 255 chars, optional)",
  "languages_spoken": ["string (optional)"],
  "health_certificate_expiry": "date (optional)",
  "medical_restrictions": "string (max 500 chars, optional)",
  "tour_guide_certified": "boolean (default: false)",
  "first_aid_certified": "boolean (default: false)",
  "notes": "string (max 2000 chars, optional)"
}
```

**Request Example**:
```bash
curl -X POST "https://api.example.com/v1/drivers/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Mohammed Alami",
    "date_of_birth": "1985-03-15",
    "gender": "Male",
    "national_id": "AB123456",
    "phone": "+212612345678",
    "email": "mohammed.alami@example.com",
    "employment_type": "Permanent",
    "hire_date": "2024-01-15",
    "license_number": "DL789012",
    "license_type": "Category D",
    "license_issue_date": "2020-01-01",
    "license_expiry_date": "2025-01-01",
    "languages_spoken": ["Arabic", "French", "English"],
    "tour_guide_certified": true,
    "first_aid_certified": true
  }'
```

**Response Structure**:
```json
{
  "id": "uuid",
  "full_name": "string",
  "date_of_birth": "date",
  "gender": "string",
  "nationality": "string",
  "national_id": "string",
  "phone": "string",
  "email": "string",
  "address": "string",
  "emergency_contact_name": "string",
  "emergency_contact_phone": "string",
  "employee_id": "string",
  "employment_type": "string",
  "hire_date": "date",
  "license_number": "string",
  "license_type": "string",
  "license_issue_date": "date",
  "license_expiry_date": "date",
  "license_issuing_authority": "string",
  "languages_spoken": ["string"],
  "health_certificate_expiry": "date",
  "medical_restrictions": "string",
  "tour_guide_certified": "boolean",
  "first_aid_certified": "boolean",
  "status": "string (enum: Active, On Leave, In Training, Suspended, Terminated, Retired)",
  "performance_rating": "float (0-5)",
  "total_tours_completed": "integer",
  "total_incidents": "integer",
  "notes": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "age": "integer",
  "years_of_service": "float",
  "is_license_expired": "boolean",
  "days_until_license_expiry": "integer",
  "is_health_cert_expired": "boolean",
  "days_until_health_cert_expiry": "integer",
  "performance_score": "float",
  "is_available_for_assignment": "boolean"
}
```

**Success Status Codes**:
- `201 Created`: Driver registered successfully

#### GET /drivers/
**Purpose**: Get list of drivers with optional filters

**Authentication Requirements**: Bearer token with `driver:read:drivers` permission

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| page | integer | 1 | No | Page number |
| size | integer | 20 | No | Items per page |
| query | string | - | No | Search in name, license, ID |
| status | string | - | No | Filter by driver status |
| employment_type | string | - | No | Filter by employment type |
| license_type | string | - | No | Filter by license type |
| languages | array | - | No | Filter by languages spoken |
| tour_guide_certified | boolean | - | No | Filter by tour guide certification |
| first_aid_certified | boolean | - | No | Filter by first aid certification |
| available_for_assignment | boolean | - | No | Filter by availability |
| license_expiring_soon | boolean | - | No | Filter by license expiry (30 days) |

#### GET /drivers/{driver_id}
**Purpose**: Get driver by ID

**Authentication Requirements**: Bearer token with `driver:read:drivers` permission

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| driver_id | uuid | Yes | Driver identifier |

#### PUT /drivers/{driver_id}
**Purpose**: Update driver information

**Authentication Requirements**: Bearer token with `driver:update:drivers` permission

**Request Body Schema**: Same as create, but all fields optional

### Assignment Management Endpoints

#### POST /assignments/
**Purpose**: Create a new driver assignment

**Authentication Requirements**: Bearer token with `driver:create:assignments` permission

**Request Body Schema**:
```json
{
  "driver_id": "uuid (required)",
  "tour_instance_id": "uuid (required)",
  "vehicle_id": "uuid (optional)",
  "start_date": "date (required)",
  "end_date": "date (required)",
  "tour_title": "string (max 255 chars, optional)",
  "pickup_location": "string (max 255 chars, optional)",
  "dropoff_location": "string (max 255 chars, optional)",
  "estimated_duration_hours": "integer (optional)",
  "special_instructions": "string (max 1000 chars, optional)",
  "notes": "string (max 1000 chars, optional)"
}
```

**Response Structure**:
```json
{
  "id": "uuid",
  "driver_id": "uuid",
  "tour_instance_id": "uuid",
  "vehicle_id": "uuid",
  "status": "string (enum: Assigned, Confirmed, In Progress, Completed, Cancelled, No Show)",
  "start_date": "date",
  "end_date": "date",
  "tour_title": "string",
  "pickup_location": "string",
  "dropoff_location": "string",
  "estimated_duration_hours": "integer",
  "assigned_by": "uuid",
  "assigned_at": "datetime",
  "confirmed_at": "datetime",
  "started_at": "datetime",
  "completed_at": "datetime",
  "actual_start_time": "datetime",
  "actual_end_time": "datetime",
  "customer_rating": "float (0-5)",
  "customer_feedback": "string",
  "special_instructions": "string",
  "notes": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "duration_days": "integer",
  "is_active": "boolean",
  "is_overdue": "boolean",
  "actual_duration_hours": "float",
  "is_on_time": "boolean"
}
```

#### GET /assignments/
**Purpose**: Get list of assignments with optional filters

**Authentication Requirements**: Bearer token with `driver:read:assignments` permission

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| page | integer | 1 | No | Page number |
| size | integer | 20 | No | Items per page |
| driver_id | uuid | - | No | Filter by driver |
| tour_instance_id | uuid | - | No | Filter by tour |
| vehicle_id | uuid | - | No | Filter by vehicle |
| status | string | - | No | Filter by assignment status |
| start_date_from | date | - | No | Filter by start date from |
| start_date_to | date | - | No | Filter by start date to |

#### PUT /assignments/{assignment_id}
**Purpose**: Update assignment information

**Authentication Requirements**: Bearer token with `driver:update:assignments` permission

### Training Management Endpoints

#### POST /training/
**Purpose**: Create a new training record

**Authentication Requirements**: Bearer token with `driver:create:training` permission

**Request Body Schema**:
```json
{
  "driver_id": "uuid (required)",
  "training_type": "string (enum: First Aid, Defensive Driving, Customer Service, Language, Tourism Law, Safety Procedures, required)",
  "training_title": "string (max 255 chars, required)",
  "description": "string (max 1000 chars, optional)",
  "scheduled_date": "date (required)",
  "start_time": "datetime (optional)",
  "end_time": "datetime (optional)",
  "duration_hours": "float (optional)",
  "trainer_name": "string (max 255 chars, optional)",
  "training_provider": "string (max 255 chars, optional)",
  "location": "string (max 255 chars, optional)",
  "pass_score": "float (default: 70.0)",
  "cost": "float (optional)",
  "mandatory": "boolean (default: false)",
  "notes": "string (max 1000 chars, optional)"
}
```

**Response Structure**:
```json
{
  "id": "uuid",
  "driver_id": "uuid",
  "training_type": "string",
  "training_title": "string",
  "description": "string",
  "scheduled_date": "date",
  "start_time": "datetime",
  "end_time": "datetime",
  "duration_hours": "float",
  "trainer_name": "string",
  "training_provider": "string",
  "location": "string",
  "status": "string (enum: Scheduled, In Progress, Completed, Failed, Cancelled)",
  "attendance_confirmed": "boolean",
  "score": "float (0-100)",
  "pass_score": "float",
  "certificate_issued": "boolean",
  "certificate_number": "string",
  "certificate_valid_until": "date",
  "certificate_file_path": "string",
  "cost": "float",
  "currency": "string",
  "mandatory": "boolean",
  "trainer_feedback": "string",
  "driver_feedback": "string",
  "notes": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "has_passed": "boolean",
  "is_certificate_valid": "boolean",
  "days_until_certificate_expiry": "integer",
  "training_effectiveness": "string"
}
```

### Incident Management Endpoints

#### POST /incidents/
**Purpose**: Create a new incident report

**Authentication Requirements**: Bearer token with `driver:create:incidents` permission

**Request Body Schema**:
```json
{
  "driver_id": "uuid (required)",
  "assignment_id": "uuid (optional)",
  "incident_type": "string (enum: Accident, Complaint, Delay, Misconduct, Vehicle Breakdown, Customer Dispute, Safety Violation, Policy Violation, Medical Emergency, Other, required)",
  "severity": "string (enum: Minor, Moderate, Major, Critical, required)",
  "title": "string (max 255 chars, required)",
  "description": "string (max 2000 chars, required)",
  "incident_date": "date (required)",
  "incident_time": "datetime (optional)",
  "location": "string (max 255 chars, optional)",
  "reported_by": "uuid (required)",
  "witness_names": "string (max 500 chars, optional)",
  "customer_involved": "boolean (default: false)",
  "customer_name": "string (max 255 chars, optional)",
  "customer_contact": "string (max 100 chars, optional)",
  "estimated_cost": "float (optional)",
  "insurance_claim": "boolean (default: false)",
  "police_report_filed": "boolean (default: false)",
  "police_report_number": "string (max 100 chars, optional)",
  "photos_taken": "boolean (default: false)"
}
```

**Response Structure**:
```json
{
  "id": "uuid",
  "driver_id": "uuid",
  "assignment_id": "uuid",
  "incident_type": "string",
  "severity": "string",
  "title": "string",
  "description": "string",
  "incident_date": "date",
  "incident_time": "datetime",
  "location": "string",
  "reported_by": "uuid",
  "reported_at": "datetime",
  "witness_names": "string",
  "customer_involved": "boolean",
  "customer_name": "string",
  "customer_contact": "string",
  "status": "string (enum: Reported, Under Investigation, Resolved, Closed, Escalated)",
  "investigated_by": "uuid",
  "investigation_notes": "string",
  "resolution_description": "string",
  "corrective_action": "string",
  "preventive_measures": "string",
  "estimated_cost": "float",
  "actual_cost": "float",
  "insurance_claim": "boolean",
  "claim_number": "string",
  "follow_up_required": "boolean",
  "follow_up_date": "date",
  "follow_up_notes": "string",
  "police_report_filed": "boolean",
  "police_report_number": "string",
  "photos_taken": "boolean",
  "resolved_at": "datetime",
  "resolved_by": "uuid",
  "created_at": "datetime",
  "updated_at": "datetime",
  "age_days": "integer",
  "is_overdue": "boolean",
  "severity_weight": "integer",
  "requires_immediate_attention": "boolean"
}
```

### Mobile API Endpoints

#### GET /mobile/driver/{driver_id}/dashboard
**Purpose**: Get driver dashboard for mobile app

**Authentication Requirements**: Bearer token with `driver:read:mobile` permission

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| driver_id | uuid | Yes | Driver identifier |

**Response Structure**:
```json
{
  "driver": {
    "id": "uuid",
    "full_name": "string",
    "license_expiry_date": "date",
    "health_certificate_expiry": "date",
    "status": "string"
  },
  "current_assignments": [
    {
      "id": "uuid",
      "tour_title": "string",
      "start_date": "date",
      "end_date": "date",
      "status": "string",
      "pickup_location": "string",
      "special_instructions": "string"
    }
  ],
  "upcoming_assignments": ["Assignment objects"],
  "recent_training": ["Training objects"],
  "alerts": [
    {
      "type": "string",
      "message": "string",
      "priority": "string",
      "due_date": "date"
    }
  ]
}
```

#### GET /mobile/assignments/{assignment_id}/details
**Purpose**: Get detailed assignment information for mobile

**Authentication Requirements**: Bearer token with `driver:read:mobile` permission

**Response Structure**:
```json
{
  "assignment": "Assignment object",
  "tour_details": {
    "title": "string",
    "description": "string",
    "participant_count": "integer",
    "language": "string",
    "special_requirements": "string"
  },
  "vehicle_details": {
    "license_plate": "string",
    "brand": "string",
    "model": "string",
    "fuel_level": "string"
  },
  "itinerary": [
    {
      "day": "integer",
      "activities": ["Activity objects"]
    }
  ]
}
```

## Data Models

### Driver Model
```json
{
  "id": "uuid",
  "full_name": "string (max 255 chars)",
  "date_of_birth": "date",
  "gender": "string (enum: Male, Female)",
  "nationality": "string (default: Moroccan)",
  "national_id": "string (unique, max 20 chars)",
  "phone": "string (max 20 chars)",
  "email": "string (email format, optional)",
  "address": "string (max 500 chars, optional)",
  "emergency_contact_name": "string (max 255 chars, optional)",
  "emergency_contact_phone": "string (max 20 chars, optional)",
  "employee_id": "string (max 20 chars, optional)",
  "employment_type": "string (enum: Permanent, Seasonal, Contract, Freelance)",
  "hire_date": "date",
  "license_number": "string (unique, max 50 chars)",
  "license_type": "string (enum: Category B, Category C, Category D, Category D1, Professional)",
  "license_issue_date": "date",
  "license_expiry_date": "date",
  "license_issuing_authority": "string (max 255 chars, optional)",
  "languages_spoken": "array of strings (JSON, optional)",
  "tour_guide_certified": "boolean (default: false)",
  "first_aid_certified": "boolean (default: false)",
  "health_certificate_expiry": "date (optional)",
  "medical_restrictions": "string (max 500 chars, optional)",
  "status": "string (enum: Active, On Leave, In Training, Suspended, Terminated, Retired)",
  "performance_rating": "float (0-5, optional)",
  "total_tours_completed": "integer (default: 0)",
  "total_incidents": "integer (default: 0)",
  "profile_photo_path": "string (max 500 chars, optional)",
  "notes": "string (max 2000 chars, optional)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### DriverAssignment Model
```json
{
  "id": "uuid",
  "driver_id": "uuid (foreign key)",
  "tour_instance_id": "uuid (reference to tour service)",
  "vehicle_id": "uuid (optional, reference to fleet service)",
  "status": "string (enum: Assigned, Confirmed, In Progress, Completed, Cancelled, No Show)",
  "start_date": "date",
  "end_date": "date",
  "tour_title": "string (max 255 chars, optional)",
  "pickup_location": "string (max 255 chars, optional)",
  "dropoff_location": "string (max 255 chars, optional)",
  "estimated_duration_hours": "integer (optional)",
  "assigned_by": "uuid",
  "assigned_at": "datetime",
  "confirmed_at": "datetime (optional)",
  "started_at": "datetime (optional)",
  "completed_at": "datetime (optional)",
  "actual_start_time": "datetime (optional)",
  "actual_end_time": "datetime (optional)",
  "customer_rating": "float (0-5, optional)",
  "customer_feedback": "string (max 1000 chars, optional)",
  "special_instructions": "string (max 1000 chars, optional)",
  "notes": "string (max 1000 chars, optional)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Frontend Integration Guidelines

### HTTP Client Configuration
```javascript
// Driver service client configuration
import axios from 'axios';

const driverClient = axios.create({
  baseURL: 'https://api.example.com/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
driverClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Driver Management Implementation
```javascript
class DriverService {
  // Register new driver
  async registerDriver(driverData) {
    const response = await driverClient.post('/drivers/', driverData);
    return response.data;
  }

  // Get drivers with filters
  async getDrivers(filters = {}) {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        if (Array.isArray(value)) {
          value.forEach(v => params.append(key, v));
        } else {
          params.append(key, value);
        }
      }
    });

    const response = await driverClient.get(`/drivers/?${params}`);
    return response.data;
  }

  // Get available drivers for assignment
  async getAvailableDrivers(startDate, endDate, requiredSkills = []) {
    const filters = {
      available_for_assignment: true,
      start_date_from: startDate,
      start_date_to: endDate
    };

    if (requiredSkills.length > 0) {
      filters.languages = requiredSkills;
    }

    return this.getDrivers(filters);
  }

  // Update driver status
  async updateDriverStatus(driverId, status, notes = '') {
    const response = await driverClient.put(`/drivers/${driverId}`, {
      status,
      notes
    });
    return response.data;
  }
}

// Assignment management
class AssignmentService {
  // Create assignment
  async createAssignment(assignmentData) {
    const response = await driverClient.post('/assignments/', assignmentData);
    return response.data;
  }

  // Get driver assignments
  async getDriverAssignments(driverId, status = null) {
    const params = { driver_id: driverId };
    if (status) params.status = status;

    const response = await driverClient.get('/assignments/', { params });
    return response.data;
  }

  // Update assignment status
  async updateAssignmentStatus(assignmentId, status, notes = '') {
    const response = await driverClient.put(`/assignments/${assignmentId}`, {
      status,
      notes
    });
    return response.data;
  }
}

// Mobile API service
class DriverMobileService {
  // Get driver dashboard
  async getDriverDashboard(driverId) {
    const response = await driverClient.get(`/mobile/driver/${driverId}/dashboard`);
    return response.data;
  }

  // Get assignment details
  async getAssignmentDetails(assignmentId) {
    const response = await driverClient.get(`/mobile/assignments/${assignmentId}/details`);
    return response.data;
  }

  // Update assignment status from mobile
  async updateAssignmentFromMobile(assignmentId, statusUpdate) {
    const response = await driverClient.put(`/assignments/${assignmentId}`, statusUpdate);
    return response.data;
  }
}
```

### Error Handling Patterns
```javascript
// Driver-specific error handler
function handleDriverError(error) {
  if (error.response) {
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        if (data.detail?.includes('License expired')) {
          return {
            type: 'license_expired',
            message: 'Driver license has expired',
            action: 'update_license'
          };
        }
        if (data.detail?.includes('Health certificate expired')) {
          return {
            type: 'health_cert_expired',
            message: 'Health certificate has expired',
            action: 'update_certificate'
          };
        }
        break;
      case 409:
        return {
          type: 'assignment_conflict',
          message: 'Driver is already assigned for this period',
          action: 'check_availability'
        };
    }
  }
  
  return handleApiError(error);
}
```

### Real-time Driver Tracking
```javascript
// Driver status tracker
class DriverStatusTracker {
  constructor(driverId) {
    this.driverId = driverId;
    this.statusUpdateInterval = null;
  }

  // Start tracking
  startTracking() {
    this.statusUpdateInterval = setInterval(async () => {
      try {
        const dashboard = await driverClient.get(`/mobile/driver/${this.driverId}/dashboard`);
        this.updateDriverStatus(dashboard.data);
      } catch (error) {
        console.error('Status update failed:', error);
      }
    }, 30000); // Update every 30 seconds
  }

  // Stop tracking
  stopTracking() {
    if (this.statusUpdateInterval) {
      clearInterval(this.statusUpdateInterval);
      this.statusUpdateInterval = null;
    }
  }

  // Update driver status in UI
  updateDriverStatus(dashboardData) {
    // Emit event or update state
    window.dispatchEvent(new CustomEvent('driverStatusUpdate', {
      detail: dashboardData
    }));
  }
}
```

### Rate Limiting
- Driver registration: 10 per minute per user
- Assignment creation: 20 per minute per user
- Mobile dashboard: 120 per hour per driver
- Incident reporting: 5 per minute per user

### CORS Policy
- Allowed origins: Frontend and mobile app domains
- Allowed methods: GET, POST, PUT, DELETE, OPTIONS
- Credentials: Supported

## Testing & Support Tools

### Sample API Calls
```javascript
// Complete driver lifecycle example
const driverLifecycleExample = async () => {
  try {
    // 1. Register driver
    const driver = await driverClient.post('/drivers/', {
      full_name: 'Mohammed Alami',
      date_of_birth: '1985-03-15',
      gender: 'Male',
      national_id: 'AB123456',
      phone: '+212612345678',
      employment_type: 'Permanent',
      hire_date: '2024-01-15',
      license_number: 'DL789012',
      license_type: 'Category D',
      license_issue_date: '2020-01-01',
      license_expiry_date: '2025-01-01',
      languages_spoken: ['Arabic', 'French', 'English'],
      tour_guide_certified: true
    });

    // 2. Create assignment
    const assignment = await driverClient.post('/assignments/', {
      driver_id: driver.data.id,
      tour_instance_id: 'tour-uuid',
      start_date: '2024-03-15',
      end_date: '2024-03-18',
      tour_title: 'Atlas Mountains Tour',
      pickup_location: 'Marrakech Hotel',
      dropoff_location: 'Marrakech Airport'
    });

    // 3. Log training
    const training = await driverClient.post('/training/', {
      driver_id: driver.data.id,
      training_type: 'Customer Service',
      training_title: 'Excellence in Tourist Service',
      scheduled_date: '2024-02-01',
      duration_hours: 8,
      trainer_name: 'Hassan Benali',
      mandatory: true
    });

    return { driver: driver.data, assignment: assignment.data, training: training.data };
  } catch (error) {
    console.error('Driver lifecycle error:', error);
    throw error;
  }
};
```

### Mock Data Examples
```javascript
// Mock driver data
const mockDriver = {
  id: "123e4567-e89b-12d3-a456-426614174000",
  full_name: "Mohammed Alami",
  date_of_birth: "1985-03-15",
  gender: "Male",
  national_id: "AB123456",
  phone: "+212612345678",
  email: "mohammed.alami@example.com",
  employment_type: "Permanent",
  hire_date: "2024-01-15",
  license_number: "DL789012",
  license_type: "Category D",
  license_expiry_date: "2025-01-01",
  languages_spoken: ["Arabic", "French", "English"],
  tour_guide_certified: true,
  first_aid_certified: true,
  status: "Active",
  performance_rating: 4.8,
  total_tours_completed: 156,
  total_incidents: 2,
  age: 39,
  years_of_service: 3.2,
  is_license_expired: false,
  days_until_license_expiry: 365,
  is_available_for_assignment: true
};

// Mock assignment data
const mockAssignment = {
  id: "456e7890-e89b-12d3-a456-426614174001",
  driver_id: "123e4567-e89b-12d3-a456-426614174000",
  tour_instance_id: "789e0123-e89b-12d3-a456-426614174002",
  status: "Confirmed",
  start_date: "2024-03-15",
  end_date: "2024-03-18",
  tour_title: "Atlas Mountains Discovery",
  pickup_location: "Marrakech Hotel Atlas",
  dropoff_location: "Marrakech Menara Airport",
  estimated_duration_hours: 72,
  customer_rating: 5.0,
  customer_feedback: "Excellent driver, very professional and knowledgeable",
  assigned_at: "2024-03-01T10:00:00Z"
};
```

### Postman Collection Structure
```json
{
  "info": {
    "name": "Driver Management API",
    "description": "Driver management and assignment endpoints"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "https://api.example.com/v1"
    },
    {
      "key": "driver_id",
      "value": "{{$guid}}"
    }
  ],
  "item": [
    {
      "name": "Drivers",
      "item": [
        {
          "name": "Register Driver",
          "request": {
            "method": "POST",
            "url": "{{base_url}}/drivers/",
            "body": {
              "mode": "raw",
              "raw": "{\n  \"full_name\": \"Mohammed Alami\",\n  \"license_type\": \"Category D\"\n}"
            }
          }
        }
      ]
    },
    {
      "name": "Mobile API",
      "item": [
        {
          "name": "Driver Dashboard",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/mobile/driver/{{driver_id}}/dashboard"
          }
        }
      ]
    }
  ]
}
```

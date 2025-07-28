# Tour Operations Service API Documentation

## 1. Service Overview

**Service Name**: Tour Operations Service  
**Purpose**: Manages tour templates, tour instances, itinerary planning, and incident tracking for the Moroccan Tourist Transport ERP system.  
**Base Path**: `/api/v1`  
**Authentication**: JWT Bearer Token with RBAC  
**Required Scopes**: `tours:read`, `tours:create`, `tours:update`, `tours:delete`

## 2. Endpoint Reference

### Tour Template Management

#### POST /tour-templates
**Purpose**: Create a new tour template  
**Authentication**: Required - `tours:create:templates`

**Request Body**:
```json
{
  "title": "Imperial Cities Discovery",
  "description": "Explore Morocco's four imperial cities: Rabat, Meknes, Fez, and Marrakech",
  "short_description": "4-day cultural tour of Morocco's imperial cities",
  "category": "CULTURAL",
  "duration_days": 4,
  "difficulty_level": "EASY",
  "default_language": "French",
  "default_region": "Central Morocco",
  "starting_location": "Casablanca",
  "ending_location": "Marrakech",
  "min_participants": 2,
  "max_participants": 15,
  "base_price": 1200.0,
  "highlights": [
    "Visit Hassan II Mosque",
    "Explore Fez Medina",
    "Traditional Moroccan cuisine",
    "Professional guide included"
  ],
  "inclusions": [
    "Transportation",
    "Accommodation (3 nights)",
    "Professional guide",
    "Entrance fees"
  ],
  "exclusions": [
    "International flights",
    "Personal expenses",
    "Travel insurance"
  ],
  "requirements": "Valid passport required. Comfortable walking shoes recommended."
}
```

**Response Structure**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Imperial Cities Discovery",
  "description": "Explore Morocco's four imperial cities: Rabat, Meknes, Fez, and Marrakech",
  "short_description": "4-day cultural tour of Morocco's imperial cities",
  "category": "CULTURAL",
  "duration_days": 4,
  "difficulty_level": "EASY",
  "default_language": "French",
  "default_region": "Central Morocco",
  "starting_location": "Casablanca",
  "ending_location": "Marrakech",
  "min_participants": 2,
  "max_participants": 15,
  "base_price": 1200.0,
  "highlights": [
    "Visit Hassan II Mosque",
    "Explore Fez Medina",
    "Traditional Moroccan cuisine",
    "Professional guide included"
  ],
  "inclusions": [
    "Transportation",
    "Accommodation (3 nights)",
    "Professional guide",
    "Entrance fees"
  ],
  "exclusions": [
    "International flights",
    "Personal expenses",
    "Travel insurance"
  ],
  "requirements": "Valid passport required. Comfortable walking shoes recommended.",
  "is_active": true,
  "is_featured": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null
}
```

**Success Status**: 201 Created

#### GET /tour-templates
**Purpose**: Retrieve tour templates with filtering and pagination  
**Authentication**: Required - `tours:read:templates`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| page | integer | 1 | No | Page number for pagination |
| size | integer | 20 | No | Number of templates per page |
| query | string | null | No | Search query for title, description |
| category | string | null | No | Filter by category (CULTURAL, ADVENTURE, DESERT, etc.) |
| difficulty_level | string | null | No | Filter by difficulty (EASY, MODERATE, etc.) |
| region | string | null | No | Filter by region |
| min_duration | integer | null | No | Minimum duration in days |
| max_duration | integer | null | No | Maximum duration in days |
| min_participants | integer | null | No | Minimum participants |
| max_participants | integer | null | No | Maximum participants |
| is_active | boolean | true | No | Filter by active status |
| is_featured | boolean | null | No | Filter by featured status |

#### GET /tour-templates/{template_id}
**Purpose**: Retrieve specific tour template  
**Authentication**: Required - `tours:read:templates`

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| template_id | string (UUID) | Yes | Template identifier |

#### PUT /tour-templates/{template_id}
**Purpose**: Update tour template  
**Authentication**: Required - `tours:update:templates`

#### GET /tour-templates/featured
**Purpose**: Get featured tour templates  
**Authentication**: Required - `tours:read:templates`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| limit | integer | 10 | No | Number of featured templates (1-50) |

#### POST /tour-templates/{template_id}/duplicate
**Purpose**: Duplicate an existing tour template  
**Authentication**: Required - `tours:create:templates`

**Query Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| new_title | string | Yes | Title for the duplicated template |

### Tour Instance Management

#### POST /tour-instances
**Purpose**: Create a new tour instance from a template  
**Authentication**: Required - `tours:create:instances`

**Request Body**:
```json
{
  "template_id": "550e8400-e29b-41d4-a716-446655440000",
  "booking_id": "550e8400-e29b-41d4-a716-446655440001",
  "customer_id": "550e8400-e29b-41d4-a716-446655440002",
  "title": "Imperial Cities Discovery - March 2024",
  "start_date": "2024-03-15",
  "end_date": "2024-03-18",
  "participant_count": 8,
  "lead_participant_name": "Ahmed Benali",
  "language": "French",
  "special_requirements": "Vegetarian meals for 2 participants",
  "participant_details": {
    "participants": [
      {
        "name": "Ahmed Benali",
        "age": 35,
        "nationality": "Moroccan",
        "dietary_requirements": "None"
      },
      {
        "name": "Sarah Johnson",
        "age": 28,
        "nationality": "American",
        "dietary_requirements": "Vegetarian"
      }
    ]
  }
}
```

**Response Structure**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "template_id": "550e8400-e29b-41d4-a716-446655440000",
  "booking_id": "550e8400-e29b-41d4-a716-446655440001",
  "customer_id": "550e8400-e29b-41d4-a716-446655440002",
  "title": "Imperial Cities Discovery - March 2024",
  "status": "PLANNED",
  "start_date": "2024-03-15",
  "end_date": "2024-03-18",
  "actual_start_date": null,
  "actual_end_date": null,
  "participant_count": 8,
  "lead_participant_name": "Ahmed Benali",
  "assigned_guide_id": null,
  "assigned_vehicle_id": null,
  "assigned_driver_id": null,
  "language": "French",
  "special_requirements": "Vegetarian meals for 2 participants",
  "participant_details": {},
  "internal_notes": null,
  "current_day": 1,
  "completion_percentage": 0.0,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null,
  "confirmed_at": null
}
```

**Success Status**: 201 Created

#### GET /tour-instances
**Purpose**: Retrieve tour instances with filtering  
**Authentication**: Required - `tours:read:instances`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| template_id | string | null | No | Filter by template ID |
| booking_id | string | null | No | Filter by booking ID |
| customer_id | string | null | No | Filter by customer ID |
| status | string | null | No | Filter by status |
| assigned_guide_id | string | null | No | Filter by assigned guide |
| assigned_vehicle_id | string | null | No | Filter by assigned vehicle |
| start_date_from | string | null | No | Filter by start date from (YYYY-MM-DD) |
| start_date_to | string | null | No | Filter by start date to (YYYY-MM-DD) |
| region | string | null | No | Filter by region |

#### GET /tour-instances/active
**Purpose**: Get all currently active tours  
**Authentication**: Required - `tours:read:instances`

#### GET /tour-instances/{instance_id}
**Purpose**: Get tour instance by ID  
**Authentication**: Required - `tours:read:instances`

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| instance_id | string (UUID) | Yes | Tour instance identifier |

#### GET /tour-instances/{instance_id}/summary
**Purpose**: Get comprehensive tour instance summary  
**Authentication**: Required - `tours:read:instances`

#### POST /tour-instances/{instance_id}/assign
**Purpose**: Assign resources (guide, vehicle, driver) to tour  
**Authentication**: Required - `tours:update:instances`

**Request Body**:
```json
{
  "guide_id": "550e8400-e29b-41d4-a716-446655440004",
  "vehicle_id": "550e8400-e29b-41d4-a716-446655440005",
  "driver_id": "550e8400-e29b-41d4-a716-446655440006",
  "notes": "Experienced guide requested for cultural tour"
}
```

#### POST /tour-instances/{instance_id}/status
**Purpose**: Update tour instance status  
**Authentication**: Required - `tours:update:instances`

**Request Body**:
```json
{
  "status": "CONFIRMED",
  "notes": "All resources assigned and confirmed",
  "actual_start_date": "2024-03-15T08:00:00Z",
  "actual_end_date": null
}
```

#### POST /tour-instances/{instance_id}/progress
**Purpose**: Update tour progress  
**Authentication**: Required - `tours:update:instances`

**Request Body**:
```json
{
  "current_day": 2,
  "completion_percentage": 50.0,
  "notes": "Day 1 completed successfully, moving to Fez"
}
```

### Itinerary Management

#### POST /itinerary/items
**Purpose**: Add an itinerary item to a tour  
**Authentication**: Required - `tours:create:itinerary`

**Request Body**:
```json
{
  "tour_instance_id": "550e8400-e29b-41d4-a716-446655440003",
  "day_number": 1,
  "start_time": "09:00",
  "end_time": "12:00",
  "duration_minutes": 180,
  "activity_type": "VISIT",
  "title": "Hassan II Mosque Visit",
  "description": "Guided tour of the magnificent Hassan II Mosque",
  "location_name": "Hassan II Mosque",
  "address": "Boulevard de la Corniche, Casablanca",
  "coordinates": [33.6084, -7.6326],
  "notes": "Dress code required - modest clothing",
  "cost": 50.0,
  "is_mandatory": true
}
```

**Success Status**: 201 Created

#### GET /itinerary/tour/{tour_instance_id}
**Purpose**: Get all itinerary items for a tour  
**Authentication**: Required - `tours:read:itinerary`

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| tour_instance_id | string (UUID) | Yes | Tour instance identifier |

#### GET /itinerary/tour/{tour_instance_id}/day/{day_number}
**Purpose**: Get itinerary for a specific day  
**Authentication**: Required - `tours:read:itinerary`

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| tour_instance_id | string (UUID) | Yes | Tour instance identifier |
| day_number | integer | Yes | Day number (≥1) |

**Response Structure**:
```json
{
  "day_number": 1,
  "date": "2024-03-15",
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440007",
      "tour_instance_id": "550e8400-e29b-41d4-a716-446655440003",
      "day_number": 1,
      "start_time": "09:00",
      "end_time": "12:00",
      "duration_minutes": 180,
      "activity_type": "VISIT",
      "title": "Hassan II Mosque Visit",
      "description": "Guided tour of the magnificent Hassan II Mosque",
      "location_name": "Hassan II Mosque",
      "address": "Boulevard de la Corniche, Casablanca",
      "coordinates": [33.6084, -7.6326],
      "notes": "Dress code required - modest clothing",
      "cost": 50.0,
      "is_mandatory": true,
      "is_completed": false,
      "completed_at": null,
      "completed_by": null,
      "is_cancelled": false,
      "cancellation_reason": null,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": null,
      "display_time": "09:00 - 12:00"
    }
  ],
  "total_items": 4,
  "completed_items": 0,
  "estimated_duration_minutes": 480
}
```

#### PUT /itinerary/items/{item_id}
**Purpose**: Update an itinerary item  
**Authentication**: Required - `tours:update:itinerary`

#### POST /itinerary/items/{item_id}/complete
**Purpose**: Mark an itinerary item as completed  
**Authentication**: Required - `tours:update:itinerary`

**Request Body**:
```json
{
  "notes": "Tour completed successfully, all participants enjoyed the visit",
  "actual_duration_minutes": 195
}
```

#### POST /itinerary/tour/{tour_instance_id}/day/{day_number}/reorder
**Purpose**: Reorder itinerary items for a specific day  
**Authentication**: Required - `tours:update:itinerary`

**Request Body**: Array of item IDs in desired order
```json
[
  "550e8400-e29b-41d4-a716-446655440007",
  "550e8400-e29b-41d4-a716-446655440008",
  "550e8400-e29b-41d4-a716-446655440009"
]
```

### Incident Management

#### POST /incidents
**Purpose**: Create a new incident  
**Authentication**: Required - `tours:create:incidents`

**Request Body**:
```json
{
  "tour_instance_id": "550e8400-e29b-41d4-a716-446655440003",
  "reporter_id": "550e8400-e29b-41d4-a716-446655440004",
  "incident_type": "DELAY",
  "severity": "MEDIUM",
  "title": "Traffic Delay on Route to Fez",
  "description": "Unexpected traffic jam caused 2-hour delay",
  "location": "Highway A2 near Rabat",
  "day_number": 2,
  "affected_participants": 8,
  "estimated_delay_minutes": 120,
  "financial_impact": 0.0
}
```

**Response Structure**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440010",
  "tour_instance_id": "550e8400-e29b-41d4-a716-446655440003",
  "reporter_id": "550e8400-e29b-41d4-a716-446655440004",
  "incident_type": "DELAY",
  "severity": "MEDIUM",
  "title": "Traffic Delay on Route to Fez",
  "description": "Unexpected traffic jam caused 2-hour delay",
  "location": "Highway A2 near Rabat",
  "day_number": 2,
  "affected_participants": 8,
  "estimated_delay_minutes": 120,
  "financial_impact": 0.0,
  "is_resolved": false,
  "resolution_description": null,
  "resolved_by": null,
  "resolved_at": null,
  "requires_follow_up": false,
  "follow_up_notes": null,
  "escalated_to": null,
  "reported_at": "2024-03-16T14:30:00Z",
  "created_at": "2024-03-16T14:30:00Z",
  "updated_at": null,
  "priority_score": 2,
  "is_urgent": false
}
```

**Success Status**: 201 Created

#### GET /incidents
**Purpose**: Retrieve incidents with filtering  
**Authentication**: Required - `tours:read:incidents`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| tour_instance_id | string | null | No | Filter by tour instance ID |
| incident_type | string | null | No | Filter by incident type |
| severity | string | null | No | Filter by severity |
| is_resolved | boolean | null | No | Filter by resolution status |
| reporter_id | string | null | No | Filter by reporter ID |
| requires_follow_up | boolean | null | No | Filter by follow-up requirement |

#### GET /incidents/urgent
**Purpose**: Get all urgent unresolved incidents  
**Authentication**: Required - `tours:read:incidents`

#### POST /incidents/{incident_id}/resolve
**Purpose**: Resolve an incident  
**Authentication**: Required - `tours:update:incidents`

**Request Body**:
```json
{
  "resolution_description": "Alternative route taken, delay minimized to 30 minutes",
  "resolved_by": "550e8400-e29b-41d4-a716-446655440004",
  "requires_follow_up": false,
  "follow_up_notes": null
}
```

#### POST /incidents/{incident_id}/escalate
**Purpose**: Escalate an incident  
**Authentication**: Required - `tours:update:incidents`

**Request Body**:
```json
{
  "escalated_to": "550e8400-e29b-41d4-a716-446655440011",
  "escalation_reason": "Requires management attention due to customer complaints",
  "notes": "Multiple customers expressed dissatisfaction"
}
```

#### GET /incidents/stats
**Purpose**: Get incident statistics  
**Authentication**: Required - `tours:read:incidents`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| days | integer | 30 | No | Number of days for statistics (1-365) |

**Response Structure**:
```json
{
  "total_incidents": 25,
  "resolved_incidents": 20,
  "unresolved_incidents": 5,
  "by_type": {
    "DELAY": 8,
    "COMPLAINT": 5,
    "BREAKDOWN": 3,
    "WEATHER": 4,
    "OTHER": 5
  },
  "by_severity": {
    "LOW": 10,
    "MEDIUM": 12,
    "HIGH": 2,
    "CRITICAL": 1
  },
  "by_tour": {
    "tour_instance_1": 3,
    "tour_instance_2": 2
  },
  "average_resolution_time_hours": 4.5,
  "urgent_incidents": 3,
  "incidents_requiring_follow_up": 2
}
```

## 3. Data Models

### TourTemplate Model
```json
{
  "id": "string (uuid, required)",
  "title": "string (max 255, required)",
  "description": "string (max 2000, optional)",
  "short_description": "string (max 500, optional)",
  "category": "enum (CULTURAL, ADVENTURE, DESERT, COASTAL, CITY, CUSTOM)",
  "duration_days": "integer (1-30, required)",
  "difficulty_level": "enum (EASY, MODERATE, CHALLENGING, EXPERT)",
  "default_language": "string (max 50, default 'French')",
  "default_region": "string (max 100, required)",
  "starting_location": "string (max 255, optional)",
  "ending_location": "string (max 255, optional)",
  "min_participants": "integer (≥1, default 1)",
  "max_participants": "integer (≥1, default 20)",
  "base_price": "number (≥0, optional)",
  "highlights": "array of strings (optional)",
  "inclusions": "array of strings (optional)",
  "exclusions": "array of strings (optional)",
  "requirements": "string (max 1000, optional)",
  "is_active": "boolean (default true)",
  "is_featured": "boolean (default false)",
  "created_at": "string (datetime, required)",
  "updated_at": "string (datetime, optional)"
}
```

### TourInstance Model
```json
{
  "id": "string (uuid, required)",
  "template_id": "string (uuid, required)",
  "booking_id": "string (uuid, required)",
  "customer_id": "string (uuid, required)",
  "title": "string (max 255, required)",
  "status": "enum (PLANNED, CONFIRMED, IN_PROGRESS, COMPLETED, CANCELLED, POSTPONED)",
  "start_date": "string (date, required)",
  "end_date": "string (date, required)",
  "actual_start_date": "string (datetime, optional)",
  "actual_end_date": "string (datetime, optional)",
  "participant_count": "integer (≥1, required)",
  "lead_participant_name": "string (max 255, required)",
  "assigned_guide_id": "string (uuid, optional)",
  "assigned_vehicle_id": "string (uuid, optional)",
  "assigned_driver_id": "string (uuid, optional)",
  "language": "string (max 50, default 'French')",
  "special_requirements": "string (max 2000, optional)",
  "participant_details": "object (optional)",
  "internal_notes": "string (max 2000, optional)",
  "current_day": "integer (≥1, default 1)",
  "completion_percentage": "number (0-100, default 0.0)",
  "created_at": "string (datetime, required)",
  "updated_at": "string (datetime, optional)",
  "confirmed_at": "string (datetime, optional)"
}
```

### ItineraryItem Model
```json
{
  "id": "string (uuid, required)",
  "tour_instance_id": "string (uuid, required)",
  "day_number": "integer (≥1, required)",
  "start_time": "string (time HH:MM, optional)",
  "end_time": "string (time HH:MM, optional)",
  "duration_minutes": "integer (≥0, optional)",
  "activity_type": "enum (VISIT, MEAL, TRANSPORT, ACCOMMODATION, ACTIVITY, FREE_TIME, MEETING_POINT, DEPARTURE, ARRIVAL, BREAK)",
  "title": "string (max 255, required)",
  "description": "string (max 1000, optional)",
  "location_name": "string (max 255, optional)",
  "address": "string (max 500, optional)",
  "coordinates": "array of numbers [lat, lng] (optional)",
  "notes": "string (max 1000, optional)",
  "cost": "number (≥0, optional)",
  "is_mandatory": "boolean (default true)",
  "is_completed": "boolean (default false)",
  "completed_at": "string (datetime, optional)",
  "completed_by": "string (uuid, optional)",
  "is_cancelled": "boolean (default false)",
  "cancellation_reason": "string (max 500, optional)",
  "created_at": "string (datetime, required)",
  "updated_at": "string (datetime, optional)",
  "display_time": "string (calculated)"
}
```

### Incident Model
```json
{
  "id": "string (uuid, required)",
  "tour_instance_id": "string (uuid, required)",
  "reporter_id": "string (uuid, required)",
  "incident_type": "enum (DELAY, MEDICAL, COMPLAINT, BREAKDOWN, WEATHER, SAFETY, ACCOMMODATION, TRANSPORT, GUIDE_ISSUE, CUSTOMER_ISSUE, OTHER)",
  "severity": "enum (LOW, MEDIUM, HIGH, CRITICAL)",
  "title": "string (max 255, required)",
  "description": "string (max 2000, required)",
  "location": "string (max 255, optional)",
  "day_number": "integer (≥1, optional)",
  "affected_participants": "integer (≥0, optional)",
  "estimated_delay_minutes": "integer (≥0, optional)",
  "financial_impact": "number (≥0, optional)",
  "is_resolved": "boolean (default false)",
  "resolution_description": "string (max 2000, optional)",
  "resolved_by": "string (uuid, optional)",
  "resolved_at": "string (datetime, optional)",
  "requires_follow_up": "boolean (default false)",
  "follow_up_notes": "string (max 1000, optional)",
  "escalated_to": "string (uuid, optional)",
  "reported_at": "string (datetime, required)",
  "created_at": "string (datetime, required)",
  "updated_at": "string (datetime, optional)",
  "priority_score": "integer (calculated)",
  "is_urgent": "boolean (calculated)"
}
```

## 4. Frontend Integration Guidelines

### HTTP Client Configuration
```javascript
// Axios configuration for Tour Service
const tourApiClient = axios.create({
  baseURL: 'https://api.example.com/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor
tourApiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor
tourApiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### Real-time Updates
```javascript
// WebSocket connection for real-time tour updates
const connectTourWebSocket = (tourInstanceId) => {
  const ws = new WebSocket(`wss://api.example.com/ws/tours/${tourInstanceId}`);
  
  ws.onmessage = (event) => {
    const update = JSON.parse(event.data);
    handleTourUpdate(update);
  };
  
  return ws;
};
```

### Error Handling Pattern
```javascript
// Tour service specific error handling
const handleTourError = (error) => {
  if (error.response?.status === 422) {
    // Validation errors
    return error.response.data.errors || [];
  }
  if (error.response?.status === 404) {
    return [{ message: 'Tour template, instance, or itinerary item not found' }];
  }
  if (error.response?.status === 409) {
    return [{ message: 'Conflict: Resource already assigned or unavailable' }];
  }
  return [{ message: error.response?.data?.detail || 'Tour operation failed' }];
};
```

### Rate Limiting
- Standard HTTP 429 response if limits exceeded
- Retry-After header provided for backoff timing

### CORS Policy
- Allowed origins: `http://localhost:3000`, `http://localhost:8080`
- Credentials allowed: Yes
- Methods: GET, POST, PUT, DELETE

## 5. Testing & Support Tools

### Example API Calls

#### Create Tour Template
```bash
curl -X POST "https://api.example.com/api/v1/tour-templates" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Imperial Cities Discovery",
    "category": "CULTURAL",
    "duration_days": 4,
    "default_region": "Central Morocco",
    "min_participants": 2,
    "max_participants": 15,
    "base_price": 1200.0
  }'
```

#### Create Tour Instance
```bash
curl -X POST "https://api.example.com/api/v1/tour-instances" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "uuid",
    "booking_id": "uuid",
    "customer_id": "uuid",
    "title": "Imperial Cities Discovery - March 2024",
    "start_date": "2024-03-15",
    "end_date": "2024-03-18",
    "participant_count": 8,
    "lead_participant_name": "Ahmed Benali"
  }'
```

#### Add Itinerary Item
```bash
curl -X POST "https://api.example.com/api/v1/itinerary/items" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "tour_instance_id": "uuid",
    "day_number": 1,
    "activity_type": "VISIT",
    "title": "Hassan II Mosque Visit",
    "start_time": "09:00",
    "end_time": "12:00"
  }'
```

#### Report Incident
```bash
curl -X POST "https://api.example.com/api/v1/incidents" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "tour_instance_id": "uuid",
    "incident_type": "DELAY",
    "severity": "MEDIUM",
    "title": "Traffic Delay",
    "description": "Unexpected traffic jam"
  }'
```

### Sample Postman Collection Structure
```json
{
  "info": {
    "name": "Tour Operations Service API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "auth": {
    "type": "bearer",
    "bearer": [{"key": "token", "value": "{{access_token}}"}]
  },
  "item": [
    {
      "name": "Tour Templates",
      "item": [
        {"name": "Create Template", "request": {"method": "POST", "url": "{{base_url}}/tour-templates"}},
        {"name": "Get Templates", "request": {"method": "GET", "url": "{{base_url}}/tour-templates"}},
        {"name": "Get Featured", "request": {"method": "GET", "url": "{{base_url}}/tour-templates/featured"}},
        {"name": "Duplicate Template", "request": {"method": "POST", "url": "{{base_url}}/tour-templates/{{template_id}}/duplicate"}}
      ]
    },
    {
      "name": "Tour Instances",
      "item": [
        {"name": "Create Instance", "request": {"method": "POST", "url": "{{base_url}}/tour-instances"}},
        {"name": "Get Instances", "request": {"method": "GET", "url": "{{base_url}}/tour-instances"}},
        {"name": "Get Active Tours", "request": {"method": "GET", "url": "{{base_url}}/tour-instances/active"}},
        {"name": "Assign Resources", "request": {"method": "POST", "url": "{{base_url}}/tour-instances/{{instance_id}}/assign"}}
      ]
    },
    {
      "name": "Itinerary",
      "item": [
        {"name": "Add Item", "request": {"method": "POST", "url": "{{base_url}}/itinerary/items"}},
        {"name": "Get Tour Itinerary", "request": {"method": "GET", "url": "{{base_url}}/itinerary/tour/{{tour_id}}"}},
        {"name": "Complete Item", "request": {"method": "POST", "url": "{{base_url}}/itinerary/items/{{item_id}}/complete"}}
      ]
    },
    {
      "name": "Incidents",
      "item": [
        {"name": "Create Incident", "request": {"method": "POST", "url": "{{base_url}}/incidents"}},
        {"name": "Get Incidents", "request": {"method": "GET", "url": "{{base_url}}/incidents"}},
        {"name": "Get Urgent", "request": {"method": "GET", "url": "{{base_url}}/incidents/urgent"}},
        {"name": "Resolve Incident", "request": {"method": "POST", "url": "{{base_url}}/incidents/{{incident_id}}/resolve"}}
      ]
    }
  ]
}
```

### Common Frontend Patterns
```javascript
// Tour template management
const createTourTemplate = async (templateData) => {
  const response = await tourApiClient.post('/tour-templates', templateData);
  return response.data;
};

const getTourTemplates = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await tourApiClient.get(`/tour-templates?${params}`);
  return response.data;
};

const getFeaturedTemplates = async (limit = 10) => {
  const response = await tourApiClient.get(`/tour-templates/featured?limit=${limit}`);
  return response.data;
};

// Tour instance management
const createTourInstance = async (instanceData) => {
  const response = await tourApiClient.post('/tour-instances', instanceData);
  return response.data;
};

const getTourInstances = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await tourApiClient.get(`/tour-instances?${params}`);
  return response.data;
};

const assignTourResources = async (instanceId, assignment) => {
  const response = await tourApiClient.post(`/tour-instances/${instanceId}/assign`, assignment);
  return response.data;
};

const updateTourStatus = async (instanceId, statusUpdate) => {
  const response = await tourApiClient.post(`/tour-instances/${instanceId}/status`, statusUpdate);
  return response.data;
};

// Itinerary management
const addItineraryItem = async (itemData) => {
  const response = await tourApiClient.post('/itinerary/items', itemData);
  return response.data;
};

const getTourItinerary = async (tourInstanceId) => {
  const response = await tourApiClient.get(`/itinerary/tour/${tourInstanceId}`);
  return response.data;
};

const getDayItinerary = async (tourInstanceId, dayNumber) => {
  const response = await tourApiClient.get(`/itinerary/tour/${tourInstanceId}/day/${dayNumber}`);
  return response.data;
};

const completeItineraryItem = async (itemId, completionData) => {
  const response = await tourApiClient.post(`/itinerary/items/${itemId}/complete`, completionData);
  return response.data;
};

// Incident management
const createIncident = async (incidentData) => {
  const response = await tourApiClient.post('/incidents', incidentData);
  return response.data;
};

const getIncidents = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await tourApiClient.get(`/incidents?${params}`);
  return response.data;
};

const getUrgentIncidents = async () => {
  const response = await tourApiClient.get('/incidents/urgent');
  return response.data;
};

const resolveIncident = async (incidentId, resolutionData) => {
  const response = await tourApiClient.post(`/incidents/${incidentId}/resolve`, resolutionData);
  return response.data;
};

const escalateIncident = async (incidentId, escalationData) => {
  const response = await tourApiClient.post(`/incidents/${incidentId}/escalate`, escalationData);
  return response.data;
};

// Real-time updates
const subscribeTourUpdates = (tourInstanceId, callback) => {
  const ws = connectTourWebSocket(tourInstanceId);
  ws.onmessage = (event) => {
    const update = JSON.parse(event.data);
    callback(update);
  };
  return ws;
};
```

### Mock Data Examples
```javascript
// Mock tour template data
const mockTourTemplates = [
  {
    id: "550e8400-e29b-41d4-a716-446655440000",
    title: "Imperial Cities Discovery",
    category: "CULTURAL",
    duration_days: 4,
    difficulty_level: "EASY",
    default_region: "Central Morocco",
    min_participants: 2,
    max_participants: 15,
    base_price: 1200.0,
    is_active: true,
    is_featured: true
  }
];

// Mock tour instance data
const mockTourInstances = [
  {
    id: "550e8400-e29b-41d4-a716-446655440003",
    template_id: "550e8400-e29b-41d4-a716-446655440000",
    title: "Imperial Cities Discovery - March 2024",
    status: "CONFIRMED",
    start_date: "2024-03-15",
    end_date: "2024-03-18",
    participant_count: 8,
    current_day: 1,
    completion_percentage: 0.0
  }
];

// Mock itinerary item data
const mockItineraryItems = [
  {
    id: "550e8400-e29b-41d4-a716-446655440007",
    day_number: 1,
    activity_type: "VISIT",
    title: "Hassan II Mosque Visit",
    start_time: "09:00",
    end_time: "12:00",
    location_name: "Hassan II Mosque",
    is_completed: false,
    is_mandatory: true
  }
];

// Mock incident data
const mockIncidents = [
  {
    id: "550e8400-e29b-41d4-a716-446655440010",
    incident_type: "DELAY",
    severity: "MEDIUM",
    title: "Traffic Delay on Route to Fez",
    is_resolved: false,
    is_urgent: false,
    priority_score: 2,
    reported_at: "2024-03-16T14:30:00Z"
  }
];
```

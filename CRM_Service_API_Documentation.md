# Customer Relationship Management (CRM) Service API Documentation

## Service Overview

**Service Name**: Customer Relationship Management (CRM) Service  
**Purpose**: Manages customer profiles, interactions, feedback, and segmentation for the Moroccan Tourist Transport ERP system.  
**Base Path**: `/api/v1`  
**Authentication**: JWT Bearer tokens with RBAC permissions

## Endpoint Reference

### Customer Management Endpoints

#### POST /customers/
**Purpose**: Create a new customer

**Authentication Requirements**: Bearer token with `crm:create:customers` permission

**Request Body Schema**:
```json
{
  "full_name": "string (optional, max 255 chars)",
  "company_name": "string (optional, max 255 chars)",
  "contact_type": "string (enum: Individual, Corporate, required)",
  "email": "string (email format, unique, required)",
  "phone": "string (max 20 chars, required)",
  "nationality": "string (max 100 chars, optional)",
  "region": "string (max 100 chars, optional)",
  "preferred_language": "string (default: French)",
  "tags": ["string (optional)"],
  "notes": "string (optional)"
}
```

**Request Example**:
```bash
curl -X POST "https://api.example.com/v1/customers/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Ahmed Hassan",
    "contact_type": "Individual",
    "email": "ahmed.hassan@example.com",
    "phone": "+212612345678",
    "nationality": "Moroccan",
    "region": "Casablanca",
    "preferred_language": "French",
    "tags": ["VIP", "Repeat Customer"]
  }'
```

**Response Structure**:
```json
{
  "id": "uuid",
  "full_name": "string",
  "company_name": "string",
  "contact_type": "string",
  "email": "string",
  "phone": "string",
  "nationality": "string",
  "region": "string",
  "preferred_language": "string",
  "loyalty_status": "string (enum: New, Bronze, Silver, Gold, Platinum, VIP)",
  "is_active": "boolean",
  "tags": ["string"],
  "notes": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "last_interaction": "datetime"
}
```

**Success Status Codes**:
- `201 Created`: Customer created successfully

#### GET /customers/
**Purpose**: Get list of customers with optional filters

**Authentication Requirements**: Bearer token with `crm:read:customers` permission

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| page | integer | 1 | No | Page number |
| size | integer | 20 | No | Items per page |
| query | string | - | No | Search in name, email, phone |
| contact_type | string | - | No | Filter by contact type |
| region | string | - | No | Filter by region |
| loyalty_status | string | - | No | Filter by loyalty status |
| tags | array | - | No | Filter by tags |
| is_active | boolean | true | No | Filter by active status |

**Response Structure**:
```json
{
  "items": ["Customer objects"],
  "total": "integer",
  "page": "integer",
  "size": "integer",
  "pages": "integer"
}
```

#### GET /customers/{customer_id}
**Purpose**: Get customer by ID

**Authentication Requirements**: Bearer token with `crm:read:customers` permission

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| customer_id | uuid | Yes | Customer identifier |

#### GET /customers/{customer_id}/summary
**Purpose**: Get comprehensive customer summary with statistics

**Authentication Requirements**: Bearer token with `crm:read:customers` permission

**Response Structure**:
```json
{
  "id": "uuid",
  "full_name": "string",
  "email": "string",
  "total_interactions": "integer",
  "total_feedback": "integer",
  "average_rating": "float",
  "last_feedback_date": "datetime",
  "segments": ["string"],
  "interaction_channels": {
    "email": "integer",
    "phone": "integer",
    "chat": "integer"
  },
  "feedback_by_service": {
    "Tour": "integer",
    "Transport": "integer"
  }
}
```

### Interaction Management Endpoints

#### POST /interactions/
**Purpose**: Create a new customer interaction

**Authentication Requirements**: Bearer token with `crm:create:interactions` permission

**Request Body Schema**:
```json
{
  "customer_id": "uuid (required)",
  "staff_member_id": "uuid (optional)",
  "channel": "string (enum: email, phone, chat, in-person, whatsapp, sms, required)",
  "subject": "string (max 255 chars, optional)",
  "summary": "string (max 2000 chars, required)",
  "duration_minutes": "integer (optional)",
  "follow_up_required": "boolean (default: false)",
  "follow_up_date": "datetime (optional)"
}
```

**Response Structure**:
```json
{
  "id": "uuid",
  "customer_id": "uuid",
  "staff_member_id": "uuid",
  "channel": "string",
  "subject": "string",
  "summary": "string",
  "duration_minutes": "integer",
  "follow_up_required": "boolean",
  "follow_up_date": "datetime",
  "timestamp": "datetime",
  "created_at": "datetime"
}
```

#### GET /interactions/
**Purpose**: Get list of interactions with optional filters

**Authentication Requirements**: Bearer token with `crm:read:interactions` permission

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| page | integer | 1 | No | Page number |
| size | integer | 20 | No | Items per page |
| customer_id | uuid | - | No | Filter by customer |
| staff_member_id | uuid | - | No | Filter by staff member |
| channel | string | - | No | Filter by channel |
| follow_up_required | boolean | - | No | Filter by follow-up requirement |

#### GET /interactions/customer/{customer_id}
**Purpose**: Get all interactions for a specific customer

**Authentication Requirements**: Bearer token with `crm:read:interactions` permission

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| customer_id | uuid | Yes | Customer identifier |

### Feedback Management Endpoints

#### POST /feedback/
**Purpose**: Submit new customer feedback

**Authentication Requirements**: Bearer token with `crm:create:feedback` permission

**Request Body Schema**:
```json
{
  "customer_id": "uuid (required)",
  "booking_id": "uuid (optional)",
  "service_type": "string (enum: Tour, Booking, Support, Transport, Accommodation, General, required)",
  "rating": "integer (1-5, required)",
  "comments": "string (max 2000 chars, optional)",
  "is_anonymous": "boolean (default: false)",
  "source": "string (default: web)"
}
```

**Response Structure**:
```json
{
  "id": "uuid",
  "customer_id": "uuid",
  "booking_id": "uuid",
  "service_type": "string",
  "rating": "integer",
  "comments": "string",
  "resolved": "boolean",
  "resolution_notes": "string",
  "resolved_by": "uuid",
  "resolved_at": "datetime",
  "is_anonymous": "boolean",
  "source": "string",
  "submitted_at": "datetime",
  "created_at": "datetime",
  "sentiment": "string (positive, neutral, negative)"
}
```

#### GET /feedback/
**Purpose**: Get list of feedback with optional filters

**Authentication Requirements**: Bearer token with `crm:read:feedback` permission

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| page | integer | 1 | No | Page number |
| size | integer | 20 | No | Items per page |
| customer_id | uuid | - | No | Filter by customer |
| service_type | string | - | No | Filter by service type |
| rating | integer | - | No | Filter by rating (1-5) |
| resolved | boolean | - | No | Filter by resolution status |
| booking_id | uuid | - | No | Filter by booking |

#### PUT /feedback/{feedback_id}
**Purpose**: Update feedback (mainly for resolution)

**Authentication Requirements**: Bearer token with `crm:update:feedback` permission

**Request Body Schema**:
```json
{
  "resolved": "boolean (optional)",
  "resolution_notes": "string (optional)",
  "resolved_by": "uuid (optional)"
}
```

#### GET /feedback/stats
**Purpose**: Get feedback statistics

**Authentication Requirements**: Bearer token with `crm:read:feedback` permission

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| days | integer | 30 | No | Number of days for statistics |

**Response Structure**:
```json
{
  "total_feedback": "integer",
  "average_rating": "float",
  "rating_distribution": {
    "1": "integer",
    "2": "integer",
    "3": "integer",
    "4": "integer",
    "5": "integer"
  },
  "by_service_type": {
    "Tour": "integer",
    "Transport": "integer"
  },
  "sentiment_analysis": {
    "positive": "integer",
    "neutral": "integer",
    "negative": "integer"
  },
  "resolution_rate": "float",
  "pending_resolution": "integer"
}
```

### Segment Management Endpoints

#### POST /segments/
**Purpose**: Create a new customer segment

**Authentication Requirements**: Bearer token with `crm:create:segments` permission

**Request Body Schema**:
```json
{
  "name": "string (unique, required)",
  "description": "string (optional)",
  "criteria": {
    "loyalty_status": ["string"],
    "region": ["string"],
    "contact_type": ["string"],
    "tags": ["string"]
  }
}
```

**Response Structure**:
```json
{
  "id": "uuid",
  "name": "string",
  "description": "string",
  "criteria": "object",
  "is_active": "boolean",
  "customer_count": "integer",
  "created_at": "datetime",
  "updated_at": "datetime",
  "last_calculated": "datetime"
}
```

#### GET /segments/{segment_id}/customers
**Purpose**: Get segment with its customers

**Authentication Requirements**: Bearer token with `crm:read:segments` permission

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| page | integer | 1 | No | Page number |
| size | integer | 20 | No | Items per page |

## Data Models

### Customer Model
```json
{
  "id": "uuid",
  "full_name": "string (max 255 chars, optional)",
  "company_name": "string (max 255 chars, optional)",
  "contact_type": "string (enum: Individual, Corporate)",
  "email": "string (email format, unique)",
  "phone": "string (max 20 chars)",
  "nationality": "string (max 100 chars, optional)",
  "region": "string (max 100 chars, optional)",
  "preferred_language": "string (default: French)",
  "tags": "array of strings (JSON)",
  "loyalty_status": "string (enum: New, Bronze, Silver, Gold, Platinum, VIP)",
  "is_active": "boolean (default: true)",
  "notes": "string (optional)",
  "created_at": "datetime",
  "updated_at": "datetime",
  "last_interaction": "datetime (optional)"
}
```

### Interaction Model
```json
{
  "id": "uuid",
  "customer_id": "uuid (foreign key)",
  "staff_member_id": "uuid (optional)",
  "channel": "string (enum: email, phone, chat, in-person, whatsapp, sms)",
  "subject": "string (max 255 chars, optional)",
  "summary": "string (max 2000 chars)",
  "duration_minutes": "integer (optional)",
  "follow_up_required": "boolean (default: false)",
  "follow_up_date": "datetime (optional)",
  "timestamp": "datetime",
  "created_at": "datetime"
}
```

### Feedback Model
```json
{
  "id": "uuid",
  "customer_id": "uuid (foreign key)",
  "booking_id": "uuid (optional, reference to booking service)",
  "service_type": "string (enum: Tour, Booking, Support, Transport, Accommodation, General)",
  "rating": "integer (1-5)",
  "comments": "string (max 2000 chars, optional)",
  "resolved": "boolean (default: false)",
  "resolution_notes": "string (max 1000 chars, optional)",
  "resolved_by": "uuid (optional)",
  "resolved_at": "datetime (optional)",
  "is_anonymous": "boolean (default: false)",
  "source": "string (default: web)",
  "submitted_at": "datetime",
  "created_at": "datetime"
}
```

### Segment Model
```json
{
  "id": "uuid",
  "name": "string (unique, max 255 chars)",
  "description": "string (max 1000 chars, optional)",
  "criteria": "object (JSON segmentation rules)",
  "is_active": "boolean (default: true)",
  "customer_count": "integer (default: 0)",
  "created_at": "datetime",
  "updated_at": "datetime (optional)",
  "last_calculated": "datetime (optional)"
}
```

## Frontend Integration Guidelines

### HTTP Client Configuration
```javascript
// CRM service client configuration
import axios from 'axios';

const crmClient = axios.create({
  baseURL: 'https://api.example.com/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
crmClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Customer Management Implementation
```javascript
class CustomerService {
  // Create customer
  async createCustomer(customerData) {
    const response = await crmClient.post('/customers/', customerData);
    return response.data;
  }

  // Get customers with search and filters
  async getCustomers(filters = {}) {
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

    const response = await crmClient.get(`/customers/?${params}`);
    return response.data;
  }

  // Get customer summary
  async getCustomerSummary(customerId) {
    const response = await crmClient.get(`/customers/${customerId}/summary`);
    return response.data;
  }

  // Update customer
  async updateCustomer(customerId, updateData) {
    const response = await crmClient.put(`/customers/${customerId}`, updateData);
    return response.data;
  }
}

// Interaction management
class InteractionService {
  // Log new interaction
  async logInteraction(interactionData) {
    const response = await crmClient.post('/interactions/', interactionData);
    return response.data;
  }

  // Get customer interactions
  async getCustomerInteractions(customerId, page = 1, size = 20) {
    const response = await crmClient.get(`/interactions/customer/${customerId}`, {
      params: { page, size }
    });
    return response.data;
  }
}

// Feedback management
class FeedbackService {
  // Submit feedback
  async submitFeedback(feedbackData) {
    const response = await crmClient.post('/feedback/', feedbackData);
    return response.data;
  }

  // Get feedback statistics
  async getFeedbackStats(days = 30) {
    const response = await crmClient.get('/feedback/stats', {
      params: { days }
    });
    return response.data;
  }

  // Resolve feedback
  async resolveFeedback(feedbackId, resolutionData) {
    const response = await crmClient.put(`/feedback/${feedbackId}`, resolutionData);
    return response.data;
  }
}
```

### Error Handling Patterns
```javascript
// CRM-specific error handler
function handleCrmError(error) {
  if (error.response) {
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        if (data.detail?.includes('Email already registered')) {
          return { 
            type: 'duplicate_email',
            message: 'A customer with this email already exists',
            field: 'email'
          };
        }
        break;
      case 404:
        return { 
          type: 'not_found',
          message: 'Customer not found',
          action: 'refresh_list'
        };
      case 422:
        return {
          type: 'validation_error',
          message: 'Please check the form data',
          errors: data.errors
        };
    }
  }
  
  return handleApiError(error);
}
```

### Real-time Updates
```javascript
// Customer activity tracking
class CustomerActivityTracker {
  constructor(customerId) {
    this.customerId = customerId;
    this.lastInteraction = null;
  }

  // Track interaction
  async trackInteraction(channel, summary, duration = null) {
    const interactionData = {
      customer_id: this.customerId,
      channel,
      summary,
      duration_minutes: duration,
      timestamp: new Date().toISOString()
    };

    const interaction = await crmClient.post('/interactions/', interactionData);
    this.lastInteraction = interaction.data;
    
    return interaction.data;
  }

  // Get recent activity
  async getRecentActivity(limit = 10) {
    const response = await crmClient.get(`/interactions/customer/${this.customerId}`, {
      params: { size: limit }
    });
    return response.data.items;
  }
}
```

### Rate Limiting
- Customer creation: 20 per minute per user
- Interaction logging: 100 per minute per user
- Feedback submission: 10 per minute per customer

### CORS Policy
- Allowed origins: Frontend domains (configurable)
- Allowed methods: GET, POST, PUT, DELETE, OPTIONS
- Credentials: Supported

## Testing & Support Tools

### Sample API Calls
```javascript
// Complete customer lifecycle example
const customerLifecycleExample = async () => {
  try {
    // 1. Create customer
    const customer = await crmClient.post('/customers/', {
      full_name: 'Ahmed Hassan',
      contact_type: 'Individual',
      email: 'ahmed.hassan@example.com',
      phone: '+212612345678',
      nationality: 'Moroccan',
      region: 'Casablanca',
      preferred_language: 'French',
      tags: ['VIP']
    });

    // 2. Log initial interaction
    const interaction = await crmClient.post('/interactions/', {
      customer_id: customer.data.id,
      channel: 'phone',
      subject: 'Initial inquiry',
      summary: 'Customer interested in Atlas Mountains tour',
      duration_minutes: 15
    });

    // 3. Submit feedback after service
    const feedback = await crmClient.post('/feedback/', {
      customer_id: customer.data.id,
      service_type: 'Tour',
      rating: 5,
      comments: 'Excellent service and beautiful scenery!'
    });

    // 4. Get customer summary
    const summary = await crmClient.get(`/customers/${customer.data.id}/summary`);

    return { customer: customer.data, summary: summary.data };
  } catch (error) {
    console.error('Customer lifecycle error:', error);
    throw error;
  }
};
```

### Mock Data Examples
```javascript
// Mock customer data
const mockCustomer = {
  id: "123e4567-e89b-12d3-a456-426614174000",
  full_name: "Ahmed Hassan",
  contact_type: "Individual",
  email: "ahmed.hassan@example.com",
  phone: "+212612345678",
  nationality: "Moroccan",
  region: "Casablanca",
  preferred_language: "French",
  loyalty_status: "Gold",
  is_active: true,
  tags: ["VIP", "Repeat Customer"],
  created_at: "2024-01-15T10:30:00Z",
  last_interaction: "2024-01-20T14:45:00Z"
};

// Mock interaction data
const mockInteraction = {
  id: "456e7890-e89b-12d3-a456-426614174001",
  customer_id: "123e4567-e89b-12d3-a456-426614174000",
  channel: "phone",
  subject: "Booking inquiry",
  summary: "Customer asking about Atlas Mountains tour availability",
  duration_minutes: 15,
  follow_up_required: true,
  follow_up_date: "2024-01-22T10:00:00Z",
  timestamp: "2024-01-20T14:45:00Z"
};

// Mock feedback data
const mockFeedback = {
  id: "789e0123-e89b-12d3-a456-426614174002",
  customer_id: "123e4567-e89b-12d3-a456-426614174000",
  service_type: "Tour",
  rating: 5,
  comments: "Amazing experience! The guide was very knowledgeable.",
  resolved: false,
  is_anonymous: false,
  source: "web",
  sentiment: "positive",
  submitted_at: "2024-01-21T16:30:00Z"
};
```

### Postman Collection Structure
```json
{
  "info": {
    "name": "CRM Service API",
    "description": "Customer relationship management endpoints"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "https://api.example.com/v1"
    },
    {
      "key": "customer_id",
      "value": "{{$guid}}"
    }
  ],
  "item": [
    {
      "name": "Customers",
      "item": [
        {
          "name": "Create Customer",
          "request": {
            "method": "POST",
            "url": "{{base_url}}/customers/",
            "body": {
              "mode": "raw",
              "raw": "{\n  \"full_name\": \"Ahmed Hassan\",\n  \"contact_type\": \"Individual\",\n  \"email\": \"ahmed@example.com\"\n}"
            }
          }
        },
        {
          "name": "Get Customer Summary",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/customers/{{customer_id}}/summary"
          }
        }
      ]
    }
  ]
}
```

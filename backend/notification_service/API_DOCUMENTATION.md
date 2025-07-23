# Notification Service API Documentation

## 1. Service Overview

**Service Name**: Notification Service  
**Purpose**: Handles multi-channel notifications (Email, SMS, Push, WhatsApp), template management, and user preferences for the Moroccan Tourist Transport ERP system.  
**Base Path**: `/api/v1`  
**Authentication**: JWT Bearer Token with RBAC  
**Required Scopes**: `notification:read`, `notification:create`, `notification:update`, `notification:delete`

## 2. Endpoint Reference

### Notification Management

#### POST /notifications/send
**Purpose**: Send notification to recipients  
**Authentication**: Required - `notification:create`

**Request Body**:
```json
{
  "type": "BOOKING_CONFIRMED",
  "recipients": [
    {
      "user_id": "uuid",
      "email": "customer@example.com",
      "phone": "+212661234567",
      "name": "Ahmed Benali"
    }
  ],
  "template_id": "uuid",
  "template_variables": {
    "customer_name": "Ahmed Benali",
    "booking_reference": "BK-2024-001",
    "tour_date": "2024-02-15"
  },
  "channels": ["EMAIL", "SMS"],
  "priority": 5,
  "scheduled_at": null,
  "source_service": "booking_service",
  "group_id": "booking_confirmation_batch_001"
}
```

**Response Structure**:
```json
[
  {
    "id": "uuid",
    "type": "BOOKING_CONFIRMED",
    "channel": "EMAIL",
    "recipient_email": "customer@example.com",
    "status": "SENT",
    "created_at": "datetime",
    "sent_at": "datetime"
  },
  {
    "id": "uuid",
    "type": "BOOKING_CONFIRMED",
    "channel": "SMS",
    "recipient_phone": "+212661234567",
    "status": "PENDING",
    "created_at": "datetime"
  }
]
```

**Success Status**: 200 OK

#### POST /notifications/send-bulk
**Purpose**: Send bulk notification to multiple recipients  
**Authentication**: Required - `notification:create`

**Request Body**:
```json
{
  "type": "TOUR_REMINDER",
  "channel": "EMAIL",
  "template_id": "uuid",
  "recipients": [
    {
      "user_id": "uuid1",
      "email": "customer1@example.com",
      "name": "Customer 1"
    },
    {
      "user_id": "uuid2",
      "email": "customer2@example.com",
      "name": "Customer 2"
    }
  ],
  "template_variables": {
    "tour_date": "2024-02-20",
    "meeting_point": "Hotel Atlas"
  },
  "priority": 3,
  "group_id": "tour_reminder_batch_001"
}
```

**Response Structure**:
```json
{
  "total_sent": 2,
  "successful": 2,
  "failed": 0,
  "group_id": "tour_reminder_batch_001"
}
```

#### GET /notifications
**Purpose**: Retrieve notifications with filtering  
**Authentication**: Required - `notification:read`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| page | integer | 1 | No | Page number for pagination |
| size | integer | 20 | No | Number of notifications per page |
| type | string | null | No | Filter by notification type |
| channel | string | null | No | Filter by channel (EMAIL, SMS, PUSH) |
| status | string | null | No | Filter by status |
| recipient_id | string | null | No | Filter by recipient ID |
| created_from | string | null | No | Start date (ISO datetime) |
| created_to | string | null | No | End date (ISO datetime) |
| source_service | string | null | No | Filter by source service |

#### GET /notifications/{notification_id}
**Purpose**: Retrieve specific notification details  
**Authentication**: Required - `notification:read`

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| notification_id | string (UUID) | Yes | Notification identifier |

#### GET /notifications/stats
**Purpose**: Get notification statistics  
**Authentication**: Required - `notification:read`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| days | integer | 30 | No | Number of days for statistics |

**Response Structure**:
```json
{
  "total_notifications": 1250,
  "by_status": {
    "sent": 1100,
    "delivered": 1050,
    "failed": 50,
    "pending": 50
  },
  "by_channel": {
    "email": 800,
    "sms": 350,
    "push": 100
  },
  "delivery_rate": 95.5,
  "failed_notifications": 50,
  "retry_rate": 15.2
}
```

### Template Management

#### GET /templates
**Purpose**: Retrieve notification templates  
**Authentication**: Required - `notification:read`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| type | string | null | No | Filter by template type |
| channel | string | null | No | Filter by channel |
| language | string | null | No | Filter by language |
| is_active | boolean | null | No | Filter by active status |

#### POST /templates
**Purpose**: Create new notification template  
**Authentication**: Required - `notification:create`

**Request Body**:
```json
{
  "name": "booking_confirmation_email",
  "description": "Email template for booking confirmations",
  "type": "TRANSACTIONAL",
  "channel": "EMAIL",
  "subject": "Booking Confirmation - {booking_reference}",
  "body": "Dear {customer_name},\n\nYour booking {booking_reference} has been confirmed for {tour_date}.\n\nThank you for choosing our services!",
  "variables": {
    "customer_name": {"type": "string", "required": true},
    "booking_reference": {"type": "string", "required": true},
    "tour_date": {"type": "string", "required": true}
  },
  "default_values": {
    "company_name": "Atlas Tours Morocco"
  },
  "content_type": "text",
  "language": "en"
}
```

**Success Status**: 201 Created

#### GET /templates/{template_id}
**Purpose**: Retrieve specific template  
**Authentication**: Required - `notification:read`

#### PUT /templates/{template_id}
**Purpose**: Update template  
**Authentication**: Required - `notification:update`

#### POST /templates/preview
**Purpose**: Preview template with variables  
**Authentication**: Required - `notification:read`

**Request Body**:
```json
{
  "template_id": "uuid",
  "variables": {
    "customer_name": "Ahmed Benali",
    "booking_reference": "BK-2024-001",
    "tour_date": "February 15, 2024"
  },
  "recipient_info": {
    "email": "ahmed@example.com",
    "name": "Ahmed Benali"
  }
}
```

**Response Structure**:
```json
{
  "subject": "Booking Confirmation - BK-2024-001",
  "body": "Dear Ahmed Benali,\n\nYour booking BK-2024-001 has been confirmed for February 15, 2024.\n\nThank you for choosing our services!",
  "variables_used": {
    "customer_name": "Ahmed Benali",
    "booking_reference": "BK-2024-001",
    "tour_date": "February 15, 2024"
  },
  "missing_variables": [],
  "validation_errors": []
}
```

### User Preferences

#### GET /preferences/{user_id}
**Purpose**: Get user notification preferences  
**Authentication**: Required - `notification:read`

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| user_id | string (UUID) | Yes | User identifier |

**Response Structure**:
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "user_type": "customer",
  "email": "customer@example.com",
  "phone": "+212661234567",
  "email_enabled": true,
  "sms_enabled": true,
  "push_enabled": false,
  "whatsapp_enabled": true,
  "notification_preferences": {
    "booking_confirmed": {
      "email": true,
      "sms": true,
      "push": false
    },
    "tour_reminder": {
      "email": true,
      "sms": false,
      "push": false
    }
  },
  "quiet_hours_enabled": true,
  "quiet_hours_start": "22:00",
  "quiet_hours_end": "08:00",
  "preferred_language": "fr",
  "is_active": true
}
```

#### PUT /preferences/{user_id}
**Purpose**: Update user notification preferences  
**Authentication**: Required - `notification:update`

**Request Body**:
```json
{
  "email_enabled": true,
  "sms_enabled": false,
  "push_enabled": true,
  "notification_preferences": {
    "booking_confirmed": {
      "email": true,
      "sms": false,
      "push": true
    }
  },
  "quiet_hours_enabled": true,
  "quiet_hours_start": "23:00",
  "quiet_hours_end": "07:00",
  "preferred_language": "ar"
}
```

#### PUT /preferences/{user_id}/contact
**Purpose**: Update user contact information  
**Authentication**: Required - `notification:update`

**Query Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| email | string | No | Email address |
| phone | string | No | Phone number |
| push_token | string | No | Push notification token |

### Notification Logs

#### GET /logs/{recipient_id}
**Purpose**: Get notification history for recipient  
**Authentication**: Required - `notification:read`

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| recipient_id | string | Yes | Recipient identifier |

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| type | string | null | No | Filter by notification type |
| channel | string | null | No | Filter by channel |
| status | string | null | No | Filter by status |
| created_from | string | null | No | Start date (ISO datetime) |
| created_to | string | null | No | End date (ISO datetime) |

#### GET /logs/{recipient_id}/summary
**Purpose**: Get notification summary for recipient  
**Authentication**: Required - `notification:read`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| days | integer | 30 | No | Number of days for summary |

**Response Structure**:
```json
{
  "recipient_id": "customer123",
  "period_days": 30,
  "total_notifications": 25,
  "by_status": {
    "sent": 22,
    "delivered": 20,
    "failed": 3
  },
  "by_channel": {
    "email": 15,
    "sms": 8,
    "push": 2
  },
  "by_type": {
    "booking_confirmed": 5,
    "tour_reminder": 10,
    "payment_received": 3
  }
}
```

## 3. Data Models

### Notification Model
```json
{
  "id": "uuid",
  "type": "enum (BOOKING_CONFIRMED, TOUR_REMINDER, etc.)",
  "channel": "enum (EMAIL, SMS, PUSH, WHATSAPP)",
  "recipient_type": "enum (USER, CUSTOMER, EMPLOYEE)",
  "recipient_id": "string (optional)",
  "recipient_email": "string (max 255, optional)",
  "recipient_phone": "string (max 20, optional)",
  "recipient_name": "string (max 255, optional)",
  "subject": "string (max 500, optional)",
  "message": "string (max 5000)",
  "payload": "object (optional)",
  "template_id": "uuid (optional)",
  "template_variables": "object (optional)",
  "status": "enum (PENDING, SENT, DELIVERED, FAILED)",
  "retry_count": "integer (default 0)",
  "max_retries": "integer (default 3)",
  "priority": "integer (1-10, default 5)",
  "scheduled_at": "datetime (optional)",
  "expires_at": "datetime (optional)",
  "sent_at": "datetime (optional)",
  "delivered_at": "datetime (optional)",
  "failed_at": "datetime (optional)",
  "error_message": "string (max 1000, optional)",
  "source_service": "string (max 50, optional)",
  "group_id": "string (max 100, optional)",
  "created_at": "datetime"
}
```

### Template Model
```json
{
  "id": "uuid",
  "name": "string (max 100, unique)",
  "description": "string (max 500, optional)",
  "type": "enum (TRANSACTIONAL, MARKETING, SYSTEM, ALERT)",
  "channel": "enum (EMAIL, SMS, PUSH, WHATSAPP)",
  "subject": "string (max 500, optional)",
  "body": "string (max 10000)",
  "variables": "object (optional)",
  "default_values": "object (optional)",
  "content_type": "string (default 'text')",
  "language": "string (max 5, default 'en')",
  "is_active": "boolean (default true)",
  "version": "integer (default 1)",
  "usage_count": "integer (default 0)",
  "last_used_at": "datetime (optional)",
  "is_validated": "boolean (default false)",
  "validation_errors": "string (max 1000, optional)",
  "created_by": "uuid (optional)",
  "created_at": "datetime"
}
```

### UserPreference Model
```json
{
  "id": "uuid",
  "user_id": "uuid (unique)",
  "user_type": "string (max 20, default 'user')",
  "email": "string (max 255, optional)",
  "phone": "string (max 20, optional)",
  "push_token": "string (max 500, optional)",
  "email_enabled": "boolean (default true)",
  "sms_enabled": "boolean (default true)",
  "push_enabled": "boolean (default true)",
  "whatsapp_enabled": "boolean (default false)",
  "notification_preferences": "object (optional)",
  "quiet_hours_enabled": "boolean (default false)",
  "quiet_hours_start": "string (max 5, optional)",
  "quiet_hours_end": "string (max 5, optional)",
  "quiet_hours_timezone": "string (max 50, default 'Africa/Casablanca')",
  "max_emails_per_day": "integer (optional)",
  "max_sms_per_day": "integer (optional)",
  "preferred_language": "string (max 5, default 'en')",
  "preferred_timezone": "string (max 50, default 'Africa/Casablanca')",
  "is_active": "boolean (default true)",
  "created_at": "datetime"
}
```

## 4. Frontend Integration Guidelines

### HTTP Client Configuration
```javascript
// Axios configuration for Notification Service
const notificationApiClient = axios.create({
  baseURL: 'https://api.example.com/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor
notificationApiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor
notificationApiClient.interceptors.response.use(
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

### Real-time Notifications
```javascript
// WebSocket connection for real-time notification status
const connectNotificationWebSocket = (userId) => {
  const ws = new WebSocket(`wss://api.example.com/ws/notifications/${userId}`);
  
  ws.onmessage = (event) => {
    const notification = JSON.parse(event.data);
    handleNotificationUpdate(notification);
  };
  
  return ws;
};
```

### Error Handling Pattern
```javascript
// Notification service specific error handling
const handleNotificationError = (error) => {
  if (error.response?.status === 422) {
    // Template validation errors
    return error.response.data.errors || [];
  }
  if (error.response?.status === 429) {
    // Rate limiting
    return [{ message: 'Too many notifications sent. Please try again later.' }];
  }
  return [{ message: error.response?.data?.detail || 'Notification failed' }];
};
```

### Rate Limiting
- Email: 100 per minute, 1000 per hour
- SMS: 50 per minute, 500 per hour
- Push: 200 per minute, 2000 per hour
- Standard HTTP 429 response if limits exceeded

### CORS Policy
- Allowed origins: `http://localhost:3000`, `http://localhost:8080`
- Credentials allowed: Yes
- Methods: GET, POST, PUT, DELETE

## 5. Testing & Support Tools

### Example API Calls

#### Send Single Notification
```bash
curl -X POST "https://api.example.com/api/v1/notifications/send" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "BOOKING_CONFIRMED",
    "recipients": [
      {
        "email": "customer@example.com",
        "name": "Ahmed Benali"
      }
    ],
    "template_id": "uuid",
    "template_variables": {
      "customer_name": "Ahmed Benali",
      "booking_reference": "BK-2024-001"
    },
    "channels": ["EMAIL"]
  }'
```

#### Create Template
```bash
curl -X POST "https://api.example.com/api/v1/templates" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "tour_reminder_sms",
    "type": "TRANSACTIONAL",
    "channel": "SMS",
    "body": "Reminder: Your tour {tour_name} starts tomorrow at {start_time}. Meeting point: {meeting_point}",
    "variables": {
      "tour_name": {"type": "string", "required": true},
      "start_time": {"type": "string", "required": true},
      "meeting_point": {"type": "string", "required": true}
    }
  }'
```

#### Update User Preferences
```bash
curl -X PUT "https://api.example.com/api/v1/preferences/uuid" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email_enabled": true,
    "sms_enabled": false,
    "notification_preferences": {
      "booking_confirmed": {
        "email": true,
        "sms": false
      }
    }
  }'
```

### Sample Postman Collection Structure
```json
{
  "info": {
    "name": "Notification Service API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "auth": {
    "type": "bearer",
    "bearer": [{"key": "token", "value": "{{access_token}}"}]
  },
  "item": [
    {
      "name": "Notifications",
      "item": [
        {"name": "Send Notification", "request": {"method": "POST", "url": "{{base_url}}/notifications/send"}},
        {"name": "Get Notifications", "request": {"method": "GET", "url": "{{base_url}}/notifications"}},
        {"name": "Get Stats", "request": {"method": "GET", "url": "{{base_url}}/notifications/stats"}}
      ]
    },
    {
      "name": "Templates",
      "item": [
        {"name": "Get Templates", "request": {"method": "GET", "url": "{{base_url}}/templates"}},
        {"name": "Create Template", "request": {"method": "POST", "url": "{{base_url}}/templates"}},
        {"name": "Preview Template", "request": {"method": "POST", "url": "{{base_url}}/templates/preview"}}
      ]
    }
  ]
}
```

### Common Frontend Patterns
```javascript
// Send notification
const sendNotification = async (notificationData) => {
  const response = await notificationApiClient.post('/notifications/send', notificationData);
  return response.data;
};

// Template management
const createTemplate = async (templateData) => {
  const response = await notificationApiClient.post('/templates', templateData);
  return response.data;
};

const previewTemplate = async (templateId, variables) => {
  const response = await notificationApiClient.post('/templates/preview', {
    template_id: templateId,
    variables: variables
  });
  return response.data;
};

// User preferences
const getUserPreferences = async (userId) => {
  const response = await notificationApiClient.get(`/preferences/${userId}`);
  return response.data;
};

const updatePreferences = async (userId, preferences) => {
  const response = await notificationApiClient.put(`/preferences/${userId}`, preferences);
  return response.data;
};

// Notification history
const getNotificationHistory = async (recipientId, filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await notificationApiClient.get(`/logs/${recipientId}?${params}`);
  return response.data;
};
```

### Mock Data Examples
```javascript
// Mock notification data
const mockNotifications = [
  {
    id: "550e8400-e29b-41d4-a716-446655440000",
    type: "BOOKING_CONFIRMED",
    channel: "EMAIL",
    recipient_email: "customer@example.com",
    subject: "Booking Confirmation - BK-2024-001",
    status: "DELIVERED",
    sent_at: "2024-01-15T10:30:00Z",
    delivered_at: "2024-01-15T10:30:15Z"
  }
];

// Mock template data
const mockTemplates = [
  {
    id: "550e8400-e29b-41d4-a716-446655440001",
    name: "booking_confirmation_email",
    type: "TRANSACTIONAL",
    channel: "EMAIL",
    subject: "Booking Confirmation - {booking_reference}",
    is_active: true,
    usage_count: 150
  }
];

// Mock user preferences
const mockUserPreferences = {
  id: "550e8400-e29b-41d4-a716-446655440002",
  user_id: "550e8400-e29b-41d4-a716-446655440003",
  email_enabled: true,
  sms_enabled: true,
  push_enabled: false,
  notification_preferences: {
    booking_confirmed: {
      email: true,
      sms: true,
      push: false
    },
    tour_reminder: {
      email: true,
      sms: false,
      push: false
    }
  }
};
```
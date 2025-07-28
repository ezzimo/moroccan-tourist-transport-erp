# Booking & Reservation Service API Documentation

## Service Overview

**Service Name**: Booking & Reservation Service  
**Purpose**: Manages customer bookings, reservations, pricing, and availability for tourist transport services.  
**Base Path**: `/api/v1`  
**Authentication**: JWT Bearer tokens with RBAC permissions

## Endpoint Reference

### Booking Management Endpoints

#### POST /bookings/
**Purpose**: Create a new booking

**Authentication Requirements**: Bearer token with `booking:create:bookings` permission

**Request Body Schema**:
```json
{
  "customer_id": "uuid (required)",
  "service_type": "string (enum: Tour, Transfer, Custom Package, required)",
  "pax_count": "integer (1-50, required)",
  "lead_passenger_name": "string (required)",
  "lead_passenger_email": "string (email format, required)",
  "lead_passenger_phone": "string (required)",
  "start_date": "date (YYYY-MM-DD, required)",
  "end_date": "date (YYYY-MM-DD, optional)",
  "base_price": "decimal (required)",
  "promo_code": "string (optional)",
  "payment_method": "string (optional)",
  "special_requests": "string (optional)"
}
```

**Request Example**:
```bash
curl -X POST "https://api.example.com/v1/bookings/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "123e4567-e89b-12d3-a456-426614174000",
    "service_type": "Tour",
    "pax_count": 4,
    "lead_passenger_name": "Ahmed Hassan",
    "lead_passenger_email": "ahmed@example.com",
    "lead_passenger_phone": "+212612345678",
    "start_date": "2024-03-15",
    "end_date": "2024-03-18",
    "base_price": 2500.00,
    "special_requests": "Vegetarian meals preferred"
  }'
```

**Response Structure**:
```json
{
  "id": "uuid",
  "customer_id": "uuid",
  "service_type": "string",
  "status": "string (enum: Pending, Confirmed, Cancelled, Expired)",
  "pax_count": "integer",
  "lead_passenger_name": "string",
  "lead_passenger_email": "string",
  "lead_passenger_phone": "string",
  "start_date": "date",
  "end_date": "date",
  "base_price": "decimal",
  "discount_amount": "decimal",
  "total_price": "decimal",
  "currency": "string",
  "payment_status": "string (enum: Pending, Partial, Paid, Failed)",
  "payment_method": "string",
  "special_requests": "string",
  "created_at": "datetime",
  "expires_at": "datetime"
}
```

**Success Status Codes**:
- `201 Created`: Booking created successfully

#### GET /bookings/
**Purpose**: Get list of bookings with optional filters

**Authentication Requirements**: Bearer token with `booking:read:bookings` permission

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| page | integer | 1 | No | Page number |
| size | integer | 20 | No | Items per page |
| customer_id | uuid | - | No | Filter by customer |
| status | string | - | No | Filter by booking status |
| service_type | string | - | No | Filter by service type |
| start_date_from | date | - | No | Filter by start date from |
| start_date_to | date | - | No | Filter by start date to |

**Response Structure**:
```json
{
  "items": ["Booking objects"],
  "total": "integer",
  "page": "integer",
  "size": "integer",
  "pages": "integer"
}
```

#### GET /bookings/{booking_id}
**Purpose**: Get booking by ID

**Authentication Requirements**: Bearer token with `booking:read:bookings` permission

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| booking_id | uuid | Yes | Booking identifier |

#### POST /bookings/{booking_id}/confirm
**Purpose**: Confirm a pending booking

**Authentication Requirements**: Bearer token with `booking:update:bookings` permission

**Request Body Schema**:
```json
{
  "payment_reference": "string (optional)",
  "internal_notes": "string (optional)"
}
```

#### POST /bookings/{booking_id}/cancel
**Purpose**: Cancel a booking

**Authentication Requirements**: Bearer token with `booking:update:bookings` permission

**Request Body Schema**:
```json
{
  "reason": "string (required)",
  "refund_amount": "decimal (optional)",
  "internal_notes": "string (optional)"
}
```

#### GET /bookings/{booking_id}/voucher
**Purpose**: Generate and download booking voucher PDF

**Authentication Requirements**: Bearer token with `booking:read:bookings` permission

**Response**: PDF file download

### Pricing Endpoints

#### POST /pricing/calculate
**Purpose**: Calculate pricing with applicable discounts

**Authentication Requirements**: Bearer token with `booking:read:pricing` permission

**Request Body Schema**:
```json
{
  "service_type": "string (required)",
  "base_price": "decimal (required)",
  "pax_count": "integer (required)",
  "start_date": "date (required)",
  "end_date": "date (optional)",
  "customer_id": "uuid (optional)",
  "promo_code": "string (optional)"
}
```

**Response Structure**:
```json
{
  "base_price": "decimal",
  "discount_amount": "decimal",
  "total_price": "decimal",
  "applied_rules": [
    {
      "rule_id": "uuid",
      "rule_name": "string",
      "discount_type": "string",
      "discount_amount": "decimal"
    }
  ],
  "currency": "string"
}
```

### Availability Endpoints

#### POST /availability/check
**Purpose**: Check availability for resources

**Authentication Requirements**: Bearer token with `booking:read:availability` permission

**Request Body Schema**:
```json
{
  "resource_type": "string (enum: Vehicle, Guide, Accommodation, optional)",
  "resource_ids": ["uuid (optional)"],
  "start_date": "date (required)",
  "end_date": "date (optional)",
  "required_capacity": "integer (default: 1)",
  "service_type": "string (optional)"
}
```

**Response Structure**:
```json
{
  "request_date": "date",
  "end_date": "date",
  "required_capacity": "integer",
  "available_resources": [
    {
      "resource_id": "uuid",
      "resource_name": "string",
      "resource_type": "string",
      "date": "date",
      "total_capacity": "integer",
      "available_capacity": "integer",
      "is_available": "boolean"
    }
  ],
  "total_available": "integer",
  "has_availability": "boolean"
}
```

### Reservation Items Endpoints

#### POST /reservation-items/
**Purpose**: Add a reservation item to a booking

**Authentication Requirements**: Bearer token with `booking:create:reservation_items` permission

**Request Body Schema**:
```json
{
  "booking_id": "uuid (required)",
  "type": "string (enum: Accommodation, Transport, Activity, Guide, Meal, required)",
  "reference_id": "uuid (optional)",
  "name": "string (required)",
  "description": "string (optional)",
  "quantity": "integer (default: 1)",
  "unit_price": "decimal (required)",
  "specifications": "object (optional)",
  "notes": "string (optional)"
}
```

#### GET /reservation-items/booking/{booking_id}
**Purpose**: Get all reservation items for a booking

**Authentication Requirements**: Bearer token with `booking:read:reservation_items` permission

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| booking_id | uuid | Yes | Booking identifier |

## Data Models

### Booking Model
```json
{
  "id": "uuid",
  "customer_id": "uuid (foreign key to CRM service)",
  "service_type": "string (enum: Tour, Transfer, Custom Package, Accommodation, Activity)",
  "status": "string (enum: Pending, Confirmed, Cancelled, Refunded, Expired)",
  "pax_count": "integer (1-50)",
  "lead_passenger_name": "string (max 255 chars)",
  "lead_passenger_email": "string (email format)",
  "lead_passenger_phone": "string (max 20 chars)",
  "start_date": "date",
  "end_date": "date (optional)",
  "base_price": "decimal (precision 10,2)",
  "discount_amount": "decimal (precision 10,2, default: 0)",
  "total_price": "decimal (precision 10,2)",
  "currency": "string (default: MAD)",
  "payment_status": "string (enum: Pending, Partial, Paid, Failed, Refunded)",
  "payment_method": "string (optional)",
  "payment_reference": "string (optional)",
  "special_requests": "string (max 2000 chars, optional)",
  "internal_notes": "string (max 2000 chars, optional)",
  "cancellation_reason": "string (optional)",
  "cancelled_by": "uuid (optional)",
  "cancelled_at": "datetime (optional)",
  "created_at": "datetime",
  "updated_at": "datetime",
  "confirmed_at": "datetime (optional)",
  "expires_at": "datetime (optional)"
}
```

### ReservationItem Model
```json
{
  "id": "uuid",
  "booking_id": "uuid (foreign key)",
  "type": "string (enum: Accommodation, Transport, Activity, Guide, Meal, Insurance)",
  "reference_id": "uuid (optional, foreign key to external service)",
  "name": "string (max 255 chars)",
  "description": "string (max 1000 chars, optional)",
  "quantity": "integer (default: 1)",
  "unit_price": "decimal (precision 10,2)",
  "total_price": "decimal (precision 10,2)",
  "specifications": "object (JSON, optional)",
  "notes": "string (max 500 chars, optional)",
  "is_confirmed": "boolean (default: false)",
  "is_cancelled": "boolean (default: false)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### PricingRule Model
```json
{
  "id": "uuid",
  "name": "string (max 255 chars, unique)",
  "description": "string (max 1000 chars, optional)",
  "code": "string (max 50 chars, unique, optional)",
  "discount_type": "string (enum: Percentage, Fixed Amount, Buy X Get Y, Early Bird, Group Discount)",
  "discount_percentage": "decimal (precision 5,2, optional)",
  "discount_amount": "decimal (precision 10,2, optional)",
  "conditions": "object (JSON)",
  "valid_from": "date",
  "valid_until": "date",
  "max_uses": "integer (optional)",
  "max_uses_per_customer": "integer (default: 1)",
  "current_uses": "integer (default: 0)",
  "priority": "integer (default: 0)",
  "is_active": "boolean (default: true)",
  "is_combinable": "boolean (default: false)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Frontend Integration Guidelines

### HTTP Client Configuration
```javascript
// Axios configuration for booking service
import axios from 'axios';

const bookingClient = axios.create({
  baseURL: 'https://api.example.com/v1',
  timeout: 15000, // Longer timeout for booking operations
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
bookingClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor with booking-specific error handling
bookingClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 409) {
      // Booking conflict (double booking, etc.)
      return Promise.reject({
        type: 'BOOKING_CONFLICT',
        message: error.response.data.detail
      });
    }
    return Promise.reject(error);
  }
);
```

### Booking Flow Implementation
```javascript
// Complete booking flow
class BookingService {
  // Step 1: Check availability
  async checkAvailability(availabilityRequest) {
    const response = await bookingClient.post('/availability/check', availabilityRequest);
    return response.data;
  }

  // Step 2: Calculate pricing
  async calculatePricing(pricingRequest) {
    const response = await bookingClient.post('/pricing/calculate', pricingRequest);
    return response.data;
  }

  // Step 3: Create booking
  async createBooking(bookingData) {
    const response = await bookingClient.post('/bookings/', bookingData);
    return response.data;
  }

  // Step 4: Add reservation items
  async addReservationItem(itemData) {
    const response = await bookingClient.post('/reservation-items/', itemData);
    return response.data;
  }

  // Step 5: Confirm booking
  async confirmBooking(bookingId, confirmData) {
    const response = await bookingClient.post(`/bookings/${bookingId}/confirm`, confirmData);
    return response.data;
  }

  // Get booking with items
  async getBookingDetails(bookingId) {
    const [booking, items] = await Promise.all([
      bookingClient.get(`/bookings/${bookingId}`),
      bookingClient.get(`/reservation-items/booking/${bookingId}`)
    ]);
    
    return {
      ...booking.data,
      items: items.data
    };
  }
}
```

### Error Handling Patterns
```javascript
// Booking-specific error handler
function handleBookingError(error) {
  if (error.type === 'BOOKING_CONFLICT') {
    return {
      type: 'conflict',
      message: 'This time slot is no longer available',
      action: 'refresh_availability'
    };
  }

  if (error.response?.status === 402) {
    return {
      type: 'payment_required',
      message: 'Payment is required to complete booking',
      action: 'redirect_payment'
    };
  }

  // Standard error handling
  return handleApiError(error);
}
```

### Rate Limiting
- Booking creation: 10 per minute per user
- Availability checks: 60 per minute per user
- Pricing calculations: 100 per minute per user

### CORS Policy
- Allowed origins: Frontend domains (configurable)
- Allowed methods: GET, POST, PUT, DELETE, OPTIONS
- Credentials: Supported for authentication

## Testing & Support Tools

### Sample API Calls
```javascript
// Create a complete booking
const createCompleteBooking = async () => {
  try {
    // 1. Check availability
    const availability = await bookingService.checkAvailability({
      start_date: '2024-03-15',
      end_date: '2024-03-18',
      required_capacity: 4,
      service_type: 'Tour'
    });

    if (!availability.has_availability) {
      throw new Error('No availability for selected dates');
    }

    // 2. Calculate pricing
    const pricing = await bookingService.calculatePricing({
      service_type: 'Tour',
      base_price: 2500.00,
      pax_count: 4,
      start_date: '2024-03-15',
      promo_code: 'EARLY2024'
    });

    // 3. Create booking
    const booking = await bookingService.createBooking({
      customer_id: 'customer-uuid',
      service_type: 'Tour',
      pax_count: 4,
      lead_passenger_name: 'Ahmed Hassan',
      lead_passenger_email: 'ahmed@example.com',
      lead_passenger_phone: '+212612345678',
      start_date: '2024-03-15',
      end_date: '2024-03-18',
      base_price: pricing.total_price
    });

    // 4. Add accommodation
    await bookingService.addReservationItem({
      booking_id: booking.id,
      type: 'Accommodation',
      name: 'Hotel Atlas Asni',
      quantity: 2,
      unit_price: 800.00
    });

    return booking;
  } catch (error) {
    console.error('Booking creation failed:', error);
    throw error;
  }
};
```

### Mock Data Examples
```javascript
// Mock booking data for testing
const mockBooking = {
  id: "123e4567-e89b-12d3-a456-426614174000",
  customer_id: "456e7890-e89b-12d3-a456-426614174001",
  service_type: "Tour",
  status: "Confirmed",
  pax_count: 4,
  lead_passenger_name: "Ahmed Hassan",
  lead_passenger_email: "ahmed@example.com",
  lead_passenger_phone: "+212612345678",
  start_date: "2024-03-15",
  end_date: "2024-03-18",
  base_price: 2500.00,
  discount_amount: 250.00,
  total_price: 2250.00,
  currency: "MAD",
  payment_status: "Paid",
  created_at: "2024-01-15T10:30:00Z"
};

// Mock availability response
const mockAvailability = {
  request_date: "2024-03-15",
  end_date: "2024-03-18",
  required_capacity: 4,
  available_resources: [
    {
      resource_id: "vehicle-uuid",
      resource_name: "Mercedes Sprinter",
      resource_type: "Vehicle",
      date: "2024-03-15",
      total_capacity: 16,
      available_capacity: 12,
      is_available: true
    }
  ],
  total_available: 1,
  has_availability: true
};
```

### Postman Collection Structure
```json
{
  "info": {
    "name": "Booking Service API",
    "description": "Booking and reservation management endpoints"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "https://api.example.com/v1"
    },
    {
      "key": "booking_id",
      "value": "{{$guid}}"
    }
  ],
  "item": [
    {
      "name": "Bookings",
      "item": [
        {
          "name": "Create Booking",
          "request": {
            "method": "POST",
            "url": "{{base_url}}/bookings/",
            "body": {
              "mode": "raw",
              "raw": "{\n  \"customer_id\": \"{{customer_id}}\",\n  \"service_type\": \"Tour\",\n  \"pax_count\": 4\n}"
            }
          }
        }
      ]
    }
  ]
}
```

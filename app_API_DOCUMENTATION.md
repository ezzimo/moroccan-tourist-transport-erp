# Authentication & Authorization Service API Documentation

## Service Overview

**Service Name**: Authentication & Authorization Service  
**Purpose**: Provides secure authentication, authorization, and user management for the Moroccan Tourist Transport ERP system.  
**Base Path**: `/api/v1`  
**Authentication**: JWT Bearer tokens with Role-Based Access Control (RBAC)

## Endpoint Reference

### Authentication Endpoints

#### POST /auth/login
**Purpose**: Authenticate user and return JWT token

**Authentication Requirements**: None (public endpoint)

**Request Body Schema**:
```json
{
  "email": "string (email format, required)",
  "password": "string (required)"
}
```

**Request Example**:
```bash
curl -X POST "https://api.example.com/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

**Response Structure**:
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": "integer (seconds)",
  "user": {
    "id": "uuid",
    "full_name": "string",
    "email": "string",
    "is_active": "boolean",
    "roles": ["string"]
  }
}
```

**Success Status Codes**:
- `200 OK`: Login successful

**Error Responses**:
```json
{
  "detail": "string",
  "error_code": "string"
}
```
- `401 Unauthorized`: Invalid credentials
- `400 Bad Request`: Invalid input data
- `429 Too Many Requests`: Rate limit exceeded

#### POST /auth/logout
**Purpose**: Logout user by blacklisting token

**Authentication Requirements**: Bearer token required

**Request Example**:
```bash
curl -X POST "https://api.example.com/v1/auth/logout" \
  -H "Authorization: Bearer <token>"
```

**Response Structure**:
```json
{
  "message": "Successfully logged out"
}
```

#### GET /auth/me
**Purpose**: Get current user information and permissions

**Authentication Requirements**: Bearer token required

**Response Structure**:
```json
{
  "permissions": ["string"],
  "roles": ["string"]
}
```

#### POST /auth/send-otp
**Purpose**: Send OTP to user's email/phone

**Authentication Requirements**: None (public endpoint)

**Request Body Schema**:
```json
{
  "email": "string (email format, required)"
}
```

**Response Structure**:
```json
{
  "message": "OTP sent to email",
  "expires_in": "integer (seconds)"
}
```

#### POST /auth/verify-otp
**Purpose**: Verify OTP code

**Authentication Requirements**: None (public endpoint)

**Request Body Schema**:
```json
{
  "email": "string (email format, required)",
  "otp_code": "string (required)"
}
```

### User Management Endpoints

#### POST /users/
**Purpose**: Create a new user

**Authentication Requirements**: Bearer token with `auth:create:users` permission

**Request Body Schema**:
```json
{
  "full_name": "string (required)",
  "email": "string (email format, required)",
  "phone": "string (required)",
  "password": "string (required)",
  "role_ids": ["uuid (optional)"]
}
```

#### GET /users/
**Purpose**: Get list of users

**Authentication Requirements**: Bearer token with `auth:read:users` permission

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| skip | integer | 0 | No | Number of records to skip |
| limit | integer | 100 | No | Maximum records to return |

**Response Structure**:
```json
[
  {
    "id": "uuid",
    "full_name": "string",
    "email": "string",
    "phone": "string",
    "is_active": "boolean",
    "is_verified": "boolean",
    "created_at": "datetime",
    "updated_at": "datetime",
    "last_login": "datetime"
  }
]
```

#### GET /users/{user_id}
**Purpose**: Get user by ID with roles

**Authentication Requirements**: Bearer token with `auth:read:users` permission

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| user_id | uuid | Yes | User identifier |

**Response Structure**:
```json
{
  "id": "uuid",
  "full_name": "string",
  "email": "string",
  "phone": "string",
  "is_active": "boolean",
  "is_verified": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime",
  "last_login": "datetime",
  "roles": [
    {
      "id": "uuid",
      "name": "string",
      "description": "string"
    }
  ]
}
```

### Role Management Endpoints

#### POST /roles/
**Purpose**: Create a new role

**Authentication Requirements**: Bearer token with `auth:create:roles` permission

**Request Body Schema**:
```json
{
  "name": "string (required)",
  "description": "string (optional)",
  "permission_ids": ["uuid (optional)"]
}
```

#### GET /roles/
**Purpose**: Get list of roles

**Authentication Requirements**: Bearer token with `auth:read:roles` permission

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| skip | integer | 0 | No | Number of records to skip |
| limit | integer | 100 | No | Maximum records to return |

#### POST /roles/permissions
**Purpose**: Create a new permission

**Authentication Requirements**: Bearer token with `auth:create:permissions` permission

**Request Body Schema**:
```json
{
  "service_name": "string (required)",
  "action": "string (required)",
  "resource": "string (default: '*')"
}
```

## Data Models

### User Model
```json
{
  "id": "uuid",
  "full_name": "string (max 255 chars, required)",
  "email": "string (email format, unique, required)",
  "phone": "string (max 20 chars, required)",
  "password_hash": "string (hashed, required)",
  "is_active": "boolean (default: true)",
  "is_verified": "boolean (default: false)",
  "created_at": "datetime",
  "updated_at": "datetime",
  "last_login": "datetime",
  "roles": ["Role objects"]
}
```

### Role Model
```json
{
  "id": "uuid",
  "name": "string (max 100 chars, unique, required)",
  "description": "string (max 500 chars, optional)",
  "created_at": "datetime",
  "updated_at": "datetime",
  "permissions": ["Permission objects"]
}
```

### Permission Model
```json
{
  "id": "uuid",
  "service_name": "string (max 100 chars, required)",
  "action": "string (max 50 chars, required)",
  "resource": "string (max 100 chars, default: '*')",
  "created_at": "datetime"
}
```

## Frontend Integration Guidelines

### HTTP Client Configuration
```javascript
// Axios configuration
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'https://api.example.com/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired, redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### Authentication Flow
```javascript
// Login function
async function login(email, password) {
  try {
    const response = await apiClient.post('/auth/login', {
      email,
      password
    });
    
    const { access_token, expires_in, user } = response.data;
    
    // Store token and user info
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('user', JSON.stringify(user));
    
    // Set token expiry
    const expiryTime = Date.now() + (expires_in * 1000);
    localStorage.setItem('token_expiry', expiryTime.toString());
    
    return { success: true, user };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Login failed' 
    };
  }
}

// Logout function
async function logout() {
  try {
    await apiClient.post('/auth/logout');
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    localStorage.removeItem('token_expiry');
    window.location.href = '/login';
  }
}

// Check if user is authenticated
function isAuthenticated() {
  const token = localStorage.getItem('access_token');
  const expiry = localStorage.getItem('token_expiry');
  
  if (!token || !expiry) return false;
  
  return Date.now() < parseInt(expiry);
}
```

### Error Handling Pattern
```javascript
// Standard error handler
function handleApiError(error) {
  if (error.response) {
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        return { message: 'Invalid request data', details: data.detail };
      case 401:
        return { message: 'Authentication required', redirect: '/login' };
      case 403:
        return { message: 'Access denied', details: data.detail };
      case 404:
        return { message: 'Resource not found' };
      case 429:
        return { message: 'Too many requests, please try again later' };
      case 500:
        return { message: 'Server error, please try again' };
      default:
        return { message: 'An unexpected error occurred' };
    }
  }
  
  return { message: 'Network error, please check your connection' };
}
```

### Rate Limiting
- Login attempts: 5 per minute per IP
- OTP requests: 3 per minute per email
- General API calls: No specific limit (monitored)

### CORS Policy
- Allowed origins: Configurable via environment variables
- Allowed methods: GET, POST, PUT, DELETE, OPTIONS
- Allowed headers: Content-Type, Authorization
- Credentials: Supported

## Testing & Support Tools

### Sample API Calls
```javascript
// Get current user
const getCurrentUser = async () => {
  const response = await apiClient.get('/auth/me');
  return response.data;
};

// Create user
const createUser = async (userData) => {
  const response = await apiClient.post('/users/', userData);
  return response.data;
};

// Get users with pagination
const getUsers = async (skip = 0, limit = 20) => {
  const response = await apiClient.get('/users/', {
    params: { skip, limit }
  });
  return response.data;
};
```

### Mock Data Examples
```javascript
// Mock user data for testing
const mockUser = {
  id: "123e4567-e89b-12d3-a456-426614174000",
  full_name: "Ahmed Hassan",
  email: "ahmed.hassan@example.com",
  phone: "+212612345678",
  is_active: true,
  is_verified: true,
  created_at: "2024-01-15T10:30:00Z",
  roles: [
    {
      id: "456e7890-e89b-12d3-a456-426614174001",
      name: "Tour Manager",
      description: "Manages tour operations"
    }
  ]
};

// Mock login response
const mockLoginResponse = {
  access_token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  token_type: "bearer",
  expires_in: 1800,
  user: mockUser
};
```

### Postman Collection Structure
```json
{
  "info": {
    "name": "Auth Service API",
    "description": "Authentication and Authorization endpoints"
  },
  "auth": {
    "type": "bearer",
    "bearer": [
      {
        "key": "token",
        "value": "{{access_token}}",
        "type": "string"
      }
    ]
  },
  "variable": [
    {
      "key": "base_url",
      "value": "https://api.example.com/v1"
    }
  ]
}
```

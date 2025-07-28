# Human Resources Service API Documentation

## 1. Service Overview

**Service Name**: Human Resources Service  
**Purpose**: Manages employee lifecycle, recruitment, training programs, and HR analytics for the Moroccan Tourist Transport ERP system.  
**Base Path**: `/api/v1`  
**Authentication**: JWT Bearer Token with RBAC  
**Required Scopes**: `hr:read`, `hr:create`, `hr:update`, `hr:delete`, `hr:approve`

## 2. Endpoint Reference

### Employee Management

#### GET /employees
**Purpose**: Retrieve paginated list of employees with optional filtering  
**Authentication**: Required - `hr:read`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| page | integer | 1 | No | Page number for pagination |
| size | integer | 20 | No | Number of employees per page |
| query | string | null | No | Search by name, employee ID, email |
| department | string | null | No | Filter by department |
| position | string | null | No | Filter by position |
| employment_type | string | null | No | Filter by employment type |
| status | string | null | No | Filter by employee status |
| is_active | boolean | true | No | Filter by active status |

**Response Structure**:
```json
{
  "items": [
    {
      "id": "uuid",
      "employee_id": "EMP001",
      "full_name": "Ahmed Benali",
      "email": "ahmed.benali@company.ma",
      "department": "Operations",
      "position": "Tour Guide",
      "employment_type": "FULL_TIME",
      "status": "ACTIVE",
      "hire_date": "2023-01-15",
      "is_active": true,
      "created_at": "datetime"
    }
  ],
  "total": "integer",
  "page": "integer",
  "size": "integer",
  "pages": "integer"
}
```

**Success Status**: 200 OK

#### POST /employees
**Purpose**: Create a new employee record  
**Authentication**: Required - `hr:create`

**Request Body**:
```json
{
  "employee_id": "EMP002",
  "full_name": "Fatima El Mansouri",
  "national_id": "AB123456",
  "gender": "Female",
  "birth_date": "1990-05-15",
  "email": "fatima.elmansouri@company.ma",
  "phone": "+212661234567",
  "department": "Customer Service",
  "position": "Customer Relations Manager",
  "employment_type": "FULL_TIME",
  "contract_type": "PERMANENT",
  "hire_date": "2024-02-01",
  "base_salary": 8500.00,
  "manager_id": "uuid"
}
```

**Success Status**: 201 Created

#### GET /employees/{employee_id}
**Purpose**: Retrieve specific employee details  
**Authentication**: Required - `hr:read`

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| employee_id | string (UUID) | Yes | Employee identifier |

#### GET /employees/{employee_id}/summary
**Purpose**: Get comprehensive employee summary with statistics  
**Authentication**: Required - `hr:read`

**Response Structure**:
```json
{
  "id": "uuid",
  "full_name": "Ahmed Benali",
  "department": "Operations",
  "position": "Tour Guide",
  "years_of_service": 1.2,
  "total_training_hours": 40,
  "completed_trainings": 5,
  "certificates_count": 3,
  "performance_rating": 4.5,
  "manager_name": "Hassan Alami",
  "direct_reports_count": 0
}
```

#### POST /employees/{employee_id}/terminate
**Purpose**: Terminate an employee  
**Authentication**: Required - `hr:update`

**Request Body**:
```json
{
  "termination_date": "2024-03-01",
  "reason": "Resignation",
  "final_pay_amount": 12000.00,
  "return_company_property": true,
  "notes": "Employee resigned for personal reasons"
}
```

### Training Management

#### GET /training/programs
**Purpose**: Retrieve training programs  
**Authentication**: Required - `hr:read`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| category | string | null | No | Filter by training category |
| status | string | null | No | Filter by program status |
| is_mandatory | boolean | null | No | Filter mandatory trainings |

#### POST /training/programs
**Purpose**: Create new training program  
**Authentication**: Required - `hr:create`

**Request Body**:
```json
{
  "title": "Customer Service Excellence",
  "description": "Advanced customer service training for tour guides",
  "category": "CUSTOMER_SERVICE",
  "trainer_name": "Sara Alaoui",
  "delivery_method": "IN_PERSON",
  "start_date": "2024-03-01",
  "end_date": "2024-03-03",
  "duration_hours": 24,
  "max_participants": 15,
  "cost_per_participant": 500.00,
  "is_mandatory": false,
  "pass_score": 75.0
}
```

#### POST /training/enrollments
**Purpose**: Enroll employees in training program  
**Authentication**: Required - `hr:create`

**Request Body**:
```json
{
  "employee_ids": ["uuid1", "uuid2"],
  "training_program_id": "uuid",
  "enrollment_date": "2024-02-15",
  "notes": "Mandatory enrollment for new hires"
}
```

#### POST /training/enrollments/{training_id}/complete
**Purpose**: Mark training as completed  
**Authentication**: Required - `hr:update`

**Request Body**:
```json
{
  "completion_date": "2024-03-03",
  "final_score": 85.5,
  "attendance_percentage": 100.0,
  "trainer_feedback": "Excellent participation and understanding",
  "issue_certificate": true
}
```

### Document Management

#### POST /documents/upload
**Purpose**: Upload employee document  
**Authentication**: Required - `hr:create`

**Request Body** (multipart/form-data):
```
employee_id: uuid
document_type: CONTRACT
title: Employment Contract
file: [binary file]
expiry_date: 2025-01-15
is_confidential: true
```

#### GET /documents
**Purpose**: Retrieve employee documents  
**Authentication**: Required - `hr:read`

#### GET /documents/expiring
**Purpose**: Get documents expiring soon  
**Authentication**: Required - `hr:read`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| days_ahead | integer | 30 | No | Days ahead to check for expiry |

### Recruitment

#### GET /recruitment/applications
**Purpose**: Retrieve job applications  
**Authentication**: Required - `hr:read`

#### POST /recruitment/applications
**Purpose**: Create new job application  
**Authentication**: Required - `hr:create`

**Request Body**:
```json
{
  "full_name": "Omar Benjelloun",
  "email": "omar.benjelloun@email.com",
  "phone": "+212662345678",
  "position_applied": "Tour Guide",
  "department": "Operations",
  "source": "JOB_BOARD",
  "years_of_experience": 3,
  "education_level": "Bachelor's Degree",
  "languages": ["Arabic", "French", "English"],
  "skills": ["Customer Service", "Tourism Knowledge"],
  "expected_salary": 7000.00
}
```

#### POST /recruitment/applications/{application_id}/stage
**Purpose**: Update application stage  
**Authentication**: Required - `hr:update`

**Request Body**:
```json
{
  "stage": "PHONE_INTERVIEW",
  "notes": "Scheduled for phone interview on Monday",
  "interview_date": "2024-02-20T10:00:00Z"
}
```

### Analytics

#### GET /analytics/dashboard
**Purpose**: Get HR dashboard overview  
**Authentication**: Required - `hr:read`

**Response Structure**:
```json
{
  "total_employees": 125,
  "active_employees": 118,
  "new_hires_this_month": 5,
  "pending_applications": 12,
  "training_completion_rate": 85.5,
  "by_department": {
    "Operations": 45,
    "Customer Service": 25,
    "Administration": 15
  },
  "upcoming_contract_renewals": 8
}
```

## 3. Data Models

### Employee Model
```json
{
  "id": "uuid",
  "employee_id": "string (max 20, unique)",
  "full_name": "string (max 255)",
  "national_id": "string (max 20, unique)",
  "gender": "enum (Male, Female, Other)",
  "birth_date": "date",
  "marital_status": "enum (Single, Married, Divorced, Widowed)",
  "email": "string (max 255, unique)",
  "phone": "string (max 20)",
  "address": "string (max 500, optional)",
  "department": "string (max 100)",
  "position": "string (max 100)",
  "employment_type": "enum (FULL_TIME, PART_TIME, CONTRACT)",
  "contract_type": "enum (PERMANENT, FIXED_TERM, PROBATION)",
  "hire_date": "date",
  "base_salary": "decimal (max 12,2)",
  "status": "enum (ACTIVE, PROBATION, SUSPENDED, TERMINATED)",
  "manager_id": "uuid (optional)",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime (optional)"
}
```

### TrainingProgram Model
```json
{
  "id": "uuid",
  "title": "string (max 255)",
  "description": "string (max 2000, optional)",
  "category": "enum (SAFETY, TECHNICAL, CUSTOMER_SERVICE, etc.)",
  "trainer_name": "string (max 255, optional)",
  "delivery_method": "enum (IN_PERSON, ONLINE, HYBRID)",
  "start_date": "date",
  "end_date": "date",
  "duration_hours": "integer",
  "max_participants": "integer",
  "cost_per_participant": "decimal (max 10,2, optional)",
  "is_mandatory": "boolean",
  "pass_score": "float (0-100)",
  "status": "enum (PLANNED, ACTIVE, COMPLETED, CANCELLED)",
  "created_at": "datetime"
}
```

### JobApplication Model
```json
{
  "id": "uuid",
  "full_name": "string (max 255)",
  "email": "string (max 255)",
  "phone": "string (max 20)",
  "position_applied": "string (max 100)",
  "department": "string (max 100)",
  "source": "enum (JOB_BOARD, COMPANY_WEBSITE, REFERRAL, etc.)",
  "stage": "enum (RECEIVED, SCREENING, INTERVIEW, etc.)",
  "years_of_experience": "integer (optional)",
  "education_level": "string (max 100, optional)",
  "languages": "array of strings",
  "skills": "array of strings",
  "expected_salary": "float (optional)",
  "overall_rating": "float (0-10, optional)",
  "application_date": "date",
  "is_active": "boolean",
  "created_at": "datetime"
}
```

### EmployeeDocument Model
```json
{
  "id": "uuid",
  "employee_id": "uuid",
  "document_type": "enum (CONTRACT, ID_COPY, DIPLOMA, etc.)",
  "title": "string (max 255)",
  "file_name": "string (max 255)",
  "file_path": "string (max 500)",
  "file_size": "integer",
  "expiry_date": "date (optional)",
  "status": "enum (PENDING, APPROVED, REJECTED, EXPIRED)",
  "is_confidential": "boolean",
  "uploaded_at": "datetime",
  "uploaded_by": "uuid (optional)"
}
```

## 4. Frontend Integration Guidelines

### HTTP Client Configuration
```javascript
// Axios configuration for HR Service
const hrApiClient = axios.create({
  baseURL: 'https://api.example.com/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor
hrApiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
hrApiClient.interceptors.response.use(
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

### File Upload Configuration
```javascript
// For document uploads
const uploadDocument = async (employeeId, file, documentData) => {
  const formData = new FormData();
  formData.append('employee_id', employeeId);
  formData.append('file', file);
  formData.append('document_type', documentData.type);
  formData.append('title', documentData.title);
  
  return hrApiClient.post('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    }
  });
};
```

### Error Handling Pattern
```javascript
// Standard error response format
{
  "detail": "Validation error",
  "errors": [
    {
      "field": "email",
      "message": "Email already exists"
    }
  ]
}

// Error handling utility
const handleApiError = (error) => {
  if (error.response?.data?.errors) {
    // Handle validation errors
    return error.response.data.errors;
  }
  return [{ message: error.response?.data?.detail || 'An error occurred' }];
};
```

### Rate Limiting
- No specific rate limits configured
- Standard HTTP 429 response if limits exceeded

### CORS Policy
- Allowed origins: `http://localhost:3000`, `http://localhost:8080`
- Credentials allowed: Yes
- Methods: GET, POST, PUT, DELETE

## 5. Testing & Support Tools

### Example API Calls

#### Create Employee
```bash
curl -X POST "https://api.example.com/api/v1/employees" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP003",
    "full_name": "Youssef Alami",
    "email": "youssef.alami@company.ma",
    "department": "Operations",
    "position": "Driver",
    "employment_type": "FULL_TIME",
    "hire_date": "2024-02-01",
    "base_salary": 6500.00
  }'
```

#### Get Training Programs
```bash
curl -X GET "https://api.example.com/api/v1/training/programs?category=SAFETY" \
  -H "Authorization: Bearer <token>"
```

#### Upload Document
```bash
curl -X POST "https://api.example.com/api/v1/documents/upload" \
  -H "Authorization: Bearer <token>" \
  -F "employee_id=uuid" \
  -F "document_type=CONTRACT" \
  -F "title=Employment Contract" \
  -F "file=@contract.pdf"
```

### Sample Postman Collection Structure
```json
{
  "info": {
    "name": "HR Service API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "auth": {
    "type": "bearer",
    "bearer": [{"key": "token", "value": "{{access_token}}"}]
  },
  "item": [
    {
      "name": "Employees",
      "item": [
        {"name": "Get Employees", "request": {"method": "GET", "url": "{{base_url}}/employees"}},
        {"name": "Create Employee", "request": {"method": "POST", "url": "{{base_url}}/employees"}},
        {"name": "Get Employee Details", "request": {"method": "GET", "url": "{{base_url}}/employees/{{employee_id}}"}}
      ]
    },
    {
      "name": "Training",
      "item": [
        {"name": "Get Training Programs", "request": {"method": "GET", "url": "{{base_url}}/training/programs"}},
        {"name": "Create Training Program", "request": {"method": "POST", "url": "{{base_url}}/training/programs"}}
      ]
    }
  ]
}
```

### Common Frontend Patterns
```javascript
// Employee management
const fetchEmployees = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await hrApiClient.get(`/employees?${params}`);
  return response.data;
};

const createEmployee = async (employeeData) => {
  const response = await hrApiClient.post('/employees', employeeData);
  return response.data;
};

// Training management
const enrollInTraining = async (employeeIds, trainingProgramId) => {
  const response = await hrApiClient.post('/training/enrollments', {
    employee_ids: employeeIds,
    training_program_id: trainingProgramId
  });
  return response.data;
};

// Document management
const getExpiringDocuments = async (daysAhead = 30) => {
  const response = await hrApiClient.get(`/documents/expiring?days_ahead=${daysAhead}`);
  return response.data;
};
```

### Mock Data Examples
```javascript
// Mock employee data
const mockEmployees = [
  {
    id: "550e8400-e29b-41d4-a716-446655440000",
    employee_id: "EMP001",
    full_name: "Ahmed Benali",
    email: "ahmed.benali@company.ma",
    department: "Operations",
    position: "Tour Guide",
    employment_type: "FULL_TIME",
    status: "ACTIVE",
    hire_date: "2023-01-15",
    base_salary: 7500.00,
    is_active: true
  }
];

// Mock training programs
const mockTrainingPrograms = [
  {
    id: "550e8400-e29b-41d4-a716-446655440001",
    title: "First Aid Certification",
    category: "SAFETY",
    duration_hours: 16,
    is_mandatory: true,
    pass_score: 80.0,
    status: "ACTIVE"
  }
];
```

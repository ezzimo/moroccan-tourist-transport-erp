# QA & Compliance Service API Documentation

## 1. Service Overview

**Service Name**: Quality Assurance & Compliance Service  
**Purpose**: Manages quality audits, non-conformity tracking, compliance requirements, and certification management for the Moroccan Tourist Transport ERP system.  
**Base Path**: `/api/v1`  
**Authentication**: JWT Bearer Token with RBAC  
**Required Scopes**: `qa:read`, `qa:create`, `qa:update`, `qa:delete`, `qa:assess`, `qa:verify`, `qa:export`

## 2. Endpoint Reference

### Quality Audit Management

#### POST /audits
**Purpose**: Create a new quality audit  
**Authentication**: Required - `qa:create`

**Request Body**:
```json
{
  "title": "Fleet Safety Audit Q1 2024",
  "entity_type": "FLEET",
  "entity_id": "VEH-001",
  "entity_name": "Mercedes Sprinter - ABC123",
  "audit_type": "INTERNAL",
  "auditor_id": "550e8400-e29b-41d4-a716-446655440000",
  "auditor_name": "Ahmed Benali",
  "external_auditor": null,
  "scheduled_date": "2024-02-15",
  "pass_score": 80.0,
  "checklist": {
    "safety_equipment": {
      "question": "Are all safety equipment items present and functional?",
      "weight": 10,
      "required": true
    },
    "vehicle_condition": {
      "question": "Is the vehicle in good mechanical condition?",
      "weight": 15,
      "required": true
    },
    "documentation": {
      "question": "Are all required documents up to date?",
      "weight": 8,
      "required": true
    }
  }
}
```

**Response Structure**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "audit_number": "AUD-2024-0001",
  "title": "Fleet Safety Audit Q1 2024",
  "entity_type": "FLEET",
  "entity_id": "VEH-001",
  "entity_name": "Mercedes Sprinter - ABC123",
  "audit_type": "INTERNAL",
  "status": "SCHEDULED",
  "auditor_id": "550e8400-e29b-41d4-a716-446655440000",
  "auditor_name": "Ahmed Benali",
  "external_auditor": null,
  "scheduled_date": "2024-02-15",
  "pass_score": 80.0,
  "checklist": {},
  "checklist_responses": {},
  "total_score": null,
  "outcome": null,
  "summary": null,
  "recommendations": null,
  "start_date": null,
  "completion_date": null,
  "requires_follow_up": false,
  "follow_up_date": null,
  "follow_up_audit_id": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null,
  "is_passed": false,
  "is_overdue": false,
  "days_overdue": 0
}
```

**Success Status**: 201 Created

#### GET /audits
**Purpose**: Retrieve audits with filtering and pagination  
**Authentication**: Required - `qa:read`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| page | integer | 1 | No | Page number for pagination |
| size | integer | 20 | No | Number of audits per page |
| query | string | null | No | Search query for title, audit number, entity name |
| entity_type | string | null | No | Filter by entity type (TOUR, FLEET, BOOKING, etc.) |
| audit_type | string | null | No | Filter by audit type (INTERNAL, EXTERNAL, etc.) |
| status | string | null | No | Filter by status (SCHEDULED, IN_PROGRESS, etc.) |
| auditor_id | string | null | No | Filter by auditor ID |
| scheduled_from | string | null | No | Filter by scheduled date from (YYYY-MM-DD) |
| scheduled_to | string | null | No | Filter by scheduled date to (YYYY-MM-DD) |
| outcome | string | null | No | Filter by outcome (Pass, Fail, Conditional) |
| requires_follow_up | boolean | null | No | Filter by follow-up requirement |

#### GET /audits/{audit_id}
**Purpose**: Retrieve specific audit details  
**Authentication**: Required - `qa:read`

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| audit_id | string (UUID) | Yes | Audit identifier |

#### POST /audits/{audit_id}/start
**Purpose**: Start an audit (change status to IN_PROGRESS)  
**Authentication**: Required - `qa:update`

#### POST /audits/{audit_id}/complete
**Purpose**: Complete an audit with responses  
**Authentication**: Required - `qa:update`

**Request Body**:
```json
{
  "responses": {
    "safety_equipment": {
      "compliant": true,
      "notes": "All equipment present and functional",
      "score": 10
    },
    "vehicle_condition": {
      "compliant": false,
      "notes": "Minor brake issue identified",
      "score": 12
    },
    "documentation": {
      "compliant": true,
      "notes": "All documents current",
      "score": 8
    }
  }
}
```

#### GET /audits/summary
**Purpose**: Get audit summary statistics  
**Authentication**: Required - `qa:read`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| days | integer | 90 | No | Number of days for summary (1-365) |

**Response Structure**:
```json
{
  "total_audits": 45,
  "by_status": {
    "scheduled": 12,
    "in_progress": 3,
    "completed": 28,
    "overdue": 2
  },
  "by_entity_type": {
    "fleet": 20,
    "tour": 15,
    "booking": 8,
    "office": 2
  },
  "by_outcome": {
    "Pass": 25,
    "Fail": 3
  },
  "average_score": 87.5,
  "pass_rate": 89.3,
  "overdue_audits": 2,
  "upcoming_audits": 8
}
```

### Non-Conformity Management

#### POST /nonconformities
**Purpose**: Create a new non-conformity  
**Authentication**: Required - `qa:create`

**Request Body**:
```json
{
  "audit_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Brake System Issue",
  "description": "Vehicle brake pads worn beyond acceptable limits",
  "severity": "MAJOR",
  "root_cause": "Delayed maintenance schedule",
  "contributing_factors": "High usage during peak season",
  "corrective_action": "Replace brake pads and adjust maintenance schedule",
  "preventive_action": "Implement more frequent brake inspections",
  "assigned_to": "550e8400-e29b-41d4-a716-446655440001",
  "due_date": "2024-02-20",
  "target_completion_date": "2024-02-18",
  "estimated_cost": 500.0
}
```

**Success Status**: 201 Created

#### GET /nonconformities
**Purpose**: Retrieve non-conformities with filtering  
**Authentication**: Required - `qa:read`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| audit_id | string | null | No | Filter by audit ID |
| severity | string | null | No | Filter by severity (MINOR, MAJOR, CRITICAL) |
| status | string | null | No | Filter by status |
| assigned_to | string | null | No | Filter by assignee |
| overdue_only | boolean | null | No | Show only overdue items |

#### POST /nonconformities/{nc_id}/resolve
**Purpose**: Resolve a non-conformity  
**Authentication**: Required - `qa:update`

**Request Body**:
```json
{
  "corrective_action": "Brake pads replaced with high-quality parts",
  "preventive_action": "Updated maintenance schedule to include monthly brake checks",
  "actual_completion_date": "2024-02-18",
  "actual_cost": 450.0,
  "resolution_notes": "Issue resolved successfully, no further action required"
}
```

#### POST /nonconformities/{nc_id}/verify
**Purpose**: Verify non-conformity resolution  
**Authentication**: Required - `qa:verify`

**Request Body**:
```json
{
  "verification_notes": "Verified brake system is functioning properly",
  "verified": true,
  "follow_up_required": false,
  "follow_up_notes": null
}
```

### Compliance Management

#### POST /compliance
**Purpose**: Create a new compliance requirement  
**Authentication**: Required - `qa:create`

**Request Body**:
```json
{
  "requirement_code": "TRS-001",
  "title": "Vehicle Insurance Compliance",
  "description": "All vehicles must maintain valid insurance coverage",
  "domain": "TRANSPORT",
  "requirement_type": "DOCUMENTATION",
  "regulatory_body": "Ministry of Equipment, Transport, Logistics and Water",
  "regulation_reference": "Law 52-05",
  "legal_basis": "Transport Code Article 15",
  "applies_to_entity": "Fleet",
  "mandatory": true,
  "responsible_person": "550e8400-e29b-41d4-a716-446655440000",
  "responsible_department": "Fleet Management",
  "evidence_required": "Valid insurance certificate",
  "compliance_cost": 2000.0,
  "estimated_effort_hours": 4,
  "risk_level": "HIGH",
  "non_compliance_impact": "Legal penalties and operational shutdown",
  "notes": "Critical for legal operation"
}
```

#### GET /compliance
**Purpose**: Retrieve compliance requirements  
**Authentication**: Required - `qa:read`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| domain | string | null | No | Filter by domain (SAFETY, LABOR, TAX, etc.) |
| requirement_type | string | null | No | Filter by type |
| status | string | null | No | Filter by status |
| responsible_person | string | null | No | Filter by responsible person |
| expiring_soon | boolean | null | No | Show expiring requirements |

#### POST /compliance/{requirement_id}/assess
**Purpose**: Assess compliance status  
**Authentication**: Required - `qa:assess`

**Request Body**:
```json
{
  "status": "COMPLIANT",
  "compliance_date": "2024-01-15",
  "assessment_notes": "All vehicles have valid insurance certificates",
  "evidence_provided": "Insurance certificates on file",
  "next_review_date": "2024-07-15"
}
```

### Certification Management

#### POST /certifications
**Purpose**: Create a new certification  
**Authentication**: Required - `qa:create`

**Request Body**:
```json
{
  "certificate_number": "ISO9001-2024-001",
  "name": "ISO 9001:2015 Quality Management",
  "type": "ISO_9001",
  "issuing_body": "Bureau Veritas Morocco",
  "issuing_authority": "International Organization for Standardization",
  "scope": "COMPANY_WIDE",
  "entity_type": "Company",
  "entity_id": "COMPANY-001",
  "entity_name": "Atlas Tours Morocco",
  "issue_date": "2024-01-15",
  "expiry_date": "2027-01-15",
  "effective_date": "2024-01-15",
  "requirements_met": "All QMS requirements satisfied",
  "renewable": true,
  "renewal_process": "Annual surveillance audits required",
  "renewal_cost": 15000.0,
  "renewal_lead_time_days": 90,
  "certificate_holder": "550e8400-e29b-41d4-a716-446655440000",
  "responsible_manager": "550e8400-e29b-41d4-a716-446655440001",
  "description": "Company-wide quality management system certification"
}
```

#### GET /certifications
**Purpose**: Retrieve certifications with filtering  
**Authentication**: Required - `qa:read`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| type | string | null | No | Filter by certification type |
| status | string | null | No | Filter by status |
| scope | string | null | No | Filter by scope |
| expiring_soon | boolean | null | No | Show expiring certifications |
| needs_renewal | boolean | null | No | Show certifications needing renewal |

#### POST /certifications/{cert_id}/renew
**Purpose**: Renew a certification  
**Authentication**: Required - `qa:update`

**Request Body**:
```json
{
  "new_certificate_number": "ISO9001-2024-002",
  "new_issue_date": "2024-01-20",
  "new_expiry_date": "2027-01-20",
  "renewal_cost": 15000.0,
  "renewal_notes": "Successful renewal with no major findings"
}
```

### Reporting

#### GET /reports/dashboard
**Purpose**: Get QA & Compliance dashboard overview  
**Authentication**: Required - `qa:read`

**Response Structure**:
```json
{
  "audit_summary": {
    "total_audits": 45,
    "completed_this_month": 8,
    "pass_rate": 89.3,
    "overdue_audits": 2
  },
  "nonconformity_summary": {
    "total_open": 12,
    "critical_open": 2,
    "overdue_actions": 3,
    "resolved_this_month": 15
  },
  "compliance_summary": {
    "total_requirements": 25,
    "compliant": 22,
    "non_compliant": 2,
    "pending": 1,
    "expiring_soon": 3
  },
  "certification_summary": {
    "total_certifications": 8,
    "active": 7,
    "expiring_soon": 2,
    "expired": 1
  }
}
```

#### GET /reports/audit-performance
**Purpose**: Get audit performance analytics  
**Authentication**: Required - `qa:read`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| period_months | integer | 12 | No | Period in months (1-60) |
| entity_type | string | null | No | Filter by entity type |

#### GET /reports/export/audit-report
**Purpose**: Export audit report  
**Authentication**: Required - `qa:export`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| start_date | string | - | Yes | Start date (YYYY-MM-DD) |
| end_date | string | - | Yes | End date (YYYY-MM-DD) |
| format | string | pdf | No | Export format (pdf, excel) |
| entity_type | string | null | No | Filter by entity type |

## 3. Data Models

### QualityAudit Model
```json
{
  "id": "string (uuid, required)",
  "audit_number": "string (max 50, unique, required)",
  "title": "string (max 255, required)",
  "entity_type": "enum (TOUR, FLEET, BOOKING, OFFICE, DRIVER, GUIDE, CUSTOMER_SERVICE, SAFETY)",
  "entity_id": "string (max 100, optional)",
  "entity_name": "string (max 255, optional)",
  "audit_type": "enum (INTERNAL, EXTERNAL, CUSTOMER_FEEDBACK, REGULATORY, FOLLOW_UP)",
  "status": "enum (SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED, OVERDUE)",
  "auditor_id": "string (uuid, required)",
  "auditor_name": "string (max 255, required)",
  "external_auditor": "string (max 255, optional)",
  "scheduled_date": "string (date, required)",
  "pass_score": "number (0-100, default 80.0)",
  "checklist": "object (required)",
  "checklist_responses": "object (optional)",
  "total_score": "number (0-100, optional)",
  "outcome": "string (max 20, optional)",
  "summary": "string (max 2000, optional)",
  "recommendations": "string (max 2000, optional)",
  "start_date": "string (datetime, optional)",
  "completion_date": "string (datetime, optional)",
  "requires_follow_up": "boolean (default false)",
  "follow_up_date": "string (date, optional)",
  "follow_up_audit_id": "string (uuid, optional)",
  "created_at": "string (datetime, required)",
  "updated_at": "string (datetime, optional)",
  "is_passed": "boolean (calculated)",
  "is_overdue": "boolean (calculated)",
  "days_overdue": "integer (calculated)"
}
```

### NonConformity Model
```json
{
  "id": "string (uuid, required)",
  "audit_id": "string (uuid, required)",
  "nc_number": "string (max 50, unique, required)",
  "title": "string (max 255, required)",
  "description": "string (max 2000, required)",
  "severity": "enum (MINOR, MAJOR, CRITICAL)",
  "root_cause": "string (max 1000, optional)",
  "contributing_factors": "string (max 1000, optional)",
  "corrective_action": "string (max 2000, optional)",
  "preventive_action": "string (max 2000, optional)",
  "assigned_to": "string (uuid, optional)",
  "due_date": "string (date, optional)",
  "target_completion_date": "string (date, optional)",
  "actual_completion_date": "string (date, optional)",
  "status": "enum (OPEN, IN_PROGRESS, RESOLVED, VERIFIED, CLOSED, ESCALATED)",
  "progress_notes": "string (max 2000, optional)",
  "verified_by": "string (uuid, optional)",
  "verification_date": "string (date, optional)",
  "verification_notes": "string (max 1000, optional)",
  "estimated_cost": "number (optional)",
  "actual_cost": "number (optional)",
  "is_recurring": "boolean (default false)",
  "previous_nc_id": "string (uuid, optional)",
  "identified_date": "string (date, required)",
  "created_at": "string (datetime, required)",
  "updated_at": "string (datetime, optional)",
  "is_overdue": "boolean (calculated)",
  "days_overdue": "integer (calculated)",
  "age_days": "integer (calculated)",
  "is_critical_overdue": "boolean (calculated)",
  "resolution_time_days": "integer (calculated, optional)"
}
```

### ComplianceRequirement Model
```json
{
  "id": "string (uuid, required)",
  "requirement_code": "string (max 50, unique, required)",
  "title": "string (max 255, required)",
  "description": "string (max 2000, required)",
  "domain": "enum (SAFETY, LABOR, TAX, TOURISM, TRANSPORT, ENVIRONMENTAL, DATA_PROTECTION, HEALTH)",
  "requirement_type": "enum (LICENSE, PERMIT, CERTIFICATION, INSPECTION, TRAINING, DOCUMENTATION, PROCEDURE)",
  "regulatory_body": "string (max 255, required)",
  "regulation_reference": "string (max 255, optional)",
  "legal_basis": "string (max 500, optional)",
  "applies_to_entity": "string (max 100, required)",
  "mandatory": "boolean (default true)",
  "status": "enum (COMPLIANT, NON_COMPLIANT, PENDING, EXPIRED, NOT_APPLICABLE)",
  "compliance_date": "string (date, optional)",
  "expiry_date": "string (date, optional)",
  "renewal_required": "boolean (default false)",
  "renewal_frequency_months": "integer (optional)",
  "next_review_date": "string (date, optional)",
  "responsible_person": "string (uuid, optional)",
  "responsible_department": "string (max 100, optional)",
  "evidence_required": "string (max 1000, optional)",
  "document_links": "array of strings (optional)",
  "compliance_cost": "number (optional)",
  "estimated_effort_hours": "integer (optional)",
  "risk_level": "string (max 20, optional)",
  "non_compliance_impact": "string (max 1000, optional)",
  "notes": "string (max 2000, optional)",
  "last_assessment_notes": "string (max 1000, optional)",
  "created_at": "string (datetime, required)",
  "updated_at": "string (datetime, optional)",
  "last_reviewed_at": "string (datetime, optional)",
  "is_expired": "boolean (calculated)",
  "days_until_expiry": "integer (calculated, optional)",
  "needs_renewal": "boolean (calculated)",
  "is_overdue_for_review": "boolean (calculated)",
  "next_renewal_date": "string (date, calculated, optional)"
}
```

### Certification Model
```json
{
  "id": "string (uuid, required)",
  "certificate_number": "string (max 100, unique, required)",
  "name": "string (max 255, required)",
  "type": "enum (ISO_9001, ISO_14001, ISO_45001, TOURISM_QUALITY, SAFETY_CERTIFICATION, DRIVER_LICENSE, GUIDE_LICENSE, BUSINESS_LICENSE, TRANSPORT_PERMIT, OTHER)",
  "issuing_body": "string (max 255, required)",
  "issuing_authority": "string (max 255, optional)",
  "accreditation_body": "string (max 255, optional)",
  "scope": "enum (COMPANY_WIDE, DEPARTMENT, INDIVIDUAL, VEHICLE, LOCATION)",
  "entity_type": "string (max 50, optional)",
  "entity_id": "string (max 100, optional)",
  "entity_name": "string (max 255, optional)",
  "issue_date": "string (date, required)",
  "expiry_date": "string (date, optional)",
  "effective_date": "string (date, optional)",
  "status": "enum (ACTIVE, EXPIRED, SUSPENDED, PENDING_RENEWAL, CANCELLED)",
  "document_path": "string (max 500, optional)",
  "document_url": "string (max 500, optional)",
  "verification_url": "string (max 500, optional)",
  "requirements_met": "string (max 2000, optional)",
  "conditions": "string (max 1000, optional)",
  "restrictions": "string (max 1000, optional)",
  "renewable": "boolean (default true)",
  "renewal_process": "string (max 1000, optional)",
  "renewal_cost": "number (optional)",
  "renewal_lead_time_days": "integer (optional)",
  "last_audit_date": "string (date, optional)",
  "next_audit_date": "string (date, optional)",
  "compliance_verified": "boolean (default true)",
  "certificate_holder": "string (uuid, optional)",
  "responsible_manager": "string (uuid, optional)",
  "description": "string (max 1000, optional)",
  "notes": "string (max 2000, optional)",
  "created_at": "string (datetime, required)",
  "updated_at": "string (datetime, optional)",
  "is_expired": "boolean (calculated)",
  "days_until_expiry": "integer (calculated, optional)",
  "needs_renewal": "boolean (calculated)",
  "is_valid": "boolean (calculated)",
  "validity_period_days": "integer (calculated, optional)",
  "renewal_start_date": "string (date, calculated, optional)"
}
```

## 4. Frontend Integration Guidelines

### HTTP Client Configuration
```javascript
// Axios configuration for QA Service
const qaApiClient = axios.create({
  baseURL: 'https://api.example.com/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor
qaApiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor
qaApiClient.interceptors.response.use(
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

### Error Handling Pattern
```javascript
// QA service specific error handling
const handleQAError = (error) => {
  if (error.response?.status === 422) {
    // Validation errors
    return error.response.data.errors || [];
  }
  if (error.response?.status === 404) {
    return [{ message: 'Audit, compliance requirement, or certification not found' }];
  }
  return [{ message: error.response?.data?.detail || 'QA operation failed' }];
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

#### Create Quality Audit
```bash
curl -X POST "https://api.example.com/api/v1/audits" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fleet Safety Audit",
    "entity_type": "FLEET",
    "audit_type": "INTERNAL",
    "auditor_id": "uuid",
    "auditor_name": "Ahmed Benali",
    "scheduled_date": "2024-02-15",
    "checklist": {
      "safety_check": {
        "question": "Safety equipment check",
        "weight": 10,
        "required": true
      }
    }
  }'
```

#### Get Compliance Requirements
```bash
curl -X GET "https://api.example.com/api/v1/compliance?domain=TRANSPORT&status=COMPLIANT" \
  -H "Authorization: Bearer <token>"
```

#### Create Non-Conformity
```bash
curl -X POST "https://api.example.com/api/v1/nonconformities" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "audit_id": "uuid",
    "title": "Safety Issue",
    "description": "Missing safety equipment",
    "severity": "MAJOR",
    "due_date": "2024-02-20"
  }'
```

### Sample Postman Collection Structure
```json
{
  "info": {
    "name": "QA & Compliance Service API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "auth": {
    "type": "bearer",
    "bearer": [{"key": "token", "value": "{{access_token}}"}]
  },
  "item": [
    {
      "name": "Quality Audits",
      "item": [
        {"name": "Create Audit", "request": {"method": "POST", "url": "{{base_url}}/audits"}},
        {"name": "Get Audits", "request": {"method": "GET", "url": "{{base_url}}/audits"}},
        {"name": "Start Audit", "request": {"method": "POST", "url": "{{base_url}}/audits/{{audit_id}}/start"}},
        {"name": "Complete Audit", "request": {"method": "POST", "url": "{{base_url}}/audits/{{audit_id}}/complete"}}
      ]
    },
    {
      "name": "Non-Conformities",
      "item": [
        {"name": "Create NC", "request": {"method": "POST", "url": "{{base_url}}/nonconformities"}},
        {"name": "Get NCs", "request": {"method": "GET", "url": "{{base_url}}/nonconformities"}},
        {"name": "Resolve NC", "request": {"method": "POST", "url": "{{base_url}}/nonconformities/{{nc_id}}/resolve"}}
      ]
    },
    {
      "name": "Compliance",
      "item": [
        {"name": "Get Requirements", "request": {"method": "GET", "url": "{{base_url}}/compliance"}},
        {"name": "Create Requirement", "request": {"method": "POST", "url": "{{base_url}}/compliance"}},
        {"name": "Assess Compliance", "request": {"method": "POST", "url": "{{base_url}}/compliance/{{req_id}}/assess"}}
      ]
    },
    {
      "name": "Certifications",
      "item": [
        {"name": "Get Certifications", "request": {"method": "GET", "url": "{{base_url}}/certifications"}},
        {"name": "Create Certification", "request": {"method": "POST", "url": "{{base_url}}/certifications"}},
        {"name": "Renew Certification", "request": {"method": "POST", "url": "{{base_url}}/certifications/{{cert_id}}/renew"}}
      ]
    }
  ]
}
```

### Common Frontend Patterns
```javascript
// Quality audit management
const createAudit = async (auditData) => {
  const response = await qaApiClient.post('/audits', auditData);
  return response.data;
};

const getAudits = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await qaApiClient.get(`/audits?${params}`);
  return response.data;
};

const completeAudit = async (auditId, responses) => {
  const response = await qaApiClient.post(`/audits/${auditId}/complete`, { responses });
  return response.data;
};

// Non-conformity management
const createNonConformity = async (ncData) => {
  const response = await qaApiClient.post('/nonconformities', ncData);
  return response.data;
};

const resolveNonConformity = async (ncId, resolutionData) => {
  const response = await qaApiClient.post(`/nonconformities/${ncId}/resolve`, resolutionData);
  return response.data;
};

// Compliance management
const getComplianceRequirements = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await qaApiClient.get(`/compliance?${params}`);
  return response.data;
};

const assessCompliance = async (requirementId, assessmentData) => {
  const response = await qaApiClient.post(`/compliance/${requirementId}/assess`, assessmentData);
  return response.data;
};

// Certification management
const getCertifications = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await qaApiClient.get(`/certifications?${params}`);
  return response.data;
};

const renewCertification = async (certId, renewalData) => {
  const response = await qaApiClient.post(`/certifications/${certId}/renew`, renewalData);
  return response.data;
};

// Dashboard and reporting
const getDashboard = async () => {
  const response = await qaApiClient.get('/reports/dashboard');
  return response.data;
};

const exportAuditReport = async (startDate, endDate, format = 'pdf') => {
  const response = await qaApiClient.get('/reports/export/audit-report', {
    params: { start_date: startDate, end_date: endDate, format },
    responseType: 'blob'
  });
  return response.data;
};
```

### Mock Data Examples
```javascript
// Mock audit data
const mockAudits = [
  {
    id: "550e8400-e29b-41d4-a716-446655440000",
    audit_number: "AUD-2024-0001",
    title: "Fleet Safety Audit Q1 2024",
    entity_type: "FLEET",
    status: "COMPLETED",
    auditor_name: "Ahmed Benali",
    scheduled_date: "2024-01-15",
    total_score: 87.5,
    outcome: "Pass",
    is_passed: true
  }
];

// Mock non-conformity data
const mockNonConformities = [
  {
    id: "550e8400-e29b-41d4-a716-446655440001",
    nc_number: "NC-2024-0001",
    title: "Brake System Issue",
    severity: "MAJOR",
    status: "RESOLVED",
    due_date: "2024-02-20",
    is_overdue: false
  }
];

// Mock compliance requirements
const mockComplianceRequirements = [
  {
    id: "550e8400-e29b-41d4-a716-446655440002",
    requirement_code: "TRS-001",
    title: "Vehicle Insurance Compliance",
    domain: "TRANSPORT",
    status: "COMPLIANT",
    expiry_date: "2024-12-31",
    needs_renewal: false
  }
];

// Mock certifications
const mockCertifications = [
  {
    id: "550e8400-e29b-41d4-a716-446655440003",
    certificate_number: "ISO9001-2024-001",
    name: "ISO 9001:2015 Quality Management",
    type: "ISO_9001",
    status: "ACTIVE",
    expiry_date: "2027-01-15",
    is_valid: true,
    needs_renewal: false
  }
];
```

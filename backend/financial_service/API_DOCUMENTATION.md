# Financial Management Service API Documentation

## 1. Service Overview

**Service Name**: Financial Management Service  
**Purpose**: Handles invoicing, payments, expenses, tax reporting, and financial analytics for the Moroccan Tourist Transport ERP system.  
**Base Path**: `/api/v1`  
**Authentication**: JWT Bearer Token with RBAC  
**Required Scopes**: `finance:read`, `finance:create`, `finance:update`, `finance:delete`, `finance:approve`

## 2. Endpoint Reference

### Invoice Management

#### GET /invoices
**Purpose**: Retrieve paginated list of invoices with optional filtering  
**Authentication**: Required - `finance:read`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| page | integer | 1 | No | Page number for pagination |
| size | integer | 20 | No | Number of invoices per page |
| query | string | null | No | Search by invoice number, customer name |
| customer_id | string | null | No | Filter by customer UUID |
| status | string | null | No | Filter by invoice status |
| payment_status | string | null | No | Filter by payment status |
| currency | string | null | No | Filter by currency (MAD, EUR, USD) |
| issue_date_from | string | null | No | Start date (YYYY-MM-DD) |
| issue_date_to | string | null | No | End date (YYYY-MM-DD) |
| is_overdue | boolean | null | No | Filter overdue invoices |

**Response Structure**:
```json
{
  "items": [
    {
      "id": "uuid",
      "invoice_number": "INV-2024-000001",
      "customer_id": "uuid",
      "customer_name": "Atlas Tours Agency",
      "total_amount": 2500.00,
      "currency": "MAD",
      "status": "SENT",
      "payment_status": "PENDING",
      "issue_date": "2024-01-15",
      "due_date": "2024-02-14",
      "is_overdue": false,
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

#### POST /invoices
**Purpose**: Create a new invoice  
**Authentication**: Required - `finance:create`

**Request Body**:
```json
{
  "customer_id": "uuid",
  "customer_name": "Atlas Tours Agency",
  "customer_email": "billing@atlastours.ma",
  "customer_address": "Casablanca, Morocco",
  "currency": "MAD",
  "tax_rate": 20.0,
  "payment_terms": "Net 30",
  "items": [
    {
      "description": "Tour Service - Desert Safari",
      "quantity": 1,
      "unit_price": 2000.00,
      "tax_rate": 20.0
    },
    {
      "description": "Transportation Service",
      "quantity": 1,
      "unit_price": 500.00,
      "tax_rate": 20.0
    }
  ],
  "discount_amount": 0.00,
  "notes": "Payment due within 30 days"
}
```

**Success Status**: 201 Created

#### POST /invoices/generate
**Purpose**: Generate invoice from booking  
**Authentication**: Required - `finance:create`

**Request Body**:
```json
{
  "booking_id": "uuid",
  "due_date": "2024-02-15",
  "payment_terms": "Net 30",
  "notes": "Generated from confirmed booking",
  "send_immediately": false
}
```

#### GET /invoices/{invoice_id}
**Purpose**: Retrieve specific invoice details  
**Authentication**: Required - `finance:read`

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| invoice_id | string (UUID) | Yes | Invoice identifier |

#### POST /invoices/{invoice_id}/send
**Purpose**: Send invoice to customer  
**Authentication**: Required - `finance:update`

#### GET /invoices/{invoice_id}/pdf
**Purpose**: Download invoice as PDF  
**Authentication**: Required - `finance:read`

**Response**: PDF file download

### Payment Management

#### GET /payments
**Purpose**: Retrieve payment records  
**Authentication**: Required - `finance:read`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| invoice_id | string | null | No | Filter by invoice UUID |
| payment_method | string | null | No | Filter by payment method |
| status | string | null | No | Filter by payment status |
| payment_date_from | string | null | No | Start date (YYYY-MM-DD) |
| payment_date_to | string | null | No | End date (YYYY-MM-DD) |

#### POST /payments
**Purpose**: Record a new payment  
**Authentication**: Required - `finance:create`

**Request Body**:
```json
{
  "invoice_id": "uuid",
  "amount": 2500.00,
  "currency": "MAD",
  "payment_method": "CREDIT_CARD",
  "payment_date": "2024-01-20",
  "reference_number": "TXN123456789",
  "transaction_id": "cc_1234567890",
  "description": "Payment for Invoice INV-2024-000001"
}
```

**Success Status**: 201 Created

#### POST /payments/{payment_id}/confirm
**Purpose**: Confirm a pending payment  
**Authentication**: Required - `finance:update`

#### POST /payments/reconcile
**Purpose**: Reconcile multiple payments  
**Authentication**: Required - `finance:update`

**Request Body**:
```json
{
  "payment_ids": ["uuid1", "uuid2"],
  "reconciled_by": "uuid",
  "notes": "Bank statement reconciliation",
  "bank_statement_reference": "STMT-2024-001"
}
```

### Expense Management

#### GET /expenses
**Purpose**: Retrieve expense records  
**Authentication**: Required - `finance:read`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| category | string | null | No | Filter by expense category |
| cost_center | string | null | No | Filter by cost center |
| department | string | null | No | Filter by department |
| status | string | null | No | Filter by approval status |
| expense_date_from | string | null | No | Start date (YYYY-MM-DD) |
| expense_date_to | string | null | No | End date (YYYY-MM-DD) |

#### POST /expenses
**Purpose**: Create new expense record  
**Authentication**: Required - `finance:create`

**Request Body**:
```json
{
  "category": "FUEL",
  "cost_center": "OPERATIONS",
  "department": "Fleet",
  "amount": 1250.00,
  "currency": "MAD",
  "description": "Fuel for tour vehicles",
  "vendor_name": "Shell Morocco",
  "expense_date": "2024-01-15",
  "tax_amount": 250.00,
  "is_tax_deductible": true,
  "receipt_url": "https://storage.example.com/receipts/receipt123.pdf"
}
```

#### POST /expenses/upload
**Purpose**: Create expense with receipt upload  
**Authentication**: Required - `finance:create`

**Request Body** (multipart/form-data):
```
category: MAINTENANCE
amount: 850.00
description: Vehicle brake repair
expense_date: 2024-01-20
receipt_file: [binary file]
```

#### POST /expenses/{expense_id}/approve
**Purpose**: Approve or reject expense  
**Authentication**: Required - `finance:approve`

**Request Body**:
```json
{
  "status": "APPROVED",
  "notes": "Approved for payment",
  "rejected_reason": null
}
```

### Tax Reporting

#### GET /tax-reports
**Purpose**: Retrieve tax reports  
**Authentication**: Required - `finance:read`

#### POST /tax-reports/generate
**Purpose**: Generate tax report for period  
**Authentication**: Required - `finance:create`

**Request Body**:
```json
{
  "tax_type": "VAT",
  "period_type": "MONTHLY",
  "period_start": "2024-01-01",
  "period_end": "2024-01-31",
  "include_draft_transactions": false,
  "notes": "Monthly VAT report for January 2024"
}
```

#### GET /tax-reports/vat/declaration
**Purpose**: Get VAT declaration for period  
**Authentication**: Required - `finance:read`

**Query Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| period_start | string | Yes | Start date (YYYY-MM-DD) |
| period_end | string | Yes | End date (YYYY-MM-DD) |

**Response Structure**:
```json
{
  "period_start": "2024-01-01",
  "period_end": "2024-01-31",
  "sales_vat": 15000.00,
  "purchase_vat": 3000.00,
  "net_vat": 12000.00,
  "sales_breakdown": {
    "standard_rate": 14000.00,
    "reduced_rate": 1000.00
  },
  "purchase_breakdown": {
    "deductible": 3000.00,
    "non_deductible": 0.00
  }
}
```

### Financial Analytics

#### GET /analytics/dashboard
**Purpose**: Get financial dashboard overview  
**Authentication**: Required - `finance:read`

**Response Structure**:
```json
{
  "total_revenue_mtd": 125000.00,
  "total_expenses_mtd": 45000.00,
  "net_profit_mtd": 80000.00,
  "outstanding_invoices": 25000.00,
  "overdue_amount": 5000.00,
  "cash_flow_forecast": {
    "next_30_days": 35000.00,
    "next_60_days": 65000.00,
    "next_90_days": 95000.00
  },
  "top_customers": [
    {
      "customer_name": "Atlas Tours",
      "total_amount": 15000.00
    }
  ]
}
```

#### GET /analytics/revenue
**Purpose**: Get revenue analytics  
**Authentication**: Required - `finance:read`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| period_months | integer | 12 | No | Period in months for analysis |
| currency | string | null | No | Filter by currency |

#### GET /analytics/export/profit-loss
**Purpose**: Export profit & loss statement  
**Authentication**: Required - `finance:export`

**Query Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| start_date | string | Yes | Start date (YYYY-MM-DD) |
| end_date | string | Yes | End date (YYYY-MM-DD) |
| format | string | No | Export format (pdf, excel) |

**Response**: File download (PDF or Excel)

## 3. Data Models

### Invoice Model
```json
{
  "id": "uuid",
  "invoice_number": "string (unique)",
  "booking_id": "uuid (optional)",
  "customer_id": "uuid",
  "customer_name": "string (max 255)",
  "customer_email": "string (max 255)",
  "customer_address": "string (max 500, optional)",
  "subtotal": "decimal (max 12,2)",
  "tax_amount": "decimal (max 12,2)",
  "discount_amount": "decimal (max 12,2)",
  "total_amount": "decimal (max 12,2)",
  "currency": "string (max 3)",
  "status": "enum (DRAFT, SENT, PAID, OVERDUE, CANCELLED)",
  "payment_status": "enum (PENDING, PARTIAL, PAID, REFUNDED)",
  "issue_date": "date",
  "due_date": "date",
  "payment_terms": "string (max 100)",
  "items": [
    {
      "description": "string",
      "quantity": "decimal",
      "unit_price": "decimal",
      "total_amount": "decimal",
      "tax_rate": "float"
    }
  ],
  "created_at": "datetime"
}
```

### Payment Model
```json
{
  "id": "uuid",
  "invoice_id": "uuid",
  "customer_id": "uuid",
  "amount": "decimal (max 12,2)",
  "currency": "string (max 3)",
  "payment_method": "enum (CASH, CREDIT_CARD, BANK_TRANSFER, etc.)",
  "payment_date": "date",
  "reference_number": "string (max 100, optional)",
  "transaction_id": "string (max 100, optional)",
  "status": "enum (PENDING, CONFIRMED, FAILED, CANCELLED)",
  "is_reconciled": "boolean",
  "processing_fee": "decimal (max 10,2, optional)",
  "description": "string (max 500, optional)",
  "created_at": "datetime"
}
```

### Expense Model
```json
{
  "id": "uuid",
  "expense_number": "string (unique)",
  "category": "enum (FUEL, MAINTENANCE, SALARIES, etc.)",
  "cost_center": "enum (OPERATIONS, SALES, MARKETING, etc.)",
  "department": "string (max 100)",
  "amount": "decimal (max 12,2)",
  "currency": "string (max 3)",
  "description": "string (max 500)",
  "vendor_name": "string (max 255, optional)",
  "expense_date": "date",
  "due_date": "date (optional)",
  "status": "enum (DRAFT, SUBMITTED, APPROVED, REJECTED, PAID)",
  "tax_amount": "decimal (max 10,2, optional)",
  "is_tax_deductible": "boolean",
  "receipt_url": "string (max 500, optional)",
  "submitted_by": "uuid (optional)",
  "approved_by": "uuid (optional)",
  "created_at": "datetime"
}
```

### TaxReport Model
```json
{
  "id": "uuid",
  "report_number": "string (unique)",
  "tax_type": "enum (VAT, INCOME_TAX, CORPORATE_TAX)",
  "period_type": "enum (MONTHLY, QUARTERLY, YEARLY)",
  "period_start": "date",
  "period_end": "date",
  "total_revenue": "decimal (max 15,2)",
  "total_expenses": "decimal (max 15,2)",
  "total_vat_collected": "decimal (max 12,2)",
  "total_vat_paid": "decimal (max 12,2)",
  "net_vat_due": "decimal (max 12,2)",
  "status": "enum (DRAFT, GENERATED, SUBMITTED, ACCEPTED)",
  "generated_at": "datetime (optional)",
  "submitted_at": "datetime (optional)",
  "created_at": "datetime"
}
```

## 4. Frontend Integration Guidelines

### HTTP Client Configuration
```javascript
// Axios configuration for Financial Service
const financeApiClient = axios.create({
  baseURL: 'https://api.example.com/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor
financeApiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor
financeApiClient.interceptors.response.use(
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

### Currency Handling
```javascript
// Currency formatting utility
const formatCurrency = (amount, currency = 'MAD') => {
  return new Intl.NumberFormat('fr-MA', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2
  }).format(amount);
};

// Multi-currency support
const supportedCurrencies = ['MAD', 'EUR', 'USD'];
```

### Error Handling Pattern
```javascript
// Financial service specific error handling
const handleFinancialError = (error) => {
  if (error.response?.status === 422) {
    // Validation errors
    return error.response.data.errors || [];
  }
  if (error.response?.status === 409) {
    // Conflict (e.g., duplicate invoice)
    return [{ message: 'Resource conflict: ' + error.response.data.detail }];
  }
  return [{ message: error.response?.data?.detail || 'Financial operation failed' }];
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

#### Create Invoice
```bash
curl -X POST "https://api.example.com/api/v1/invoices" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "uuid",
    "customer_name": "Desert Adventures",
    "customer_email": "billing@desertadventures.ma",
    "currency": "MAD",
    "items": [
      {
        "description": "3-Day Desert Tour",
        "quantity": 1,
        "unit_price": 3500.00,
        "tax_rate": 20.0
      }
    ]
  }'
```

#### Record Payment
```bash
curl -X POST "https://api.example.com/api/v1/payments" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_id": "uuid",
    "amount": 3500.00,
    "currency": "MAD",
    "payment_method": "BANK_TRANSFER",
    "payment_date": "2024-01-25",
    "reference_number": "BT20240125001"
  }'
```

#### Create Expense with Receipt
```bash
curl -X POST "https://api.example.com/api/v1/expenses/upload" \
  -H "Authorization: Bearer <token>" \
  -F "category=FUEL" \
  -F "amount=450.00" \
  -F "description=Fuel for tour vehicles" \
  -F "expense_date=2024-01-20" \
  -F "receipt_file=@fuel_receipt.pdf"
```

### Sample Postman Collection Structure
```json
{
  "info": {
    "name": "Financial Service API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "auth": {
    "type": "bearer",
    "bearer": [{"key": "token", "value": "{{access_token}}"}]
  },
  "item": [
    {
      "name": "Invoices",
      "item": [
        {"name": "Get Invoices", "request": {"method": "GET", "url": "{{base_url}}/invoices"}},
        {"name": "Create Invoice", "request": {"method": "POST", "url": "{{base_url}}/invoices"}},
        {"name": "Send Invoice", "request": {"method": "POST", "url": "{{base_url}}/invoices/{{invoice_id}}/send"}}
      ]
    },
    {
      "name": "Payments",
      "item": [
        {"name": "Get Payments", "request": {"method": "GET", "url": "{{base_url}}/payments"}},
        {"name": "Record Payment", "request": {"method": "POST", "url": "{{base_url}}/payments"}}
      ]
    }
  ]
}
```

### Common Frontend Patterns
```javascript
// Invoice management
const createInvoice = async (invoiceData) => {
  const response = await financeApiClient.post('/invoices', invoiceData);
  return response.data;
};

const generateInvoiceFromBooking = async (bookingId, options = {}) => {
  const response = await financeApiClient.post('/invoices/generate', {
    booking_id: bookingId,
    ...options
  });
  return response.data;
};

// Payment processing
const recordPayment = async (paymentData) => {
  const response = await financeApiClient.post('/payments', paymentData);
  return response.data;
};

// Expense management
const createExpense = async (expenseData) => {
  const response = await financeApiClient.post('/expenses', expenseData);
  return response.data;
};

// Financial analytics
const getDashboard = async () => {
  const response = await financeApiClient.get('/analytics/dashboard');
  return response.data;
};
```

### Mock Data Examples
```javascript
// Mock invoice data
const mockInvoices = [
  {
    id: "550e8400-e29b-41d4-a716-446655440000",
    invoice_number: "INV-2024-000001",
    customer_name: "Atlas Tours Agency",
    total_amount: 4200.00,
    currency: "MAD",
    status: "SENT",
    payment_status: "PENDING",
    issue_date: "2024-01-15",
    due_date: "2024-02-14"
  }
];

// Mock payment data
const mockPayments = [
  {
    id: "550e8400-e29b-41d4-a716-446655440001",
    invoice_id: "550e8400-e29b-41d4-a716-446655440000",
    amount: 4200.00,
    currency: "MAD",
    payment_method: "CREDIT_CARD",
    payment_date: "2024-01-20",
    status: "CONFIRMED"
  }
];
```
# Inventory Management Service API Documentation

## 1. Service Overview

**Service Name**: Inventory Management Service  
**Purpose**: Manages inventory items, stock movements, suppliers, and purchase orders for the Moroccan Tourist Transport ERP system.  
**Base Path**: `/api/v1`  
**Authentication**: JWT Bearer Token with RBAC  
**Required Scopes**: `inventory:read`, `inventory:create`, `inventory:update`, `inventory:delete`

## 2. Endpoint Reference

### Items Management

#### GET /items
**Purpose**: Retrieve paginated list of inventory items with optional filtering  
**Authentication**: Required - `inventory:read`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| page | integer | 1 | No | Page number for pagination |
| size | integer | 20 | No | Number of items per page |
| query | string | null | No | Search query for name, SKU, description |
| category | string | null | No | Filter by item category |
| status | string | null | No | Filter by status (Active, Inactive, Discontinued) |
| warehouse_location | string | null | No | Filter by warehouse location |
| supplier_id | string | null | No | Filter by supplier UUID |
| is_low_stock | boolean | null | No | Filter items with low stock |
| is_critical | boolean | null | No | Filter critical items |

**Response Structure**:
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "string",
      "description": "string",
      "sku": "string",
      "barcode": "string",
      "category": "ENGINE_PARTS",
      "unit": "PIECE",
      "unit_cost": "decimal",
      "current_quantity": "decimal",
      "reorder_level": "decimal",
      "warehouse_location": "string",
      "is_low_stock": "boolean",
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
**Error Responses**: 401 Unauthorized, 403 Forbidden, 500 Internal Server Error

#### POST /items
**Purpose**: Create a new inventory item  
**Authentication**: Required - `inventory:create`

**Request Body**:
```json
{
  "name": "Engine Oil Filter",
  "description": "High-quality oil filter for diesel engines",
  "sku": "EOF-001",
  "barcode": "1234567890123",
  "category": "ENGINE_PARTS",
  "unit": "PIECE",
  "unit_cost": 25.50,
  "current_quantity": 100,
  "reorder_level": 20,
  "warehouse_location": "Main Warehouse",
  "primary_supplier_id": "uuid",
  "is_critical": true
}
```

**Success Status**: 201 Created  
**Response**: Item object with generated ID

#### GET /items/{item_id}
**Purpose**: Retrieve specific item details  
**Authentication**: Required - `inventory:read`

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| item_id | string (UUID) | Yes | Item identifier |

#### PUT /items/{item_id}
**Purpose**: Update item information  
**Authentication**: Required - `inventory:update`

#### POST /items/{item_id}/adjust-stock
**Purpose**: Adjust item stock quantity  
**Authentication**: Required - `inventory:update`

**Request Body**:
```json
{
  "quantity": 10,
  "reason": "Stock adjustment after physical count",
  "reference_number": "ADJ-2024-001"
}
```

### Stock Movements

#### GET /movements
**Purpose**: Retrieve stock movement history  
**Authentication**: Required - `inventory:read`

**Query Parameters**:
| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| item_id | string | null | No | Filter by item UUID |
| movement_type | string | null | No | Filter by type (IN, OUT, ADJUST) |
| date_from | string | null | No | Start date (ISO format) |
| date_to | string | null | No | End date (ISO format) |

#### POST /movements
**Purpose**: Create new stock movement  
**Authentication**: Required - `inventory:create`

**Request Body**:
```json
{
  "item_id": "uuid",
  "movement_type": "OUT",
  "reason": "MAINTENANCE",
  "quantity": 5,
  "reference_type": "maintenance_job",
  "reference_id": "MJ-001",
  "notes": "Used for vehicle maintenance"
}
```

### Suppliers Management

#### GET /suppliers
**Purpose**: Retrieve supplier list  
**Authentication**: Required - `inventory:read`

#### POST /suppliers
**Purpose**: Create new supplier  
**Authentication**: Required - `inventory:create`

**Request Body**:
```json
{
  "name": "Atlas Auto Parts",
  "code": "AAP",
  "type": "PARTS_SUPPLIER",
  "contact_person": "Ahmed Benali",
  "email": "ahmed@atlasautoparts.ma",
  "phone": "+212522123456",
  "address": "Casablanca, Morocco",
  "payment_terms": "Net 30",
  "delivery_time_days": 7
}
```

### Purchase Orders

#### GET /purchase-orders
**Purpose**: Retrieve purchase orders  
**Authentication**: Required - `inventory:read`

#### POST /purchase-orders
**Purpose**: Create new purchase order  
**Authentication**: Required - `inventory:create`

**Request Body**:
```json
{
  "supplier_id": "uuid",
  "items": [
    {
      "item_id": "uuid",
      "quantity": 50,
      "unit_cost": 25.50
    }
  ],
  "required_date": "2024-02-15",
  "delivery_address": "Main Warehouse, Casablanca",
  "notes": "Urgent order for maintenance"
}
```

#### POST /purchase-orders/{po_id}/approve
**Purpose**: Approve purchase order  
**Authentication**: Required - `inventory:approve`

#### POST /purchase-orders/{po_id}/receive
**Purpose**: Receive items from purchase order  
**Authentication**: Required - `inventory:update`

### Analytics

#### GET /analytics/dashboard
**Purpose**: Get inventory dashboard overview  
**Authentication**: Required - `inventory:read`

**Response Structure**:
```json
{
  "total_items": 1250,
  "low_stock_items": 45,
  "total_stock_value": 125000.50,
  "by_category": {
    "ENGINE_PARTS": 450,
    "TIRES": 200
  },
  "recent_movements": []
}
```

## 3. Data Models

### Item Model
```json
{
  "id": "uuid",
  "name": "string (max 255)",
  "description": "string (max 1000, optional)",
  "sku": "string (max 50, unique)",
  "barcode": "string (max 50, optional)",
  "category": "enum (ENGINE_PARTS, TIRES, FLUIDS, etc.)",
  "unit": "enum (PIECE, LITER, KILOGRAM, etc.)",
  "unit_cost": "decimal (max 10,2)",
  "current_quantity": "decimal (max 10,2)",
  "reorder_level": "decimal (max 10,2)",
  "warehouse_location": "string (max 100)",
  "primary_supplier_id": "uuid (optional)",
  "status": "enum (ACTIVE, INACTIVE, DISCONTINUED)",
  "is_critical": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime (optional)"
}
```

### StockMovement Model
```json
{
  "id": "uuid",
  "item_id": "uuid",
  "movement_type": "enum (IN, OUT, ADJUST, TRANSFER)",
  "reason": "enum (PURCHASE, MAINTENANCE, ADJUSTMENT, etc.)",
  "quantity": "decimal (max 10,2)",
  "reference_type": "string (max 50, optional)",
  "reference_id": "string (max 100, optional)",
  "performed_by": "uuid",
  "movement_date": "datetime",
  "notes": "string (max 1000, optional)"
}
```

### Supplier Model
```json
{
  "id": "uuid",
  "name": "string (max 255)",
  "code": "string (max 20, unique)",
  "type": "enum (PARTS_SUPPLIER, SERVICE_PROVIDER, etc.)",
  "contact_person": "string (max 255, optional)",
  "email": "string (max 255, optional)",
  "phone": "string (max 20, optional)",
  "address": "string (max 500, optional)",
  "payment_terms": "string (max 100, optional)",
  "delivery_time_days": "integer (optional)",
  "performance_rating": "float (0-5, optional)",
  "status": "enum (ACTIVE, INACTIVE, SUSPENDED)",
  "created_at": "datetime"
}
```

### PurchaseOrder Model
```json
{
  "id": "uuid",
  "po_number": "string (unique)",
  "supplier_id": "uuid",
  "status": "enum (DRAFT, PENDING, APPROVED, SENT, RECEIVED)",
  "subtotal": "decimal (max 12,2)",
  "total_amount": "decimal (max 12,2)",
  "order_date": "date",
  "required_date": "date (optional)",
  "items": [
    {
      "item_id": "uuid",
      "quantity": "decimal",
      "unit_cost": "decimal",
      "total_cost": "decimal"
    }
  ],
  "created_at": "datetime"
}
```

## 4. Frontend Integration Guidelines

### HTTP Client Configuration
```javascript
// Axios configuration
const apiClient = axios.create({
  baseURL: 'https://api.example.com/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor for auth
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Authentication Header Format
```
Authorization: Bearer <jwt_token>
```

### Error Handling Pattern
```javascript
// Standard error response format
{
  "detail": "Error message",
  "errors": [
    {
      "field": "field_name",
      "message": "Validation error message"
    }
  ]
}

// Error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### Rate Limiting
- No specific rate limits configured
- Standard HTTP 429 Too Many Requests if limits exceeded

### CORS Policy
- Allowed origins: `http://localhost:3000`, `http://localhost:8080`
- Credentials allowed: Yes
- Methods: GET, POST, PUT, DELETE

## 5. Testing & Support Tools

### Example API Calls

#### Create Item
```bash
curl -X POST "https://api.example.com/api/v1/items" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Brake Pads",
    "sku": "BP-001",
    "category": "BRAKE_PARTS",
    "unit": "SET",
    "unit_cost": 85.00,
    "current_quantity": 25,
    "reorder_level": 5
  }'
```

#### Get Low Stock Items
```bash
curl -X GET "https://api.example.com/api/v1/items/low-stock" \
  -H "Authorization: Bearer <token>"
```

### Sample Postman Collection Structure
```json
{
  "info": {
    "name": "Inventory Service API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "auth": {
    "type": "bearer",
    "bearer": [{"key": "token", "value": "{{access_token}}"}]
  },
  "item": [
    {
      "name": "Items",
      "item": [
        {"name": "Get Items", "request": {"method": "GET", "url": "{{base_url}}/items"}},
        {"name": "Create Item", "request": {"method": "POST", "url": "{{base_url}}/items"}}
      ]
    }
  ]
}
```

### Mock Data Examples
```javascript
// Mock item data for development
const mockItems = [
  {
    id: "550e8400-e29b-41d4-a716-446655440000",
    name: "Engine Oil 5W-30",
    sku: "EO-5W30-001",
    category: "FLUIDS",
    unit: "LITER",
    unit_cost: 12.50,
    current_quantity: 150,
    reorder_level: 30,
    is_low_stock: false
  },
  {
    id: "550e8400-e29b-41d4-a716-446655440001",
    name: "Brake Disc Front",
    sku: "BD-F-001",
    category: "BRAKE_PARTS",
    unit: "PIECE",
    unit_cost: 95.00,
    current_quantity: 8,
    reorder_level: 10,
    is_low_stock: true
  }
];
```

### Common Frontend Patterns
```javascript
// Fetch items with pagination
const fetchItems = async (page = 1, filters = {}) => {
  const params = new URLSearchParams({
    page: page.toString(),
    size: '20',
    ...filters
  });
  
  const response = await apiClient.get(`/items?${params}`);
  return response.data;
};

// Create new item
const createItem = async (itemData) => {
  const response = await apiClient.post('/items', itemData);
  return response.data;
};

// Adjust stock
const adjustStock = async (itemId, adjustment) => {
  const response = await apiClient.post(`/items/${itemId}/adjust-stock`, adjustment);
  return response.data;
};
```
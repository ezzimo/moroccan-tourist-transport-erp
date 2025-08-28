# Inventory Management Microservice

A comprehensive inventory management microservice for the Moroccan Tourist Transport ERP system, built with FastAPI, SQLModel, and PostgreSQL.

## Features

### 📦 **Item Management**
- **Complete Item Catalog**: Track spare parts, tools, office supplies, and consumables
- **Multi-Category Support**: Engine parts, tires, fluids, electrical, tools, office supplies
- **Stock Level Monitoring**: Real-time quantity tracking with reorder alerts
- **Multi-Warehouse Support**: Track items across multiple warehouse locations
- **Barcode Integration**: SKU and barcode support for efficient tracking
- **Expiry Management**: Track items with expiration dates and shelf life

### 📊 **Stock Movement Tracking**
- **Complete Movement History**: Track all IN, OUT, ADJUST, TRANSFER movements
- **Reference Linking**: Link movements to maintenance jobs, purchase orders, etc.
- **Audit Trail**: Complete traceability with user and timestamp information
- **Bulk Operations**: Support for bulk stock movements
- **Cost Tracking**: Track unit costs and total values for all movements
- **Automated Calculations**: Automatic stock level updates and average cost calculations

### 🏢 **Supplier Management**
- **Vendor Database**: Complete supplier information and contact details
- **Performance Tracking**: On-time delivery rates and quality ratings
- **Contract Management**: Track contract periods and terms
- **Multi-Supplier Support**: Multiple suppliers per item with preferred vendor selection
- **Evaluation System**: Rate suppliers on delivery, quality, and communication
- **Purchase History**: Complete order history and spending analysis

### 📋 **Purchase Order Management**
- **Complete PO Lifecycle**: Draft → Pending → Approved → Sent → Received
- **Approval Workflows**: Multi-level approval based on order value
- **Receiving Management**: Partial and complete receiving with quantity tracking
- **Cost Tracking**: Track subtotals, taxes, shipping, and discounts
- **Delivery Monitoring**: Expected vs actual delivery date tracking
- **Auto-Generation**: Generate POs from reorder suggestions

### 📈 **Analytics & Reporting**
- **Real-time Dashboard**: Live inventory metrics and KPIs
- **Stock Level Analytics**: Current stock, low stock alerts, and trends
- **Inventory Valuation**: FIFO, LIFO, and average cost methods
- **Turnover Analysis**: Inventory turnover rates and velocity
- **ABC Analysis**: Classify items by value and importance
- **Consumption Patterns**: Usage trends and forecasting
- **Supplier Performance**: Delivery and quality metrics

## API Endpoints

### Item Management
- `POST /api/v1/items/` - Create new item
- `GET /api/v1/items/` - List items with search and filters
- `GET /api/v1/items/summary` - Get inventory summary statistics
- `GET /api/v1/items/low-stock` - Get low stock items
- `GET /api/v1/items/reorder-suggestions` - Get reorder suggestions
- `GET /api/v1/items/{id}` - Get item details
- `PUT /api/v1/items/{id}` - Update item information
- `POST /api/v1/items/{id}/adjust-stock` - Adjust stock quantity
- `DELETE /api/v1/items/{id}` - Delete item
- `GET /api/v1/items/{id}/movements` - Get item movement history

### Stock Movement Management
- `POST /api/v1/movements/` - Create stock movement
- `POST /api/v1/movements/bulk` - Create bulk movements
- `GET /api/v1/movements/` - List movements with filters
- `GET /api/v1/movements/summary` - Get movement statistics
- `GET /api/v1/movements/{id}` - Get movement details
- `PUT /api/v1/movements/{id}` - Update movement
- `GET /api/v1/movements/item/{id}` - Get item movement history
- `GET /api/v1/movements/reference/{type}/{id}` - Get movements by reference

### Supplier Management
- `POST /api/v1/suppliers/` - Create new supplier
- `GET /api/v1/suppliers/` - List suppliers with filters
- `GET /api/v1/suppliers/summary` - Get supplier statistics
- `GET /api/v1/suppliers/performance` - Get performance report
- `GET /api/v1/suppliers/{id}` - Get supplier details
- `PUT /api/v1/suppliers/{id}` - Update supplier information
- `DELETE /api/v1/suppliers/{id}` - Delete supplier
- `POST /api/v1/suppliers/{id}/evaluate` - Evaluate supplier
- `GET /api/v1/suppliers/{id}/items` - Get supplier items
- `GET /api/v1/suppliers/{id}/orders` - Get supplier orders

### Purchase Order Management
- `POST /api/v1/purchase-orders/` - Create purchase order
- `POST /api/v1/purchase-orders/generate` - Generate from reorder suggestions
- `GET /api/v1/purchase-orders/` - List purchase orders
- `GET /api/v1/purchase-orders/summary` - Get PO statistics
- `GET /api/v1/purchase-orders/pending-approval` - Get pending approvals
- `GET /api/v1/purchase-orders/{id}` - Get PO details
- `PUT /api/v1/purchase-orders/{id}` - Update PO
- `POST /api/v1/purchase-orders/{id}/approve` - Approve/reject PO
- `POST /api/v1/purchase-orders/{id}/send` - Send PO to supplier
- `POST /api/v1/purchase-orders/{id}/receive` - Receive PO items
- `POST /api/v1/purchase-orders/{id}/cancel` - Cancel PO

### Analytics & Reporting
- `GET /api/v1/analytics/dashboard` - Inventory dashboard
- `GET /api/v1/analytics/stock-levels` - Stock level analytics
- `GET /api/v1/analytics/valuation` - Inventory valuation
- `GET /api/v1/analytics/turnover` - Turnover analysis
- `GET /api/v1/analytics/consumption` - Consumption patterns
- `GET /api/v1/analytics/abc-analysis` - ABC analysis
- `GET /api/v1/analytics/supplier-performance` - Supplier analytics
- `GET /api/v1/analytics/cost-analysis` - Cost analysis
- `GET /api/v1/analytics/alerts` - Current alerts
- `GET /api/v1/analytics/forecasting` - Demand forecasting
- `GET /api/v1/analytics/export/stock-report` - Export stock report
- `GET /api/v1/analytics/export/movement-report` - Export movement report
- `GET /api/v1/analytics/export/valuation-report` - Export valuation report

## Quick Start

### Using Docker Compose (Recommended)
```bash
# Clone and setup
cd inventory_service

# Copy environment variables
cp .env.example .env

# Start services
docker-compose up -d

# Check health
curl http://localhost:8008/health
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env

# Start PostgreSQL and Redis services
# Update .env with connection strings

# Run application
python -m inventory_service.main
```

## Configuration

Key environment variables in `.env`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5440/inventory_db
REDIS_URL=redis://localhost:6387/8
AUTH_SERVICE_URL=http://auth_service:8000
FLEET_SERVICE_URL=http://fleet_app:8004
FINANCIAL_SERVICE_URL=http://financial_app:8006
DEFAULT_CURRENCY=MAD
LOW_STOCK_ALERT_THRESHOLD=0.2
AUTO_REORDER_ENABLED=false
```

## Data Models

### Item
- **Basic Info**: name, SKU, barcode, category, brand, model
- **Stock Info**: current quantity, reserved quantity, reorder level
- **Pricing**: unit cost, average cost, currency
- **Location**: warehouse, bin location
- **Supplier**: primary supplier relationship
- **Expiry**: expiration tracking for perishable items

### StockMovement
- **Movement Info**: type (IN/OUT/ADJUST), reason, quantity
- **Cost Info**: unit cost, total cost
- **Reference**: link to maintenance jobs, purchase orders
- **Audit**: performed by, approved by, timestamps
- **Location**: from/to location for transfers

### Supplier
- **Contact Info**: name, contact person, address, phone, email
- **Business Info**: tax ID, registration, payment terms
- **Performance**: delivery rate, quality rating, total orders
- **Contract**: start/end dates, terms and conditions

### PurchaseOrder
- **Order Info**: PO number, supplier, status, priority
- **Financial**: subtotal, tax, shipping, discount, total
- **Dates**: order date, required date, delivery dates
- **Items**: line items with quantities and costs
- **Workflow**: approval and receiving tracking

## Security & Integration

- **JWT Authentication**: Integration with auth microservice
- **Role-Based Access Control**: Granular permissions per endpoint
- **Audit Logging**: Complete audit trail for all operations
- **Data Validation**: Comprehensive input validation and sanitization
- **Service Integration**: Fleet, Financial, HR service integration

## Real-time Features

- **Low Stock Alerts**: Automatic alerts when items reach reorder level
- **Expiry Warnings**: Alerts for items approaching expiration
- **Purchase Order Notifications**: Status updates and approvals
- **Performance Monitoring**: Real-time supplier performance tracking

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=inventory_service

# Run specific test file
pytest inventory_service/tests/test_items.py -v
```

## Integration with ERP Ecosystem

The inventory microservice integrates seamlessly with other ERP components:

- **Fleet Service**: Vehicle maintenance parts and supplies
- **Financial Service**: Purchase order costs and expense tracking
- **HR Service**: Office supplies and equipment
- **Auth Service**: User authentication and authorization
- **Notification Service**: Alerts and notifications

## Performance & Scalability

- **Database Optimization**: Indexed queries and efficient pagination
- **Redis Caching**: Fast alert delivery and session management
- **Async Operations**: Non-blocking I/O for better performance
- **Horizontal Scaling**: Stateless design for easy scaling
- **Connection Pooling**: Efficient database connection management

## Moroccan Market Considerations

- **Multi-language Support**: Arabic, French, English inventory management
- **Currency Support**: Moroccan Dirham (MAD) as default currency
- **Local Suppliers**: Support for Moroccan supplier information
- **Compliance**: Morocco business regulations and tax requirements
- **Cultural Considerations**: Respect for local business practices

## Contributing

1. Follow the modular architecture pattern
2. Add comprehensive tests for new features
3. Update documentation and API schemas
4. Follow Python code style guidelines
5. Ensure proper error handling and validation

## License

Private - Moroccan Tourist Transport ERP System
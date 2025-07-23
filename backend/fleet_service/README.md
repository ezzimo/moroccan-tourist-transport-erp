# Fleet Management Microservice

A comprehensive fleet management microservice for the Moroccan Tourist Transport ERP system, built with FastAPI, SQLModel, and PostgreSQL.

## Features

### 🚗 Vehicle Management
- **Complete Vehicle Inventory**: Track all vehicle details including type, capacity, specifications
- **Real-time Status Tracking**: Available, In Use, Under Maintenance, Out of Service, Retired
- **Compliance Monitoring**: Automatic tracking of registration, insurance, and inspection expiry
- **Vehicle Assignment**: Assign vehicles to tour instances with conflict detection
- **Availability Checking**: Real-time availability verification for date ranges

### 🔧 Maintenance Management
- **Preventive Maintenance Scheduling**: Schedule and track regular maintenance
- **Service History**: Complete maintenance records with costs and parts
- **Maintenance Alerts**: Automatic reminders for upcoming service
- **Warranty Tracking**: Track warranty periods for repairs and parts
- **Cost Analysis**: Detailed maintenance cost tracking and reporting

### 📋 Assignment Management
- **Tour Integration**: Seamless integration with tour operations service
- **Conflict Detection**: Prevent double-booking with intelligent conflict checking
- **Assignment Lifecycle**: Complete workflow from scheduled to completed
- **Driver Assignment**: Link drivers to vehicle assignments
- **Odometer Tracking**: Track vehicle usage with start/end odometer readings

### ⛽ Fuel Management
- **Fuel Consumption Tracking**: Detailed fuel logs with efficiency calculations
- **Cost Monitoring**: Track fuel costs and price trends
- **Efficiency Analysis**: Calculate fuel efficiency and cost per kilometer
- **Station Tracking**: Record fuel station information and receipts
- **Reporting**: Comprehensive fuel consumption reports and statistics

### 📄 Document Management
- **Digital Document Storage**: Upload and manage vehicle documents
- **Compliance Documents**: Registration, insurance, inspection certificates
- **Expiry Alerts**: Automatic alerts for document renewals
- **Document Verification**: Approval workflow for document validation
- **Secure Storage**: Encrypted document storage with access control

## API Endpoints

### Vehicle Management
- `POST /api/v1/vehicles/` - Create new vehicle
- `GET /api/v1/vehicles/` - List vehicles with search and filters
- `GET /api/v1/vehicles/available` - Get available vehicles for period
- `GET /api/v1/vehicles/compliance-alerts` - Get compliance alerts
- `GET /api/v1/vehicles/{id}` - Get vehicle details
- `GET /api/v1/vehicles/{id}/summary` - Get comprehensive vehicle summary
- `GET /api/v1/vehicles/{id}/availability` - Check vehicle availability
- `PUT /api/v1/vehicles/{id}` - Update vehicle information
- `DELETE /api/v1/vehicles/{id}` - Deactivate vehicle

### Maintenance Management
- `POST /api/v1/maintenance/` - Create maintenance record
- `GET /api/v1/maintenance/` - List maintenance records with filters
- `GET /api/v1/maintenance/upcoming` - Get upcoming maintenance
- `GET /api/v1/maintenance/stats` - Get maintenance statistics
- `GET /api/v1/maintenance/{id}` - Get maintenance record details
- `PUT /api/v1/maintenance/{id}` - Update maintenance record
- `DELETE /api/v1/maintenance/{id}` - Delete maintenance record
- `GET /api/v1/maintenance/vehicle/{id}` - Get vehicle maintenance history

### Assignment Management
- `POST /api/v1/assignments/` - Create new assignment
- `GET /api/v1/assignments/` - List assignments with filters
- `GET /api/v1/assignments/{id}` - Get assignment details
- `PUT /api/v1/assignments/{id}` - Update assignment
- `POST /api/v1/assignments/{id}/cancel` - Cancel assignment
- `POST /api/v1/assignments/{id}/start` - Start assignment
- `POST /api/v1/assignments/{id}/complete` - Complete assignment
- `GET /api/v1/assignments/vehicle/{id}` - Get vehicle assignments

### Fuel Management
- `POST /api/v1/fuel/` - Create fuel log entry
- `GET /api/v1/fuel/` - List fuel logs with filters
- `GET /api/v1/fuel/stats` - Get fuel consumption statistics
- `GET /api/v1/fuel/{id}` - Get fuel log details
- `PUT /api/v1/fuel/{id}` - Update fuel log
- `DELETE /api/v1/fuel/{id}` - Delete fuel log
- `GET /api/v1/fuel/vehicle/{id}` - Get vehicle fuel history

### Document Management
- `POST /api/v1/documents/upload` - Upload vehicle document
- `GET /api/v1/documents/` - List documents with filters
- `GET /api/v1/documents/expiring` - Get expiring documents
- `GET /api/v1/documents/{id}` - Get document details
- `PUT /api/v1/documents/{id}` - Update document information
- `DELETE /api/v1/documents/{id}` - Delete document
- `GET /api/v1/documents/vehicle/{id}` - Get vehicle documents

## Quick Start

### Using Docker Compose (Recommended)
```bash
# Clone and setup
cd fleet_service

# Copy environment variables
cp .env.example .env

# Start services
docker-compose up -d

# Check health
curl http://localhost:8004/health
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
python -m fleet_service.main
```

## Configuration

Key environment variables in `.env`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5436/fleet_db
REDIS_URL=redis://localhost:6383/4
AUTH_SERVICE_URL=http://localhost:8000
CRM_SERVICE_URL=http://localhost:8001
BOOKING_SERVICE_URL=http://localhost:8002
TOUR_SERVICE_URL=http://localhost:8003
SECRET_KEY=your-super-secret-key
MAINTENANCE_ALERT_DAYS=7
COMPLIANCE_ALERT_DAYS=30
```

## Data Models

### Vehicle
- **Basic Info**: license_plate, vehicle_type, brand, model, year, color
- **Specifications**: seating_capacity, fuel_type, engine_size, transmission
- **Status**: status, current_odometer, is_active
- **Compliance**: registration_expiry, insurance_expiry, inspection_expiry
- **Purchase**: purchase_date, purchase_price, vin_number

### MaintenanceRecord
- **Service Info**: maintenance_type, description, date_performed
- **Provider**: provider_name, provider_contact
- **Cost**: cost, currency, labor_hours, parts_replaced
- **Schedule**: next_service_date, next_service_odometer
- **Warranty**: warranty_until, is_completed

### Assignment
- **References**: vehicle_id, tour_instance_id, driver_id
- **Schedule**: start_date, end_date, status
- **Tracking**: start_odometer, end_odometer, actual_dates
- **Details**: pickup_location, dropoff_location, estimated_distance

### FuelLog
- **Consumption**: date, odometer_reading, fuel_amount, fuel_cost
- **Efficiency**: distance_since_last_fill, fuel_efficiency
- **Location**: station_name, location, receipt_number
- **Trip**: trip_purpose, driver_id, is_full_tank

### Document
- **File Info**: document_type, title, file_name, file_path, file_size
- **Validity**: issue_date, expiry_date, issuing_authority
- **Status**: is_active, is_verified, verification_dates

## Security & Integration

- **JWT Authentication**: Integration with auth microservice
- **Role-Based Access Control**: Granular permissions per endpoint
- **Document Security**: Secure file upload and storage
- **Service Integration**: Seamless communication with Tour Operations service
- **Audit Logging**: Track all fleet modifications and assignments

## Real-time Features

- **Compliance Alerts**: Automatic notifications for expiring documents
- **Maintenance Reminders**: Proactive maintenance scheduling alerts
- **Assignment Updates**: Real-time status changes for vehicle assignments
- **Availability Notifications**: Instant updates on vehicle availability

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=fleet_service

# Run specific test file
pytest fleet_service/tests/test_vehicles.py -v
```

## Integration with ERP Ecosystem

The fleet management microservice integrates seamlessly with other ERP components:

- **Authentication Service**: User authentication and authorization
- **CRM Service**: Customer information for assignment context
- **Booking Service**: Booking details for vehicle requirements
- **Tour Operations**: Tour instance assignment and coordination
- **Business Intelligence**: Fleet analytics and performance reporting

## Performance & Scalability

- **Database Optimization**: Indexed queries and efficient pagination
- **Redis Caching**: Fast notification delivery and session management
- **Async Operations**: Non-blocking I/O for better performance
- **Horizontal Scaling**: Stateless design for easy scaling
- **File Management**: Efficient document storage and retrieval

## Moroccan Market Considerations

- **Local Compliance**: Morocco-specific vehicle registration and inspection requirements
- **Multi-language Support**: Arabic, French, English documentation
- **Currency Support**: Moroccan Dirham (MAD) as default currency
- **Regional Adaptation**: Support for Moroccan fuel stations and service providers
- **Cultural Considerations**: Respect for local business practices and regulations

## Contributing

1. Follow the modular architecture pattern
2. Add comprehensive tests for new features
3. Update documentation and API schemas
4. Follow Python code style guidelines
5. Ensure proper error handling and validation

## License

Private - Moroccan Tourist Transport ERP System
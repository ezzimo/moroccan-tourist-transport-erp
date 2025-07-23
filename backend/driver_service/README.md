# Driver Management Microservice

A comprehensive driver management microservice for the Moroccan Tourist Transport ERP system, built with FastAPI, SQLModel, and PostgreSQL.

## Features

### 👨‍💼 **Driver Profile Management**
- **Complete Driver Registry**: Personal info, contact details, employment data
- **License Management**: License types (B, C, D, D1, Professional) with expiry tracking
- **Health Compliance**: Health certificate tracking with expiry alerts
- **Skills & Certifications**: Language skills, tour guide, first aid certifications
- **Document Management**: Secure upload and storage of driver documents
- **Status Tracking**: Active, On Leave, In Training, Suspended, Terminated

### 🚗 **Assignment Management**
- **Tour Assignment**: Link drivers to specific tour instances
- **Vehicle Integration**: Connect with fleet management for vehicle assignments
- **Status Tracking**: Assigned → Confirmed → In Progress → Completed
- **Performance Monitoring**: Customer ratings, on-time performance, completion rates
- **Conflict Detection**: Prevent double-booking and scheduling conflicts

### 📚 **Training & Development**
- **Training Programs**: First Aid, Defensive Driving, Customer Service, Languages
- **Certification Tracking**: Issue and expiry date management
- **Performance Scoring**: Training scores with pass/fail determination
- **Mandatory Training**: Track compliance with required training
- **Certificate Management**: Digital certificate storage and validation

### 🚨 **Incident Management**
- **Incident Types**: Accidents, Complaints, Delays, Misconduct, Safety Violations
- **Severity Classification**: Minor, Moderate, Major, Critical
- **Investigation Workflow**: Complete investigation and resolution tracking
- **Cost Impact**: Track financial impact and insurance claims
- **Follow-up Actions**: Corrective and preventive measures

### 📱 **Mobile API**
- **Driver Dashboard**: View assignments, schedules, and notifications
- **Offline Support**: Critical data available without internet
- **Assignment Details**: Tour information, customer details, itineraries
- **Status Updates**: Real-time assignment status updates
- **Document Access**: View certificates and important documents

## API Endpoints

### Driver Management
- `POST /api/v1/drivers/` - Create new driver
- `GET /api/v1/drivers/` - List drivers with search and filters
- `GET /api/v1/drivers/summary` - Get driver statistics
- `GET /api/v1/drivers/{id}` - Get driver details
- `PUT /api/v1/drivers/{id}` - Update driver information
- `DELETE /api/v1/drivers/{id}` - Deactivate driver
- `GET /api/v1/drivers/available` - Get available drivers
- `GET /api/v1/drivers/expiring-licenses` - Get drivers with expiring licenses

### Assignment Management
- `POST /api/v1/assignments/` - Create driver assignment
- `GET /api/v1/assignments/` - List assignments with filters
- `GET /api/v1/assignments/{id}` - Get assignment details
- `PUT /api/v1/assignments/{id}` - Update assignment
- `POST /api/v1/assignments/{id}/confirm` - Confirm assignment
- `POST /api/v1/assignments/{id}/start` - Start assignment
- `POST /api/v1/assignments/{id}/complete` - Complete assignment
- `DELETE /api/v1/assignments/{id}` - Cancel assignment

### Training Management
- `POST /api/v1/training/` - Create training record
- `GET /api/v1/training/` - List training records
- `GET /api/v1/training/{id}` - Get training details
- `PUT /api/v1/training/{id}` - Update training record
- `POST /api/v1/training/{id}/complete` - Complete training
- `GET /api/v1/training/expiring` - Get expiring certifications
- `GET /api/v1/training/driver/{id}` - Get driver training history

### Incident Management
- `POST /api/v1/incidents/` - Report new incident
- `GET /api/v1/incidents/` - List incidents with filters
- `GET /api/v1/incidents/{id}` - Get incident details
- `PUT /api/v1/incidents/{id}` - Update incident
- `POST /api/v1/incidents/{id}/resolve` - Resolve incident
- `GET /api/v1/incidents/driver/{id}` - Get driver incidents
- `GET /api/v1/incidents/overdue` - Get overdue incidents

### Document Management
- `POST /api/v1/documents/upload` - Upload driver document
- `GET /api/v1/documents/` - List documents with filters
- `GET /api/v1/documents/{id}` - Get document details
- `PUT /api/v1/documents/{id}` - Update document
- `DELETE /api/v1/documents/{id}` - Delete document
- `GET /api/v1/documents/driver/{id}` - Get driver documents
- `GET /api/v1/documents/expiring` - Get expiring documents

### Mobile API
- `GET /api/v1/mobile/driver/{id}/dashboard` - Driver dashboard
- `GET /api/v1/mobile/driver/{id}/assignments` - Current assignments
- `GET /api/v1/mobile/assignments/{id}/details` - Assignment details
- `POST /api/v1/mobile/assignments/{id}/status` - Update assignment status
- `GET /api/v1/mobile/driver/{id}/documents` - Driver documents
- `POST /api/v1/mobile/incidents/report` - Report incident

## Quick Start

### Using Docker Compose (Recommended)
```bash
# Clone and setup
cd driver_service

# Copy environment variables
cp .env.example .env

# Start services
docker-compose up -d

# Check health
curl http://localhost:8010/health
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
python -m driver_service.main
```

## Configuration

Key environment variables in `.env`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5442/driver_db
REDIS_URL=redis://localhost:6389/10
AUTH_SERVICE_URL=http://localhost:8000
TOUR_SERVICE_URL=http://localhost:8003
FLEET_SERVICE_URL=http://localhost:8004
LICENSE_ALERT_DAYS=30
HEALTH_CERT_ALERT_DAYS=60
MAX_DAILY_HOURS=10
```

## Data Models

### Driver
- **Personal Info**: name, birth date, gender, nationality, contact details
- **Employment**: employee ID, type, hire date, status
- **License**: number, type, issue/expiry dates, issuing authority
- **Skills**: languages, certifications (tour guide, first aid)
- **Health**: health certificate expiry, medical restrictions
- **Performance**: rating, tours completed, incidents

### DriverAssignment
- **Assignment Info**: driver, tour, vehicle, dates, status
- **Performance**: actual times, customer rating, feedback
- **Metadata**: assigned by, special instructions, notes

### DriverTrainingRecord
- **Training Info**: type, title, provider, location
- **Scheduling**: dates, duration, trainer
- **Results**: score, pass/fail, certificate details
- **Feedback**: trainer and driver feedback

### DriverIncident
- **Incident Info**: type, severity, description, location
- **Investigation**: status, notes, resolution
- **Impact**: costs, insurance claims, follow-up actions

### DriverDocument
- **Document Info**: type, title, file information
- **Metadata**: issue/expiry dates, issuing authority
- **Workflow**: upload, review, approval status

## Security & Integration

- **JWT Authentication**: Integration with auth microservice
- **Role-Based Access Control**: Granular permissions per endpoint
- **Document Security**: Secure file upload and storage
- **Mobile Security**: Secure mobile API with session management
- **Service Integration**: Tour Operations, Fleet, HR, Notification services

## Morocco Compliance Features

- **Professional Driver Licenses**: Support for Morocco license categories
- **Health Certificates**: Track mandatory health certifications
- **Tourism Law Training**: Compliance with Morocco tourism regulations
- **Language Requirements**: Track Arabic, French, English proficiency
- **Safety Standards**: Morocco transport safety compliance

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=driver_service

# Run specific test file
pytest driver_service/tests/test_drivers.py -v
```

## Integration with ERP Ecosystem

The driver management microservice integrates seamlessly with other ERP components:

- **Tour Operations**: Driver assignment to tour instances
- **Fleet Management**: Vehicle assignment and maintenance coordination
- **HR Service**: Employee data synchronization and training
- **Notification Service**: Alerts for assignments, expiries, incidents
- **Auth Service**: User authentication and authorization

## Performance & Scalability

- **Database Optimization**: Indexed queries and efficient pagination
- **Redis Caching**: Fast session management and notifications
- **Async Operations**: Non-blocking I/O for better performance
- **Mobile Optimization**: Offline-capable endpoints for drivers
- **Horizontal Scaling**: Stateless design for easy scaling

## Moroccan Market Considerations

- **Multi-language Support**: Arabic, French, English driver interfaces
- **Local Regulations**: Morocco transport and tourism law compliance
- **Cultural Sensitivity**: Respect for local customs and practices
- **Mobile-First**: Optimized for mobile usage by drivers
- **Offline Capability**: Critical features work without internet

## Contributing

1. Follow the modular architecture pattern
2. Add comprehensive tests for new features
3. Update documentation and API schemas
4. Follow Python code style guidelines
5. Ensure proper error handling and validation

## License

Private - Moroccan Tourist Transport ERP System
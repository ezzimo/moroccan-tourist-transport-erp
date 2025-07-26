# Driver Management Microservice

A comprehensive driver management system for Moroccan Tourist Transport ERP, built with FastAPI, SQLModel, and PostgreSQL.

## 🎯 Overview

The Driver Management microservice handles all administrative and operational aspects of professional drivers including:

- Driver profile and document management
- License and certification tracking
- Tour assignment and scheduling
- Training record management
- Incident reporting and tracking
- Mobile API for driver access
- Compliance monitoring and alerts

## 🏗️ Architecture

### Tech Stack
- **Framework**: FastAPI 0.104.1
- **ORM**: SQLModel 0.0.14
- **Database**: PostgreSQL 15
- **Authentication**: JWT with RBAC
- **File Storage**: Local filesystem (S3-compatible ready)
- **Cache**: Redis 7
- **Testing**: pytest + httpx

### Service Layer Pattern
```
├── models/          # SQLModel database models
├── schemas/         # Pydantic request/response models
├── services/        # Business logic layer
├── routers/         # FastAPI route handlers
├── utils/           # Utilities and dependencies
└── tests/           # Comprehensive test suite
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Environment Setup

1. **Clone and navigate to the service**:
```bash
cd driver_service
```

2. **Copy environment variables**:
```bash
cp .env.example .env
```

3. **Configure environment variables** in `.env`:
```env
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5442/driver_db

# Redis Configuration
REDIS_URL=redis://localhost:6389/10

# Service Integration
AUTH_SERVICE_URL=http://localhost:8000
TOUR_SERVICE_URL=http://localhost:8003
FLEET_SERVICE_URL=http://localhost:8004
HR_SERVICE_URL=http://localhost:8005
NOTIFICATION_SERVICE_URL=http://localhost:8007

# JWT Configuration (should match auth service)
SECRET_KEY=your-super-secret-jwt-key-change-in-production
ALGORITHM=HS256

# File Upload
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=["pdf","jpg","jpeg","png","doc","docx"]

# Driver Configuration
LICENSE_ALERT_DAYS=30
HEALTH_CERT_ALERT_DAYS=60
TRAINING_VALIDITY_MONTHS=24
```

### Installation & Running

#### Option 1: Docker Compose (Recommended)
```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f app

# Stop services
docker-compose down
```

#### Option 2: Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL and Redis
# Update .env with connection strings

# Run database migrations
alembic upgrade head

# Start the application
python -m driver_service.main

# Or with uvicorn directly
uvicorn driver_service.main:app --host 0.0.0.0 --port 8010 --reload
```

### Health Check
```bash
curl http://localhost:8010/health
```

## 📊 Database Schema

### Core Entities

#### Driver
```sql
CREATE TABLE drivers (
    id UUID PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) NOT NULL,
    nationality VARCHAR(100) DEFAULT 'Moroccan',
    national_id VARCHAR(20) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    license_number VARCHAR(50) UNIQUE NOT NULL,
    license_type VARCHAR(20) NOT NULL,
    license_expiry_date DATE NOT NULL,
    employment_type VARCHAR(20) NOT NULL,
    health_certificate_expiry DATE,
    status VARCHAR(20) DEFAULT 'Active',
    languages_spoken TEXT, -- JSON array
    performance_rating FLOAT,
    total_tours_completed INTEGER DEFAULT 0,
    total_incidents INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

#### Driver Assignment
```sql
CREATE TABLE driver_assignments (
    id UUID PRIMARY KEY,
    driver_id UUID REFERENCES drivers(id),
    tour_instance_id UUID NOT NULL,
    vehicle_id UUID,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'Assigned',
    assigned_by UUID NOT NULL,
    assigned_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Training Record
```sql
CREATE TABLE driver_training_records (
    id UUID PRIMARY KEY,
    driver_id UUID REFERENCES drivers(id),
    training_type VARCHAR(50) NOT NULL,
    training_title VARCHAR(255) NOT NULL,
    scheduled_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'Scheduled',
    score FLOAT,
    certificate_valid_until DATE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Incident
```sql
CREATE TABLE driver_incidents (
    id UUID PRIMARY KEY,
    driver_id UUID REFERENCES drivers(id),
    incident_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    incident_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'Reported',
    reported_by UUID NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔌 API Endpoints

### Driver Management
```
POST   /api/v1/drivers                    # Create driver
GET    /api/v1/drivers                    # List drivers
GET    /api/v1/drivers/{id}               # Get driver details
PUT    /api/v1/drivers/{id}               # Update driver
DELETE /api/v1/drivers/{id}               # Delete driver
GET    /api/v1/drivers/summary            # Driver statistics
```

### Assignment Management
```
POST   /api/v1/assignments                # Create assignment
GET    /api/v1/assignments                # List assignments
GET    /api/v1/assignments/{id}           # Get assignment
PUT    /api/v1/assignments/{id}           # Update assignment
PUT    /api/v1/assignments/{id}/confirm   # Confirm assignment
PUT    /api/v1/assignments/{id}/complete  # Complete assignment
```

### Training Management
```
POST   /api/v1/training                   # Create training record
GET    /api/v1/training                   # List training records
GET    /api/v1/training/{id}              # Get training record
PUT    /api/v1/training/{id}/complete     # Mark training complete
```

### Incident Management
```
POST   /api/v1/incidents                  # Report incident
GET    /api/v1/incidents                  # List incidents
GET    /api/v1/incidents/{id}             # Get incident
PUT    /api/v1/incidents/{id}/resolve     # Resolve incident
```

### Mobile API
```
GET    /api/v1/mobile/dashboard           # Driver dashboard
GET    /api/v1/mobile/assignments         # My assignments
PUT    /api/v1/mobile/assignments/{id}/status # Update status
POST   /api/v1/mobile/incidents           # Report incident
GET    /api/v1/mobile/offline-bundle      # Offline data
```

### Document Management
```
POST   /api/v1/drivers/{id}/documents     # Upload document
GET    /api/v1/drivers/{id}/documents     # List documents
PUT    /api/v1/drivers/{id}/documents/{doc_id}/approve # Approve
```

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=driver_service --cov-report=html

# Run specific test file
pytest tests/test_drivers.py -v

# Run tests with output
pytest -s -v
```

### Test Structure
```
tests/
├── conftest.py              # Test configuration
├── test_drivers.py          # Driver CRUD tests
├── test_assignments.py      # Assignment tests
├── test_training.py         # Training tests
├── test_incidents.py        # Incident tests
├── test_mobile.py           # Mobile API tests
└── test_utils.py            # Utility tests
```

### Test Coverage Requirements
- **Minimum Coverage**: 90%
- **Critical Paths**: 100% (authentication, assignments, compliance)
- **Integration Tests**: All external service calls mocked

## 🔒 Security

### Authentication & Authorization
- **JWT Tokens**: Bearer token authentication
- **RBAC**: Role-based access control
- **Permissions**: Fine-grained permissions (e.g., `drivers:create:all`)

### File Upload Security
- **File Type Validation**: MIME type checking
- **Size Limits**: 10MB maximum
- **Virus Scanning**: Ready for integration
- **Secure Storage**: Path traversal protection

### Data Protection
- **Input Validation**: Comprehensive Pydantic validation
- **SQL Injection**: SQLModel ORM protection
- **XSS Prevention**: Output encoding
- **Rate Limiting**: Redis-based rate limiting

## 📈 Performance

### Optimization Features
- **Database Indexing**: Optimized queries
- **Connection Pooling**: PostgreSQL connection pool
- **Caching**: Redis caching for frequent queries
- **Pagination**: Efficient data retrieval
- **Async Operations**: Non-blocking I/O

### Performance Targets
- **API Response Time**: <150ms (p95)
- **Database Queries**: <50ms average
- **File Upload**: <5s for 10MB files
- **Concurrent Users**: 1000+ supported

## 🔄 Integration

### External Services
- **Auth Service**: User authentication and permissions
- **Tour Service**: Tour instance data
- **Fleet Service**: Vehicle assignment
- **HR Service**: Employee data sync
- **Notification Service**: Alerts and notifications

### Event Publishing
```python
# Assignment events
driver.assignment.created
driver.assignment.completed
driver.assignment.cancelled

# Compliance events
driver.license.expiring
driver.health_cert.expiring
driver.training.due

# Incident events
driver.incident.reported
driver.incident.resolved
```

## 🚨 Monitoring & Alerts

### Health Checks
- **Database**: Connection and query health
- **Redis**: Cache availability
- **External Services**: Service connectivity
- **File System**: Storage availability

### Compliance Alerts
- **License Expiry**: 30 days before expiration
- **Health Certificate**: 60 days before expiration
- **Training Due**: Automatic renewal reminders
- **Document Status**: Pending approvals

### Performance Monitoring
- **Response Times**: API endpoint performance
- **Error Rates**: 4xx/5xx error tracking
- **Resource Usage**: CPU, memory, disk
- **Business Metrics**: Assignments, incidents, compliance

## 🔧 Configuration

### Environment Variables
```env
# Core Configuration
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port/db

# Services
AUTH_SERVICE_URL=http://auth:8000
NOTIFICATION_SERVICE_URL=http://notification:8007

# Driver Settings
LICENSE_ALERT_DAYS=30
HEALTH_CERT_ALERT_DAYS=60
MAX_DAILY_HOURS=10
REST_PERIOD_HOURS=11

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_DIR=/app/uploads
ALLOWED_FILE_TYPES=["pdf","jpg","jpeg","png"]

# Mobile API
MOBILE_SESSION_TIMEOUT=86400
OFFLINE_SYNC_ENABLED=true
```

## 📱 Mobile API Features

### Offline Support
- **Data Bundle**: 7-day assignment data
- **Sync Mechanism**: Conflict resolution
- **Local Storage**: SQLite cache
- **Background Sync**: Automatic when online

### Real-time Features
- **Push Notifications**: Assignment updates
- **Live Tracking**: GPS integration ready
- **Status Updates**: Real-time assignment status
- **Emergency Contacts**: Always accessible

## 🚀 Deployment

### Docker Production
```bash
# Build image
docker build -t driver-service:latest .

# Run container
docker run -d \
  --name driver-service \
  -p 8010:8010 \
  -e DATABASE_URL=postgresql://... \
  -e REDIS_URL=redis://... \
  driver-service:latest
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: driver-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: driver-service
  template:
    metadata:
      labels:
        app: driver-service
    spec:
      containers:
      - name: driver-service
        image: driver-service:latest
        ports:
        - containerPort: 8010
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

## 🔍 Troubleshooting

### Common Issues

#### Database Connection
```bash
# Check database connectivity
psql $DATABASE_URL -c "SELECT 1"

# Check migrations
alembic current
alembic upgrade head
```

#### Redis Connection
```bash
# Test Redis connection
redis-cli -u $REDIS_URL ping
```

#### File Upload Issues
```bash
# Check upload directory permissions
ls -la uploads/
chmod 755 uploads/

# Check disk space
df -h
```

### Logging
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check logs
docker-compose logs -f app
tail -f logs/driver-service.log
```

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8010/docs
- **ReDoc**: http://localhost:8010/redoc
- **OpenAPI JSON**: http://localhost:8010/openapi.json

### Postman Collection
Import the Postman collection from `docs/postman/driver-service.json`

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes and add tests
4. Run tests: `pytest`
5. Run linting: `flake8 driver_service/`
6. Commit changes: `git commit -m "Add new feature"`
7. Push branch: `git push origin feature/new-feature`
8. Create Pull Request

### Code Standards
- **Python**: PEP 8 compliance
- **Type Hints**: Required for all functions
- **Documentation**: Docstrings for all public methods
- **Testing**: 90%+ coverage required

## 📄 License

This project is proprietary software for Moroccan Tourist Transport ERP System.

## 📞 Support

For technical support or questions:
- **Email**: tech-support@company.com
- **Slack**: #driver-service-support
- **Documentation**: https://docs.company.com/driver-service
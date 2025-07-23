# Authentication & Authorization Microservice

A secure, production-ready FastAPI microservice for authentication and authorization in Moroccan tourist transport ERP systems.

## Features

### 🔐 Authentication
- JWT-based authentication with secure token handling
- Password hashing using bcrypt
- Token blacklisting for logout functionality
- Rate limiting for login attempts

### 📱 OTP Verification
- Time-based OTP generation (6-digit codes)
- Redis-based storage with automatic expiration
- Maximum attempt limits with rate limiting
- Mocked SMS/Email delivery (production-ready for integration)

### 👥 Role-Based Access Control (RBAC)
- Granular permission system with service:action:resource format
- Role-based permission grouping
- Dynamic permission checking
- Support for hierarchical permissions

### 🛡️ Security Features
- Password strength validation
- JWT token expiration and refresh
- Rate limiting on sensitive endpoints
- Audit logging capabilities
- CORS configuration for cross-origin requests

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/auth/logout` - Token revocation
- `GET /api/v1/auth/me` - Current user info
- `GET /api/v1/auth/permissions` - User permissions

### OTP Management
- `POST /api/v1/auth/send-otp` - Send OTP code
- `POST /api/v1/auth/verify-otp` - Verify OTP code

### User Management
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/` - List users
- `GET /api/v1/users/{id}` - Get user details
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Deactivate user

### Role & Permission Management
- `POST /api/v1/roles/` - Create role
- `GET /api/v1/roles/` - List roles
- `GET /api/v1/roles/{id}` - Get role details
- `PUT /api/v1/roles/{id}` - Update role
- `DELETE /api/v1/roles/{id}` - Delete role
- `POST /api/v1/roles/permissions` - Create permission
- `GET /api/v1/roles/permissions` - List permissions
- `DELETE /api/v1/roles/permissions/{id}` - Delete permission

## Quick Start

### Using Docker Compose (Recommended)
```bash
# Clone and setup
git clone <repository>
cd auth-microservice

# Copy environment variables
cp .env.example .env

# Start services
docker-compose up -d

# Check health
curl http://localhost:8000/health
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
python -m app.main
```

## Configuration

Key environment variables in `.env`:

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/auth_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
OTP_EXPIRE_MINUTES=5
```

## Permission System

Permissions follow the format: `service:action:resource`

Examples:
- `vehicles:read:all` - Read all vehicles
- `bookings:create:own` - Create own bookings
- `reports:read:*` - Read any reports

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest app/tests/test_auth.py -v
```

## Production Deployment

1. **Environment Setup**
   - Set strong SECRET_KEY
   - Configure production database
   - Setup Redis cluster for high availability
   - Enable SSL/TLS

2. **Integration Services**
   - SMS Gateway for Morocco (e.g., local providers)
   - Email service (SendGrid, AWS SES)
   - Monitoring and logging

3. **Security Checklist**
   - Regular security audits
   - Monitor failed login attempts
   - Implement IP whitelisting if needed
   - Regular token rotation

## Architecture

```
├── app/
│   ├── models/          # SQLModel database models
│   ├── schemas/         # Pydantic request/response models
│   ├── services/        # Business logic layer
│   ├── routers/         # FastAPI route handlers
│   ├── utils/           # Utilities and dependencies
│   └── tests/           # Comprehensive test suite
```

## Contributing

1. Follow the modular architecture pattern
2. Add tests for new features
3. Update documentation
4. Follow Python code style guidelines

## License

Private - Moroccan Tourist Transport ERP System
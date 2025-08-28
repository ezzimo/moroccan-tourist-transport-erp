# Human Resources Management Microservice

A comprehensive HR management microservice for the Moroccan Tourist Transport ERP system, built with FastAPI, SQLModel, and PostgreSQL.

## Features

### 👥 Employee Management
- **Complete Employee Lifecycle**: From hiring to termination with full profile management
- **Contract Management**: Track contract types, durations, and renewal dates
- **Organizational Structure**: Manager-employee relationships and department hierarchies
- **Compensation Tracking**: Salary management with currency support (MAD)
- **Status Management**: Active, probation, suspended, terminated, resigned, retired
- **Compliance**: Morocco labor law compliance with probation periods and leave entitlements

### 🎯 Recruitment & Applicant Tracking
- **Full ATS Functionality**: Complete applicant tracking from application to hire
- **Multi-stage Pipeline**: Screening, interviews, tests, reference checks, offers
- **Document Management**: Resume and cover letter uploads with secure storage
- **Evaluation System**: Scoring for screening, interviews, and technical assessments
- **Source Tracking**: Track application sources for recruitment ROI analysis
- **Recruiter Assignment**: Assign and track recruiter responsibilities

### 📚 Training & Development
- **Training Program Management**: Create and manage comprehensive training programs
- **Employee Enrollment**: Bulk enrollment with automatic notifications
- **Progress Tracking**: Attendance, scores, and completion status monitoring
- **Certification Management**: Digital certificate generation and expiry tracking
- **Training Analytics**: ROI analysis, completion rates, and effectiveness metrics
- **Mandatory Training**: Compliance training with automatic reminders

### 📄 Document Management
- **Secure File Storage**: Encrypted storage for sensitive HR documents
- **Document Types**: Contracts, IDs, diplomas, certificates, medical records
- **Approval Workflow**: Multi-stage approval process with audit trails
- **Expiry Tracking**: Automatic alerts for document renewals
- **Access Control**: Role-based access with confidentiality levels

### 📊 HR Analytics & Reporting
- **Comprehensive Dashboard**: Real-time HR metrics and KPIs
- **Workforce Analytics**: Headcount, demographics, and distribution analysis
- **Turnover Analysis**: Retention rates, exit patterns, and cost analysis
- **Training ROI**: Training effectiveness and investment analysis
- **Payroll Integration**: Export data for external payroll systems
- **Compliance Reporting**: Labor law compliance and audit reports

## API Endpoints

### Employee Management
- `POST /api/v1/employees/` - Create new employee
- `GET /api/v1/employees/` - List employees with search and filters
- `GET /api/v1/employees/{id}` - Get employee details
- `GET /api/v1/employees/{id}/summary` - Get comprehensive employee summary
- `PUT /api/v1/employees/{id}` - Update employee information
- `POST /api/v1/employees/{id}/terminate` - Terminate employee
- `DELETE /api/v1/employees/{id}` - Deactivate employee
- `GET /api/v1/employees/department/{dept}` - Get employees by department
- `GET /api/v1/employees/contracts/expiring` - Get expiring contracts

### Recruitment Management
- `POST /api/v1/recruitment/applications` - Create job application
- `POST /api/v1/recruitment/applications/upload` - Create application with files
- `GET /api/v1/recruitment/applications` - List applications with filters
- `GET /api/v1/recruitment/applications/{id}` - Get application details
- `PUT /api/v1/recruitment/applications/{id}` - Update application
- `POST /api/v1/recruitment/applications/{id}/stage` - Update application stage
- `POST /api/v1/recruitment/applications/{id}/evaluate` - Evaluate application
- `POST /api/v1/recruitment/applications/{id}/hire` - Hire applicant
- `GET /api/v1/recruitment/stats` - Get recruitment statistics
- `GET /api/v1/recruitment/pipeline` - Get recruitment pipeline

### Training Management
- `POST /api/v1/training/programs` - Create training program
- `GET /api/v1/training/programs` - List training programs
- `GET /api/v1/training/programs/{id}` - Get program details
- `GET /api/v1/training/programs/{id}/summary` - Get program summary
- `PUT /api/v1/training/programs/{id}` - Update program
- `POST /api/v1/training/enrollments` - Enroll employees
- `GET /api/v1/training/enrollments` - List employee trainings
- `PUT /api/v1/training/enrollments/{id}` - Update training record
- `POST /api/v1/training/enrollments/{id}/complete` - Complete training
- `POST /api/v1/training/certificates/generate` - Generate certificate
- `GET /api/v1/training/stats` - Get training statistics

### Document Management
- `POST /api/v1/documents/upload` - Upload employee document
- `GET /api/v1/documents/` - List documents with filters
- `GET /api/v1/documents/expiring` - Get expiring documents
- `GET /api/v1/documents/{id}` - Get document details
- `PUT /api/v1/documents/{id}` - Update document
- `POST /api/v1/documents/{id}/approve` - Approve/reject document
- `DELETE /api/v1/documents/{id}` - Delete document
- `GET /api/v1/documents/employee/{id}` - Get employee documents

### Analytics & Reporting
- `GET /api/v1/analytics/dashboard` - HR dashboard overview
- `GET /api/v1/analytics/workforce` - Workforce analytics
- `GET /api/v1/analytics/turnover` - Turnover analytics
- `GET /api/v1/analytics/recruitment` - Recruitment analytics
- `GET /api/v1/analytics/training` - Training analytics
- `GET /api/v1/analytics/compensation` - Compensation analytics
- `GET /api/v1/analytics/demographics` - Demographics analytics
- `GET /api/v1/analytics/payroll-export` - Export payroll data
- `GET /api/v1/analytics/reports/headcount` - Headcount report
- `GET /api/v1/analytics/reports/absence` - Absence report

## Quick Start

### Using Docker Compose (Recommended)
```bash
# Clone and setup
cd hr_service

# Copy environment variables
cp .env.example .env

# Start services
docker-compose up -d

# Check health
curl http://localhost:8005/health
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
python -m hr_service.main
```

## Configuration

Key environment variables in `.env`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5437/hr_db
REDIS_URL=redis://localhost:6384/5
AUTH_SERVICE_URL=http://auth_service:8000
SECRET_KEY=your-super-secret-key
PROBATION_PERIOD_MONTHS=6
ANNUAL_LEAVE_DAYS=22
SICK_LEAVE_DAYS=90
```

## Data Models

### Employee
- **Personal Info**: full_name, national_id, gender, birth_date, contact details
- **Employment**: department, position, employment_type, contract_type, dates
- **Compensation**: base_salary, benefits, tax information
- **Status**: status, manager relationships, probation tracking
- **Compliance**: social security, tax ID, bank details

### JobApplication
- **Applicant Info**: personal details, experience, education, skills
- **Application**: position, department, source, stage, priority
- **Evaluation**: screening, interview, technical scores, overall rating
- **Process**: recruiter assignment, interview scheduling, notes
- **Documents**: resume and cover letter file management

### TrainingProgram
- **Program Info**: title, description, category, trainer details
- **Schedule**: dates, duration, location, delivery method
- **Targeting**: departments, positions, prerequisites
- **Evaluation**: pass scores, certification requirements
- **Budget**: costs, participant limits, resource allocation

### EmployeeTraining
- **Enrollment**: employee assignment, enrollment tracking
- **Attendance**: status, percentage, participation tracking
- **Assessment**: pre/post scores, practical evaluation, final scores
- **Completion**: status, dates, certification issuance
- **Feedback**: trainer and employee feedback, ratings

### EmployeeDocument
- **Document Info**: type, title, description, metadata
- **File Management**: secure storage, size limits, type validation
- **Lifecycle**: upload, review, approval workflow
- **Compliance**: expiry tracking, renewal alerts
- **Security**: confidentiality levels, access control

## Security & Integration

- **JWT Authentication**: Integration with auth microservice
- **Role-Based Access Control**: Granular permissions per endpoint
- **Document Security**: Encrypted file storage with access logging
- **Data Privacy**: GDPR-compliant data handling and retention
- **Audit Logging**: Complete audit trail for all HR operations

## Morocco Labor Law Compliance

- **Probation Periods**: 6-month probation for new employees
- **Leave Entitlements**: 22 days annual leave, 90 days sick leave
- **Contract Types**: Permanent, fixed-term, seasonal, probation
- **Minimum Wage**: Validation against Morocco minimum wage requirements
- **Social Security**: Integration with CNSS requirements
- **Document Requirements**: ID copies, medical certificates, diplomas

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=hr_service

# Run specific test file
pytest hr_service/tests/test_employees.py -v
```

## Integration with ERP Ecosystem

The HR microservice integrates seamlessly with other ERP components:

- **Authentication Service**: User authentication and authorization
- **CRM Service**: Customer service staff management
- **Fleet Service**: Driver and maintenance staff management
- **Tour Operations**: Guide and coordinator management
- **Business Intelligence**: HR analytics and reporting
- **Payroll Systems**: External payroll system integration

## Performance & Scalability

- **Database Optimization**: Indexed queries and efficient pagination
- **Redis Caching**: Fast session management and notifications
- **Async Operations**: Non-blocking I/O for better performance
- **File Management**: Efficient document storage and retrieval
- **Horizontal Scaling**: Stateless design for easy scaling

## Moroccan Market Considerations

- **Multi-language Support**: Arabic, French, English HR operations
- **Local Compliance**: Morocco-specific labor laws and regulations
- **Currency Support**: Moroccan Dirham (MAD) as default currency
- **Cultural Sensitivity**: Respect for local business practices
- **Integration Ready**: Support for local payroll and benefits providers

## Contributing

1. Follow the modular architecture pattern
2. Add comprehensive tests for new features
3. Update documentation and API schemas
4. Follow Python code style guidelines
5. Ensure proper error handling and validation

## License

Private - Moroccan Tourist Transport ERP System

# ##################################################################################################################
# ##################################################################################################################
#                                           New README
# ##################################################################################################################
# Human Resources Management Microservice

A comprehensive HR management system for Moroccan Tourist Transport ERP using FastAPI + SQLModel + PostgreSQL.

## Features

### 👥 Employee Management
- Complete employee lifecycle management
- Contract and document management
- Department and role assignment
- Salary and benefits tracking
- Morocco labor law compliance

### 🎯 Recruitment & Hiring
- Applicant Tracking System (ATS)
- Multi-stage hiring funnel
- Resume and document management
- Interview scheduling and tracking
- Automated hiring workflows

### 📚 Training Management
- Training program creation and management
- Employee training assignments
- Attendance and evaluation tracking
- Certificate management
- Training effectiveness analytics

### 📄 Document Management
- Secure document upload and storage
- Document approval workflows
- Expiry tracking and alerts
- Compliance monitoring

### 📊 HR Analytics & Reporting
- Employee demographics and statistics
- Turnover and retention analysis
- Recruitment funnel analytics
- Training ROI and effectiveness
- Compliance reporting
- **Status Management**: Active, probation, suspended, terminated, resigned, retired
- **Compliance**: Morocco labor law compliance with probation periods and leave entitlements

### 🎯 Recruitment & Applicant Tracking
- **Full ATS Functionality**: Complete applicant tracking from application to hire
- **Multi-stage Pipeline**: Screening, interviews, tests, reference checks, offers
- **Document Management**: Resume and cover letter uploads with secure storage
- **Evaluation System**: Scoring for screening, interviews, and technical assessments
- **Source Tracking**: Track application sources for recruitment ROI analysis
- **Recruiter Assignment**: Assign and track recruiter responsibilities

### 📚 Training & Development
- **Training Program Management**: Create and manage comprehensive training programs
- **Employee Enrollment**: Bulk enrollment with automatic notifications
- **Progress Tracking**: Attendance, scores, and completion status monitoring
- **Certification Management**: Digital certificate generation and expiry tracking
- **Training Analytics**: ROI analysis, completion rates, and effectiveness metrics
- **Mandatory Training**: Compliance training with automatic reminders

### 📄 Document Management
- **Secure File Storage**: Encrypted storage for sensitive HR documents
- **Document Types**: Contracts, IDs, diplomas, certificates, medical records
- **Approval Workflow**: Multi-stage approval process with audit trails
- **Expiry Tracking**: Automatic alerts for document renewals
- **Access Control**: Role-based access with confidentiality levels

### 📊 HR Analytics & Reporting
- **Comprehensive Dashboard**: Real-time HR metrics and KPIs
- **Workforce Analytics**: Headcount, demographics, and distribution analysis
- **Turnover Analysis**: Retention rates, exit patterns, and cost analysis
- **Training ROI**: Training effectiveness and investment analysis
- **Payroll Integration**: Export data for external payroll systems
- **Compliance Reporting**: Labor law compliance and audit reports

## API Endpoints

### Employee Management
- `POST /api/v1/employees/` - Create new employee
- `GET /api/v1/employees/` - List employees with search and filters
- `GET /api/v1/employees/{id}` - Get employee details
- `GET /api/v1/employees/{id}/summary` - Get comprehensive employee summary
- `PUT /api/v1/employees/{id}` - Update employee information
- `POST /api/v1/employees/{id}/terminate` - Terminate employee
- `DELETE /api/v1/employees/{id}` - Deactivate employee
- `GET /api/v1/employees/department/{dept}` - Get employees by department
- `GET /api/v1/employees/contracts/expiring` - Get expiring contracts

### Recruitment Management
- `POST /api/v1/recruitment/applications` - Create job application
- `POST /api/v1/recruitment/applications/upload` - Create application with files
- `GET /api/v1/recruitment/applications` - List applications with filters
- `GET /api/v1/recruitment/applications/{id}` - Get application details
- `PUT /api/v1/recruitment/applications/{id}` - Update application
- `POST /api/v1/recruitment/applications/{id}/stage` - Update application stage
- `POST /api/v1/recruitment/applications/{id}/evaluate` - Evaluate application
- `POST /api/v1/recruitment/applications/{id}/hire` - Hire applicant
- `GET /api/v1/recruitment/stats` - Get recruitment statistics
- `GET /api/v1/recruitment/pipeline` - Get recruitment pipeline

### Training Management
- `POST /api/v1/training/programs` - Create training program
- `GET /api/v1/training/programs` - List training programs
- `GET /api/v1/training/programs/{id}` - Get program details
- `GET /api/v1/training/programs/{id}/summary` - Get program summary
- `PUT /api/v1/training/programs/{id}` - Update program
- `POST /api/v1/training/enrollments` - Enroll employees
- `GET /api/v1/training/enrollments` - List employee trainings
- `PUT /api/v1/training/enrollments/{id}` - Update training record
- `POST /api/v1/training/enrollments/{id}/complete` - Complete training
- `POST /api/v1/training/certificates/generate` - Generate certificate
- `GET /api/v1/training/stats` - Get training statistics

### Document Management
- `POST /api/v1/documents/upload` - Upload employee document
- `GET /api/v1/documents/` - List documents with filters
- `GET /api/v1/documents/expiring` - Get expiring documents
## Architecture

```
hr_service/
├── models/                 # SQLModel database models
│   ├── employee.py        # Employee core model
│   ├── job_application.py # Recruitment models
│   ├── training_program.py# Training models
│   ├── employee_training.py
│   └── employee_document.py
├── schemas/               # Pydantic request/response models
├── services/              # Business logic layer
│   ├── employee_service.py
│   ├── recruitment_service.py
│   ├── training_service.py
│   ├── document_service.py
│   └── analytics_service.py
├── routers/               # FastAPI route handlers
├── utils/                 # Utilities and helpers
│   ├── auth.py           # Authentication utilities
│   ├── upload.py         # File upload handling
│   ├── validation.py     # Data validation
│   └── notifications.py  # Notification integration
└── tests/                # Comprehensive test suite
```
- `GET /api/v1/analytics/training` - Training analytics
## Entities

### Employee
- Personal information and contact details
- Employment contract and terms
- Department, role, and reporting structure
- Salary, benefits, and compensation
- Status tracking and lifecycle management

### Job Application
- Applicant information and resume
- Position applied and source tracking
- Multi-stage hiring funnel
- Interview notes and evaluations
- Hiring decision workflow

### Training Program
- Training content and curriculum
- Scheduling and resource allocation
- Trainer and location management
- Cost tracking and budgeting

### Employee Training
- Training assignments and enrollment
- Attendance and participation tracking
- Evaluation scores and feedback
- Certificate issuance and management

### Employee Document
- Document type classification
- Upload and storage management
- Approval workflow and status
- Expiry tracking and alerts

## API Endpoints

### Employee Management (`/api/v1/employees`)
- `POST /` - Create employee
- `GET /` - List employees with filtering
- `GET /{id}` - Get employee details
- `PUT /{id}` - Update employee
- `DELETE /{id}` - Deactivate employee
- `GET /{id}/documents` - Get employee documents
- `POST /{id}/documents` - Upload employee document

### Recruitment (`/api/v1/recruitment`)
- `POST /applications` - Submit job application
- `GET /applications` - List applications with filtering
- `GET /applications/{id}` - Get application details
- `PUT /applications/{id}/stage` - Advance application stage
- `POST /applications/{id}/hire` - Hire applicant
- `PUT /applications/{id}/reject` - Reject application

### Training (`/api/v1/training`)
- `POST /programs` - Create training program
- `GET /programs` - List training programs
- `POST /assignments` - Assign employee to training
- `GET /assignments` - List training assignments
- `PUT /assignments/{id}/complete` - Complete training
- `POST /assignments/{id}/certificate` - Upload certificate

### Analytics (`/api/v1/analytics`)
- `GET /dashboard` - HR dashboard metrics
- `GET /employees` - Employee analytics
- `GET /recruitment` - Recruitment funnel analysis
- `GET /training` - Training effectiveness metrics
- `GET /turnover` - Turnover and retention analysis
- `GET /compliance` - Compliance reporting

## Quick Start

### Using Docker Compose (Recommended)
```bash
# Clone and setup
cd hr_service

# Copy environment variables
cp .env.example .env

# Start services
docker-compose up -d

# Check health
curl http://localhost:8005/health
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
python -m hr_service.main
```

## Configuration

Key environment variables in `.env`:

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/hr_db
REDIS_URL=redis://localhost:6379/5
SECRET_KEY=your-super-secret-key
AUTH_SERVICE_URL=http://auth_service:8000
NOTIFICATION_SERVICE_URL=http://notification_app:8007

# Morocco-specific settings
MIN_SALARY_MAD=2000
MAX_WEEKLY_HOURS=44
MIN_ANNUAL_LEAVE_DAYS=18
```

## Morocco Labor Law Compliance

The system enforces Morocco-specific labor regulations:

- **Working Hours**: Maximum 44 hours per week
- **Annual Leave**: Minimum 18 days per year
- **Minimum Wage**: MAD 2000+ validation
- **CNSS Integration**: Social security number validation
- **Contract Types**: Permanent, fixed-term, seasonal

## Business Features

### Recruitment Pipeline
1. **Application Submission** - Online application with resume upload
2. **Screening** - Initial review and qualification
3. **Interview** - Structured interview process
4. **Offer** - Job offer and negotiation
5. **Hiring** - Onboarding and employee creation

### Training Lifecycle
1. **Program Creation** - Define training curriculum
2. **Employee Assignment** - Assign relevant staff
3. **Attendance Tracking** - Monitor participation
4. **Evaluation** - Score and assess performance
5. **Certification** - Issue completion certificates

### Document Workflow
1. **Upload** - Secure document submission
2. **Review** - HR review and validation
3. **Approval/Rejection** - Decision workflow
4. **Storage** - Secure long-term storage
5. **Expiry Monitoring** - Automated renewal alerts

## Integration Points

### Internal Services
- **Auth Service**: JWT authentication and RBAC
- **Driver Service**: Driver-specific HR data
- **Notification Service**: Alerts and communications
- **Financial Service**: Payroll integration

### External Systems
- **Payroll Systems**: Employee data export
- **CNSS**: Social security integration
- **Email/SMS**: Notification delivery
- **Document Storage**: S3-compatible storage

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=hr_service --cov-report=html

# Run specific test categories
pytest -m "recruitment"  # Recruitment tests
pytest -m "training"     # Training tests
pytest -m "analytics"    # Analytics tests
```

## Performance & Scalability

- **Database Optimization**: Proper indexing and query optimization
- **Caching**: Redis for frequently accessed data
- **File Storage**: S3-compatible for document storage
- **Async Operations**: Non-blocking I/O for external calls
- **Pagination**: Efficient data retrieval

## Security Features

- **File Upload Security**: MIME type validation, size limits
- **Data Encryption**: Sensitive data encryption at rest
- **Access Control**: Role-based permissions
- **Audit Logging**: Complete audit trail
- **Input Validation**: Comprehensive data validation

## Monitoring & Alerts

- **Health Checks**: Service and database connectivity
- **Performance Metrics**: Response times and throughput
- **Business Alerts**: Document expiry, compliance issues
- **Error Tracking**: Comprehensive error logging

## Future Enhancements

- **AI-Powered Recruitment**: Candidate scoring and matching
- **Advanced Analytics**: Predictive turnover modeling
- **Mobile App**: Employee self-service portal
- **E-Signature**: Digital contract signing
- **Biometric Integration**: Attendance tracking
SICK_LEAVE_DAYS=90
```

## Data Models

### Employee
- **Personal Info**: full_name, national_id, gender, birth_date, contact details
- **Employment**: department, position, employment_type, contract_type, dates
- **Compensation**: base_salary, benefits, tax information
- **Status**: status, manager relationships, probation tracking
- **Compliance**: social security, tax ID, bank details

### JobApplication
- **Applicant Info**: personal details, experience, education, skills
- **Application**: position, department, source, stage, priority
- **Evaluation**: screening, interview, technical scores, overall rating
- **Process**: recruiter assignment, interview scheduling, notes
- **Documents**: resume and cover letter file management

### TrainingProgram
- **Program Info**: title, description, category, trainer details
- **Schedule**: dates, duration, location, delivery method
- **Targeting**: departments, positions, prerequisites
- **Evaluation**: pass scores, certification requirements
- **Budget**: costs, participant limits, resource allocation

### EmployeeTraining
- **Enrollment**: employee assignment, enrollment tracking
- **Attendance**: status, percentage, participation tracking
- **Assessment**: pre/post scores, practical evaluation, final scores
- **Completion**: status, dates, certification issuance
- **Feedback**: trainer and employee feedback, ratings

### EmployeeDocument
- **Document Info**: type, title, description, metadata
- **File Management**: secure storage, size limits, type validation
- **Lifecycle**: upload, review, approval workflow
- **Compliance**: expiry tracking, renewal alerts
- **Security**: confidentiality levels, access control

## Security & Integration

- **JWT Authentication**: Integration with auth microservice
- **Role-Based Access Control**: Granular permissions per endpoint
- **Document Security**: Encrypted file storage with access logging
- **Data Privacy**: GDPR-compliant data handling and retention
- **Audit Logging**: Complete audit trail for all HR operations

## Morocco Labor Law Compliance

- **Probation Periods**: 6-month probation for new employees
- **Leave Entitlements**: 22 days annual leave, 90 days sick leave
- **Contract Types**: Permanent, fixed-term, seasonal, probation
- **Minimum Wage**: Validation against Morocco minimum wage requirements
- **Social Security**: Integration with CNSS requirements
- **Document Requirements**: ID copies, medical certificates, diplomas

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=hr_service

# Run specific test file
pytest hr_service/tests/test_employees.py -v
```

## Integration with ERP Ecosystem

The HR microservice integrates seamlessly with other ERP components:

- **Authentication Service**: User authentication and authorization
- **CRM Service**: Customer service staff management
- **Fleet Service**: Driver and maintenance staff management
- **Tour Operations**: Guide and coordinator management
- **Business Intelligence**: HR analytics and reporting
- **Payroll Systems**: External payroll system integration

## Performance & Scalability

- **Database Optimization**: Indexed queries and efficient pagination
- **Redis Caching**: Fast session management and notifications
- **Async Operations**: Non-blocking I/O for better performance
- **File Management**: Efficient document storage and retrieval
- **Horizontal Scaling**: Stateless design for easy scaling

## Moroccan Market Considerations

- **Multi-language Support**: Arabic, French, English HR operations
- **Local Compliance**: Morocco-specific labor laws and regulations
- **Currency Support**: Moroccan Dirham (MAD) as default currency
- **Cultural Sensitivity**: Respect for local business practices
- **Integration Ready**: Support for local payroll and benefits providers

## Contributing

1. Follow the modular architecture pattern
2. Add comprehensive tests for new features
3. Update documentation and API schemas
4. Follow Python code style guidelines
5. Ensure proper error handling and validation

## License

Private - Moroccan Tourist Transport ERP System
# Quality Assurance & Compliance Microservice

A comprehensive Quality Assurance & Compliance microservice for the Moroccan Tourist Transport ERP system, built with FastAPI, SQLModel, and PostgreSQL.

## Features

### 🔍 **Quality Audit Management**
- **Comprehensive Audit System**: Schedule and conduct quality audits across all business areas
- **Multi-Entity Support**: Audit tours, fleet operations, bookings, offices, drivers, and guides
- **Dynamic Checklists**: Configurable audit checklists with weighted scoring
- **Audit Types**: Internal, external, customer feedback, regulatory, and follow-up audits
- **Automated Scoring**: Calculate audit scores with pass/fail determination
- **Follow-up Tracking**: Automatic follow-up scheduling for failed audits

### 📋 **Non-Conformity Management**
- **Issue Tracking**: Comprehensive tracking of quality issues and defects
- **Severity Classification**: Minor, Major, and Critical severity levels
- **Root Cause Analysis**: Detailed root cause and contributing factor analysis
- **Corrective Actions**: Track corrective and preventive actions with due dates
- **Resolution Workflow**: Complete resolution and verification process
- **Recurring Issue Detection**: Identify and track recurring problems

### 📊 **Compliance Management**
- **Regulatory Tracking**: Monitor compliance with Morocco tourism and transport regulations
- **Multi-Domain Support**: Safety, Labor, Tax, Tourism, Transport, Environmental compliance
- **Requirement Registry**: Comprehensive database of regulatory requirements
- **Expiry Monitoring**: Track compliance expiry dates with automated alerts
- **Risk Assessment**: Risk-based compliance prioritization
- **Evidence Management**: Track compliance evidence and documentation

### 🏆 **Certification Management**
- **Certificate Tracking**: Manage ISO, tourism quality, and safety certifications
- **Multi-Scope Support**: Company-wide, department, individual, vehicle, and location certificates
- **Renewal Management**: Track renewal requirements and lead times
- **Document Storage**: Secure storage of certification documents
- **Validity Monitoring**: Real-time validity status and expiry alerts
- **Audit Integration**: Link certifications to audit requirements

### 📈 **Analytics & Reporting**
- **Real-time Dashboard**: Live QA and compliance metrics
- **Audit Performance**: Success rates, scores, and trend analysis
- **Compliance Status**: Current compliance status across all domains
- **Non-Conformity Trends**: Issue patterns and resolution effectiveness
- **Risk Assessment**: Risk-based prioritization and heat maps
- **Export Capabilities**: PDF and Excel reports for stakeholders

## API Endpoints

### Quality Audit Management
- `POST /api/v1/audits/` - Create new audit
- `GET /api/v1/audits/` - List audits with search and filters
- `GET /api/v1/audits/summary` - Get audit summary statistics
- `GET /api/v1/audits/overdue` - Get overdue audits
- `GET /api/v1/audits/{id}` - Get audit details
- `PUT /api/v1/audits/{id}` - Update audit information
- `POST /api/v1/audits/{id}/start` - Start audit
- `POST /api/v1/audits/{id}/complete` - Complete audit with responses
- `DELETE /api/v1/audits/{id}` - Delete audit

### Non-Conformity Management
- `POST /api/v1/nonconformities/` - Create non-conformity
- `GET /api/v1/nonconformities/` - List non-conformities with filters
- `GET /api/v1/nonconformities/summary` - Get NC summary statistics
- `GET /api/v1/nonconformities/overdue` - Get overdue NCs
- `GET /api/v1/nonconformities/{id}` - Get NC details
- `PUT /api/v1/nonconformities/{id}` - Update NC information
- `POST /api/v1/nonconformities/{id}/resolve` - Resolve NC
- `POST /api/v1/nonconformities/{id}/verify` - Verify NC resolution
- `DELETE /api/v1/nonconformities/{id}` - Delete NC
- `GET /api/v1/nonconformities/audit/{id}` - Get audit NCs

### Compliance Management
- `POST /api/v1/compliance/` - Create compliance requirement
- `GET /api/v1/compliance/` - List requirements with filters
- `GET /api/v1/compliance/summary` - Get compliance summary
- `GET /api/v1/compliance/expiring` - Get expiring requirements
- `GET /api/v1/compliance/{id}` - Get requirement details
- `PUT /api/v1/compliance/{id}` - Update requirement
- `POST /api/v1/compliance/{id}/assess` - Assess compliance
- `DELETE /api/v1/compliance/{id}` - Delete requirement
- `GET /api/v1/compliance/domain/{domain}` - Get domain requirements

### Certification Management
- `POST /api/v1/certifications/` - Create certification
- `POST /api/v1/certifications/upload` - Create with file upload
- `GET /api/v1/certifications/` - List certifications with filters
- `GET /api/v1/certifications/summary` - Get certification summary
- `GET /api/v1/certifications/expiring` - Get expiring certifications
- `GET /api/v1/certifications/{id}` - Get certification details
- `PUT /api/v1/certifications/{id}` - Update certification
- `POST /api/v1/certifications/{id}/renew` - Renew certification
- `DELETE /api/v1/certifications/{id}` - Delete certification
- `GET /api/v1/certifications/entity/{type}/{id}` - Get entity certifications

### Reports & Analytics
- `GET /api/v1/reports/dashboard` - QA & Compliance dashboard
- `GET /api/v1/reports/audit-performance` - Audit performance analytics
- `GET /api/v1/reports/compliance-status` - Compliance status report
- `GET /api/v1/reports/nonconformity-trends` - NC trend analysis
- `GET /api/v1/reports/certification-status` - Certification status
- `GET /api/v1/reports/corrective-actions` - Corrective action effectiveness
- `GET /api/v1/reports/risk-assessment` - Risk assessment report
- `GET /api/v1/reports/export/audit-report` - Export audit report
- `GET /api/v1/reports/export/compliance-report` - Export compliance report
- `GET /api/v1/reports/export/nonconformity-report` - Export NC report

## Quick Start

### Using Docker Compose (Recommended)
```bash
# Clone and setup
cd qa_service

# Copy environment variables
cp .env.example .env

# Start services
docker-compose up -d

# Check health
curl http://localhost:8009/health
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
python -m qa_service.main
```

## Configuration

Key environment variables in `.env`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5441/qa_db
REDIS_URL=redis://localhost:6388/9
AUTH_SERVICE_URL=http://localhost:8000
AUDIT_FREQUENCY_DAYS=90
CORRECTIVE_ACTION_DEFAULT_DAYS=30
CERTIFICATION_ALERT_DAYS=60
AUDIT_PASS_SCORE=80.0
```

## Data Models

### QualityAudit
- **Identification**: audit_number, title, entity information
- **Checklist**: JSON-based configurable checklists with scoring
- **Execution**: auditor assignment, scheduling, and completion tracking
- **Outcomes**: scoring, pass/fail determination, recommendations
- **Follow-up**: automatic follow-up scheduling for failed audits

### NonConformity
- **Issue Details**: title, description, severity classification
- **Analysis**: root cause analysis and contributing factors
- **Actions**: corrective and preventive action tracking
- **Resolution**: completion tracking and verification
- **Cost Impact**: estimated and actual cost tracking

### ComplianceRequirement
- **Regulatory Info**: domain, type, regulatory body, legal basis
- **Tracking**: status, compliance dates, expiry monitoring
- **Responsibility**: assigned personnel and departments
- **Risk**: risk level and non-compliance impact assessment
- **Documentation**: evidence requirements and document links

### Certification
- **Certificate Info**: number, type, issuing body, scope
- **Validity**: issue/expiry dates, status tracking
- **Renewal**: renewal process and lead time management
- **Documentation**: secure document storage and verification
- **Compliance**: audit dates and compliance verification

## Security & Integration

- **JWT Authentication**: Integration with auth microservice
- **Role-Based Access Control**: Granular permissions per endpoint
- **Audit Logging**: Complete audit trail for all operations
- **Document Security**: Secure file storage with access control
- **Service Integration**: All ERP microservices for comprehensive QA

## Morocco Compliance Features

- **Tourism Authority**: Ministry of Tourism compliance tracking
- **Transport Authority**: Ministry of Transport regulations
- **Labor Law**: Morocco labor law compliance monitoring
- **Safety Standards**: Morocco safety and health regulations
- **Tax Compliance**: Integration with tax and financial requirements

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=qa_service

# Run specific test file
pytest qa_service/tests/test_audits.py -v
```

## Integration with ERP Ecosystem

The QA & Compliance microservice integrates with all ERP components:

- **Tour Operations**: Tour quality audits and incident tracking
- **Fleet Management**: Vehicle compliance and safety audits
- **HR Service**: Employee certification and training compliance
- **Booking Service**: Customer satisfaction and service quality
- **Financial Service**: Compliance cost tracking and budgeting
- **CRM Service**: Customer feedback integration

## Performance & Scalability

- **Database Optimization**: Indexed queries and efficient pagination
- **Redis Caching**: Fast alert delivery and session management
- **Async Operations**: Non-blocking I/O for better performance
- **Horizontal Scaling**: Stateless design for easy scaling
- **Real-time Alerts**: Automated compliance and expiry notifications

## Moroccan Market Considerations

- **Multi-language Support**: Arabic, French, English QA documentation
- **Local Regulations**: Morocco-specific compliance requirements
- **Cultural Sensitivity**: Respect for local business practices
- **Government Integration**: Ready for regulatory reporting
- **Tourism Standards**: Morocco tourism quality standards

## Contributing

1. Follow the modular architecture pattern
2. Add comprehensive tests for new features
3. Update documentation and API schemas
4. Follow Python code style guidelines
5. Ensure proper error handling and validation

## License

Private - Moroccan Tourist Transport ERP System
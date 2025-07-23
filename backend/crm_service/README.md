# Customer Relationship Management (CRM) Microservice

A comprehensive CRM microservice for the Moroccan Tourist Transport ERP system, built with FastAPI, SQLModel, and PostgreSQL.

## Features

### 🏢 Customer Management
- **Individual & Corporate Customers**: Support for both individual travelers and corporate clients
- **360° Customer View**: Comprehensive customer profiles with contact information, preferences, and history
- **Customer Segmentation**: Dynamic segmentation based on behavior, location, loyalty status, and custom criteria
- **Tagging System**: Flexible tagging for customer categorization (VIP, Repeat Customer, etc.)
- **Loyalty Tracking**: Multi-tier loyalty system (New, Bronze, Silver, Gold, Platinum, VIP)

### 💬 Interaction Management
- **Multi-Channel Tracking**: Email, phone, chat, in-person, WhatsApp, SMS communications
- **Interaction History**: Complete timeline of customer communications
- **Follow-up Management**: Track and schedule follow-up actions
- **Staff Attribution**: Link interactions to specific staff members
- **Duration Tracking**: Monitor interaction duration for performance analysis

### 📝 Feedback System
- **Service-Specific Feedback**: Separate feedback for Tours, Bookings, Support, Transport, etc.
- **Rating System**: 1-5 star rating with automatic sentiment analysis
- **Resolution Tracking**: Track feedback resolution status and assign resolution owners
- **Anonymous Feedback**: Support for anonymous customer feedback
- **Multi-Source Collection**: Web, mobile, email, and other feedback sources

### 🎯 Customer Segmentation
- **Dynamic Segments**: Create segments based on multiple criteria
- **Real-time Matching**: Automatic customer assignment to matching segments
- **Flexible Criteria**: Support for loyalty status, region, tags, contact type, and custom rules
- **Segment Analytics**: Track segment size and performance over time

## API Endpoints

### Customer Management
- `POST /api/v1/customers/` - Create new customer
- `GET /api/v1/customers/` - List customers with search and filters
- `GET /api/v1/customers/{id}` - Get customer details
- `GET /api/v1/customers/{id}/summary` - Get comprehensive customer summary
- `PUT /api/v1/customers/{id}` - Update customer information
- `DELETE /api/v1/customers/{id}` - Deactivate customer

### Interaction Management
- `POST /api/v1/interactions/` - Create new interaction
- `GET /api/v1/interactions/` - List interactions with filters
- `GET /api/v1/interactions/stats` - Get interaction statistics
- `GET /api/v1/interactions/{id}` - Get interaction details
- `PUT /api/v1/interactions/{id}` - Update interaction
- `DELETE /api/v1/interactions/{id}` - Delete interaction
- `GET /api/v1/interactions/customer/{id}` - Get customer interactions

### Feedback Management
- `POST /api/v1/feedback/` - Submit new feedback
- `GET /api/v1/feedback/` - List feedback with filters
- `GET /api/v1/feedback/stats` - Get feedback statistics
- `GET /api/v1/feedback/{id}` - Get feedback details
- `PUT /api/v1/feedback/{id}` - Update feedback (resolution)
- `DELETE /api/v1/feedback/{id}` - Delete feedback
- `GET /api/v1/feedback/customer/{id}` - Get customer feedback

### Segment Management
- `POST /api/v1/segments/` - Create new segment
- `GET /api/v1/segments/` - List segments
- `GET /api/v1/segments/{id}` - Get segment details
- `GET /api/v1/segments/{id}/customers` - Get segment customers
- `PUT /api/v1/segments/{id}` - Update segment
- `DELETE /api/v1/segments/{id}` - Delete segment
- `POST /api/v1/segments/customer/{id}/assign` - Assign customer to segments
- `POST /api/v1/segments/recalculate` - Recalculate all segments

## Quick Start

### Using Docker Compose (Recommended)
```bash
# Clone and setup
cd crm_service

# Copy environment variables
cp .env.example .env

# Start services
docker-compose up -d

# Check health
curl http://localhost:8001/health
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
python -m crm_service.main
```

## Configuration

Key environment variables in `.env`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5433/crm_db
REDIS_URL=redis://localhost:6380/1
AUTH_SERVICE_URL=http://localhost:8000
SECRET_KEY=your-super-secret-key
```

## Data Models

### Customer
- **Individual**: full_name, email, phone, nationality, region, preferences
- **Corporate**: company_name, email, phone, region, contact preferences
- **Attributes**: loyalty_status, tags, notes, activity status
- **Timestamps**: created_at, updated_at, last_interaction

### Interaction
- **Communication**: channel (email/phone/chat/etc.), subject, summary
- **Metadata**: duration, staff_member_id, follow_up requirements
- **Tracking**: timestamp, creation date

### Feedback
- **Content**: service_type, rating (1-5), comments, sentiment
- **Resolution**: resolved status, resolution_notes, resolved_by
- **Metadata**: source, anonymous flag, booking reference

### Segment
- **Definition**: name, description, criteria (JSON)
- **Analytics**: customer_count, last_calculated
- **Status**: is_active, creation/update timestamps

## Segmentation Examples

```json
{
  "name": "VIP Moroccan Customers",
  "criteria": {
    "loyalty_status": ["Gold", "Platinum", "VIP"],
    "nationality": ["Moroccan"],
    "tags": ["VIP"]
  }
}
```

```json
{
  "name": "Casablanca Corporate Clients",
  "criteria": {
    "contact_type": ["Corporate"],
    "region": ["Casablanca"],
    "tags": ["High Volume"]
  }
}
```

## Security & Compliance

- **JWT Authentication**: Integration with auth microservice
- **Role-Based Access Control**: Granular permissions per endpoint
- **GDPR Compliance**: Data retention policies and anonymization support
- **Audit Logging**: Track all customer data modifications
- **Data Privacy**: Secure handling of personal information

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=crm_service

# Run specific test file
pytest crm_service/tests/test_customers.py -v
```

## Integration with ERP Ecosystem

The CRM microservice integrates seamlessly with other ERP components:

- **Authentication Service**: User authentication and authorization
- **Booking Service**: Customer booking history and preferences
- **Tour Operations**: Customer tour feedback and preferences
- **Business Intelligence**: Customer analytics and reporting
- **Notification Service**: Customer communication and alerts

## Performance & Scalability

- **Database Optimization**: Indexed queries and efficient pagination
- **Caching**: Redis caching for frequently accessed data
- **Async Operations**: Non-blocking I/O for better performance
- **Horizontal Scaling**: Stateless design for easy scaling

## Moroccan Market Considerations

- **Multi-language Support**: Arabic, French, English customer preferences
- **Regional Segmentation**: Morocco-specific regions and cities
- **Cultural Preferences**: Respect for local business practices
- **Compliance**: Moroccan data protection and business regulations

## Contributing

1. Follow the modular architecture pattern
2. Add comprehensive tests for new features
3. Update documentation and API schemas
4. Follow Python code style guidelines
5. Ensure GDPR compliance for customer data

## License

Private - Moroccan Tourist Transport ERP System
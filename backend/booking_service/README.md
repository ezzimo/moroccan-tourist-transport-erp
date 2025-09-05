# Booking & Reservation Microservice

A comprehensive booking and reservation microservice for the Moroccan Tourist Transport ERP system, built with FastAPI, SQLModel, and PostgreSQL.

## Features

### 🎫 Booking Management
- **Real-time Booking Creation**: Secure booking creation with distributed locking
- **Booking Lifecycle**: Complete workflow from pending to confirmed/cancelled/refunded
- **Multi-service Reservations**: Support for tours, transfers, accommodations, activities
- **Automatic Expiry**: Unconfirmed bookings expire after 30 minutes
- **PDF Voucher Generation**: Professional booking vouchers with QR codes

### 💰 Dynamic Pricing Engine
- **Flexible Pricing Rules**: Percentage, fixed amount, group, and early bird discounts
- **Promo Code Support**: Promotional codes with usage limits and validation
- **Rule Prioritization**: Priority-based rule application with combinable options
- **Real-time Calculation**: Sub-300ms pricing response times
- **Usage Tracking**: Automatic tracking of rule usage and limits

### 📅 Availability Management
- **Resource Scheduling**: Vehicle, guide, accommodation, and activity availability
- **Capacity Management**: Total, available, and reserved capacity tracking
- **Resource Blocking**: Manual blocking for maintenance or other reasons
- **Real-time Checks**: Instant availability verification
- **Conflict Prevention**: Distributed locking prevents double-booking

### 🛍️ Reservation Items
- **Multi-component Bookings**: Add transport, accommodation, activities, guides, meals
- **Item Management**: CRUD operations on individual booking components
- **Confirmation Tracking**: Individual item confirmation status
- **Pricing Integration**: Automatic total calculation with item changes

## API Endpoints

### Booking Management
- `POST /api/v1/bookings/` - Create new booking
- `GET /api/v1/bookings/` - List bookings with search and filters
- `GET /api/v1/bookings/{id}` - Get booking details
- `GET /api/v1/bookings/{id}/summary` - Get comprehensive booking summary
- `PUT /api/v1/bookings/{id}` - Update booking information
- `POST /api/v1/bookings/{id}/confirm` - Confirm pending booking
- `POST /api/v1/bookings/{id}/cancel` - Cancel booking
- `GET /api/v1/bookings/{id}/voucher` - Download PDF voucher

### Availability Management
- `POST /api/v1/availability/check` - Check resource availability
- `POST /api/v1/availability/slots` - Create availability slot
- `PUT /api/v1/availability/slots/{id}` - Update availability slot
- `POST /api/v1/availability/reserve` - Reserve capacity
- `POST /api/v1/availability/release` - Release capacity
- `GET /api/v1/availability/schedule/{resource_id}` - Get resource schedule
- `POST /api/v1/availability/block/{resource_id}` - Block resource
- `GET /api/v1/availability/summary` - Get availability summary

### Pricing Management
- `POST /api/v1/pricing/calculate` - Calculate pricing with discounts
- `POST /api/v1/pricing/validate-promo` - Validate promo code
- `POST /api/v1/pricing/rules` - Create pricing rule
- `GET /api/v1/pricing/rules` - List pricing rules
- `GET /api/v1/pricing/rules/{id}` - Get pricing rule details
- `PUT /api/v1/pricing/rules/{id}` - Update pricing rule
- `DELETE /api/v1/pricing/rules/{id}` - Delete pricing rule

### Reservation Items
- `POST /api/v1/reservation-items/` - Add reservation item
- `GET /api/v1/reservation-items/{id}` - Get reservation item
- `GET /api/v1/reservation-items/booking/{id}` - Get booking items
- `PUT /api/v1/reservation-items/{id}` - Update reservation item
- `DELETE /api/v1/reservation-items/{id}` - Remove reservation item
- `POST /api/v1/reservation-items/{id}/confirm` - Confirm item
- `POST /api/v1/reservation-items/{id}/cancel` - Cancel item

## Quick Start

### Using Docker Compose (Recommended)
```bash
# Clone and setup
cd booking_service

# Copy environment variables
cp .env.example .env

# Start services
docker-compose up -d

# Check health
curl http://localhost:8002/health
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
python -m booking_service.main
```

## Configuration

Key environment variables in `.env`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5434/booking_db
REDIS_URL=redis://localhost:6381/2
AUTH_SERVICE_URL=http://auth_service:8000
CRM_SERVICE_URL=http://crm_app:8001
SECRET_KEY=your-super-secret-key
DEFAULT_CURRENCY=MAD
BOOKING_EXPIRY_MINUTES=30
```

## Data Models

### Booking
- **Core Info**: customer_id, service_type, status, pax_count, dates
- **Pricing**: base_price, discount_amount, total_price, currency
- **Payment**: payment_status, payment_method, payment_reference
- **Lifecycle**: created_at, confirmed_at, expires_at, cancelled_at

### ReservationItem
- **Details**: type, name, description, quantity, unit_price, total_price
- **References**: booking_id, reference_id (external service)
- **Status**: is_confirmed, is_cancelled
- **Specifications**: JSON field for item-specific data

### PricingRule
- **Rule Info**: name, description, code (promo), discount_type
- **Discounts**: discount_percentage, discount_amount
- **Conditions**: JSON criteria for rule application
- **Validity**: valid_from, valid_until, max_uses, priority

### AvailabilitySlot
- **Resource**: resource_type, resource_id, resource_name
- **Scheduling**: date, start_time, end_time
- **Capacity**: total_capacity, available_capacity, reserved_capacity
- **Status**: is_blocked, block_reason, booking_id

## Pricing Rules Examples

### Early Bird Discount
```json
{
  "name": "Early Bird 20%",
  "discount_type": "Percentage",
  "discount_percentage": 20.0,
  "conditions": {
    "min_advance_days": 30,
    "service_types": ["Tour"]
  }
}
```

### Group Discount
```json
{
  "name": "Group Discount",
  "discount_type": "Group Discount",
  "discount_percentage": 15.0,
  "conditions": {
    "group_threshold": 10,
    "service_types": ["Tour", "Transfer"]
  }
}
```

### Promo Code
```json
{
  "name": "Summer Special",
  "code": "SUMMER2024",
  "discount_type": "Fixed Amount",
  "discount_amount": 200.0,
  "max_uses": 100,
  "max_uses_per_customer": 1
}
```

## Security & Integration

- **JWT Authentication**: Integration with auth microservice
- **Role-Based Access Control**: Granular permissions per endpoint
- **Distributed Locking**: Redis-based locking prevents double-booking
- **Rate Limiting**: Protection against abuse and concurrent requests
- **Audit Logging**: Track all booking modifications and cancellations

## PDF Voucher Generation

- **Professional Design**: Company branding with QR codes
- **Comprehensive Details**: Booking info, customer details, pricing breakdown
- **Service Items**: Detailed list of included services
- **QR Code**: Quick verification and mobile-friendly access
- **Multi-language Support**: Ready for Arabic, French, English

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=booking_service

# Run specific test file
pytest booking_service/tests/test_bookings.py -v
```

## Integration with ERP Ecosystem

The booking microservice integrates seamlessly with other ERP components:

- **Authentication Service**: User authentication and authorization
- **CRM Service**: Customer information and interaction tracking
- **Tour Operations**: Tour scheduling and guide assignment
- **Driver Management**: Vehicle and driver availability
- **Business Intelligence**: Booking analytics and reporting
- **Notification Service**: Booking confirmations and reminders

## Performance & Scalability

- **Database Optimization**: Indexed queries and efficient pagination
- **Redis Caching**: Fast availability checks and locking mechanisms
- **Async Operations**: Non-blocking I/O for better performance
- **Horizontal Scaling**: Stateless design for easy scaling
- **Connection Pooling**: Efficient database connection management

## Moroccan Market Considerations

- **Multi-currency Support**: MAD (Moroccan Dirham) as default
- **Local Payment Methods**: Integration-ready for Moroccan payment gateways
- **Cultural Preferences**: Respect for local business practices
- **Compliance**: Moroccan tourism and business regulations
- **Language Support**: Arabic, French, English customer communications

## Contributing

1. Follow the modular architecture pattern
2. Add comprehensive tests for new features
3. Update documentation and API schemas
4. Follow Python code style guidelines
5. Ensure proper error handling and validation

## License

Private - Moroccan Tourist Transport ERP System
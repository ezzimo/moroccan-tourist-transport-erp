# Tour Operations Microservice

A comprehensive tour operations microservice for the Moroccan Tourist Transport ERP system, built with FastAPI, SQLModel, and PostgreSQL.

## Features

### 🗺️ Tour Template Management
- **Reusable Tour Definitions**: Create and manage tour templates with detailed information
- **Categorization**: Support for Cultural, Adventure, Desert, Coastal, City, and Custom tours
- **Difficulty Levels**: Easy, Moderate, Challenging, and Expert classifications
- **Comprehensive Details**: Highlights, inclusions, exclusions, requirements, and pricing
- **Template Duplication**: Easy cloning of existing templates for variations

### 🎯 Tour Instance Operations
- **Operationalized Tours**: Convert templates into actual tour instances linked to bookings
- **Resource Assignment**: Assign guides, vehicles, and drivers to tours
- **Status Management**: Complete lifecycle from planned to completed
- **Progress Tracking**: Real-time monitoring of tour execution and completion
- **Customer Integration**: Seamless integration with CRM for customer data

### 📋 Itinerary Management
- **Detailed Scheduling**: Day-by-day, time-based activity planning
- **Activity Types**: Visits, meals, transport, accommodation, activities, and more
- **Location Tracking**: GPS coordinates and address information
- **Completion Tracking**: Mark activities as completed with notes and actual duration
- **Dynamic Reordering**: Flexible itinerary adjustments during tour execution

### 🚨 Incident Management
- **Real-time Reporting**: Immediate incident logging with severity classification
- **Comprehensive Types**: Delays, medical, complaints, breakdowns, weather, safety issues
- **Priority Scoring**: Automatic priority calculation based on type and severity
- **Resolution Tracking**: Complete incident lifecycle with resolution notes
- **Escalation Workflow**: Escalate incidents to appropriate personnel

### 📱 Mobile-Ready Features
- **Offline Support**: Critical data available without internet connection
- **Real-time Notifications**: Push updates to guides and coordinators
- **QR Code Integration**: Quick access to tour information
- **WebSocket Support**: Live updates for tour progress and incidents

## API Endpoints

### Tour Template Management
- `POST /api/v1/tour-templates/` - Create new tour template
- `GET /api/v1/tour-templates/` - List templates with search and filters
- `GET /api/v1/tour-templates/featured` - Get featured templates
- `GET /api/v1/tour-templates/category/{category}` - Get templates by category
- `GET /api/v1/tour-templates/{id}` - Get template details
- `PUT /api/v1/tour-templates/{id}` - Update template
- `DELETE /api/v1/tour-templates/{id}` - Delete template
- `POST /api/v1/tour-templates/{id}/duplicate` - Duplicate template

### Tour Instance Operations
- `POST /api/v1/tour-instances/` - Create new tour instance
- `GET /api/v1/tour-instances/` - List instances with filters
- `GET /api/v1/tour-instances/active` - Get currently active tours
- `GET /api/v1/tour-instances/{id}` - Get instance details
- `GET /api/v1/tour-instances/{id}/summary` - Get comprehensive summary
- `PUT /api/v1/tour-instances/{id}` - Update instance
- `POST /api/v1/tour-instances/{id}/assign` - Assign resources
- `POST /api/v1/tour-instances/{id}/status` - Update status
- `POST /api/v1/tour-instances/{id}/progress` - Update progress

### Itinerary Management
- `POST /api/v1/itinerary/items` - Add itinerary item
- `GET /api/v1/itinerary/items/{id}` - Get item details
- `PUT /api/v1/itinerary/items/{id}` - Update item
- `POST /api/v1/itinerary/items/{id}/complete` - Mark as completed
- `DELETE /api/v1/itinerary/items/{id}` - Delete item
- `GET /api/v1/itinerary/tour/{id}` - Get full tour itinerary
- `GET /api/v1/itinerary/tour/{id}/day/{day}` - Get day itinerary
- `POST /api/v1/itinerary/tour/{id}/day/{day}/reorder` - Reorder items

### Incident Management
- `POST /api/v1/incidents/` - Create new incident
- `GET /api/v1/incidents/` - List incidents with filters
- `GET /api/v1/incidents/urgent` - Get urgent incidents
- `GET /api/v1/incidents/stats` - Get incident statistics
- `GET /api/v1/incidents/{id}` - Get incident details
- `PUT /api/v1/incidents/{id}` - Update incident
- `POST /api/v1/incidents/{id}/resolve` - Resolve incident
- `POST /api/v1/incidents/{id}/escalate` - Escalate incident
- `GET /api/v1/incidents/tour/{id}` - Get tour incidents

## Quick Start

### Using Docker Compose (Recommended)
```bash
# Clone and setup
cd tour_service

# Copy environment variables
cp .env.example .env

# Start services
docker-compose up -d

# Check health
curl http://localhost:8003/health
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
python -m tour_service.main
```

## Configuration

Key environment variables in `.env`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5435/tour_db
REDIS_URL=redis://localhost:6382/3
AUTH_SERVICE_URL=http://localhost:8000
CRM_SERVICE_URL=http://localhost:8001
BOOKING_SERVICE_URL=http://localhost:8002
SECRET_KEY=your-super-secret-key
DEFAULT_LANGUAGE=French
MAX_TOUR_DURATION_DAYS=30
```

## Data Models

### TourTemplate
- **Basic Info**: title, description, category, difficulty, duration
- **Location**: default_region, starting_location, ending_location
- **Capacity**: min_participants, max_participants, base_price
- **Content**: highlights, inclusions, exclusions, requirements
- **Status**: is_active, is_featured, timestamps

### TourInstance
- **References**: template_id, booking_id, customer_id
- **Details**: title, status, dates, participant_count, language
- **Resources**: assigned_guide_id, assigned_vehicle_id, assigned_driver_id
- **Progress**: current_day, completion_percentage, actual_dates
- **Notes**: special_requirements, internal_notes, participant_details

### ItineraryItem
- **Schedule**: day_number, start_time, end_time, duration_minutes
- **Activity**: activity_type, title, description, location_name
- **Location**: address, coordinates, notes, cost
- **Status**: is_completed, completed_at, completed_by, is_cancelled

### Incident
- **Classification**: incident_type, severity, title, description
- **Context**: location, day_number, affected_participants, delay_minutes
- **Resolution**: is_resolved, resolution_description, resolved_by, resolved_at
- **Escalation**: escalated_to, follow_up_notes, requires_follow_up

## Real-time Features

### WebSocket Notifications
- Tour status changes
- Itinerary updates
- Incident alerts
- Resource assignments
- Progress updates

### Notification Channels
- `tour_updates:{tour_id}` - Tour-specific updates
- `incident_alerts` - System-wide incident alerts
- `resource_updates:{type}:{id}` - Resource-specific updates

### Offline Support
- Critical tour data cached locally
- Incident reporting works offline
- Sync when connection restored

## Security & Integration

- **JWT Authentication**: Integration with auth microservice
- **Role-Based Access Control**: Granular permissions per endpoint
- **Service Integration**: Seamless communication with CRM and Booking services
- **Data Validation**: Comprehensive input validation and sanitization
- **Audit Logging**: Track all tour modifications and incidents

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=tour_service

# Run specific test file
pytest tour_service/tests/test_tour_templates.py -v
```

## Integration with ERP Ecosystem

The tour operations microservice integrates seamlessly with other ERP components:

- **Authentication Service**: User authentication and authorization
- **CRM Service**: Customer information and interaction tracking
- **Booking Service**: Booking details and reservation management
- **Driver Management**: Vehicle and driver availability
- **Business Intelligence**: Tour analytics and performance reporting
- **Notification Service**: Real-time alerts and communications

## Performance & Scalability

- **Database Optimization**: Indexed queries and efficient pagination
- **Redis Caching**: Fast notification delivery and session management
- **Async Operations**: Non-blocking I/O for better performance
- **Horizontal Scaling**: Stateless design for easy scaling
- **Real-time Updates**: WebSocket connections for live data

## Moroccan Market Considerations

- **Multi-language Support**: Arabic, French, English tour operations
- **Regional Expertise**: Morocco-specific tour categories and locations
- **Cultural Sensitivity**: Respect for local customs and practices
- **Compliance**: Moroccan tourism regulations and safety standards
- **Local Integration**: Support for Moroccan guides and local businesses

## Contributing

1. Follow the modular architecture pattern
2. Add comprehensive tests for new features
3. Update documentation and API schemas
4. Follow Python code style guidelines
5. Ensure proper error handling and validation

## License

Private - Moroccan Tourist Transport ERP System
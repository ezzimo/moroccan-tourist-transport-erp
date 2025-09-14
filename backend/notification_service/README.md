# Notification Service Microservice

A comprehensive notification service microservice for the Moroccan Tourist Transport ERP system, built with FastAPI, SQLModel, and PostgreSQL.

## Features

### 📧 Multi-Channel Notifications
- **Email Notifications**: SMTP-based email delivery with HTML/text support
- **SMS Notifications**: Twilio integration for SMS delivery
- **Push Notifications**: Firebase Cloud Messaging for mobile apps
- **WhatsApp Messages**: WhatsApp Business API integration
- **Webhook Notifications**: HTTP webhook delivery for system integrations
- **In-App Notifications**: Real-time in-app messaging

### 📝 Template Management
- **Dynamic Templates**: Variable-based templates with Jinja2-like syntax
- **Multi-Channel Support**: Templates for email, SMS, push, and WhatsApp
- **Template Validation**: Syntax validation and variable checking
- **Version Control**: Template versioning with usage tracking
- **Preview System**: Test templates with sample data
- **Multi-Language**: Support for Arabic, French, and English templates

### ⚙️ User Preferences
- **Channel Preferences**: Users can enable/disable specific channels
- **Notification Type Control**: Granular control over notification types
- **Quiet Hours**: Configurable quiet hours with timezone support
- **Rate Limiting**: Daily limits for emails and SMS
- **Contact Management**: Email, phone, and push token management
- **Fallback Channels**: Automatic fallback when primary channel fails

### 📊 Delivery Tracking & Analytics
- **Real-time Status**: Track pending, sent, delivered, and failed notifications
- **Retry Logic**: Automatic retry with exponential backoff
- **Delivery Analytics**: Success rates, delivery times, and failure analysis
- **Audit Trails**: Complete history of all notification events
- **Performance Metrics**: Channel performance and user engagement stats
- **Export Capabilities**: CSV and JSON export for compliance

### 🔄 Advanced Features
- **Bulk Notifications**: Send to multiple recipients efficiently
- **Scheduled Notifications**: Schedule notifications for future delivery
- **Priority Queuing**: Priority-based message delivery
- **Group Notifications**: Group related notifications together
- **Fallback Logic**: Automatic channel fallback on delivery failure
- **Rate Limiting**: Prevent spam and respect provider limits

## API Endpoints

### Notification Management
- `POST /api/v1/notifications/send` - Send notification to recipients
- `POST /api/v1/notifications/send-bulk` - Send bulk notifications
- `GET /api/v1/notifications/` - List notifications with filters
- `GET /api/v1/notifications/stats` - Get notification statistics
- `GET /api/v1/notifications/{id}` - Get notification details
- `PUT /api/v1/notifications/{id}` - Update notification status
- `POST /api/v1/notifications/retry-failed` - Retry failed notifications
- `GET /api/v1/notifications/recipient/{id}` - Get recipient notifications
- `GET /api/v1/notifications/group/{id}` - Get group notifications

### Template Management
- `POST /api/v1/templates/` - Create new template
- `GET /api/v1/templates/` - List templates with filters
- `GET /api/v1/templates/channel/{channel}` - Get templates by channel
- `GET /api/v1/templates/{id}` - Get template details
- `PUT /api/v1/templates/{id}` - Update template
- `DELETE /api/v1/templates/{id}` - Delete template
- `POST /api/v1/templates/preview` - Preview template with variables
- `GET /api/v1/templates/{id}/validate` - Validate template
- `POST /api/v1/templates/{id}/duplicate` - Duplicate template

### User Preferences
- `POST /api/v1/preferences/` - Create user preferences
- `GET /api/v1/preferences/` - Get all preferences
- `GET /api/v1/preferences/{user_id}` - Get user preferences
- `PUT /api/v1/preferences/{user_id}` - Update user preferences
- `DELETE /api/v1/preferences/{user_id}` - Delete preferences
- `POST /api/v1/preferences/bulk-update` - Bulk update preferences
- `GET /api/v1/preferences/channel/{channel}` - Get users by channel
- `PUT /api/v1/preferences/{user_id}/contact` - Update contact info

### Notification Logs
- `GET /api/v1/logs/{recipient_id}` - Get recipient notification history
- `GET /api/v1/logs/{recipient_id}/summary` - Get recipient summary
- `GET /api/v1/logs/audit/{notification_id}` - Get audit trail
- `GET /api/v1/logs/export/{recipient_id}` - Export notification history

## Quick Start

### Using Docker Compose (Recommended)
```bash
# Clone and setup
cd notification_service

# Copy environment variables
cp .env.example .env

# Configure email/SMS providers in .env
# SMTP_USERNAME=your-email@gmail.com
# SMTP_PASSWORD=your-app-password
# TWILIO_ACCOUNT_SID=your-twilio-sid
# TWILIO_AUTH_TOKEN=your-twilio-token

# Start services
docker-compose up -d

# Check health
curl http://localhost:8007/health
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
python -m notification_service.main
```

## Configuration

Key environment variables in `.env`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5439/notification_db
REDIS_URL=redis://localhost:6386/7
AUTH_SERVICE_URL=http://auth_service:8000

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@atlastours.ma

# SMS Configuration (Twilio)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Push Notifications (Firebase)
FIREBASE_SERVER_KEY=your-server-key
FIREBASE_PROJECT_ID=your-project-id

# Notification Settings
MAX_RETRY_ATTEMPTS=3
RETRY_DELAY_SECONDS=60
ENABLE_FALLBACK_CHANNELS=true
```

## Data Models

### Notification
- **Identification**: type, channel, recipient information
- **Content**: subject, message, template variables
- **Status**: pending, queued, sending, sent, delivered, failed
- **Tracking**: retry count, delivery timestamps, error information
- **Metadata**: priority, scheduling, expiry, grouping

### Template
- **Content**: name, subject, body with variable placeholders
- **Configuration**: channel, type, language, content format
- **Variables**: JSON schema for required/optional variables
- **Validation**: syntax checking and variable validation
- **Usage**: tracking usage count and last used timestamp

### UserPreference
- **Channels**: enable/disable email, SMS, push, WhatsApp
- **Contact Info**: email, phone, push token management
- **Notification Types**: granular control per notification type
- **Quiet Hours**: configurable quiet periods with timezone
- **Limits**: daily rate limits for different channels

## Integration Examples

### Booking Confirmation
```python
# Send booking confirmation
await notification_service.send_notification({
    "type": "booking_confirmed",
    "recipients": [{"user_id": customer_id, "email": customer_email}],
    "template_id": booking_confirmation_template_id,
    "template_variables": {
        "customer_name": "Ahmed Hassan",
        "booking_reference": "BK-2024-001",
        "tour_name": "Sahara Desert Adventure",
        "start_date": "2024-03-15"
    }
})
```

### System Alert
```python
# Send system alert to administrators
await notification_service.send_bulk_notification({
    "type": "system_alert",
    "channel": "email",
    "template_id": alert_template_id,
    "recipients": admin_users,
    "template_variables": {
        "alert_type": "Vehicle Breakdown",
        "severity": "High",
        "location": "Highway A7"
    }
})
```

## Security & Integration

- **JWT Authentication**: Integration with auth microservice
- **Role-Based Access Control**: Granular permissions per endpoint
- **Data Encryption**: Sensitive data encryption at rest
- **Rate Limiting**: Prevent abuse and respect provider limits
- **Audit Logging**: Complete audit trail for compliance

## Provider Integration

### Email (SMTP)
- Gmail, Outlook, SendGrid, AWS SES support
- HTML and plain text email support
- Attachment support (future enhancement)
- Bounce and complaint handling

### SMS (Twilio)
- International SMS delivery
- Delivery status tracking
- Cost optimization with local providers
- Morocco-specific SMS gateway support

### Push Notifications (Firebase)
- iOS and Android push notifications
- Rich notifications with images and actions
- Topic-based messaging for broadcasts
- Analytics and engagement tracking

### WhatsApp Business
- WhatsApp Business API integration
- Template message support
- Media message capabilities
- Delivery and read receipts

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=notification_service

# Run specific test file
pytest notification_service/tests/test_notifications.py -v
```

## Integration with ERP Ecosystem

The notification service integrates seamlessly with all ERP components:

- **Booking Service**: Booking confirmations, cancellations, reminders
- **Tour Operations**: Assignment notifications, incident alerts
- **Fleet Management**: Maintenance reminders, compliance alerts
- **HR Service**: Training notifications, contract reminders
- **Financial Service**: Payment confirmations, invoice notifications
- **CRM Service**: Customer communication and follow-ups

## Performance & Scalability

- **Async Processing**: Non-blocking notification delivery
- **Redis Queue**: Efficient message queuing and retry logic
- **Database Optimization**: Indexed queries and efficient pagination
- **Connection Pooling**: Efficient database and Redis connections
- **Horizontal Scaling**: Stateless design for easy scaling
- **Rate Limiting**: Respect provider limits and prevent abuse

## Moroccan Market Considerations

- **Multi-language Support**: Arabic, French, English templates
- **Local Providers**: Integration with Moroccan SMS providers
- **Timezone Support**: Africa/Casablanca timezone handling
- **Cultural Sensitivity**: Respect for local communication preferences
- **Compliance**: Morocco telecommunications regulations

## Contributing

1. Follow the modular architecture pattern
2. Add comprehensive tests for new features
3. Update documentation and API schemas
4. Follow Python code style guidelines
5. Ensure proper error handling and validation

## License

Private - Moroccan Tourist Transport ERP System
# Frontend API Routing Configuration

## Overview

The frontend has been updated to properly route API requests to the correct microservices. Previously, all `/api/v1` requests were routed to the auth service on port 8000. Now, each service endpoint is routed to its respective microservice.

## Service Port Mapping

| Service | Port | Endpoints |
|---------|------|-----------|
| Auth Service | 8000 | `/api/v1/auth/*`, `/api/v1/users/*`, `/api/v1/roles/*` |
| CRM Service | 8001 | `/api/v1/customers/*`, `/api/v1/interactions/*`, `/api/v1/feedback/*`, `/api/v1/segments/*` |
| Booking Service | 8002 | `/api/v1/bookings/*`, `/api/v1/reservations/*`, `/api/v1/availability/*`, `/api/v1/pricing/*` |
| Driver Service | 8003 | `/api/v1/drivers/*`, `/api/v1/assignments/*`, `/api/v1/incidents/*`, `/api/v1/training/*` |
| Fleet Service | 8004 | `/api/v1/vehicles/*`, `/api/v1/maintenance/*`, `/api/v1/fleet/*` |
| Financial Service | 8005 | `/api/v1/invoices/*`, `/api/v1/payments/*`, `/api/v1/expenses/*`, `/api/v1/analytics/*` |
| HR Service | 8006 | `/api/v1/employees/*`, `/api/v1/schedules/*`, `/api/v1/payroll/*` |
| Inventory Service | 8007 | `/api/v1/inventory/*`, `/api/v1/parts/*`, `/api/v1/suppliers/*` |
| Notification Service | 8008 | `/api/v1/notifications/*`, `/api/v1/templates/*` |
| QA Service | 8009 | `/api/v1/quality/*`, `/api/v1/audits/*`, `/api/v1/reports/*` |
| Tour Service | 8010 | `/api/v1/tours/*`, `/api/v1/packages/*`, `/api/v1/guides/*` |

## Configuration Files

### 1. `vite.config.ts`
Updated with comprehensive proxy configuration that routes each API endpoint to the correct microservice port.

### 2. `src/config/services.ts`
New service configuration file that provides:
- Environment-based service URL configuration
- Centralized endpoint management
- Support for development, production, and Docker environments

### 3. `.env.example`
Environment configuration template with all service URLs and application settings.

## Development Setup

1. **Start all microservices** using Docker Compose:
   ```bash
   docker compose -f docker-compose.full.yml up -d
   ```

2. **Start the frontend** development server:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the application** at `http://localhost:5173`

## How It Works

### Development Environment
- Vite proxy intercepts `/api/v1/*` requests
- Routes them to the appropriate microservice based on the path
- Example: `/api/v1/customers/` → `http://localhost:8001/api/v1/customers/`

### Production Environment
- Direct API calls to service URLs
- Configure service URLs in environment variables
- Example: `VITE_CRM_SERVICE_URL=https://crm.yourdomain.com`

### Docker Environment
- Uses container networking
- Services communicate via container names
- Example: `http://crm_service:8001/api/v1/customers/`

## API Client Usage

The existing API clients (`src/*/api/*.ts`) continue to work without changes because they use relative paths (`/api/v1/*`). The routing is handled transparently by the Vite proxy in development and by the service configuration in production.

### Example API Call Flow

1. **Frontend makes request**: `GET /api/v1/customers/`
2. **Vite proxy intercepts**: Matches `/api/v1/customers` pattern
3. **Routes to CRM service**: `http://localhost:8001/api/v1/customers/`
4. **CRM service responds**: Returns customer data
5. **Frontend receives response**: Processes the data normally

## Environment Variables

### Development
```bash
VITE_ENVIRONMENT=development
```

### Production
```bash
VITE_ENVIRONMENT=production
VITE_CRM_SERVICE_URL=https://crm.yourdomain.com
VITE_AUTH_SERVICE_URL=https://auth.yourdomain.com
# ... other service URLs
```

### Docker
```bash
VITE_ENVIRONMENT=docker
```

## Troubleshooting

### Common Issues

1. **Service not responding**
   - Check if the microservice is running on the expected port
   - Verify Docker containers are healthy: `docker compose ps`

2. **CORS errors**
   - Ensure microservices have proper CORS configuration
   - Check that `changeOrigin: true` is set in Vite proxy

3. **Wrong service routing**
   - Verify the endpoint path matches the proxy configuration
   - Check the order of proxy rules (more specific rules should come first)

### Debug API Routing

Enable debug logging by setting:
```bash
VITE_DEBUG_API=true
```

This will log all API requests and their routing in the browser console.

## Migration Notes

### For Existing Code
- No changes required to existing API client code
- All existing endpoints continue to work
- Authentication flow remains unchanged

### For New Features
- Use the `serviceEndpoints` object from `src/config/services.ts` for consistent endpoint URLs
- Follow the established pattern for new API clients

## Testing

To test the routing configuration:

1. **Start all services**: `docker compose -f docker-compose.full.yml up -d`
2. **Start frontend**: `npm run dev`
3. **Test authentication**: Login should work (auth service)
4. **Test CRM**: Customer list should load (CRM service)
5. **Check browser network tab**: Verify requests go to correct ports

## Future Improvements

1. **API Gateway**: Consider implementing an API gateway for production
2. **Load Balancing**: Add load balancing for high availability
3. **Service Discovery**: Implement dynamic service discovery
4. **Health Checks**: Add health check endpoints for all services


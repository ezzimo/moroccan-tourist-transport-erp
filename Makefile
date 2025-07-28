# Moroccan Tourist Transport ERP - Makefile
# Development and deployment automation

.PHONY: help bootstrap-users bootstrap-users-prod bootstrap-users-dry test-bootstrap build up down logs clean

# Default target
help:
	@echo "Moroccan Tourist Transport ERP - Available Commands:"
	@echo ""
	@echo "🚀 Bootstrap Commands:"
	@echo "  bootstrap-users      - Create demo roles and users for development"
	@echo "  bootstrap-users-prod - Create roles and users for production"
	@echo "  bootstrap-users-dry  - Show what would be created (dry run)"
	@echo "  test-bootstrap       - Test bootstrap script with verbose output"
	@echo ""
	@echo "🐳 Docker Commands:"
	@echo "  build               - Build all Docker containers"
	@echo "  up                  - Start all services"
	@echo "  down                - Stop all services"
	@echo "  logs                - Show logs from all services"
	@echo "  clean               - Clean up containers and volumes"
	@echo ""
	@echo "🧪 Testing Commands:"
	@echo "  test-auth           - Run authentication service tests"
	@echo "  test-frontend       - Run frontend tests"
	@echo ""

# Bootstrap commands
bootstrap-users:
	@echo "🔧 Bootstrapping roles and users for development..."
	python3 scripts/bootstrap_roles_users.py --environment development

bootstrap-users-prod:
	@echo "🔧 Bootstrapping roles and users for production..."
	python3 scripts/bootstrap_roles_users.py --environment production

bootstrap-users-dry:
	@echo "🔍 Dry run - showing what would be created..."
	python3 scripts/bootstrap_roles_users.py --dry-run --verbose

test-bootstrap:
	@echo "🧪 Testing bootstrap script..."
	python3 scripts/bootstrap_roles_users.py --dry-run --verbose --environment development

# Docker commands
build:
	@echo "🏗️  Building Docker containers..."
	docker compose build

up:
	@echo "🚀 Starting all services..."
	docker compose up -d

down:
	@echo "🛑 Stopping all services..."
	docker compose down

logs:
	@echo "📋 Showing logs from all services..."
	docker compose logs -f

clean:
	@echo "🧹 Cleaning up containers and volumes..."
	docker compose down -v
	docker system prune -f

# Testing commands
test-auth:
	@echo "🧪 Running authentication service tests..."
	cd backend/app && python3 -m pytest tests/test_auth.py -v

test-frontend:
	@echo "🧪 Running frontend tests..."
	cd frontend && npm run test:run

# Development workflow
dev-setup: build up bootstrap-users
	@echo "✅ Development environment ready!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000"
	@echo ""
	@echo "Demo users created:"
	@echo "  - superadmin@demo.local (SuperAdmin123!)"
	@echo "  - admin@demo.local (Admin123!)"
	@echo "  - dispatcher@demo.local (Dispatcher123!)"
	@echo "  - driver@demo.local (Driver123!)"

# Production deployment
prod-deploy: build up bootstrap-users-prod
	@echo "🚀 Production deployment completed!"

# Quick development restart
restart: down up
	@echo "🔄 Services restarted!"

# Database operations
db-reset:
	@echo "⚠️  Resetting database..."
	docker compose down -v
	docker compose up -d db_auth redis_auth
	sleep 10
	$(MAKE) bootstrap-users

# Health check
health:
	@echo "🏥 Checking service health..."
	@curl -f http://localhost:8000/health || echo "❌ Backend unhealthy"
	@curl -f http://localhost:3000 || echo "❌ Frontend unhealthy"
	@echo "✅ Health check completed"


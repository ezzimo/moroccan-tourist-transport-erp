"""
Test configuration and fixtures for fleet management microservice
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from main import app
from database import get_session, get_redis
from models.vehicle import Vehicle, VehicleType, VehicleStatus, FuelType
from models.maintenance_record import MaintenanceRecord, MaintenanceType
from models.assignment import Assignment, AssignmentStatus
from models.fuel_log import FuelLog
import fakeredis
import os
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal


# Test database engine
@pytest.fixture(name="session")
def session_fixture():
    """Create test database session"""
    # Use in-memory SQLite for testing
    engine = create_engine(
        "sqlite:///test_fleet.db",
        connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session
    
    # Clean up
    try:
        os.unlink("test_fleet.db")
    except:
        pass


@pytest.fixture(name="redis_client")
def redis_client_fixture():
    """Create fake Redis client for testing"""
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture(name="client")
def client_fixture(session: Session, redis_client):
    """Create test client with dependency overrides"""
    def get_session_override():
        return session
    
    def get_redis_override():
        return redis_client
    
    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_redis] = get_redis_override
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_vehicle_data():
    """Sample vehicle data for testing"""
    return {
        "license_plate": "ABC-123-45",
        "vehicle_type": "Bus",
        "brand": "Mercedes",
        "model": "Sprinter",
        "year": 2022,
        "color": "White",
        "seating_capacity": 16,
        "fuel_type": "Diesel",
        "engine_size": 2.2,
        "transmission": "Manual",
        "current_odometer": 15000,
        "registration_expiry": "2025-12-31",
        "insurance_expiry": "2024-06-30",
        "inspection_expiry": "2024-03-15",
        "purchase_date": "2022-01-15",
        "purchase_price": 45000.0,
        "vin_number": "WDB9066351234567",
        "notes": "Primary tour vehicle for desert excursions"
    }


@pytest.fixture
def sample_maintenance_data():
    """Sample maintenance data for testing"""
    return {
        "maintenance_type": "Preventive",
        "description": "Regular oil change and filter replacement",
        "date_performed": "2024-01-15",
        "provider_name": "Atlas Auto Service",
        "provider_contact": "+212522123456",
        "cost": 350.0,
        "currency": "MAD",
        "odometer_reading": 15000,
        "parts_replaced": "Oil filter, air filter",
        "labor_hours": 2.0,
        "next_service_date": "2024-07-15",
        "next_service_odometer": 20000,
        "warranty_until": "2024-07-15",
        "notes": "All systems checked and functioning properly"
    }


@pytest.fixture
def sample_assignment_data():
    """Sample assignment data for testing"""
    return {
        "tour_instance_id": str(uuid.uuid4()),
        "start_date": "2024-03-01",
        "end_date": "2024-03-03",
        "pickup_location": "Marrakech Hotel",
        "dropoff_location": "Merzouga Desert Camp",
        "estimated_distance": 560,
        "notes": "3-day desert tour with overnight camping",
        "special_instructions": "Vehicle needs to be equipped with camping gear"
    }


@pytest.fixture
def sample_fuel_log_data():
    """Sample fuel log data for testing"""
    return {
        "date": "2024-01-20",
        "odometer_reading": 15200,
        "fuel_amount": 65.0,
        "fuel_cost": 845.0,
        "price_per_liter": 13.0,
        "station_name": "Total Marrakech",
        "location": "Marrakech, Morocco",
        "trip_purpose": "Desert tour return",
        "is_full_tank": True,
        "receipt_number": "TOT-2024-001234",
        "notes": "Full tank after 3-day desert tour"
    }


@pytest.fixture
def create_test_vehicle(session):
    """Factory function to create test vehicles"""
    def _create_vehicle(**kwargs):
        default_data = {
            "license_plate": f"TEST-{uuid.uuid4().hex[:6].upper()}",
            "vehicle_type": VehicleType.BUS,
            "brand": "Test Brand",
            "model": "Test Model",
            "year": 2020,
            "seating_capacity": 16,
            "fuel_type": FuelType.DIESEL,
            "current_odometer": 10000
        }
        default_data.update(kwargs)
        
        vehicle = Vehicle(**default_data)
        session.add(vehicle)
        session.commit()
        session.refresh(vehicle)
        return vehicle
    
    return _create_vehicle


@pytest.fixture
def create_test_maintenance_record(session):
    """Factory function to create test maintenance records"""
    def _create_record(vehicle_id, **kwargs):
        default_data = {
            "vehicle_id": vehicle_id,
            "maintenance_type": MaintenanceType.PREVENTIVE,
            "description": "Test maintenance",
            "date_performed": date.today(),
            "cost": 100.0
        }
        default_data.update(kwargs)
        
        record = MaintenanceRecord(**default_data)
        session.add(record)
        session.commit()
        session.refresh(record)
        return record
    
    return _create_record


@pytest.fixture
def create_test_assignment(session):
    """Factory function to create test assignments"""
    def _create_assignment(vehicle_id, **kwargs):
        default_data = {
            "vehicle_id": vehicle_id,
            "tour_instance_id": uuid.uuid4(),
            "start_date": date.today() + timedelta(days=1),
            "end_date": date.today() + timedelta(days=3),
            "status": AssignmentStatus.SCHEDULED
        }
        default_data.update(kwargs)
        
        assignment = Assignment(**default_data)
        session.add(assignment)
        session.commit()
        session.refresh(assignment)
        return assignment
    
    return _create_assignment


@pytest.fixture
def create_test_fuel_log(session):
    """Factory function to create test fuel logs"""
    def _create_log(vehicle_id, **kwargs):
        default_data = {
            "vehicle_id": vehicle_id,
            "date": date.today(),
            "odometer_reading": 10000,
            "fuel_amount": 50.0,
            "fuel_cost": 650.0,
            "price_per_liter": 13.0
        }
        default_data.update(kwargs)
        
        log = FuelLog(**default_data)
        session.add(log)
        session.commit()
        session.refresh(log)
        return log
    
    return _create_log


@pytest.fixture
def mock_auth_user():
    """Mock authenticated user for testing"""
    from utils.auth import CurrentUser
    return CurrentUser(
        user_id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test User",
        permissions=["fleet:create:*", "fleet:read:*", "fleet:update:*", "fleet:delete:*"]
    )
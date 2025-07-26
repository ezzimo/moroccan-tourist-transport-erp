"""
Test configuration and fixtures for booking microservice
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from main import app
from database import get_session, get_redis
from models.booking import (
    Booking,
    ServiceType,
    ReservationItem,
    ItemType,
    PricingRule,
    DiscountType,
    AvailabilitySlot,
    ResourceType,
)
import fakeredis
import os
import uuid
from datetime import date, timedelta
from decimal import Decimal


# Test database engine
@pytest.fixture(name="session")
def session_fixture():
    """Create test database session"""
    # Use in-memory SQLite for testing
    engine = create_engine(
        "sqlite:///test_booking.db", connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    # Clean up
    try:
        os.unlink("test_booking.db")
    except Exception:
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
def sample_booking_data():
    """Sample booking data for testing"""
    return {
        "customer_id": str(uuid.uuid4()),
        "service_type": "Tour",
        "pax_count": 4,
        "lead_passenger_name": "Ahmed Hassan",
        "lead_passenger_email": "ahmed@example.com",
        "lead_passenger_phone": "+212600123456",
        "start_date": "2024-06-15",
        "end_date": "2024-06-17",
        "base_price": 2000.00,
        "special_requests": "Vegetarian meals preferred",
    }


@pytest.fixture
def sample_reservation_item_data():
    """Sample reservation item data for testing"""
    return {
        "type": "Transport",
        "name": "Airport Transfer",
        "description": "Round trip airport transfer",
        "quantity": 1,
        "unit_price": 150.00,
        "specifications": {"vehicle_type": "SUV", "pickup_time": "08:00"},
    }


@pytest.fixture
def sample_pricing_rule_data():
    """Sample pricing rule data for testing"""
    return {
        "name": "Early Bird Discount",
        "description": "10% discount for bookings made 30 days in advance",
        "discount_type": "Percentage",
        "discount_percentage": 10.0,
        "conditions": {"min_advance_days": 30, "service_types": ["Tour"]},
        "valid_from": "2024-01-01",
        "valid_until": "2024-12-31",
        "priority": 1,
        "is_active": True,
    }


@pytest.fixture
def sample_availability_slot_data():
    """Sample availability slot data for testing"""
    return {
        "resource_type": "Vehicle",
        "resource_id": str(uuid.uuid4()),
        "resource_name": "Toyota Land Cruiser - TC001",
        "date": "2024-06-15",
        "total_capacity": 8,
        "start_time": "2024-06-15T08:00:00",
        "end_time": "2024-06-15T18:00:00",
    }


@pytest.fixture
def create_test_booking(session):
    """Factory function to create test bookings"""

    def _create_booking(**kwargs):
        default_data = {
            "customer_id": uuid.uuid4(),
            "service_type": ServiceType.TOUR,
            "pax_count": 2,
            "lead_passenger_name": "Test Customer",
            "lead_passenger_email": "test@example.com",
            "lead_passenger_phone": "+212600000000",
            "start_date": date.today() + timedelta(days=7),
            "base_price": Decimal("1000.00"),
            "discount_amount": Decimal("0.00"),
            "total_price": Decimal("1000.00"),
        }
        default_data.update(kwargs)

        booking = Booking(**default_data)
        session.add(booking)
        session.commit()
        session.refresh(booking)
        return booking

    return _create_booking


@pytest.fixture
def create_test_reservation_item(session):
    """Factory function to create test reservation items"""

    def _create_item(booking_id, **kwargs):
        default_data = {
            "booking_id": booking_id,
            "type": ItemType.TRANSPORT,
            "name": "Test Service",
            "quantity": 1,
            "unit_price": Decimal("100.00"),
            "total_price": Decimal("100.00"),
        }
        default_data.update(kwargs)

        item = ReservationItem(**default_data)
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    return _create_item


@pytest.fixture
def create_test_pricing_rule(session):
    """Factory function to create test pricing rules"""

    def _create_rule(**kwargs):
        default_data = {
            "name": f"Test Rule {uuid.uuid4().hex[:8]}",
            "discount_type": DiscountType.PERCENTAGE,
            "discount_percentage": Decimal("10.00"),
            "conditions": '{"service_types": ["Tour"]}',
            "valid_from": date.today(),
            "valid_until": date.today() + timedelta(days=365),
            "priority": 1,
            "is_active": True,
        }
        default_data.update(kwargs)

        rule = PricingRule(**default_data)
        session.add(rule)
        session.commit()
        session.refresh(rule)
        return rule

    return _create_rule


@pytest.fixture
def create_test_availability_slot(session):
    """Factory function to create test availability slots"""

    def _create_slot(**kwargs):
        default_data = {
            "resource_type": ResourceType.VEHICLE,
            "resource_id": uuid.uuid4(),
            "resource_name": "Test Vehicle",
            "date": date.today() + timedelta(days=7),
            "total_capacity": 8,
            "available_capacity": 8,
        }
        default_data.update(kwargs)

        slot = AvailabilitySlot(**default_data)
        session.add(slot)
        session.commit()
        session.refresh(slot)
        return slot

    return _create_slot


@pytest.fixture
def mock_auth_user():
    """Mock authenticated user for testing"""
    from utils.auth import CurrentUser

    return CurrentUser(
        user_id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test User",
        permissions=[
            "booking:create:*",
            "booking:read:*",
            "booking:update:*",
            "booking:delete:*",
        ],
    )

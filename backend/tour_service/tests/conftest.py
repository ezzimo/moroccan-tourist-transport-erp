"""
Test configuration and fixtures for tour operations microservice
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from main import app
from database import get_session, get_redis
from models.tour_template import TourTemplate, TourCategory, DifficultyLevel
from models.tour_instance import TourInstance, TourStatus
from models.itinerary_item import ItineraryItem, ActivityType
from models.incident import Incident, IncidentType, SeverityLevel
import fakeredis
import os
import uuid
from datetime import datetime, date, timedelta, time


# Test database engine
@pytest.fixture(name="session")
def session_fixture():
    """Create test database session"""
    # Use in-memory SQLite for testing
    engine = create_engine(
        "sqlite:///test_tour.db",
        connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session
    
    # Clean up
    try:
        os.unlink("test_tour.db")
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
def sample_tour_template_data():
    """Sample tour template data for testing"""
    return {
        "title": "Sahara Desert Adventure",
        "description": "3-day desert tour with camel trekking and camping",
        "short_description": "Desert adventure with camel trekking",
        "category": "Desert",
        "duration_days": 3,
        "difficulty_level": "Moderate",
        "default_language": "French",
        "default_region": "Merzouga",
        "starting_location": "Marrakech",
        "ending_location": "Merzouga",
        "min_participants": 2,
        "max_participants": 12,
        "base_price": 350.0,
        "highlights": ["Camel trekking", "Desert camping", "Sunset viewing"],
        "inclusions": ["Transportation", "Meals", "Accommodation"],
        "exclusions": ["Personal expenses", "Tips"],
        "requirements": "Good physical condition required"
    }


@pytest.fixture
def sample_tour_instance_data():
    """Sample tour instance data for testing"""
    return {
        "title": "Sahara Desert Adventure - March 2024",
        "start_date": "2024-03-15",
        "end_date": "2024-03-17",
        "participant_count": 4,
        "lead_passenger_name": "Ahmed Hassan",
        "language": "French",
        "special_requirements": "Vegetarian meals for 2 participants",
        "participant_details": {
            "participants": [
                {"name": "Ahmed Hassan", "age": 35, "dietary": "vegetarian"},
                {"name": "Fatima Hassan", "age": 32, "dietary": "vegetarian"},
                {"name": "John Smith", "age": 28, "dietary": "none"},
                {"name": "Jane Smith", "age": 26, "dietary": "none"}
            ]
        }
    }


@pytest.fixture
def sample_itinerary_item_data():
    """Sample itinerary item data for testing"""
    return {
        "day_number": 1,
        "start_time": "09:00",
        "end_time": "12:00",
        "duration_minutes": 180,
        "activity_type": "Visit",
        "title": "Ait Benhaddou Kasbah",
        "description": "Visit the UNESCO World Heritage site",
        "location_name": "Ait Benhaddou",
        "address": "Ait Benhaddou, Morocco",
        "coordinates": (31.047043, -7.129532),
        "notes": "Bring comfortable walking shoes",
        "cost": 50.0,
        "is_mandatory": True
    }


@pytest.fixture
def sample_incident_data():
    """Sample incident data for testing"""
    return {
        "incident_type": "Delay",
        "severity": "Medium",
        "title": "Traffic delay on route",
        "description": "Heavy traffic causing 30-minute delay",
        "location": "Highway A7 near Casablanca",
        "day_number": 1,
        "affected_participants": 4,
        "estimated_delay_minutes": 30,
        "financial_impact": 0.0
    }


@pytest.fixture
def create_test_tour_template(session):
    """Factory function to create test tour templates"""
    def _create_template(**kwargs):
        default_data = {
            "title": f"Test Tour {uuid.uuid4().hex[:8]}",
            "description": "Test tour description",
            "category": TourCategory.CULTURAL,
            "duration_days": 3,
            "difficulty_level": DifficultyLevel.EASY,
            "default_language": "French",
            "default_region": "Marrakech",
            "min_participants": 2,
            "max_participants": 10,
            "base_price": 200.0
        }
        default_data.update(kwargs)
        
        template = TourTemplate(**default_data)
        session.add(template)
        session.commit()
        session.refresh(template)
        return template
    
    return _create_template


@pytest.fixture
def create_test_tour_instance(session):
    """Factory function to create test tour instances"""
    def _create_instance(template_id, **kwargs):
        default_data = {
            "template_id": template_id,
            "booking_id": uuid.uuid4(),
            "customer_id": uuid.uuid4(),
            "title": "Test Tour Instance",
            "start_date": date.today() + timedelta(days=7),
            "end_date": date.today() + timedelta(days=9),
            "participant_count": 4,
            "lead_passenger_name": "Test Customer",
            "language": "French"
        }
        default_data.update(kwargs)
        
        instance = TourInstance(**default_data)
        session.add(instance)
        session.commit()
        session.refresh(instance)
        return instance
    
    return _create_instance


@pytest.fixture
def create_test_itinerary_item(session):
    """Factory function to create test itinerary items"""
    def _create_item(tour_instance_id, **kwargs):
        default_data = {
            "tour_instance_id": tour_instance_id,
            "day_number": 1,
            "start_time": time(9, 0),
            "end_time": time(12, 0),
            "activity_type": ActivityType.VISIT,
            "title": "Test Activity",
            "location_name": "Test Location"
        }
        default_data.update(kwargs)
        
        item = ItineraryItem(**default_data)
        session.add(item)
        session.commit()
        session.refresh(item)
        return item
    
    return _create_item


@pytest.fixture
def create_test_incident(session):
    """Factory function to create test incidents"""
    def _create_incident(tour_instance_id, **kwargs):
        default_data = {
            "tour_instance_id": tour_instance_id,
            "reporter_id": uuid.uuid4(),
            "incident_type": IncidentType.DELAY,
            "severity": SeverityLevel.MEDIUM,
            "title": "Test Incident",
            "description": "Test incident description"
        }
        default_data.update(kwargs)
        
        incident = Incident(**default_data)
        session.add(incident)
        session.commit()
        session.refresh(incident)
        return incident
    
    return _create_incident


@pytest.fixture
def mock_auth_user():
    """Mock authenticated user for testing"""
    from utils.auth import CurrentUser
    return CurrentUser(
        user_id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test User",
        permissions=["tours:create:*", "tours:read:*", "tours:update:*", "tours:delete:*"]
    )
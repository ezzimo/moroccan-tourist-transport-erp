"""
Test configuration and fixtures for CRM microservice
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from main import app
from database import get_session, get_redis
from config import settings
from models.customer import Customer, ContactType, LoyaltyStatus
from models.interaction import Interaction, ChannelType
from models.feedback import Feedback, ServiceType
from models.segment import Segment
import fakeredis
import tempfile
import os
import uuid
from datetime import datetime


# Test database engine
@pytest.fixture(name="session")
def session_fixture():
    """Create test database session"""
    # Use in-memory SQLite for testing
    engine = create_engine(
        "sqlite:///test_crm.db",
        connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session
    
    # Clean up
    try:
        os.unlink("test_crm.db")
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
def sample_customer_data():
    """Sample customer data for testing"""
    return {
        "full_name": "Ahmed Hassan",
        "contact_type": "Individual",
        "email": "ahmed.hassan@example.com",
        "phone": "+212600123456",
        "nationality": "Moroccan",
        "region": "Casablanca",
        "preferred_language": "French",
        "tags": ["VIP", "Repeat Customer"]
    }


@pytest.fixture
def sample_corporate_customer_data():
    """Sample corporate customer data for testing"""
    return {
        "company_name": "Atlas Tours Morocco",
        "contact_type": "Corporate",
        "email": "contact@atlastours.ma",
        "phone": "+212522123456",
        "nationality": "Moroccan",
        "region": "Marrakech",
        "preferred_language": "Arabic",
        "tags": ["Corporate", "High Volume"]
    }


@pytest.fixture
def sample_interaction_data():
    """Sample interaction data for testing"""
    return {
        "channel": "email",
        "subject": "Booking inquiry",
        "summary": "Customer inquired about desert tour packages",
        "duration_minutes": 15,
        "follow_up_required": True
    }


@pytest.fixture
def sample_feedback_data():
    """Sample feedback data for testing"""
    return {
        "service_type": "Tour",
        "rating": 5,
        "comments": "Excellent service and professional guide",
        "source": "web"
    }


@pytest.fixture
def sample_segment_data():
    """Sample segment data for testing"""
    return {
        "name": "VIP Customers",
        "description": "High-value customers with VIP status",
        "criteria": {
            "loyalty_status": ["Gold", "Platinum", "VIP"],
            "tags": ["VIP"]
        }
    }


@pytest.fixture
def create_test_customer(session):
    """Factory function to create test customers"""
    def _create_customer(**kwargs):
        default_data = {
            "full_name": "Test Customer",
            "contact_type": ContactType.INDIVIDUAL,
            "email": f"test{uuid.uuid4().hex[:8]}@example.com",
            "phone": "+212600000000",
            "region": "Casablanca",
            "preferred_language": "French"
        }
        default_data.update(kwargs)
        
        customer = Customer(**default_data)
        session.add(customer)
        session.commit()
        session.refresh(customer)
        return customer
    
    return _create_customer


@pytest.fixture
def create_test_interaction(session):
    """Factory function to create test interactions"""
    def _create_interaction(customer_id, **kwargs):
        default_data = {
            "customer_id": customer_id,
            "channel": ChannelType.EMAIL,
            "summary": "Test interaction",
            "timestamp": datetime.utcnow()
        }
        default_data.update(kwargs)
        
        interaction = Interaction(**default_data)
        session.add(interaction)
        session.commit()
        session.refresh(interaction)
        return interaction
    
    return _create_interaction


@pytest.fixture
def create_test_feedback(session):
    """Factory function to create test feedback"""
    def _create_feedback(customer_id, **kwargs):
        default_data = {
            "customer_id": customer_id,
            "service_type": ServiceType.TOUR,
            "rating": 4,
            "comments": "Good service",
            "submitted_at": datetime.utcnow()
        }
        default_data.update(kwargs)
        
        feedback = Feedback(**default_data)
        session.add(feedback)
        session.commit()
        session.refresh(feedback)
        return feedback
    
    return _create_feedback


@pytest.fixture
def mock_auth_user():
    """Mock authenticated user for testing"""
    from utils.auth import CurrentUser
    return CurrentUser(
        user_id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test User",
        permissions=["crm:create:*", "crm:read:*", "crm:update:*", "crm:delete:*"]
    )
"""
Test configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from main import app
from database import get_session, get_redis
from test_database import get_test_session, get_test_redis, create_test_db_and_tables, test_engine
from test_config import test_settings
import fakeredis
import tempfile
import os


# Test database engine
@pytest.fixture(name="session")
def session_fixture():
    """Create test database session"""
    # Create tables
    create_test_db_and_tables()
    
    with Session(test_engine) as session:
        yield session
    
    # Clean up
    if os.path.exists("test_auth.db"):
        os.unlink("test_auth.db")


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
def sample_user_data():
    """Sample user data for testing"""
    return {
        "full_name": "Ahmed Hassan",
        "email": "ahmed@example.com",
        "phone": "+212600123456",
        "password": "SecurePassword123!"
    }


@pytest.fixture
def sample_role_data():
    """Sample role data for testing"""
    return {
        "name": "transport_manager",
        "description": "Manager for transport operations"
    }


@pytest.fixture
def sample_permission_data():
    """Sample permission data for testing"""
    return {
        "service_name": "vehicles",
        "action": "read",
        "resource": "all"
    }
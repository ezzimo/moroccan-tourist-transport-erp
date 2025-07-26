"""
Test configuration and fixtures for driver service
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient
from httpx import AsyncClient
import redis.asyncio as redis
from unittest.mock import AsyncMock, MagicMock

from main import app
from database import get_session, get_redis
from models.driver import Driver, DriverStatus, LicenseType, EmploymentType, Gender
from models.driver_assignment import DriverAssignment, AssignmentStatus
from models.driver_training import DriverTrainingRecord, TrainingType, TrainingStatus
from models.driver_incident import DriverIncident, IncidentType, IncidentSeverity, IncidentStatus
from models.driver_document import DriverDocument, DocumentType, DocumentStatus
from utils.auth import CurrentUser
from datetime import date, datetime, timedelta
import uuid


# Test database URL
TEST_DATABASE_URL = "sqlite:///./test_driver.db"


@pytest.fixture(name="engine")
def engine_fixture():
    """Create test database engine"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    """Create test database session"""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="redis_mock")
def redis_mock_fixture():
    """Create mock Redis client"""
    mock_redis = AsyncMock(spec=redis.Redis)
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.setex.return_value = True
    mock_redis.delete.return_value = 1
    mock_redis.incr.return_value = 1
    return mock_redis


@pytest.fixture(name="client")
def client_fixture(session: Session, redis_mock):
    """Create test client with dependency overrides"""
    def get_session_override():
        return session

    def get_redis_override():
        return redis_mock

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_redis] = get_redis_override
    
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="async_client")
async def async_client_fixture(session: Session, redis_mock) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client"""
    def get_session_override():
        return session

    def get_redis_override():
        return redis_mock

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_redis] = get_redis_override
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture(name="current_user")
def current_user_fixture():
    """Create mock current user"""
    return CurrentUser(
        user_id=uuid.uuid4(),
        email="admin@example.com",
        full_name="Test Admin",
        permissions=[
            "drivers:create:all",
            "drivers:read:all",
            "drivers:update:all",
            "drivers:delete:all",
            "assignments:create:all",
            "assignments:read:all",
            "assignments:update:all",
            "assignments:delete:all",
            "training:create:all",
            "training:read:all",
            "training:update:all",
            "training:delete:all",
            "incidents:create:all",
            "incidents:read:all",
            "incidents:update:all",
            "incidents:delete:all"
        ]
    )


@pytest.fixture(name="sample_driver")
def sample_driver_fixture(session: Session) -> Driver:
    """Create sample driver for testing"""
    driver = Driver(
        full_name="Ahmed Hassan",
        date_of_birth=date(1985, 5, 15),
        gender=Gender.MALE,
        nationality="Moroccan",
        national_id="AB123456",
        phone="+212-123-456-789",
        email="ahmed.hassan@example.com",
        address="123 Main St, Casablanca",
        emergency_contact_name="Fatima Hassan",
        emergency_contact_phone="+212-987-654-321",
        employee_id="EMP001",
        employment_type=EmploymentType.PERMANENT,
        hire_date=date(2020, 1, 15),
        license_number="DL123456789",
        license_type=LicenseType.CATEGORY_D,
        license_issue_date=date(2019, 12, 1),
        license_expiry_date=date(2025, 12, 1),
        license_issuing_authority="Morocco Transport Authority",
        languages_spoken='["Arabic", "French", "English"]',
        tour_guide_certified=True,
        first_aid_certified=True,
        health_certificate_expiry=date(2024, 6, 1),
        status=DriverStatus.ACTIVE,
        performance_rating=4.5,
        total_tours_completed=150,
        total_incidents=2
    )
    
    session.add(driver)
    session.commit()
    session.refresh(driver)
    return driver


@pytest.fixture(name="sample_assignment")
def sample_assignment_fixture(session: Session, sample_driver: Driver) -> DriverAssignment:
    """Create sample assignment for testing"""
    assignment = DriverAssignment(
        driver_id=sample_driver.id,
        tour_instance_id=uuid.uuid4(),
        vehicle_id=uuid.uuid4(),
        start_date=date.today() + timedelta(days=1),
        end_date=date.today() + timedelta(days=3),
        tour_title="Marrakech City Tour",
        pickup_location="Hotel Atlas",
        dropoff_location="Hotel Atlas",
        estimated_duration_hours=8,
        special_instructions="VIP group, English speaking guide required",
        assigned_by=uuid.uuid4(),
        status=AssignmentStatus.ASSIGNED
    )
    
    session.add(assignment)
    session.commit()
    session.refresh(assignment)
    return assignment


@pytest.fixture(name="sample_training")
def sample_training_fixture(session: Session, sample_driver: Driver) -> DriverTrainingRecord:
    """Create sample training record for testing"""
    training = DriverTrainingRecord(
        driver_id=sample_driver.id,
        training_type=TrainingType.FIRST_AID,
        training_title="First Aid Certification",
        description="Basic first aid training for tourist transport drivers",
        scheduled_date=date.today() + timedelta(days=7),
        trainer_name="Dr. Khalid Benali",
        training_provider="Morocco Safety Institute",
        location="Casablanca Training Center",
        duration_hours=8.0,
        pass_score=70.0,
        cost=500.0,
        currency="MAD",
        mandatory=True,
        status=TrainingStatus.SCHEDULED
    )
    
    session.add(training)
    session.commit()
    session.refresh(training)
    return training


@pytest.fixture(name="sample_incident")
def sample_incident_fixture(session: Session, sample_driver: Driver) -> DriverIncident:
    """Create sample incident for testing"""
    incident = DriverIncident(
        driver_id=sample_driver.id,
        assignment_id=uuid.uuid4(),
        incident_type=IncidentType.DELAY,
        severity=IncidentSeverity.MINOR,
        title="Traffic Delay",
        description="Delayed arrival due to unexpected traffic jam on highway",
        incident_date=date.today(),
        incident_time=datetime.now(),
        location="Highway A7, Casablanca",
        reported_by=uuid.uuid4(),
        customer_involved=False,
        estimated_cost=0.0,
        status=IncidentStatus.REPORTED
    )
    
    session.add(incident)
    session.commit()
    session.refresh(incident)
    return incident


@pytest.fixture(name="sample_document")
def sample_document_fixture(session: Session, sample_driver: Driver) -> DriverDocument:
    """Create sample document for testing"""
    document = DriverDocument(
        driver_id=sample_driver.id,
        document_type=DocumentType.DRIVING_LICENSE,
        title="Driving License",
        description="Current driving license document",
        file_name="license_ahmed_hassan.pdf",
        file_path="/uploads/documents/license_ahmed_hassan.pdf",
        file_size=1024000,
        mime_type="application/pdf",
        document_number="DL123456789",
        issue_date=date(2019, 12, 1),
        expiry_date=date(2025, 12, 1),
        issuing_authority="Morocco Transport Authority",
        status=DocumentStatus.APPROVED,
        uploaded_by=uuid.uuid4(),
        approved_by=uuid.uuid4(),
        approved_at=datetime.now()
    )
    
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


@pytest.fixture(name="auth_headers")
def auth_headers_fixture():
    """Create authentication headers for testing"""
    return {
        "Authorization": "Bearer test-jwt-token",
        "Content-Type": "application/json"
    }


@pytest.fixture(name="mock_notification_service")
def mock_notification_service_fixture():
    """Mock notification service"""
    mock = AsyncMock()
    mock.send_notification.return_value = True
    mock.send_bulk_notification.return_value = {"user1": True, "user2": True}
    return mock


@pytest.fixture(name="mock_file_upload")
def mock_file_upload_fixture():
    """Mock file upload handler"""
    mock = MagicMock()
    mock.validate_file.return_value = {
        "original_filename": "test_document.pdf",
        "file_extension": ".pdf",
        "mime_type": "application/pdf",
        "file_size": 1024000,
        "file_hash": "abc123def456",
        "content": b"fake pdf content"
    }
    mock.save_file.return_value = {
        "file_id": str(uuid.uuid4()),
        "file_path": "/uploads/test_document.pdf",
        "file_name": "test_document.pdf",
        "original_filename": "test_document.pdf",
        "file_size": 1024000,
        "mime_type": "application/pdf",
        "file_hash": "abc123def456"
    }
    return mock


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Test data factories

def create_driver_data(**overrides):
    """Create driver test data"""
    default_data = {
        "full_name": "Test Driver",
        "date_of_birth": "1985-01-01",
        "gender": "Male",
        "nationality": "Moroccan",
        "national_id": "AB123456",
        "phone": "+212-123-456-789",
        "email": "test@example.com",
        "employment_type": "Permanent",
        "hire_date": "2020-01-01",
        "license_number": "DL123456789",
        "license_type": "Category D",
        "license_issue_date": "2019-01-01",
        "license_expiry_date": "2025-01-01",
        "languages_spoken": ["Arabic", "French", "English"],
        "tour_guide_certified": True,
        "first_aid_certified": True
    }
    default_data.update(overrides)
    return default_data


def create_assignment_data(driver_id: uuid.UUID, **overrides):
    """Create assignment test data"""
    default_data = {
        "driver_id": str(driver_id),
        "tour_instance_id": str(uuid.uuid4()),
        "start_date": (date.today() + timedelta(days=1)).isoformat(),
        "end_date": (date.today() + timedelta(days=3)).isoformat(),
        "tour_title": "Test Tour",
        "pickup_location": "Test Hotel",
        "dropoff_location": "Test Hotel"
    }
    default_data.update(overrides)
    return default_data


def create_training_data(driver_id: uuid.UUID, **overrides):
    """Create training test data"""
    default_data = {
        "driver_id": str(driver_id),
        "training_type": "First Aid",
        "training_title": "First Aid Certification",
        "scheduled_date": (date.today() + timedelta(days=7)).isoformat(),
        "trainer_name": "Test Trainer",
        "duration_hours": 8.0,
        "mandatory": True
    }
    default_data.update(overrides)
    return default_data


def create_incident_data(driver_id: uuid.UUID, **overrides):
    """Create incident test data"""
    default_data = {
        "driver_id": str(driver_id),
        "incident_type": "Delay",
        "severity": "Minor",
        "title": "Test Incident",
        "description": "Test incident description",
        "incident_date": date.today().isoformat(),
        "location": "Test Location"
    }
    default_data.update(overrides)
    return default_data


# Utility functions for tests

def assert_driver_response(response_data: dict, expected_driver: Driver):
    """Assert driver response matches expected driver"""
    assert response_data["id"] == str(expected_driver.id)
    assert response_data["full_name"] == expected_driver.full_name
    assert response_data["email"] == expected_driver.email
    assert response_data["phone"] == expected_driver.phone
    assert response_data["license_number"] == expected_driver.license_number
    assert response_data["status"] == expected_driver.status


def assert_assignment_response(response_data: dict, expected_assignment: DriverAssignment):
    """Assert assignment response matches expected assignment"""
    assert response_data["id"] == str(expected_assignment.id)
    assert response_data["driver_id"] == str(expected_assignment.driver_id)
    assert response_data["tour_instance_id"] == str(expected_assignment.tour_instance_id)
    assert response_data["status"] == expected_assignment.status
    assert response_data["tour_title"] == expected_assignment.tour_title


def assert_training_response(response_data: dict, expected_training: DriverTrainingRecord):
    """Assert training response matches expected training"""
    assert response_data["id"] == str(expected_training.id)
    assert response_data["driver_id"] == str(expected_training.driver_id)
    assert response_data["training_type"] == expected_training.training_type
    assert response_data["training_title"] == expected_training.training_title
    assert response_data["status"] == expected_training.status


def assert_incident_response(response_data: dict, expected_incident: DriverIncident):
    """Assert incident response matches expected incident"""
    assert response_data["id"] == str(expected_incident.id)
    assert response_data["driver_id"] == str(expected_incident.driver_id)
    assert response_data["incident_type"] == expected_incident.incident_type
    assert response_data["severity"] == expected_incident.severity
    assert response_data["title"] == expected_incident.title
    assert response_data["status"] == expected_incident.status
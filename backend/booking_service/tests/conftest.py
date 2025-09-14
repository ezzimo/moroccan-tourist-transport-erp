import sys
import os
# Add the service root to the path to allow direct import of 'config'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import subprocess
import pytest
from unittest.mock import AsyncMock

from fastapi import FastAPI, Depends, HTTPException, Header, APIRouter
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel
from pydantic import BaseModel
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

# --- Client Imports for Mocking & Logic ---
from backend.booking_service.clients.base import IntegrationBadRequest, ExternalServiceError
from backend.booking_service.clients.fleet_client import FleetServiceClient
from backend.booking_service.clients.payment_client import PaymentServiceClient
from backend.booking_service.clients.notification_client import NotificationServiceClient

# --- App Imports ---
from backend.booking_service.models.booking import Booking
from backend.booking_service.models.enums import BookingStatus, PaymentStatus, ServiceType
from backend.booking_service.database import get_session

# 1. --- Database Fixtures & Config ---

TEST_DB_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DB_URL:
    pytest.skip("TEST_DATABASE_URL not set; skipping DB-backed tests.", allow_module_level=True)

@pytest.fixture(scope="session")
def db_url():
    """Returns the test database URL."""
    return TEST_DB_URL

@pytest.fixture(scope="session")
def test_engine(db_url):
    """Creates a SQLAlchemy engine for the test database, for the whole session."""
    engine = create_engine(db_url)
    # The real app does this via alembic, but for tests, a clean slate is good.
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture(scope="session", autouse=True)
def alembic_upgrade_head(db_url):
    """
    Ensures the test database is migrated to the latest version.
    """
    env = {**os.environ, "DATABASE_URL": db_url}
    alembic_config_path = "backend/booking_service/alembic.ini"
    subprocess.run(
        ["alembic", "-c", alembic_config_path, "upgrade", "head"],
        check=True,
        env=env,
    )
    yield

@pytest.fixture()
def session(test_engine):
    """
    Provides a clean, transaction-rolled-back session for each test.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    db_session = Session(bind=connection)

    yield db_session

    db_session.close()
    transaction.rollback()
    connection.close()

# 2. --- Test Application Fixture with custom endpoint ---

class ConfirmAtomicBody(BaseModel):
    payment_reference: str
    vehicle_id: uuid.UUID
    driver_id: uuid.UUID

async def confirm_atomic_test_logic(
    booking_id: uuid.UUID,
    body: ConfirmAtomicBody,
    idempotency_key: Optional[str] = Header(None),
    db: Session = Depends(get_session)
):
    fleet_client = FleetServiceClient(base_url="http://fleet-service")
    payment_client = PaymentServiceClient(base_url="http://payment-service", api_key="test")
    notification_client = NotificationServiceClient(base_url="http://notification-service")

    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status != BookingStatus.PENDING:
        raise HTTPException(status_code=409, detail="Booking not in pending state")

    try:
        await fleet_client.reserve_vehicle(
            vehicle_id=body.vehicle_id, booking_id=booking.id, idempotency_key=idempotency_key
        )
    except Exception as e:
        raise HTTPException(status_code=409, detail=f"Fleet reservation failed: {e}")

    try:
        await payment_client.confirm_payment(
            reference=body.payment_reference,
            expected_amount=booking.total_price,
            currency=booking.currency,
            idempotency_key=idempotency_key,
        )
    except Exception as e:
        await fleet_client.release_vehicle(
            vehicle_id=body.vehicle_id, booking_id=booking.id
        )
        if isinstance(e, IntegrationBadRequest):
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=500, detail=f"Payment failed, compensation run: {e}")

    booking.status = BookingStatus.CONFIRMED
    booking.payment_status = PaymentStatus.PAID
    booking.vehicle_id = body.vehicle_id
    booking.driver_id = body.driver_id
    booking.confirmed_at = datetime.now(timezone.utc)

    notification_status = "PENDING"
    try:
        await notification_client.send_booking_confirmation_email(
            recipient_email=booking.lead_passenger_email,
            booking_payload={"id": str(booking.id), "status": "confirmed"}
        )
        notification_status = "SENT"
    except Exception:
        notification_status = "FAILED"

    db.add(booking)
    db.commit()
    db.refresh(booking)

    response_data = booking.model_dump()
    response_data["notification_status"] = notification_status
    return response_data

@pytest.fixture(scope="session")
def app(db_url):
    from backend.booking_service.main import app as main_app

    def get_test_session_override():
        engine = create_engine(db_url)
        with Session(engine) as s:
            yield s

    main_app.dependency_overrides[get_session] = get_test_session_override

    test_router = APIRouter()
    test_router.add_api_route(
        "/bookings/{booking_id}/confirm_atomic",
        confirm_atomic_test_logic,
        methods=["POST"],
        response_model=None, # Use dict for flexibility
    )
    main_app.include_router(test_router)

    return main_app

@pytest.fixture(scope="module")
def client(app):
    with TestClient(app) as c:
        yield c

# 3. --- Mock Client Fixtures ---

@pytest.fixture
def mock_fleet_ok(monkeypatch):
    mock_reserve = AsyncMock(return_value={"reserved": True})
    mock_release = AsyncMock(return_value=True)
    monkeypatch.setattr(FleetServiceClient, "reserve_vehicle", mock_reserve)
    monkeypatch.setattr(FleetServiceClient, "release_vehicle", mock_release)
    return {"reserve": mock_reserve, "release": mock_release}

@pytest.fixture
def mock_payment_ok(monkeypatch):
    mock_confirm = AsyncMock(return_value={"status": "succeeded"})
    monkeypatch.setattr(PaymentServiceClient, "confirm_payment", mock_confirm)
    return mock_confirm

@pytest.fixture
def mock_payment_fail(monkeypatch):
    mock_confirm = AsyncMock(side_effect=IntegrationBadRequest("Payment provider declined"))
    monkeypatch.setattr(PaymentServiceClient, "confirm_payment", mock_confirm)
    return mock_confirm

@pytest.fixture
def mock_note_fail(monkeypatch):
    mock_send = AsyncMock(side_effect=ExternalServiceError("SMTP server down"))
    monkeypatch.setattr(NotificationServiceClient, "send_booking_confirmation_email", mock_send)
    return mock_send

# 4. --- Test Helpers ---

@pytest.fixture
def utc_ts_factory():
    def _utc_ts(hour: int, minute: int):
        return datetime(2025, 9, 5, hour, minute, 0, tzinfo=timezone.utc)
    return _utc_ts

@pytest.fixture
def make_booking(session):
    def _make_booking(**kwargs):
        defaults = {
            "customer_id": uuid.uuid4(),
            "status": BookingStatus.PENDING,
            "start_time": datetime(2025, 9, 5, 10, 0, tzinfo=timezone.utc),
            "end_time": datetime(2025, 9, 5, 11, 0, tzinfo=timezone.utc),
            "total_price": Decimal("100.00"),
            "currency": "MAD",
            "lead_passenger_email": "test@example.com",
            "service_type": ServiceType.TRANSFER,
            "vehicle_type_requested": "Sedan",
        }
        booking_data = {**defaults, **kwargs}
        if isinstance(booking_data.get("status"), str):
            booking_data["status"] = BookingStatus(booking_data["status"])
        booking = Booking(**booking_data)
        session.add(booking)
        session.commit()
        session.refresh(booking)
        return booking
    return _make_booking

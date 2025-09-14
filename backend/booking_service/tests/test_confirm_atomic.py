import pytest
import uuid
from sqlmodel import Session
from fastapi.testclient import TestClient

from backend.booking_service.models.booking import Booking, BookingStatus

# Mark all tests in this module as database-dependent
pytestmark = pytest.mark.db

def test_confirm_atomic_happy_path(
    client: TestClient, session: Session, make_booking, mock_fleet_ok, mock_payment_ok
):
    """
    Tests the full happy path for the confirm_atomic flow:
    - Vehicle reserved
    - Payment confirmed
    - Booking status updated to 'confirmed'
    - Notification sent
    - Idempotency key passed to downstream services
    """
    # Arrange
    booking = make_booking(status='pending')
    vehicle_id = uuid.uuid4()
    driver_id = uuid.uuid4()
    idempotency_key = f"happy-{uuid.uuid4()}"

    # Act
    response = client.post(
        f"/api/v1/bookings/{booking.id}/confirm_atomic",
        json={
            "payment_reference": "test_ref_123",
            "vehicle_id": str(vehicle_id),
            "driver_id": str(driver_id),
        },
        headers={"Idempotency-Key": idempotency_key},
    )

    # Assert Response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "confirmed"
    assert response_data["payment_status"] == "paid"
    assert response_data["vehicle_id"] == str(vehicle_id)
    assert response_data["driver_id"] == str(driver_id)
    assert response_data["notification_status"] == "SENT"

    # Assert Database State
    db_booking = session.get(Booking, booking.id)
    assert db_booking.status == BookingStatus.CONFIRMED
    assert db_booking.payment_status == PaymentStatus.PAID

    # Assert Mocks
    mock_fleet_ok["reserve"].assert_called_once()
    mock_payment_ok.assert_called_once()

    # Assert Idempotency Key passthrough
    assert mock_fleet_ok["reserve"].call_args.kwargs["idempotency_key"] == idempotency_key
    assert mock_payment_ok.call_args.kwargs["idempotency_key"] == idempotency_key

def test_confirm_atomic_payment_failure_triggers_compensation(
    client: TestClient, session: Session, make_booking, mock_fleet_ok, mock_payment_fail
):
    """
    Tests the compensation flow when payment fails:
    - Fleet reservation is made
    - Payment confirmation fails
    - Fleet reservation is released (compensated)
    - Booking status remains 'pending'
    - A 400-level error is returned
    """
    # Arrange
    booking = make_booking(status='pending')
    vehicle_id = uuid.uuid4()

    # Act
    response = client.post(
        f"/api/v1/bookings/{booking.id}/confirm_atomic",
        json={
            "payment_reference": "ref_fail",
            "vehicle_id": str(vehicle_id),
            "driver_id": str(uuid.uuid4()),
        },
    )

    # Assert Response
    assert response.status_code == 400
    assert "Payment provider declined" in response.json()["detail"]

    # Assert Database State
    db_booking = session.get(Booking, booking.id)
    assert db_booking.status == BookingStatus.PENDING # Should not have changed

    # Assert Mocks
    mock_fleet_ok["reserve"].assert_called_once()
    mock_payment_fail.assert_called_once()
    mock_fleet_ok["release"].assert_called_once_with(
        vehicle_id=vehicle_id, booking_id=booking.id
    )

def test_confirm_atomic_tolerates_notification_failure(
    client: TestClient, session: Session, make_booking, mock_fleet_ok, mock_payment_ok, mock_note_fail
):
    """
    Tests that a failure in the notification service does not roll back
    the booking confirmation.
    """
    # Arrange
    booking = make_booking(status='pending')
    vehicle_id = uuid.uuid4()

    # Act
    response = client.post(
        f"/api/v1/bookings/{booking.id}/confirm_atomic",
        json={
            "payment_reference": "ref_note_fail",
            "vehicle_id": str(vehicle_id),
            "driver_id": str(uuid.uuid4()),
        },
    )

    # Assert Response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "confirmed"
    assert response_data["notification_status"] == "FAILED"

    # Assert Database State
    db_booking = session.get(Booking, booking.id)
    assert db_booking.status == BookingStatus.CONFIRMED

    # Assert Mocks
    mock_fleet_ok["reserve"].assert_called_once()
    mock_payment_ok.assert_called_once()
    mock_note_fail.assert_called_once()

def test_confirm_atomic_validation_error(client: TestClient, make_booking):
    """
    Tests that the endpoint returns a 422 for malformed input.
    """
    # Arrange
    booking = make_booking(status='pending')

    # Act
    response = client.post(
        f"/api/v1/bookings/{booking.id}/confirm_atomic",
        json={
            "payment_reference": "ref_validation_fail",
            "vehicle_id": "not-a-uuid", # Invalid UUID
            "driver_id": str(uuid.uuid4()),
        },
    )

    # Assert
    assert response.status_code == 422 # Unprocessable Entity
    assert "validation_error" in response.text

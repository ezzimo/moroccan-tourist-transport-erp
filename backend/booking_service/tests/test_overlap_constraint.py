import pytest
import uuid
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

# Mark all tests in this module as database-dependent
pytestmark = pytest.mark.db

def test_overlap_constraint_rejects_overlapping_bookings_same_vehicle(
    session: Session, make_booking, utc_ts_factory
):
    """
    Tests that the DB constraint 'bookings_no_overlap' prevents inserting
    a booking that overlaps with an existing one for the same vehicle.
    """
    vehicle_id = uuid.uuid4()
    t = utc_ts_factory

    # Arrange: Create an initial booking
    make_booking(
        vehicle_id=vehicle_id,
        start_time=t(10, 0),
        end_time=t(11, 0),
        status='pending'
    )

    # Act & Assert: Try to create an overlapping booking
    with pytest.raises(IntegrityError) as ei:
        make_booking(
            vehicle_id=vehicle_id,
            start_time=t(10, 30),
            end_time=t(11, 30),
            status='pending'
        )

    # Assert that the correct constraint was violated, as per user snippet
    assert getattr(ei.value.orig, "diag", None), "Error did not have 'diag' attribute"
    assert ei.value.orig.diag.constraint_name == "bookings_no_overlap"

def test_overlap_constraint_allows_back_to_back_bookings(
    session: Session, make_booking, utc_ts_factory
):
    """
    Tests that the constraint allows bookings that are perfectly back-to-back.
    """
    vehicle_id = uuid.uuid4()
    t = utc_ts_factory

    # Arrange
    make_booking(
        vehicle_id=vehicle_id,
        start_time=t(10, 0),
        end_time=t(11, 0),
        status='confirmed'
    )

    # Act & Assert: No error should be raised
    try:
        make_booking(
            vehicle_id=vehicle_id,
            start_time=t(11, 0),
            end_time=t(12, 0),
            status='pending'
        )
    except IntegrityError:
        pytest.fail("IntegrityError was raised for a valid back-to-back booking.")

def test_overlap_constraint_allows_overlap_for_different_vehicles(
    session: Session, make_booking, utc_ts_factory
):
    """
    Tests that the constraint allows overlapping bookings on different vehicles.
    """
    t = utc_ts_factory

    # Arrange
    make_booking(
        vehicle_id=uuid.uuid4(),
        start_time=t(10, 0),
        end_time=t(11, 0),
    )

    # Act & Assert: No error should be raised
    try:
        make_booking(
            vehicle_id=uuid.uuid4(), # A different vehicle ID
            start_time=t(10, 30),
            end_time=t(11, 30),
        )
    except IntegrityError:
        pytest.fail("IntegrityError was raised for an overlap on different vehicles.")

def test_overlap_constraint_ignores_non_constrained_statuses(
    session: Session, make_booking, utc_ts_factory
):
    """
    Tests that the constraint's WHERE clause correctly ignores rows with
    non-constrained statuses like 'cancelled' or 'expired'.
    """
    vehicle_id = uuid.uuid4()
    t = utc_ts_factory

    # Arrange: Create a cancelled booking
    make_booking(
        vehicle_id=vehicle_id,
        start_time=t(10, 0),
        end_time=t(11, 0),
        status='cancelled' # This status should be ignored by the constraint
    )

    # Act & Assert: Creating an overlapping booking should succeed
    try:
        make_booking(
            vehicle_id=vehicle_id,
            start_time=t(10, 30),
            end_time=t(11, 30),
            status='pending'
        )
    except IntegrityError:
        pytest.fail("IntegrityError was raised despite the first booking being cancelled.")

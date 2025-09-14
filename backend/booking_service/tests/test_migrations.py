import pytest
from sqlalchemy import inspect, text
from sqlmodel import Session

# Mark all tests in this module as database-dependent
pytestmark = pytest.mark.db

def test_phase1_schema_at_head(session: Session, alembic_upgrade_head):
    """
    Tests that after running migrations, the 'bookings' table has the expected
    Phase-1 columns and the exclusion constraint.
    """
    inspector = inspect(session.get_bind())
    columns = [col['name'] for col in inspector.get_columns('bookings')]

    # 1. Assert that all required Phase-1 columns exist
    expected_columns = [
        'start_time',
        'end_time',
        'vehicle_id',
        'driver_id',
        'vehicle_type_requested',
        'pickup_location_text',
        'pickup_location_coords',
        'dropoff_location_text',
        'dropoff_location_coords',
        'estimated_duration_minutes',
        'estimated_distance_km',
        'booking_source',
        'agent_id',
        'price_snapshot',
        'payment_provider',
    ]

    for col in expected_columns:
        assert col in columns, f"Column '{col}' not found in 'bookings' table"

    # 2. Assert that the exclusion constraint exists using the provided SQL snippet
    constraint_query = text(
        "SELECT conname FROM pg_constraint WHERE conname = 'bookings_no_overlap'"
    )
    result = session.exec(constraint_query).first()
    assert result is not None, "Exclusion constraint 'bookings_no_overlap' not found"
    assert result[0] == 'bookings_no_overlap'

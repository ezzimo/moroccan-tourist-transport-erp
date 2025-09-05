"""Add phase-1 operational fields to bookings

Revision ID: 75437a4bf26b
Revises: 12ee15ddc189
Create Date: 2025-09-03 19:14:26.123456

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "75437a4bf26b"
down_revision = "12ee15ddc189"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("bookings", sa.Column("start_time", sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column("bookings", sa.Column("end_time", sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column("bookings", sa.Column("vehicle_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("bookings", sa.Column("driver_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("bookings", sa.Column("vehicle_type_requested", sa.String(length=100), nullable=True))
    op.add_column("bookings", sa.Column("pickup_location_text", sa.String(length=500), nullable=True))
    op.add_column("bookings", sa.Column("pickup_location_coords", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("bookings", sa.Column("dropoff_location_text", sa.String(length=500), nullable=True))
    op.add_column("bookings", sa.Column("dropoff_location_coords", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("bookings", sa.Column("estimated_duration_minutes", sa.Integer(), nullable=True))
    op.add_column("bookings", sa.Column("estimated_distance_km", sa.Float(), nullable=True))
    op.add_column("bookings", sa.Column("booking_source", sa.String(length=50), server_default="web", nullable=False))
    op.add_column("bookings", sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("bookings", sa.Column("price_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("bookings", sa.Column("payment_provider", sa.String(length=50), nullable=True))

    op.create_index(op.f("ix_bookings_start_time"), "bookings", ["start_time"], unique=False)
    op.create_index(op.f("ix_bookings_vehicle_id"), "bookings", ["vehicle_id"], unique=False)
    op.create_index(op.f("ix_bookings_driver_id"), "bookings", ["driver_id"], unique=False)
    op.create_index(op.f("ix_bookings_booking_source"), "bookings", ["booking_source"], unique=False)

def downgrade():
    op.drop_index(op.f("ix_bookings_booking_source"), table_name="bookings")
    op.drop_index(op.f("ix_bookings_driver_id"), table_name="bookings")
    op.drop_index(op.f("ix_bookings_vehicle_id"), table_name="bookings")
    op.drop_index(op.f("ix_bookings_start_time"), table_name="bookings")

    op.drop_column("bookings", "payment_provider")
    op.drop_column("bookings", "price_snapshot")
    op.drop_column("bookings", "agent_id")
    op.drop_column("bookings", "booking_source")
    op.drop_column("bookings", "estimated_distance_km")
    op.drop_column("bookings", "estimated_duration_minutes")
    op.drop_column("bookings", "dropoff_location_coords")
    op.drop_column("bookings", "dropoff_location_text")
    op.drop_column("bookings", "pickup_location_coords")
    op.drop_column("bookings", "pickup_location_text")
    op.drop_column("bookings", "vehicle_type_requested")
    op.drop_column("bookings", "driver_id")
    op.drop_column("bookings", "vehicle_id")
    op.drop_column("bookings", "end_time")
    op.drop_column("bookings", "start_time")

"""add bookings_no_overlap exclusion constraint

Revision ID: 8df432895bde
Revises: 75437a4bf26b
Create Date: 2025-09-04 02:33:57.801974

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "8df432895bde"
down_revision = "75437a4bf26b"  # BK-003 revision id
branch_labels = None
depends_on = None

def upgrade():
    # 1) Ensure btree_gist (required for '=' with GiST on UUID)
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist;")

    # 2) Add exclusion constraint to prevent overlapping bookings per vehicle
    #    Half-open interval '[)' allows back-to-back bookings.
    op.execute("""
        ALTER TABLE bookings
        ADD CONSTRAINT bookings_no_overlap
        EXCLUDE USING gist (
            vehicle_id WITH =,
            tstzrange(start_time, end_time, '[)') WITH &&
        )
        WHERE (
            status IN ('Pending','Confirmed')
            AND start_time IS NOT NULL
            AND end_time IS NOT NULL
        );
    """)

def downgrade():
    op.execute("ALTER TABLE bookings DROP CONSTRAINT IF EXISTS bookings_no_overlap;")

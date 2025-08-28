"""add 'Pending' to expensestatus

Revision ID: 3cd1a4b3144d
Revises: 26f7e221ee26
Create Date: 2025-08-28 03:27:03.772200

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3cd1a4b3144d'
down_revision: Union[str, Sequence[str], None] = '26f7e221ee26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Works on PG >= 10; safe to re-run
    op.execute("ALTER TYPE expensestatus ADD VALUE IF NOT EXISTS 'Pending'")


def downgrade() -> None:
    """Downgrade schema."""
    pass

"""
ReservationItem model (child in 1:N with Booking).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
import json
import uuid

from sqlalchemy import Column, ForeignKey, Numeric
from sqlalchemy.orm import relationship  # << explicit SA relationship
from sqlmodel import SQLModel, Field, Relationship

from .enums import ItemType

# Only for type-checkers; avoids runtime circular import
if TYPE_CHECKING:
    from .booking import Booking


class ReservationItem(SQLModel, table=True):
    """Reservation item model for booking components"""

    __tablename__ = "reservation_items"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )

    # Foreign Keys
    booking_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("bookings.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )

    # Item Details
    type: Optional[ItemType] = Field(index=True, default=None)
    reference_id: Optional[uuid.UUID] = Field(default=None, index=True)
    name: Optional[str] = Field(max_length=255, default=None)
    description: Optional[str] = Field(default=None, max_length=1000)

    # Quantity and Pricing
    quantity: int = Field(default=1, ge=1)
    unit_price: Optional[Decimal] = Field(
        sa_column=Column(Numeric(10, 2)), default=None
    )
    total_price: Optional[Decimal] = Field(
        sa_column=Column(Numeric(10, 2)), default=None
    )

    # Additional Information
    specifications: Optional[str] = Field(default=None)  # JSON string
    notes: Optional[str] = Field(default=None, max_length=500)

    # Status
    is_confirmed: bool = Field(default=False)
    is_cancelled: bool = Field(default=False)

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # MANY -> ONE: explicitly bind back to Booking
    booking: "Booking" = Relationship(
        sa_relationship=relationship(
            "Booking",
            back_populates="reservation_items",
        )
    )

    # ---------- helpers ----------
    def get_specifications_dict(self) -> dict:
        if not self.specifications:
            return {}
        try:
            return json.loads(self.specifications)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_specifications_dict(self, specs: dict) -> None:
        self.specifications = json.dumps(specs) if specs else None

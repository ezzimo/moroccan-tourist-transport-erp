"""
Reservation item model for booking components
"""

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Numeric
from typing import Optional
from datetime import datetime
from enum import Enum
from decimal import Decimal
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .booking import Booking


class ItemType(str, Enum):
    """Reservation item type enumeration"""

    ACCOMMODATION = "Accommodation"
    TRANSPORT = "Transport"
    ACTIVITY = "Activity"
    GUIDE = "Guide"
    MEAL = "Meal"
    INSURANCE = "Insurance"


class ReservationItem(SQLModel, table=True):
    """Reservation item model for booking components"""

    __tablename__ = "reservation_items"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )

    # Foreign Keys
    booking_id: uuid.UUID = Field(foreign_key="bookings.id", index=True)

    # Item Details
    type: ItemType = Field(index=True)
    reference_id: Optional[uuid.UUID] = Field(
        default=None, index=True
    )  # FK to external service
    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)

    # Quantity and Pricing
    quantity: int = Field(default=1, ge=1)
    unit_price: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    total_price: Decimal = Field(sa_column=Column(Numeric(10, 2)))

    # Additional Information
    specifications: Optional[str] = Field(
        default=None
    )  # JSON string for item-specific data
    notes: Optional[str] = Field(default=None, max_length=500)

    # Status
    is_confirmed: bool = Field(default=False)
    is_cancelled: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    booking: Optional["Booking"] = Relationship(
        back_populates="reservation_items", repr=False
    )

    def get_specifications_dict(self) -> dict:
        """Parse specifications from JSON string"""
        if not self.specifications:
            return {}
        try:
            import json

            return json.loads(self.specifications)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_specifications_dict(self, specs: dict):
        """Set specifications as JSON string"""
        import json

        self.specifications = json.dumps(specs) if specs else None

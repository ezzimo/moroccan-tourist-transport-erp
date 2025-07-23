"""
Define relationships between models after they are all loaded
"""

from sqlmodel import Relationship
from typing import List, Optional
from .booking import Booking
from .reservation_item import ReservationItem


# Add relationships to models after import
def setup_relationships():
    """Setup model relationships after all models are imported"""

    # Add reservation_items relationship to Booking
    Booking.__annotations__["reservation_items"] = List[ReservationItem]
    setattr(
        Booking,
        "reservation_items",
        Relationship(
            back_populates="booking",
            sa_relationship_kwargs={
                "cascade": "all, delete-orphan",
                "lazy": "select",
            },
        ),
    )

    # Add booking relationship to ReservationItem
    ReservationItem.__annotations__["booking"] = Optional[Booking]
    setattr(
        ReservationItem,
        "booking",
        Relationship(
            back_populates="reservation_items",
            sa_relationship_kwargs={"lazy": "select"},
        ),
    )

    # Rebuild models to register the new relationships
    try:
        Booking.model_rebuild()
        ReservationItem.model_rebuild()
    except Exception:
        # Models should still work at runtime even if rebuild fails
        pass

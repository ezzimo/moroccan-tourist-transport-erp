"""
Public model API for the booking service. Import from here in the rest
of the app:

    from models import Booking, ReservationItem, BookingStatus, ...

This layout prevents circular imports while keeping types discoverable.
"""

from .enums import (
    BookingStatus,
    ServiceType,
    PaymentStatus,
    ItemType,
    DiscountType,
    ResourceType,
)

from .booking import Booking
from .reservation_item import ReservationItem
from .pricing_rule import PricingRule
from .availability_slot import AvailabilitySlot

__all__ = [
    # enums
    "BookingStatus",
    "ServiceType",
    "PaymentStatus",
    "ItemType",
    "DiscountType",
    "ResourceType",
    # models
    "Booking",
    "ReservationItem",
    "PricingRule",
    "AvailabilitySlot",
]

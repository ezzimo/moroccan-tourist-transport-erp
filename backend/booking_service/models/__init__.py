"""
Database models for the booking microservice
"""
from .booking import Booking, BookingStatus, ServiceType, PaymentStatus
from .reservation_item import ReservationItem, ItemType
from .pricing_rule import PricingRule, DiscountType
from .availability import AvailabilitySlot

# Setup relationships after all models are imported
from .relationships import setup_relationships
setup_relationships()

__all__ = [
    "Booking", "BookingStatus", "ServiceType", "PaymentStatus",
    "ReservationItem", "ItemType",
    "PricingRule", "DiscountType",
    "AvailabilitySlot"
]
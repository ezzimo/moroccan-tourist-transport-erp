"""Shared enumerations for the booking service models."""

from enum import Enum


class BookingStatus(str, Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    REFUNDED = "Refunded"
    EXPIRED = "Expired"


class ServiceType(str, Enum):
    TOUR = "Tour"
    TRANSFER = "Transfer"
    CUSTOM_PACKAGE = "Custom Package"
    ACCOMMODATION = "Accommodation"
    ACTIVITY = "Activity"


class PaymentStatus(str, Enum):
    PENDING = "Pending"
    PARTIAL = "Partial"
    PAID = "Paid"
    REFUNDED = "Refunded"
    FAILED = "Failed"


class ItemType(str, Enum):
    ACCOMMODATION = "Accommodation"
    TRANSPORT = "Transport"
    ACTIVITY = "Activity"
    GUIDE = "Guide"
    MEAL = "Meal"
    INSURANCE = "Insurance"


class DiscountType(str, Enum):
    PERCENTAGE = "Percentage"
    FIXED_AMOUNT = "Fixed Amount"
    BUY_X_GET_Y = "Buy X Get Y"
    EARLY_BIRD = "Early Bird"
    GROUP_DISCOUNT = "Group Discount"


class ResourceType(str, Enum):
    VEHICLE = "Vehicle"
    GUIDE = "Guide"
    ACCOMMODATION = "Accommodation"
    ACTIVITY = "Activity"

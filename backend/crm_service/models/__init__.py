"""
Database models for the CRM microservice
"""
from .customer import Customer, ContactType, LoyaltyStatus
from .interaction import Interaction, ChannelType
from .feedback import Feedback, ServiceType
from .segment import Segment

__all__ = [
    "Customer", "ContactType", "LoyaltyStatus",
    "Interaction", "ChannelType", 
    "Feedback", "ServiceType",
    "Segment"
]
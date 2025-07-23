"""
Pydantic schemas for request/response models
"""
from .customer import *
from .interaction import *
from .feedback import *
from .segment import *

__all__ = [
    "CustomerCreate", "CustomerUpdate", "CustomerResponse", "CustomerSummary",
    "InteractionCreate", "InteractionUpdate", "InteractionResponse",
    "FeedbackCreate", "FeedbackUpdate", "FeedbackResponse", "FeedbackStats",
    "SegmentCreate", "SegmentUpdate", "SegmentResponse", "SegmentWithCustomers"
]
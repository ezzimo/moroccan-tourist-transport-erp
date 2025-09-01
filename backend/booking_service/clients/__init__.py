"""
Client modules for external service communication
"""
from .customer_client import get_customer_by_id, CustomerVerificationError

__all__ = ["get_customer_by_id", "CustomerVerificationError"]
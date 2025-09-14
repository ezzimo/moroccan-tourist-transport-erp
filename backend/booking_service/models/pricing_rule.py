"""
Pricing rule model for dynamic pricing and discounts.
"""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict, Any
import json
import uuid

from sqlalchemy import Column, Numeric
from sqlmodel import SQLModel, Field

from .enums import DiscountType


class PricingRule(SQLModel, table=True):
    """Pricing rule model for dynamic pricing and discounts"""

    __tablename__ = "pricing_rules"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )

    # Rule Information
    name: str = Field(unique=True, max_length=255, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    code: Optional[str] = Field(default=None, unique=True, max_length=50)

    # Rule Type and Value
    discount_type: DiscountType = Field(index=True)
    discount_percentage: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(10, 2)),
    )
    discount_amount: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(10, 2)),
    )

    # Conditions (stored as JSON)
    conditions: str = Field()

    # Validity
    valid_from: date = Field(index=True)
    valid_until: date = Field(index=True)

    # Usage Limits
    max_uses: Optional[int] = Field(default=None)
    max_uses_per_customer: Optional[int] = Field(default=1)
    current_uses: int = Field(default=0)

    # Priority and Status
    priority: int = Field(default=0, index=True)
    is_active: bool = Field(default=True, index=True)
    is_combinable: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    def get_conditions_dict(self) -> Dict[str, Any]:
        try:
            return json.loads(self.conditions)
        except Exception:
            return {}

    def set_conditions_dict(self, conditions_dict: Dict[str, Any]) -> None:
        self.conditions = json.dumps(conditions_dict)

    def is_valid_now(self) -> bool:
        today = date.today()
        return (
            self.is_active
            and self.valid_from <= today <= self.valid_until
            and (self.max_uses is None or self.current_uses < self.max_uses)
        )

    def can_apply_to_booking(self, booking_data: dict) -> bool:
        if not self.is_valid_now():
            return False

        conditions = self.get_conditions_dict()

        if (
            "min_pax" in conditions
            and booking_data.get("pax_count", 0) < conditions["min_pax"]
        ):
            return False

        if (
            "service_types" in conditions
            and booking_data.get("service_type")
            not in conditions["service_types"]
        ):
            return False

        if (
            "min_booking_value" in conditions
            and booking_data.get("base_price", 0)
            < conditions["min_booking_value"]
        ):
            return False

        if "min_advance_days" in conditions:
            booking_date = booking_data.get("start_date")
            if booking_date:
                if isinstance(booking_date, str):
                    booking_date = datetime.strptime(
                        booking_date,
                        "%Y-%m-%d",
                    ).date()
                days_advance = (booking_date - date.today()).days
                if days_advance < conditions["min_advance_days"]:
                    return False

        return True

    def calculate_discount(
            self,
            base_price: Decimal,
            pax_count: int = 1,
    ) -> Decimal:
        if (
            self.discount_type == DiscountType.PERCENTAGE
            and self.discount_percentage
        ):
            return base_price * (
                self.discount_percentage / 100
            )
        if (
            self.discount_type == DiscountType.FIXED_AMOUNT
            and self.discount_amount
        ):
            return self.discount_amount
        if self.discount_type == DiscountType.GROUP_DISCOUNT:
            conditions = self.get_conditions_dict()
            group_threshold = conditions.get("group_threshold", 10)
            if pax_count >= group_threshold and self.discount_percentage:
                return base_price * (self.discount_percentage / 100)
        return Decimal(0)

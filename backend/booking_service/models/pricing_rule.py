"""
Pricing rule model for dynamic pricing and discounts
"""

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric
from typing import Optional, Dict, Any
from datetime import datetime, date
from enum import Enum
from decimal import Decimal
import uuid
import json


class DiscountType(str, Enum):
    """Discount type enumeration"""

    PERCENTAGE = "Percentage"
    FIXED_AMOUNT = "Fixed Amount"
    BUY_X_GET_Y = "Buy X Get Y"
    EARLY_BIRD = "Early Bird"
    GROUP_DISCOUNT = "Group Discount"


class PricingRule(SQLModel, table=True):
    """Pricing rule model for dynamic pricing and discounts"""

    __tablename__ = "pricing_rules"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True,
    )

    # Rule Information
    name: Optional[str] = Field(
        unique=True,
        max_length=255,
        index=True,
        default=None,
    )
    description: Optional[str] = Field(default=None, max_length=1000)
    # Promo code
    code: Optional[str] = Field(default=None, unique=True, max_length=50)

    # Rule Type and Value
    discount_type: Optional[DiscountType] = Field(index=True, default=None)
    discount_percentage: Optional[Decimal] = Field(
        default=None, sa_column=Column(Numeric(10, 2))
    )
    discount_amount: Optional[Decimal] = Field(
        default=None, sa_column=Column(Numeric(10, 2))
    )

    # Conditions (stored as JSON)
    conditions: Optional[str] = Field(
        default=None
    )  # JSON string containing rule conditions

    # Validity
    valid_from: Optional[date] = Field(index=True, default=None)
    valid_until: Optional[date] = Field(index=True, default=None)

    # Usage Limits
    max_uses: Optional[int] = Field(default=None)
    max_uses_per_customer: Optional[int] = Field(default=1)
    current_uses: int = Field(default=0)

    # Priority and Status
    # Higher number = higher priority
    priority: int = Field(default=0, index=True)
    is_active: bool = Field(default=True, index=True)
    # Can be combined with other rules
    is_combinable: bool = Field(default=False)

    # Timestamps
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
    )
    updated_at: Optional[datetime] = Field(default=None)

    def get_conditions_dict(self) -> Dict[str, Any]:
        """Parse conditions from JSON string"""
        try:
            return json.loads(self.conditions)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_conditions_dict(self, conditions_dict: Dict[str, Any]):
        """Set conditions as JSON string"""
        self.conditions = json.dumps(conditions_dict)

    def is_valid_now(self) -> bool:
        """Check if rule is currently valid"""
        today = date.today()
        return (
            self.is_active
            and self.valid_from <= today <= self.valid_until
            and (self.max_uses is None or self.current_uses < self.max_uses)
        )

    def can_apply_to_booking(self, booking_data: dict) -> bool:
        """Check if rule can be applied to a booking"""
        if not self.is_valid_now():
            return False

        conditions = self.get_conditions_dict()

        # Check minimum passenger count
        if "min_pax" in conditions:
            if booking_data.get("pax_count", 0) < conditions["min_pax"]:
                return False

        # Check service type
        if "service_types" in conditions:
            if (
                booking_data.get("service_type")
                not in conditions["service_types"]
            ):
                return False

        # Check booking value
        if "min_booking_value" in conditions:
            if booking_data.get("base_price", 0) < conditions[
                "min_booking_value"
            ]:
                return False

        # Check advance booking days
        if "min_advance_days" in conditions:
            booking_date = booking_data.get("start_date")
            if booking_date:
                from datetime import datetime
                booking_date = datetime.strptime(
                    booking_date, "%Y-%m-%d"
                ).date()
                if isinstance(booking_date, str):
                    booking_date = datetime.strptime(
                        booking_date, "%Y-%m-%d"
                    ).date()
                days_advance = (booking_date - date.today()).days
                if days_advance < conditions["min_advance_days"]:
                    return False

        return True

    def calculate_discount(
            self, base_price: Decimal, pax_count: int = 1
    ) -> Decimal:
        """Calculate discount amount for given base price"""
        if self.discount_type == DiscountType.PERCENTAGE:
            if self.discount_percentage:
                return base_price * (self.discount_percentage / 100)

        elif self.discount_type == DiscountType.FIXED_AMOUNT:
            if self.discount_amount:
                return self.discount_amount

        elif self.discount_type == DiscountType.GROUP_DISCOUNT:
            conditions = self.get_conditions_dict()
            group_threshold = conditions.get("group_threshold", 10)
            if pax_count >= group_threshold and self.discount_percentage:
                return base_price * (self.discount_percentage / 100)

        return Decimal(0)

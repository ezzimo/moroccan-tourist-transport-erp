"""
Pricing service with pure Python calculations
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Dict, Any

from sqlmodel import Session

logger = logging.getLogger(__name__)

def _to_decimal(x: Any) -> Decimal:
    """Convert any numeric value to Decimal safely"""
    if isinstance(x, Decimal):
        return x
    try:
        return Decimal(str(x))
    except Exception:
        return Decimal("0")

def _money(x: Decimal) -> Decimal:
    """Round to 2 decimal places for currency"""
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

@dataclass
class PricingInput:
    service_type: str
    base_price: Decimal
    pax_count: int
    start_date: date
    end_date: Optional[date] = None
    currency: str = "MAD"

class PricingService:
    """Service for handling pricing calculations with pure Python arithmetic"""
    
    def __init__(self, session: Session):
        self.session = session

    async def calculate_pricing(
        self,
        *,
        service_type: str,
        base_price: Decimal | float | int,
        pax_count: int,
        start_date: date,
        end_date: Optional[date] = None,
        currency: str = "MAD",
    ) -> Dict[str, Any]:
        """
        Minimal, deterministic calculator that avoids SQLAlchemy expressions entirely.
        Rules:
          - price per day per pax = base_price
          - days = 1 if end_date not provided; else inclusive day count (min 1)
          - season surcharge +20% if month in {6,7,8,12}
          - weekend surcharge +10% if start_date is Sat/Sun
        """
        bp = _to_decimal(base_price)
        pax = max(int(pax_count or 0), 1)

        # Compute day span
        if end_date and end_date >= start_date:
            days = (end_date - start_date).days + 1
        else:
            days = 1

        # Base subtotal
        base_subtotal = bp * pax * days

        # Season/Weekend surcharges
        season_months = {6, 7, 8, 12}
        season_factor = Decimal("1.20") if start_date.month in season_months else Decimal("1.00")
        weekend_factor = Decimal("1.10") if start_date.weekday() >= 5 else Decimal("1.00")

        subtotal_after_surcharges = base_subtotal * season_factor * weekend_factor

        # (Hooks for future DB-driven discounts or promos can be added here AFTER materializing rows)

        total = _money(subtotal_after_surcharges)

        breakdown = {
            "base_price": _money(bp),
            "pax_count": pax,
            "days": days,
            "season_applied": season_factor != Decimal("1.00"),
            "weekend_applied": weekend_factor != Decimal("1.00"),
            "season_factor": str(season_factor),
            "weekend_factor": str(weekend_factor),
            "currency": currency,
        }

        logger.info(
            "Calculated pricing for %s: base=%s, pax=%s, days=%s, season=%s, weekend=%s, total=%s %s",
            service_type, bp, pax, days, breakdown["season_applied"], breakdown["weekend_applied"], total, currency
        )

        return {
            "service_type": service_type,
            "currency": currency,
            "total": total,
            "breakdown": breakdown,
        }

    async def validate_pricing_input(
        self,
        service_type: str,
        base_price: Any,
        pax_count: int,
        start_date: date,
        end_date: Optional[date] = None
    ) -> None:
        """Validate pricing calculation inputs"""
        if not service_type or not service_type.strip():
            raise ValueError("Service type is required")
        
        if _to_decimal(base_price) <= 0:
            raise ValueError("Base price must be greater than 0")
        
        if pax_count <= 0:
            raise ValueError("Passenger count must be greater than 0")
        
        if end_date and end_date < start_date:
            raise ValueError("End date cannot be before start date")
        
        # Validate date is not too far in the past or future
        from datetime import datetime, timedelta
        today = datetime.now().date()
        if start_date < today - timedelta(days=30):
            raise ValueError("Start date cannot be more than 30 days in the past")
        
        if start_date > today + timedelta(days=365):
            raise ValueError("Start date cannot be more than 1 year in the future")
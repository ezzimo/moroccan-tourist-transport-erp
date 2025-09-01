# backend/booking_service/app/routers/pricing.py
import logging
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session

from database import get_session
from services.pricing_service import PricingService
from utils.auth import get_current_user, require_permission, CurrentUser

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/pricing", tags=["Pricing"])

class PricingCalculateRequest(BaseModel):
    service_type: str = Field(..., examples=["Transfer"])
    base_price: float | int | str
    pax_count: int = 1
    start_date: date
    end_date: Optional[date] = None
    currency: Optional[str] = "MAD"

@router.post("/calculate")
async def calculate_pricing(
    payload: PricingCalculateRequest,
    db: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("pricing", "read", "pricing"))
):
    logger.info(
        "Pricing calculation requested by %s", current_user.email if hasattr(current_user, "email") else "unknown"
    )
    svc = PricingService(db)
    try:
        result = await svc.calculate_pricing(
            service_type=payload.service_type,
            base_price=payload.base_price,
            pax_count=payload.pax_count,
            start_date=payload.start_date,
            end_date=payload.end_date,
            currency=payload.currency or "MAD",
        )
        return result
    except HTTPException:
        raise
    except Exception as ex:
        logger.error("Pricing calculation failed: %s", ex, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to calculate pricing")
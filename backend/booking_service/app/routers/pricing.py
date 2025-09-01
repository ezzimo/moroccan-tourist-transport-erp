"""
Pricing calculation routes
"""
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
    """Calculate pricing for a booking with dynamic rules"""
    logger.info(
        "Pricing calculation requested by %s for service_type=%s, pax=%s", 
        current_user.email if hasattr(current_user, "email") else "unknown",
        payload.service_type,
        payload.pax_count
    )
    
    svc = PricingService(db)
    
    try:
        # Validate input first
        await svc.validate_pricing_input(
            service_type=payload.service_type,
            base_price=payload.base_price,
            pax_count=payload.pax_count,
            start_date=payload.start_date,
            end_date=payload.end_date
        )
        
        # Calculate pricing
        result = await svc.calculate_pricing(
            service_type=payload.service_type,
            base_price=payload.base_price,
            pax_count=payload.pax_count,
            start_date=payload.start_date,
            end_date=payload.end_date,
            currency=payload.currency or "MAD",
        )
        
        logger.info(
            "Pricing calculation successful: total=%s %s", 
            result["total"], 
            result["currency"]
        )
        
        return result
        
    except ValueError as ve:
        logger.warning("Pricing validation error: %s", ve)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except HTTPException:
        raise
    except Exception as ex:
        logger.error("Pricing calculation failed: %s", ex, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to calculate pricing"
        )

@router.get("/health")
async def pricing_health_check():
    """Health check endpoint for pricing service"""
    return {
        "status": "healthy",
        "service": "pricing",
        "version": "1.0.0"
    }
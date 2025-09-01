"""
Pricing calculation router with safe error handling
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from database import get_session
from utils.auth import get_current_user, require_permission, CurrentUser
from services.pricing_service import PricingService
from schemas.pricing import PricingRequest, PricingResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/pricing", tags=["Pricing"])


# === ROUTER: PRICING CALCULATE ===
@router.post("/calculate", response_model=PricingResponse)
async def calculate_pricing(
    body: PricingRequest,
    db: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("booking", "read", "pricing")),
):
    """
    Calculate pricing for a booking request
    
    This endpoint applies all applicable pricing rules to calculate
    the final price including discounts and surcharges.
    """
    logger.info("Pricing calculation requested by %s for service_type=%s", 
               current_user.email, body.service_type)
    
    try:
        service = PricingService(db)
        result = await service.calculate_pricing(body)
        
        logger.info("Pricing calculation successful: base=%s, total=%s", 
                   result.base_price, result.total_price)
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors, etc.)
        raise
    except Exception as ex:
        logger.exception("Pricing calculation failed unexpectedly: %s", ex)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate pricing - please try again"
        )


@router.get("/rules")
async def get_pricing_rules(
    service_type: str = None,
    db: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("booking", "read", "pricing")),
):
    """Get all active pricing rules, optionally filtered by service type"""
    try:
        service = PricingService(db)
        rules = await service.get_pricing_rules(service_type)
        return {"items": rules, "total": len(rules)}
    except Exception as ex:
        logger.exception("Failed to fetch pricing rules: %s", ex)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch pricing rules"
        )
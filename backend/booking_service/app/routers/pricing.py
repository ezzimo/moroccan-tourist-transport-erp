"""
Pricing calculation routes
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


@router.post("/calculate", response_model=PricingResponse)
async def calculate_pricing(
    payload: PricingRequest,
    db: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("booking", "create", "bookings")),
):
    """Calculate pricing for a booking request"""
    logger.info("Pricing calculation requested by %s for service %s", 
                current_user.email, payload.service_type)
    
    try:
        service = PricingService(db)
        result = await service.calculate_pricing(payload)
        
        logger.info("Pricing calculation successful: total=%s %s", 
                   result.total_price, result.currency)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Pricing calculation failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate pricing"
        )
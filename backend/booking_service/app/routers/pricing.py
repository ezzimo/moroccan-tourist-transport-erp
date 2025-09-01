"""
Pricing routes with fixed request handling
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from database import get_session
from utils.auth import get_current_user, require_permission, CurrentUser
from services.pricing_service import PricingService
from schemas.pricing import PricingRequest, PricingCalculation

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/pricing", tags=["Pricing"])


@router.post("/calculate", response_model=PricingCalculation)
async def calculate_pricing(
    request: PricingRequest,
    db: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("booking", "read", "pricing")),
):
    """Calculate pricing with applicable discounts"""
    
    logger.info(
        "Pricing calculation requested by %s for service_type=%s",
        current_user.email, request.service_type
    )
    
    try:
        pricing_service = PricingService(db)
        result = await pricing_service.calculate_pricing(request)
        
        logger.info(
            "Pricing calculation successful: base=%s, total=%s, discount=%s",
            result.base_price, result.total_price, result.discount_amount
        )
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.exception("Unexpected error in pricing calculation: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during pricing calculation"
        )


@router.post("/validate-promo")
async def validate_promo_code(
    promo_code: str,
    pricing_request: PricingRequest,
    db: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("booking", "read", "pricing")),
):
    """Validate a promotional code"""
    
    logger.info(
        "Promo code validation requested by %s: %s",
        current_user.email, promo_code
    )
    
    try:
        pricing_service = PricingService(db)
        rule = await pricing_service.validate_promo_code(promo_code, pricing_request)
        
        if rule:
            return {
                "valid": True,
                "rule_name": rule.name,
                "discount_type": rule.discount_type.value,
                "discount_value": rule.get_discount_value(),
                "description": rule.description
            }
        else:
            return {
                "valid": False,
                "message": "Invalid promotional code"
            }
            
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.exception("Unexpected error in promo validation: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during promo code validation"
        )
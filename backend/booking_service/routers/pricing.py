"""
Pricing calculation routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session
from database import get_session
from services.pricing_service import PricingService
from schemas.pricing import PricingRequest, PricingCalculation, PricingContext
from utils.auth import require_permission, CurrentUser
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/pricing", tags=["Pricing"])


@router.post("/calculate", response_model=PricingCalculation)
async def calculate_pricing(
    request: Request,
    pricing_request: PricingRequest,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "read", "pricing"))
):
    """Calculate pricing with applicable discounts"""
    logger.info(f"Pricing calculation requested by user: {current_user.email}")
    
    try:
        # Convert request to pricing context
        context = pricing_request.to_pricing_context()
        
        # Calculate pricing
        pricing_service = PricingService(session)
        calculation = await pricing_service.calculate_pricing(context)
        
        logger.info(f"Pricing calculation completed: {calculation.base_price} -> {calculation.total_price}")
        return calculation
        
    except Exception as e:
        logger.error(f"Pricing calculation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Pricing calculation failed"
        )


@router.post("/validate-promo")
async def validate_promo_code(
    request: Request,
    promo_data: dict,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "read", "pricing"))
):
    """Validate promotional code"""
    try:
        promo_code = promo_data.get("promo_code")
        if not promo_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Promo code is required"
            )
        
        # Create context from request data
        context = PricingContext(
            service_type=promo_data.get("service_type", "Tour"),
            base_price=Decimal(str(promo_data.get("base_price", 0))),
            pax_count=promo_data.get("pax_count", 1),
            start_date=datetime.strptime(promo_data.get("start_date", "2024-01-01"), "%Y-%m-%d").date(),
            promo_code=promo_code
        )
        
        pricing_service = PricingService(session)
        rule = await pricing_service.validate_promo_code(promo_code, context)
        
        if rule:
            return {
                "valid": True,
                "rule_name": rule.name,
                "discount_type": rule.discount_type,
                "discount_percentage": rule.discount_percentage,
                "discount_amount": rule.discount_amount,
                "message": f"Promo code '{promo_code}' is valid"
            }
        else:
            return {
                "valid": False,
                "message": "Promo code is not valid"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Promo code validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Promo code validation failed"
        )
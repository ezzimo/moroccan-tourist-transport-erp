"""
Pricing routes for booking service
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from database import get_session
from services.pricing_service import PricingService
from schemas.pricing import (
    PricingRequest,
    PricingCalculation,
    PromoCodeValidation,
    PromoCodeResponse
)
from utils.auth import require_permission, CurrentUser
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/pricing", tags=["Pricing"])


@router.post("/calculate", response_model=PricingCalculation)
async def calculate_pricing(
    pricing_request: PricingRequest,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "read", "pricing"))
):
    """Calculate pricing with applicable discounts"""
    logger.info(f"Pricing calculation requested by {current_user.email}")
    
    try:
        # Convert request to pricing context
        context = pricing_request.to_pricing_context()
        
        # Calculate pricing
        pricing_service = PricingService(session)
        result = await pricing_service.calculate_pricing(context)
        
        logger.info(f"Pricing calculation successful: {result.total_price} {result.currency}")
        return result
        
    except Exception as e:
        logger.error(f"Pricing calculation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate pricing"
        )


@router.post("/validate-promo", response_model=PromoCodeResponse)
async def validate_promo_code(
    validation_request: PromoCodeValidation,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "read", "pricing"))
):
    """Validate a promotional code"""
    logger.info(f"Promo code validation requested: {validation_request.promo_code}")
    
    try:
        # Convert to pricing context
        context = PricingRequest(
            service_type=validation_request.service_type,
            base_price=validation_request.base_price,
            pax_count=validation_request.pax_count,
            start_date=validation_request.start_date,
            customer_id=validation_request.customer_id,
            promo_code=validation_request.promo_code
        ).to_pricing_context()
        
        # Validate promo code
        pricing_service = PricingService(session)
        result = await pricing_service.validate_promo_code(validation_request.promo_code, context)
        
        logger.info(f"Promo code validation result: {result.valid}")
        return result
        
    except Exception as e:
        logger.error(f"Promo code validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate promo code"
        )


@router.get("/rules")
async def get_pricing_rules(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "read", "pricing"))
):
    """Get all active pricing rules"""
    logger.info(f"Pricing rules requested by {current_user.email}")
    
    try:
        from models.pricing_rule import PricingRule
        from sqlmodel import select
        
        query = select(PricingRule).where(PricingRule.is_active == True)
        result = self.session.exec(query)
        rules = result.all()
        
        return [
            {
                "id": rule.id,
                "name": rule.name,
                "description": rule.description,
                "discount_type": rule.discount_type.value,
                "discount_percentage": rule.discount_percentage,
                "discount_amount": rule.discount_amount,
                "valid_from": rule.valid_from,
                "valid_until": rule.valid_until,
                "is_active": rule.is_active
            }
            for rule in rules
        ]
        
    except Exception as e:
        logger.error(f"Failed to get pricing rules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pricing rules"
        )
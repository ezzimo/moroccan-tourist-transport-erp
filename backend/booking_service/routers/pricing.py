"""
Pricing routes with comprehensive error handling
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session
from database import get_session
from services.pricing_service import PricingService, PricingValidationError
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
    """
    Calculate pricing with applicable discounts
    
    This endpoint calculates the total price for a booking including any applicable
    discounts based on pricing rules, customer loyalty, promotional codes, etc.
    """
    try:
        # Log the incoming request for debugging
        logger.info(f"Pricing calculation request from user {current_user.email}: {pricing_request.model_dump()}")
        
        pricing_service = PricingService(session)
        result = await pricing_service.calculate_pricing(pricing_request)
        
        logger.info(f"Pricing calculation successful: total={result.total_price}")
        return result
        
    except PricingValidationError as e:
        logger.warning(f"Pricing validation error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error_code": e.error_code,
                "message": e.message,
                "type": "validation_error"
            }
        )
    except ValueError as e:
        logger.warning(f"Pricing value error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error_code": "INVALID_INPUT",
                "message": str(e),
                "type": "validation_error"
            }
        )
    except Exception as e:
        logger.exception(f"Unexpected error in pricing calculation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during pricing calculation",
                "type": "system_error"
            }
        )


@router.post("/validate-promo", response_model=dict)
async def validate_promo_code(
    promo_data: dict,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "read", "pricing"))
):
    """
    Validate a promotional code
    
    This endpoint validates whether a promotional code is valid and applicable
    to the given booking context.
    """
    try:
        promo_code = promo_data.get('promo_code', '').strip()
        
        if not promo_code:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Promo code is required"
            )
        
        # Create pricing context from request data
        try:
            context = PricingContext(
                service_type=promo_data.get('service_type', ''),
                base_price=Decimal(str(promo_data.get('base_price', 0))),
                pax_count=int(promo_data.get('pax_count', 1)),
                start_date=datetime.strptime(promo_data.get('start_date', ''), '%Y-%m-%d').date(),
                end_date=datetime.strptime(promo_data.get('end_date'), '%Y-%m-%d').date() if promo_data.get('end_date') else None,
                customer_id=promo_data.get('customer_id'),
                promo_code=promo_code
            )
        except (ValueError, TypeError, KeyError) as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid request data: {e}"
            )
        
        pricing_service = PricingService(session)
        result = await pricing_service.validate_promo_code(promo_code, context)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error validating promo code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error validating promotional code"
        )


@router.get("/rules", response_model=list)
async def get_pricing_rules(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "read", "pricing"))
):
    """Get all active pricing rules"""
    try:
        from models.pricing_rule import PricingRule as PricingRuleModel
        from sqlmodel import select
        
        query = select(PricingRuleModel).where(PricingRuleModel.is_active == True)
        rules = session.exec(query).all()
        
        return [
            {
                "id": str(rule.id),
                "name": rule.name,
                "description": rule.description,
                "discount_type": rule.discount_type,
                "discount_percentage": float(rule.discount_percentage) if rule.discount_percentage else None,
                "discount_amount": float(rule.discount_amount) if rule.discount_amount else None,
                "valid_from": rule.valid_from.isoformat(),
                "valid_until": rule.valid_until.isoformat() if rule.valid_until else None,
                "conditions": rule.conditions
            }
            for rule in rules
        ]
        
    except Exception as e:
        logger.exception(f"Error retrieving pricing rules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving pricing rules"
        )
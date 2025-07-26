"""
Pricing management routes
"""

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session
from services.pricing_service import PricingService
from schemas.booking import (
    PricingRuleCreate,
    PricingRuleUpdate,
    PricingRuleResponse,
    PricingRequest,
    PricingResponse,
)
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional, Dict, Any
import uuid


router = APIRouter(prefix="/pricing", tags=["Pricing Management"])


@router.post("/calculate", response_model=PricingResponse)
async def calculate_pricing(
    pricing_request: PricingRequest,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(
        require_permission("booking", "read", "pricing")
    ),
):
    """Calculate pricing with applicable discounts"""
    pricing_service = PricingService(session)

    # Convert request to dict for service
    request_dict = {
        "service_type": pricing_request.service_type,
        "base_price": pricing_request.base_price,
        "pax_count": pricing_request.pax_count,
        "start_date": pricing_request.start_date,
        "end_date": pricing_request.end_date,
        "customer_id": pricing_request.customer_id,
        "promo_code": pricing_request.promo_code,
    }

    result = await pricing_service.calculate_pricing(request_dict)

    return PricingResponse(**result)


@router.post("/validate-promo")
async def validate_promo_code(
    promo_code: str = Query(..., description="Promo code to validate"),
    service_type: str = Query(..., description="Service type"),
    base_price: float = Query(..., description="Base price"),
    pax_count: int = Query(..., description="Number of passengers"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(
        require_permission("booking", "read", "pricing")
    ),
):
    """Validate a promo code"""
    from datetime import datetime

    pricing_service = PricingService(session)

    booking_data = {
        "service_type": service_type,
        "base_price": base_price,
        "pax_count": pax_count,
        "start_date": datetime.strptime(start_date, "%Y-%m-%d").date(),
    }

    return await pricing_service.validate_promo_code(promo_code, booking_data)


@router.post("/rules", response_model=PricingRuleResponse)
async def create_pricing_rule(
    rule_data: PricingRuleCreate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(
        require_permission("booking", "create", "pricing")
    ),
):
    """Create a new pricing rule"""
    pricing_service = PricingService(session)

    rule_dict = rule_data.model_dump()
    rule = await pricing_service.create_pricing_rule(rule_dict)

    return PricingRuleResponse(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        code=rule.code,
        discount_type=rule.discount_type,
        discount_percentage=rule.discount_percentage,
        discount_amount=rule.discount_amount,
        conditions=rule.get_conditions_dict(),
        valid_from=rule.valid_from,
        valid_until=rule.valid_until,
        max_uses=rule.max_uses,
        max_uses_per_customer=rule.max_uses_per_customer,
        current_uses=rule.current_uses,
        priority=rule.priority,
        is_active=rule.is_active,
        is_combinable=rule.is_combinable,
        created_at=rule.created_at,
        updated_at=rule.updated_at,
    )


@router.get("/rules", response_model=PaginatedResponse[PricingRuleResponse])
async def get_pricing_rules(
    pagination: PaginationParams = Depends(),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(
        require_permission("booking", "read", "pricing")
    ),
):
    """Get list of pricing rules"""
    from sqlmodel import select
    from models.pricing_rule import PricingRule
    from utils.pagination import paginate_query

    query = select(PricingRule)

    if is_active is not None:
        query = query.where(PricingRule.is_active == is_active)

    query = query.order_by(PricingRule.priority.desc(), PricingRule.created_at.desc())

    rules, total = paginate_query(session, query, pagination)

    rule_responses = []
    for rule in rules:
        rule_responses.append(
            PricingRuleResponse(
                id=rule.id,
                name=rule.name,
                description=rule.description,
                code=rule.code,
                discount_type=rule.discount_type,
                discount_percentage=rule.discount_percentage,
                discount_amount=rule.discount_amount,
                conditions=rule.get_conditions_dict(),
                valid_from=rule.valid_from,
                valid_until=rule.valid_until,
                max_uses=rule.max_uses,
                max_uses_per_customer=rule.max_uses_per_customer,
                current_uses=rule.current_uses,
                priority=rule.priority,
                is_active=rule.is_active,
                is_combinable=rule.is_combinable,
                created_at=rule.created_at,
                updated_at=rule.updated_at,
            )
        )

    return PaginatedResponse.create(
        items=rule_responses, total=total, page=pagination.page, size=pagination.size
    )


@router.get("/rules/{rule_id}", response_model=PricingRuleResponse)
async def get_pricing_rule(
    rule_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(
        require_permission("booking", "read", "pricing")
    ),
):
    """Get pricing rule by ID"""
    from sqlmodel import select
    from models.pricing_rule import PricingRule
    from fastapi import HTTPException, status

    statement = select(PricingRule).where(PricingRule.id == rule_id)
    rule = session.exec(statement).first()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pricing rule not found"
        )

    return PricingRuleResponse(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        code=rule.code,
        discount_type=rule.discount_type,
        discount_percentage=rule.discount_percentage,
        discount_amount=rule.discount_amount,
        conditions=rule.get_conditions_dict(),
        valid_from=rule.valid_from,
        valid_until=rule.valid_until,
        max_uses=rule.max_uses,
        max_uses_per_customer=rule.max_uses_per_customer,
        current_uses=rule.current_uses,
        priority=rule.priority,
        is_active=rule.is_active,
        is_combinable=rule.is_combinable,
        created_at=rule.created_at,
        updated_at=rule.updated_at,
    )


@router.put("/rules/{rule_id}", response_model=PricingRuleResponse)
async def update_pricing_rule(
    rule_id: uuid.UUID,
    rule_data: PricingRuleUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(
        require_permission("booking", "update", "pricing")
    ),
):
    """Update a pricing rule"""
    pricing_service = PricingService(session)

    update_dict = rule_data.model_dump(exclude_unset=True)
    rule = await pricing_service.update_pricing_rule(rule_id, update_dict)

    return PricingRuleResponse(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        code=rule.code,
        discount_type=rule.discount_type,
        discount_percentage=rule.discount_percentage,
        discount_amount=rule.discount_amount,
        conditions=rule.get_conditions_dict(),
        valid_from=rule.valid_from,
        valid_until=rule.valid_until,
        max_uses=rule.max_uses,
        max_uses_per_customer=rule.max_uses_per_customer,
        current_uses=rule.current_uses,
        priority=rule.priority,
        is_active=rule.is_active,
        is_combinable=rule.is_combinable,
        created_at=rule.created_at,
        updated_at=rule.updated_at,
    )


@router.delete("/rules/{rule_id}")
async def delete_pricing_rule(
    rule_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(
        require_permission("booking", "delete", "pricing")
    ),
):
    """Delete a pricing rule"""
    from sqlmodel import select
    from models.pricing_rule import PricingRule
    from fastapi import HTTPException, status

    statement = select(PricingRule).where(PricingRule.id == rule_id)
    rule = session.exec(statement).first()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pricing rule not found"
        )

    session.delete(rule)
    session.commit()

    return {"message": "Pricing rule deleted successfully"}

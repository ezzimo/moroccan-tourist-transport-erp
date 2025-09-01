"""
Pricing service with pure Python calculations (no SQL expression subscripting)
"""
import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import List
from sqlmodel import Session, select, and_
from fastapi import HTTPException, status
from datetime import date

from models.pricing_rule import PricingRule
from schemas.pricing import PricingRequest, PricingResponse

logger = logging.getLogger(__name__)


class PricingService:
    """Service for calculating booking pricing using pure Python arithmetic"""
    
    def __init__(self, session: Session):
        self.session = session

    async def _get_applicable_rules(self, service_type: str, pax_count: int, start_date: date) -> List[PricingRule]:
        """Fetch applicable pricing rules using SQL filters only"""
        conditions = [
            PricingRule.is_active == True,
            (PricingRule.service_type == service_type) | (PricingRule.service_type.is_(None))
        ]
        
        # Use SQL conditions for basic filtering, detailed checks in Python
        stmt = (
            select(PricingRule)
            .where(and_(*conditions))
            .order_by(PricingRule.priority.asc(), PricingRule.id.asc())
        )
        
        all_rules = self.session.exec(stmt).all()
        
        # Filter in Python using attribute access only
        applicable_rules = []
        for rule in all_rules:
            if rule.is_applicable(pax_count, start_date):
                applicable_rules.append(rule)
        
        return applicable_rules

    async def calculate_pricing(self, req: PricingRequest) -> PricingResponse:
        """
        Calculate pricing using pure Python arithmetic - no SQL expression subscripting
        """
        logger.info(
            "Calculating pricing for service_type=%s, base_price=%s, pax_count=%s, start_date=%s",
            req.service_type, req.base_price, req.pax_count, req.start_date
        )
        
        # Validate inputs
        if req.base_price < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Base price cannot be negative"
            )
        if req.pax_count < 1:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Passenger count must be at least 1"
            )

        # Convert to Decimal for precise calculations
        base_price = Decimal(str(req.base_price))
        pax_count = int(req.pax_count)
        
        # Calculate subtotal
        subtotal = (base_price * pax_count).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        # Get applicable rules
        try:
            rules = await self._get_applicable_rules(req.service_type, pax_count, req.start_date)
        except Exception as e:
            logger.error("Failed to fetch pricing rules: %s", e)
            # Fallback to base pricing if rule fetching fails
            rules = []

        # === PRICING: RULE EVAL START ===
        total_discount = Decimal("0.00")
        total_surcharge = Decimal("0.00")
        applied_rules = []

        for rule in rules:
            # All attribute access - never rule['...'] or SQL column math
            rule_name = rule.name
            rule_type = rule.rule_type
            
            try:
                if rule_type == "percentage_discount" and rule.discount_percentage is not None:
                    discount_amount = (subtotal * Decimal(str(rule.discount_percentage)) / Decimal("100")).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                    total_discount += discount_amount
                    applied_rules.append(f"{rule_name} (-{rule.discount_percentage}%)")
                    
                elif rule_type == "flat_discount" and rule.discount_amount is not None:
                    discount_amount = Decimal(str(rule.discount_amount)).quantize(Decimal("0.01"))
                    total_discount += discount_amount
                    applied_rules.append(f"{rule_name} (-{discount_amount} {req.currency or 'MAD'})")
                    
                elif rule_type == "surcharge_percentage" and rule.surcharge_percentage is not None:
                    surcharge_amount = (subtotal * Decimal(str(rule.surcharge_percentage)) / Decimal("100")).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                    total_surcharge += surcharge_amount
                    applied_rules.append(f"{rule_name} (+{rule.surcharge_percentage}%)")
                    
                elif rule_type == "surcharge_flat" and rule.surcharge_amount is not None:
                    surcharge_amount = Decimal(str(rule.surcharge_amount)).quantize(Decimal("0.01"))
                    total_surcharge += surcharge_amount
                    applied_rules.append(f"{rule_name} (+{surcharge_amount} {req.currency or 'MAD'})")
                    
            except Exception as e:
                logger.warning("Failed to apply pricing rule %s: %s", rule_name, e)
                continue
        # === PRICING: RULE EVAL END ===

        # Calculate final total
        final_total = (subtotal - total_discount + total_surcharge).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        
        # Ensure total is never negative
        if final_total < 0:
            final_total = Decimal("0.00")

        # === PRICING: RETURN DTO ===
        result = PricingResponse(
            base_price=base_price,
            pax_count=pax_count,
            service_type=req.service_type,
            subtotal=subtotal,
            discount_amount=total_discount,
            surcharge_amount=total_surcharge,
            total_price=final_total,
            currency=req.currency or "MAD",
            applied_rules=applied_rules,
        )
        
        logger.info(
            "Pricing calculated: subtotal=%s, discount=%s, surcharge=%s, total=%s",
            subtotal, total_discount, total_surcharge, final_total
        )
        
        return result
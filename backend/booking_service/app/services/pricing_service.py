"""
Pricing service with safe attribute access and no ORM subscripting
"""
import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import List
from sqlmodel import Session, select, and_
from fastapi import HTTPException, status
from datetime import date

from models.pricing_rule import PricingRule, RuleType
from schemas.pricing import PricingRequest, PricingResponse, AppliedRule

logger = logging.getLogger(__name__)


class PricingService:
    """Service for pricing calculations using safe attribute access"""
    
    def __init__(self, session: Session):
        self.session = session

    async def calculate_pricing(self, req: PricingRequest) -> PricingResponse:
        """
        Calculate pricing using pure Python evaluation - no subscripting of SQL expressions
        """
        logger.info(
            "Calculating pricing for service_type=%s, base_price=%s, pax_count=%s, start_date=%s",
            req.service_type, req.base_price, req.pax_count, req.start_date
        )
        
        # Input validation
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

        # Normalize to Decimal for precise calculations
        base_price = Decimal(str(req.base_price)).quantize(Decimal("0.01"))
        pax_count = int(req.pax_count)
        
        # === PRICING: RULE EVAL START ===
        # Fetch applicable rules using safe SQL filtering
        stmt = select(PricingRule).where(
            and_(
                PricingRule.is_active == True,
                # Service type filter - use OR for null (applies to all)
                (PricingRule.service_type == req.service_type) | (PricingRule.service_type.is_(None))
            )
        ).order_by(PricingRule.priority.asc(), PricingRule.id.asc())
        
        rules: List[PricingRule] = self.session.exec(stmt).all()
        logger.debug("Found %d potential pricing rules", len(rules))

        # Calculate subtotal
        subtotal = base_price * pax_count
        total_discount = Decimal("0.00")
        total_surcharge = Decimal("0.00")
        applied_rules: List[AppliedRule] = []

        # Apply rules using safe attribute access only
        for rule in rules:
            # Check applicability using model method (safe attribute access)
            if not rule.is_applicable(req.service_type, pax_count, req.start_date):
                continue

            # Calculate effect using safe attribute access
            effect_amount = self._calculate_rule_effect(rule, subtotal, pax_count)
            if effect_amount == 0:
                continue

            # Apply the effect
            if rule.rule_type in [RuleType.PERCENTAGE_DISCOUNT, RuleType.FLAT_DISCOUNT]:
                total_discount += effect_amount
            elif rule.rule_type in [RuleType.SURCHARGE_PERCENTAGE, RuleType.SURCHARGE_FLAT]:
                total_surcharge += effect_amount

            # Track applied rule
            applied_rules.append(AppliedRule(
                rule_id=rule.id,
                rule_name=rule.name,
                rule_type=rule.rule_type.value,
                effect_amount=effect_amount,
                description=rule.description
            ))

            logger.debug(
                "Applied rule %s (%s): %s %s",
                rule.name, rule.rule_type.value, 
                "+" if rule.rule_type.value.startswith("surcharge") else "-",
                effect_amount
            )

        # Calculate final totals
        total_discount = max(total_discount, Decimal("0.00"))
        total_surcharge = max(total_surcharge, Decimal("0.00"))
        final_total = (subtotal - total_discount + total_surcharge).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        
        # Ensure total is never negative
        final_total = max(final_total, Decimal("0.00"))
        # === PRICING: RULE EVAL END ===

        # === PRICING: RETURN DTO ===
        result = PricingResponse(
            base_price=base_price,
            pax_count=pax_count,
            subtotal=subtotal,
            discount_amount=total_discount,
            surcharge_amount=total_surcharge,
            total_price=final_total,
            currency=req.currency or "MAD",
            applied_rules=applied_rules
        )
        
        logger.info(
            "Pricing calculation complete: base=%s, subtotal=%s, discount=%s, surcharge=%s, total=%s",
            base_price, subtotal, total_discount, total_surcharge, final_total
        )
        
        return result

    def _calculate_rule_effect(self, rule: PricingRule, subtotal: Decimal, pax_count: int) -> Decimal:
        """Calculate the monetary effect of a pricing rule using safe attribute access"""
        try:
            if rule.rule_type == RuleType.PERCENTAGE_DISCOUNT:
                if rule.discount_percentage is not None:
                    return (subtotal * Decimal(str(rule.discount_percentage)) / Decimal("100")).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
            elif rule.rule_type == RuleType.FLAT_DISCOUNT:
                if rule.discount_amount is not None:
                    return Decimal(str(rule.discount_amount)).quantize(Decimal("0.01"))
            elif rule.rule_type == RuleType.SURCHARGE_PERCENTAGE:
                if rule.surcharge_percentage is not None:
                    return (subtotal * Decimal(str(rule.surcharge_percentage)) / Decimal("100")).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
            elif rule.rule_type == RuleType.SURCHARGE_FLAT:
                if rule.surcharge_amount is not None:
                    return Decimal(str(rule.surcharge_amount)).quantize(Decimal("0.01"))
            elif rule.rule_type == RuleType.GROUP_DISCOUNT:
                # Group discount based on passenger count
                if rule.discount_percentage is not None and pax_count >= (rule.min_pax or 1):
                    return (subtotal * Decimal(str(rule.discount_percentage)) / Decimal("100")).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
            elif rule.rule_type == RuleType.EARLY_BIRD:
                # Early bird discount - could be enhanced with booking date logic
                if rule.discount_percentage is not None:
                    return (subtotal * Decimal(str(rule.discount_percentage)) / Decimal("100")).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                    
        except (ValueError, TypeError, ArithmeticError) as e:
            logger.warning("Error calculating rule effect for rule %s: %s", rule.name, e)
            
        return Decimal("0.00")

    async def get_pricing_rules(self, service_type: Optional[str] = None) -> List[PricingRule]:
        """Get all active pricing rules, optionally filtered by service type"""
        stmt = select(PricingRule).where(PricingRule.is_active == True)
        
        if service_type:
            stmt = stmt.where(
                (PricingRule.service_type == service_type) | (PricingRule.service_type.is_(None))
            )
            
        stmt = stmt.order_by(PricingRule.priority.asc(), PricingRule.name.asc())
        
        return self.session.exec(stmt).all()

    async def create_pricing_rule(self, rule_data: dict) -> PricingRule:
        """Create a new pricing rule"""
        rule = PricingRule(**rule_data)
        self.session.add(rule)
        self.session.commit()
        self.session.refresh(rule)
        return rule

    async def update_pricing_rule(self, rule_id: UUID, rule_data: dict) -> PricingRule:
        """Update an existing pricing rule"""
        stmt = select(PricingRule).where(PricingRule.id == rule_id)
        rule = self.session.exec(stmt).first()
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pricing rule not found"
            )
        
        for field, value in rule_data.items():
            if hasattr(rule, field):
                setattr(rule, field, value)
        
        self.session.add(rule)
        self.session.commit()
        self.session.refresh(rule)
        return rule
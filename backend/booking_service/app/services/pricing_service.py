"""
Pricing service with fixed ORM attribute access
"""
import logging
from typing import List
from sqlmodel import Session, select, and_
from fastapi import HTTPException, status
from datetime import date, datetime
from decimal import Decimal

from models.pricing_rule import PricingRule, DiscountType
from schemas.pricing import PricingRequest, PricingCalculation, AppliedRule

logger = logging.getLogger(__name__)


class PricingService:
    """Service for handling pricing calculations"""
    
    def __init__(self, session: Session):
        self.session = session

    async def get_applicable_rules(
        self, 
        service_type: str, 
        pax_count: int, 
        start_date: date,
        base_price: float,
        customer_id: str = None
    ) -> List[PricingRule]:
        """Get applicable pricing rules using attribute access only"""
        
        # Build conditions using attribute access
        conditions = [
            PricingRule.is_active == True,
            PricingRule.valid_from <= date.today(),
            PricingRule.valid_until >= date.today(),
        ]
        
        # Service type filter
        if service_type:
            conditions.append(
                (PricingRule.service_type.is_(None)) | 
                (PricingRule.service_type == service_type)
            )
        
        # Passenger count filters
        conditions.append(
            (PricingRule.min_pax.is_(None)) | 
            (PricingRule.min_pax <= pax_count)
        )
        conditions.append(
            (PricingRule.max_pax.is_(None)) | 
            (PricingRule.max_pax >= pax_count)
        )
        
        # Amount filters
        conditions.append(
            (PricingRule.min_amount.is_(None)) | 
            (PricingRule.min_amount <= base_price)
        )
        conditions.append(
            (PricingRule.max_amount.is_(None)) | 
            (PricingRule.max_amount >= base_price)
        )
        
        # Date range filters
        if start_date:
            conditions.append(
                (PricingRule.start_date_from.is_(None)) | 
                (PricingRule.start_date_from <= start_date)
            )
            conditions.append(
                (PricingRule.start_date_to.is_(None)) | 
                (PricingRule.start_date_to >= start_date)
            )
        
        # Usage limits
        conditions.append(
            (PricingRule.max_uses.is_(None)) | 
            (PricingRule.current_uses < PricingRule.max_uses)
        )
        
        stmt = (
            select(PricingRule)
            .where(and_(*conditions))
            .order_by(PricingRule.priority.asc(), PricingRule.created_at.asc())
        )
        
        rules = self.session.exec(stmt).all()
        logger.info(f"Found {len(rules)} applicable pricing rules")
        
        return rules

    async def calculate_pricing(self, request: PricingRequest) -> PricingCalculation:
        """Calculate pricing with applied rules using attribute access"""
        
        logger.info(
            "Calculating pricing for service_type=%s, base_price=%s, pax_count=%s",
            request.service_type, request.base_price, request.pax_count
        )
        
        # Validate input
        if request.base_price < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Base price must be non-negative"
            )
        
        if request.pax_count < 1:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Passenger count must be at least 1"
            )
        
        # Get applicable rules
        try:
            rules = await self.get_applicable_rules(
                service_type=request.service_type,
                pax_count=request.pax_count,
                start_date=request.start_date,
                base_price=request.base_price,
                customer_id=str(request.customer_id) if request.customer_id else None
            )
        except Exception as e:
            logger.error(f"Failed to get pricing rules: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve pricing rules"
            )
        
        # Calculate pricing
        total_price = Decimal(str(request.base_price))
        total_discount = Decimal('0')
        applied_rules = []
        breakdown = []
        
        for rule in rules:
            try:
                # Use attribute access only - no subscripting
                discount_amount = self._calculate_rule_discount(rule, total_price, request.pax_count)
                
                if discount_amount > 0:
                    total_discount += discount_amount
                    total_price -= discount_amount
                    
                    # Create applied rule info
                    applied_rule = AppliedRule(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        discount_type=rule.discount_type.value,
                        discount_amount=float(discount_amount),
                        description=rule.description
                    )
                    applied_rules.append(applied_rule)
                    
                    breakdown.append({
                        "rule_name": rule.name,
                        "type": rule.discount_type.value,
                        "amount": float(discount_amount),
                        "description": rule.description
                    })
                    
                    logger.info(f"Applied rule '{rule.name}': -{discount_amount}")
                
            except Exception as e:
                logger.warning(f"Failed to apply rule '{rule.name}': {e}")
                continue
        
        # Ensure total price doesn't go negative
        if total_price < 0:
            total_price = Decimal('0')
        
        result = PricingCalculation(
            base_price=float(request.base_price),
            discount_amount=float(total_discount),
            total_price=float(total_price),
            applied_rules=applied_rules,
            currency=request.currency or "MAD",
            breakdown=breakdown
        )
        
        logger.info(
            "Pricing calculated: base=%s, discount=%s, total=%s",
            result.base_price, result.discount_amount, result.total_price
        )
        
        return result
    
    def _calculate_rule_discount(self, rule: PricingRule, current_price: Decimal, pax_count: int) -> Decimal:
        """Calculate discount for a single rule using attribute access"""
        
        # Use attribute access to get discount value
        if rule.discount_type == DiscountType.PERCENTAGE_DISCOUNT:
            if rule.discount_percentage is not None:
                return current_price * Decimal(str(rule.discount_percentage)) / Decimal('100')
        
        elif rule.discount_type == DiscountType.FLAT_DISCOUNT:
            if rule.discount_amount is not None:
                return Decimal(str(rule.discount_amount))
        
        elif rule.discount_type == DiscountType.GROUP_DISCOUNT:
            # Group discount based on passenger count
            if rule.discount_percentage is not None and pax_count >= (rule.min_pax or 1):
                return current_price * Decimal(str(rule.discount_percentage)) / Decimal('100')
        
        elif rule.discount_type == DiscountType.EARLY_BIRD:
            # Early bird discount - could check booking date vs start date
            if rule.discount_percentage is not None:
                return current_price * Decimal(str(rule.discount_percentage)) / Decimal('100')
        
        # If we need to access conditions JSON, do it safely after materialization
        if rule.conditions:
            conditions_dict = rule.conditions  # This is now a Python dict, safe to subscript
            # Example: threshold = conditions_dict.get("threshold", 0)
        
        return Decimal('0')
    
    async def validate_promo_code(self, promo_code: str, request: PricingRequest) -> Optional[PricingRule]:
        """Validate promotional code"""
        if not promo_code:
            return None
        
        stmt = select(PricingRule).where(
            PricingRule.code == promo_code,
            PricingRule.is_active == True,
            PricingRule.valid_from <= date.today(),
            PricingRule.valid_until >= date.today()
        )
        
        rule = self.session.exec(stmt).first()
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid or expired promo code: {promo_code}"
            )
        
        # Check usage limits using attribute access
        if rule.max_uses is not None and rule.current_uses >= rule.max_uses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Promo code '{promo_code}' has reached its usage limit"
            )
        
        # Check applicability using methods (which use attribute access)
        if not rule.is_applicable_for_pax(request.pax_count):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Promo code '{promo_code}' is not valid for {request.pax_count} passengers"
            )
        
        if not rule.is_applicable_for_amount(request.base_price):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Promo code '{promo_code}' is not valid for this price range"
            )
        
        if not rule.is_applicable_for_dates(request.start_date, date.today()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Promo code '{promo_code}' is not valid for the selected dates"
            )
        
        return rule
"""
Pricing service for calculating booking prices with discounts
"""
from sqlmodel import Session, select, and_, or_
from fastapi import HTTPException, status
from models.pricing_rule import PricingRule, DiscountType
from schemas.pricing import PricingContext, PricingCalculation, AppliedRule, PromoCodeResponse
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
import logging
import uuid

logger = logging.getLogger(__name__)


class PricingService:
    """Service for handling pricing calculations and discount rules"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def calculate_pricing(self, context: PricingContext) -> PricingCalculation:
        """Calculate pricing with applicable discounts"""
        logger.info(f"Calculating pricing for {context.service_type}, base_price={context.base_price}, pax_count={context.pax_count}")
        
        try:
            # Get applicable pricing rules
            applicable_rules = await self._get_applicable_rules(context)
            
            # Calculate discounts
            total_discount = Decimal('0')
            applied_rules = []
            
            for rule in applicable_rules:
                discount_amount = await self._calculate_rule_discount(rule, context)
                if discount_amount > 0:
                    total_discount += discount_amount
                    applied_rules.append(AppliedRule(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        discount_type=rule.discount_type.value,
                        discount_amount=discount_amount,
                        discount_percentage=rule.discount_percentage
                    ))
            
            # Calculate final price
            final_price = max(context.base_price - total_discount, Decimal('0'))
            
            result = PricingCalculation(
                base_price=context.base_price,
                discount_amount=total_discount,
                total_price=final_price,
                applied_rules=applied_rules,
                currency="MAD"
            )
            
            logger.info(f"Pricing calculated: base={result.base_price}, discount={result.discount_amount}, total={result.total_price}")
            return result
            
        except Exception as e:
            logger.error(f"Pricing calculation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to calculate pricing"
            )
    
    async def _get_applicable_rules(self, context: PricingContext) -> List[PricingRule]:
        """Get pricing rules applicable to the given context"""
        logger.debug(f"Finding applicable rules for context: service_type={context.service_type}, customer_id={context.customer_id}")
        
        # Build query conditions
        conditions = [
            PricingRule.is_active == True,
            PricingRule.valid_from <= context.start_date,
            or_(
                PricingRule.valid_until.is_(None),
                PricingRule.valid_until >= context.start_date
            )
        ]
        
        # Service type condition
        conditions.append(
            or_(
                PricingRule.conditions['service_type'].astext == context.service_type,
                PricingRule.conditions['service_type'].astext == 'ALL'
            )
        )
        
        # Promo code condition
        if context.promo_code:
            conditions.append(PricingRule.code == context.promo_code)
        
        # Build query
        query = select(PricingRule).where(and_(*conditions))
        
        # Execute query
        result = self.session.exec(query)
        rules = result.all()
        
        # Filter rules based on complex conditions
        applicable_rules = []
        for rule in rules:
            if await self._check_rule_conditions(rule, context):
                applicable_rules.append(rule)
        
        logger.debug(f"Found {len(applicable_rules)} applicable rules")
        return applicable_rules
    
    async def _check_rule_conditions(self, rule: PricingRule, context: PricingContext) -> bool:
        """Check if a rule's conditions are met"""
        conditions = rule.conditions or {}
        
        # Check minimum party size
        if 'min_party_size' in conditions:
            if context.pax_count < conditions['min_party_size']:
                return False
        
        # Check maximum party size
        if 'max_party_size' in conditions:
            if context.pax_count > conditions['max_party_size']:
                return False
        
        # Check minimum booking value
        if 'min_booking_value' in conditions:
            if context.base_price < Decimal(str(conditions['min_booking_value'])):
                return False
        
        # Check customer loyalty status (would need CRM integration)
        if 'loyalty_status' in conditions and context.customer_id:
            # TODO: Integrate with CRM service to check customer loyalty
            pass
        
        # Check usage limits
        if rule.max_uses and rule.current_uses >= rule.max_uses:
            return False
        
        # Check per-customer usage limits
        if rule.max_uses_per_customer and context.customer_id:
            # TODO: Check customer-specific usage
            pass
        
        return True
    
    async def _calculate_rule_discount(self, rule: PricingRule, context: PricingContext) -> Decimal:
        """Calculate discount amount for a specific rule"""
        if rule.discount_type == DiscountType.PERCENTAGE:
            if rule.discount_percentage:
                discount = context.base_price * (rule.discount_percentage / 100)
                return min(discount, context.base_price)
        
        elif rule.discount_type == DiscountType.FIXED_AMOUNT:
            if rule.discount_amount:
                return min(rule.discount_amount, context.base_price)
        
        elif rule.discount_type == DiscountType.GROUP_DISCOUNT:
            # Group discount based on party size
            if context.pax_count >= 5 and rule.discount_percentage:
                discount = context.base_price * (rule.discount_percentage / 100)
                return min(discount, context.base_price)
        
        elif rule.discount_type == DiscountType.EARLY_BIRD:
            # Early bird discount based on booking advance
            days_advance = (context.start_date - date.today()).days
            if days_advance >= 30 and rule.discount_percentage:
                discount = context.base_price * (rule.discount_percentage / 100)
                return min(discount, context.base_price)
        
        return Decimal('0')
    
    async def validate_promo_code(self, promo_code: str, context: PricingContext) -> PromoCodeResponse:
        """Validate a promotional code"""
        logger.info(f"Validating promo code: {promo_code}")
        
        # Find promo code rule
        query = select(PricingRule).where(
            and_(
                PricingRule.code == promo_code,
                PricingRule.is_active == True,
                PricingRule.valid_from <= context.start_date,
                or_(
                    PricingRule.valid_until.is_(None),
                    PricingRule.valid_until >= context.start_date
                )
            )
        )
        
        result = self.session.exec(query)
        rule = result.first()
        
        if not rule:
            return PromoCodeResponse(
                valid=False,
                message="Invalid or expired promo code"
            )
        
        # Check rule conditions
        if not await self._check_rule_conditions(rule, context):
            return PromoCodeResponse(
                valid=False,
                message="Promo code conditions not met"
            )
        
        # Calculate discount
        discount_amount = await self._calculate_rule_discount(rule, context)
        
        return PromoCodeResponse(
            valid=True,
            discount_amount=discount_amount,
            discount_percentage=rule.discount_percentage,
            message="Promo code applied successfully",
            rule_name=rule.name
        )
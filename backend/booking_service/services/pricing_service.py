"""
Pricing service for calculating booking prices with discounts
"""
from sqlmodel import Session, select, and_, or_
from fastapi import HTTPException, status
from models.pricing_rule import PricingRule
from schemas.pricing import PricingContext, PricingCalculation, AppliedRule
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class PricingService:
    """Service for handling pricing calculations and rule management"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def calculate_pricing(self, context: PricingContext) -> PricingCalculation:
        """Calculate pricing with applicable discounts using unified context"""
        logger.debug(f"Calculating pricing for context: {context.service_type}, {context.pax_count} pax, {context.base_price} base")
        
        # Get applicable rules
        applicable_rules = await self._get_applicable_rules(context)
        
        # Calculate discounts
        total_discount = Decimal('0.00')
        applied_rules = []
        
        for rule in applicable_rules:
            discount_amount = self._calculate_rule_discount(rule, context)
            if discount_amount > 0:
                total_discount += discount_amount
                applied_rules.append(AppliedRule(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    discount_type=rule.discount_type,
                    discount_amount=discount_amount,
                    discount_percentage=rule.discount_percentage
                ))
                
                # Update rule usage
                rule.current_uses += 1
                self.session.add(rule)
        
        # Calculate final price
        final_price = max(context.base_price - total_discount, Decimal('0.00'))
        
        # Commit rule usage updates
        self.session.commit()
        
        calculation = PricingCalculation(
            base_price=context.base_price,
            discount_amount=total_discount,
            total_price=final_price,
            applied_rules=applied_rules,
            currency="MAD",
            calculation_details={
                "service_type": context.service_type,
                "pax_count": context.pax_count,
                "start_date": context.start_date.isoformat(),
                "rules_evaluated": len(applicable_rules),
                "rules_applied": len(applied_rules)
            }
        )
        
        logger.info(f"Pricing calculated: {context.base_price} -> {final_price} (discount: {total_discount})")
        return calculation
    
    async def _get_applicable_rules(self, context: PricingContext) -> List[PricingRule]:
        """Get pricing rules applicable to the given context"""
        logger.debug(f"Finding applicable rules for: {context.service_type}, customer: {context.customer_id}")
        
        # Base query for active rules within date range
        query = select(PricingRule).where(
            and_(
                PricingRule.is_active == True,
                PricingRule.valid_from <= context.start_date,
                PricingRule.valid_until >= context.start_date
            )
        )
        
        # Check usage limits
        query = query.where(
            or_(
                PricingRule.max_uses.is_(None),
                PricingRule.current_uses < PricingRule.max_uses
            )
        )
        
        # Order by priority (higher priority first)
        query = query.order_by(PricingRule.priority.desc())
        
        rules = self.session.exec(query).all()
        
        # Filter rules based on conditions
        applicable_rules = []
        for rule in rules:
            if self._rule_matches_context(rule, context):
                applicable_rules.append(rule)
                logger.debug(f"Rule '{rule.name}' is applicable")
            else:
                logger.debug(f"Rule '{rule.name}' conditions not met")
        
        logger.debug(f"Found {len(applicable_rules)} applicable rules out of {len(rules)} total")
        return applicable_rules
    
    def _rule_matches_context(self, rule: PricingRule, context: PricingContext) -> bool:
        """Check if a pricing rule matches the given context"""
        conditions = rule.get_conditions_dict()
        
        # Check passenger count
        if conditions.get('min_pax_count') and context.pax_count < conditions['min_pax_count']:
            return False
        if conditions.get('max_pax_count') and context.pax_count > conditions['max_pax_count']:
            return False
        
        # Check service types
        valid_service_types = conditions.get('valid_service_types')
        if valid_service_types and context.service_type not in valid_service_types:
            return False
        
        # Check customer-specific rules
        valid_customers = conditions.get('valid_customers')
        if valid_customers and context.customer_id:
            if str(context.customer_id) not in [str(c) for c in valid_customers]:
                return False
        
        # Check advance booking days
        if context.start_date and conditions.get('min_advance_days'):
            advance_days = (context.start_date - date.today()).days
            if advance_days < conditions['min_advance_days']:
                return False
        
        # Check booking value
        if conditions.get('min_booking_value') and context.base_price < conditions['min_booking_value']:
            return False
        if conditions.get('max_booking_value') and context.base_price > conditions['max_booking_value']:
            return False
        
        return True
    
    def _calculate_rule_discount(self, rule: PricingRule, context: PricingContext) -> Decimal:
        """Calculate discount amount for a specific rule"""
        if rule.discount_type == "Percentage":
            if rule.discount_percentage:
                return context.base_price * (rule.discount_percentage / 100)
        elif rule.discount_type == "Fixed Amount":
            if rule.discount_amount:
                return min(rule.discount_amount, context.base_price)
        elif rule.discount_type == "Group Discount":
            # Group discount based on passenger count
            if context.pax_count >= 10 and rule.discount_percentage:
                return context.base_price * (rule.discount_percentage / 100)
        elif rule.discount_type == "Early Bird":
            # Early bird discount based on advance booking
            if context.start_date:
                advance_days = (context.start_date - date.today()).days
                if advance_days >= 30 and rule.discount_percentage:
                    return context.base_price * (rule.discount_percentage / 100)
        
        return Decimal('0.00')
    
    async def validate_promo_code(self, promo_code: str, context: PricingContext) -> Optional[PricingRule]:
        """Validate and return pricing rule for promo code"""
        if not promo_code:
            return None
        
        query = select(PricingRule).where(
            and_(
                PricingRule.code == promo_code.upper(),
                PricingRule.is_active == True,
                PricingRule.valid_from <= context.start_date,
                PricingRule.valid_until >= context.start_date
            )
        )
        
        rule = self.session.exec(query).first()
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired promo code"
            )
        
        # Check usage limits
        if rule.max_uses and rule.current_uses >= rule.max_uses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Promo code usage limit exceeded"
            )
        
        # Check if rule matches context
        if not self._rule_matches_context(rule, context):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Promo code not applicable to this booking"
            )
        
        return rule
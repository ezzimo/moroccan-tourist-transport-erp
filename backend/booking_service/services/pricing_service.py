"""
Pricing service with robust error handling and input validation
"""
from sqlmodel import Session, select, and_, or_
from fastapi import HTTPException, status
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import List, Optional
from datetime import date, datetime
import logging

from models.pricing_rule import PricingRule as PricingRuleModel
from schemas.pricing import PricingRequest, PricingCalculation, PricingContext, PricingRule
from utils.currency import format_currency, validate_currency_amount

logger = logging.getLogger(__name__)


class PricingValidationError(Exception):
    """Custom exception for pricing validation errors"""
    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class PricingService:
    """Service for handling pricing calculations with robust error handling"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def calculate_pricing(self, request: PricingRequest) -> PricingCalculation:
        """
        Calculate pricing with applied discounts and rules
        
        Args:
            request: Validated pricing request
            
        Returns:
            PricingCalculation with base price, discounts, and total
            
        Raises:
            PricingValidationError: For validation issues
            HTTPException: For system errors
        """
        try:
            # Handle both dict and PricingRequest objects for backward compatibility
            if isinstance(request, dict):
                from schemas.pricing import PricingRequest
                request = PricingRequest(**request)
            
            logger.info(f"Calculating pricing for service_type={request.service_type}, base_price={request.base_price}, pax_count={request.pax_count}")
            
            # Convert request to internal context
            context = PricingContext.from_request(request)
            
            # Validate business rules
            self._validate_pricing_context(context)
            
            # Get applicable pricing rules
            applicable_rules = await self._get_applicable_rules(context)
            
            # Calculate discounts
            total_discount = Decimal('0')
            applied_rules = []
            
            for rule in applicable_rules:
                try:
                    discount = self._calculate_rule_discount(rule, context)
                    if discount > 0:
                        total_discount += discount
                        applied_rules.append(PricingRule(
                            rule_id=rule.id,
                            rule_name=rule.name,
                            discount_type=rule.discount_type,
                            discount_amount=discount
                        ))
                except Exception as e:
                    logger.warning(f"Failed to apply pricing rule {rule.id}: {e}")
                    continue
            
            
            # Calculate final price
            final_price = max(context.base_price - total_discount, Decimal('0'))
            
            # Quantize to currency precision
            base_price = context.base_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            discount_amount = total_discount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            total_price = final_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            
            result = PricingCalculation(
                base_price=base_price,
                discount_amount=discount_amount,
                total_price=total_price,
                applied_rules=applied_rules,
                currency="MAD"
            )
            
            logger.info(f"Pricing calculation successful: base={base_price}, discount={discount_amount}, total={total_price}")
            return result
            
        except PricingValidationError:
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in pricing calculation: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal error during pricing calculation"
            )
    
    def _validate_pricing_context(self, context: PricingContext) -> None:
        """Validate pricing context for business rules"""
        
        # Validate service type
        valid_service_types = ['Tour', 'Transfer', 'Custom Package', 'Accommodation', 'Activity']
        if context.service_type not in valid_service_types:
            raise PricingValidationError(
                f"Invalid service type. Must be one of: {', '.join(valid_service_types)}",
                "INVALID_SERVICE_TYPE"
            )
        
        # Validate base price
        if context.base_price <= 0:
            raise PricingValidationError(
                "Base price must be greater than zero",
                "INVALID_BASE_PRICE"
            )
        
        if context.base_price > Decimal('999999.99'):
            raise PricingValidationError(
                "Base price exceeds maximum allowed amount",
                "BASE_PRICE_TOO_HIGH"
            )
        
        # Validate passenger count
        if context.pax_count < 1 or context.pax_count > 50:
            raise PricingValidationError(
                "Passenger count must be between 1 and 50",
                "INVALID_PAX_COUNT"
            )
        
        # Validate dates
        if context.start_date < date.today():
            raise PricingValidationError(
                "Start date cannot be in the past",
                "INVALID_START_DATE"
            )
        
        if context.end_date and context.end_date < context.start_date:
            raise PricingValidationError(
                "End date must be after start date",
                "INVALID_END_DATE"
            )
    
    async def _get_applicable_rules(self, context: PricingContext) -> List[PricingRuleModel]:
        """
        Get pricing rules applicable to the given context
        
        Args:
            context: Pricing context
            
        Returns:
            List of applicable pricing rules
        """
        try:
            # Build query for active rules
            query = select(PricingRuleModel).where(
                and_(
                    PricingRuleModel.is_active == True,
                    PricingRuleModel.valid_from <= context.start_date,
                    or_(
                        PricingRuleModel.valid_until.is_(None),
                        PricingRuleModel.valid_until >= context.start_date
                    )
                )
            ).order_by(PricingRuleModel.priority.desc())
            
            rules = self.session.exec(query).all()
            
            # Filter rules based on conditions (done in Python to avoid SQL JSON issues)
            applicable_rules = []
            for rule in rules:
                try:
                    if self._rule_applies_to_context(rule, context):
                        applicable_rules.append(rule)
                except Exception as e:
                    logger.warning(f"Error checking rule {rule.id} applicability: {e}")
                    continue
            
            logger.info(f"Found {len(applicable_rules)} applicable pricing rules")
            return applicable_rules
            
        except Exception as e:
            logger.exception(f"Error retrieving pricing rules: {e}")
            return []
    
    def _rule_applies_to_context(self, rule: PricingRuleModel, context: PricingContext) -> bool:
        """
        Check if a pricing rule applies to the given context
        
        Args:
            rule: Pricing rule to check
            context: Pricing context
            
        Returns:
            True if rule applies, False otherwise
        """
        try:
            # Parse rule conditions safely
            conditions = rule.conditions or {}
            
            # Check service type condition
            if 'service_types' in conditions:
                allowed_types = conditions['service_types']
                if isinstance(allowed_types, list) and context.service_type not in allowed_types:
                    return False
            
            # Check minimum passenger count
            if 'min_pax_count' in conditions:
                min_pax = conditions['min_pax_count']
                if isinstance(min_pax, (int, float)) and context.pax_count < min_pax:
                    return False
            
            # Check minimum base price
            if 'min_base_price' in conditions:
                min_price = conditions['min_base_price']
                if isinstance(min_price, (int, float)) and context.base_price < Decimal(str(min_price)):
                    return False
            
            # Check customer loyalty (if customer_id provided)
            if 'customer_loyalty_levels' in conditions and context.customer_id:
                # This would require a call to CRM service to get customer loyalty level
                # For now, we'll skip this check to avoid service dependencies
                pass
            
            # Check usage limits
            if rule.max_uses and rule.current_uses >= rule.max_uses:
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Error evaluating rule conditions for rule {rule.id}: {e}")
            return False
    
    def _calculate_rule_discount(self, rule: PricingRuleModel, context: PricingContext) -> Decimal:
        """
        Calculate discount amount for a specific rule
        
        Args:
            rule: Pricing rule
            context: Pricing context
            
        Returns:
            Discount amount as Decimal
        """
        try:
            discount = Decimal('0')
            
            if rule.discount_type == 'Percentage':
                if rule.discount_percentage:
                    percentage = Decimal(str(rule.discount_percentage)) / Decimal('100')
                    discount = context.base_price * percentage
            
            elif rule.discount_type == 'Fixed Amount':
                if rule.discount_amount:
                    discount = Decimal(str(rule.discount_amount))
            
            elif rule.discount_type == 'Group Discount':
                # Apply group discount based on passenger count
                conditions = rule.conditions or {}
                group_threshold = conditions.get('group_threshold', 10)
                if context.pax_count >= group_threshold and rule.discount_percentage:
                    percentage = Decimal(str(rule.discount_percentage)) / Decimal('100')
                    discount = context.base_price * percentage
            
            elif rule.discount_type == 'Early Bird':
                # Apply early bird discount based on booking advance
                conditions = rule.conditions or {}
                advance_days = conditions.get('advance_days', 30)
                days_in_advance = (context.start_date - date.today()).days
                if days_in_advance >= advance_days and rule.discount_percentage:
                    percentage = Decimal(str(rule.discount_percentage)) / Decimal('100')
                    discount = context.base_price * percentage
            
            # Ensure discount doesn't exceed base price
            discount = min(discount, context.base_price)
            
            return discount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
        except Exception as e:
            logger.warning(f"Error calculating discount for rule {rule.id}: {e}")
            return Decimal('0')
    
    async def validate_promo_code(self, promo_code: str, context: PricingContext) -> dict:
        """
        Validate a promotional code
        
        Args:
            promo_code: Promotional code to validate
            context: Pricing context
            
        Returns:
            Validation result with discount information
        """
        try:
            if not promo_code or not promo_code.strip():
                return {
                    "valid": False,
                    "message": "Promo code is required"
                }
            
            # Find promo code rule
            query = select(PricingRuleModel).where(
                and_(
                    PricingRuleModel.code == promo_code.strip().upper(),
                    PricingRuleModel.is_active == True,
                    PricingRuleModel.valid_from <= context.start_date,
                    or_(
                        PricingRuleModel.valid_until.is_(None),
                        PricingRuleModel.valid_until >= context.start_date
                    )
                )
            )
            
            rule = self.session.exec(query).first()
            
            if not rule:
                return {
                    "valid": False,
                    "message": "Invalid or expired promo code"
                }
            
            # Check usage limits
            if rule.max_uses and rule.current_uses >= rule.max_uses:
                return {
                    "valid": False,
                    "message": "Promo code usage limit exceeded"
                }
            
            # Check if rule applies to context
            if not self._rule_applies_to_context(rule, context):
                return {
                    "valid": False,
                    "message": "Promo code not applicable to this booking"
                }
            
            # Calculate discount
            discount_amount = self._calculate_rule_discount(rule, context)
            
            return {
                "valid": True,
                "discount_amount": float(discount_amount),
                "message": f"Promo code applied: {rule.name}"
            }
            
        except Exception as e:
            logger.exception(f"Error validating promo code {promo_code}: {e}")
            return {
                "valid": False,
                "message": "Error validating promo code"
            }
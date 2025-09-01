"""
Pricing service with fixed SQLAlchemy queries
"""
from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException, status
from models.pricing_rule import PricingRule
from schemas.pricing import PricingRequest, PricingCalculation, PricingRuleResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class PricingService:
    """Service for handling pricing calculations and discount rules"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def calculate_pricing(self, request: PricingRequest) -> PricingCalculation:
        """Calculate pricing with applicable discounts"""
        try:
            logger.info(f"Calculating pricing for: {request.service_type}, {request.pax_count} pax, base: {request.base_price}")
            
            # Validate input
            if request.base_price <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Base price must be greater than 0"
                )
            
            if request.pax_count <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Passenger count must be greater than 0"
                )
            
            # Parse dates
            start_date = self._parse_date(request.start_date)
            end_date = self._parse_date(request.end_date) if request.end_date else None
            
            # Get applicable pricing rules
            applicable_rules = self._get_applicable_rules(
                service_type=request.service_type,
                pax_count=request.pax_count,
                start_date=start_date,
                end_date=end_date,
                customer_id=request.customer_id,
                promo_code=request.promo_code
            )
            
            logger.info(f"Found {len(applicable_rules)} applicable pricing rules")
            
            # Calculate base amount
            base_amount = Decimal(str(request.base_price)) * Decimal(str(request.pax_count))
            
            # Apply discounts
            total_discount = Decimal('0')
            applied_rules = []
            
            for rule in applicable_rules:
                discount_amount = self._calculate_rule_discount(rule, base_amount, request)
                if discount_amount > 0:
                    total_discount += discount_amount
                    applied_rules.append({
                        "rule_id": str(rule.id),
                        "rule_name": rule.name,
                        "discount_type": rule.discount_type,
                        "discount_amount": float(discount_amount)
                    })
                    
                    logger.info(f"Applied rule '{rule.name}': -{discount_amount}")
                    
                    # Update rule usage
                    rule.current_uses += 1
                    self.session.add(rule)
            
            # Calculate final price
            final_price = max(base_amount - total_discount, Decimal('0'))
            
            # Commit rule usage updates
            self.session.commit()
            
            result = PricingCalculation(
                base_price=float(base_amount),
                discount_amount=float(total_discount),
                total_price=float(final_price),
                applied_rules=applied_rules,
                currency="MAD"
            )
            
            logger.info(f"Pricing calculation complete: {result.total_price} MAD (discount: {result.discount_amount})")
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Pricing calculation failed: {e}")
            logger.error(f"Request data: {request}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Pricing calculation failed: {str(e)}"
            )
    
    def _get_applicable_rules(
        self,
        service_type: str,
        pax_count: int,
        start_date: date,
        end_date: Optional[date] = None,
        customer_id: Optional[str] = None,
        promo_code: Optional[str] = None
    ) -> List[PricingRule]:
        """Get applicable pricing rules with fixed SQLAlchemy queries"""
        try:
            # Build base query with proper SQLAlchemy syntax
            query = select(PricingRule).where(
                and_(
                    PricingRule.is_active == True,
                    PricingRule.valid_from <= start_date,
                    or_(
                        PricingRule.valid_until.is_(None),
                        PricingRule.valid_until >= start_date
                    )
                )
            )
            
            # Add max uses filter - FIXED: Use proper SQLAlchemy comparison
            query = query.where(
                or_(
                    PricingRule.max_uses.is_(None),
                    PricingRule.current_uses < PricingRule.max_uses
                )
            )
            
            # Add promo code filter if provided
            if promo_code:
                query = query.where(
                    or_(
                        PricingRule.code.is_(None),
                        PricingRule.code == promo_code
                    )
                )
            
            # Execute query
            result = self.session.exec(query)
            rules = result.all()
            
            logger.info(f"Found {len(rules)} potential rules before condition filtering")
            
            # Filter by conditions (JSON-based filtering)
            applicable_rules = []
            for rule in rules:
                if self._check_rule_conditions(rule, service_type, pax_count, customer_id):
                    applicable_rules.append(rule)
            
            # Sort by priority (higher priority first)
            applicable_rules.sort(key=lambda r: r.priority, reverse=True)
            
            logger.info(f"Final applicable rules: {len(applicable_rules)}")
            return applicable_rules
            
        except Exception as e:
            logger.error(f"Error getting applicable rules: {e}")
            # Return empty list on error to allow pricing to continue
            return []
    
    def _check_rule_conditions(
        self, 
        rule: PricingRule, 
        service_type: str, 
        pax_count: int, 
        customer_id: Optional[str] = None
    ) -> bool:
        """Check if rule conditions are met"""
        try:
            if not rule.conditions:
                return True
            
            conditions = rule.conditions
            
            # Check service type condition
            if 'service_types' in conditions:
                allowed_types = conditions['service_types']
                if isinstance(allowed_types, list) and service_type not in allowed_types:
                    return False
            
            # Check passenger count conditions
            if 'min_passengers' in conditions:
                if pax_count < conditions['min_passengers']:
                    return False
            
            if 'max_passengers' in conditions:
                if pax_count > conditions['max_passengers']:
                    return False
            
            # Check customer-specific conditions
            if customer_id and 'customer_segments' in conditions:
                # In a real implementation, you'd check customer segments
                # For now, we'll assume all customers are eligible
                pass
            
            return True
            
        except Exception as e:
            logger.warning(f"Error checking rule conditions for rule {rule.id}: {e}")
            return False
    
    def _calculate_rule_discount(
        self, 
        rule: PricingRule, 
        base_amount: Decimal, 
        request: PricingRequest
    ) -> Decimal:
        """Calculate discount amount for a specific rule"""
        try:
            if rule.discount_type == "Percentage":
                if rule.discount_percentage:
                    discount = base_amount * (Decimal(str(rule.discount_percentage)) / Decimal('100'))
                    return min(discount, base_amount)
            
            elif rule.discount_type == "Fixed Amount":
                if rule.discount_amount:
                    discount = Decimal(str(rule.discount_amount))
                    return min(discount, base_amount)
            
            elif rule.discount_type == "Group Discount":
                # Apply group discount based on passenger count
                if request.pax_count >= 10:
                    discount_percentage = Decimal('15')  # 15% for groups of 10+
                elif request.pax_count >= 6:
                    discount_percentage = Decimal('10')  # 10% for groups of 6+
                else:
                    return Decimal('0')
                
                discount = base_amount * (discount_percentage / Decimal('100'))
                return min(discount, base_amount)
            
            elif rule.discount_type == "Early Bird":
                # Apply early bird discount if booking is made in advance
                booking_date = datetime.now().date()
                start_date = self._parse_date(request.start_date)
                days_in_advance = (start_date - booking_date).days
                
                if days_in_advance >= 30:  # 30 days in advance
                    discount_percentage = Decimal('20')  # 20% early bird
                    discount = base_amount * (discount_percentage / Decimal('100'))
                    return min(discount, base_amount)
            
            return Decimal('0')
            
        except Exception as e:
            logger.warning(f"Error calculating discount for rule {rule.id}: {e}")
            return Decimal('0')
    
    def _parse_date(self, date_str: str) -> date:
        """Parse date string to date object"""
        try:
            if isinstance(date_str, str):
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            return date_str
        except ValueError as e:
            logger.error(f"Invalid date format: {date_str}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid date format: {date_str}. Expected YYYY-MM-DD"
            )
    
    def get_pricing_rules(self, skip: int = 0, limit: int = 100) -> List[PricingRuleResponse]:
        """Get all pricing rules"""
        try:
            query = select(PricingRule).offset(skip).limit(limit).order_by(PricingRule.priority.desc())
            result = self.session.exec(query)
            rules = result.all()
            
            return [PricingRuleResponse.model_validate(rule) for rule in rules]
            
        except Exception as e:
            logger.error(f"Error getting pricing rules: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve pricing rules"
            )
    
    def create_pricing_rule(self, rule_data: Dict[str, Any]) -> PricingRuleResponse:
        """Create a new pricing rule"""
        try:
            # Validate rule data
            if not rule_data.get('name'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rule name is required"
                )
            
            # Check for duplicate names
            existing_query = select(PricingRule).where(PricingRule.name == rule_data['name'])
            existing_result = self.session.exec(existing_query)
            if existing_result.first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A pricing rule with this name already exists"
                )
            
            # Create rule
            rule = PricingRule(**rule_data)
            self.session.add(rule)
            self.session.commit()
            self.session.refresh(rule)
            
            logger.info(f"Created pricing rule: {rule.name}")
            return PricingRuleResponse.model_validate(rule)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating pricing rule: {e}")
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create pricing rule"
            )
    
    def validate_promo_code(
        self, 
        promo_code: str, 
        booking_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate a promo code and return discount information"""
        try:
            # Find promo code rule
            query = select(PricingRule).where(
                and_(
                    PricingRule.code == promo_code,
                    PricingRule.is_active == True,
                    PricingRule.valid_from <= datetime.now().date(),
                    or_(
                        PricingRule.valid_until.is_(None),
                        PricingRule.valid_until >= datetime.now().date()
                    )
                )
            )
            
            result = self.session.exec(query)
            rule = result.first()
            
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
            
            # Calculate potential discount
            base_amount = Decimal(str(booking_data.get('base_price', 0))) * Decimal(str(booking_data.get('pax_count', 1)))
            
            # Create a temporary pricing request for calculation
            temp_request = PricingRequest(
                service_type=booking_data.get('service_type', 'Tour'),
                base_price=booking_data.get('base_price', 0),
                pax_count=booking_data.get('pax_count', 1),
                start_date=booking_data.get('start_date', datetime.now().date().isoformat()),
                promo_code=promo_code
            )
            
            discount_amount = self._calculate_rule_discount(rule, base_amount, temp_request)
            
            return {
                "valid": True,
                "discount_amount": float(discount_amount),
                "message": f"Promo code applied: {rule.name}"
            }
            
        except Exception as e:
            logger.error(f"Error validating promo code: {e}")
            return {
                "valid": False,
                "message": "Error validating promo code"
            }
"""
Pricing service for dynamic pricing and discount calculations
"""
from sqlmodel import Session, select
from models.booking import PricingRule, DiscountType
from schemas.booking import PricingRequest, PricingResponse
from typing import List, Dict, Any
from decimal import Decimal
from datetime import date
import uuid


class PricingService:
    """Service for handling pricing calculations and discount applications"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def calculate_pricing(self, pricing_request: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate final pricing with applicable discounts"""
        base_price = Decimal(str(pricing_request["base_price"]))
        pax_count = pricing_request["pax_count"]
        service_type = pricing_request["service_type"]
        start_date = pricing_request["start_date"]
        customer_id = pricing_request.get("customer_id")
        promo_code = pricing_request.get("promo_code")
        
        # Get applicable pricing rules
        applicable_rules = await self._get_applicable_rules(
            service_type=service_type,
            start_date=start_date,
            base_price=base_price,
            pax_count=pax_count,
            promo_code=promo_code
        )
        
        # Calculate discounts
        total_discount = Decimal(0)
        applied_rules = []
        
        for rule in applicable_rules:
            discount_amount = rule.calculate_discount(base_price, pax_count)
            
            if discount_amount > 0:
                total_discount += discount_amount
                applied_rules.append({
                    "rule_id": str(rule.id),
                    "rule_name": rule.name,
                    "discount_type": rule.discount_type.value,
                    "discount_amount": float(discount_amount)
                })
                
                # Update rule usage
                rule.current_uses += 1
                self.session.add(rule)
        
        # Ensure discount doesn't exceed base price
        if total_discount > base_price:
            total_discount = base_price
        
        final_price = base_price - total_discount
        
        # Commit rule usage updates
        self.session.commit()
        
        return {
            "base_price": base_price,
            "discount_amount": total_discount,
            "total_price": final_price,
            "applied_rules": applied_rules,
            "currency": "MAD"
        }
    
    async def _get_applicable_rules(
        self,
        service_type: str,
        start_date: date,
        base_price: Decimal,
        pax_count: int,
        promo_code: str = None
    ) -> List[PricingRule]:
        """Get all applicable pricing rules"""
        query = select(PricingRule).where(
            PricingRule.is_active == True,
            PricingRule.valid_from <= date.today(),
            PricingRule.valid_until >= date.today()
        )
        
        # Add promo code filter if provided
        if promo_code:
            query = query.where(PricingRule.code == promo_code)
        
        # Order by priority (higher priority first)
        query = query.order_by(PricingRule.priority.desc())
        
        all_rules = self.session.exec(query).all()
        
        # Filter rules that can apply to this booking
        applicable_rules = []
        booking_data = {
            "service_type": service_type,
            "start_date": start_date,
            "base_price": base_price,
            "pax_count": pax_count
        }
        
        for rule in all_rules:
            if rule.can_apply_to_booking(booking_data):
                applicable_rules.append(rule)
                
                # If rule is not combinable, stop here
                if not rule.is_combinable:
                    break
        
        return applicable_rules
    
    async def create_pricing_rule(self, rule_data: Dict[str, Any]) -> PricingRule:
        """Create a new pricing rule"""
        rule = PricingRule(**rule_data)
        rule.set_conditions_dict(rule_data["conditions"])
        
        self.session.add(rule)
        self.session.commit()
        self.session.refresh(rule)
        
        return rule
    
    async def update_pricing_rule(self, rule_id: uuid.UUID, rule_data: Dict[str, Any]) -> PricingRule:
        """Update an existing pricing rule"""
        statement = select(PricingRule).where(PricingRule.id == rule_id)
        rule = self.session.exec(statement).first()
        
        if not rule:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pricing rule not found"
            )
        
        # Update fields
        for field, value in rule_data.items():
            if field == "conditions":
                rule.set_conditions_dict(value)
            else:
                setattr(rule, field, value)
        
        self.session.add(rule)
        self.session.commit()
        self.session.refresh(rule)
        
        return rule
    
    async def validate_promo_code(self, promo_code: str, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a promo code and return discount information"""
        statement = select(PricingRule).where(
            PricingRule.code == promo_code,
            PricingRule.is_active == True
        )
        
        rule = self.session.exec(statement).first()
        
        if not rule:
            return {
                "valid": False,
                "message": "Invalid promo code"
            }
        
        if not rule.is_valid_now():
            return {
                "valid": False,
                "message": "Promo code has expired or reached usage limit"
            }
        
        if not rule.can_apply_to_booking(booking_data):
            return {
                "valid": False,
                "message": "Promo code is not applicable to this booking"
            }
        
        discount_amount = rule.calculate_discount(
            Decimal(str(booking_data["base_price"])),
            booking_data["pax_count"]
        )
        
        return {
            "valid": True,
            "rule_name": rule.name,
            "discount_type": rule.discount_type.value,
            "discount_amount": float(discount_amount),
            "message": f"Promo code applied: {rule.name}"
        }
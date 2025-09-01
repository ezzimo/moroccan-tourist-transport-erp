"""
Tests for pricing functionality
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from services.pricing_service import PricingService
from schemas.pricing import PricingContext, PricingRequest
from models.pricing_rule import PricingRule
import uuid


class TestPricingService:
    """Test class for pricing service operations"""
    
    @pytest.mark.asyncio
    async def test_basic_pricing_calculation(self, session):
        """Test basic pricing calculation without discounts"""
        pricing_service = PricingService(session)
        
        context = PricingContext(
            service_type="Tour",
            base_price=Decimal('1000.00'),
            pax_count=4,
            start_date=date.today() + timedelta(days=30)
        )
        
        calculation = await pricing_service.calculate_pricing(context)
        
        assert calculation.base_price == Decimal('1000.00')
        assert calculation.discount_amount == Decimal('0.00')
        assert calculation.total_price == Decimal('1000.00')
        assert calculation.currency == "MAD"
        assert len(calculation.applied_rules) == 0
    
    @pytest.mark.asyncio
    async def test_percentage_discount_rule(self, session):
        """Test pricing calculation with percentage discount"""
        pricing_service = PricingService(session)
        
        # Create a test discount rule
        rule = PricingRule(
            name="Early Bird 10%",
            description="10% discount for early bookings",
            discount_type="Percentage",
            discount_percentage=Decimal('10.00'),
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=365),
            is_active=True,
            conditions='{"min_advance_days": 14}'
        )
        session.add(rule)
        session.commit()
        session.refresh(rule)
        
        context = PricingContext(
            service_type="Tour",
            base_price=Decimal('1000.00'),
            pax_count=4,
            start_date=date.today() + timedelta(days=30)  # 30 days advance
        )
        
        calculation = await pricing_service.calculate_pricing(context)
        
        assert calculation.base_price == Decimal('1000.00')
        assert calculation.discount_amount == Decimal('100.00')  # 10% of 1000
        assert calculation.total_price == Decimal('900.00')
        assert len(calculation.applied_rules) == 1
        assert calculation.applied_rules[0].rule_name == "Early Bird 10%"
    
    @pytest.mark.asyncio
    async def test_fixed_amount_discount_rule(self, session):
        """Test pricing calculation with fixed amount discount"""
        pricing_service = PricingService(session)
        
        # Create a test discount rule
        rule = PricingRule(
            name="Fixed 50 MAD Off",
            description="50 MAD discount",
            discount_type="Fixed Amount",
            discount_amount=Decimal('50.00'),
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=365),
            is_active=True,
            conditions='{}'
        )
        session.add(rule)
        session.commit()
        session.refresh(rule)
        
        context = PricingContext(
            service_type="Tour",
            base_price=Decimal('500.00'),
            pax_count=2,
            start_date=date.today() + timedelta(days=7)
        )
        
        calculation = await pricing_service.calculate_pricing(context)
        
        assert calculation.base_price == Decimal('500.00')
        assert calculation.discount_amount == Decimal('50.00')
        assert calculation.total_price == Decimal('450.00')
        assert len(calculation.applied_rules) == 1
    
    @pytest.mark.asyncio
    async def test_group_discount_rule(self, session):
        """Test group discount for large parties"""
        pricing_service = PricingService(session)
        
        # Create a group discount rule
        rule = PricingRule(
            name="Group Discount 15%",
            description="15% discount for groups of 10+",
            discount_type="Group Discount",
            discount_percentage=Decimal('15.00'),
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=365),
            is_active=True,
            conditions='{"min_pax_count": 10}'
        )
        session.add(rule)
        session.commit()
        session.refresh(rule)
        
        # Test with large group
        context = PricingContext(
            service_type="Tour",
            base_price=Decimal('2000.00'),
            pax_count=12,  # Qualifies for group discount
            start_date=date.today() + timedelta(days=15)
        )
        
        calculation = await pricing_service.calculate_pricing(context)
        
        assert calculation.base_price == Decimal('2000.00')
        assert calculation.discount_amount == Decimal('300.00')  # 15% of 2000
        assert calculation.total_price == Decimal('1700.00')
        assert len(calculation.applied_rules) == 1
    
    @pytest.mark.asyncio
    async def test_promo_code_validation(self, session):
        """Test promo code validation"""
        pricing_service = PricingService(session)
        
        # Create a promo code rule
        rule = PricingRule(
            name="SUMMER2024",
            description="Summer 2024 promotion",
            code="SUMMER2024",
            discount_type="Percentage",
            discount_percentage=Decimal('20.00'),
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=90),
            is_active=True,
            max_uses=100,
            current_uses=0,
            conditions='{}'
        )
        session.add(rule)
        session.commit()
        session.refresh(rule)
        
        context = PricingContext(
            service_type="Tour",
            base_price=Decimal('800.00'),
            pax_count=2,
            start_date=date.today() + timedelta(days=14),
            promo_code="SUMMER2024"
        )
        
        # Validate promo code
        validated_rule = await pricing_service.validate_promo_code("SUMMER2024", context)
        
        assert validated_rule is not None
        assert validated_rule.code == "SUMMER2024"
        assert validated_rule.discount_percentage == Decimal('20.00')
    
    @pytest.mark.asyncio
    async def test_invalid_promo_code(self, session):
        """Test validation of invalid promo code"""
        pricing_service = PricingService(session)
        
        context = PricingContext(
            service_type="Tour",
            base_price=Decimal('800.00'),
            pax_count=2,
            start_date=date.today() + timedelta(days=14),
            promo_code="INVALID"
        )
        
        # Should raise HTTPException for invalid code
        with pytest.raises(Exception) as exc_info:
            await pricing_service.validate_promo_code("INVALID", context)
        
        assert "Invalid or expired promo code" in str(exc_info.value)
    
    def test_pricing_request_to_context_conversion(self):
        """Test conversion from PricingRequest to PricingContext"""
        request = PricingRequest(
            service_type="Tour",
            base_price=Decimal('1200.00'),
            pax_count=6,
            start_date=date.today() + timedelta(days=21),
            customer_id=uuid.uuid4(),
            promo_code="TEST2024"
        )
        
        context = request.to_pricing_context()
        
        assert context.service_type == "Tour"
        assert context.base_price == Decimal('1200.00')
        assert context.pax_count == 6
        assert context.start_date == date.today() + timedelta(days=21)
        assert context.customer_id == request.customer_id
        assert context.promo_code == "TEST2024"
    
    @pytest.mark.asyncio
    async def test_multiple_applicable_rules(self, session):
        """Test pricing with multiple applicable rules"""
        pricing_service = PricingService(session)
        
        # Create multiple rules
        early_bird_rule = PricingRule(
            name="Early Bird 5%",
            discount_type="Early Bird",
            discount_percentage=Decimal('5.00'),
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=365),
            is_active=True,
            priority=1,
            conditions='{"min_advance_days": 14}'
        )
        
        group_rule = PricingRule(
            name="Group 10%",
            discount_type="Group Discount", 
            discount_percentage=Decimal('10.00'),
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=365),
            is_active=True,
            priority=2,
            conditions='{"min_pax_count": 8}'
        )
        
        session.add(early_bird_rule)
        session.add(group_rule)
        session.commit()
        
        context = PricingContext(
            service_type="Tour",
            base_price=Decimal('2000.00'),
            pax_count=10,  # Qualifies for group discount
            start_date=date.today() + timedelta(days=30)  # Qualifies for early bird
        )
        
        calculation = await pricing_service.calculate_pricing(context)
        
        # Should apply both discounts
        assert calculation.base_price == Decimal('2000.00')
        assert calculation.discount_amount == Decimal('300.00')  # 5% + 10% = 300
        assert calculation.total_price == Decimal('1700.00')
        assert len(calculation.applied_rules) == 2
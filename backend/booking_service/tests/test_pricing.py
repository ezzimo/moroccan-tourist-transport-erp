"""
Tests for pricing service functionality
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from services.pricing_service import PricingService
from schemas.pricing import PricingContext, PricingCalculation
from models.pricing_rule import PricingRule, DiscountType
import uuid


class TestPricingService:
    """Test class for pricing service operations"""
    
    @pytest.mark.asyncio
    async def test_basic_pricing_without_discounts(self, session):
        """Test basic pricing calculation without any discounts"""
        pricing_service = PricingService(session)
        
        context = PricingContext(
            service_type="Tour",
            base_price=Decimal('1000.00'),
            pax_count=4,
            start_date=date.today() + timedelta(days=30)
        )
        
        result = await pricing_service.calculate_pricing(context)
        
        assert isinstance(result, PricingCalculation)
        assert result.base_price == Decimal('1000.00')
        assert result.discount_amount == Decimal('0')
        assert result.total_price == Decimal('1000.00')
        assert result.currency == "MAD"
        assert len(result.applied_rules) == 0
    
    @pytest.mark.asyncio
    async def test_percentage_discount_rule(self, session, create_test_pricing_rule):
        """Test percentage discount application"""
        pricing_service = PricingService(session)
        
        # Create a 10% discount rule
        rule = create_test_pricing_rule(
            name="10% Tour Discount",
            discount_type=DiscountType.PERCENTAGE,
            discount_percentage=Decimal('10.0'),
            conditions={"service_type": "Tour"}
        )
        
        context = PricingContext(
            service_type="Tour",
            base_price=Decimal('1000.00'),
            pax_count=2,
            start_date=date.today() + timedelta(days=30)
        )
        
        result = await pricing_service.calculate_pricing(context)
        
        assert result.base_price == Decimal('1000.00')
        assert result.discount_amount == Decimal('100.00')  # 10% of 1000
        assert result.total_price == Decimal('900.00')
        assert len(result.applied_rules) == 1
        assert result.applied_rules[0].rule_name == "10% Tour Discount"
    
    @pytest.mark.asyncio
    async def test_fixed_amount_discount(self, session, create_test_pricing_rule):
        """Test fixed amount discount application"""
        pricing_service = PricingService(session)
        
        # Create a 200 MAD discount rule
        rule = create_test_pricing_rule(
            name="200 MAD Off",
            discount_type=DiscountType.FIXED_AMOUNT,
            discount_amount=Decimal('200.00'),
            conditions={"service_type": "Transfer"}
        )
        
        context = PricingContext(
            service_type="Transfer",
            base_price=Decimal('500.00'),
            pax_count=1,
            start_date=date.today() + timedelta(days=15)
        )
        
        result = await pricing_service.calculate_pricing(context)
        
        assert result.base_price == Decimal('500.00')
        assert result.discount_amount == Decimal('200.00')
        assert result.total_price == Decimal('300.00')
        assert len(result.applied_rules) == 1
    
    @pytest.mark.asyncio
    async def test_group_discount(self, session, create_test_pricing_rule):
        """Test group discount for large parties"""
        pricing_service = PricingService(session)
        
        # Create a group discount rule (15% for 5+ people)
        rule = create_test_pricing_rule(
            name="Group Discount",
            discount_type=DiscountType.GROUP_DISCOUNT,
            discount_percentage=Decimal('15.0'),
            conditions={"service_type": "Tour", "min_party_size": 5}
        )
        
        context = PricingContext(
            service_type="Tour",
            base_price=Decimal('2000.00'),
            pax_count=6,  # Qualifies for group discount
            start_date=date.today() + timedelta(days=20)
        )
        
        result = await pricing_service.calculate_pricing(context)
        
        assert result.base_price == Decimal('2000.00')
        assert result.discount_amount == Decimal('300.00')  # 15% of 2000
        assert result.total_price == Decimal('1700.00')
        assert len(result.applied_rules) == 1
    
    @pytest.mark.asyncio
    async def test_promo_code_validation_valid(self, session, create_test_pricing_rule):
        """Test valid promo code validation"""
        pricing_service = PricingService(session)
        
        # Create a promo code rule
        rule = create_test_pricing_rule(
            name="SUMMER2024",
            code="SUMMER2024",
            discount_type=DiscountType.PERCENTAGE,
            discount_percentage=Decimal('20.0'),
            conditions={"service_type": "Tour"}
        )
        
        context = PricingContext(
            service_type="Tour",
            base_price=Decimal('1500.00'),
            pax_count=3,
            start_date=date.today() + timedelta(days=45),
            promo_code="SUMMER2024"
        )
        
        result = await pricing_service.validate_promo_code("SUMMER2024", context)
        
        assert result.valid is True
        assert result.discount_amount == Decimal('300.00')  # 20% of 1500
        assert result.discount_percentage == Decimal('20.0')
        assert result.rule_name == "SUMMER2024"
        assert "successfully" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_promo_code_validation_invalid(self, session):
        """Test invalid promo code validation"""
        pricing_service = PricingService(session)
        
        context = PricingContext(
            service_type="Tour",
            base_price=Decimal('1000.00'),
            pax_count=2,
            start_date=date.today() + timedelta(days=30),
            promo_code="INVALID_CODE"
        )
        
        result = await pricing_service.validate_promo_code("INVALID_CODE", context)
        
        assert result.valid is False
        assert result.discount_amount is None
        assert "invalid" in result.message.lower() or "expired" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_multiple_applicable_rules(self, session, create_test_pricing_rule):
        """Test multiple discount rules applying to same booking"""
        pricing_service = PricingService(session)
        
        # Create multiple rules
        rule1 = create_test_pricing_rule(
            name="Early Bird",
            discount_type=DiscountType.EARLY_BIRD,
            discount_percentage=Decimal('10.0'),
            conditions={"service_type": "Tour"}
        )
        
        rule2 = create_test_pricing_rule(
            name="Group Discount",
            discount_type=DiscountType.GROUP_DISCOUNT,
            discount_percentage=Decimal('5.0'),
            conditions={"service_type": "Tour", "min_party_size": 4}
        )
        
        context = PricingContext(
            service_type="Tour",
            base_price=Decimal('2000.00'),
            pax_count=5,  # Qualifies for group discount
            start_date=date.today() + timedelta(days=45)  # Qualifies for early bird
        )
        
        result = await pricing_service.calculate_pricing(context)
        
        # Should apply both discounts
        assert result.base_price == Decimal('2000.00')
        assert result.discount_amount > Decimal('0')
        assert result.total_price < Decimal('2000.00')
        assert len(result.applied_rules) >= 1  # At least one rule should apply
    
    @pytest.mark.asyncio
    async def test_pricing_context_conversion(self):
        """Test PricingRequest to PricingContext conversion"""
        from schemas.pricing import PricingRequest
        
        request = PricingRequest(
            service_type="Tour",
            base_price=Decimal('1200.00'),
            pax_count=3,
            start_date=date.today() + timedelta(days=20),
            customer_id=uuid.uuid4(),
            promo_code="TEST2024"
        )
        
        context = request.to_pricing_context()
        
        assert context.service_type == "Tour"
        assert context.base_price == Decimal('1200.00')
        assert context.pax_count == 3
        assert context.party_size == 3  # Alias property
        assert context.customer_id == request.customer_id
        assert context.promo_code == "TEST2024"
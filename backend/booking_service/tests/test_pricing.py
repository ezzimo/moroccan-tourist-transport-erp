"""
Tests for pricing functionality
"""
import pytest
from services.pricing_service import PricingService
from models.enums import DiscountType
from decimal import Decimal
from datetime import date, timedelta


class TestPricing:
    """Test class for pricing operations"""
    
    @pytest.mark.asyncio
    async def test_calculate_pricing_no_discounts(self, session):
        """Test pricing calculation without discounts"""
        pricing_service = PricingService(session)
        
        pricing_request = {
            "service_type": "Tour",
            "base_price": Decimal("1000.00"),
            "pax_count": 2,
            "start_date": date.today() + timedelta(days=7)
        }
        
        result = await pricing_service.calculate_pricing(pricing_request)
        
        assert result["base_price"] == Decimal("1000.00")
        assert result["discount_amount"] == Decimal("0.00")
        assert result["total_price"] == Decimal("1000.00")
        assert result["applied_rules"] == []
    
    @pytest.mark.asyncio
    async def test_calculate_pricing_with_percentage_discount(self, session, create_test_pricing_rule):
        """Test pricing calculation with percentage discount"""
        pricing_service = PricingService(session)
        
        # Create percentage discount rule
        rule = create_test_pricing_rule(
            name="10% Tour Discount",
            discount_type=DiscountType.PERCENTAGE,
            discount_percentage=Decimal("10.00"),
            conditions='{"service_types": ["Tour"]}'
        )
        
        pricing_request = {
            "service_type": "Tour",
            "base_price": Decimal("1000.00"),
            "pax_count": 2,
            "start_date": date.today() + timedelta(days=7)
        }
        
        result = await pricing_service.calculate_pricing(pricing_request)
        
        assert result["base_price"] == Decimal("1000.00")
        assert result["discount_amount"] == Decimal("100.00")  # 10% of 1000
        assert result["total_price"] == Decimal("900.00")
        assert len(result["applied_rules"]) == 1
        assert result["applied_rules"][0]["rule_name"] == "10% Tour Discount"
    
    @pytest.mark.asyncio
    async def test_calculate_pricing_with_fixed_discount(self, session, create_test_pricing_rule):
        """Test pricing calculation with fixed amount discount"""
        pricing_service = PricingService(session)
        
        # Create fixed discount rule
        rule = create_test_pricing_rule(
            name="200 MAD Off",
            discount_type=DiscountType.FIXED_AMOUNT,
            discount_amount=Decimal("200.00"),
            conditions='{"service_types": ["Tour"]}'
        )
        
        pricing_request = {
            "service_type": "Tour",
            "base_price": Decimal("1000.00"),
            "pax_count": 2,
            "start_date": date.today() + timedelta(days=7)
        }
        
        result = await pricing_service.calculate_pricing(pricing_request)
        
        assert result["base_price"] == Decimal("1000.00")
        assert result["discount_amount"] == Decimal("200.00")
        assert result["total_price"] == Decimal("800.00")
        assert len(result["applied_rules"]) == 1
    
    @pytest.mark.asyncio
    async def test_calculate_pricing_with_group_discount(self, session, create_test_pricing_rule):
        """Test pricing calculation with group discount"""
        pricing_service = PricingService(session)
        
        # Create group discount rule
        rule = create_test_pricing_rule(
            name="Group Discount",
            discount_type=DiscountType.GROUP_DISCOUNT,
            discount_percentage=Decimal("15.00"),
            conditions='{"group_threshold": 5, "service_types": ["Tour"]}'
        )
        
        # Test with group size meeting threshold
        pricing_request = {
            "service_type": "Tour",
            "base_price": Decimal("1000.00"),
            "pax_count": 6,  # Above threshold
            "start_date": date.today() + timedelta(days=7)
        }
        
        result = await pricing_service.calculate_pricing(pricing_request)
        
        assert result["discount_amount"] == Decimal("150.00")  # 15% of 1000
        assert result["total_price"] == Decimal("850.00")
        
        # Test with group size below threshold
        pricing_request["pax_count"] = 3  # Below threshold
        
        result = await pricing_service.calculate_pricing(pricing_request)
        
        assert result["discount_amount"] == Decimal("0.00")
        assert result["total_price"] == Decimal("1000.00")
    
    @pytest.mark.asyncio
    async def test_calculate_pricing_with_early_bird_discount(self, session, create_test_pricing_rule):
        """Test pricing calculation with early bird discount"""
        pricing_service = PricingService(session)
        
        # Create early bird discount rule
        rule = create_test_pricing_rule(
            name="Early Bird 20%",
            discount_type=DiscountType.EARLY_BIRD,
            discount_percentage=Decimal("20.00"),
            conditions='{"min_advance_days": 30, "service_types": ["Tour"]}'
        )
        
        # Test with booking made in advance
        pricing_request = {
            "service_type": "Tour",
            "base_price": Decimal("1000.00"),
            "pax_count": 2,
            "start_date": date.today() + timedelta(days=35)  # 35 days in advance
        }
        
        result = await pricing_service.calculate_pricing(pricing_request)
        
        assert result["discount_amount"] == Decimal("200.00")  # 20% of 1000
        assert result["total_price"] == Decimal("800.00")
        
        # Test with booking made too late
        pricing_request["start_date"] = date.today() + timedelta(days=7)  # Only 7 days
        
        result = await pricing_service.calculate_pricing(pricing_request)
        
        assert result["discount_amount"] == Decimal("0.00")
        assert result["total_price"] == Decimal("1000.00")
    
    @pytest.mark.asyncio
    async def test_validate_promo_code_valid(self, session, create_test_pricing_rule):
        """Test validating a valid promo code"""
        pricing_service = PricingService(session)
        
        # Create promo code rule
        rule = create_test_pricing_rule(
            name="Summer Special",
            code="SUMMER2024",
            discount_type=DiscountType.PERCENTAGE,
            discount_percentage=Decimal("25.00"),
            conditions='{"service_types": ["Tour"]}'
        )
        
        booking_data = {
            "service_type": "Tour",
            "base_price": Decimal("1000.00"),
            "pax_count": 2,
            "start_date": date.today() + timedelta(days=7)
        }
        
        result = await pricing_service.validate_promo_code("SUMMER2024", booking_data)
        
        assert result["valid"] is True
        assert result["rule_name"] == "Summer Special"
        assert result["discount_amount"] == 250.0  # 25% of 1000
    
    @pytest.mark.asyncio
    async def test_validate_promo_code_invalid(self, session):
        """Test validating an invalid promo code"""
        pricing_service = PricingService(session)
        
        booking_data = {
            "service_type": "Tour",
            "base_price": Decimal("1000.00"),
            "pax_count": 2,
            "start_date": date.today() + timedelta(days=7)
        }
        
        result = await pricing_service.validate_promo_code("INVALID", booking_data)
        
        assert result["valid"] is False
        assert "Invalid promo code" in result["message"]
    
    @pytest.mark.asyncio
    async def test_multiple_combinable_rules(self, session, create_test_pricing_rule):
        """Test applying multiple combinable pricing rules"""
        pricing_service = PricingService(session)
        
        # Create combinable rules
        rule1 = create_test_pricing_rule(
            name="Base Discount",
            discount_type=DiscountType.PERCENTAGE,
            discount_percentage=Decimal("10.00"),
            conditions='{"service_types": ["Tour"]}',
            priority=1,
            is_combinable=True
        )
        
        rule2 = create_test_pricing_rule(
            name="Additional Discount",
            discount_type=DiscountType.FIXED_AMOUNT,
            discount_amount=Decimal("50.00"),
            conditions='{"service_types": ["Tour"]}',
            priority=2,
            is_combinable=True
        )
        
        pricing_request = {
            "service_type": "Tour",
            "base_price": Decimal("1000.00"),
            "pax_count": 2,
            "start_date": date.today() + timedelta(days=7)
        }
        
        result = await pricing_service.calculate_pricing(pricing_request)
        
        # Should apply both discounts: 10% (100) + 50 = 150 total discount
        assert result["discount_amount"] == Decimal("150.00")
        assert result["total_price"] == Decimal("850.00")
        assert len(result["applied_rules"]) == 2
    
    @pytest.mark.asyncio
    async def test_rule_usage_limit(self, session, create_test_pricing_rule):
        """Test pricing rule usage limits"""
        pricing_service = PricingService(session)
        
        # Create rule with usage limit
        rule = create_test_pricing_rule(
            name="Limited Offer",
            discount_type=DiscountType.PERCENTAGE,
            discount_percentage=Decimal("20.00"),
            conditions='{"service_types": ["Tour"]}',
            max_uses=1,
            current_uses=0
        )
        
        pricing_request = {
            "service_type": "Tour",
            "base_price": Decimal("1000.00"),
            "pax_count": 2,
            "start_date": date.today() + timedelta(days=7)
        }
        
        # First use should work
        result1 = await pricing_service.calculate_pricing(pricing_request)
        assert result1["discount_amount"] == Decimal("200.00")
        
        # Second use should not apply the rule (limit reached)
        result2 = await pricing_service.calculate_pricing(pricing_request)
        assert result2["discount_amount"] == Decimal("0.00")
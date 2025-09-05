#!/usr/bin/env python3
"""
Test script to validate SQLAlchemy fixes in booking service
"""
import sys
import os
import asyncio
from datetime import date, datetime
from decimal import Decimal
import uuid

# Add the booking service to the path
sys.path.append('/home/ubuntu/moroccan-tourist-transport-erp/backend/booking_service')

async def test_pricing_service():
    """Test the pricing service with the SQLAlchemy fixes"""
    print("Testing Pricing Service...")
    
    try:
        # Import after path setup
        from services.pricing_service import PricingService
        from schemas.pricing import PricingContext
        from sqlmodel import Session, create_engine
        
        # Create a test database connection
        # Note: This would normally use the actual database
        engine = create_engine("sqlite:///test.db", echo=True)
        
        with Session(engine) as session:
            pricing_service = PricingService(session)
            
            # Create test pricing context
            context = PricingContext(
                service_type="AIRPORT_TRANSFER",
                base_price=Decimal("100.00"),
                pax_count=2,
                start_date=date.today(),
                end_date=date.today(),
                customer_id=uuid.uuid4(),
                promo_code=None
            )
            
            # Test the fixed _get_applicable_rules method
            print("Testing _get_applicable_rules method...")
            rules = await pricing_service._get_applicable_rules(context)
            print(f"✓ Successfully retrieved {len(rules)} applicable rules")
            
            # Test pricing calculation
            print("Testing pricing calculation...")
            result = await pricing_service.calculate_pricing(context)
            print(f"✓ Pricing calculation successful: base={result.base_price}, total={result.total_price}")
            
        print("✓ Pricing Service tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Pricing Service test failed: {e}")
        return False

def test_imports():
    """Test that all imports work correctly"""
    print("Testing imports...")
    
    try:
        # Test database imports
        from database import get_session, get_redis
        print("✓ Database imports successful")
        
        # Test pricing service imports
        from services.pricing_service import PricingService
        print("✓ Pricing service imports successful")
        
        # Test SQLAlchemy imports
        from sqlalchemy import text
        print("✓ SQLAlchemy imports successful")
        
        print("✓ All imports successful!")
        return True
        
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

def test_syntax():
    """Test that the Python syntax is valid"""
    print("Testing Python syntax...")
    
    files_to_check = [
        '/home/ubuntu/moroccan-tourist-transport-erp/backend/booking_service/main.py',
        '/home/ubuntu/moroccan-tourist-transport-erp/backend/booking_service/services/pricing_service.py'
    ]
    
    for file_path in files_to_check:
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            
            # Compile to check syntax
            compile(code, file_path, 'exec')
            print(f"✓ Syntax valid for {os.path.basename(file_path)}")
            
        except SyntaxError as e:
            print(f"✗ Syntax error in {file_path}: {e}")
            return False
        except Exception as e:
            print(f"✗ Error checking {file_path}: {e}")
            return False
    
    print("✓ All syntax checks passed!")
    return True

async def main():
    """Run all tests"""
    print("=" * 50)
    print("SQLAlchemy Fixes Validation Test")
    print("=" * 50)
    
    tests = [
        ("Syntax Check", test_syntax),
        ("Import Check", test_imports),
        ("Pricing Service", test_pricing_service),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("✓ All tests passed! The fixes are working correctly.")
    else:
        print("✗ Some tests failed. Please review the errors above.")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main())


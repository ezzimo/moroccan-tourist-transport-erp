#!/usr/bin/env python3
"""
Test script to verify booking creation with customer verification
"""
import asyncio
import httpx
import json
from datetime import date, timedelta

# Configuration
BOOKING_SERVICE_URL = "http://localhost:8002"
AUTH_SERVICE_URL = "http://localhost:8000"
CRM_SERVICE_URL = "http://localhost:8001"

async def test_booking_creation():
    """Test the complete booking creation flow with customer verification"""
    print("🔍 Testing Booking Creation with Customer Verification")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        # Step 1: Login to get token
        print("1. Logging in to auth service...")
        login_response = await client.post(
            f"{AUTH_SERVICE_URL}/api/v1/auth/login",
            json={"email": "admin@example.com", "password": "ChangeMe!123"}
        )
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed: {login_response.status_code} - {login_response.text}")
            return
        
        login_data = login_response.json()
        token = login_data.get("access_token")
        print(f"   ✅ Login successful, token: {token[:50]}...")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 2: Get a customer to use for booking
        print("\n2. Getting customer list...")
        customers_response = await client.get(
            f"{CRM_SERVICE_URL}/api/v1/customers/?size=5",
            headers=headers
        )
        
        if customers_response.status_code != 200:
            print(f"   ❌ Failed to get customers: {customers_response.status_code}")
            return
        
        customers_data = customers_response.json()
        customers = customers_data.get("items", [])
        
        if not customers:
            print("   ⚠️ No customers found, creating a test customer...")
            # Create a test customer
            customer_data = {
                "full_name": "Test Customer",
                "contact_type": "Individual",
                "email": "testcustomer@example.com",
                "phone": "+212600000001",
                "preferred_language": "French"
            }
            
            create_customer_response = await client.post(
                f"{CRM_SERVICE_URL}/api/v1/customers/",
                headers=headers,
                json=customer_data
            )
            
            if create_customer_response.status_code == 201:
                customer = create_customer_response.json()
                print(f"   ✅ Created test customer: {customer['email']}")
            else:
                print(f"   ❌ Failed to create customer: {create_customer_response.status_code}")
                return
        else:
            customer = customers[0]
            print(f"   ✅ Using existing customer: {customer['email']}")
        
        # Step 3: Test pricing calculation
        print("\n3. Testing pricing calculation...")
        pricing_data = {
            "service_type": "Tour",
            "base_price": 500.0,
            "pax_count": 2,
            "start_date": (date.today() + timedelta(days=7)).isoformat(),
            "customer_id": customer["id"]
        }
        
        pricing_response = await client.post(
            f"{BOOKING_SERVICE_URL}/api/v1/pricing/calculate",
            headers=headers,
            json=pricing_data
        )
        
        if pricing_response.status_code == 200:
            pricing_result = pricing_response.json()
            print(f"   ✅ Pricing calculated: {pricing_result}")
        else:
            print(f"   ❌ Pricing failed: {pricing_response.status_code} - {pricing_response.text}")
            return
        
        # Step 4: Create booking with verified customer
        print("\n4. Creating booking with verified customer...")
        booking_data = {
            "customer_id": customer["id"],
            "service_type": "Tour",
            "pax_count": 2,
            "lead_passenger_name": customer.get("full_name", "Test Customer"),
            "lead_passenger_email": customer["email"],
            "lead_passenger_phone": customer["phone"],
            "start_date": (date.today() + timedelta(days=7)).isoformat(),
            "end_date": (date.today() + timedelta(days=9)).isoformat(),
            "base_price": pricing_result["total_price"],
            "special_requests": "Test booking with customer verification"
        }
        
        booking_response = await client.post(
            f"{BOOKING_SERVICE_URL}/api/v1/bookings/",
            headers=headers,
            json=booking_data
        )
        
        print(f"   Status: {booking_response.status_code}")
        
        if booking_response.status_code == 201:
            booking_result = booking_response.json()
            print(f"   ✅ Booking created successfully!")
            print(f"   📋 Booking ID: {booking_result['id']}")
            print(f"   👤 Customer: {booking_result['lead_passenger_name']}")
            print(f"   💰 Total: {booking_result['total_price']} {booking_result['currency']}")
            print(f"   📝 Notes: {booking_result.get('internal_notes', 'None')}")
        else:
            print(f"   ❌ Booking creation failed: {booking_response.text}")
            
            # Try to parse error details
            try:
                error_data = booking_response.json()
                error_type = error_data.get("type", "unknown")
                error_detail = error_data.get("detail", "No details")
                print(f"   🔍 Error Type: {error_type}")
                print(f"   🔍 Error Detail: {error_detail}")
            except:
                print("   🔍 Could not parse error response")
        
        # Step 5: Test with non-existent customer (if strict mode)
        print("\n5. Testing with non-existent customer...")
        fake_booking_data = {
            **booking_data,
            "customer_id": "00000000-0000-0000-0000-000000000000",  # Non-existent UUID
        }
        
        fake_booking_response = await client.post(
            f"{BOOKING_SERVICE_URL}/api/v1/bookings/",
            headers=headers,
            json=fake_booking_data
        )
        
        print(f"   Status: {fake_booking_response.status_code}")
        
        if fake_booking_response.status_code in [422, 404]:
            print("   ✅ Properly rejected non-existent customer")
            try:
                error_data = fake_booking_response.json()
                print(f"   🔍 Error Type: {error_data.get('type', 'unknown')}")
            except:
                pass
        elif fake_booking_response.status_code == 201:
            print("   ⚠️ Booking created despite non-existent customer (non-strict mode)")
        else:
            print(f"   ❌ Unexpected response: {fake_booking_response.text}")

if __name__ == "__main__":
    asyncio.run(test_booking_creation())
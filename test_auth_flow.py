#!/usr/bin/env python3
"""
Test script to verify the authentication flow between auth_service and crm_service
"""
import asyncio
import httpx
import json
from typing import Optional

# Configuration
AUTH_SERVICE_URL = "http://localhost:8000"
CRM_SERVICE_URL = "http://localhost:8001"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "ChangeMe!123"


async def test_auth_flow():
    """Test the complete authentication flow"""
    print("🔍 Testing Authentication Flow")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Step 1: Login to auth service
        print("1. Logging in to auth service...")
        login_response = await client.post(
            f"{AUTH_SERVICE_URL}/api/v1/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        
        print(f"   Status: {login_response.status_code}")
        if login_response.status_code != 200:
            print(f"   Error: {login_response.text}")
            return
        
        login_data = login_response.json()
        token = login_data.get("access_token")
        print(f"   Token received: {token[:50]}...")
        
        # Step 2: Test auth service /me endpoint
        print("\n2. Testing auth service /me endpoint...")
        me_response = await client.get(
            f"{AUTH_SERVICE_URL}/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"   Status: {me_response.status_code}")
        if me_response.status_code == 200:
            me_data = me_response.json()
            print(f"   User: {me_data.get('email')}")
            print(f"   Permissions: {len(me_data.get('permissions', []))} permissions")
            
            # Check for CRM permissions
            permissions = me_data.get('permissions', [])
            crm_read_customers = "crm:read:customers" in permissions
            print(f"   Has 'crm:read:customers': {crm_read_customers}")
        else:
            print(f"   Error: {me_response.text}")
            return
        
        # Step 3: Test CRM service customers endpoint
        print("\n3. Testing CRM service customers endpoint...")
        customers_response = await client.get(
            f"{CRM_SERVICE_URL}/api/v1/customers/?is_active=true&page=1&size=20",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"   Status: {customers_response.status_code}")
        if customers_response.status_code == 200:
            print("   ✅ SUCCESS: CRM service accepted the token!")
            customers_data = customers_response.json()
            print(f"   Response: {json.dumps(customers_data, indent=2)[:200]}...")
        else:
            print(f"   ❌ FAILED: {customers_response.text}")
            
            # Step 4: Debug - Test CRM auth directly
            print("\n4. Debug: Testing CRM auth service call...")
            try:
                # Simulate what CRM service does internally
                crm_auth_response = await client.get(
                    f"{AUTH_SERVICE_URL}/api/v1/auth/me",
                    headers={"Authorization": f"Bearer {token}"}
                )
                print(f"   Direct auth call status: {crm_auth_response.status_code}")
                if crm_auth_response.status_code == 200:
                    print("   ✅ Auth service responds correctly to CRM")
                else:
                    print(f"   ❌ Auth service error: {crm_auth_response.text}")
            except Exception as e:
                print(f"   ❌ Connection error: {e}")


if __name__ == "__main__":
    asyncio.run(test_auth_flow())


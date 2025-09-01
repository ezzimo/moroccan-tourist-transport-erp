#!/usr/bin/env python3
"""
Diagnostic script to test tour service functionality
Run this to identify specific issues with tour templates
and active/planned tours
"""

import requests
from datetime import datetime

# Configuration
FRONTEND_URL = "http://localhost:3000"
TOUR_SERVICE_URL = "http://localhost:8010"
AUTH_SERVICE_URL = "http://localhost:8000"


def test_auth_and_permissions():
    """Test authentication and tour permissions"""
    print("🔐 Testing Authentication & Permissions")
    print("=" * 50)

    # Test login
    try:
        login_response = requests.post(
            f"{AUTH_SERVICE_URL}/api/v1/auth/login",
            json={"email": "admin@example.com", "password": "ChangeMe!123"},
            timeout=10,
        )

        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            print("✅ Login successful")

            # Test permissions
            me_response = requests.get(
                f"{AUTH_SERVICE_URL}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )

            if me_response.status_code == 200:
                user_data = me_response.json()
                permissions = user_data.get("permissions", [])
                print(
                    "✅ User permissions loaded:"
                    f"{len(permissions)} permissions"
                )

                # Check for tour-related permissions
                tour_perms = [p for p in permissions if "tour" in p.lower()]
                print(f"🎯 Tour-related permissions: {tour_perms}")

                return token, permissions
            else:
                print(f"❌ Failed to get user info: {me_response.status_code}")
                return None, []
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return None, []

    except Exception as e:
        print(f"❌ Auth test failed: {e}")
        return None, []


def test_tour_service_direct(token):
    """Test tour service endpoints directly"""
    print("\n🎯 Testing Tour Service Direct Access")
    print("=" * 50)

    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # Test health endpoint
    try:
        health_response = requests.get(f"{TOUR_SERVICE_URL}/health", timeout=5)
        print(f"🏥 Health check: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"   Response: {health_response.json()}")
    except Exception as e:
        print(f"❌ Tour service health check failed: {e}")
        return False

    # Test tour templates endpoint
    try:
        templates_response = requests.get(
            f"{TOUR_SERVICE_URL}/api/v1/tour-templates/",
            headers=headers,
            timeout=10,
        )
        print(f"📋 Tour templates: {templates_response.status_code}")
        if templates_response.status_code == 200:
            templates = templates_response.json()
            print(f"   Found {len(templates.get('items', []))} templates")
        else:
            print(f"   Error: {templates_response.text}")
    except Exception as e:
        print(f"❌ Tour templates test failed: {e}")

    # Test create template endpoint
    try:
        create_data = {
            "title": f"Test Template {datetime.now().strftime('%H%M%S')}",
            "category": "CULTURAL",
            "duration_days": 3,
            "default_region": "Marrakech",
            "min_participants": 2,
            "max_participants": 10,
            "base_price": 500.0,
        }

        create_response = requests.post(
            f"{TOUR_SERVICE_URL}/api/v1/tour-templates",
            headers=headers,
            json=create_data,
            timeout=10,
        )
        print(f"➕ Create template: {create_response.status_code}")
        if create_response.status_code in [200, 201]:
            print("   ✅ Template creation successful")
        else:
            print(f"   ❌ Error: {create_response.text}")
    except Exception as e:
        print(f"❌ Create template test failed: {e}")

    return True


def test_frontend_proxy():
    """Test frontend proxy routing"""
    print("\n🌐 Testing Frontend Proxy Routing")
    print("=" * 50)

    try:
        # Test if frontend is accessible
        frontend_response = requests.get(f"{FRONTEND_URL}", timeout=5)
        print(f"🖥️  Frontend access: {frontend_response.status_code}")

        # Test API proxy routing
        proxy_response = requests.get(
            f"{FRONTEND_URL}/api/v1/tour-templates/", timeout=10
        )
        print(f"🔄 Proxy routing: {proxy_response.status_code}")

        if proxy_response.status_code != 200:
            print(f"   Error: {proxy_response.text}")

    except Exception as e:
        print(f"❌ Frontend proxy test failed: {e}")


def main():
    """Run all diagnostic tests"""
    print("🚀 Tour Service Diagnostic Suite")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Test authentication
    token, permissions = test_auth_and_permissions()

    # Test tour service
    if token:
        test_tour_service_direct(token)
    else:
        print("⚠️  Skipping tour service tests (no auth token)")

    # Test frontend proxy
    test_frontend_proxy()

    print("\n📊 Diagnostic Complete")
    print("=" * 60)
    print("Next steps:")
    print("1. Review the output above for specific error codes and messages")
    print("2. Check if tour_service is running on port 8010")
    print("3. Verify frontend proxy configuration for tour endpoints")
    print("4. Confirm tour permissions are properly seeded in auth_service")


if __name__ == "__main__":
    main()

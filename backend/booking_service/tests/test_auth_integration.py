"""
Integration tests for booking service authentication
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from config import settings
import json


@pytest.fixture
def client():
    """Test client for booking service"""
    return TestClient(app)


def test_health_check_shows_jwt_config(client):
    """Test that health check shows JWT configuration"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "jwt_config" in data
    assert data["jwt_config"]["audience"] == settings.jwt_audience
    assert data["jwt_config"]["allowed_audiences"] == settings.jwt_allowed_audiences


def test_unauthenticated_booking_request(client):
    """Test that unauthenticated requests are rejected"""
    response = client.post("/api/v1/bookings/", json={
        "customer_id": "550e8400-e29b-41d4-a716-446655440000",
        "service_type": "Tour",
        "pax_count": 2,
        "lead_passenger_name": "Test User",
        "lead_passenger_email": "test@example.com",
        "lead_passenger_phone": "+212600000000",
        "start_date": "2024-03-15",
        "base_price": 500.0
    })
    
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]


def test_pricing_calculate_unauthenticated(client):
    """Test that pricing calculation requires authentication"""
    response = client.post("/api/v1/pricing/calculate", json={
        "service_type": "Tour",
        "base_price": 500.0,
        "pax_count": 2,
        "start_date": "2024-03-15"
    })
    
    assert response.status_code == 401


def test_jwt_audience_configuration():
    """Test JWT audience configuration parsing"""
    # Test that settings parse correctly
    assert isinstance(settings.jwt_allowed_audiences, list)
    assert len(settings.jwt_allowed_audiences) > 0
    assert settings.jwt_audience in settings.jwt_allowed_audiences


def test_cors_configuration(client):
    """Test CORS configuration"""
    response = client.options("/api/v1/bookings/", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Authorization,Content-Type"
    })
    
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
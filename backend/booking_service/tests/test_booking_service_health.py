"""
Health check tests for booking service
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    
    # Should return either 200 (healthy) or 503 (unhealthy)
    assert response.status_code in [200, 503]
    
    data = response.json()
    assert "status" in data
    assert "service" in data
    assert "version" in data
    assert data["service"] == "booking-microservice"


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert "features" in data
    assert data["service"] == "Booking & Reservation Microservice"


def test_docs_endpoint():
    """Test API documentation endpoint"""
    response = client.get("/docs")
    
    # Should return 200 in debug mode, 404 in production
    assert response.status_code in [200, 404]


def test_service_startup():
    """Test that service starts without import errors"""
    # If we can create a test client, the service started successfully
    assert client is not None
    
    # Test that we can make a basic request
    response = client.get("/")
    assert response.status_code == 200
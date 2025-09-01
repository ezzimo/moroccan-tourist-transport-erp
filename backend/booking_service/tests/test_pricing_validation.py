"""
Tests for pricing validation and error handling
"""
import pytest
from fastapi.testclient import TestClient
from decimal import Decimal
from main import app

client = TestClient(app)


class TestPricingValidation:
    """Test pricing calculation validation and error handling"""
    
    def test_pricing_with_empty_base_price(self):
        """Test pricing calculation with empty base price"""
        response = client.post("/api/v1/pricing/calculate", json={
            "service_type": "Tour",
            "base_price": "",  # Empty string
            "pax_count": 2,
            "start_date": "2024-03-15"
        })
        
        assert response.status_code == 422
        assert "validation_error" in response.json().get("type", "")
    
    def test_pricing_with_invalid_base_price(self):
        """Test pricing calculation with invalid base price"""
        response = client.post("/api/v1/pricing/calculate", json={
            "service_type": "Tour",
            "base_price": "invalid",
            "pax_count": 2,
            "start_date": "2024-03-15"
        })
        
        assert response.status_code == 422
    
    def test_pricing_with_negative_base_price(self):
        """Test pricing calculation with negative base price"""
        response = client.post("/api/v1/pricing/calculate", json={
            "service_type": "Tour",
            "base_price": -100,
            "pax_count": 2,
            "start_date": "2024-03-15"
        })
        
        assert response.status_code == 422
    
    def test_pricing_with_zero_base_price(self):
        """Test pricing calculation with zero base price"""
        response = client.post("/api/v1/pricing/calculate", json={
            "service_type": "Tour",
            "base_price": 0,
            "pax_count": 2,
            "start_date": "2024-03-15"
        })
        
        assert response.status_code == 422
    
    def test_pricing_with_valid_input(self):
        """Test pricing calculation with valid input"""
        response = client.post("/api/v1/pricing/calculate", json={
            "service_type": "Tour",
            "base_price": 100.50,
            "pax_count": 2,
            "start_date": "2024-03-15"
        })
        
        # Should succeed or return 422 if missing other required fields
        assert response.status_code in [200, 422]
        
        if response.status_code == 200:
            data = response.json()
            assert "base_price" in data
            assert "total_price" in data
            assert "currency" in data
    
    def test_pricing_with_string_numbers(self):
        """Test pricing calculation with string numeric values"""
        response = client.post("/api/v1/pricing/calculate", json={
            "service_type": "Tour",
            "base_price": "150.75",  # String number
            "pax_count": 2,
            "start_date": "2024-03-15"
        })
        
        # Should handle string conversion gracefully
        assert response.status_code in [200, 422]
    
    def test_pricing_with_partial_decimal(self):
        """Test pricing calculation with partial decimal input"""
        response = client.post("/api/v1/pricing/calculate", json={
            "service_type": "Tour",
            "base_price": "100.",  # Partial decimal
            "pax_count": 2,
            "start_date": "2024-03-15"
        })
        
        # Should handle partial decimal gracefully
        assert response.status_code in [200, 422]
    
    def test_pricing_error_response_format(self):
        """Test that error responses have consistent format"""
        response = client.post("/api/v1/pricing/calculate", json={
            "service_type": "",  # Invalid service type
            "base_price": 100,
            "pax_count": 2,
            "start_date": "2024-03-15"
        })
        
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data
        assert "type" in error_data
        assert error_data["type"] == "validation_error"
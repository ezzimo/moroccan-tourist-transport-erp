"""
Tests for driver management endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from models.driver import Driver, DriverStatus
from utils.auth import CurrentUser
from tests.conftest import (
    create_driver_data, assert_driver_response
)
from datetime import date, timedelta
import uuid


class TestDriverCRUD:
    """Test driver CRUD operations"""
    
    def test_create_driver_success(
        self, 
        client: TestClient, 
        auth_headers: dict,
        current_user: CurrentUser
    ):
        """Test successful driver creation"""
        # Mock authentication
        from utils.auth import get_current_user
        from main import app
        
        def mock_get_current_user():
            return current_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        driver_data = create_driver_data()
        
        response = client.post(
            "/api/v1/drivers/",
            json=driver_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["full_name"] == driver_data["full_name"]
        assert data["email"] == driver_data["email"]
        assert data["phone"] == driver_data["phone"]
        assert data["license_number"] == driver_data["license_number"]
        assert data["status"] == "Active"
        assert "id" in data
        assert "created_at" in data
        
        app.dependency_overrides.clear()
    
    def test_create_driver_duplicate_license(
        self, 
        client: TestClient, 
        auth_headers: dict,
        current_user: CurrentUser,
        sample_driver: Driver
    ):
        """Test driver creation with duplicate license number"""
        from utils.auth import get_current_user
        from main import app
        
        def mock_get_current_user():
            return current_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        driver_data = create_driver_data(
            license_number=sample_driver.license_number
        )
        
        response = client.post(
            "/api/v1/drivers/",
            json=driver_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "License number already exists" in response.json()["detail"]
        
        app.dependency_overrides.clear()
    
    def test_create_driver_invalid_data(
        self, 
        client: TestClient, 
        auth_headers: dict,
        current_user: CurrentUser
    ):
        """Test driver creation with invalid data"""
        from utils.auth import get_current_user
        from main import app
        
        def mock_get_current_user():
            return current_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        # Missing required fields
        driver_data = {
            "full_name": "Test Driver"
            # Missing other required fields
        }
        
        response = client.post(
            "/api/v1/drivers/",
            json=driver_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
        
        app.dependency_overrides.clear()
    
    def test_get_driver_success(
        self, 
        client: TestClient, 
        auth_headers: dict,
        current_user: CurrentUser,
        sample_driver: Driver
    ):
        """Test successful driver retrieval"""
        from utils.auth import get_current_user
        from main import app
        
        def mock_get_current_user():
            return current_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.get(
            f"/api/v1/drivers/{sample_driver.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert_driver_response(data, sample_driver)
        
        app.dependency_overrides.clear()
    
    def test_get_driver_not_found(
        self, 
        client: TestClient, 
        auth_headers: dict,
        current_user: CurrentUser
    ):
        """Test driver retrieval with non-existent ID"""
        from utils.auth import get_current_user
        from main import app
        
        def mock_get_current_user():
            return current_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        fake_id = uuid.uuid4()
        response = client.get(
            f"/api/v1/drivers/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "Driver not found" in response.json()["detail"]
        
        app.dependency_overrides.clear()
    
    def test_update_driver_success(
        self, 
        client: TestClient, 
        auth_headers: dict,
        current_user: CurrentUser,
        sample_driver: Driver
    ):
        """Test successful driver update"""
        from utils.auth import get_current_user
        from main import app
        
        def mock_get_current_user():
            return current_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        update_data = {
            "phone": "+212-999-888-777",
            "email": "updated@example.com",
            "performance_rating": 4.8
        }
        
        response = client.put(
            f"/api/v1/drivers/{sample_driver.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["phone"] == update_data["phone"]
        assert data["email"] == update_data["email"]
        assert data["performance_rating"] == update_data["performance_rating"]
        assert "updated_at" in data
        
        app.dependency_overrides.clear()
    
    def test_delete_driver_success(
        self, 
        client: TestClient, 
        auth_headers: dict,
        current_user: CurrentUser,
        sample_driver: Driver
    ):
        """Test successful driver deletion (soft delete)"""
        from utils.auth import get_current_user
        from main import app
        
        def mock_get_current_user():
            return current_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.delete(
            f"/api/v1/drivers/{sample_driver.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify driver is marked as terminated
        get_response = client.get(
            f"/api/v1/drivers/{sample_driver.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        assert get_response.json()["status"] == "Terminated"
        
        app.dependency_overrides.clear()


class TestDriverListing:
    """Test driver listing and filtering"""
    
    def test_get_drivers_list(
        self, 
        client: TestClient, 
        auth_headers: dict,
        current_user: CurrentUser,
        sample_driver: Driver
    ):
        """Test driver list retrieval"""
        from utils.auth import get_current_user
        from main import app
        
        def mock_get_current_user():
            return current_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.get(
            "/api/v1/drivers/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Find our sample driver in the list
        driver_found = False
        for driver in data:
            if driver["id"] == str(sample_driver.id):
                assert_driver_response(driver, sample_driver)
                driver_found = True
                break
        
        assert driver_found, "Sample driver not found in list"
        
        app.dependency_overrides.clear()
    
    def test_get_drivers_with_filters(
        self, 
        client: TestClient, 
        auth_headers: dict,
        current_user: CurrentUser,
        sample_driver: Driver
    ):
        """Test driver list with filters"""
        from utils.auth import get_current_user
        from main import app
        
        def mock_get_current_user():
            return current_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        # Test status filter
        response = client.get(
            "/api/v1/drivers/?status=Active",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for driver in data:
            assert driver["status"] == "Active"
        
        # Test license type filter
        response = client.get(
            f"/api/v1/drivers/?license_type={sample_driver.license_type}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for driver in data:
            assert driver["license_type"] == sample_driver.license_type
        
        app.dependency_overrides.clear()
    
    def test_get_drivers_pagination(
        self, 
        client: TestClient, 
        auth_headers: dict,
        current_user: CurrentUser
    ):
        """Test driver list pagination"""
        from utils.auth import get_current_user
        from main import app
        
        def mock_get_current_user():
            return current_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        # Test with limit
        response = client.get(
            "/api/v1/drivers/?limit=5",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5
        
        # Test with skip and limit
        response = client.get(
            "/api/v1/drivers/?skip=0&limit=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 10
        
        app.dependency_overrides.clear()


class TestDriverSearch:
    """Test driver search functionality"""
    
    def test_search_drivers_by_name(
        self, 
        client: TestClient, 
        auth_headers: dict,
        current_user: CurrentUser,
        sample_driver: Driver
    ):
        """Test driver search by name"""
        from utils.auth import get_current_user
        from main import app
        
        def mock_get_current_user():
            return current_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        # Search by partial name
        search_term = sample_driver.full_name.split()[0]  # First name
        response = client.get(
            f"/api/v1/drivers/search?query={search_term}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find our sample driver
        driver_found = False
        for driver in data:
            if driver["id"] == str(sample_driver.id):
                driver_found = True
                break
        
        assert driver_found, "Driver not found in search results"
        
        app.dependency_overrides.clear()
    
    def test_search_drivers_by_license(
        self, 
        client: TestClient, 
        auth_headers: dict,
        current_user: CurrentUser,
        sample_driver: Driver
    ):
        """Test driver search by license number"""
        from utils.auth import get_current_user
        from main import app
        
        def mock_get_current_user():
            return current_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.get(
            f"/api/v1/drivers/search?query={sample_driver.license_number}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find our sample driver
        assert len(data) >= 1
        assert data[0]["id"] == str(sample_driver.id)
        
        app.dependency_overrides.clear()
    
    def test_search_drivers_by_languages(
        self, 
        client: TestClient, 
        auth_headers: dict,
        current_user: CurrentUser,
        sample_driver: Driver
    ):
        """Test driver search by languages"""
        from utils.auth import get_current_user
        from main import app
        
        def mock_get_current_user():
            return current_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.get(
            "/api/v1/drivers/search?languages=English,French",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find drivers with English or French
        for driver in data:
            languages = driver.get("languages_spoken", [])
            assert any(lang in ["English", "French"] for lang in languages)
        
        app.dependency_overrides.clear()


class TestDriverCompliance:
    """Test driver compliance tracking"""
    
    def test_get_expiring_licenses(
        self, 
        client: TestClient, 
        auth_headers: dict,
        current_user: CurrentUser,
        session: Session
    ):
        """Test getting drivers with expiring licenses"""
        from utils.auth import get_current_user
        from main import app
        
        def mock_get_current_user():
            return current_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        # Create driver with license expiring soon
        expiring_driver = Driver(
            full_name="Expiring License Driver",
            date_of_birth=date(1980, 1, 1),
            gender="Male",
            national_id="EXP123456",
            phone="+212-111-222-333",
            license_number="EXP123456789",
            license_type="Category D",
            license_issue_date=date(2020, 1, 1),
            license_expiry_date=date.today() + timedelta(days=15),  # Expires in 15 days
            employment_type="Permanent",
            hire_date=date(2020, 1, 1),
            status=DriverStatus.ACTIVE
        )
        
        session.add(expiring_driver)
        session.commit()
        session.refresh(expiring_driver)
        
        response = client.get(
            "/api/v1/drivers/expiring-licenses?days=30",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find our expiring driver
        expiring_found = False
        for driver in data:
            if driver["id"] == str(expiring_driver.id):
                expiring_found = True
                assert driver["days_until_license_expiry"] <= 30
                break
        
        assert expiring_found, "Expiring license driver not found"
        
        app.dependency_overrides.clear()
    
    def test_get_drivers_summary(
        self, 
        client: TestClient, 
        auth_headers: dict,
        current_user: CurrentUser,
        sample_driver: Driver
    ):
        """Test driver summary statistics"""
        from utils.auth import get_current_user
        from main import app
        
        def mock_get_current_user():
            return current_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.get(
            "/api/v1/drivers/summary",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "total_drivers" in data
        assert "active_drivers" in data
        assert "by_employment_type" in data
        assert "by_license_type" in data
        assert "average_performance_rating" in data
        
        # Should have at least our sample driver
        assert data["total_drivers"] >= 1
        
        app.dependency_overrides.clear()


class TestDriverPerformance:
    """Test driver performance tracking"""
    
    def test_get_driver_performance(
        self, 
        client: TestClient, 
        auth_headers: dict,
        current_user: CurrentUser,
        sample_driver: Driver
    ):
        """Test driver performance metrics"""
        from utils.auth import get_current_user
        from main import app
        
        def mock_get_current_user():
            return current_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.get(
            f"/api/v1/drivers/{sample_driver.id}/performance",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "driver_id" in data
        assert "driver_name" in data
        assert "total_assignments" in data
        assert "completion_rate" in data
        assert "performance_score" in data
        
        assert data["driver_id"] == str(sample_driver.id)
        assert data["driver_name"] == sample_driver.full_name
        
        app.dependency_overrides.clear()


class TestDriverValidation:
    """Test driver data validation"""
    
    def test_create_driver_invalid_age(
        self, 
        client: TestClient, 
        auth_headers: dict,
        current_user: CurrentUser
    ):
        """Test driver creation with invalid age"""
        from utils.auth import get_current_user
        from main import app
        
        def mock_get_current_user():
            return current_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        # Too young (under 21)
        driver_data = create_driver_data(
            date_of_birth=(date.today() - timedelta(days=365 * 18)).isoformat()
        )
        
        response = client.post(
            "/api/v1/drivers/",
            json=driver_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
        
        app.dependency_overrides.clear()
    
    def test_create_driver_expired_license(
        self, 
        client: TestClient, 
        auth_headers: dict,
        current_user: CurrentUser
    ):
        """Test driver creation with expired license"""
        from utils.auth import get_current_user
        from main import app
        
        def mock_get_current_user():
            return current_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        driver_data = create_driver_data(
            license_expiry_date=(date.today() - timedelta(days=1)).isoformat()
        )
        
        response = client.post(
            "/api/v1/drivers/",
            json=driver_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
        
        app.dependency_overrides.clear()
    
    def test_create_driver_invalid_phone(
        self, 
        client: TestClient, 
        auth_headers: dict,
        current_user: CurrentUser
    ):
        """Test driver creation with invalid phone number"""
        from utils.auth import get_current_user
        from main import app
        
        def mock_get_current_user():
            return current_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        driver_data = create_driver_data(
            phone="invalid-phone"
        )
        
        response = client.post(
            "/api/v1/drivers/",
            json=driver_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
        
        app.dependency_overrides.clear()
    
    def test_create_driver_invalid_email(
        self, 
        client: TestClient, 
        auth_headers: dict,
        current_user: CurrentUser
    ):
        """Test driver creation with invalid email"""
        from utils.auth import get_current_user
        from main import app
        
        def mock_get_current_user():
            return current_user
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        driver_data = create_driver_data(
            email="invalid-email"
        )
        
        response = client.post(
            "/api/v1/drivers/",
            json=driver_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
        
        app.dependency_overrides.clear()


class TestDriverAuthentication:
    """Test driver authentication and authorization"""
    
    def test_create_driver_unauthorized(self, client: TestClient):
        """Test driver creation without authentication"""
        driver_data = create_driver_data()
        
        response = client.post(
            "/api/v1/drivers/",
            json=driver_data
        )
        
        assert response.status_code == 401
    
    def test_get_driver_unauthorized(self, client: TestClient, sample_driver: Driver):
        """Test driver retrieval without authentication"""
        response = client.get(f"/api/v1/drivers/{sample_driver.id}")
        
        assert response.status_code == 401
    
    def test_update_driver_unauthorized(self, client: TestClient, sample_driver: Driver):
        """Test driver update without authentication"""
        update_data = {"phone": "+212-999-888-777"}
        
        response = client.put(
            f"/api/v1/drivers/{sample_driver.id}",
            json=update_data
        )
        
        assert response.status_code == 401
    
    def test_delete_driver_unauthorized(self, client: TestClient, sample_driver: Driver):
        """Test driver deletion without authentication"""
        response = client.delete(f"/api/v1/drivers/{sample_driver.id}")
        
        assert response.status_code == 401
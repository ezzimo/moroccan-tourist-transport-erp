"""
Tests for customer functionality
"""
import pytest
from fastapi.testclient import TestClient
from services.customer_service import CustomerService
from schemas.customer import CustomerCreate
from models.customer import ContactType, LoyaltyStatus


class TestCustomers:
    """Test class for customer endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_customer_individual(self, session, sample_customer_data):
        """Test creating an individual customer"""
        customer_service = CustomerService(session)
        customer_create = CustomerCreate(**sample_customer_data)
        
        customer = await customer_service.create_customer(customer_create)
        
        assert customer.full_name == sample_customer_data["full_name"]
        assert customer.email == sample_customer_data["email"]
        assert customer.contact_type == ContactType.INDIVIDUAL
        assert customer.loyalty_status == LoyaltyStatus.NEW
        assert customer.is_active is True
        assert len(customer.tags) == 2
        assert "VIP" in customer.tags
    
    @pytest.mark.asyncio
    async def test_create_customer_corporate(self, session, sample_corporate_customer_data):
        """Test creating a corporate customer"""
        customer_service = CustomerService(session)
        customer_create = CustomerCreate(**sample_corporate_customer_data)
        
        customer = await customer_service.create_customer(customer_create)
        
        assert customer.company_name == sample_corporate_customer_data["company_name"]
        assert customer.contact_type == ContactType.CORPORATE
        assert customer.preferred_language == "Arabic"
    
    @pytest.mark.asyncio
    async def test_create_customer_duplicate_email(self, session, sample_customer_data):
        """Test creating customer with duplicate email"""
        customer_service = CustomerService(session)
        customer_create = CustomerCreate(**sample_customer_data)
        
        # Create first customer
        await customer_service.create_customer(customer_create)
        
        # Try to create second customer with same email
        with pytest.raises(Exception) as exc_info:
            await customer_service.create_customer(customer_create)
        
        assert "Email already registered" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_customer(self, session, create_test_customer):
        """Test getting customer by ID"""
        customer_service = CustomerService(session)
        
        # Create test customer
        test_customer = create_test_customer(
            full_name="John Doe",
            email="john.doe@example.com"
        )
        
        # Get customer
        retrieved_customer = await customer_service.get_customer(test_customer.id)
        
        assert retrieved_customer.id == test_customer.id
        assert retrieved_customer.full_name == "John Doe"
        assert retrieved_customer.email == "john.doe@example.com"
    
    @pytest.mark.asyncio
    async def test_get_customer_not_found(self, session):
        """Test getting non-existent customer"""
        customer_service = CustomerService(session)
        
        import uuid
        fake_id = uuid.uuid4()
        
        with pytest.raises(Exception) as exc_info:
            await customer_service.get_customer(fake_id)
        
        assert "Customer not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_update_customer(self, session, create_test_customer):
        """Test updating customer information"""
        from schemas.customer import CustomerUpdate
        
        customer_service = CustomerService(session)
        
        # Create test customer
        test_customer = create_test_customer()
        
        # Update customer
        update_data = CustomerUpdate(
            full_name="Updated Name",
            loyalty_status=LoyaltyStatus.GOLD,
            tags=["Updated", "Tags"]
        )
        
        updated_customer = await customer_service.update_customer(
            test_customer.id, update_data
        )
        
        assert updated_customer.full_name == "Updated Name"
        assert updated_customer.loyalty_status == LoyaltyStatus.GOLD
        assert "Updated" in updated_customer.tags
        assert updated_customer.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_delete_customer(self, session, create_test_customer):
        """Test soft deleting customer"""
        customer_service = CustomerService(session)
        
        # Create test customer
        test_customer = create_test_customer()
        
        # Delete customer
        result = await customer_service.delete_customer(test_customer.id)
        
        assert "deactivated successfully" in result["message"]
        
        # Verify customer is marked as inactive
        updated_customer = await customer_service.get_customer(test_customer.id)
        assert updated_customer.is_active is False
    
    @pytest.mark.asyncio
    async def test_get_customer_summary(self, session, create_test_customer, create_test_interaction, create_test_feedback):
        """Test getting comprehensive customer summary"""
        customer_service = CustomerService(session)
        
        # Create test customer
        test_customer = create_test_customer()
        
        # Create test interactions
        create_test_interaction(test_customer.id, summary="First interaction")
        create_test_interaction(test_customer.id, summary="Second interaction")
        
        # Create test feedback
        create_test_feedback(test_customer.id, rating=5)
        create_test_feedback(test_customer.id, rating=4)
        
        # Get customer summary
        summary = await customer_service.get_customer_summary(test_customer.id)
        
        assert summary.id == test_customer.id
        assert summary.total_interactions == 2
        assert summary.total_feedback == 2
        assert summary.average_rating == 4.5
        assert "email" in summary.interaction_channels
        assert "Tour" in summary.feedback_by_service
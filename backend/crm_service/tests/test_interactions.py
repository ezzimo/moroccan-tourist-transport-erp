"""
Tests for interaction functionality
"""
import pytest
from services.interaction_service import InteractionService
from schemas.interaction import InteractionCreate
from models.interaction import ChannelType


class TestInteractions:
    """Test class for interaction endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_interaction(self, session, create_test_customer):
        """Test creating a new interaction"""
        interaction_service = InteractionService(session)
        
        # Create test customer
        test_customer = create_test_customer()
        
        # Create interaction
        interaction_data = InteractionCreate(
            customer_id=test_customer.id,
            channel=ChannelType.EMAIL,
            subject="Test Subject",
            summary="Test interaction summary",
            duration_minutes=30,
            follow_up_required=True
        )
        
        interaction = await interaction_service.create_interaction(interaction_data)
        
        assert interaction.customer_id == test_customer.id
        assert interaction.channel == ChannelType.EMAIL
        assert interaction.subject == "Test Subject"
        assert interaction.summary == "Test interaction summary"
        assert interaction.duration_minutes == 30
        assert interaction.follow_up_required is True
    
    @pytest.mark.asyncio
    async def test_create_interaction_invalid_customer(self, session):
        """Test creating interaction with invalid customer ID"""
        interaction_service = InteractionService(session)
        
        import uuid
        fake_customer_id = uuid.uuid4()
        
        interaction_data = InteractionCreate(
            customer_id=fake_customer_id,
            channel=ChannelType.EMAIL,
            summary="Test summary"
        )
        
        with pytest.raises(Exception) as exc_info:
            await interaction_service.create_interaction(interaction_data)
        
        assert "Customer not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_customer_interactions(self, session, create_test_customer, create_test_interaction):
        """Test getting all interactions for a customer"""
        from utils.pagination import PaginationParams
        
        interaction_service = InteractionService(session)
        
        # Create test customer
        test_customer = create_test_customer()
        
        # Create multiple interactions
        create_test_interaction(test_customer.id, summary="First interaction")
        create_test_interaction(test_customer.id, summary="Second interaction")
        create_test_interaction(test_customer.id, summary="Third interaction")
        
        # Get customer interactions
        pagination = PaginationParams(page=1, size=10)
        interactions, total = await interaction_service.get_customer_interactions(
            test_customer.id, pagination
        )
        
        assert total == 3
        assert len(interactions) == 3
        assert all(interaction.customer_id == test_customer.id for interaction in interactions)
    
    @pytest.mark.asyncio
    async def test_update_interaction(self, session, create_test_customer, create_test_interaction):
        """Test updating interaction information"""
        from schemas.interaction import InteractionUpdate
        
        interaction_service = InteractionService(session)
        
        # Create test customer and interaction
        test_customer = create_test_customer()
        test_interaction = create_test_interaction(test_customer.id)
        
        # Update interaction
        update_data = InteractionUpdate(
            summary="Updated summary",
            duration_minutes=45,
            follow_up_required=False
        )
        
        updated_interaction = await interaction_service.update_interaction(
            test_interaction.id, update_data
        )
        
        assert updated_interaction.summary == "Updated summary"
        assert updated_interaction.duration_minutes == 45
        assert updated_interaction.follow_up_required is False
    
    @pytest.mark.asyncio
    async def test_get_interaction_stats(self, session, create_test_customer, create_test_interaction):
        """Test getting interaction statistics"""
        interaction_service = InteractionService(session)
        
        # Create test customer
        test_customer = create_test_customer()
        
        # Create interactions with different channels
        create_test_interaction(test_customer.id, channel=ChannelType.EMAIL)
        create_test_interaction(test_customer.id, channel=ChannelType.PHONE)
        create_test_interaction(test_customer.id, channel=ChannelType.CHAT)
        create_test_interaction(test_customer.id, channel=ChannelType.EMAIL)
        
        # Get statistics
        stats = await interaction_service.get_interaction_stats(days=30)
        
        assert stats.total_interactions == 4
        assert stats.by_channel["email"] == 2
        assert stats.by_channel["phone"] == 1
        assert stats.by_channel["chat"] == 1
    
    @pytest.mark.asyncio
    async def test_delete_interaction(self, session, create_test_customer, create_test_interaction):
        """Test deleting interaction"""
        interaction_service = InteractionService(session)
        
        # Create test customer and interaction
        test_customer = create_test_customer()
        test_interaction = create_test_interaction(test_customer.id)
        
        # Delete interaction
        result = await interaction_service.delete_interaction(test_interaction.id)
        
        assert "deleted successfully" in result["message"]
        
        # Verify interaction is deleted
        with pytest.raises(Exception) as exc_info:
            await interaction_service.get_interaction(test_interaction.id)
        
        assert "Interaction not found" in str(exc_info.value)
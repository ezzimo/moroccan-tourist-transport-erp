"""
Tests for feedback functionality
"""
import pytest
from services.feedback_service import FeedbackService
from schemas.feedback import FeedbackCreate, FeedbackUpdate
from models.feedback import ServiceType


class TestFeedback:
    """Test class for feedback endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_feedback(self, session, create_test_customer):
        """Test creating new feedback"""
        feedback_service = FeedbackService(session)
        
        # Create test customer
        test_customer = create_test_customer()
        
        # Create feedback
        feedback_data = FeedbackCreate(
            customer_id=test_customer.id,
            service_type=ServiceType.TOUR,
            rating=5,
            comments="Excellent desert tour experience!",
            source="mobile"
        )
        
        feedback = await feedback_service.create_feedback(feedback_data)
        
        assert feedback.customer_id == test_customer.id
        assert feedback.service_type == ServiceType.TOUR
        assert feedback.rating == 5
        assert feedback.comments == "Excellent desert tour experience!"
        assert feedback.source == "mobile"
        assert feedback.sentiment == "positive"
        assert feedback.resolved is False
    
    @pytest.mark.asyncio
    async def test_create_feedback_invalid_customer(self, session):
        """Test creating feedback with invalid customer ID"""
        feedback_service = FeedbackService(session)
        
        import uuid
        fake_customer_id = uuid.uuid4()
        
        feedback_data = FeedbackCreate(
            customer_id=fake_customer_id,
            service_type=ServiceType.TOUR,
            rating=4,
            comments="Good service"
        )
        
        with pytest.raises(Exception) as exc_info:
            await feedback_service.create_feedback(feedback_data)
        
        assert "Customer not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_feedback_sentiment_analysis(self, session, create_test_customer):
        """Test feedback sentiment analysis based on rating"""
        feedback_service = FeedbackService(session)
        
        # Create test customer
        test_customer = create_test_customer()
        
        # Test positive sentiment (rating 4-5)
        positive_feedback = FeedbackCreate(
            customer_id=test_customer.id,
            service_type=ServiceType.TOUR,
            rating=5
        )
        positive_result = await feedback_service.create_feedback(positive_feedback)
        assert positive_result.sentiment == "positive"
        
        # Test neutral sentiment (rating 3)
        neutral_feedback = FeedbackCreate(
            customer_id=test_customer.id,
            service_type=ServiceType.BOOKING,
            rating=3
        )
        neutral_result = await feedback_service.create_feedback(neutral_feedback)
        assert neutral_result.sentiment == "neutral"
        
        # Test negative sentiment (rating 1-2)
        negative_feedback = FeedbackCreate(
            customer_id=test_customer.id,
            service_type=ServiceType.SUPPORT,
            rating=2
        )
        negative_result = await feedback_service.create_feedback(negative_feedback)
        assert negative_result.sentiment == "negative"
    
    @pytest.mark.asyncio
    async def test_update_feedback_resolution(self, session, create_test_customer, create_test_feedback):
        """Test updating feedback for resolution"""
        feedback_service = FeedbackService(session)
        
        # Create test customer and feedback
        test_customer = create_test_customer()
        test_feedback = create_test_feedback(
            test_customer.id,
            rating=2,
            comments="Poor service quality"
        )
        
        # Resolve feedback
        import uuid
        resolver_id = uuid.uuid4()
        
        update_data = FeedbackUpdate(
            resolved=True,
            resolution_notes="Issue addressed and customer contacted",
            resolved_by=resolver_id
        )
        
        updated_feedback = await feedback_service.update_feedback(
            test_feedback.id, update_data
        )
        
        assert updated_feedback.resolved is True
        assert updated_feedback.resolution_notes == "Issue addressed and customer contacted"
        assert updated_feedback.resolved_by == resolver_id
        assert updated_feedback.resolved_at is not None
    
    @pytest.mark.asyncio
    async def test_get_customer_feedback(self, session, create_test_customer, create_test_feedback):
        """Test getting all feedback for a customer"""
        from utils.pagination import PaginationParams
        
        feedback_service = FeedbackService(session)
        
        # Create test customer
        test_customer = create_test_customer()
        
        # Create multiple feedback entries
        create_test_feedback(test_customer.id, rating=5, service_type=ServiceType.TOUR)
        create_test_feedback(test_customer.id, rating=4, service_type=ServiceType.BOOKING)
        create_test_feedback(test_customer.id, rating=3, service_type=ServiceType.SUPPORT)
        
        # Get customer feedback
        pagination = PaginationParams(page=1, size=10)
        feedback_list, total = await feedback_service.get_customer_feedback(
            test_customer.id, pagination
        )
        
        assert total == 3
        assert len(feedback_list) == 3
        assert all(feedback.customer_id == test_customer.id for feedback in feedback_list)
    
    @pytest.mark.asyncio
    async def test_get_feedback_stats(self, session, create_test_customer, create_test_feedback):
        """Test getting feedback statistics"""
        feedback_service = FeedbackService(session)
        
        # Create test customer
        test_customer = create_test_customer()
        
        # Create feedback with different ratings and service types
        create_test_feedback(test_customer.id, rating=5, service_type=ServiceType.TOUR)
        create_test_feedback(test_customer.id, rating=4, service_type=ServiceType.TOUR)
        create_test_feedback(test_customer.id, rating=3, service_type=ServiceType.BOOKING)
        create_test_feedback(test_customer.id, rating=2, service_type=ServiceType.SUPPORT, resolved=True)
        create_test_feedback(test_customer.id, rating=1, service_type=ServiceType.SUPPORT)
        
        # Get statistics
        stats = await feedback_service.get_feedback_stats(days=30)
        
        assert stats.total_feedback == 5
        assert stats.average_rating == 3.0  # (5+4+3+2+1)/5
        assert stats.rating_distribution["5"] == 1
        assert stats.rating_distribution["4"] == 1
        assert stats.rating_distribution["3"] == 1
        assert stats.rating_distribution["2"] == 1
        assert stats.rating_distribution["1"] == 1
        
        # Check service type distribution
        assert stats.by_service_type["Tour"] == 2
        assert stats.by_service_type["Booking"] == 1
        assert stats.by_service_type["Support"] == 2
        
        # Check sentiment analysis
        assert stats.sentiment_analysis["positive"] == 2  # ratings 4-5
        assert stats.sentiment_analysis["neutral"] == 1   # rating 3
        assert stats.sentiment_analysis["negative"] == 2  # ratings 1-2
        
        # Check resolution rate
        assert stats.resolution_rate == 20.0  # 1 out of 5 resolved
        assert stats.pending_resolution == 4
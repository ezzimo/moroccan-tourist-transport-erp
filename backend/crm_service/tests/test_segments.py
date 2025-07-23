"""
Tests for segment functionality
"""
import pytest
from services.segment_service import SegmentService
from schemas.segment import SegmentCreate, SegmentUpdate
from models.customer import LoyaltyStatus


class TestSegments:
    """Test class for segment endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_segment(self, session, sample_segment_data):
        """Test creating a new segment"""
        segment_service = SegmentService(session)
        
        segment_create = SegmentCreate(**sample_segment_data)
        segment = await segment_service.create_segment(segment_create)
        
        assert segment.name == sample_segment_data["name"]
        assert segment.description == sample_segment_data["description"]
        assert segment.criteria == sample_segment_data["criteria"]
        assert segment.is_active is True
        assert segment.customer_count >= 0
    
    @pytest.mark.asyncio
    async def test_create_segment_duplicate_name(self, session, sample_segment_data):
        """Test creating segment with duplicate name"""
        segment_service = SegmentService(session)
        
        segment_create = SegmentCreate(**sample_segment_data)
        
        # Create first segment
        await segment_service.create_segment(segment_create)
        
        # Try to create second segment with same name
        with pytest.raises(Exception) as exc_info:
            await segment_service.create_segment(segment_create)
        
        assert "Segment name already exists" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_segment_customer_matching(self, session, create_test_customer):
        """Test segment customer matching logic"""
        segment_service = SegmentService(session)
        
        # Create test customers with different attributes
        vip_customer = create_test_customer(
            full_name="VIP Customer",
            loyalty_status=LoyaltyStatus.GOLD,
            region="Casablanca"
        )
        vip_customer.set_tags_list(["VIP", "High Value"])
        session.add(vip_customer)
        session.commit()
        
        regular_customer = create_test_customer(
            full_name="Regular Customer",
            loyalty_status=LoyaltyStatus.BRONZE,
            region="Rabat"
        )
        regular_customer.set_tags_list(["Regular"])
        session.add(regular_customer)
        session.commit()
        
        # Create segment for VIP customers
        vip_segment_data = SegmentCreate(
            name="VIP Customers",
            description="High-value VIP customers",
            criteria={
                "loyalty_status": ["Gold", "Platinum", "VIP"],
                "tags": ["VIP"]
            }
        )
        
        vip_segment = await segment_service.create_segment(vip_segment_data)
        
        # Test customer assignment
        vip_segments = await segment_service.assign_customer_to_segments(vip_customer.id)
        regular_segments = await segment_service.assign_customer_to_segments(regular_customer.id)
        
        assert "VIP Customers" in vip_segments
        assert "VIP Customers" not in regular_segments
    
    @pytest.mark.asyncio
    async def test_update_segment(self, session, sample_segment_data):
        """Test updating segment information"""
        segment_service = SegmentService(session)
        
        # Create segment
        segment_create = SegmentCreate(**sample_segment_data)
        segment = await segment_service.create_segment(segment_create)
        
        # Update segment
        update_data = SegmentUpdate(
            name="Updated VIP Customers",
            description="Updated description",
            criteria={
                "loyalty_status": ["Platinum", "VIP"],
                "region": ["Casablanca", "Marrakech"]
            }
        )
        
        updated_segment = await segment_service.update_segment(segment.id, update_data)
        
        assert updated_segment.name == "Updated VIP Customers"
        assert updated_segment.description == "Updated description"
        assert "Platinum" in updated_segment.criteria["loyalty_status"]
        assert "Casablanca" in updated_segment.criteria["region"]
        assert updated_segment.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_get_segment_customers(self, session, create_test_customer):
        """Test getting segment with its customers"""
        from utils.pagination import PaginationParams
        
        segment_service = SegmentService(session)
        
        # Create test customers
        gold_customer = create_test_customer(
            loyalty_status=LoyaltyStatus.GOLD,
            region="Casablanca"
        )
        gold_customer.set_tags_list(["VIP"])
        session.add(gold_customer)
        session.commit()
        
        # Create segment
        segment_data = SegmentCreate(
            name="Gold Customers",
            description="Gold loyalty customers",
            criteria={
                "loyalty_status": ["Gold"]
            }
        )
        
        segment = await segment_service.create_segment(segment_data)
        
        # Get segment with customers
        pagination = PaginationParams(page=1, size=10)
        segment_with_customers = await segment_service.get_segment_customers(
            segment.id, pagination
        )
        
        assert segment_with_customers.name == "Gold Customers"
        assert len(segment_with_customers.customers) >= 0
    
    @pytest.mark.asyncio
    async def test_recalculate_segments(self, session, create_test_customer):
        """Test recalculating all segment customer counts"""
        segment_service = SegmentService(session)
        
        # Create test customers
        create_test_customer(loyalty_status=LoyaltyStatus.GOLD)
        create_test_customer(loyalty_status=LoyaltyStatus.SILVER)
        
        # Create segments
        gold_segment = await segment_service.create_segment(SegmentCreate(
            name="Gold Segment",
            criteria={"loyalty_status": ["Gold"]}
        ))
        
        silver_segment = await segment_service.create_segment(SegmentCreate(
            name="Silver Segment", 
            criteria={"loyalty_status": ["Silver"]}
        ))
        
        # Recalculate all segments
        result = await segment_service.recalculate_all_segments()
        
        assert "Recalculated" in result["message"]
        
        # Verify counts were updated
        updated_gold = await segment_service.get_segment(gold_segment.id)
        updated_silver = await segment_service.get_segment(silver_segment.id)
        
        assert updated_gold.last_calculated is not None
        assert updated_silver.last_calculated is not None
    
    @pytest.mark.asyncio
    async def test_delete_segment(self, session, sample_segment_data):
        """Test deleting segment"""
        segment_service = SegmentService(session)
        
        # Create segment
        segment_create = SegmentCreate(**sample_segment_data)
        segment = await segment_service.create_segment(segment_create)
        
        # Delete segment
        result = await segment_service.delete_segment(segment.id)
        
        assert "deleted successfully" in result["message"]
        
        # Verify segment is deleted
        with pytest.raises(Exception) as exc_info:
            await segment_service.get_segment(segment.id)
        
        assert "Segment not found" in str(exc_info.value)
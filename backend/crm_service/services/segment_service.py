"""
Segment service for customer segmentation operations
"""
from sqlmodel import Session, select, func
from fastapi import HTTPException, status
from models.segment import Segment
from models.customer import Customer
from schemas.segment import SegmentCreate, SegmentUpdate, SegmentResponse, SegmentWithCustomers
from schemas.customer import CustomerResponse
from utils.pagination import PaginationParams, paginate_query
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
import uuid


class SegmentService:
    """Service for handling segment operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_segment(self, segment_data: SegmentCreate) -> SegmentResponse:
        """Create a new segment"""
        # Check if segment name already exists
        statement = select(Segment).where(Segment.name == segment_data.name)
        existing_segment = self.session.exec(statement).first()
        
        if existing_segment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Segment name already exists"
            )
        
        # Create segment
        segment = Segment(
            name=segment_data.name,
            description=segment_data.description
        )
        segment.set_criteria_dict(segment_data.criteria)
        
        self.session.add(segment)
        self.session.commit()
        self.session.refresh(segment)
        
        # Calculate initial customer count
        await self._update_segment_count(segment.id)
        
        return SegmentResponse(
            id=segment.id,
            name=segment.name,
            description=segment.description,
            criteria=segment.get_criteria_dict(),
            is_active=segment.is_active,
            customer_count=segment.customer_count,
            created_at=segment.created_at,
            updated_at=segment.updated_at,
            last_calculated=segment.last_calculated
        )
    
    async def get_segment(self, segment_id: uuid.UUID) -> SegmentResponse:
        """Get segment by ID"""
        statement = select(Segment).where(Segment.id == segment_id)
        segment = self.session.exec(statement).first()
        
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Segment not found"
            )
        
        return SegmentResponse(
            id=segment.id,
            name=segment.name,
            description=segment.description,
            criteria=segment.get_criteria_dict(),
            is_active=segment.is_active,
            customer_count=segment.customer_count,
            created_at=segment.created_at,
            updated_at=segment.updated_at,
            last_calculated=segment.last_calculated
        )
    
    async def get_segments(
        self, 
        pagination: PaginationParams,
        is_active: Optional[bool] = None
    ) -> Tuple[List[SegmentResponse], int]:
        """Get list of segments"""
        query = select(Segment)
        
        if is_active is not None:
            query = query.where(Segment.is_active == is_active)
        
        # Order by creation date (newest first)
        query = query.order_by(Segment.created_at.desc())
        
        segments, total = paginate_query(self.session, query, pagination)
        
        response_list = []
        for segment in segments:
            response_list.append(SegmentResponse(
                id=segment.id,
                name=segment.name,
                description=segment.description,
                criteria=segment.get_criteria_dict(),
                is_active=segment.is_active,
                customer_count=segment.customer_count,
                created_at=segment.created_at,
                updated_at=segment.updated_at,
                last_calculated=segment.last_calculated
            ))
        
        return response_list, total
    
    async def update_segment(self, segment_id: uuid.UUID, segment_data: SegmentUpdate) -> SegmentResponse:
        """Update segment information"""
        statement = select(Segment).where(Segment.id == segment_id)
        segment = self.session.exec(statement).first()
        
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Segment not found"
            )
        
        # Update fields
        update_data = segment_data.model_dump(exclude_unset=True, exclude={"criteria"})
        
        for field, value in update_data.items():
            setattr(segment, field, value)
        
        # Handle criteria separately
        if segment_data.criteria is not None:
            segment.set_criteria_dict(segment_data.criteria)
        
        segment.updated_at = datetime.utcnow()
        
        self.session.add(segment)
        self.session.commit()
        self.session.refresh(segment)
        
        # Recalculate customer count if criteria changed
        if segment_data.criteria is not None:
            await self._update_segment_count(segment.id)
        
        return SegmentResponse(
            id=segment.id,
            name=segment.name,
            description=segment.description,
            criteria=segment.get_criteria_dict(),
            is_active=segment.is_active,
            customer_count=segment.customer_count,
            created_at=segment.created_at,
            updated_at=segment.updated_at,
            last_calculated=segment.last_calculated
        )
    
    async def delete_segment(self, segment_id: uuid.UUID) -> dict:
        """Delete segment"""
        statement = select(Segment).where(Segment.id == segment_id)
        segment = self.session.exec(statement).first()
        
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Segment not found"
            )
        
        self.session.delete(segment)
        self.session.commit()
        
        return {"message": "Segment deleted successfully"}
    
    async def get_segment_customers(
        self, 
        segment_id: uuid.UUID, 
        pagination: PaginationParams
    ) -> SegmentWithCustomers:
        """Get segment with its customers"""
        statement = select(Segment).where(Segment.id == segment_id)
        segment = self.session.exec(statement).first()
        
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Segment not found"
            )
        
        # Get customers that match the segment criteria
        customers = await self._get_matching_customers(segment, pagination)
        
        segment_response = SegmentResponse(
            id=segment.id,
            name=segment.name,
            description=segment.description,
            criteria=segment.get_criteria_dict(),
            is_active=segment.is_active,
            customer_count=segment.customer_count,
            created_at=segment.created_at,
            updated_at=segment.updated_at,
            last_calculated=segment.last_calculated
        )
        
        return SegmentWithCustomers(
            **segment_response.model_dump(),
            customers=[CustomerResponse.from_model(customer) for customer in customers]
        )
    
    async def assign_customer_to_segments(self, customer_id: uuid.UUID) -> List[str]:
        """Assign customer to matching segments and return segment names"""
        # Get customer
        customer_stmt = select(Customer).where(Customer.id == customer_id)
        customer = self.session.exec(customer_stmt).first()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Get all active segments
        segments_stmt = select(Segment).where(Segment.is_active == True)
        segments = self.session.exec(segments_stmt).all()
        
        matching_segments = []
        for segment in segments:
            if segment.matches_customer(customer):
                matching_segments.append(segment.name)
        
        return matching_segments
    
    async def recalculate_all_segments(self) -> dict:
        """Recalculate customer counts for all segments"""
        segments_stmt = select(Segment).where(Segment.is_active == True)
        segments = self.session.exec(segments_stmt).all()
        
        updated_count = 0
        for segment in segments:
            await self._update_segment_count(segment.id)
            updated_count += 1
        
        return {"message": f"Recalculated {updated_count} segments"}
    
    async def _update_segment_count(self, segment_id: uuid.UUID):
        """Update customer count for a segment"""
        statement = select(Segment).where(Segment.id == segment_id)
        segment = self.session.exec(statement).first()
        
        if not segment:
            return
        
        # Get all active customers
        customers_stmt = select(Customer).where(Customer.is_active == True)
        customers = self.session.exec(customers_stmt).all()
        
        # Count matching customers
        count = 0
        for customer in customers:
            if segment.matches_customer(customer):
                count += 1
        
        # Update segment
        segment.customer_count = count
        segment.last_calculated = datetime.utcnow()
        
        self.session.add(segment)
        self.session.commit()
    
    async def _get_matching_customers(self, segment: Segment, pagination: PaginationParams) -> List[Customer]:
        """Get customers that match segment criteria with pagination"""
        # For now, we'll get all customers and filter in Python
        # In production, you'd want to convert criteria to SQL queries for better performance
        customers_stmt = select(Customer).where(Customer.is_active == True)
        all_customers = self.session.exec(customers_stmt).all()
        
        matching_customers = []
        for customer in all_customers:
            if segment.matches_customer(customer):
                matching_customers.append(customer)
        
        # Apply pagination manually
        start = pagination.offset
        end = start + pagination.size
        
        return matching_customers[start:end]
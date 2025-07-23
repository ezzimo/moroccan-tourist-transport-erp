"""
Interaction service for customer communication tracking
"""
from sqlmodel import Session, select, func
from fastapi import HTTPException, status
from models.interaction import Interaction
from models.customer import Customer
from schemas.interaction import InteractionCreate, InteractionUpdate, InteractionResponse, InteractionStats
from utils.pagination import PaginationParams, paginate_query
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
import uuid


class InteractionService:
    """Service for handling interaction operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_interaction(self, interaction_data: InteractionCreate) -> InteractionResponse:
        """Create a new interaction"""
        # Verify customer exists
        customer_stmt = select(Customer).where(Customer.id == interaction_data.customer_id)
        customer = self.session.exec(customer_stmt).first()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Create interaction
        interaction = Interaction(**interaction_data.model_dump())
        
        self.session.add(interaction)
        
        # Update customer's last interaction timestamp
        customer.last_interaction = datetime.utcnow()
        customer.updated_at = datetime.utcnow()
        self.session.add(customer)
        
        self.session.commit()
        self.session.refresh(interaction)
        
        return InteractionResponse(**interaction.model_dump())
    
    async def get_interaction(self, interaction_id: uuid.UUID) -> InteractionResponse:
        """Get interaction by ID"""
        statement = select(Interaction).where(Interaction.id == interaction_id)
        interaction = self.session.exec(statement).first()
        
        if not interaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interaction not found"
            )
        
        return InteractionResponse(**interaction.model_dump())
    
    async def get_interactions(
        self, 
        pagination: PaginationParams,
        customer_id: Optional[uuid.UUID] = None,
        staff_member_id: Optional[uuid.UUID] = None,
        channel: Optional[str] = None,
        follow_up_required: Optional[bool] = None
    ) -> Tuple[List[InteractionResponse], int]:
        """Get list of interactions with optional filters"""
        query = select(Interaction)
        
        # Apply filters
        conditions = []
        
        if customer_id:
            conditions.append(Interaction.customer_id == customer_id)
        
        if staff_member_id:
            conditions.append(Interaction.staff_member_id == staff_member_id)
        
        if channel:
            conditions.append(Interaction.channel == channel)
        
        if follow_up_required is not None:
            conditions.append(Interaction.follow_up_required == follow_up_required)
        
        if conditions:
            query = query.where(*conditions)
        
        # Order by timestamp (newest first)
        query = query.order_by(Interaction.timestamp.desc())
        
        interactions, total = paginate_query(self.session, query, pagination)
        
        return [InteractionResponse(**interaction.model_dump()) for interaction in interactions], total
    
    async def update_interaction(self, interaction_id: uuid.UUID, interaction_data: InteractionUpdate) -> InteractionResponse:
        """Update interaction information"""
        statement = select(Interaction).where(Interaction.id == interaction_id)
        interaction = self.session.exec(statement).first()
        
        if not interaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interaction not found"
            )
        
        # Update fields
        update_data = interaction_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(interaction, field, value)
        
        self.session.add(interaction)
        self.session.commit()
        self.session.refresh(interaction)
        
        return InteractionResponse(**interaction.model_dump())
    
    async def delete_interaction(self, interaction_id: uuid.UUID) -> dict:
        """Delete interaction"""
        statement = select(Interaction).where(Interaction.id == interaction_id)
        interaction = self.session.exec(statement).first()
        
        if not interaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interaction not found"
            )
        
        self.session.delete(interaction)
        self.session.commit()
        
        return {"message": "Interaction deleted successfully"}
    
    async def get_customer_interactions(
        self, 
        customer_id: uuid.UUID, 
        pagination: PaginationParams
    ) -> Tuple[List[InteractionResponse], int]:
        """Get all interactions for a specific customer"""
        # Verify customer exists
        customer_stmt = select(Customer).where(Customer.id == customer_id)
        customer = self.session.exec(customer_stmt).first()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        return await self.get_interactions(pagination, customer_id=customer_id)
    
    async def get_interaction_stats(self, days: int = 30) -> InteractionStats:
        """Get interaction statistics for the specified period"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total interactions
        total_stmt = select(func.count(Interaction.id)).where(
            Interaction.timestamp >= start_date
        )
        total_interactions = self.session.exec(total_stmt).one()
        
        # By channel
        channel_stmt = select(
            Interaction.channel, func.count(Interaction.id)
        ).where(
            Interaction.timestamp >= start_date
        ).group_by(Interaction.channel)
        
        by_channel = {}
        for channel, count in self.session.exec(channel_stmt):
            by_channel[channel.value] = count
        
        # By month (last 12 months)
        monthly_stmt = select(
            func.date_trunc('month', Interaction.timestamp).label('month'),
            func.count(Interaction.id)
        ).where(
            Interaction.timestamp >= datetime.utcnow() - timedelta(days=365)
        ).group_by(func.date_trunc('month', Interaction.timestamp))
        
        by_month = {}
        for month, count in self.session.exec(monthly_stmt):
            by_month[month.strftime('%Y-%m')] = count
        
        # Average duration
        avg_duration_stmt = select(func.avg(Interaction.duration_minutes)).where(
            Interaction.timestamp >= start_date,
            Interaction.duration_minutes.is_not(None)
        )
        average_duration = self.session.exec(avg_duration_stmt).one()
        
        # Follow-ups pending
        follow_ups_stmt = select(func.count(Interaction.id)).where(
            Interaction.follow_up_required == True,
            Interaction.follow_up_date <= datetime.utcnow()
        )
        follow_ups_pending = self.session.exec(follow_ups_stmt).one()
        
        return InteractionStats(
            total_interactions=total_interactions,
            by_channel=by_channel,
            by_month=by_month,
            average_duration=float(average_duration) if average_duration else None,
            follow_ups_pending=follow_ups_pending
        )
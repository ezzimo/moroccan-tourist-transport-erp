"""
Customer service for customer management operations
"""
from sqlmodel import Session, select, or_, and_, func
from fastapi import HTTPException, status
from models.customer import Customer
from models.interaction import Interaction
from models.feedback import Feedback
from schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerSummary, CustomerSearch
from utils.pagination import PaginationParams, paginate_query
from typing import List, Optional, Tuple
from datetime import datetime
import uuid


class CustomerService:
    """Service for handling customer operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_customer(self, customer_data: CustomerCreate) -> CustomerResponse:
        """Create a new customer"""
        # Check if email already exists
        statement = select(Customer).where(Customer.email == customer_data.email)
        existing_customer = self.session.exec(statement).first()
        
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create customer
        customer = Customer(**customer_data.model_dump(exclude={"tags"}))
        if customer_data.tags:
            customer.set_tags_list(customer_data.tags)
        
        self.session.add(customer)
        self.session.commit()
        self.session.refresh(customer)
        
        return CustomerResponse.from_model(customer)
    
    async def get_customer(self, customer_id: uuid.UUID) -> CustomerResponse:
        """Get customer by ID"""
        statement = select(Customer).where(Customer.id == customer_id)
        customer = self.session.exec(statement).first()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        return CustomerResponse.from_model(customer)
    
    async def get_customers(
        self, 
        pagination: PaginationParams,
        search: Optional[CustomerSearch] = None
    ) -> Tuple[List[CustomerResponse], int]:
        """Get list of customers with optional search"""
        query = select(Customer)
        
        # Apply search filters
        if search:
            conditions = []
            
            if search.query:
                search_term = f"%{search.query}%"
                conditions.append(
                    or_(
                        Customer.full_name.ilike(search_term),
                        Customer.company_name.ilike(search_term),
                        Customer.email.ilike(search_term),
                        Customer.phone.ilike(search_term)
                    )
                )
            
            if search.contact_type:
                conditions.append(Customer.contact_type == search.contact_type)
            
            if search.region:
                conditions.append(Customer.region == search.region)
            
            if search.loyalty_status:
                conditions.append(Customer.loyalty_status == search.loyalty_status)
            
            if search.is_active is not None:
                conditions.append(Customer.is_active == search.is_active)
            
            if search.tags:
                # Search for customers with any of the specified tags
                tag_conditions = []
                for tag in search.tags:
                    tag_conditions.append(Customer.tags.ilike(f'%"{tag}"%'))
                conditions.append(or_(*tag_conditions))
            
            if conditions:
                query = query.where(and_(*conditions))
        
        # Order by creation date (newest first)
        query = query.order_by(Customer.created_at.desc())
        
        customers, total = paginate_query(self.session, query, pagination)
        
        return [CustomerResponse.from_model(customer) for customer in customers], total
    
    async def update_customer(self, customer_id: uuid.UUID, customer_data: CustomerUpdate) -> CustomerResponse:
        """Update customer information"""
        statement = select(Customer).where(Customer.id == customer_id)
        customer = self.session.exec(statement).first()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Update fields
        update_data = customer_data.model_dump(exclude_unset=True, exclude={"tags"})
        
        for field, value in update_data.items():
            setattr(customer, field, value)
        
        # Handle tags separately
        if customer_data.tags is not None:
            customer.set_tags_list(customer_data.tags)
        
        customer.updated_at = datetime.utcnow()
        
        self.session.add(customer)
        self.session.commit()
        self.session.refresh(customer)
        
        return CustomerResponse.from_model(customer)
    
    async def delete_customer(self, customer_id: uuid.UUID) -> dict:
        """Delete customer (soft delete by marking inactive)"""
        statement = select(Customer).where(Customer.id == customer_id)
        customer = self.session.exec(statement).first()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        customer.is_active = False
        customer.updated_at = datetime.utcnow()
        
        self.session.add(customer)
        self.session.commit()
        
        return {"message": "Customer deactivated successfully"}
    
    async def get_customer_summary(self, customer_id: uuid.UUID) -> CustomerSummary:
        """Get comprehensive customer summary with statistics"""
        statement = select(Customer).where(Customer.id == customer_id)
        customer = self.session.exec(statement).first()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Get interaction statistics
        interaction_count_stmt = select(func.count(Interaction.id)).where(
            Interaction.customer_id == customer_id
        )
        total_interactions = self.session.exec(interaction_count_stmt).one()
        
        # Get interaction channels breakdown
        channel_stats_stmt = select(
            Interaction.channel, func.count(Interaction.id)
        ).where(
            Interaction.customer_id == customer_id
        ).group_by(Interaction.channel)
        
        interaction_channels = {}
        for channel, count in self.session.exec(channel_stats_stmt):
            interaction_channels[channel.value] = count
        
        # Get feedback statistics
        feedback_count_stmt = select(func.count(Feedback.id)).where(
            Feedback.customer_id == customer_id
        )
        total_feedback = self.session.exec(feedback_count_stmt).one()
        
        # Get average rating
        avg_rating_stmt = select(func.avg(Feedback.rating)).where(
            Feedback.customer_id == customer_id
        )
        average_rating = self.session.exec(avg_rating_stmt).one()
        
        # Get last feedback date
        last_feedback_stmt = select(func.max(Feedback.submitted_at)).where(
            Feedback.customer_id == customer_id
        )
        last_feedback_date = self.session.exec(last_feedback_stmt).one()
        
        # Get feedback by service type
        service_stats_stmt = select(
            Feedback.service_type, func.count(Feedback.id)
        ).where(
            Feedback.customer_id == customer_id
        ).group_by(Feedback.service_type)
        
        feedback_by_service = {}
        for service_type, count in self.session.exec(service_stats_stmt):
            feedback_by_service[service_type.value] = count
        
        # Create summary response
        base_response = CustomerResponse.from_model(customer)
        
        return CustomerSummary(
            **base_response.model_dump(),
            total_interactions=total_interactions,
            total_feedback=total_feedback,
            average_rating=float(average_rating) if average_rating else None,
            last_feedback_date=last_feedback_date,
            segments=[],  # TODO: Implement segment assignment
            interaction_channels=interaction_channels,
            feedback_by_service=feedback_by_service
        )
"""
Feedback service for customer service evaluation
"""
from sqlmodel import Session, select, func
from fastapi import HTTPException, status
from models.feedback import Feedback
from models.customer import Customer
from schemas.feedback import FeedbackCreate, FeedbackUpdate, FeedbackResponse, FeedbackStats
from utils.pagination import PaginationParams, paginate_query
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
import uuid


class FeedbackService:
    """Service for handling feedback operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_feedback(self, feedback_data: FeedbackCreate) -> FeedbackResponse:
        """Create new feedback"""
        # Verify customer exists
        customer_stmt = select(Customer).where(Customer.id == feedback_data.customer_id)
        customer = self.session.exec(customer_stmt).first()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Create feedback
        feedback = Feedback(**feedback_data.model_dump())
        
        self.session.add(feedback)
        self.session.commit()
        self.session.refresh(feedback)
        
        # Create response with sentiment
        response_data = feedback.model_dump()
        response_data["sentiment"] = feedback.get_sentiment()
        
        return FeedbackResponse(**response_data)
    
    async def get_feedback(self, feedback_id: uuid.UUID) -> FeedbackResponse:
        """Get feedback by ID"""
        statement = select(Feedback).where(Feedback.id == feedback_id)
        feedback = self.session.exec(statement).first()
        
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )
        
        response_data = feedback.model_dump()
        response_data["sentiment"] = feedback.get_sentiment()
        
        return FeedbackResponse(**response_data)
    
    async def get_feedback_list(
        self, 
        pagination: PaginationParams,
        customer_id: Optional[uuid.UUID] = None,
        service_type: Optional[str] = None,
        rating: Optional[int] = None,
        resolved: Optional[bool] = None,
        booking_id: Optional[uuid.UUID] = None
    ) -> Tuple[List[FeedbackResponse], int]:
        """Get list of feedback with optional filters"""
        query = select(Feedback)
        
        # Apply filters
        conditions = []
        
        if customer_id:
            conditions.append(Feedback.customer_id == customer_id)
        
        if service_type:
            conditions.append(Feedback.service_type == service_type)
        
        if rating:
            conditions.append(Feedback.rating == rating)
        
        if resolved is not None:
            conditions.append(Feedback.resolved == resolved)
        
        if booking_id:
            conditions.append(Feedback.booking_id == booking_id)
        
        if conditions:
            query = query.where(*conditions)
        
        # Order by submission date (newest first)
        query = query.order_by(Feedback.submitted_at.desc())
        
        feedback_list, total = paginate_query(self.session, query, pagination)
        
        # Add sentiment to each feedback
        response_list = []
        for feedback in feedback_list:
            response_data = feedback.model_dump()
            response_data["sentiment"] = feedback.get_sentiment()
            response_list.append(FeedbackResponse(**response_data))
        
        return response_list, total
    
    async def update_feedback(self, feedback_id: uuid.UUID, feedback_data: FeedbackUpdate) -> FeedbackResponse:
        """Update feedback (mainly for resolution)"""
        statement = select(Feedback).where(Feedback.id == feedback_id)
        feedback = self.session.exec(statement).first()
        
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )
        
        # Update fields
        update_data = feedback_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(feedback, field, value)
        
        # Set resolved timestamp if marking as resolved
        if feedback_data.resolved and not feedback.resolved:
            feedback.resolved_at = datetime.utcnow()
        
        self.session.add(feedback)
        self.session.commit()
        self.session.refresh(feedback)
        
        response_data = feedback.model_dump()
        response_data["sentiment"] = feedback.get_sentiment()
        
        return FeedbackResponse(**response_data)
    
    async def delete_feedback(self, feedback_id: uuid.UUID) -> dict:
        """Delete feedback"""
        statement = select(Feedback).where(Feedback.id == feedback_id)
        feedback = self.session.exec(statement).first()
        
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )
        
        self.session.delete(feedback)
        self.session.commit()
        
        return {"message": "Feedback deleted successfully"}
    
    async def get_customer_feedback(
        self, 
        customer_id: uuid.UUID, 
        pagination: PaginationParams
    ) -> Tuple[List[FeedbackResponse], int]:
        """Get all feedback for a specific customer"""
        # Verify customer exists
        customer_stmt = select(Customer).where(Customer.id == customer_id)
        customer = self.session.exec(customer_stmt).first()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        return await self.get_feedback_list(pagination, customer_id=customer_id)
    
    async def get_feedback_stats(self, days: int = 30) -> FeedbackStats:
        """Get feedback statistics for the specified period"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total feedback
        total_stmt = select(func.count(Feedback.id)).where(
            Feedback.submitted_at >= start_date
        )
        total_feedback = self.session.exec(total_stmt).one()
        
        # Average rating
        avg_rating_stmt = select(func.avg(Feedback.rating)).where(
            Feedback.submitted_at >= start_date
        )
        average_rating = self.session.exec(avg_rating_stmt).one() or 0.0
        
        # Rating distribution
        rating_dist_stmt = select(
            Feedback.rating, func.count(Feedback.id)
        ).where(
            Feedback.submitted_at >= start_date
        ).group_by(Feedback.rating)
        
        rating_distribution = {}
        for rating, count in self.session.exec(rating_dist_stmt):
            rating_distribution[str(rating)] = count
        
        # By service type
        service_stmt = select(
            Feedback.service_type, func.count(Feedback.id)
        ).where(
            Feedback.submitted_at >= start_date
        ).group_by(Feedback.service_type)
        
        by_service_type = {}
        for service_type, count in self.session.exec(service_stmt):
            by_service_type[service_type.value] = count
        
        # Sentiment analysis
        sentiment_analysis = {
            "positive": 0,
            "neutral": 0,
            "negative": 0
        }
        
        for rating, count in rating_distribution.items():
            rating_int = int(rating)
            if rating_int >= 4:
                sentiment_analysis["positive"] += count
            elif rating_int == 3:
                sentiment_analysis["neutral"] += count
            else:
                sentiment_analysis["negative"] += count
        
        # Resolution rate
        resolved_stmt = select(func.count(Feedback.id)).where(
            Feedback.submitted_at >= start_date,
            Feedback.resolved == True
        )
        resolved_count = self.session.exec(resolved_stmt).one()
        
        resolution_rate = (resolved_count / total_feedback * 100) if total_feedback > 0 else 0.0
        
        # Pending resolution
        pending_stmt = select(func.count(Feedback.id)).where(
            Feedback.resolved == False
        )
        pending_resolution = self.session.exec(pending_stmt).one()
        
        return FeedbackStats(
            total_feedback=total_feedback,
            average_rating=float(average_rating),
            rating_distribution=rating_distribution,
            by_service_type=by_service_type,
            sentiment_analysis=sentiment_analysis,
            resolution_rate=float(resolution_rate),
            pending_resolution=pending_resolution
        )
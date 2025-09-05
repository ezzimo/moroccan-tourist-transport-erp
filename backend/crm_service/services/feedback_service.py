"""
Feedback service for customer service evaluation
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlmodel import Session, select, func

from models.feedback import Feedback
from models.customer import Customer
from schemas.feedback import (
    FeedbackCreate,
    FeedbackUpdate,
    FeedbackResponse,
    FeedbackStats,
)
from utils.pagination import PaginationParams, paginate_query
import uuid


def _scalar_from_exec(session: Session, stmt, default=None):
    """
    Extract a scalar value from a SQLAlchemy/SQLModel execution in a way that's
    robust across SQLAlchemy versions.

    - session.exec(stmt) returns a ScalarResult for scalar selects (e.g., func.count()).
    - .one() returns either a scalar or a one-tuple depending on dialect/context.
    - We normalize to a plain Python value (or `default` if none).
    """
    res = session.exec(stmt)
    row = None
    try:
        row = res.one()
    except Exception:
        # Fall back to first() in case .one() raises for empty results
        row = res.first()

    if row is None:
        return default

    # Some drivers return a plain scalar, others a 1-tuple
    return row[0] if isinstance(row, tuple) else row


def _scalar_int(session: Session, stmt, default: int = 0) -> int:
    val = _scalar_from_exec(session, stmt, default=default)
    return int(val or 0)


def _scalar_float(session: Session, stmt, default: float = 0.0) -> float:
    val = _scalar_from_exec(session, stmt, default=default)
    # val may be Decimal/None/float/int
    return float(val or 0.0)


class FeedbackService:
    """Service for handling feedback operations"""

    def __init__(self, session: Session):
        self.session = session

    async def create_feedback(self, feedback_data: FeedbackCreate) -> FeedbackResponse:
        """Create new feedback"""
        # Verify customer exists (fetch ORM instance, not a Row)
        customer = self.session.get(Customer, feedback_data.customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
            )

        feedback = Feedback(**feedback_data.model_dump())
        self.session.add(feedback)
        self.session.commit()
        self.session.refresh(feedback)

        response_data = feedback.model_dump()
        response_data["sentiment"] = feedback.get_sentiment()
        return FeedbackResponse(**response_data)

    async def get_feedback(self, feedback_id: uuid.UUID) -> FeedbackResponse:
        """Get feedback by ID"""
        feedback = self.session.get(Feedback, feedback_id)  # ORM instance
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found"
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
        booking_id: Optional[uuid.UUID] = None,
    ) -> Tuple[List[FeedbackResponse], int]:
        """Get list of feedback with optional filters"""
        query = select(Feedback)

        # Apply filters
        if customer_id:
            query = query.where(Feedback.customer_id == customer_id)
        if service_type:
            query = query.where(Feedback.service_type == service_type)
        if rating:
            query = query.where(Feedback.rating == rating)
        if resolved is not None:
            query = query.where(Feedback.resolved == resolved)
        if booking_id:
            query = query.where(Feedback.booking_id == booking_id)

        # Newest first
        query = query.order_by(Feedback.submitted_at.desc())

        feedback_list, total = paginate_query(self.session, query, pagination)

        # Add sentiment to each feedback
        response_list: List[FeedbackResponse] = []
        for fb in feedback_list:
            data = fb.model_dump()
            data["sentiment"] = fb.get_sentiment()
            response_list.append(FeedbackResponse(**data))

        return response_list, total

    async def update_feedback(
        self, feedback_id: uuid.UUID, feedback_data: FeedbackUpdate
    ) -> FeedbackResponse:
        """Update feedback (mainly for resolution)"""
        feedback = self.session.get(Feedback, feedback_id)  # ORM instance
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found"
            )

        update_data = feedback_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(feedback, field, value)

        # Set resolved timestamp if marking as resolved
        if feedback_data.resolved and not feedback.resolved:
            feedback.resolved_at = datetime.utcnow()

        self.session.add(feedback)
        self.session.commit()
        self.session.refresh(feedback)

        data = feedback.model_dump()
        data["sentiment"] = feedback.get_sentiment()
        return FeedbackResponse(**data)

    async def delete_feedback(self, feedback_id: uuid.UUID) -> dict:
        """Delete feedback"""
        feedback = self.session.get(Feedback, feedback_id)
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found"
            )

        self.session.delete(feedback)
        self.session.commit()
        return {"message": "Feedback deleted successfully"}

    async def get_customer_feedback(
        self, customer_id: uuid.UUID, pagination: PaginationParams
    ) -> Tuple[List[FeedbackResponse], int]:
        """Get all feedback for a specific customer"""
        # Verify customer exists
        customer = self.session.get(Customer, customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
            )
        return await self.get_feedback_list(pagination, customer_id=customer_id)

    async def get_feedback_stats(self, days: int = 30) -> FeedbackStats:
        """Get feedback statistics for the specified period"""
        start_date = datetime.utcnow() - timedelta(days=days)

        # Total feedback
        total_stmt = select(func.count(Feedback.id)).where(
            Feedback.submitted_at >= start_date
        )
        total_feedback: int = _scalar_int(self.session, total_stmt, default=0)

        # Average rating
        avg_rating_stmt = select(func.avg(Feedback.rating)).where(
            Feedback.submitted_at >= start_date
        )
        average_rating: float = _scalar_float(
            self.session, avg_rating_stmt, default=0.0
        )

        # Rating distribution: { "1": n, ..., "5": n }
        rating_dist_stmt = (
            select(Feedback.rating, func.count(Feedback.id))
            .where(Feedback.submitted_at >= start_date)
            .group_by(Feedback.rating)
        )
        rating_distribution: dict[str, int] = {}
        for row in self.session.exec(rating_dist_stmt).all():
            # row can be a tuple (rating, count) or a Row
            rating, count = (row[0], row[1]) if isinstance(row, tuple) else (row.rating, row.count_1)  # type: ignore
            rating_distribution[str(int(rating))] = int(count)

        # By service type: normalize Enum/str to string keys
        service_stmt = (
            select(Feedback.service_type, func.count(Feedback.id))
            .where(Feedback.submitted_at >= start_date)
            .group_by(Feedback.service_type)
        )
        by_service_type: dict[str, int] = {}
        for row in self.session.exec(service_stmt).all():
            st, count = (row[0], row[1]) if isinstance(row, tuple) else (row.service_type, row.count_1)  # type: ignore
            key = getattr(st, "value", str(st))
            by_service_type[key] = int(count)

        # Sentiment analysis derived from rating buckets
        sentiment_analysis = {"positive": 0, "neutral": 0, "negative": 0}
        for rating_str, count in rating_distribution.items():
            r = int(rating_str)
            if r >= 4:
                sentiment_analysis["positive"] += count
            elif r == 3:
                sentiment_analysis["neutral"] += count
            else:
                sentiment_analysis["negative"] += count

        # Resolution rate
        resolved_stmt = select(func.count(Feedback.id)).where(
            Feedback.submitted_at >= start_date, Feedback.resolved.is_(True)
        )
        resolved_count: int = _scalar_int(self.session, resolved_stmt, default=0)
        resolution_rate = (
            (resolved_count / total_feedback * 100.0) if total_feedback else 0.0
        )

        # Pending resolution (all time or same window? Keeping your original: all unresolved)
        pending_stmt = select(func.count(Feedback.id)).where(
            Feedback.resolved.is_(False)
        )
        pending_resolution: int = _scalar_int(self.session, pending_stmt, default=0)

        return FeedbackStats(
            total_feedback=total_feedback,
            average_rating=float(average_rating),
            rating_distribution=rating_distribution,
            by_service_type=by_service_type,
            sentiment_analysis=sentiment_analysis,
            resolution_rate=float(resolution_rate),
            pending_resolution=pending_resolution,
        )

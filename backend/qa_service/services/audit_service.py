"""
Audit service for quality audit management
"""
from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException, status
from models.quality_audit import QualityAudit, AuditStatus
from schemas.quality_audit import (
    QualityAuditCreate, QualityAuditUpdate, QualityAuditResponse,
    AuditSummary, AuditSearch, AuditResponse
)
from utils.pagination import PaginationParams, paginate_query
from typing import List, Optional, Tuple
from datetime import datetime, date, timedelta
import redis
import uuid


class AuditService:
    """Service for handling audit operations"""
    
    def __init__(self, session: Session, redis_client: redis.Redis):
        self.session = session
        self.redis = redis_client
    
    async def create_audit(self, audit_data: QualityAuditCreate) -> QualityAuditResponse:
        """Create a new quality audit"""
        # Generate audit number
        audit_number = await self._generate_audit_number()
        
        # Create audit
        audit = QualityAudit(
            audit_number=audit_number,
            title=audit_data.title,
            entity_type=audit_data.entity_type,
            entity_id=audit_data.entity_id,
            entity_name=audit_data.entity_name,
            audit_type=audit_data.audit_type,
            auditor_id=audit_data.auditor_id,
            auditor_name=audit_data.auditor_name,
            external_auditor=audit_data.external_auditor,
            scheduled_date=audit_data.scheduled_date,
            pass_score=audit_data.pass_score
        )
        
        # Set checklist
        audit.set_checklist_dict(audit_data.checklist)
        
        self.session.add(audit)
        self.session.commit()
        self.session.refresh(audit)
        
        return self._create_audit_response(audit)
    
    async def get_audit(self, audit_id: uuid.UUID) -> QualityAuditResponse:
        """Get audit by ID"""
        statement = select(QualityAudit).where(QualityAudit.id == audit_id)
        audit = self.session.exec(statement).first()
        
        if not audit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit not found"
            )
        
        return self._create_audit_response(audit)
    
    async def get_audits(
        self, 
        pagination: PaginationParams,
        search: Optional[AuditSearch] = None
    ) -> Tuple[List[QualityAuditResponse], int]:
        """Get list of audits with optional search"""
        query = select(QualityAudit)
        
        # Apply search filters
        if search:
            conditions = []
            
            if search.query:
                search_term = f"%{search.query}%"
                conditions.append(
                    or_(
                        QualityAudit.title.ilike(search_term),
                        QualityAudit.audit_number.ilike(search_term),
                        QualityAudit.entity_name.ilike(search_term),
                        QualityAudit.auditor_name.ilike(search_term)
                    )
                )
            
            if search.entity_type:
                conditions.append(QualityAudit.entity_type == search.entity_type)
            
            if search.audit_type:
                conditions.append(QualityAudit.audit_type == search.audit_type)
            
            if search.status:
                conditions.append(QualityAudit.status == search.status)
            
            if search.auditor_id:
                conditions.append(QualityAudit.auditor_id == search.auditor_id)
            
            if search.scheduled_from:
                conditions.append(QualityAudit.scheduled_date >= search.scheduled_from)
            
            if search.scheduled_to:
                conditions.append(QualityAudit.scheduled_date <= search.scheduled_to)
            
            if search.outcome:
                conditions.append(QualityAudit.outcome == search.outcome)
            
            if search.requires_follow_up is not None:
                conditions.append(QualityAudit.requires_follow_up == search.requires_follow_up)
            
            if conditions:
                query = query.where(and_(*conditions))
        
        # Order by scheduled date (newest first)
        query = query.order_by(QualityAudit.scheduled_date.desc())
        
        audits, total = paginate_query(self.session, query, pagination)
        
        return [self._create_audit_response(audit) for audit in audits], total
    
    async def update_audit(self, audit_id: uuid.UUID, audit_data: QualityAuditUpdate) -> QualityAuditResponse:
        """Update audit information"""
        statement = select(QualityAudit).where(QualityAudit.id == audit_id)
        audit = self.session.exec(statement).first()
        
        if not audit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit not found"
            )
        
        # Update fields
        update_data = audit_data.model_dump(exclude_unset=True, exclude={"checklist_responses"})
        
        for field, value in update_data.items():
            setattr(audit, field, value)
        
        # Handle checklist responses separately
        if audit_data.checklist_responses is not None:
            audit.set_responses_dict(audit_data.checklist_responses)
            # Recalculate score if responses provided
            audit.total_score = audit.calculate_score()
        
        audit.updated_at = datetime.utcnow()
        
        self.session.add(audit)
        self.session.commit()
        self.session.refresh(audit)
        
        return self._create_audit_response(audit)
    
    async def start_audit(self, audit_id: uuid.UUID, auditor_id: uuid.UUID) -> QualityAuditResponse:
        """Start an audit"""
        statement = select(QualityAudit).where(QualityAudit.id == audit_id)
        audit = self.session.exec(statement).first()
        
        if not audit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit not found"
            )
        
        if audit.status != AuditStatus.SCHEDULED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only scheduled audits can be started"
            )
        
        # Update audit status
        audit.status = AuditStatus.IN_PROGRESS
        audit.start_date = datetime.utcnow()
        audit.updated_at = datetime.utcnow()
        
        self.session.add(audit)
        self.session.commit()
        self.session.refresh(audit)
        
        return self._create_audit_response(audit)
    
    async def complete_audit(
        self, 
        audit_id: uuid.UUID, 
        responses: AuditResponse,
        auditor_id: uuid.UUID
    ) -> QualityAuditResponse:
        """Complete an audit with responses"""
        statement = select(QualityAudit).where(QualityAudit.id == audit_id)
        audit = self.session.exec(statement).first()
        
        if not audit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit not found"
            )
        
        if audit.status != AuditStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only in-progress audits can be completed"
            )
        
        # Set responses and calculate score
        audit.set_responses_dict(responses.responses)
        audit.total_score = audit.calculate_score()
        
        # Determine outcome
        if audit.is_passed():
            audit.outcome = "Pass"
        else:
            audit.outcome = "Fail"
            audit.requires_follow_up = True
            # Schedule follow-up audit in 30 days
            audit.follow_up_date = date.today() + timedelta(days=30)
        
        # Update status and completion
        audit.status = AuditStatus.COMPLETED
        audit.completion_date = datetime.utcnow()
        audit.updated_at = datetime.utcnow()
        
        self.session.add(audit)
        self.session.commit()
        self.session.refresh(audit)
        
        return self._create_audit_response(audit)
    
    async def delete_audit(self, audit_id: uuid.UUID) -> dict:
        """Delete audit"""
        statement = select(QualityAudit).where(QualityAudit.id == audit_id)
        audit = self.session.exec(statement).first()
        
        if not audit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit not found"
            )
        
        # Check if audit can be deleted
        if audit.status in [AuditStatus.IN_PROGRESS, AuditStatus.COMPLETED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete in-progress or completed audits"
            )
        
        self.session.delete(audit)
        self.session.commit()
        
        return {"message": "Audit deleted successfully"}
    
    async def get_audit_summary(self, days: int = 90) -> AuditSummary:
        """Get audit summary statistics"""
        start_date = date.today() - timedelta(days=days)
        
        # Total audits
        total_stmt = select(func.count(QualityAudit.id)).where(
            QualityAudit.scheduled_date >= start_date
        )
        total_audits = self.session.exec(total_stmt).one()
        
        # By status
        status_stmt = select(
            QualityAudit.status, func.count(QualityAudit.id)
        ).where(
            QualityAudit.scheduled_date >= start_date
        ).group_by(QualityAudit.status)
        
        by_status = {}
        for status_val, count in self.session.exec(status_stmt):
            by_status[status_val.value] = count
        
        # By entity type
        entity_stmt = select(
            QualityAudit.entity_type, func.count(QualityAudit.id)
        ).where(
            QualityAudit.scheduled_date >= start_date
        ).group_by(QualityAudit.entity_type)
        
        by_entity_type = {}
        for entity_type, count in self.session.exec(entity_stmt):
            by_entity_type[entity_type.value] = count
        
        # By outcome
        outcome_stmt = select(
            QualityAudit.outcome, func.count(QualityAudit.id)
        ).where(
            and_(
                QualityAudit.scheduled_date >= start_date,
                QualityAudit.outcome.is_not(None)
            )
        ).group_by(QualityAudit.outcome)
        
        by_outcome = {}
        for outcome, count in self.session.exec(outcome_stmt):
            by_outcome[outcome] = count
        
        # Average score
        avg_score_stmt = select(func.avg(QualityAudit.total_score)).where(
            and_(
                QualityAudit.scheduled_date >= start_date,
                QualityAudit.total_score.is_not(None)
            )
        )
        average_score = self.session.exec(avg_score_stmt).one() or 0.0
        
        # Pass rate
        passed_count = by_outcome.get("Pass", 0)
        total_completed = sum(by_outcome.values())
        pass_rate = (passed_count / total_completed * 100) if total_completed > 0 else 0.0
        
        # Overdue audits
        overdue_stmt = select(func.count(QualityAudit.id)).where(
            and_(
                QualityAudit.status.in_([AuditStatus.SCHEDULED, AuditStatus.IN_PROGRESS]),
                QualityAudit.scheduled_date < date.today()
            )
        )
        overdue_audits = self.session.exec(overdue_stmt).one()
        
        # Upcoming audits (next 30 days)
        upcoming_date = date.today() + timedelta(days=30)
        upcoming_stmt = select(func.count(QualityAudit.id)).where(
            and_(
                QualityAudit.status == AuditStatus.SCHEDULED,
                QualityAudit.scheduled_date.between(date.today(), upcoming_date)
            )
        )
        upcoming_audits = self.session.exec(upcoming_stmt).one()
        
        return AuditSummary(
            total_audits=total_audits,
            by_status=by_status,
            by_entity_type=by_entity_type,
            by_outcome=by_outcome,
            average_score=float(average_score),
            pass_rate=pass_rate,
            overdue_audits=overdue_audits,
            upcoming_audits=upcoming_audits
        )
    
    async def get_overdue_audits(self) -> List[QualityAuditResponse]:
        """Get all overdue audits"""
        statement = select(QualityAudit).where(
            and_(
                QualityAudit.status.in_([AuditStatus.SCHEDULED, AuditStatus.IN_PROGRESS]),
                QualityAudit.scheduled_date < date.today()
            )
        ).order_by(QualityAudit.scheduled_date)
        
        audits = self.session.exec(statement).all()
        
        return [self._create_audit_response(audit) for audit in audits]
    
    async def _generate_audit_number(self) -> str:
        """Generate unique audit number"""
        year = date.today().year
        
        # Get count of audits this year
        count_stmt = select(func.count(QualityAudit.id)).where(
            QualityAudit.audit_number.like(f"AUD-{year}-%")
        )
        count = self.session.exec(count_stmt).one()
        
        return f"AUD-{year}-{count + 1:04d}"
    
    def _create_audit_response(self, audit: QualityAudit) -> QualityAuditResponse:
        """Create audit response with calculated fields"""
        return QualityAuditResponse(
            id=audit.id,
            audit_number=audit.audit_number,
            title=audit.title,
            entity_type=audit.entity_type,
            entity_id=audit.entity_id,
            entity_name=audit.entity_name,
            audit_type=audit.audit_type,
            status=audit.status,
            auditor_id=audit.auditor_id,
            auditor_name=audit.auditor_name,
            external_auditor=audit.external_auditor,
            scheduled_date=audit.scheduled_date,
            pass_score=audit.pass_score,
            checklist=audit.get_checklist_dict(),
            checklist_responses=audit.get_responses_dict(),
            total_score=audit.total_score,
            outcome=audit.outcome,
            summary=audit.summary,
            recommendations=audit.recommendations,
            start_date=audit.start_date,
            completion_date=audit.completion_date,
            requires_follow_up=audit.requires_follow_up,
            follow_up_date=audit.follow_up_date,
            follow_up_audit_id=audit.follow_up_audit_id,
            created_at=audit.created_at,
            updated_at=audit.updated_at,
            is_passed=audit.is_passed(),
            is_overdue=audit.is_overdue(),
            days_overdue=audit.get_days_overdue()
        )
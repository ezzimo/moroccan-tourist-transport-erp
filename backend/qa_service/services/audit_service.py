"""
Audit service for quality audit management operations
"""
from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException, status
from models.quality_audit import QualityAudit, AuditStatus, EntityType
from models.nonconformity import NonConformity, Severity, NCStatus
from schemas.quality_audit import (
    QualityAuditCreate, QualityAuditUpdate, QualityAuditResponse
)
from schemas.nonconformity import (
    NonConformityCreate, NonConformityUpdate, NonConformityResponse
)
from utils.notifications import send_audit_notification, send_nonconformity_alert
from utils.validation import validate_audit_data, validate_checklist
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import uuid
import json
import logging

logger = logging.getLogger(__name__)


class AuditService:
    """Service for handling quality audit operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_audit(
        self, 
        audit_data: QualityAuditCreate, 
        auditor_id: uuid.UUID
    ) -> QualityAuditResponse:
        """Create a new quality audit
        
        Args:
            audit_data: Audit creation data
            auditor_id: User ID of the auditor
            
        Returns:
            Created audit
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate audit data
        validation_errors = validate_audit_data(audit_data.model_dump())
        if validation_errors:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"message": "Validation failed", "errors": validation_errors}
            )
        
        # Validate checklist format
        if audit_data.checklist:
            checklist_errors = validate_checklist(audit_data.checklist)
            if checklist_errors:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"message": "Invalid checklist format", "errors": checklist_errors}
                )
        
        # Generate audit number
        audit_number = await self._generate_audit_number()
        
        # Create audit
        audit = QualityAudit(
            **audit_data.model_dump(),
            auditor_id=auditor_id,
            audit_number=audit_number,
            status=AuditStatus.SCHEDULED
        )
        
        self.session.add(audit)
        self.session.commit()
        self.session.refresh(audit)
        
        # Send notification
        try:
            await send_audit_notification(
                audit_id=str(audit.id),
                audit_data={
                    "audit_number": audit.audit_number,
                    "entity_type": audit.entity_type.value,
                    "scheduled_date": audit.scheduled_date.isoformat(),
                    "auditor_id": str(auditor_id)
                },
                notification_type="audit_scheduled"
            )
        except Exception as e:
            logger.error(f"Failed to send audit notification: {str(e)}")
        
        logger.info(f"Created audit {audit.audit_number}")
        return self._to_response(audit)
    
    async def get_audit(self, audit_id: uuid.UUID) -> QualityAuditResponse:
        """Get audit by ID
        
        Args:
            audit_id: Audit UUID
            
        Returns:
            Audit details
            
        Raises:
            HTTPException: If audit not found
        """
        audit = self.session.get(QualityAudit, audit_id)
        if not audit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit not found"
            )
        
        return self._to_response(audit)
    
    async def get_audits(
        self,
        skip: int = 0,
        limit: int = 100,
        entity_type: Optional[EntityType] = None,
        status: Optional[AuditStatus] = None,
        auditor_id: Optional[uuid.UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        overdue_only: bool = False
    ) -> List[QualityAuditResponse]:
        """Get audits with filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            entity_type: Filter by entity type
            status: Filter by audit status
            auditor_id: Filter by auditor
            start_date: Filter audits from this date
            end_date: Filter audits until this date
            overdue_only: Show only overdue audits
            
        Returns:
            List of audits
        """
        query = select(QualityAudit)
        
        # Apply filters
        conditions = []
        
        if entity_type:
            conditions.append(QualityAudit.entity_type == entity_type)
        
        if status:
            conditions.append(QualityAudit.status == status)
        
        if auditor_id:
            conditions.append(QualityAudit.auditor_id == auditor_id)
        
        if start_date:
            conditions.append(QualityAudit.scheduled_date >= start_date)
        
        if end_date:
            conditions.append(QualityAudit.scheduled_date <= end_date)
        
        if overdue_only:
            conditions.extend([
                QualityAudit.scheduled_date < date.today(),
                QualityAudit.status.in_([AuditStatus.SCHEDULED, AuditStatus.IN_PROGRESS])
            ])
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(QualityAudit.scheduled_date.desc()).offset(skip).limit(limit)
        audits = self.session.exec(query).all()
        
        return [self._to_response(audit) for audit in audits]
    
    async def update_audit(
        self, 
        audit_id: uuid.UUID, 
        audit_data: QualityAuditUpdate
    ) -> QualityAuditResponse:
        """Update audit information
        
        Args:
            audit_id: Audit UUID
            audit_data: Update data
            
        Returns:
            Updated audit
            
        Raises:
            HTTPException: If audit not found
        """
        audit = self.session.get(QualityAudit, audit_id)
        if not audit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit not found"
            )
        
        # Update fields
        update_data = audit_data.model_dump(exclude_unset=True)
        
        # Validate checklist if provided
        if "checklist" in update_data and update_data["checklist"]:
            checklist_errors = validate_checklist(update_data["checklist"])
            if checklist_errors:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"message": "Invalid checklist format", "errors": checklist_errors}
                )
        
        for field, value in update_data.items():
            setattr(audit, field, value)
        
        audit.updated_at = datetime.utcnow()
        
        self.session.add(audit)
        self.session.commit()
        self.session.refresh(audit)
        
        logger.info(f"Updated audit {audit.audit_number}")
        return self._to_response(audit)
    
    async def start_audit(self, audit_id: uuid.UUID) -> dict:
        """Start an audit
        
        Args:
            audit_id: Audit UUID
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If audit not found or cannot be started
        """
        audit = self.session.get(QualityAudit, audit_id)
        if not audit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit not found"
            )
        
        if audit.status != AuditStatus.SCHEDULED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot start audit with status {audit.status}"
            )
        
        audit.status = AuditStatus.IN_PROGRESS
        audit.actual_date = date.today()
        audit.updated_at = datetime.utcnow()
        
        self.session.add(audit)
        self.session.commit()
        
        logger.info(f"Started audit {audit.audit_number}")
        return {"message": "Audit started successfully"}
    
    async def complete_audit(
        self,
        audit_id: uuid.UUID,
        score: Optional[float] = None,
        outcome: Optional[str] = None,
        remarks: Optional[str] = None
    ) -> dict:
        """Complete an audit
        
        Args:
            audit_id: Audit UUID
            score: Audit score (0-100)
            outcome: Audit outcome
            remarks: Final remarks
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If audit not found or cannot be completed
        """
        audit = self.session.get(QualityAudit, audit_id)
        if not audit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit not found"
            )
        
        if audit.status != AuditStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot complete audit with status {audit.status}"
            )
        
        if score is not None and not (0 <= score <= 100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Score must be between 0 and 100"
            )
        
        audit.status = AuditStatus.COMPLETED
        audit.score = score
        audit.outcome = outcome
        audit.remarks = remarks
        audit.completed_date = date.today()
        audit.updated_at = datetime.utcnow()
        
        self.session.add(audit)
        self.session.commit()
        
        logger.info(f"Completed audit {audit.audit_number} with score {score}")
        return {"message": "Audit completed successfully"}
    
    async def cancel_audit(self, audit_id: uuid.UUID, reason: Optional[str] = None) -> dict:
        """Cancel an audit
        
        Args:
            audit_id: Audit UUID
            reason: Cancellation reason
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If audit not found or cannot be cancelled
        """
        audit = self.session.get(QualityAudit, audit_id)
        if not audit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit not found"
            )
        
        if audit.status in [AuditStatus.COMPLETED, AuditStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel audit with status {audit.status}"
            )
        
        audit.status = AuditStatus.CANCELLED
        if reason:
            audit.remarks = f"Cancelled: {reason}"
        audit.updated_at = datetime.utcnow()
        
        self.session.add(audit)
        self.session.commit()
        
        logger.info(f"Cancelled audit {audit.audit_number}")
        return {"message": "Audit cancelled successfully"}
    
    async def create_nonconformity(
        self,
        audit_id: uuid.UUID,
        nonconformity_data: NonConformityCreate,
        created_by: uuid.UUID
    ) -> NonConformityResponse:
        """Create a non-conformity for an audit
        
        Args:
            audit_id: Audit UUID
            nonconformity_data: Non-conformity data
            created_by: User who created the non-conformity
            
        Returns:
            Created non-conformity
            
        Raises:
            HTTPException: If audit not found
        """
        # Verify audit exists
        audit = self.session.get(QualityAudit, audit_id)
        if not audit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit not found"
            )
        
        # Generate NC number
        nc_number = await self._generate_nc_number()
        
        # Create non-conformity
        nonconformity = NonConformity(
            **nonconformity_data.model_dump(),
            audit_id=audit_id,
            nc_number=nc_number,
            created_by=created_by,
            status=NCStatus.OPEN
        )
        
        self.session.add(nonconformity)
        self.session.commit()
        self.session.refresh(nonconformity)
        
        # Send alert for critical non-conformities
        if nonconformity.severity == Severity.CRITICAL:
            try:
                await send_nonconformity_alert(
                    nonconformity_id=str(nonconformity.id),
                    nonconformity_data={
                        "nc_number": nonconformity.nc_number,
                        "severity": nonconformity.severity.value,
                        "description": nonconformity.description,
                        "audit_number": audit.audit_number
                    },
                    notification_type="critical_nonconformity"
                )
            except Exception as e:
                logger.error(f"Failed to send non-conformity alert: {str(e)}")
        
        logger.info(f"Created non-conformity {nonconformity.nc_number}")
        return self._nc_to_response(nonconformity)
    
    async def get_audit_nonconformities(self, audit_id: uuid.UUID) -> List[NonConformityResponse]:
        """Get non-conformities for an audit
        
        Args:
            audit_id: Audit UUID
            
        Returns:
            List of non-conformities
        """
        query = select(NonConformity).where(NonConformity.audit_id == audit_id)
        query = query.order_by(NonConformity.created_at.desc())
        
        nonconformities = self.session.exec(query).all()
        return [self._nc_to_response(nc) for nc in nonconformities]
    
    async def update_nonconformity(
        self,
        nc_id: uuid.UUID,
        nc_data: NonConformityUpdate
    ) -> NonConformityResponse:
        """Update non-conformity
        
        Args:
            nc_id: Non-conformity UUID
            nc_data: Update data
            
        Returns:
            Updated non-conformity
            
        Raises:
            HTTPException: If non-conformity not found
        """
        nonconformity = self.session.get(NonConformity, nc_id)
        if not nonconformity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Non-conformity not found"
            )
        
        # Update fields
        update_data = nc_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(nonconformity, field, value)
        
        nonconformity.updated_at = datetime.utcnow()
        
        self.session.add(nonconformity)
        self.session.commit()
        self.session.refresh(nonconformity)
        
        logger.info(f"Updated non-conformity {nonconformity.nc_number}")
        return self._nc_to_response(nonconformity)
    
    async def resolve_nonconformity(
        self,
        nc_id: uuid.UUID,
        resolution_notes: str,
        resolved_by: uuid.UUID
    ) -> dict:
        """Resolve a non-conformity
        
        Args:
            nc_id: Non-conformity UUID
            resolution_notes: Resolution description
            resolved_by: User who resolved it
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If non-conformity not found
        """
        nonconformity = self.session.get(NonConformity, nc_id)
        if not nonconformity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Non-conformity not found"
            )
        
        nonconformity.status = NCStatus.RESOLVED
        nonconformity.resolution_notes = resolution_notes
        nonconformity.resolved_by = resolved_by
        nonconformity.resolved_date = date.today()
        nonconformity.updated_at = datetime.utcnow()
        
        self.session.add(nonconformity)
        self.session.commit()
        
        logger.info(f"Resolved non-conformity {nonconformity.nc_number}")
        return {"message": "Non-conformity resolved successfully"}
    
    async def get_audit_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        entity_type: Optional[EntityType] = None
    ) -> Dict[str, Any]:
        """Get audit analytics
        
        Args:
            start_date: Analytics start date
            end_date: Analytics end date
            entity_type: Filter by entity type
            
        Returns:
            Analytics data
        """
        query = select(QualityAudit)
        
        conditions = []
        if start_date:
            conditions.append(QualityAudit.scheduled_date >= start_date)
        if end_date:
            conditions.append(QualityAudit.scheduled_date <= end_date)
        if entity_type:
            conditions.append(QualityAudit.entity_type == entity_type)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        audits = self.session.exec(query).all()
        
        # Calculate metrics
        total_audits = len(audits)
        completed_audits = len([a for a in audits if a.status == AuditStatus.COMPLETED])
        overdue_audits = len([a for a in audits if a.is_overdue()])
        
        # Score analysis
        scores = [a.score for a in audits if a.score is not None]
        average_score = sum(scores) / len(scores) if scores else None
        
        # Non-conformities
        nc_query = select(NonConformity).join(QualityAudit)
        if conditions:
            nc_query = nc_query.where(and_(*conditions))
        
        nonconformities = self.session.exec(nc_query).all()
        total_ncs = len(nonconformities)
        critical_ncs = len([nc for nc in nonconformities if nc.severity == Severity.CRITICAL])
        
        return {
            "total_audits": total_audits,
            "completed_audits": completed_audits,
            "overdue_audits": overdue_audits,
            "completion_rate": completed_audits / total_audits * 100 if total_audits > 0 else 0,
            "average_score": average_score,
            "total_nonconformities": total_ncs,
            "critical_nonconformities": critical_ncs,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    async def _generate_audit_number(self) -> str:
        """Generate unique audit number"""
        today = date.today()
        prefix = f"AUD-{today.strftime('%Y%m')}"
        
        # Get last audit number for this month
        query = select(QualityAudit).where(
            QualityAudit.audit_number.like(f"{prefix}%")
        ).order_by(QualityAudit.audit_number.desc())
        
        last_audit = self.session.exec(query).first()
        
        if last_audit:
            last_number = int(last_audit.audit_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:04d}"
    
    async def _generate_nc_number(self) -> str:
        """Generate unique non-conformity number"""
        today = date.today()
        prefix = f"NC-{today.strftime('%Y%m')}"
        
        # Get last NC number for this month
        query = select(NonConformity).where(
            NonConformity.nc_number.like(f"{prefix}%")
        ).order_by(NonConformity.nc_number.desc())
        
        last_nc = self.session.exec(query).first()
        
        if last_nc:
            last_number = int(last_nc.nc_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:04d}"
    
    def _to_response(self, audit: QualityAudit) -> QualityAuditResponse:
        """Convert audit model to response schema"""
        return QualityAuditResponse(
            id=audit.id,
            audit_number=audit.audit_number,
            entity_type=audit.entity_type,
            entity_id=audit.entity_id,
            auditor_id=audit.auditor_id,
            scheduled_date=audit.scheduled_date,
            actual_date=audit.actual_date,
            completed_date=audit.completed_date,
            status=audit.status,
            checklist=audit.checklist,
            score=audit.score,
            outcome=audit.outcome,
            remarks=audit.remarks,
            created_at=audit.created_at,
            updated_at=audit.updated_at,
            is_overdue=audit.is_overdue(),
            days_since_scheduled=audit.get_days_since_scheduled()
        )
    
    def _nc_to_response(self, nc: NonConformity) -> NonConformityResponse:
        """Convert non-conformity model to response schema"""
        return NonConformityResponse(
            id=nc.id,
            audit_id=nc.audit_id,
            nc_number=nc.nc_number,
            description=nc.description,
            severity=nc.severity,
            root_cause=nc.root_cause,
            corrective_action=nc.corrective_action,
            due_date=nc.due_date,
            status=nc.status,
            created_by=nc.created_by,
            resolved_by=nc.resolved_by,
            resolved_date=nc.resolved_date,
            resolution_notes=nc.resolution_notes,
            created_at=nc.created_at,
            updated_at=nc.updated_at,
            is_overdue=nc.is_overdue(),
            days_until_due=nc.days_until_due()
        )
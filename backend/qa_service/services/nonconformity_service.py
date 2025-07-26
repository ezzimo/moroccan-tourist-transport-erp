"""
Non-conformity service for QA non-conformity management operations
"""
from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException, status
from models.nonconformity import NonConformity, Severity, NCStatus
from models.quality_audit import QualityAudit
from schemas.nonconformity import (
    NonConformityCreate, NonConformityUpdate, NonConformityResponse
)
from utils.notifications import send_nonconformity_alert
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)


class NonConformityService:
    """Service for handling non-conformity operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_nonconformity(
        self, 
        nonconformity_data: NonConformityCreate,
        reported_by: uuid.UUID
    ) -> NonConformityResponse:
        """Create a new non-conformity
        
        Args:
            nonconformity_data: Non-conformity creation data
            reported_by: User ID who reported the non-conformity
            
        Returns:
            Created non-conformity
            
        Raises:
            HTTPException: If validation fails or audit not found
        """
        # Verify audit exists
        audit = self.session.get(QualityAudit, nonconformity_data.audit_id)
        if not audit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quality audit not found"
            )
        
        # Generate non-conformity number
        nc_number = await self._generate_nc_number()
        
        # Create non-conformity
        nonconformity = NonConformity(
            **nonconformity_data.model_dump(),
            nc_number=nc_number,
            reported_by=reported_by,
            status=NCStatus.OPEN
        )
        
        self.session.add(nonconformity)
        self.session.commit()
        self.session.refresh(nonconformity)
        
        # Send notifications for critical/major non-conformities
        if nonconformity.severity in [Severity.CRITICAL, Severity.MAJOR]:
            try:
                # Get management team (mock - would come from HR service)
                management_team = ["qa_manager", "operations_manager", "director"]
                
                await send_nonconformity_alert(
                    nonconformity_data={
                        "nc_number": nonconformity.nc_number,
                        "severity": nonconformity.severity.value,
                        "description": nonconformity.description,
                        "audit_id": str(nonconformity.audit_id),
                        "due_date": nonconformity.due_date.isoformat() if nonconformity.due_date else None
                    },
                    recipients=management_team,
                    notification_type="nonconformity_reported"
                )
            except Exception as e:
                logger.error(f"Failed to send non-conformity notification: {str(e)}")
        
        logger.info(f"Created non-conformity {nonconformity.nc_number}")
        return self._to_response(nonconformity)
    
    async def get_nonconformity(self, nonconformity_id: uuid.UUID) -> NonConformityResponse:
        """Get non-conformity by ID
        
        Args:
            nonconformity_id: Non-conformity UUID
            
        Returns:
            Non-conformity details
            
        Raises:
            HTTPException: If non-conformity not found
        """
        nonconformity = self.session.get(NonConformity, nonconformity_id)
        if not nonconformity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Non-conformity not found"
            )
        
        return self._to_response(nonconformity)
    
    async def get_nonconformities(
        self,
        skip: int = 0,
        limit: int = 100,
        audit_id: Optional[uuid.UUID] = None,
        severity: Optional[Severity] = None,
        status: Optional[NCStatus] = None,
        overdue_only: bool = False,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[NonConformityResponse]:
        """Get non-conformities with filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            audit_id: Filter by audit ID
            severity: Filter by severity
            status: Filter by status
            overdue_only: Show only overdue non-conformities
            start_date: Filter from this date
            end_date: Filter until this date
            
        Returns:
            List of non-conformities
        """
        query = select(NonConformity)
        
        # Apply filters
        conditions = []
        
        if audit_id:
            conditions.append(NonConformity.audit_id == audit_id)
        
        if severity:
            conditions.append(NonConformity.severity == severity)
        
        if status:
            conditions.append(NonConformity.status == status)
        
        if start_date:
            conditions.append(NonConformity.created_at >= start_date)
        
        if end_date:
            conditions.append(NonConformity.created_at <= end_date)
        
        if overdue_only:
            today = date.today()
            conditions.extend([
                NonConformity.due_date.is_not(None),
                NonConformity.due_date < today,
                NonConformity.status.in_([NCStatus.OPEN, NCStatus.IN_PROGRESS])
            ])
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(NonConformity.created_at.desc()).offset(skip).limit(limit)
        nonconformities = self.session.exec(query).all()
        
        return [self._to_response(nc) for nc in nonconformities]
    
    async def update_nonconformity(
        self, 
        nonconformity_id: uuid.UUID, 
        nonconformity_data: NonConformityUpdate
    ) -> NonConformityResponse:
        """Update non-conformity information
        
        Args:
            nonconformity_id: Non-conformity UUID
            nonconformity_data: Update data
            
        Returns:
            Updated non-conformity
            
        Raises:
            HTTPException: If non-conformity not found
        """
        nonconformity = self.session.get(NonConformity, nonconformity_id)
        if not nonconformity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Non-conformity not found"
            )
        
        # Update fields
        update_data = nonconformity_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(nonconformity, field, value)
        
        nonconformity.updated_at = datetime.utcnow()
        
        self.session.add(nonconformity)
        self.session.commit()
        self.session.refresh(nonconformity)
        
        logger.info(f"Updated non-conformity {nonconformity.nc_number}")
        return self._to_response(nonconformity)
    
    async def assign_corrective_action(
        self,
        nonconformity_id: uuid.UUID,
        corrective_action: str,
        assigned_to: uuid.UUID,
        due_date: Optional[date] = None
    ) -> dict:
        """Assign corrective action to non-conformity
        
        Args:
            nonconformity_id: Non-conformity UUID
            corrective_action: Description of corrective action
            assigned_to: User assigned to resolve
            due_date: Due date for resolution
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If non-conformity not found
        """
        nonconformity = self.session.get(NonConformity, nonconformity_id)
        if not nonconformity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Non-conformity not found"
            )
        
        nonconformity.corrective_action = corrective_action
        nonconformity.assigned_to = assigned_to
        nonconformity.due_date = due_date
        nonconformity.status = NCStatus.IN_PROGRESS
        nonconformity.updated_at = datetime.utcnow()
        
        self.session.add(nonconformity)
        self.session.commit()
        
        # Send notification to assigned user
        try:
            await send_nonconformity_alert(
                nonconformity_data={
                    "nc_number": nonconformity.nc_number,
                    "corrective_action": corrective_action,
                    "due_date": due_date.isoformat() if due_date else None
                },
                recipients=[str(assigned_to)],
                notification_type="corrective_action_assigned"
            )
        except Exception as e:
            logger.error(f"Failed to send assignment notification: {str(e)}")
        
        logger.info(f"Assigned corrective action for non-conformity {nonconformity.nc_number}")
        return {"message": "Corrective action assigned successfully"}
    
    async def resolve_nonconformity(
        self,
        nonconformity_id: uuid.UUID,
        resolution_notes: str,
        resolved_by: uuid.UUID
    ) -> dict:
        """Resolve a non-conformity
        
        Args:
            nonconformity_id: Non-conformity UUID
            resolution_notes: Resolution description
            resolved_by: User who resolved the issue
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If non-conformity not found or cannot be resolved
        """
        nonconformity = self.session.get(NonConformity, nonconformity_id)
        if not nonconformity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Non-conformity not found"
            )
        
        if nonconformity.status == NCStatus.CLOSED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Non-conformity is already closed"
            )
        
        nonconformity.status = NCStatus.RESOLVED
        nonconformity.resolution_notes = resolution_notes
        nonconformity.resolved_by = resolved_by
        nonconformity.resolved_at = datetime.utcnow()
        nonconformity.updated_at = datetime.utcnow()
        
        self.session.add(nonconformity)
        self.session.commit()
        
        logger.info(f"Resolved non-conformity {nonconformity.nc_number}")
        return {"message": "Non-conformity resolved successfully"}
    
    async def close_nonconformity(
        self,
        nonconformity_id: uuid.UUID,
        closure_notes: Optional[str] = None
    ) -> dict:
        """Close a resolved non-conformity
        
        Args:
            nonconformity_id: Non-conformity UUID
            closure_notes: Final closure notes
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If non-conformity not found or cannot be closed
        """
        nonconformity = self.session.get(NonConformity, nonconformity_id)
        if not nonconformity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Non-conformity not found"
            )
        
        if nonconformity.status != NCStatus.RESOLVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Non-conformity must be resolved before closing"
            )
        
        nonconformity.status = NCStatus.CLOSED
        if closure_notes:
            nonconformity.resolution_notes = f"{nonconformity.resolution_notes or ''}\n\nClosure Notes: {closure_notes}"
        nonconformity.updated_at = datetime.utcnow()
        
        self.session.add(nonconformity)
        self.session.commit()
        
        logger.info(f"Closed non-conformity {nonconformity.nc_number}")
        return {"message": "Non-conformity closed successfully"}
    
    async def get_overdue_nonconformities(self) -> List[NonConformityResponse]:
        """Get overdue non-conformities
        
        Returns:
            List of overdue non-conformities
        """
        return await self.get_nonconformities(overdue_only=True, limit=1000)
    
    async def get_nonconformity_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get non-conformity analytics
        
        Args:
            start_date: Analytics start date
            end_date: Analytics end date
            
        Returns:
            Analytics data
        """
        query = select(NonConformity)
        
        # Apply date filters
        conditions = []
        if start_date:
            conditions.append(NonConformity.created_at >= start_date)
        if end_date:
            conditions.append(NonConformity.created_at <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        nonconformities = self.session.exec(query).all()
        
        # Calculate metrics
        total_ncs = len(nonconformities)
        open_ncs = len([nc for nc in nonconformities if nc.status == NCStatus.OPEN])
        resolved_ncs = len([nc for nc in nonconformities if nc.status == NCStatus.RESOLVED])
        closed_ncs = len([nc for nc in nonconformities if nc.status == NCStatus.CLOSED])
        overdue_ncs = len([nc for nc in nonconformities if nc.is_overdue()])
        
        # By severity
        by_severity = {}
        for severity in Severity:
            by_severity[severity.value] = len([nc for nc in nonconformities if nc.severity == severity])
        
        # Resolution time analysis
        resolved_with_time = [nc for nc in nonconformities if nc.resolved_at and nc.created_at]
        if resolved_with_time:
            resolution_times = [(nc.resolved_at.date() - nc.created_at.date()).days for nc in resolved_with_time]
            avg_resolution_time = sum(resolution_times) / len(resolution_times)
        else:
            avg_resolution_time = None
        
        return {
            "total_nonconformities": total_ncs,
            "open_nonconformities": open_ncs,
            "resolved_nonconformities": resolved_ncs,
            "closed_nonconformities": closed_ncs,
            "overdue_nonconformities": overdue_ncs,
            "by_severity": by_severity,
            "resolution_rate": (resolved_ncs + closed_ncs) / total_ncs * 100 if total_ncs > 0 else 0,
            "average_resolution_time_days": avg_resolution_time,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    async def delete_nonconformity(self, nonconformity_id: uuid.UUID) -> dict:
        """Delete a non-conformity
        
        Args:
            nonconformity_id: Non-conformity UUID
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If non-conformity not found
        """
        nonconformity = self.session.get(NonConformity, nonconformity_id)
        if not nonconformity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Non-conformity not found"
            )
        
        self.session.delete(nonconformity)
        self.session.commit()
        
        logger.info(f"Deleted non-conformity {nonconformity.nc_number}")
        return {"message": "Non-conformity deleted successfully"}
    
    async def _generate_nc_number(self) -> str:
        """Generate unique non-conformity number"""
        current_date = datetime.now()
        prefix = f"NC-{current_date.strftime('%Y%m')}"
        
        # Get the latest number for this month
        query = select(func.count(NonConformity.id)).where(
            NonConformity.nc_number.like(f"{prefix}%")
        )
        count = self.session.exec(query).first() or 0
        
        return f"{prefix}-{count + 1:04d}"
    
    def _to_response(self, nonconformity: NonConformity) -> NonConformityResponse:
        """Convert non-conformity model to response schema
        
        Args:
            nonconformity: Non-conformity model
            
        Returns:
            Non-conformity response schema
        """
        return NonConformityResponse(
            id=nonconformity.id,
            audit_id=nonconformity.audit_id,
            nc_number=nonconformity.nc_number,
            description=nonconformity.description,
            severity=nonconformity.severity,
            root_cause=nonconformity.root_cause,
            corrective_action=nonconformity.corrective_action,
            due_date=nonconformity.due_date,
            status=nonconformity.status,
            reported_by=nonconformity.reported_by,
            assigned_to=nonconformity.assigned_to,
            resolved_by=nonconformity.resolved_by,
            resolution_notes=nonconformity.resolution_notes,
            resolved_at=nonconformity.resolved_at,
            created_at=nonconformity.created_at,
            updated_at=nonconformity.updated_at,
            is_overdue=nonconformity.is_overdue(),
            days_overdue=nonconformity.days_overdue(),
            age_days=nonconformity.age_days()
        )
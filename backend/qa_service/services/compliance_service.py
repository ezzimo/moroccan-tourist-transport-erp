"""
Compliance service for regulatory compliance management
"""
from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException, status
from models.compliance_requirement import ComplianceRequirement, ComplianceStatus, ComplianceDomain
from schemas.compliance_requirement import (
    ComplianceRequirementCreate, ComplianceRequirementUpdate, ComplianceRequirementResponse
)
from utils.notifications import send_compliance_alert
from utils.validation import validate_compliance_data
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)


class ComplianceService:
    """Service for handling regulatory compliance operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_requirement(
        self, 
        requirement_data: ComplianceRequirementCreate,
        created_by: uuid.UUID
    ) -> ComplianceRequirementResponse:
        """Create a new compliance requirement
        
        Args:
            requirement_data: Requirement creation data
            created_by: User who created the requirement
            
        Returns:
            Created requirement
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate requirement data
        validation_errors = validate_compliance_data(requirement_data.model_dump())
        if validation_errors:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"message": "Validation failed", "errors": validation_errors}
            )
        
        # Create requirement
        requirement = ComplianceRequirement(
            **requirement_data.model_dump(),
            created_by=created_by,
            status=ComplianceStatus.PENDING
        )
        
        self.session.add(requirement)
        self.session.commit()
        self.session.refresh(requirement)
        
        logger.info(f"Created compliance requirement {requirement.id}")
        return self._to_response(requirement)
    
    async def get_requirement(self, requirement_id: uuid.UUID) -> ComplianceRequirementResponse:
        """Get requirement by ID
        
        Args:
            requirement_id: Requirement UUID
            
        Returns:
            Requirement details
            
        Raises:
            HTTPException: If requirement not found
        """
        requirement = self.session.get(ComplianceRequirement, requirement_id)
        if not requirement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Compliance requirement not found"
            )
        
        return self._to_response(requirement)
    
    async def get_requirements(
        self,
        skip: int = 0,
        limit: int = 100,
        domain: Optional[ComplianceDomain] = None,
        status: Optional[ComplianceStatus] = None,
        expiring_soon: bool = False,
        overdue_only: bool = False
    ) -> List[ComplianceRequirementResponse]:
        """Get requirements with filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            domain: Filter by compliance domain
            status: Filter by compliance status
            expiring_soon: Show requirements expiring within 30 days
            overdue_only: Show only overdue requirements
            
        Returns:
            List of requirements
        """
        query = select(ComplianceRequirement)
        
        # Apply filters
        conditions = []
        
        if domain:
            conditions.append(ComplianceRequirement.domain == domain)
        
        if status:
            conditions.append(ComplianceRequirement.status == status)
        
        if expiring_soon:
            alert_date = date.today() + timedelta(days=30)
            conditions.extend([
                ComplianceRequirement.next_review_date.is_not(None),
                ComplianceRequirement.next_review_date <= alert_date,
                ComplianceRequirement.next_review_date > date.today()
            ])
        
        if overdue_only:
            conditions.extend([
                ComplianceRequirement.next_review_date.is_not(None),
                ComplianceRequirement.next_review_date < date.today(),
                ComplianceRequirement.status != ComplianceStatus.MET
            ])
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(ComplianceRequirement.next_review_date.asc()).offset(skip).limit(limit)
        requirements = self.session.exec(query).all()
        
        return [self._to_response(req) for req in requirements]
    
    async def update_requirement(
        self, 
        requirement_id: uuid.UUID, 
        requirement_data: ComplianceRequirementUpdate
    ) -> ComplianceRequirementResponse:
        """Update requirement information
        
        Args:
            requirement_id: Requirement UUID
            requirement_data: Update data
            
        Returns:
            Updated requirement
            
        Raises:
            HTTPException: If requirement not found
        """
        requirement = self.session.get(ComplianceRequirement, requirement_id)
        if not requirement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Compliance requirement not found"
            )
        
        # Update fields
        update_data = requirement_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(requirement, field, value)
        
        requirement.updated_at = datetime.utcnow()
        
        self.session.add(requirement)
        self.session.commit()
        self.session.refresh(requirement)
        
        logger.info(f"Updated compliance requirement {requirement_id}")
        return self._to_response(requirement)
    
    async def mark_as_met(
        self,
        requirement_id: uuid.UUID,
        compliance_notes: Optional[str] = None,
        evidence_document: Optional[str] = None
    ) -> dict:
        """Mark requirement as met
        
        Args:
            requirement_id: Requirement UUID
            compliance_notes: Notes about compliance
            evidence_document: Document path as evidence
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If requirement not found
        """
        requirement = self.session.get(ComplianceRequirement, requirement_id)
        if not requirement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Compliance requirement not found"
            )
        
        requirement.status = ComplianceStatus.MET
        requirement.compliance_notes = compliance_notes
        requirement.evidence_document = evidence_document
        requirement.last_review_date = date.today()
        
        # Calculate next review date based on frequency
        if requirement.frequency_months:
            requirement.next_review_date = date.today() + timedelta(days=requirement.frequency_months * 30)
        
        requirement.updated_at = datetime.utcnow()
        
        self.session.add(requirement)
        self.session.commit()
        
        logger.info(f"Marked requirement {requirement_id} as met")
        return {"message": "Requirement marked as met"}
    
    async def mark_as_expired(self, requirement_id: uuid.UUID) -> dict:
        """Mark requirement as expired
        
        Args:
            requirement_id: Requirement UUID
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If requirement not found
        """
        requirement = self.session.get(ComplianceRequirement, requirement_id)
        if not requirement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Compliance requirement not found"
            )
        
        requirement.status = ComplianceStatus.EXPIRED
        requirement.updated_at = datetime.utcnow()
        
        self.session.add(requirement)
        self.session.commit()
        
        # Send alert for expired requirement
        try:
            await send_compliance_alert(
                requirement_id=str(requirement_id),
                compliance_data={
                    "title": requirement.title,
                    "domain": requirement.domain.value,
                    "required_by": requirement.required_by,
                    "status": "expired"
                },
                notification_type="compliance_expired"
            )
        except Exception as e:
            logger.error(f"Failed to send compliance alert: {str(e)}")
        
        logger.info(f"Marked requirement {requirement_id} as expired")
        return {"message": "Requirement marked as expired"}
    
    async def get_expiring_requirements(self, days: int = 30) -> List[ComplianceRequirementResponse]:
        """Get requirements expiring within specified days
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of expiring requirements
        """
        return await self.get_requirements(expiring_soon=True, limit=1000)
    
    async def get_overdue_requirements(self) -> List[ComplianceRequirementResponse]:
        """Get overdue requirements
        
        Returns:
            List of overdue requirements
        """
        return await self.get_requirements(overdue_only=True, limit=1000)
    
    async def get_compliance_dashboard(self) -> Dict[str, Any]:
        """Get compliance dashboard data
        
        Returns:
            Dashboard metrics
        """
        # Total requirements
        total_requirements = self.session.exec(select(func.count(ComplianceRequirement.id))).first()
        
        # By status
        met_requirements = self.session.exec(
            select(func.count(ComplianceRequirement.id)).where(
                ComplianceRequirement.status == ComplianceStatus.MET
            )
        ).first()
        
        pending_requirements = self.session.exec(
            select(func.count(ComplianceRequirement.id)).where(
                ComplianceRequirement.status == ComplianceStatus.PENDING
            )
        ).first()
        
        expired_requirements = self.session.exec(
            select(func.count(ComplianceRequirement.id)).where(
                ComplianceRequirement.status == ComplianceStatus.EXPIRED
            )
        ).first()
        
        # Expiring soon
        alert_date = date.today() + timedelta(days=30)
        expiring_soon = self.session.exec(
            select(func.count(ComplianceRequirement.id)).where(
                and_(
                    ComplianceRequirement.next_review_date.is_not(None),
                    ComplianceRequirement.next_review_date <= alert_date,
                    ComplianceRequirement.next_review_date > date.today()
                )
            )
        ).first()
        
        # Overdue
        overdue = self.session.exec(
            select(func.count(ComplianceRequirement.id)).where(
                and_(
                    ComplianceRequirement.next_review_date.is_not(None),
                    ComplianceRequirement.next_review_date < date.today(),
                    ComplianceRequirement.status != ComplianceStatus.MET
                )
            )
        ).first()
        
        # By domain
        domain_stats = {}
        for domain in ComplianceDomain:
            count = self.session.exec(
                select(func.count(ComplianceRequirement.id)).where(
                    ComplianceRequirement.domain == domain
                )
            ).first()
            domain_stats[domain.value] = count or 0
        
        # Compliance rate
        compliance_rate = (met_requirements / total_requirements * 100) if total_requirements > 0 else 0
        
        return {
            "total_requirements": total_requirements or 0,
            "met_requirements": met_requirements or 0,
            "pending_requirements": pending_requirements or 0,
            "expired_requirements": expired_requirements or 0,
            "expiring_soon": expiring_soon or 0,
            "overdue": overdue or 0,
            "compliance_rate": compliance_rate,
            "by_domain": domain_stats
        }
    
    async def get_compliance_trends(self, months: int = 12) -> List[Dict[str, Any]]:
        """Get compliance trends over time
        
        Args:
            months: Number of months to analyze
            
        Returns:
            Monthly trend data
        """
        start_date = date.today().replace(day=1) - timedelta(days=months * 30)
        
        query = select(ComplianceRequirement).where(
            ComplianceRequirement.created_at >= start_date
        )
        
        requirements = self.session.exec(query).all()
        
        # Group by month
        monthly_data = {}
        
        for requirement in requirements:
            month_key = requirement.created_at.strftime("%Y-%m")
            
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    "month": month_key,
                    "total_requirements": 0,
                    "met_requirements": 0,
                    "expired_requirements": 0,
                    "compliance_rate": 0
                }
            
            data = monthly_data[month_key]
            data["total_requirements"] += 1
            
            if requirement.status == ComplianceStatus.MET:
                data["met_requirements"] += 1
            elif requirement.status == ComplianceStatus.EXPIRED:
                data["expired_requirements"] += 1
        
        # Calculate compliance rates
        for month_data in monthly_data.values():
            if month_data["total_requirements"] > 0:
                month_data["compliance_rate"] = (
                    month_data["met_requirements"] / month_data["total_requirements"] * 100
                )
        
        return sorted(monthly_data.values(), key=lambda x: x["month"])
    
    async def delete_requirement(self, requirement_id: uuid.UUID) -> dict:
        """Delete a compliance requirement
        
        Args:
            requirement_id: Requirement UUID
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If requirement not found
        """
        requirement = self.session.get(ComplianceRequirement, requirement_id)
        if not requirement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Compliance requirement not found"
            )
        
        self.session.delete(requirement)
        self.session.commit()
        
        logger.info(f"Deleted compliance requirement {requirement_id}")
        return {"message": "Compliance requirement deleted successfully"}
    
    def _to_response(self, requirement: ComplianceRequirement) -> ComplianceRequirementResponse:
        """Convert requirement model to response schema"""
        return ComplianceRequirementResponse(
            id=requirement.id,
            title=requirement.title,
            description=requirement.description,
            domain=requirement.domain,
            required_by=requirement.required_by,
            frequency_months=requirement.frequency_months,
            status=requirement.status,
            last_review_date=requirement.last_review_date,
            next_review_date=requirement.next_review_date,
            compliance_notes=requirement.compliance_notes,
            evidence_document=requirement.evidence_document,
            created_by=requirement.created_by,
            created_at=requirement.created_at,
            updated_at=requirement.updated_at,
            is_overdue=requirement.is_overdue(),
            days_until_due=requirement.days_until_due()
        )
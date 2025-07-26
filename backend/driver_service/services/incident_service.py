"""
Incident service for driver incident management operations
"""
from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException, status
from models.driver_incident import DriverIncident, IncidentType, IncidentSeverity, IncidentStatus
from models.driver import Driver
from schemas.driver_incident import (
    DriverIncidentCreate, DriverIncidentUpdate, DriverIncidentResponse
)
from utils.notifications import send_incident_notification
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)


class IncidentService:
    """Service for handling driver incident operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_incident(
        self, 
        incident_data: DriverIncidentCreate, 
        reported_by: uuid.UUID
    ) -> DriverIncidentResponse:
        """Create a new incident report
        
        Args:
            incident_data: Incident creation data
            reported_by: User ID who reported the incident
            
        Returns:
            Created incident
            
        Raises:
            HTTPException: If validation fails or driver not found
        """
        # Verify driver exists
        driver = self.session.get(Driver, incident_data.driver_id)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        # Create incident
        incident = DriverIncident(
            **incident_data.model_dump(),
            reported_by=reported_by,
            status=IncidentStatus.REPORTED
        )
        
        self.session.add(incident)
        self.session.commit()
        self.session.refresh(incident)
        
        # Update driver incident count
        driver.total_incidents += 1
        self.session.add(driver)
        self.session.commit()
        
        # Send notifications for critical incidents
        if incident.requires_immediate_attention():
            try:
                # Get management team (mock - would come from HR service)
                management_team = ["manager1", "manager2", "safety_officer"]
                
                await send_incident_notification(
                    incident_data={
                        "driver_name": driver.full_name,
                        "incident_type": incident.incident_type.value,
                        "severity": incident.severity.value,
                        "incident_date": incident.incident_date.isoformat(),
                        "location": incident.location,
                        "description": incident.description
                    },
                    recipients=management_team,
                    notification_type="incident_reported"
                )
            except Exception as e:
                logger.error(f"Failed to send incident notification: {str(e)}")
        
        logger.info(f"Created incident {incident.id} for driver {driver.full_name}")
        return self._to_response(incident)
    
    async def get_incident(self, incident_id: uuid.UUID) -> DriverIncidentResponse:
        """Get incident by ID
        
        Args:
            incident_id: Incident UUID
            
        Returns:
            Incident details
            
        Raises:
            HTTPException: If incident not found
        """
        incident = self.session.get(DriverIncident, incident_id)
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found"
            )
        
        return self._to_response(incident)
    
    async def get_incidents(
        self,
        skip: int = 0,
        limit: int = 100,
        driver_id: Optional[uuid.UUID] = None,
        incident_type: Optional[IncidentType] = None,
        severity: Optional[IncidentSeverity] = None,
        status: Optional[IncidentStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        overdue_only: bool = False
    ) -> List[DriverIncidentResponse]:
        """Get incidents with filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            driver_id: Filter by driver ID
            incident_type: Filter by incident type
            severity: Filter by severity
            status: Filter by status
            start_date: Filter incidents from this date
            end_date: Filter incidents until this date
            overdue_only: Show only overdue incidents
            
        Returns:
            List of incidents
        """
        query = select(DriverIncident)
        
        # Apply filters
        conditions = []
        
        if driver_id:
            conditions.append(DriverIncident.driver_id == driver_id)
        
        if incident_type:
            conditions.append(DriverIncident.incident_type == incident_type)
        
        if severity:
            conditions.append(DriverIncident.severity == severity)
        
        if status:
            conditions.append(DriverIncident.status == status)
        
        if start_date:
            conditions.append(DriverIncident.incident_date >= start_date)
        
        if end_date:
            conditions.append(DriverIncident.incident_date <= end_date)
        
        if overdue_only:
            # Filter for incidents that are overdue based on severity
            conditions.append(
                or_(
                    and_(
                        DriverIncident.severity == IncidentSeverity.CRITICAL,
                        DriverIncident.incident_date < date.today() - timedelta(days=1),
                        DriverIncident.status.not_in([IncidentStatus.RESOLVED, IncidentStatus.CLOSED])
                    ),
                    and_(
                        DriverIncident.severity == IncidentSeverity.MAJOR,
                        DriverIncident.incident_date < date.today() - timedelta(days=3),
                        DriverIncident.status.not_in([IncidentStatus.RESOLVED, IncidentStatus.CLOSED])
                    ),
                    and_(
                        DriverIncident.severity.in_([IncidentSeverity.MINOR, IncidentSeverity.MODERATE]),
                        DriverIncident.incident_date < date.today() - timedelta(days=7),
                        DriverIncident.status.not_in([IncidentStatus.RESOLVED, IncidentStatus.CLOSED])
                    )
                )
            )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(DriverIncident.incident_date.desc()).offset(skip).limit(limit)
        incidents = self.session.exec(query).all()
        
        return [self._to_response(incident) for incident in incidents]
    
    async def get_driver_incidents(
        self,
        driver_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        incident_type: Optional[IncidentType] = None,
        severity: Optional[IncidentSeverity] = None
    ) -> List[DriverIncidentResponse]:
        """Get incidents for a specific driver
        
        Args:
            driver_id: Driver UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            incident_type: Filter by incident type
            severity: Filter by severity
            
        Returns:
            List of driver incidents
        """
        return await self.get_incidents(
            skip=skip,
            limit=limit,
            driver_id=driver_id,
            incident_type=incident_type,
            severity=severity
        )
    
    async def update_incident(
        self, 
        incident_id: uuid.UUID, 
        incident_data: DriverIncidentUpdate
    ) -> DriverIncidentResponse:
        """Update incident information
        
        Args:
            incident_id: Incident UUID
            incident_data: Update data
            
        Returns:
            Updated incident
            
        Raises:
            HTTPException: If incident not found
        """
        incident = self.session.get(DriverIncident, incident_id)
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found"
            )
        
        # Update fields
        update_data = incident_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(incident, field, value)
        
        incident.updated_at = datetime.utcnow()
        
        self.session.add(incident)
        self.session.commit()
        self.session.refresh(incident)
        
        logger.info(f"Updated incident {incident_id}")
        return self._to_response(incident)
    
    async def start_investigation(
        self,
        incident_id: uuid.UUID,
        investigated_by: uuid.UUID,
        investigation_notes: Optional[str] = None
    ) -> dict:
        """Start investigation of an incident
        
        Args:
            incident_id: Incident UUID
            investigated_by: User ID who started the investigation
            investigation_notes: Initial investigation notes
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If incident not found or cannot be investigated
        """
        incident = self.session.get(DriverIncident, incident_id)
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found"
            )
        
        if incident.status != IncidentStatus.REPORTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot start investigation for incident with status {incident.status}"
            )
        
        incident.status = IncidentStatus.UNDER_INVESTIGATION
        incident.investigated_by = investigated_by
        incident.investigation_notes = investigation_notes
        incident.updated_at = datetime.utcnow()
        
        self.session.add(incident)
        self.session.commit()
        
        logger.info(f"Started investigation for incident {incident_id}")
        return {"message": "Investigation started successfully"}
    
    async def resolve_incident(
        self,
        incident_id: uuid.UUID,
        resolution_description: str,
        corrective_action: Optional[str] = None,
        preventive_measures: Optional[str] = None,
        actual_cost: Optional[float] = None,
        resolved_by: uuid.UUID = None
    ) -> dict:
        """Resolve an incident
        
        Args:
            incident_id: Incident UUID
            resolution_description: Description of the resolution
            corrective_action: Corrective actions taken
            preventive_measures: Preventive measures implemented
            actual_cost: Actual cost of the incident
            resolved_by: User who resolved the incident
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If incident not found or cannot be resolved
        """
        incident = self.session.get(DriverIncident, incident_id)
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found"
            )
        
        if incident.status in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Incident is already {incident.status.value.lower()}"
            )
        
        incident.status = IncidentStatus.RESOLVED
        incident.resolution_description = resolution_description
        incident.corrective_action = corrective_action
        incident.preventive_measures = preventive_measures
        incident.actual_cost = actual_cost
        incident.resolved_by = resolved_by
        incident.resolved_at = datetime.utcnow()
        incident.updated_at = datetime.utcnow()
        
        self.session.add(incident)
        self.session.commit()
        
        logger.info(f"Resolved incident {incident_id}")
        return {"message": "Incident resolved successfully"}
    
    async def escalate_incident(self, incident_id: uuid.UUID, escalation_reason: str) -> dict:
        """Escalate an incident
        
        Args:
            incident_id: Incident UUID
            escalation_reason: Reason for escalation
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If incident not found
        """
        incident = self.session.get(DriverIncident, incident_id)
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found"
            )
        
        incident.status = IncidentStatus.ESCALATED
        incident.investigation_notes = f"{incident.investigation_notes or ''}\n\nESCALATED: {escalation_reason}"
        incident.updated_at = datetime.utcnow()
        
        self.session.add(incident)
        self.session.commit()
        
        logger.info(f"Escalated incident {incident_id}: {escalation_reason}")
        return {"message": "Incident escalated successfully"}
    
    async def close_incident(self, incident_id: uuid.UUID, closure_notes: Optional[str] = None) -> dict:
        """Close an incident
        
        Args:
            incident_id: Incident UUID
            closure_notes: Final closure notes
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If incident not found or cannot be closed
        """
        incident = self.session.get(DriverIncident, incident_id)
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found"
            )
        
        if incident.status != IncidentStatus.RESOLVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incident must be resolved before closing"
            )
        
        incident.status = IncidentStatus.CLOSED
        if closure_notes:
            incident.investigation_notes = f"{incident.investigation_notes or ''}\n\nCLOSED: {closure_notes}"
        incident.updated_at = datetime.utcnow()
        
        self.session.add(incident)
        self.session.commit()
        
        logger.info(f"Closed incident {incident_id}")
        return {"message": "Incident closed successfully"}
    
    async def delete_incident(self, incident_id: uuid.UUID) -> dict:
        """Delete an incident
        
        Args:
            incident_id: Incident UUID
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If incident not found
        """
        incident = self.session.get(DriverIncident, incident_id)
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found"
            )
        
        # Update driver incident count
        driver = self.session.get(Driver, incident.driver_id)
        if driver and driver.total_incidents > 0:
            driver.total_incidents -= 1
            self.session.add(driver)
        
        self.session.delete(incident)
        self.session.commit()
        
        logger.info(f"Deleted incident {incident_id}")
        return {"message": "Incident deleted successfully"}
    
    async def get_overdue_incidents(
        self, 
        severity: Optional[IncidentSeverity] = None
    ) -> List[DriverIncidentResponse]:
        """Get overdue incidents that need immediate attention
        
        Args:
            severity: Filter by specific severity
            
        Returns:
            List of overdue incidents
        """
        return await self.get_incidents(
            overdue_only=True,
            severity=severity,
            limit=1000  # Get all overdue incidents
        )
    
    async def get_critical_incidents(self) -> List[DriverIncidentResponse]:
        """Get critical incidents requiring immediate attention
        
        Returns:
            List of critical incidents
        """
        return await self.get_incidents(
            severity=IncidentSeverity.CRITICAL,
            status=IncidentStatus.REPORTED,
            limit=1000
        )
    
    async def get_incident_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        driver_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Get incident analytics and summary
        
        Args:
            start_date: Analytics start date
            end_date: Analytics end date
            driver_id: Filter by specific driver
            
        Returns:
            Analytics data
        """
        query = select(DriverIncident)
        
        # Apply date filters
        conditions = []
        if start_date:
            conditions.append(DriverIncident.incident_date >= start_date)
        if end_date:
            conditions.append(DriverIncident.incident_date <= end_date)
        if driver_id:
            conditions.append(DriverIncident.driver_id == driver_id)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        incidents = self.session.exec(query).all()
        
        # Calculate metrics
        total_incidents = len(incidents)
        open_incidents = len([i for i in incidents if i.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]])
        resolved_incidents = len([i for i in incidents if i.status == IncidentStatus.RESOLVED])
        critical_incidents = len([i for i in incidents if i.severity == IncidentSeverity.CRITICAL])
        overdue_incidents = len([i for i in incidents if i.is_overdue()])
        
        # Group by type and severity
        by_type = {}
        by_severity = {}
        total_cost = 0
        resolution_times = []
        
        for incident in incidents:
            # By type
            incident_type = incident.incident_type.value
            by_type[incident_type] = by_type.get(incident_type, 0) + 1
            
            # By severity
            severity = incident.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            # Cost tracking
            if incident.actual_cost:
                total_cost += incident.actual_cost
            
            # Resolution time
            if incident.resolved_at:
                resolution_days = (incident.resolved_at.date() - incident.incident_date).days
                resolution_times.append(resolution_days)
        
        # Calculate average resolution time
        avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else None
        
        return {
            "total_incidents": total_incidents,
            "open_incidents": open_incidents,
            "resolved_incidents": resolved_incidents,
            "critical_incidents": critical_incidents,
            "overdue_incidents": overdue_incidents,
            "by_type": by_type,
            "by_severity": by_severity,
            "average_resolution_time_days": avg_resolution_time,
            "total_cost": total_cost,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    async def get_incident_trends(self, months: int = 12) -> List[Dict[str, Any]]:
        """Get incident trends over time
        
        Args:
            months: Number of months to analyze
            
        Returns:
            Monthly trend data
        """
        start_date = date.today().replace(day=1) - timedelta(days=months * 30)
        
        query = select(DriverIncident).where(
            DriverIncident.incident_date >= start_date
        )
        
        incidents = self.session.exec(query).all()
        
        # Group by month
        monthly_data = {}
        
        for incident in incidents:
            month_key = incident.incident_date.strftime("%Y-%m")
            
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    "month": month_key,
                    "total_incidents": 0,
                    "by_type": {},
                    "by_severity": {},
                    "resolution_rate": 0,
                    "average_cost": 0
                }
            
            data = monthly_data[month_key]
            data["total_incidents"] += 1
            
            # By type
            incident_type = incident.incident_type.value
            data["by_type"][incident_type] = data["by_type"].get(incident_type, 0) + 1
            
            # By severity
            severity = incident.severity.value
            data["by_severity"][severity] = data["by_severity"].get(severity, 0) + 1
        
        # Calculate resolution rates and costs
        for month_data in monthly_data.values():
            month_incidents = [i for i in incidents if i.incident_date.strftime("%Y-%m") == month_data["month"]]
            resolved_count = len([i for i in month_incidents if i.status == IncidentStatus.RESOLVED])
            
            if month_data["total_incidents"] > 0:
                month_data["resolution_rate"] = resolved_count / month_data["total_incidents"] * 100
            
            costs = [i.actual_cost for i in month_incidents if i.actual_cost]
            month_data["average_cost"] = sum(costs) / len(costs) if costs else 0
        
        return sorted(monthly_data.values(), key=lambda x: x["month"])
    
    def _to_response(self, incident: DriverIncident) -> DriverIncidentResponse:
        """Convert incident model to response schema
        
        Args:
            incident: Incident model
            
        Returns:
            Incident response schema
        """
        return DriverIncidentResponse(
            id=incident.id,
            driver_id=incident.driver_id,
            assignment_id=incident.assignment_id,
            incident_type=incident.incident_type,
            severity=incident.severity,
            title=incident.title,
            description=incident.description,
            incident_date=incident.incident_date,
            incident_time=incident.incident_time,
            location=incident.location,
            reported_by=incident.reported_by,
            reported_at=incident.reported_at,
            witness_names=incident.witness_names,
            customer_involved=incident.customer_involved,
            customer_name=incident.customer_name,
            customer_contact=incident.customer_contact,
            status=incident.status,
            investigated_by=incident.investigated_by,
            investigation_notes=incident.investigation_notes,
            resolution_description=incident.resolution_description,
            corrective_action=incident.corrective_action,
            preventive_measures=incident.preventive_measures,
            estimated_cost=incident.estimated_cost,
            actual_cost=incident.actual_cost,
            insurance_claim=incident.insurance_claim,
            claim_number=incident.claim_number,
            follow_up_required=incident.follow_up_required,
            follow_up_date=incident.follow_up_date,
            follow_up_notes=incident.follow_up_notes,
            police_report_filed=incident.police_report_filed,
            police_report_number=incident.police_report_number,
            photos_taken=incident.photos_taken,
            resolved_at=incident.resolved_at,
            resolved_by=incident.resolved_by,
            created_at=incident.created_at,
            updated_at=incident.updated_at,
            age_days=incident.get_age_days(),
            is_overdue=incident.is_overdue(),
            severity_weight=incident.get_severity_weight(),
            requires_immediate_attention=incident.requires_immediate_attention()
        )
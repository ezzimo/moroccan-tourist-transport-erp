"""
Incident service for managing tour issues and problems
"""
from sqlmodel import Session, select, and_, func, or_
from fastapi import HTTPException, status
from models.incident import Incident, IncidentType, SeverityLevel
from models.tour_instance import TourInstance
from schemas.incident import (
    IncidentCreate, IncidentUpdate, IncidentResponse, IncidentResolution,
    IncidentEscalation, IncidentStats, IncidentSearch
)
from utils.pagination import PaginationParams, paginate_query
from utils.notifications import send_incident_alert, send_tour_update
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
import redis
import uuid


class IncidentService:
    """Service for handling incident operations"""
    
    def __init__(self, session: Session, redis_client: redis.Redis):
        self.session = session
        self.redis = redis_client
    
    async def create_incident(self, incident_data: IncidentCreate) -> IncidentResponse:
        """Create a new incident"""
        # Verify tour instance exists
        tour_stmt = select(TourInstance).where(TourInstance.id == incident_data.tour_instance_id)
        tour_instance = self.session.exec(tour_stmt).first()
        
        if not tour_instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tour instance not found"
            )
        
        # Validate day number if provided
        if incident_data.day_number:
            duration_days = tour_instance.get_duration_days()
            if incident_data.day_number > duration_days:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Day number cannot exceed tour duration ({duration_days} days)"
                )
        
        # Create incident
        incident = Incident(**incident_data.model_dump())
        
        self.session.add(incident)
        self.session.commit()
        self.session.refresh(incident)
        
        # Send incident alert
        await send_incident_alert(
            self.redis,
            incident.id,
            incident.tour_instance_id,
            incident.severity.value,
            {
                "incident_type": incident.incident_type.value,
                "title": incident.title,
                "description": incident.description,
                "location": incident.location,
                "day_number": incident.day_number,
                "is_urgent": incident.is_urgent(),
                "priority_score": incident.get_priority_score()
            }
        )
        
        # Send tour update
        await send_tour_update(
            self.redis,
            incident.tour_instance_id,
            "incident_reported",
            {
                "incident_id": str(incident.id),
                "incident_type": incident.incident_type.value,
                "severity": incident.severity.value,
                "title": incident.title,
                "is_urgent": incident.is_urgent()
            }
        )
        
        # Create response with calculated fields
        response_data = incident.model_dump()
        response_data["priority_score"] = incident.get_priority_score()
        response_data["is_urgent"] = incident.is_urgent()
        
        return IncidentResponse(**response_data)
    
    async def get_incident(self, incident_id: uuid.UUID) -> IncidentResponse:
        """Get incident by ID"""
        statement = select(Incident).where(Incident.id == incident_id)
        incident = self.session.exec(statement).first()
        
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found"
            )
        
        response_data = incident.model_dump()
        response_data["priority_score"] = incident.get_priority_score()
        response_data["is_urgent"] = incident.is_urgent()
        
        return IncidentResponse(**response_data)
    
    async def get_incidents(
        self, 
        pagination: PaginationParams,
        search: Optional[IncidentSearch] = None
    ) -> Tuple[List[IncidentResponse], int]:
        """Get list of incidents with optional search"""
        query = select(Incident)
        
        # Apply search filters
        if search:
            conditions = []
            
            if search.tour_instance_id:
                conditions.append(Incident.tour_instance_id == search.tour_instance_id)
            
            if search.incident_type:
                conditions.append(Incident.incident_type == search.incident_type)
            
            if search.severity:
                conditions.append(Incident.severity == search.severity)
            
            if search.is_resolved is not None:
                conditions.append(Incident.is_resolved == search.is_resolved)
            
            if search.reporter_id:
                conditions.append(Incident.reporter_id == search.reporter_id)
            
            if search.resolved_by:
                conditions.append(Incident.resolved_by == search.resolved_by)
            
            if search.reported_from:
                conditions.append(Incident.reported_at >= search.reported_from)
            
            if search.reported_to:
                conditions.append(Incident.reported_at <= search.reported_to)
            
            if search.requires_follow_up is not None:
                conditions.append(Incident.requires_follow_up == search.requires_follow_up)
            
            if conditions:
                query = query.where(and_(*conditions))
        
        # Order by urgency and report time
        query = query.order_by(Incident.severity.desc(), Incident.reported_at.desc())
        
        incidents, total = paginate_query(self.session, query, pagination)
        
        # Add calculated fields to response
        response_list = []
        for incident in incidents:
            response_data = incident.model_dump()
            response_data["priority_score"] = incident.get_priority_score()
            response_data["is_urgent"] = incident.is_urgent()
            response_list.append(IncidentResponse(**response_data))
        
        return response_list, total
    
    async def update_incident(self, incident_id: uuid.UUID, incident_data: IncidentUpdate) -> IncidentResponse:
        """Update incident information"""
        statement = select(Incident).where(Incident.id == incident_id)
        incident = self.session.exec(statement).first()
        
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found"
            )
        
        # Update fields
        update_data = incident_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(incident, field, value)
        
        # Set resolved timestamp if marking as resolved
        if incident_data.is_resolved and not incident.is_resolved:
            incident.resolved_at = datetime.utcnow()
        
        incident.updated_at = datetime.utcnow()
        
        self.session.add(incident)
        self.session.commit()
        self.session.refresh(incident)
        
        # Send notification if status changed
        if incident_data.is_resolved is not None:
            status_text = "resolved" if incident_data.is_resolved else "reopened"
            await send_tour_update(
                self.redis,
                incident.tour_instance_id,
                f"incident_{status_text}",
                {
                    "incident_id": str(incident.id),
                    "incident_type": incident.incident_type.value,
                    "title": incident.title,
                    "resolution_description": incident.resolution_description
                }
            )
        
        response_data = incident.model_dump()
        response_data["priority_score"] = incident.get_priority_score()
        response_data["is_urgent"] = incident.is_urgent()
        
        return IncidentResponse(**response_data)
    
    async def resolve_incident(self, incident_id: uuid.UUID, resolution_data: IncidentResolution) -> IncidentResponse:
        """Resolve an incident"""
        statement = select(Incident).where(Incident.id == incident_id)
        incident = self.session.exec(statement).first()
        
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found"
            )
        
        if incident.is_resolved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incident is already resolved"
            )
        
        # Mark as resolved
        incident.is_resolved = True
        incident.resolution_description = resolution_data.resolution_description
        incident.resolved_by = resolution_data.resolved_by
        incident.resolved_at = datetime.utcnow()
        incident.requires_follow_up = resolution_data.requires_follow_up
        incident.follow_up_notes = resolution_data.follow_up_notes
        incident.updated_at = datetime.utcnow()
        
        self.session.add(incident)
        self.session.commit()
        self.session.refresh(incident)
        
        # Send notification
        await send_tour_update(
            self.redis,
            incident.tour_instance_id,
            "incident_resolved",
            {
                "incident_id": str(incident.id),
                "incident_type": incident.incident_type.value,
                "title": incident.title,
                "resolved_by": str(resolution_data.resolved_by),
                "resolution_description": resolution_data.resolution_description,
                "requires_follow_up": resolution_data.requires_follow_up
            }
        )
        
        response_data = incident.model_dump()
        response_data["priority_score"] = incident.get_priority_score()
        response_data["is_urgent"] = incident.is_urgent()
        
        return IncidentResponse(**response_data)
    
    async def escalate_incident(self, incident_id: uuid.UUID, escalation_data: IncidentEscalation) -> IncidentResponse:
        """Escalate an incident"""
        statement = select(Incident).where(Incident.id == incident_id)
        incident = self.session.exec(statement).first()
        
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found"
            )
        
        if incident.is_resolved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot escalate resolved incident"
            )
        
        # Escalate incident
        incident.escalated_to = escalation_data.escalated_to
        incident.updated_at = datetime.utcnow()
        
        # Add escalation notes
        escalation_note = f"Escalated to {escalation_data.escalated_to}: {escalation_data.escalation_reason}"
        if escalation_data.notes:
            escalation_note += f"\nNotes: {escalation_data.notes}"
        
        if incident.follow_up_notes:
            incident.follow_up_notes += f"\n\n{escalation_note}"
        else:
            incident.follow_up_notes = escalation_note
        
        self.session.add(incident)
        self.session.commit()
        self.session.refresh(incident)
        
        # Send escalation alert
        await send_incident_alert(
            self.redis,
            incident.id,
            incident.tour_instance_id,
            "ESCALATED",
            {
                "incident_type": incident.incident_type.value,
                "title": incident.title,
                "escalated_to": str(escalation_data.escalated_to),
                "escalation_reason": escalation_data.escalation_reason,
                "original_severity": incident.severity.value
            }
        )
        
        response_data = incident.model_dump()
        response_data["priority_score"] = incident.get_priority_score()
        response_data["is_urgent"] = incident.is_urgent()
        
        return IncidentResponse(**response_data)
    
    async def get_tour_incidents(self, tour_instance_id: uuid.UUID, pagination: PaginationParams) -> Tuple[List[IncidentResponse], int]:
        """Get all incidents for a specific tour"""
        # Verify tour exists
        tour_stmt = select(TourInstance).where(TourInstance.id == tour_instance_id)
        tour_instance = self.session.exec(tour_stmt).first()
        
        if not tour_instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tour instance not found"
            )
        
        search = IncidentSearch(tour_instance_id=tour_instance_id)
        return await self.get_incidents(pagination, search)
    
    async def get_urgent_incidents(self) -> List[IncidentResponse]:
        """Get all urgent unresolved incidents"""
        # Get incidents with high/critical severity or urgent types
        statement = select(Incident).where(
            and_(
                Incident.is_resolved == False,
                or_(
                    Incident.severity.in_([SeverityLevel.HIGH, SeverityLevel.CRITICAL]),
                    Incident.incident_type.in_([IncidentType.MEDICAL, IncidentType.SAFETY, IncidentType.BREAKDOWN])
                )
            )
        ).order_by(Incident.severity.desc(), Incident.reported_at.desc())
        
        incidents = self.session.exec(statement).all()
        
        response_list = []
        for incident in incidents:
            response_data = incident.model_dump()
            response_data["priority_score"] = incident.get_priority_score()
            response_data["is_urgent"] = incident.is_urgent()
            response_list.append(IncidentResponse(**response_data))
        
        return response_list
    
    async def get_incident_stats(self, days: int = 30) -> IncidentStats:
        """Get incident statistics for the specified period"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total incidents
        total_stmt = select(func.count(Incident.id)).where(
            Incident.reported_at >= start_date
        )
        total_incidents = self.session.exec(total_stmt).one()
        
        # Resolved incidents
        resolved_stmt = select(func.count(Incident.id)).where(
            Incident.reported_at >= start_date,
            Incident.is_resolved == True
        )
        resolved_incidents = self.session.exec(resolved_stmt).one()
        
        unresolved_incidents = total_incidents - resolved_incidents
        
        # By type
        type_stmt = select(
            Incident.incident_type, func.count(Incident.id)
        ).where(
            Incident.reported_at >= start_date
        ).group_by(Incident.incident_type)
        
        by_type = {}
        for incident_type, count in self.session.exec(type_stmt):
            by_type[incident_type.value] = count
        
        # By severity
        severity_stmt = select(
            Incident.severity, func.count(Incident.id)
        ).where(
            Incident.reported_at >= start_date
        ).group_by(Incident.severity)
        
        by_severity = {}
        for severity, count in self.session.exec(severity_stmt):
            by_severity[severity.value] = count
        
        # By tour
        tour_stmt = select(
            Incident.tour_instance_id, func.count(Incident.id)
        ).where(
            Incident.reported_at >= start_date
        ).group_by(Incident.tour_instance_id)
        
        by_tour = {}
        for tour_id, count in self.session.exec(tour_stmt):
            by_tour[str(tour_id)] = count
        
        # Average resolution time
        resolution_time_stmt = select(
            func.avg(
                func.extract('epoch', Incident.resolved_at - Incident.reported_at) / 3600
            )
        ).where(
            Incident.reported_at >= start_date,
            Incident.is_resolved == True,
            Incident.resolved_at.is_not(None)
        )
        avg_resolution_time = self.session.exec(resolution_time_stmt).one()
        
        # Urgent incidents
        urgent_stmt = select(func.count(Incident.id)).where(
            Incident.reported_at >= start_date,
            or_(
                Incident.severity.in_([SeverityLevel.HIGH, SeverityLevel.CRITICAL]),
                Incident.incident_type.in_([IncidentType.MEDICAL, IncidentType.SAFETY, IncidentType.BREAKDOWN])
            )
        )
        urgent_incidents = self.session.exec(urgent_stmt).one()
        
        # Follow-up required
        follow_up_stmt = select(func.count(Incident.id)).where(
            Incident.requires_follow_up == True,
            Incident.is_resolved == True
        )
        incidents_requiring_follow_up = self.session.exec(follow_up_stmt).one()
        
        return IncidentStats(
            total_incidents=total_incidents,
            resolved_incidents=resolved_incidents,
            unresolved_incidents=unresolved_incidents,
            by_type=by_type,
            by_severity=by_severity,
            by_tour=by_tour,
            average_resolution_time_hours=float(avg_resolution_time) if avg_resolution_time else None,
            urgent_incidents=urgent_incidents,
            incidents_requiring_follow_up=incidents_requiring_follow_up
        )
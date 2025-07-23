"""
Tour instance service for managing operationalized tours
"""
from sqlmodel import Session, select, and_, or_
from fastapi import HTTPException, status
from models.tour_instance import TourInstance, TourStatus
from models.tour_template import TourTemplate
from models.itinerary_item import ItineraryItem
from models.incident import Incident
from schemas.tour_instance import (
    TourInstanceCreate, TourInstanceUpdate, TourInstanceResponse, TourInstanceSummary,
    TourAssignment, TourStatusUpdate, TourProgressUpdate, TourInstanceSearch
)
from utils.pagination import PaginationParams, paginate_query
from utils.notifications import send_tour_update
from typing import List, Optional, Tuple
from datetime import datetime
import redis
import uuid
import httpx


class TourInstanceService:
    """Service for handling tour instance operations"""
    
    def __init__(self, session: Session, redis_client: redis.Redis):
        self.session = session
        self.redis = redis_client
    
    async def create_instance(self, instance_data: TourInstanceCreate) -> TourInstanceResponse:
        """Create a new tour instance"""
        # Verify template exists
        template_stmt = select(TourTemplate).where(TourTemplate.id == instance_data.template_id)
        template = self.session.exec(template_stmt).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tour template not found"
            )
        
        if not template.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create instance from inactive template"
            )
        
        # Verify booking exists (call booking service)
        await self._verify_booking_exists(instance_data.booking_id)
        
        # Verify customer exists (call CRM service)
        await self._verify_customer_exists(instance_data.customer_id)
        
        # Validate participant count against template limits
        if (instance_data.participant_count < template.min_participants or 
            instance_data.participant_count > template.max_participants):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Participant count must be between {template.min_participants} and {template.max_participants}"
            )
        
        # Create instance
        instance = TourInstance(**instance_data.model_dump(exclude={"participant_details"}))
        
        # Set participant details if provided
        if instance_data.participant_details:
            instance.set_participant_details_dict(instance_data.participant_details)
        
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        
        # Send notification
        await send_tour_update(
            self.redis, 
            instance.id, 
            "created", 
            {"title": instance.title, "start_date": str(instance.start_date)}
        )
        
        return TourInstanceResponse.from_model(instance)
    
    async def get_instance(self, instance_id: uuid.UUID) -> TourInstanceResponse:
        """Get tour instance by ID"""
        statement = select(TourInstance).where(TourInstance.id == instance_id)
        instance = self.session.exec(statement).first()
        
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tour instance not found"
            )
        
        return TourInstanceResponse.from_model(instance)
    
    async def get_instances(
        self, 
        pagination: PaginationParams,
        search: Optional[TourInstanceSearch] = None
    ) -> Tuple[List[TourInstanceResponse], int]:
        """Get list of tour instances with optional search"""
        query = select(TourInstance)
        
        # Apply search filters
        if search:
            conditions = []
            
            if search.template_id:
                conditions.append(TourInstance.template_id == search.template_id)
            
            if search.booking_id:
                conditions.append(TourInstance.booking_id == search.booking_id)
            
            if search.customer_id:
                conditions.append(TourInstance.customer_id == search.customer_id)
            
            if search.status:
                conditions.append(TourInstance.status == search.status)
            
            if search.assigned_guide_id:
                conditions.append(TourInstance.assigned_guide_id == search.assigned_guide_id)
            
            if search.assigned_vehicle_id:
                conditions.append(TourInstance.assigned_vehicle_id == search.assigned_vehicle_id)
            
            if search.start_date_from:
                conditions.append(TourInstance.start_date >= search.start_date_from)
            
            if search.start_date_to:
                conditions.append(TourInstance.start_date <= search.start_date_to)
            
            if search.region:
                # Join with template to filter by region
                query = query.join(TourTemplate).where(
                    TourTemplate.default_region.ilike(f"%{search.region}%")
                )
            
            if conditions:
                query = query.where(and_(*conditions))
        
        # Order by start date (newest first)
        query = query.order_by(TourInstance.start_date.desc())
        
        instances, total = paginate_query(self.session, query, pagination)
        
        return [TourInstanceResponse.from_model(instance) for instance in instances], total
    
    async def update_instance(self, instance_id: uuid.UUID, instance_data: TourInstanceUpdate) -> TourInstanceResponse:
        """Update tour instance information"""
        statement = select(TourInstance).where(TourInstance.id == instance_id)
        instance = self.session.exec(statement).first()
        
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tour instance not found"
            )
        
        if not instance.can_be_modified():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify tour instance in current status"
            )
        
        # Update fields
        update_data = instance_data.model_dump(exclude_unset=True, exclude={"participant_details"})
        
        for field, value in update_data.items():
            setattr(instance, field, value)
        
        # Handle participant details separately
        if instance_data.participant_details is not None:
            instance.set_participant_details_dict(instance_data.participant_details)
        
        instance.updated_at = datetime.utcnow()
        
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        
        # Send notification
        await send_tour_update(
            self.redis, 
            instance.id, 
            "updated", 
            {"fields_updated": list(update_data.keys())}
        )
        
        return TourInstanceResponse.from_model(instance)
    
    async def assign_resources(self, instance_id: uuid.UUID, assignment: TourAssignment) -> TourInstanceResponse:
        """Assign guide, vehicle, and driver to tour instance"""
        statement = select(TourInstance).where(TourInstance.id == instance_id)
        instance = self.session.exec(statement).first()
        
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tour instance not found"
            )
        
        if not instance.can_be_modified():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify tour instance in current status"
            )
        
        # Update assignments
        if assignment.guide_id is not None:
            instance.assigned_guide_id = assignment.guide_id
        
        if assignment.vehicle_id is not None:
            instance.assigned_vehicle_id = assignment.vehicle_id
        
        if assignment.driver_id is not None:
            instance.assigned_driver_id = assignment.driver_id
        
        if assignment.notes:
            if instance.internal_notes:
                instance.internal_notes += f"\n\nAssignment Notes: {assignment.notes}"
            else:
                instance.internal_notes = f"Assignment Notes: {assignment.notes}"
        
        instance.updated_at = datetime.utcnow()
        
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        
        # Send notification
        await send_tour_update(
            self.redis, 
            instance.id, 
            "resources_assigned", 
            {
                "guide_id": str(assignment.guide_id) if assignment.guide_id else None,
                "vehicle_id": str(assignment.vehicle_id) if assignment.vehicle_id else None,
                "driver_id": str(assignment.driver_id) if assignment.driver_id else None
            }
        )
        
        return TourInstanceResponse.from_model(instance)
    
    async def update_status(self, instance_id: uuid.UUID, status_update: TourStatusUpdate) -> TourInstanceResponse:
        """Update tour instance status"""
        statement = select(TourInstance).where(TourInstance.id == instance_id)
        instance = self.session.exec(statement).first()
        
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tour instance not found"
            )
        
        # Validate status transition
        if not self._is_valid_status_transition(instance.status, status_update.status):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status transition from {instance.status} to {status_update.status}"
            )
        
        # Update status
        old_status = instance.status
        instance.status = status_update.status
        instance.updated_at = datetime.utcnow()
        
        # Set timestamps based on status
        if status_update.status == TourStatus.CONFIRMED:
            instance.confirmed_at = datetime.utcnow()
        elif status_update.status == TourStatus.IN_PROGRESS:
            instance.actual_start_date = status_update.actual_start_date or datetime.utcnow()
        elif status_update.status == TourStatus.COMPLETED:
            instance.actual_end_date = status_update.actual_end_date or datetime.utcnow()
            instance.completion_percentage = 100.0
        
        # Add notes if provided
        if status_update.notes:
            if instance.internal_notes:
                instance.internal_notes += f"\n\nStatus Update ({old_status} → {status_update.status}): {status_update.notes}"
            else:
                instance.internal_notes = f"Status Update ({old_status} → {status_update.status}): {status_update.notes}"
        
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        
        # Send notification
        await send_tour_update(
            self.redis, 
            instance.id, 
            "status_changed", 
            {
                "old_status": old_status.value,
                "new_status": status_update.status.value,
                "notes": status_update.notes
            }
        )
        
        return TourInstanceResponse.from_model(instance)
    
    async def update_progress(self, instance_id: uuid.UUID, progress_update: TourProgressUpdate) -> TourInstanceResponse:
        """Update tour progress"""
        statement = select(TourInstance).where(TourInstance.id == instance_id)
        instance = self.session.exec(statement).first()
        
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tour instance not found"
            )
        
        # Validate progress data
        duration_days = instance.get_duration_days()
        if progress_update.current_day > duration_days:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Current day cannot exceed tour duration ({duration_days} days)"
            )
        
        if progress_update.completion_percentage < 0 or progress_update.completion_percentage > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Completion percentage must be between 0 and 100"
            )
        
        # Update progress
        instance.current_day = progress_update.current_day
        instance.completion_percentage = progress_update.completion_percentage
        instance.updated_at = datetime.utcnow()
        
        # Add notes if provided
        if progress_update.notes:
            if instance.internal_notes:
                instance.internal_notes += f"\n\nProgress Update (Day {progress_update.current_day}): {progress_update.notes}"
            else:
                instance.internal_notes = f"Progress Update (Day {progress_update.current_day}): {progress_update.notes}"
        
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        
        # Send notification
        await send_tour_update(
            self.redis, 
            instance.id, 
            "progress_updated", 
            {
                "current_day": progress_update.current_day,
                "completion_percentage": progress_update.completion_percentage,
                "notes": progress_update.notes
            }
        )
        
        return TourInstanceResponse.from_model(instance)
    
    async def get_instance_summary(self, instance_id: uuid.UUID) -> TourInstanceSummary:
        """Get comprehensive tour instance summary"""
        statement = select(TourInstance).where(TourInstance.id == instance_id)
        instance = self.session.exec(statement).first()
        
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tour instance not found"
            )
        
        # Get itinerary items count
        items_stmt = select(ItineraryItem).where(ItineraryItem.tour_instance_id == instance_id)
        itinerary_items = self.session.exec(items_stmt).all()
        
        # Get incidents count
        incidents_stmt = select(Incident).where(Incident.tour_instance_id == instance_id)
        incidents = self.session.exec(incidents_stmt).all()
        
        # Get template information
        template_stmt = select(TourTemplate).where(TourTemplate.id == instance.template_id)
        template = self.session.exec(template_stmt).first()
        
        # Get customer information from CRM service
        customer_info = await self._get_customer_info(instance.customer_id)
        
        # Create summary response
        base_response = TourInstanceResponse.from_model(instance)
        
        return TourInstanceSummary(
            **base_response.model_dump(),
            duration_days=instance.get_duration_days(),
            itinerary_items_count=len(itinerary_items),
            completed_items_count=len([item for item in itinerary_items if item.is_completed]),
            incidents_count=len(incidents),
            unresolved_incidents_count=len([incident for incident in incidents if not incident.is_resolved]),
            is_active=instance.is_active(),
            can_be_modified=instance.can_be_modified(),
            template_title=template.title if template else None,
            customer_name=customer_info.get("full_name") if customer_info else None
        )
    
    async def get_active_tours(self) -> List[TourInstanceResponse]:
        """Get all currently active tours"""
        statement = select(TourInstance).where(
            TourInstance.status.in_([TourStatus.CONFIRMED, TourStatus.IN_PROGRESS])
        ).order_by(TourInstance.start_date)
        
        instances = self.session.exec(statement).all()
        
        return [TourInstanceResponse.from_model(instance) for instance in instances]
    
    def _is_valid_status_transition(self, current_status: TourStatus, new_status: TourStatus) -> bool:
        """Check if status transition is valid"""
        valid_transitions = {
            TourStatus.PLANNED: [TourStatus.CONFIRMED, TourStatus.CANCELLED],
            TourStatus.CONFIRMED: [TourStatus.IN_PROGRESS, TourStatus.CANCELLED, TourStatus.POSTPONED],
            TourStatus.IN_PROGRESS: [TourStatus.COMPLETED, TourStatus.CANCELLED],
            TourStatus.COMPLETED: [],  # Final state
            TourStatus.CANCELLED: [TourStatus.PLANNED],  # Can be reactivated
            TourStatus.POSTPONED: [TourStatus.CONFIRMED, TourStatus.CANCELLED]
        }
        
        return new_status in valid_transitions.get(current_status, [])
    
    async def _verify_booking_exists(self, booking_id: uuid.UUID) -> bool:
        """Verify booking exists in booking service"""
        try:
            from config import settings
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.booking_service_url}/api/v1/bookings/{booking_id}"
                )
                return response.status_code == 200
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to verify booking information"
            )
    
    async def _verify_customer_exists(self, customer_id: uuid.UUID) -> bool:
        """Verify customer exists in CRM service"""
        try:
            from config import settings
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.crm_service_url}/api/v1/customers/{customer_id}"
                )
                return response.status_code == 200
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to verify customer information"
            )
    
    async def _get_customer_info(self, customer_id: uuid.UUID) -> Optional[dict]:
        """Get customer information from CRM service"""
        try:
            from config import settings
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.crm_service_url}/api/v1/customers/{customer_id}"
                )
                if response.status_code == 200:
                    return response.json()
        except:
            pass
        return None
"""
Itinerary service for managing tour schedule and activities
"""
from sqlmodel import Session, select, and_
from fastapi import HTTPException, status
from models.itinerary_item import ItineraryItem
from models.tour_instance import TourInstance
from schemas.itinerary_item import (
    ItineraryItemCreate, ItineraryItemUpdate, ItineraryItemResponse,
    ItineraryItemCompletion, ItineraryDayResponse
)
from utils.notifications import send_tour_update
from typing import List, Optional
from datetime import datetime, date, timedelta
import redis
import uuid


class ItineraryService:
    """Service for handling itinerary operations"""
    
    def __init__(self, session: Session, redis_client: redis.Redis):
        self.session = session
        self.redis = redis_client
    
    async def add_item(self, item_data: ItineraryItemCreate) -> ItineraryItemResponse:
        """Add an itinerary item to a tour"""
        # Verify tour instance exists and can be modified
        tour_instance = await self._get_modifiable_tour(item_data.tour_instance_id)
        
        # Validate day number
        duration_days = tour_instance.get_duration_days()
        if item_data.day_number > duration_days:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Day number cannot exceed tour duration ({duration_days} days)"
            )
        
        # Create itinerary item
        item = ItineraryItem(**item_data.model_dump(exclude={"coordinates"}))
        
        # Set coordinates if provided
        if item_data.coordinates:
            item.set_coordinates_tuple(item_data.coordinates[0], item_data.coordinates[1])
        
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        
        # Send notification
        await send_tour_update(
            self.redis,
            item_data.tour_instance_id,
            "itinerary_item_added",
            {
                "item_id": str(item.id),
                "day_number": item.day_number,
                "title": item.title,
                "activity_type": item.activity_type.value
            }
        )
        
        return ItineraryItemResponse.from_model(item)
    
    async def get_item(self, item_id: uuid.UUID) -> ItineraryItemResponse:
        """Get itinerary item by ID"""
        statement = select(ItineraryItem).where(ItineraryItem.id == item_id)
        item = self.session.exec(statement).first()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Itinerary item not found"
            )
        
        return ItineraryItemResponse.from_model(item)
    
    async def get_tour_itinerary(self, tour_instance_id: uuid.UUID) -> List[ItineraryItemResponse]:
        """Get all itinerary items for a tour"""
        # Verify tour exists
        await self._verify_tour_exists(tour_instance_id)
        
        statement = select(ItineraryItem).where(
            ItineraryItem.tour_instance_id == tour_instance_id
        ).order_by(ItineraryItem.day_number, ItineraryItem.start_time)
        
        items = self.session.exec(statement).all()
        
        return [ItineraryItemResponse.from_model(item) for item in items]
    
    async def get_day_itinerary(self, tour_instance_id: uuid.UUID, day_number: int) -> ItineraryDayResponse:
        """Get itinerary for a specific day"""
        # Verify tour exists
        tour_instance = await self._verify_tour_exists(tour_instance_id)
        
        # Validate day number
        duration_days = tour_instance.get_duration_days()
        if day_number < 1 or day_number > duration_days:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Day number must be between 1 and {duration_days}"
            )
        
        # Get items for the day
        statement = select(ItineraryItem).where(
            and_(
                ItineraryItem.tour_instance_id == tour_instance_id,
                ItineraryItem.day_number == day_number
            )
        ).order_by(ItineraryItem.start_time)
        
        items = self.session.exec(statement).all()
        
        # Calculate day date
        day_date = tour_instance.start_date + timedelta(days=day_number - 1)
        
        # Calculate statistics
        total_items = len(items)
        completed_items = len([item for item in items if item.is_completed])
        estimated_duration = sum(item.duration_minutes or 0 for item in items)
        
        return ItineraryDayResponse(
            day_number=day_number,
            date=day_date.isoformat(),
            items=[ItineraryItemResponse.from_model(item) for item in items],
            total_items=total_items,
            completed_items=completed_items,
            estimated_duration_minutes=estimated_duration
        )
    
    async def update_item(self, item_id: uuid.UUID, item_data: ItineraryItemUpdate) -> ItineraryItemResponse:
        """Update an itinerary item"""
        statement = select(ItineraryItem).where(ItineraryItem.id == item_id)
        item = self.session.exec(statement).first()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Itinerary item not found"
            )
        
        # Verify tour can be modified
        tour_instance = await self._get_modifiable_tour(item.tour_instance_id)
        
        # Update fields
        update_data = item_data.model_dump(exclude_unset=True, exclude={"coordinates"})
        
        for field, value in update_data.items():
            setattr(item, field, value)
        
        # Handle coordinates separately
        if item_data.coordinates is not None:
            if item_data.coordinates:
                item.set_coordinates_tuple(item_data.coordinates[0], item_data.coordinates[1])
            else:
                item.coordinates = None
        
        # Validate day number if updated
        if item_data.day_number is not None:
            duration_days = tour_instance.get_duration_days()
            if item_data.day_number > duration_days:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Day number cannot exceed tour duration ({duration_days} days)"
                )
        
        item.updated_at = datetime.utcnow()
        
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        
        # Send notification
        await send_tour_update(
            self.redis,
            item.tour_instance_id,
            "itinerary_item_updated",
            {
                "item_id": str(item.id),
                "day_number": item.day_number,
                "title": item.title,
                "updated_fields": list(update_data.keys())
            }
        )
        
        return ItineraryItemResponse.from_model(item)
    
    async def complete_item(self, item_id: uuid.UUID, completion_data: ItineraryItemCompletion, completed_by: uuid.UUID) -> ItineraryItemResponse:
        """Mark an itinerary item as completed"""
        statement = select(ItineraryItem).where(ItineraryItem.id == item_id)
        item = self.session.exec(statement).first()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Itinerary item not found"
            )
        
        if item.is_completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Itinerary item is already completed"
            )
        
        if item.is_cancelled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot complete cancelled itinerary item"
            )
        
        # Mark as completed
        item.is_completed = True
        item.completed_at = datetime.utcnow()
        item.completed_by = completed_by
        item.updated_at = datetime.utcnow()
        
        # Add completion notes
        if completion_data.notes:
            if item.notes:
                item.notes += f"\n\nCompletion Notes: {completion_data.notes}"
            else:
                item.notes = f"Completion Notes: {completion_data.notes}"
        
        # Update duration if provided
        if completion_data.actual_duration_minutes:
            item.duration_minutes = completion_data.actual_duration_minutes
        
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        
        # Update tour progress
        await self._update_tour_progress(item.tour_instance_id)
        
        # Send notification
        await send_tour_update(
            self.redis,
            item.tour_instance_id,
            "itinerary_item_completed",
            {
                "item_id": str(item.id),
                "day_number": item.day_number,
                "title": item.title,
                "completed_by": str(completed_by),
                "notes": completion_data.notes
            }
        )
        
        return ItineraryItemResponse.from_model(item)
    
    async def delete_item(self, item_id: uuid.UUID) -> dict:
        """Delete an itinerary item"""
        statement = select(ItineraryItem).where(ItineraryItem.id == item_id)
        item = self.session.exec(statement).first()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Itinerary item not found"
            )
        
        # Verify tour can be modified
        await self._get_modifiable_tour(item.tour_instance_id)
        
        tour_instance_id = item.tour_instance_id
        item_info = {
            "item_id": str(item.id),
            "day_number": item.day_number,
            "title": item.title
        }
        
        self.session.delete(item)
        self.session.commit()
        
        # Send notification
        await send_tour_update(
            self.redis,
            tour_instance_id,
            "itinerary_item_deleted",
            item_info
        )
        
        return {"message": "Itinerary item deleted successfully"}
    
    async def reorder_items(self, tour_instance_id: uuid.UUID, day_number: int, item_order: List[uuid.UUID]) -> List[ItineraryItemResponse]:
        """Reorder itinerary items for a specific day"""
        # Verify tour can be modified
        await self._get_modifiable_tour(tour_instance_id)
        
        # Get all items for the day
        statement = select(ItineraryItem).where(
            and_(
                ItineraryItem.tour_instance_id == tour_instance_id,
                ItineraryItem.day_number == day_number
            )
        )
        items = self.session.exec(statement).all()
        
        # Verify all items in order exist
        item_dict = {item.id: item for item in items}
        if set(item_order) != set(item_dict.keys()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item order must include all items for the day"
            )
        
        # Update order (using start_time as order indicator)
        base_time = datetime.strptime("08:00", "%H:%M").time()
        for index, item_id in enumerate(item_order):
            item = item_dict[item_id]
            # Set start times in 30-minute intervals
            hour = 8 + (index * 30) // 60
            minute = (index * 30) % 60
            item.start_time = datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").time()
            item.updated_at = datetime.utcnow()
            self.session.add(item)
        
        self.session.commit()
        
        # Get updated items
        updated_items = self.session.exec(statement.order_by(ItineraryItem.start_time)).all()
        
        # Send notification
        await send_tour_update(
            self.redis,
            tour_instance_id,
            "itinerary_reordered",
            {
                "day_number": day_number,
                "new_order": [str(item_id) for item_id in item_order]
            }
        )
        
        return [ItineraryItemResponse.from_model(item) for item in updated_items]
    
    async def _verify_tour_exists(self, tour_instance_id: uuid.UUID) -> TourInstance:
        """Verify that a tour instance exists"""
        statement = select(TourInstance).where(TourInstance.id == tour_instance_id)
        tour_instance = self.session.exec(statement).first()
        
        if not tour_instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tour instance not found"
            )
        
        return tour_instance
    
    async def _get_modifiable_tour(self, tour_instance_id: uuid.UUID) -> TourInstance:
        """Get a tour instance that can be modified"""
        tour_instance = await self._verify_tour_exists(tour_instance_id)
        
        if not tour_instance.can_be_modified():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify tour instance in current status"
            )
        
        return tour_instance
    
    async def _update_tour_progress(self, tour_instance_id: uuid.UUID):
        """Update tour progress based on completed itinerary items"""
        # Get tour instance
        tour_stmt = select(TourInstance).where(TourInstance.id == tour_instance_id)
        tour_instance = self.session.exec(tour_stmt).first()
        
        if not tour_instance:
            return
        
        # Get all itinerary items
        items_stmt = select(ItineraryItem).where(ItineraryItem.tour_instance_id == tour_instance_id)
        items = self.session.exec(items_stmt).all()
        
        if not items:
            return
        
        # Calculate completion percentage
        total_items = len(items)
        completed_items = len([item for item in items if item.is_completed])
        completion_percentage = (completed_items / total_items) * 100
        
        # Update tour instance
        tour_instance.completion_percentage = completion_percentage
        tour_instance.updated_at = datetime.utcnow()
        
        self.session.add(tour_instance)
        self.session.commit()
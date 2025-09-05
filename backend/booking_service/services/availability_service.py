"""
Availability service for resource scheduling and availability checks
"""

from sqlmodel import Session, select, and_
from fastapi import HTTPException, status
from ..models.enums import ResourceType
from ..models.availability_slot import AvailabilitySlot
from ..schemas.booking import (
    AvailabilityRequest,
    AvailabilityResponse,
    ResourceAvailability,
    AvailabilitySlotCreate,
    AvailabilitySlotUpdate,
    AvailabilitySlotResponse,
)
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import uuid


class AvailabilityService:
    """Service for handling availability checks and resource scheduling"""

    def __init__(self, session: Session):
        self.session = session

    async def check_availability(
        self, request: AvailabilityRequest
    ) -> AvailabilityResponse:
        """Check availability for resources based on request criteria"""
        start_date = request.start_date
        end_date = request.end_date or start_date
        required_capacity = request.required_capacity

        # Build query conditions
        conditions = [
            AvailabilitySlot.date >= start_date,
            AvailabilitySlot.date <= end_date,
            AvailabilitySlot.is_blocked is False,
            AvailabilitySlot.available_capacity >= required_capacity,
        ]

        if request.resource_type:
            conditions.append(
                AvailabilitySlot.resource_type == request.resource_type
            )

        if request.resource_ids:
            conditions.append(
                AvailabilitySlot.resource_id.in_(request.resource_ids)
            )

        # Execute query
        query = select(AvailabilitySlot).where(and_(*conditions))
        available_slots = self.session.exec(query).all()

        # Group by resource and date
        resource_availability = {}
        for slot in available_slots:
            key = f"{slot.resource_id}_{slot.date}"
            if key not in resource_availability:
                resource_availability[key] = ResourceAvailability(
                    resource_id=slot.resource_id,
                    resource_name=slot.resource_name,
                    resource_type=slot.resource_type,
                    date=slot.date,
                    total_capacity=slot.total_capacity,
                    available_capacity=slot.available_capacity,
                    is_available=slot.is_available(required_capacity),
                    start_time=slot.start_time,
                    end_time=slot.end_time,
                )

        available_resources = list(resource_availability.values())
        total_available = len(
            [
                r for r in available_resources if r.is_available
            ]
        )

        return AvailabilityResponse(
            request_date=start_date,
            end_date=end_date,
            required_capacity=required_capacity,
            available_resources=available_resources,
            total_available=total_available,
            has_availability=total_available > 0,
        )

    async def create_availability_slot(
        self, slot_data: AvailabilitySlotCreate
    ) -> AvailabilitySlotResponse:
        """Create a new availability slot"""
        # Check if slot already exists for this resource and date
        existing_slot = self.session.exec(
            select(AvailabilitySlot).where(
                and_(
                    AvailabilitySlot.resource_id == slot_data.resource_id,
                    AvailabilitySlot.date == slot_data.date,
                )
            )
        ).first()

        if existing_slot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Availability slot already exists for this resource and"
                    "date"
                ),
            )

        slot = AvailabilitySlot(
            resource_type=slot_data.resource_type,
            resource_id=slot_data.resource_id,
            resource_name=slot_data.resource_name,
            date=slot_data.date,
            start_time=slot_data.start_time,
            end_time=slot_data.end_time,
            total_capacity=slot_data.total_capacity,
            # Initially all capacity is available
            available_capacity=slot_data.total_capacity,
            is_blocked=slot_data.is_blocked,
            block_reason=slot_data.block_reason,
        )

        self.session.add(slot)
        self.session.commit()
        self.session.refresh(slot)

        return AvailabilitySlotResponse(**slot.model_dump())

    async def update_availability_slot(
        self, slot_id: uuid.UUID, slot_data: AvailabilitySlotUpdate
    ) -> AvailabilitySlotResponse:
        """Update an existing availability slot"""
        statement = select(AvailabilitySlot).where(
            AvailabilitySlot.id == slot_id
        )
        slot = self.session.exec(statement).first()

        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Availability slot not found",
            )

        # Update fields
        update_data = slot_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(slot, field, value)

        slot.updated_at = datetime.utcnow()

        self.session.add(slot)
        self.session.commit()
        self.session.refresh(slot)

        return AvailabilitySlotResponse(**slot.model_dump())

    async def reserve_capacity(
        self,
        resource_id: uuid.UUID,
        date: date,
        capacity: int,
        booking_id: uuid.UUID,
    ) -> bool:
        """Reserve capacity for a booking"""
        statement = select(AvailabilitySlot).where(
            and_(
                AvailabilitySlot.resource_id == resource_id,
                AvailabilitySlot.date == date,
            )
        )
        slot = self.session.exec(statement).first()

        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Availability slot not found",
            )

        if not slot.reserve_capacity(capacity, booking_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient capacity available",
            )

        self.session.add(slot)
        self.session.commit()

        return True

    async def release_capacity(
        self, resource_id: uuid.UUID, date: date, capacity: int
    ) -> bool:
        """Release reserved capacity"""
        statement = select(AvailabilitySlot).where(
            and_(
                AvailabilitySlot.resource_id == resource_id,
                AvailabilitySlot.date == date,
            )
        )
        slot = self.session.exec(statement).first()

        if not slot:
            return False

        if not slot.release_capacity(capacity):
            return False

        self.session.add(slot)
        self.session.commit()

        return True

    async def get_resource_schedule(
        self, resource_id: uuid.UUID, start_date: date, end_date: date
    ) -> List[AvailabilitySlotResponse]:
        """Get schedule for a specific resource"""
        statement = (
            select(AvailabilitySlot)
            .where(
                and_(
                    AvailabilitySlot.resource_id == resource_id,
                    AvailabilitySlot.date >= start_date,
                    AvailabilitySlot.date <= end_date,
                )
            )
            .order_by(AvailabilitySlot.date)
        )

        slots = self.session.exec(statement).all()

        return [
            AvailabilitySlotResponse(**slot.model_dump()) for slot in slots
        ]

    async def block_resource(
        self,
        resource_id: uuid.UUID,
        start_date: date,
        end_date: date,
        reason: str,
    ) -> List[AvailabilitySlotResponse]:
        """Block a resource for a date range"""
        statement = select(AvailabilitySlot).where(
            and_(
                AvailabilitySlot.resource_id == resource_id,
                AvailabilitySlot.date >= start_date,
                AvailabilitySlot.date <= end_date,
            )
        )

        slots = self.session.exec(statement).all()
        updated_slots = []

        for slot in slots:
            slot.is_blocked = True
            slot.block_reason = reason
            slot.updated_at = datetime.utcnow()

            self.session.add(slot)
            updated_slots.append(AvailabilitySlotResponse(**slot.model_dump()))

        self.session.commit()

        return updated_slots

    async def unblock_resource(
        self, resource_id: uuid.UUID, start_date: date, end_date: date
    ) -> List[AvailabilitySlotResponse]:
        """Unblock a resource for a date range"""
        statement = select(AvailabilitySlot).where(
            and_(
                AvailabilitySlot.resource_id == resource_id,
                AvailabilitySlot.date >= start_date,
                AvailabilitySlot.date <= end_date,
            )
        )

        slots = self.session.exec(statement).all()
        updated_slots = []

        for slot in slots:
            slot.is_blocked = False
            slot.block_reason = None
            slot.updated_at = datetime.utcnow()

            self.session.add(slot)
            updated_slots.append(AvailabilitySlotResponse(**slot.model_dump()))

        self.session.commit()

        return updated_slots

    async def get_availability_summary(
        self,
        start_date: date,
        end_date: date,
        resource_type: Optional[ResourceType] = None,
    ) -> Dict[str, Any]:
        """Get availability summary for a date range"""
        conditions = [
            AvailabilitySlot.date >= start_date,
            AvailabilitySlot.date <= end_date,
        ]

        if resource_type:
            conditions.append(AvailabilitySlot.resource_type == resource_type)

        statement = select(AvailabilitySlot).where(and_(*conditions))
        slots = self.session.exec(statement).all()

        summary = {
            "total_slots": len(slots),
            "available_slots": len(
                [
                    s
                    for s in slots
                    if s.available_capacity > 0 and not s.is_blocked
                ]
            ),
            "blocked_slots": len([s for s in slots if s.is_blocked]),
            "fully_booked_slots": len(
                [
                    s for s in slots if s.available_capacity == 0 and not s.is_blocked
                ]
            ),
            "total_capacity": sum(s.total_capacity for s in slots),
            "available_capacity": sum(
                s.available_capacity for s in slots if not s.is_blocked
            ),
            "reserved_capacity": sum(s.reserved_capacity for s in slots),
            "by_resource_type": {},
        }

        # Group by resource type
        for slot in slots:
            resource_type_key = slot.resource_type.value
            if resource_type_key not in summary["by_resource_type"]:
                summary["by_resource_type"][resource_type_key] = {
                    "total_slots": 0,
                    "available_slots": 0,
                    "total_capacity": 0,
                    "available_capacity": 0,
                }

            summary["by_resource_type"][resource_type_key]["total_slots"] += 1
            summary["by_resource_type"][resource_type_key][
                "total_capacity"
            ] += slot.total_capacity

            if slot.available_capacity > 0 and not slot.is_blocked:
                summary["by_resource_type"][resource_type_key]["available_slots"] += 1
                summary["by_resource_type"][resource_type_key][
                    "available_capacity"
                ] += slot.available_capacity

        return summary

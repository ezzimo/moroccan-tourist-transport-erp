"""
Reservation item management routes
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from services.reservation_service import ReservationService
from schemas.booking import (
    ReservationItemCreate, ReservationItemUpdate, ReservationItemResponse
)
from utils.auth import require_permission, CurrentUser
from typing import List, Dict, Any
import uuid


router = APIRouter(prefix="/reservation-items", tags=["Reservation Items"])


@router.post("/", response_model=ReservationItemResponse)
async def add_reservation_item(
    item_data: ReservationItemCreate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "create", "reservation_items"))
):
    """Add a reservation item to a booking"""
    reservation_service = ReservationService(session)
    return await reservation_service.add_reservation_item(item_data)


@router.get("/{item_id}", response_model=ReservationItemResponse)
async def get_reservation_item(
    item_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "read", "reservation_items"))
):
    """Get reservation item by ID"""
    reservation_service = ReservationService(session)
    return await reservation_service.get_reservation_item(item_id)


@router.get("/booking/{booking_id}", response_model=List[ReservationItemResponse])
async def get_booking_items(
    booking_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "read", "reservation_items"))
):
    """Get all reservation items for a booking"""
    reservation_service = ReservationService(session)
    return await reservation_service.get_booking_items(booking_id)


@router.put("/{item_id}", response_model=ReservationItemResponse)
async def update_reservation_item(
    item_id: uuid.UUID,
    item_data: ReservationItemUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "update", "reservation_items"))
):
    """Update a reservation item"""
    reservation_service = ReservationService(session)
    return await reservation_service.update_reservation_item(item_id, item_data)


@router.delete("/{item_id}")
async def remove_reservation_item(
    item_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "delete", "reservation_items"))
):
    """Remove a reservation item from a booking"""
    reservation_service = ReservationService(session)
    return await reservation_service.remove_reservation_item(item_id)


@router.post("/{item_id}/confirm", response_model=ReservationItemResponse)
async def confirm_reservation_item(
    item_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "update", "reservation_items"))
):
    """Confirm a reservation item"""
    reservation_service = ReservationService(session)
    return await reservation_service.confirm_reservation_item(item_id)


@router.post("/{item_id}/cancel", response_model=ReservationItemResponse)
async def cancel_reservation_item(
    item_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "update", "reservation_items"))
):
    """Cancel a reservation item"""
    reservation_service = ReservationService(session)
    return await reservation_service.cancel_reservation_item(item_id)


@router.get("/booking/{booking_id}/summary", response_model=Dict[str, Any])
async def get_booking_items_summary(
    booking_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "read", "reservation_items"))
):
    """Get summary of all reservation items for a booking"""
    reservation_service = ReservationService(session)
    return await reservation_service.get_booking_summary(booking_id)
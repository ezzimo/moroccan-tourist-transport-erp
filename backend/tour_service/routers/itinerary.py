"""
Itinerary management routes
"""

from fastapi import APIRouter, Depends, Query, Path
from sqlmodel import Session
from database import get_session, get_redis
from services.itinerary_service import ItineraryService
from schemas.itinerary_item import (
    ItineraryItemCreate,
    ItineraryItemUpdate,
    ItineraryItemResponse,
    ItineraryItemCompletion,
    ItineraryDayResponse,
)
from utils.auth import require_permission, CurrentUser
from typing import List
import redis
import uuid


router = APIRouter(prefix="/itinerary", tags=["Itinerary Management"])


@router.post("/items", response_model=ItineraryItemResponse)
async def add_itinerary_item(
    item_data: ItineraryItemCreate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("tours", "create", "itinerary")
    ),
):
    """Add an itinerary item to a tour"""
    itinerary_service = ItineraryService(session, redis_client)
    return await itinerary_service.add_item(item_data)


@router.get("/items/{item_id}", response_model=ItineraryItemResponse)
async def get_itinerary_item(
    item_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("tours", "read", "itinerary")
    ),
):
    """Get itinerary item by ID"""
    itinerary_service = ItineraryService(session, redis_client)
    return await itinerary_service.get_item(item_id)


@router.put("/items/{item_id}", response_model=ItineraryItemResponse)
async def update_itinerary_item(
    item_id: uuid.UUID,
    item_data: ItineraryItemUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("tours", "update", "itinerary")
    ),
):
    """Update an itinerary item"""
    itinerary_service = ItineraryService(session, redis_client)
    return await itinerary_service.update_item(item_id, item_data)


@router.post("/items/{item_id}/complete", response_model=ItineraryItemResponse)
async def complete_itinerary_item(
    item_id: uuid.UUID,
    completion_data: ItineraryItemCompletion,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("tours", "update", "itinerary")
    ),
):
    """Mark an itinerary item as completed"""
    itinerary_service = ItineraryService(session, redis_client)
    return await itinerary_service.complete_item(
        item_id, completion_data, current_user.user_id
    )


@router.delete("/items/{item_id}")
async def delete_itinerary_item(
    item_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("tours", "delete", "itinerary")
    ),
):
    """Delete an itinerary item"""
    itinerary_service = ItineraryService(session, redis_client)
    return await itinerary_service.delete_item(item_id)


@router.get(
    "/tour/{tour_instance_id}",
    response_model=List[ItineraryItemResponse],
)
async def get_tour_itinerary(
    tour_instance_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("tours", "read", "itinerary")
    ),
):
    """Get all itinerary items for a tour"""
    itinerary_service = ItineraryService(session, redis_client)
    return await itinerary_service.get_tour_itinerary(tour_instance_id)


@router.get(
    "/tour/{tour_instance_id}/day/{day_number}",
    response_model=ItineraryDayResponse,
)
async def get_day_itinerary(
    tour_instance_id: uuid.UUID,
    day_number: int = Path(..., ge=1, description="Day number"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("tours", "read", "itinerary")
    ),
):
    """Get itinerary for a specific day"""
    itinerary_service = ItineraryService(session, redis_client)
    return await itinerary_service.get_day_itinerary(
        tour_instance_id,
        day_number,
    )


@router.post(
    "/tour/{tour_instance_id}/day/{day_number}/reorder",
    response_model=List[ItineraryItemResponse],
)
async def reorder_day_items(
    tour_instance_id: uuid.UUID,
    day_number: int = Path(..., ge=1, description="Day number"),
    item_order: List[uuid.UUID] = Query(
        ...,
        description="Ordered list of itinerary item IDs for the day",
    ),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("tours", "update", "itinerary")
    ),
):
    """Reorder itinerary items for a specific day"""
    itinerary_service = ItineraryService(session, redis_client)
    return await itinerary_service.reorder_items(
        tour_instance_id, day_number, item_order
    )

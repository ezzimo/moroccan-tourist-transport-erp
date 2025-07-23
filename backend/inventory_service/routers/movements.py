"""
Stock movement management routes
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session, get_redis
from services.movement_service import MovementService
from schemas.stock_movement import (
    StockMovementCreate, StockMovementUpdate, StockMovementResponse,
    StockMovementSummary, StockMovementSearch, BulkStockMovement
)
from models.stock_movement import MovementType, MovementReason
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import redis
import uuid
from datetime import datetime


router = APIRouter(prefix="/movements", tags=["Stock Movement Management"])


@router.post("/", response_model=StockMovementResponse)
async def create_stock_movement(
    movement_data: StockMovementCreate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "create", "movements"))
):
    """Create a new stock movement"""
    # Set performed_by to current user if not provided
    if not movement_data.performed_by:
        movement_data.performed_by = current_user.user_id
    
    movement_service = MovementService(session, redis_client)
    return await movement_service.create_movement(movement_data)


@router.post("/bulk", response_model=List[StockMovementResponse])
async def create_bulk_stock_movements(
    bulk_data: BulkStockMovement,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "create", "movements"))
):
    """Create multiple stock movements in bulk"""
    movement_service = MovementService(session, redis_client)
    return await movement_service.create_bulk_movements(bulk_data, current_user.user_id)


@router.get("/", response_model=PaginatedResponse[StockMovementResponse])
async def get_stock_movements(
    pagination: PaginationParams = Depends(),
    item_id: Optional[uuid.UUID] = Query(None, description="Filter by item"),
    movement_type: Optional[MovementType] = Query(None, description="Filter by movement type"),
    reason: Optional[MovementReason] = Query(None, description="Filter by reason"),
    reference_type: Optional[str] = Query(None, description="Filter by reference type"),
    reference_id: Optional[str] = Query(None, description="Filter by reference ID"),
    performed_by: Optional[uuid.UUID] = Query(None, description="Filter by user"),
    date_from: Optional[str] = Query(None, description="Filter by date from (ISO datetime)"),
    date_to: Optional[str] = Query(None, description="Filter by date to (ISO datetime)"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "movements"))
):
    """Get list of stock movements with optional filters"""
    movement_service = MovementService(session, redis_client)
    
    # Build search criteria
    search = None
    if any([item_id, movement_type, reason, reference_type, reference_id, 
            performed_by, date_from, date_to]):
        from fastapi import HTTPException, status
        
        date_from_parsed = None
        date_to_parsed = None
        
        if date_from:
            try:
                date_from_parsed = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_from format. Use ISO datetime format"
                )
        
        if date_to:
            try:
                date_to_parsed = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_to format. Use ISO datetime format"
                )
        
        search = StockMovementSearch(
            item_id=item_id,
            movement_type=movement_type,
            reason=reason,
            reference_type=reference_type,
            reference_id=reference_id,
            performed_by=performed_by,
            date_from=date_from_parsed,
            date_to=date_to_parsed
        )
    
    movements, total = await movement_service.get_movements(pagination, search)
    
    return PaginatedResponse.create(
        items=movements,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/summary", response_model=StockMovementSummary)
async def get_movements_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days for summary"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "movements"))
):
    """Get stock movement summary statistics"""
    movement_service = MovementService(session, redis_client)
    return await movement_service.get_movements_summary(days)


@router.get("/{movement_id}", response_model=StockMovementResponse)
async def get_stock_movement(
    movement_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "movements"))
):
    """Get stock movement by ID"""
    movement_service = MovementService(session, redis_client)
    return await movement_service.get_movement(movement_id)


@router.put("/{movement_id}", response_model=StockMovementResponse)
async def update_stock_movement(
    movement_id: uuid.UUID,
    movement_data: StockMovementUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "update", "movements"))
):
    """Update stock movement information"""
    movement_service = MovementService(session, redis_client)
    return await movement_service.update_movement(movement_id, movement_data, current_user.user_id)


@router.get("/item/{item_id}", response_model=List[StockMovementResponse])
async def get_item_movement_history(
    item_id: uuid.UUID,
    limit: int = Query(100, ge=1, le=500, description="Number of movements to return"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "movements"))
):
    """Get movement history for a specific item"""
    movement_service = MovementService(session, redis_client)
    return await movement_service.get_item_movement_history(item_id, limit)


@router.get("/reference/{reference_type}/{reference_id}", response_model=List[StockMovementResponse])
async def get_movements_by_reference(
    reference_type: str,
    reference_id: str,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "movements"))
):
    """Get all movements for a specific reference (e.g., maintenance job, purchase order)"""
    movement_service = MovementService(session, redis_client)
    return await movement_service.get_movements_by_reference(reference_type, reference_id)
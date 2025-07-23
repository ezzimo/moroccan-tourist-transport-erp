"""
Item management routes
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session
from database import get_session, get_redis
from services.item_service import ItemService
from schemas.item import (
    ItemCreate, ItemUpdate, ItemResponse, ItemSummary,
    ItemSearch, ItemStockAdjustment, ItemReorderSuggestion
)
from models.item import ItemCategory, ItemStatus
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import redis
import uuid


router = APIRouter(prefix="/items", tags=["Item Management"])


@router.post("/", response_model=ItemResponse)
async def create_item(
    item_data: ItemCreate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "create", "items"))
):
    """Create a new inventory item"""
    item_service = ItemService(session, redis_client)
    return await item_service.create_item(item_data)


@router.get("/", response_model=PaginatedResponse[ItemResponse])
async def get_items(
    pagination: PaginationParams = Depends(),
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[ItemCategory] = Query(None, description="Filter by category"),
    status: Optional[ItemStatus] = Query(None, description="Filter by status"),
    warehouse_location: Optional[str] = Query(None, description="Filter by warehouse"),
    supplier_id: Optional[uuid.UUID] = Query(None, description="Filter by supplier"),
    is_low_stock: Optional[bool] = Query(None, description="Filter low stock items"),
    is_critical: Optional[bool] = Query(None, description="Filter critical items"),
    has_expiry: Optional[bool] = Query(None, description="Filter items with expiry"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "items"))
):
    """Get list of items with optional search and filters"""
    item_service = ItemService(session, redis_client)
    
    # Build search criteria
    search = None
    if any([query, category, status, warehouse_location, supplier_id, 
            is_low_stock is not None, is_critical is not None, has_expiry is not None]):
        search = ItemSearch(
            query=query,
            category=category,
            status=status,
            warehouse_location=warehouse_location,
            supplier_id=supplier_id,
            is_low_stock=is_low_stock,
            is_critical=is_critical,
            has_expiry=has_expiry
        )
    
    items, total = await item_service.get_items(pagination, search)
    
    return PaginatedResponse.create(
        items=items,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/summary", response_model=ItemSummary)
async def get_items_summary(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "items"))
):
    """Get inventory summary statistics"""
    item_service = ItemService(session, redis_client)
    return await item_service.get_items_summary()


@router.get("/low-stock", response_model=List[ItemResponse])
async def get_low_stock_items(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "items"))
):
    """Get all items with low stock levels"""
    item_service = ItemService(session, redis_client)
    return await item_service.get_low_stock_items()


@router.get("/reorder-suggestions", response_model=List[ItemReorderSuggestion])
async def get_reorder_suggestions(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "items"))
):
    """Get reorder suggestions for low stock items"""
    item_service = ItemService(session, redis_client)
    return await item_service.get_reorder_suggestions()


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "items"))
):
    """Get item by ID"""
    item_service = ItemService(session, redis_client)
    return await item_service.get_item(item_id)


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: uuid.UUID,
    item_data: ItemUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "update", "items"))
):
    """Update item information"""
    item_service = ItemService(session, redis_client)
    return await item_service.update_item(item_id, item_data)


@router.post("/{item_id}/adjust-stock", response_model=ItemResponse)
async def adjust_item_stock(
    item_id: uuid.UUID,
    adjustment: ItemStockAdjustment,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "update", "items"))
):
    """Adjust item stock quantity"""
    item_service = ItemService(session, redis_client)
    return await item_service.adjust_stock(item_id, adjustment, current_user.user_id)


@router.delete("/{item_id}")
async def delete_item(
    item_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "delete", "items"))
):
    """Delete item (soft delete by marking inactive)"""
    item_service = ItemService(session, redis_client)
    return await item_service.delete_item(item_id)


@router.get("/{item_id}/movements", response_model=List[dict])
async def get_item_movements(
    item_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200, description="Number of movements to return"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "items"))
):
    """Get stock movement history for an item"""
    item_service = ItemService(session, redis_client)
    return await item_service.get_item_movements(item_id, limit)


@router.get("/category/{category}", response_model=List[ItemResponse])
async def get_items_by_category(
    category: ItemCategory,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "items"))
):
    """Get all items in a specific category"""
    item_service = ItemService(session, redis_client)
    return await item_service.get_items_by_category(category)


@router.get("/warehouse/{warehouse}", response_model=List[ItemResponse])
async def get_items_by_warehouse(
    warehouse: str,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "items"))
):
    """Get all items in a specific warehouse"""
    item_service = ItemService(session, redis_client)
    return await item_service.get_items_by_warehouse(warehouse)
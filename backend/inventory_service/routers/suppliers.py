"""
Supplier management routes
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session, get_redis
from services.supplier_service import SupplierService
from schemas.supplier import (
    SupplierCreate, SupplierUpdate, SupplierResponse, SupplierSummary,
    SupplierSearch, SupplierEvaluation, SupplierPerformance
)
from models.supplier import SupplierStatus, SupplierType
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import redis
import uuid


router = APIRouter(prefix="/suppliers", tags=["Supplier Management"])


@router.post("/", response_model=SupplierResponse)
async def create_supplier(
    supplier_data: SupplierCreate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "create", "suppliers"))
):
    """Create a new supplier"""
    supplier_service = SupplierService(session, redis_client)
    return await supplier_service.create_supplier(supplier_data)


@router.get("/", response_model=PaginatedResponse[SupplierResponse])
async def get_suppliers(
    pagination: PaginationParams = Depends(),
    query: Optional[str] = Query(None, description="Search query"),
    type: Optional[SupplierType] = Query(None, description="Filter by supplier type"),
    status: Optional[SupplierStatus] = Query(None, description="Filter by status"),
    city: Optional[str] = Query(None, description="Filter by city"),
    country: Optional[str] = Query(None, description="Filter by country"),
    is_preferred: Optional[bool] = Query(None, description="Filter preferred suppliers"),
    min_performance_rating: Optional[float] = Query(None, description="Minimum performance rating"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "suppliers"))
):
    """Get list of suppliers with optional search and filters"""
    supplier_service = SupplierService(session, redis_client)
    
    # Build search criteria
    search = None
    if any([query, type, status, city, country, is_preferred is not None, min_performance_rating]):
        search = SupplierSearch(
            query=query,
            type=type,
            status=status,
            city=city,
            country=country,
            is_preferred=is_preferred,
            min_performance_rating=min_performance_rating
        )
    
    suppliers, total = await supplier_service.get_suppliers(pagination, search)
    
    return PaginatedResponse.create(
        items=suppliers,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/summary", response_model=SupplierSummary)
async def get_suppliers_summary(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "suppliers"))
):
    """Get supplier summary statistics"""
    supplier_service = SupplierService(session, redis_client)
    return await supplier_service.get_suppliers_summary()


@router.get("/performance", response_model=List[SupplierPerformance])
async def get_supplier_performance_report(
    days: int = Query(365, ge=1, le=1095, description="Period for performance calculation"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "suppliers"))
):
    """Get supplier performance report"""
    supplier_service = SupplierService(session, redis_client)
    return await supplier_service.get_performance_report(days)


@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "suppliers"))
):
    """Get supplier by ID"""
    supplier_service = SupplierService(session, redis_client)
    return await supplier_service.get_supplier(supplier_id)


@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: uuid.UUID,
    supplier_data: SupplierUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "update", "suppliers"))
):
    """Update supplier information"""
    supplier_service = SupplierService(session, redis_client)
    return await supplier_service.update_supplier(supplier_id, supplier_data)


@router.delete("/{supplier_id}")
async def delete_supplier(
    supplier_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "delete", "suppliers"))
):
    """Delete supplier (soft delete by marking inactive)"""
    supplier_service = SupplierService(session, redis_client)
    return await supplier_service.delete_supplier(supplier_id)


@router.post("/{supplier_id}/evaluate", response_model=SupplierResponse)
async def evaluate_supplier(
    supplier_id: uuid.UUID,
    evaluation: SupplierEvaluation,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "update", "suppliers"))
):
    """Evaluate supplier performance"""
    supplier_service = SupplierService(session, redis_client)
    return await supplier_service.evaluate_supplier(supplier_id, evaluation)


@router.get("/{supplier_id}/items", response_model=List[dict])
async def get_supplier_items(
    supplier_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "suppliers"))
):
    """Get all items supplied by a specific supplier"""
    supplier_service = SupplierService(session, redis_client)
    return await supplier_service.get_supplier_items(supplier_id)


@router.get("/{supplier_id}/orders", response_model=List[dict])
async def get_supplier_orders(
    supplier_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200, description="Number of orders to return"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "suppliers"))
):
    """Get purchase order history for a supplier"""
    supplier_service = SupplierService(session, redis_client)
    return await supplier_service.get_supplier_orders(supplier_id, limit)
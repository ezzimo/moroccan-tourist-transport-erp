"""
Purchase order management routes
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session, get_redis
from services.purchase_order_service import PurchaseOrderService
from schemas.purchase_order import (
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderResponse,
    PurchaseOrderSummary, PurchaseOrderSearch, PurchaseOrderApproval,
    PurchaseOrderReceiving, PurchaseOrderGeneration
)
from models.purchase_order import PurchaseOrderStatus, PurchaseOrderPriority
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import redis
import uuid
from datetime import date


router = APIRouter(prefix="/purchase-orders", tags=["Purchase Order Management"])


@router.post("/", response_model=PurchaseOrderResponse)
async def create_purchase_order(
    po_data: PurchaseOrderCreate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "create", "purchase_orders"))
):
    """Create a new purchase order"""
    po_service = PurchaseOrderService(session, redis_client)
    return await po_service.create_purchase_order(po_data, current_user.user_id)


@router.post("/generate", response_model=PurchaseOrderResponse)
async def generate_purchase_order(
    generation_data: PurchaseOrderGeneration,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "create", "purchase_orders"))
):
    """Generate purchase order from reorder suggestions"""
    po_service = PurchaseOrderService(session, redis_client)
    return await po_service.generate_from_reorder(generation_data, current_user.user_id)


@router.get("/", response_model=PaginatedResponse[PurchaseOrderResponse])
async def get_purchase_orders(
    pagination: PaginationParams = Depends(),
    query: Optional[str] = Query(None, description="Search query"),
    supplier_id: Optional[uuid.UUID] = Query(None, description="Filter by supplier"),
    status: Optional[PurchaseOrderStatus] = Query(None, description="Filter by status"),
    priority: Optional[PurchaseOrderPriority] = Query(None, description="Filter by priority"),
    requested_by: Optional[uuid.UUID] = Query(None, description="Filter by requester"),
    order_date_from: Optional[str] = Query(None, description="Filter by order date from (YYYY-MM-DD)"),
    order_date_to: Optional[str] = Query(None, description="Filter by order date to (YYYY-MM-DD)"),
    is_overdue: Optional[bool] = Query(None, description="Filter overdue orders"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "purchase_orders"))
):
    """Get list of purchase orders with optional search and filters"""
    po_service = PurchaseOrderService(session, redis_client)
    
    # Build search criteria
    search = None
    if any([query, supplier_id, status, priority, requested_by, 
            order_date_from, order_date_to, is_overdue is not None]):
        from datetime import datetime
        from fastapi import HTTPException, status as http_status
        
        order_date_from_parsed = None
        order_date_to_parsed = None
        
        if order_date_from:
            try:
                order_date_from_parsed = datetime.strptime(order_date_from, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="Invalid order_date_from format. Use YYYY-MM-DD"
                )
        
        if order_date_to:
            try:
                order_date_to_parsed = datetime.strptime(order_date_to, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="Invalid order_date_to format. Use YYYY-MM-DD"
                )
        
        search = PurchaseOrderSearch(
            query=query,
            supplier_id=supplier_id,
            status=status,
            priority=priority,
            requested_by=requested_by,
            order_date_from=order_date_from_parsed,
            order_date_to=order_date_to_parsed,
            is_overdue=is_overdue
        )
    
    orders, total = await po_service.get_purchase_orders(pagination, search)
    
    return PaginatedResponse.create(
        items=orders,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/summary", response_model=PurchaseOrderSummary)
async def get_purchase_orders_summary(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "purchase_orders"))
):
    """Get purchase order summary statistics"""
    po_service = PurchaseOrderService(session, redis_client)
    return await po_service.get_purchase_orders_summary()


@router.get("/pending-approval", response_model=List[PurchaseOrderResponse])
async def get_pending_approval_orders(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "purchase_orders"))
):
    """Get purchase orders pending approval"""
    po_service = PurchaseOrderService(session, redis_client)
    return await po_service.get_pending_approval_orders()


@router.get("/{po_id}", response_model=PurchaseOrderResponse)
async def get_purchase_order(
    po_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "purchase_orders"))
):
    """Get purchase order by ID"""
    po_service = PurchaseOrderService(session, redis_client)
    return await po_service.get_purchase_order(po_id)


@router.put("/{po_id}", response_model=PurchaseOrderResponse)
async def update_purchase_order(
    po_id: uuid.UUID,
    po_data: PurchaseOrderUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "update", "purchase_orders"))
):
    """Update purchase order information"""
    po_service = PurchaseOrderService(session, redis_client)
    return await po_service.update_purchase_order(po_id, po_data)


@router.post("/{po_id}/approve", response_model=PurchaseOrderResponse)
async def approve_purchase_order(
    po_id: uuid.UUID,
    approval: PurchaseOrderApproval,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "approve", "purchase_orders"))
):
    """Approve or reject a purchase order"""
    po_service = PurchaseOrderService(session, redis_client)
    return await po_service.approve_purchase_order(po_id, approval, current_user.user_id)


@router.post("/{po_id}/send", response_model=PurchaseOrderResponse)
async def send_purchase_order(
    po_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "update", "purchase_orders"))
):
    """Send purchase order to supplier"""
    po_service = PurchaseOrderService(session, redis_client)
    return await po_service.send_purchase_order(po_id)


@router.post("/{po_id}/receive", response_model=PurchaseOrderResponse)
async def receive_purchase_order(
    po_id: uuid.UUID,
    receiving_data: PurchaseOrderReceiving,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "update", "purchase_orders"))
):
    """Receive items from purchase order"""
    po_service = PurchaseOrderService(session, redis_client)
    return await po_service.receive_purchase_order(po_id, receiving_data, current_user.user_id)


@router.post("/{po_id}/cancel", response_model=PurchaseOrderResponse)
async def cancel_purchase_order(
    po_id: uuid.UUID,
    reason: str = Query(..., description="Cancellation reason"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "update", "purchase_orders"))
):
    """Cancel a purchase order"""
    po_service = PurchaseOrderService(session, redis_client)
    return await po_service.cancel_purchase_order(po_id, reason, current_user.user_id)


@router.delete("/{po_id}")
async def delete_purchase_order(
    po_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "delete", "purchase_orders"))
):
    """Delete purchase order (only if in draft status)"""
    po_service = PurchaseOrderService(session, redis_client)
    return await po_service.delete_purchase_order(po_id)
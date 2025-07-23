"""
Payment management routes
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session, get_redis
from services.payment_service import PaymentService
from schemas.payment import (
    PaymentCreate, PaymentUpdate, PaymentResponse, PaymentSummary,
    PaymentSearch, PaymentReconciliation
)
from models.payment import PaymentMethod, PaymentStatus
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import redis
import uuid


router = APIRouter(prefix="/payments", tags=["Payment Management"])


@router.post("/", response_model=PaymentResponse)
async def create_payment(
    payment_data: PaymentCreate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "create", "payments"))
):
    """Create a new payment"""
    payment_service = PaymentService(session, redis_client)
    return await payment_service.create_payment(payment_data, current_user.user_id)


@router.get("/", response_model=PaginatedResponse[PaymentResponse])
async def get_payments(
    pagination: PaginationParams = Depends(),
    query: Optional[str] = Query(None, description="Search query"),
    invoice_id: Optional[uuid.UUID] = Query(None, description="Filter by invoice"),
    customer_id: Optional[uuid.UUID] = Query(None, description="Filter by customer"),
    payment_method: Optional[PaymentMethod] = Query(None, description="Filter by payment method"),
    status: Optional[PaymentStatus] = Query(None, description="Filter by status"),
    currency: Optional[str] = Query(None, description="Filter by currency"),
    payment_date_from: Optional[str] = Query(None, description="Filter by payment date from (YYYY-MM-DD)"),
    payment_date_to: Optional[str] = Query(None, description="Filter by payment date to (YYYY-MM-DD)"),
    is_reconciled: Optional[bool] = Query(None, description="Filter by reconciliation status"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "payments"))
):
    """Get list of payments with optional search and filters"""
    payment_service = PaymentService(session, redis_client)
    
    # Build search criteria
    search = None
    if any([query, invoice_id, customer_id, payment_method, status, currency, 
            payment_date_from, payment_date_to, is_reconciled is not None]):
        from datetime import datetime
        from fastapi import HTTPException, status as http_status
        
        payment_date_from_parsed = None
        payment_date_to_parsed = None
        
        if payment_date_from:
            try:
                payment_date_from_parsed = datetime.strptime(payment_date_from, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="Invalid payment_date_from format. Use YYYY-MM-DD"
                )
        
        if payment_date_to:
            try:
                payment_date_to_parsed = datetime.strptime(payment_date_to, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="Invalid payment_date_to format. Use YYYY-MM-DD"
                )
        
        search = PaymentSearch(
            query=query,
            invoice_id=invoice_id,
            customer_id=customer_id,
            payment_method=payment_method,
            status=status,
            currency=currency,
            payment_date_from=payment_date_from_parsed,
            payment_date_to=payment_date_to_parsed,
            is_reconciled=is_reconciled
        )
    
    payments, total = await payment_service.get_payments(pagination, search)
    
    return PaginatedResponse.create(
        items=payments,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/summary", response_model=PaymentSummary)
async def get_payment_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days for summary"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "payments"))
):
    """Get payment summary statistics"""
    payment_service = PaymentService(session, redis_client)
    return await payment_service.get_payment_summary(days)


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "payments"))
):
    """Get payment by ID"""
    payment_service = PaymentService(session, redis_client)
    return await payment_service.get_payment(payment_id)


@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: uuid.UUID,
    payment_data: PaymentUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "update", "payments"))
):
    """Update payment information"""
    payment_service = PaymentService(session, redis_client)
    return await payment_service.update_payment(payment_id, payment_data)


@router.post("/{payment_id}/confirm", response_model=PaymentResponse)
async def confirm_payment(
    payment_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "update", "payments"))
):
    """Confirm a pending payment"""
    payment_service = PaymentService(session, redis_client)
    return await payment_service.confirm_payment(payment_id, current_user.user_id)


@router.post("/reconcile")
async def reconcile_payments(
    reconciliation: PaymentReconciliation,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "update", "payments"))
):
    """Reconcile multiple payments"""
    payment_service = PaymentService(session, redis_client)
    return await payment_service.reconcile_payments(reconciliation, current_user.user_id)


@router.get("/unreconciled/list", response_model=List[PaymentResponse])
async def get_unreconciled_payments(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "payments"))
):
    """Get all unreconciled payments"""
    payment_service = PaymentService(session, redis_client)
    return await payment_service.get_unreconciled_payments()


@router.delete("/{payment_id}")
async def delete_payment(
    payment_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "delete", "payments"))
):
    """Delete payment"""
    payment_service = PaymentService(session, redis_client)
    return await payment_service.delete_payment(payment_id)
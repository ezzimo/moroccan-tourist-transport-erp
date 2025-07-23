"""
Invoice management routes
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from database import get_session, get_redis
from services.invoice_service import InvoiceService
from schemas.invoice import (
    InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceSummary,
    InvoiceSearch, InvoiceGeneration
)
from models.invoice import InvoiceStatus, PaymentStatus
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import redis
import uuid


router = APIRouter(prefix="/invoices", tags=["Invoice Management"])


@router.post("/", response_model=InvoiceResponse)
async def create_invoice(
    invoice_data: InvoiceCreate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "create", "invoices"))
):
    """Create a new invoice"""
    invoice_service = InvoiceService(session, redis_client)
    return await invoice_service.create_invoice(invoice_data, current_user.user_id)


@router.post("/generate", response_model=InvoiceResponse)
async def generate_invoice_from_booking(
    generation_data: InvoiceGeneration,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "create", "invoices"))
):
    """Generate invoice from booking"""
    invoice_service = InvoiceService(session, redis_client)
    return await invoice_service.generate_from_booking(generation_data, current_user.user_id)


@router.get("/", response_model=PaginatedResponse[InvoiceResponse])
async def get_invoices(
    pagination: PaginationParams = Depends(),
    query: Optional[str] = Query(None, description="Search query"),
    customer_id: Optional[uuid.UUID] = Query(None, description="Filter by customer"),
    booking_id: Optional[uuid.UUID] = Query(None, description="Filter by booking"),
    status: Optional[InvoiceStatus] = Query(None, description="Filter by status"),
    payment_status: Optional[PaymentStatus] = Query(None, description="Filter by payment status"),
    currency: Optional[str] = Query(None, description="Filter by currency"),
    issue_date_from: Optional[str] = Query(None, description="Filter by issue date from (YYYY-MM-DD)"),
    issue_date_to: Optional[str] = Query(None, description="Filter by issue date to (YYYY-MM-DD)"),
    is_overdue: Optional[bool] = Query(None, description="Filter overdue invoices"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "invoices"))
):
    """Get list of invoices with optional search and filters"""
    invoice_service = InvoiceService(session, redis_client)
    
    # Build search criteria
    search = None
    if any([query, customer_id, booking_id, status, payment_status, currency, 
            issue_date_from, issue_date_to, is_overdue is not None]):
        from datetime import datetime
        
        issue_date_from_parsed = None
        issue_date_to_parsed = None
        
        if issue_date_from:
            try:
                issue_date_from_parsed = datetime.strptime(issue_date_from, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid issue_date_from format. Use YYYY-MM-DD"
                )
        
        if issue_date_to:
            try:
                issue_date_to_parsed = datetime.strptime(issue_date_to, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid issue_date_to format. Use YYYY-MM-DD"
                )
        
        search = InvoiceSearch(
            query=query,
            customer_id=customer_id,
            booking_id=booking_id,
            status=status,
            payment_status=payment_status,
            currency=currency,
            issue_date_from=issue_date_from_parsed,
            issue_date_to=issue_date_to_parsed,
            is_overdue=is_overdue
        )
    
    invoices, total = await invoice_service.get_invoices(pagination, search)
    
    return PaginatedResponse.create(
        items=invoices,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/summary", response_model=InvoiceSummary)
async def get_invoice_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days for summary"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "invoices"))
):
    """Get invoice summary statistics"""
    invoice_service = InvoiceService(session, redis_client)
    return await invoice_service.get_invoice_summary(days)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "invoices"))
):
    """Get invoice by ID"""
    invoice_service = InvoiceService(session, redis_client)
    return await invoice_service.get_invoice(invoice_id)


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: uuid.UUID,
    invoice_data: InvoiceUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "update", "invoices"))
):
    """Update invoice information"""
    invoice_service = InvoiceService(session, redis_client)
    return await invoice_service.update_invoice(invoice_id, invoice_data)


@router.post("/{invoice_id}/send", response_model=InvoiceResponse)
async def send_invoice(
    invoice_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "update", "invoices"))
):
    """Send invoice to customer"""
    invoice_service = InvoiceService(session, redis_client)
    return await invoice_service.send_invoice(invoice_id)


@router.post("/{invoice_id}/cancel", response_model=InvoiceResponse)
async def cancel_invoice(
    invoice_id: uuid.UUID,
    reason: str = Query(..., description="Cancellation reason"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "update", "invoices"))
):
    """Cancel an invoice"""
    invoice_service = InvoiceService(session, redis_client)
    return await invoice_service.cancel_invoice(invoice_id, reason, current_user.user_id)


@router.get("/{invoice_id}/pdf")
async def download_invoice_pdf(
    invoice_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "invoices"))
):
    """Download invoice as PDF"""
    invoice_service = InvoiceService(session, redis_client)
    
    # Get invoice
    invoice = await invoice_service.get_invoice(invoice_id)
    
    # Generate PDF
    pdf_buffer = await invoice_service.generate_invoice_pdf(invoice)
    
    # Return PDF as streaming response
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=invoice_{invoice.invoice_number}.pdf"}
    )


@router.get("/overdue/list", response_model=List[InvoiceResponse])
async def get_overdue_invoices(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "invoices"))
):
    """Get all overdue invoices"""
    invoice_service = InvoiceService(session, redis_client)
    return await invoice_service.get_overdue_invoices()


@router.post("/bulk-send")
async def bulk_send_invoices(
    invoice_ids: List[uuid.UUID],
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "update", "invoices"))
):
    """Send multiple invoices at once"""
    invoice_service = InvoiceService(session, redis_client)
    return await invoice_service.bulk_send_invoices(invoice_ids)
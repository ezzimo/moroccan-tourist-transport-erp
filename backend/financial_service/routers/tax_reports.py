"""
Tax report management routes
"""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from database import get_session, get_redis
from services.tax_service import TaxService
from schemas.tax_report import (
    TaxReportCreate, TaxReportUpdate, TaxReportResponse, TaxSummary,
    TaxReportGeneration, VATDeclaration
)
from models.tax_report import ReportPeriod, ReportStatus, TaxType
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import redis
import uuid


router = APIRouter(prefix="/tax-reports", tags=["Tax Reporting"])


@router.post("/", response_model=TaxReportResponse)
async def create_tax_report(
    report_data: TaxReportCreate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "create", "tax_reports"))
):
    """Create a new tax report"""
    tax_service = TaxService(session, redis_client)
    return await tax_service.create_tax_report(report_data, current_user.user_id)


@router.post("/generate", response_model=TaxReportResponse)
async def generate_tax_report(
    generation_data: TaxReportGeneration,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "create", "tax_reports"))
):
    """Generate tax report for specified period"""
    tax_service = TaxService(session, redis_client)
    return await tax_service.generate_tax_report(generation_data, current_user.user_id)


@router.get("/", response_model=PaginatedResponse[TaxReportResponse])
async def get_tax_reports(
    pagination: PaginationParams = Depends(),
    tax_type: Optional[TaxType] = Query(None, description="Filter by tax type"),
    period_type: Optional[ReportPeriod] = Query(None, description="Filter by period type"),
    status: Optional[ReportStatus] = Query(None, description="Filter by status"),
    tax_year: Optional[int] = Query(None, description="Filter by tax year"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "tax_reports"))
):
    """Get list of tax reports with optional filters"""
    tax_service = TaxService(session, redis_client)
    
    reports, total = await tax_service.get_tax_reports(
        pagination=pagination,
        tax_type=tax_type,
        period_type=period_type,
        status=status,
        tax_year=tax_year
    )
    
    return PaginatedResponse.create(
        items=reports,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/summary", response_model=TaxSummary)
async def get_tax_summary(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "tax_reports"))
):
    """Get tax summary and compliance status"""
    tax_service = TaxService(session, redis_client)
    return await tax_service.get_tax_summary()


@router.get("/{report_id}", response_model=TaxReportResponse)
async def get_tax_report(
    report_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "tax_reports"))
):
    """Get tax report by ID"""
    tax_service = TaxService(session, redis_client)
    return await tax_service.get_tax_report(report_id)


@router.put("/{report_id}", response_model=TaxReportResponse)
async def update_tax_report(
    report_id: uuid.UUID,
    report_data: TaxReportUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "update", "tax_reports"))
):
    """Update tax report information"""
    tax_service = TaxService(session, redis_client)
    return await tax_service.update_tax_report(report_id, report_data, current_user.user_id)


@router.post("/{report_id}/submit", response_model=TaxReportResponse)
async def submit_tax_report(
    report_id: uuid.UUID,
    submission_reference: Optional[str] = Query(None, description="Government submission reference"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "submit", "tax_reports"))
):
    """Submit tax report to authorities"""
    tax_service = TaxService(session, redis_client)
    return await tax_service.submit_tax_report(report_id, submission_reference, current_user.user_id)


@router.get("/{report_id}/pdf")
async def download_tax_report_pdf(
    report_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "tax_reports"))
):
    """Download tax report as PDF"""
    tax_service = TaxService(session, redis_client)
    
    # Get report
    report = await tax_service.get_tax_report(report_id)
    
    # Generate PDF
    pdf_buffer = await tax_service.generate_tax_report_pdf(report)
    
    # Return PDF as streaming response
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=tax_report_{report.report_number}.pdf"}
    )


@router.get("/vat/declaration", response_model=VATDeclaration)
async def get_vat_declaration(
    period_start: str = Query(..., description="Period start date (YYYY-MM-DD)"),
    period_end: str = Query(..., description="Period end date (YYYY-MM-DD)"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "tax_reports"))
):
    """Get VAT declaration for specified period"""
    tax_service = TaxService(session, redis_client)
    
    from datetime import datetime
    from fastapi import HTTPException, status
    
    try:
        period_start_parsed = datetime.strptime(period_start, "%Y-%m-%d").date()
        period_end_parsed = datetime.strptime(period_end, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    return await tax_service.get_vat_declaration(period_start_parsed, period_end_parsed)


@router.delete("/{report_id}")
async def delete_tax_report(
    report_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "delete", "tax_reports"))
):
    """Delete tax report (only if not submitted)"""
    tax_service = TaxService(session, redis_client)
    return await tax_service.delete_tax_report(report_id)
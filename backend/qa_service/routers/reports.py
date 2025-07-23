"""
QA & Compliance reporting routes
"""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from database import get_session, get_redis
from services.report_service import ReportService
from utils.auth import require_permission, CurrentUser
from typing import Dict, Any, Optional
import redis


router = APIRouter(prefix="/reports", tags=["QA & Compliance Reports"])


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_qa_dashboard(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "reports"))
):
    """Get QA & Compliance dashboard overview"""
    report_service = ReportService(session, redis_client)
    return await report_service.get_dashboard_overview()


@router.get("/audit-performance", response_model=Dict[str, Any])
async def get_audit_performance_report(
    period_months: int = Query(12, ge=1, le=60, description="Period in months"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "reports"))
):
    """Get audit performance analytics"""
    report_service = ReportService(session, redis_client)
    return await report_service.get_audit_performance_report(period_months, entity_type)


@router.get("/compliance-status", response_model=Dict[str, Any])
async def get_compliance_status_report(
    domain: Optional[str] = Query(None, description="Filter by compliance domain"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "reports"))
):
    """Get compliance status report"""
    report_service = ReportService(session, redis_client)
    return await report_service.get_compliance_status_report(domain)


@router.get("/nonconformity-trends", response_model=Dict[str, Any])
async def get_nonconformity_trends(
    period_months: int = Query(12, ge=1, le=60, description="Period in months"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "reports"))
):
    """Get non-conformity trend analysis"""
    report_service = ReportService(session, redis_client)
    return await report_service.get_nonconformity_trends(period_months, severity)


@router.get("/certification-status", response_model=Dict[str, Any])
async def get_certification_status_report(
    scope: Optional[str] = Query(None, description="Filter by certification scope"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "reports"))
):
    """Get certification status report"""
    report_service = ReportService(session, redis_client)
    return await report_service.get_certification_status_report(scope)


@router.get("/corrective-actions", response_model=Dict[str, Any])
async def get_corrective_action_report(
    period_months: int = Query(6, ge=1, le=24, description="Period in months"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "reports"))
):
    """Get corrective action effectiveness report"""
    report_service = ReportService(session, redis_client)
    return await report_service.get_corrective_action_report(period_months)


@router.get("/risk-assessment", response_model=Dict[str, Any])
async def get_risk_assessment_report(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "reports"))
):
    """Get risk assessment report"""
    report_service = ReportService(session, redis_client)
    return await report_service.get_risk_assessment_report()


@router.get("/export/audit-report")
async def export_audit_report(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    format: str = Query("pdf", description="Export format: pdf, excel"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "export", "reports"))
):
    """Export audit report"""
    report_service = ReportService(session, redis_client)
    
    from datetime import datetime
    from fastapi import HTTPException, status
    
    try:
        start_date_parsed = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_parsed = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Generate report
    report_buffer, content_type, filename = await report_service.export_audit_report(
        start_date_parsed, end_date_parsed, format, entity_type
    )
    
    return StreamingResponse(
        report_buffer,
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/export/compliance-report")
async def export_compliance_report(
    format: str = Query("pdf", description="Export format: pdf, excel"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "export", "reports"))
):
    """Export compliance status report"""
    report_service = ReportService(session, redis_client)
    
    # Generate report
    report_buffer, content_type, filename = await report_service.export_compliance_report(
        format, domain
    )
    
    return StreamingResponse(
        report_buffer,
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/export/nonconformity-report")
async def export_nonconformity_report(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    format: str = Query("pdf", description="Export format: pdf, excel"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "export", "reports"))
):
    """Export non-conformity report"""
    report_service = ReportService(session, redis_client)
    
    from datetime import datetime
    from fastapi import HTTPException, status
    
    try:
        start_date_parsed = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_parsed = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Generate report
    report_buffer, content_type, filename = await report_service.export_nonconformity_report(
        start_date_parsed, end_date_parsed, format, severity
    )
    
    return StreamingResponse(
        report_buffer,
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
"""
Financial analytics and reporting routes
"""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from database import get_session, get_redis
from services.analytics_service import AnalyticsService
from utils.auth import require_permission, CurrentUser
from typing import Dict, Any, List, Optional
import redis


router = APIRouter(prefix="/analytics", tags=["Financial Analytics"])


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_financial_dashboard(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "analytics"))
):
    """Get financial dashboard overview"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_dashboard_overview()


@router.get("/revenue", response_model=Dict[str, Any])
async def get_revenue_analytics(
    period_months: int = Query(12, ge=1, le=60, description="Period in months"),
    currency: Optional[str] = Query(None, description="Filter by currency"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "analytics"))
):
    """Get revenue analytics"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_revenue_analytics(period_months, currency)


@router.get("/expenses", response_model=Dict[str, Any])
async def get_expense_analytics(
    period_months: int = Query(12, ge=1, le=60, description="Period in months"),
    cost_center: Optional[str] = Query(None, description="Filter by cost center"),
    department: Optional[str] = Query(None, description="Filter by department"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "analytics"))
):
    """Get expense analytics"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_expense_analytics(period_months, cost_center, department)


@router.get("/cash-flow", response_model=Dict[str, Any])
async def get_cash_flow_analytics(
    period_months: int = Query(12, ge=1, le=60, description="Period in months"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "analytics"))
):
    """Get cash flow analytics"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_cash_flow_analytics(period_months)


@router.get("/profitability", response_model=Dict[str, Any])
async def get_profitability_analytics(
    period_months: int = Query(12, ge=1, le=60, description="Period in months"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "analytics"))
):
    """Get profitability analytics"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_profitability_analytics(period_months)


@router.get("/kpis", response_model=Dict[str, Any])
async def get_financial_kpis(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "analytics"))
):
    """Get key financial performance indicators"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_financial_kpis()


@router.get("/aging", response_model=Dict[str, Any])
async def get_aging_report(
    report_type: str = Query("receivables", description="Type: receivables or payables"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "analytics"))
):
    """Get aging report for receivables or payables"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_aging_report(report_type)


@router.get("/budget-variance", response_model=Dict[str, Any])
async def get_budget_variance(
    period_months: int = Query(12, ge=1, le=60, description="Period in months"),
    cost_center: Optional[str] = Query(None, description="Filter by cost center"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "analytics"))
):
    """Get budget variance analysis"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_budget_variance(period_months, cost_center)


@router.get("/forecasting", response_model=Dict[str, Any])
async def get_financial_forecast(
    forecast_months: int = Query(6, ge=1, le=24, description="Months to forecast"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "read", "analytics"))
):
    """Get financial forecasting"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_financial_forecast(forecast_months)


@router.get("/export/profit-loss")
async def export_profit_loss_statement(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    format: str = Query("pdf", description="Export format: pdf, excel"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "export", "reports"))
):
    """Export profit & loss statement"""
    analytics_service = AnalyticsService(session, redis_client)
    
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
    report_buffer, content_type, filename = await analytics_service.export_profit_loss_statement(
        start_date_parsed, end_date_parsed, format
    )
    
    return StreamingResponse(
        report_buffer,
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/export/balance-sheet")
async def export_balance_sheet(
    as_of_date: str = Query(..., description="As of date (YYYY-MM-DD)"),
    format: str = Query("pdf", description="Export format: pdf, excel"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "export", "reports"))
):
    """Export balance sheet"""
    analytics_service = AnalyticsService(session, redis_client)
    
    from datetime import datetime
    from fastapi import HTTPException, status
    
    try:
        as_of_date_parsed = datetime.strptime(as_of_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Generate report
    report_buffer, content_type, filename = await analytics_service.export_balance_sheet(
        as_of_date_parsed, format
    )
    
    return StreamingResponse(
        report_buffer,
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/export/cash-flow")
async def export_cash_flow_statement(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    format: str = Query("pdf", description="Export format: pdf, excel"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("finance", "export", "reports"))
):
    """Export cash flow statement"""
    analytics_service = AnalyticsService(session, redis_client)
    
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
    report_buffer, content_type, filename = await analytics_service.export_cash_flow_statement(
        start_date_parsed, end_date_parsed, format
    )
    
    return StreamingResponse(
        report_buffer,
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
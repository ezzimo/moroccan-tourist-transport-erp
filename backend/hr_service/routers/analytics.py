"""
HR analytics and reporting routes
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session, get_redis
from services.analytics_service import AnalyticsService
from utils.auth import require_permission, CurrentUser
from typing import Dict, Any, List, Optional
import redis


router = APIRouter(prefix="/analytics", tags=["HR Analytics"])


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_hr_dashboard(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "analytics"))
):
    """Get HR dashboard overview"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_dashboard_overview()


@router.get("/workforce", response_model=Dict[str, Any])
async def get_workforce_analytics(
    period_months: int = Query(12, ge=1, le=60, description="Period in months"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "analytics"))
):
    """Get workforce analytics"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_workforce_analytics(period_months)


@router.get("/turnover", response_model=Dict[str, Any])
async def get_turnover_analytics(
    period_months: int = Query(12, ge=1, le=60, description="Period in months"),
    department: Optional[str] = Query(None, description="Filter by department"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "analytics"))
):
    """Get employee turnover analytics"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_turnover_analytics(period_months, department)


@router.get("/recruitment", response_model=Dict[str, Any])
async def get_recruitment_analytics(
    period_months: int = Query(12, ge=1, le=60, description="Period in months"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "analytics"))
):
    """Get recruitment analytics"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_recruitment_analytics(period_months)


@router.get("/training", response_model=Dict[str, Any])
async def get_training_analytics(
    period_months: int = Query(12, ge=1, le=60, description="Period in months"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "analytics"))
):
    """Get training analytics"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_training_analytics(period_months)


@router.get("/compensation", response_model=Dict[str, Any])
async def get_compensation_analytics(
    department: Optional[str] = Query(None, description="Filter by department"),
    position: Optional[str] = Query(None, description="Filter by position"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "compensation"))
):
    """Get compensation analytics"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_compensation_analytics(department, position)


@router.get("/demographics", response_model=Dict[str, Any])
async def get_demographics_analytics(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "analytics"))
):
    """Get workforce demographics analytics"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_demographics_analytics()


@router.get("/performance", response_model=Dict[str, Any])
async def get_performance_analytics(
    period_months: int = Query(12, ge=1, le=60, description="Period in months"),
    department: Optional[str] = Query(None, description="Filter by department"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "analytics"))
):
    """Get performance analytics"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_performance_analytics(period_months, department)


@router.get("/compliance", response_model=Dict[str, Any])
async def get_compliance_analytics(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "compliance"))
):
    """Get compliance analytics"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_compliance_analytics()


@router.get("/payroll-export", response_model=List[Dict[str, Any]])
async def export_payroll_data(
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, le=2030, description="Year"),
    department: Optional[str] = Query(None, description="Filter by department"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "export", "payroll"))
):
    """Export payroll data for external payroll system"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.export_payroll_data(month, year, department)


@router.get("/reports/headcount", response_model=Dict[str, Any])
async def get_headcount_report(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    group_by: str = Query("department", description="Group by: department, position, employment_type"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "reports"))
):
    """Get headcount report"""
    analytics_service = AnalyticsService(session, redis_client)
    
    from datetime import datetime
    try:
        start_date_parsed = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_parsed = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    return await analytics_service.get_headcount_report(start_date_parsed, end_date_parsed, group_by)


@router.get("/reports/absence", response_model=Dict[str, Any])
async def get_absence_report(
    period_months: int = Query(6, ge=1, le=24, description="Period in months"),
    department: Optional[str] = Query(None, description="Filter by department"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "reports"))
):
    """Get absence and attendance report"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_absence_report(period_months, department)
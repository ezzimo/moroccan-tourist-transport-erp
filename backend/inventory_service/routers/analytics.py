"""
Inventory analytics and reporting routes
"""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from database import get_session, get_redis
from services.analytics_service import AnalyticsService
from utils.auth import require_permission, CurrentUser
from typing import Dict, Any, List, Optional
import redis


router = APIRouter(prefix="/analytics", tags=["Inventory Analytics"])


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_inventory_dashboard(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "analytics"))
):
    """Get inventory dashboard overview"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_dashboard_overview()


@router.get("/stock-levels", response_model=Dict[str, Any])
async def get_stock_level_analytics(
    warehouse: Optional[str] = Query(None, description="Filter by warehouse"),
    category: Optional[str] = Query(None, description="Filter by category"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "analytics"))
):
    """Get stock level analytics"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_stock_level_analytics(warehouse, category)


@router.get("/valuation", response_model=Dict[str, Any])
async def get_inventory_valuation(
    method: str = Query("average", description="Valuation method: average, fifo, lifo"),
    warehouse: Optional[str] = Query(None, description="Filter by warehouse"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "analytics"))
):
    """Get inventory valuation report"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_inventory_valuation(method, warehouse)


@router.get("/turnover", response_model=Dict[str, Any])
async def get_inventory_turnover(
    period_months: int = Query(12, ge=1, le=60, description="Period in months"),
    category: Optional[str] = Query(None, description="Filter by category"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "analytics"))
):
    """Get inventory turnover analysis"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_inventory_turnover(period_months, category)


@router.get("/consumption", response_model=Dict[str, Any])
async def get_consumption_analytics(
    period_months: int = Query(6, ge=1, le=24, description="Period in months"),
    item_id: Optional[str] = Query(None, description="Filter by specific item"),
    category: Optional[str] = Query(None, description="Filter by category"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "analytics"))
):
    """Get consumption pattern analytics"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_consumption_analytics(period_months, item_id, category)


@router.get("/abc-analysis", response_model=Dict[str, Any])
async def get_abc_analysis(
    period_months: int = Query(12, ge=1, le=60, description="Period in months"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "analytics"))
):
    """Get ABC analysis of inventory items"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_abc_analysis(period_months)


@router.get("/supplier-performance", response_model=Dict[str, Any])
async def get_supplier_performance_analytics(
    period_months: int = Query(12, ge=1, le=60, description="Period in months"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "analytics"))
):
    """Get supplier performance analytics"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_supplier_performance_analytics(period_months)


@router.get("/cost-analysis", response_model=Dict[str, Any])
async def get_cost_analysis(
    period_months: int = Query(12, ge=1, le=60, description="Period in months"),
    cost_center: Optional[str] = Query(None, description="Filter by cost center"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "analytics"))
):
    """Get inventory cost analysis"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_cost_analysis(period_months, cost_center)


@router.get("/alerts", response_model=Dict[str, Any])
async def get_inventory_alerts(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "analytics"))
):
    """Get current inventory alerts and warnings"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_inventory_alerts()


@router.get("/forecasting", response_model=Dict[str, Any])
async def get_demand_forecasting(
    item_id: Optional[str] = Query(None, description="Specific item for forecasting"),
    forecast_months: int = Query(6, ge=1, le=24, description="Months to forecast"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "read", "analytics"))
):
    """Get demand forecasting analysis"""
    analytics_service = AnalyticsService(session, redis_client)
    return await analytics_service.get_demand_forecasting(item_id, forecast_months)


@router.get("/export/stock-report")
async def export_stock_report(
    format: str = Query("excel", description="Export format: excel, csv"),
    warehouse: Optional[str] = Query(None, description="Filter by warehouse"),
    category: Optional[str] = Query(None, description="Filter by category"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "export", "reports"))
):
    """Export stock level report"""
    analytics_service = AnalyticsService(session, redis_client)
    
    # Generate report
    report_buffer, content_type, filename = await analytics_service.export_stock_report(
        format, warehouse, category
    )
    
    return StreamingResponse(
        report_buffer,
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/export/movement-report")
async def export_movement_report(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    format: str = Query("excel", description="Export format: excel, csv"),
    item_id: Optional[str] = Query(None, description="Filter by item"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "export", "reports"))
):
    """Export stock movement report"""
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
    report_buffer, content_type, filename = await analytics_service.export_movement_report(
        start_date_parsed, end_date_parsed, format, item_id
    )
    
    return StreamingResponse(
        report_buffer,
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/export/valuation-report")
async def export_valuation_report(
    as_of_date: str = Query(..., description="Valuation date (YYYY-MM-DD)"),
    method: str = Query("average", description="Valuation method: average, fifo, lifo"),
    format: str = Query("excel", description="Export format: excel, csv"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("inventory", "export", "reports"))
):
    """Export inventory valuation report"""
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
    report_buffer, content_type, filename = await analytics_service.export_valuation_report(
        as_of_date_parsed, method, format
    )
    
    return StreamingResponse(
        report_buffer,
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
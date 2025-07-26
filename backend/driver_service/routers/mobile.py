"""
Mobile API routes for drivers
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session
from database import get_session
from models.driver_assignment import AssignmentStatus
from schemas.driver_assignment import DriverAssignmentResponse
from schemas.driver import DriverResponse
from schemas.mobile import (
    DriverDashboard, AssignmentDetails, OfflineDataBundle, 
    StatusUpdate, IncidentReport
)
from utils.auth import get_current_user, CurrentUser
from services.mobile_service import MobileService
from typing import List, Optional
from datetime import date
import uuid


router = APIRouter(prefix="/mobile", tags=["Mobile API"])


@router.get("/dashboard", response_model=DriverDashboard)
async def get_driver_dashboard(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get driver dashboard with current assignments and notifications"""
    mobile_service = MobileService(session)
    return await mobile_service.get_driver_dashboard(current_user.user_id)


@router.get("/assignments", response_model=List[DriverAssignmentResponse])
async def get_my_assignments(
    status: Optional[AssignmentStatus] = Query(None, description="Filter by assignment status"),
    start_date: Optional[date] = Query(None, description="Filter assignments from this date"),
    end_date: Optional[date] = Query(None, description="Filter assignments until this date"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get current driver's assignments"""
    mobile_service = MobileService(session)
    return await mobile_service.get_driver_assignments(
        driver_user_id=current_user.user_id,
        status=status,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/assignments/{assignment_id}", response_model=AssignmentDetails)
async def get_assignment_details(
    assignment_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get detailed assignment information with itinerary"""
    mobile_service = MobileService(session)
    return await mobile_service.get_assignment_details(assignment_id, current_user.user_id)


@router.put("/assignments/{assignment_id}/status")
async def update_assignment_status(
    assignment_id: uuid.UUID,
    status_update: StatusUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Update assignment status from mobile app"""
    mobile_service = MobileService(session)
    return await mobile_service.update_assignment_status(
        assignment_id=assignment_id,
        status=status_update.status,
        notes=status_update.notes,
        location=status_update.location,
        driver_user_id=current_user.user_id
    )


@router.get("/assignments/today", response_model=List[DriverAssignmentResponse])
async def get_today_assignments(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get today's assignments for the driver"""
    mobile_service = MobileService(session)
    return await mobile_service.get_today_assignments(current_user.user_id)


@router.get("/assignments/upcoming", response_model=List[DriverAssignmentResponse])
async def get_upcoming_assignments(
    days: int = Query(7, ge=1, le=30, description="Number of days ahead to look"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get upcoming assignments for the driver"""
    mobile_service = MobileService(session)
    return await mobile_service.get_upcoming_assignments(current_user.user_id, days)


@router.post("/incidents")
async def report_incident(
    incident_report: IncidentReport,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Report an incident from mobile app"""
    mobile_service = MobileService(session)
    return await mobile_service.report_incident(incident_report, current_user.user_id)


@router.get("/profile", response_model=DriverResponse)
async def get_my_profile(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get current driver's profile information"""
    mobile_service = MobileService(session)
    return await mobile_service.get_driver_profile(current_user.user_id)


@router.get("/documents")
async def get_my_documents(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get current driver's documents and certificates"""
    mobile_service = MobileService(session)
    return await mobile_service.get_driver_documents(current_user.user_id)


@router.get("/training")
async def get_my_training(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get current driver's training records"""
    mobile_service = MobileService(session)
    return await mobile_service.get_driver_training(current_user.user_id)


@router.get("/offline-bundle", response_model=OfflineDataBundle)
async def get_offline_data_bundle(
    days: int = Query(7, ge=1, le=14, description="Number of days of data to include"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get offline data bundle for mobile app"""
    mobile_service = MobileService(session)
    return await mobile_service.get_offline_data_bundle(current_user.user_id, days)


@router.post("/sync")
async def sync_offline_data(
    sync_data: dict,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Sync offline data changes back to server"""
    mobile_service = MobileService(session)
    return await mobile_service.sync_offline_data(sync_data, current_user.user_id)


@router.get("/notifications")
async def get_notifications(
    unread_only: bool = Query(False, description="Show only unread notifications"),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get driver notifications"""
    mobile_service = MobileService(session)
    return await mobile_service.get_driver_notifications(
        driver_user_id=current_user.user_id,
        unread_only=unread_only,
        limit=limit
    )


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Mark notification as read"""
    mobile_service = MobileService(session)
    return await mobile_service.mark_notification_read(notification_id, current_user.user_id)


@router.get("/performance")
async def get_my_performance(
    months: int = Query(6, ge=1, le=12, description="Number of months to analyze"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get current driver's performance metrics"""
    mobile_service = MobileService(session)
    return await mobile_service.get_driver_performance_metrics(current_user.user_id, months)
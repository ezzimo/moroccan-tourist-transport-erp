"""
Notification management routes
"""
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlmodel import Session
from database import get_session, get_redis
from services.notification_service import NotificationService
from schemas.notification import (
    NotificationCreate, NotificationUpdate, NotificationResponse,
    NotificationSend, NotificationBulkSend, NotificationSearch, NotificationStats
)
from models.notification import (
    NotificationType, NotificationChannel, NotificationStatus, RecipientType
)
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional, Dict, Any
import redis
import uuid


router = APIRouter(prefix="/notifications", tags=["Notification Management"])


@router.post("/send", response_model=List[NotificationResponse])
async def send_notification(
    notification_data: NotificationSend,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("notification", "create", "notifications"))
):
    """Send notification to recipients"""
    notification_service = NotificationService(session, redis_client)
    
    # Set source service if not provided
    if not notification_data.source_service:
        notification_data.source_service = "manual"
    
    return await notification_service.send_notification(notification_data)


@router.post("/send-bulk", response_model=Dict[str, Any])
async def send_bulk_notification(
    bulk_data: NotificationBulkSend,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("notification", "create", "notifications"))
):
    """Send bulk notification to multiple recipients"""
    notification_service = NotificationService(session, redis_client)
    return await notification_service.send_bulk_notification(bulk_data)


@router.get("/", response_model=PaginatedResponse[NotificationResponse])
async def get_notifications(
    pagination: PaginationParams = Depends(),
    type: Optional[NotificationType] = Query(None, description="Filter by notification type"),
    channel: Optional[NotificationChannel] = Query(None, description="Filter by channel"),
    status: Optional[NotificationStatus] = Query(None, description="Filter by status"),
    recipient_type: Optional[RecipientType] = Query(None, description="Filter by recipient type"),
    recipient_id: Optional[str] = Query(None, description="Filter by recipient ID"),
    recipient_email: Optional[str] = Query(None, description="Filter by recipient email"),
    created_from: Optional[str] = Query(None, description="Filter by created from (ISO datetime)"),
    created_to: Optional[str] = Query(None, description="Filter by created to (ISO datetime)"),
    source_service: Optional[str] = Query(None, description="Filter by source service"),
    group_id: Optional[str] = Query(None, description="Filter by group ID"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("notification", "read", "notifications"))
):
    """Get list of notifications with optional search and filters"""
    notification_service = NotificationService(session, redis_client)
    
    # Build search criteria
    search = None
    if any([type, channel, status, recipient_type, recipient_id, recipient_email, 
            created_from, created_to, source_service, group_id]):
        from datetime import datetime
        from fastapi import HTTPException, status as http_status
        
        created_from_parsed = None
        created_to_parsed = None
        
        if created_from:
            try:
                created_from_parsed = datetime.fromisoformat(created_from.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="Invalid created_from format. Use ISO datetime format"
                )
        
        if created_to:
            try:
                created_to_parsed = datetime.fromisoformat(created_to.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="Invalid created_to format. Use ISO datetime format"
                )
        
        search = NotificationSearch(
            type=type,
            channel=channel,
            status=status,
            recipient_type=recipient_type,
            recipient_id=recipient_id,
            recipient_email=recipient_email,
            created_from=created_from_parsed,
            created_to=created_to_parsed,
            source_service=source_service,
            group_id=group_id
        )
    
    notifications, total = await notification_service.get_notifications(pagination, search)
    
    return PaginatedResponse.create(
        items=notifications,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days for statistics"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("notification", "read", "notifications"))
):
    """Get notification statistics"""
    notification_service = NotificationService(session, redis_client)
    return await notification_service.get_notification_stats(days)


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("notification", "read", "notifications"))
):
    """Get notification by ID"""
    notification_service = NotificationService(session, redis_client)
    return await notification_service.get_notification(notification_id)


@router.put("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: uuid.UUID,
    notification_data: NotificationUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("notification", "update", "notifications"))
):
    """Update notification status and information"""
    notification_service = NotificationService(session, redis_client)
    return await notification_service.update_notification(notification_id, notification_data)


@router.post("/retry-failed", response_model=Dict[str, int])
async def retry_failed_notifications(
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("notification", "update", "notifications"))
):
    """Retry all failed notifications that can be retried"""
    notification_service = NotificationService(session, redis_client)
    
    # Run retry in background
    background_tasks.add_task(notification_service.retry_failed_notifications)
    
    return {"message": "Retry process started in background"}


@router.get("/recipient/{recipient_id}", response_model=PaginatedResponse[NotificationResponse])
async def get_recipient_notifications(
    recipient_id: str,
    pagination: PaginationParams = Depends(),
    channel: Optional[NotificationChannel] = Query(None, description="Filter by channel"),
    status: Optional[NotificationStatus] = Query(None, description="Filter by status"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("notification", "read", "notifications"))
):
    """Get all notifications for a specific recipient"""
    notification_service = NotificationService(session, redis_client)
    
    search = NotificationSearch(
        recipient_id=recipient_id,
        channel=channel,
        status=status
    )
    
    notifications, total = await notification_service.get_notifications(pagination, search)
    
    return PaginatedResponse.create(
        items=notifications,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/group/{group_id}", response_model=List[NotificationResponse])
async def get_group_notifications(
    group_id: str,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("notification", "read", "notifications"))
):
    """Get all notifications for a specific group"""
    notification_service = NotificationService(session, redis_client)
    
    search = NotificationSearch(group_id=group_id)
    
    # Get all notifications for the group (no pagination)
    from utils.pagination import PaginationParams
    pagination = PaginationParams(page=1, size=1000)  # Large page size for groups
    
    notifications, _ = await notification_service.get_notifications(pagination, search)
    
    return notifications
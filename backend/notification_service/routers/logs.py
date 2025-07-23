"""
Notification log and history routes
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session, get_redis
from services.notification_service import NotificationService
from schemas.notification import NotificationResponse, NotificationSearch
from models.notification import NotificationChannel, NotificationStatus, NotificationType
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional, Dict, Any
import redis
import uuid


router = APIRouter(prefix="/logs", tags=["Notification Logs"])


@router.get("/{recipient_id}", response_model=PaginatedResponse[NotificationResponse])
async def get_recipient_notification_history(
    recipient_id: str,
    pagination: PaginationParams = Depends(),
    type: Optional[NotificationType] = Query(None, description="Filter by notification type"),
    channel: Optional[NotificationChannel] = Query(None, description="Filter by channel"),
    status: Optional[NotificationStatus] = Query(None, description="Filter by status"),
    created_from: Optional[str] = Query(None, description="Filter by created from (ISO datetime)"),
    created_to: Optional[str] = Query(None, description="Filter by created to (ISO datetime)"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("notification", "read", "logs"))
):
    """Get notification history for a specific recipient"""
    notification_service = NotificationService(session, redis_client)
    
    # Build search criteria
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
        recipient_id=recipient_id,
        type=type,
        channel=channel,
        status=status,
        created_from=created_from_parsed,
        created_to=created_to_parsed
    )
    
    notifications, total = await notification_service.get_notifications(pagination, search)
    
    return PaginatedResponse.create(
        items=notifications,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/{recipient_id}/summary", response_model=Dict[str, Any])
async def get_recipient_notification_summary(
    recipient_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days for summary"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("notification", "read", "logs"))
):
    """Get notification summary for a specific recipient"""
    from datetime import datetime, timedelta
    from sqlmodel import select, func
    from models.notification import Notification
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total notifications
    total_stmt = select(func.count(Notification.id)).where(
        and_(
            Notification.recipient_id == recipient_id,
            Notification.created_at >= start_date
        )
    )
    total_notifications = session.exec(total_stmt).one()
    
    # By status
    status_stmt = select(
        Notification.status, func.count(Notification.id)
    ).where(
        and_(
            Notification.recipient_id == recipient_id,
            Notification.created_at >= start_date
        )
    ).group_by(Notification.status)
    
    by_status = {}
    for status_val, count in session.exec(status_stmt):
        by_status[status_val.value] = count
    
    # By channel
    channel_stmt = select(
        Notification.channel, func.count(Notification.id)
    ).where(
        and_(
            Notification.recipient_id == recipient_id,
            Notification.created_at >= start_date
        )
    ).group_by(Notification.channel)
    
    by_channel = {}
    for channel_val, count in session.exec(channel_stmt):
        by_channel[channel_val.value] = count
    
    # By type
    type_stmt = select(
        Notification.type, func.count(Notification.id)
    ).where(
        and_(
            Notification.recipient_id == recipient_id,
            Notification.created_at >= start_date
        )
    ).group_by(Notification.type)
    
    by_type = {}
    for type_val, count in session.exec(type_stmt):
        by_type[type_val.value] = count
    
    # Recent notifications
    recent_stmt = select(Notification).where(
        and_(
            Notification.recipient_id == recipient_id,
            Notification.created_at >= start_date
        )
    ).order_by(Notification.created_at.desc()).limit(5)
    
    recent_notifications = session.exec(recent_stmt).all()
    
    return {
        "recipient_id": recipient_id,
        "period_days": days,
        "total_notifications": total_notifications,
        "by_status": by_status,
        "by_channel": by_channel,
        "by_type": by_type,
        "recent_notifications": [
            {
                "id": str(n.id),
                "type": n.type.value,
                "channel": n.channel.value,
                "status": n.status.value,
                "subject": n.subject,
                "created_at": n.created_at.isoformat()
            }
            for n in recent_notifications
        ]
    }


@router.get("/audit/{notification_id}", response_model=Dict[str, Any])
async def get_notification_audit_trail(
    notification_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("notification", "read", "logs"))
):
    """Get detailed audit trail for a specific notification"""
    notification_service = NotificationService(session, redis_client)
    notification = await notification_service.get_notification(notification_id)
    
    # Build audit trail
    audit_trail = {
        "notification_id": str(notification.id),
        "created_at": notification.created_at.isoformat(),
        "events": []
    }
    
    # Add creation event
    audit_trail["events"].append({
        "event": "created",
        "timestamp": notification.created_at.isoformat(),
        "details": {
            "type": notification.type.value,
            "channel": notification.channel.value,
            "recipient": notification.recipient_email or notification.recipient_phone,
            "source_service": notification.source_service
        }
    })
    
    # Add status change events
    if notification.sent_at:
        audit_trail["events"].append({
            "event": "sent",
            "timestamp": notification.sent_at.isoformat(),
            "details": {
                "external_id": notification.external_id,
                "provider_response": notification.provider_response
            }
        })
    
    if notification.delivered_at:
        audit_trail["events"].append({
            "event": "delivered",
            "timestamp": notification.delivered_at.isoformat(),
            "details": {}
        })
    
    if notification.failed_at:
        audit_trail["events"].append({
            "event": "failed",
            "timestamp": notification.failed_at.isoformat(),
            "details": {
                "error_message": notification.error_message,
                "error_code": notification.error_code,
                "retry_count": notification.retry_count
            }
        })
    
    # Add retry events
    for i in range(notification.retry_count):
        audit_trail["events"].append({
            "event": f"retry_{i + 1}",
            "timestamp": notification.updated_at.isoformat() if notification.updated_at else None,
            "details": {
                "attempt": i + 1,
                "max_retries": notification.max_retries
            }
        })
    
    # Sort events by timestamp
    audit_trail["events"].sort(key=lambda x: x["timestamp"] or "")
    
    return audit_trail


@router.get("/export/{recipient_id}")
async def export_recipient_notifications(
    recipient_id: str,
    format: str = Query("csv", description="Export format: csv, json"),
    days: int = Query(90, ge=1, le=365, description="Number of days to export"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("notification", "export", "logs"))
):
    """Export notification history for a recipient"""
    from datetime import datetime, timedelta
    from sqlmodel import select
    from models.notification import Notification
    from fastapi.responses import StreamingResponse
    import csv
    import json
    from io import StringIO
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get notifications
    statement = select(Notification).where(
        and_(
            Notification.recipient_id == recipient_id,
            Notification.created_at >= start_date
        )
    ).order_by(Notification.created_at.desc())
    
    notifications = session.exec(statement).all()
    
    if format.lower() == "csv":
        # Generate CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "ID", "Type", "Channel", "Status", "Subject", "Recipient",
            "Created At", "Sent At", "Delivered At", "Failed At", "Error Message"
        ])
        
        # Write data
        for notification in notifications:
            writer.writerow([
                str(notification.id),
                notification.type.value,
                notification.channel.value,
                notification.status.value,
                notification.subject or "",
                notification.recipient_email or notification.recipient_phone or "",
                notification.created_at.isoformat(),
                notification.sent_at.isoformat() if notification.sent_at else "",
                notification.delivered_at.isoformat() if notification.delivered_at else "",
                notification.failed_at.isoformat() if notification.failed_at else "",
                notification.error_message or ""
            ])
        
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=notifications_{recipient_id}.csv"}
        )
    
    else:  # JSON format
        data = []
        for notification in notifications:
            data.append({
                "id": str(notification.id),
                "type": notification.type.value,
                "channel": notification.channel.value,
                "status": notification.status.value,
                "subject": notification.subject,
                "message": notification.message,
                "recipient_email": notification.recipient_email,
                "recipient_phone": notification.recipient_phone,
                "created_at": notification.created_at.isoformat(),
                "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
                "delivered_at": notification.delivered_at.isoformat() if notification.delivered_at else None,
                "failed_at": notification.failed_at.isoformat() if notification.failed_at else None,
                "error_message": notification.error_message,
                "retry_count": notification.retry_count
            })
        
        json_str = json.dumps(data, indent=2)
        
        return StreamingResponse(
            iter([json_str]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=notifications_{recipient_id}.json"}
        )
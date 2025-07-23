"""
Notification service for sending and managing notifications
"""
from sqlmodel import Session, select, and_, or_
from fastapi import HTTPException, status
from models.notification import (
    Notification, NotificationStatus, NotificationChannel, NotificationType
)
from models.template import Template
from models.user_preference import UserPreference
from schemas.notification import (
    NotificationCreate, NotificationUpdate, NotificationResponse,
    NotificationSend, NotificationBulkSend, NotificationSearch, NotificationStats
)
from utils.pagination import PaginationParams, paginate_query
from services.channel_services import (
    EmailService, SMSService, PushService, WhatsAppService
)
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
import redis
import uuid
import asyncio


class NotificationService:
    """Service for handling notification operations"""
    
    def __init__(self, session: Session, redis_client: redis.Redis):
        self.session = session
        self.redis = redis_client
        self.email_service = EmailService()
        self.sms_service = SMSService()
        self.push_service = PushService()
        self.whatsapp_service = WhatsAppService()
    
    async def send_notification(self, notification_data: NotificationSend) -> List[NotificationResponse]:
        """Send notification to multiple recipients"""
        notifications = []
        
        for recipient in notification_data.recipients:
            # Determine channels to use
            channels = notification_data.channels
            if not channels:
                # Get user preferences to determine channels
                channels = await self._get_preferred_channels(
                    recipient.get("user_id"),
                    notification_data.type
                )
            
            # Create notification for each channel
            for channel in channels:
                notification = await self._create_notification(
                    notification_data, recipient, channel
                )
                notifications.append(notification)
        
        # Send notifications asynchronously
        await self._dispatch_notifications(notifications)
        
        return [self._create_notification_response(n) for n in notifications]
    
    async def send_bulk_notification(self, bulk_data: NotificationBulkSend) -> Dict[str, Any]:
        """Send bulk notification to multiple recipients"""
        notifications = []
        
        for recipient in bulk_data.recipients:
            notification = await self._create_notification(
                bulk_data, recipient, bulk_data.channel
            )
            notifications.append(notification)
        
        # Batch send notifications
        success_count = 0
        failed_count = 0
        
        for notification in notifications:
            try:
                await self._send_single_notification(notification)
                success_count += 1
            except Exception as e:
                notification.status = NotificationStatus.FAILED
                notification.error_message = str(e)
                notification.failed_at = datetime.utcnow()
                self.session.add(notification)
                failed_count += 1
        
        self.session.commit()
        
        return {
            "total_sent": len(notifications),
            "successful": success_count,
            "failed": failed_count,
            "group_id": bulk_data.group_id
        }
    
    async def get_notification(self, notification_id: uuid.UUID) -> NotificationResponse:
        """Get notification by ID"""
        statement = select(Notification).where(Notification.id == notification_id)
        notification = self.session.exec(statement).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return self._create_notification_response(notification)
    
    async def get_notifications(
        self, 
        pagination: PaginationParams,
        search: Optional[NotificationSearch] = None
    ) -> Tuple[List[NotificationResponse], int]:
        """Get list of notifications with optional search"""
        query = select(Notification)
        
        # Apply search filters
        if search:
            conditions = []
            
            if search.type:
                conditions.append(Notification.type == search.type)
            
            if search.channel:
                conditions.append(Notification.channel == search.channel)
            
            if search.status:
                conditions.append(Notification.status == search.status)
            
            if search.recipient_type:
                conditions.append(Notification.recipient_type == search.recipient_type)
            
            if search.recipient_id:
                conditions.append(Notification.recipient_id == search.recipient_id)
            
            if search.recipient_email:
                conditions.append(Notification.recipient_email.ilike(f"%{search.recipient_email}%"))
            
            if search.created_from:
                conditions.append(Notification.created_at >= search.created_from)
            
            if search.created_to:
                conditions.append(Notification.created_at <= search.created_to)
            
            if search.source_service:
                conditions.append(Notification.source_service == search.source_service)
            
            if search.group_id:
                conditions.append(Notification.group_id == search.group_id)
            
            if conditions:
                query = query.where(and_(*conditions))
        
        # Order by creation date (newest first)
        query = query.order_by(Notification.created_at.desc())
        
        notifications, total = paginate_query(self.session, query, pagination)
        
        return [self._create_notification_response(n) for n in notifications], total
    
    async def update_notification(
        self, 
        notification_id: uuid.UUID, 
        notification_data: NotificationUpdate
    ) -> NotificationResponse:
        """Update notification status and information"""
        statement = select(Notification).where(Notification.id == notification_id)
        notification = self.session.exec(statement).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Update fields
        update_data = notification_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(notification, field, value)
        
        notification.updated_at = datetime.utcnow()
        
        self.session.add(notification)
        self.session.commit()
        self.session.refresh(notification)
        
        return self._create_notification_response(notification)
    
    async def retry_failed_notifications(self) -> Dict[str, int]:
        """Retry failed notifications that can be retried"""
        statement = select(Notification).where(
            and_(
                Notification.status == NotificationStatus.FAILED,
                Notification.retry_count < Notification.max_retries
            )
        )
        
        failed_notifications = self.session.exec(statement).all()
        
        retry_count = 0
        success_count = 0
        
        for notification in failed_notifications:
            if notification.can_retry() and not notification.is_expired():
                try:
                    await self._send_single_notification(notification)
                    success_count += 1
                except Exception as e:
                    notification.retry_count += 1
                    notification.error_message = str(e)
                    notification.updated_at = datetime.utcnow()
                    self.session.add(notification)
                
                retry_count += 1
        
        self.session.commit()
        
        return {
            "retried": retry_count,
            "successful": success_count,
            "failed": retry_count - success_count
        }
    
    async def get_notification_stats(self, days: int = 30) -> NotificationStats:
        """Get notification statistics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total notifications
        total_stmt = select(Notification).where(Notification.created_at >= start_date)
        total_notifications = len(self.session.exec(total_stmt).all())
        
        # By status
        status_stmt = select(Notification.status, Notification.id).where(
            Notification.created_at >= start_date
        )
        status_results = self.session.exec(status_stmt).all()
        
        by_status = {}
        for status_val, _ in status_results:
            by_status[status_val.value] = by_status.get(status_val.value, 0) + 1
        
        # By channel
        channel_stmt = select(Notification.channel, Notification.id).where(
            Notification.created_at >= start_date
        )
        channel_results = self.session.exec(channel_stmt).all()
        
        by_channel = {}
        for channel_val, _ in channel_results:
            by_channel[channel_val.value] = by_channel.get(channel_val.value, 0) + 1
        
        # By type
        type_stmt = select(Notification.type, Notification.id).where(
            Notification.created_at >= start_date
        )
        type_results = self.session.exec(type_stmt).all()
        
        by_type = {}
        for type_val, _ in type_results:
            by_type[type_val.value] = by_type.get(type_val.value, 0) + 1
        
        # Calculate rates
        delivered_count = by_status.get("delivered", 0) + by_status.get("sent", 0)
        failed_count = by_status.get("failed", 0)
        
        delivery_rate = (delivered_count / total_notifications * 100) if total_notifications > 0 else 0
        retry_rate = (sum(1 for n in self.session.exec(total_stmt).all() if n.retry_count > 0) / total_notifications * 100) if total_notifications > 0 else 0
        
        return NotificationStats(
            total_notifications=total_notifications,
            by_status=by_status,
            by_channel=by_channel,
            by_type=by_type,
            delivery_rate=delivery_rate,
            average_delivery_time_minutes=None,  # TODO: Calculate from delivery times
            failed_notifications=failed_count,
            retry_rate=retry_rate
        )
    
    async def _create_notification(
        self, 
        notification_data, 
        recipient: Dict[str, Any], 
        channel: NotificationChannel
    ) -> Notification:
        """Create notification record"""
        # Render template if provided
        subject = None
        message = getattr(notification_data, 'message', '')
        
        if hasattr(notification_data, 'template_id') and notification_data.template_id:
            template = self.session.exec(
                select(Template).where(Template.id == notification_data.template_id)
            ).first()
            
            if template:
                variables = getattr(notification_data, 'template_variables', {}) or {}
                rendered = template.render(variables)
                subject = rendered.get('subject')
                message = rendered.get('body')
        
        # Create notification
        notification = Notification(
            type=notification_data.type,
            channel=channel,
            recipient_type=getattr(notification_data, 'recipient_type', 'user'),
            recipient_id=recipient.get('user_id') or recipient.get('id'),
            recipient_email=recipient.get('email'),
            recipient_phone=recipient.get('phone'),
            recipient_name=recipient.get('name'),
            subject=subject,
            message=message,
            template_id=getattr(notification_data, 'template_id', None),
            priority=getattr(notification_data, 'priority', 5),
            scheduled_at=getattr(notification_data, 'scheduled_at', None),
            expires_at=getattr(notification_data, 'expires_at', None),
            source_service=getattr(notification_data, 'source_service', None),
            source_event=getattr(notification_data, 'source_event', None),
            group_id=getattr(notification_data, 'group_id', None)
        )
        
        if hasattr(notification_data, 'payload'):
            notification.set_payload_dict(notification_data.payload or {})
        
        if hasattr(notification_data, 'template_variables'):
            notification.set_template_variables_dict(notification_data.template_variables or {})
        
        self.session.add(notification)
        self.session.commit()
        self.session.refresh(notification)
        
        return notification
    
    async def _dispatch_notifications(self, notifications: List[Notification]):
        """Dispatch notifications asynchronously"""
        tasks = []
        for notification in notifications:
            if notification.should_send_now() and not notification.is_expired():
                task = asyncio.create_task(self._send_single_notification(notification))
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_single_notification(self, notification: Notification):
        """Send a single notification"""
        try:
            notification.status = NotificationStatus.SENDING
            notification.updated_at = datetime.utcnow()
            self.session.add(notification)
            self.session.commit()
            
            # Send based on channel
            if notification.channel == NotificationChannel.EMAIL:
                await self.email_service.send_email(
                    to_email=notification.recipient_email,
                    subject=notification.subject,
                    body=notification.message,
                    recipient_name=notification.recipient_name
                )
            elif notification.channel == NotificationChannel.SMS:
                await self.sms_service.send_sms(
                    to_phone=notification.recipient_phone,
                    message=notification.message
                )
            elif notification.channel == NotificationChannel.PUSH:
                payload = notification.get_payload_dict()
                await self.push_service.send_push(
                    token=payload.get('push_token'),
                    title=notification.subject,
                    body=notification.message,
                    data=payload
                )
            elif notification.channel == NotificationChannel.WHATSAPP:
                await self.whatsapp_service.send_message(
                    to_phone=notification.recipient_phone,
                    message=notification.message
                )
            
            # Update status to sent
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.utcnow()
            
        except Exception as e:
            notification.status = NotificationStatus.FAILED
            notification.error_message = str(e)
            notification.failed_at = datetime.utcnow()
            notification.retry_count += 1
            
            # Try fallback channel if enabled
            if self._should_use_fallback(notification):
                await self._send_fallback_notification(notification)
        
        notification.updated_at = datetime.utcnow()
        self.session.add(notification)
        self.session.commit()
    
    async def _get_preferred_channels(
        self, 
        user_id: Optional[str], 
        notification_type: NotificationType
    ) -> List[NotificationChannel]:
        """Get preferred channels for user and notification type"""
        if not user_id:
            return [NotificationChannel.EMAIL]  # Default fallback
        
        try:
            user_uuid = uuid.UUID(user_id)
            preferences = self.session.exec(
                select(UserPreference).where(UserPreference.user_id == user_uuid)
            ).first()
            
            if preferences:
                enabled_channels = []
                for channel in preferences.get_enabled_channels():
                    if preferences.is_notification_type_enabled(notification_type, channel):
                        enabled_channels.append(channel)
                return enabled_channels
        except:
            pass
        
        return [NotificationChannel.EMAIL]  # Default fallback
    
    def _should_use_fallback(self, notification: Notification) -> bool:
        """Check if fallback channel should be used"""
        from config import settings
        return (
            settings.enable_fallback_channels and
            notification.retry_count >= 1 and
            notification.channel.value in settings.fallback_mapping
        )
    
    async def _send_fallback_notification(self, original_notification: Notification):
        """Send notification via fallback channel"""
        from config import settings
        
        fallback_channels = settings.fallback_mapping.get(original_notification.channel.value, [])
        
        for fallback_channel in fallback_channels:
            try:
                # Create new notification for fallback
                fallback_notification = Notification(
                    type=original_notification.type,
                    channel=NotificationChannel(fallback_channel),
                    recipient_type=original_notification.recipient_type,
                    recipient_id=original_notification.recipient_id,
                    recipient_email=original_notification.recipient_email,
                    recipient_phone=original_notification.recipient_phone,
                    recipient_name=original_notification.recipient_name,
                    subject=f"[Fallback] {original_notification.subject}",
                    message=original_notification.message,
                    priority=original_notification.priority,
                    source_service=original_notification.source_service,
                    group_id=original_notification.group_id
                )
                
                self.session.add(fallback_notification)
                self.session.commit()
                
                await self._send_single_notification(fallback_notification)
                break  # Stop after first successful fallback
                
            except Exception:
                continue  # Try next fallback channel
    
    def _create_notification_response(self, notification: Notification) -> NotificationResponse:
        """Create notification response with calculated fields"""
        return NotificationResponse(
            id=notification.id,
            type=notification.type,
            channel=notification.channel,
            recipient_type=notification.recipient_type,
            recipient_id=notification.recipient_id,
            recipient_email=notification.recipient_email,
            recipient_phone=notification.recipient_phone,
            recipient_name=notification.recipient_name,
            subject=notification.subject,
            message=notification.message,
            payload=notification.get_payload_dict(),
            template_id=notification.template_id,
            template_variables=notification.get_template_variables_dict(),
            status=notification.status,
            retry_count=notification.retry_count,
            max_retries=notification.max_retries,
            priority=notification.priority,
            scheduled_at=notification.scheduled_at,
            expires_at=notification.expires_at,
            sent_at=notification.sent_at,
            delivered_at=notification.delivered_at,
            failed_at=notification.failed_at,
            external_id=notification.external_id,
            provider_response=notification.provider_response,
            error_message=notification.error_message,
            error_code=notification.error_code,
            source_service=notification.source_service,
            source_event=notification.source_event,
            group_id=notification.group_id,
            created_at=notification.created_at,
            updated_at=notification.updated_at,
            can_retry=notification.can_retry(),
            is_expired=notification.is_expired(),
            should_send_now=notification.should_send_now()
        )
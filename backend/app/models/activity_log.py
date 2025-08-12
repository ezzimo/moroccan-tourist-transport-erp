"""
Activity log model for auditing user management actions
"""
from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import json


class ActivityLog(SQLModel, table=True):
    """Activity log for tracking user management actions"""
    __tablename__ = "activity_logs"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # User who performed the action
    actor_id: Optional[uuid.UUID] = Field(
        foreign_key="users.id", index=True, description="User who performed the action"
    )
    actor_email: str = Field(max_length=255, index=True, description="Email of the actor")
    
    # Target of the action (if applicable)
    target_user_id: Optional[uuid.UUID] = Field(
        foreign_key="users.id", index=True, description="User who was affected by the action"
    )
    target_user_email: Optional[str] = Field(max_length=255, description="Email of the target user")
    
    # Action details
    action: str = Field(max_length=100, index=True, description="Action performed (e.g., 'user_created', 'role_assigned')")
    resource: str = Field(max_length=100, index=True, description="Resource affected (e.g., 'user', 'role')")
    
    # Additional context
    description: str = Field(description="Human-readable description of the action")
    extra_data: Optional[str] = Field(default=None, description="JSON string with additional action metadata")
    
    # Request context
    ip_address: Optional[str] = Field(max_length=45, description="IP address of the actor")
    user_agent: Optional[str] = Field(max_length=500, description="User agent of the request")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    def set_metadata(self, data: dict[str, Any]):
        """Set metadata as JSON string"""
        self.extra_data = json.dumps(data) if data else None
    
    def get_metadata(self) -> dict[str, Any]:
        """Get metadata as dictionary"""
        if self.extra_data:
            try:
                return json.loads(self.extra_data)
            except json.JSONDecodeError:
                return {}
        return {}
    
    @classmethod
    def create_log(
        cls,
        actor_id: uuid.UUID,
        actor_email: str,
        action: str,
        resource: str,
        description: str,
        target_user_id: Optional[uuid.UUID] = None,
        target_user_email: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> "ActivityLog":
        """Create a new activity log entry"""
        log = cls(
            actor_id=actor_id,
            actor_email=actor_email,
            target_user_id=target_user_id,
            target_user_email=target_user_email,
            action=action,
            resource=resource,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if metadata:
            log.set_metadata(metadata)
        
        return log


# Common activity log actions
class ActivityActions:
    # User management
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_RESTORED = "user_restored"
    USER_LOCKED = "user_locked"
    USER_UNLOCKED = "user_unlocked"
    USER_PASSWORD_RESET = "user_password_reset"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_LOGIN_FAILED = "user_login_failed"
    
    # Role management
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REMOVED = "role_removed"
    ROLES_BULK_ASSIGNED = "roles_bulk_assigned"
    
    # Bulk operations
    USERS_BULK_ACTIVATED = "users_bulk_activated"
    USERS_BULK_DEACTIVATED = "users_bulk_deactivated"
    USERS_BULK_DELETED = "users_bulk_deleted"
    
    # Import/Export
    USERS_IMPORTED = "users_imported"
    USERS_EXPORTED = "users_exported"


# Common resource types
class ActivityResources:
    USER = "user"
    ROLE = "role"
    PERMISSION = "permission"
    SYSTEM = "system"


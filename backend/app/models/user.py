"""
User model with authentication fields
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .role import Role


class UserRole(SQLModel, table=True):
    """Many-to-many relationship between users and roles"""
    __tablename__ = "user_roles"

    user_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="users.id", primary_key=True
    )
    role_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="roles.id", primary_key=True
    )


class User(SQLModel, table=True):
    """User model with authentication and profile information"""
    __tablename__ = "users"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    full_name: str = Field(max_length=255, index=True)
    email: str = Field(unique=True, index=True, max_length=255)
    phone: str = Field(max_length=20, index=True)
    password_hash: str = Field(max_length=255)

    # Status fields
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    is_locked: bool = Field(
        default=False, description="Account locked by admin"
    )
    must_change_password: bool = Field(
        default=False, description="User must change password on next login"
    )

    # Profile fields
    avatar_url: Optional[str] = Field(
        default=None, max_length=500, description="URL to user's avatar image"
    )

    # Security fields
    failed_login_attempts: int = Field(
        default=0, description="Number of consecutive failed login attempts"
    )
    last_login_at: Optional[datetime] = Field(
        default=None, description="Last successful login timestamp"
    )

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    deleted_at: Optional[datetime] = Field(
        default=None, description="Soft deletion timestamp"
    )

    # Relationships
    roles: list["Role"] = Relationship(
        back_populates="users",
        link_model=UserRole,
    )

    def has_permission(
            self, service_name: str, action: str, resource: str
    ) -> bool:
        """
        Check if user has specific permission
        (case- and whitespace-insensitive, supports '*' wildcard).
        Args:
            service_name (str): Name of the service.
            action (str): Action to be performed.
            resource (str): Resource on which action is performed.
        Returns:
            bool: True if user has permission, False otherwise.
        """
        if self.deleted_at is not None or self.is_locked:
            return False

        svc = (service_name or "").strip().lower()
        act = (action or "").strip().lower()
        res = (str(resource) or "").strip().lower()

        # Super/admin short-circuit if you want:
        # if self.is_admin():
        #     return True

        for role in self.roles:
            for permission in role.permissions:
                p_svc = (permission.service_name or "").strip().lower()
                p_act = (permission.action or "").strip().lower()
                p_res = (permission.resource or "*").strip().lower()

                if p_svc != svc:
                    continue
                if p_act != act:
                    continue
                # Resource match with wildcard support
                if p_res == "*" or p_res == "all" or p_res == res:
                    return True
        return False

    def get_all_permissions(self) -> list[str]:
        """
        Get all permissions for the user in normalized 
        'service:action:resource' form.
        Returns:
            list[str]: Sorted list of unique permissions.
        """
        perms: set[str] = set()
        for role in self.roles:
            for permission in role.permissions:
                svc = (permission.service_name or "").strip().lower()
                act = (permission.action or "").strip().lower()
                res = (permission.resource or "*").strip().lower()
                perms.add(f"{svc}:{act}:{res}")
        return sorted(perms)

    def is_admin(self) -> bool:
        """Check if user has admin privileges"""
        admin_roles = ['super_admin', 'tenant_admin', 'role_manager']
        return any(role.name in admin_roles for role in self.roles)

    def can_manage_users(self) -> bool:
        """Check if user can manage other users"""
        return self.has_permission("auth", "write", "users") or self.is_admin()

    def reset_failed_attempts(self):
        """Reset failed login attempts counter"""
        self.failed_login_attempts = 0

    def increment_failed_attempts(self):
        """Increment failed login attempts counter"""
        self.failed_login_attempts += 1

    def lock_account(self):
        """Lock the user account"""
        self.is_locked = True
        self.updated_at = datetime.utcnow()

    def unlock_account(self):
        """Unlock the user account"""
        self.is_locked = False
        self.failed_login_attempts = 0
        self.updated_at = datetime.utcnow()

    def soft_delete(self):
        """Soft delete the user"""
        self.deleted_at = datetime.utcnow()
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def restore(self):
        """Restore soft deleted user"""
        self.deleted_at = None
        self.is_active = True
        self.updated_at = datetime.utcnow()

"""
Role model for RBAC system
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid
from .user import UserRole
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .permission import Permission


class RolePermission(SQLModel, table=True):
    """Many-to-many relationship between roles and permissions"""

    role_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="role.id", primary_key=True
    )
    permission_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="permissions.id", primary_key=True
    )


class Role(SQLModel, table=True):
    """Role model for grouping permissions"""

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    name: str = Field(unique=True, max_length=100, index=True)
    description: Optional[str] = Field(default=None, max_length=500)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    users: List["User"] = Relationship(
        back_populates="roles",
        link_model=UserRole
    )
    permissions: List["Permission"] = Relationship(
        back_populates="roles",
        link_model=RolePermission
    )

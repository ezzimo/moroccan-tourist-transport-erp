"""
Permission model for granular access control
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid
from .role import RolePermission
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .role import Role


class Permission(SQLModel, table=True):
    """Permission model for fine-grained access control"""
    __tablename__ = "permissions"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    # e.g., "vehicles", "bookings"
    service_name: str = Field(max_length=100, index=True)
    # e.g., "create", "read", "update", "delete" 
    action: str = Field(max_length=50, index=True)
    # e.g., "own", "all", specific resource ID
    resource: str = Field(max_length=100, default="*")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    roles: list["Role"] = Relationship(
        back_populates="permissions",
        link_model=RolePermission
    )

    def __str__(self) -> str:
        return f"{self.service_name}:{self.action}:{self.resource}"

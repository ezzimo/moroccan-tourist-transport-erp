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
        default=None, foreign_key="role.id", primary_key=True
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
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    last_login: Optional[datetime] = Field(default=None)
    
    # Relationships
    roles: List["Role"] = Relationship(
        back_populates="users", 
        link_model=UserRole
    )
    
    def has_permission(self, service_name: str, action: str, resource: str = "*") -> bool:
        """Check if user has specific permission"""
        for role in self.roles:
            for permission in role.permissions:
                if (permission.service_name == service_name and 
                    permission.action == action and 
                    (permission.resource == resource or permission.resource == "*")):
                    return True
        return False
    
    def get_all_permissions(self) -> List[str]:
        """Get all permissions for the user"""
        permissions = set()
        for role in self.roles:
            for permission in role.permissions:
                permissions.add(f"{permission.service_name}:{permission.action}:{permission.resource}")
        return list(permissions)
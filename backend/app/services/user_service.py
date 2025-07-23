"""
User service for user management operations
"""
from sqlmodel import Session, select
from fastapi import HTTPException, status
from models.user import User, UserRole
from models.role import Role
from schemas.user import UserCreate, UserUpdate, UserResponse, UserWithRoles
from utils.security import get_password_hash
from typing import List, Optional
from datetime import datetime
import uuid


class UserService:
    """Service for handling user operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user"""
        # Check if email already exists
        statement = select(User).where(User.email == user_data.email)
        existing_user = self.session.exec(statement).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            phone=user_data.phone,
            password_hash=get_password_hash(user_data.password)
        )
        
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        
        # Assign roles if provided
        if user_data.role_ids:
            await self._assign_roles(user.id, user_data.role_ids)
        
        return UserResponse.model_validate(user)
    
    async def get_user(self, user_id: uuid.UUID) -> UserWithRoles:
        """Get user by ID with roles"""
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserWithRoles.model_validate(user)
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Get list of users"""
        statement = select(User).offset(skip).limit(limit)
        users = self.session.exec(statement).all()
        return [UserResponse.model_validate(user) for user in users]
    
    async def update_user(self, user_id: uuid.UUID, user_data: UserUpdate) -> UserResponse:
        """Update user information"""
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields
        update_data = user_data.model_dump(exclude_unset=True)
        role_ids = update_data.pop("role_ids", None)
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        
        # Update roles if provided
        if role_ids is not None:
            await self._assign_roles(user_id, role_ids)
        
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        
        return UserResponse.model_validate(user)
    
    async def delete_user(self, user_id: uuid.UUID) -> dict:
        """Delete user (soft delete by marking inactive)"""
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        self.session.add(user)
        self.session.commit()
        
        return {"message": "User deactivated successfully"}
    
    async def _assign_roles(self, user_id: uuid.UUID, role_ids: List[uuid.UUID]):
        """Assign roles to user"""
        # Remove existing roles
        statement = select(UserRole).where(UserRole.user_id == user_id)
        existing_roles = self.session.exec(statement).all()
        for role in existing_roles:
            self.session.delete(role)
        
        # Add new roles
        for role_id in role_ids:
            # Verify role exists
            role_statement = select(Role).where(Role.id == role_id)
            role = self.session.exec(role_statement).first()
            if role:
                user_role = UserRole(user_id=user_id, role_id=role_id)
                self.session.add(user_role)
        
        self.session.commit()
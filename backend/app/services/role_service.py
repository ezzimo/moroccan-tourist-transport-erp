"""
Role and Permission service for RBAC operations
"""

from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from models.role import Role, RolePermission
from models.permission import Permission
from schemas.role import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleWithPermissions,
    PermissionCreate,
    PermissionResponse,
)
from typing import List
from datetime import datetime
import uuid


class RoleService:
    """Service for handling role and permission operations"""

    def __init__(self, session: Session):
        self.session = session

    # Role operations
    async def create_role(self, role_data: RoleCreate) -> RoleResponse:
        """Create a new role"""
        # Check if role name already exists
        statement = select(Role).where(Role.name == role_data.name)
        existing_role = self.session.exec(statement).first()

        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role name already exists",
            )

        # Create role
        role = Role(name=role_data.name, description=role_data.description)

        self.session.add(role)
        self.session.commit()
        self.session.refresh(role)

        # Assign permissions if provided
        if role_data.permission_ids:
            await self._assign_permissions(role.id, role_data.permission_ids)

        return RoleResponse.model_validate(role)

    async def get_role(self, role_id: uuid.UUID) -> RoleWithPermissions:
        """Get role by ID with permissions"""
        statement = select(Role).where(Role.id == role_id)
        role = self.session.exec(statement).first()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )

        return RoleWithPermissions.model_validate(role)

    async def get_roles(
        self, skip: int = 0, limit: int = 100
    ) -> list[RoleWithPermissions]:
        """Get list of roles with permissions"""
        statement = (
            select(Role)
            .options(selectinload(Role.permissions))
            .offset(skip)
            .limit(limit)
        )
        roles = self.session.exec(statement).all()
        return [RoleWithPermissions.model_validate(role) for role in roles]

    async def update_role(
        self, role_id: uuid.UUID, role_data: RoleUpdate
    ) -> RoleResponse:
        """Update role information"""
        statement = select(Role).where(Role.id == role_id)
        role = self.session.exec(statement).first()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )

        # Update fields
        update_data = role_data.model_dump(exclude_unset=True)
        permission_ids = update_data.pop("permission_ids", None)

        for field, value in update_data.items():
            setattr(role, field, value)

        role.updated_at = datetime.utcnow()

        # Update permissions if provided
        if permission_ids is not None:
            await self._assign_permissions(role_id, permission_ids)

        self.session.add(role)
        self.session.commit()
        self.session.refresh(role)

        return RoleResponse.model_validate(role)

    async def delete_role(self, role_id: uuid.UUID) -> dict:
        """Delete role"""
        statement = select(Role).where(Role.id == role_id)
        role = self.session.exec(statement).first()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )

        self.session.delete(role)
        self.session.commit()

        return {"message": "Role deleted successfully"}

    # Permission operations
    async def create_permission(
        self, permission_data: PermissionCreate
    ) -> PermissionResponse:
        """Create a new permission"""
        # Check if permission already exists
        statement = select(Permission).where(
            Permission.service_name == permission_data.service_name,
            Permission.action == permission_data.action,
            Permission.resource == permission_data.resource,
        )
        existing_permission = self.session.exec(statement).first()

        if existing_permission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission already exists",
            )

        permission = Permission(**permission_data.model_dump())
        self.session.add(permission)
        self.session.commit()
        self.session.refresh(permission)

        return PermissionResponse.model_validate(permission)

    async def get_permissions(
        self, skip: int = 0, limit: int = 100
    ) -> list[PermissionResponse]:
        """Get list of permissions"""
        statement = select(Permission).offset(skip).limit(limit)
        permissions = self.session.exec(statement).all()
        return [PermissionResponse.model_validate(perm) for perm in permissions]

    async def delete_permission(self, permission_id: uuid.UUID) -> dict:
        """Delete permission"""
        statement = select(Permission).where(Permission.id == permission_id)
        permission = self.session.exec(statement).first()

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found"
            )

        self.session.delete(permission)
        self.session.commit()

        return {"message": "Permission deleted successfully"}

    async def _assign_permissions(
        self, role_id: uuid.UUID, permission_ids: list[uuid.UUID]
    ):
        """Assign permissions to role"""
        # Remove existing permissions
        statement = select(RolePermission).where(RolePermission.role_id == role_id)
        existing_permissions = self.session.exec(statement).all()
        for perm in existing_permissions:
            self.session.delete(perm)

        # Add new permissions
        for permission_id in permission_ids:
            # Verify permission exists
            perm_statement = select(Permission).where(Permission.id == permission_id)
            permission = self.session.exec(perm_statement).first()
            if permission:
                role_permission = RolePermission(
                    role_id=role_id, permission_id=permission_id
                )
                self.session.add(role_permission)

        self.session.commit()

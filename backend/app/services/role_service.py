"""
Async Role & Permission service
"""

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
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
from datetime import datetime
import uuid


class RoleService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_role(self, role_data: RoleCreate) -> RoleResponse:
        existing = await self.session.execute(
            select(Role).where(Role.name == role_data.name)
        )
        if (
            existing.scalar_one_or_none()
        ):  # Changed from first() to scalar_one_or_none()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role name already exists",
            )
        role = Role(name=role_data.name, description=role_data.description)
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)

        if role_data.permission_ids:
            await self._assign_permissions(role.id, role_data.permission_ids)

        return RoleResponse.model_validate(role)

    async def get_role(self, role_id: uuid.UUID) -> RoleWithPermissions:
        # Load role with permissions relationship
        stmt = (
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id)
        )
        res = await self.session.execute(stmt)
        role = res.scalar_one_or_none()  # Changed from first() to scalar_one_or_none()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )
        return RoleWithPermissions.model_validate(role)

    async def get_roles(
        self, skip: int = 0, limit: int = 100
    ) -> list[RoleWithPermissions]:
        stmt = (
            select(Role)
            .options(selectinload(Role.permissions))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        roles = (
            result.scalars().all()
        )  # Changed: use scalars() to get the actual objects
        return [RoleWithPermissions.model_validate(role) for role in roles]

    async def update_role(
        self, role_id: uuid.UUID, role_data: RoleUpdate
    ) -> RoleResponse:
        res = await self.session.execute(select(Role).where(Role.id == role_id))
        role = res.scalar_one_or_none()  # Changed from first() to scalar_one_or_none()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )

        update_data = role_data.model_dump(exclude_unset=True)
        permission_ids = update_data.pop("permission_ids", None)
        for k, v in update_data.items():
            setattr(role, k, v)
        role.updated_at = datetime.utcnow()

        if permission_ids is not None:
            await self._assign_permissions(role_id, permission_ids)

        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)
        return RoleResponse.model_validate(role)

    async def delete_role(self, role_id: uuid.UUID) -> dict:
        res = await self.session.execute(select(Role).where(Role.id == role_id))
        role = res.scalar_one_or_none()  # Changed from first() to scalar_one_or_none()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )
        await self.session.delete(role)
        await self.session.commit()
        return {"message": "Role deleted successfully"}

    async def create_permission(
        self, permission_data: PermissionCreate
    ) -> PermissionResponse:
        res = await self.session.execute(
            select(Permission).where(
                Permission.service_name == permission_data.service_name,
                Permission.action == permission_data.action,
                Permission.resource == permission_data.resource,
            )
        )
        if res.scalar_one_or_none():  # Changed from first() to scalar_one_or_none()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission already exists",
            )
        permission = Permission(**permission_data.model_dump())
        self.session.add(permission)
        await self.session.commit()
        await self.session.refresh(permission)
        return PermissionResponse.model_validate(permission)

    async def get_permissions(
        self, skip: int = 0, limit: int = 100
    ) -> list[PermissionResponse]:
        result = await self.session.execute(
            select(Permission).offset(skip).limit(limit)
        )
        perms = (
            result.scalars().all()
        )  # Changed: use scalars() to get the actual objects
        return [PermissionResponse.model_validate(perm) for perm in perms]

    async def delete_permission(self, permission_id: uuid.UUID) -> dict:
        res = await self.session.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        perm = res.scalar_one_or_none()  # Changed from first() to scalar_one_or_none()
        if not perm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found"
            )
        await self.session.delete(perm)
        await self.session.commit()
        return {"message": "Permission deleted successfully"}

    async def _assign_permissions(
        self, role_id: uuid.UUID, permission_ids: list[uuid.UUID]
    ):
        # Delete existing role permissions
        result = await self.session.execute(
            select(RolePermission).where(RolePermission.role_id == role_id)
        )
        existing = result.scalars().all()  # Changed: use scalars()
        for rp in existing:
            await self.session.delete(rp)

        # Add new permissions
        for pid in permission_ids:
            check = await self.session.execute(
                select(Permission).where(Permission.id == pid)
            )
            if (
                check.scalar_one_or_none()
            ):  # Changed from first() to scalar_one_or_none()
                self.session.add(RolePermission(role_id=role_id, permission_id=pid))
        await self.session.commit()
